"""The keyboard network's training model, checked without recordings.

Tools/keyboard_network.py fits a whole keyboard through a closed form of what
the fitter measures. These checks hold that closed form to the fitter's own
window model (piano_analysis._WindowedExponentials) and to envelopes measured
from a synthetic strike, check what the loss leaves free and what the knob's
penalty skips, check that a short training run learns a synthetic keyboard,
and check the settings and the locked splits the run reads. They read no
recording. `keyboard_network.py all` runs them first; they need NumPy, SciPy
and PyTorch.
"""
from __future__ import annotations

import json
import math
import pickle
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Tools'))
import fit_realtime_modal as fit  # noqa: E402
import keyboard_measurements as km  # noqa: E402
import keyboard_network as kn  # noqa: E402
import piano_analysis as pa  # noqa: E402

F1, SR = 110.0, 48000
# Frames as keyboard_measurements takes them: dense through the strike, then
# every 20 ms; the first ones before contact, as a take's are.
TIMES = np.r_[np.arange(-.004, .5, .0025), np.arange(.5, 3.0, .02)]


def window(f1=F1, sr=SR):
    length = pa.window_length(f1, sr)
    grid, profile = pa.window_profile(f1, sr, min(.002, length / sr / 24), length)
    return length, grid, profile


def truth_figures(orders, layers, seed):
    """Figures for every layer's series of one pitch as Net.forward gives
    them, layer by layer: the strings' (tuning and lanes) by partial alone,
    the strike's (levels, phases, rise) by layer too."""
    gen = np.random.default_rng(seed)
    t = lambda a: torch.tensor(a, dtype=torch.float64)  # noqa: E731
    unit = lambda a: torch.polar(torch.ones(a.shape, dtype=torch.float64), t(a))  # noqa: E731
    string = lambda a: np.tile(a, (layers,) + (1,) * (a.ndim - 1))  # noqa: E731
    rows = orders * layers
    return {'f1_cents': t(np.full(rows, 3.0)), 'log_b': t(np.full(rows, math.log(4e-4))),
            'cents': t(string(gen.uniform(-3, 3, orders))),
            'log_rate': t(string(np.sort(np.log(gen.uniform(.3, 60, (orders, 4))), 1)[:, ::-1].copy())),
            'offset': t(string(gen.uniform(-.8, .8, (orders, 4)))), 'theta': t(string(gen.uniform(.2, 1.3, (orders, 4)))),
            'lag': unit(string(gen.uniform(-.5, .5, (orders, 4)))),
            'level_db': t(gen.uniform(-40, -10, (rows, 4))), 'phase': unit(gen.uniform(-3, 3, (rows, 4))),
            'log_rise': t(np.log(gen.uniform(5e-4, .01, rows)))}


def lanes_of(out, f, fd):
    """Complex rates (rows x 8, the rise rate second) and channel amplitudes
    (rows x 2 x 4) of the figures, as network_prediction forms them."""
    s = torch.complex(-torch.exp(out['log_rate']), 2 * math.pi * (out['offset'] + (f - fd)[:, None]))
    S = torch.cat([s, s - torch.exp(-out['log_rise'])[:, None]], 1)
    amp = 10 ** (out['level_db'] / 20) * out['phase']
    left = (math.sqrt(2) * torch.cos(out['theta'])).to(amp.dtype)
    right = math.sqrt(2) * torch.sin(out['theta']) * out['lag']
    return S, amp[:, None, :] * torch.stack([left, right], 1)


def measured(t, s, C):
    """The fitter's model of a partial's envelope (channels x frames)."""
    _, grid, profile = window()
    B, _ = pa._WindowedExponentials(t, grid, profile)(s)
    return C @ (B[:, :4] - B[:, 4:]).T


def pitch(note, velocities, orders, envelope, freqs, t=TIMES):
    """One measured pitch in keyboard_measurements' format, its envelopes
    from envelope(layer, order index) and its frames weighed as
    measure_anchor weighs them."""
    length = pa.window_length(F1, SR)
    series = [[None] * len(velocities) for _ in orders]
    layers = []
    for i, v in enumerate(velocities):
        for k in range(len(orders)):
            z = envelope(i, k)
            amp = np.sqrt(np.mean(np.abs(z) ** 2, axis=0))
            local = np.array([amp[np.abs(t - x) <= km.BEAT].max() for x in t])
            series[k][i] = {'t': t, 'z': z.astype(np.complex64), 'w': (1 / local / math.sqrt(len(t))).astype(np.float32),
                            'floor_db': -300.0, 'peak': float(amp.max())}
        layers.append({'velocity': v, 'early_rms_db': -30.0 + 20 * math.log10(v / 127)})
    return {'note': note, 'sr': SR, 'f1': F1, 'length': length, 'orders': list(orders),
            'freqs': np.asarray(freqs, float), 'layers': layers, 'series': series, 'cache_key': 'synthetic'}


