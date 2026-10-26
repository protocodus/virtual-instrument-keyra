# Connected physical modules and isolated checks

The immediate priority is matching the **default grand** against recordings.
These modules are a separately testable research path. They do not silently
replace the current calibrated live model, and adding a component is not evidence
that its parameters or recorded sound are correct.

The user prioritizes a complete perceptual model over excessive precision in
one component. Precision and model reductions are acceptable when hardly
audible, with measured errors and musical listening. Key/pedal sounds must
excite the body/network, with body reaction observable at the mechanism.

The [mechanism/body prototype](MECHANISM_NETWORK.md) now exercises that
connection on the original full piano. Its authored key/pedal resonators have
direct/body/string stems, reciprocal reaction tests and source/coupling
ablations. [Lossless listening exports](../Audio/mechanism-network/manifest.json)
retain a shared gain within each bundle; their effective levels are uncalibrated.

`PhysicalInstrument` connects the modules below through mechanical displacement,
force and reciprocal acoustic ports. Nonlinear hammer/string contact potential
is included in the combined energy; radiation observation never changes the
mechanical forces. Finger motion supplies external work. Bridge resistance,
contact loss, damping and radiation remove energy through explicit ledgers.

| Requested part | Current reduced implementation | Isolated evidence and remaining limit |
|---|---|---|
| Finger/key contact | Prescribed moving finger, unilateral contact and key inertia | Action force/work tests; MIDI trajectory is an authored proxy |
| Key/keybed contact | Unilateral compliant pad and contact loss | Keybed ablation, travel/reaction/loss witnesses; pad law unmeasured |
| Key release | Finger retraction, key return and jack reset | Full press/release/return cycle; no measured action identification |
| Hammer hit/release | Reciprocal jack, escapement, nonlinear discrete-gradient contact, return/backcheck | Two-mass and harmonic-port work tests; no hereditary felt-memory model |
| String vibration | Persistent mass-normalized stiff-string modes | Free decay, exact force/impulse work; 32-partial aggregate choirs rather than 230 individual strings |
| Sympathetic resonance | Reciprocal three-port string/board junction | Unstruck-key energy transfer, damper/pedal and disconnected-junction tests |
| Wood resonance | Orthotropic plate or preserved-reference projection | Material-driven frequency/mass tests; 48 authored material modes or 475 reference poles; no ribbed/crowned finite-element identification |
| Air | One cavity/aperture mode with mechanical reaction | Isolated and coupled energy balances; no full air field or room |
| Lid position | Setup aperture geometry plus positive radiation load | Opening/radiation ablations; no moving flexible lid or geometry-work simulation |
| Player body | Positive local acoustic load | Presence/distance and reaction tests; impedance is explicitly unmeasured |

The material database distinguishes published bulk constants, construction facts,
and missing contact/assembly measurements. See [MATERIALS.md](MATERIALS.md).
Material variations remain secondary to the default-model recording work.

## Integration protocol

1. Advance the finger/key action and freely rotate the string modes.
2. Read old/free string contact displacement and positive force compliance.
3. Solve the nonlinear hammer contact and apply its force to the same string port.
4. Finish action losses and the reciprocal string/bridge/soundboard junction.
5. Step the acoustic load using the current board velocity/inverse mass and apply
   its equal-and-opposite reaction impulse once.
6. Observe the mechanical state for audio. No observation coefficient enters a
   force, loss coefficient or stored energy.

The connected wrapper does **not** also inject the convenience instantaneous
strike from `PhysicalPiano::noteOn`; all excitation enters through the action.
Physical finger travel currently introduces latency relative to MIDI note-on.
This is an experimental input convention, not a release-ready keyboard response.

## Running the isolated and connected tests

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j
ctest --test-dir build --output-on-failure \
  -R 'physical_piano|action|acoustics|physical_instrument'
build/keyra_benchmark_modules > Validation/module-benchmarks.json
```

The benchmark has 18 scenarios, with finite-output and activation witnesses.
Setup and a separate diagnostic pass are excluded from timing. Finger, keybed,
hammer and release cases share the action solver; air, lid and player cases share
the acoustic load. String/wood ablations retain the mechanical container's
overhead, while a separate modal-bank entry isolates that kernel. The rows are
not an additive CPU decomposition and do not establish the Jukebox compiler's
performance. Some research-container callbacks exceed the 48 kHz/64-frame budget;
the physical path must not become the default on the strength of these tests.

Per-module derivations and assumptions are in [ACTION_MODEL.md](ACTION_MODEL.md),
[PHYSICAL_MODEL.md](PHYSICAL_MODEL.md) and [ACOUSTIC_MODEL.md](ACOUSTIC_MODEL.md).

## Evidence required for each component

1. An isolated fixture verifies its event response, decay, stability and CPU.
2. Stems read from one intact simulation reveal its direct observation and the
   body/string responses without altering the network to record them.
3. Excitation and coupling ablations separately measure output changes, energy
   transfer and effects on other modules. A stem does not substitute for an
   ablation in an interacting system.
4. Shared velocity, key, pedal and contact state coordinate timing and strength.
   Passive reciprocal ports account for reactions; external drives report work.
5. Listening and recording comparisons judge whether the approximation helps
   the whole instrument. Adding a module or passing an energy test is not enough.
