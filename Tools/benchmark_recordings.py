#!/usr/bin/env python3
"""Score a Keyra renderer against one piano's recordings, note by note: the
grand's Salamander recordings or, with --model upright, the upright's
Helsinki 1967 recordings, which the renderer then plays.

Each case renders one held note (50 ms of silence, then the note at its
layer's velocity) through a `keyra_render` binary and measures the render and
the recording with the same `piano_analysis` operators, at the recording's
partials: the render's are its peaks nearest them, order by order
(matched_partials). One scalar gain, from the 50-750 ms RMS, is removed per
case and kept for every later window.
Stereo channels are compared in power and as left/right relations, never as
cancelling waveforms. These scores measure agreement with one recorded piano
and microphone pair; they are not perceptual ratings.

Metrics per case (lower is better):

  partial_db      partial levels in four windows (0.05-0.25, -0.75, -1.5,
                  -3.5 s), every recorded partial at least 10 dB above its
                  floor (the power of its quietest second before the
                  library's fade-out) in that window; a missing partial
                  scores its full level
  tuning_cents    absolute partial frequency error, partials 1-30
  decay_db_s      late decay slope (0.5 s to 3.5 s, Theil-Sen) per partial,
                  both over the frames where the recording, averaged over
                  0.1 s, is 6 dB above its floor, where those frames span
                  half a second or more; the render's with that floor added
  attack_db       third-octave level error, 0-100 ms (10 ms hops)
  early_db        third-octave level error, 0.1-0.5 s
  sustain_db      third-octave level error, 0.5-3.0 s; a band counts where
                  either sound is within 50 dB of the recording's peak and
                  10 dB above its floor
  noise_db        third-octave level between partials, 0-300 ms; a band
                  counts where either sound is within 40 dB of the
                  recording's loudest and 10 dB above its floor
  ild_db / icc    per third-octave band left/right level difference and
                  inter-channel coherence error, 0.05-1.5 s
  envelope_db     5 ms RMS envelope error, 0.02-3.5 s, where the recording
                  stands 10 dB above its own floor, the power of its quietest
                  second before the library's fade-out (both high-passed at
                  20 Hz)
  rise_ms         10-90 % envelope rise error within the first 150 ms
  level_db        loudness error across notes and velocities: each case's
                  gain against the run's median gain, which stands for the
                  instrument's one output level

  python3 Tools/benchmark_recordings.py --renderer build-dsp/keyra_render \\
      --roles train dev --out out/bench/candidate
  python3 Tools/benchmark_recordings.py --model upright --renderer build-dsp/keyra_render \\
      --roles train dev --out out/bench/upright-candidate
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# One BLAS thread per worker: the pool already fills every core.
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')

import numpy as np  # noqa: E402
from scipy import ndimage, signal, stats  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fit_realtime_modal as fit  # noqa: E402
import piano_analysis as pa  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
# The grand's corpus, which the other tools score against.
CORPUS = fit.MODELS['grand']['wav']
SPLIT = fit.MODELS['grand']['split']
MANIFEST = fit.MODELS['grand']['corpus']
# Each piano's record of the openings of its sealed cases.
SEALED_LOGS = {'grand': ROOT / 'Tools/corpus/sealed-openings.json',
               'upright': ROOT / 'Tools/corpus/sealed-openings-helsinki.json'}
WINDOWS = [(.05, .25), (.25, .75), (.75, 1.5), (1.5, 3.5)]
LAYER_VELOCITY = fit.LAYER_VELOCITY
RENDER_SECONDS = 4.6
FEATURES = 'features 6'  # bump when features() changes, to refresh cached references
LEAD = .05
# keyra_render's Output for measurements: 20 dB under the default, where the
# output stage (Source/DSP/OutputStage.h) passes every strike untouched. The
# scores take each render's level out, so they do not depend on it.
MEASURE = ['--gain', '.07']


def band_spectrogram(x, sr, start, seconds, hop=.01, win=.04):
    """Third-octave band power (dB, stereo mean) over time, with the per-band
    left and right powers and cross-spectrum the stereo scores need."""
    n = int(win * sr)
    w = signal.windows.hann(n, sym=False)
    nfft = 1 << int(math.ceil(math.log2(2 * n)))
    hz = np.fft.rfftfreq(nfft, 1 / sr)
    edges = np.c_[pa.THIRD_OCTAVE * 2 ** (-1 / 6), pa.THIRD_OCTAVE * 2 ** (1 / 6)]
    member = np.stack([(hz >= lo) & (hz < hi) for lo, hi in edges], axis=1).astype(float)
    y = np.concatenate([np.zeros((n, 2)), x, np.zeros((n, 2))])
    centres = start + n + np.round(np.arange(int(seconds / hop)) * hop * sr).astype(int)
    centres = centres[centres + n - n // 2 <= len(y)]
    idx = centres[:, None] - n // 2 + np.arange(n)[None, :]
    norm = 2 / (nfft * np.sum(w * w))
    zl = np.fft.rfft(y[idx, 0] * w, nfft, axis=1)
    zr = np.fft.rfft(y[idx, 1] * w, nfft, axis=1)
    left = (np.abs(zl) ** 2 * norm) @ member
    right = (np.abs(zr) ** 2 * norm) @ member
    cross = (zr * np.conj(zl) * norm) @ member
    level = 10 * np.log10(np.maximum(.5 * (left + right), 1e-30))
    return level, left, right, cross


def matched_partials(x, sr, note, start, reference):
    """A render's partials where the recording (`reference`, its features) has
    them: at each of its orders, the peak of the spectrum pa.partials searches
    nearest the recording's frequency, within that search's width and
    standing as clear of its surroundings (6 dB at the fundamental, 10
    above), so that a recording matched against itself finds its own peaks.
    pa.partials looks for each order where the stiff string through the
    orders found so far puts it, and C7's second partial lies at the edge of
    that search: a render whose fundamental sat 0.4 Hz sharper than the
    recording's lost it there, and every order above it."""
    nominal = pa.midi_hz(note)
    seconds = 3.0 if nominal < 150 else 2.0 if nominal < 600 else 1.0
    a = start + int(.03 * sr)
    hz, p = pa._spectrum(x[a:min(len(x), a + int(seconds * sr))], sr)
    db = 10 * np.log10(np.maximum(p, 1e-30))
    orders, freqs = [], []
    for n, target in zip(reference['n'], reference['hz']):
        half = nominal * (2 ** (50 / 1200) - 1) if n == 1 else min(.25 * reference['f1'], 4.0 + .006 * target)
        lo, hi = np.searchsorted(hz, [target - half, target + half])
        if hi - lo < 5:
            continue
        k = np.arange(lo + 1, hi - 1)
        k = k[(db[k] > db[k - 1]) & (db[k] >= db[k + 1])
              & (db[k] - np.median(db[lo:hi]) >= (6 if n == 1 else 10))]
        if not len(k):
            continue
        k = int(k[np.argmin(np.abs(hz[k] - target))])
        y0, y1, y2 = db[k - 1:k + 2]
        d = y0 - 2 * y1 + y2
        orders.append(int(n))
        freqs.append(hz[k] + float(np.clip(.5 * (y0 - y2) / d if d < 0 else 0.0, -1, 1)) * (hz[1] - hz[0]))
    return orders, np.array(freqs)


