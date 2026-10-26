# One effective key-local resonance

This bounded research component asks whether a separate key-local energy store
can be excited by the speaking strings, persist across strikes, and return
energy to the piano network. It is not a new default, a fitted instrument bank
or an identified physical duplex model.

The motivating **TRAIN-only** C8 audit reports a weak, vendor-consistent family
near 4276 Hz and a strong short component near 4434 Hz. A cross-key check did not
find a comparable shared line in ten other training keys. Its early band decay
is approximately 50 dB/s. The [calibration evidence](FULL_CALIBRATION.md) retains
the physical ambiguity: string, local auxiliary length, frame, bridge and other
interpretations are not uniquely identified. One component's frequency does
not establish its physical part or authorize a whole-key retune.

`physics/LocalResonance.h` supplies one unit-mass oscillator at 4433.86 Hz, with
the free amplitude-loss prior `sigma=50 ln(10)/20`, approximately 5.756/s.
Its resistance of 0.5 and separate unit direct-observation gain are authored,
unfitted demonstration inputs. Coupling changes its effective frequency and
loss; the complete driven response is not assumed to reproduce the recorded
decay. The prototype has **no independent note/trigger/impulse input**.

## Mechanical boundary

Initial and reset state is zero. All auxiliary energy comes through a speaking
string port; note-on and note-off operate only on the original piano and do not
reset the auxiliary. Both string polarizations remain in their existing banks.
The auxiliary's energy coordinates are `x=omega q`, `v=qdot`, giving
`E_aux=.5(x²+v²)` and inverse mass 1.

For a key containing N speaking strings, use equal weights `w=1/sqrt(N)`:

```text
u_key = sum_s(w u_s)
G_key = sum_s(w² G_s)
u_s = sum_j(b_sj omega_sj p_sj)
G_s = sum_j(b_sj²)
```

A conjugate key impulse J gives each string **w J**, not an unweighted copy of
the same impulse. Modal updates are `p_sj += b_sj w J / omega_sj`. Consequently,

```text
delta E_key = J u_key + .5 G_key J²
```

Positive resistance R couples key velocity to auxiliary velocity using:

```text
J_to_aux = h R (u_key-v_aux) / [1 + .5 h R (G_key+1)]
J_to_key = -J_to_aux
relative_mid = (u_key-v_aux) / [1 + .5 h R (G_key+1)]
delta(E_aux+E_key) = -h R relative_mid² <= 0
```

The existing string-to-body bridge remains intact. The auxiliary is connected
only to the selected key's speaking port; it has no direct access to other
keys, the global pressure mix or the board state. Subsequent original-network
steps carry its effect through the existing bridge, body and sympathetic paths.
The source can also receive energy from those paths through its speaking key.

Free motion and positive damping precede the passive key impulse. The adapter
performs this split after each original full-network step. It is a first-order
composition, not an exact simultaneous solve of all contacts and junctions.
All actual work, internal/coupling loss and tiny-state retirement are observable
in the ledger. A charged auxiliary can transfer energy back into an initially
resting speaking string. Removing the module retires its energy explicitly.

## Observation and independent checks

The original step has already computed its pressure when the local impulse is
applied. Changing string p coordinates changes the current string-radiation
field. The research adapter therefore adds exactly the linear correction from
the **actual applied p deltas** and the original `radPL/radPR` coefficients.
It does not add another loaded-board response. The board is unchanged within
this impulse substep and responds through the next original-network step.

The auxiliary's optional direct observer is a separate, authored local-air
pressure proxy. It does not feed forces, losses or energy. It is not calibrated
to the missing component or a microphone geometry. Network-only output is the
observer-muted field of the same intact simulation. Direct gain has not been
increased to force the 4434 Hz feature into the mix.

Tests cover:

- zero auxiliary state under silent speaking input;
- randomized positive-port energy/work identities and free conservation;
- speaking-key excitation into the auxiliary and reverse energy return;
- persistence across a key restrike;
- observation-only muting without mechanical changes;
- exact baseline output when disabled or disconnected from zero state;
- a current-field recomputation check after string impulses;
- invalid-input state preservation and C++ allocation traps.

`tools/local_resonance_support.h` is a research-only template adapter. It includes
the immutable canonical full renderer with a renamed CLI entry point. Define
the quoted `KEYRA_LOCAL_RESONANCE_SOLVER` macro to use a frozen V3 mechanics
snapshot. It does not edit either source or its calibration.

## C8-only probe

Root CMake targets are `keyra_local_resonance_tests` and
`keyra_local_resonance_probe`. The probe synthesizes only C8 with authored MIDI
velocities **40 and 93**. No reference waveform, A0 recording or C8v8 recording
is read. Other keys remain present in the original physical network.

```sh
cmake --build build --target keyra_local_resonance_tests keyra_local_resonance_probe
build/keyra_local_resonance_tests
build/keyra_local_resonance_probe out/local-resonance/control
```

The C8 event sequence has strikes at 20 and 450 ms and releases at 350 and
650 ms. Each auxiliary begins at zero and remains continuous across the second
strike. Baseline, coupled and coupling-off runs share the same events. Intact
body, string field, network, optional auxiliary-direct and combined stems come
from one coupled simulation. Network-effect and total-effect differences are
separate counterfactual comparisons. One common export gain applies to all
fields, counterfactuals and both velocities; no component receives a solo boost.
Exports use the original 24 Hz high-pass and no added room.

The JSON reports work/field errors, transferred energy, restrike continuity,
relative effect levels and fixed-frequency Hann projections over 50–250 ms.
Those projections are diagnostics, not source separation, independent
identification or a perceptual verdict. Whole-network timings include the
expensive original solver and diagnostic field recomputations. The isolated
one-mode timing uses a minimal finite-mass speaking-port fixture, not Reason.

Frequency agreement alone is insufficient. An effect that is too weak, adds
unwanted damping, or fails listening comparison should stay a research result.
This initial proof does not resolve the strong recorded component or establish
that a duplex implementation improves realism.

The first frozen V3 mechanics probe (`out/local-resonance/v3.json`) illustrates
that limit. With the authored resistance and unit direct observer, the auxiliary
stem is approximately **102 / 87 dB below** the whole baseline RMS at MIDI
40 / 93. The network-feedback differences are approximately **56 / 39 dB below**
baseline RMS. The auxiliary is mechanically active and persists across the
restrike, but this parameter choice does not supply a strong 4434 Hz component.
No observer boost or fit was applied and no improvement is promoted. Unit
pressure gain is not a physical level calibration, so this weak result also
does not falsify every possible local-resonance mechanism.
