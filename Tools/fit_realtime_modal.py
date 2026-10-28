#!/usr/bin/env python3
"""Fit Keyra's measured modal data from the calibration split of the
Salamander Grand Piano V3 (Tools/corpus/split-2026-10-27.json).

Only the split's train recordings are opened: every A, C and F# pitch from A0
to A7 (22 anchors; C8 is left out, see UNCALIBRATED) at twelve velocity
layers. Each anchor is calibrated by `piano_analysis.analyse_anchor`: every
partial is fitted jointly across the layers, with lanes whose rates and
frequencies the strings fix and whose complex amplitude per microphone the
hammer and the pickup set. What the partials leave below the treble's
fundamentals gives the body modes every strike knocks. The fitted numbers go
into Source/DSP/MeasuredModalData.h; no recorded waveform or impulse response
enters the header.

  python3 Tools/fetch_salamander.py                  # the corpus, once
  python3 Tools/fit_realtime_modal.py --analyse      # measure the anchors (cached in out/)
  python3 Tools/fit_realtime_modal.py                # regenerate the header and provenance
  python3 Tools/fit_realtime_modal.py --check        # verify both reproduce exactly
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
CORPUS = ROOT / 'Tools/corpus/salamander-v3.json'
SPLIT = ROOT / 'Tools/corpus/split-2026-10-27.json'
WAV = ROOT / 'out/salamander/wav'
CACHE = ROOT / 'out/calibration/anchors'
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
# The keys from F6 up have no dampers: their strings ring with every strike
# at their own pitches. The analysis searches beside each one's pitch; a
# string is a residual peak that recurs, within RING_CENTS, in RING_PITCHES
# recorded pitches or more (find_rings). A peak within HALO_CENTS of an
# anchor's own fundamental is its unison, which the partial's lanes hold.
UNDAMPED = range(89, 109)
HALO_CENTS = 15.0
RING_CENTS = 1.5
RING_PITCHES = 4


def train_anchors():
    """Each calibrated train pitch with its train layers' (id, velocity, flac pin)."""
    corpus = {f['id']: f for f in json.loads(CORPUS.read_text())['files']}
    roles = json.loads(SPLIT.read_text())['cases']
    anchors = {}
    for case, role in roles.items():
        item = corpus[case]
        if role == 'train' and item['kind'] == 'note':
            anchors.setdefault(item['midi'], []).append(
                (case, LAYER_VELOCITY[item['layer'] - 1], item['flac_sha256']))
    return {note: sorted(layers, key=lambda layer: layer[1]) for note, layers in sorted(anchors.items())
            if note not in UNCALIBRATED}


def cache_key(layers) -> str:
    h = hashlib.sha256(ANALYSIS.read_bytes())
    for case, velocity, pin in layers:
        h.update(f'{case}:{velocity}:{pin}\n'.encode())
    return h.hexdigest()


def analyse_one(note, layers):
    import piano_analysis as pa
    key = cache_key(layers)
    target = CACHE / f'{note}.pkl'
    if target.exists():
        with target.open('rb') as f:
            if pickle.load(f).get('cache_key') == key:
                return note, 'cached'
    result = pa.analyse_anchor([WAV / f'{case}.wav' for case, _, _ in layers], note,
                               [velocity for _, velocity, _ in layers])
    result['cache_key'] = key
    result['cases'] = [case for case, _, _ in layers]
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('wb') as f:
        pickle.dump(result, f)
    return note, 'analysed'


