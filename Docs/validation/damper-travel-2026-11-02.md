# Damper travel across the six Keyra pianos

In 0.4.9 a released key had two different damper positions. The struck
voice followed an 18 ms travel model, while the bank that rings in sympathy
went straight to the pedal's target. Repeating the note could also leave
its first strike partly damped while its second strike of the same string
was already undamped. These are state inconsistencies: no recording or
listening preference is needed to decide whether a string has two dampers.

Askenfelt and Jansson observed damper lift **before** hammer impact in their
[grand-action timing experiment](https://www.speech.kth.se/music/5_lectures/askenflt/measure.html).
Lehtonen, Askenfelt and Välimäki measured successive phases of free vibration
and felt contact under [partial pedaling](https://research.spa.aalto.fi/publications/papers/jasael-part-pedaling/).
This supports preserving the remaining vibration at a new strike and treating
contact as a transition. Neither study supplies an 18 ms constant for these
six instruments; that is the reduced engine's existing travel time.

The earlier [strike-repetition experiment](../../Experiments/docs/STRIKE_REPETITION.md)
checked that launching a hammer preserves existing string state. The reduced
engine can apply that principle without importing the experiment's hammer
solver. Previous [interpolation trials](../research/consistency-and-belmont-2026-11-02.md)
addressed a different problem and produced regressions at neighboring pitches.
They do not provide a reason to change these pianos' measured spectra.

The change operates on existing receiver banks at control boundaries. A
restrike clears the felt on earlier strikes of the same key and MIDI channel;
their modal phases and amplitudes continue. The top twenty damperless keys
remain damperless. The player's full-pedal setting still leaves the small
amount of felt contact selected in the earlier pedal calibration.

## The measured pedal strike

Kakegawa's recorded pedal-down event already includes the strings that were
freed. Simply injecting its fitted ring under a fully closed felt attenuates
that ring a second time. Delaying both the knock and the ring instead broke
the original sample timing of the mechanical event. Both trials were rejected.

Keep the event at its original time and express only its fitted excitation in
the starting position of the moving felt. If `a` is its position at the event
and `b` the target, the model travels as `d(t) = b + (a-b) exp(-t/T)`, where
`T = 18 ms`. With the existing contact law `F(d) = max(0,(d-.08)/.92)^2.5`,
the extra log-amplitude loss over a sustained lift is
`60 ∫ [F(d(t)) - F(b)] dt`. The new impulse receives the exponential of that
quantity. Existing string vibration receives no gain. This is a change of
initial condition under the measured pedal stroke, not extra mechanical noise.
If the pedal changes direction subsequently, the new trajectory acts normally.

The integral is evaluated once per unheld key at the pedal event. Substituting
`q=(d-.08)/(b-.08)` gives an integrand `(max(0,q)^2.5-1)/(q-1)` multiplied by
`T·F(b)`. For `q ≥ 0` its primitive is `2(u⁵/5 + u³/3 + u - log(1+u))` with
`u=√q`; below zero continue it with `-log(1-q)`. The test independently checks
the result against time integration, including travel across the clearance
point. The native receiver uses control chunks, so exact continuous-time
compensation is not a claim of exact discrete waveform equality.

## Verification against 0.4.9

- **Six pianos, three discriminating checks each:** the original implementation
  failed the direct/receiver contact comparison, same-channel restrike, and
  a public-audio test isolating the sympathetic tail. The correction passes.
  Tests also cover rapid repedaling, sostenuto/channel ownership, damperless
  treble, uninterrupted state, reset, silent travel and host block sizes.
- **933 isolated held-note renders** (699 TRAIN, 234 DEV) were byte-identical
  to 0.4.9 at the recording benchmark's frozen controls. Its 432 Kakegawa,
  158 Helsinki, 127 Hamamatsu, 48 Hamburg, 78 New York and 90 Belmont cases
  therefore retain all their recording scores. These isolated notes do not
  exercise a restrike or a changing pedal.
- In six piano-only factory-preset comparisons, the 120 ms windows around
  rapid restrikes shifted by as much as **0.58–0.91 dB per piano**. The six
  uninterrupted controls and the beginnings of all twelve musical comparisons
  were identical. During the pedal phrase the aligned waveform difference was
  63–66 dB below the original phrase RMS, with less than 0.0002 dB change in
  whole-phrase level. A waveform difference establishes no listener preference.
- Re-scoring the grand's pedal knock with the original observer and frozen
  pedalD1 TRAIN / pedalD2 DEV recording features: full-band ring/knock was
  **7.819 → 7.774 dB**. Band-averaged ring errors changed **2.881 → 2.925 dB**
  and **7.558 → 7.602 dB** respectively; fall errors changed by less than
  0.001 dB. This preserves the earlier calibration closely but does not improve
  its reference error. No equivalent pedal-position captures exist for all six.
- On one 10-core Mac, five rounds alternating both native builds across all
  six pianos gave a pooled process-CPU ratio of **0.998×** (0.994–1.005×).
  The pedal phrase was **1.012×**, repeated notes **0.995×**, and a dense
  162-strike pedal scene **0.996×**. These are native measurements, not
  guarantees about a particular DAW or Reason's realtime meter.
