#!/usr/bin/env python3
"""Fit the measured modal data of each of Keyra's pianos from the calibration
split of its recordings (MODELS): the grand from the Salamander Grand Piano V3
(Tools/corpus/split-2026-10-27.json), the upright from the Helsinki 1967
Tube-Ribbon Edition (Tools/corpus/split-helsinki-2026-10-28.json).

Only a split's train recordings are opened: for the grand every A, C and F#
pitch from A0 to A7 (22 anchors; C8 is left out, see UNCALIBRATED) at twelve
velocity layers, for the upright 28 of its 35 recorded pitches at their five
layers' first takes. Each anchor is calibrated by
`piano_analysis.analyse_anchor`: every partial is fitted jointly across the
layers, with lanes whose rates and frequencies the strings fix and whose
complex amplitude per microphone the hammer and the pickup set. What the
partials leave below the treble's fundamentals gives the body modes every
strike knocks, and the undamped strings from F6 up, which every strike sets
ringing, are measured as tones at their own pitches across the anchors. The
upright's key-release takes give what its dampers leave ringing. The
fitted numbers go into the piano's header in Source/DSP (MeasuredModalData.h,
MeasuredUprightData.h), in the types of MeasuredTypes.h; no recorded waveform
or impulse response enters a header.

  python3 Tools/fetch_salamander.py                  # the grand's corpus, once
  python3 Tools/decode_helsinki.py --library <path>  # the upright's, from a copy of the library
  python3 Tools/fit_realtime_modal.py --analyse      # measure the anchors (cached in out/)
  python3 Tools/fit_realtime_modal.py                # regenerate the header and provenance
  python3 Tools/fit_realtime_modal.py --check        # verify both reproduce exactly
  python3 Tools/fit_realtime_modal.py --model upright [--analyse | --check]
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import pickle
from pathlib import Path

# One BLAS thread per worker: the pool already fills every core, and a fixed
# thread count keeps the floating-point results the same on any machine.
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / 'Tools/piano_analysis.py'
# The SFZ velocity bins' rounded midpoints, layer 1..16 (the split's mapping).
LAYER_VELOCITY = [14, 31, 36, 40, 45, 49, 54, 61, 69, 77, 85, 93, 101, 109, 117, 124]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# Recorded pitches the fit does not use. C8's strongest components sit 90 to
# 100 cents above the stretch that F#7 and A7 set, and the partial series that
# does follow the stretch explains a few per cent of the recording; the fit
# picks no pitch for the note. The engine plays the keys above A7 from A7's
# data on the stretch curve.
UNCALIBRATED = {108: 'strongest components 90-100 cents above the stretch trend; no partial series explains '
                     'the recording'}
# The two pianos, each fitted from its own corpus and split into its own
# header. A key let go knocks the body as the take of each anchor's key does:
# Salamander's key release noise, and on the upright the hammer noise its
# library plays on key release. Only the grand's corpus records the pedal.
# The upright's key-release takes also show what its dampers leave ringing
# (damper_data); the grand's fade in over the damper's first tenth of a
# second (Docs/research/release-recordings-2026-10-27.md).
MODELS = {
    'grand': {'title': 'the Salamander Grand Piano V3 (Alexander Holm, CC BY 3.0)',
              'corpus': ROOT / 'Tools/corpus/salamander-v3.json',
              'split': ROOT / 'Tools/corpus/split-2026-10-27.json',
              'wav': ROOT / 'out/salamander/wav', 'cache': ROOT / 'out/calibration/anchors',
              'header': ROOT / 'Source/DSP/MeasuredModalData.h',
              'metadata': ROOT / 'Docs/research/realtime-modal-fit-2026-10-27.json',
              'uncalibrated': UNCALIBRATED, 'release': 'rel{key}', 'pedal': ('pedalD1', 'pedalU1'),
              'actions': 'The action\'s knocks on the body modes: each recorded pitch\'s key let go (its damper '
                         'landing) and the sustain pedal going down and up, from one take each in those '
                         'recordings\' own scale, gained up as a set.'},
    'upright': {'title': 'the Helsinki 1967 Tube-Ribbon Edition (Mikko Patama), with its author\'s permission; '
                         'the recordings are not distributed',
                'corpus': ROOT / 'Tools/corpus/helsinki-1967.json',
                'split': ROOT / 'Tools/corpus/split-helsinki-2026-10-28.json',
                'wav': ROOT / 'out/helsinki/wav', 'cache': ROOT / 'out/calibration/upright',
                'header': ROOT / 'Source/DSP/MeasuredUprightData.h',
                'metadata': ROOT / 'Docs/research/upright-modal-fit-2026-10-28.json',
                'uncalibrated': {}, 'release': 'hammer{note}', 'pedal': (), 'tail_floor': True, 'damper': True,
                'actions': 'The action\'s knocks on the body modes: the hammer noise the library plays as each '
                           'recorded pitch\'s key is let go, from one take each in those recordings\' own scale.'},
}
# The keys from F6 up have no dampers: every strike sets their strings
# ringing at their own pitches (halo_data). The analysis also searches the
# residual beside each one's pitch, so that the noise is measured clear of
# them; a pitch's components leave those peaks out, and any other within
# HALO_UNISON of another key's string, which is that string: 95 % of the
# peaks halo_pitches takes for a string lie that close to it. (Within 15
# cents instead, a fifth of the bass's components fell near some string by
# chance.) A peak beside an anchor's own fundamental lies beyond its lanes'
# reach (piano_analysis.lane_span: about 3 cents, or 10 where a lane settles
# at 3) and is one of its own unison strings: from C6 up the upright's sit 2
# to 10 cents out. Taken for the partial's own and left out, they left G7's
# fundamental 14 to 30 dB under the recordings from 0.25 to 1.5 s.
UNDAMPED = range(89, 109)
HALO_UNISON = 3.5


def layer_velocity(item) -> int:
    """The velocity a recorded layer plays at: its velocity range's midpoint,
    rounded half up, which for Salamander the SFZ's bins give (LAYER_VELOCITY)."""
    if 'velocity' in item:
        lo, hi = item['velocity']
        return (lo + hi + 1) // 2
    return LAYER_VELOCITY[item['layer'] - 1]


def train_anchors(model):
    """Each calibrated train pitch with its train layers' (id, velocity, flac pin)."""
    corpus = {f['id']: f for f in json.loads(model['corpus'].read_text())['files']}
    roles = json.loads(model['split'].read_text())['cases']
    anchors = {}
    for case, role in roles.items():
        item = corpus[case]
        if role == 'train' and item['kind'] == 'note':
            anchors.setdefault(item['midi'], []).append((case, layer_velocity(item), item['flac_sha256']))
    return {note: sorted(layers, key=lambda layer: layer[1]) for note, layers in sorted(anchors.items())
            if note not in model['uncalibrated']}


def cache_key(layers) -> str:
    h = hashlib.sha256(ANALYSIS.read_bytes())
    for case, velocity, pin in layers:
        h.update(f'{case}:{velocity}:{pin}\n'.encode())
    return h.hexdigest()


def analyse_one(name, note, layers):
    import piano_analysis as pa
    model = MODELS[name]
    key = cache_key(layers)
    target = model['cache'] / f'{note}.pkl'
    if target.exists():
        with target.open('rb') as f:
            if pickle.load(f).get('cache_key') == key:
                return note, 'cached'
    result = pa.analyse_anchor([model['wav'] / f'{case}.wav' for case, _, _ in layers], note,
                               [velocity for _, velocity, _ in layers])
    result['cache_key'] = key
    result['cases'] = [case for case, _, _ in layers]
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('wb') as f:
        pickle.dump(result, f)
    return note, 'analysed'


def analyse(name, jobs):
    anchors = train_anchors(MODELS[name])
    # Bass anchors carry the most partials; start them first.
    with concurrent.futures.ProcessPoolExecutor(jobs) as pool:
        futures = [pool.submit(analyse_one, name, note, layers) for note, layers in anchors.items()]
        for future in concurrent.futures.as_completed(futures):
            note, state = future.result()
            print(f'anchor {note}: {state}', flush=True)


def stiff_fit(orders, freqs, weights):
    """f1 and B of the stiff-string series through an anchor's partials."""
    import numpy as np
    from scipy import optimize
    import piano_analysis as pa
    n = np.asarray(orders, float)
    f = np.asarray(freqs, float)

    def residual(v):
        return weights * 1200 * np.log2(pa.stiff(v[0], v[1], n) / f)
    first = f[0] / n[0]
    fit = optimize.least_squares(residual, [first, 1e-4], bounds=([first * .97, 0], [first * 1.03, .05]),
                                 loss='soft_l1', f_scale=2.0, x_scale=[first, 1e-3])
    return float(fit.x[0]), float(fit.x[1])


def series(result):
    """An anchor's f1 and B: the stiff-string series through its reliable
    partials, each weighed by its signal to noise."""
    import numpy as np
    snr = np.array([L['peak_db'] - L['floor_db'] for L in result['layers']])
    reliable = np.array([f is not None for f in result['fits']])
    strength = np.clip(np.nanmax(snr, axis=0) / 30, .2, 1.5)
    return stiff_fit(np.array(result['orders'])[reliable], result['freqs'][reliable], strength[reliable])


def string_pitches(f1s):
    """The fundamental (Hz) the engine gives each undamped key, from the
    anchors' f1 ({note: f1}) as the engine interpolates them: cents from equal
    temperament linear in the note between the anchors around it, continued
    from the last two beyond them."""
    import math
    notes = sorted(f1s)
    cents = {n: 1200 * math.log2(f1s[n] / (440 * 2 ** ((n - 69) / 12))) for n in notes}
    pitches = {}
    for key in UNDAMPED:
        upper = next((k for k in range(1, len(notes)) if notes[k] >= key), len(notes) - 1)
        a, b = notes[upper - 1], notes[upper]
        c = cents[a] + (cents[b] - cents[a]) * (key - a) / (b - a)
        pitches[key] = 440 * 2 ** ((key - 69 + c / 100) / 12)
    return pitches


def lane_shapes(amplitudes):
    """Split per-layer lane amplitudes a[layer][channel, lane] into each lane's
    velocity-independent pickup shape and its complex level per layer.

    The shape u (left real and positive, unit mean channel power) is the
    lane's dominant singular vector across layers; a lane keeps it to within a
    few per cent of its energy, which `explained` reports. Each layer's
    complex level is the projection on it.
    """
    import numpy as np
    A = np.array(amplitudes)                                   # layers x channels x lanes
    u = np.empty((A.shape[1], A.shape[2]), complex)
    mu = np.empty((A.shape[0], A.shape[2]), complex)
    kept = 0.0
    for j in range(A.shape[2]):
        w, s, _ = np.linalg.svd(A[:, :, j].T, full_matrices=False)
        shape = w[:, 0] * np.exp(-1j * np.angle(w[0, 0])) * np.sqrt(A.shape[1])
        u[:, j] = shape
        mu[:, j] = np.conj(shape) @ A[:, :, j].T / A.shape[1]
        kept += s[0] ** 2
    explained = kept / max(np.sum(np.abs(A) ** 2), 1e-300)
    return u, mu, float(explained)


