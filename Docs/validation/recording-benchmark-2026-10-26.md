# Keyra live-engine recording benchmark

These errors measure agreement with one recorded piano and microphone setup. They do not measure perceptual realism or demonstrate commercial readiness.

The source FLACs and decoded PCM were verified for all 24 cases. Ten notes/velocities train the numerical model, twelve in-range cases are held out, and two extreme notes measure extrapolation separately.

The original twelve held-out cases stayed excluded from all numerical fitting, but their results were inspected before the train-only choir correction. These are now development-validation results. The separately locked eight-note fresh report supplies the first score after the final model coefficients were frozen.

The measured attack and fixed 2 ms attack use identical events, rate and engine parameters. The attack coefficients come only from the ten training recordings. The preserved offline v2 renderer is a different, much more expensive model; its metrics are shown as historical context. In the attack comparison, the exposed resonance control is zero to measure the fitted modal source. The product-default column uses resonance 0.25; all other controls retain their defaults. This is a native-engine measurement, with no DAW or Rack host in the path.

## Twelve development holdout cases

| Mean error; lower is better | Offline v2 | Fixed 2 ms | Measured attack | Product default |
|---|---:|---:|---:|---:|
| Broad spectral bands (dB) | 12.088 | 12.281 | 12.274 | 12.274 |
| Harmonic levels (dB) | 4.963 | 3.827 | 3.821 | 3.820 |
| Amplitude envelope (dB) | 4.300 | 4.405 | 4.396 | 4.398 |
| Partial decay (dB/s) | 2.828 | 2.625 | 2.624 | 2.634 |
| Fundamental pitch (cents) | 1.943 | 1.566 | 1.566 | 1.567 |
| Attack rise (ms) | 19.168 | 17.845 | 7.231 | 7.233 |

## Ten training cases

| Mean error; lower is better | Offline v2 | Fixed 2 ms | Measured attack | Product default |
|---|---:|---:|---:|---:|
| Broad spectral bands (dB) | 12.849 | 12.322 | 12.312 | 12.317 |
| Harmonic levels (dB) | 5.045 | 2.185 | 2.178 | 2.180 |
| Amplitude envelope (dB) | 3.891 | 5.277 | 5.267 | 5.276 |
| Partial decay (dB/s) | 3.532 | 2.096 | 2.096 | 2.101 |
| Fundamental pitch (cents) | 0.934 | 0.532 | 0.532 | 0.532 |
| Attack rise (ms) | 19.389 | 18.194 | 7.898 | 7.898 |

## Two edge cases

| Mean error; lower is better | Offline v2 | Fixed 2 ms | Measured attack | Product default |
|---|---:|---:|---:|---:|
| Broad spectral bands (dB) | 18.933 | 22.299 | 22.261 | 22.260 |
| Harmonic levels (dB) | 9.206 | 8.826 | 8.810 | 8.815 |
| Amplitude envelope (dB) | 7.384 | 9.844 | 9.772 | 9.767 |
| Partial decay (dB/s) | 8.675 | 3.281 | 3.290 | 3.303 |
| Fundamental pitch (cents) | 11.982 | 16.146 | 16.146 | 16.145 |
| Attack rise (ms) | 17.792 | 9.208 | 7.958 | 7.958 |

## Limits

- Recorded pedal positions, release events and physical hammer speeds are unknown. Pedal behavior requires new synchronized captures and host playing tests.
- Modal phases, the recording room, detailed contact mechanics and complete mechanical noises are not identified by this fit. Positive prompt/late decay components are a compact empirical model.
- One early scalar gain is removed for scoring; later windows keep that gain. Stereo channels combine in power. Missing prominent model partials receive a penalty.
- The two edge cases are not part of the twelve-case held-out mean. Per-case regressions and all metric values remain in the matching JSON and CSV.
