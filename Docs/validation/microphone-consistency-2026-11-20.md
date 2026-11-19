# Keyra 2.24.2 microphone and keyboard audit

All five bodies played every one of the 88 keys at MIDI velocities 40, 80 and 112 through each dedicated stereo microphone output. Across 6,600 captures per revision, the 95th percentile deviation from the local keyboard level fell from **7.81 to 0.65 dB**. The largest adjacent-key change fell from **23.60 to 6.64 dB**.

## How to read the keyboard results

Each cell shows 2.24.1 → 2.24.2 in dB. Lower values indicate a more even keyboard. For each note at the same velocity, the reference is the median held level of its seven-key neighborhood. The held level is the stereo RMS over 40–600 ms. The table gives the 95th percentile of the absolute deviations within each piano and microphone combination. It retains each instrument’s bass-to-treble level contour.

| Piano | Close | XY | Live | Distant | Tube |
|---|---:|---:|---:|---:|---:|
| Concert Grand | 0.44 → 0.36 | 7.34 → 0.69 | 7.54 → 0.85 | 8.80 → 0.78 | 9.63 → 0.49 |
| Parlor Grand | 0.58 → 0.55 | 7.26 → 0.87 | 9.03 → 0.93 | 8.58 → 0.77 | 5.91 → 0.57 |
| Baby Grand | 0.43 → 0.42 | 8.23 → 0.66 | 7.82 → 0.72 | 10.68 → 0.87 | 10.58 → 0.52 |
| Upright | 0.53 → 0.52 | 7.46 → 0.49 | 8.71 → 0.51 | 7.29 → 0.61 | 9.28 → 0.78 |
| Studio Grand | 0.52 → 0.57 | 8.94 → 0.72 | 7.72 → 0.57 | 7.19 → 0.55 | 8.55 → 0.68 |

## What changed in the engine

- Each dedicated mic now receives the string forces calibrated for its own position. Previously every mic socket inherited a common set of string forces, which left holes and exaggerated individual keys as mic placement changed.
- The soundboard integration now resolves the acoustic wavelength as well as the structural modes of the plate. A denser numerical reference confirmed false modal peaks on all five bodies. For the five documented bridge-impulse examples, the updated amplitude is within 0.41 dB of the reference.
- The mono Tube pickup now measures direct and scattered radiation through its one physical capsule. Its calibration previously averaged in a second modeled capsule.

- The first 20 ms of each pickup is measured with the string force isolated from the mechanical knock. The calibration recombines their signed pressures. Where sustained voicing made a boosted first arrival more than 6 dB above its local keyboard curve, it chooses the closest early string gain that reaches that curve, or the quietest physically attainable peak. The engine applies this gain to the new hammer strike. Its contribution blends into the sustained gain over 40 ms. The resulting table covers 29 of 2,200 key and microphone combinations.

## Notes behind the averages

On the Baby Grand’s Distant microphone, F♯4 to G4 at velocity 80 changed by 23.60 dB on 2.24.1 and 0.23 dB on 2.24.2. The original problem is audible on the third note in the A/B phrase.

The intermediate sustained-only fix boosted the Upright Tube C7 strike to +8.69 dBFS at velocity 112. With independent first-arrival calibration the direct socket peaks at -3.65 dBFS. The independent floating-point outputs are before master gain and limiting. The mastered main output has a −1.5 dBFS sample ceiling.

All 145 selected first arrivals tested at five velocities decreased in peak pressure. The median reduction was 6.33 dB. On the Upright Tube C7 at MIDI velocity 127, the peak fell from +11.57 to −1.13 dBFS. The largest remaining adjacent-key difference is 6.64 dB from B6 to C7 on that microphone at velocity 40, measured over the 40–600 ms held window.

## Ringing checks

The sustained and late windows were 450–740 ms and 1.5–2.0 seconds after note-on. The screen checked the strongest spectral peak against the played string’s modeled inharmonic partials, within the larger of 5 Hz or 1.2% of the partial frequency.

Candidate, sustain window. 0 of 5,867 direct outputs above −50 dBFS had a dominant frequency outside the modeled partials.

Candidate, late window. 0 of 78 direct outputs above −50 dBFS had a dominant frequency outside the modeled partials.

The 60 pedal-stress outputs at the two tested room extremes decayed to at most −174 dBFS in the 8–9 seconds after pedal lift.

## Reproduction

Use `KeyraLevels --write-keys` for the model-derived pickup calibration and `KeyraLevels --check` for the shipped level gates. The soundboard, capsule and direct-mic regression cases run in `Keyra.PianoModel` and `Keyra.MicField`. The listening fixture used the canonical main revision `9208c42` as A. All A/B pairs used identical event timing and repeatable strikes at 48 kHz. Whole-file stereo RMS was matched within each pair.
