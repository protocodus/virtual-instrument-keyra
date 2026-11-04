#!/usr/bin/env python3
"""Conditionally update declared existing partials in accepted measurements.

This first schema supports same-order, same-carrier residue/rise updates only.
It does not recover historical raw fits, add partials, change stiffness or fit a
global law. Immutable numeric JSON owns accepted exported values; trusted raw
fit pickles are external, hash-checked inputs, never part of that archive.
All source roles and hashes are checked before pickle/audio access. Original
anchor_data runs with the accepted layer clock before its phase smoothing;
only declared rise/lanes are replaced. The original formatter owns the header.
Local residual noise can be remeasured against the accepted global basis, with
unsupported versus observed-silent fields distinguished by original gates.
No-target output must reproduce the accepted header byte for byte.
"""
from __future__ import annotations
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import pickle
import sys
import tempfile
import measurement_source_provenance as source_provenance

SCHEMA = 'keyra-accepted-measurements-v1'
MANIFEST = 'keyra-existing-partial-update-v2'

class InvalidInput(ValueError):
    pass

def require(ok, message):
    if not ok:
        raise InvalidInput(message)

def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def aliases(left, right):
    """Compare destinations through symlinks and existing hard links."""
    left, right = Path(left), Path(right)
    if left.resolve() == right.resolve():
        return True
    try:
        return left.samefile(right)
    except FileNotFoundError:
        return False

def protect_outputs(outputs, inputs):
    """Check the complete output set before the first write, including --check."""
    outputs = [Path(p) for p in outputs if p is not None]
    inputs = [Path(p) for p in inputs]
    for i, path in enumerate(outputs):
        require(not any(aliases(path, p) for p in inputs),
                'output aliases input: ' + str(path))
        require(not any(aliases(path, p) for p in outputs[:i]),
                'outputs alias each other: ' + str(path))

def verify_pins(pins):
    require(isinstance(pins, dict) and pins, 'missing input pins')
    for path, expected in pins.items():
        require(digest(path) == expected, 'input changed: ' + str(path))

def pinned_identity(path, pins):
    """Resolve an identity only if every recorded alias agrees on its hash."""
    expected = [value for name, value in pins.items() if aliases(path, name)]
    require(expected and len(set(expected)) == 1, 'missing/conflicting input pin: ' + str(path))
    return expected[0]

def json_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=False, allow_nan=False) + '\n').encode()