def layer_alignment(phases, weights, freqs, reference, span):
    """Per-layer time shifts (s) that bring the partials' phases into one pattern.

    `phases` and `weights` (partials x layers) are each partial's strongest
    lane at its layer's measured string contact. That contact is only known
    to a millisecond or so, which turns a partial at 2 kHz through whole
    cycles, yet the strike gives every layer much the same pattern of phases
    across the partials: the wave's arrival at the bridge and its dispersion.
    Alternately, the pattern is the weighted mean of the shifted layers and
    each layer's shift maximises its agreement with the pattern (a 5 us grid
    within `span` seconds); layer `reference` keeps shift zero. Returns the
    shifts and each partial's agreement across layers (0 to 1).
    """
    import math
    import numpy as np
    grid = np.arange(-span, span, 5e-6)
    steer = np.exp(-2j * math.pi * np.outer(grid, freqs))
    delta = np.zeros(phases.shape[1])
    for _ in range(10):
        pattern = np.angle(np.sum(weights * np.exp(1j * (phases - 2 * math.pi * np.outer(freqs, delta))), axis=1))
        previous = delta.copy()
        for i in range(phases.shape[1]):
            delta[i] = grid[int(np.argmax(np.real(steer @ (weights[:, i] * np.exp(1j * (phases[:, i] - pattern))))))]
        delta -= delta[reference]
        if np.allclose(delta, previous):
            break
    z = np.sum(weights * np.exp(1j * (phases - 2 * math.pi * np.outer(freqs, delta))), axis=1)
    return delta, np.abs(z) / np.maximum(np.sum(weights, axis=1), 1e-30)


def smooth_levels(velocity, levels_db, weights, strength=2.0):
    """Regularised levels: weighted least squares to the measured levels plus a
    penalty on curvature across velocity, so a single noisy layer cannot put a
    bump in the velocity response."""
    import numpy as np
    v = np.asarray(velocity, float)
    n = len(v)
    rows = [np.diag(np.sqrt(weights))]
    rhs = [np.sqrt(weights) * levels_db]
    for i in range(1, n - 1):
        h0, h1 = v[i] - v[i - 1], v[i + 1] - v[i]
        row = np.zeros(n)
        scale = strength * 20 / (h0 + h1)
        row[i - 1], row[i], row[i + 1] = scale / h0, -scale * (1 / h0 + 1 / h1), scale / h1
        rows.append(row[None])
        rhs.append([0.0])
    return np.linalg.lstsq(np.vstack(rows), np.concatenate(rhs), rcond=None)[0]


def onset_rise(x, sr, start, delay, f1, waves, rises, seconds=.03):
    """The shortest rise (s) a layer's partials take from string contact.

    Envelope windows six periods of the fundamental long cannot tell a 0.2 ms
    rise from a 5 ms one, so most bass partials' fitted rises are unidentified,
    and partials that start too abruptly click. The recording decides, from 2
    ms before contact to `seconds` after at 0.5 ms resolution: the stereo power
    of its strongest partials (0.7 to 8.5 times f1) has to build up as the
    fitted partials `waves` do (partials x samples x channels from the
    detected onset, without their rises), each rising over the larger of its
    own fitted rise `rises` and the candidate; and every octave band above
    them may not exceed the recording, which there holds the hammer's knock
    the partials lack. The candidate with the least mean squared dB error
    wins, the shortest of those within 1% of it where several tie: below the
    strongest partials' own rises the floor barely changes the error (most
    of the treble), and the shortest leaves the fitted rises alone. Each
    band's floor before the onset bounds both, so the recording's noise is
    not fitted.
    """
    import math
    import numpy as np
    from scipy import ndimage, signal
    samples = waves.shape[1]
    t = np.arange(samples) / sr
    tau = np.maximum(t - delay, 0.0)
    pad = int(.05 * sr)
    top = 8.5 * f1
    bands = [(.7 * f1, min(top, .4 * sr), True)]
    centre = 1000.0 * 2.0 ** np.arange(-1, 5)
    bands += [(c / math.sqrt(2), min(c * math.sqrt(2), .45 * sr), False) for c in centre
              if c / math.sqrt(2) >= top and c / math.sqrt(2) < .4 * sr]
    pre = x[max(0, start - int(.05 * sr)):start]
    frames = np.flatnonzero((t >= delay - .002) & (t <= delay + seconds))[::max(1, int(.00025 * sr))]
    measured = []
    for lo, hi, both in bands:
        sos = signal.butter(4, [lo, hi], 'bandpass', fs=sr, output='sos')

        def power(y, sos=sos):
            y = signal.sosfiltfilt(sos, np.vstack([np.zeros((pad, 2)), y, np.zeros((pad, 2))]), axis=0)
            p = np.mean(np.abs(signal.hilbert(y, axis=0)) ** 2, axis=1)[pad:pad + len(y) - 2 * pad]
            return ndimage.uniform_filter1d(p, max(1, int(.0005 * sr)))
        recorded = power(x[start:start + samples])
        floor = float(recorded.max()) * 1e-5
        if len(pre) >= int(.01 * sr):
            floor = max(floor, float(np.median(power(pre))))
        measured.append((power, 10 * np.log10(recorded[frames] + floor), floor, both))
    grid = np.geomspace(2e-4, .03, 37)
    errors = []
    for candidate in grid:
        envelope = 1 - np.exp(-tau[None, :] / np.maximum(rises, candidate)[:, None])
        model = np.einsum('ks,ksc->sc', envelope, waves)
        error = 0.0
        for power, recorded_db, floor, both in measured:
            e = 10 * np.log10(power(model)[frames] + floor) - recorded_db
            error += float(np.mean((e if both else np.maximum(e, 0.0)) ** 2))
        errors.append(error / len(measured))
    errors = np.array(errors)
    return float(grid[np.flatnonzero(errors <= 1.01 * errors.min())[0]])


def header_waves(data, i, sr, samples, contact):
    """Each partial and extra component of an anchor's generated data as the
    engine plays it at layer i, both channels from `contact` seconds into
    `samples`, without its rise; and each one's own rise (s) there, none for a
    component beside the series, which starts at contact."""
    import math
    import numpy as np
    import piano_analysis as pa
    t = np.arange(samples) / sr
    tau = np.maximum(t - contact, 0.0)
    on = t >= contact
    x = (data['velocities'][i] - 64) / 64
    waves, rises = [], []
    for p in data['partials'] + data['extras']:
        hz = pa.stiff(data['f1'], data['B'], p['order']) * 2 ** (p['cents'] / 1200)
        wave = np.zeros((samples, 2))
        for lane in p['lanes']:
            g = 10 ** (lane['level_db'][i] / 20) * np.exp(1j * lane['phase'][i])
            z = np.exp((-lane['rate'] + 2j * math.pi * (hz + lane['offset_hz'])) * tau) * on
            wave[:, 0] += np.real(g * lane['left'] * z)
            wave[:, 1] += np.real(g * lane['right'] * z)
        waves.append(wave)
        rises.append(p['rise_seconds'] * math.exp(p['rise_slope'] * x) if 'rise_seconds' in p else 0.0)
    return np.array(waves), np.array(rises)


def anchor_data(result, halo_hz, wav):
    """The engine's data for one calibrated anchor; `halo_hz` are the
    undamped strings' frequencies (halo_pitches) and `wav` the folder of the
    model's recordings."""
    import math
    import numpy as np
    from scipy import stats
    import piano_analysis as pa
    velocities = np.array([L['velocity'] for L in result['layers']], float)
    delays = np.array([L['delay'] for L in result['layers']])
    peaks = np.array([L['peak_db'] for L in result['layers']])                     # layers x orders
    snr = peaks - np.array([L['floor_db'] for L in result['layers']])
    orders, freqs = result['orders'], result['freqs']
    f1, B = series(result)
    shaped = []
    for k, (n, fit) in enumerate(zip(orders, result['fits'])):
        if fit is None:
            continue
        layers = [i for i, a in enumerate(fit['amplitudes']) if a is not None]
        if len(layers) < 3:
            continue
        u, mu, explained = lane_shapes([fit['amplitudes'][i] for i in layers])
        # The fit's carrier runs from the detected onset; the engine's from contact.
        mu *= np.exp(2j * math.pi * freqs[k] * delays[layers])[:, None]
        shaped.append((k, n, fit, layers, u, mu, explained))
    phases = np.zeros((len(shaped), len(velocities)))
    weights = np.zeros_like(phases)
    for row, (k, _, _, layers, _, mu, _) in enumerate(shaped):
        strongest = int(np.argmax(np.sum(np.abs(mu) ** 2, axis=0)))
        phases[row, layers] = np.angle(mu[:, strongest])
        weights[row, layers] = np.abs(mu[:, strongest]) * np.clip((snr[layers, k] - 15) / 15, .02, 1)
    weights /= np.maximum(weights.max(axis=0, keepdims=True), 1e-30)
    # The pattern repeats every period of the fundamental, so the search stays
    # within half a period of the detected onset (and 3 ms in the bass, whose
    # slow onsets are detected late by up to that much).
    shifts, agreement = layer_alignment(phases, weights, np.array([freqs[k] for k, *_ in shaped]),
                                        int(np.argmax(velocities)), min(.003, .5 / f1))
    def lanes_of(theta, u, mu, layers, snr_db, peak_db):
        """Each lane's rate, offset, pickup and smoothed level and phase per
        layer; `peak_db` is the component's recorded peak in every layer."""
        count = mu.shape[1]
        lanes = []
        for j in range(count):
            # A lane counts at a layer in proportion to the component's signal
            # to noise there and to the lane's share of it.
            share = np.abs(mu[:, j]) / np.max(np.abs(mu), axis=1)
            w = np.full(len(velocities), 1e-3)
            w[layers] = np.clip((snr_db - 15) / 15, .02, 1) * np.clip(share, .05, 1)
            measured = 20 * np.log10(np.maximum(np.abs(mu[:, j]), 1e-10))
            phase = np.exp(1j * np.angle(mu[:, j]))
            full_level = np.interp(velocities, velocities[layers], measured)
            full_phase = (np.interp(velocities, velocities[layers], phase.real)
                          + 1j * np.interp(velocities, velocities[layers], phase.imag))
            smooth_phase = (smooth_levels(velocities, full_phase.real, w, .5)
                            + 1j * smooth_levels(velocities, full_phase.imag, w, .5))
            lanes.append({'rate': math.exp(theta[j]), 'offset_hz': float(theta[count + j]),
                          'left': float(u[0, j].real), 'right': complex(u[1, j]),
                          'level_db': smooth_levels(velocities, full_level, w),
                          'phase': np.angle(smooth_phase)})
        # A layer where the component does not stand clear of its floor only
        # bounds it: no louder there than its recorded peak, carried into the
        # lanes' scale by the median difference over the layers that measured
        # it. Held at the nearest measured layer's level instead, the softest
        # layers took the first loud one's treble: at the upright's softest
        # layer, C2's partials above 2.4 kHz sounded 30 to 45 dB over a
        # recording that holds none of them.
        total = 10 * np.log10(np.sum(np.abs(mu) ** 2, axis=1))
        bound = peak_db + np.median(total - peak_db[layers])
        played = 10 * np.log10(np.sum([10 ** (lane['level_db'] / 10) for lane in lanes], axis=0))
        hidden = np.setdiff1d(np.arange(len(velocities)), layers)
        for lane in lanes:
            lane['level_db'][hidden] += np.minimum(0.0, bound[hidden] - played[hidden])
        return lanes

    partials = []
    for row, (k, n, fit, layers, u, mu, explained) in enumerate(shaped):
        mu = mu * np.exp(-2j * math.pi * freqs[k] * shifts[layers])[:, None]
        theta = fit['theta']
        lanes = lanes_of(theta, u, mu, layers, snr[layers, k], peaks[:, k])
        peak = max(float(np.max(lane['level_db'])) for lane in lanes)
        if peak < -110:
            continue
        lanes.sort(key=lambda lane: -lane['rate'])
        partials.append({'order': int(n), 'cents': float(1200 * math.log2(freqs[k] / pa.stiff(f1, B, n))),
                         'rise_seconds': math.exp(theta[2 * pa.LANES]), 'rise_slope': float(theta[2 * pa.LANES + 1]),
                         'lanes': lanes, 'explained': explained, 'phase_agreement': float(agreement[row]),
                         'error': float(np.median([e for e in fit['relative_error'] if e is not None]))})
    # The components beside the series, in the same frame. One within
    # HALO_UNISON of another key's undamped string, and every peak the
    # strings' own search finds, is left to halo_data, which measures the
    # strings across the recorded pitches. The others, the struck key's own
    # unison strings among them, sit at the order of the series nearest them,
    # cents from there.
    extras = []
    orders_all = np.arange(1, 400)
    ladder = pa.stiff(f1, B, orders_all)
    extra_peaks = np.array([L['extra_peak_db'] for L in result['layers']]) \
        if len(result.get('extra_freqs', [])) else None
    extra_snr = extra_peaks - np.array([L['extra_floor_db'] for L in result['layers']]) \
        if extra_peaks is not None else None
    for k, (f, fit) in enumerate(zip(result['extra_freqs'], result['extra_fits'])):
        if fit is None or result['extra_halo'][k] or min(
                abs(1200 * math.log2(f / hz)) for key, hz in halo_hz.items() if key != result['note']) <= HALO_UNISON:
            continue
        layers = [i for i, a in enumerate(fit['amplitudes']) if a is not None]
        if len(layers) < 3:
            continue
        u, mu, _ = lane_shapes([fit['amplitudes'][i] for i in layers])
        mu = mu * np.exp(2j * math.pi * f * (delays[layers] - shifts[layers]))[:, None]
        lanes = sorted(lanes_of(fit['theta'], u, mu, layers, extra_snr[layers, k], extra_peaks[:, k]),
                       key=lambda lane: -lane['rate'])
        peak = max(float(np.max(lane['level_db'])) for lane in lanes)
        if peak < -110:
            continue
        n = int(orders_all[np.argmin(np.abs(ladder - f))])
        extras.append({'lanes': lanes, 'error': float(np.median([e for e in fit['relative_error'] if e is not None])),
                       'order': n, 'cents': float(1200 * math.log2(f / ladder[n - 1]))})
    data = {'note': result['note'], 'f1': f1, 'B': B, 'velocities': velocities.tolist(), 'partials': partials,
            'extras': extras, 'layer_shift_ms': [round(1000 * d, 3) for d in shifts]}
    # The onset rise of every layer as the engine plays the data. Layer to
    # layer it scatters by a factor of several, more than any trend, so the
    # anchor keeps a straight line through it in log time over velocity:
    # Theil-Sen, which a few outlying layers cannot tilt, held within the
    # range the layers measure. Through the upright's five layers the line
    # ran past every one of them at the ends: at A#6, 8.2 ms at the softest
    # layer, where none measured over 3.7 ms.
    sr, onsets = result['sr'], []
    for i, (case, L) in enumerate(zip(result['cases'], result['layers'])):
        _, x = pa.load(wav / f'{case}.wav')
        contact = L['delay'] - shifts[i]
        waves, rises = header_waves(data, i, sr, int((contact + .05) * sr), contact)
        onsets.append(onset_rise(x, sr, L['start'], contact, result['f1'], waves, rises))
    slope, intercept = stats.theilslopes(np.log(onsets), velocities)[:2]
    line = np.clip(intercept + slope * velocities, math.log(min(onsets)), math.log(max(onsets)))
    data.update({'onset_rise': np.exp(line), 'layer_onset_rise_ms': [round(1000 * r, 3) for r in onsets]})
    return data


