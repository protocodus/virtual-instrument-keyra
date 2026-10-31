#!/usr/bin/env python3
"""Write the committed per-preset demo phrases, Docs/audio/midi/<NN>-<slug>.mid.

One phrase for each of eight of the ten factory presets (README G3a), <NN>
its program number, each written for what that preset is for: Kakegawa
Grand plays a full-range romantic phrase with legato pedalling, Warm Walnut
jazz voicings with the soft pedal, Felt Nocturne a quiet nocturne whose felt
the modulation wheel brings in, and Open Strings struck notes with the
dampers raised so the undamped strings ring. Helsinki Upright plays a song
accompaniment of broken chords under a tune, and Pop Upright pumping chords
over octave roots with the pedal up. Hamamatsu Grand plays two voices without
the pedal, each line heard on its own, and Three Cities, every part a third
of each piano, a chorale whose chords sound the blend across the range.
Studio Grand and Felt Upright, voicings of the grand and the upright like
those beside them, have none. The .mid files are the committed sources the
demo renderer reads; this script only records how they were written. Re-run
it only to change a phrase on purpose, and commit the changed .mid files on
their own:

    python3 Tools/write_preset_midi.py           # write Docs/audio/midi
    python3 Tools/write_preset_midi.py --check   # the committed files match

Every file is format 0 on MIDI channel 1 at 480 PPQ, with a tempo and a track
name, and its last event falls 5.5-9.5 s in, so with the renderer's 2.5 s
release tail every demo is 8-12 s long (G3c). Notes stay inside
the piano's A0..C8: MIDI 12-14 are Keyra's pedal keyswitches.
"""
import argparse
from pathlib import Path
import re
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
MIDI_DIR = ROOT / "Docs/audio/midi"
BANK = ROOT / "Source/DSP/KeyraPresets.h"

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


def kakegawa_grand():
    # C minor, a bar of the tonic and one of the dominant in left-hand
    # arpeggios under a melody that grows from piano to forte, then a
    # full-range final chord.
    p = Phrase(72)
    bars = [
        ["C2", "G2", "C3", "Eb3", "G3", "Eb3", "C3", "G2"],
        ["G1", "D2", "G2", "B2", "F3", "D3", "B2", "G2"],
    ]
    melody = [
        [("G4", 2), ("Eb5", 1), ("D5", 1)],
        [("D5", 1), ("Eb5", 0.5), ("D5", 0.5), ("B4", 2)],
    ]
    p.cc(0, SUSTAIN, 127)
    for bar, (arpeggio, line) in enumerate(zip(bars, melody)):
        start = 4 * bar
        if bar:
            p.change_pedal(start)
        p.arpeggio(start, 0.5, arpeggio, 0.5, 60 + 16 * bar)
        p.line(start, line, 66 + 20 * bar)
    p.change_pedal(8)
    p.chord(8, 2.5, ["C1", "C2", "G2", "Eb3", "G4", "C5", "Eb5", "C6"], 104)
    p.cc(10.5, SUSTAIN, 0)
    return p


