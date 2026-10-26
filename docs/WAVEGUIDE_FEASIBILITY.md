# Bounded dispersive-string feasibility study

The integer-delay traveling-wave string conserves energy, and the dispersive version has an explicit passive storage and loss ledger. The present low-order dispersion fit is promising for bass and middle strings with many retained partials. It is insufficient in high treble: even the stronger 32-section candidate misses C6's prominent fundamental by 8.36 cents. A hybrid representation using waveguides below a register boundary and the existing modal representation above it deserves investigation. This study does not replace a piano solver or establish sound equivalence.

The preserved `Research/GrandPianoV2` and working `src/full_reference/grand.cpp` are unchanged. The future target remains the connected physical instrument: persistent strings, nonlinear hammer/contact, two polarizations, unisons and their reciprocal loss ports, the three bridge groups, and 475 board modes. This prototype contains one polarization of one string with an interior force port and a prescribed-motion bridge port. It contains no recording, impulse response, sound generator substituted for a mechanical interaction, or hammer mechanism. There is no new piano render, SDK integration, callback deadline test, or Reason readiness claim.

## Files and evidence

- `include/keyra/physics/WaveguideString.h`: fixed-capacity 48 kHz experimental string.
- `tests/waveguide_string_tests.cpp`: integer scattering, allpass/loss storage, repeated force inputs, validation and allocation checks.
- `tools/probe_waveguide_string.cpp`: pole/decay, two-port transfer, admittance and isolated-string workload probe.
- `tools/fit_waveguide_study.py`: bounded offline fit driver and source selection.
- `out/waveguide-study/sections16/` and `sections32/`: fitted configurations, phase-fit reports and final state/pole/workload reports.
- `tools/probe_waveguide_workload.cpp`, `out/waveguide-study/mode-counts.csv` and `hybrid-workload-report.json`: exact source-count and representation workload experiment.
- `out/waveguide-study/provenance.json`: input, source snapshot, executable, fit and report hashes, compiler and host.

The fitter reads only the combined TRAIN feature export and selects `C2v4`, `C4v4` and `C6v4`. It reads no audio and does not open reserved A0/C8 velocity-8 recordings. Fundamental and normalized stiffness are:

| TRAIN row | f1, Hz | B |
|---|---:|---:|
| C2v4 | 65.0142144684 | 0.0001146331552 |
| C4v4 | 261.603870857 | 0.0002802474286 |
| C6v4 | 1050.36444350 | 0.002686841386 |

The target partial formula is `f[n] = n*f1*sqrt((1+B*n*n)/(1+B))`. Up to 20 partials are fitted below the original primary-mode 19 kHz cutoff. C6 has only 14 such targets; omitted higher targets are not aliased into the study. Linear density and length follow the original authored string anchors; `Z = 2*mu*length*f1/sqrt(1+B)` fixes the characteristic impedance in kg/s. These are model priors, not physical dimensions identified from a microphone recording. The corpus and its noise/unison/room/velocity ambiguities remain those documented in `FULL_CALIBRATION.md`.

## Mechanical ports and energy proof

Samples on the rails are traveling velocities in m/s. With sample period `h` and impedance `Z`, every stored rail sample `u` contributes `h*Z*u*u` joules. One path folds the two directions between the contact point and the fixed left end; two identical reciprocal paths connect contact and bridge. Every path contains at least one integer-delay sample, so current outputs are known before the current port solve.

At the equal-impedance interior contact junction, with incoming waves `aL,aR` and applied force `FC`,

```text
u  = FC/(2Z)
vC = aL+aR+u
bL = aR+u
bR = aL+u
Z*(bL²+bR²-aL²-aR²) = FC*vC.
```

At the bridge, prescribed velocity `vB` and incoming wave `aB` give `bB=vB-aB` and force **into the string** `FB=Z*(vB-2aB)`. The force on a board is `-FB`. Here `Z*(bB²-aB²)=FB*vB`. The fixed left end reflects velocity with sign `-1`. Consequently each complete step satisfies

```text
Enew-Eold + dissipated = h*(FC*vC+FB*vB).
```