# The strings from F6 up have no dampers, so every strike sets all of them
# ringing through the bridge, and they ring on after the key is let go: a
# second after contact they sound 40 to 80 dB under the note. Each string is
# measured as a tone at one frequency (halo_pitches) through 0.5 s Hann
# windows every 0.25 s from 1 to 2 s after contact (HALO_TIMES): the largest
# amplitude within 1 Hz of it, both channels' mean power. It rings clear
# where that stands HALO_CLEAR over the median from 4 to 20 Hz either side.
# Later the strings fall more slowly, but by then the room's noise hides most
# of them. Where a partial of the struck key's series lies within HALO_APART
# of a string, the tone there is that partial's; below F#3 (HALO_LOWEST) the
# tone at every string's pitch is the struck key's own dense series.
HALO_TIMES = (1.0, 1.25, 1.5, 1.75, 2.0)   # s after contact
HALO_CLEAR = 10.0                          # dB
HALO_APART = 10.0                          # Hz
HALO_LOWEST = 54
# Where the noise hides a string the recording only bounds it: its level is
# taken this far (dB) under the tone there.
HALO_HIDDEN = 10.0


def halo_spectra(result, i, windows, wav):
    """Layer i's stereo spectrum (the recording's units, zero-padded 8 times)
    through each Hann window of `windows` (its centre in seconds after string
    contact, its length in seconds), with its frequencies; (None, None) for a
    window past the recording's end."""
    import numpy as np
    import piano_analysis as pa
    L = result['layers'][i]
    sr, x = pa.load(wav / f'{result["cases"][i]}.wav')
    contact = L['start'] + L['delay'] * sr
    spectra = []
    for centre, seconds in windows:
        n = int(seconds * sr)
        start = int(round(contact + centre * sr)) - n // 2
        if start + n > len(x):
            spectra.append((None, None))
            continue
        w = np.hanning(n)
        spectra.append((np.fft.rfftfreq(8 * n, 1 / sr),
                        np.fft.rfft(x[start:start + n] * w[:, None], 8 * n, axis=0) * 2 / np.sum(w)))
    return spectra


def halo_tone(f, z, hz):
    """At `hz` in a stereo spectrum `z` (frequencies `f`): the tone (dB, both
    channels' mean power, the largest within 1 Hz), how far it stands over the
    median from 4 to 20 Hz either side (dB), and both channels there."""
    import numpy as np
    d = np.abs(f - hz)
    power = np.mean(np.abs(z) ** 2, axis=1)
    near = np.flatnonzero(d <= 1)
    k = near[np.argmax(power[near])]
    noise = np.median(power[(d >= 4) & (d <= 20)])
    return 10 * np.log10(power[k] + 1e-30), 10 * np.log10(power[k] / (noise + 1e-30)), z[k]


def halo_pitches(results, strings, wav):
    """Each undamped string's frequency (Hz), by key: through a Hann window
    from 1 to 2 s after contact in the train recordings struck from C6 up,
    the strongest peak within 30 cents of the pitch the engine gives the key
    (`strings`), where it lies HALO_APART or more from every partial of the
    struck key's series and rings clear 1 s after contact; the median over
    those recordings. A string that rings clear in none keeps the pitch the
    engine gives its key, as the upright's A#7 and B7 do."""
    import numpy as np
    import piano_analysis as pa
    found = {key: [] for key in UNDAMPED}
    for r in results:
        if r['note'] < 84:
            continue
        ladder = pa.stiff(*series(r), np.arange(1, 400))
        for i in range(len(r['layers'])):
            (f, z), (g, y) = halo_spectra(r, i, [(1.5, 1.0), (1.0, .5)], wav)
            power = np.mean(np.abs(z) ** 2, axis=1)
            for key in UNDAMPED:
                span = (f >= strings[key] * 2 ** (-30 / 1200)) & (f <= strings[key] * 2 ** (30 / 1200))
                hz = float(f[span][np.argmax(power[span])])
                if key != r['note'] and np.min(np.abs(ladder - hz)) >= HALO_APART and halo_tone(g, y, hz)[1] >= HALO_CLEAR:
                    found[key].append(hz)
    return {key: float(np.median(hzs)) if hzs else strings[key] for key, hzs in found.items()}


def halo_data(results, strings, hz, wav):
    """The undamped strings every strike sets ringing (see HALO_TIMES), at
    their frequencies `hz` (halo_pitches) by key; `strings` are the pitches
    the engine gives their keys.

    Each string decays at one rate and is heard through one stereo pickup.
    The pickup: the median right-over-left level and the mean phase between
    the channels over every window where the string rings clear; a string
    that never does is heard through the pickup of the nearest string that
    does. The rate: the string's fall from 1 to 2 s where it
    rings 20 dB clear at the start and 6 dB at the end, the median over the
    recordings, drawn towards the median of all the strings' by ten
    recordings' worth (most ring clear in dozens, a few in under five).
    Brought back to contact at that rate, its level in a layer is the mean
    over the windows where it rings clear, if two or more; otherwise the
    recording only bounds it, at the 1 s window's tone. One slope across
    velocity (dB per 64) serves every string and pitch, pooled within each
    pitch and string that rings clear in three layers or more. A recorded
    pitch's level for a string at velocity 64 is the mean over the layers
    where it rings clear, if two or more do; otherwise HALO_HIDDEN under the
    median bound. A string that the struck key's series or its own key
    covers, and every string below HALO_LOWEST, takes the levels of the
    recorded pitches around it, interpolated by key and held beyond them."""
    import math
    import numpy as np
    import piano_analysis as pa
    db = 20 / math.log(10)
    t = np.array(HALO_TIMES)
    keys = list(UNDAMPED)
    measured = []
    for a, r in enumerate(results):
        if r['note'] < HALO_LOWEST:
            continue
        ladder = pa.stiff(*series(r), np.arange(1, 400))
        shape = (len(r['layers']), len(keys), len(t))
        m = {'anchor': a, 'velocities': np.array([L['velocity'] for L in r['layers']], float),
             'apart': np.array([key != r['note'] and np.min(np.abs(ladder - hz[key])) >= HALO_APART for key in keys]),
             'tone': np.full(shape, np.nan), 'margin': np.full(shape, np.nan),
             'channels': np.zeros(shape + (2,), complex)}
        for i in range(len(r['layers'])):
            for k, (f, z) in enumerate(halo_spectra(r, i, [(c, .5) for c in t], wav)):
                if z is None:
                    continue
                for j, key in enumerate(keys):
                    m['tone'][i, j, k], m['margin'][i, j, k], m['channels'][i, j, k] = halo_tone(f, z, hz[key])
        m['clear'] = (m['margin'] >= HALO_CLEAR) & m['apart'][None, :, None]
        measured.append(m)
    pickups = []
    for j in range(len(keys)):
        pairs = np.concatenate([m['channels'][:, j][m['clear'][:, j]] for m in measured])
        if not len(pairs):
            pickups.append(None)
            continue
        balance = float(np.median(20 * np.log10(np.abs(pairs[:, 1]) / np.abs(pairs[:, 0]))))
        phase = float(np.angle(np.sum(pairs[:, 1] * np.conj(pairs[:, 0]) / np.abs(pairs[:, 1] * pairs[:, 0]))))
        left = math.sqrt(2 / (1 + 10 ** (balance / 10)))
        pickups.append((left, left * 10 ** (balance / 20) * complex(math.cos(phase), math.sin(phase))))
    heard = [j for j, pickup in enumerate(pickups) if pickup is not None]
    pickups = [pickups[min(heard, key=lambda h: abs(h - j))] for j in range(len(keys))]
    falls = [np.concatenate([(m['tone'][:, j, 0] - m['tone'][:, j, -1])
                             [(m['margin'][:, j, 0] >= 20) & (m['margin'][:, j, -1] >= 6)]
                             for m in measured if m['apart'][j]]) for j in range(len(keys))]
    pooled = float(np.median([np.median(x) for x in falls if len(x)]))
    rates = np.array([(len(x) * np.median(x) + 10 * pooled) / (len(x) + 10) if len(x) else pooled
                      for x in falls]) / db / (t[-1] - t[0])
    xs, ys = [], []
    for m in measured:
        back = m['tone'] + db * rates[None, :, None] * t
        m['rang'] = m['clear'].sum(axis=2) >= 2
        m['level'] = np.where(m['rang'], np.sum(np.where(m['clear'], back, 0), axis=2)
                              / np.maximum(m['clear'].sum(axis=2), 1), back[:, :, 0])
        for j in np.flatnonzero(m['apart']):
            rang = m['rang'][:, j]
            if rang.sum() >= 3:
                xs += list((m['velocities'][rang] - m['velocities'][rang].mean()) / 64)
                ys += list(m['level'][rang, j] - m['level'][rang, j].mean())
    slope = float(np.dot(xs, ys) / np.dot(xs, xs))
    levels = np.full((len(results), len(keys)), np.nan)
    kinds = [['filled'] * len(keys) for _ in results]
    for m in measured:
        at64 = m['level'] - slope * (m['velocities'][:, None] - 64) / 64
        for j in np.flatnonzero(m['apart']):
            rang = m['rang'][:, j]
            if rang.sum() >= 2:
                levels[m['anchor'], j], kinds[m['anchor']][j] = np.mean(at64[rang, j]), 'clear'
            else:
                levels[m['anchor'], j], kinds[m['anchor']][j] = np.median(at64[~rang, j]) - HALO_HIDDEN, 'under'
    notes = np.array([r['note'] for r in results], float)
    for j in range(len(keys)):
        known = np.isfinite(levels[:, j])
        levels[~known, j] = np.interp(notes[~known], notes[known], levels[known, j])
    return {'keys': keys, 'hz': [hz[key] for key in keys],
            'cents': [1200 * math.log2(hz[key] / strings[key]) for key in keys], 'rates': rates.tolist(),
            'rate_layers': [len(x) for x in falls], 'pickups': pickups, 'slope': slope, 'levels': levels,
            'kinds': kinds}


