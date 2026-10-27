# Contact-driven attack correction

The frequency-aware transient candidate improves early recording agreement,
but remains **33/34: rejected as a universal replacement**. Hard C8 still
exceeds an original early-window limit. Runtime sound and defaults are unchanged.
The [frozen experiment package](../tools/experiments/transient_completion/README.md)
includes the preceding failures and the complete results.

The reported high, ringing click also occurs in the original demo with added
mechanical sources disabled. It cannot yet be identified as a keybed, hammer,
frame or other pictured part. The [parts map](PIANO_PARTS_COVERAGE.md) retains
that distinction. This experiment changes radiation observation, rather than
claiming to add a missing physical part.

## Construction

An additional copy of the original coupled string/unison/bridge/soundboard
network receives the **actual solved hammer contact forces**. It computes its
own bridge forces; captured primary bridge forces serve only as authentication.
The saved primary mechanical trajectory and pressure remain intact.

Both coordinates of each companion mode receive extra loss before its free
update. The final rule applies across all 88 keys and all modes:

```text
string gamma = 100 * max(1, key_f0 / C3_f0, mode_frequency / 1000 Hz)
board gamma  = 100 * max(1, board_frequency / 1000 Hz)
prior q,p   *= exp(-gamma / sample_rate)

candidateRaw = originalRaw - HP200(companionCompletePressure)
candidate    = float32(originalHP24(candidateRaw))
```

Complete pressure includes the board's acceleration and instantaneous force
term, together with the original empirical string-state correction. Subtracting
the string correction alone damaged body and worsened C3 ringing. The fixed
200 Hz high-pass protects low body energy; faster pitch-dependent memory avoids
removing too much treble attack. The final modal term also shortens high-mode
memory on lower, sympathetically excited keys.

These constants are posthoc engineering choices informed by earlier failures,
not measured propagation or material damping. Nonuniform modal loss does not
commute with the coupled network, so the uniform scalar impulse-ramp identity
does not apply. The same filters serve L/R and retain state across blocks and
events. Existing string state is never reset to create a new strike.

## Recording results

The 34 already observed TRAIN cases cover A0 and 16 other pitches through C8 at
two layers. Fixed old gains, onsets, masks, float32 scoring and original guards
remain unchanged. Six pilot outcomes are reused exactly; the remaining 28
companion responses are newly calculated for this operator. This is regression
evidence from the same recorded piano, not fresh validation.

| Metric | Original | Frequency-aware candidate |
|---|---:|---:|
| Mean early five-band error, all 34, dB MAE | 14.963 | 13.730 |
| Mean included late harmonic error, all 34, dB MAE | 13.217 | 13.217 |
| Mean late envelope error, all 34, dB MAE | 5.965 | 5.965 |
| Hard C8, 5–20 ms five-band error, dB MAE | 6.282 | 7.425 |

Every case improves its first-5ms band MAE. C3's first-5ms positive excess falls
by 6.48 / 7.03 dB and its 5–20ms ringing excess by 3.22 / 3.23 dB. Those are
measured criteria, not a listening verdict that the click is fixed.

Hard C8 worsens by **1.143 dB**, exceeding the unchanged +1 dB allowance. Its
250–1000 Hz and 1–4 kHz components become quieter where the original was already
deficient. The earlier pitch-only version failed the same case by +1.423 dB;
the later improvement does not turn either global failure into a pass.

All late harmonic, envelope, RMS and **sustain** stereo guards pass. Early and
whole-note stereo remain diagnostics: hard C8's whole-note L/R changes about
−1.02 dB, and soft C8's whole-note mono energy changes about −4.94 dB. Sustain
preservation must not be presented as unchanged attack image or mono behavior.
C8v4 uses only complete reference windows and full-support envelope samples,
without padding its short tail.

## Qualification and next work

The implementation controls cover six exact original force replays, uniform-loss
compatibility through the same per-mode scaler, finite state, force identities,
energy contraction, retirement/wake and arbitrary-block filter identity. A
future-pressure bound includes force feedthrough; state energy alone would not
bound current board pressure. Only the companion may retire, while filters
retain their history.

This is the historical 5-anchor model at 48 kHz, with mechanisms and humanization
off and repetition control bypassed. The companion retains all 17,778 string
modes and 475 board modes. It is an expensive offline quality experiment and
requires a cheaper realization before plugin integration. It does not establish
current connected-default behavior, other sample rates or Reason/Recon readiness.

A [matched musical comparison](../Audio/full-transient-completion/README.md)
plays original at 0 s and candidate at 9.5 s, dry and with identical room/gain
processing. The original full nine-second float32 audio is bit-identical to its
historical control. A separate unity-memory observer reproduces raw pressure
and 1,689 physical checkpoints, with all 432,000 before/after force-hash pairs
matching. Independent review reconstructs the exported PCM under the same
presentation recipe. The diagnostic's three networks consume 147.11 CPU seconds
for nine seconds of audio; this includes controls and instrumentation and is
not a plugin callback benchmark.

The earlier, unrun musical protocol required 34/34. A new diagnostic protocol
explicitly admits this exact failed candidate for listening; it changes no
acoustic acceptance gate. No listener verdict has been inferred. Further
parameter adjustment waits for this comparison to inform the next change.
If the attack improvement is useful, subsequent work must address the register
regression and find an efficient representation while retaining repeated-strike,
pedal and mechanical body interactions.
