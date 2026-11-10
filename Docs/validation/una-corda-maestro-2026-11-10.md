# Una corda sized from concert performances: 0.4.37 against MAESTRO's openings

The grands' soft pedal played everything at 0.72 of its level, the prompt
lane at 0.72 of that again with a share going to the slowest lane, and each
partial 1 dB under the one before, however high. None of it had a source.
Beside thirty concert performances
([played phrases](played-phrases-maestro-2026-11-10.md)) it took 1 to 4 dB
more than the pianists' una corda from 125 Hz to 2 kHz. The owner chose to
resize it from that measurement (decision log, 2026-11-10).

The measure is `Tools/benchmark_phrases.py`'s soft row: in the 0.2 s after a
key, the recording less the render with the soft pedal down, less the same
with it up, within one velocity range, by octave band; the median over the
performances that hold enough of both (14 train, 7 dev). 0 is the render's
soft pedal doing what the recorded one does; positive is the render taking
too much. Train is fitted, dev only scored.

## What each size does: the Kakegawa grand with one of them alone, dB (train / dev)

| | 62–125 | 125–250 | 250–500 | 500–1k | 1–2k | 2–4k | 4–8k | whole |
|---|---|---|---|---|---|---|---|---|
| no soft pedal: the recorded una corda | −2.2 / −0.8 | −1.2 / −1.1 | −1.6 / −1.6 | −1.9 / −0.8 | −2.5 / −2.2 | −3.0 / −3.1 | −4.7 / −5.0 | −2.5 / −1.5 |
| the lane move alone | −1.6 / −0.6 | −0.5 / −0.1 | +0.2 / +0.1 | +0.0 / +1.2 | −1.2 / −1.0 | −2.1 / −1.8 | −3.7 / −4.1 | −0.9 / +0.8 |
| the level at 0.72 alone | +0.5 / +2.0 | +1.4 / +1.2 | +1.0 / +0.8 | +0.8 / +1.6 | +0.2 / +0.5 | −0.8 / −0.4 | −2.9 / −2.5 | +0.1 / +1.3 |
| 1 dB a partial alone | −1.7 / −0.8 | −0.8 / −0.4 | −0.9 / −1.4 | −1.2 / −0.6 | −0.8 / −0.1 | −0.2 / +0.2 | −0.6 / +0.4 | −2.0 / −1.2 |

The partials' fall alone has the recorded shape from 1 kHz up and leaves
0.8 to 1.7 dB below it on train; the lane move takes about that much there;
the 0.72 takes 2.6 dB everywhere, more than the recordings show below 1 kHz
before anything else is added.

## Candidates, dB (train / dev)

The lane move and 1 dB a partial, the 0.72 gone:

| | 62–125 | 125–250 | 250–500 | 500–1k | 1–2k | 2–4k | 4–8k | whole |
|---|---|---|---|---|---|---|---|---|
| Kakegawa | −1.1 / −0.3 | +0.2 / +0.7 | +1.0 / +0.3 | +1.1 / +1.6 | +0.5 / +1.0 | +0.1 / +1.3 | +0.3 / +1.4 | −0.5 / +1.0 |
| Hamamatsu | +0.5 / +1.2 | +0.3 / +0.9 | +0.7 / +0.4 | +0.1 / +0.9 | +2.4 / +1.5 | −1.4 / +2.3 | +5.4 / +3.4 | −0.2 / +0.7 |
| Hamburg | −1.4 / +0.4 | −1.2 / −0.3 | −1.5 / −0.9 | −0.7 / −0.2 | −0.1 / −0.4 | −1.4 / +1.0 | +3.4 / +6.8 | −1.8 / −0.5 |
| New York | −0.2 / +0.7 | +1.3 / +1.4 | +0.7 / −0.1 | −0.8 / +0.2 | +0.6 / +0.6 | +0.2 / +0.5 | +5.4 / +2.8 | −0.3 / +0.0 |

No lane move, the level at 0.90 and 1 dB a partial:

| | 62–125 | 125–250 | 250–500 | 500–1k | 1–2k | 2–4k | 4–8k | whole |
|---|---|---|---|---|---|---|---|---|
| Kakegawa | −0.8 / +0.2 | +0.1 / +0.4 | −0.1 / −0.6 | −0.4 / +0.2 | +0.1 / +0.7 | −0.1 / +1.0 | +0.1 / +1.2 | −1.1 / −0.3 |
| Hamamatsu | −0.0 / +1.9 | −0.3 / +0.3 | −0.3 / −0.5 | −1.0 / +0.2 | +1.0 / +0.8 | −2.2 / +1.1 | +5.5 / +3.2 | −1.3 / −0.2 |
| Hamburg | −1.2 / +1.1 | −0.7 / +0.3 | −0.7 / −0.3 | −0.1 / +0.5 | +0.0 / −0.0 | −1.3 / +1.2 | +3.8 / +7.5 | −1.3 / −0.1 |
| New York | −0.3 / +0.8 | +1.0 / +1.4 | +0.3 / −0.2 | −1.0 / +0.1 | −0.2 / −0.1 | −0.9 / −0.7 | +4.5 / +1.9 | −0.5 / −0.1 |

