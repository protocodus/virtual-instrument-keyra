# Keyra beside concert performances: 0.4.36 against MAESTRO's openings

Every corpus Keyra is fitted from holds one note at a time. This sets it
beside played music: thirty performances from MAESTRO v3.0.0 (Hawthorne et
al., ICLR 2019; CC BY-NC-SA 4.0), the International Piano-e-Competition's
Yamaha Disklavier grands recorded in concert, each with the piano's own MIDI:
keys, velocities and the three pedals as continuous values, aligned to the
audio to about 3 ms. `Tools/fetch_maestro.py` reads the first 60 s of three
performances a year from 2004 to 2018 (two train, one dev, by the rule at its
head) out of the published archive; the audio stays in the ignored `out/`
tree. `Tools/benchmark_phrases.py` plays each opening's MIDI through the
renderer as the plug-in plays, and reads how the recording moves against the
render within the performance (its protocol is at its head). The engine is
unchanged.

The pianos, halls and microphones are none of Keyra's and change from year to
year, so no level or balance is scored: every number is a difference inside
one performance, less that performance's own median, and then the median over
performances (20 train, 10 dev).

## How far recording and render part ways: median absolute difference, dB (train / dev)

| | 62–125 | 125–250 | 250–500 | 500–1k | 1–2k | 2–4k | 4–8k | whole |
|---|---|---|---|---|---|---|---|---|
| Kakegawa grand | 4.1 / 5.5 | 3.8 / 3.6 | 2.9 / 3.0 | 3.0 / 3.0 | 3.2 / 2.8 | 3.8 / 3.7 | 4.6 / 4.3 | 2.3 / 2.1 |
| Helsinki upright | 5.2 / 4.6 | 3.1 / 3.3 | 2.9 / 2.9 | 3.6 / 3.4 | 3.5 / 3.3 | 4.0 / 4.9 | 4.5 / 5.6 | 2.4 / 2.2 |
| Hamamatsu grand | 4.5 / 5.1 | 3.9 / 3.5 | 2.9 / 3.0 | 3.0 / 3.1 | 3.7 / 3.6 | 4.3 / 4.7 | 4.3 / 4.5 | 2.2 / 2.3 |
| Hamburg grand | 4.0 / 4.8 | 3.2 / 3.4 | 2.6 / 2.7 | 3.0 / 3.0 | 3.2 / 3.2 | 3.8 / 4.2 | 3.8 / 4.4 | 2.3 / 2.3 |
| New York grand | 4.1 / 4.9 | 3.5 / 3.5 | 2.7 / 3.1 | 3.4 / 3.2 | 3.3 / 3.1 | 3.6 / 3.5 | 3.9 / 4.3 | 2.2 / 2.4 |

## Velocity: the recording less the render in the 0.2 s after a key alone, soft pedal up, dB (train / dev)

| | 1–39 | 40–54 | 55–69 | 70–84 | 85–127 | per 10 steps, median (quartiles) |
|---|---|---|---|---|---|---|
| Kakegawa grand | −2.9 / −2.7 | −1.2 / −1.4 | −1.7 / −0.5 | −0.6 / −0.5 | +1.4 / +1.2 | +0.9 (+0.7 to +1.5) / +0.8 (+0.6 to +1.2) |
| Helsinki upright | −2.0 / −1.1 | −0.2 / −0.9 | −1.0 / −0.9 | −0.0 / −1.2 | +1.2 / +1.6 | +0.8 (+0.3 to +1.6) / +0.7 (+0.3 to +0.9) |
| Hamamatsu grand | −3.5 / −2.1 | −0.3 / −1.7 | −1.3 / −0.3 | −0.8 / −1.5 | +1.8 / −0.1 | +0.7 (+0.2 to +1.3) / +0.7 (+0.4 to +0.9) |
| Hamburg grand | −2.7 / −3.3 | −2.0 / −1.2 | −0.3 / +0.7 | −0.4 / −0.2 | +1.0 / +2.0 | +0.9 (+0.8 to +1.3) / +1.2 (+0.9 to +1.7) |
| New York grand | −1.3 / −2.4 | −1.4 / −0.6 | −0.9 / −0.7 | −0.7 / −0.9 | +0.5 / +0.4 | +0.9 (+0.4 to +1.1) / +0.7 (+0.5 to +0.8) |