# The soundboard and case. Every strike also knocks the instrument's body,
# whose modes ring under the treble's fundamentals where no string sounds:
# there the recordings measure them directly. The model is one bank of modes
# shared by every key, each key exciting each mode with its own level and
# phase, and each mode heard through one stereo pickup.
BODY_LOW, BODY_TOP = 25.0, 1000.0       # Hz: the band the body modes are measured in
BODY_SKIP, BODY_SECONDS = .02, .6       # s after contact: past the partials' onset, to the residual's end
BODY_RATE = 4000                        # Hz: the measurement's sample rate
BODY_HUM = [50.0 * k for k in range(1, 11)]  # the room's mains lines, fitted and discarded


def body_signal(result, i, contact):
    """Layer i's residual with the partials removed, BODY_LOW to BODY_TOP, from
    BODY_SKIP to BODY_SECONDS after string contact, at BODY_RATE."""
    from scipy import signal
    sr = result['sr']
    residual = result['layers'][i]['residual'].astype(float)
    sos = signal.butter(6, [BODY_LOW, BODY_TOP], 'bandpass', fs=sr, output='sos')
    y = signal.sosfiltfilt(sos, residual, axis=0)
    y = y[int((contact + BODY_SKIP) * sr):int((contact + BODY_SECONDS) * sr)]
    return signal.resample_poly(y, BODY_RATE, sr, axis=0)


def body_modes(results, contacts):
    """The shared modes (Hz) and their decay rates (1/s).

    Every anchor whose fundamental lies above 375 Hz contributes its layers
    below 0.8 f1, where no partial sounds. Modes are the peaks (2 dB
    prominence, 3.5 Hz apart) of the mean of those spectra, each normalised
    over its band, away from the mains lines; each mode's decay is the
    energy-weighted median slope of its +-3 Hz envelope from 35 to 400 ms
    over the layers whose band holds it.
    """
    import numpy as np
    from scipy import signal, stats
    signals = []
    for result, contact in zip(results, contacts):
        top = min(BODY_TOP, .8 * result['f1'])
        if top < 300:
            continue
        sos = signal.butter(6, [BODY_LOW, top], 'bandpass', fs=BODY_RATE, output='sos')
        for i in range(len(result['layers'])):
            signals.append((signal.sosfiltfilt(sos, body_signal(result, i, contact[i]), axis=0), top))
    n = min(len(y) for y, _ in signals)
    f = np.fft.rfftfreq(8 * n, 1 / BODY_RATE)
    total, count = np.zeros(len(f)), np.zeros(len(f))
    for y, top in signals:
        power = np.sum(np.abs(np.fft.rfft(y[:n] * np.hanning(n)[:, None], 8 * n, axis=0)) ** 2, axis=1)
        band = (f > BODY_LOW) & (f < top)
        total[band] += power[band] / power[band].mean()
        count[band] += 1
    band = (f > BODY_LOW) & (f < BODY_TOP) & (count >= 3)
    level = 10 * np.log10(total[band] / count[band] + 1e-30)
    peaks, _ = signal.find_peaks(level, prominence=2.0, distance=int(3.5 / (f[1] - f[0])))
    hz = f[band][peaks]
    hz = hz[np.min(np.abs(hz[:, None] - np.array(BODY_HUM)[None]), axis=1) > 1.5]
    t = np.arange(n) / BODY_RATE + BODY_SKIP
    late = (t >= .035) & (t <= .4)
    modes = []
    for fm in hz:
        sos = signal.butter(2, [max(BODY_LOW, fm - 3), fm + 3], 'bandpass', fs=BODY_RATE, output='sos')
        slopes, weights = [], []
        for y, top in signals:
            if fm > .95 * top:
                continue
            env = np.sum(np.abs(signal.hilbert(signal.sosfiltfilt(sos, y[:n], axis=0), axis=0)) ** 2, axis=1)
            slopes.append(stats.theilslopes(10 * np.log10(env[late][::8] + 1e-30), t[late][::8])[0])
            weights.append(env[late].mean())
        if len(slopes) < 6:
            continue
        order = np.argsort(slopes)
        cumulative = np.cumsum(np.array(weights)[order]) / np.sum(weights)
        modes.append((float(fm), max(.5, -float(np.array(slopes)[order][np.searchsorted(cumulative, .5)]) / 8.686)))
    return np.array([m[0] for m in modes]), np.array([m[1] for m in modes])


def body_amplitudes(result, contact, hz, rates, ridge=1e-3):
    """Each layer's complex amplitude per mode and channel at string contact
    (layers x modes x channels), by least squares with the modes fixed; NaN
    for modes within 4 Hz of one of the anchor's partials, whose misfit would
    pass for them. Also each layer's fraction of the band's energy explained."""
    import math
    import numpy as np
    usable = np.min(np.abs(hz[:, None] - np.asarray(result['freqs'])[None]), axis=1) > 4.0
    f, rate = hz[usable], rates[usable]
    out, explained = [], []
    for i in range(len(result['layers'])):
        y = body_signal(result, i, contact[i])
        t = BODY_SKIP + np.arange(len(y)) / BODY_RATE
        decay, phase = np.exp(-np.outer(t, rate)), 2 * math.pi * np.outer(t, f)
        hum = 2 * math.pi * np.outer(t, BODY_HUM)
        A = np.hstack([decay * np.cos(phase), decay * np.sin(phase), np.cos(hum), np.sin(hum)])
        gram = A.T @ A
        c = np.linalg.solve(gram + ridge * np.trace(gram) / len(gram) * np.eye(len(gram)), A.T @ y)
        z = np.full((len(hz), 2), np.nan + 0j)
        z[usable] = c[:len(f)] - 1j * c[len(f):2 * len(f)]      # Re(z e^(i w t)) = a cos - b sin
        out.append(z)
        explained.append(float(1 - np.sum((y - A @ c) ** 2) / np.sum(y ** 2)))
    return np.array(out), np.array(explained)


def body_rise(result, contact, hz, rates, amplitudes, seconds=.03):
    """Each layer's body onset rise (s): the rise 1 - e^(-t/rise) under which
    the fitted modes' power below 0.8 f1 best builds up as the residual's
    does, from 2 ms before contact to `seconds` after, in dB at 0.25 ms steps
    with 0.5 ms smoothing above the floor before the onset where a take has
    10 ms before it (as onset_rise measures it), else 50 dB under the peak."""
    import math
    import numpy as np
    from scipy import ndimage, signal
    sr = result['sr']
    top = min(BODY_TOP, .8 * result['f1'])
    sos = signal.butter(6, [BODY_LOW, top], 'bandpass', fs=sr, output='sos')
    pad = int(.05 * sr)

    def power(y):
        y = signal.sosfiltfilt(sos, np.vstack([np.zeros((pad, 2)), y, np.zeros((pad, 2))]), axis=0)
        p = np.mean(np.abs(signal.hilbert(y, axis=0)) ** 2, axis=1)[pad:pad + len(y) - 2 * pad]
        return ndimage.uniform_filter1d(p, max(1, int(.0005 * sr)))
    grid = np.geomspace(1e-4, .02, 41)
    rises = []
    for i, L in enumerate(result['layers']):
        pre = L['pre_onset'].astype(float)
        samples = len(pre) + int((contact[i] + seconds + .02) * sr)
        x = np.vstack([pre, L['residual'].astype(float)])[:samples]
        t = (np.arange(samples) - len(pre)) / sr
        tau = np.maximum(t - contact[i], 0.0)
        known = np.all(np.isfinite(amplitudes[i]), axis=1)
        z = np.exp(np.outer(tau, -rates[known] + 2j * math.pi * hz[known])) * (t >= contact[i])[:, None]
        model = np.real(z @ amplitudes[i][known])
        recorded = power(x)
        floor = float(recorded.max()) * 1e-5
        if len(pre) >= int(.01 * sr):
            floor = max(floor, float(np.median(recorded[:len(pre) - int(.005 * sr)])))
        frames = np.flatnonzero((t >= contact[i] - .002) & (t <= contact[i] + seconds))[::max(1, int(.00025 * sr))]
        target = 10 * np.log10(recorded[frames] + floor)
        errors = [float(np.mean((10 * np.log10(power(model * (1 - np.exp(-tau / r))[:, None])[frames] + floor)
                                 - target) ** 2)) for r in grid]
        rises.append(float(grid[int(np.argmin(errors))]))
    return rises


