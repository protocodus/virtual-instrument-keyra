#!/usr/bin/env python3
"""Rebuild or verify the exact, full-topology reference optimization.

The research files are inputs only. Hashes deliberately pin the starting model
and this tested performance-only candidate. Intentional acoustic development may
establish a new reviewed version, evaluated against recordings and listening.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASELINE_SHA256 = "732f2ef6054b6536197351cab928ecadbcdd05ef870f533db93ec04ff88e8889"
CALIBRATION_SHA256 = "619d6bf4d3200a6b55007a1abcc0658e76a14124ce5f3abad9f5f4b94d8979f7"
LOOP_FUSION_SHA256 = "02d5ae237006eb5e5a16fdea53e5cbf68c2b65b608e9738b9947fe9301c67ef7"
LAYOUT_EXPERIMENT_SHA256 = "d8cd5ee7522936dba072e205e8d72a880187188a5d98afee2236bec7588cbace"
OPTIMIZED_SHA256 = "0de379e97ceb26851c92c19f41f065bc554346e916dc0b91bac5117a1c4267e2"

# The reviewed grouped scalar layout, without the experiment's unused GNU
# vectorStep member. Keep canonical source parseable without vector extensions.
PORTABLE_GROUP_CLASS = r'''
// Setup-only cache of contiguous unison rows. Every source row remains present;
// detuned upper-partial membership changes start a new run rather than dropping
// a participant. Canonical double states retain their original q/p storage.
struct UnisonGroup {
  int count=0;
  std::array<double*,3> velocity{};
  std::array<std::vector<double>,3> omega,inverse;
  std::vector<double> coefficient;
  template<int N> void scalarStep(){
    double *__restrict p0=velocity[0],*__restrict p1=velocity[1],*__restrict p2=velocity[2];
    const double *__restrict w0=omega[0].data(),*__restrict w1=omega[1].data(),*__restrict w2=omega[2].data();
    const double *__restrict r0=inverse[0].data(),*__restrict r1=inverse[1].data(),*__restrict r2=inverse[2].data();
    const double *__restrict c=coefficient.data();
    for(size_t i=0;i<coefficient.size();++i){
      double sum=w0[i]*p0[i];
      if constexpr(N>1)sum+=w1[i]*p1[i];
      if constexpr(N>2)sum+=w2[i]*p2[i];
      double impulse=c[i]*sum;
      p0[i]-=impulse*r0[i];
      if constexpr(N>1)p1[i]-=impulse*r1[i];
      if constexpr(N>2)p2[i]-=impulse*r2[i];
    }
  }

};
'''


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(source: str, old: str, new: str) -> str:
    if source.count(old) != 1:
        raise ValueError("Expected exactly one frozen-source match: " + old[:70])
    return source.replace(old, new, 1)


def loop_fusion(source: str) -> str:
    source = replace_once(source, "  void finishDamping(){", """  // Exact-order free/damping fusion only while this key has no active hammer.
  void freeDampedStep(){
    double *__restrict yq=q.data(),*__restrict yp=p.data();
    const double *__restrict yc=c.data(),*__restrict ys=s.data(),*__restrict yd=damp.data();
    for(size_t i=0;i<size();++i){
      double v=yp[i]*yd[i],y=yq[i];
      yq[i]=yc[i]*y+ys[i]*v;
      double rotated=yc[i]*v-ys[i]*y;yp[i]=rotated*yd[i];
    }
  }
  void finishDamping(){""")
    source = replace_once(source, """  void portImpulse(double impulse){
    double *__restrict yp=p.data();const double *__restrict bi=portInverse.data();
    for(size_t i=0;i<size();++i)yp[i]+=bi[i]*impulse;
  }
""", """  void portImpulse(double impulse){
    double *__restrict yp=p.data();const double *__restrict bi=portInverse.data();
    for(size_t i=0;i<size();++i)yp[i]+=bi[i]*impulse;
  }
  // Update and observe one string while its q/p state is hot. The reduction
  // order within the string is unchanged, and callers add cached strings in
  // the original order after the board's acceleration observation.
  std::array<double,2> portImpulseRadiation(double impulse){
#pragma clang fp reassociate(on)
    double *__restrict yp=p.data();
    const double *__restrict bi=portInverse.data();
    double l=0,r=0;
    for(size_t i=0;i<size();++i){
      yp[i]+=bi[i]*impulse;
      l+=radQL[i]*q[i]+radPL[i]*yp[i];
      r+=radQR[i]*q[i]+radPR[i]*yp[i];
    }
    return {l,r};
  }
""")
    source = replace_once(source,
        "  double resistance=.85,compliance=0,velocity=0,force=0;",
        "  double resistance=.85,compliance=0,velocity=0,force=0;\n  std::array<double,2> cachedRadiation{};")
    source = replace_once(source, "    for(auto &k:keys){\n      double y0=0;",
        "    for(auto &k:keys){\n      if(!k.hammerActive){for(int i:k.strings)strings[i].m.freeDampedStep();continue;}\n      double y0=0;")
    source = replace_once(source, "  void bridgeStep(double step){",
        "  void bridgeStep(double step,bool cacheRadiation=false){")
    source = replace_once(source,
        "      auto &k=keys[st.note-21];if(!opt.sympathetic&&!k.everStruck)continue;",
        """      auto &k=keys[st.note-21];
      if(!opt.sympathetic&&!k.everStruck){
        if(cacheRadiation)st.cachedRadiation=st.m.radiation();
        continue;
      }""")
    source = replace_once(source,
        "      st.force-=r*correction[st.group]/den;st.m.portImpulse(step*st.force);",
        """      st.force-=r*correction[st.group]/den;
      if(cacheRadiation)st.cachedRadiation=st.m.portImpulseRadiation(step*st.force);
      else st.m.portImpulse(step*st.force);""")
    source = replace_once(source, "    oscillators();unisonStep();bridgeStep(dt);",
        """    bool cachedRadiation=opt.calibrated&&piano_calibration::radiationEnabled&&opt.bridge>0;
    oscillators();unisonStep();bridgeStep(dt,cachedRadiation);""")
    return replace_once(source,
        "    if(opt.calibrated&&piano_calibration::radiationEnabled)for(auto &st:strings){auto r=st.m.radiation();out[0]+=r[0];out[1]+=r[1];}",
        "    if(opt.calibrated&&piano_calibration::radiationEnabled)for(auto &st:strings){auto r=cachedRadiation?st.cachedRadiation:st.m.radiation();out[0]+=r[0];out[1]+=r[1];}")


def grouped_unisons(source: str) -> str:
    source = replace_once(source, "class Piano {", PORTABLE_GROUP_CLASS + "\nclass Piano {")
    source = replace_once(source, "  std::vector<UnisonPort> unisonPorts;",
        "  std::vector<UnisonPort> unisonPorts;\n  std::vector<UnisonGroup> unisonGroups;")
    source = replace_once(source, "    setDamping();\n    if(opt.calibrated)buildRadiation();",
        "    setDamping();\n    if(opt.calibrated)buildRadiation();\n    buildUnisonGroups();")
    start = source.index("  void unisonStep(){")
    end = source.index("\n  void noteOn(", start)
    direct_step = source[start:end]
    grouped_step = r'''  void buildUnisonGroups(){
    unisonGroups.clear();
    for(const auto& port:unisonPorts){
      bool contiguous=!unisonGroups.empty()&&unisonGroups.back().count==port.count;
      if(contiguous){const auto& group=unisonGroups.back();
        for(int lane=0;lane<port.count;++lane)
          contiguous=contiguous&&port.velocityState[lane]==group.velocity[lane]+group.coefficient.size();
      }
      if(!contiguous){unisonGroups.emplace_back();auto& group=unisonGroups.back();group.count=port.count;group.velocity=port.velocityState;}
      auto& group=unisonGroups.back();group.coefficient.push_back(port.coefficient);
      for(int lane=0;lane<port.count;++lane){group.omega[lane].push_back(port.omega[lane]);group.inverse[lane].push_back(port.inverseOmega[lane]);}
    }
  }
''' + direct_step + r'''
  void groupedUnisonStep(){
    for(auto& group:unisonGroups){
      if(group.count==1)group.scalarStep<1>();
      else if(group.count==2)group.scalarStep<2>();
      else group.scalarStep<3>();
    }
  }
'''
    source = source[:start] + grouped_step + source[end:]
    return replace_once(source, "    oscillators();unisonStep();bridgeStep(dt,cachedRadiation);",
        "    oscillators();groupedUnisonStep();bridgeStep(dt,cachedRadiation);")


def optimize(source: str) -> str:
    fused = loop_fusion(source)
    if digest(fused.encode("utf-8")) != LOOP_FUSION_SHA256:
        raise ValueError("Intermediate source differs from the independently tested loop-fusion candidate")
    return grouped_unisons(fused)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="Regenerate the local copies and provenance")
    mode.add_argument("--check", action="store_true", help="Check local copies without writing (the default)")
    parser.add_argument("--reference-root", type=Path, default=ROOT / "Research/GrandPianoV2")
    args = parser.parse_args()

    original = (args.reference_root / "src/grand.cpp").read_bytes()
    calibration = (args.reference_root / "src/calibration.h").read_bytes()
    if digest(original) != BASELINE_SHA256 or digest(calibration) != CALIBRATION_SHA256:
        parser.error("Frozen original or calibration hash changed; a new quality review is required")
    candidate = optimize(original.decode("utf-8")).encode("utf-8")
    if digest(candidate) != OPTIMIZED_SHA256:
        parser.error("Generated source differs from the reviewed portable grouped-unison candidate")
    provenance = {
        "schema_version": 2,
        "performance_version": "full-reference-2",
        "baseline_source": "Research/GrandPianoV2/src/grand.cpp",
        "baseline_sha256": BASELINE_SHA256,
        "calibration_source": "Research/GrandPianoV2/src/calibration.h",
        "calibration_sha256": CALIBRATION_SHA256,
        "optimized_sha256": OPTIMIZED_SHA256,
        "loop_fusion_sha256": LOOP_FUSION_SHA256,
        "layout_experiment_sha256": LAYOUT_EXPERIMENT_SHA256,
        "generator_sha256": digest(Path(__file__).read_bytes()),
        "validated_variant": "grouped_unison_portable",
        "validation_reports": ["Validation/reference-optimization.json", "Validation/full-layout-optimization.json",
                               "Validation/full-reference-parity.json", "Validation/full-reference-unison-physics.json"],
        "transformations": ["inactive-hammer free/damping loop fusion", "string port-impulse/radiation loop fusion",
                            "contiguous grouped scalar unison rows"],
        "portable_layout_adaptation": "Unused GNU vectorStep removed; original direct unisonStep retained; production uses groupedUnisonStep",
        "topology": {"keys": 88, "strings": 230, "string_modes": 17778, "soundboard_modes": 475},
        "physics_or_calibration_removed": False,
    }
    files = {"grand.cpp": candidate, "calibration.h": calibration,
             "provenance.json": (json.dumps(provenance, indent=2) + "\n").encode("utf-8")}
    for name, data in files.items():
        path = HERE / name
        if args.write:
            path.write_bytes(data)
        elif not path.is_file() or path.read_bytes() != data:
            parser.error(str(path) + " differs; inspect changes before explicitly regenerating with --write")
    print("Full reference copies " + ("regenerated" if args.write else "verified") + "; frozen research inputs unchanged.")


if __name__ == "__main__":
    main()