## Soft pedal down less up, the render WITHOUT the soft pedal: the recorded una corda, dB (train / dev)

| against | 62–125 | 125–250 | 250–500 | 500–1k | 1–2k | 2–4k | 4–8k | whole |
|---|---|---|---|---|---|---|---|---|
| Kakegawa grand | −2.2 / −0.8 | −1.2 / −1.1 | −1.6 / −1.6 | −1.9 / −0.8 | −2.5 / −2.2 | −3.0 / −3.1 | −4.7 / −5.0 | −2.5 / −1.5 |
| Helsinki upright | +1.1 / −1.1 | −1.6 / −0.9 | −2.2 / −1.4 | −1.1 / −1.0 | −3.0 / −2.9 | −5.9 / −3.5 | −5.4 / −3.4 | −2.3 / −1.6 |
| Hamamatsu grand | −1.1 / +0.2 | −1.5 / −0.7 | −1.4 / −1.3 | −2.4 / −1.0 | −1.9 / −1.9 | −6.0 / −2.8 | −6.7 / −2.4 | −2.4 / −1.5 |
| Hamburg grand | −2.5 / +0.3 | −1.3 / −1.0 | −2.0 / −1.2 | −1.1 / −0.9 | −2.3 / −2.9 | −3.2 / −3.1 | −5.6 / −2.1 | −2.5 / −1.0 |
| New York grand | −1.6 / −0.2 | −0.9 / −0.3 | −1.1 / −1.2 | −2.2 / −1.5 | −2.5 / −2.4 | −3.8 / −5.2 | −6.9 / −3.7 | −1.8 / −1.2 |

## Soft pedal down less up, the render WITH its soft pedal: what Keyra's leaves over, dB (train / dev)

| | 62–125 | 125–250 | 250–500 | 500–1k | 1–2k | 2–4k | 4–8k | whole |
|---|---|---|---|---|---|---|---|---|
| Kakegawa grand | +1.3 / +2.3 | +3.0 / +3.1 | +3.6 / +3.0 | +3.9 / +3.9 | +3.2 / +3.5 | +1.2 / +3.6 | +2.5 / +3.9 | +2.2 / +3.2 |
| Helsinki upright | +2.9 / +1.7 | −0.3 / +1.1 | +0.6 / +1.9 | +2.4 / +3.0 | +2.8 / +3.4 | +2.4 / +6.1 | +6.2 / +10.7 | +0.6 / +2.0 |
| Hamamatsu grand | +3.2 / +3.8 | +3.1 / +3.6 | +3.2 / +2.7 | +2.9 / +3.6 | +3.6 / +4.2 | +0.4 / +4.6 | +6.7 / +4.8 | +2.4 / +3.0 |
| Hamburg grand | +1.2 / +2.6 | +1.0 / +2.2 | +1.2 / +1.3 | +1.6 / +2.5 | +2.5 / +2.4 | +0.6 / +2.9 | +5.2 / +9.1 | +0.7 / +1.9 |
| New York grand | +2.5 / +2.8 | +4.0 / +3.8 | +3.3 / +2.6 | +1.9 / +2.8 | +2.8 / +3.1 | +1.7 / +2.9 | +8.1 / +5.2 | +2.4 / +2.6 |

## Sustain pedal down less up by the time since the last key, dB, median (quartiles), train / dev