The sampled velocity is the scattering port velocity used in this identity. Interpreting it as a particular midpoint velocity of the existing hammer/board integrator requires a separate derivation and coupled test.

A force-driven endpoint with the other end fixed would produce free/fixed quarter-wave modes. This study instead excites the interior and sets `vB=0` when fitting the fixed/fixed string modes. The bridge's driving mobility has zeros at those fixed/fixed modes; its poles describe the free/fixed termination. Those are different measurements.

## Dispersion and positive loss

Each first-order allpass is implemented as an orthogonal two-variable scatterer:

```text
y  = c*x + sqrt(1-c²)*q
q' = sqrt(1-c²)*x - c*q
x²+q² = y²+q'²
H(z) = (c+z^-1)/(1+c*z^-1), |c|<1.
```

Its stored state contributes `h*Z*q*q` to energy. This proves numerical passivity of the implemented fractional/dispersion delay; it does not identify that auxiliary energy with the exact bending energy of a stiff string. No generic interpolator is assumed passive.

The loss filter is `y0=(1-alpha)*x+alpha*q`, `q'=x`, followed by `y=g*y0`, with `0<=alpha<=0.5` and `0<=g<=1`. Storage is `h*Z*alpha*q*q`. Positive dissipation is

```text
h*Z * [alpha*(1-alpha)*(x-q)² + (1-g²)*y0²].
```

Thus both the frequency-dependent loss and scalar attenuation have explicit storage accounting. The same forward/return right-path configuration is required at prepare time, preserving reciprocity.

The fit uses 16 or 32 allpass sections per complete roundtrip, divided as 2/7/7 or 4/14/14 between the three paths. Every case uses the controlled contact position `x/length=.12`; the original register-dependent hammer positions are not integrated. Coefficients are fitted in two groups per distinct path, with integer delay selected by a bounded search. Negative coefficients supply a group delay that decreases with frequency. This is a small approximate fit, not a globally optimal passive rational approximation. Loss is fitted afterward and its additional phase is retained in the final pole measurements.

For an explicit positive control, decay is compared against the original authored isolated intrinsic-loss prior

```text
sigma(f) = .11 + .21*(f1/440)^.6 + .000012*f^1.30 + .00000000035*f².
```

This is not the current calibrated common-unison or loaded-board decay and is not an identification of recorded partial-band slopes. Both those interactions are absent from this test.

## Accuracy and loss results

Final frequencies and decay rates come from complex poles of the actual lossy path transfer product. The largest pole-equation residual is below `2e-12`. The state implementation is checked independently against the analytic two-port transfers using exponentially weighted, three-second force and bridge-velocity impulses; maximum relative transfer residual is below `5e-7`.

| Case | Sections/roundtrip | Fundamental error, cents | Max absolute cents | RMS cents | Max relative sigma error |
|---|---:|---:|---:|---:|---:|
| C2, 20 partials | 16 | -0.865 | 1.739 | 0.639 | 6.46% |
| C2, 20 partials | 32 | -0.592 | 0.934 | 0.401 | 6.56% |
| C4, 20 partials | 16 | -2.181 | 6.076 | 2.251 | 19.87% |
| C4, 20 partials | 32 | -1.177 | 2.886 | 1.077 | 20.33% |
| C6, 14 partials | 16 | -14.326 | 33.121 | 14.640 | 23.01% |
| C6, 14 partials | 32 | +8.364 | 18.103 | 8.037 | 27.74% |

The first-five-partial maximum error equals the listed fundamental error magnitude in each case. These errors therefore cannot all be dismissed as weak upper-partial discrepancies. Conversely, an unweighted 20-partial score is not a perceptual objective: in C4v4 the early measured partial-20 band is about -77 dB relative to early RMS power; C6v4 is already about -54 dB by partial 5. C2 retains much stronger upper-partial energy. Future fitting should protect the identifiable, prominent frequencies while keeping all errors visible. No audibility threshold is inferred from these numbers alone.

## Admittance and residue limits

For left-path transmission `p`, right forward `q`, return `r`, and `P=p*q*r`, the independently derived transfers are

