# Physical material evidence and limits

Default recording agreement takes priority over material variety. The live
preview's Spruce/Cedar/Maple names remain **authored voicings**, not measured
species substitutions. This evidence table supplies the separate mechanical
candidate; it does not silently change the live default or add product controls.

## Small, documented material set

The soundboard candidate has two published orthotropic inputs:

| Material | Density kg/m³ | E longitudinal GPa | E radial GPa | G LR GPa | ν LR |
|---|---:|---:|---:|---:|---:|
| Sitka spruce | 392 | 11.5 | 0.47 | 0.50 | 0.30 |
| Norway spruce | 440 | 15.8 | 0.85 | 0.84 | 0.30 |
| Maple bridge | 660 | 10.0 | 2.20 | 2.00 | 0.30 |

These are the piano-model literature inputs of [Boutillon and Ege, Table1](https://arxiv.org/abs/1305.3057v1).
The table traces earlier studies; it does not report a common moisture condition
or identify our recorded instruments. Wood variability, grain, ribs, crown,
lamination, glue and boundary mobility remain separate variables. No fabricated
species-specific damping coefficient is included.

The physical plate helper enforces elastic reciprocity and positive strain
energy. Its thickness and shape come from the model geometry, not from the
material name. A thin homogeneous plate is still an approximation of a real
ribbed/crowned soundboard.

For key sticks, two documented construction choices are retained: Sitka spruce
and American basswood. [USDA FPL-GTR-190, Table5–3a](https://www.fpl.fs.usda.gov/documnts/fplgtr/fpl_gtr190.pdf)
supplies specific gravity and bending modulus at **12% moisture**. At that
condition the derived densities are **448 and 414.4 kg/m³**, respectively.
Specific gravity there uses oven-dry mass, so multiplying by1000 alone would
understate current specimen mass. These are clear-specimen averages, not an
assembled key's effective mass. Inertia still needs actual geometry and lever arms.

[Yamaha's construction guide](https://hub.yamaha.com/pianos/p-acoustic/a-brief-guide-to-piano-tonewoods/)
supports these woods and maple/beech structural construction. It is construction
evidence, not a market-share ranking or an acoustic calibration. Bridge/rim
laminates are not replaced by a guessed generic solid-wood damping value.

## Metals, keytops, and contact materials

The table retains one high-carbon music-wire core and one copper winding proxy.
[Sato and Samejima2023, Table1](https://doi.org/10.1250/ast.44.230) supplies the
piano-string model values **7850 kg/m³, 200 GPa and ν=0.3**. The
[Copper Development Association](https://alloys.copper.org/alloy/C11000) supplies
typical C11000 density and elastic moduli. Copper is used to add wrap mass;
its solid modulus is not the effective modulus of a wound piano string.
Wrap geometry, packing, contact/slip and loss need separate identification.

Acrylic is documented as a keytop construction by
[Yamaha](https://www.yamaha.com/en/musical_instrument_guide/piano/manufacturing/manufacturing002.html).
The PMMA entry uses typical bulk sheet data from the
[manufacturer's technical information](https://www.plexiglas.de/files/plexiglas-content/pdf/technische-informationen/232-32-PLEXIGLAS-Soundstop-XT_EN.pdf).
It is a material proxy, not a verified piano formulation or a skin-contact law.

Hammerfelt has one supported composition: wool. Its compressed density,
nonlinear stiffness, hysteresis, relaxation and voicing are intentionally **not**
filled with a fiber tensile modulus. Experiments show why that would be wrong:
[Yanagisawa and Nakamura1984](https://doi.org/10.20697/jasj.40.11_725) measured
dynamic force and deformation, and [Stulov1995](https://doi.org/10.1121/1.411912)
modeled history-dependent loading and unloading. The candidate contact solver's
authored parameters must remain labeled as assumptions until separately measured.

## Air, lid, and player boundary

Dry air uses an ideal-gas approximation, with temperature in kelvin;
[NPL](https://www.npl.co.uk/getattachment/19d0d4d3-5bd9-47d9-b392-01be4c8e453d/Speed-of-Sound-Toilet-Roll-Report.pdf?lang=en-GB)
provides its sound-speed context and humidity limitation. It does not validate
room reverberation or humid-air attenuation.

The lid's composition/layup and seated player's local complex acoustic impedance
are **unidentified**. A room-absorption result cannot simply become a local
resistance. [Sabbagh and Elkhateeb2021](https://doi.org/10.1016/j.apacoust.2021.108317)
provides posture/clothing context, not a calibrated pianist boundary. No new
numeric material variants are added to hide these gaps.

## Traceability and checks

[sources.json](../References/Materials/sources.json) records source URLs, exact
table locations, conditioning caveats, conversions, downloaded-document hashes
where available and explicit missing data. Full papers, images and handbooks
are not redistributed. Run:

```sh
python3 tools/check_materials.py
```

The check compiles the actual C++ table with exception-free/no-builtin flags,
compares factual values with the source records and tests positive plate energy,
geometry bounds, moisture conversion and core/wrap separation. This establishes
internal consistency, not acoustic fidelity or a uniquely identified material.