def body_data(results, datas, grid, layer_level):
    """The body bank and each anchor's excitation of it (see BODY_LOW).

    A knock's level (dB) is a line in the level its layer plays at
    (`layer_level` over the velocities `grid`, 0 dB at the loudest), weighted
    by the knock's amplitude: it grows with the strike as the strings do, a
    median 0.93 dB per dB on the grand and 0.96 on the upright. A line in
    velocity weighted by power, where the knocks' levels curve down toward
    the softest layers, played the softest layer's knock a median 5.9 dB
    (grand) and 5.0 dB (upright) over its recordings, summed over the modes;
    this one plays it 1.1 and 0.8 dB over. Weighting every layer alike lets
    the soft layers pull the loudest layer's third-octave levels a median
    2.0 dB off on both pianos, against 1.3 (grand) and 0.7 (upright) here. A
    quadratic in the level, fitted without a layer, predicted it within
    0.1 dB of this line inside the recorded layers and far worse past them."""
    import math
    import numpy as np
    contacts = [np.array([L['delay'] for L in r['layers']]) - np.array(d['layer_shift_ms']) / 1000
                for r, d in zip(results, datas)]
    hz, rates = body_modes(results, contacts)
    amplitudes, explained = zip(*(body_amplitudes(r, c, hz, rates) for r, c in zip(results, contacts)))
    # The body's rise, where its band below the fundamental is clear.
    rises = {r['note']: body_rise(r, c, hz, rates, a) for r, c, a in zip(results, contacts, amplitudes)
             if .8 * r['f1'] >= 300}
    # One pickup per mode: the dominant stereo shape over every layer of every key.
    shapes, kept = [], []
    for m in range(len(hz)):
        Z = np.concatenate([a[:, m] for a in amplitudes])
        Z = Z[np.all(np.isfinite(Z), axis=1)]
        u, s, _ = np.linalg.svd(Z.T, full_matrices=False)
        shape = u[:, 0] * np.exp(-1j * np.angle(u[0, 0])) * math.sqrt(2)
        shapes.append(shape)
        kept.append(float(s[0] ** 2 / np.sum(s ** 2)))
    anchors = []
    for r, a in zip(results, amplitudes):
        x = np.interp([L['velocity'] for L in r['layers']], grid, layer_level)
        knocks = []
        for m, shape in enumerate(shapes):
            level = np.conj(shape) @ a[:, m].T / 2                    # complex level per layer
            if not np.all(np.isfinite(level)):
                knocks.append(None)
                continue
            db = 20 * np.log10(np.abs(level) + 1e-12)
            root = np.sqrt(np.abs(level))                             # rows weighted by amplitude
            intercept, slope = np.linalg.lstsq(np.c_[np.ones_like(x), x] * root[:, None], db * root, rcond=None)[0]
            # One phase, the louder layers' (theirs stands clearest of the noise).
            weight = np.abs(level) ** 2
            resultant = np.sum(level / np.maximum(np.abs(level), 1e-30) * weight)
            knocks.append({'level_db': float(intercept), 'slope_db': float(slope),
                           'phase': float(np.angle(resultant)),
                           'coherence': float(np.abs(resultant) / np.sum(weight))})
        anchors.append(knocks)
    # Modes a key's partials hide take the nearest measured keys' levels.
    notes = np.array([r['note'] for r in results], float)
    for m in range(len(hz)):
        known = [k for k, knocks in enumerate(anchors) if knocks[m] is not None]
        for k, knocks in enumerate(anchors):
            if knocks[m] is not None:
                continue
            near = min(known, key=lambda j: abs(notes[j] - notes[k]))
            values = {key: float(np.interp(notes[k], notes[known], [anchors[j][m][key] for j in known]))
                      for key in ('level_db', 'slope_db')}
            knocks[m] = values | {'phase': anchors[near][m]['phase'], 'coherence': 0.0, 'filled': True}
    return {'hz': hz, 'rates': rates, 'shapes': shapes, 'pickup_explained': kept, 'anchors': anchors,
            'explained': [list(e) for e in explained], 'layer_rises': rises,
            'rise': float(np.median([r for layer in rises.values() for r in layer]))}


# The action's knocks on the body: a key's damper landing as the key is let
# go (Salamander's rel<k>, one take per key, the anchors' own keys) and the
# sustain pedal going down and up (pedalD1, pedalU1). Their energy lies in the
# body's modes, most of it from 100 to 300 Hz; what lies from 1 to 3 kHz, 20 dB
# under it, the modes leave out. Each is fitted with the modes fixed from its
# onset, where its power over 5 ms first comes within 30 dB of its peak, under
# one rise 1 - e^(-t/rise) that every knock shares: they build up over tens of
# milliseconds, where a strike's knock takes a fraction of one. The files were
# gained up as a set, so the levels are in their own scale; the engine sets
# them against the notes as the library's SFZ does.
ACTION_SECONDS = 1.0


def action_signal(path):
    """A knock's recording from its onset for ACTION_SECONDS, BODY_LOW to
    BODY_TOP, at BODY_RATE."""
    import numpy as np
    from scipy import ndimage, signal
    import piano_analysis as pa
    sr, x = pa.load(path)
    sos = signal.butter(6, [BODY_LOW, BODY_TOP], 'bandpass', fs=sr, output='sos')
    y = signal.sosfiltfilt(sos, x, axis=0)
    p = ndimage.uniform_filter1d(np.mean(y * y, axis=1), int(.005 * sr))
    peak = int(np.argmax(p[:int(1.0 * sr)]))
    onset = int(np.flatnonzero(p >= p[peak] * 1e-3)[0])
    return signal.resample_poly(y[onset:onset + int(ACTION_SECONDS * sr)], BODY_RATE, sr, axis=0)


def action_fit(y, hz, rates, shapes, rise, ridge=1e-3):
    """One knock under `rise`: per mode its complex level on the mode's pickup
    at the onset, and the fraction of the knock's energy left unexplained."""
    import math
    import numpy as np
    t = np.arange(len(y)) / BODY_RATE
    envelope = (1 - np.exp(-t / rise))[:, None] * np.exp(-np.outer(t, rates))
    phase, hum = 2 * math.pi * np.outer(t, hz), 2 * math.pi * np.outer(t, BODY_HUM)
    A = np.hstack([envelope * np.cos(phase), envelope * np.sin(phase), np.cos(hum), np.sin(hum)])
    gram = A.T @ A
    c = np.linalg.solve(gram + ridge * np.trace(gram) / len(gram) * np.eye(len(gram)), A.T @ y)
    z = c[:len(hz)] - 1j * c[len(hz):2 * len(hz)]                 # modes x channels
    levels = np.array([np.conj(shape) @ zm / 2 for shape, zm in zip(shapes, z)])
    return levels, float(np.sum((y - A @ c) ** 2) / np.sum(y ** 2))


def action_data(model, notes, hz, rates, shapes):
    """The anchors' key releases and, where the corpus records it, the pedal's
    down and up as knocks (MODELS): their shared rise (s), the one under which
    the modes leave least of them unexplained, and per knock and mode the
    level (dB) and phase at the onset."""
    import numpy as np
    names = [model['release'].format(key=note - 20, note=note) for note in notes] + list(model['pedal'])
    roles = json.loads(model['split'].read_text())['cases']
    if any(roles.get(name) != 'train' for name in names):
        raise SystemExit('the action knocks are fitted on train recordings only')
    signals = [action_signal(model['wav'] / f'{name}.wav') for name in names]
    grid = np.geomspace(.005, .3, 25)
    unexplained = [float(np.mean([action_fit(y, hz, rates, shapes, rise)[1] for y in signals])) for rise in grid]
    rise = float(grid[int(np.argmin(unexplained))])
    fits = [action_fit(y, hz, rates, shapes, rise) for y in signals]
    knocks = [[{'level_db': float(20 * np.log10(abs(level) + 1e-12)), 'phase': float(np.angle(level))}
               for level in levels] for levels, _ in fits]
    out = {'rise': rise, 'releases': knocks[:len(notes)], 'cases': names,
           'unexplained': [round(u, 3) for _, u in fits]}
    if model['pedal']:
        out.update({'pedal_down': knocks[len(notes)], 'pedal_up': knocks[len(notes) + 1]})
    return out


# What a piano's dampers leave ringing, from its key-release takes where they
# show it (MODELS 'damper'): each take is a key let go, recorded from about
# the key-up. Its partials up to the tenth are measured every 10 ms through
# the analysis window to DAMPER_SECONDS or half a second before its end, with
# its last half second as their floor; those 25 dB over the floor in the first
# 60 ms count, but not within DAMPER_HALO cents of an undamped string's first
# three partials, where the take holds that string's sympathy, which the halo
# plays.
DAMPER_SECONDS, DAMPER_HALO = 3.0, 60.0
# The takes match a note struck at velocity 85 and held about 1.5 s, so under
# the felt a partial also decays as its anchor's lanes at that velocity do
# from then on.
DAMPER_VELOCITY, DAMPER_HOLD = 85, 1.5
# The engine's damper (KeyraEngine.cpp, boundary() and setDamper()): it moves
# toward the strings with an 18 ms time constant, its contact is
# ((d - .08) / .92)^2.5, and the felt takes 24 + 1.4 sqrt(f) + .001 f (1/s at
# full contact). The forward model samples envelopes at DAMPER_RATE.
DAMPER_SMOOTH, DAMPER_REST, DAMPER_RATE = .018, .08, 4000
DAMPER_SHIFTS = [-.06 + .005 * k for k in range(93)]           # key-up, s into a take


def felt_loss(hz):
    return 24 + 1.4 * hz ** .5 + .001 * hz


