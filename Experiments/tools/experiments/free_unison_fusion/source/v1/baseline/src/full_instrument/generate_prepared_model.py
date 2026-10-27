#!/usr/bin/env python3
"""Reproduce the private full-instrument model from an explicit renderer source.

Only standard Python is required. Precision transforms are copied verbatim from
tools/probe_full_precision.py: precision() and hot_precision(). Default inputs
are the immutable working control; an alternate prepared renderer requires an
explicit calibration header and never silently promotes a fitted candidate.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PINNED_SOURCE = "0de379e97ceb26851c92c19f41f065bc554346e916dc0b91bac5117a1c4267e2"
PINNED_CALIBRATION = "619d6bf4d3200a6b55007a1abcc0658e76a14124ce5f3abad9f5f4b94d8979f7"
CONFIDENCE_DIR = Path(__file__).resolve().parent/'profiles/confidence_grand'
PINNED_CONFIDENCE_PROFILE = "3cdd77c04d5507ff6c20e150bb8503c7accf21486c3bbead590f63dbb99fd90e"
PINNED_CONFIDENCE_HEADER = "fdeee2144dc45bd7b56078c146a6444710c038b62610e9be156adbc321908b63"
PINNED_CANDIDATE_BUILDER = "8adccc4f229fcf2a247435f1ac054615c05427bddb01a3aa07828c0865ffc2d6"
PINNED_HEADER_BUILDER = "b0febd24607b8d7ac8a4d028f9e8a6bc73155813eae430c806dfb287d2421856"
PINNED_CANDIDATE_DOUBLE = "aeab17da971bc0136635af0d0a83134936ae23d39c5f3b3f0cdbdf0fbd7240ba"
PINNED_CANDIDATE_HOT = "8d6abcd41d89a32b54366106c54ebb62a9b52de21dc21402a7c179c55af88e56"
CONFIDENCE_ANCHORS = (21,24,33,36,39,45,48,51,60,63,69,72,75,81,84,96,108)

def replace(source, old, new):
    if source.count(old) != 1:
        raise ValueError('Source transform must match exactly once: ' + old[:80])
    return source.replace(old, new, 1)


def precision(source, coefficients=False):
    begin = source.index('struct Modes {')
    end = source.index('\nstruct String {', begin)
    modes = source[begin:end]
    modes = replace(modes,
        'std::vector<double> q,p,c,s,omega,hammer,b,forceQ,forceP,loss,damper,damp;',
        'std::vector<float> q,p;\n  std::vector<double> c,s,omega,hammer,b,forceQ,forceP,loss,damper,damp;')
    modes = modes.replace('double *__restrict yq=', 'float *__restrict yq=')
    modes = modes.replace('double *__restrict yp=', 'float *__restrict yp=')
    if coefficients:
        modes = modes.replace('std::vector<double>', 'std::vector<float>')
        modes = modes.replace('const double *__restrict', 'const float *__restrict')
        # Float oscillator kernels; nonlinear contact and all scalar sums stay double.
        modes = modes.replace('double v=yp[i]*yd[i],y=yq[i];', 'float v=yp[i]*yd[i],y=yq[i];')
        modes = modes.replace('double rotated=yc[i]*v-ys[i]*y;', 'float rotated=yc[i]*v-ys[i]*y;')
    # Explicit double products in energy and reductions, including state-only profile.
    for old, new in [
        ('omega[i]*omega[i]*(q[i]*q[i]+p[i]*p[i])', 'double(omega[i])*omega[i]*(double(q[i])*q[i]+double(p[i])*p[i])'),
        ('y+=hammer[i]*q[i]', 'y+=double(hammer[i])*q[i]'),
        ('v+=portOmega[i]*p[i]', 'v+=double(portOmega[i])*p[i]'),
        ('l+=radQL[i]*q[i]+radPL[i]*yp[i]', 'l+=double(radQL[i])*q[i]+double(radPL[i])*yp[i]'),
        ('r+=radQR[i]*q[i]+radPR[i]*yp[i]', 'r+=double(radQR[i])*q[i]+double(radPR[i])*yp[i]'),
        ('l+=radQL[i]*q[i]+radPL[i]*p[i]', 'l+=double(radQL[i])*q[i]+double(radPL[i])*p[i]'),
        ('r+=radQR[i]*q[i]+radPR[i]*p[i]', 'r+=double(radQR[i])*q[i]+double(radPR[i])*p[i]')]:
        modes = modes.replace(old, new)
    source = source[:begin] + modes + source[end:]
    source = replace(source, 'double q=0,p=0,w=0,c=0,s=0,damp=1,sigma=0,force=0;',
                     'float q=0,p=0;\n  double w=0,c=0,s=0,damp=1,sigma=0,force=0;')
    source = source.replace('std::array<double*,3> velocityState', 'std::array<float*,3> velocityState')
    source = source.replace('std::array<double*,3> velocity{}', 'std::array<float*,3> velocity{}')
    source = source.replace('double *__restrict p0=velocity[0]', 'float *__restrict p0=velocity[0]')
    if coefficients:
        source = replace(source, 'double coefficient=0;\n  std::array<float*,3> velocityState',
                         'float coefficient=0;\n  std::array<float*,3> velocityState')
        source = replace(source, 'std::array<double,3> omega{},inverseOmega{};',
                         'std::array<float,3> omega{},inverseOmega{};')
        source = replace(source, 'std::array<std::vector<double>,3> omega,inverse;',
                         'std::array<std::vector<float>,3> omega,inverse;')
        source = replace(source, 'std::vector<double> coefficient;', 'std::vector<float> coefficient;')
        for prefix in ('w0=omega[0]', 'r0=inverse[0]', 'c=coefficient.data()'):
            source = source.replace('const double *__restrict ' + prefix,
                                    'const float *__restrict ' + prefix)
        source = source.replace('double sum=w0[i]*p0[i]', 'double sum=double(w0[i])*p0[i]')
        source = source.replace('sum+=w1[i]*p1[i]', 'sum+=double(w1[i])*p1[i]')
        source = source.replace('sum+=w2[i]*p2[i]', 'sum+=double(w2[i])*p2[i]')
        source = source.replace('double sum=u.omega[0]*', 'double sum=double(u.omega[0])*')
        source = source.replace('sum+=u.omega[1]*', 'sum+=double(u.omega[1])*')
        source = source.replace('sum+=u.omega[2]*', 'sum+=double(u.omega[2])*')
        source = source.replace('opt.bridge*m.b[j]*H[ch]', 'opt.bridge*double(m.b[j])*H[ch]')
        source = source.replace('st.compliance+=st.m.b[j]*st.m.b[j]', 'st.compliance+=double(st.m.b[j])*st.m.b[j]')
        source = source.replace('k.contactCompliance+=st.m.hammer[j]*st.m.forceQ[j]',
                                'k.contactCompliance+=double(st.m.hammer[j])*st.m.forceQ[j]')
    source = source.replace('double l=m.baseQL[j]*m.q[j]+m.basePL[j]*m.p[j],r=m.baseQR[j]*m.q[j]+m.basePR[j]*m.p[j]',
                            'double l=double(m.baseQL[j])*m.q[j]+double(m.basePL[j])*m.p[j],r=double(m.baseQR[j])*m.q[j]+double(m.basePR[j])*m.p[j]')
    return source

def hot_precision(source):
    """True float hot kernels, double nonlinear/contact/junction solves.

    The conservative coefficient bias is deliberate added numerical loss; its
    ten-second drift must be reported rather than called a free accuracy gain.
    """
    source=precision(source,True)
    begin=source.index('struct Modes {');end=source.index('\nstruct String {',begin)
    modes=source[begin:end]
    modes=replace(modes,
        'q.push_back(0);p.push_back(0);c.push_back(std::cos(phase));s.push_back(std::sin(phase));omega.push_back(w);',
        '''q.push_back(0);p.push_back(0);
    float cf=static_cast<float>(std::cos(phase)),sf=static_cast<float>(std::sin(phase));
    // A rounded float rotation must not inject energy. Bias only the larger
    // component toward zero; the resulting loss is measured by the probe.
    while(double(cf)*cf+double(sf)*sf>1.0){
      if(std::abs(cf)>=std::abs(sf))cf=std::nextafter(cf,0.0f);
      else sf=std::nextafter(sf,0.0f);
    }
    c.push_back(cf);s.push_back(sf);omega.push_back(w);''')
    modes=modes.replace('double y=0;for(size_t i=0;i<size();++i)y+=double(hammer[i])*q[i]',
                        'float y=0;for(size_t i=0;i<size();++i)y+=hammer[i]*q[i]')
    modes=modes.replace('double v=0;for(size_t i=0;i<size();++i)v+=double(portOmega[i])*p[i]',
                        'float v=0;for(size_t i=0;i<size();++i)v+=portOmega[i]*p[i]')
    modes=replace(modes,'void force(double f){',
                  'void force(double f){\n    const float forceValue=static_cast<float>(f);')
    modes=modes.replace('fq[i]*f','fq[i]*forceValue').replace('fp[i]*f','fp[i]*forceValue')
    modes=replace(modes,'void portImpulse(double impulse){',
                  'void portImpulse(double impulse){\n    const float impulseValue=static_cast<float>(impulse);')
    modes=replace(modes,'std::array<double,2> portImpulseRadiation(double impulse){',
                  'std::array<double,2> portImpulseRadiation(double impulse){\n    const float impulseValue=static_cast<float>(impulse);')
    modes=modes.replace('bi[i]*impulse','bi[i]*impulseValue')
    modes=modes.replace('double l=0,r=0;', 'float l=0,r=0;')
    for field in ('radQL','radPL','radQR','radPR'):
        modes=modes.replace(f'double({field}[i])',f'{field}[i]')
    source=source[:begin]+modes+source[end:]
    begin=source.index('struct UnisonGroup {');end=source.index('\nclass Piano {',begin)
    group=source[begin:end]
    group=group.replace('double sum=double(w0[i])*p0[i]', 'float sum=w0[i]*p0[i]')
    group=group.replace('sum+=double(w1[i])*p1[i]', 'sum+=w1[i]*p1[i]')
    group=group.replace('sum+=double(w2[i])*p2[i]', 'sum+=w2[i]*p2[i]')
    group=group.replace('double impulse=c[i]*sum;', 'float impulse=c[i]*sum;')
    return source[:begin]+group+source[end:]


def guarded_pressure_reduction(source):
    """Opt-in observer-only SIMD; preserve the complete original fallback.

    Build support must accept -fopenmp-simd before defining the numeric macro.
    Per-mode impulse expressions stay unchanged; only pressure sums reassociate.
    """
    begin = source.index('  std::array<double,2> portImpulseRadiation(double impulse){')
    end = source.index('\n\n};', begin)
    original = source[begin:end]
    optimized = '''  std::array<double,2> portImpulseRadiation(double impulse){
    const float impulseValue=static_cast<float>(impulse);
    const size_t count=size();
    float *__restrict yp=p.data();
    const float *__restrict bi=portInverse.data(),*__restrict yq=q.data();
    const float *__restrict ql=radQL.data(),*__restrict pl=radPL.data();
    const float *__restrict qr=radQR.data(),*__restrict pr=radPR.data();
    float l=0,r=0;
    #pragma omp simd reduction(+:l,r) simdlen(4)
    for(size_t i=0;i<count;++i){
      yp[i]+=bi[i]*impulseValue;
      l+=ql[i]*yq[i]+pl[i]*yp[i];
      r+=qr[i]*yq[i]+pr[i]*yp[i];
    }
    return {l,r};
  }
  std::array<double,2> radiation()const{
    const size_t count=size();
    const float *__restrict yp=p.data(),*__restrict yq=q.data();
    const float *__restrict ql=radQL.data(),*__restrict pl=radPL.data();
    const float *__restrict qr=radQR.data(),*__restrict pr=radPR.data();
    float l=0,r=0;
    #pragma omp simd reduction(+:l,r) simdlen(4)
    for(size_t i=0;i<count;++i){
      l+=ql[i]*yq[i]+pl[i]*yp[i];
      r+=qr[i]*yq[i]+pr[i]*yp[i];
    }
    return {l,r};
  }'''
    guarded = '''#if defined(KEYRA_FULL_PRESSURE_SIMD) && KEYRA_FULL_PRESSURE_SIMD && (defined(__GNUC__) || defined(__clang__))
  // Only the pressure observer reassociates. The per-mode impulse is exact.
''' + optimized + '\n#else\n' + original + '\n#endif'
    result = source[:begin] + guarded + source[end:]
    return replace(result,
        '''  // Update and observe one string while its q/p state is hot. The reduction
  // order within the string is unchanged, and callers add cached strings in
  // the original order after the board's acceleration observation.''',
        '''  // Update and observe one string while its q/p state is hot. The fallback
  // keeps the original reduction order. The opt-in branch changes only pressure
  // sums; callers still add strings after the board in their original order.''')


def guarded_contact_solver(source):
    """Portable opt-in contact root solve; retain the legacy fallback verbatim."""
    source = replace(source, '#include "PreparedCalibration.h"',
        '''#include "PreparedCalibration.h"
#if defined(KEYRA_FULL_FAST_CONTACT) && KEYRA_FULL_FAST_CONTACT
#include "keyra/physics/ContactSolver.h"
#endif''')
    source = replace(source, '  uint64_t forceSolves=0;',
        '''  uint64_t forceSolves=0;
  // FAST-only solve counters; legacy fallback arithmetic is untouched.
  uint64_t contactEvaluations=0,contactNewtonIterations=0,contactBisectionIterations=0,contactFallbacks=0;
  unsigned maximumContactNewton=0,maximumContactBisections=0;''')
    source = replace(source,
        '    forceSolves=bridgeFaults=contactFaults=0;faultFlags=0;lastStems={};',
        '''    forceSolves=bridgeFaults=contactFaults=0;faultFlags=0;lastStems={};
    contactEvaluations=contactNewtonIterations=contactBisectionIterations=contactFallbacks=0;
    maximumContactNewton=maximumContactBisections=0;''')
    begin = source.index('  double contact(Key &k,double delta0,double freeDelta){')
    end = source.index('  void oscillators(){', begin)
    original = source[begin:end]
    optimized = '''  double contact(Key &k,double delta0,double freeDelta){
    const auto result=keyra::physics::solveFullContact({delta0,freeDelta,
      k.contactCompliance,dt,k.K,k.power,opt.hammerLoss});
    contactEvaluations+=result.evaluations;
    contactNewtonIterations+=result.newtonIterations;
    contactBisectionIterations+=result.bisectionIterations;
    if(result.usedBisection)++contactFallbacks;
    maximumContactNewton=std::max(maximumContactNewton,result.newtonIterations);
    maximumContactBisections=std::max(maximumContactBisections,result.bisectionIterations);
    if(!result.valid||!result.converged){
      // Never apply an unconverged/tentative force. Retire only this hammer;
      // oscillators() keeps the free string step and completes its damping.
      faultFlags|=FaultContact;++contactFaults;
      k.hammerActive=false;k.hammerX=0;k.hammerV=0;
      return 0;
    }
    if(result.evaluations){
      maxContactResidual=std::max(maxContactResidual,result.normalizedResidual);
      ++forceSolves;
    }
    return result.force;
  }
'''
    return source[:begin] + '#if defined(KEYRA_FULL_FAST_CONTACT) && KEYRA_FULL_FAST_CONTACT\n' + optimized + '#else\n' + original + '#endif\n' + source[end:]


def runtime_model(source):
    """Strip the CLI and add per-instance passive failure handling.

    Successful solve/contact arithmetic is retained verbatim. A failed contact
    retires only that hammer. A failed bridge solve skips that junction impulse
    for this sample and clears force observations; neither fallback adds energy.
    """
    source = hot_precision(source)
    source = source[:source.index('struct Event{')]
    # These renderer-only methods perform file I/O and are deliberately absent
    # from the runtime model, along with all events/WAV/self-test/main code.
    source = source[:source.index('  void dump(const std::string &path)const{')] + '};\n'
    for header in ('chrono', 'fstream', 'iomanip', 'iostream', 'random',
                   'sstream', 'stdexcept', 'string'):
        source = replace(source, '#include <' + header + '>\n', '')
    source = replace(source, '#include "calibration.h"', '#include "PreparedCalibration.h"')
    source = replace(source, 'Vec3 solve3(Mat3 a,Vec3 b){',
                     'inline bool solve3(Mat3 a,Vec3 b,Vec3& x) noexcept {')
    source = replace(source,
        'if(std::abs(a[pivot][k])<1e-20)throw std::runtime_error("singular bridge");',
        'if(!std::isfinite(a[pivot][k])||std::abs(a[pivot][k])<1e-20)return false;')
    source = replace(source,
        'Vec3 x{};for(int k=2;k>=0;--k){double y=b[k];for(int j=k+1;j<3;++j)y-=a[k][j]*x[j];x[k]=y/a[k][k];}return x;',
        'x={};for(int k=2;k>=0;--k){double y=b[k];for(int j=k+1;j<3;++j)y-=a[k][j]*x[j];x[k]=y/a[k][k];}\n  for(double value:x){if(!std::isfinite(value))return false;}\n  return true;')
    source = replace(source, '  uint64_t forceSolves=0;',
        '''  uint64_t forceSolves=0;
  // Sticky per-instance flags. No global/thread-local failure state.
  static constexpr uint32_t FaultBridge=1u,FaultContact=2u;
  uint32_t faultFlags=0;
  uint64_t bridgeFaults=0,contactFaults=0;''')
    source = replace(source,
        'if(residual(hi)<0)throw std::runtime_error("contact bracket failed");',
        '''if(!std::isfinite(hi)||!std::isfinite(residual(hi))||residual(hi)<0){
      faultFlags|=FaultContact;++contactFaults;
      k.hammerActive=false;k.hammerX=0;k.hammerV=0;
      return 0;
    }''')
    source = replace(source,
        '        for(int i:k.strings)strings[i].m.force(F);',
        '''        // A failed contact has retired this hammer; keep the free
        // string step and complete its damping without applying a new force.
        if(k.hammerActive){
        for(int i:k.strings)strings[i].m.force(F);''')
    source = replace(source,
        'if((k.hammerV<0&&k.hammerX<yf-.002)||k.age>.040)k.hammerActive=false;',
        'if((k.hammerV<0&&k.hammerX<yf-.002)||k.age>.040)k.hammerActive=false;\n        }')
    source = replace(source,
        '    Vec3 total=solve3(mat,sum),correction{};',
        '''    Vec3 total{},correction{};
    if(!solve3(mat,sum,total)){
      faultFlags|=FaultBridge;++bridgeFaults;
      for(auto& st:strings){st.velocity=0;st.force=0;
        if(cacheRadiation)st.cachedRadiation=st.m.radiation();}
      for(auto& z:board)z.force=0;
      return;
    }''')
    # Non-allocating reset: mode arrays and all cached unison pointers survive.
    # Damping is recomputed from the unchanged prepared coefficients/options.
    source = replace(source, '  void noteOn(int n,double vel){',
        '''  void resetState() noexcept {
    pedal=pedalTarget=0;maxForce=contactTime=maxContactResidual=maxEnergy=0;
    forceSolves=bridgeFaults=contactFaults=0;faultFlags=0;lastStems={};
    for(auto& st:strings){
      std::fill(st.m.q.begin(),st.m.q.end(),0.f);
      std::fill(st.m.p.begin(),st.m.p.end(),0.f);
      st.velocity=st.force=0;st.cachedRadiation={};
    }
    for(auto& z:board){z.q=z.p=0;z.force=0;}
    for(auto& k:keys){
      k.hammerX=k.hammerV=k.age=k.maxForce=k.contactSeconds=0;
      k.down=k.hammerActive=k.everStruck=false;k.damperPosition=1;
      k.cachedContact=k.cachedLoss=std::numeric_limits<double>::quiet_NaN();
    }
    setDamping();
  }
  void noteOn(int n,double vel){''')
    # Helper definitions are inline because the generated file is a private
    # header, even though the facade normally includes it in just one TU.
    for function in ('double lerp(', 'double loglerp(', 'double anchor(', 'double sinc('):
        source = replace(source, function, 'inline ' + function)
    # Preserve Clang's existing reduction permission while avoiding unknown
    # pragma diagnostics from other compilers, which already ignored it.
    source = source.replace('#pragma clang fp reassociate(on)',
                            '#if defined(__clang__)\n#pragma clang fp reassociate(on)\n#endif')
    source = guarded_pressure_reduction(source)
    source = guarded_contact_solver(source)
    if 'throw ' in source or 'ofstream' in source or 'struct Event' in source:
        raise ValueError('Renderer/exception code leaked into prepared model')
    return source + '\n} // namespace grand\n'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def transform_hash(source):
    tree = ast.parse(source)
    names = ('precision', 'hot_precision')
    functions = {node.name: ast.get_source_segment(source, node)
                 for node in tree.body if isinstance(node, ast.FunctionDef)}
    return sha('\n\n'.join(functions[name] for name in names).encode())


def frozen_function(source, name, expected):
    """Read a pinned function's syntax without importing/executing the fitter."""
    tree=ast.parse(source)
    nodes=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name==name]
    if len(nodes)!=1 or sha(ast.get_source_segment(source,nodes[0]).encode())!=expected:
        raise ValueError('Frozen fitter function changed: '+name)
    return nodes[0]