```text
Ycc = vC/FC | vB=0 = (1-p)*(1-q*r)/(2Z*(1-P))
Zbb = FB/vB | FC=0 = Z*(1+P)/(1-P)
-FB/FC | vB=0 = q*(1-p)/(1-P)
vC/vB  | FC=0 = r*(1-p)/(1-P).
```

Since `q=r`, the cross transfers agree. The probe compares `Ycc` with an isolated stiff-string sine-mode mobility using the same f1/B, density/length and positive intrinsic losses. It also compares `1/Zbb` against a traveling-line prior using the analytic stiff-string wavenumber and group-delay loss. The latter comparison tests dispersion/termination behavior; it does not supply the missing bending boundary conditions or the original authored modal bridge transformer.

Seven probe frequencies span `0.77,1.13,1.37,2.61,4.31,8.37,12.2` times f1. For the 16-section version, C2's bridge-mobility relative discrepancy stays below 2.6% on that grid; C4 and C6 can reach roughly 46% and 54%. The 32-section version improves those maximum grid discrepancies to about 0.8%, 21% and 20%. A small frequency error near a narrow resonance/antiresonance can produce a large relative response error.

The contact mobility exposes another limit: the grid deliberately includes near-antiresonance ratios 1.13 and 8.37. For example, 32-section C2's 8.37*f1 point is about 16.5 dB below the truncated stiff-modal prediction, despite a sub-cent mode fit. Finite modal bandwidth itself changes antiresonance cancellation, and an allpass line with constant `Z` does not reproduce all stiff-string modal masses/residues. Neither a fitted partial frequency nor a positive energy ledger proves matching bridge or contact admittance. These discrepancies must remain visible before attaching a physical hammer or board.

The original solver's bridge coefficients are authored modal loss/mobility transformers, rather than a literal endpoint slope alone. Equating them to the current waveguide endpoint would change the coupled instrument. A representation change must preserve or approximate those reciprocal driving and observation ports, not merely its free frequencies.

## Computational evidence and hybrid hypothesis

On the recorded host/compiler, strict double arithmetic at 48 kHz gives the following median process CPU seconds per audio second for 230 independent strings. Three trials are taken per case, each advancing 0.25 seconds. These are string-only measurements with one polarization; board, hammer, unison coupling, radiation, resampling, host and synchronization costs are excluded.

| Identical string profile | 16 sections | 32 sections |
|---|---:|---:|
| C2 | 0.390 | 0.636 |
| C4 | 0.385 | 0.615 |
| C6 | 0.357 | 0.612 |

The class currently reserves 100,080 bytes per string (about 22 MiB for 230 strings), most of which is conservative fixed delay capacity. Actual active delay lengths are much smaller. This storage can be packed during a later prepare/layout design; it has not been optimized here.

A separate bounded workload probe instantiates the snapshotted working full reference once and counts its actual primary modes: 230 strings, 12,507 primary modes; 5,271 secondary modes and 475 board modes are explicitly excluded. It compares original double `Modes` rotations and a bridge reduction against the 16-section waveguide workload. Waveguide delays are resized for source frequencies where feasible, using the three existing anchor profiles. This is a computational distribution of work, **not** a fitted 88-key waveguide instrument.

| Representation workload | Median process CPU s/audio s |
|---|---:|
| Existing primary modal strings | 0.919 |
| All 230 strings using 16-section waveguides | 0.366 |
| 119 bass/middle waveguides, modal strings at MIDI >=72 | 0.308 |

The hybrid retains 1,314 primary modes in the upper register. It is cheaper in this workload than giving those few-mode treble strings a large allpass cascade, and preserves the exact modal frequencies there. This supports a per-register representation hypothesis. It does not predict a corresponding whole-piano speedup: the current full solver also does substantial nonlinear contact, secondary-polarization, shared-unison, bridge and radiation work. Average CPU measurements do not establish callback deadline safety.

## Tests, persistence and remaining integration work