def features(path, note, reference=None):
    """Everything the comparison needs from one note, measured identically for any audio;
    a render's partials are sought where its `reference` recording's are."""
    sr, x = pa.load(path)
    start = pa.onset(x, sr)
    if reference is None:
        f1, B, found = pa.partials(x, sr, note, start)
        orders, freqs = [q['n'] for q in found], np.array([q['hz'] for q in found])
    else:
        # Measured through the recording's window, as its f1 sets the length.
        f1, B = reference['f1'], reference['B']
        orders, freqs = matched_partials(x, sr, note, start, reference)
    tracked = freqs if len(freqs) else np.array([pa.midi_hz(note)])
    seconds = min(3.6, (len(x) - start) / sr - .02)
    t, z = pa.envelopes(x, sr, tracked, f1, start, seconds)
    power = np.mean(np.abs(z) ** 2, axis=1)
    level, left, right, cross = band_spectrogram(x, sr, start, min(3.0, seconds))
    # The recording's own floor per band (room, microphones, ventilation): the
    # mean power of its quietest second before the library's fade-out (the
    # analysis' horizon); nothing near it is scored. The quietest single frames
    # sat 10-15 dB under the room's rumble, as a band of one or two bins swings
    # that far from frame to frame and the files fade to silence, so in the
    # treble that rumble scored as the piano's sustain.
    duration = len(x) / sr
    end = duration - max(1.0, .25 * duration) if duration > 8 else duration - 1.0
    whole, _, _, _ = band_spectrogram(x, sr, 0, end, hop=.05)
    whole = 10 ** (whole / 10)
    second = np.array([whole[k:k + 20].mean(axis=0) for k in range(max(1, len(whole) - 19))])
    band_floor = 10 * np.log10(np.maximum(second.min(axis=0), 1e-30))
    # Each partial's floor the same way, from its envelope up to the fade-out.
    # The last quarter of the 3.6 s scored is the fade itself in the treble's
    # short files, which put those floors 20-30 dB under the room, so the
    # room's noise at a partial's frequency scored as the partial's late decay.
    _, zw = pa.envelopes(x, sr, tracked, f1, start, max(1.0, end - start / sr), hop=int(.05 * sr))
    pw = np.mean(np.abs(zw) ** 2, axis=1)
    second = np.array([pw[:, k:k + 20].mean(axis=1) for k in range(max(1, pw.shape[1] - 19))])
    partial_floor = 10 * np.log10(np.maximum(second.min(axis=0), 1e-30))
    _, noise = pa.residual_bands(x, sr, freqs, f1, start, seconds=.3, hop_s=.01)
    # The broadband measures leave out the room's infrasonic rumble, which in
    # the quiet treble files outweighs the piano a second after the strike.
    xh = signal.sosfiltfilt(signal.butter(2, 20, 'highpass', fs=sr, output='sos'), x, axis=0)
    early = xh[start + int(.05 * sr):start + int(.75 * sr)]
    env = np.sqrt(np.maximum(ndimage.uniform_filter1d(np.mean(xh * xh, axis=1), max(3, int(.005 * sr)),
                                                      mode='nearest'), 0))[start:]
    peak = float(np.max(env[:int(.15 * sr)]))
    cross10 = np.flatnonzero(env[:int(.15 * sr)] >= .1 * peak)
    cross90 = np.flatnonzero(env[:int(.15 * sr)] >= .9 * peak)
    times = np.arange(.02, 3.501, .02)
    envelope = np.interp(times * sr, np.arange(len(env)), env)
    # The broadband floor like the bands': the quietest second before the
    # fade-out. A floor from the envelope's own last frames sat 10 to 60 dB
    # under the room in the treble's short files, whose last frames are the
    # fade, and so scored the room's rumble as the piano's tail there.
    total = np.cumsum(np.r_[0.0, np.mean(xh * xh, axis=1)[:max(sr, int(end * sr))]])
    quietest = float(np.min((total[sr:] - total[:-sr])[::int(.05 * sr)])) / sr
    return {'sr': sr, 'f1': f1, 'B': B, 'n': orders, 'hz': freqs.tolist(),
            'env_t': t, 'env_power': power, 'floor': partial_floor,
            'bands': level, 'band_floor': band_floor, 'left': left, 'right': right, 'cross': cross, 'noise': noise,
            'early_rms': float(np.sqrt(np.mean(early * early))),
            'rise': (cross90[0] - cross10[0]) / sr if len(cross10) and len(cross90) else None,
            'envelope': envelope,
            'envelope_floor_db': 10 * math.log10(max(quietest, 1e-30))}


