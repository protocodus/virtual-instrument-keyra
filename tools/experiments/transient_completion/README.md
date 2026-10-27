# Contact-driven transient completion — offline studies

**Runtime sound and defaults are unchanged.** Both full-range candidates pass
33/34 original preservation cases and fail C8v12. The later frequency-aware
operator improves the early average, but still misses the unchanged C8 limit.
Neither result establishes that the reported click sounds better.

These studies address the excessive start of the original radiation readout.
They retain the saved original physical trajectory and add a separate, short
memory observation driven by its actual solved contact forces. They do not
identify the click as a key, hammer, frame or other physical part. In particular,
this is not a newly measured key-down sound or a replacement action model.

| Frozen study | All original gates passed | Result |
|---|---:|---|
| `v1`: uniform loss, empirical string correction only | 2/6 | C3 ringing worsens; C6 loses body. |
| `v2`: uniform loss, complete pressure | 4/6 | C3 passes; both C6 cases fail early band preservation. |
| `lf-protected-v1`: fixed 200 Hz high-pass on counterterm | 5/6 | C6v12 misses the 5–20 ms limit. |
| `pitch-scaled-v1`: key frequency controls extra loss | 6/6 | Pilot passes. |
| `train34`: same pitch-scaled operator, full TRAIN | 33/34 | C8v12 misses the 5–20 ms limit; global failure retained. |
| `modal-scaled-v1`: key and modal frequency control extra loss | 6/6 | Pilot passes. |
| `modal-train34`: same frequency-aware operator, full TRAIN | 33/34 | C8v12 still misses the 5–20 ms limit; global failure retained. |

Every six-case pilot uses C3/C4/C6 at the already observed v4/v12 layers. Each
later design is posthoc engineering informed by the preceding failures. One
frozen law is evaluated per study, without an internal parameter sweep, fitting,
per-note output exception, new gain or shifted onset. This sequence is not fresh
validation and should not be presented as one predeclared candidate.

## What the observer computes

An additional copy of the original string/board model receives the saved
contact forces at their original position in the split recurrence. Its own
unison and three-port bridge solve remain active. Captured bridge forces
authenticate the input history; they are never injected as a second drive into
this companion. The saved primary trajectory and its raw output are unchanged.

Before each companion free update, both coordinates of every selected modal
pair are multiplied by `exp(-gamma / sample_rate)`. The first two studies use
gamma 100/s throughout. The later pitch law uses

```text
string gamma(key) = 100 * max(1, f0(key) / f0(C3))
board gamma       = 100
```

The frequency-aware law additionally shortens the memory of high modes on
lower, unstruck keys and of high board modes:

```text
string gamma(key, mode) = 100 * max(1, f0(key)/f0(C3), f_mode/1000 Hz)
board gamma(mode)       = 100 * max(1, f_board/1000 Hz)
```

Frequencies come from the actual prepared model. The same rule applies to every
key, choir and mode; there is no C8 branch. The 1 kHz boundary is an engineering
choice, not measured physical damping. A nominal modal damping law does not
prove a bound on the coupled network's eigenvalue quality factors.

`v1` subtracts the companion's empirical string correction. `v2` subtracts its
complete pressure: board acceleration, including instantaneous force, plus the
string correction. From `lf-protected-v1` onward the operator is

```text
candidateRaw = savedOriginalRaw - HP200(companionCompletePressure)
candidate    = float32(originalHP24(candidateRaw))
```

The bilinear first-order HP200 uses identical coefficients for L/R, zero initial
state and continuous state across blocks. HP24 is the original output filter.
Neither filter resets on note events. There is no MIDI-age gate, recording
sample playback or changed static radiation coefficient.

Uniform scaling nominally gives `A_fast = rho*A`. A mode-dependent diagonal
scale does not commute with the bridge coupling; the scalar impulse-ramp
identity does **not** apply to either nonuniform law. The original physical
poles and observation remain in the saved primary signal, while the additional
observer has deliberately faster memory.

## Numerical controls and acoustic limits

The original full rho=1 force replay reproduces all six raw original/body
captures bit for bit. Later studies reuse that historical implementation
control. Each nonuniform pilot also runs its actual new scaling routine with
every gamma set to 100 and requires complete-pressure bit identity against the
uniform observer through the fixed old onset plus 250 ms. Full TRAIN confirmation
reuses those six exact pilot outcome objects and emits only the other 28 cases;
it does not claim 28 additional rho=1 or uniform-prefix controls.

