#!/usr/bin/env python3
"""Package the locally validated Linux development preview, without installing it."""
import argparse
import hashlib
import json
import platform
import shutil
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--clap',type=Path,default=ROOT/'build/plugin/Keyra.clap')
    p.add_argument('--vst3',type=Path,default=ROOT/'build-vst3/VST3/Release/Keyra.vst3')
    a=p.parse_args()
    if platform.system()!='Linux':raise RuntimeError('This preview packaging layout is Linux only')
    destination=ROOT/'deliverables';destination.mkdir(exist_ok=True)
    stage=destination/'Keyra-0.2.0-linux-preview'
    if stage.exists():shutil.rmtree(stage)
    stage.mkdir()
    shutil.copy2(a.clap,stage/'Keyra.clap')
    if a.vst3.exists():shutil.copytree(a.vst3,stage/'Keyra.vst3',symlinks=True)
    for path in ('README.md','plugin/README.md','vst3/README.md','third_party/clap/LICENSE','vst3/SDK-LICENSE.txt',
                 'Research/GrandPianoV2/reference/ATTRIBUTION.md','Research/GrandPianoV2/reference/upstream/LICENSE-CC-BY-3.0.txt',
                 'References/Upright/README.md','References/Upright/upstream/LICENSE'):
        source=ROOT/path
        if source.exists():
            target=stage/'notices'/path;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
    (stage/'INSTALL.txt').write_text('Keyra 0.2.0 Linux development preview\n\nCopy Keyra.clap to ~/.clap/ and/or Keyra.vst3 to ~/.vst3/, then rescan in your DAW.\nUse the host generic parameter editor. This is an unsigned Linux binary, not a Windows/macOS build.\n\nThis preview has not passed commercial DAW, perceptual listening or release performance gates.\nNo sample recordings or impulse responses are loaded or included in the runtime.\nCalibration provenance and third-party notices are in notices/.\n')
    hashes={str(path.relative_to(stage)):hashlib.sha256(path.read_bytes()).hexdigest()
            for path in stage.rglob('*') if path.is_file() and not path.is_symlink()}
    (stage/'manifest.json').write_text(json.dumps({'version':'0.2.0-preview','platform':platform.platform(),'files':hashes},indent=2)+'\n')
    archive=destination/(stage.name+'.tar.gz')
    with tarfile.open(archive,'w:gz') as out:out.add(stage,arcname=stage.name)
    print(archive)


if __name__=='__main__':main()
