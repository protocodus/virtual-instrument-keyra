# Click benchmark: candidate 0.4.20 against shipping 0.4.18

Every release take of each piano's locked split, train and dev, and the Kakegawa grand's pedal coming up, scored by `Tools/benchmark_action.py` (protocol at the head of the tool; lower is better): per take the mean |dB| between its density and the render's per noise band from 1.26 kHz, where the take stands 6 dB over its floor, the render being the action alone (the default Mechanics less Mechanics 0), set to the take's knock on the header's modes. *Fitted* takes are the train takes `Tools/fit_action_noise.py` reads, one per recorded pitch; the other train takes lie between them and score the mixing; dev takes were never fitted. A take with no band standing so is not scored. Receipt: [`action-click-benchmark-2026-11-05.json`](action-click-benchmark-2026-11-05.json).

| Piano | Group | Takes | 0.4.18 | 0.4.20 | Least gain |
|---|---|---:|---:|---:|---:|
| Kakegawa grand | fitted | 23 | 17.83 | 0.42 | 12.27 |
| Kakegawa grand | other train | 59 | 17.94 | 2.46 | 7.60 |
| Kakegawa grand | dev | 5 | 20.13 | 3.53 | 10.75 |
| Helsinki upright | fitted | 4 | 17.82 | 0.63 | 9.43 |
| Hamburg grand | fitted | 10 | 25.80 | 0.74 | 19.86 |
| Hamburg grand | dev | 2 | 23.58 | 3.57 | 19.77 |
| New York grand | fitted | 13 | 12.05 | 1.31 | 6.07 |
| New York grand | dev | 5 | 11.12 | 3.21 | 4.70 |

No scored take is worse on 0.4.20. Not scored: Helsinki upright, 28 takes (dev and train).

## Kakegawa grand

