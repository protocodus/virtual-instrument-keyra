# Waveguide radiation feasibility

The bounded C2/C4 study does **not** support replacing the original string microphone observation with the tested compact filters. Fifty stable, phase-aware IIR fits retain substantial complex response and attack error. No default piano, header, calibration, Reason prototype or recording is changed by this study.

The mechanical coupled-waveguide proof observes the original soundboard acceleration. That output alone omits the calibrated string correction used by the full model. This experiment asks whether a small causal observer can recover that missing contribution from quantities already available at the waveguide ports. It is a numerical comparison with the authored full-model control, not a fit to new recordings or a listening approval.

## Target and available observations

The target is the first choir line's **primary polarization only**, driven by generalized key force, with intrinsic string losses and the damper open. C2 has 152 primary modes and two choir lines; C4 has 53 modes and three lines. The modal force coefficients already contain the original `1/N` choir transformer. The corresponding single waveguide receives `F/N`; no extra output normalization is fitted afterward.

The target pressure is only

```text
correctionL = sum(radQL*q + radPL*p)
correctionR = sum(radQR*q + radPR*p).
```

In the original model `rad` represents `(calibratedRatio - 1)` times the analytic radiation map. Adding `base + rad` while retaining soundboard pressure would count the analytic body contribution twice. This study excludes the body observer and targets the additive correction alone. It does not establish equivalent correction for arbitrary bridge-driven motion, full unison behavior or secondary polarization.

For each modal state after a sample, with rotation coefficients `c,s`, half-step velocity damping `d` and the original exact force coefficients,

```text
A = [ c,     s*d   ]
    [-s*d, c*d*d   ]
b = [forceQ, d*forceP]
H(z) = C * inverse(I - A*z^-1) * b.
```

This is the implemented discrete update; no continuous oscillator approximation is substituted. The original 24 Hz high-pass is applied equally to target and candidate in the comparisons.

The waveguide uses the tracked 32-section C2/C4 configurations, the actual allpass/FIR paths and the passive 2 Hz DC-preserving shelf. Its two accessible observations are fixed-bridge reaction force `R` and contact velocity `v`. With path transfers `p,q,r`, loop `P=p*q*r` and impedance `Z`,

```text
R/F = q*(1-p)/(1-P) / N
v/F = (1-p)*(1-q*r)/(2*Z*(1-P)) / N.
```

The actual C++ impulse traces match these formulas and the modal formula within `3.51e-13` relative to the global transfer peak. Separate math checks also verify the general two-port signs. Contact force remains a runtime excitation; coefficients are numeric filter parameters, never a stored note or full impulse recording.

## Causality and mechanical limits

Bridge reaction cannot reproduce immediate attack by itself. It has at least the outbound integer delay: 238 samples for C2 (4.958 ms) and 50 samples for C4 (1.042 ms). The original correction responds in the same frame as modal force. Allpass dispersion adds frequency-dependent delay. Contact velocity has force feedthrough and supplies an immediate second observation, but both force responses share contact-position zeros. The fit operates on complex forward responses rather than dividing by a nearly zero observation.

A radiation filter also inherits its source string's resonances. Correcting mismatched poles requires additional target dynamics or cancellation, which can erase the intended efficiency benefit. The current C2/C4 profiles originally fit only the first twenty partials. Below 19 kHz their waveguide loop phase crosses 229/59 resonance orders, compared with 152/53 primary modes in the control. These phase-crossing counts are not a complete complex-pole analysis. Pitch, damping, excitation footprint and high-frequency modal count must be considered alongside radiation; matching a low-partial pitch list is insufficient.

## Frozen fit and results

Each observer has a direct term and a shared bank of stable conjugate pole pairs, geometrically spaced from 60 Hz to 14 kHz with Q=2. Real and imaginary filter states have separate real L/R weights. Fits use real regularized least squares on the complex response, with frequency quadrature, the common high-pass and a broad force-power prior `1/(1+(f/5000)^4)`.

The matrix contains one or two inputs, 2/4/8 pole pairs per input, two ridge strengths and zero or 256-sample delayed targets, plus a 16-pair two-input diagnostic: 25 models per key. The 256-sample cases are **delayed-reference fits**, not an implemented pure delay or qualified host latency setting. Their filters may respond before the delayed target; the report measures this leakage. The zero-delay cases are the main comparison. The fitting and validation frequency grids differ, and validation includes impulse, 2 ms force, 0.5 ms force and repeated unequal force pulses without state resets.

| Zero target delay, ridge 0.0001 | C2 complex relative error | C4 complex relative error | C2 2 ms force waveform error | C4 2 ms force waveform error |
| --- | ---: | ---: | ---: | ---: |
| Reaction, 8 pairs | 0.937 | 0.988 | 0.835 | 0.873 |
| Reaction + contact, 8 pairs | 0.901 | 0.964 | 0.511 | 0.496 |
| Reaction + contact, 16 pairs | 0.863 | 0.963 | 0.450 | 0.479 |

