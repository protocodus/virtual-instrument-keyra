# Release benchmark: the upright's dampers

Every train and dev key-release take of `Tools/corpus/split-helsinki-2026-10-28.json`
below F6, scored by `Tools/benchmark_releases.py` (protocol in its docstring;
lower is better): each take's key struck at velocity 85, held 1.5 s and let go
through `keyra_render`, and the render's release measured at the take's
partials against the take's after one level per partial, with the key-up
searched from 60 ms before the take to 400 ms into it. Train takes set the
candidate's law; dev takes were never fitted. Before: the engine at `cd4660d`,
whose felt takes all of every partial. After: the same engine with
`measured::Damper`, a share of each partial held loosely
([research note](../research/upright-dampers-2026-10-28.md)). Per-partial
results and hashes are in the [JSON](upright-release-benchmark-2026-10-28.json);
each run is `python3 Tools/benchmark_releases.py --renderer <build>/keyra_render --out <dir>`.

| take | note | role | key-up ms, before | dB, before | key-up ms, after | dB, after |
|---|---|---|---|---|---|---|
| rel24 | C1 | train | -60 | 10.65 | 300 | 3.93 |
| rel27 | D♯1 | train | -60 | 13.02 | 340 | 4.79 |
| rel33 | A1 | train | -60 | 12.67 | 190 | 3.90 |
| rel36 | C2 | train | -60 | 10.81 | 230 | 5.38 |
| rel39 | D♯2 | dev | -60 | 9.85 | 180 | 5.03 |
| rel42 | F♯2 | train | -60 | 10.54 | 110 | 5.43 |
| rel45 | A2 | train | -60 | 10.62 | 110 | 5.06 |
| rel48 | C3 | train | -60 | 8.97 | 70 | 4.27 |
| rel50 | D3 | train | -60 | 10.56 | 30 | 3.94 |
| rel52 | E3 | train | -60 | 8.75 | 30 | 3.62 |
| rel54 | F♯3 | train | -60 | 7.56 | 100 | 4.71 |
| rel56 | G♯3 | dev | -60 | 9.39 | 120 | 4.91 |
| rel58 | A♯3 | train | -60 | 6.83 | 100 | 4.93 |
| rel60 | C4 | train | -60 | 6.51 | -10 | 3.88 |
| rel62 | D4 | train | -60 | 6.89 | 60 | 4.45 |
| rel66 | F♯4 | train | -60 | 8.44 | -50 | 5.31 |
| rel68 | G♯4 | train | -60 | 8.57 | 50 | 5.11 |
| rel70 | A♯4 | train | -60 | 6.83 | -50 | 4.90 |
| rel72 | C5 | dev | -60 | 5.81 | -50 | 6.61 |
| rel74 | D5 | train | -60 | 8.61 | 70 | 4.17 |
| rel76 | E5 | train | -60 | 9.56 | 70 | 4.79 |
| rel78 | F♯5 | train | -60 | 8.94 | 60 | 3.89 |
| rel82 | A♯5 | train | -30 | 4.46 | 20 | 3.13 |
| rel84 | C6 | train | -60 | 5.06 | -10 | 3.62 |
| rel86 | D6 | train | -50 | 5.16 | 30 | 3.93 |
| rel88 | E6 | dev | 20 | 8.58 | 20 | 8.62 |

| role | dB, before | dB, after |
|---|---|---|
| train (22 takes) | 8.64 | 4.42 |
| dev (4 takes) | 8.41 | 6.29 |

Before, the key-up sits at the search's earliest on 23 of the 26 takes: with
the felt taking all of a partial, the render's release falls too fast to
follow a take's wherever it starts. From C1 to F♯2 the key-up the candidate
finds lies 110 to 340 ms into the take, against −50 to 120 ms from A2 up
(research note).

## Regressions

Every take where the candidate is worse, with its partials; "by an undamped
string" marks a partial within 60 cents of one of the first three partials of
an undamped string's measured pitch, which the fit leaves out because the
take holds that string's sympathy.

- rel72 (C5, dev): 5.81 → 6.61 dB. Partial 1 (521 Hz) 9.10 → 7.81; partial 2
  (1042 Hz) 6.50 → 6.16; partial 3 (1575 Hz, by an undamped string) 3.48 →
  6.63; partial 4 (2107 Hz, by an undamped string) 6.80 → 4.65; partial 6
  (3173 Hz, by an undamped string) 9.22 → 9.62. The third partial lies 4 cents
  from the G6 string, which the take holds ringing within 8 dB of its level
  for 0.6 s and the halo plays about 60 dB under the partial (research note,
  What is left out). Once the felt took all of the partial, what the render
  left there was that string alone, whose fall the take's follows after one
  level offset; the loosely held share falls faster than both.
- rel88 (E6, dev): 8.58 → 8.62 dB, its one partial (1315 Hz). Its share is
  29 dB under the partial, so the release barely changes.