| Take | Group | Key | Bands | 0.4.18 | 0.4.20 |
|---|---|---:|---:|---:|---:|
| rel1 | fitted | 21 | 12 | 14.67 | 0.34 |
| rel2 | other train | 22 | 12 | 16.10 | 3.57 |
| rel3 | other train | 23 | 12 | 13.18 | 5.58 |
| rel4 | fitted | 24 | 12 | 13.43 | 0.42 |
| rel5 | other train | 25 | 12 | 15.51 | 3.19 |
| rel6 | other train | 26 | 12 | 16.52 | 1.32 |
| rel7 | dev | 27 | 12 | 15.53 | 3.28 |
| rel8 | other train | 28 | 12 | 15.25 | 1.04 |
| rel9 | other train | 29 | 12 | 14.30 | 2.43 |
| rel10 | fitted | 30 | 12 | 16.50 | 0.48 |
| rel11 | other train | 31 | 12 | 14.10 | 2.71 |
| rel12 | other train | 32 | 12 | 15.45 | 2.03 |
| rel13 | fitted | 33 | 12 | 13.27 | 0.36 |
| rel14 | other train | 34 | 12 | 14.75 | 1.22 |
| rel15 | other train | 35 | 12 | 17.66 | 0.99 |
| rel16 | fitted | 36 | 12 | 13.33 | 0.35 |
| rel17 | other train | 37 | 12 | 14.86 | 2.78 |
| rel18 | other train | 38 | 12 | 16.49 | 4.21 |
| rel20 | other train | 40 | 12 | 13.72 | 3.35 |
| rel21 | other train | 41 | 12 | 15.83 | 2.27 |
| rel22 | fitted | 42 | 12 | 12.65 | 0.38 |
| rel23 | other train | 43 | 12 | 14.51 | 1.60 |
| rel24 | other train | 44 | 12 | 14.67 | 3.89 |
| rel25 | fitted | 45 | 12 | 12.81 | 0.33 |
| rel26 | other train | 46 | 12 | 18.55 | 2.58 |
| rel27 | other train | 47 | 12 | 13.88 | 3.80 |
| rel28 | fitted | 48 | 12 | 13.49 | 0.32 |
| rel29 | other train | 49 | 12 | 17.39 | 2.83 |
| rel30 | other train | 50 | 12 | 16.33 | 3.41 |
| rel31 | dev | 51 | 12 | 16.13 | 5.38 |
| rel32 | other train | 52 | 12 | 16.10 | 2.00 |
| rel33 | other train | 53 | 12 | 18.30 | 1.05 |
| rel34 | fitted | 54 | 12 | 17.28 | 0.36 |
| rel35 | other train | 55 | 12 | 18.29 | 1.15 |
| rel36 | other train | 56 | 12 | 17.43 | 2.20 |
| rel37 | fitted | 57 | 12 | 19.16 | 0.35 |
| rel38 | other train | 58 | 12 | 18.43 | 0.87 |
| rel39 | other train | 59 | 12 | 17.69 | 1.61 |
| rel40 | fitted | 60 | 12 | 18.18 | 0.37 |
| rel41 | other train | 61 | 12 | 16.05 | 2.50 |
| rel42 | other train | 62 | 12 | 17.11 | 1.19 |
| rel44 | other train | 64 | 12 | 17.55 | 2.84 |
| rel45 | other train | 65 | 12 | 18.72 | 1.03 |
| rel46 | fitted | 66 | 12 | 16.57 | 0.42 |
| rel47 | other train | 67 | 12 | 20.73 | 2.38 |
| rel48 | other train | 68 | 12 | 19.91 | 1.72 |
| rel49 | fitted | 69 | 12 | 19.04 | 0.42 |
| rel50 | other train | 70 | 12 | 19.90 | 1.91 |
| rel51 | other train | 71 | 12 | 17.09 | 1.43 |
| rel52 | fitted | 72 | 12 | 19.52 | 0.38 |
| rel53 | other train | 73 | 12 | 17.87 | 2.11 |
| rel54 | other train | 74 | 12 | 17.05 | 1.55 |
| rel55 | dev | 75 | 12 | 22.06 | 2.95 |
| rel56 | other train | 76 | 12 | 22.04 | 2.70 |
| rel57 | other train | 77 | 12 | 20.77 | 2.11 |
| rel58 | fitted | 78 | 12 | 18.37 | 0.43 |
| rel59 | other train | 79 | 12 | 18.59 | 1.22 |
| rel60 | other train | 80 | 12 | 23.83 | 2.97 |
| rel61 | fitted | 81 | 12 | 20.38 | 0.53 |
| rel62 | other train | 82 | 12 | 18.72 | 2.03 |
| rel63 | other train | 83 | 12 | 26.55 | 5.04 |
| rel64 | fitted | 84 | 12 | 21.62 | 0.54 |
| rel65 | other train | 85 | 12 | 25.12 | 5.83 |
| rel66 | other train | 86 | 12 | 23.39 | 3.18 |
| rel68 | other train | 88 | 12 | 16.94 | 2.86 |
| rel69 | other train | 89 | 12 | 23.17 | 4.45 |
| rel70 | fitted | 90 | 12 | 20.67 | 0.48 |
| rel71 | other train | 91 | 12 | 21.25 | 3.71 |
| rel72 | other train | 92 | 12 | 18.65 | 1.21 |
| rel73 | fitted | 93 | 12 | 19.17 | 0.49 |
| rel74 | other train | 94 | 12 | 23.27 | 1.92 |
| rel75 | other train | 95 | 12 | 20.18 | 1.61 |
| rel76 | fitted | 96 | 12 | 19.73 | 0.52 |
| rel77 | other train | 97 | 12 | 22.43 | 2.68 |
| rel78 | other train | 98 | 12 | 18.17 | 3.17 |
| rel79 | dev | 99 | 12 | 16.72 | 2.97 |
| rel80 | other train | 100 | 12 | 15.74 | 1.28 |
| rel81 | other train | 101 | 12 | 14.27 | 1.34 |
| rel82 | fitted | 102 | 12 | 16.00 | 0.49 |
| rel83 | other train | 103 | 12 | 16.52 | 3.17 |
| rel84 | other train | 104 | 12 | 18.72 | 1.75 |
| rel85 | fitted | 105 | 12 | 19.47 | 0.53 |
| rel86 | other train | 106 | 12 | 17.26 | 2.67 |
| rel87 | other train | 107 | 12 | 20.34 | 1.94 |
| rel88 | other train | 108 | 12 | 15.42 | 3.96 |
| pedalU1 | fitted | pedal up | 12 | 34.70 | 0.49 |
| pedalU2 | dev | pedal up | 12 | 30.21 | 3.08 |

## Helsinki upright

