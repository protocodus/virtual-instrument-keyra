# Complete piano block API

`keyra::FullInstrument` in `include/keyra/FullInstrument.h` exposes the complete
working grand model as a block processor. It is separate from the live preview
and the smaller `PhysicalInstrument` experiment. No plugin wrapper, UI, or SDK
integration is changed. This is an integration starting point, not a claim that
the full solver meets a DAW's real-time budget: previous hot-float measurements
still cost roughly three CPU seconds per audio second on the study machine.
Those timing reports predate the finite key-lift controller revision and remain
historical evidence for their recorded source hashes; this revision has not
been assigned a supported real-time budget. The pressure integration evidence
below includes a bounded comparison using the current controller.

The default uses the preserved control calibration, all **230 strings, 17,778
string modes, and 475 soundboard modes**, reciprocal bridge and unison coupling,
and the original stereo radiation. It uses the previously studied hot-float
storage/rotation transformation. Hammer contact and the bridge solve retain
their double-precision arithmetic. The rotation rounding avoids adding free
oscillator energy; the small additional decay is the documented precision
tradeoff in `docs/PRECISION_FINDINGS.md`. The unvalidated 17-anchor radiation
candidate is not selected by this API.

## Use and threading

```cpp
#include <keyra/FullInstrument.h>
keyra::FullInstrument piano;
keyra::FullInstrumentConfig config;
config.sampleRate = 48000;
if (!piano.prepare(config)) { /* invalid configuration */ }
piano.noteOn(60, .75);
piano.process(left, right, frames);
piano.noteOff(60);
piano.sustain(.5);
```

This is one 88-key instrument (MIDI 21 through 108) with one physical pedal and
shared resonating body. It does not provide independent voice IDs, channels, or
64 isolated pianos. Existing strings continue vibrating across new strikes.
Events apply before the next sample; callers split blocks at event offsets.
The absolute frame counter persists across blocks, including the original
64-sample pedal/damper update cadence. `reset()` and `allSoundOff()` clear strings,
board, hammers, action controllers, mechanical sources, pedal, filters, counters,
and the frame clock in place, preserving prepared mode storage and cached
pointers. Virgin inactive hammers start at the controller's authored 12 mm rest
depth. Existing body/string motion therefore cannot spuriously gate an untouched
key's first request using the original renderer's zero hammer coordinate.
Parameters remain selected.

Callers serialize all access. Construction, destruction, move assignment, and
`prepare()` belong off the audio thread. `prepare()` builds fresh model storage;
it never appends a second model to existing vectors. Invalid configurations
return false before replacing a prepared model. The allocation policy is the
standard C++ allocation policy, including termination on allocation failure in
an exceptions-disabled build; `false` does not promise recovery from exhausted
memory. The supported integral sample rates are 44,100 through 96,000 Hz;
higher rates remain outside this API's validated range.

After prepare, events, parameter updates, block rendering, diagnostics, and
reset perform no allocation, locking, file access, or exceptions. The core is
also compiled with exceptions, RTTI, and compiler builtins disabled in its
portable build. Left and right buffers must be separate, writable, nonoverlapping
arrays. Nonzero blocks with null or identical buffers return false without
advancing state; zero-frame blocks are successful no-ops. Rendering overwrites
the buffers. Before prepare, nonzero processing returns false.

## Controls and action

| Control | Range | Default | Meaning |
| --- | --- | --- | --- |
| Gain | -60 to +12 dB | 0 dB | Output gain after the original 24 Hz high-pass |
| Dynamics | 0 to 1 | .5 | Normalized velocity mapping; .5 is the original response |
| Humanization | 0 to 1 | .65 | Bounded, correlated hammer velocity and hardness variation |
| Mechanical level | 0 to 1 | .025 | Quiet, authored key and pedal excitation; zero disables sources |
| Stereo width | 0 to 2 | 1 | Mid/side observation width; 1 retains the original output |

At full humanization, the existing controller bounds its excitation factors by
the configured .8% velocity and 2.5% hardness limits. It never changes string
tuning. Each instance has a deterministic seed; reset reproduces its initial
sequence. Parameters can change without clearing vibrating strings. The gain
and width have no smoothing, so hosts should ramp large automation jumps.

