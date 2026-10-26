# Air load on the preserved full piano

This research adapter connects the existing reduced `physics::AcousticLoad` to
the original full piano, including its hammer/string contact, all 230 strings,
17,778 string modes, 475 soundboard modes, sympathetic coupling, calibrated
radiation, repeated-strike controller and four mechanical texture modules.
It changes no original source, calibration, public API or production default.
The result is a testable reciprocal network, not an established realism improvement.

`tools/full_acoustic_network_support.h` imports the existing
`strike_repetition_support.h` convention. The exact original solver is included
once with only its CLI entry point renamed. `src/physics/Acoustics.cpp` supplies
the same air equations already documented in [ACOUSTIC_MODEL.md](ACOUSTIC_MODEL.md).
No sample, waveform, impulse response, recording-derived parameter fit or new
material claim is introduced. The eight reserved mechanism recordings remain
unopened.

## Frame and pressure observation

1. Advance the complete original string/board network and existing strike and
   mechanism adapter.
2. Read fresh soundboard velocity and inverse mass at board port 0.
3. Call the first acoustic load and apply its returned `boardImpulse` exactly
   once to that same board port. For a second diagnostic load, read velocity
   again after the first reaction, then step/apply the second load.
4. Add the observation correction from the changed board velocity and the
   acoustic frame-average external force `sum(J)/dt` once. Preserve each
   original bridge `z.force`; neither overwrite it nor apply it again.

This is a first-order composition after the original mechanics. Acoustic
reaction changes the board state used by the next original bridge solve, so
it reaches every connected string and mechanical source. It is not a one-way
post-processing/reverb feed. The mechanical adapter's own external-force
observation remains in its returned pressure proxy; the acoustic correction
adds only the air contribution.

`JunctionFrame` exposes each supplied port, returned acoustic step, actual
board work, summed added force and pressure-proxy correction. This allows a
module to be inspected alone, connected, or ablated while testing its reaction.
Full acoustic and mechanical state remain separate and inspectable.

The original stereo output is an authored pressure proxy. The cavity pressure
is in pascals for the configured reduced geometry, but its relation to that
original proxy, microphone capture gain and propagation path is uncalibrated.
`directAirGain` is a separate authored observation gain, **zero by default**.
An observation-only change never changes physical state. The cavity diagnostic
is mono; the original two pressure observations retain their original stereo
structure. This adds no measured lid directivity or stereo microphone model.

`originalPressureGain` and `mechanicalImpulseLevel` are diagnostic scales, not
validated commercial presets. This probe uses 1 and 0.025 respectively. The
mechanical coupling coefficients remain those of the existing research
adapter; this is not a parity claim for the public `FullInstrument` texture
scales. With air disabled, unity proxy gain and the existing mechanism scales,
the adapter preserves the strike/mechanism adapter's output exactly.

## Static lid/player benchmark

Run `keyra_full_acoustic_probe OUTPUT_DIRECTORY`. The checked bundle is under
`out/full-acoustic-network/render/`; its report is preserved as
[Validation/full-acoustic-network.json](../Validation/full-acoustic-network.json).
All targets have the same seed, note and pedal schedule, authored gains, 48-kHz
rate and room-none path. Preparation and export are outside timing. The 0.72-s
test includes a repeated C4 and low/high notes, including A0 and C8. It begins
with a deliberately authored external cavity pressure impulse of 0.02 Pa·s at
5 ms to expose reverse transfer. This stress excitation is not an input model
of an ordinarily played piano or a recording match.

The nine intact targets prepare lid 0, 0.5 and 1 separately, each with an absent
player, player present at 0.2 m, or player present at 2 m. For the authored
geometry, the cavity frequencies are about 23.03, 53.88 and 64.23 Hz;
`ka` is about 0.013, 0.138 and 0.230, within the module's low-`ka` range.
Player loss uses the existing positive, unmeasured proximity/loss budget.

Three half-lid, player-absent counterfactuals expose different controls:

| Control | Cavity pressure source | Reciprocal coupling | Interpretation |
| --- | --- | --- | --- |
| Intact | Enabled | Enabled | Complete test network |
| Source off | Removed | Enabled | Air is still driven by the played board/strings/mechanisms |
| Coupling off | Enabled | Removed | Independent cavity and the ordinary mechanical network |
| Load off | Removed | Removed | Entire air module bypassed |
| Observation mute (unit test) | Enabled | Enabled | Same physical state; only direct-air observation gain changes |

