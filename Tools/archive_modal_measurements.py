#!/usr/bin/env python3
"""Bootstrap a canonical numeric archive from an accepted generated header.

The restricted importer only reads public numeric C++ initializers. It is not
a raw-fit recovery tool. Original exporter roundtrip is mandatory; raw audio,
fit caches and pickles never enter the archive.
"""
import argparse
import gzip
from pathlib import Path
import sys
import update_modal_measurements as u

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['header', 'metadata', 'corpus', 'split', 'fitter', 'analysis', 'importer', 'output']:
        p.add_argument('--' + name, required=True, type=Path)
    p.add_argument('--model', required=True)
    a = p.parse_args()
    paths = {k: getattr(a, k).absolute() for k in ['header', 'metadata', 'corpus', 'split', 'fitter', 'analysis', 'importer']}
    u.protect_outputs([a.output], [*paths.values(), Path(__file__), Path(u.__file__)])
    pins = {k: u.digest(v) for k, v in paths.items()}
    fit, _ = u.operators(paths)
    importer = u.module('accepted_numeric_importer', paths['importer'])
    metadata, corpus = u.read_json(paths['metadata']), u.read_json(paths['corpus'])
    u.require(metadata['generated_header_sha256'] == pins['header'], 'metadata/header mismatch')
    u.require(metadata['corpus_sha256'] == pins['corpus'] and metadata['split_sha256'] == pins['split'], 'metadata corpus/split mismatch')
    values = importer.load(paths['header'])
    content = fit.header(fit.MODELS[a.model], **values)
    u.require(content.encode() == paths['header'].read_bytes(), 'original formatter roundtrip differs')
    notes = {q['note'] for q in values['anchors']}
    clocks = [{'note': q['note'], 'layer_shift_ms': q['layer_shift_ms']}
              for q in metadata['anchors'] if q['note'] in notes]
    u.require(len(clocks) == len(notes), 'missing accepted layer clocks')
    value = {'schema': u.SCHEMA, 'model': a.model, 'measurements': values,
             'clocks': clocks, 'provenance': {
                 'header_sha256': pins['header'], 'metadata_sha256': pins['metadata'],
                 'corpus_sha256': pins['corpus'], 'split_sha256': pins['split'],
                 'historical_analysis_sha256': metadata['analysis_source_sha256'],
                 'historical_fitter_sha256': metadata['fitter_source_sha256'],
                 'bootstrap_analysis_sha256': pins['analysis'], 'fitter_sha256': pins['fitter'],
                 'importer_sha256': pins['importer'], 'archive_script_sha256': u.digest(__file__),
                 'recording_attribution': {k: corpus[k] for k in ['title', 'author', 'license'] if k in corpus},
                 'meaning': 'Accepted exported numeric measurements, not historical raw-fit sufficient statistics.'}}
    packed = gzip.compress(u.json_bytes(u.encode(value)), mtime=0)
    for k, path in paths.items():
        u.require(u.digest(path) == pins[k], 'bootstrap input changed')
    u.protect_outputs([a.output], [*paths.values(), Path(__file__), Path(u.__file__)])
    u.publish(a.output, packed)
    print(u.digest(a.output))

if __name__ == '__main__':
    main()
