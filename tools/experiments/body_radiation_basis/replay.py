#!/usr/bin/env python3
"""Portable board-only replay of external historical captures; never a piano render."""
from pathlib import Path
import argparse,gzip,hashlib,json,struct,subprocess,time
PACKAGE=Path(__file__).resolve().parent
ROOT=PACKAGE.parents[2]
ORIGINAL='/workspace/virtual-instrument-keyra/'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name):return json.loads(gzip.decompress((PACKAGE/'evidence/study'/name).read_bytes()))
def require(x,message):
    if not x:raise ValueError(message)
def write_json(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def coefficients(destination):
    c=json.loads(gzip.decompress((PACKAGE/'coefficients.json.gz').read_bytes()))
    require(c['shape']==[475,11] and len(c['values'])==475*11,'Coefficient shape changed')
    blob=struct.pack('<'+'d'*len(c['values']),*c['values'])
    require(hashlib.sha256(blob).hexdigest()==c['binary_sha256'],'Lossless coefficient encoding changed')
    destination.write_bytes(blob);return c['binary_sha256']
def export_static(args):
    args.output.mkdir(parents=True,exist_ok=False)
    source=PACKAGE/'export_coefficients.cpp';include=ROOT/'tools/experiments/causal_radiation_pilot/producer/original_core/src/full_instrument'
    index=json.loads((PACKAGE/'index.json').read_text())
    for name,expected in index['static_export_source_bindings'].items():require(digest(ROOT/name)==expected,'Static source changed: '+name)
    exe=args.output/'export_coefficients';command=['g++','-std=c++17','-O3','-fno-builtin','-ffp-contract=off','-I',str(include),str(source),'-o',str(exe)]
    subprocess.run(command,check=True);subprocess.run([str(exe),str(args.output)],check=True)
    expected=json.loads(gzip.decompress((PACKAGE/'coefficients.json.gz').read_bytes()))['binary_sha256'];actual=digest(args.output/'board-coefficients.f64le')
    receipt={'scope':'Static originalmodel constructor only; no note, frame, recording or simulation. No sound/performance claim.','command':command,'expected_board_sha256':expected,'actual_board_sha256':actual,'byte_identical_on_this_platform':actual==expected}
    write_json(args.output/'receipt.json',receipt);print(json.dumps(receipt,indent=2));require(actual==expected,'Platform static coefficients differ; retained result. Do not replace frozen coefficients silently.')
def replay(args):
    subprocess.run(['python3',str(PACKAGE/'check.py')],check=True)
    p=load('protocol.json.gz');binding=load('input-bindings.json.gz');cases=binding['cases']
    if args.ids:
        wanted=set(args.ids);require(wanted<={c['id'] for c in cases},'Unknown case id');cases=[c for c in cases if c['id'] in wanted]
    require(not args.output.exists(),'Output directory already exists; retain prior outputs and choose a new directory')
    def mapped(old):
        require(old.startswith(ORIGINAL),'Unknown archived capture prefix');return args.capture_root/old[len(ORIGINAL):]
    for c in cases:
        require(digest(mapped(c['trace']))==c['expected_trace_sha256'],'Trace hash mismatch: '+c['id'])
        require(digest(mapped(c['force_proof']))==c['expected_proof_sha256'],'Forceproof hash mismatch: '+c['id'])
    args.output.mkdir(parents=True);coeff=args.output/'board-coefficients.f64le';coeff_sha=coefficients(coeff);exe=args.output/'replay'
    command=['g++','-std=c++17','-O3','-fno-builtin','-ffp-contract=off',str(PACKAGE/'producer/replay.cpp'),'-o',str(exe)];subprocess.run(command,check=True)
    results=[];started=time.monotonic()
    for c in cases:
        d=args.output/c['id'];d.mkdir();raw=d/'basis.f64le';stats=d/'stats.json';cmd=[str(exe),str(coeff),str(mapped(c['trace'])),str(raw),str(stats),'canonical',str(mapped(c['force_proof'])),str(c['midi'])]
        subprocess.run(cmd,check=True);s=json.loads(stats.read_text())
        gates={'frames':s['frames']==182400,'raw_board_bitexact':s['direct_nonidentical_samples']==0 and s['direct_max_error']==0,'force_proof':s['force_proof_mismatches']==0,'partition':s['partition_error_over_bound']<=1,'weighted_recombination':s['positive_weight_error_over_bound']<=1,'hp24_partition':s['hp24_partition_max_error']<=s['hp24_partition_bound'],'finite':s['nonfinite']==0,'basis':s['basis_min']>=0 and s['basis_max']<=1 and s['basis_partition_max_error']==0 and min(s['basis_support_modes'])>0}
        if c['id'] in p['stages']['witnesses']:
            alt=d/'alternate.f64le';ast=d/'alternate-stats.json';subprocess.run([str(exe),str(coeff),str(mapped(c['trace'])),str(alt),str(ast),'alternate',str(mapped(c['force_proof'])),str(c['midi'])],check=True)
            gates['chunks']=digest(alt)==digest(raw) and ast.read_bytes()==stats.read_bytes();alt.unlink()
        gates['inputs_unchanged']=digest(mapped(c['trace']))==c['expected_trace_sha256'] and digest(mapped(c['force_proof']))==c['expected_proof_sha256']
        record={'id':c['id'],'output_sha256':digest(raw),'gates':gates,'pass':all(gates.values())};write_json(d/'receipt.json',record);results.append(record);print(json.dumps(record),flush=True)
        if not record['pass']:break
    result={'scope':'Portable external-capture board-only replay. Same frozen C++ producer; no reference fit, sound change or fullpiano runtime benchmark. This launcher checks recurrence/basis/chunks; stored original12coherentGram checks verified by source-onlychecker, not recomputed here.','cases':results,'pass':len(results)==len(cases) and all(c['pass'] for c in results),'coefficients_sha256':coeff_sha,'compiler_command':command,'wall_seconds':time.monotonic()-started,'retained_raw_bytes':sum((args.output/c['id']/'basis.f64le').stat().st_size for c in results)}
    write_json(args.output/'result.json',result);require(result['pass'],'Replay failed; outputs retained. No automatic retry.')
def main():
    parser=argparse.ArgumentParser(description=__doc__);commands=parser.add_subparsers(dest='command',required=True)
    ex=commands.add_parser('export-static',help='Rebuild original static475board coefficients; no physical frames');ex.add_argument('--output',type=Path,required=True);ex.set_defaults(function=export_static)
    rep=commands.add_parser('replay',help='Replay frozen external traces without string/contact simulation');rep.add_argument('--capture-root',type=Path,required=True,help='Archive root containing out/full-causal-radiation and out/full-radiation-crossover');rep.add_argument('--output',type=Path,required=True);rep.add_argument('--ids',nargs='+',help='Optional exact case ids, e.g. C3v4 C3v12');rep.set_defaults(function=replay)
    args=parser.parse_args();args.function(args)
if __name__=='__main__':main()