def load(pitches, normalised=False):
    """The pitches as load_library gives them to training."""
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp) / 'synthetic'
        folder.mkdir()
        for m in pitches:
            with (folder / f'{m["note"]}.pkl').open('wb') as f:
                pickle.dump(m, f)
        with mock.patch.object(kn, 'library_corpus', return_value={'normalised': normalised}):
            groups, _ = kn.load_library('synthetic', {}, 0, 0, {}, root=Path(tmp))
    return [u for g in groups for u in g['units']]


def tiny_net(tenor=50):
    return kn.Net(['p'], [[tenor]], ['synthetic'], [], {'code': 2, 'width': 16, 'depth': 2, 'fourier': 1})


class Fixture:
    """A measured pitch whose envelopes are the fitter's model of known
    figures, with those figures in the batch's row order."""

    def __init__(self, normalised=False, seed=1):
        self.note, self.orders, self.velocities = 45, [1, 2, 3, 5, 8], [40, 100]
        rows = len(self.orders) * len(self.velocities)
        self.out = truth_figures(len(self.orders), len(self.velocities), seed)
        n = torch.tensor([float(self.note)] * rows)
        order = torch.tensor([float(o) for o in self.orders] * len(self.velocities))
        net = tiny_net()
        self.f = net.frequency(self.out, n, order)
        # Measured where the partial plays: its lanes' offsets are the only detuning.
        self.fd = self.f.clone()
        self.S, self.C = lanes_of(self.out, self.f, self.fd)
        k = len(self.orders)
        self.units = load([pitch(self.note, self.velocities, self.orders,
                                 lambda i, j: measured(TIMES, self.S[i * k + j].numpy(), self.C[i * k + j].numpy()),
                                 self.fd[:k].numpy())], normalised)
        self.b = kn.batch_of(self.units)


class WindowModel(unittest.TestCase):
    def test_windowed_response_is_the_fitters(self):
        """windowed_response's recursion against _WindowedExponentials' direct
        sum, through frames before contact and rises far shorter than a cell."""
        fx = Fixture()
        gen = np.random.default_rng(2)
        rates = -np.exp(gen.uniform(np.log(.3), np.log(300), (len(fx.b['fd']), 4)))
        s = rates + 2j * np.pi * gen.uniform(-3, 3, rates.shape)
        rise = np.array([2e-4, 2e-3, .02, .3])[None, :]
        S = torch.from_numpy(np.c_[s, s - 1 / rise])
        B = kn.windowed_response(fx.b, S).numpy()
        _, grid, profile = window()
        for row in range(len(fx.b['fd'])):
            frames = (fx.b['sid'] == row).numpy()
            want, _ = pa._WindowedExponentials(fx.b['t'].numpy()[frames], grid, profile)(S[row].numpy())
            np.testing.assert_allclose(B[frames], want, rtol=0, atol=1e-10 * np.abs(want).max())


