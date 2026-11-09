# The strike's wave reaching the bridge

9 November 2026, Keyra 0.4.29. A hammer strikes its string about an eighth of
the speaking length from the near end, and the board hears the string only
once the strike's wave has run the other seven eighths to the bridge. 0.4.28
played every partial and the board's knock at the strike, so in the lowest
keys the tone came in 8 to 15 ms sooner after the first sound than in their
recordings. 0.4.29 starts them when the wave arrives. Nothing is fitted: the
delay follows from each key's pitch and stiffness.

The measurement is `Tools/measure_string_travel.py`; its protocol is at the
head of the tool. It reads the train and dev takes of each piano's locked
split; no sealed take is read, and no number is fitted from it.

## What the recordings show

Each train and dev take from A0 to B3 and its render at the take's layer,
both from the benchmark's onset: per band, the first 1 ms frame that comes
within 20 dB of the band's loudest over the first 150 ms, through the same
causal fourth-order Butterworth filters on recording and render (under
400 Hz, 400 Hz to 2 kHz, over 2 kHz). The table holds the medians of the band
under 400 Hz less the band over 2 kHz, in ms, and the time the strike's wave
takes to reach the bridge, (7/8) / (2 f), at the median take's pitch.

| piano | keys | takes | recording | 0.4.28 | 0.4.29 | the wave |
|---|---|---|---|---|---|---|
| Kakegawa grand | A0–C♯1 | 32 | 12.5 | 2.6 | 12.9 | 14.6 |
|  | D♯1–G♯1 | 32 | 10.3 | 2.9 | 9.5 | 10.4 |
|  | A1–D2 | 32 | 8.3 | 2.2 | 3.4 | 7.3 |
|  | D♯2–G♯2 | 16 | 6.4 | 2.5 | 4.9 | 4.7 |
|  | A2–D3 | 32 | 4.9 | 2.9 | 3.5 | 3.7 |
|  | D♯3–B3 | 48 | 3.1 | 2.1 | 2.3 | 2.4 |
| upright | A0–C♯1 | 5 | 14.0 | 1.1 | 14.1 | 13.4 |
|  | D♯1–G♯1 | 5 | 12.4 | 2.3 | 12.1 | 11.2 |
|  | A1–D2 | 10 | 9.1 | 1.5 | 7.3 | 7.3 |
|  | D♯2–G♯2 | 10 | 7.6 | 2.0 | 5.6 | 5.2 |
|  | A2–D3 | 15 | 5.6 | 2.3 | 3.5 | 3.3 |
|  | D♯3–B3 | 20 | 5.1 | 1.4 | 2.5 | 2.2 |
| Hamamatsu grand | A0–C♯1 | 7 | 11.2 | 3.4 | 15.3 | 13.4 |
|  | D♯1–G♯1 | 8 | 8.2 | 2.9 | 10.6 | 10.4 |
|  | A1–D2 | 8 | 6.6 | 1.9 | 5.1 | 7.3 |
|  | D♯2–G♯2 | 8 | 4.2 | 2.4 | 6.2 | 5.2 |
|  | A2–D3 | 8 | 3.5 | 2.4 | 3.8 | 3.7 |
|  | D♯3–B3 | 16 | 2.9 | 1.6 | 2.9 | 2.2 |
| Hamburg grand | A0–C♯1 | 4 | 16.7 | 2.1 | 13.6 | 13.4 |
|  | D♯1–G♯1 | 4 | 12.8 | 2.7 | 6.0 | 8.9 |
|  | A1–D2 | 4 | 9.2 | 2.1 | 3.4 | 6.0 |
|  | A2–D3 | 4 | 4.4 | 2.8 | 4.1 | 4.0 |
|  | D♯3–B3 | 8 | 3.3 | 1.3 | 1.3 | 2.2 |
| New York grand | A0–C♯1 | 5 | 3.9 | 4.0 | 17.4 | 13.4 |
|  | D♯1–G♯1 | 5 | 6.0 | 1.9 | 11.9 | 10.0 |
|  | A1–D2 | 5 | 5.1 | 3.2 | 9.2 | 7.5 |
|  | D♯2–G♯2 | 10 | 3.2 | 3.0 | 6.1 | 4.9 |
|  | A2–D3 | 5 | 3.4 | 4.0 | 5.2 | 3.2 |
|  | D♯3–B3 | 5 | 1.1 | 1.1 | 0.9 | 1.8 |

On four pianos the recordings' band under 400 Hz comes in after the band over
2 kHz by about as long as the wave takes, and longer the lower the key; 0.4.28
brought both in 1 to 4 ms apart at every register. New York's bass takes start
too close to their sound to show it: its A0 to C♯1 read 3.9 ms where the wave
takes 13.4, and 0.4.28 already stood there. The Hamburg's split has no
D♯2 to G♯2 take.

