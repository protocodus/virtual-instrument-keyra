# Coupled waveguide experiment

The C2/C4 experiment connects a nonlinear hammer, persistent dispersive strings and all 475 original soundboard modes with a measured numerical work balance. It establishes a bounded mechanical interface for a cheaper string representation. It does not replace the default full model or demonstrate equivalent piano sound.

`include/keyra/physics/CoupledWaveguide.h` contains the fixed-capacity runtime network. `tools/coupled_waveguide_support.h` copies authored hammer and board parameters from the unchanged working full reference during offline setup. `tests/coupled_waveguide_tests.cpp` exercises the coupled network, and `tools/probe_coupled_waveguide.cpp` produces twelve one-second diagnostic cases. The two string configurations are tracked under `tests/data/coupled-waveguide/`, with their original study hashes and limitations.

The default piano backend, calibration, Reason prototype and `Research/` remain unchanged. This network is limited to 48 kHz and a single key, with one primary string polarization and the source key's two or three choir lines. All choir lines have identical coefficients here. Real unison detuning, the original frequency-selective common-unison losses, secondary polarization and direct string radiation are absent. The preserved experiment has its damper disabled; an optional authored contact resistance now provides a bounded damper interface described below. It does not reproduce physical damper geometry or its body reaction. The raw microphone output observes board acceleration only and is not the complete calibrated pressure output of the full model.

## Contact and reciprocal bridge

Every waveguide path has a positive integer delay, so its filtered incoming waves can be read without advancing state. `ports()` exposes these known velocities and contact force mobility `1/(2Z)`. A string advances exactly once per output frame.

For `N` choir lines the hammer acts through equal positive transformer weights `t=1/N`. With old string contact displacement `y`, known contact velocity `u`, step `h`, mass `m`, and external string force `f`, the free contact displacement and scalar compliance are

```text
yFree = sum_i t * [y_i + h*(u_i + f_i/(2Z_i))]
A     = h*h/(2m) + h*sum_i t*t/(2Z_i).
```

The safeguarded contact solver evaluates the same discrete-gradient Hunt-Crossley law as the full model. Hammer motion uses midpoint force, and each string receives `t*F + f_i`. The resulting hammer/string work cancels the contact potential change plus nonnegative contact dissipation. An invalid contact solve stops the research instance; it never applies an unverified tentative force.

For the three board ports let `G` be the positive semidefinite Gram matrix of mode/port coefficients, `C` the diagonal sum of connected string impedances, and `a` the summed incoming string forces plus external board force. After exact modal rotation with positive split damping, the board midpoint velocity satisfies

```text
(I + h*G*C/2) * vMid = vFree + h*G*a/2
FBoard = a - C*vMid.
```

The board receives impulse `h*FBoard` once. The same midpoint velocity terminates each connected waveguide. The equal and opposite bridge work cancels without a fitted output gain. Coupling can be disconnected, and observation can be muted independently. Muting observation leaves the mechanical trajectory exactly unchanged.

## Loss that preserves static compliance

The earlier isolated string used scalar path attenuation. It was passive but gave nonzero DC contact mobility: a constant force could produce displacement creep. That is unsuitable for a displacement-coupled nonlinear hammer.

An optional positive low shelf now preserves unity DC transmission. It is disabled by default in `WaveguideString`, preserving the old isolated study's arithmetic and output digest. The coupled experiment enables it with a 2 Hz pole. For filtered input `x`, pole `p` and high-frequency gain `g`,

```text
s' = p*s + (1-p)*x
y  = g*x + (1-g)*s'
stored energy / (h*Z) = (1-g)*p/(1-p) * s*s
loss / (h*Z) = (1-g)*p*(x-s)^2 + g*(1-g)*(x-s')^2.
```

Both loss terms are nonnegative. The existing orthogonal allpass and FIR storage remain included. Independent state/transfer tests check the actual shelf response. Its phase affects tuning; the old scalar-loss frequency fit is not silently treated as a new coupled fit.

## Repetition and energy accounting

The shared `StrikeController` admits a new launch only after the previous hammer is inactive, separated and sufficiently recovered. An explicit touching note-off/note-on pair completes finite key lift. A partial return retains the separated hammer position and reduces the launch velocity. The already vibrating waveguide rails, filters, contact displacement and board modes persist through every event. Humanization changes hammer speed and hardness with a deterministic correlated seed; it does not reset phase or tuning.

The global ledger includes string rails and filter storage, board energy, active hammer kinetic/contact potential energy, external force work, hammer launch work, positive path/board/contact loss, and energy removed when a separated hammer retires. Retirement removes no string or board state. Runtime diagnostics can scan all stored states; that scanning is deliberately separate from the per-step coupling calculations.

## Optional continuous damper load

`Config::damperEnabled` defaults to false. Its disabled force path preserves the prior twelve diagnostic WAVs exactly. Enabling a zero-strength load also preserves the mechanical output exactly. The original source and receipt remain frozen under `out/coupled-waveguide-damper/control/` and `out/coupled-waveguide/source-snapshot/`.

