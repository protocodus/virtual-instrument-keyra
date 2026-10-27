"""Measurements of isolated piano notes, shared by Keyra's fitter and benchmark.

Every measurement here is applied in exactly the same way to a recording and
to an engine render, so analysis bias (window smearing, leakage, onset
detection) cancels in a comparison.

- onset: the first 1 ms stereo-power crossing of a noise-aware threshold near
  -45 dB of the first-second peak (the preserved benchmark's definition);
- partials: sequential peak tracking of a long Hann spectrum, each partial
  searched where the stiff-string fit of the partials found so far predicts it,
  so per-partial deviations from that fit (bridge coupling, wound strings) are
  measured rather than assumed;
- envelopes: the complex amplitude of every partial in each channel from a
  direct DTFT with a 4-term Blackman-Harris window six periods of the
  fundamental long, so a neighbouring partial leaks below -90 dB;
- residual_bands: the power between partials, in third-octave bands over time,
  which is where the hammer knock, the body and the action noises live;
- analyse_anchor: the calibration of one recorded pitch from its velocity
  layers (see the section at the end).
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from scipy import ndimage, optimize, signal, stats
from scipy.io import wavfile

THIRD_OCTAVE = 1000.0 * 2.0 ** (np.arange(-17, 14) / 3.0)  # 19.7 Hz .. 16 kHz centres


def load(path):
    """Stereo float64 audio and its rate; mono files are duplicated."""
    sr, x = wavfile.read(str(path))
    if x.dtype.kind == 'i':
        x = x.astype(np.float64) / 2.0 ** (8 * x.dtype.itemsize - 1)
    elif x.dtype.kind == 'u':
        x = (x.astype(np.float64) - 128.0) / 128.0
    else:
        x = x.astype(np.float64)
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    if not np.isfinite(x).all():
        raise ValueError(f'non-finite audio in {path}')
    return int(sr), x


def midi_hz(note, a4=440.0):
    return a4 * 2.0 ** ((note - 69) / 12.0)


def stiff(f1, B, n):
    """Partial frequencies of a stiff string, normalised so n=1 is f1."""
    n = np.asarray(n, dtype=float)
    return f1 * n * np.sqrt((1 + B * n * n) / (1 + B))


def onset(x, sr):
    power = np.mean(x * x, axis=1)
    env = ndimage.uniform_filter1d(power, max(3, int(.001 * sr)), mode='constant')
    peak = float(np.max(env[:min(len(env), int(1.5 * sr))]))
    if peak <= 1e-22:
        raise ValueError('no audible onset in the first 1.5 seconds')
    noise = float(np.median(env[:max(1, int(.008 * sr))]))
    threshold = max(peak * 10 ** (-4.5), min(noise * 25, peak * 1e-4))
    return max(0, int(np.flatnonzero(env > threshold)[0]) - int(.0005 * sr))


def blackman_harris(n):
    return signal.windows.blackmanharris(n, sym=False)


def _spectrum(seg, sr, pad=4):
    """Hann power spectrum of a stereo segment, channels summed, and its bins."""
    n = len(seg)
    w = signal.windows.hann(n, sym=False)
    nfft = 1 << int(math.ceil(math.log2(n * pad)))
    z = np.fft.rfft(seg * w[:, None], n=nfft, axis=0)
    p = np.sum(np.abs(z) ** 2, axis=1) * 2 / (nfft * np.sum(w * w)) / seg.shape[1]
    return np.fft.rfftfreq(nfft, 1 / sr), p


def partials(x, sr, note, start, max_partials=160, top=None):
    """Track partial frequencies of one note.

    Returns f1, B and a list of dicts (n, hz, level_db, prominence_db) for the
    partials found; missing orders are simply absent. `top` caps frequency.
    """
    nominal = midi_hz(note)
    top = min(top or 18000.0, .45 * sr)
    # Long windows resolve bass partials; treble notes do not last as long.
    seconds = 3.0 if nominal < 150 else 2.0 if nominal < 600 else 1.0
    a = start + int(.03 * sr)
    b = min(len(x), a + int(seconds * sr))
    hz, p = _spectrum(x[a:b], sr)
    df = hz[1] - hz[0]
    db = 10 * np.log10(np.maximum(p, 1e-30))

    def peak_near(target, half):
        lo, hi = np.searchsorted(hz, [target - half, target + half])
        if hi - lo < 5:
            return None
        k = lo + int(np.argmax(db[lo:hi]))
        if k <= lo or k >= hi - 1:
            return None
        y0, y1, y2 = db[k - 1:k + 2]
        d = y0 - 2 * y1 + y2
        off = .5 * (y0 - y2) / d if d < 0 else 0.0
        floor = np.median(db[lo:hi])
        return hz[k] + float(np.clip(off, -1, 1)) * df, float(y1), float(y1 - floor)

    found = []
    # Start from a typical grand's stiffness, lowest in the lower tenor and
    # doubling about every 8 semitones towards the top: in the treble the
    # second and third partials are already tens of hertz sharp, and a
    # search started from a lower value locks on to the wrong peaks.
    f1, B = nominal, 7e-5 * 2 ** ((note - 42) / 8 if note >= 42 else (42 - note) / 12)
    first = peak_near(nominal, nominal * (2 ** (50 / 1200) - 1))
    if first is not None and first[2] >= 6:
        found.append({'n': 1, 'hz': first[0], 'level_db': first[1], 'prominence_db': first[2]})
        f1 = first[0]
    misses = 0
    for n in range(2, max_partials + 1):
        target = float(stiff(f1, B, n))
        if target > top:
            break
        pk = peak_near(target, min(.25 * f1, 4.0 + .006 * target))
        if pk is None or pk[2] < 10:
            misses += 1
            if misses >= 10:
                break
            continue
        misses = 0
        found.append({'n': n, 'hz': pk[0], 'level_db': pk[1], 'prominence_db': pk[2]})
        if len(found) >= 3:
            ns = np.array([q['n'] for q in found], float)
            fs = np.array([q['hz'] for q in found])
            wts = np.clip(np.array([q['prominence_db'] for q in found]) / 30, .2, 1.5)

            def res(t):
                return wts * 1200 * np.log2(stiff(t[0], t[1], ns) / fs)
            fit = optimize.least_squares(res, [f1, max(B, 1e-8)], bounds=([f1 * .97, 0], [f1 * 1.03, .05]),
                                         loss='soft_l1', f_scale=2.0, x_scale=[f1, 1e-3])
            f1, B = map(float, fit.x)
        else:
            # Too few partials for a stiffness fit: keep B, take f1 from the orders found.
            f1 = float(np.mean([q['hz'] / q['n'] for q in found]))
    return f1, B, found


def window_length(f1, sr):
    """Envelope window in samples (even): six periods of the fundamental,
    between 4 ms and 250 ms."""
    length = int(np.clip(round(6.0 / f1 * sr), int(.004 * sr), int(.25 * sr)))
    return length + length % 2


def envelopes(x, sr, freqs, f1, start, seconds, hop=None, times=None):
    """Complex amplitude of each partial in each channel.

    Returns (times after onset, z[partial, channel, frame]); |z| is the
    sinusoid's amplitude. The window is centred on each frame time, so the
    first frames see the pre-onset signal and the attack is smeared by about
    a third of the window; the same holds for any audio measured this way.
    Frames are every `hop` samples for `seconds`, or at the given `times`.
    """
    freqs = np.asarray(freqs, float)
    length = window_length(f1, sr)
    w = blackman_harris(length)
    gain = 2.0 / np.sum(w)
    pad = np.zeros((length // 2, x.shape[1]))
    y = np.concatenate([pad, x, pad])
    if times is None:
        hop = hop or max(1, int(.005 * sr))
        frames = min(int(seconds * sr) // hop, (len(x) - start) // hop)
        offsets = np.arange(frames) * hop
    else:
        offsets = np.round(np.asarray(times) * sr).astype(int)
        offsets = offsets[(offsets >= 0) & (offsets < len(x) - start)]
        frames = len(offsets)
    centres = start + offsets
    n = np.arange(length) - length // 2
    # Direct DTFT at each partial frequency: exact, no bin scalloping.
    basis = np.exp(-2j * np.pi * np.outer(n, freqs) / sr) * (w * gain)[:, None]
    z = np.empty((len(freqs), x.shape[1], frames), complex)
    chunk = max(1, int(4e7 // (length * max(1, len(freqs)))))
    for c0 in range(0, frames, chunk):
        idx = centres[c0:c0 + chunk]
        seg = np.stack([y[i:i + length] for i in idx])          # frames, length, ch
        for ch in range(x.shape[1]):
            v = seg[:, :, ch] @ basis                            # frames, partials
            # Reference phase to absolute time so a steady partial keeps a steady phase.
            v *= np.exp(-2j * np.pi * np.outer(idx - start, freqs) / sr)
            z[:, ch, c0:c0 + chunk] = v.T
    return offsets / sr, z


def residual_bands(x, sr, freqs, f1, start, seconds=.5, hop_s=.005, win_s=.02):
    """Third-octave power between partials over time (dB re full scale).

    Bins within 1.5 main-lobe widths of a partial are excluded and each band's
    remaining power is rescaled by the fraction of bins kept; bands that keep
    less than a quarter of their bins are reported as NaN.
    """
    length = int(win_s * sr)
    hop = int(hop_s * sr)
    w = signal.windows.hann(length, sym=False)
    nfft = 1 << int(math.ceil(math.log2(length * 2)))
    hz = np.fft.rfftfreq(nfft, 1 / sr)
    keep = np.ones(len(hz), bool)
    lobe = 2.0 / win_s * 1.5
    for f in freqs:
        keep &= np.abs(hz - f) > lobe
    edges = np.c_[THIRD_OCTAVE * 2 ** (-1 / 6), THIRD_OCTAVE * 2 ** (1 / 6)]
    frames = min(int(seconds / hop_s), (len(x) - start - length) // hop)
    out = np.full((frames, len(THIRD_OCTAVE)), np.nan)
    times = np.arange(frames) * hop_s
    norm = 2 / (nfft * np.sum(w * w))
    for m in range(frames):
        a = start + m * hop - length // 2
        seg = x[max(0, a):a + length]
        if a < 0:
            seg = np.concatenate([np.zeros((-a, x.shape[1])), seg])
        p = np.mean(np.abs(np.fft.rfft(seg * w[:, None], nfft, axis=0)) ** 2, axis=1) * norm
        for j, (lo, hi) in enumerate(edges):
            band = (hz >= lo) & (hz < hi)
            total = band.sum()
            kept = (band & keep).sum()
            if total and kept >= .25 * total:
                out[m, j] = 10 * np.log10(max(np.sum(p[band & keep]) * total / kept, 1e-30))
    return times, out


def window_profile(f1, sr, step):
    """The envelope window's normalised weights on a grid of `step` seconds,
    so a model envelope can be measured the way `envelopes` measures audio."""
    length = window_length(f1, sr)
    w = blackman_harris(length)
    t = (np.arange(length) - length // 2) / sr
    grid = np.arange(math.floor(t[0] / step), math.ceil(t[-1] / step) + 1) * step
    profile = np.interp(grid, t, w, left=0, right=0)
    return grid, profile / profile.sum()


class _WindowedExponentials:
    """The window-measured response of unit complex exponentials e^(s t), t >= 0.

    `envelopes` measures a partial's complex envelope as the window-weighted
    mean of the true envelope around each frame time. The window is held
    constant over each grid cell and the exponential is integrated exactly
    across it, so a rise far shorter than a cell is still measured without
    bias. Once the whole window lies after the onset the sum factors into a
    closed form; frames whose window straddles the onset are summed cell by
    cell from the onset. Returns the responses B and their derivatives D with
    respect to s.
    """

    def __init__(self, tt, grid, profile):
        h = grid[1] - grid[0]
        self.h = h
        half = -grid[0] + h / 2
        self.full = tt >= half
        self.tf = tt[self.full] - half
        self.u = grid - grid[0]                       # cell starts, 0 .. 2 half - h
        self.w = profile / h
        self.wu = self.w * self.u
        centre = tt[~self.full][:, None] + grid[None, :]
        self.a = np.maximum(centre - h / 2, 0.0)       # each cell from the onset on
        self.length = np.maximum(centre + h / 2 - self.a, 0.0)
        self.n = len(tt)

    @staticmethod
    def _cell(s, length):
        """(e^(s L) - 1) / s and its derivative in s, stable for small s L."""
        e = np.expm1(s * length) / s
        return e, (length * np.exp(s * length) - e) / s

    def __call__(self, s):
        B = np.empty((self.n, len(s)), complex)
        D = np.empty_like(B)
        e, de = self._cell(s, self.h)
        eu = np.exp(np.outer(self.u, s))
        s0, s1 = self.w @ eu, self.wu @ eu
        et = np.exp(np.outer(self.tf, s))
        B[self.full] = et * (s0 * e)
        D[self.full] = et * (self.tf[:, None] * s0 * e + s1 * e + s0 * de)
        if not self.full.all():
            sa = self.a[:, :, None] * s[None, None, :]
            ea = np.exp(sa)
            ce, cde = self._cell(s[None, None, :], self.length[:, :, None])
            cell = ea * ce
            B[~self.full] = np.einsum('g,pgk->pk', self.w, cell)
            D[~self.full] = np.einsum('g,pgk->pk', self.w, self.a[:, :, None] * cell + ea * cde)
        return B, D


def fit_partial(times, power_db, floor_db, f1, sr):
    """Fit one partial's stereo-mean power envelope, through the measuring window.

    The model is a prompt and a late exponential, a second late component
    offset by `beat` Hz (unison and polarisation beating) and a rise component
    that cancels their sum at t = 0 and dies with time constant `rise`; zero
    before t = 0. `times`/`power_db` come from `envelopes` (frame times after
    string contact, any spacing). Returns the seven parameters (amplitudes
    linear, rates 1/s, beat Hz, rise s) and the fit's dB error, or None when
    fewer than six frames stand clear of the floor. Its rates seed the joint
    fit across layers.
    """
    sel = _layer_frames(times, power_db, floor_db)
    if sel is None:
        return None
    end = times[int(np.flatnonzero(power_db > floor_db + 8)[-1])]
    tt, yy = times[sel], power_db[sel]
    length = window_length(f1, sr) / sr
    grid, profile = window_profile(f1, sr, min(.002, length / 24))
    response = _WindowedExponentials(tt, grid, profile)
    to_db = 10 / math.log(10)

    def unpack(v):
        cp, cl, cb = math.exp(v[0]), math.exp(v[1]), math.exp(v[2])
        el, er = math.exp(v[4]), math.exp(-v[6])
        c = np.array([cp, cl, cb, -(cp + cl + cb)], complex)
        s = np.array([-(math.exp(v[3]) + el), -el, -el + 2j * math.pi * v[5], -er])
        return c, s

    cache = {}

    def evaluate(v):
        key = tuple(v)
        if key not in cache:
            cache.clear()
            c, s = unpack(v)
            B, D = response(s)
            m = B @ c
            power = np.maximum(np.abs(m) ** 2, 1e-30)
            cache[key] = (c, s, B, D, m, power)
        return cache[key]

    def res(v):
        *_, power = evaluate(v)
        return to_db * np.log(power) - yy

    def jac(v):
        c, s, B, D, m, power = evaluate(v)
        dm = np.empty((len(m), 7), complex)
        dm[:, 0] = c[0] * (B[:, 0] - B[:, 3])
        dm[:, 1] = c[1] * (B[:, 1] - B[:, 3])
        dm[:, 2] = c[2] * (B[:, 2] - B[:, 3])
        dm[:, 3] = -math.exp(v[3]) * c[0] * D[:, 0]
        dm[:, 4] = -math.exp(v[4]) * (c[0] * D[:, 0] + c[1] * D[:, 1] + c[2] * D[:, 2])
        dm[:, 5] = 2j * math.pi * c[2] * D[:, 2]
        dm[:, 6] = math.exp(-v[6]) * c[3] * D[:, 3]
        return 2 * to_db * np.real(np.conj(m)[:, None] * dm) / power[:, None]

    k0 = int(np.argmax(yy))
    amp0 = 10 ** (yy[k0] / 20)
    after = tt > max(.5, tt[k0])
    sl0 = .3 if after.sum() < 4 else max(.02, -np.polyfit(tt[after], yy[after], 1)[0] / 8.686)
    lower = [-30, -30, -30, math.log(.05), math.log(.005), -6, math.log(2e-4)]
    upper = [3, 3, 3, math.log(400), math.log(60), 6, math.log(.4)]
    best = None
    for prompt_share, beat0, rise0 in ((.5, .3, .005), (.1, .8, .015), (.8, .1, .002), (.3, 1.5, .04)):
        v0 = np.clip([math.log(amp0 * prompt_share + 1e-9), math.log(amp0 * (1 - prompt_share) + 1e-9),
                      math.log(amp0 * .15 + 1e-9), math.log(max(sl0 * 3, .5)), math.log(sl0), beat0,
                      math.log(rise0)], np.add(lower, 1e-9), np.subtract(upper, 1e-9))
        try:
            fit = optimize.least_squares(res, v0, jac=jac, loss='soft_l1', f_scale=1.0, max_nfev=200,
                                         bounds=(lower, upper), x_scale='jac')
        except ValueError:
            continue
        if best is None or fit.cost < best.cost:
            best = fit
    if best is None:
        return None
    v = best.x
    r = res(v)
    return {'prompt': math.exp(v[0]), 'late': math.exp(v[1]), 'beat_amp': math.exp(v[2]),
            'sp': math.exp(v[3]) + math.exp(v[4]), 'sl': math.exp(v[4]), 'beat': float(v[5]),
            'rise': math.exp(v[6]), 'rmse_db': float(np.sqrt(np.mean(r * r))), 'end_s': float(end),
            'frames': int(len(tt))}


def _fit_frames(times, power_db, floor_db, end):
    """The frames a fit weighs: at most 150 before 0.3 s, where the attack and
    the knee carry the rise and the prompt decay, and at most 150 after, where
    the tail carries the late rates and the beats."""
    sel = np.flatnonzero((times <= end) & (power_db > floor_db + 3))
    early, late = sel[times[sel] < .3], sel[times[sel] >= .3]
    if len(early) > 150:
        early = early[np.unique(np.round(np.linspace(0, len(early) - 1, 150)).astype(int))]
    if len(late) > 150:
        late = late[np.unique(np.round(np.linspace(0, len(late) - 1, 150)).astype(int))]
    return np.r_[early, late]


# --- Joint calibration of one recorded pitch across its velocity layers -----
#
# A partial is the sum of a few normal modes of the unison strings and their
# two polarisations. Their rates and frequencies are properties of the strings
# and the bridge, the same at every velocity; the hammer sets only how much of
# each is excited, and each microphone hears its own mixture. So one partial is
# fitted across all layers at once: four lanes with shared complex rates
# (decay and frequency offset) under one shared, velocity-dependent rise
# 1 - e^(-t/rise) that starts them from zero, and per layer and channel a
# complex amplitude per lane. Four lanes hold a prompt decay, a beating pair
# and the treble's slow aftersound together; three had to drop one of them.

LANES = 4


def lane_complex_rates(theta, velocity):
    """Complex rates of the lanes and the rise rate at one MIDI velocity."""
    rise = math.exp(theta[2 * LANES] + theta[2 * LANES + 1] * (velocity - 64) / 64)
    return -np.exp(theta[:LANES]) + 2j * math.pi * np.asarray(theta[LANES:2 * LANES]), 1 / rise


def _tail_rate(L):
    """Late amplitude decay rate (1/s) from the frames after 1 s clear of the floor."""
    t, p = L['times'], L['power_db']
    m = (t > 1.0) & (p > L['floor_db'] + 10)
    if m.sum() < 8:
        return None
    return max(.003, -stats.theilslopes(p[m], t[m])[0] / 8.686)


def _layer_frames(times, power_db, floor_db):
    live = power_db > floor_db + 8
    if live.sum() < 6:
        return None
    end = times[int(np.flatnonzero(live)[-1])]
    sel = _fit_frames(times, power_db, floor_db, end)
    return sel if len(sel) >= 6 else None


def fit_partial_layers(layers, f1, sr, n, hz, beat=.3, ridge=.03):
    """Fit one partial jointly across velocity layers.

    `layers` is a list of dicts with `times` (seconds after that layer's
    string contact), `z` (channels x frames complex envelope), `power_db`,
    `floor_db` and `velocity`. Each frame is weighted by the inverse of the
    envelope's largest value within `beat` seconds plus the partial's floor,
    so the whole decay is fitted in relative terms down to the floor, frames
    near the floor count as the noise they hold, and a null between unison
    beats weighs as the beat around it. (Weights capped 20 dB below the peak
    left the treble's slow aftersound to the noise: C6's fitted tails fell
    20 dB/s faster than the recordings'.)
    Each lane amplitude also costs `ridge` times its size relative to the
    layer's peak: without it, two lanes can merge into a cancelling pair of
    huge amplitudes that only float64 arithmetic reproduces, and that no
    interpolation between pitches survives.
    Returns theta (four lane log rates, four lane offsets in Hz, the log rise
    at velocity 64 and its slope), per-layer amplitudes a[layer, channel,
    lane] and per-layer relative errors (of the envelope alone), or None.
    """
    length = window_length(f1, sr) / sr
    grid, profile = window_profile(f1, sr, min(.002, length / 24))
    prepared = []
    for L in layers:
        sel = _layer_frames(L['times'], L['power_db'], L['floor_db'])
        if sel is None:
            prepared.append(None)
            continue
        tt = L['times'][sel]
        amp = 10 ** (L['power_db'][sel] / 20)
        local = np.array([amp[np.abs(tt - s) <= beat].max() for s in tt])
        w = 1 / (local + 10 ** (L['floor_db'] / 20))
        w /= math.sqrt(len(sel))
        zw = L['z'][:, sel] * w
        prepared.append({'response': _WindowedExponentials(tt, grid, profile), 'w': w,
                         'z': np.hstack([zw, np.zeros((len(zw), LANES))]), 'frames': len(sel),
                         'penalty': ridge / amp.max(), 'velocity': L['velocity']})
    used = [p for p in prepared if p is not None]
    if len(used) < 2:
        return None
    count = 2 * LANES + 2

    def evaluate(theta, jacobian=False):
        """Residuals of the variable projection and, optionally, their exact
        Jacobian with the amplitudes re-solved (Golub and Pereyra)."""
        res, amps, jac = [], [], []
        for p in used:
            x = (p['velocity'] - 64) / 64
            s, rho = lane_complex_rates(theta, p['velocity'])
            B, D = p['response'](np.r_[s, s - rho])                     # e^(st) and e^((s-rho)t)
            w = p['w'][:, None]
            X = np.vstack([(B[:, :LANES] - B[:, LANES:]) * w, p['penalty'] * np.eye(LANES)])
            q, r_ = np.linalg.qr(X)
            a = np.linalg.solve(r_, q.conj().T @ p['z'].T)              # lanes x channels
            r = X @ a - p['z'].T
            res.append(r)
            amps.append(a.T)
            if jacobian:
                F = p['frames']                                           # the penalty rows are constant
                dX = np.zeros((count,) + X.shape, complex)
                both = D[:, :LANES] - D[:, LANES:]
                for k in range(LANES):
                    dX[k, :F, k] = -math.exp(theta[k]) * both[:, k]
                    dX[LANES + k, :F, k] = 2j * math.pi * both[:, k]
                dX[2 * LANES, :F] = -rho * D[:, LANES:]
                dX[2 * LANES + 1, :F] = -x * rho * D[:, LANES:]
                dX[:, :F] *= w[None]
                v = dX @ a                                                # params x frames x channels
                v -= q[None] @ (q.conj().T[None] @ v)
                # Golub-Pereyra's second term: how re-solving the amplitudes
                # moves the residual. Kaufman's approximation drops it.
                g = np.conj(np.swapaxes(dX, 1, 2)) @ r                    # params x lanes x channels
                v -= q[None] @ np.linalg.solve(np.conj(r_.T)[None], g)
                jac.append(v)
        if jacobian:
            return res, amps, jac
        return res, amps

    def residual(theta):
        res, _ = evaluate(theta)
        r = np.concatenate([x.ravel() for x in res])
        return np.r_[r.real, r.imag]

    def jacobian(theta):
        _, _, jac = evaluate(theta, True)
        j = np.concatenate([v.reshape(count, -1) for v in jac], axis=1).T
        return np.r_[j.real, j.imag]

    # Start from the stereo-mean power fits and late slopes of the loudest layers.
    starts, tails = [], []
    for p, L in sorted(((p, L) for p, L in zip(prepared, layers) if p is not None),
                       key=lambda pl: -pl[1]['velocity'])[:3]:
        fit = fit_partial(L['times'], L['power_db'], L['floor_db'], f1, sr)
        if fit:
            starts.append(fit)
        tail = _tail_rate(L)
        if tail is not None:
            tails.append(tail)
    if not starts:
        return None
    sp = float(np.median([s['sp'] for s in starts]))
    sl = float(np.median([s['sl'] for s in starts]))
    beat = float(np.median([abs(s['beat']) for s in starts]))
    rise = float(np.median([s['rise'] for s in starts]))
    slow = min(float(np.median(tails)) if tails else sl / 3, sl)
    # Lanes may sit a few cents from the measured partial (unison strings).
    span = max(2.5, .2 * n, .0017 * hz)
    lower = [math.log(.003)] * LANES + [-span] * LANES + [math.log(2e-4), -3.0]
    upper = [math.log(500)] * LANES + [span] * LANES + [math.log(.5), 3.0]
    best = None
    for sign in (1.0, -1.0):
        # The beating pair at the late rate, or at the slow tail's.
        for rates, offsets in (((sp, sl, sl, slow), (0, 0, sign * beat, 0)),
                               ((sp, sl, slow, slow), (0, 0, 0, sign * beat))):
            theta0 = np.clip([math.log(r) for r in rates] + list(offsets) + [math.log(rise), 0.0],
                             np.add(lower, 1e-6), np.subtract(upper, 1e-6))
            try:
                fit = optimize.least_squares(residual, theta0, jac=jacobian, bounds=(lower, upper), max_nfev=200,
                                             x_scale=[1] * LANES + [.1] * LANES + [1, 1])
            except (ValueError, np.linalg.LinAlgError):
                continue
            if best is None or fit.cost < best.cost:
                best = fit
    if best is None:
        return None
    res, amps = evaluate(best.x)
    out_amps, errors, k = [], [], 0
    for p in prepared:
        if p is None:
            out_amps.append(None)
            errors.append(None)
            continue
        r, z = res[k][:p['frames']], p['z'][:, :p['frames']]
        errors.append(float(np.vdot(r, r).real / max(np.vdot(z, z).real, 1e-30)))
        out_amps.append(amps[k])
        k += 1
    return {'theta': best.x, 'amplitudes': out_amps, 'relative_error': errors}


def layer_partial_waveform(theta, amplitudes, velocity, hz, sr, samples, delay):
    """Both channels of one jointly fitted partial, from the detected onset;
    the lanes start `delay` seconds later, at string contact."""
    t = np.arange(samples) / sr
    tau = t - delay
    on = tau >= 0
    tau = np.where(on, tau, 0.0)
    s, rho = lane_complex_rates(theta, velocity)
    lane = np.exp(np.outer(tau, s)) * ((1 - np.exp(-rho * tau)) * on)[:, None]
    carrier = np.exp(2j * math.pi * hz * t)
    return np.real((lane @ amplitudes.T) * carrier[:, None])


def envelope_floor(times, power_db, decaying_db_s=2.0):
    """Each partial's measurement floor (dB): the mean power of its last
    quarter, once the partial has sunk into the recording's noise there.

    Noise measured through a short window has exponentially distributed
    power, so its 2nd percentile lies some 17 dB below its mean and frames of
    pure noise would pass as signal; the mean is the median plus 1.6 dB. A
    partial still falling by more than `decaying_db_s` over its last quarter
    has not reached the noise: the treble files end a few seconds after the
    strike, and their quietest frames are the tail itself. Its floor is put
    10 dB below those frames, so the whole tail counts.
    """
    late = times >= times[-1] - .25 * (times[-1] - times[0])
    floor = np.empty(len(power_db))
    for k, p in enumerate(power_db):
        if stats.theilslopes(p[late], times[late])[0] < -decaying_db_s:
            floor[k] = p[late].min() - 10
        else:
            floor[k] = 10 * np.log10(np.median(10 ** (p[late] / 10)) + 1e-30) + 1.6
    return floor


def contact_delay(x, sr, start, window=.15, drop_db=20.0):
    """Delay (s) from the detected onset to string contact.

    The detected onset fires on the first audible sound, which in the middle
    and treble is the key and action a few milliseconds before the hammer
    reaches the strings. Contact is taken where the 1 ms stereo power first
    comes within `drop_db` of its peak over the next `window` seconds; in the
    bass, whose partials build up over several periods, that is the start of
    the build-up, which the partials' rise then follows.
    """
    power = ndimage.uniform_filter1d(np.mean(x * x, axis=1), max(3, int(.001 * sr)), mode='constant')
    seg = power[start:start + int(window * sr)]
    k = int(np.flatnonzero(seg >= seg.max() * 10 ** (-drop_db / 10))[0])
    return max(0.0, k / sr - .0005)


def analyse_anchor(paths, note, velocities, residual_seconds=1.0, horizon_max=16.0, min_layers=3):
    """Calibrate one recorded pitch from its velocity layers (see above).

    Returns the layers' measurements, the jointly fitted partials and, per
    layer, the residual left in the recording once every fitted partial is
    subtracted: the hammer knock, the body and the action, plus whatever the
    partial model misses.
    """
    layers = []
    for path, velocity in zip(paths, velocities):
        sr, x = load(path)
        start = onset(x, sr)
        f1, B, found = partials(x, sr, note, start)
        duration = (len(x) - start) / sr
        # The library fades every file out over its last seconds.
        horizon = min(horizon_max, duration - max(1.0, .25 * duration) if duration > 8 else duration - 1.0)
        seg = x[start + int(.05 * sr):start + int(.75 * sr)]
        layers.append({'path': str(path), 'x': x, 'sr': sr, 'start': start, 'f1': f1, 'B': B, 'found': found,
                       'velocity': velocity, 'horizon': horizon, 'duration': duration,
                       'early_rms_db': float(10 * np.log10(np.mean(seg ** 2) + 1e-30))})
    sr = layers[0]['sr']
    by_order = {}
    for L in layers:
        for q in L['found']:
            by_order.setdefault(q['n'], []).append(q['hz'])
    orders = sorted(n for n, hz in by_order.items() if len(hz) >= min(min_layers, len(layers)))
    freqs = np.array([float(np.median(by_order[n])) for n in orders])
    f1 = float(np.median([L['f1'] for L in layers]))
    length = window_length(f1, sr) / sr
    hop = float(np.clip(length / 8, .0005, .005))
    for L in layers:
        times = np.r_[np.arange(0, .5, hop), np.arange(.5, L['horizon'], .02)]
        t, z = envelopes(L['x'], sr, freqs, f1, L['start'], None, times=times)
        power_db = 10 * np.log10(np.maximum(np.mean(np.abs(z) ** 2, axis=1), 1e-30))
        floor = envelope_floor(t, power_db)
        delay = contact_delay(L['x'], sr, L['start'])
        L.update({'times': t - delay, 'z': z, 'power_db': power_db, 'floor_db': floor, 'delay': delay})
    fits = []
    for k, n in enumerate(orders):
        fits.append(fit_partial_layers([{'times': L['times'], 'z': L['z'][k], 'power_db': L['power_db'][k],
                                         'floor_db': L['floor_db'][k], 'velocity': L['velocity']}
                                        for L in layers], f1, sr, n, freqs[k]))
    out_layers = []
    for i, L in enumerate(layers):
        samples = min(len(L['x']) - L['start'], int(residual_seconds * sr))
        residual = L['x'][L['start']:L['start'] + samples].copy()
        for k, fit in enumerate(fits):
            if fit is None or fit['amplitudes'][i] is None:
                continue
            residual -= layer_partial_waveform(fit['theta'], fit['amplitudes'][i], L['velocity'], freqs[k], sr,
                                               samples, L['delay'])
        pre = L['x'][max(0, L['start'] - int(.05 * sr)):L['start']]
        out_layers.append({k: L[k] for k in ('path', 'start', 'f1', 'B', 'found', 'velocity', 'horizon',
                                             'duration', 'early_rms_db', 'delay')}
                          | {'floor_db': L['floor_db'], 'peak_db': L['power_db'].max(axis=1),
                             'residual': residual.astype(np.float32), 'pre_onset': pre.astype(np.float32)})
    return {'note': int(note), 'sr': sr, 'f1': f1, 'orders': orders, 'freqs': freqs, 'fits': fits,
            'layers': out_layers}
