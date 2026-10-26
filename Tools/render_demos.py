#!/usr/bin/env python3
"""Render original musical/controller examples through the current live engine.

No post-render normalization, equalization, room or reverb is applied. MP3s
are previews of the default product settings, not the offline research solver.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--renderer', type=Path, default=ROOT/'build/keyra_render')
    args = parser.parse_args()
    renderer = args.renderer.resolve()
    target = ROOT/'Docs/audio/live'
    working = ROOT/'build/live-demos'
    target.mkdir(parents=True, exist_ok=True)
    working.mkdir(parents=True, exist_ok=True)
    scores = json.loads((ROOT/'Experiments/Research/GrandPianoV2/scores/manifest.json').read_text())
    cases = [(s['id'], s['title'], ROOT/'Experiments/Research/GrandPianoV2/scores'/s['events'],
              s['duration_seconds']+7) for s in scores
             if s['id'] in ('01_nocturne', '03_jazz_waltz')]
    cases.append(('pedal-study', 'Keyra pedal and mute study',
                  ROOT/'Docs/audio/events/pedal-study.events', 14))
    manifest = {
        'engine': 'Current reduced modal engine; not the preserved nonlinear solver',
        'renderer_sha256': digest(renderer),
        'source_sha256': digest(ROOT/'Source/DSP/KeyraEngine.cpp'),
        'calibration_sha256': digest(ROOT/'Source/DSP/MeasuredModalData.h'),
        'settings': '48 kHz, all product defaults, no post-render normalization or effects',
        'composition_provenance': 'Original authored scores and controller study; no external MIDI',
        'cases': [],
    }
    for identity, title, events, duration in cases:
        wav = working/(identity+'.wav')
        mp3 = target/(identity+'.mp3')
        command = [str(renderer), '--events', str(events), '--duration', str(duration),
                   '--output', str(wav), '--sample-rate', '48000']
        metrics = json.loads(subprocess.check_output(command, text=True))
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(wav),
                        '-codec:a', 'libmp3lame', '-b:a', '192k',
                        '-metadata', 'title='+title, str(mp3)], check=True)
        manifest['cases'].append({'id': identity, 'title': title,
                                  'events': str(events.relative_to(ROOT)),
                                  'events_sha256': digest(events),
                                  'render_command': command, 'metrics': metrics,
                                  'mp3': mp3.name, 'sha256': digest(mp3)})
        print(identity, metrics)
    (target/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')


if __name__ == '__main__':
    main()
