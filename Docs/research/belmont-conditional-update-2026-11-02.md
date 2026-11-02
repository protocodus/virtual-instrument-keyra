# Belmont conditional measurement repair — 2026-11-02

The proposal updates only Belmont 72, partial 2, and Belmont 81, partial 1, using the generic optional component warm start. It preserves their accepted carriers, clocks and onset floors. It fixes supported local envelope errors; it does not claim that every neighboring key, velocity or spatial statistic improves. No Brightness, Mechanics, output gain, other piano data or DSP implementation changes are included.

The combined numeric archive regenerates `MeasuredBelmontData.h` exactly: SHA256 `c8eadcc8f3a9bf3a5439ead81624de0486f6f68b5fc1c05f8b70611927c229d6`. The archive is a copy of the frozen final-v2 result, SHA256 `85ccae7c49212c44a170f3db2357ac4a40b262912273b8277346e7cd1913de26`. Its historical execution identities remain intact. Current-tool stored-number regeneration is a separate check, with no source audio, cache access or fitting.

## Recommendation and evidence

Adopt the combined local measurement repair with the tradeoffs below recorded. Belmont 72 retains the independently tested local residual noise and knock policy from the original analysis; Belmont 81 retains its accepted noise. There is no fresh global refit, velocity-law adjustment or per-key gain compensation.

For Belmont 81, the standard TRAIN scorer’s mean partial error improves by 3.643 dB, full-envelope error by 14.206 dB and sustain error by 15.623 dB. At fixed source scale, the target partial’s errors in the 1.5–3.5 s window change from −25.24, −31.19 and −22.40 dB to −6.80, −2.15 and −4.84 dB across the soft, medium and hard layers, respectively. The previously missing tail is recovered across all three recorded layers.

The frozen candidate also improves all four soft and medium RR2/RR3 recordings that were held out of fitting: envelope MAE of 17.36–21.99 dB becomes 2.88–4.03 dB, and partial MAE falls by 3.93–4.48 dB. Their fixed-scale late partial 1 stereo and mono levels both improve; each late window is above the observational tail proxy by 12–31 dB. These are repeated performances of the same instrument, not independent instruments. No hard-layer repeat exists.

The native neighborhood contains notes 78–84 at all 127 MIDI velocities under ordinary controls, Soft = 1, Width = 0 and Tube = 1: **3,556 baseline/candidate pairs**. Each profile has 889 pairs, zero nonfinite output, seven exact repeated-render controls, and all 254 endpoint renders at notes 78 and 84 bit-identical. Maximum sample peaks do not increase; the largest across these profiles is 0.04405 at the fixed 0.07 output gain. The source and dense observations use different normalization conventions and are not interchangeable loudness scores.

## Explicit tradeoffs

The dense windows are 0–50 ms, 50–300 ms, 300–750 ms and 750–1500 ms while held, followed by 1500–2000 ms after note-off. Levels below are native dBFS at gain 0.07, without listening gain. Low absolute level qualifies the evidence; it is not an audibility assertion.

| Profile | Worst new stereo velocity step, held late | Worst new stereo step, release | Largest increase in release excess variation |
|---|---:|---:|---:|
| Ordinary | −0.0327 dB at note 83, v119; −68.60 dBFS | −0.1836 dB at note 83, v63; −94.00 dBFS | +0.2321 dB at note 82 |
| Soft = 1 | −0.0347 dB at note 83, v119; −71.40 dBFS | −0.1861 dB at note 83, v63; −96.79 dBFS | +0.5489 dB at note 79 |
| Width = 0 | −0.1254 dB at note 83, v63; −80.38 dBFS | −0.1198 dB at note 83, v122; −94.48 dBFS | +1.6121 dB at note 82 |
| Tube = 1 | −0.1258 dB at note 83, v63; −78.93 dBFS | −0.1100 dB at note 83, v122; −92.67 dBFS | +1.1285 dB at note 82 |

“v63” denotes the velocity 63 → 64 step. These are new negative steps, not the largest pre-existing negative steps. All four profiles have no new **stereo** velocity reversal before 750 ms. This does not hold identically for individual channels: the ordinary and Soft left channels have small new early steps, the worst being −0.01252 dB. The Soft right channel has a −0.02130 dB middle step at note 83, v114, and its mono observation has a −0.000804 dB step. Their complete channel rows remain in the public numerical receipt.

Pitch balance is a meaningful residual cost. At note 82, velocity 66, in the 300–750 ms window, the middle key relative to its two neighbors changes from −0.228 to −4.846 dB for Width = 0 (level −77.40 dBFS), and from −0.174 to −4.770 dB for Tube = 1 (−75.42 dBFS). At note 82, velocity 64, ordinary middle-window curvature changes from −0.120 to −2.644 dB at −71.17 dBFS. These are not asserted to be recording errors at unrecorded neighbors. They expose the current interpolation’s reaction to the repaired anchor.

The largest onset level reduction is at note 83, velocity 93: −1.759 dB for Width = 0 and −1.735 dB for Tube = 1, ending at −44.13 and −42.61 dBFS, respectively. Ordinary onset falls by 1.386 dB there. The largest release curvature worsening is a quiet Width = 0 tail at note 80, velocity 1: −2.927 to −10.200 dB, at −117.69 dBFS. The report retains it rather than declaring all tails unchanged.

Source-based spatial and decay costs remain: TRAIN soft ILD error grows by 1.032 dB, fitted decay-rate error by 1.254 dB/s, and hard-layer middle partial 1 power error changes from −0.741 to −1.471 dB. Soft repeat ILD has the same 1.032 dB increase; medium repeat mono/stereo-ratio error grows by 1.755 dB despite greatly improved absolute mono tail power. Those tradeoffs do not erase the supported envelope recovery, but prevent a claim of uniform improvement.

## Preserved domains and reproducibility

Exactly 593 other partial rows, all accepted carriers, f1, B, cents and membership, clocks and onset floors, global body/action/halo/open-string/layer laws, and 26 other noise anchors remain unchanged. The combined header is the exact numeric union of the independently validated 72-only and 81-only exports. Stock velocity guards regenerate to the unchanged 405 bits. The combined engine passes the unchanged `KeyraLevels` check; no threshold or gain adjustment was made. Any later added velocity masks require their own compatibility replay against this final data.

`belmont-conditional-update-2026-11-02.json` contains public hashes, per-case source identity, decoder gain conventions, conditioning and residual proofs, actual historical operators, current regeneration identity and bounded validation outcomes. It contains no user-local source paths or audio. The library is Mom’s 1974 Baby Grand by The Imperfect Drummer/Brian Peat; its library states no license. Only fitted numeric parameters and provenance are proposed, not redistributed recordings. The original samples are peak normalized and processed; no calibrated hammer-force or untreated acoustic-loudness claim follows.

The proposed CTest runs the stored-number command with `--check` against the header **and deterministic regeneration receipt**. It requires no recordings, scientific Python, decoded caches or optimizer. It verifies reproducibility of stored data, not a fresh acoustic calibration or a listener preference. Separate normal engine/native/level gates remain required by the repository.