Recorded checks cover finite state, model dimensions, authenticated force
histories, no new faults, energy contraction and a conservative complete
pressure bound. That bound includes current force feedthrough; end-state energy
alone would not suffice. When zero-input future pressure is bounded below
1e-20, only companion coordinates may be cleared. Filters retain state and a
later force wakes the companion. Synthetic retirement/wake and arbitrary-block
filter tests pass. FNV force checks are not cryptographic collision proofs.

Every acoustic score uses the emitted float32 candidate, the immutable original
gate arithmetic, fixed old gains/onsets and frozen reference masks. The C3
criteria require at least 3 dB less first-5ms positive excess and 5–20ms ringing
excess. Other keys allow at most 1 dB early-window band-MAE worsening. Original
late harmonic, envelope, RMS and sustain stereo guards remain unchanged.

The pitch-scaled full TRAIN failure is specific: C8v12's 5–20 ms five-band MAE
increases from 6.2822 to 7.7053 dB, **+1.4231 dB**. Its 250–1000 Hz and 1–4 kHz
bands become quieter where the original was already deficient. All 34 late and
sustain stereo guards pass. Whole-note and early stereo are stored diagnostics,
not those gates: C8v12's whole-note L/R changes −1.121 dB and mono energy
−1.938 dB. Signed errors remain available because reducing positive excess can
also reward excessive attenuation.

C8v4's short reference supplies only three complete late spectral windows,
through 2.5 s, and full-support envelope samples through 2.80 s. No missing tail
is padded, clipped into a substitute window or extrapolated. Its weak H1 and
unassigned components retain their existing interpretation.

The frequency-aware confirmation improves the all-34 mean early five-band MAE
from 14.963 to 13.730 dB, with every first-5ms band-MAE improving by 1.966–6.066 dB.
It still fails C8v12: 5–20 ms MAE is 7.4252 dB, **+1.1430 dB** over the original,
above the unchanged +1 dB allowance. All 34 late and sustain stereo guards pass.
Whole-note preservation is not established: C8v4 mono energy changes −4.935 dB
and its first-5ms mono energy changes −5.629 dB. C8v12 whole-note L/R changes
−1.018 dB and mono energy −1.852 dB. These diagnostic changes remain visible;
the aggregate improvement does not remove the failed gate or qualify stereo
behavior. No later parameter tuning is included in this archive.

This is the frozen historical 5-anchor model at 48 kHz stereo, with humanization
and mechanisms off and repetition control bypassed. The full 17,778-string-mode
plus 475-board-mode companion is an **offline quality proof**, not an efficient
realtime architecture. It adds substantial computation. Numerical preservation
does not establish perceived click removal, current connected/default behavior,
other sample rates, unseen piano recordings or Reason/Recon/U45 readiness.

## Inspect and reproduce the evidence

From the repository root:

```sh
python3 tools/experiments/transient_completion/check.py
```

The standard-library checker verifies archived identities, frozen source/input
bindings, stored numerical predicates, the exact original gate arithmetic, all
case decisions, complete support and pilot-object reuse. It does not decode
audio, rerun a physical model, calculate spectral features or assess hearing.
Independent private post-run audits additionally rescored all 34 pitch-scaled
and all 34 frequency-aware float32 candidate outputs exactly; both receipts are
included.

`index.json` maps immutable historical paths and decoded SHA256 identities to
this checkout. JSON is losslessly gzip-compressed with timestamp zero; source
is retained verbatim. Repeated content and prior public evidence are reused by
hash. Raw pressure, force/proof traces, PCM, compiled binaries and caches remain
external identities. Closed publication-time logs are included; the original
study manifests deliberately exclude their live outer `run.log` files.

The archived runners retain absolute paths and once-only guards. They are review
sources rather than portable launchers. To reproduce a study, use a separate
workspace, map its declared historical paths, restore the exact external
simulation traces and source identities, and preserve the original compile
flags, coefficients, gains, onsets and support rules. Set
`OPENBLAS_NUM_THREADS=1` before NumPy starts. Declare that reproduction separately
instead of overwriting the original frozen files. No experiment is rerun for
publication.

Reference targets derive from Alexander Holm's Salamander Grand Piano V3,
[CC BY 3.0](../../../References/GrandFullRange/upstream/LICENSE-CC-BY-3.0.txt),
with [attribution and recording limits](../../../References/GrandFullRange/README.md).
Existing source retains its ownership terms; this archive adds no license grant.

The separate [musical evidence archive](music/README.md) preserves the matched
diagnostic passage, physical/output controls and fixed presentation receipts.
Its verifier also checks the published FLAC identities. The candidate's global
33/34 failure and absent listener verdict remain explicit.
