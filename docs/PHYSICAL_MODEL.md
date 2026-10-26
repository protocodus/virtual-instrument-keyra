# Passive mechanical candidate

`PhysicalPiano` is a separate research engine. It does not replace the calibrated
live `Piano` model or change its frozen recording results. It implements persistent
string modes, reciprocal string/bridge/soundboard coupling and explicit mechanical
contact ports. It is a foundation for testing connected physical components, not a
claim that all piano parts, materials or recorded timbres have been identified.

## Component boundaries

- `physics/ModalBank.h`: finite, mass-normalized mechanical oscillators, exact
  free rotations, positive velocity loss and reciprocal impulse/force ports.
- `physics/Bridge.h`: the complete simultaneous three-port viscous junction,
  including a discrete energy balance diagnostic.
- `PhysicalPiano`: 88 persistent key banks, up to 32 partials in each of two
  mechanical polarizations per key, selectable 48-mode material or 475-mode
  preserved-reference soundboard,
  dampers, an optional at-string nonlinear hammer and a complex radiation observer.
- Mechanical action and acoustic-load components can connect through the contact
  and board ports. They are not copied into the string solver. Their own physical
  assumptions and energy accounting must be validated independently.

The initial candidate is grand-only. Each key bank represents an aggregate
coherent choir with primary/secondary transverse branches; it does not explicitly
simulate the piano's 230 separate strings, longitudinal waves, duplex strings or
torsional bridge behavior. A repeated strike acts on existing mechanical state;
it does not reset a fresh pressure oscillator.

## Mechanical coordinates and observation

For each mass-normalized mode, with angular frequency omega:

```text
x = omega q,   v = qdot
E = (x² + v²) / 2
```

The free rotation is exact at the chosen sample rate. Positive velocity losses
are split around it; the bridge is a separate passive step. This combination is
unconditionally energy stable for the unforced, fixed-configuration network.
The complete oscillator/junction composition is a first-order split; energy
stability does not establish sample-rate convergence or acoustic accuracy.
Modes above 0.44 times the sample rate or 19 kHz are excluded.

Frequencies and bounded late-loss priors come from the locked grand calibration.
Authored string length, linear mass, contact location and felt footprint define
the contact shape. These inputs do not uniquely identify an actual piano's wire
diameters, tension, winding, hammer or bridge mobility. The parameter units are
mechanical because the modal masses and ports are specified; that does not make
their authored geometry a measured instrument reconstruction.

The primary branch uses prompt loss priors; the secondary uses late loss priors,
a small authored detuning and a bounded weaker hammer/contact participation
(0.035 times the primary). Secondary bridge participation is also weaker. These
losses are empirical recording priors, not independently identified wood or wire
properties. Two branches permit actual fast/slow mechanical states but do not
guarantee that the full reference's unison aftersound has been recovered.

The radiation observer is separate from mechanics. Positive interpolated fixed
magnitude weights use the training anchor's primary/secondary hard-strike
amplitudes and the candidate's reference impulse, with a bounded observation
gain. Their phases come from the loaded mechanical board transfer. For angular
frequency w, board modes define admittance Y and observation T; the three-port
load gives H = T (I + R Y)^-1. In the energy coordinates the source modal
coefficient is C = i R_s b_s H, so y = Re(C) x + Im(C) v. The observer retains
the actual driven board signal and adds the desired-minus-base modal projection,
avoiding double counting its steady response. When the bridge is disconnected,
a fixed nominal board phase remains an observation only, with zero actual base
board contribution. This is a continuous-frequency reduced-board approximation,
not an exact recovery of the full reference's phase or acoustic field.

Observation weights never enter forces, stored energy, damping or the Schur
complement. Turning radiation off or changing complex/real observation mode
leaves mechanical states and energies unchanged. `observeStems()` returns primary,
secondary and board signals from one complete simulation. They reconstruct the
output without separately rerendering or disconnecting components. The additional
`observeQuadratureStems()` exposes positive reference-weight x/v bases for later
offline observation fitting.

These are empirical pressure proxies, not calibrated pascals. The candidate does
not reproduce the live surrogate's fitted attack shaping or
microphone/room output. It needs a new recording evaluation before any sound
quality improvement can be asserted.

## Reciprocal string and soundboard junction

A key's string port has velocity `u_s = sum(b_sj v_sj)`. A board port has velocity
`U_g = sum(d_mg v_bm)`. Each key connects to one of three board groups through:

```text
f_s = -R_s (u_s - U_g),   R_s >= 0
```

The board receives the equal and opposite force. Let `G_s = sum(b_sj²)`,
`H_gh = sum(d_mg d_mh)`, and `h` be the sample interval. Implicit midpoint gives:

```text
a_s = 1 + h R_s G_s / 2
beta_g = sum_in_group(R_s / a_s)
q_g = sum_in_group[-R_s (u_s - U_g) / a_s]
(I + h diag(beta) H / 2) S = q
c = h H S / 2
f_s = -R_s (u_s - U_g + c_g) / a_s
v_sj += h b_sj f_s
v_bm -= h sum_g(d_mg S_g)
```

The Schur matrix is similar to positive definite
`I + h sqrt(beta) H sqrt(beta) / 2`. Only a three-by-three inverse is needed;
it is cached until the port configuration or resistance changes. Keys with no
retained modes have zero resistance and cannot become spurious grounded loads.

The exact discrete power identity is:

```text
delta E = h sum_s[f_s (u_s_mid - U_g_mid)]
        = -h sum_s[R_s (u_s_mid - U_g_mid)²] <= 0
```

The diagnostic accumulates actual impulse work and
`h sum(f_s² / R_s)`, reporting their residual. This is a reciprocal energy transfer
network: exciting strings can excite the board and then unstruck strings; an
initial board impulse can also excite strings. It is not a feed-forward resonance
filter. Disabling the junction isolates string and wood subsystems.

## Contact ports and frame protocol

The contact shape `h_j` defines `y = sum(h_j x_j / omega_j)` and
`ydot = sum(h_j v_j)`. A contact impulse `J` updates `v_j += h_j J` and returns
the mechanical work `J ydot_old + J² sum(h_j²) / 2`.

For a constant contact force over one sample, the exact oscillator response is:

```text
x_j += h_j F (1 - cos(omega_j dt)) / omega_j
v_j += h_j F sin(omega_j dt) / omega_j
C_string = sum[h_j² (1 - cos(omega_j dt)) / omega_j²]
delta E_force = F (y_next - y_old)
```

This gives a nonlinear hammer/contact solver a consistent positive compliance.
The public frame protocol is:

1. `beginFrame()` saves old contact displacements and advances damped free motion.
2. Read `keyPreviousDisplacement`, `keyDisplacement` and `contactCompliance`.
3. Solve an external contact, then call `applyContactForce(note, F)` once.
4. `finishFrame()` completes losses and the reciprocal string/board junction.
5. Apply an independently passive acoustic-load reaction through `boardImpulse`.
6. `observe(left,right)` reads the current mechanical state.

`endFrame` combines finish and observation. `process` supplies frames without an
external action. By default `noteOn` remains an instantaneous perfectly inelastic
hammer collision for isolated mechanical tests. `setNonlinearHammerEnabled(true)`
instead launches a preallocated hammer at a 50 micrometre string gap, avoiding
the separate action module's key-travel latency for a direct physical-note
audition. The existing discrete-gradient `solveContact` finds a nonnegative
constant hammer force using the exact string compliance plus dt²/(2m_hammer).
The same force drives the string and slows the hammer. Hammer kinetic energy and
contact potential are included in `energy()`/`hammerEnergy()`, and the ledger
exposes contact dissipation, numerical residuals and outgoing energy removed by
an authored backcheck/50ms retirement. After launch, the closed conservative
contact conserves energy; its dissipative law can only remove energy.

The at-string hammer is off by default. `PhysicalInstrument` external Action
owns excitation and calls `setKeyDown`, so it does not also launch this internal
hammer. Using both excitation paths for the same key at once is unsupported.
The at-string candidate is a hammer/string experiment, not a replacement for
the complete finger/key/action sequence. Contact-law changes are setup-only and
clear state; mechanical loss and coupling ablations support isolated tests.

## Material inputs and dampers

The board uses published Sitka/Norway spruce bulk moduli and density from
`physics/Materials.h`; provenance is in `References/Materials/sources.json`.
For thickness `t`, reciprocal plane-stress Poisson coefficients give `D11`,
`D22`, `D12`, `D66` and areal mass `rho t`. Modal frequency follows:

```text
f = pi/2 sqrt[(D11 X⁴ + 2(D12 + 2D66)X²Y² + D22 Y⁴) / (rho t)]
```

The 2.02 by 1.32 m geometry, 9.5 mm homogeneous effective thickness, shifted
boundary indices and a positive 70 Hz foundation proxy remain authored. This is
not a crowned, ribbed finite-element soundboard. Modal port normalization also
changes with physical mass. The setup-only material setter rebuilds coefficients
and clears state; it is not a real-time morph or an automated plugin parameter.
No unsupported species-dependent damping factor is introduced.

The current 8-by-6 candidate grid is deliberately a low-frequency body study:
its 48 Sitka modes span **72.25–491.42 Hz**, and the Norway configuration spans
**73.03–560.09 Hz**. It has no modes above 1.2 kHz. In particular, it cannot
reproduce the preserved reference board's 475 structural poles spanning roughly
75–12,992 Hz. A complex observer over this narrow grid therefore cannot restore
the reference's high-frequency phase or detailed attack. This is a quality
limitation, not evidence that a 48-mode reduction is sufficient. Frequency-spanning
positive-residue reduction or restoration of a fuller board needs matched
transfer/recording and CPU evidence before reducing a reference-quality board.