def encode(value):
    if type(value).__module__.startswith('numpy'):
        return encode(value.tolist())
    if isinstance(value, complex):
        require(math.isfinite(value.real) and math.isfinite(value.imag), 'nonfinite complex')
        return {'$complex': [value.real, value.imag]}
    if isinstance(value, dict):
        require('$complex' not in value and all(isinstance(k, str) for k in value), 'reserved/invalid key')
        return {k: encode(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(v) for v in value]
    if isinstance(value, float):
        require(math.isfinite(value), 'nonfinite numeric archive')
    require(value is None or isinstance(value, (str, bool, int, float)), 'unsupported numeric archive type')
    return value

def decode(value):
    if isinstance(value, dict):
        if '$complex' in value:
            require(set(value) == {'$complex'} and isinstance(value['$complex'], list)
                    and len(value['$complex']) == 2, 'invalid complex encoding')
            a, b = value['$complex']
            require(type(a) in (int, float) and type(b) in (int, float), 'invalid complex numbers')
            return complex(a, b)
        return {k: decode(v) for k, v in value.items()}
    if isinstance(value, list):
        return [decode(v) for v in value]
    return value

def reject_constant(value):
    raise InvalidInput('nonfinite JSON constant: ' + value)

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'), parse_constant=reject_constant)

def read_archive(path):
    raw = Path(path).read_bytes()
    if raw[:2] == b'\x1f\x8b':
        raw = gzip.decompress(raw)
    require(len(raw) <= 64 * 1024 * 1024, 'numeric archive too large')
    value = json.loads(raw, parse_constant=reject_constant)
    require(raw == json_bytes(value), 'archive is not canonical JSON')
    require(value.get('schema') == SCHEMA, 'unsupported archive schema')
    decoded = decode(value)
    # This also checks finite numbers inside complex tags and rejects unknown types.
    encode(decoded)
    return decoded

def pinned(ref, base, pins):
    require(isinstance(ref, dict) and set(ref) == {'path', 'sha256'}, 'invalid input reference')
    path = Path(ref['path'])
    if not path.is_absolute():
        path = base / path
    path = path.absolute()
    require(digest(path) == ref['sha256'], 'input hash mismatch: ' + str(path))
    pins[str(path)] = ref['sha256']
    return path

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value

def operators(paths):
    require(paths['analysis'].parent == paths['fitter'].parent,
            'original fitter and analysis must be sibling files')
    sys.path.insert(0, str(paths['analysis'].parent))
    pa = module('piano_analysis', paths['analysis'])
    fit = module('fit_realtime_modal', paths['fitter'])
    require(Path(fit.ANALYSIS).resolve() == paths['analysis'].resolve(), 'wrong analysis imported')
    return fit, pa

def preflight(manifest_path):
    manifest_path = Path(manifest_path).absolute()
    m = read_json(manifest_path)
    require(m.get('schema') == MANIFEST, 'unsupported manifest schema')
    base, pins = manifest_path.parent, {str(manifest_path): digest(manifest_path), str(Path(__file__).absolute()): digest(__file__)}
    pins[str(Path(source_provenance.__file__).absolute())] = digest(source_provenance.__file__)
    importer_path = Path(__file__).with_name('import_modal_measurements.py').absolute()
    pins[str(importer_path)] = digest(importer_path)
    paths = {k: pinned(m[k], base, pins) for k in ['accepted', 'fitter', 'analysis', 'baseline_analysis', 'corpus', 'split']}
    archive = read_archive(paths['accepted'])
    require(m['model'] == archive['model'], 'wrong model')
    # Historical measurement hashes remain provenance. A current exporter may
    # have changed; exact no-target output below establishes compatibility.
    corpus, split = read_json(paths['corpus']), read_json(paths['split'])
    files = {q['id']: q for q in corpus['files']}
    roles = split['cases']
    require(len(files) == len(corpus['files']), 'duplicate corpus ID')
    require(digest(paths['corpus']) == archive['provenance']['corpus_sha256'], 'wrong corpus')
    require(digest(paths['split']) == archive['provenance']['split_sha256'], 'wrong split')
    targets = m.get('targets')
    require(isinstance(targets, list), 'targets must be a list')
    notes = [t['note'] for t in targets]
    require(len(notes) == len(set(notes)), 'duplicate target note')
    anchors = {a['note']: a for a in archive['measurements']['anchors']}
    clocks = {a['note']: a['layer_shift_ms'] for a in archive['clocks']}
    checked = []
    for t in sorted(targets, key=lambda q: q['note']):
        note, orders = t['note'], t['orders']
        require(note in anchors and note in clocks, 'target is not an accepted anchor')
        require(isinstance(orders, list) and orders and all(type(o) is int for o in orders)
                and len(orders) == len(set(orders)), 'invalid/duplicate target order')
        require(set(orders) <= {q['order'] for q in anchors[note]['partials']}, 'membership changes unsupported')
        require(t['conditioning'] == 'accepted-clock-floor-carrier', 'unsupported conditioning')
        require(t['noise_policy'] in ('accepted', 'original-local'), 'unsupported noise policy')
        rows = t['sources']
        require(len(rows) == len(anchors[note]['velocities']), 'source layer count differs')
        require([q['velocity'] for q in rows] == anchors[note]['velocities'], 'source coordinates differ')
        require(len({q['id'] for q in rows}) == len(rows), 'duplicate source case')
        source_paths, source_records = [], []
        for q in rows:
            require(roles.get(q['id']) == 'train', 'non-TRAIN input: ' + q['id'])
            item = files.get(q['id'], {})
            require(item.get('midi') == note and item.get('kind') == 'note', 'wrong corpus note')
            try:
                record = source_provenance.prepare(item, q, m['model'], base, pins, pinned)
            except source_provenance.ProvenanceError as error:
                raise InvalidInput(str(error)) from error
            source_records.append(record)
            source_paths.append(Path(record['analysis_wav']))
        require(len({p.parent for p in source_paths}) == 1, 'source WAVs need one directory')
        require(all(p.name == q['id'] + '.wav' for p, q in zip(source_paths, rows)), 'source filenames differ from cases')
        extra = {k: pinned(t[k], base, pins) for k in ['baseline_cache', 'candidate_cache', 'selection_receipt']}
        require(isinstance(t['analysis_options'], dict), 'analysis options must be explicit')
        checked.append((t, extra, source_paths, source_records))
    return m, archive, paths, checked, pins

def equal(a, b):
    import numpy as np
    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        return isinstance(a, np.ndarray) and isinstance(b, np.ndarray) and a.dtype == b.dtype and np.array_equal(a, b, equal_nan=True)
    if isinstance(a, dict) or isinstance(b, dict):
        return isinstance(a, dict) and isinstance(b, dict) and a.keys() == b.keys() and all(equal(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)) or isinstance(b, (list, tuple)):
        return isinstance(a, type(b)) and len(a) == len(b) and all(equal(x, y) for x, y in zip(a, b))
    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        return True
    return a == b

def validate_caches(t, paths, source_paths, old, new, analysis_path):
    require(old['note'] == new['note'] == t['note'], 'raw note mismatch')
    require(old['cases'] == new['cases'] == [q['id'] for q in t['sources']], 'raw case mismatch')
    h = hashlib.sha256(analysis_path.read_bytes())
    for q in t['sources']:
        historical = q.get('provenance', {}).get('historical_cache_pin', q['wav']['sha256'])
        h.update(f"{q['id']}:{q['velocity']}:{historical}\n".encode())
    for k, v in sorted(t['analysis_options'].items()):
        h.update(f'{k}:{v}\n'.encode())
    require(old['cache_key'] == h.hexdigest(), 'stale original analysis options/source key')
    require(new.get('diagnostic_parent_cache_sha256') == digest(paths['baseline_cache']), 'candidate does not declare this baseline cache')
    allowed = {'fits', 'layers', 'cache_key', 'diagnostic_parent_cache_sha256'}
    require(set(new) - set(old) <= {'diagnostic_parent_cache_sha256'}, 'unknown derived-cache fields')
    require(set(old) <= set(new), 'missing derived-cache fields')
    for key in old:
        if key not in allowed:
            require(equal(old[key], new[key]), 'changed raw carrier/order/observation: ' + key)
    for k, order in enumerate(old['orders']):
        if order not in t['orders']:
            require(equal(old['fits'][k], new['fits'][k]), 'undeclared raw partial changed')
        else:
            require(old['fits'][k] is not None and new['fits'][k] is not None, 'missing selected fit')
            import numpy as np
            previous, selected = old['fits'][k], new['fits'][k]
            require(np.asarray(selected['theta']).shape == np.asarray(previous['theta']).shape
                    and np.all(np.isfinite(selected['theta'])), 'invalid selected pole/rise vector')
            require(len(selected['amplitudes']) == len(old['layers']), 'selected amplitude layer count')
            lanes = (len(selected['theta']) - 2) // 2
            for amplitude in selected['amplitudes']:
                if amplitude is not None:
                    require(np.asarray(amplitude).shape == (2, lanes) and lanes > 0
                            and np.all(np.isfinite(amplitude)), 'invalid selected residues')
    require(len(old['layers']) == len(new['layers']) == len(t['sources']), 'raw layer count mismatch')
    for a, b, q in zip(old['layers'], new['layers'], t['sources']):
        require(a.keys() == b.keys(), 'raw layer fields mismatch')
        require(a['velocity'] == b['velocity'] == q['velocity'], 'raw velocity mismatch')
        for key in a:
            if key != 'residual':
                require(equal(a[key], b[key]), 'undeclared source observation changed: ' + key)

def residual_proof(t, paths, old, new, pa):
    """Rebuild original subtraction, then declared delta, before float32 storage."""
    import numpy as np
    proofs = []
    for i, (source, layer) in enumerate(zip(paths, old['layers'])):
        sr, x = pa.load(source)
        require(sr == old['sr'] and pa.onset(x, sr) == layer['start'], 'source clock/rate mismatch')
        start = layer['start']
        end = pa.recorded_end(x, sr, start) - start
        n = min(end, int((layer['horizon'] + 1) * sr))
        y = x.copy()
        def wave(fit, hz):
            return pa.layer_partial_waveform(fit['theta'], fit['amplitudes'][i], layer['velocity'], hz, sr, n, layer['delay'])
        for hz, f in zip(old['freqs'], old['fits']):
            if f is not None and f['amplitudes'][i] is not None:
                y[start:start+n] -= wave(f, hz)
        # Original residual includes ring-fit extras where available.
        for k, hz in enumerate(old['extra_freqs']):
            f = old['ring_fits'][k] or old['extra_fits'][k]
            if f is not None and f['amplitudes'][i] is not None:
                y[start:start+n] -= wave(f, hz)
        count = len(layer['residual'])
        require(np.array_equal(y[start:start+count].astype(np.float32), layer['residual']), 'original residual reconstruction differs')
        for order in sorted(t['orders']):
            k = old['orders'].index(order)
            for sign, f in [(1, old['fits'][k]), (-1, new['fits'][k])]:
                if f['amplitudes'][i] is not None:
                    y[start:start+n] += sign * wave(f, old['freqs'][k])
        require(np.array_equal(y[start:start+count].astype(np.float32), new['layers'][i]['residual']), 'derived residual does not equal declared partial replacement')
        proofs.append({'case': t['sources'][i]['id'], 'old_float32_exact': True, 'new_float32_exact': True})
    return proofs

def fixed_clock_anchor(raw, shifts_ms, halo_hz, wav, fit):
    import numpy as np
    shifts = np.asarray(shifts_ms, dtype=float) / 1000
    before, record = fit.layer_alignment, []
    def accepted_alignment(phases, weights, freqs, reference, span):
        require(len(shifts) == phases.shape[1] and shifts[reference] == 0, 'accepted clock shape/reference differs')
        z = np.sum(weights * np.exp(1j * (phases - 2 * math.pi * np.outer(freqs, shifts))), axis=1)
        agreement = np.abs(z) / np.maximum(np.sum(weights, axis=1), 1e-30)
        record.append({'shifts_s': shifts.tolist(), 'agreement': agreement.tolist()})
        return shifts.copy(), agreement
    fit.layer_alignment = accepted_alignment
    try:
        value = fit.anchor_data(raw, halo_hz, wav)
    finally:
        fit.layer_alignment = before
    return value, record

def local_noise(raw, anchor, accepted, index, wav, fit, tail_floor=False):
    import numpy as np
    observations, decisions = [], []
    before = fit.noise_bands
    def capture(*a, **kw):
        value = before(*a, **kw)
        observations.append(value)
        return value
    fit.noise_bands = capture
    try:
        noise = fit.noise_data([raw], [anchor], wav, tail_floor)
    finally:
        fit.noise_bands = before
    # Accepted band centers are original seven-digit header numbers. Compare
    # the original formatter's values rather than unrounded Python doubles.
    band_index = {fit.number(v): j for j, v in enumerate(accepted['noise']['hz'])}
    require(len(band_index) == len(accepted['noise']['hz']), 'duplicate accepted noise band')
    require(all(fit.number(v) in band_index for v in noise['hz']), 'noise basis differs')
    level, decay, floor, balance, coherence, slow, slow_decay = observations[0]
    for j, hz in enumerate(noise['hz']):
        prior, new = accepted['noise']['anchors'][index][band_index[fit.number(hz)]], noise['anchors'][0][j]
        known, held = int(np.isfinite(level[:, j]).sum()), int(np.isfinite(slow[:, j]).sum())
        if known < 3:
            for key in ['level_db', 'decay_db_s', 'balance_db']:
                new[key] = copy.deepcopy(prior[key])
        if held < 3:
            require(np.all(np.asarray(new['slow_db']) == fit.NOISE_SILENT), 'slow silence contract')
            new['slow_decay_db_s'] = prior['slow_decay_db_s']
        decisions.append({'hz': hz, 'component': 'ring', 'known': known, 'held': held})
    noise['coherence'] = [accepted['noise']['coherence'][band_index[fit.number(hz)]] for hz in noise['hz']]
    body = copy.deepcopy(accepted['body'])
    body['anchors'] = [body['anchors'][index]]
    observations = []
    before = fit.knock_bands
    def capture_knock(*a, **kw):
        value = before(*a, **kw)
        observations.append(value)
        return value
    fit.knock_bands = capture_knock
    try:
        knock = fit.knock_data([raw], [anchor], body, noise, accepted['grid'], accepted['layer_level'])
    finally:
        fit.knock_bands = before
    decay, level, balance, coherence, bound = observations[0]
    for j, hz in enumerate(knock['hz']):
        require(fit.number(hz) in band_index, 'knock basis differs')
        prior, new = accepted['noise']['anchors'][index][band_index[fit.number(hz)]], knock['anchors'][0][j]
        measured, observed = bool(np.isfinite(decay[j])), bool(np.isfinite(bound[:, j]).any())
        if not measured:
            new['decay_db_s'] = prior['knock_decay_db_s']
            if not observed:
                new['level_db'] = copy.deepcopy(prior['knock_db'])
                new['balance_db'] = prior['knock_balance_db']
            else:
                require(np.all(np.asarray(new['level_db']) == fit.NOISE_SILENT), 'knock silence contract')
        decisions.append({'hz': hz, 'component': 'knock', 'measured': measured, 'observed': observed})
    knock['coherence'] = [accepted['noise']['coherence'][band_index[fit.number(hz)]] for hz in knock['hz']]
    return fit.noise_with_knock(noise, knock)['anchors'][0], decisions

def generate(manifest_path):
    import numpy as np
    m, archive, paths, targets, pins = preflight(manifest_path)
    fit, pa = operators(paths)
    require(m['model'] in fit.MODELS, 'unknown original model')
    for t, _, _, _ in targets:
        require(t['analysis_options'] == fit.analysis_options(fit.MODELS[m['model']]),
                'nondefault analysis options unsupported in residue-update schema')
    accepted = archive['measurements']
    original = fit.header(fit.MODELS[m['model']], **accepted)
    require(hashlib.sha256(original.encode()).hexdigest() == archive['provenance']['header_sha256'], 'accepted formatter roundtrip differs')
    output = copy.deepcopy(accepted)
    clocks = {q['note']: q['layer_shift_ms'] for q in archive['clocks']}
    target_records = []
    # Fixed accepted physical halo frequencies only serve original extra exclusion;
    # no halo or extra coefficient is ever adopted from the conditional export.
    halo_hz = {}
    if targets:
        def stored(x):
            return float(np.float32(float(fit.number(x).removesuffix('f'))))
        references = fit.string_pitches({a['note']: stored(a['f1']) for a in accepted['anchors']})
        for key, cents in zip(accepted['halo']['keys'], accepted['halo']['cents']):
            octave = float(np.float32(np.float32(stored(cents)) / np.float32(1200)))
            halo_hz[key] = references[key] * 2 ** octave
    source_proofs = []
    decoder_runtime = source_provenance.runtime() if any(source_records for _, _, _, source_records in targets) else None
    # Complete every transform proof before loading any raw fit pickle.
    for _, _, _, source_records in targets:
        for record in source_records:
            source_proofs.append(source_provenance.verify(record))
    for t, cache_paths, source_paths, _ in targets:
        with cache_paths['baseline_cache'].open('rb') as f:
            old = pickle.load(f)
        with cache_paths['candidate_cache'].open('rb') as f:
            new = pickle.load(f)
        validate_caches(t, cache_paths, source_paths, old, new, paths['baseline_analysis'])
        proof = residual_proof(t, source_paths, old, new, pa)
        conditional, clock = fixed_clock_anchor(new, clocks[t['note']], halo_hz, source_paths[0].parent, fit)
        index = next(i for i, a in enumerate(output['anchors']) if a['note'] == t['note'])
        anchor = output['anchors'][index]
        for order in sorted(t['orders']):
            slot = next(p for p in anchor['partials'] if p['order'] == order)
            found = [p for p in conditional['partials'] if p['order'] == order]
            require(len(found) == 1, 'selected order failed original export admission')
            for key in ['rise_seconds', 'rise_slope', 'lanes']:
                slot[key] = copy.deepcopy(found[0][key])
        anchor['layer_shift_ms'] = clocks[t['note']]
        record = {'note': t['note'], 'orders': sorted(t['orders']), 'residual_proof': proof,
                  'clock': clock, 'accepted_onset_floor': accepted['anchors'][index]['onset_rise'],
                  'unused_new_onset_floor': conditional['onset_rise'].tolist(), 'noise_policy': t['noise_policy']}
        if t['noise_policy'] == 'original-local':
            tail_floor = fit.MODELS[m['model']].get('tail_floor', False)
            old_noise, old_support = local_noise(old, anchor, accepted, index, source_paths[0].parent, fit, tail_floor)
            new_noise, support = local_noise(new, anchor, accepted, index, source_paths[0].parent, fit, tail_floor)
            record['noise_three_way'] = encode({'accepted': accepted['noise']['anchors'][index], 'old_recovered': old_noise, 'new': new_noise})
            record['noise_support'] = {'old_recovered': old_support, 'new': support}
            output['noise']['anchors'][index] = new_noise
        target_records.append(record)
    # Restore allowed fields into a copy and demand exact equality of all other
    # accepted numbers. This covers globals, extras, halo, floor and membership.
    unchanged = copy.deepcopy(output)
    for t, _, _, _ in targets:
        i = next(i for i, a in enumerate(unchanged['anchors']) if a['note'] == t['note'])
        for order in t['orders']:
            j = next(j for j, p in enumerate(unchanged['anchors'][i]['partials']) if p['order'] == order)
            unchanged['anchors'][i]['partials'][j] = copy.deepcopy(accepted['anchors'][i]['partials'][j])
        unchanged['anchors'][i].pop('layer_shift_ms', None)
        unchanged['noise']['anchors'][i] = copy.deepcopy(accepted['noise']['anchors'][i])
    require(equal(unchanged, accepted), 'immutable accepted domain changed')
    content = fit.header(fit.MODELS[m['model']], **output)
    for path, expected in pins.items():
        require(digest(path) == expected, 'input changed during generation: ' + path)
    receipt = {'schema': MANIFEST, 'model': m['model'], 'input_pins': pins, 'manifest_path': str(Path(manifest_path).absolute()),
               'accepted_archive_path': str(paths['accepted']), 'accepted_archive_sha256': digest(paths['accepted']),
               'script_sha256': digest(__file__), 'accepted_roundtrip_exact': True,
               'source_proofs': source_proofs, 'decoder_runtime': decoder_runtime,
               'unchanged_domains_exact': True, 'targets': target_records,
               'output_sha256': hashlib.sha256(content.encode()).hexdigest(),
               'fits_run': 0, 'scope': 'Conditional same-carrier partial update; native/source acceptance is external.',
               'versions': {'python': sys.version.split()[0], 'numpy': np.__version__}}
    return content, receipt

def snapshot(content, receipt):
    """New immutable exported-number snapshot; the parent archive is untouched."""
    pins = receipt['input_pins']
    verify_pins(pins)
    # operators() puts the historical fitter directory first on sys.path.
    # That directory (or a prior sys.modules entry) must not substitute its
    # importer for the sibling implementation recorded by preflight().
    importer_path = Path(__file__).with_name('import_modal_measurements.py').absolute()
    require(digest(importer_path) == pinned_identity(importer_path, pins),
            'snapshot importer differs from pinned input')
    importer = module('_keyra_snapshot_importer', importer_path)
    require(Path(importer.__file__).resolve() == importer_path.resolve(),
            'wrong snapshot importer loaded')
    require(digest(importer_path) == pinned_identity(importer_path, pins),
            'snapshot importer changed during loading')
    require(hashlib.sha256(content.encode()).hexdigest() == receipt['output_sha256'], 'snapshot content differs from receipt')
    require(pinned_identity(receipt['accepted_archive_path'], pins) == receipt['accepted_archive_sha256'],
            'parent archive is not the pinned input')
    parent = read_archive(receipt['accepted_archive_path'])
    require(digest(receipt['accepted_archive_path']) == receipt['accepted_archive_sha256'], 'parent archive changed')
    require(parent['model'] == receipt['model'], 'snapshot model differs from parent')
    with tempfile.TemporaryDirectory() as directory:
        header = Path(directory)/'generated.h'
        header.write_bytes(content.encode('utf-8'))
        values = importer.load(header)
    p = parent['provenance']
    update_sha = hashlib.sha256(json_bytes(receipt)).hexdigest()
    # The execution operator is explicitly named by the manifest, not guessed
    # from a historical source digest when two analysis implementations differ.
    manifest_path = Path(receipt['manifest_path'])
    manifest_bytes = manifest_path.read_bytes()
    require(hashlib.sha256(manifest_bytes).hexdigest() == pinned_identity(manifest_path, pins),
            'manifest differs from pinned input')
    manifest = json.loads(manifest_bytes, parse_constant=reject_constant)
    execution = {}
    for key in ['analysis', 'fitter']:
        ref = manifest[key]
        require(isinstance(ref, dict) and set(ref) == {'path', 'sha256'}, 'invalid operator reference')
        path = Path(ref['path'])
        if not path.is_absolute():
            path = manifest_path.parent / path
        require(ref['sha256'] == pinned_identity(path, pins), 'operator identity differs from input pins: ' + key)
        execution[key] = ref['sha256']
    provenance = {'derivation': 'conditional-partial-update-v1', 'header_sha256': receipt['output_sha256'],
                  'parent_archive_sha256': receipt['accepted_archive_sha256'], 'parent_header_sha256': p['header_sha256'],
                  'update_receipt_sha256': update_sha, 'corpus_sha256': p['corpus_sha256'], 'split_sha256': p['split_sha256'],
                  'execution_analysis_sha256': execution['analysis'], 'execution_fitter_sha256': execution['fitter'],
                  'recording_attribution': p['recording_attribution'],
                  'conditioning': 'Accepted clocks, onset floors, carriers and all undeclared domains retained; see update receipt.',
                  'meaning': 'Current exported numeric measurements. Stored-number regeneration does not recalibrate source audio.'}
    # Explicitly label the historical metadata as belonging to the parent.
    if 'metadata_sha256' in p:
        provenance['parent_metadata_sha256'] = p['metadata_sha256']
    value = {'schema': SCHEMA, 'model': receipt['model'], 'measurements': values,
             'clocks': copy.deepcopy(parent['clocks']), 'provenance': provenance}
    verify_pins(pins)
    return gzip.compress(json_bytes(encode(value)), mtime=0)

def publish(path, content, check=False):
    path = Path(path)
    if check:
        require(path.read_bytes() == content, 'generated output differs: ' + str(path))
        return
    require(not path.exists(), 'refusing to overwrite existing output: ' + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(content)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('--header', type=Path, required=True)
    p.add_argument('--receipt', type=Path, required=True)
    p.add_argument('--snapshot', type=Path, help='new immutable current-number archive; parent archive stays unchanged')
    p.add_argument('--check', action='store_true')
    a = p.parse_args()
    content, receipt = generate(a.manifest)
    protect_outputs([a.header, a.receipt, a.snapshot], receipt['input_pins'])
    packed = snapshot(content, receipt) if a.snapshot else None
    publish(a.header, content.encode(), a.check)
    publish(a.receipt, json_bytes(receipt), a.check)
    if a.snapshot:
        publish(a.snapshot, packed, a.check)
    print(receipt['output_sha256'])

if __name__ == '__main__':
    main()