Normalized velocity and pedal position must be finite and within 0 through 1;
invalid inputs are rejected. Velocity zero is a note-off. A note-on reports
acceptance of a request, which can launch immediately or wait for physical
separation. Repeated requests for one key coalesce into its bounded pending
slot. The controller models finite return/recovery, cancels pending launches on
release, and expires requests after 120 ms. A new press after a short explicit
release completes the minimum effective key lift while pending (about 4 ms
from fully depressed), so touching quantized notes can rearm without a full
reset. Existing contact/separation/recovery gates still apply; a release during
that lift cancels the request. An active hammer is never moved to a new strike
position. Its finite-return proxy only moves an inactive hammer
and cannot directly drive strings. Recovery-dependent launch speed is authored
action behavior rather than measured key geometry.

The four three-mode mechanical sources cover key press, keybed, release, and
pedal motion. They use `physics/MechanismExciter.h` and connect to the same board
through equal/opposite midpoint impulses. The observer includes the impulse's
frame-average force `J/dt` exactly once. The sources are cheap authored proxies,
not recorded noise or measured action materials. The default trigger level is
.025 and coupling resistance is .025 times the research presets, chosen
conservatively to reduce continuous loading of the piano. These amounts have
not been calibrated against recordings. Body coupling and direct observation
can be disabled independently in the setup configuration for controlled tests;
an enabled body's reaction remains audible through the original board observer.
Mechanical level zero disables both source excitation and source loading.

## Reciprocal mechanism cache option

`KEYRA_FULL_MECHANISM_CACHE` defaults to `ON` for native and scalar full cores.
The pure C++17 helper caches constant board coefficients and gathers fresh
velocities for the two mechanism ports after each original network step.
Every source receives the body velocity updated by the preceding source's
signed impulse through the full two-port Gram matrix. The equal/opposite source
reaction and direct source observer remain active. Board modes receive one
accumulated float write; the observer adds `J/dt` once and uses the actual
rounded state change for its damping term. Board position and the string-bridge
force are preserved during this extra coupling stage.

The one-write path changes float rounding compared with the original four
source writes. It can change subsequent string, hammer and continuous return
state by small amounts; it is not mechanically bit identical. The original
arithmetic remains selectable with `-DKEYRA_FULL_MECHANISM_CACHE=OFF`, and direct
compilation without the selector retains that control. No compiler extension,
new runtime, source reduction, control change or sample loading is added.
The renderer reports `mechanism_cache` from its selected library build.

Preparation rebuilds coefficient storage for the new model and sample rate.
Reset clears per-frame cached impulses; every connected frame regathers fresh
body velocity. Disabling/re-enabling mechanical level cannot reuse an old
impulse. The private helper templates its model-facing methods, so an explicit
calibration build profile supplies one model without including a second set of
model definitions. Cache storage allocates during prepare under the existing
allocation policy; callback/reset methods do not allocate.

The frozen [cache study](FULL_MECHANISM_CACHE.md) records 24 isolated reciprocal
work cases per branch and 14 complete .35-second renders at 48/96 kHz. Checked
admission diagnostics and seven sampled discrete controller fields match;
source-off, coupling-off and silent ablations are exact. Intact output nulls
range from −117.12 to −109.49 dB relative RMS, with maximum sample difference
`4.80e-6` (−106.38 dB relative to magnitude one). These are normalized model
samples, not an acoustic-pressure or audibility claim. The largest observed
return-depth difference is `2.06e-10` nominal metres; the action geometry remains
an authored proxy. The study preserves failed overly strict continuous-state
analysis expectations and explicitly lists unsampled controller fields.

In 12 preregistered paired comparisons, average CPU/wall and p95 all improve;
median CPU reductions are 6.8–18.2% across the four tested case/rate cells.
Four peak pairs regress, including one 66.86% CPU peak increase. All pairs,
raw traces and variation remain in the report. The integrated build still
requires realtime optimization and actual host qualification. These timings
belong to the frozen study source, rather than a new integrated-core benchmark.

A separate four-second 48-kHz correctness pair uses mechanical level .2 and no
external events after .08 seconds. Independent double energy scans include
strings, board, active contact and source modes. Both branches decay
monotonically; maximum observed energy ratio is one. The whole-render output
null is −116.68 dB relative RMS; quieter tail windows retain their absolute
errors as well. See `Validation/full-mechanism-cache-tail.json`.

