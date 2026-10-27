# Current pressure SIMD — source-only harness

The current full model is copied identically to both arms. Free/unison SIMD,
fast contact and mechanism cache stay enabled, OriginalControl profile 0.
Only pressure observer SIMD changes from off to on. The validated four-rate,
four-case schedules and later AB/BA/AB timing recipes are unchanged.

Deep physical snapshots omit exactly `String.cachedRadiation`, `Impl.previous`
and `Impl.highpass`. All string/body coordinates, force/velocity, damping,
hammer, controller/RNG, mechanism state/ledgers, body cache and `lastStems`
remain exact requirements. Raw float64 pressure and final float32 output may
differ, subject to the frozen `quality.py` numerical recipe. It covers all
samples, seven bands from DC through Nyquist and four fixed time windows,
including L/R, correlation and masked mono energy. Baseline-only masks and
weak/degenerate diagnostics remain visible. No gain, delay or onset matching.
Numerical gates do not prove inaudibility or recording realism.

Preparation compiles only and runs manufactured metric checks. Actual models
require a separate root authorization bound to the final protocol; performance
requires a passed correctness result and its own quiet-window authorization.
No default adoption follows. No recording inputs are used.