| | 0–0.05 s | 0.05–0.2 s | 0.2–0.5 s |
|---|---|---|---|
| Kakegawa grand | +0.4 (−0.1 to +0.8) / −0.2 (−1.3 to +0.3) | +0.1 (−1.1 to +1.0) / −0.4 (−0.7 to +0.8) | −0.4 (−2.9 to +1.4) / −0.1 (−0.5 to +0.7) |
| Helsinki upright | +0.6 (+0.2 to +1.0) / −0.3 (−1.1 to +0.4) | +0.4 (−0.4 to +0.6) / −0.3 (−1.0 to +0.3) | −0.7 (−2.5 to +0.7) / +0.2 (+0.0 to +0.8) |
| Hamamatsu grand | +0.2 (−0.6 to +0.6) / −0.2 (−1.9 to +0.5) | −0.3 (−1.3 to +0.4) / −0.8 (−1.2 to −0.0) | −0.8 (−3.1 to +0.5) / +0.0 (−0.3 to +1.6) |
| Hamburg grand | +0.1 (−0.5 to +1.2) / +0.1 (−0.4 to +0.4) | −0.0 (−0.7 to +0.5) / +0.5 (−0.2 to +1.0) | −1.5 (−2.1 to +0.2) / +1.3 (+0.5 to +1.7) |
| New York grand | −0.0 (−0.7 to +0.9) / −0.9 (−1.8 to +0.1) | −0.0 (−0.7 to +0.7) / −1.2 (−1.9 to −0.7) | −1.1 (−1.8 to −0.7) / −0.5 (−1.0 to +0.3) |

Under the soft pedal 14 train and 7 dev performances hold enough frames; the
velocity line stands on 13 and 9, and the sustain pedal's columns on 18, 16
and 8 train and 8, 9 and 7 dev performances. From 0.5 s after a key only
three performances of each role hold a key alone with the pedal up, so
nothing is read there.

## Reading

- **Velocity.** On all five pianos the recorded Disklaviers grow 0.7 to
  1.2 dB more per 10 steps of velocity than Keyra does, train and dev alike,
  and the hall works against it (a quiet key after a loud passage is recorded
  over that passage's ring). Keyra's response spans the 21 dB between the
  Kakegawa grand's softest and loudest recorded layers over velocities 1 to
  127 (1.7 dB per 10 steps); its shape is the owner's choice of 2026-10-28,
  not a measurement. By these performances a Disklavier's spans about half
  as much again.
- **Soft pedal.** Played without its soft pedal, every piano stands over the
  recordings where the pianist's is down: the recorded una corda takes 0.3 to
  3 dB off the first 0.2 s of a note from 125 Hz to 2 kHz, mostly 1 to 2.5,
  and 2 to 7 dB above (whole: 1.8 to 2.5 dB train, 1.0 to 1.6 dB dev, against
  five different renders). Keyra's una corda (the four grands) takes 1 to
  4 dB more than that from 125 Hz to 2 kHz, the Hamburg's the least: its
  sizes (0.72 of the level, 0.72 of that again on the prompt sound, 1 dB more
  per partial) have no source. The upright's half-blow lands within 1 dB of
  the recorded una corda from 125 to 500 Hz on train and 2 dB on dev, and
  takes 2 to 11 dB more above.
- **Sustain pedal.** Pedal down less pedal up, the recordings and the renders
  agree within 1.2 dB (medians) for the first 0.2 s after a key and within
  1.5 dB to 0.5 s. These openings hold too few long notes to say more; the
  Yamaha C3's pairs do
  ([report](pedalled-note-ring-2026-11-10.md)).
- **Movement.** Recording and render part ways by a median 2.1 to 2.4 dB in
  the whole range and 2.6 to 5.6 dB in an octave band. Part of it is the hall
  and the other piano; it is the figure a later change to how notes run
  together would be read against.
- **Not read.** After everything comes up the recordings stand 20 dB over the
  renders within 0.3 s: the hall's ring, not the dampers'. With one key in
  the last second the grand's recordings stand 1.8 dB (train) and 0.5 dB
  (dev) over, for the same reason.
