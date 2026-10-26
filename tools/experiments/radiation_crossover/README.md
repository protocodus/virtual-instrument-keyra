# Fixed 400 Hz observation crossover

This is one **post-hoc TRAIN-reuse experiment** using six already observed
C3/C4/C6 cases at layers 4/12. All six pass the original pilot's unchanged
numerical gates. This does not qualify the broader TRAIN34 set, listening,
default sound, realtime processing or a Reason host. No production source,
calibration, runtime controls or defaults change.

The [original radiation-startup pilot](../causal_radiation_pilot/README.md)
remains **failed: 4/6**, with both C6 cases failing. Its published files are
reused by hash, not copied or rewritten. This separate construction was chosen
after those failures were observed; 400 Hz is an engineering choice, not an
identified piano material or radiation parameter. No cutoff sweep was run.

The fixed processing is `Y = new + LP400(old − new)`, identically for L/R,
starting from frame zero with zero filter state. The first-order prewarped
Tustin filter has `a = 0.9489645667148798` and
`b0 = b1 = 0.02551771664256012`. Its DC gain is one and Nyquist gain zero.
This retains the old low-frequency observation and the proposed high-frequency
observation with a complementary transition. Different correlated inputs can
still boost or cancel in that transition. Both source observers are causal.

The private experiment processed the existing float32 source pairs once,
emitted float32, and measured each case once with the old gain, old onset and
unchanged reference features/gates. It rendered no new instrument trajectory.
Physical-state/force evidence is inherited from the source pairs, not a new
mechanics run. Shared-board preservation follows in exact arithmetic; float
readout and output quantization prevent a claim of bit-exact component
preservation. The added filter is an observation operation, not another
physical piano part.

## What the six passes leave unresolved

| Case | C3 first 5 ms / ring reduction, dB | Largest early five-band MAE worsening, dB | Smallest gate margin, dB |
|---|---:|---:|---:|
| C3v4 | 3.806 / 4.353 | −0.148 | 0.338 |
| C3v12 | 4.266 / 4.330 | −0.140 | 0.323 |
| C4v4 | — | +0.108 | 0.493 |
| C4v12 | — | +0.108 | 0.494 |
| C6v4 | — | +0.777 | 0.223 |
| C6v12 | — | +0.446 | 0.477 |

Margins are remaining headroom to relative guards, not confidence intervals or
perceptual guarantees. For C4/C6 the gate permits at most +1 dB worsening in
each window's **mean** absolute error across five bands. C6 worsens in every
early five-band window; individual-band behavior is retained separately:

| C6 case | First 0–5 ms LF error, old → crossover, dB | Individual LF absolute-error worsening, dB | Crossover LF error at 20–50 / 50–100 ms, dB |
|---|---:|---:|---:|
| v4 | +43.223 → +44.289 | **+1.067** | **−35.982 / −36.043** |
| v12 | +36.033 → +37.389 | **+1.356** | **−36.446 / −37.999** |

Here LF means the fixed 31.25–250 Hz band. The aggregate passes can hide that
first-window regression. Large inherited low-frequency deficits also remain.
The first 5 ms has roughly 200 Hz frequency resolution, so this band does not
identify an isolated physical component. Values are fixed-gain pressure-power
errors against reference PCM, not acoustic SPL or mechanical energy. C3 still
has first-5-ms broad excess of +21.993/+31.806 dB and ring excess of
+11.836/+12.695 dB despite the reductions. These passes establish neither
accurate absolute attack/body levels nor perceived click removal.

## Evidence and review

The selected archives retain their original bytes and absolute paths.
`index.json` maps them to this checkout and pins the reused public source
package from commit `85a606b`. It deliberately omits duplicate per-case JSON,
Python bytecode, broad private completion manifests, plans and captured audio.
The combined result already contains all six case rows. Original `private` and
`published:false` labels remain as evidence of collection-time scope; this
documentation describes the later research-package publication separately.

| Item | SHA-256 |
|---|---|
| Frozen postprocessor | `636dc354c5eb475757bbf8f0a1195d7b40782dd5a72969af0127beaccdb51a3e` |
| Protocol | `90c143438639a27b073ba2c35babebc2e31d8711be35d1ebb72476eda3e16815` |
| Source/protocol freeze | `a30adc67e25c3ee6109f81750adf8b8e9016f660f89d9726bca24c46dee35782` |
| Six-case result | `e807196b36d7f9cca224630cfc7b9de64bd06c2b5ec73e9f48ff7001ae2b32ec` |
| Gate margins and C6 signed bands | `de6e106aaed99afde93cb29596a5aa9d03dc194f431e85e2417b1b19a1eaa660` |

Run the portable verifier from the repository root:

```sh
python3 tools/experiments/radiation_crossover/check.py
```

This standard-library command checks published hashes, source/protocol/opening
chronology, source-pair bindings, the exact original gate block, stored changes,
all margins, C6 signed-band caveats and independent reviews. It reads no PCM,
runs no filter and performs no new scoring. Floating tolerance applies only to
replaying stored arithmetic; gate comparisons keep their exact thresholds.
Use `--output /path/to/new-review.json` to save a new receipt. A verifier pass
means stored-evidence consistency, not independent waveform validation.

The archived `evidence/postprocess.py` has its original NumPy/SciPy imports,
absolute paths and once-only writer. It is retained for source review, not as
a portable replay command. Actual waveform verification additionally needs
the external source/crossover WAVs listed in `index.json:unbundled_audio`, plus
the original public pilot's authenticated recording/capture input bundle.
No new reference acquisition, holdout or listening approval is claimed here.

For numerical or presentation replay, set the environment **before Python
starts**, as detailed in [the replay-environment addendum](../../../docs/REPLAY_ENVIRONMENT.md):

```sh
OPENBLAS_NUM_THREADS=1 python3 tools/check_causal_radiation_review.py --recompute --capture-root /path/to/archive --output /path/to/new-numeric-review.json
OPENBLAS_NUM_THREADS=1 python3 Audio/full-radiation-pilot/export.py --inputs source-files.json --output /tmp/keyra-radiation-listening
```

The latter reproduces the **old failed-pilot presentation**, not this crossover.
Its procedural room IR needs the specified reduction environment for the
historical fingerprint. The addendum preserves the failed attempt and the
environment-only retry without rewriting the old package or its hashes.

Reference measurements use Alexander Holm's Salamander Grand Piano V3,
[CC BY 3.0](../../../References/GrandFullRange/upstream/LICENSE-CC-BY-3.0.txt).
See [corpus attribution and capture limits](../../../References/GrandFullRange/README.md).
No recording, impulse response or plugin build is bundled in this source and
evidence package. A separate [18.5-second musical comparison](../../../Audio/full-radiation-crossover/README.md)
plays old control at 0 seconds, then the fixed crossover at 9.5 seconds with
the same room and fixed gains. Its exact reproduction is presentation evidence,
not a listener verdict or broader recording validation.
