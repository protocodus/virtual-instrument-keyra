# Full-model contact optimization

The cached-potential safeguarded-Newton candidate reduces dense hammer-attack
spikes while preserving pressure output exactly in the two short tested
fixtures. It does not improve ordinary musical throughput. The candidate is
an isolated source copy; no canonical, Research or Action implementation changed.

## Method and numerical scope

The pinned extended-calibration float source is `8d6abcd41d89a32b...`, with header
`45935c2fbe67e191...`; the complete hashes are in both reports. All keys, strings,
polarizations, board modes, coupling operators, sample rate and calibration stay
unchanged. No recording or evaluation feature was read.

`physics::solveContact` still uses bisection. The reusable safeguarding pattern
is in `Action::advanceKey`: bracketed Newton steps with bounded bisection fallback.
That code was inspected but not modified or called by this experiment.

The candidate caches V(oldCompression) once, uses the same convex contact
potential and nonnegative Hunt-Crossley factor, and differentiates the residual
analytically. The initial target force brackets the root because the target
decreases as force reduces compression. The derivative respects the inactive HC
clamp and positive-to-negative unloading crossings.

Subtracting near-equal potentials makes the old evaluator cancellation-prone.
A six-term integral/binomial series for positive endpoints within 1% evaluates
the same discrete-gradient law more accurately; this is an intentional algebra
change, not a claim of bit-equivalent quotient evaluation. Other crossings use
stable positive formulas. The solver permits at most 10 Newton steps and 56
fallback bisections: at most 67 residual evaluations including initialization.

## Scalar and energy checks

The independent reference uses long-double `expm1/log1p` arithmetic and up to
100 bisections. The 7,229 cases include 5,000 seeded physical-key random cases,
near-equality boundaries, zero crossings, HC clamp boundaries, zero compliance
and stiffness, multiple rates, and explicitly flagged parameter stress tests.

- All force-accuracy cases pass `abs(F-Fref)/(1+abs(Fref)) <= 1e-10`.
  The worst error is 9.69e-12; within physical ranges it is 3.33e-13.
- For reference forces above 1e-3 N, the worst pure relative error is 1.32e-11.
- Scalar work/dissipation checks pass their declared normalized 1e-10 gate.
  Within physical ranges, maximum absolute work defect is 2.00e-16 J and maximum
  negative dissipation is 2.09e-17 J.
- The original quotient/42-step result exceeds the force-accuracy tolerance in
  533 constructed cases. Its physical-range worst error is 3.94e-7, principally
  demonstrating cancellation rather than a different physical law.

Six extreme cases outside the piano's physical parameter range still return
`valid:false`; the umbrella `passed:false` remains visible. Their force estimates
meet the force-accuracy test, but their stiff residual checks fail. They are not
silently promoted to successful solves.

Both full float models pass declared component tolerances: contact relative
energy error <=5e-5, bridge relative step rise <=5e-7 and contact residual <=1e-8.
Both retain the original strict self-test's failure at its tighter double-era
threshold. Their measured conservative energy errors agree at approximately
1.1818772e-5; the candidate's contact residual improves from 2.64e-13 to 1.97e-14.

## Full-model timing and pressure

Both variants use the same g++ compiler with `-O3 -DNDEBUG -std=c++17
-ffp-contract=off`, without fast math. Construction and I/O are excluded. Each
fixture has two sequential pairs, with order reversed. This remains shared-host
evidence rather than a realtime deadline guarantee.

| Fixture | Baseline median CPU | Candidate median CPU | Speedup |
|---|---:|---:|---:|
| First 1 s of original music | 6.5688 s | 6.6265 s | 0.991x |
| All 88 keys, first 50 ms | 0.19250 s | 0.17604 s | 1.093x |

The dense fixture's maximum 64-sample CPU cost drops from 13.07–13.48 to
5.86–6.42 CPU seconds per audio second, about 2.16x using the medians of the two
peak measurements. This attack-spike reduction is the useful result. Music has
unexplained noncontact-window outliers; their actual values remain in the report
and do not support a music peak-cost improvement claim.

Both fixtures produce **identical WAV bytes and float64 pressure samples** in
both repetitions. This is limited to these short 48 kHz fixtures, not all states,
long tails, event streams or rates. Candidate failures and fallback bisections
are zero in these renders. Maximum Newton iterations are three for music and
four for the dense strike. Residual evaluations per contact fall from 45 to
3.44 and 3.66 respectively. These are residual evaluations, not pow calls.

The failure counter currently records invalid tentative forces; the diagnostic
harness rejects the render afterward. Production integration requires an
explicit failure policy. This experiment does not establish a complete realtime
API or justify removing the remaining steady-state performance work.

## Reproduce

```sh
python3 tools/probe_fast_full_contact.py
# Run only after the physical force/work gates pass and other heavy batches finish:
python3 tools/probe_fast_full_contact.py --render
```

`math-report.json` contains every aggregate gate and worst-case parameters.
`render-report.json` contains all 64-sample CPU/counter windows, raw component
checks and precise-pressure comparisons. Source, helper, compiler, binary,
tool-snapshot and output hashes preserve provenance. Earlier bounded scalar
passes remain under the `stage1-` and `stage2-` prefixes.
