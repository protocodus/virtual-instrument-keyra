#!/usr/bin/env python3
"""Audit and clarify the frozen TRAIN attack diagnostic without new synthesis."""
from __future__ import annotations
from datetime import datetime,timezone
from pathlib import Path
import json
import hashlib
import sys
import math
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import probe_full_attack_timing as probe
import probe_full_inverse_loss as loss


def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def record(p):return {'path':str(Path(p).resolve()),'sha256':sha(p)}
def main():
    frozen=probe.locked();out=probe.OUT
    report=read(out/'report.json');batch=read(out/'renders.json')
    probe.verify([report['freeze'],report['batch'],batch['build']])
    for row in batch['renders']:probe.verify(row['outputs'])
    if sha(out/'report.json')!=sha(ROOT/'Validation/full-attack-timing.json'):
        raise ValueError('Diagnostic report copies differ')
    if not report['existing_analytic_vs_v4_physical_key_fields_exact'] or not all(r['all_fields_exact'] for r in report['existing_analytic_vs_v4_mechanics']):
        raise ValueError('Existing controlled observation pair changed physics')
    scores={name:read(path/'score.json') for name,path in probe.SCORES.items()}
    attacks={name:loss.attack_by_case(s) for name,s in scores.items()}
    summaries=[]
    for ident in ('A0v4','A0v12'):
        values={}
        for label,row in [('real',report['references'][ident]),*report['cached'][ident].items()]:
            e=row['envelope']['smoothing_ms']['5'];cross=e['crossings_seconds']
            values[label]={'rise_ms':1000*e['rise10_90_seconds'],
                't10_ms':1000*cross['0.1'],'t50_ms':1000*cross['0.5'],'t90_ms':1000*cross['0.9'],
                'peak_ms':1000*e['peak_seconds'],'first25ms_peak_fraction':e['first25ms_peak_fraction'],
                'first25ms_peak_to90pct_amplitude_db':20*math.log10(.9/e['first25ms_peak_fraction']),
                'threshold_crossings_ms':{k:1000*v for k,v in cross.items()},
                'smoothing_1_2_5_10ms_rise_ms':[1000*row['envelope']['smoothing_ms'][str(ms)]['rise10_90_seconds'] for ms in (1,2,5,10)],
                'centroids_250_19000_hz':[w['centroid_250_19000_hz'] for w in row['texture']],
                'official_attack_5_100ms_prominent_band_mae_db':None if label=='real' else attacks[label][ident]}
        short=[]
        for row in report['new']:
            if row['id']!=ident:continue
            e=row['envelope']['smoothing_ms']['5'];onset=(row['envelope']['onset_frame']-4800)/48000
            short.append({'variant':row['variant'],'rise_ms':1000*e['rise10_90_seconds'],
                'detected_onset_ms_after_true_event':1000*onset,
                't50_ms_after_true_event':1000*(onset+e['crossings_seconds']['0.5']),
                't90_ms_after_true_event':1000*(onset+e['crossings_seconds']['0.9']),
                'peak_ms_after_true_event':1000*(onset+e['peak_seconds']),
                'peak_force_N':row['metrics']['max_force_N'],
                'contact_ms_above_1e_minus4_N':1000*row['metrics']['contact_seconds_above_1e_minus4_N']})
        baseline=next(r for r in report['new'] if r['id']==ident and r['variant']=='v4')
        cross=baseline['stem_coherent_power'][1]
        ratio=cross['sum_coherent_power']/cross['incoherent_stem_power']
        summaries.append({'id':ident,'cached':values,'short_variants_true_event_axis':short,
            'v4_5_20ms_coherent_to_incoherent_stem_power_db':10*math.log10(ratio)})
    checks=[]
    for row in report['mechanical_checks']:
        if row['variant'] not in ('v4','hardness-prior'):
            if not row['force_hammer_trace_exact_to_v4'] or not row['mechanical_checkpoints_exact_to_v4']:
                raise ValueError('Observation ablation changed force/state checksum')
        checks.append({'id':row['id'],'variant':row['variant'],
            'complete_force_hammer_trace_exact_to_v4':row['force_hammer_trace_exact_to_v4'],
            'sampled_mechanical_checksums_exact_to_v4':row['mechanical_checkpoints_exact_to_v4']})
    result={'schema_version':1,'reviewed_at_utc':datetime.now(timezone.utc).isoformat(),
        'frozen_protocol':record(out/'freeze.json'),'report':record(out/'report.json'),
        'review_tool':record(__file__),'summary':summaries,'mechanical_checks':checks,
        'verification':{'frozen_input_count':len(frozen['inputs']),'completed_short_renders':len(batch['renders']),
            'total_new_audio_seconds':sum(r['metrics']['frames']/48000 for r in batch['renders']),
            'cached_v4_and_analytic_prefix_parity_passed':True,'existing_controlled_pair_physics_exact':True,
            'plots':[record(ROOT/'Validation'/('full-attack-timing'+ext)) for ext in ('.svg','.png')]},
        'interpretation':['The large5ms-envelope t90 change is output-shape/relative-peak weighting, not a56ms hammer-contact delay.',
            'Restoring hardness has negligible t90 effect. Phase-only or sub250Hz removal is not a consistent remedy across both layers.',
            'At fixed early-RMS gain,V4 initial0–5ms pressure remains excessive relative to the edited recording despite better later spectral agreement.',
            'The controlled observation pair preserves force/contact/mechanics. The broader original-to-V4 comparison also changes other physical calibration fields.',
            'Keep official onset/rise measurements unchanged; retain threshold/smoothing sensitivity only as diagnosis,not a replacement score.'],
        'clarifications':{
            'state_checksum':'The driver uses the FNV-1a recurrence with a nonstandard offset basis1469598103934665603. Its fnv1a64 field is a sampled state checksum,not standard FNV-1a,not a collision-proof full-state comparison. It covers modalq/p and hammerx/v/active at5frames; complete force/hammer traces and source-only observation changes provide separate evidence.',
            'band_mask':'The diagnostic texture.reference_prominent_mask uses each windowband power divided by sum of that windowbands. It differs from official fitter masks normalized by early RMS. No masked aggregate from that diagnostic mask is used as officialattackerror; above summaries reuse frozen score masks.',
            'short_onset_roi':'Short ablations use the detector maximum over available0.35s instead of up to1.5s. Baseline and analytic detected onsets match the full-render onsets exactly. Every ablation has additional timings relative to the known100ms event; no real-recording MIDI event is known.',
            'contact_geometry':'Immediate modeled force reflects the frozen original near-string launch shortcut. It is not a measured finger-to-hammer latency.',
            'reference_conditions':'Unknown acoustic/action onset,editing,room,pedal and physical hammer speed constrain interpretation of first0–5ms ratios. No real waveform is supplied to synthesis.'},
        'historical_audio_or_feature_access':False,'numeric_fit':False,'default_promoted':False,
        'review_scope':'Completing-agent numerical/provenance review with a separate read-only agent audit; not an acoustic listening verdict.'}
    (ROOT/'Validation/full-attack-timing-review.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print('Frozen TRAIN attack diagnostic verified; no fitting or synthesis run.')
    for row in summaries:
        print(row['id'],'official5–100ms texture MAE',{k:round(v['official_attack_5_100ms_prominent_band_mae_db'],3) for k,v in row['cached'].items() if k!='real'},
              'stem cancellation dB',round(row['v4_5_20ms_coherent_to_incoherent_stem_power_db'],3))


if __name__=='__main__':main()