The source-off target reaches about `8.3e-11 J` of cavity energy through the
mechanical network without any pressure impulse. Coupling-off and load-off
have identical combined mechanical output because direct air mixing is zero.
The source-off versus load-off combined difference has raw pressure-proxy RMS
about `3.80e-4` (peak `1.92e-3`) in this short event sequence.
Differences involving the intact injected-source target must not be presented
as the passive load's size under normal playing.

Each target exports combined stereo pressure proxy, acoustic reaction proxy,
mechanism direct proxy and separate cavity-pressure diagnostic, plus its
combined difference from the half-lid/player-absent target. Proxy observations
use the original 24-Hz high-pass; cavity pressure stays unfiltered. One common
export gain is used across every target, stem and delta. Sharing gain does
not make pascals and proxy units physically comparable. No target or delta is
independently normalized.

The isolated benchmark is one uncoupled cavity with the same prepared controls
and pressure event, without any strings, board or mechanisms. It reports
one-second CPU/wall time, cavity energy and losses. It consumed about
1.8–2.0 ms CPU per audio second in this run. The full diagnostic GCC probe took
about 5.65–7.76 CPU seconds per audio second, including per-sample diagnostics
and interval energy scans. Those are indicative shared-host/compiler results,
not a matched production overhead measurement or a Reason callback deadline.
This integration supplies no new production, SDK or real-time claim.

## Focused checks

`tests/full_acoustic_network_tests.cpp` verifies:

- Actual board-energy change equals the reported impulse work, with each
  impulse applied once. Two loads match independent sequential calculation;
  the second port contains the first reaction.
- Nonzero original bridge forces survive intact. A separately calculated
  acceleration change confirms the external `J/dt` observation appears once.
- Unforced complete cavity/board/string/mechanism energy never increases beyond
  tolerance. Cavity-only excitation reaches unstruck strings and mechanical
  sources; board-only and mechanism-only excitation reach the cavity.
- Air bypass preserves the existing strike/mechanism output exactly. Coupling
  ablation isolates cavity state. Observation changes leave all measured
  string/board/hammer/controller/source and cavity state identical.
- Equal seeds/events remain exact across different external groupings of the
  same absolute-frame step calls; a different seed changes struck output.
  This is a step-adapter partition check, not a DAW block-API test.
- Low/high-note output stays finite at 44.1, 48 and 96 kHz with static lid/player
  cases; invalid setup is rejected. Acoustic geometry preparation resets only
  acoustic state when called outside processing.
- The prepared event/frame path makes no counted C++ allocations. The GNU/ELF
  native build additionally wraps mutex and selected libc I/O calls from the
  compiled translation units. Positive controls exercise every audit category
  before counters are cleared. This is a focused path audit, not a guarantee
  about dynamic libraries, a DAW, SDK or all possible libc entry points.

The checked native run reports maximum acoustic balance residual
`4.6e-20 J`, actual board-work residual `1.1e-22 J`, no measured unforced energy
increase and zero callback allocation/mutex/I/O counts. Cavity-only excitation
reaches about `4.8e-12 J` in unstruck strings and `3.5e-11 J` in mechanical
sources. Focused ASan/UBSan checks cover the same network. Receipts and source
hashes are in the accompanying `Validation/full-acoustic-network*.json` files.

## Remaining limits

The module is one cavity/aperture mode, with authored moving board area,
resistance, volume and aperture dimensions. A static prepared lid changes
aperture geometry; geometry preparation clears the acoustic oscillator. It
must occur outside processing. Continuous lid motion/work, a flexible lid
plate, full three-dimensional air, microphone propagation, room acoustics,
anatomical player scattering and player/finger feedback are absent. Live
player/radiation controls change only positive losses under the existing law.

Numerical passivity and connected transfer establish useful integration
behavior. They do not identify real piano-cavity parameters or establish a
sound-quality improvement. A frozen candidate and controlled acoustic/listening
evidence must precede any production/default adoption. Ambiguous library pedal
low-frequency spectra are not a basis for fitting this cavity.