class Truth(unittest.TestCase):
    def test_truth_scores_nothing(self):
        """The figures that made the envelopes, through network_prediction,
        leave no envelope misfit, no fitter's misfit and no tuning error
        beyond their lanes' own offsets."""
        fx = Fixture()
        net = tiny_net()
        net.forward = lambda piano, note, order, level: fx.out
        with torch.no_grad():
            S, C, cents = kn.network_prediction(net, fx.b)
            loss = kn.envelope_misfit(fx.b, S, C)
            _, rel = kn.misfit(fx.b, S, C)
        self.assertLess(float(loss.max()), 1e-9)
        self.assertLess(float(rel.abs().max()), 1e-6)
        power = 10 ** (fx.out['level_db'] / 10)
        centre = fx.f + torch.sum(power * fx.out['offset'], 1) / torch.sum(power, 1)
        np.testing.assert_allclose(cents.numpy(), (1200 * torch.log2(centre / fx.fd)).numpy(), atol=1e-9)

    def test_truth_is_the_minimum(self):
        """Away from the figures the loss grows, and at them it is flat."""
        fx = Fixture()
        net = tiny_net()
        level = fx.out['level_db'].clone().requires_grad_(True)
        net.forward = lambda piano, note, order, lv: {**fx.out, 'level_db': level}
        S, C, _ = kn.network_prediction(net, fx.b)
        loss = kn.envelope_misfit(fx.b, S, C).mean()
        loss.backward()
        self.assertLess(float(level.grad.abs().max()), 1e-6)
        with torch.no_grad():
            for step in (-3.0, 3.0):
                net.forward = lambda piano, note, order, lv: {**fx.out, 'level_db': fx.out['level_db'] + step}
                S, C, _ = kn.network_prediction(net, fx.b)
                self.assertGreater(float(kn.envelope_misfit(fx.b, S, C).mean()), .01)

    def test_envelopes_of_a_synthetic_strike(self):
        """A strike synthesised sample by sample and measured with
        piano_analysis.envelopes, as every take is, against the closed form
        of the same lanes. What is left is the window held constant over each
        grid cell and the partials' leakage through its sidelobes."""
        fx = Fixture()
        k = len(fx.orders)
        start, seconds = 4800, 3.2
        tau = (np.arange(int((seconds + .1) * SR)) - start) / SR
        on = tau >= 0
        for i in range(len(fx.velocities)):
            x = np.zeros((len(tau), 2))
            fd = []
            for j, order in enumerate(fx.orders):
                row = i * k + j
                # Partials an octave apart and more, so that the window parts them.
                hz = float(fx.fd[row]) * (1 + j)
                fd.append(hz)
                s, C = fx.S[row].numpy(), fx.C[row].numpy()
                lanes = np.exp(np.outer(tau[on], s[:4])) - np.exp(np.outer(tau[on], s[4:]))
                x[on] += np.real((lanes @ C.T) * np.exp(2j * np.pi * hz * tau[on])[:, None])
            t, z = pa.envelopes(x, SR, fd, F1, start, None, times=TIMES[TIMES >= 0])
            for j in range(k):
                row = i * k + j
                closed = measured(t, fx.S[row].numpy(), fx.C[row].numpy())
                power = np.mean(np.abs(closed) ** 2)
                err = np.mean(np.abs(z[j] - closed) ** 2) / power
                self.assertLess(err, 2e-4, f'layer {i}, partial {fx.orders[j]}: relative error {err:.1e}')


class FreeAndFixed(unittest.TestCase):
    def test_power_loss_ignores_each_partials_phase(self):
        fx = Fixture()
        gen = np.random.default_rng(3)
        turn = torch.polar(torch.ones(len(fx.b['fd']), 2, 1, dtype=torch.float64),
                           torch.from_numpy(gen.uniform(-np.pi, np.pi, (len(fx.b['fd']), 2, 1))))
        C = fx.C * 1.3
        np.testing.assert_allclose(kn.envelope_misfit(fx.b, fx.S, C * turn).numpy(),
                                   kn.envelope_misfit(fx.b, fx.S, C).numpy(), rtol=1e-12, atol=1e-15)

    def test_normalised_take_level_is_free(self):
        """Where a library normalised its takes, each take's level in each
        channel is the recording's, not the piano's; elsewhere it counts.
        Exact without the floor under each frame's power."""
        gains = torch.tensor([[1.8, .4]], dtype=torch.complex128)[:, :, None]
        with mock.patch.object(kn, 'NULL', 0.0):
            for normalised in (True, False):
                fx = Fixture(normalised=normalised)
                wrong = fx.C * torch.from_numpy(np.random.default_rng(4).uniform(.5, 2, (len(fx.b['fd']), 1, 4)))
                scaled = wrong.clone()
                first = fx.b['unit'] == 0
                scaled[first] = scaled[first] * gains
                a = kn.envelope_misfit(fx.b, fx.S, wrong)
                b = kn.envelope_misfit(fx.b, fx.S, scaled)
                if normalised:
                    np.testing.assert_allclose(b.numpy(), a.numpy(), rtol=1e-9)
                else:
                    self.assertGreater(float(b[first].mean() - a[first].mean()), .1)

    def test_channel_gain_meets_the_frames(self):
        fx = Fixture()
        pw = kn.predicted_frames(fx.b, fx.S, fx.C) * torch.tensor([.1, 3.0])
        gain = kn.channel_gain([(fx.b, pw, torch.ones(len(fx.b['t']), dtype=torch.bool))])
        np.testing.assert_allclose(gain.numpy(), [10.0, 1 / 3], rtol=1e-4)