## The mechanism

The wave runs at the fundamental's group velocity, c (1 + 2B) / sqrt(1 + B)
for the string's inharmonicity B (Podlesak and Lee, JASA 83(1), 1988), so the
bridge hears a key (7/8) (1 + B) / ((1 + 2B) 2 f1) after the strike, f1 its
fundamental: 15.9 ms at A0, 13.4 ms at C1, 5.3 ms at E2 and 2.0 ms at A3
(`strikeTravel` in `Source/DSP/KeyraEngine.cpp`). The strike point, a seventh
to a ninth of the speaking length, is Fletcher and Rossing's (The Physics of
Musical Instruments, 2nd ed., 1998, section 12.2).

The engine starts every partial, extra and unison slot of the key, and its
knock on the body's modes, from the 32-sample chunk boundary nearest that
time, as one time shift of the sound as fitted. Each lane, a damped rotation,
is run back by the wait, so it arrives at the phase the fit measured, and its
rise starts from zero there. `fit_realtime_modal.py` measured the partials
from the recordings' contact, where the sound comes up, so the phases and
rises fitted between them stand. The hammer's noise, which the felt makes on
the string, and the key landing on the keybed do not travel the string and
stay at the strike. A strike's knock waits in one of 128 slots, one per voice;
with none free it starts at the strike.

## Five builds

The first three held each partial's rise until the wave arrived but let its
oscillator run from the strike. The first left the board's knock at the
strike, which the recordings show quiet under 400 Hz for the first 4 to 8 ms;
the second also held back the strike's noise, whose click then came 10 ms
late; the third held the partials and the knock and left the noise and the key
landing at the strike. Its partials came in at the phase their oscillators had
run to, not the phase fitted at contact, and the bass built up 10 to 30 ms
late. The fourth plays each key as one time shift, as above; the fifth starts
each partial at its own group velocity, the higher partials of a stiff string
sooner. The paired means against 0.4.28 on every train and dev take, summed
over the eleven measures other than level in tolerance units:

| piano | third, train | dev | fifth (stiff string), train | dev | fourth (0.4.29), train | dev |
|---|---|---|---|---|---|---|
| Kakegawa grand | +5.08 | +3.72 | +0.80 | +0.78 | −0.04 | −0.02 |
| upright | +0.86 | +1.67 | +0.04 | +1.20 | +0.11 | −0.19 |
| Hamamatsu grand | +0.95 | +5.34 | +0.40 | −0.92 | +0.38 | −0.55 |
| Hamburg grand | +1.08 | −0.62 | −1.23 | −0.15 | −1.05 | −0.18 |
| New York grand | +0.08 | −0.53 | +0.26 | +0.37 | +0.33 | −0.29 |

The fourth stands closer on every piano's dev takes, which nothing was fitted
on, and summed over the five pianos; the fifth stands further on three
pianos' dev takes. 0.4.29 ships the fourth. Its source renders within
−154 dB of the build benchmarked, and the Hamamatsu, whose output was
re-pinned afterwards, was benchmarked again on the final source.

## On the benchmark

The paired changes against 0.4.28 (lower is closer), from the scorecards
under `Docs/validation/` (`*-string-travel-benchmark-2026-11-09.md`):

| piano | role | attack (dB) | early (dB) | envelope (dB) | rise (ms) | noise (dB) | sum |
|---|---|---|---|---|---|---|---|
| Kakegawa grand | train | −0.09 | −0.03 | −0.10 | +0.49 | −0.01 | −0.04 |
|  | dev | −0.12 | −0.02 | −0.09 | +0.43 | −0.00 | −0.02 |
| upright | train | −0.01 | +0.01 | −0.02 | +0.06 | +0.08 | +0.11 |
|  | dev | −0.03 | +0.00 | +0.01 | −0.38 | +0.10 | −0.19 |
| Hamamatsu grand | train | +0.05 | +0.03 | +0.00 | +0.01 | +0.05 | +0.38 |
|  | dev | −0.05 | +0.01 | +0.00 | −0.63 | +0.08 | −0.55 |
| Hamburg grand | train | −0.23 | −0.07 | −0.12 | −0.27 | −0.06 | −1.05 |
|  | dev | −0.03 | −0.03 | +0.02 | −0.23 | −0.11 | −0.18 |
| New York grand | train | +0.22 | +0.04 | +0.10 | −0.48 | −0.03 | +0.33 |
|  | dev | −0.01 | +0.00 | +0.02 | −0.13 | −0.11 | −0.29 |

