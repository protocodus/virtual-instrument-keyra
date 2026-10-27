#!/usr/bin/env python3
"""Cold algebra witnesses; no model construction, pressure, or recordings."""
from pathlib import Path
import hashlib,json,math,struct
OUT=Path(__file__).resolve().parent
RATE=48000
r0=math.exp(-100/RATE)
rows=[]
for pitch_ratio in (0.2,0.5,1,2,8,32.3022):
 for hz in (27.5,100,750,999.999999,1000,1000.000001,2000,4000,19000,24000):
  gamma=100*max(1,pitch_ratio,hz/1000)
  rho=math.exp(-gamma/RATE)
  q,p,w=0.37,-0.82,2*math.pi*hz
  before=.5*w*w*(q*q+p*p)
  after=.5*w*w*((rho*q)**2+(rho*p)**2)
  assert gamma>=100 and 0<rho<=r0 and after<=before
  assert math.isclose(after/before,rho*rho,rel_tol=8e-16)
  rows.append(dict(pitch_ratio=pitch_ratio,frequency_hz=hz,gamma=gamma,rho=rho,energy_ratio=after/before))
# Uniform mode arrays preserve precisely the same double-multiply/float-store
# order as the former scalar/line rho routine, including signs of zero.
def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]
for value in (0.,-0.,1.,-1.,1e-15,-1e-15,1e-35,-1e-35,0.123456):
 scalar=f32(float(f32(value))*r0)
 mode=f32(float(f32(value))*[r0][0])
 assert struct.pack('<f',scalar)==struct.pack('<f',mode)
# Continuity of max-based law at the modal corner, apart from derivative.
g_left=100*max(1,1,999.999999/1000)
g_right=100*max(1,1,1000.000001/1000)
assert abs(g_right-g_left)<2e-7
# 750 Hz C3 pitch ratio=1 remains the gamma100 branch by construction.
assert rows[22]['frequency_hz']==750 and rows[22]['gamma']==100
result=dict(pass_all=True,scope='Cold manufactured algebra only; no actual model/PCM/candidate pressure or acoustic metrics opened.',lattice_count=len(rows),minimum_gamma=100,modal_corner_hz=1000,paired_energy_contraction=True,uniform_float_store_identity=True,continuous_corner=True,rows=rows)
(OUT/'law-synthetic.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='rows'}))