Complex error is weighted complex L2 error divided by target L2, evaluated on the separate frequency grid. Waveform error is the same ratio over the one-second high-passed force response, with no gain matching. These are errors of the isolated correction, not percentages of full-piano sound quality.

High-Q poles make pointwise complex comparison particularly sensitive to small pitch or decay differences: comparing a resonance with a nearby off-resonance value can produce a large complex error even when their pitches are close. The 86–96% figures alone imply no audibility judgment. Corresponding resonance pitch and relative L/R gain/phase, attack-band power and time envelopes must also be inspected. The best 16-pair diagnostics still have prominent-frequency phase MAE near 68 degrees. C4's 2 ms-force first-100-ms third-octave magnitude MAE reaches 2.79 dB, while its waveform error over that attack remains 0.644. The two-input 8-pair C4 observer changes the side/mid energy ratio from -21.50 to -15.88 dB. The 16-pair version recovers that aggregate ratio more closely (-21.18 dB), but retains the large waveform error. Spectral magnitude or one stereo summary therefore cannot establish equivalent attack and image. Reports retain separate 0–5, 5–20, 20–100 and 100–900 ms errors, mono error, channel correlation, level ratio, peak and pretarget leakage for every model and fixture.

The post-fit pole-aligned check factors out each system's own modal denominator. It finds each actual complex waveguide pole by solving `p*q*r=1` and compares the corresponding mode residues, rather than sampling one system off its resonance. The first twenty pole errors are max/RMS 0.510/0.264 cents for C2 and 2.448/1.176 cents for C4. Small relative pitch errors in high partials still accumulate phase: the largest C4 difference reaches 281 degrees over 100 ms. No listener judgment follows from that phase decorrelation alone.

The following L/R errors compare the radiation of corresponding natural modes after removing those different pole denominators. They use reference mode-energy weights and exclude modes where either reference channel is more than 50 dB below the largest first-twenty amplitude. All individual mode results and equally weighted summaries remain in the report.

| Zero target delay, two inputs | C2 L/R gain MAE | C2 L/R phase MAE | C4 L/R gain MAE | C4 L/R phase MAE |
| --- | ---: | ---: | ---: | ---: |
| 8 pairs | 5.58 dB | 17.35 degrees | 5.73 dB | 46.18 degrees |
| 16 pairs | 2.79 dB | 10.33 degrees | 2.55 dB | 12.63 degrees |

For the 2 ms force fixture, the 16-pair observers have 5 ms RMS-envelope MAE of 4.04 dB (C2) and 1.68 dB (C4), with no gain fitting. C2's fitted 200–800 ms envelope slope changes from -5.07 to -1.82 dB/s, while C4 changes from -2.52 to -3.00 dB/s. These separate decay/excitation mismatches from the relative L/R observation error. They remain isolated correction diagnostics, with no claim that a complete piano would be perceived as that numerical error.

This family uses fixed geometrically spaced poles. Its failure does not prove that every compact causal IIR or spatial observer must fail. More informative next candidates include shared-pole identification with strict complexity limits, physically positioned traveling-wave taps, or a small retained modal contribution for radiation and high partials. Those need their own complex, time-domain and cost evidence before replacing the current control.

## Cost, setup correction and reproducibility

The scalar observer-only benchmark runs 88 independent C2/C4 filter banks at 48 kHz, three half-second trials. Median CPU seconds per audio second are 0.102 for one input/eight pairs, 0.180 for two inputs/eight pairs and 0.339 for two inputs/sixteen pairs. These exclude all waveguides, board, hammer, mechanisms and host work. They measure a compact filter cost, not a complete piano or Reason deadline. No allocation occurs in the observer step; configuration uses offline vectors and I/O.

Independent implementation checks compare all fifty coefficient sets against the actual C++ observer recurrence over 2,048 synthesized samples; maximum difference is `1.47e-12` relative to each case's global output peak. Every pole radius is below one. The full frozen inputs, coefficients, errors and adverse results are in `out/waveguide-radiation/`; `Validation/waveguide-radiation.json` links their hashes.

The first export accidentally inherited the original constructor's closed-damper coefficients. Review caught that mismatch before any adoption. Its entire frozen run is preserved under `out/waveguide-radiation/v1-closed-damper/` with a scope correction. The current exporter explicitly uses `d=exp(-intrinsicLoss*dt)` for the held-string target and records each intrinsic loss; the independent audit verifies that equality for every mode. The same fitting matrix was rerun after that setup correction.

Reproduce with the commands recorded in the validation report: compile/run `tools/probe_waveguide_radiation.cpp`, then `OPENBLAS_NUM_THREADS=1 python3 tools/fit_waveguide_radiation.py`. `--selfcheck-only` checks the actual-state transfer formulas without fitting. The separate cost tool consumes the generated numeric coefficient files. Research, canonical DSP and all public recording splits remain untouched.