def confidence_calibration(profile):
    """Stdlib-only serialization of the exact frozen TRAIN numeric profile."""
    keys=profile.get('keys',[])
    if tuple(k.get('midi') for k in keys)!=CONFIDENCE_ANCHORS or any(
            type(k.get('midi')) is not int for k in keys):
        raise ValueError('Confidence profile requires the frozen seventeen anchors')
    if profile.get('radiation_enabled') is not True:
        raise ValueError('Frozen confidence radiation must remain enabled')
    def numeric(value):
        return type(value) in (int,float) and math.isfinite(value)
    for key in keys:
        for field in ('f1_hz','B','hardness','velocity_exponent','detune_scale'):
            if not numeric(key.get(field)) or key[field]<=0:
                raise ValueError('Invalid confidence scalar: '+field)
        for field in ('sigma_late','sigma_prompt','radiation_db','radiation_after_db'):
            values=key.get(field)
            if not isinstance(values,list) or len(values)!=64 or not all(numeric(v) for v in values):
                raise ValueError('Invalid confidence modal array: '+field)
            if field.startswith('sigma') and not all(v>0 for v in values):
                raise ValueError('Confidence losses must remain positive')
        if any(prompt<late for prompt,late in zip(key['sigma_prompt'],key['sigma_late'])):
            raise ValueError('Confidence prompt loss must not fall below late loss')
    def number(value):return format(float(value),'.17g')
    def array(values):return '{'+','.join(map(number,values))+'}'
    rows=[]
    for key in keys:
        values=[str(key['midi'])]+[number(key[f]) for f in ('f1_hz','B','hardness','velocity_exponent','detune_scale')]
        values += [array(key[f]) for f in ('sigma_late','sigma_prompt','radiation_db','radiation_after_db')]
        rows.append('{'+','.join(values)+'}')
    content='''// Generated by tools/fit_full_calibration.py; locked TRAIN only.
// Variable anchors require the candidate Cal integration in docs/FULL_CALIBRATION.md.
#pragma once
#include <array>
namespace piano_calibration {
constexpr int partials=64;
struct Anchor {int note;double f1,B,hardness,velocityExponent,detuneScale;
 std::array<double,partials> late,prompt,radiationDb,radiationAfterDb;};
constexpr bool radiationEnabled=true;
constexpr std::array<Anchor,'''+str(len(rows))+'''> anchors={{
'''+',\n'.join(rows)+'''\n}};
} // namespace piano_calibration
'''
    return content.encode()


