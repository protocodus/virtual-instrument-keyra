# Grand piano POC v2: model, calibration and numerical method

The native model in [src/grand.cpp](src/grand.cpp) generates sound from moving hammers, dispersive string modes and a shared vibrating soundboard. V2 adds measured scalar and modal parameters in [src/calibration.h](src/calibration.h). It loads no audio samples, impulse responses or neural weights. Recordings serve as offline calibration and benchmark data.

Calibration targets one acoustic piano recording set, not a unique physical reconstruction of that piano. The geometry, contact law and coupled soundboard remain reduced approximations. This document distinguishes the mechanical simulation from the empirical output observation. [BENCHMARK.md](BENCHMARK.md) describes the locked training/held-out split and measured results.

## Strings and tuning

All 88 keys, MIDI 21–108, remain in the simulation, including unstruck strings. There are 230 strings: single strings through MIDI 31, pairs through MIDI 43 and three strings per key above that. Each string has two transverse polarizations. The primary polarization retains at most 320 modes below 19 kHz; the weaker secondary retains at most 48 below 9 kHz. The exact count depends on the calibrated frequencies; the current mechanical calibration has 17,778 string modes. The secondary polarization has a small frequency offset and lighter intrinsic loss. This is not a three-dimensional string solver.

For mode number n, fundamental f₁ and inharmonicity B:

```text
fₙ = n f₁ sqrt((1 + B n²) / (1 + B))
```

The normalization preserves the requested first partial. V2 fits fundamental and B at C2–C6 from the two training velocity layers, then interpolates across the keyboard. Positive quantities use logarithmic interpolation where appropriate; tuning offsets use cents. Extrapolation outside the anchors is bounded. Bass inharmonicity has an explicit rising extrapolation rather than a free fit to the edge recording. Detuned unisons remain deterministic. Their scale is register-dependent.

