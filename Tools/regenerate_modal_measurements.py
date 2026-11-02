"""Stored-number regeneration, explicitly NOT source recalibration."""
import hashlib
import re
import update_modal_measurements as shared

def validate(archive, model):
    shared.require(archive['model'] == model, 'measurement snapshot model mismatch')
    p = archive.get('provenance', {})
    fields = ['header_sha256', 'corpus_sha256', 'split_sha256']
    conditional = p.get('derivation') == 'conditional-partial-update-v1'
    if conditional:
        fields += ['parent_archive_sha256', 'parent_header_sha256', 'update_receipt_sha256',
                   'execution_analysis_sha256', 'execution_fitter_sha256']
        shared.require('metadata_sha256' not in p, 'historical metadata cannot describe updated header')
    else:
        shared.require(not any(k in p for k in ['parent_archive_sha256', 'parent_header_sha256', 'update_receipt_sha256']),
                       'incomplete/unknown snapshot derivation')
        fields += ['metadata_sha256', 'historical_analysis_sha256', 'historical_fitter_sha256',
                   'bootstrap_analysis_sha256', 'fitter_sha256', 'importer_sha256']
    for key in fields:
        shared.require(isinstance(p.get(key), str) and re.fullmatch('[0-9a-f]{64}', p[key]) is not None,
                       'missing/invalid snapshot provenance: ' + key)
    shared.require(isinstance(p.get('recording_attribution'), dict) and p['recording_attribution'], 'missing recording attribution')
    anchors = archive['measurements']['anchors']
    clocks = archive['clocks']
    shared.require(len(clocks) == len(anchors) and len({q['note'] for q in clocks}) == len(clocks), 'snapshot clock coverage differs')
    by_note = {q['note']: q['layer_shift_ms'] for q in clocks}
    shared.require(all(a['note'] in by_note and len(by_note[a['note']]) == len(a['velocities']) for a in anchors), 'snapshot clock shape differs')

def regenerate(path, model, formatter, model_config):
    archive_sha = shared.digest(path)
    archive = shared.read_archive(path)
    validate(archive, model)
    content = formatter(model_config, **archive['measurements'])
    actual = hashlib.sha256(content.encode()).hexdigest()
    shared.require(actual == archive['provenance']['header_sha256'], 'stored-number header SHA differs from snapshot provenance')
    shared.require(shared.digest(path) == archive_sha, 'measurement snapshot changed during regeneration')
    return content, {'operation': 'stored-number regeneration, not source recalibration',
                     'model': model, 'archive_sha256': archive_sha, 'header_sha256': actual,
                     'source_audio_reads': 0, 'raw_cache_reads': 0,
                     'snapshot_provenance': archive['provenance']}