The canonical [integration receipt](../Validation/full-mechanism-integration.json)
records native/scalar ON and explicit OFF checks, all nine API groups including
48→96→48 cache reprepare/reset, and one actual API ASAN/UBSAN run. Eight actual
renderer cells at 48/96 kHz (ON/OFF, active/zero mechanics) match the frozen
study bytes. Render allocation traps report zero ordinary/nothrow C++ calls.
The SDK-free Reason source variant has a separate default-ON option and frozen
wrapper checks; its generic-header rebuild retains exact short mechanism/pedal
wrapper output. No additional wrapper sanitizer run is claimed. These receipts
pin the original-control source before subsequent build-profile selection and
renderer metadata edits, which carry separate validation.

## Pressure reduction build option

`KEYRA_FULL_PRESSURE_SIMD` is an experimental option that defaults to `OFF`.
Timings are mixed: the 48 kHz repetition/pedal median regresses by 12.2%, despite
lower medians in seven other case/rate cells. All checked mechanical state is
identical across branches, but compiler support alone does not establish a
benefit for every workload.

When explicitly enabled on GNU or Clang, CMake first checks acceptance of
`-fopenmp-simd`; only a successful check
adds that private compiler flag and defines `KEYRA_FULL_PRESSURE_SIMD=1` for the
full piano library. Other builds retain the original pressure sums. No OpenMP
runtime, worker threads, global fast math, FMA, or architecture-specific flags
are added. The scalar compatibility target explicitly defines the macro as zero
and retains its scalar flags regardless of the main option.
On the supported GNU/Clang path, target options clear and redefine the selector
after parent/global flags, so a conflicting parent macro cannot select SIMD in
the scalar target or override an explicit OFF selection.

The optimized branch changes only the float pressure reductions in
`Modes::portImpulseRadiation()` and `Modes::radiation()`. It uses nonaliasing local
pointers and `simdlen(4)`. Every mode's impulse update keeps its original float
expression; no oscillator, force, bridge, unison, damper, controller, or mechanical
source arithmetic changes. Pressure and output filter values can differ because
the observation sum has a different order. This is a numerical tradeoff, not an
inaudibility claim.

The default `-DKEYRA_FULL_PRESSURE_SIMD=OFF` retains the original pressure reduction order and
exact same-compiler CLI null comparisons. Direct compilation without the macro
also retains that fallback and needs no OpenMP flag. A custom integration must
explicitly establish compiler support before enabling the macro and flag; SDK
support is not inferred from native Linux results. The SDK-free Reason prototype
uses its own explicit option, whose default remains off.

ON and OFF native/scalar tests, the optimized AddressSanitizer/UndefinedBehaviorSanitizer
path, a feature-unavailable fallback build, generated-artifact reproduction, and
48/96 kHz fallback CLI nulls pass. Selecting the fallback reproduces the former
model header byte-for-byte apart from the explanatory comment. Current-controller
mechanical state and pressure comparisons, compiler vectorization diagnostics,
and bounded timings are recorded in `Validation/full-pressure-integration.json`.
All 80 checked mechanical state comparisons match exactly. Across four scores
at 48/96 kHz, optimized output nulls are -127.29 to -138.69 dB relative to the
fallback. These short numerical comparisons do not establish inaudibility.

All three timing pairs are retained, including the mixed initial pass. Seven
of eight case/rate median CPU costs decrease by 10.1–24.5%, but the **48 kHz
repetition/pedal median increases by 12.2%**. Seven of 24 individual pairs
regress. The two later pairs ran in a coordinated quiet window; no initial
measurement was discarded. These results support a selectable compiler
optimization with workload-dependent cost, not a universal speedup or a
real-time deadline guarantee.

The earlier full-backend report and its exact source snapshots remain preserved
under `out/full-pressure-integration/baseline`.

## Bounded fast contact option

`KEYRA_FULL_FAST_CONTACT` selects a bounded pure C++17 contact solver and
defaults to `ON`. The OFF branch retains the legacy method verbatim for control
comparisons. ON applies to both native and scalar compatibility targets; unlike pressure
SIMD it requires no compiler extension or additional runtime. GNU/Clang target
options enforce the selection against conflicting parent macros; an actual
Reason SDK compiler and MSVC have not been validated. The render tool records
the selected branch through `KEYRA_RENDER_FAST_CONTACT`. Current contact studies
keep pressure SIMD OFF.

