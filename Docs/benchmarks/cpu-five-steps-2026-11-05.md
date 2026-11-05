# CPU: five profiled savings (0.4.25)

Five changes to `Source/DSP/KeyraEngine.cpp`, each found with callgrind on
the factory demos (Kakegawa Grand, Three Cities, Hamamatsu Grand) and each
committed on its own:

1. **The felt's damping without `std::pow`.** While a damper's felt holds a
   partial, every chunk took `std::pow(total, 1/64)` and each base change
   `std::pow(base, -64)`: 3.6 million calls and a twentieth of the Kakegawa
   Grand demo's instructions. The per-sample damping is now the chunk
   damping's fifth square root and the chunk loss the base's reciprocal
   squared six times. These differ from `std::pow` in the last bits; it is
   the only step that changes a sample.
2. **A strike's window integrals once per pair of lanes.** Blending a partial
   between two recorded pitches evaluated every lane pair's exponentials and
   sines six times over (each channel's power, then the channels' angle, for
   both pitches and the blend). They depend only on the lanes' decays and
   offsets, so each unordered pair's is now evaluated once per partial and
   shared; a swapped pair's are the conjugates, bit for bit.
3. **The open strings' banks four at a time**, in one loop, as the steady
   partials run, so their dependent rotations overlap.
4. **The soundboard's banks at rest are not run.** The bodies hold 108 modes
   in 27 banks; a piano with fewer (the Kawai has 38, the grand 91) left the
   rest turning zeros every sample.
5. **The undamped strings string by string through a chunk**, their state in
   registers, where every string was loaded and stored again each sample.

Steps 2 to 5 change no sample: they add the same terms in the same order.

## Sound

Each 24-bit demo against 0.4.24's, sample by sample:

| Demo | Largest change | Samples changed |
| --- | --- | --- |
| 01 Kakegawa Grand | 1 step (−138.5 dBFS) | 2023 |
| 03 Warm Walnut | 1 step | 6 |
| 04 Felt Nocturne | none | 0 |
| 05 Open Strings | 1 step | 3020 |
| 06 Helsinki Upright | 1 step | 52 |
| 08 Pop Upright | none | 0 |
| 09 Hamamatsu Grand | none | 0 |
| 10 Three Cities | 1 step | 14 |

## Time

`RenderKeyraPresetDemos --cpu --repeats 3`, one thread, 48 kHz in 256-frame
blocks, DSP seconds per audio second. 0.4.24 and 0.4.25 built the same way
(GCC 13.3.0, Release, `-O3`, x86-64 without FMA) and run alternately, twice
each, on the same development machine (Intel Xeon at 2.8 GHz, 4 hardware
threads); the figure is the mean of the two medians. These are
development-machine figures, never Reason or DAW CPU.

| Demo | 0.4.24 | 0.4.25 | Change |
| --- | --- | --- | --- |
| 01 Kakegawa Grand | 0.1533x | 0.1241x | −19 % |
| 03 Warm Walnut | 0.1133x | 0.0857x | −24 % |
| 04 Felt Nocturne | 0.0822x | 0.0551x | −33 % |
| 05 Open Strings | 0.1427x | 0.1096x | −23 % |
| 06 Helsinki Upright | 0.1390x | 0.1090x | −22 % |
| 08 Pop Upright | 0.1526x | 0.1317x | −14 % |
| 09 Hamamatsu Grand | 0.0710x | 0.0538x | −24 % |
| 10 Three Cities | 0.1165x | 0.0867x | −26 % |

The slowest block, where a chord is struck: Three Cities' seven-note chord
(three pianos, every partial blended) took 9.6 ms of its 5.33 ms period and
now takes 6.2 to 6.4 ms; Kakegawa Grand's eight-note chord 4.7 to 4.8 ms and
now 3.5 ms (best of three renders each, two runs).

## Instructions executed

Callgrind over the whole program rendering one demo (the engine's
construction is 5 % of it and unchanged).

| Demo | 0.4.24 | 0.4.25 | Change |
| --- | --- | --- | --- |
| 01 Kakegawa Grand | 11.74 G | 10.36 G | −12 % |
| 05 Open Strings | 10.82 G | 9.29 G | −14 % |
| 08 Pop Upright | 12.11 G | 11.07 G | −9 % |
| 10 Three Cities | 8.43 G | 7.54 G | −11 % |

Time falls further than instructions: steps 3 and 5 mostly remove waiting on
dependent multiplies and memory, not instructions.
