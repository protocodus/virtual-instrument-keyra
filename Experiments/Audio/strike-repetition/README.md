# Repeated-key comparison

These four 0.6-second clips use the same C4 (MIDI 60), velocity-80 press/release
requests and sustain sequence in the original full physical model: 230 strings,
17,778 string modes and 475 board modes. They retain one shared gain and the
original 24 Hz high-pass, with no added room or per-clip normalization.

- `repetitions-legacy-reset.flac`: original convenience note-on behavior,
  including one overwrite of an active hammer in this sequence.
- `repetitions-recovery-control.flac`: persistent string state and hammer
  recovery gating, with excitation variation disabled.
- `repetitions-varied-recovery.flac`: the same controller with bounded,
  correlated per-key velocity/hardness variation (amount 0.65, seed 123456).
- `repetitions-varied-with-mechanisms.flac`: adds key/pedal mechanism resonators
  coupled reciprocally to the existing body, using authored diagnostic levels.

Presses occur at 10, 10.5, 15, 30, 110, 250 and 350 ms. Releases occur at 11,
16, 40, 150, 290 and 390 ms. Sustain starts down, moves halfway at 320 ms and
releases at 480 ms. The very fast opening requests intentionally exercise the
recovery gate. These are matched-input network comparisons: state-dependent
admitted hammer events need not coincide. Exact launch times and request
accounting remain visible in the manifest. The first launch is immediate even
after the pedal has already excited the body and unstruck strings. All three
controlled variants admit six strikes at 10, 15, 30, 110, 250 and 350 ms, with
one cancelled request and no coalescing or expiration. The 15 and 30 ms launches
retain separated hammer positions and have partial-recovery excitation.

String vibration is never cleared on a press. An in-flight or contacting hammer
is not reset; a pending request waits for separation and sufficient recovery.
Partial recovery weakens the launch. Successive strikes draw new bounded
excitation values while the same seed and reset state reproduce a performance.
An explicit short release/repress schedules enough additional key lift at the
existing 18 ms release rate to meet the 20% lift gate; it does not reset an
active hammer or strand the key below the gate. The physical launch still waits
for hammer separation/recovery and can be cancelled by the next release.
The return/key-lift timings and variation ranges are authored approximations,
not measured action geometry or player statistics. The mechanism levels are
also uncalibrated. This is a diagnostic comparison, not listener-approved
realism, realtime performance, or Reason production validation.

`manifest.json` records the exact events, admitted launches, source/producer
hashes, one shared gain and decoded PCM checks. The FLAC files losslessly store
a 24-bit conversion of the frozen float WAVs; the exporter verifies the
conversion and applies no further processing. Reproduce with
`python3 tools/export_strike_listening.py` from the repository root.

This is version 3, adding finite key-lift scheduling for short explicit
release/repress requests. Version 2 could leave such a request permanently
unready until it was cancelled or expired. It already initialized unused
hammers at the authored rest depth; version 1 had a separate initialization
bug that could falsely defer a virgin first strike. Both earlier versions'
source snapshots, producers, reports, WAV/FLAC audio and original hashes are
preserved under `out/strike-repetition/v1` and `v2` with archive receipts.