`physics::solveFullContact()` solves the same convex felt potential and
nonnegative Hunt-Crossley law:

```text
V(x) = K max(x,0)^(p+1)/(p+1)
b = freeCompression - compliance * F
F = DG(V)(a,b) * max(0, 1 + loss*(b-a)/dt)
```

It caches `V(a)`, uses a stable divided difference and derivative near equal
positive endpoints, and takes safeguarded Newton steps within a nonnegative
bracket. At most 10 Newton and 56 fallback bisection steps follow the initial
evaluation: **67 residual evaluations maximum**. The refinement target is
`2e-14*(1+F)`; acceptance requires a finite normalized residual at most `1e-10`.
These are solver accuracy gates, not a change to the contact potential or loss
law. This adapts the prior cached-potential experiment with explicit failure
handling.

The result reports validity, convergence, residual, iteration/evaluation counts,
fallback use and a failure reason. Every failure returns force zero. Invalid or
nonconverged solves retire only the offending hammer before any force update;
the already computed free string step and normal finishing damping remain.
Positive-potential underflow is an explicit numerical-range failure, avoiding a
false zero-force success for extreme finite inputs. Inputs must be finite,
compliance/stiffness/loss nonnegative, time step positive, and power in [1,5].
All actual prepared keys and supported rates are covered by the tests. Counters
in each prepared piano track FAST evaluations, Newton steps, bisections,
fallbacks and maxima; they are zero in legacy builds and reset in place. No
global or thread-local counters, allocation, exceptions or RTTI are introduced.

The independent long-double scalar suite passes 17,396 cases using fresh models
for all 88 keys at 44.1/48/88.2/96 kHz, with velocity/hardness variation,
crossings, separation, near equality and HC clamp boundaries. Maximum normalized
force error is `7.87e-13`; maximum normalized work-law defect is `1.64e-16`.
The work check verifies nonnegative `F*(b-a) - (V(b)-V(a))` against the declared
HC dissipation. All 33 expected failures return zero force, including an actual
67-evaluation nonconvergence case. Twelve valid cases exercise bisection.

Current-controller core comparisons cover four scores at all four rates.
Legacy OFF matches the former model's pressure/output bytes and checked states.
FAST produces identical float output in the 16 tested score/rate cells; five
raw-pressure files differ by at most `1.11e-16`. This observed output equality
does not guarantee bit identity for other states or compilers. String/board
states match in these tests; hammer/controller differences are measured and
retained. Thirty-six conservative contact trajectory audits pass the existing
hot-float energy gate of `5e-5` relative drift; the maximum `3.79033e-5` matches
the legacy baseline. This does not claim exact floating-point energy conservation.
Fault injection verifies no tentative force and exact free-step/damping state
on retirement. Native/scalar API checks, scalar math and ASan/UBSan checks pass.
The default was selected after these correctness checks and two balanced timing
pairs reduced every tested dense-strike peak by about 2.1 times. Whole-score
average gains are smaller and inconsistent. Across all 32 paired score/rate
measurements, 13 average-cost and 16 global-peak comparisons regress; all remain
in the report. The 48 kHz repetition/pedal median average cost rises by 22.47%,
from 3.476 to 4.256 CPU seconds per audio second. The dense fixture uses velocity .7; its median 64-frame peak
callback CPU times are:

| Rate | Legacy OFF | FAST ON | Peak speedup |
| --- | ---: | ---: | ---: |
| 44.1 kHz | 24.69 ms | 11.41 ms | 2.16x |
| 48 kHz | 20.51 ms | 9.73 ms | 2.11x |
| 88.2 kHz | 21.03 ms | 9.92 ms | 2.12x |
| 96 kHz | 21.39 ms | 9.81 ms | 2.18x |

Dense whole-score CPU cost decreases by 4.7–9.7%. A separate, single-pair
velocity-1 dense supplement improves peaks by 1.87–2.23x with identical tested
float output at all four rates. Both fast and legacy peaks still exceed every
64-frame deadline. Late noncontact peaks are retained, including two fast dense
maxima outside contact windows. There is no universal speedup or supported
real-time budget claim. Evidence is in `Validation/full-contact-integration.json`.