def frozen_confidence_inputs():
    """Rebuild candidate DOUBLE input; historical out/ paths are never read."""
    canonical=(ROOT/'src/full_reference/grand.cpp').read_bytes()
    control=(ROOT/'src/full_reference/calibration.h').read_bytes()
    profile_bytes=(CONFIDENCE_DIR/'calibration.json').read_bytes()
    calibration=(CONFIDENCE_DIR/'PreparedCalibration.h').read_bytes()
    if sha(canonical)!=PINNED_SOURCE or sha(control)!=PINNED_CALIBRATION:
        raise ValueError('Immutable control inputs changed')
    if sha(profile_bytes)!=PINNED_CONFIDENCE_PROFILE or sha(calibration)!=PINNED_CONFIDENCE_HEADER:
        raise ValueError('Frozen confidence numeric profile/header changed')
    fitter=(ROOT/'tools/fit_full_calibration.py').read_text()
    builder=frozen_function(fitter,'build_candidate',PINNED_CANDIDATE_BUILDER)
    frozen_function(fitter,'generate_header',PINNED_HEADER_BUILDER)
    assignments=[node for node in builder.body if isinstance(node,ast.Assign) and
                 any(isinstance(target,ast.Name) and target.id=='replacements' for target in node.targets)]
    if len(assignments)!=1:
        raise ValueError('Frozen candidate replacement list missing')
    changes=ast.literal_eval(assignments[0].value)
    if len(changes)!=5 or not all(len(row)==3 and all(isinstance(v,str) for v in row) for row in changes):
        raise ValueError('Frozen candidate requires five string replacement sites')
    source=canonical.decode()
    records=[]
    for before,after,reason in changes:
        source=replace(source,before,after)
        records.append({'before':before,'after':after,'reason':reason})
    if sha(source.encode())!=PINNED_CANDIDATE_DOUBLE or sha(hot_precision(source).encode())!=PINNED_CANDIDATE_HOT:
        raise ValueError('Frozen confidence source or one-pass hot transform differs')
    profile=json.loads(profile_bytes)
    if confidence_calibration(profile)!=calibration:
        raise ValueError('Frozen confidence JSON/header do not reproduce exactly')
    metadata={'name':'FrozenConfidenceGrand','selector':1,
        'numeric_profile_sha256':sha(profile_bytes),
        'profile_provenance_sha256':sha((CONFIDENCE_DIR/'profile_provenance.json').read_bytes()),
        'canonical_source_sha256':sha(canonical),
        'adapted_double_source_sha256':sha(source.encode()),
        'frozen_hot_source_sha256':PINNED_CANDIDATE_HOT,
        'candidate_builder_function_sha256':PINNED_CANDIDATE_BUILDER,
        'header_builder_function_sha256':PINNED_HEADER_BUILDER,
        'source_adaptations':records,'anchor_midis':list(CONFIDENCE_ANCHORS),
        'expected_topology':{'strings':230,'string_modes':17849,'board_modes':475},
        'runtime_audio_or_json_loading':False,'new_fit_or_acquisition':False,'default_promoted':False}
    return source.encode(),calibration,metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile',choices=('OriginalControl','FrozenConfidenceGrand'),default='OriginalControl',
                        help='Explicit build profile; OriginalControl remains the default')
    parser.add_argument('--prepared-source', type=Path,
                        help='Explicit prepared double renderer source; not an automatic candidate selection')
    parser.add_argument('--calibration', type=Path,
                        help='Calibration matching the explicit prepared source')
    parser.add_argument('--output-dir', type=Path,
                        help='Defaults to the selected profile directory; candidate never overwrites the control')
    args = parser.parse_args()
    if bool(args.prepared_source) != bool(args.calibration):
        parser.error('--prepared-source and --calibration must be supplied together')
    if args.profile!='OriginalControl' and args.prepared_source:
        parser.error('An explicit source/calibration cannot be combined with the frozen confidence profile')
    control_dir=Path(__file__).resolve().parent
    output_dir=args.output_dir or (CONFIDENCE_DIR if args.profile=='FrozenConfidenceGrand' else control_dir)
    if args.profile=='FrozenConfidenceGrand' and output_dir.resolve()==control_dir:
        parser.error('The confidence profile cannot overwrite the OriginalControl directory')
    if args.profile=='OriginalControl' and output_dir.resolve()==CONFIDENCE_DIR:
        parser.error('The control cannot overwrite the frozen confidence profile directory')
    if args.profile=='FrozenConfidenceGrand':
        source_bytes,calibration_bytes,profile_metadata=frozen_confidence_inputs()
    else:
        source_path = args.prepared_source or ROOT/'src/full_reference/grand.cpp'
        calibration_path = args.calibration or ROOT/'src/full_reference/calibration.h'
        source_bytes, calibration_bytes = source_path.read_bytes(), calibration_path.read_bytes()
        profile_metadata={'name':'ExplicitSource' if args.prepared_source else 'OriginalControl',
            'selector':None if args.prepared_source else 0,
            'expected_topology':None if args.prepared_source else {'strings':230,'string_modes':17778,'board_modes':475},
            'runtime_audio_or_json_loading':False}
    tool_bytes = (ROOT/'tools/probe_full_precision.py').read_bytes()
    generator_bytes = Path(__file__).read_bytes()
    copied_transform_hash = transform_hash(generator_bytes.decode())
    tool_transform_hash = transform_hash(tool_bytes.decode())
    if copied_transform_hash != tool_transform_hash:
        raise ValueError('Copied precision/hot_precision differs from the precision probe; inspect before regeneration')
    if args.profile=='OriginalControl' and not args.prepared_source and (sha(source_bytes) != PINNED_SOURCE or
                                     sha(calibration_bytes) != PINNED_CALIBRATION):
        raise ValueError('Immutable control input hash differs; inspect before regeneration')
    provenance = {
        'source_sha256': sha(source_bytes),
        'calibration_sha256': sha(calibration_bytes),
        'precision': 'hot_f32_biased',
        'default_control': args.profile=='OriginalControl' and not bool(args.prepared_source),
        'profile':profile_metadata,
        'generator_sha256': sha(generator_bytes),
        'precision_transform_source': 'tools/probe_full_precision.py:precision,hot_precision',
        'precision_tool_sha256': sha(tool_bytes),
        'precision_transform_sha256': copied_transform_hash,
        'pressure_reduction': {
            'macro': 'KEYRA_FULL_PRESSURE_SIMD',
            'required_compiler_flag': '-fopenmp-simd',
            'optimized': 'local nonaliasing pointers; pressure-only float reduction, simdlen(4)',
            'fallback': 'original expressions and summation order; macro zero or undefined',
        },
        'fast_contact': {
            'macro': 'KEYRA_FULL_FAST_CONTACT',
            'solver_header': 'include/keyra/physics/ContactSolver.h',
            'solver_sha256': sha((ROOT/'include/keyra/physics/ContactSolver.h').read_bytes()),
            'fallback': 'legacy contact method verbatim; macro zero or undefined',
            'failure_policy': 'invalid or unconverged result retires only the hammer; tentative force never applied',
        },
    }
    prefix = '// Generated by generate_prepared_model.py; do not edit.\n#pragma once\n'
    prefix += '// Input renderer SHA-256: '+provenance['source_sha256']+'\n'
    prefix += '// Input calibration SHA-256: '+provenance['calibration_sha256']+'\n'
    result = (prefix + runtime_model(source_bytes.decode())).encode()
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir/'PreparedModel.h').write_bytes(result)
    (output_dir/'PreparedCalibration.h').write_bytes(calibration_bytes)
    provenance['generated_model_sha256'] = sha(result)
    (output_dir/'prepared_model_provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    print(json.dumps(provenance, indent=2))


if __name__ == '__main__':
    main()

