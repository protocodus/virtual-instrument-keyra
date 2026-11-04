# Realism candidates, by audible impact

4 November 2026, Keyra 0.4.18 and 0.4.19. Five string effects were taken in
order of how much each could add to the sound for its CPU: phantom partials,
the unison's modes (strike variety, signed restrikes, una corda), duplex
scaling, the damper's contact position and the upright's pitch glide. Each was
measured on the locked split's train takes first; one ships only where the
recordings decide it, and a law fitted where they do not would be an invented
number.

| Candidate | Outcome |
| --- | --- |
| Phantom partials | Ships in 0.4.18 ([phantom partials](phantom-partials-2026-11-04.md)) |
| Unison modes | Not modelled: the recordings do not show the modes, and a restrike moves the strings' balance less than the measurement's noise |
| Duplex scaling | Not modelled: every line ringing on after the dampers land is an undamped string the engine plays |
| Damper position | Not modelled: the best contact laws improve the release fits by about 1 %, the shuffled controls nearly as much |
| Pitch glide | Ships in 0.4.19 on the upright ([pitch glide](pitch-glide-2026-11-04.md)) |

The probes behind the three that do not ship were one-off scripts over the
tables, the corpus and the Hamburg library's second takes; their methods and
numbers are below.

## Unison modes

A unison's strings, coupled at the bridge, ring as modes the hammer excites
together; a restrike, a strike that differs in force along the strings, or
the soft pedal's shift to fewer strings would excite them in another balance
(G. Weinreich, JASA 62(6), 1474–1484, 1977). Playing that needs a partial's
fitted lanes read as the modes of two or three coupled strings.

**The lanes do not read as modes.** For N strings with their own poles d(i),
coupled through the bridge by one complex Z and struck evenly, the response
is G F / (1 + Z F), F = Σ 1 / (s − d(i)); a partial's lanes' poles and
residues give G and Z linearly and then the d(i). The reading holds where
what the fit never imposed comes out: the strings' own losses equal (spread
under a fifth of the lanes'), the bridge taking energy (Re Z > 0) and a
residual under 5 %. On the grand's table it holds for 23 % of the partials
with two strings and 5 % with three, against 19 to 20 % and 4 to 5 % with
the lanes' phases drawn at random; on the upright's for 30 % and 8 %, against
22 to 25 % and 5 to 7 %. The lanes are fitted components, which two
polarisations of one string or the board's coupling also make, and una corda
and signed restrikes have nothing to project onto.

**A restrike's balance is under the noise.** Without the modes, strike
variety could still scale each lane from strike to strike, by as much as the
recordings vary. The Hamburg library holds a second take of each train pitch
at each of its four layers. Of the 40 pairs, 6 are new strikes (their first
30 ms, band-passed to 2 to 12 kHz, correlate under 0.8:
`Tools/find_repeated_takes.py`'s impact); the rest repeat the first take's
hammer noise. Each take's lanes were fitted on the table's own poles from
0.15 to 3 s, and each lane's balance against the partial's strongest,
(c2k / c2d) / (c1k / c1d) in each channel, compared between the takes. On
the new strikes it spreads by 2.09 dB and 0.33 rad (1.4826 times the median
absolute deviation); between the two microphones of the same take, which a
different strike cannot make since both hear the same strings, it spreads by
3.33 dB and 0.41 rad. On the repeated takes the two read 1.83 and 2.02 dB.
What a new strike changes does not stand out from the measurement's own
scatter, so there is no spread to play.

## Duplex scaling

The string segments beyond the bridge and the agraffe ring at their own
pitches when the speaking length drives them, and keep ringing after its
damper lands. Every piano's release takes were searched for lines that the
struck note's series and the undamped strings (MIDI 89 up) do not explain,
and for narrow lines recurring at one frequency across different keys'
release tails (20 dB over the local floor from 0.15 to 0.55 s after the key
is let go, within 1.5 Hz across files):

- the Hamburg and New York grands' release takes hold only the key's thump;
- the upright's and the Hamamatsu grand's treble releases show no line the
  strings do not explain;
- the Kakegawa grand's treble release tails share lines from F♯6 to C♯7,
  each within 3.4 cents of an undamped string's partial, which the engine
  already plays as its open strings.

No recording holds a line a duplex segment would add.

## Damper position

A felt pressing the string at a fraction d of its speaking length spares the
partials with a node there. Scaling the felt's two measured rates per
partial by g(n) = 1 − cos(2π n d) sinc(n q d), q the felt's width over d and
d log-linear along the keys, was fitted on the train key-up takes of the two
pianos with release recordings that score clean of other strings (the upright
and the Hamamatsu grand), each take's key-up time and each partial's level
refitted with it, against the same fit without it.

- **Both rates scaled**, the best laws lie at the grid's widest felt (q = 5),
  where the sinc smooths the nodes away: they improve the fit's cost by
  0.46 % (upright) and 0.22 % (Hamamatsu).
- **The fast rate only**, the upright's best law (d 0.40 at C4, flat across
  the keys, q 0.2) improves it by 0.43 %, and 3 of 12 laws refitted with
  each take's partial orders shuffled do as well; the Hamamatsu's (d 0.29 at
  C4, 1.35 times per octave up, q 0.5) by 1.05 %, which none of 12 shuffles
  match. The two pianos' contacts disagree, and neither lies near the eighth
  to a quarter of the string that the upright's lingering partials alone
  pointed to.
- **On the Hamamatsu's dev releases**, never fitted, its train law lowers
  the cost by 0.84 %, which 1 of 30 shuffles matches; the mean error per
  take moves by 0.11 dB at most (MIDI 27, 3.23 to 3.12 dB) and gets 0.07 dB
  worse at MIDI 39.

A law that moves a release by a tenth of a dB on one piano, disagrees between
the two, and nearly matches its own shuffles is not decided by the recordings.