def window_db(t, power, lo, hi):
    m = (t >= lo) & (t < hi)
    return 10 * np.log10(np.maximum(np.mean(power[..., m], axis=-1), 1e-30)) if m.any() else None


def slope(t, db, m):
    if m.sum() < 8:
        return None
    return float(stats.theilslopes(db[m], t[m])[0])


def compare(ref, mod):
    gain_db = 20 * math.log10(ref['early_rms'] / max(mod['early_rms'], 1e-20))
    g = 10 ** (gain_db / 10)
    out = {'gain_db': gain_db}
    # Partials: levels per window, tuning, late decay.
    mod_index = {n: i for i, n in enumerate(mod['n'])}
    level_err, tune_err, decay_err = [], [], []
    # Partials more than 50 dB below the strongest one in a window, or within
    # 10 dB of the recording's floor, are not scored in that window.
    strongest = [max(window_db(ref['env_t'], p, lo, hi) for p in ref['env_power']) for lo, hi in WINDOWS]
    for i, n in enumerate(ref['n']):
        j = mod_index.get(n)
        rdb = 10 * np.log10(np.maximum(ref['env_power'][i], 1e-30))
        scored = False
        for (lo, hi), top in zip(WINDOWS, strongest):
            r = window_db(ref['env_t'], ref['env_power'][i], lo, hi)
            if r is None or r < max(ref['floor'][i] + 10, top - 50):
                continue
            scored = True
            m = window_db(mod['env_t'], mod['env_power'][j] * g, lo, hi) if j is not None else -300.0
            level_err.append(min(abs(r - m), 30.0))
        if j is None or not scored:
            continue
        if n <= 30:
            tune_err.append(abs(1200 * math.log2(mod['hz'][j] / ref['hz'][i])))
        # The render as the recording would hold it, over its floor. Without
        # it, a partial that falls silent within the span (A7v3's second, at
        # the recording's floor throughout, from 2 s) left the slope to
        # rounding residue 150 dB under it.
        mdb = 10 * np.log10(mod['env_power'][j] * g + 10 ** (ref['floor'][i] / 10))
        # Both slopes over the frames where the recording stands clear of its
        # floor: a two-stage decay measured over different spans differs even
        # when the model is exact. The frames are chosen on the envelope
        # averaged over 0.1 s; chosen frame by frame, the noise's own peaks
        # passed once a treble partial had sunk into it (A7's second partial
        # from 0.6 s) and set the recording's slope there.
        rt = ref['env_t']
        smooth = ndimage.uniform_filter1d(ref['env_power'][i], max(1, round(.1 / (rt[1] - rt[0]))), mode='nearest')
        late = (rt >= .5) & (rt <= 3.5) & (10 * np.log10(np.maximum(smooth, 1e-30)) > ref['floor'][i] + 6)
        # Over less than half a second a slope measures the unison beat, not
        # the decay: C7v12's third partial stood clear of its floor for 45 ms
        # after 0.5 s and scored -163 dB/s against a render's +66.
        if not late.any() or rt[late][-1] - rt[late][0] < .5:
            continue
        rs = slope(rt, rdb, late)
        ms = slope(rt, np.interp(rt, mod['env_t'], mdb), late)
        if rs is not None and ms is not None:
            decay_err.append(abs(rs - ms))
    out['partial_db'] = float(np.mean(level_err)) if level_err else None
    out['tuning_cents'] = float(np.mean(tune_err)) if tune_err else None
    out['decay_db_s'] = float(np.mean(decay_err)) if decay_err else None
    # Third-octave spectrogram, split into attack/early/sustain.
    rb, mb = ref['bands'], mod['bands'] + gain_db
    frames = min(len(rb), len(mb))
    rb, mb = rb[:frames], mb[:frames]
    peak = np.max(rb)
    # A band counts where either sound stands out, so energy the render adds
    # (an onset click, say) is scored as well as energy it lacks.
    loud = np.maximum(rb, mb)
    live = (loud > peak - 50) & (loud > ref['band_floor'][None, :] + 10)
    t = np.arange(frames) * .01
    for name, lo, hi in (('attack_db', 0, .1), ('early_db', .1, .5), ('sustain_db', .5, 3.0)):
        m = live & ((t >= lo) & (t < hi))[:, None]
        out[name] = float(np.mean(np.minimum(np.abs(rb - mb)[m], 30))) if m.any() else None
    # Noise likewise. Scored where the recording's noise alone stood within
    # 40 dB of its loudest, soft notes scored the recording's hiss, level to
    # 20 kHz, as the piano's noise, and hiss a render added over a quiet
    # band went unscored.
    rn, mn = ref['noise'], mod['noise'] + gain_db
    loud = np.fmax(rn, mn)
    m = np.isfinite(rn) & np.isfinite(mn) & (loud > np.nanmax(rn) - 40) & (loud > ref['band_floor'][None, :] + 10)
    out['noise_db'] = float(np.mean(np.minimum(np.abs(rn - mn)[m], 30))) if m.any() else None
    # Stereo per band over 0.05-1.5 s.
    sel = (t >= .05) & (t < 1.5)
    ild_err, icc_err = [], []
    for j in range(rb.shape[1]):
        rl, rr = ref['left'][:frames][sel, j].sum(), ref['right'][:frames][sel, j].sum()
        ml, mr = mod['left'][:frames][sel, j].sum(), mod['right'][:frames][sel, j].sum()
        if np.mean(rb[sel, j]) < max(peak - 50, ref['band_floor'][j] + 10) or min(rl, rr, ml, mr) <= 0:
            continue
        ild_err.append(abs(10 * math.log10(rr / rl) - 10 * math.log10(mr / ml)))
        ricc = abs(ref['cross'][:frames][sel, j].sum()) / math.sqrt(rl * rr)
        micc = abs(mod['cross'][:frames][sel, j].sum()) / math.sqrt(ml * mr)
        icc_err.append(abs(ricc - micc))
    out['ild_db'] = float(np.mean(ild_err)) if ild_err else None
    out['icc'] = float(np.mean(icc_err)) if icc_err else None
    er = ref['envelope'] / ref['early_rms']
    em = mod['envelope'] / mod['early_rms']
    # Frames within 10 dB of the recording's own floor (mains hum, room) are
    # not the piano and are not scored.
    m = (er > 10 ** (-50 / 20)) & (20 * np.log10(np.maximum(ref['envelope'], 1e-12)) > ref['envelope_floor_db'] + 10)
    out['envelope_db'] = float(np.mean(np.abs(20 * np.log10(np.maximum(er[m], 1e-4)) -
                                              20 * np.log10(np.maximum(em[m], 1e-4)))))
    out['rise_ms'] = abs(ref['rise'] - mod['rise']) * 1000 if ref['rise'] is not None and mod['rise'] is not None else None
    return out