The Kakegawa grand's bass, train A0 to B2, stands 0.32 dB closer in the
envelope (2.12 to 1.80 dB) and 0.25 dB in the attack.

Past a tolerance, 25 scores stand further:

- 14 rises (10 to 90 % of the broadband envelope): the Kakegawa grand's F♯5
  (train 0.86 to 7.34 ms, dev 1.21 to 7.07), A5 (dev 0.45 to 3.58, train 2.22
  to 3.61), F♯4 (train 4.35 to 5.88, dev 4.30 to 5.43), C4 (train 2.15 to
  3.40) and D♯1 (dev 7.10 to 8.67); the upright's train C3 (13.81 to 16.68),
  F♯3 (9.70 to 10.76) and E5 (6.13 to 7.14); the Hamamatsu's train G♯4 (7.84
  to 10.11) and G♯5 (2.42 to 4.32) and dev A♯5 (0.78 to 2.38). Eleven are from
  C4 up, where the wave takes 1.7 ms or less, and there the rise moves where
  the envelope stands near its 90 % line: at the grand's F♯5 at velocity 69 it
  stood −2.42 dB under its peak at 11 ms and −0.99 dB at 20 ms on 0.4.28, and
  −0.99 and −0.55 dB on 0.4.29, against the line at −0.92 dB, so its crossing
  moved from 20 ms to 11, where the recordings' is at 19.
- 8 in the deepest bass: the Kakegawa grand's dev A0 attack (4.27 to 5.87 dB),
  early (3.43 to 4.05) and sustain (2.93 to 3.53), four takes; the Hamamatsu's
  train A0 attack (7.81 to 9.77) and early (7.78 to 8.47) and C1 attack (6.53
  to 7.45); New York's train C1 attack (7.45 to 9.81) and envelope (2.68 to
  3.36). These keys wait 13 to 16 ms. The Hamamatsu's recordings come in 11.2
  ms apart from A0 to C♯1, where the wave takes 13.4 and 0.4.29 15.3, and New
  York's takes do not show the travel.
- 2 noises, the upright's train E3 (17.77 to 18.38 dB) and the Hamamatsu's
  train C2 (4.34 to 4.85), and the Hamburg's train G♯5 coherence (0.15 to
  0.19).

On the grand's held-out evaluation (`Tools/evaluate_recordings.py`, the
preserved research split, every case of which the live model is calibrated
from), the twelve in-range cases at the product's defaults stand 4.950 dB
from their recordings in bands (4.968), 3.990 dB in harmonics (3.991), 1.676 dB
in envelope (1.708), 2.270 dB/s in decay and 0.190 cents in pitch (both
unchanged), and 4.090 ms in rise (4.038). By case, rises:

| case | bands (dB) | harmonics (dB) | envelope (dB) | rise (ms) |
|---|---|---|---|---|
| C2 v8 | 3.37 → 3.37 | 3.89 → 3.90 | 1.72 → 1.41 | 10.83 → 1.19 |
| C3 v6 | 5.77 → 5.74 | 5.39 → 5.39 | 1.57 → 1.57 | 9.17 → 9.19 |
| C3 v8 | 4.52 → 4.52 | 4.27 → 4.27 | 1.18 → 1.17 | 9.00 → 9.00 |
| C4 v6 | 5.91 → 5.86 | 4.92 → 4.91 | 1.04 → 1.08 | 2.77 → 2.98 |
| C4 v8 | 4.51 → 4.49 | 3.89 → 3.88 | 1.17 → 1.17 | 2.77 → 3.04 |
| C5 v6 | 5.12 → 5.05 | 4.26 → 4.25 | 1.10 → 1.08 | 1.23 → 1.29 |
| C5 v8 | 4.47 → 4.46 | 3.24 → 3.24 | 0.80 → 0.78 | 0.67 → 0.73 |
| C6 v8 | 6.53 → 6.51 | 2.57 → 2.58 | 9.40 → 9.38 | 1.08 → 1.79 |
| F♯2 v8 | 4.30 → 4.30 | 4.85 → 4.85 | 1.02 → 0.98 | 1.06 → 1.04 |
| F♯3 v8 | 5.42 → 5.35 | 4.17 → 4.18 | 0.76 → 0.73 | 5.69 → 5.42 |
| F♯4 v8 | 4.65 → 4.70 | 3.45 → 3.44 | 0.31 → 0.31 | 3.21 → 5.31 |
| F♯5 v8 | 5.05 → 5.05 | 2.99 → 2.99 | 0.43 → 0.45 | 0.98 → 8.10 |
| C1 v8 (edge) | 2.61 → 2.64 | 3.15 → 3.20 | 2.38 → 2.86 | 2.85 → 2.85 |
| C7 v8 (edge) | 6.56 → 6.56 | 1.37 → 1.37 | 13.69 → 13.69 | 0.00 → 0.00 |