class FakeGenerator:
    """roughness()'s draws, fixed: every partial of `order`, at -10 dB."""

    def __init__(self, order):
        self.order = order

    def uniform(self, low, high, size=None):
        return np.full(size, math.log(self.order)) if size else -10.0


class Roughness(unittest.TestCase):
    def roughness_of(self, step_at, order=2, tenor=50):
        """The knob's penalty on figures straight over the keys but for one
        step of each, between keys step_at - 1 and step_at."""
        net = tiny_net(tenor)

        def forward(piano, note, order_, level):
            u = (note - 64.5) / 43.5
            up = (note >= step_at).to(u.dtype)
            n = len(note)
            figures = {'f1_cents': 2 * u + up, 'log_b': -8 + u + .3 * up, 'cents': u + up}
            line = lambda a, b: (a + b * u + up)[:, None].expand(n, 4)  # noqa: E731
            figures.update(log_rate=line(1.0, .5), theta=line(.5, .1), level_db=line(-20, 4), log_rise=-5 + u + up,
                           lag=torch.polar(torch.ones(n, 4), (.3 + .4 * up)[:, None].expand(n, 4)),
                           phase=torch.polar(torch.ones(n, 4), (1 + .4 * up)[:, None].expand(n, 4)))
            # Offsets a fixed share of the partial's frequency, so that their
            # cents, which the penalty reads, are straight too.
            figures['offset'] = net.frequency(figures, note, order_)[:, None] * (1e-3 + 1e-3 * up)[:, None]
            return figures
        net.forward = forward
        with torch.no_grad():
            return float(kn.roughness(net, FakeGenerator(order), [0]))

    def test_no_penalty_across_the_bass_break(self):
        self.assertLess(self.roughness_of(step_at=50), 1e-20)
        self.assertGreater(self.roughness_of(step_at=60), 1e-4)

    def test_no_penalty_above_the_highest_partial(self):
        # Key 100 plays 2.6 kHz: its 20th partial would be over TOP_HZ, its second is not.
        self.assertLess(self.roughness_of(step_at=100, order=20), 1e-20)
        self.assertGreater(self.roughness_of(step_at=100, order=2), 1e-4)


class Training(unittest.TestCase):
    def test_start_does_not_depend_on_what_ran_before(self):
        """A worker trains entries in turn: each starts as it would alone."""
        first = tiny_net().state_dict()
        torch.randn(1000)
        again = tiny_net().state_dict()
        for name, value in first.items():
            self.assertTrue(torch.equal(value, again[name]), name)

    def test_short_run_learns_a_synthetic_keyboard(self):
        """A smooth synthetic keyboard, one partial set per pitch: a short
        run at the settings' rate takes the loss well under where it starts."""
        notes, orders, velocities = [33, 45, 57, 69, 81], [1, 2, 3, 4], [50, 110]
        pitches = []
        for note in notes:
            fd = [float(pa.stiff(pa.midi_hz(note), 3e-4, n)) for n in orders]

            def envelope(i, j, note=note, fd=fd):
                rate = .5 + .02 * (note - 21) + .3 * orders[j]
                level = -10 * math.log10(orders[j]) + 12 * math.log10(velocities[i] / 127) - .1 * (note - 60)
                s = -rate * np.array([8, 3, 1, 1 / 3]) + 2j * np.pi * np.array([.4, -.3, .2, -.1])
                s = np.r_[s, s - 1 / .003]
                C = 10 ** (level / 20) * np.array([[.5, .3, .2, .1], [.4, .3, .25, .1]], complex)
                return measured(TIMES, s, C)
            pitches.append(pitch(note, velocities, orders, envelope, fd))
        units = {'synthetic': load(pitches)}
        net = tiny_net()
        kn.start_gains(net, units)
        settings = dict(kn.load_config()['training'], units_per_library=4)
        with torch.no_grad():
            before = float(kn.loss_of(net, units['synthetic'], {0: 1.0}, settings['tune_weight'])[0])
        kn.train(net, units, {0: 1.0}, settings, 0.0, 1, steps=400)
        with torch.no_grad():
            after = float(kn.loss_of(net, units['synthetic'], {0: 1.0}, settings['tune_weight'])[0])
        self.assertLess(after, .3 * before, f'loss {before:.3f} -> {after:.3f}')


