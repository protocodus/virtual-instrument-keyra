#!/usr/bin/env python3
"""Known-answer tests using cached TRAIN controls only; no new candidate access."""
from __future__ import annotations
import copy,hashlib,json,math
from datetime import datetime,timedelta
from pathlib import Path
import numpy as np
import probe_full_causal_radiation_metrics as metrics


def main():
    protocol,rows=metrics.locked();study=metrics.read(metrics.OUT/'reference-control.json')
    metrics.verify([study['protocol'],study['tool']]);results=[]
    for ident in ('C3v4','C4v12'):
        old=next(r for r in study['cases'] if r['id']==ident)
        raw,_=metrics.load_float(old['baseline_audio']['path']);x=raw.astype(np.float64)
        baseline=old['baseline'];onset=baseline['fixed_onset_frame'];gain=baseline['fixed_gain']
        same=metrics.observation_features(x,onset,gain,old['reference'],rows[ident])
        assert same==baseline,'Cached identity mismatch'
        doubled=metrics.observation_features(2*x,onset,gain,old['reference'],rows[ident])
        expected=20*math.log10(2)
        assert abs(20*math.log10(doubled['sustain_RMS']/baseline['sustain_RMS'])-expected)<1e-11
        assert doubled['fixed_gain']==gain and doubled['fixed_onset_frame']==onset
        assert doubled['detected_onset_diagnostic']['frame']==baseline['detected_onset_diagnostic']['frame']
        observed=[];floor=old['reference']['sustain_power']*1e-10
        for a,b in zip(baseline['early'],doubled['early']):
            assert abs((b['broad_signed_error_db']-a['broad_signed_error_db'])-expected)<1e-10
            for pa,pb,ea,eb in zip(a['band_power'],b['band_power'],a['band_signed_errors_db'],b['band_signed_errors_db']):
                if pa>floor and pb>floor:observed.append(abs((eb-ea)-expected))
        assert observed and max(observed)<1e-9
        for name in baseline['stereo']:
            assert abs(doubled['stereo'][name]['LR_db']-baseline['stereo'][name]['LR_db'])<1e-10
            a,b=baseline['stereo'][name]['mono_power'],doubled['stereo'][name]['mono_power']
            if a>floor:assert abs(metrics.power_db(b,a,floor)-expected)<1e-10
        delayed=np.zeros_like(x);delayed[48:]=x[:-48]
        shifted=metrics.observation_features(delayed,onset,gain,old['reference'],rows[ident])
        assert shifted['fixed_onset_frame']==onset and shifted['fixed_gain']==gain
        assert shifted['detected_onset_diagnostic']['frame']==baseline['detected_onset_diagnostic']['frame']+48
        assert shifted['early'][0]['broad_power']!=baseline['early'][0]['broad_power'],'Shift was hidden by retiming'
        results.append({'id':ident,'cached_identity_exact':True,'amplitude2_fixed_gain_RMS_and_power_shift_db':expected,
            'maximum_nonfloored_band_error_shift_defect_db':max(observed),'stereo_LR_invariant_under_common_gain':True,
            'mono_energy_gain_db_correct':True,'known48frame_delay_detected_but_not_retimed':True})
    # Synthetic metadata tests use only cached-control audio descriptors.
    # They exercise provenance guards without opening any new candidate file.
    fixture=metrics.OUT/'metric-guard-fixtures';fixture.mkdir(exist_ok=True)
    source_records=[row for row in protocol['inputs'] if row['sha256'] in {
        protocol['producer_contract'][k] for k in ('calibration_sha256','prepared_model_sha256','frozen_facade_sha256')}]
    math_path=fixture/'synthetic-math.json';metrics.write(math_path,{'passed':True,'scope':'Synthetic schema fixture, not physical math validation.'})
    binary=metrics.record(metrics.ROOT/'out/full-calibration/v3/control-f32/render')
    fixture_time=datetime.fromisoformat(protocol['frozen_at_utc'])+timedelta(seconds=1)
    freeze_path=fixture/'synthetic-freeze.json';metrics.write(freeze_path,{'frozen_at_utc':fixture_time.isoformat(),
        'protocol':metrics.record(metrics.OUT/'protocol.json'),'binary':binary,'source_inputs':source_records,
        'readout_method':'Synthetic schema fixture only','math_validation':metrics.record(math_path)})
    cases=[{'id':c['id'],'midi':c['midi'],'velocity':c['midi_velocity'],'frames':182400,
        'baseline':c['cached_control_audio'],'candidate':c['cached_control_audio'],
        'mechanical_state_bit_parity':True,'force_bit_parity':True,'new_faults':0} for c in protocol['cases']]
    producer={'protocol':metrics.record(metrics.OUT/'protocol.json'),'source_inputs':source_records,
        'configuration':{'sample_rate':48000,'frames':182400,'note_on_frame':4800,'pedal_initial':0,
            'humanization':0,'mechanical_level':0,'repetition_controller':False,'gain_db':0,'stereo_width':1},
        'candidate_freeze':metrics.record(freeze_path),'binary':binary,'render_started_at_utc':(fixture_time+timedelta(seconds=1)).isoformat(),'cases':cases}
    capture={'cases':[{'id':c['id'],'baseline':c['baseline'],'candidate':c['candidate'],
        'mechanical_state_force_bit_parity':True,'new_faults':0} for c in cases]}
    metrics.producer_evidence(producer,protocol,capture)
    failures=[]
    def expect_bad(name,mutate):
        p,c=copy.deepcopy(producer),copy.deepcopy(capture);mutate(p,c)
        try:metrics.producer_evidence(p,protocol,c)
        except ValueError:failures.append(name)
        else:raise AssertionError('Invalid producer/capture accepted:'+name)
    expect_bad('missing_frozen_source_identity',lambda p,c:p['source_inputs'].pop(0))
    expect_bad('changed_humanization',lambda p,c:p['configuration'].__setitem__('humanization',.1))
    expect_bad('render_before_frozen_protocol',lambda p,c:p.__setitem__('render_started_at_utc','2026-01-01T00:00:00+00:00'))
    expect_bad('binary_mismatch',lambda p,c:p.__setitem__('binary',metrics.record(Path(__file__))))
    expect_bad('wrong_case_midi',lambda p,c:p['cases'][0].__setitem__('midi',1))
    expect_bad('capture_only_parity_claim',lambda p,c:c['cases'][0].__setitem__('mechanical_state_force_bit_parity',False))
    expect_bad('capture_only_fault_claim',lambda p,c:c['cases'][0].__setitem__('new_faults',1))
    expect_bad('capture_audio_binding_changed',lambda p,c:c['cases'][0].__setitem__('candidate',c['cases'][1]['candidate']))
    changing=fixture/'changing-metadata.json';changing.write_text('{}\n');_,identity=metrics.read_snapshot(changing)
    changing.write_text('{"changed":true}\n')
    try:metrics.verify([identity])
    except ValueError:failures.append('post_read_metadata_mutation')
    else:raise AssertionError('Post-read metadata change accepted')
    report={'passed':True,'scope':'Known-answer cached TRAIN controls and synthetic metadata only; no new candidate access.',
        'protocol':metrics.record(metrics.OUT/'protocol.json'),'reference_control':metrics.record(metrics.OUT/'reference-control.json'),
        'metric_tool':metrics.record(Path(metrics.__file__)),'test_tool':metrics.record(Path(__file__)),
        'cases':results,'producer_capture_guards_rejected':failures,
        'synthetic_guard_fixture_scope':'Metadata only, not a physical validation receipt.',
        'new_fit_acquisition_or_candidate_access':False}
    metrics.write(metrics.ROOT/'Validation/full-causal-radiation-metric-checks.json',report)
    print(json.dumps({'passed':True,'cached_TRAIN_controls':2,'identity_gain_stereo_delay_checks':True,
        'producer_capture_guards':len(failures),'candidate_access':False},indent=2))


if __name__=='__main__':main()
