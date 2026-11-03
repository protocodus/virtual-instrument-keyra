# CPU: steady partials and body banks four at a time (0.4.14)

`RenderKeyraPresetDemos --cpu --repeats 3` on the eight factory demos, one
thread, denormals flushed, 48 kHz in 256-frame blocks; the figure is DSP
seconds per audio second (median of three). Paired runs of the parent commit
(`fix: give every note of a chord its per-key trim and crowding verdict`) and
the commit that interleaves, built with the same compiler (GCC 13.3.0,
`-O3`, x86-64 without FMA) and run alternately on the same development machine
(Intel Xeon at 2.3 GHz, 4 hardware threads, shared). These are development
machine figures, never Reason or DAW CPU. The two renders of every demo are
byte-identical.

| Demo | Before (mean of 2 runs) | After | Change |
| --- | --- | --- | --- |
| 01 Kakegawa Grand | 0.1284x | 0.1007x | −22 % |
| 03 Warm Walnut | 0.0821x | 0.0697x | −15 % |
| 04 Felt Nocturne | 0.0440x | 0.0379x | −14 % |
| 05 Open Strings | 0.1137x | 0.0888x | −22 % |
| 06 Helsinki Upright | 0.1094x | 0.0907x | −17 % |
| 08 Pop Upright | 0.1333x | 0.1070x | −20 % |
| 09 Hamamatsu Grand | 0.0506x | 0.0404x | −20 % |
| 10 Three Cities | 0.0800x | 0.0641x | −20 % |

Instructions executed fall only 7 % (callgrind, Pop Upright: 17.8 to 16.6
billion), so the gain is latency hiding: a partial's rotation is a chain of
dependent multiplies, and four independent chains in one loop keep the
multipliers busy. Each partial is still added to the mix in its old order.

Not changed, and measured on the same machine: a strike costs 0.02 to
0.07 ms on a single-piano build, but 0.26 ms on Three Cities, whose three
pianos each evaluate `windowPower` (exponentials and sines) for every partial,
so seven notes struck together there take 1.9 ms, over a third of a 256-frame
block. Caching those per anchor and velocity is the next saving.