def cached_reference(case, note, cache: Path, corpus: Path):
    wav = corpus / f'{case}.wav'
    key = hashlib.sha256((Path(pa.__file__).read_text() + FEATURES).encode()).hexdigest()[:12]
    target = cache / f'{case}-{key}.npz'
    if target.exists():
        data = dict(np.load(target, allow_pickle=True))
        return {k: (v.item() if v.shape == () else v) for k, v in data.items()}
    f = features(wav, note)
    cache.mkdir(parents=True, exist_ok=True)
    np.savez(target, **{k: np.asarray(v, dtype=object) if v is None else np.asarray(v) for k, v in f.items()})
    return f


def run_case(args):
    case, note, layer, velocity, renderer, extra, cache, corpus, keep = args
    ref = cached_reference(case, note, cache, corpus)
    with tempfile.TemporaryDirectory(prefix='keyra-bench-') as tmp:
        events = Path(tmp) / 'note.events'
        events.write_text(f'{LEAD} on {note} {velocity}\n')
        wav = Path(keep) / f'{case}.wav' if keep else Path(tmp) / 'render.wav'
        subprocess.run([renderer, '--events', str(events), '--output', str(wav),
                        '--duration', str(RENDER_SECONDS)] + MEASURE + extra, check=True, stdout=subprocess.DEVNULL)
        mod = features(wav, note, ref)
    result = compare(ref, mod)
    result.update({'case': case, 'note': note, 'layer': layer, 'velocity': velocity})
    return result