def warm_walnut():
    # A ii-V-I in rootless jazz voicings in the middle register, played
    # quietly with the soft pedal down for the first bar and up for the rest.
    p = Phrase(84)
    changes = [
        ("D2", ["F3", "A3", "C4", "E4"], [("A4", 1.5), ("G4", 0.5), ("F4", 1), ("E4", 1)]),
        ("G1", ["F3", "B3", "E4"], [("F4", 1), ("A4", 1), ("G4", 2)]),
        ("C2", ["E3", "G3", "B3", "D4"], [("E4", 1.5), ("D4", 0.5), ("B3", 1), ("C4", 1)]),
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
    p.cc(4, SOFT, 0)
    p.cc(12, SUSTAIN, 0)
    return p


def felt_nocturne():
    # A quiet nocturne in F through the preset's felt, tonic to dominant and
    # home; the modulation wheel brings more felt in under the second bar and
    # takes it out again before the final chord. Past about 64 the extra felt
    # chokes even held notes within a beat, so the wheel stays below it.
    p = Phrase(66)
    left = [
        ["F2", "C3", "A3", "C4", "A3", "C3"],
        ["C2", "G2", "Bb2", "E3", "Bb2", "G2"],
    ]
    melody = [
        [("A4", 1.5), ("C5", 0.5), ("A4", 1)],
        [("G4", 1.5), ("A4", 0.5), ("Bb4", 1)],
    ]
    p.cc(0, SUSTAIN, 127)
    for bar, (arpeggio, line) in enumerate(zip(left, melody)):
        start = 3 * bar
        if bar:
            p.change_pedal(start)
        p.arpeggio(start, 0.5, arpeggio, 0.5, 44)
        p.line(start, line, 58)
    p.ramp_cc(2.5, 1.5, MODULATION, 0, 60)
    p.ramp_cc(4, 1.6, MODULATION, 60, 0)
    p.change_pedal(6)
    p.chord(6, 3, ["F2", "C3", "A3", "F4", "A4", "C5"], 52)
    p.cc(9, SUSTAIN, 0)
    return p


def open_strings():
    # Dampers up before anything is struck, so every undamped string answers
    # the staccato notes, the low octave and the rising arpeggio; the pedal
    # comes up at the end and the resonance stops with it.
    p = Phrase(72)
    p.cc(0, SUSTAIN, 127)
    for index, pitch in enumerate(["C6", "G5", "E6", "C7"]):
        p.note(0.5 + 0.75 * index, 0.12, pitch, 100)
    p.chord(3.5, 0.25, ["C1", "C2"], 116)
    p.arpeggio(5, 0.25, ["C2", "G2", "D3", "E3", "B3", "D4", "E4", "G4",
                         "B4", "D5", "E5", "G5", "B5", "D6", "E6"], 0.4, 84)
    p.chord(9.25, 0.3, ["E5", "G5", "B5", "D6"], 96)
    p.cc(11, SUSTAIN, 0)
    return p


def helsinki_upright():
    # A song accompaniment in G: a bass note and broken chords in the left
    # hand under a plain tune, the pedal changed with each chord, home to a
    # spread G major.
    p = Phrase(92)
    bars = [
        ["G2", "D3", "B3", "D3", "G3", "D3", "B3", "D3"],
        ["E2", "B2", "G3", "B2", "E3", "B2", "G3", "B2"],
        ["C3", "G3", "E4", "G3", "D3", "A3", "F#4", "A3"],
    ]
    tune = [
        [("B4", 1), ("D5", 1), ("B4", 1), ("A4", 1)],
        [("G4", 1.5), ("B4", 0.5), ("E5", 1), ("D5", 1)],
        [("E5", 1), ("D5", 1), ("C5", 1), ("A4", 1)],
    ]
    p.cc(0, SUSTAIN, 127)
    for bar, (arpeggio, line) in enumerate(zip(bars, tune)):
        start = 4 * bar
        if bar:
            p.change_pedal(start)
        p.arpeggio(start, 0.5, arpeggio, 0.5, 62)
        p.line(start, line, 76)
    p.change_pedal(12)
    p.chord(12, 2, ["G1", "G2", "D3", "B3", "D4", "G4", "B4"], 84)
    p.cc(14, SUSTAIN, 0)
    return p


def pop_upright():
    # Pumping eighth-note chords over octave roots, pushed into each bar on
    # the last eighth before it, with the pedal up for a tight, percussive
    # upright; only the final chord rings.
    p = Phrase(116)
    progression = [
        (["C2", "C3"], ["E4", "G4", "C5"]),
        (["B1", "B2"], ["D4", "G4", "B4"]),
        (["A1", "A2"], ["C4", "E4", "A4"]),
        (["F1", "F2"], ["C4", "F4", "A4"]),
    ]
    for bar, (bass, chord) in enumerate(progression):
        start = 4 * bar
        p.chord(start, 1.4, bass, 92)
        p.chord(start + 1.5, 0.4, bass, 74)
        p.chord(start + 2, 1.4, bass, 86)
        for eighth in range(8):
            if bar < 3 and eighth == 7:
                continue
            p.chord(start + eighth / 2, 0.35, chord, 90 if eighth % 2 == 0 else 70)
        if bar < 3:
            p.chord(start + 3.5, 0.45, progression[bar + 1][1], 94)
    p.cc(16, SUSTAIN, 127)
    p.chord(16, 1.5, ["C2", "C3", "G3", "E4", "G4", "C5"], 96)
    p.cc(17.5, SUSTAIN, 0)
    return p


def hamamatsu_grand():
    # Two voices in D without the pedal: the right hand's figure answered by
    # the left a bar later and two octaves down, then a cadence home, so each
    # note's attack and decay is heard on its own.
    p = Phrase(100)
    p.line(0, [("D5", 0.5), ("E5", 0.5), ("F#5", 0.5), ("G5", 0.5), ("A5", 1), ("F#5", 1)], 76)
    p.line(0, [("D3", 1), ("A2", 1), ("D3", 1), ("F#3", 1)], 62)
    p.line(4, [("G5", 1), ("B5", 1), ("A5", 0.5), ("G5", 0.5), ("F#5", 0.5), ("E5", 0.5)], 80)
    p.line(4, [("D3", 0.5), ("E3", 0.5), ("F#3", 0.5), ("G3", 0.5), ("A3", 1), ("F#3", 1)], 68)
    p.line(8, [("F#5", 0.5), ("G5", 0.5), ("E5", 0.5), ("C#5", 0.5), ("D5", 2)], 78)
    p.line(8, [("G3", 1), ("A2", 1)], 70)
    p.chord(10, 2, ["D2", "D3"], 72)
    return p


def three_cities():
    # A chorale in B-flat, four voices moving to the dominant seventh and
    # home, the pedal changed with each chord and the last spread over five
    # octaves, so the blend is heard in chords from the bass to the treble.
    p = Phrase(80)
    chords = [
        ["Bb2", "F3", "D4", "Bb4"],
        ["G2", "G3", "D4", "Bb4"],
        ["C3", "G3", "Eb4", "C5"],
        ["F2", "A3", "Eb4", "C5"],
    ]
    p.cc(0, SUSTAIN, 127)
    for index, chord in enumerate(chords):
        if index:
            p.change_pedal(2 * index)
        p.chord(2 * index, 1.95, chord, 64 + 5 * index)
    p.change_pedal(8)
    p.chord(8, 3, ["Bb1", "Bb2", "F3", "D4", "F4", "Bb4", "D5"], 80)
    p.cc(11, SUSTAIN, 0)
    return p


# The demos, each by its preset's slug: at most eight, so the bank's other
# presets have none (README G3).
PRESETS = [
    ("kakegawa-grand", kakegawa_grand), ("warm-walnut", warm_walnut),
    ("felt-nocturne", felt_nocturne), ("open-strings", open_strings),
    ("helsinki-upright", helsinki_upright), ("pop-upright", pop_upright),
    ("hamamatsu-grand", hamamatsu_grand), ("three-cities", three_cities),
]


def files() -> dict[str, bytes]:
    presets = BANK.read_text(encoding="utf-8").split("factoryPresets", 1)[1].split("}};", 1)[0]
    bank = [re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
            for name in re.findall(r'\{ "([^"]+)",', presets)]
    slugs = [slug for slug, _ in PRESETS]
    if any(slug not in bank for slug in slugs) or len(slugs) > 8 or (len(bank) <= 8 and sorted(slugs) != sorted(bank)):
        sys.exit(f"phrases {slugs} are not at most eight of the bank {bank}, or all of a bank of eight or fewer")
    result = {}
    for slug, build in PRESETS:
        index = bank.index(slug) + 1
        phrase = build()
        last = max(beat for beat, _, _ in phrase.events)
        seconds = last * 60 / phrase.bpm
        if not 5.5 <= seconds <= 9.5:
            raise SystemExit(f"{slug}: {seconds:.1f} s is outside the 5.5-9.5 s phrase length")
        result[f"{index:02d}-{slug}.mid"] = phrase.smf(slug)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="fail unless the committed files match")
    args = parser.parse_args()
    expected = files()
    found = {path.name: path.read_bytes() for path in MIDI_DIR.glob("*.mid")}
    if args.check:
        stale = sorted(set(found) ^ set(expected) | {name for name in expected if found.get(name) != expected[name]})
        if stale:
            sys.exit(f"Docs/audio/midi differs from {Path(__file__).name} in: {', '.join(stale)}")
        print(f"{len(expected)} demo phrases match {Path(__file__).name}")
        return
    MIDI_DIR.mkdir(parents=True, exist_ok=True)
    for name in set(found) - set(expected):
        (MIDI_DIR / name).unlink()
    for name, data in expected.items():
        (MIDI_DIR / name).write_bytes(data)
        print(name)


if __name__ == "__main__":
    main()
