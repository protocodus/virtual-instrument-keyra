#!/usr/bin/env python3
"""Add a derived parity alias to producer metadata; never open pressure audio."""
import argparse,hashlib,json
from pathlib import Path


def snapshot(path):
    path=Path(path).resolve();data=path.read_bytes()
    return json.loads(data),{'path':str(path),'sha256':hashlib.sha256(data).hexdigest()}
def verify(row):
    if hashlib.sha256(Path(row['path']).read_bytes()).hexdigest()!=row['sha256']:
        raise ValueError('Metadata changed:'+row['path'])
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('Adapter output already exists')
    capture,original=snapshot(args.capture)
    producer,proof=snapshot(capture['producer_receipt']['path'])
    if proof['sha256']!=capture['producer_receipt']['sha256']:raise ValueError('Producer binding differs')
    rows={r['id']:r for r in producer['cases']};verified=[]
    for case in capture['cases']:
        bound=rows[case['id']]
        if case!=bound:raise ValueError('Original capture row is not the bound producer row')
        for key in ('mechanical_state_bit_parity','force_bit_parity'):
            if type(bound[key]) is not bool:raise ValueError('Parity proof is not boolean')
        case['mechanical_state_force_bit_parity']=bound['mechanical_state_bit_parity'] and bound['force_bit_parity']
        for key in ('parity_proof','diagnostics'):
            item=bound.get(key)
            if isinstance(item,dict) and {'path','sha256'}<=item.keys():
                if Path(item['path']).suffix!='.json':raise ValueError('Expected metadata JSON proof, not pressure audio')
                verify(item);verified.append(item)
    capture['metadata_schema_adapter']={'tool':{'path':str(Path(__file__).resolve()),'sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        'original_capture':original,'producer_receipt':proof,'verified_metadata_proofs':verified,
        'change':'Add logical AND alias only; preserve original separate proof fields and all signal descriptors.',
        'pressure_audio_opened':False,'numeric_gates_or_audio_changed':False}
    verify(original);verify(proof)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(capture,indent=2,allow_nan=False)+'\n')
    print('Metadata adapter complete; pressure audio untouched.')


if __name__=='__main__':main()
