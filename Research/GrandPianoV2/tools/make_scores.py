#!/usr/bin/env python3
"""Write original, reproducible piano POC performances as events and MIDI.

No external music, recordings, MIDI performances, or Python packages are used.
The event time unit is seconds; MIDI is a lossless 960-tick/s timing companion.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import random
import struct


class Score:
    def __init__(self, name, title, description, bpm, beats, rubato=0.0):
        self.name, self.title, self.description = name, title, description
        self.bpm, self.beats = bpm, beats
        self.notes = []
        self.pedals = []
        self.rng = random.Random(name)
        self.times = [0.20]
        # Integrate a smooth tempo contour instead of jittering whole bars.
        for i in range(int((beats + 4) * 32)):
            b = (i + 0.5) / 32
            phrasing = math.sin(2 * math.pi * b / 16)
            closing = max(0, min(1, (b - beats + 4) / 4)) ** 2
            duration = 60 / bpm * (1 + rubato * phrasing + 0.16 * closing)
            self.times.append(self.times[-1] + duration / 32)

    def time(self, beat):
        index = max(0.0, beat * 32)
        i = int(index)
        return self.times[i] + (index - i) * (self.times[i + 1] - self.times[i])

    def note(self, beat, pitch, duration, velocity, hand="r", spread=0.0):
        jitter = self.rng.uniform(-0.005, 0.005)
        start = self.time(beat) + jitter + spread + (0.009 if hand == "r" else 0)
        end = self.time(beat + duration) + jitter + spread
        vel = max(1, min(127, int(round(velocity + self.rng.uniform(-2, 2)))))
        self.notes.append([start, max(start + 0.025, end), pitch, vel])

    def chord(self, beat, pitches, duration, velocity, hand="l", roll=0.009):
        for i, pitch in enumerate(pitches):
            self.note(beat, pitch, duration, velocity - (1 if i < len(pitches) - 1 else 0), hand, i * roll)

    def pedal(self, beat, value):
        self.pedals.append((self.time(beat), value))

    def finish(self):
        # A repeated key releases its preceding depression, even with pedal held.
        # Resonant continuation is then the physical model's responsibility.
        by_pitch = {}
        for n in sorted(self.notes):
            previous = by_pitch.get(n[2])
            if previous is not None and previous[1] >= n[0]:
                previous[1] = max(previous[0] + 0.01, n[0] - 0.006)
            by_pitch[n[2]] = n
        events = []
        for start, end, pitch, velocity in self.notes:
            events.extend([(start, "on", pitch, velocity), (end, "off", pitch, 0)])
        for t, value in self.pedals:
            events.append((t, "pedal", 0, value))
        end = max(self.time(self.beats), max(n[1] for n in self.notes)) + 0.35
        events.append((end, "pedal", 0, 0))
        order = {"off": 0, "pedal": 1, "on": 2}
        return sorted(events, key=lambda e: (e[0], order[e[1]], e[2])), end


def nocturne():
    s = Score("01_nocturne", "Window at Dusk", "Original lyrical F-minor nocturne; singing melody, rolled bass figures, rubato and changing half pedal.", 64, 32, 0.08)
    harmony = [(29, 48, 56, 60), (34, 53, 56, 61), (32, 51, 55, 60), (36, 52, 58, 61),
               (37, 53, 56, 60), (34, 53, 58, 62), (36, 55, 58, 64), (29, 48, 56, 60)]
    melodies = [
        [(0,72,1.45,77),(1.5,75,.45,72),(2,77,.85,83),(3,75,.85,74)],
        [(0,73,1.8,78),(2,72,.45,70),(2.5,70,.45,68),(3,68,.85,67)],
        [(0,67,.8,70),(1,72,.8,77),(2,75,1.35,83),(3.5,79,.4,86)],
        [(0,77,1.35,85),(1.5,76,.4,75),(2,73,.8,73),(3,72,.9,69)],
        [(0,80,1.35,88),(1.5,79,.4,82),(2,77,.8,80),(3,75,.85,76)],
        [(0,74,.9,79),(1,77,.9,85),(2,80,1.7,91)],
        [(0,79,.85,85),(1,76,.85,76),(2,73,.85,71),(3,72,.75,66)],
        [(0,72,.8,70),(1,68,.8,63),(2,65,1.9,59)],
    ]
    for bar, bass in enumerate(harmony):
        b = bar * 4
        for beat, pitch in zip([0, 1, 2, 3], bass):
            s.note(b + beat, pitch, 0.92, 51 + 3 * (bar in [4,5]) - beat, "l")
        for beat, pitch, dur, vel in melodies[bar]:
            s.note(b + beat + 0.025, pitch, dur, vel)
        s.pedal(b + 0.08, 0.75 if bar not in [3,6] else 0.6)
        s.pedal(b + 3.88, 0.08)
    s.chord(30, [53, 60], 1.8, 43, roll=0.018)
    s.pedal(31.85, 0.42)
    return s


def prelude():
    s = Score("02_prelude", "Two Voices in Morning Light", "Original D-major contrapuntal miniature; overlapping voices, light articulation, restrained pedal.", 82, 32, 0.018)
    treble = [
        [74,69,66,69,76,69,66,69], [78,74,69,74,79,74,71,74],
        [81,76,73,76,79,76,73,76], [78,74,69,74,76,73,69,73],
        [74,71,67,71,76,71,67,71], [78,74,69,74,79,76,73,76],
        [81,78,74,78,76,73,69,73], [74,69,66,69,74,78,81,78],
    ]
    bass = [[38,45,50,54], [35,42,47,50], [33,40,45,49], [38,45,42,45],
            [43,50,47,50], [42,49,45,49], [38,45,33,45], [38,50,54,57]]
    for bar, notes in enumerate(treble):
        for i, n in enumerate(notes):
            s.note(bar * 4 + i * 0.5, n, 0.43 if i % 2 else 0.49, 65 + [8,0,2,-1,6,0,1,-2][i] + (3 if bar >= 4 else 0))
        for i, n in enumerate(bass[bar]):
            s.note(bar * 4 + i, n, .91, 57 + [4,0,2,-1][i], "l")
        # Shallow foot support; articulation remains primarily finger driven.
        s.pedal(bar * 4 + .1, .17)
        s.pedal(bar * 4 + 3.8, 0)
    s.chord(31.5, [62,66,69], .48, 62)
    return s


def jazz_waltz():
    s = Score("03_jazz_waltz", "Sunday on the River", "Original twelve-bar jazz waltz in C; rootless voicings, melodic variations and a soft final turnaround.", 90, 36, 0.035)
    harmonies = [(36,[52,59,62]),(33,[55,60,64]),(38,[53,60,64]),(43,[53,59,64]),
                 (36,[52,59,62]),(40,[55,62,66]),(45,[55,61,64]),(38,[53,60,64]),
                 (41,[57,60,64]),(46,[56,62,65]),(43,[53,59,64]),(36,[52,59,62])]
    melody = [
        [(0,67,.8),(1,71,.7),(2,74,.8)], [(0,76,1.3),(1.5,72,.4),(2,69,.8)],
        [(0,65,.8),(1,69,.7),(2,72,.8)], [(0,71,1.3),(1.5,69,.4),(2,67,.8)],
        [(0,67,.8),(1,71,.7),(2,74,.8)], [(0,78,1.7),(2,76,.8)],
        [(0,76,.8),(1,73,.8),(2,71,.8)], [(0,69,1.7),(2,72,.8)],
        [(0,76,1.7),(2,72,.8)], [(0,74,.8),(1,70,.7),(2,68,.8)],
        [(0,67,.8),(1,69,.4),(1.5,71,.4),(2,74,.8)], [(0,72,2.8)],
    ]
    for bar, (root, voicing) in enumerate(harmonies):
        b = bar * 3
        s.note(b, root, 1.15, 63 if bar < 10 else 56, "l")
        s.chord(b + 1.04, voicing, .7, 48 if bar < 10 else 43, roll=.004)
        s.chord(b + 2.03, voicing, .64 if bar < 11 else .92, 45 if bar < 10 else 41, roll=.005)
        for beat, pitch, dur in melody[bar]:
            s.note(b + beat + .04, pitch, dur, 76 + (4 if bar in [4,5,8] else 0) - (9 if bar == 11 else 0))
        s.pedal(b + .1, .38)
        s.pedal(b + 2.87, 0)
    return s


def etude():
    s = Score("04_etude", "Copper and Thunder", "Original C-minor concert study; wide register, dynamic build, alternating broken octaves and a resonant final cadence.", 86, 32, 0.028)
    figures = [
        [60,67,72,75,79,75,72,67], [56,63,68,72,75,72,68,63],
        [53,60,65,68,72,68,65,60], [55,62,67,71,74,71,67,62],
        [72,79,84,87,91,87,84,79], [68,75,80,84,87,84,80,75],
        [65,72,77,80,83,80,77,72], [67,74,79,83,86,83,79,72],
    ]
    roots = [36,32,29,31,24,32,29,31]
    for bar, notes in enumerate(figures):
        b = bar * 4
        base = [69,72,75,80,91,94,99,103][bar]
        for i, pitch in enumerate(notes):
            if bar == 7 and i == 7:
                continue  # The final cadence replaces this eighth-note pickup.
            s.note(b + i * .5, pitch, .43 if i % 2 else .53, base + [4,-3,0,1,6,0,-2,-4][i])
        for i, pitch in enumerate([roots[bar], roots[bar] + 12, roots[bar] + 7, roots[bar] + 12]):
            s.note(b + i, pitch, .78, base - 9 + (5 if i == 0 else 0), "l")
        s.pedal(b + .08, .56 if bar < 4 else .72)
        if bar < 7:
            s.pedal(b + 3.85, .02)
    # Final cadence enters after a short breath and stays under the onset cap.
    s.chord(31.5, [24,36,48], .48, 106, "l", .010)
    s.chord(31.52, [60,67,72,75], .47, 103, "r", .012)
    s.pedal(31.60, .8)
    return s


def diagnostic():
    s = Score("05_diagnostics", "Velocity, Register and Pedal Study", "Controlled low/mid/high notes, soft-to-hard velocities, damped/pedal comparison and a sustained harmonic-chord response.", 60, 28, 0)
    for i, (pitch, vel) in enumerate([(45,44),(60,44),(81,44),(45,90),(60,90),(81,90),(45,120),(60,120),(81,120)]):
        s.note(i * 1.8, pitch, 1.15, vel)
    s.pedal(17, 1)
    s.chord(17.1, [36,48,55,60,64,67,72], .65, 88, roll=.012)
    s.pedal(21, .48)
    s.pedal(23, 0)
    s.note(24, 21, 1.1, 108)
    s.note(26, 108, .6, 100)
    return s


def vlq(value):
    values = [value & 127]
    value >>= 7
    while value:
        values.insert(0, (value & 127) | 128)
        value >>= 7
    return bytes(values)


def chunk(kind, data):
    return kind + struct.pack(">I", len(data)) + data


def write_midi(path, title, events, end):
    # 480 PPQ at 120 BPM = 960 ticks per second. Expressive timing is in ticks.
    title_bytes = title.encode("utf-8")
    conductor = b"\x00\xff\x03" + vlq(len(title_bytes)) + title_bytes
    conductor += b"\x00\xff\x51\x03\x07\xa1\x20\x00\xff\x58\x04\x04\x02\x18\x08\x00\xff\x2f\x00"
    track = bytearray(b"\x00\xc0\x00")
    last_tick = 0
    for seconds, kind, note, value in events:
        tick = round(seconds * 960)
        track.extend(vlq(tick - last_tick))
        if kind == "on":
            track.extend([0x90, note, int(value)])
        elif kind == "off":
            track.extend([0x80, note, 0])
        else:
            track.extend([0xB0, 64, round(value * 127)])
        last_tick = tick
    track.extend(vlq(max(0, round((end + .1) * 960) - last_tick)))
    track.extend(b"\xff\x2f\x00")
    path.write_bytes(chunk(b"MThd", struct.pack(">HHH", 1, 2, 480)) + chunk(b"MTrk", conductor) + chunk(b"MTrk", bytes(track)))


def write_score(s, out):
    events, end = s.finish()
    assert len(s.notes) < 130, (s.name, len(s.notes))
    lines = [f"# {s.title}", f"# {s.description}", "# Original composition and original algorithmic performance, 2026-10-25.", "# seconds kind note value; pedal value ranges from 0 to 1."]
    for seconds, kind, note, value in events:
        value_text = f"{value:.4f}" if kind == "pedal" else str(int(value))
        lines.append(f"{seconds:.6f} {kind} {note} {value_text}")
    (out / (s.name + ".events")).write_text("\n".join(lines) + "\n")
    write_midi(out / (s.name + ".mid"), s.title, events, end)
    return {"id":s.name, "title":s.title, "description":s.description,
            "provenance":"Original composition and original deterministic algorithmic performance created for this POC; no external MIDI or recordings.",
            "note_onsets":len(s.notes), "duration_seconds":round(end, 3),
            "nominal_bpm":s.bpm, "events":s.name + ".events", "midi":s.name + ".mid"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parents[1] / "scores")
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    metadata = [write_score(factory(), args.out_dir) for factory in [nocturne, prelude, jazz_waltz, etude, diagnostic]]
    (args.out_dir / "manifest.json").write_text(json.dumps(metadata, indent=2) + "\n")
    for score in metadata:
        print(f"{score['id']}: {score['title']}, {score['duration_seconds']:.2f} s, {score['note_onsets']} notes")


if __name__ == "__main__":
    main()
