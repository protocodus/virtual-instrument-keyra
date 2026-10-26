#!/usr/bin/env python3
"""Write the committed per-preset demo phrases, Docs/audio/midi/<NN>-<slug>.mid.

One phrase per factory preset (README G3a), written for what that preset is
for: Concert Grand plays a full-range romantic phrase with legato pedalling,
Studio Grand a pop ballad pattern, Warm Walnut jazz voicings with the soft
pedal, Felt Nocturne a quiet nocturne whose felt the modulation wheel brings
in, and Open Strings struck notes with the dampers raised so the undamped
strings ring. The .mid files are the committed sources the demo renderer
reads; this script only records how they were written. Re-run it only to
change a phrase on purpose, and commit the changed .mid files on their own:

    python3 Tools/write_preset_midi.py Docs/audio/midi

Every file is format 0 on MIDI channel 1 at 480 PPQ, with a tempo and a track
name, and lasts 10-16 s before the renderer's release tail. Notes stay inside
the piano's A0..C8: MIDI 12-14 are Keyra's pedal keyswitches.
"""
import argparse
from pathlib import Path
import struct

PPQ = 480
NAMES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
SUSTAIN, SOSTENUTO, SOFT, MODULATION = 64, 66, 67, 1


def n(name: str) -> int:
    """'C4' is MIDI 60; sharps as 'F#3', flats as 'Bb2'."""
    pitch = NAMES[name[0]]
    rest = name[1:]
    if rest[0] == "#":
        pitch, rest = pitch + 1, rest[1:]
    elif rest[0] == "b":
        pitch, rest = pitch - 1, rest[1:]
    return 12 * (int(rest) + 1) + pitch


class Phrase:
    def __init__(self, bpm: float):
        self.bpm = bpm
        self.events = []  # (beat, order, bytes); note-offs sort before note-ons

    def note(self, beat, length, pitch, velocity=80):
        pitch = n(pitch) if isinstance(pitch, str) else pitch
        if not 21 <= pitch <= 108:
            raise ValueError(f"{pitch} is outside the piano")
        self.events.append((beat, 1, bytes([0x90, pitch, velocity])))
        self.events.append((beat + length, 0, bytes([0x80, pitch, 64])))

    def chord(self, beat, length, pitches, velocity=80):
        for pitch in pitches:
            self.note(beat, length, pitch, velocity)

    def line(self, beat, notes, velocity=80):
        """(pitch, beats) pairs played legato from `beat`; a None pitch rests."""
        for pitch, length in notes:
            if pitch is not None:
                self.note(beat, length * 0.98, pitch, velocity)
            beat += length
        return beat

    def arpeggio(self, beat, step, pitches, length, velocity=70):
        """Each note `step` after the last, held `length` beats from its strike."""
        for index, pitch in enumerate(pitches):
            self.note(beat + index * step, length, pitch, velocity)

    def cc(self, beat, controller, value):
        self.events.append((beat, 2, bytes([0xB0, controller, value])))

    def ramp_cc(self, beat, length, controller, start, end, steps=32):
        for step in range(steps + 1):
            fraction = step / steps
            self.cc(beat + length * fraction, controller, round(start + (end - start) * fraction))

    def change_pedal(self, beat):
        """Legato pedalling: lift as the new harmony strikes, catch it just after."""
        self.cc(beat, SUSTAIN, 0)
        self.cc(beat + 0.2, SUSTAIN, 127)

    def smf(self, name: str) -> bytes:
        def vlq(value):
            out = [value & 0x7F]
            value >>= 7
            while value:
                out.append(0x80 | (value & 0x7F))
                value >>= 7
            return bytes(reversed(out))

        tempo = round(60_000_000 / self.bpm)
        track = bytearray()
        track += b"\x00\xff\x03" + vlq(len(name)) + name.encode("ascii")
        track += b"\x00\xff\x51\x03" + tempo.to_bytes(3, "big")
        last = 0
        for beat, _, message in sorted(self.events, key=lambda e: (e[0], e[1], e[2])):
            tick = round(beat * PPQ)
            track += vlq(tick - last) + message
            last = tick
        track += b"\x00\xff\x2f\x00"
        return (b"MThd" + struct.pack(">IHHH", 6, 0, 1, PPQ)
                + b"MTrk" + struct.pack(">I", len(track)) + track)