class BlendCorrection(unittest.TestCase):
    """The correction's examples: today's engine's blend between two recorded
    pitches (KeyraEngine.cpp blended()) as keyboard_network mirrors it, on a
    piano's fitted table, and a correction that moves it only between them."""
    table = kn.header_of('hamburg')
    piano = kn.ENGINE_PIANOS.index('hamburg')

    def test_blend_plays_each_fit_at_its_pitch(self):
        """At either end the blend is the fit there: its lanes' rates and
        each lane's power in each channel, at the softest and loudest layer."""
        grid = self.table['grid']
        for lower in (0, 4, 8):
            for t, side in ((0.0, lower), (1.0, lower + 1)):
                for v in (grid[0], grid[-1]):
                    blends = kn.engine_blended(self.piano, self.table, lower, lower + 1, t, v, {})
                    for p in self.table['anchors'][side]['partials']:
                        S, C = kn.closed_form(*blends[p['order']], np.ones(2))
                        S0, C0 = kn.closed_form(kn.engine_partial(p, grid, v), 1.0, np.ones(2))
                        np.testing.assert_allclose(np.sort_complex(S), np.sort_complex(S0), rtol=1e-12)
                        np.testing.assert_allclose(np.sort(np.abs(C), 1), np.sort(np.abs(C0), 1), rtol=1e-5)

    def test_blend_power_lies_between_the_pitches(self):
        """Between them each channel's power over the window lies between the
        two pitches' and both channels' sum at its place between theirs in
        dB, as Tests/pitch_blend_tests.cpp holds the engine's."""
        grid = self.table['grid']
        a, b = ({p['order']: p for p in self.table['anchors'][i]['partials']} for i in (2, 3))
        for order in sorted(set(a) & set(b)):
            x, y = (kn.engine_partial(p[order], grid, 80.0) for p in (a, b))
            pair = kn.lane_pairing(a[order], b[order])
            for t in (.25, .5, .75):
                d = kn.engine_blend(x, y, t, pair)
                for channel in ((1, 0), (0, 1)):
                    low, high = sorted(kn.window_power(p, *channel) for p in (x, y))
                    self.assertTrue(low * (1 - 1e-9) <= kn.window_power(d, *channel) <= high * (1 + 1e-9), order)
                self.assertAlmostEqual(math.log(kn.window_power(d)),
                                       (1 - t) * math.log(kn.window_power(x)) + t * math.log(kn.window_power(y)),
                                       places=9)

    def test_departure_vanishes_at_the_recorded_pitches(self):
        net = kn.Correction(['p'], [[50]], {'code': 2, 'width': 16, 'depth': 1, 'fourier': 1})
        with torch.no_grad():
            for w in net.parameters():
                w.add_(.3 * torch.randn(w.shape, generator=torch.Generator().manual_seed(2)))
        rows = 6
        args = (torch.zeros(rows, dtype=torch.long), None, torch.tensor([1., 2., 3., 5., 8., 13.]),
                torch.linspace(-30, 0, rows), torch.full((rows,), 40.), torch.full((rows,), 47.))
        with torch.no_grad():
            for note, t in ((40., 0.), (47., 1.)):
                d = kn.departure(net, args[0], torch.full((rows,), note), *args[2:], torch.full((rows,), t))
                for k, v in d.items():
                    self.assertTrue(torch.all(v == 0), k)
            d = kn.departure(net, args[0], torch.full((rows,), 43.), *args[2:], torch.full((rows,), 3 / 7))
        self.assertGreater(float(torch.abs(d['level_db']).max()), 1e-3)

    def test_short_run_learns_a_synthetic_correction(self):
        """Hidden pitches whose fits stand 2.5 to 4 dB over the blend around
        them, the more the higher the partial, and decay faster: a short run
        takes the loss well under where it starts."""
        notes, orders, velocities = [33, 45, 57, 69, 81], [1, 2, 3, 4], [50, 110]
        pitches, blends = [], {}
        for note in notes:
            fd = [float(pa.stiff(pa.midi_hz(note), 3e-4, n)) for n in orders]

            def figures(i, j, note=note):
                rate = .5 + .02 * (note - 21) + .3 * orders[j]
                level = -10 * math.log10(orders[j]) + 12 * math.log10(velocities[i] / 127) - .1 * (note - 60)
                s = -rate * np.array([8, 3, 1, 1 / 3]) + 2j * np.pi * np.array([.4, -.3, .2, -.1])
                C = 10 ** (level / 20) * np.array([[.5, .3, .2, .1], [.4, .3, .25, .1]], complex)
                return np.r_[s, s - 1 / .003], C

            def envelope(i, j, figures=figures):
                return measured(TIMES, *figures(i, j))
            pitches.append(pitch(note, velocities, orders, envelope, fd))
            for i in range(len(velocities)):
                for j in range(len(orders)):
                    S, C = figures(i, j)
                    S = np.r_[S[:4].real * .8 + 1j * S[:4].imag, S[:4].real * .8 + 1j * S[:4].imag - 1 / .003]
                    blends[note, i, j] = S, C * 10 ** (-(2 + orders[j] / 2) / 20)
        units = load(pitches)
        for u in units:
            i, k = velocities.index(u['velocity']), u['group']['note']
            u.update(blend_S=np.array([blends[k, i, orders.index(int(o))][0] for o in u['order']]),
                     blend_C=np.array([blends[k, i, orders.index(int(o))][1] for o in u['order']]),
                     lower=k - 6, upper=k + 6, mix=.5)
        net = kn.Correction(['p'], [[50]], {'code': 2, 'width': 16, 'depth': 2, 'fourier': 1})
        settings = dict(kn.load_config()['training'], units_per_library=4)
        with torch.no_grad():
            before = float(kn.loss_of(net, units, {0: 1.0}, settings['tune_weight'])[0])
        kn.train(net, {'synthetic': units}, {0: 1.0}, settings, 0.0, 1, steps=300)
        with torch.no_grad():
            after = float(kn.loss_of(net, units, {0: 1.0}, settings['tune_weight'])[0])
        self.assertLess(after, .3 * before, f'loss {before:.3f} -> {after:.3f}')


