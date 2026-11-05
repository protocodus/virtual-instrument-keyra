# Keyboard network: run alone

Learns from the five Keyra pianos alone. Every figure is the rms level error of every partial's frames against the recording, in dB (Tools/keyboard_network.py: lower is better).

## Today

Today's tables in closed form at their own train pitches, and today's engine as it ships, rendered at the train and dev takes with its own voicing (velocity colour, per-key trims, strike noise).

| Piano | Tables, closed form, train | Engine, train | Engine, dev |
| --- | --- | --- | --- |
| grand | 3.55 | 5.59 | 7.68 |
| upright | 4.60 | 7.04 | 9.54 |
| kawai | 6.84 | 8.87 | 10.53 |
| hamburg | 6.63 | 7.56 | 10.90 |
| newyork | 6.14 | 9.37 | 11.42 |

## Cross-validation

Held-out train pitches, each piano at its best fine-tuning depth (none, its code, or its code and the last layers).

| Architecture : knob | Level error | Envelope misfit | grand | upright | kawai | hamburg | newyork |
| --- | --- | --- | --- | --- | --- | --- | --- |
| small:0.0 | 10.18 | 5.493 ± 0.367 | 10.51 (last) | 9.29 (last) | 9.21 (last) | 11.52 (last) | 10.18 (last) |
| medium:0.0 | 9.97 | 5.268 ± 0.571 | 9.81 (code) | 9.46 (last) | 9.20 (last) | 11.37 (last) | 9.86 (last) |
| medium:1.0 | 9.91 | 5.207 ± 0.516 | 9.67 (code) | 9.54 (last) | 9.20 (last) | 11.05 (last) | 9.99 (last) |
| medium:10.0 | 9.90 | 5.201 ± 0.500 | 9.35 (none) | 9.57 (last) | 9.19 (code) | 11.35 (code) | 9.91 (last) |
| medium:100.0 | 10.00 | 5.304 ± 0.484 | 9.77 (code) | 9.46 (code) | 9.15 (last) | 11.47 (last) | 10.00 (last) |
| medium:1000.0 | 9.89 | 5.184 ± 0.387 | 9.55 (none) | 9.35 (last) | 9.20 (last) | 11.34 (last) | 9.85 (last) |
| large:0.0 | 10.26 | 5.584 ± 0.432 | 10.50 (code) | 9.45 (none) | 9.83 (none) | 11.03 (none) | 10.43 (none) |

small: character knob 0.0, smooth knob 0.0.

medium: character knob 1000.0, smooth knob 1000.0.

large: character knob 0.0, smooth knob 0.0.

## Backtest on the dev takes

Architecture medium, fitted on every train pitch and fine-tuned to each piano at the depth in brackets; the dev takes are never trained on. The network is scored in closed form and today's engine as rendered with its own voicing, so each compares with itself from train to dev takes until the table writer renders the network's tables too.

| Piano | Tables, closed form, train | Character, train | Character, dev | Smooth, train | Smooth, dev | Engine, train | Engine, dev |
| --- | --- | --- | --- | --- | --- | --- | --- |
| grand | 3.55 | 8.05 (none) | 9.06 | 8.05 (none) | 9.06 | 5.59 | 7.68 |
| upright | 4.60 | 8.04 (last) | 7.84 | 8.04 (last) | 7.84 | 7.04 | 9.54 |
| kawai | 6.84 | 8.36 (last) | 8.94 | 8.36 (last) | 8.94 | 8.87 | 10.53 |
| hamburg | 6.63 | 7.31 (last) | 9.54 | 7.31 (last) | 9.54 | 7.56 | 10.90 |
| newyork | 6.14 | 7.50 (last) | 7.64 | 7.50 (last) | 7.64 | 9.37 | 11.42 |
