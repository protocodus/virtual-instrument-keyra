# Fresh same-piano holdout — 26 October 2026

Eight pitches (D♯2–D♯5 and A2–A5, velocity layer 8) were declared and the model header frozen before any new recording was downloaded or scored. No fitting used these recordings. They come from the same piano and recording session as the training data, so they do not establish independent-piano generalization.

| Mean error; lower is better | Fixed 2 ms | Measured attack | Product default |
|---|---:|---:|---:|
| log_band_mae_db | 14.487 | 14.487 | 14.470 |
| harmonic_level_mae_db | 6.986 | 6.984 | 6.965 |
| envelope_mae_db | 5.901 | 5.898 | 5.875 |
| partial_decay_slope_mae_db_per_second | 3.057 | 3.056 | 3.055 |
| absolute_f1_error_cents | 1.868 | 1.868 | 1.864 |
| partial_tuning_mae_cents | 1.709 | 1.709 | 1.705 |
| attack_rise10_90_error_ms | 11.211 | 6.979 | 6.979 |

The attack comparison uses the exposed resonance control at zero; the product-default column uses 0.25. All other controls retain their defaults. Every per-case result is retained in the JSON and CSV, including regressions. These are native-engine measurements, without a DAW or Rack host in the path.

Further tuning after reading this report needs another new validation set. Recorded pedal/release conditions and physical hammer velocities remain unknown; these measurements do not validate pedal calibration or commercial readiness.