## Fault handling and diagnostics

The generated core replaces its two throwing runtime paths with per-instance
flags and counters. A singular/nonfinite bridge solve skips that frame's entire
bridge impulse, clears board/string forces, and refreshes radiation caches. A
failed/nonfinite contact bracket retires that hammer, keeps the already advanced
free string state, and applies its normal finishing damping. These aborts remove
or avoid energy rather than applying an unbounded tentative force. With fast
contact OFF, valid-case solver math and iteration counts are unchanged; the
selected solver's bounded solve and failure handling are described above.

If the final filtered sample is nonfinite or exceeds float range, the facade
outputs zero for that frame and retires all dynamic state. It retains the
absolute frame clock and accumulated fault/request counters. Other instances
are unaffected. `reset()` clears fault history. No global or thread-local error
state is used.

Diagnostics report requests, launches, deferred/coalesced/cancelled/expired
requests, rejected inputs, fault counts, topology, active hammers, and pedal
state. They are operational counters, not a complete physical-energy audit.
Fault flags are 1 for bridge, 2 for contact, and 4 for output retirement. Output
is the original unnormalized pressure proxy converted to float, with no limiter,
clipping, reverb, or automatic gain. A host must choose suitable playback gain.

## Reproduction and validation

`src/full_instrument/generate_prepared_model.py` reproduces the private model and
calibration headers. Its manifest records input, generator, transform, solver
header, and output hashes. It applies `tools/probe_full_precision.py:hot_precision` to the pinned
control source, extracts the model before its event/CLI code, removes setup dump
I/O, and adds the documented fault policy, in-place reset and guarded pressure/
contact options. It can also
accept explicit `--prepared-source` and `--calibration` inputs into a separate
output directory; this capability does not promote a candidate calibration.
Neither canonical source nor Research files are modified.

`tests/full_instrument_tests.cpp` covers block partition identity, endpoint sample
rates, deterministic reset and instance independence, rapid request coalescing,
no active-hammer teleport, pedal transitions, validation, full topology, and
absence of allocation in events/render/reset. Tests exercise the connected
mechanical path. The optional `src/full_instrument/check_cli_parity.py` compares
the pressure-SIMD-OFF, fast-contact-OFF facade against the actual same-hot-float
reference CLI including its 24 Hz high-pass. The command compiles without either
option macro, selecting both original fallbacks. Its control configuration selects
repetition bypass, zero
humanization, dynamics .5, mechanical level zero, body coupling and mechanical
observation disabled, gain zero, and width one. Bypass rejects an already active
hammer rather than overwriting it; parity scores must therefore use separated
strikes. This control mode exists for comparison and does not claim action
humanization. Neither validation establishes a DAW real-time deadline guarantee.

Run the optional CLI check with `python3 src/full_instrument/check_cli_parity.py`;
add `--sample-rate 96000 --output-dir out/full-backend-parity-96k` for 96 kHz.
With pressure SIMD and fast contact disabled, both 48 and 96 kHz checks pass with byte-identical
float output over 8,192 frames,
including event boundaries 63, 64, and 65. They also exercise both private fault
paths and verify that reset preserves cached unison pointers. Explicit
`--compiler "c++ -DKEYRA_FULL_FAST_CONTACT=1 -Iinclude"` checks at both rates
also pass with byte-identical float output; their compile receipt verifies the
preprocessed API selects the fast solver. These control-mode checks disable
the repetition controller and mechanical sound; the separate full API tests
exercise those connected paths.

The CMake `full_instrument` and scalar `full_sdk_portable` tests pass, including
the initial-hammer moving-body and touching MIDI note regressions. A focused
AddressSanitizer and UndefinedBehaviorSanitizer build also passes with leak checking
enabled. Current guarded-header hashes, results, and explicit ON/OFF CLI parity
references are recorded in `Validation/full-contact-integration.json`. The
pressure option's separate evidence is in `Validation/full-pressure-integration.json`. The
earlier API validation and its exact inputs remain preserved as baseline evidence
in `Validation/full-backend-checks.json` and the integration's snapshot directory.