def concert_grand():
    # C minor, four bars of left-hand arpeggios under a melody that grows
    # from piano to forte, then a full-range final chord.
    p = Phrase(72)
    bars = [
        ["C2", "G2", "C3", "Eb3", "G3", "Eb3", "C3", "G2"],
        ["Ab1", "Eb2", "Ab2", "C3", "Eb3", "C3", "Ab2", "Eb2"],
        ["F1", "C2", "F2", "Ab2", "C3", "Ab2", "F2", "C2"],
        ["G1", "D2", "G2", "B2", "F3", "D3", "B2", "G2"],
    ]
    melody = [
        [("G4", 2), ("Eb5", 1), ("D5", 1)],
        [("C5", 1.5), ("Bb4", 0.5), ("Ab4", 2)],
        [("Ab4", 1), ("C5", 1), ("F5", 1.5), ("Eb5", 0.5)],
        [("D5", 1), ("Eb5", 0.5), ("D5", 0.5), ("B4", 2)],
    ]
    p.cc(0, SUSTAIN, 127)
    for bar, (arpeggio, line) in enumerate(zip(bars, melody)):
        start = 4 * bar
        if bar:
            p.change_pedal(start)
        p.arpeggio(start, 0.5, arpeggio, 0.5, 56 + 8 * bar)
        p.line(start, line, 62 + 12 * bar)
    p.change_pedal(16)
    p.chord(16, 3, ["C1", "C2", "G2", "Eb3", "G4", "C5", "Eb5", "C6"], 104)
    p.cc(19, SUSTAIN, 0)
    return p


def studio_grand():
    # A pop ballad pattern: syncopated right-hand chords over left-hand
    # octaves, pedal caught after each change and lifted before the next.
    p = Phrase(96)
    progression = [
        (["C2", "C3"], ["E4", "G4", "C5"]),
        (["B1", "B2"], ["D4", "G4", "B4"]),
        (["A1", "A2"], ["C4", "E4", "A4"]),
        (["F1", "F2"], ["C4", "F4", "A4"]),
    ]
    for bar, (bass, chord) in enumerate(progression):
        start = 4 * bar
        p.chord(start, 3.8, bass, 84)
        for beat, velocity in ((0, 88), (1, 72), (1.5, 78), (2.5, 80), (3, 74)):
            p.chord(start + beat, 0.4, chord, velocity)
        p.cc(start + 0.1, SUSTAIN, 127)
        p.cc(start + 3.85, SUSTAIN, 0)
    p.line(14, [("G5", 0.5), ("A5", 0.5), ("G5", 0.5), ("E5", 0.5)], 86)
    p.chord(16, 1.9, ["G1", "G2"], 86)
    p.chord(16, 1, ["D4", "G4", "C5"], 84)
    p.chord(17, 0.9, ["D4", "G4", "B4"], 80)
    p.cc(16.1, SUSTAIN, 127)
    p.cc(17.95, SUSTAIN, 0)
    p.chord(18, 4, ["C2", "C3", "E4", "G4", "C5", "E5"], 90)
    p.cc(18.1, SUSTAIN, 127)
    p.cc(22, SUSTAIN, 0)
    return p