class Settings(unittest.TestCase):
    config = kn.load_config()

    def test_pianos_and_libraries(self):
        libraries, pianos = self.config['libraries'], self.config['pianos']
        used = {info['piano'] for info in libraries.values()}
        self.assertEqual(used, set(pianos), 'every piano has a library and a tenor, and no other')
        for name, piano in pianos.items():
            self.assertIn(piano['tenor'], range(22, 108), name)
        keyra = {n for n, i in libraries.items() if i.get('keyra')}
        self.assertEqual(keyra, set(fit.MODELS), 'the Keyra pianos are the ones fit_realtime_modal fits')
        for name in keyra:
            self.assertEqual(libraries[name]['piano'], name)
        for name, info in libraries.items():
            corpus = kn.library_corpus(name)
            if 'capture_of' in corpus:
                self.assertEqual(info['piano'], corpus['capture_of'], f'{name} records the piano it captures')

    def test_architectures_knobs_and_training(self):
        for name, arch in self.config['architectures'].items():
            self.assertEqual(set(arch), {'code', 'width', 'depth', 'fourier'}, name)
            self.assertTrue(arch['code'] > 0 and arch['depth'] > 0 and arch['fourier'] >= 0, name)
            self.assertTrue(arch['width'] >= 2 and arch['width'] % 2 == 0, name)
        knobs = self.config['knobs']
        self.assertEqual(knobs, sorted(knobs))
        self.assertGreaterEqual(knobs[0], 0)
        self.assertGreaterEqual(self.config['folds'], 2)
        training = self.config['training']
        for key in ('steps', 'units_per_library', 'learning_rate', 'fine_tune_steps', 'fine_tune_learning_rate'):
            self.assertGreater(training[key], 0, key)


class Split(unittest.TestCase):
    def test_train_and_dev_takes_keep_their_roles(self):
        """Training reads the train takes, the backtest the dev takes, and
        neither reads a sealed one."""
        for name, model in fit.MODELS.items():
            roles = json.loads(model['split'].read_text())['cases']
            train = {case for job in km.piano_jobs(name) for case, _, _ in job[4]}
            dev = {case for job in kn.dev_jobs(name) for case, _, _ in job[4]}
            self.assertTrue(train, name)
            self.assertEqual({roles[c] for c in train}, {'train'}, name)
            self.assertTrue(not dev or {roles[c] for c in dev} == {'dev'}, name)
            self.assertFalse(train & dev, name)



if __name__ == '__main__':
    torch.set_num_threads(1)
    unittest.main()