String length, mass, hammer mass and felt exponent retain authored C2/C4/C7 anchors informed by [van Walstijn et al. (2023)](https://www.dafx.de/paper-archive/2023/DAFx23_paper_18.pdf). They are not separately identified from the recordings.

Coordinates are mass-normalized. With pₙ = q̇ₙ/ωₙ:

```text
Eₙ = ½ ωₙ² (qₙ² + pₙ²)
```

Free steps rotate (q,p) using precomputed sine/cosine values. Passive velocity damping is split around that rotation. This avoids the frequency warping of a basic finite-difference oscillator. Modes retain their state between strikes.

## Nonlinear hammer contact

A note-on launches a hammer mass with a continuous velocity curve:

```text
v_hammer = 0.22 + 5.6 (MIDI_velocity / 127)^exponent
```

The calibrated exponent varies by register. It is an empirical mapping from performance input to hammer speed, not a measurement of the recording hammer's speed. No velocity layer is played back.

The hammer sees a weighted average of choir displacement. Both displacement and reciprocal force use the same 1/C factor for C unison strings. The spatial weighting is a sine mode shape times a Gaussian contact footprint, approximately 10 mm in the bass to 5 mm in the treble. Secondary-polarization hammer excitation is weak. A single averaged contact does not represent separate compression states or contact times for individual strings.

Positive compression δ has potential:

```text
Φ(δ) = K max(δ,0)^(r+1) / (r+1)
F_DG = (Φ(δ_next) − Φ(δ)) / (δ_next − δ)
F = F_DG max(0, 1 + α (δ_next − δ)/dt)
```

The equal-argument limit is used for F_DG. Compression depends on this force through the hammer and string compliances, so a scalar bracketed bisection solves the implicit contact equation. The constant force is integrated through the oscillator and hammer motions. The nonnegative Hunt–Crossley factor prevents adhesive forces and introduces dissipation. The implementation uses a discrete gradient, not the 2023 paper's energy-quadratization method.

Felt stiffness initially corresponds to roughly 8–16 N at 1 mm compression, with a multiplicative calibration parameter. The current fitting does not identify a complete hammer force curve. This is **not [Stulov's hereditary felt model](https://doi.org/10.1121/1.411912)**: there is no felt relaxation-memory state.

## Two-stage decay and passive common-unison loss

Training recordings supply robust early and late partial decay slopes. The mechanical fitter estimates up to 64 partial losses at each of five anchors, rejects weak or unreliable slopes and regularizes the logarithmic loss curves. Missing values fall back to smooth authored priors. Above the measured range, losses are extrapolated with explicit bounds. A fitted exponential slope is not a claim that the actual recording decays exponentially for its full duration.

Late loss is divided between intrinsic string damping and bridge participation. For an isolated primary mode, intrinsic damping uses 0.82 of the fitted late rate and the port weight uses the remaining 0.18. The secondary polarization has lighter intrinsic and port loss. These fractions do not guarantee the exact target decay in the complete coupled system.

A new dissipative port acts on primary modes with the same harmonic index across a key's unison strings. Let vᵢ = ωᵢpᵢ and N be the number of participating strings:

```text
rate = max(sigma_prompt − sigma_late, 0) × loss_control
γ = (1 − exp(−2 rate dt)) / N
vᵢ ← vᵢ − γ Σⱼ vⱼ
```

This contracts the common velocity while preserving zero-sum relative velocities in this operator. It cannot increase modal kinetic energy. Combined with detuning, the common motion decays faster while relative motion can persist, producing a more flexible two-stage envelope. The collective damping is phenomenological; it is not a measured complex admittance of a real bridge.

## Reciprocal bridge and analytic soundboard

Each string exposes a weighted modal velocity v_s and connects to one of three soundboard ports v_b through:

```text
F_s = −R_s (v_s − v_b),    R_s ≥ 0
```

The board receives the opposite force. Coupling power is −R_s(v_s−v_b)². An implicit midpoint junction reduces to a 3×3 Schur-complement solve, followed by reciprocal impulses to string and board modes. This permits energy transfer into unstruck strings and back without an active feedback junction.

The shared network couples unisons and polarizations. It differs from the one-way secondary-resonator approximation in [Bank, Zambon and Fontana (2010)](https://home.mit.bme.hu/~bank/publist/taslp10.pdf). It approximates terminal mobility rather than imposing an exact moving-end boundary condition. Detailed bridge torsion and location-specific horizontal/vertical admittances are omitted.

The soundboard remains an authored orthotropic plate approximation. Effective dimensions are 2.02×1.32 m, areal mass parameter 3.65, and bending parameters Dₓ=1800, Dᵧ=180 and Dₓᵧ=300. Shifted indices, small frequency perturbations and a correction f→sqrt(f²+70²) modify the plate formula.

The selector considers a 60×48 grid, rejects modes at or above 13 kHz, keeps all below 1.2 kHz and retains the first candidate in each occupied 32 Hz band above that. It keeps **475 of 1,398 candidates**, spanning **75.34–12,992.36 Hz**: 112 lower modes and 363 higher-band representatives. Discarded modes' weights are not aggregated. This is not a mobility-preserving reduction or a finite-element identification.

Port weights are 0.55 sin(mπx_g) sin(nπy_g). Board damping and two observation weights remain authored. [Boutillon and Ege (2013)](https://arxiv.org/abs/1305.3057) supplies context for measured soundboard behavior, not calibration data for this board.

## Calibrated radiation observation

The physical board produces a stereo acceleration proxy:

```text
y_board,c = Σₘ (−ωₘ²qₘ − 2σₘωₘpₘ + F_bridge,m) wₘ,c
```

Including driving force and damping preserves the forced response. V2 computes the continuous-frequency transfer of this same loaded board to construct a modal output correction. For angular frequency ω, modal bridge weights dₘg and microphone weights wₘc:

```text
Zₘ = ωₘ² − ω² + i 2σₘω
Y_gh = iω Σₘ dₘg dₘh / Zₘ
T_cg = −ω² Σₘ wₘc dₘg / Zₘ
H = T (I + R Y)^−1
```

R is the diagonal total string-port resistance for each bridge group. For a string mode with bridge participation b and port resistance R_s, its analytic steady-state output coefficient is C_base = iω R_s b H. Since p = −A sin(ωt) for q = A cos(ωt), its real output is Re(C_base)q + Im(C_base)p.

The calibration supports separate primary/secondary target magnitudes of H for up to 64 partials at each anchor. Interpolation uses decibels, retaining the analytic phase and stereo relationship. The ratio between target and analytic stereo RMS magnitude is bounded to 0.025–40; above the last fitted partial the correction fades towards unity. The final observation is:

```text
y_c = y_board,c + Σₙ [Re(ΔCₙc)qₙ + Im(ΔCₙc)pₙ]
ΔC = C_base (target_magnitude / analytic_magnitude − 1)
```

This correction changes the **observation**, not mechanical forces or stored energy. Equivalently, the model retains the board's transient residual and replaces the steady modal projection with a calibrated one. Applying a steady-state transfer during the attack is approximate. These magnitudes absorb errors in geometry, radiation, polarization balance and microphone response; they cannot uniquely identify each physical cause. There is no boundary-element radiation simulation or calibrated sound-pressure unit.

The fitting stage uses both training velocities at each anchor and four fixed time windows. It estimates bounded positive primary/secondary gains from the stereo band-power and cross-power of three rendered stems, keeping the transient coefficient fixed. Log-frequency and register regularization smooth the absolute target magnitudes, followed by joint refinement with smoothness priors. Weak or poorly identifiable observations are downweighted; the secondary profile uses a training-derived prior where evidence is sparse. [benchmark/radiation_fit.json](benchmark/radiation_fit.json) records the training IDs, gain bounds, fit diagnostics and stem hashes. Its internal fit errors are distinct from the benchmark MAE and do not replace held-out rendering.

`--stem-prefix` exports primary, secondary and transient components whose sum reconstructs the output. The generated header's `radiationEnabled` controls whether the projection correction is active. The delivered candidate has this correction enabled. [Its render manifest](benchmark/candidate/render-manifest.json) freezes the source, header and executable; [BENCHMARK.md](BENCHMARK.md) reports the held-out improvements and regressions.

## Pedal, output and numerical validation

Continuous pedal and key release control additional modal damper loss. Pedal changes smooth over approximately 12 ms and damper engagement over 22 ms; MIDI 89 and above have no damper. A repeated note retains vibrating strings and launches another hammer. A returning hammer is removed by a virtual backcheck. Action, escapement and individual damper contact geometry are not simulated.

The reference acquisition pedal state is unknown, so pedal and sympathetic strength have no recording-based validation here. `--no-sympathetic` disconnects time-domain ports of never-struck keys, while the analytic observation is still built with the full loading; it is an exploratory ablation, not an exact independently calibrated acoustic transfer.

A 24 Hz high-pass follows the output observation. Musical masters target 192 kHz internal synthesis and 48 kHz exported audio; isolated-note benchmarks use 96 kHz internally. Decimation, common export gain and optional procedural room belong to the separate Python pipeline. Native output is floating point with arbitrary gain.

The numerical probes test contact residual/energy, passive bridge exchange, common-unison contraction, preservation of relative unison motion, analytic loaded-board transfer and the observation sign convention. The [v2 probe](validation/v2_physics.json) passes with radiation enabled: no random-state energy increase in the common-unison operator, loaded-transfer error below 2×10⁻¹⁵, finite projection coefficients for all 17,778 modes and zero mechanical-energy change on rebuilding the observation. These establish implementation behavior. They do not establish acoustic indistinguishability. The complete source and calibration hashes must accompany validation of a finished candidate.

A [sample-rate check](validation/rate-convergence.json) compares one training note, C4 at layer 12, without refitting. The current binary at 96 kHz is bit-identical to the frozen benchmark render; the 96/192 kHz render-to-render differences are 0.0135 dB log-band MAE, 0.0191 dB partial-level MAE and 0.0031 dB envelope MAE. This checks one note only and does not establish convergence across all notes, dynamics or pedal states.

## Remaining limits

Recordings now constrain tuning, inharmonicity, decay and output magnitude, but they do not identify hammer force curves, full bridge admittance or acoustic radiation independently. The fitted data covers one piano and microphone setup. There is no blind listening study. A [2024 physics-informed differentiable piano study](https://www.frontiersin.org/journals/signal-processing/articles/10.3389/frsip.2023.1276748/full) is relevant research context; this implementation does not use its network or claim to reproduce its training method.

Missing phenomena include longitudinal and phantom partials, amplitude-dependent geometric nonlinearity and pitch glide, duplex/aliquot strings, individual choir contacts, hereditary felt memory, una-corda mechanics, action/pedal noise, detailed damper geometry and frequency-dependent propagation around the rim and lid. [Chabassier, Chaigne and Joly (2014)](https://doi.org/10.1051/m2an/2013136) describes a much fuller coupled string/plate/air formulation. Extra complexity should be justified by controlled comparisons, especially at the keyboard extremes and under pedal.
