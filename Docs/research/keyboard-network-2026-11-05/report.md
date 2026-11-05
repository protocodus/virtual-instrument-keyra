# Keyboard network: run full

Learns from every library in the settings. Every figure is the rms level error of every partial's frames against the recording, in dB (Tools/keyboard_network.py: lower is better).

## Today

Today's tables in closed form at their own train pitches, and today's engine as it ships, rendered at the train and dev takes with its own voicing (velocity colour, per-key trims, strike noise).

| Piano | Tables, closed form, train | Engine, train | Engine, dev |
| --- | --- | --- | --- |
| grand |  |  |  |
| upright |  |  |  |
| kawai |  |  |  |
| hamburg |  |  |  |
| newyork |  |  |  |

## Cross-validation

Held-out train pitches, each piano at its best fine-tuning depth (none, its code, or its code and the last layers).

| Architecture : knob | Level error | Envelope misfit | grand | upright | kawai | hamburg | newyork |
| --- | --- | --- | --- | --- | --- | --- | --- |
| medium:1000.0 | 10.24 | 5.556 ± 0.338 | 10.12 (last) | 9.39 (none) | 10.94 (last) | 10.90 (none) | 9.73 (none) |

medium: character knob 1000.0, smooth knob 1000.0.

## Backtest on the dev takes

Architecture medium, fitted on every train pitch and fine-tuned to each piano at the depth in brackets; the dev takes are never trained on. The network is scored in closed form and today's engine as rendered with its own voicing, so each compares with itself from train to dev takes until the table writer renders the network's tables too.

| Piano | Tables, closed form, train | Character, train | Character, dev | Smooth, train | Smooth, dev | Engine, train | Engine, dev |
| --- | --- | --- | --- | --- | --- | --- | --- |
| grand |  | 8.24 (last) | 8.94 | 8.24 (last) | 8.94 |  |  |
| upright |  | 8.20 (none) | 7.54 | 8.20 (none) | 7.54 |  |  |
| kawai |  | 11.11 (last) | 11.25 | 11.11 (last) | 11.25 |  |  |
| hamburg |  | 7.57 (none) | 7.69 | 7.57 (none) | 7.69 |  |  |
| newyork |  | 7.94 (none) | 7.60 | 7.94 (none) | 7.60 |  |  |