KEYS = ['partial_db', 'tuning_cents', 'decay_db_s', 'attack_db', 'early_db', 'sustain_db', 'noise_db',
        'ild_db', 'icc', 'envelope_db', 'rise_ms', 'level_db']


def add_levels(rows):
    median = float(np.median([r['gain_db'] for r in rows]))
    for r in rows:
        r['level_db'] = abs(r['gain_db'] - median)


def summarise(rows):
    out = {'cases': len(rows)}
    for k in KEYS:
        v = [r[k] for r in rows if r.get(k) is not None and np.isfinite(r[k])]
        out[k] = {'mean': float(np.mean(v)), 'median': float(np.median(v)), 'n': len(v)} if v else None
    return out


def register(note):
    return 'bass A0-B2' if note < 48 else 'middle C3-B5' if note < 84 else 'treble C6-C8'


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--model', choices=fit.MODELS, default='grand', help='the piano rendered and scored against')
    p.add_argument('--renderer', required=True)
    p.add_argument('--roles', nargs='+', default=['train', 'dev'])
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--jobs', type=int, default=os.cpu_count())
    p.add_argument('--cache', type=Path, default=ROOT / 'out/bench/reference-cache')
    p.add_argument('--keep-renders', action='store_true')
    p.add_argument('--layers', type=int, nargs='*', help='restrict to these velocity layers')
    p.add_argument('--open-sealed', metavar='REASON', help='required to score sealed cases; the opening is logged')
    p.add_argument('--rescore', action='store_true', help="re-summarise the --out report's cases without rendering")
    p.add_argument('renderer_args', nargs=argparse.REMAINDER, help='after --: extra keyra_render options')
    a = p.parse_args()
    if a.rescore:
        old = json.loads((a.out / 'report.json').read_text())
        a.renderer, a.roles, a.model = old['renderer'], list(old['summary']), old.get('model', 'grand')
    if 'sealed' in a.roles and not a.open_sealed:
        p.error('sealed cases need --open-sealed REASON')
    model = fit.MODELS[a.model]
    split = json.loads(model['split'].read_text())['cases']
    items = {i['id']: i for i in json.loads(model['corpus'].read_text())['files']}
    cases = [(c, items[c]['midi'], items[c]['layer'], fit.layer_velocity(items[c])) for c, r in split.items()
             if r in a.roles and items[c]['kind'] == 'note' and (not a.layers or items[c]['layer'] in a.layers)]
    if a.open_sealed and not a.rescore:
        sealed_log = SEALED_LOGS[a.model]
        log = json.loads(sealed_log.read_text()) if sealed_log.exists() else []
        log.append({'renderer': a.renderer, 'reason': a.open_sealed,
                    'renderer_sha256': hashlib.sha256(Path(a.renderer).read_bytes()).hexdigest()})
        sealed_log.write_text(json.dumps(log, indent=1) + '\n')
    a.out.mkdir(parents=True, exist_ok=True)
    keep = a.out / 'renders' if a.keep_renders else None
    if keep:
        keep.mkdir(exist_ok=True)
    # The renderer plays the piano it is scored against.
    extra = (['--model', a.model] if a.model != 'grand' else []) + [x for x in a.renderer_args if x != '--']
    if a.rescore:
        # Under the split as it stands: a case it no longer gives these roles is dropped.
        rows, extra = [r for r in old['cases'] if split[r['case']] in a.roles], old['renderer_args']
    else:
        jobs = [(c, n, l, v, a.renderer, extra, a.cache, model['wav'], keep) for c, n, l, v in cases]
        with concurrent.futures.ProcessPoolExecutor(a.jobs) as pool:
            rows = list(pool.map(run_case, jobs))
    rows.sort(key=lambda r: (r['note'], r['layer']))
    add_levels(rows)
    roles = {r: [x for x in rows if split[x['case']] == r] for r in a.roles}
    report = {'renderer': a.renderer, 'renderer_args': extra, 'model': a.model,
              'split': str(model['split'].relative_to(ROOT)),
              'summary': {r: summarise(v) for r, v in roles.items()},
              'by_register': {f'{r} / {g}': summarise([x for x in v if register(x['note']) == g])
                              for r, v in roles.items() for g in ('bass A0-B2', 'middle C3-B5', 'treble C6-C8')},
              'cases': rows}
    (a.out / 'report.json').write_text(json.dumps(report, indent=1) + '\n')
    lines = ['| role | ' + ' | '.join(KEYS) + ' |', '|---' * (len(KEYS) + 1) + '|']
    for name, s in list(report['summary'].items()) + list(report['by_register'].items()):
        lines.append(f'| {name} ({s["cases"]}) | ' + ' | '.join(
            f'{s[k]["mean"]:.2f}' if s.get(k) else '-' for k in KEYS) + ' |')
    (a.out / 'summary.md').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