def felt_curves(f1, times, rates, sr):
    """How the analysis window sees a partial whose amplitude falls as
    e^(-rate C) from the key-up, C the time integral of the damper's contact,
    the take silent before its first sample: dB re before the key-up at the
    take's `times`, per key-up of DAMPER_SHIFTS and per rate (1/s)."""
    import numpy as np
    from scipy import signal
    import piano_analysis as pa
    w = pa.blackman_harris(pa.window_length(f1, sr))
    w = np.add.reduceat(w, np.arange(0, len(w), sr // DAMPER_RATE))
    half = len(w) // 2
    tau = np.arange(0, times[-1] + .05 + half / DAMPER_RATE, 1 / DAMPER_RATE)
    out = np.empty((len(DAMPER_SHIFTS), len(rates), len(times)))
    for i, shift in enumerate(DAMPER_SHIFTS):
        after = np.maximum(tau - shift, 0)
        d = 1 - np.exp(-after / DAMPER_SMOOTH)
        c = np.maximum(0, (d - DAMPER_REST) / (1 - DAMPER_REST)) ** 2.5
        C = np.concatenate([[0], np.cumsum((c[1:] + c[:-1]) / 2) / DAMPER_RATE])
        a = np.exp(-np.outer(rates, C))
        pad = np.zeros((len(rates), half))
        m = signal.fftconvolve(np.hstack([pad, a, pad]), w[None, ::-1], mode='valid', axes=1)
        idx = np.round(np.asarray(times) * DAMPER_RATE).astype(int)
        out[i] = 20 * np.log10(np.abs(m[:, idx]) / w.sum() + 1e-12)
    return out


def damper_data(model, results, halo_hz):
    """The law of measured::Damper fitted to the train key-release takes:
    per partial the power (1 - r) e^(-2 F C) + r e^(-2 S C) under its lanes'
    own decay, F the felt loss, r and S the law (dB and ln 1/s, each linear in
    log2(f / 261.63 Hz)), seen through the analysis window with the take's
    floor added; per take a key-up time and per partial a level. Robust
    (soft L1, 2 dB) in dB over frames 6 dB over the floor."""
    import math
    import numpy as np
    from scipy import optimize, sparse
    import piano_analysis as pa
    corpus = json.loads(model['corpus'].read_text())['files']
    roles = json.loads(model['split'].read_text())['cases']
    by_note = {r['note']: r for r in results}
    halo = np.array([k * hz for hz in halo_hz.values() for k in (1, 2, 3)])
    rates = np.geomspace(.05, 600, 64)
    takes = []
    for item in corpus:
        if item['kind'] != 'key-release' or item['midi'] >= UNDAMPED.start or roles.get(item['id']) != 'train':
            continue
        result = by_note.get(item['midi'])
        if result is None:
            raise SystemExit(f'{item["id"]} has no anchor whose lanes decay under its felt')
        sr, x = pa.load(model['wav'] / f'{item["id"]}.wav')
        end = len(x) / sr
        times = np.arange(0, min(DAMPER_SECONDS, end - .55), .01)
        orders = [n for n in result['orders'] if n <= 10 and result['fits'][result['orders'].index(n)] is not None]
        hz = [float(result['freqs'][result['orders'].index(n)]) for n in orders]
        _, z = pa.envelopes(x, sr, hz, result['f1'], 0, None, times=times)
        db = 10 * np.log10(np.mean(np.abs(z) ** 2, axis=1) + 1e-30)
        _, z = pa.envelopes(x, sr, hz, result['f1'], 0, None, times=np.arange(end - .5, end - .03, .01))
        floors = 10 * np.log10(np.mean(np.abs(z) ** 2, axis=(1, 2)) + 1e-30)
        layer = int(np.argmin([abs(L['velocity'] - DAMPER_VELOCITY) for L in result['layers']]))
        curves = felt_curves(result['f1'], times, rates, sr)
        partials = []
        for n, f, p, floor in zip(orders, hz, db, floors):
            if p[times <= .06].max() < floor + 25 or np.min(np.abs(1200 * np.log2(halo / f))) < DAMPER_HALO:
                continue
            fit = result['fits'][result['orders'].index(n)]
            lanes = (len(fit['theta']) - 2) // 2
            power = (np.abs(fit['amplitudes'][layer]) ** 2).sum(axis=0)
            decay = np.exp(np.asarray(fit['theta'][:lanes]))
            own = np.array([10 * np.log10(power @ np.exp(-2 * np.outer(decay, DAMPER_HOLD - shift + times)) + 1e-300)
                            for shift in DAMPER_SHIFTS])
            partials.append({'order': n, 'hz': f, 'db': p, 'floor': float(floor), 'use': p > floor + 6, 'own': own})
        if partials:
            takes.append({'case': item['id'], 'curves': curves, 'partials': partials})
    if not takes:
        raise SystemExit('no train key-release take shows the felt')

    def at(grid, shift):
        """`grid` (per shift of DAMPER_SHIFTS) at `shift`, linear between them."""
        y = min(max((shift - DAMPER_SHIFTS[0]) / .005, 0), len(DAMPER_SHIFTS) - 1.000001)
        i = int(y)
        return grid[i] + (y - i) * (grid[i + 1] - grid[i])

    def view(curves, rate, shift):
        """The window's view at `rate`, log-linear between the grid's rates."""
        y = min(max(math.log(rate / rates[0]) / math.log(rates[1] / rates[0]), 0), len(rates) - 1.000001)
        j = int(y)
        a, b = at(curves[:, j], shift), at(curves[:, j + 1], shift)
        return a + (y - j) * (b - a)

    starts = []
    count = 4
    for take in takes:
        starts.append(count)
        count += 1 + len(take['partials'])

    def residual(theta):
        out = []
        for take, start in zip(takes, starts):
            shift = theta[start]
            for k, q in enumerate(take['partials']):
                x = math.log2(q['hz'] / 261.63)
                r = min(10 ** ((theta[0] + theta[1] * x) / 10), 1.0)
                fast = 10 ** (view(take['curves'], felt_loss(q['hz']), shift) / 10)
                slow = 10 ** (view(take['curves'], math.exp(theta[2] + theta[3] * x), shift) / 10)
                m = theta[start + 1 + k] + at(q['own'], shift) + 10 * np.log10((1 - r) * fast + r * slow + 1e-30)
                out.append((q['db'] - 10 * np.log10(10 ** (m / 10) + 10 ** (q['floor'] / 10)))[q['use']])
        return np.concatenate(out)

    theta = [-14.0, -3.0, 0.0, 0.0]
    lower, upper = [-np.inf] * 4, [np.inf] * 4
    rows = sum(int(q['use'].sum()) for take in takes for q in take['partials'])
    pattern = sparse.lil_matrix((rows, count), dtype=int)
    row = 0
    for take, start in zip(takes, starts):
        theta += [.03]
        lower += [DAMPER_SHIFTS[0]]
        upper += [DAMPER_SHIFTS[-1]]
        for k, q in enumerate(take['partials']):
            theta += [float(q['db'][:6].max() - q['own'][0][:6].max())]
            lower += [-np.inf]
            upper += [np.inf]
            used = int(q['use'].sum())
            pattern[row:row + used, [0, 1, 2, 3, start, start + 1 + k]] = 1
            row += used
    fit = optimize.least_squares(residual, theta, bounds=(lower, upper), loss='soft_l1', f_scale=2.0,
                                 jac_sparsity=pattern, x_scale='jac', max_nfev=300)
    errors = np.abs(residual(fit.x))
    out, row = [], 0
    for take, start in zip(takes, starts):
        used = sum(int(q['use'].sum()) for q in take['partials'])
        out.append({'case': take['case'], 'key_up_ms': round(1000 * float(fit.x[start]), 1),
                    'partials': [q['order'] for q in take['partials']],
                    'mean_abs_db': round(float(np.mean(errors[row:row + used])), 3)})
        row += used
    return {'law': [float(v) for v in fit.x[:4]], 'takes': out,
            'mean_abs_db': round(float(np.mean(errors)), 3)}


# Above the body modes the soundboard's response is too dense to resolve,
# and every strike leaves a broadband, decorrelated ring between the partials.
# It is measured as band power in third octaves from 1 kHz, in the residual
# the fitted partials leave, and played as band noise.
NOISE_BANDS = [1000.0 * 2 ** (k / 3) for k in range(13)]   # Hz: 1 to 16 kHz
NOISE_SILENT = -200.0                                     # dB re 1/Hz: a band no recording measures


def noise_bands(result, contact, wav, tail_floor, window=.04, hop=.002):
    """Per layer and band (layers x bands): the residual's noise density
    between the partials (dB re 1/Hz, stereo mean) at contact and its decay
    (dB/s), from a Theil-Sen line through 40 ms Hann frames 20 to 120 ms after
    contact, and the density before the onset; NaN where the band never stands
    10 dB above that floor. As the benchmark measures noise, bins within 1.5
    main-lobe half-widths (75 Hz) of the partials the recordings show are left
    out, and a band that keeps under a quarter of its bins is not measured.
    Above the highest of them a band is measured whole, as the benchmark
    measures it: excluding every partial the stiff string could have left no
    band to measure below A3, whose keys then took the treble's louder noise.
    A frame's density is the band's mean bin power, except in the bands
    centred below the struck note's fundamental, where none of its own
    partials can lie: there it is the median of the band's bin powers over
    ln 2, each channel's, then the channels' mean (a noise bin's power is
    exponential, whose median is ln 2 times its mean, and the median passes
    over the few bins a tone holds). The tones there are other strings',
    chiefly the undamped treble strings' detuned unisons, which the engine
    rings at one pitch each and a one-pitch fit leaves partly in the residual
    (B6's span 1957 to 1992 Hz). The mean took them for noise decaying at
    their rate: the upright's 2 kHz band after C7 decayed at 17 dB/s, where
    the noise between them falls at 170, and rang on as a hiss for seconds.
    Above the fundamental the residue between the partials is mostly the
    note's own unresolved partials, which have no voice but the noise:
    measured by the median there too, the upright's 12.7 kHz band went silent
    and E3's 8 kHz band fell 16 dB further under its recording.
    Also the right-over-left level difference (dB) and left/right coherence
    there. Where a take starts too close to its onset to measure the floor
    before it and runs on into the room's noise (`tail_floor`, the upright's
    takes), the floor is measured over its last frames instead (`wav` holds
    the takes); Salamander's takes are faded out at their ends. Frames that
    would start before the take, where it is cut at its onset and the layer's
    contact falls before that, are left out of the line."""
    import math
    import numpy as np
    from scipy import signal, stats
    import piano_analysis as pa
    sr = result['sr']
    length = int(window * sr)
    nfft = 1 << int(math.ceil(math.log2(2 * length)))
    w = signal.windows.hann(length, sym=False)
    hz = np.fft.rfftfreq(nfft, 1 / sr)
    keep = np.ones(len(hz), bool)
    for f in np.r_[result['freqs'], [q['hz'] for L in result['layers'] for q in L['found']]]:
        keep &= np.abs(hz - f) > 1.5 * 2 / window
    bins = []
    for centre in NOISE_BANDS:
        band = (hz >= centre * 2 ** (-1 / 6)) & (hz < centre * 2 ** (1 / 6))
        bins.append(band & keep if band.sum() and (band & keep).sum() >= .25 * band.sum() else None)
    below = [centre < result['f1'] for centre in NOISE_BANDS]
    scale = 2 / (sr * np.sum(w * w))                         # one-sided density per bin

    def power(z, j):
        p = np.abs(z) ** 2 * scale
        return float(np.mean(np.median(p, axis=0))) / math.log(2) if below[j] else float(np.mean(p))
    shape = (len(result['layers']), len(NOISE_BANDS))
    level, decay, floor, balance, coherence = (np.full(shape, np.nan) for _ in range(5))
    times = np.arange(window / 2, window / 2 + .1001, hop)
    for i, L in enumerate(result['layers']):
        pre = L['pre_onset'].astype(float)
        x = np.vstack([pre, L['residual'].astype(float)])
        zero = len(pre) + contact[i] * sr

        def spectrum(t):
            a = int(round(zero + t * sr)) - length // 2
            return np.fft.rfft(x[a:a + length] * w[:, None], nfft, axis=0) if a >= 0 else None
        frames = [(t, z) for t in times if (z := spectrum(t)) is not None]
        at = np.array([t for t, _ in frames])
        quiet = [z for z in (spectrum(-window / 2 - .005), spectrum(-window / 2)) if z is not None]
        if not quiet and tail_floor:
            _, take = pa.load(wav / f'{result["cases"][i]}.wav')
            quiet = [np.fft.rfft(take[len(take) - length - a:len(take) - a] * w[:, None], nfft, axis=0)
                     for a in (int(.005 * sr), 0)]
        for j, band in enumerate(bins):
            if band is None:
                continue
            density = 10 * np.log10(np.array([power(z[band], j) for _, z in frames]) + 1e-30)
            if quiet:
                floor[i, j] = 10 * math.log10(np.mean([power(z[band], j) for z in quiet]) + 1e-30)
            clear = density > (floor[i, j] if quiet else -np.inf) + 10
            if clear.sum() < 10:
                continue
            slope, intercept, _, _ = stats.theilslopes(density[clear], at[clear])
            level[i, j], decay[i, j] = intercept, slope
            left = np.concatenate([z[band, 0] for _, z in frames])
            right = np.concatenate([z[band, 1] for _, z in frames])
            balance[i, j] = 10 * math.log10(np.sum(np.abs(right) ** 2) / np.sum(np.abs(left) ** 2))
            coherence[i, j] = abs(np.sum(left * np.conj(right))) / math.sqrt(
                np.sum(np.abs(left) ** 2) * np.sum(np.abs(right) ** 2))
    return level, decay, floor, balance, coherence


def noise_data(results, datas, wav, tail_floor):
    """The noise bands and each anchor's excitation of them (see NOISE_BANDS).

    Per anchor and band: the density at contact per layer, smoothed across
    velocity like the partials' levels, where a band that stays near its floor
    counts weakly at 3 dB under it; the decay, the median over the layers that
    start 20 dB above their floor (over all measured layers if none does), so
    the floor does not flatten it; the right-over-left difference, the median
    over the measured layers. Bands an anchor cannot measure take the
    neighbouring anchors' values at its layers' velocities (as level_at plays
    them), the nearest one's beyond them; a band no anchor measures stays
    silent (NOISE_SILENT), as the upright's 16 kHz band does. The coherence
    is one per band, the median over every measured layer.
    """
    import numpy as np
    measured = []
    for r, d in zip(results, datas):
        contact = np.array([L['delay'] for L in r['layers']]) - np.array(d['layer_shift_ms']) / 1000
        measured.append(noise_bands(r, contact, wav, tail_floor))
    anchors = []
    for r, d, (level, decay, floor, balance, _) in zip(results, datas, measured):
        velocities = np.array(d['velocities'])
        bands = []
        for j in range(len(NOISE_BANDS)):
            known = np.isfinite(level[:, j])
            if known.sum() < 3:
                bands.append(None)
                continue
            target = np.where(known, level[:, j], floor[:, j] - 3)
            levels = smooth_levels(velocities, target, np.where(known, 1.0, .1))
            strong = known & (level[:, j] >= floor[:, j] + 20)
            slopes = decay[strong if strong.any() else known, j]
            bands.append({'level_db': levels, 'decay_db_s': float(np.clip(np.median(slopes), -400, -5)),
                          'balance_db': float(np.median(balance[known, j]))})
        anchors.append(bands)
    notes = np.array([r['note'] for r in results], float)
    for j in range(len(NOISE_BANDS)):
        known = [k for k, bands in enumerate(anchors) if bands[j] is not None]
        for k, bands in enumerate(anchors):
            if bands[j] is None and not known:
                bands[j] = {'level_db': np.full(len(datas[k]['velocities']), NOISE_SILENT),
                            'decay_db_s': -400.0, 'balance_db': 0.0, 'filled': True}
            elif bands[j] is None:
                pick = lambda key: np.interp(notes[k], notes[known], [anchors[i][j][key] for i in known])
                bands[j] = {'level_db': np.array([np.interp(notes[k], notes[known],
                                                            [level_at(datas[i]['velocities'],
                                                                      anchors[i][j]['level_db'], v) for i in known])
                                                  for v in datas[k]['velocities']]),
                            'decay_db_s': float(pick('decay_db_s')), 'balance_db': float(pick('balance_db')),
                            'filled': True}
    coherence = [float(np.nanmedian(np.concatenate([m[4][:, j] for m in measured])))
                 for j in range(len(NOISE_BANDS))]
    return {'hz': NOISE_BANDS, 'coherence': coherence, 'anchors': anchors}


def level_at(velocities, db, v):
    """A level (dB) at velocity v from its layers', as the engine's levelAt
    takes it: piecewise linear, continued beyond the layers with the end
    segments' slopes, never rising toward softer playing."""
    if v <= velocities[0]:
        return db[0] - max(0.0, (db[1] - db[0]) / (velocities[1] - velocities[0])) * (velocities[0] - v)
    if v >= velocities[-1]:
        return db[-1] + max(0.0, (db[-1] - db[-2]) / (velocities[-1] - velocities[-2])) * (v - velocities[-1])
    import numpy as np
    return float(np.interp(v, velocities, db))


def phase_at(velocities, phase, v):
    """A phase (rad) at velocity v from its layers', as the engine's phaseAt
    takes it: along the chord between the layers' unit vectors, held beyond."""
    import cmath
    import numpy as np
    if v <= velocities[0]:
        return float(phase[0])
    if v >= velocities[-1]:
        return float(phase[-1])
    i = int(np.searchsorted(velocities, v)) - 1
    t = (v - velocities[i]) / (velocities[i + 1] - velocities[i])
    z = (1 - t) * cmath.exp(1j * phase[i]) + t * cmath.exp(1j * phase[i + 1])
    return cmath.phase(z) if abs(z) > 1e-6 else float(phase[i] if t < .5 else phase[i + 1])


def on_grid(anchors, noise, grid):
    """Anchors whose layers lie at other velocities than `grid` (a pitch
    without one of the layers, or a layer whose range spans two of the
    grid's) carried onto it as the engine would play them: levels and
    densities by level_at, phases by phase_at, the onset rise log-linear and
    held beyond the layers."""
    import numpy as np
    for a, bands in zip(anchors, noise['anchors']):
        v = list(a['velocities'])
        if v == list(grid):
            continue
        for p in a['partials'] + a['extras']:
            for lane in p['lanes']:
                lane['level_db'] = np.array([level_at(v, lane['level_db'], g) for g in grid])
                lane['phase'] = np.array([phase_at(v, lane['phase'], g) for g in grid])
        a['onset_rise'] = np.exp(np.interp(grid, v, np.log(a['onset_rise'])))
        for b in bands:
            b['level_db'] = np.array([level_at(v, b['level_db'], g) for g in grid])
        a['velocities'] = list(grid)


def number(x):
    value = f'{float(x):.7g}'
    return value + ('f' if '.' in value or 'e' in value else '.f')


def wrap(text, width=76):
    """`text` as // comment lines."""
    import textwrap
    return ['// ' + line for line in textwrap.wrap(text, width)]


def header(model, grid, layer_level, anchors, halo, body, noise, action, damper):
    """The model's generated header: its data in the types of MeasuredTypes.h,
    in namespace keyra::measured::<name>."""
    name = next(key for key, m in MODELS.items() if m is model)
    rows, total = len(anchors), sum(len(a['partials']) for a in anchors)
    modes, bands, strings = len(body['hz']), len(noise['hz']), len(halo['keys'])

    def lane(lane):
        return ('{' + ','.join(number(x) for x in (lane['rate'], lane['offset_hz'], lane['left'],
                                                   lane['right'].real, lane['right'].imag))
                + ',{{' + ','.join(number(x) for x in lane['level_db']) + '}}'
                + ',{{' + ','.join(number(x) for x in lane['phase']) + '}}}')

    def table(kind, name, size, row_values):
        """A flat table over the recorded pitches, a commented row per pitch."""
        out = [f'constexpr std::array<{kind},{rows}*{size}> {name}' + '{{']
        for a, values in zip(anchors, row_values):
            out += [f'  // MIDI {a["note"]}', '  ' + ','.join(values) + ',']
        return out + ['}};']

    def action_knock(k):
        return '{' + number(k['level_db']) + ',' + number(k['phase']) + '}'
    lines = wrap(f'Generated by Tools/fit_realtime_modal.py from the calibration split of {model["title"]}; '
                 'regenerate, never edit.')
    lines += ['// Fitted numbers only: no recorded waveform or impulse response.',
              '#pragma once', '#include "MeasuredTypes.h"', '',
              f'namespace keyra {{ namespace measured {{ namespace {name} {{',
              f'constexpr int layers={len(grid)};',
              '// Each recorded layer the levels are measured at: its velocity in the',
              '// library\'s own map from MIDI velocity, and its early level (dB) under',
              '// the loudest layer\'s, the median over the pitches recorded at every layer.',
              'constexpr std::array<float,maxLayers> layerVelocity{{' + ','.join(number(v) for v in grid) + '}};',
              'constexpr std::array<float,maxLayers> layerLevelDb{{' + ','.join(number(v) for v in layer_level) + '}};',
              f'constexpr std::array<Anchor,{rows}> anchors{{{{']
    first = extra = 0
    for a in anchors:
        lines.append(f'  {{{a["note"]},{number(a["f1"])},{number(a["B"])},'
                     + '{{' + ','.join(number(x) for x in a['onset_rise']) + '}}'
                     + f',{first},{len(a["partials"])},{extra},{len(a["extras"])}}},')
        first += len(a['partials'])
        extra += len(a['extras'])
    lines.append('}};')
    lines.append(f'constexpr std::array<Partial,{total}> partials{{{{')
    for a in anchors:
        lines.append(f'  // MIDI {a["note"]}')
        for p in a['partials']:
            lines.append(f'  {{{p["order"]},' + ','.join(number(p[k]) for k in ('cents', 'rise_seconds', 'rise_slope'))
                         + ',{{' + ','.join(lane(x) for x in p['lanes']) + '}}},')
    lines.append('}};')
    lines.append(f'constexpr std::array<Extra,{extra}> extras{{{{')
    for a in anchors:
        if a['extras']:
            lines.append(f'  // MIDI {a["note"]}')
        for p in a['extras']:
            only, = p['lanes']
            lines.append(f'  {{{p["order"]},{number(p["cents"])},{lane(only)}}},')
    lines += ['}};',
              f'constexpr std::array<HaloString,{strings}> haloStrings{{{{'
              + ','.join('{' + ','.join(number(x) for x in (c, r, u[0], u[1].real, u[1].imag)) + '}'
                         for c, r, u in zip(halo['cents'], halo['rates'], halo['pickups'])) + '}};',
              '// How loudly each recorded pitch\'s strike sets each undamped string',
              '// ringing: the level (dB) at contact at velocity 64, and the slope of',
              '// every level (dB per 64 velocity).',
              f'constexpr float haloSlopeDb={number(halo["slope"])};']
    lines += table('float', 'haloLevels', strings, [[number(x) for x in levels] for levels in halo['levels']])
    lines += [f'constexpr std::array<BodyMode,{modes}> bodyModes{{{{']
    lines += ['  {' + ','.join(number(x) for x in (f, r, u[0].real, u[1].real, u[1].imag)) + '},'
              for f, r, u in zip(body['hz'], body['rates'], body['shapes'])]
    lines += ['}};',
              '// The rise 1 - e^(-t/rise) (seconds) of the body\'s ring, measured from the',
              '// treble recordings\' onsets.',
              f'constexpr float bodyRise={number(body["rise"])};']
    lines += table('Knock', 'knocks', modes, [['{' + ','.join(number(k[key]) for key in ('level_db', 'slope_db', 'phase')) + '}'
                                     for k in knocks] for knocks in body['anchors']])
    lines += wrap(model['actions'] + ' Each knock\'s level and phase per mode, and the rise '
                  '1 - e^(-t/rise) (seconds) the knocks share.')
    lines += [f'constexpr float actionRise={number(action["rise"])};']
    lines += table('ActionKnock', 'releaseKnocks', modes, [[action_knock(k) for k in knocks] for knocks in action['releases']])
    for edge in ('pedal_down', 'pedal_up'):
        if edge in action:
            lines.append(f'constexpr std::array<ActionKnock,{modes}> {"pedalDown" if edge == "pedal_down" else "pedalUp"}'
                         + '{{' + ','.join(action_knock(k) for k in action[edge]) + '}};')
    if damper:
        lines += wrap('What the felt leaves ringing of a damped partial (measured::Damper), from the '
                      'train key-release takes.')
        lines.append('constexpr Damper damper{' + ','.join(number(x) for x in damper['law']) + '};')
    lines += [f'constexpr std::array<NoiseBand,{bands}> noiseBands{{{{'
              + ','.join('{' + number(f) + ',' + number(c) + '}' for f, c in zip(noise['hz'], noise['coherence']))
              + '}};']
    lines += table('Noise', 'noise', bands, [['{' + number(-b['decay_db_s'] / 8.685889638) + ',' + number(b['balance_db'])
                                     + ',{{' + ','.join(number(x) for x in b['level_db']) + '}}}' for b in band_rows]
                                    for band_rows in noise['anchors']])
    lines.extend([f'}}}}}} // namespace keyra::measured::{name}', ''])
    return '\n'.join(lines)


def generate(model):
    import cmath
    import math
    import statistics
    import numpy as np
    import scipy
    anchors_in = train_anchors(model)
    anchors, records, results = [], [], []
    for note, layers in anchors_in.items():
        target = model['cache'] / f'{note}.pkl'
        if not target.exists():
            raise SystemExit(f'anchor {note} is not analysed: run with --analyse first')
        with target.open('rb') as f:
            result = pickle.load(f)
        if result.get('cache_key') != cache_key(layers):
            raise SystemExit(f'anchor {note} was analysed from other inputs: run with --analyse')
        results.append(result)
    strings = string_pitches({r['note']: series(r)[0] for r in results})
    halo_hz = halo_pitches(results, strings, model['wav'])
    for (note, layers), result in zip(anchors_in.items(), results):
        data = anchor_data(result, halo_hz, model['wav'])
        anchors.append(data)
        errors = [p['error'] for p in data['partials']]
        records.append({'note': note, 'cases': [case for case, _, _ in layers], 'f1_hz': data['f1'],
                        'stiffness': data['B'], 'partials': len(data['partials']), 'extras': len(data['extras']),
                        'contact_delay_ms': [round(1000 * L['delay'], 3) for L in result['layers']],
                        'layer_shift_ms': data['layer_shift_ms'],
                        'median_phase_agreement': float(np.median([p['phase_agreement'] for p in data['partials']])),
                        'onset_rise_ms': data['layer_onset_rise_ms'],
                        'median_relative_error': float(np.median(errors)) if errors else None})
    # The layers most recorded pitches have; the others are carried onto them.
    grid = list(statistics.mode(tuple(a['velocities']) for a in anchors))
    for record, a in zip(records, anchors):
        if list(a['velocities']) != grid:
            record['recorded_velocities'] = list(a['velocities'])
    # How loud each layer plays: both channels' RMS from 50 to 750 ms after the
    # onset, as the benchmark sets a case's gain, under the same pitch's
    # loudest layer, the median over the pitches recorded at every layer. The
    # engine's velocity response picks the layer coordinate where this reaches
    # the level a MIDI velocity asks for.
    levels = np.array([[L['early_rms_db'] for L in r['layers']]
                       for r, a in zip(results, anchors) if list(a['velocities']) == grid])
    layer_level = np.median(levels - levels[:, -1:], axis=0)
    if np.any(np.diff(layer_level) <= 0):
        raise SystemExit(f'the layers\' median levels do not rise with velocity: {np.round(layer_level, 2)}')
    body = body_data(results, anchors, grid, layer_level)
    for record, explained, knocks in zip(records, body['explained'], body['anchors']):
        record.update({'body_explained': [round(e, 3) for e in explained],
                       'body_modes_hidden': sum(1 for k in knocks if k.get('filled')),
                       'body_phase_coherence': float(np.median([k['coherence'] for k in knocks
                                                                if not k.get('filled')]))})
    noise = noise_data(results, anchors, model['wav'], model.get('tail_floor', False))
    for record, bands in zip(records, noise['anchors']):
        record['noise_bands_filled'] = sum(1 for b in bands if b.get('filled'))
    action = action_data(model, [a['note'] for a in anchors], body['hz'], body['rates'], body['shapes'])
    halo = halo_data(results, strings, halo_hz, model['wav'])
    for record, kinds in zip(records, halo['kinds']):
        record['halo_strings'] = {kind: [key for key, k in zip(halo['keys'], kinds) if k == kind]
                                  for kind in ('clear', 'under', 'filled')}
    on_grid(anchors, noise, grid)
    damper = damper_data(model, results, halo_hz) if model.get('damper') else None
    content = header(model, grid, layer_level, anchors, halo, body, noise, action, damper)
    metadata = {
        'schema_version': 5,
        'corpus': str(model['corpus'].relative_to(ROOT)), 'corpus_sha256': sha256(model['corpus']),
        'split': str(model['split'].relative_to(ROOT)), 'split_sha256': sha256(model['split']),
        'roles_used': ['train'], 'dev_or_sealed_recordings_opened': False,
        'analysis_source_sha256': sha256(ANALYSIS), 'fitter_source_sha256': sha256(Path(__file__)),
        'tool_versions': {'numpy': np.__version__, 'scipy': scipy.__version__},
        'layer_velocity': grid, 'layer_level_db': [round(float(v), 3) for v in layer_level],
        'model': ('Per partial four lanes with complex rates shared by all layers under one rise 1 - e^(-t/rise) '
                  'that starts them from zero, never shorter than the anchor\'s onset rise measured from the '
                  'recordings\' build-up; per lane a velocity-independent pickup shape and a smoothed level and '
                  'phase at string contact per layer, the layers shifted in time to one phase pattern across the '
                  'partials; in a layer where a component does not stand clear of its floor, no louder than its '
                  'recorded peak there. Partials are interpolated between anchors by order, lanes fastest first. Beside the '
                  'series, the residual peaks at least four layers share: above 1 kHz those 20 dB over their '
                  'surroundings (the 64 most powerful per anchor), each measured through a window that parts it '
                  'from its neighbours and fitted with one lane from contact, placed by the series in cents from '
                  'its nearest order and cross-faded in power between anchors; peaks within 15 cents of the '
                  'fundamental are left to the partial\'s lanes, and those beside the undamped strings\' pitches '
                  '(MIDI 89-108) to the halo. The undamped strings ring with every strike, struck key excepted: '
                  'each at one frequency, the median of the strongest peak within 30 cents of its key\'s pitch 1 to '
                  '2 s after contact in the train recordings from C6 up, where clear; measured as tones (the '
                  'largest amplitude within 1 Hz through 0.5 s Hann windows every 0.25 s from 1 to 2 s after '
                  'contact, both channels\' mean power, clear where 10 dB over the median 4 to 20 Hz either side) '
                  'in the train recordings from F#3 up, where no partial of the struck series lies within 10 Hz: '
                  'per string one decay rate (its median fall from 1 to 2 s, drawn towards all the strings\' median '
                  'by ten recordings) and one stereo pickup (the median level difference and mean phase between '
                  'the channels), one velocity slope pooled within pitch and string, and per anchor and string a '
                  'level at contact at velocity 64: the mean over the layers clear in two or more windows, '
                  'brought back at the rate, or else 10 dB under the median 1 s bound; strings the struck series '
                  'or key covers and anchors below F#3 take the levels of the anchors around. One bank of '
                  'body modes shared by every key, found in the treble anchors\' residuals below 0.8 f1, each with '
                  'one stereo pickup; per anchor and mode a complex excitation at string contact whose dB level is '
                  'linear in the level its layer plays at, modes hidden by an anchor\'s partials taken from its neighbours. The '
                  'action\'s knocks on the same modes (each anchor\'s key release'
                  + (', the sustain pedal down and up' if model['pedal'] else '') + '; one train take each, in those files\' own scale) fitted from their onsets under one shared '
                  'rise. Above the modes, third-octave band noise from 1 to 16 kHz: per anchor and band a density '
                  'at contact per layer, one exponential decay and a left/right balance, measured in the residual 2 '
                  'to 100 ms after contact; one left/right coherence per band. Anchors recorded at other '
                  'velocities than the layers most have are carried onto those as the engine plays between and '
                  'beyond layers.'
                  + (' What the dampers leave ringing, from the train key-release takes below F6: their partials to '
                     'the tenth, 25 dB over their floor and clear of the undamped strings\' first three partials, '
                     'every 10 ms to 3 s, under the engine\'s damper landing as a share the felt loss takes and a '
                     'loosely held share r falling at S, both besides the lanes\' own decay at velocity 85 from '
                     '1.5 s; r (dB) and ln S linear in octaves from 261.63 Hz, per take a key-up time and per '
                     'partial a level.' if damper else '')),
        'anchors': records,
        'halo': {'strings': [{'key': key, 'hz': round(hz, 2), 'cents': round(cents, 2), 'rate': round(rate, 3),
                              'rate_layers': count, 'right_over_left_db': round(20 * math.log10(abs(u[1]) / u[0]), 2),
                              'phase': round(cmath.phase(u[1]), 3)}
                             for key, hz, cents, rate, count, u in zip(halo['keys'], halo['hz'], halo['cents'],
                                                                       halo['rates'], halo['rate_layers'],
                                                                       halo['pickups'])],
                 'slope_db_per_64': round(halo['slope'], 3)},
        'body': {'modes': len(body['hz']), 'hz': [round(float(f), 2) for f in body['hz']],
                 't60_seconds': [round(6.907755 / float(r), 3) for r in body['rates']],
                 'pickup_explained': [round(k, 3) for k in body['pickup_explained']],
                 'rise_ms': round(1000 * body['rise'], 3),
                 'layer_rise_ms': {str(note): [round(1000 * r, 3) for r in rises]
                                   for note, rises in body['layer_rises'].items()}},
        'action': {'cases': action['cases'], 'rise_ms': round(1000 * action['rise'], 3),
                   'unexplained': dict(zip(action['cases'], action['unexplained']))},
        **({'damper': {'share_db': round(damper['law'][0], 3), 'share_db_per_octave': round(damper['law'][1], 3),
                       'slow_rate_per_s': round(math.exp(damper['law'][2]), 4),
                       'slow_rate_ratio_per_octave': round(math.exp(damper['law'][3]), 4),
                       'mean_abs_db': damper['mean_abs_db'], 'takes': damper['takes']}} if damper else {}),
        'noise': {'band_hz': [round(f, 1) for f in noise['hz']],
                  'coherence': [round(c, 3) for c in noise['coherence']]},
        'uncalibrated_anchors': [{'note': note, 'reason': reason} for note, reason in model['uncalibrated'].items()],
        'generated_header_sha256': hashlib.sha256(content.encode()).hexdigest(),
    }
    return content, metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--model', choices=MODELS, default='grand')
    parser.add_argument('--analyse', action='store_true', help='measure the train anchors into out/')
    parser.add_argument('--jobs', type=int, default=os.cpu_count() or 1)
    parser.add_argument('--check', action='store_true', help='verify the header and provenance reproduce')
    parser.add_argument('--header', type=Path, help='default: the model\'s header in Source/DSP')
    parser.add_argument('--metadata', type=Path, help='default: the model\'s provenance in Docs/research')
    args = parser.parse_args()
    model = MODELS[args.model]
    args.header = args.header or model['header']
    args.metadata = args.metadata or model['metadata']
    if args.analyse:
        analyse(args.model, args.jobs)
        return
    content, metadata = generate(model)
    if args.check:
        if args.header.read_text() != content:
            raise SystemExit('Measured modal header differs from the regenerated fit')
        if json.loads(args.metadata.read_text()) != metadata:
            raise SystemExit('Measured modal provenance differs from the regenerated fit')
        print('measured modal header and provenance reproduce exactly')
        return
    args.header.write_text(content)
    args.metadata.parent.mkdir(parents=True, exist_ok=True)
    args.metadata.write_text(json.dumps(metadata, indent=2, allow_nan=False) + '\n')
    print(f'{len(metadata["anchors"])} anchors, '
          f'{sum(a["partials"] for a in metadata["anchors"])} partials written to {args.header}')


if __name__ == '__main__':
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    main()