| Take | Group | Key | Bands | 0.4.18 | 0.4.20 |
|---|---|---:|---:|---:|---:|
| hammer52 | fitted | 52 | 2 | 9.90 | 0.47 |
| hammer66 | fitted | 66 | 1 | 12.69 | 0.50 |
| hammer100 | fitted | 100 | 1 | 17.66 | 0.80 |
| hammer103 | fitted | 103 | 1 | 31.04 | 0.75 |

## Hamburg grand

| Take | Group | Key | Bands | 0.4.18 | 0.4.20 |
|---|---|---:|---:|---:|---:|
| rel24 | fitted | 24 | 8 | 27.39 | 0.86 |
| rel31 | fitted | 31 | 10 | 27.64 | 1.04 |
| rel38 | fitted | 38 | 9 | 24.22 | 0.66 |
| rel45 | fitted | 45 | 6 | 26.55 | 0.83 |
| rel52 | dev | 52 | 8 | 23.18 | 3.41 |
| rel59 | fitted | 59 | 8 | 24.09 | 0.78 |
| rel66 | fitted | 66 | 7 | 20.60 | 0.74 |
| rel73 | dev | 73 | 7 | 23.99 | 3.74 |
| rel80 | fitted | 80 | 8 | 34.15 | 0.57 |
| rel87 | fitted | 87 | 6 | 21.31 | 0.69 |
| rel94 | fitted | 94 | 9 | 29.32 | 0.75 |
| rel101 | fitted | 101 | 6 | 22.75 | 0.48 |

## New York grand

| Take | Group | Key | Bands | 0.4.18 | 0.4.20 |
|---|---|---:|---:|---:|---:|
| rel24 | fitted | 24 | 5 | 14.62 | 1.59 |
| rel29 | fitted | 29 | 6 | 12.26 | 1.15 |
| rel34 | fitted | 34 | 4 | 12.10 | 1.58 |
| rel39 | dev | 39 | 3 | 12.49 | 1.27 |
| rel44 | fitted | 44 | 6 | 11.83 | 1.01 |
| rel49 | fitted | 49 | 3 | 6.90 | 0.83 |
| rel59 | fitted | 59 | 5 | 14.62 | 1.59 |
| rel64 | dev | 64 | 6 | 12.26 | 1.98 |
| rel69 | fitted | 69 | 4 | 12.10 | 1.58 |
| rel74 | fitted | 74 | 3 | 12.49 | 1.55 |
| rel79 | fitted | 79 | 6 | 11.83 | 1.01 |
| rel84 | dev | 84 | 3 | 6.90 | 1.91 |
| rel89 | fitted | 89 | 4 | 8.57 | 0.75 |
| rel94 | fitted | 94 | 5 | 14.62 | 1.61 |
| rel99 | fitted | 99 | 6 | 12.26 | 1.17 |
| rel100 | dev | 100 | 4 | 12.10 | 3.76 |
| rel104 | fitted | 104 | 3 | 12.49 | 1.61 |
| rel105 | dev | 105 | 6 | 11.83 | 7.13 |

## The upright's releases

`Tools/benchmark_releases.py`, the shape of each partial's release on the upright's release takes (protocol at the head of the tool; lower is better):

| Role | Takes | 0.4.18 | 0.4.20 |
|---|---:|---:|---:|
| train | 22 | 5.935 | 5.822 |
| dev | 4 | 7.201 | 7.005 |

10 takes score worse on 0.4.20:

| Take | Role | 0.4.18 | 0.4.20 | Change |
|---|---|---:|---:|---:|
| rel70 | train | 4.293 | 4.836 | +0.543 |
| rel82 | train | 4.374 | 4.499 | +0.125 |
| rel84 | train | 4.837 | 4.954 | +0.118 |
| rel72 | dev | 5.558 | 5.626 | +0.068 |
| rel52 | train | 7.999 | 8.026 | +0.027 |
| rel78 | train | 5.163 | 5.190 | +0.027 |
| rel42 | train | 5.781 | 5.790 | +0.009 |
| rel50 | train | 7.576 | 7.581 | +0.006 |
| rel24 | train | 4.578 | 4.581 | +0.003 |
| rel60 | train | 6.518 | 6.519 | +0.001 |

Renderers: 0.4.18 at commit 52231e2 and 0.4.20 as committed, GCC 13.3.0 Release; their sha256 are in the receipt.