The lossless integer-delay test advances eight seconds with exactly zero measured energy drift. Randomized allpass/FIR tests with both ports doing work have a maximum accumulated balance residual of `5.33e-15` J. The three-second transfer probes have energy residuals below `1e-16` J. Address/undefined-behavior sanitizer tests pass. An allocation counter sees no allocations in `step()`; code review finds no locks or I/O there. The prototype neither changes the floating-point environment nor enables fast math.

Every force input advances the existing state. A repeated-force test checks linear superposition with a second force while the first vibration remains active; no per-strike reset is performed. `prepare()` is an explicit reinitialization boundary, not a note-on operation. Arbitrary rail initialization is intentionally absent: an incompatible initial strain can introduce a constant bridge reaction. The present test uses physical port work from an initially resting state. It has no hammer to reset, reposition or teleport.

Before a coupled replacement can be evaluated:

1. Fit the important bass/middle modes and their force/velocity residues, including frequency-dependent impedance or an appropriate passive reciprocal transformer. Improve the bounded rational fit where justified by audible energy; retain sparse modal treble where cheaper and more accurate.
2. Derive the nonlinear hammer's simultaneous force/compression update using the scattering port velocity and positive contact compliance. Validate contact work, repeated strikes, separation and the existing persistent hammer/action state. A force waveform supplied by this probe is not a validated hammer interface.
3. Derive a simultaneous reciprocal solve between all string bridge ports and the existing 475-mode board/three grouped ports. Include all stored allpass/FIR energy and board energy in the ledger. Preserve common-unison loss paths and both polarizations; a feedforward board filter would not satisfy this target.
4. Verify the representation's full port admittance, weak/strong partial behavior, coupled decay/beat patterns and onset response against the preserved modal control. Then measure the entire instrument, repetitions, pedal transitions, dense playing and long tails, with SDK-compatible arithmetic and memory rules.

## Reproduction

From the repository root, with NumPy/SciPy available:

```sh
g++ -O3 -std=c++14 -Wall -Wextra -Wpedantic -ffp-contract=off -Iinclude \
  tests/waveguide_string_tests.cpp -o out/waveguide-study/waveguide_string_tests
out/waveguide-study/waveguide_string_tests

OPENBLAS_NUM_THREADS=1 python3 tools/fit_waveguide_study.py --sections 16
OPENBLAS_NUM_THREADS=1 python3 tools/fit_waveguide_study.py --sections 32

g++ -O3 -DNDEBUG -std=c++14 -Wall -Wextra -Wpedantic -ffp-contract=off -Iinclude \
  tools/probe_waveguide_string.cpp -o out/waveguide-study/keyra_waveguide_probe
out/waveguide-study/keyra_waveguide_probe \
  out/waveguide-study/sections16/C2-s16.cfg \
  out/waveguide-study/sections16/C4-s16.cfg \
  out/waveguide-study/sections16/C6-s16.cfg \
  > out/waveguide-study/sections16/probe-report.json
```

Repeat the last command with `sections32` and `s32` for the second candidate. The original workload used the private source snapshot recorded in the provenance receipt. Its retained reproduction driver builds with C++17 and includes the unchanged `src/full_reference/grand.cpp`; verify that source hash against the receipt before comparing results:

```sh
g++ -O3 -DNDEBUG -std=c++17 -Wno-unknown-pragmas -ffp-contract=off -Iinclude \
  tools/probe_waveguide_workload.cpp \
  -o out/waveguide-study/probe_hybrid_workload
out/waveguide-study/probe_hybrid_workload \
  out/waveguide-study/sections16/C2-s16.cfg \
  out/waveguide-study/sections16/C4-s16.cfg \
  out/waveguide-study/sections16/C6-s16.cfg \
  > out/waveguide-study/hybrid-workload-report.json
```

The original fit/probe/workload reports and provenance receipt are also retained under `Validation/waveguide-*.json`. The copied fit driver changes only input/output path resolution; `--output` can place a fresh reproduction outside the frozen study directory. Root CMake builds `keyra_waveguide_string_tests` and `keyra_waveguide_probe`.

Runtime measurements will vary. Source/calibration snapshots and input/configuration hashes bind the reported experiment; they are not a frozen sound-equivalent instrument candidate.