def analyse(jobs):
    anchors = train_anchors()
    # Bass anchors carry the most partials; start them first.
    with concurrent.futures.ProcessPoolExecutor(jobs) as pool:
        futures = [pool.submit(analyse_one, note, layers) for note, layers in anchors.items()]
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
    """Each partial, extra component and ringing undamped string of an
    anchor's generated data as the engine plays it at layer i, both channels from `contact` seconds into
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
    for p in data['partials'] + data['extras'] + data['undamped']:
        hz = p['hz'] if 'hz' in p else pa.stiff(data['f1'], data['B'], p['order']) * 2 ** (p['cents'] / 1200)
        wave = np.zeros((samples, 2))
        for lane in p['lanes']:
            g = 10 ** (lane['level_db'][i] / 20) * np.exp(1j * lane['phase'][i])
            z = np.exp((-lane['rate'] + 2j * math.pi * (hz + lane['offset_hz'])) * tau) * on
            wave[:, 0] += np.real(g * lane['left'] * z)
            wave[:, 1] += np.real(g * lane['right'] * z)
        waves.append(wave)
        rises.append(p['rise_seconds'] * math.exp(p['rise_slope'] * x) if 'rise_seconds' in p else 0.0)
    return np.array(waves), np.array(rises)


def find_rings(results, strings):
    """The undamped strings heard ringing: every recorded pitch's residual
    peaks from the undamped strings' search span up, its own unison aside,
    pooled and grouped where they agree within RING_CENTS of a group's lowest.
    A group heard in RING_PITCHES recorded pitches or more is a string: kept
    at its median frequency, by the key whose pitch (`strings`) it sits
    nearest. Returns the strings ({key, cents, hz}, by frequency), the string
    each peak joins, {(note, index): string}, and how many such groups the
    same peaks form on average when each recorded pitch's are shifted by a
    random amount up to 50 cents: the strings that may be chance alignments."""
    import math
    import numpy as np
    import piano_analysis as pa
    low = pa.HALO_LOW
    peaks = sorted((float(f), r['note'], k) for r in results for k, f in enumerate(r['extra_freqs'])
                   if f >= low and abs(1200 * math.log2(f / series(r)[0])) > HALO_CENTS)

    def strings_in(peaks):
        groups = []
        for peak in sorted(peaks):
            if groups and 1200 * math.log2(peak[0] / groups[-1][0][0]) <= RING_CENTS:
                groups[-1].append(peak)
            else:
                groups.append([peak])
        return [g for g in groups if len({note for _, note, _ in g}) >= RING_PITCHES]
    rings, member = [], {}
    for group in strings_in(peaks):
        hz = float(np.median([f for f, _, _ in group]))
        key = min(strings, key=lambda m: abs(math.log2(hz / strings[m])))
        member.update({(note, k): len(rings) for _, note, k in group})
        rings.append({'key': key, 'cents': 1200 * math.log2(hz / strings[key]), 'hz': hz})
    rng = np.random.default_rng(0)
    notes = sorted({note for _, note, _ in peaks})
    chance = []
    for _ in range(50):
        shift = dict(zip(notes, rng.uniform(-50, 50, len(notes))))
        chance.append(len(strings_in([(f * 2 ** (shift[note] / 1200), note, k) for f, note, k in peaks])))
    return rings, member, float(np.mean(chance))


def ring_rates(results, rings, member):
    """Each string's `rate` (1/s): the median of its slower lane's over the
    recorded pitches whose fits timed that lane (left it above the slowest
    rate a fit allows)."""
    import numpy as np
    import piano_analysis as pa
    rates = {}
    for r in results:
        for k in range(len(r['extra_freqs'])):
            ring, fit = member.get((r['note'], k)), r['ring_fits'][k]
            if ring is None or fit is None:
                continue
            slow = float(np.min(np.exp(fit['theta'][:2])))
            if slow > pa.SLOWEST_RATE * 1.001:
                rates.setdefault(ring, []).append(slow)
    for ring, string in enumerate(rings):
        string['rate'] = float(np.median(rates[ring]))


# An undamped string's ring measured as a tone. The fit measures a string
# through a window as wide as the gap to its neighbours, which also holds the
# board's noise around a faint string, and a slow lane can take that noise for
# the string ringing on. Through a 0.5 s Hann window the recording's largest
# amplitude within 2 Hz of the string, from 1 s after contact every 0.25 s, is
# the string's tone where it stands 10 dB over the median from 4 to 20 Hz
# either side; elsewhere it is at most the string's.
RING_LATE = tuple(1 + .25 * k for k in range(11))     # s after contact


def ring_tones(result, shifts, hzs):
    """Per layer, string and RING_LATE time: the recording's tone (dB) at each
    of `hzs`, and whether it stands clear of the noise around it."""
    import numpy as np
    import piano_analysis as pa
    tone = np.full((len(result['layers']), len(hzs), len(RING_LATE)), np.nan)
    clear = np.zeros(tone.shape, bool)
    for i, (case, L) in enumerate(zip(result['cases'], result['layers'])):
        sr, x = pa.load(WAV / f'{case}.wav')
        mono = x.mean(axis=1)
        n = int(.5 * sr)
        w = np.hanning(n)
        f = np.fft.rfftfreq(8 * n, 1 / sr)
        for k, t in enumerate(RING_LATE):
            start = int(round((L['delay'] - shifts[i] + t - .25) * sr))
            if start + n > len(mono):
                break
            spectrum = np.abs(np.fft.rfft(mono[start:start + n] * w, 8 * n)) * 2 / np.sum(w)
            for j, hz in enumerate(hzs):
                d = np.abs(f - hz)
                tone[i, j, k] = 20 * np.log10(np.max(spectrum[d < 2]) + 1e-15)
                clear[i, j, k] = tone[i, j, k] >= 20 * np.log10(np.median(spectrum[(d >= 4) & (d <= 20)]) + 1e-15) + 10
    return tone, clear


def time_ring(lanes, tone, clear, slowest, velocities, sr):
    """An undamped string's lanes, fastest first, timed and held by its tone
    (layers x RING_LATE, from ring_tones). Where the slower lane carries the
    ring (10 dB over the faster as fitted) and the tone stands clear in two or
    more frames of a layer, spanning a second in all, the tone's decay, shared
    by the layers, times that lane and its level there sets the lane's, the
    correction interpolated across velocity to the other layers. Otherwise no
    lane decays more slowly than `slowest`. At no layer does the string then
    sound over the tone, both lanes heard at once."""
    import numpy as np
    import piano_analysis as pa
    t = np.array(RING_LATE)
    n = int(.5 * sr)
    u, w = (np.arange(n) - n / 2) / sr, np.hanning(n)

    def heard(lane):
        """dB, layers x RING_LATE, as the tone is measured."""
        gain = abs(lane['left'] + lane['right']) / 2 * np.sum(w * np.exp(-lane['rate'] * u)) / np.sum(w)
        return np.asarray(lane['level_db'])[:, None] + 20 * np.log10(gain + 1e-30) - 8.686 * lane['rate'] * t[None, :]

    fast, slow = lanes[0], lanes[-1]
    late = clear & np.isfinite(tone) & (heard(slow) >= heard(fast) + 10)
    used = late.sum(axis=1) >= 2
    span = max((float(np.ptp(t[row])) for row in late[used]), default=0.0)
    if span >= 1:
        dt = np.concatenate([t[row] - t[row].mean() for row in late[used]])
        dy = np.concatenate([tone[i, row] - tone[i, row].mean() for i, row in zip(np.flatnonzero(used), late[used])])
        slow['rate'] = max(pa.SLOWEST_RATE, -float(np.sum(dt * dy) / np.sum(dt * dt)) / 8.686)
        error = np.where(late, tone - heard(slow), np.nan)
        shift = np.array([np.nanmean(row) for row in error[used]])
        slow['level_db'] = np.asarray(slow['level_db']) + np.interp(velocities, velocities[used], shift)
    else:
        for lane in lanes:
            lane['rate'] = max(lane['rate'], slowest)
    total = 20 * np.log10(sum(10 ** (heard(lane) / 20) for lane in lanes))
    excess = np.nanmax(np.where(np.isfinite(tone), total - tone, -np.inf), axis=1)
    for lane in lanes:
        lane['level_db'] = np.asarray(lane['level_db']) - np.maximum(excess, 0)
    lanes.sort(key=lambda lane: -lane['rate'])
    return span >= 1


def anchor_data(result, rings, member):
    """The engine's data for one calibrated anchor; `rings` and `member` are
    find_rings' strings and the string each residual peak joins."""
    import math
    import numpy as np
    from scipy import stats
    import piano_analysis as pa
    velocities = np.array([L['velocity'] for L in result['layers']], float)
    delays = np.array([L['delay'] for L in result['layers']])
    snr = np.array([L['peak_db'] - L['floor_db'] for L in result['layers']])      # layers x orders
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
    def lanes_of(theta, u, mu, layers, snr_db):
        """Each lane's rate, offset, pickup and smoothed level and phase per layer."""
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
        return lanes

    partials = []
    for row, (k, n, fit, layers, u, mu, explained) in enumerate(shaped):
        mu = mu * np.exp(-2j * math.pi * freqs[k] * shifts[layers])[:, None]
        theta = fit['theta']
        lanes = lanes_of(theta, u, mu, layers, snr[layers, k])
        peak = max(float(np.max(lane['level_db'])) for lane in lanes)
        if peak < -110:
            continue
        lanes.sort(key=lambda lane: -lane['rate'])
        partials.append({'order': int(n), 'cents': float(1200 * math.log2(freqs[k] / pa.stiff(f1, B, n))),
                         'rise_seconds': math.exp(theta[2 * pa.LANES]), 'rise_slope': float(theta[2 * pa.LANES + 1]),
                         'lanes': lanes, 'explained': explained, 'phase_agreement': float(agreement[row]),
                         'error': float(np.median([e for e in fit['relative_error'] if e is not None]))})
    # The components beside the series, in the same frame. One within
    # HALO_CENTS of the fundamental is the struck key's own unison, which the
    # partial's lanes hold. One that joins a ringing string is kept as that
    # string (the strongest, where several join one); the rest of the strings'
    # search finds no string. The others sit at the order of the series
    # nearest them, cents from there.
    extras, ringing = [], {}
    orders_all = np.arange(1, 400)
    ladder = pa.stiff(f1, B, orders_all)
    extra_snr = np.array([L['extra_peak_db'] - L['extra_floor_db'] for L in result['layers']]) \
        if len(result.get('extra_freqs', [])) else None
    def peak_db(lanes):
        return max(float(np.max(lane['level_db'])) for lane in lanes)
    tone_hz = sorted({rings[ring]['hz'] for (note, _), ring in member.items() if note == result['note']})
    tones = ring_tones(result, shifts, tone_hz) if tone_hz else None
    for k, (f, fit) in enumerate(zip(result['extra_freqs'], result['extra_fits'])):
        ring = member.get((result['note'], k))
        if ring is not None:
            fit = result['ring_fits'][k]
        if fit is None or (ring is None and result['extra_halo'][k]):
            continue
        layers = [i for i, a in enumerate(fit['amplitudes']) if a is not None]
        if len(layers) < 3:
            continue
        u, mu, _ = lane_shapes([fit['amplitudes'][i] for i in layers])
        mu = mu * np.exp(2j * math.pi * f * (delays[layers] - shifts[layers]))[:, None]
        lanes = sorted(lanes_of(fit['theta'], u, mu, layers, extra_snr[layers, k]), key=lambda lane: -lane['rate'])
        if peak_db(lanes) < -110 or abs(1200 * math.log2(f / f1)) <= HALO_CENTS:
            continue
        component = {'lanes': lanes, 'error': float(np.median([e for e in fit['relative_error'] if e is not None]))}
        if ring is not None:
            # A string decays at its own rates whichever key sets it ringing,
            # but its measurement can outlast it: through a window as wide as
            # the gap to its neighbours, a faint string's envelope also holds
            # the board's noise, which a slow lane takes for the string ringing
            # on. Its tone in the recording times the slower lane where it
            # rings clear of that noise, and holds both lanes under it
            # everywhere (time_ring; the rules compared are in
            # Docs/decisions.md, 28 October).
            j = tone_hz.index(rings[ring]['hz'])
            component['timed'] = time_ring(lanes, tones[0][:, j], tones[1][:, j], rings[ring]['rate'], velocities,
                                           result['sr'])
            # It rings at one pitch too: its group's median, where the slower
            # lane, the one that rings on, sits within a few tenths of a hertz.
            # The fit's offsets refine this pitch's own peak, which may sit up
            # to RING_CENTS from it, so the faster lane keeps only its spacing
            # from the slower.
            slow = lanes[-1]['offset_hz']
            for lane in lanes:
                lane['offset_hz'] -= slow
            if ring not in ringing or peak_db(lanes) > peak_db(ringing[ring]['lanes']):
                ringing[ring] = component | {'ring': ring, 'hz': rings[ring]['hz']}
            continue
        n = int(orders_all[np.argmin(np.abs(ladder - f))])
        extras.append(component | {'order': n, 'cents': float(1200 * math.log2(f / ladder[n - 1]))})
    data = {'note': result['note'], 'f1': f1, 'B': B, 'velocities': velocities.tolist(), 'partials': partials,
            'extras': extras, 'undamped': [ringing[ring] for ring in sorted(ringing)],
            'layer_shift_ms': [round(1000 * d, 3) for d in shifts]}
    # The onset rise of every layer as the engine plays the data. Layer to
    # layer it scatters by a factor of several, more than any trend, so the
    # anchor keeps a straight line through it in log time over velocity:
    # Theil-Sen, which a few outlying layers cannot tilt.
    sr, onsets = result['sr'], []
    for i, (case, L) in enumerate(zip(result['cases'], result['layers'])):
        _, x = pa.load(WAV / f'{case}.wav')
        contact = L['delay'] - shifts[i]
        waves, rises = header_waves(data, i, sr, int((contact + .05) * sr), contact)
        onsets.append(onset_rise(x, sr, L['start'], contact, result['f1'], waves, rises))
    slope, intercept = stats.theilslopes(np.log(onsets), velocities)[:2]
    line = intercept + slope * velocities
    data.update({'onset_rise': np.exp(line), 'layer_onset_rise_ms': [round(1000 * r, 3) for r in onsets]})
    return data


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
    with 0.5 ms smoothing above the floor before the onset."""
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
        floor = max(float(recorded.max()) * 1e-5, float(np.median(recorded[:len(pre) - int(.005 * sr)])))
        frames = np.flatnonzero((t >= contact[i] - .002) & (t <= contact[i] + seconds))[::max(1, int(.00025 * sr))]
        target = 10 * np.log10(recorded[frames] + floor)
        errors = [float(np.mean((10 * np.log10(power(model * (1 - np.exp(-tau / r))[:, None])[frames] + floor)
                                 - target) ** 2)) for r in grid]
        rises.append(float(grid[int(np.argmin(errors))]))
    return rises


def body_data(results, datas):
    """The body bank and each anchor's excitation of it (see BODY_LOW)."""
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
        velocity = np.array([L['velocity'] for L in r['layers']], float)
        x = (velocity - 64) / 64
        knocks = []
        for m, shape in enumerate(shapes):
            level = np.conj(shape) @ a[:, m].T / 2                    # complex level per layer
            if not np.all(np.isfinite(level)):
                knocks.append(None)
                continue
            db = 20 * np.log10(np.abs(level) + 1e-12)
            weight = np.abs(level) ** 2
            # Level linear in velocity (dB), weighted to the louder layers; one phase.
            X = np.c_[np.ones_like(x), x] * np.sqrt(weight)[:, None]
            intercept, slope = np.linalg.lstsq(X, db * np.sqrt(weight), rcond=None)[0]
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


