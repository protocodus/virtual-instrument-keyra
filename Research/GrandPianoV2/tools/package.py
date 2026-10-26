#!/usr/bin/env python3
"""Package source, reproducibility evidence, attributed references and demos.

Large native-rate scratch renders are excluded; tools regenerate them. The
archive manifest identifies every included byte and zip CRCs are checked.
"""
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def included(path):
    rel = path.relative_to(ROOT)
    if any(x in {'__pycache__', '.DS_Store', 'build'} for x in rel.parts):
        return False
    if rel.suffix in {'.pyc', '.log'} or rel.name == 'artifact-manifest.json':
        return False
    if rel.parts[:2] == ('reference', 'wav'):
        return False  # original lossless FLACs and fetch/decode tool are included
    if rel.parts[0] == 'benchmark' and rel.suffix == '.wav':
        return False
    return rel.parts[0] in {'src', 'tools', 'scores', 'renders', 'listening',
                            'reference', 'benchmark', 'validation', 'bin'} or len(rel.parts) == 1


def main():
    (ROOT/'bin').mkdir(exist_ok=True)
    for source, target in [('build/grand', 'grand-macos-arm64'),
                           ('build/grand_candidate', 'grand-benchmark-macos-arm64')]:
        shutil.copy2(ROOT/source, ROOT/'bin'/target)
    files = sorted(p for p in ROOT.rglob('*') if p.is_file() and included(p))
    manifest = {'format': 1, 'project': ROOT.name,
        'omitted': ['Native float benchmark WAVs and projection stems', '192 kHz build/raw intermediates',
                    'Decoded reference WAV copies (original FLACs included)', 'Build/profiling scratch files'],
        'files': [{'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size,
                   'sha256': sha(p)} for p in files]}
    report = ROOT/'artifact-manifest.json'
    report.write_text(json.dumps(manifest, indent=2)+'\n')
    files.append(report)
    destination = ROOT.parents[1]/'deliverables'/'grand-piano-physical-model-poc-v2-20261025.zip'
    destination.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(destination, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for p in files:
            archive.write(p, ROOT.name+'/'+str(p.relative_to(ROOT)))
    with zipfile.ZipFile(destination) as archive:
        assert archive.testzip() is None, 'Archive CRC verification failed'
    result = {'archive': str(destination), 'bytes': destination.stat().st_size,
              'sha256': sha(destination), 'files': len(files)}
    destination.with_suffix('.sha256').write_text(result['sha256']+'  '+destination.name+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
