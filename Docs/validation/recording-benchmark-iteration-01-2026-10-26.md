# Keyra live-engine recording benchmark

These errors measure agreement with one recorded piano and microphone setup. They do not measure perceptual realism or demonstrate commercial readiness.

The source FLACs and decoded PCM were verified for all 24 cases. Ten notes/velocities train the numerical model, twelve in-range cases are held out, and two extreme notes measure extrapolation separately.

The measured attack and fixed 2 ms attack use identical events, rate and engine parameters. The attack coefficients come only from the ten training recordings. The preserved offline v2 renderer is a different, much more expensive model; its metrics are shown as historical context. The exposed resonance control is set to zero to measure the fitted modal source; other controls retain their defaults. This is a native-engine measurement, with no DAW or Rack host in the path.

## Twelve held-out cases

| Mean error; lower is better | Offline v2 | Fixed 2 ms | Measured attack |
|---|---:|---:|---:|
| Broad spectral bands (dB) | 12.088 | 14.356 | 14.343 |
| Harmonic levels (dB) | 4.963 | 7.328 | 7.311 |
| Amplitude envelope (dB) | 4.300 | 7.345 | 7.315 |
| Partial decay (dB/s) | 2.828 | 3.555 | 3.555 |
| Fundamental pitch (cents) | 1.943 | 1.416 | 1.416 |
| Attack rise (ms) | 19.168 | 17.594 | 7.542 |

## Ten training cases

| Mean error; lower is better | Offline v2 | Fixed 2 ms | Measured attack |
|---|---:|---:|---:|
| Broad spectral bands (dB) | 12.849 | 14.436 | 14.409 |
| Harmonic levels (dB) | 5.045 | 5.622 | 5.593 |
| Amplitude envelope (dB) | 3.891 | 7.569 | 7.529 |
| Partial decay (dB/s) | 3.532 | 3.101 | 3.101 |
| Fundamental pitch (cents) | 0.934 | 0.394 | 0.394 |
| Attack rise (ms) | 19.389 | 18.069 | 8.850 |

## Two edge cases

| Mean error; lower is better | Offline v2 | Fixed 2 ms | Measured attack |
|---|---:|---:|---:|
| Broad spectral bands (dB) | 18.933 | 23.167 | 23.122 |
| Harmonic levels (dB) | 9.206 | 9.524 | 9.486 |
| Amplitude envelope (dB) | 7.384 | 9.427 | 9.320 |
| Partial decay (dB/s) | 8.675 | 6.985 | 6.628 |
| Fundamental pitch (cents) | 11.982 | 16.150 | 16.150 |
| Attack rise (ms) | 17.792 | 9.219 | 8.021 |

## Limits

- Recorded pedal positions, release events and physical hammer speeds are unknown. Pedal behavior requires new synchronized captures and host playing tests.
- Modal phases, the recording room, detailed contact mechanics and complete mechanical noises are not identified by this fit. Positive prompt/late decay components are a compact empirical model.
- One early scalar gain is removed for scoring; later windows keep that gain. Stereo channels combine in power. Missing prominent model partials receive a penalty.
- The two edge cases are not part of the twelve-case held-out mean. Per-case regressions and all metric values remain in the matching JSON and CSV.