# Above the body modes the soundboard's response is too dense to resolve,
# and every strike leaves a broadband, decorrelated ring between the partials.
# It is measured as band power in third octaves from 1 kHz, in the residual
# the fitted partials leave, and played as band noise.
NOISE_BANDS = [1000.0 * 2 ** (k / 3) for k in range(13)]   # Hz: 1 to 16 kHz


def noise_bands(result, contact, window=.04, hop=.002):
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
    Also the right-over-left level difference (dB) and left/right coherence
    there."""
    import math
    import numpy as np
    from scipy import signal, stats
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
    scale = 2 / (sr * np.sum(w * w))                         # one-sided density per bin
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
        frames = [spectrum(t) for t in times]
        quiet = [z for z in (spectrum(-window / 2 - .005), spectrum(-window / 2)) if z is not None]
        for j, band in enumerate(bins):
            if band is None:
                continue
            density = 10 * np.log10(np.array([np.mean(np.abs(z[band]) ** 2) * scale for z in frames]) + 1e-30)
            if quiet:
                floor[i, j] = 10 * math.log10(np.mean([np.mean(np.abs(z[band]) ** 2) * scale for z in quiet]) + 1e-30)
            clear = density > (floor[i, j] if quiet else -np.inf) + 10
            if clear.sum() < 10:
                continue
            slope, intercept, _, _ = stats.theilslopes(density[clear], times[clear])
            level[i, j], decay[i, j] = intercept, slope
            left = np.concatenate([z[band, 0] for z in frames])
            right = np.concatenate([z[band, 1] for z in frames])
            balance[i, j] = 10 * math.log10(np.sum(np.abs(right) ** 2) / np.sum(np.abs(left) ** 2))
            coherence[i, j] = abs(np.sum(left * np.conj(right))) / math.sqrt(
                np.sum(np.abs(left) ** 2) * np.sum(np.abs(right) ** 2))
    return level, decay, floor, balance, coherence


def noise_data(results, datas):
    """The noise bands and each anchor's excitation of them (see NOISE_BANDS).

    Per anchor and band: the density at contact per layer, smoothed across
    velocity like the partials' levels, where a band that stays near its floor
    counts weakly at 3 dB under it; the decay, the median over the layers that
    start 20 dB above their floor (over all measured layers if none does), so
    the floor does not flatten it; the right-over-left difference, the median
    over the measured layers. Bands an anchor cannot measure take the
    neighbouring anchors' values, the nearest one's beyond them. The coherence
    is one per band, the median over every measured layer.
    """
    import numpy as np
    measured = []
    for r, d in zip(results, datas):
        contact = np.array([L['delay'] for L in r['layers']]) - np.array(d['layer_shift_ms']) / 1000
        measured.append(noise_bands(r, contact))
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
            if bands[j] is None:
                pick = lambda key: np.interp(notes[k], notes[known], [anchors[i][j][key] for i in known])
                bands[j] = {'level_db': np.array([np.interp(notes[k], notes[known],
                                                            [anchors[i][j]['level_db'][m] for i in known])
                                                  for m in range(len(results[k]['layers']))]),
                            'decay_db_s': float(pick('decay_db_s')), 'balance_db': float(pick('balance_db')),
                            'filled': True}
    coherence = [float(np.nanmedian(np.concatenate([m[4][:, j] for m in measured])))
                 for j in range(len(NOISE_BANDS))]
    return {'hz': NOISE_BANDS, 'coherence': coherence, 'anchors': anchors}


def number(x):
    value = f'{float(x):.7g}'
    return value + ('f' if '.' in value or 'e' in value else '.f')


def header(anchors, rings, body, noise):
    velocities = anchors[0]['velocities']
    layers = len(velocities)
    total = sum(len(a['partials']) for a in anchors)
    lines = ['// Generated by Tools/fit_realtime_modal.py from the calibration split of the',
             '// Salamander Grand Piano V3 (Alexander Holm, CC BY 3.0); regenerate, never edit.',
             '// Fitted numbers only: no recorded waveform or impulse response.',
             '#pragma once', '#include <array>', '', 'namespace keyra { namespace measured {',
             f'constexpr int layers={layers};',
             '// MIDI velocity of each recorded layer the levels are measured at.',
             'constexpr std::array<float,layers> layerVelocity{{' + ','.join(number(v) for v in velocities) + '}};',
             '// One lane of a partial: decay rate (1/s), frequency offset from the',
             '// partial (Hz), the pickup shape (left real; right complex; mean channel',
             '// power 1), and per layer its level (dB) and its phase (rad) at string',
             '// contact, the layers aligned to one pattern across the partials.',
             'struct Lane { float rate, offsetHz, left, rightRe, rightIm; std::array<float,layers> levelDb, phase; };',
             '// A partial of the stiff-string series: its tuning (cents from the series),',
             '// the rise 1 - e^(-t/rise) its lanes share (seconds at velocity 64; log',
             '// slope per 64 velocity), and its lanes, fastest first.',
             'struct Partial { int order; float cents, riseSeconds, riseSlope; std::array<Lane,4> lanes; };',
             '// A recorded pitch: its series (f1 at A4 = 440 Hz, stiffness B), per layer',
             '// the shortest rise its partials take (seconds), measured from the',
             '// recordings\' onsets, and its partials.',
             '// A component beside the series (below A3: the unison strings\' own series',
             '// at high orders and phantom partials): one lane at its place by the',
             '// series (cents from an order), starting at contact.',
             'struct Extra { int order; float cents; Lane lane; };',
             '// A string from F6 up, which has no damper, ringing with every strike at',
             '// its own frequency: the key it sits nearest and its cents from the pitch the',
             '// engine gives that key. Some sit 20 to 45 cents from every key\'s pitch;',
             '// they recur across the recorded pitches like the rest.',
             'struct Ring { int key; float cents; };',
             f'constexpr std::array<Ring,{len(rings)}> rings{{{{'
             + ','.join('{' + str(r['key']) + ',' + number(r['cents']) + '}' for r in rings) + '}};',
             '// A component within unisonCents of a pitch\'s fundamental is that key\'s',
             '// own unison, which its partial\'s lanes hold.',
             f'constexpr float unisonCents={number(HALO_CENTS)};',
             '// A string as a recorded pitch sets it ringing: two lanes, fastest first.',
             '// Driven through the bridge, it follows the strike\'s decay, then rings on',
             '// at its own, slower one.',
             'struct Undamped { int ring; std::array<Lane,2> lanes; };',
             'struct Anchor { int note; float f1, B; std::array<float,layers> onsetRise; int first, count, '
             'extraFirst, extraCount, undampedFirst, undampedCount; };',
             f'constexpr std::array<Anchor,{len(anchors)}> anchors{{{{']
    first = extra = ring = 0
    for a in anchors:
        lines.append(f'  {{{a["note"]},{number(a["f1"])},{number(a["B"])},'
                     + '{{' + ','.join(number(x) for x in a['onset_rise']) + '}}'
                     + f',{first},{len(a["partials"])},{extra},{len(a["extras"])},{ring},{len(a["undamped"])}}},')
        first += len(a['partials'])
        extra += len(a['extras'])
        ring += len(a['undamped'])
    lines.append('}};')
    lines.append(f'constexpr std::array<Partial,{total}> partials{{{{')
    for a in anchors:
        lines.append(f'  // MIDI {a["note"]}')
        for p in a['partials']:
            lanes = []
            for lane in p['lanes']:
                lanes.append('{' + ','.join(number(x) for x in (lane['rate'], lane['offset_hz'], lane['left'],
                                                               lane['right'].real, lane['right'].imag))
                             + ',{{' + ','.join(number(x) for x in lane['level_db']) + '}}'
                             + ',{{' + ','.join(number(x) for x in lane['phase']) + '}}}')
            lines.append(f'  {{{p["order"]},' + ','.join(number(p[k]) for k in ('cents', 'rise_seconds', 'rise_slope'))
                         + ',{{' + ','.join(lanes) + '}}},')
    lines.append('}};')
    for kind, field, count, place in (('Extra', 'extras', extra, ('order', 'cents')), ('Undamped', 'undamped', ring, ('ring',))):
        lines.append(f'constexpr std::array<{kind},{count}> {field}{{{{')
        for a in anchors:
            if a[field]:
                lines.append(f'  // MIDI {a["note"]}')
            for p in a[field]:
                lanes = ['{' + ','.join(number(x) for x in (lane['rate'], lane['offset_hz'], lane['left'],
                                                            lane['right'].real, lane['right'].imag))
                         + ',{{' + ','.join(number(x) for x in lane['level_db']) + '}}'
                         + ',{{' + ','.join(number(x) for x in lane['phase']) + '}}}' for lane in p['lanes']]
                lines.append(f'  {{{p[place[0]]},' + ''.join(number(p[k]) + ',' for k in place[1:])
                             + ('{{' + ','.join(lanes) + '}}' if len(lanes) > 1 else lanes[0]) + '},')
        lines.append('}};')
    lines += ['// The soundboard and case: modes every strike knocks, shared by every key',
              '// and measured under the treble\'s fundamentals. Each has its frequency (Hz),',
              '// decay rate (1/s) and one stereo pickup (left real; right complex; mean',
              '// channel power 1).',
              'struct BodyMode { float hz, rate, left, rightRe, rightIm; };',
              f'constexpr std::array<BodyMode,{len(body["hz"])}> bodyModes{{{{']
    lines += ['  {' + ','.join(number(x) for x in (f, r, u[0].real, u[1].real, u[1].imag)) + '},'
              for f, r, u in zip(body['hz'], body['rates'], body['shapes'])]
    lines += ['}};',
              '// The rise 1 - e^(-t/rise) (seconds) of the body\'s ring, measured from the',
              '// treble recordings\' onsets.',
              f'constexpr float bodyRise={number(body["rise"])};',
              '// How each recorded pitch knocks each body mode: the level (dB at velocity',
              '// 64), its slope (dB per 64 velocity) and the phase (rad) at string contact.',
              'struct Knock { float levelDb, slopeDb, phase; };',
              f'constexpr std::array<std::array<Knock,{len(body["hz"])}>,{len(anchors)}> knocks{{{{']
    for a, knocks in zip(anchors, body['anchors']):
        lines.append(f'  // MIDI {a["note"]}')
        lines.append('  {{' + ','.join('{' + ','.join(number(k[key]) for key in ('level_db', 'slope_db', 'phase'))
                                         + '}' for k in knocks) + '}},')
    lines += ['}};',
              '// Above the modes, the board\'s dense ring as noise in third-octave bands:',
              '// each band\'s centre (Hz) and its left/right coherence.',
              'struct NoiseBand { float hz, coherence; };',
              f'constexpr std::array<NoiseBand,{len(noise["hz"])}> noiseBands{{{{'
              + ','.join('{' + number(f) + ',' + number(c) + '}' for f, c in zip(noise['hz'], noise['coherence']))
              + '}};',
              '// How each recorded pitch\'s strike excites each band: the decay rate (1/s),',
              '// the right-over-left level difference (dB) and per layer the noise',
              '// density at contact (dB re 1/Hz).',
              'struct Noise { float rate, balanceDb; std::array<float,layers> densityDb; };',
              f'constexpr std::array<std::array<Noise,{len(noise["hz"])}>,{len(anchors)}> noise{{{{']
    for a, bands in zip(anchors, noise['anchors']):
        lines.append(f'  // MIDI {a["note"]}')
        lines.append('  {{' + ','.join('{' + number(-b['decay_db_s'] / 8.685889638) + ',' + number(b['balance_db'])
                                         + ',{{' + ','.join(number(x) for x in b['level_db']) + '}}}'
                                         for b in bands) + '}},')
    lines.extend(['}};', '}} // namespace keyra::measured', ''])
    return '\n'.join(lines)


def generate():
    import numpy as np
    import scipy
    anchors_in = train_anchors()
    anchors, records, results = [], [], []
    for note, layers in anchors_in.items():
        target = CACHE / f'{note}.pkl'
        if not target.exists():
            raise SystemExit(f'anchor {note} is not analysed: run with --analyse first')
        with target.open('rb') as f:
            result = pickle.load(f)
        if result.get('cache_key') != cache_key(layers):
            raise SystemExit(f'anchor {note} was analysed from other inputs: run with --analyse')
        results.append(result)
    strings = string_pitches({r['note']: series(r)[0] for r in results})
    rings, member, chance = find_rings(results, strings)
    ring_rates(results, rings, member)
    for (note, layers), result in zip(anchors_in.items(), results):
        data = anchor_data(result, rings, member)
        anchors.append(data)
        errors = [p['error'] for p in data['partials']]
        records.append({'note': note, 'cases': [case for case, _, _ in layers], 'f1_hz': data['f1'],
                        'stiffness': data['B'], 'partials': len(data['partials']), 'extras': len(data['extras']),
                        'rings': [u['ring'] for u in data['undamped']],
                        'contact_delay_ms': [round(1000 * L['delay'], 3) for L in result['layers']],
                        'layer_shift_ms': data['layer_shift_ms'],
                        'median_phase_agreement': float(np.median([p['phase_agreement'] for p in data['partials']])),
                        'onset_rise_ms': data['layer_onset_rise_ms'],
                        'median_relative_error': float(np.median(errors)) if errors else None})
    body = body_data(results, anchors)
    for record, explained, knocks in zip(records, body['explained'], body['anchors']):
        record.update({'body_explained': [round(e, 3) for e in explained],
                       'body_modes_hidden': sum(1 for k in knocks if k.get('filled')),
                       'body_phase_coherence': float(np.median([k['coherence'] for k in knocks
                                                                if not k.get('filled')]))})
    noise = noise_data(results, anchors)
    for record, bands in zip(records, noise['anchors']):
        record['noise_bands_filled'] = sum(1 for b in bands if b.get('filled'))
    content = header(anchors, rings, body, noise)
    metadata = {
        'schema_version': 4,
        'corpus': str(CORPUS.relative_to(ROOT)), 'corpus_sha256': sha256(CORPUS),
        'split': str(SPLIT.relative_to(ROOT)), 'split_sha256': sha256(SPLIT),
        'roles_used': ['train'], 'dev_or_sealed_recordings_opened': False,
        'analysis_source_sha256': sha256(ANALYSIS), 'fitter_source_sha256': sha256(Path(__file__)),
        'tool_versions': {'numpy': np.__version__, 'scipy': scipy.__version__},
        'layer_velocity': anchors[0]['velocities'],
        'model': ('Per partial four lanes with complex rates shared by all layers under one rise 1 - e^(-t/rise) '
                  'that starts them from zero, never shorter than the anchor\'s onset rise measured from the '
                  'recordings\' build-up; per lane a velocity-independent pickup shape and a smoothed level and '
                  'phase at string contact per layer, the layers shifted in time to one phase pattern across the '
                  'partials. Partials are interpolated between anchors by order, lanes fastest first. Beside the '
                  'series, the residual peaks at least four layers share: above 1 kHz those 20 dB over their '
                  'surroundings (the 64 most powerful per anchor), and beside each undamped string\'s pitch (MIDI '
                  '89-108, the struck key excepted) the strongest 10 dB over them; each is measured through a '
                  'window that parts it from its neighbours and fitted with one lane from contact. '
                  'Peaks within 15 cents of the fundamental are left to the partial\'s lanes. Peaks from F6 up '
                  'that recur within 1.5 cents in four or more anchors are undamped strings ringing, fitted '
                  'with two lanes instead. Where a string\'s tone (the largest amplitude within 2 Hz through 0.5 s '
                  'Hann windows every 0.25 s from 1 to 3.5 s after contact) stands 10 dB over the median 4 to 20 Hz '
                  'either side in two or more windows of a layer, a second apart in all, its decay there times the '
                  'slower lane and its level sets the lane\'s; elsewhere no lane is slower than the string\'s median '
                  'slower lane where its fits timed one; at no layer do the two lanes together stand over the tone. '
                  'Each string is kept at one frequency for its slower lane and interpolated between anchors by '
                  'string, lanes fastest first; the rest of the strings\' search is '
                  'dropped. The other peaks are placed by the series in cents from their nearest order and '
                  'cross-faded in power between anchors. One bank of '
                  'body modes shared by every key, found in the treble anchors\' residuals below 0.8 f1, each with '
                  'one stereo pickup; per anchor and mode a complex excitation at string contact whose dB level is '
                  'linear in velocity, modes hidden by an anchor\'s partials taken from its neighbours. Above the '
                  'modes, third-octave band noise from 1 to 16 kHz: per anchor and band a density at contact per '
                  'layer, one exponential decay and a left/right balance, measured in the residual 2 to 100 ms '
                  'after contact; one left/right coherence per band.'),
        'anchors': records,
        'rings': {'strings': [{'key': r['key'], 'cents': round(r['cents'], 2), 'hz': round(r['hz'], 2),
                               'rate': round(r['rate'], 3),
                               'anchors': [a['note'] for a in anchors if any(u['ring'] == i for u in a['undamped'])],
                               'timed_by_tone': [a['note'] for a in anchors
                                                 if any(u['ring'] == i and u['timed'] for u in a['undamped'])]}
                              for i, r in enumerate(rings)],
                  'by_chance': round(chance, 1)},
        'body': {'modes': len(body['hz']), 'hz': [round(float(f), 2) for f in body['hz']],
                 't60_seconds': [round(6.907755 / float(r), 3) for r in body['rates']],
                 'pickup_explained': [round(k, 3) for k in body['pickup_explained']],
                 'rise_ms': round(1000 * body['rise'], 3),
                 'layer_rise_ms': {str(note): [round(1000 * r, 3) for r in rises]
                                   for note, rises in body['layer_rises'].items()}},
        'noise': {'band_hz': [round(f, 1) for f in noise['hz']],
                  'coherence': [round(c, 3) for c in noise['coherence']]},
        'uncalibrated_anchors': [{'note': note, 'reason': reason} for note, reason in UNCALIBRATED.items()],
        'generated_header_sha256': hashlib.sha256(content.encode()).hexdigest(),
    }
    return content, metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--analyse', action='store_true', help='measure the train anchors into out/')
    parser.add_argument('--jobs', type=int, default=os.cpu_count() or 1)
    parser.add_argument('--check', action='store_true', help='verify the header and provenance reproduce')
    parser.add_argument('--header', type=Path, default=ROOT / 'Source/DSP/MeasuredModalData.h')
    parser.add_argument('--metadata', type=Path, default=ROOT / 'Docs/research/realtime-modal-fit-2026-10-27.json')
    args = parser.parse_args()
    if args.analyse:
        analyse(args.jobs)
        return
    content, metadata = generate()
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
