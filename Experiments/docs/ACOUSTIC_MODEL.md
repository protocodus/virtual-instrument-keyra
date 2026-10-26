# Reduced air, lid and player-load prototype

`physics::AcousticLoad` is a separate, passive acoustic candidate. It does not
change the current live modal renderer. It contains one cavity/aperture mode,
a lid-dependent aperture, radiation resistance and a positive player-load term.
It can run alone or load the mechanical soundboard reciprocally. It is not a
room impulse response, an air-field solver, a flexible lid plate, or an
anatomical body model.

## Physical state and data

For volume displacement `Q` in cubic metres, acoustic inertance `M` and
compliance `C`, the state is:

```text
omega = 1 / sqrt(M C)
x = omega sqrt(M) Q
v = sqrt(M) dQ/dt
E = (x^2 + v^2) / 2
```

Dry air uses `rho=P/(R T)` and `c=sqrt(gamma R T)`, with `R=287.05 J/(kg K)`
and `gamma=1.4`. This is an ideal dry-mixture approximation. NPL's
[speed-of-sound report](https://www.npl.co.uk/getattachment/19d0d4d3-5bd9-47d9-b392-01be4c8e453d/Speed-of-Sound-Toilet-Roll-Report.pdf?lang=en-GB)
gives the corresponding `20.047 sqrt(T_K)` relation and explicitly discusses
the dry-air assumption. Humidity and temperature gradients are not modeled.

The cavity compliance is `C=V/(rho c^2)`. Aperture inertance is
`M=rho L_eff/A`; this candidate uses a circular aperture with
`L_eff=neck_length+1.7 radius`. The factor represents two ideal flanged ends,
as described by [UNSW's Helmholtz resonator explanation](https://www.phys.unsw.edu.au/jw/Helmholtz.html).
It is geometry dependent and is **not** a measured piano lid opening. Volume,
aperture endpoints, neck and moving board area are authored configuration.

The leading low-`ka` baffled circular-piston radiation resistance, expressed in
volume-flow coordinates, is:

```text
R_radiation = (rho c / A) (ka)^2 / 2
k = omega/c
```

This follows the low-frequency force/velocity form in Eq. 7 of
[Hambric and Fahnline's structural-acoustics tutorial](https://hambricacoustics.com/StructuralAcousticsTutorialPart2AcousticsTodayrev1.pdf),
divided by area squared. `properties().lowKaApproximation` reports whether
`ka<=0.5`. Positive damping remains numerically passive outside that range,
but the low-frequency approximation is then acoustically unreliable.

## Reciprocal coupling

The mechanical board port supplies velocity `u` and inverse mass `G`. A board
impulse `J` must be applied once by the caller and changes mechanical energy by
`u J + G J^2/2`. For effective moving area `S`, the relative volume velocity is
`w=S u-v/sqrt(M)`. A positive acoustic resistance `R` connects the two ports.
One implicit-midpoint junction computes:

```text
w_mid = w / [1 + dt R (S^2 G + 1/M)/2]
J_board = -dt S R w_mid
delta_v = dt R w_mid / sqrt(M)
```

The exact kinetic-energy change is `-dt R w_mid^2`. Thus the load sends its
reaction back to the soundboard; the cavity is not driven through a one-way
reverb feed. Free cavity rotations and positive velocity-loss half steps
surround this junction. The complete step reports cavity energy, board work,
each loss term and their numerical balance residual.

The physical wrapper should sequence `PhysicalPiano::finishFrame()`, read
`boardVelocity(0)`/`boardInverseMass(0)`, call `AcousticLoad::step()`, apply
`boardImpulse(0,result.boardImpulse)`, then call `observe()`. The returned board
work can be compared directly with the mechanical module's own work result.
Multiple acoustic loads must be applied sequentially with updated port
velocity, never all computed from the same stale velocity.

## Lid and player controls

`AcousticConfig::lidPosition` selects aperture geometry during `prepare`.
Changing the aperture/inertance rebuilds and clears this acoustic state;
continuously moving lid geometry and the associated mechanical work are not
implemented. `setLidRadiation` changes only a nonnegative loss multiplier in
running audio. It injects no instantaneous energy and does not silently
relabel a fixed-inertia model as a moving lid.

Player presence/distance select additional positive modal damping using an
authored proximity law. Its maximum loss is explicitly marked unmeasured.
[Sabbagh and Elkhateeb (2021)](https://doi.org/10.1016/j.apacoust.2021.108317)
measured posture/clothing-dependent absorption, but those room-equivalent
results do not identify a seated pianist's local near-field impedance. No
published absorption coefficient is converted into this resistance by guess.
Human-body scattering, posture and player/finger action feedback remain open.

## Isolation and verification

- `setCouplingEnabled(false)` removes the mechanical junction while retaining
  the acoustic oscillator/losses. It is an ablation, not a different calibrated
  piano preset.
- Zero radiation, player and internal losses isolate the conservative cavity.
  External pressure impulses report their supplied work.
- Separate lid/body/internal loss terms allow energy-accounted benchmarks.
- Test coverage includes dry-air equations, aperture changes, ten seconds of
  isolated lossless motion, randomized reciprocal energy balances, an integrated
  board oscillator, nonzero lid/player effects, invalid-input state preservation,
  seven sample rates and C++ allocation instrumentation.

The unit tests establish equations, state handling and passivity. They do not
establish measured piano-cavity fidelity, real lid directivity or player-body
realism. Controlled acoustic recordings/measurements are required before those
claims or a production default can be justified.