### Full preserved-reference board profile

`setReferenceSoundboardEnabled(true)` is a setup-only alternative that rebuilds
and clears state. It copies the authored board construction from immutable
`Research/GrandPianoV2/src/grand.cpp` (the board build documented by that
directory's `import-provenance.json`): the 60-by-48 candidate grid, original
bending/areal-mass constants, small frequency perturbation, all retained poles
below 1.2 kHz and the first pole in each occupied 32 Hz band above it. At 48 kHz this
preserves **475 modes spanning 75.3371–12992.4 Hz**, within a fixed 512-mode capacity.
The Nyquist guard still removes unrepresentable poles at lower sample rates.
This profile deliberately uses the original authored board constants rather
than substituting either literature wood choice; the material grid remains a
separate experiment.

Its ports, damping, radiative cancellation and two microphone weights follow
the same preserved formula. The physical board observer is acceleration:

```text
y_c = sum_m mic_mc (-omega_m x_m - 2 sigma_m v_m + F_m)
T_cg(w) = -w² sum_m mic_mc d_mg / (omega_m²-w²+i2sigma_m w)
```

The midpoint bridge impulse records modal force as `J_m/dt`. The new frame clears
that accumulator, and later acoustic reaction impulses add to it. Thus the
observer includes the complete driving force exactly once rather than observing
only displacement or discarding air-load reactions. The loaded modal coefficient
remains `C=i R b H` in energy coordinates. The actual acceleration board response
plus desired-minus-base modal correction is observed; it is not a replacement by
a generic reverb or a delayed mono feed.

For this profile, an aggregate coherent choir of N identical strings uses
`b_effective=b/sqrt(N)` and `R_effective=N R`. This preserves both
`R_effective b_effective²=R b²` and the board-driving term
`R_effective b_effective=sqrt(N)R b`, including nominal 230-string group loading.
This reduction does not preserve detuned relative unison motion; the two
polarizations remain empirical prompt/late mechanical priors. A resonance value
of 0.5 maps to the preserved nominal per-string resistance 0.85; 0.3 is weaker.

The full board corrects the preceding projection's missing high-frequency poles,
but it does not restore the reference's complete 17,778 string modes, unison
operator, hammer parameters or calibrated complex radiation magnitudes. It is
still a separate audition candidate. An initial scalar, no-vectorization host
probe at 48 kHz took 2.676 wall seconds per audio second with 48 board modes and 3.275
with 475 (+22%). Those shared-host figures are development diagnostics, not a
Reason CPU claim or evidence of real-time readiness. Both runs had no unforced
energy increase and midpoint bridge-work residual below 9e-21 J.

Released key dampers add nonnegative velocity loss, reduced continuously by the
sustain position. Keys at MIDI 89 and above remain undamped. `setKeyDown` can lift
a receiver's damper without striking it. Current damper strengths are authored;
pedal-controlled recordings are still needed to validate them. The resonance
control adjusts nonnegative junction resistance rather than injecting an
unaccounted feedback gain.

## Verification and limits

`physical_piano_tests` checks the midpoint energy identity, unforced energy
contraction at 8/44.1/48/96/192 kHz, transfer to unstruck keys, uncoupled isolation,
exact force compliance/work, board impulse work, persistent repeated strikes,
observation isolation, pedal differences, block partition invariance, invalid
configuration preservation, material-driven frequency/mass changes, conservative
and dissipative at-string hammer/contact energy, two-polarization/wood stems and
their exact reconstruction of the shared complex observation. All pass
in the standalone host build with C++17, no exceptions, no RTTI and
`-fno-builtin`. They do not establish the actual Jukebox compiler's performance.
The full-profile test also checks the 475-mode count and frequency endpoints,
finite nonlinear-hammer output, bridge passivity, accumulated reaction-force
terms in acceleration, force clearing between frames and stem reconstruction.

No allocation occurs during stepping. Sines, exponentials, square roots and matrix
inversion occur during configuration or note/controller events, not in modal
sample loops. Contact and port displacement weights are precomputed to avoid
per-mode divisions. Long-lived state is protected from subnormal arithmetic.

Physical passivity is a numerical property, not a perceptual realism score. This
candidate still needs held-out recording evaluation, rate-convergence analysis,
and controlled mechanical recordings. `PhysicalInstrument` now connects the action
and acoustic modules with work-balance tests and isolated CPU diagnostics; that
integration does not identify the component parameters or prove acoustic realism.