The new load is a nonnegative memoryless resistance `Rd` at each string's existing hammer contact. With known incoming velocity `u`, external force `f`, hammer transformer weight `t`, and hammer force `FH`,

```text
M       = 1/(2Z + Rd)
vFree   = (2Z*u + f)*M
v       = vFree + t*FH*M
FString = t*FH + f - Rd*v
damper dissipation = h*Rd*v*v.
```

Hammer free displacement uses `vFree`, and its scalar contact compliance becomes `h*h/(2m) + h*sum(t*t*M)`. Thus the force solve sees the damper load while contact is active. The bridge solve is unchanged. The string receives `FString` once, and the ledger adds positive damper dissipation once. String/board work plus hammer kinetic and contact-potential changes, contact loss and damper loss equal external force work. Changing `Rd` adds no hidden storage, displacement reset, or source impulse.

`setPedal(1)` means sustain pedal depressed and dampers lifted; `setPedal(0)` lets dampers return on released keys. A down key always requests zero closure. Otherwise the normalized target closure is `1-pedal`. Closure approaches its target exponentially, with authored 1 ms lift and 10 ms return defaults. Resistance is `2Z*strength*closure*closure`; half pedal therefore produces a quarter of the fully returned resistance. `pedal()`, `damperClosure()` and `damperTargetClosure()` expose the control state, while each frame reports resistance, signed damper force, string contact velocity and dissipated work. The strength/timing controls are bounded, experimental parameters, not measured felt or action properties.

Pedal, key-release and load-bypass events preserve all stored mechanical energy and accumulated loss. Restrikes lift the load through the same bounded control without resetting rails or board modes, and retain the existing separated-hammer/recovery gates. The tests cover partial return, changing pedal while strings ring, and bypassing/re-enabling a loaded string.

In the one-second C2/C4 tests the key releases at 100 ms. Pedal 0, 0.5 and 1 give strictly ordered tail energy and final energy in both cases. For C2, the final energies are `1.30e-8`, `1.71e-6` and `4.25e-3 J`; for C4 they are `9.09e-11`, `1.73e-10` and `8.70e-5 J`. These values show the control's mechanical effect; they are not recorded-piano decay targets. Maximum global balance residual in these six loaded cases is `9.91e-15 J`, and the implicit damper velocity differs from the actual string junction by at most `4.45e-16 m/s`. A separate varying-pedal test with independent string and board forces checks signed external work; its maximum damper force/work discrepancy is `4.97e-24 J`.

The twelve prior diagnostic WAVs remain byte-identical with the load disabled. `probe_coupled_waveguide OUTPUT_DIR PROFILE_DIR --damper` adds pedal 0/half/1, load-off, coupling-off, observer-off, source-off, dynamic-pedal and repeated-strike cases for both notes. The new proof is recorded in `Validation/coupled-waveguide-damper.json`, with native and one ASAN/UBSAN test run and frozen source/artifact hashes.

This is deliberately a damper **proxy**. Its contact point coincides with the hammer, so it does not reproduce a real damper's position-dependent modal losses, felt contact, inertia, noise or reaction through the piano body. With no pre-roll, the authored finite lift initially loads even a first strike with pedal 1: the test removes approximately `0.00784 J` for C2 and `0.00475 J` for C4 while the initially closed load opens. The near-string hammer launch shortcut omits the real travel interval that normally precedes impact. No attack or release realism claim follows from this numerical interface proof.

## Validation and limits

Native tests pass for C2/C4 with passive losses enabled and disabled. The maximum global balance residual over the four one-second strike cases is `5.74e-14 J`, and the maximum single-step interaction residual is `1.77e-17 J`. Unforced tails do not grow beyond rounding error. A board-only force transfers energy into unstruck strings; disabling coupling gives exactly zero string energy. Observation-off trajectories remain identical.

At touching 10 Hz, all three requested strikes launch, including two partial-recovery strikes. Note events leave existing string and board energy exactly unchanged. The repeated C4 trajectory has a final global residual of `4.44e-16 J`. Runtime allocation instrumentation detects no allocations. The test source has no runtime locks or I/O in the network. Sanitizer and reproducibility receipts are recorded separately in `Validation/coupled-waveguide.json` and the shelf review cited there.

The probe's raw floating-point WAVs under `out/coupled-waveguide/render/` are diagnostics with no normalization, limiter, room or final radiation calibration. Their amplitudes can exceed a conventional audio player's full scale. They are not listening comparisons. Probe CPU timing includes energy scans and one key only; it is not a callback deadline test or a prediction of full-keyboard CPU use.

Before any replacement is considered, the representation must match important contact/bridge admittances and radiation as well as pole frequencies, then add the missing polarization, unison and physical damper interactions. The earlier high-treble dispersion errors remain unresolved. A positive energy ledger proves stability of this implemented network, not fidelity to a recorded piano.