def warm_walnut():
    # Rootless jazz voicings in the middle register, played quietly with the
    # soft pedal down for two bars and up for the rest.
    p = Phrase(84)
    changes = [
        ("D2", ["F3", "A3", "C4", "E4"], [("A4", 1.5), ("G4", 0.5), ("F4", 1), ("E4", 1)]),
        ("G1", ["F3", "B3", "E4"], [("F4", 1), ("A4", 1), ("G4", 2)]),
        ("C2", ["E3", "G3", "B3", "D4"], [("E4", 1.5), ("D4", 0.5), ("B3", 1), ("C4", 1)]),
        ("A1", ["G3", "C#4", "F4", "Bb4"], [("E4", 1), ("C#4", 1), ("A3", 2)]),
    ]
    p.cc(0, SOFT, 127)
    p.cc(0, SUSTAIN, 127)
    for bar, (bass, voicing, line) in enumerate(changes):
        start = 4 * bar
        if bar:
            p.change_pedal(start)
        p.note(start, 3.9, bass, 64)
        p.chord(start + 0.5, 3.3, voicing, 52)
        p.line(start, line, 66)
    p.cc(8, SOFT, 0)
    p.change_pedal(16)
    p.note(16, 3, "D2", 60)
    p.chord(16.1, 2.9, ["F3", "A3", "C4", "E4", "A4"], 54)
    p.cc(19, SUSTAIN, 0)
    return p


def felt_nocturne():
    # A quiet nocturne in F through the preset's felt; the modulation wheel
    # brings more felt in under the third bar and takes it out again before
    # the final chord. Past about 64 the extra felt chokes even held notes
    # within a beat, so the wheel stays below it.
    p = Phrase(66)
    left = [
        ["F2", "C3", "A3", "C4", "A3", "C3"],
        ["Bb1", "F2", "D3", "F3", "D3", "F2"],
        ["G1", "D2", "Bb2", "E3", "Bb2", "D2"],
        ["C2", "G2", "Bb2", "E3", "Bb2", "G2"],
    ]
    melody = [
        [("A4", 1.5), ("C5", 0.5), ("A4", 1)],
        [("Bb4", 1), ("D5", 1), ("C5", 1)],
        [("Bb4", 2), ("A4", 0.5), ("G4", 0.5)],
        [("G4", 1.5), ("A4", 0.5), ("Bb4", 1)],
    ]
    p.cc(0, SUSTAIN, 127)
    for bar, (arpeggio, line) in enumerate(zip(left, melody)):
        start = 3 * bar
        if bar:
            p.change_pedal(start)
        p.arpeggio(start, 0.5, arpeggio, 0.5, 44)
        p.line(start, line, 58)
    p.ramp_cc(6, 3, MODULATION, 0, 60)
    p.ramp_cc(9, 2.5, MODULATION, 60, 0)
    p.change_pedal(12)
    p.chord(12, 3, ["F2", "C3", "A3", "F4", "A4", "C5"], 52)
    p.cc(15, SUSTAIN, 0)
    return p


def open_strings():
    # Dampers up before anything is struck, so every undamped string answers
    # the staccato notes, the low octave and the rising arpeggio; the pedal
    # comes up at the end and the resonance stops with it.
    p = Phrase(72)
    p.cc(0, SUSTAIN, 127)
    for index, pitch in enumerate(["C6", "G5", "E6", "C7"]):
        p.note(0.5 + 0.75 * index, 0.12, pitch, 100)
    p.chord(4, 0.25, ["C1", "C2"], 116)
    p.arpeggio(6, 0.25, ["C2", "G2", "D3", "E3", "B3", "D4", "E4", "G4",
                         "B4", "D5", "E5", "G5", "B5", "D6", "E6"], 0.4, 84)
    p.chord(10.5, 0.3, ["E5", "G5", "B5", "D6"], 96)
    p.cc(13, SUSTAIN, 0)
    return p


PRESETS = [
    ("concert-grand", concert_grand), ("studio-grand", studio_grand),
    ("warm-walnut", warm_walnut), ("felt-nocturne", felt_nocturne),
    ("open-strings", open_strings),
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for index, (slug, build) in enumerate(PRESETS, 1):
        phrase = build()
        last = max(beat for beat, _, _ in phrase.events)
        seconds = last * 60 / phrase.bpm
        if not 9.5 <= seconds <= 16.5:
            raise SystemExit(f"{slug}: {seconds:.1f} s is outside the 10-16 s phrase length")
        path = args.output / f"{index:02d}-{slug}.mid"
        path.write_bytes(phrase.smf(slug))
        print(f"{path.name:28s} {seconds:5.1f} s")


if __name__ == "__main__":
    main()