## Chords and levels

The engine stays linear: under the output stage a chord is its notes' sum to
rounding (−129 dB). But a chord's notes now start their partials at their own
waits, so the coincident partials of notes struck together meet at other
phases than in 0.4.28. Single notes keep their level (the single notes of the
upright's typical playing move +0.002 dB in the mean on the meter); a chord
moves by how its voicing lines up. The open-fifth chord E1, B1, E2, B2, E3 at
velocity 80 through the Kakegawa grand's tube played 5.1 dB under its notes'
powers summed on 0.4.28 and plays 2.1 dB over them on 0.4.29: from 60 to 140
Hz, where E1's second and third partials meet E2 and B2, it stands 8 to 9 dB
louder. Through New York's tube the same chord played 3.0 dB over its notes'
powers and plays 3.4 dB under them, 14 dB quieter from 100 to 140 Hz, and 3.6
to 6.8 dB quieter at every velocity of the factory audit.

On Reason's meter, the presets' typical playing moves 0.09 dB at most from
0.4.28's readings and New York's tube 0.12 dB, and the loudest chords move
from −1.06 to +1.34 dB: Studio Grand's 1.34 dB louder, Warm Walnut's, the
grand's tube's and Kakegawa Grand's 0.7 dB, Helsinki Upright's and Pop
Upright's 1.06 and 0.77 dB quieter. The Hamamatsu's output and tube scales and
New York's tube scale are re-pinned to their earlier readings, as in earlier
rounds. Eleven readings then passed their approved levels, and the owner
accepted them (`Docs/decisions.md`, 2026-11-09).

The 0.4.11 factory audit (`Keyra.FactoryDynamics`), whose floors and limits
are unchanged, fails as it did on 0.4.28, on 1,134 rows where 0.4.28 failed
on 1,019. Over its 2,120 pairs the median step from one velocity to the next
moves −0.005 dB and the median chord +0.006 dB, but single chords move from
−6.8 to +8.3 dB, the most the open-fifth chord above; at the Hamamatsu's
tube, A1, E2, A2, C3, E3, A3 at velocity 64 reads 5.6 dB louder than on
0.4.28 and its step to velocity 80 falls from +4.85 to −0.07 dB.

## The tests

Two `Keyra.Engine` checks read chords where the change exposed their
fixtures, and both are corrected beside them. The check that a chord is the
sum of its notes read it at the default Output, where the output stage now
acts on that chord's attack (−28.6 dB against its −35 dB limit); it reads the
chord 24 dB down, as the headroom check reads its chords, and the chord is its
notes' sum to −129 dB. The headroom check took the emergency bound ahead of
the output stage as 4 (+12 dBFS) in its own units, where `ForteOutput` feeds
the guard half of what it reads and clamps it at 4, so the bound is 8
(+18 dBFS); the upright's ten-note chord, whose attacks line up differently,
peaks at +9.3 dBFS, 8.7 dB under it.

A third check is new. On every piano, C1 struck alone with the action, the
room and the knock under the noise bands off plays under 400 Hz over its
first 12 ms only the hammer's noise, 51 to 70 dB under the 10 ms from
14.4 ms on, where its partials play; through `keyra_render`, 0.4.28 read 3
to 12 dB.

## What it does not do

- One delay plays each key: a stiff string's higher partials, which run
  faster, arrive with its fundamental. Started at their own arrivals, they
  stood further on three pianos' dev takes.
- From A1 to D2 at forte, the noise over 2 kHz stands 25 to 35 dB under the
  partials' later level there, so that band comes in with the partials: the
  Kakegawa grand's A1 at velocity 124 at 7.5 ms, where the recordings' median
  is 1.0 ms. At soft layers the hammer's noise lies under the benchmark's
  onset threshold, 45 dB under the render's peak.
- On the upright and the Hamamatsu, the bass's 400 Hz to 2 kHz band comes in
  5.2 and 2.8 ms after the onset in the recordings, and 12.6 and 14.1 ms in
  the render: something sounds there before the wave that the engine does
  not play.
- The Hamamatsu's lowest keys wait longer than its recordings show (15.3 ms
  against 11.2 from A0 to C♯1), and New York's trimmed bass takes cannot show
  the travel at all.
- A chord struck at one sample meets its notes' coincident partials at the
  phases their waits set. Hands spread a chord's strikes by milliseconds,
  which moves those phases; the engine plays a MIDI chord as one instant, so
  a voicing's level is fixed by its notes.
- The treble's action sounds before the strike, which the recordings hold,
  are not played.
