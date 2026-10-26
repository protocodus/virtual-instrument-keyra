#!/usr/bin/env python3
"""Validate factual material inputs and positive reduced constitutive models.

This checks the actual C++ material header, not a second Python implementation.
It does not calibrate a soundboard, a felt contact, or a complete piano.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / 'include/keyra/physics/Materials.h'
SOURCES = ROOT / 'References/Materials/sources.json'
PROGRAM = r'''
#include "keyra/physics/Materials.h"
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
using namespace keyra::physics::materials;
int main() {
  int failures=0;
  const auto check=[&](bool ok){if(!ok)++failures;};
  const double nan=std::numeric_limits<double>::quiet_NaN();
  for(const auto& wood:soundboardWoods) {
    check(validWood(wood));
    const auto plate=plateStiffness(wood,.0095);
    const auto thick=plateStiffness(wood,.019);
    check(plate.valid&&plate.d11*plate.d22>plate.d12*plate.d12&&plate.d66>0);
    check(std::abs(thick.d11/plate.d11-8)<1e-12);
    check(std::abs(thick.massPerArea/plate.massPerArea-2)<1e-12);
    for(double x:{-1.,-.2,0.,.7,1.})for(double y:{-1.,-.1,.3,1.})
      check(plate.d11*x*x+2*plate.d12*x*y+plate.d22*y*y>0||x==0&&y==0);
    check(!plateStiffness(wood,nan).valid&&!plateStiffness(wood,-.01).valid);
  }
  check(validWood(mapleBridge));
  check(validSolid(musicWire)&&validSolid(copperWinding)&&validSolid(acrylicKeyTop));
  check(std::abs(keyWoods[0].densityKgM3()-448)<1e-12);
  check(std::abs(keyWoods[1].densityKgM3()-414.4)<1e-12);
  const auto plain=stringSection(StringConstruction::PlainSteel,.001,.001);
  const auto wound=stringSection(StringConstruction::CopperWoundSteel,.001,.002);
  check(plain.valid&&wound.valid&&wound.linearDensityKgM>plain.linearDensityKgM);
  check(plain.coreBendingRigidityNm2==wound.coreBendingRigidityNm2);
  check(!stringSection(StringConstruction::PlainSteel,nan,.001).valid);
  check(!stringSection(StringConstruction::CopperWoundSteel,.002,.001).valid);
  check(!stringSection(static_cast<StringConstruction>(255),.001,.001).valid);
  std::cout<<std::setprecision(17)<<"{\"failures\":"<<failures<<",\"woods\":[";
  for(unsigned i=0;i<soundboardWoods.size();++i) {
    const auto& w=soundboardWoods[i];
    std::cout<<(i?",":"")<<"["<<w.densityKgM3<<","<<w.longitudinalPa<<","<<w.radialPa<<","<<w.shearLRPa<<","<<w.poissonLR<<"]";
  }
  std::cout<<"],\"key_densities\":["<<keyWoods[0].densityKgM3()<<","<<keyWoods[1].densityKgM3()<<"]}\n";
  return failures?1:0;
}
'''


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cxx',default='g++')
    parser.add_argument('--report',type=Path,default=ROOT/'References/Materials/checks.json')
    args=parser.parse_args()
    source=json.loads(SOURCES.read_text())
    ids=set(re.findall(r'"([A-Z][A-Z0-9_]+)"',HEADER.read_text()))
    missing=ids-set(source['sources'])
    if missing:raise ValueError(f'Unresolved material source IDs: {sorted(missing)}')
    with tempfile.TemporaryDirectory(prefix='keyra-materials-') as temporary:
        path=Path(temporary);(path/'check.cpp').write_text(PROGRAM)
        command=shlex.split(args.cxx)+['-std=c++17','-O2','-fno-exceptions','-fno-rtti','-fno-builtin',
                                     '-I'+str(ROOT/'include'),str(path/'check.cpp'),'-o',str(path/'check')]
        subprocess.run(command,check=True)
        result=json.loads(subprocess.check_output([str(path/'check')],text=True))
    expected=[source['sources']['BE2013_T1']['values'][name] for name in ('sitka_spruce','norway_spruce')]
    for actual,record in zip(result['woods'],expected):
        assert actual==[record[key] for key in ('density_kg_m3','E_L_Pa','E_R_Pa','G_LR_Pa','nu_LR')]
    report={'schema_version':1,'passed':True,'actual_header_probe':result,
            'source_ids_resolved':sorted(ids),'header_sha256':hashlib.sha256(HEADER.read_bytes()).hexdigest(),
            'sources_sha256':hashlib.sha256(SOURCES.read_bytes()).hexdigest(),
            'checks':['Actual C++ header/source data agree','Positive elastic energy for both soundboards',
                      'Plate thickness has cubic stiffness and linear mass scaling','Invalid geometry rejected',
                      'Moisture-specific gravity converted to current bulk density',
                      'Winding adds mass without pretending copper is the steel core bending stiffness'],
            'limits':'Constitutive/source checks only. No acoustic measurement or assembled instrument/contact identification.'}
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'passed':True,'sources':len(ids),'report':str(args.report)},indent=2))


if __name__=='__main__':main()