Both stand within 1.5 dB of the recordings from 62 Hz to 4 kHz on nearly
every piano and role, and they cannot be told apart here: they differ in how
a note rings on, and after 0.5 s only four performances hold enough frames
under the soft pedal. The first keeps the engine's account of the pedal (a
softer felt, and the unstruck string driven through the bridge) and drops the
one size the recordings contradict, so it is the one taken. From 4 kHz the
Hamamatsu, Hamburg and New York grands still took 3 to 7 dB too much: there
a band holds partials far up a low string's series, each 1 dB under the last.
With the fall held from the fourth partial above the first the train medians
at 4 to 8 kHz stood −1.1, −2.2, −1.7 and −1.1 dB (too little taken), from the
sixth −0.3, +2.2, −0.2 and +0.6 dB; the fifth is taken.

## 0.4.36: soft pedal down less up, recording less render, dB (train / dev)

| | 62–125 | 125–250 | 250–500 | 500–1k | 1–2k | 2–4k | 4–8k | whole |
|---|---|---|---|---|---|---|---|---|
| Kakegawa | +1.3 / +2.3 | +3.0 / +3.1 | +3.6 / +3.0 | +3.9 / +3.9 | +3.2 / +3.5 | +1.2 / +3.6 | +2.5 / +3.9 | +2.2 / +3.2 |
| Hamamatsu | +3.2 / +3.8 | +3.1 / +3.6 | +3.2 / +2.7 | +2.9 / +3.6 | +3.6 / +4.2 | +0.4 / +4.6 | +6.7 / +4.8 | +2.4 / +3.0 |
| Hamburg | +1.2 / +2.6 | +1.0 / +2.2 | +1.2 / +1.3 | +1.6 / +2.5 | +2.5 / +2.4 | +0.6 / +2.9 | +5.2 / +9.1 | +0.7 / +1.9 |
| New York | +2.5 / +2.8 | +4.0 / +3.8 | +3.3 / +2.6 | +1.9 / +2.8 | +2.8 / +3.1 | +1.7 / +2.9 | +8.1 / +5.2 | +2.4 / +2.6 |

## 0.4.37

| | 62–125 | 125–250 | 250–500 | 500–1k | 1–2k | 2–4k | 4–8k | whole |
|---|---|---|---|---|---|---|---|---|
| Kakegawa | −1.2 / −0.4 | +0.2 / +0.7 | +1.0 / +0.3 | +1.1 / +1.6 | +0.6 / +0.9 | −0.1 / +0.9 | −0.9 / +0.0 | −0.5 / +1.0 |
| Hamamatsu | +0.5 / +1.2 | +0.3 / +0.9 | +0.7 / +0.4 | +0.1 / +0.9 | +2.4 / +1.5 | −1.8 / +1.8 | −1.3 / +2.4 | −0.2 / +0.7 |
| Hamburg | −1.4 / +0.4 | −1.2 / −0.3 | −1.5 / −0.9 | −0.7 / −0.2 | −0.0 / −0.5 | +0.3 / +0.8 | −0.9 / +2.7 | −1.8 / −0.5 |
| New York | −0.2 / +0.4 | +1.3 / +1.4 | +0.7 / −0.1 | −0.8 / +0.2 | +0.5 / +0.5 | +1.1 / +0.3 | −0.2 / +1.5 | −0.4 / +0.0 |

Over the four grands' seven bands the mean distance from the recordings goes
from 2.8 to 0.8 dB on train and from 3.4 to 0.9 dB on dev. The upright's
half-blow is unchanged, and so is every render without the soft pedal, byte
for byte.

## What it does not settle

- How much of the prompt sound moves to the slowest lane (0.28 and 0.08) is
  still 0.4.12's: these openings hold too little after 0.5 s to size it.
- The Hamburg takes 0.7 to 1.5 dB less than the recorded pedal up to 1 kHz on
  train, the Hamamatsu 2.4 dB more at 1 to 2 kHz.
- The recorded pianos are Disklavier concert grands, none of Keyra's four,
  and a pianist's pedal at 0.8 of its travel or more is taken as down.
