#!/usr/bin/env python3
"""Import Standard MIDI Files into the standalone grand's seconds-based score.

Supports SMF 0/1, PPQ timing and merged tempo maps without dependencies.
All channels except channel 9 (GM percussion) are selected by default; repeat
--channel 0..15 to choose channels explicitly. Multiple tracks/channels share
one 88-key piano: simultaneous duplicate strikes merge at maximum velocity,
later note-ons retrigger, and reference-counted key releases wait for every
overlapping depression. Continuous CC64 values combine by maximum channel
value. Program/bank changes, other controllers, SysEx and unneeded metadata
are ignored. Notes beyond A0..C8 are counted and skipped.

Usage: python3 tools/midi_to_events.py input.mid output.events
       python3 tools/midi_to_events.py --self-test
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import struct


class MidiError(ValueError):
    """The input cannot be interpreted as a supported Standard MIDI File."""


class Reader:
    def __init__(self, data, label):
        self.data, self.pos, self.label = data, 0, label

    def take(self, count):
        if count < 0 or self.pos + count > len(self.data):
            raise MidiError(f"{self.label}: truncated data at byte {self.pos}")
        result = self.data[self.pos:self.pos + count]
        self.pos += count
        return result

    def byte(self):
        return self.take(1)[0]

    def vlq(self):
        value = 0
        for _ in range(4):
            byte = self.byte()
            value = (value << 7) | (byte & 127)
            if byte < 128:
                return value
        raise MidiError(f"{self.label}: variable-length quantity exceeds four bytes")


def parse_track(data, track):
    r = Reader(data, f"track {track}")
    tick, running, sequence = 0, None, 0
    events = []
    while r.pos < len(data):
        tick += r.vlq()
        status = r.byte()
        first_data = None
        if status < 128:
            if running is None:
                raise MidiError(f"track {track}: running status without a channel status")
            first_data, status = status, running
        elif status < 240:
            running = status
        else:
            running = None  # Meta and SysEx interrupt channel running status.
        order = (tick, track, sequence)
        sequence += 1
        if status == 255:
            kind = r.byte()
            if kind >= 128:
                raise MidiError(f"track {track}: invalid meta-event type")
            payload = r.take(r.vlq())
            if kind == 0x51:
                if len(payload) != 3 or int.from_bytes(payload, "big") == 0:
                    raise MidiError(f"track {track}: tempo must be three nonzero-value bytes")
                events.append((*order, "tempo", -1, 0, int.from_bytes(payload, "big")))
            elif kind == 0x2F:
                if payload or r.pos != len(data):
                    raise MidiError(f"track {track}: end-of-track must be empty and final")
                return events, tick
        elif status in (0xF0, 0xF7):
            r.take(r.vlq())
        elif 0x80 <= status <= 0xEF:
            op, channel = status & 0xF0, status & 15
            count = 1 if op in (0xC0, 0xD0) else 2
            payload = ([first_data] if first_data is not None else [])
            payload.extend(r.take(count - len(payload)))
            if any(value >= 128 for value in payload):
                raise MidiError(f"track {track}: channel data contains a status byte")
            if op in (0x80, 0x90):
                pitch, velocity = payload
                kind = "on" if op == 0x90 and velocity else "off"
                events.append((*order, kind, channel, pitch, velocity if kind == "on" else 0))
            elif op == 0xB0 and payload[0] == 64:
                events.append((*order, "pedal", channel, 0, payload[1]))
        else:
            raise MidiError(f"track {track}: unsupported SMF status 0x{status:02X}")
    raise MidiError(f"track {track}: missing end-of-track event")


def parse_midi(data):
    r = Reader(data, "MIDI file")
    if r.take(4) != b"MThd":
        raise MidiError("not an SMF file: missing MThd header")
    header = r.take(int.from_bytes(r.take(4), "big"))
    if len(header) < 6:
        raise MidiError("SMF header is shorter than six bytes")
    fmt, tracks, division = struct.unpack(">HHH", header[:6])
    if fmt not in (0, 1):
        raise MidiError(f"SMF format {fmt} is unsupported; use synchronous format 0 or 1")
    if tracks == 0 or (fmt == 0 and tracks != 1):
        raise MidiError("SMF track count is inconsistent with its format")
    if division & 0x8000:
        raise MidiError("SMPTE timing is unsupported; export a PPQ-timed MIDI file")
    if division == 0:
        raise MidiError("PPQ time division must be positive")
    events, track_ends, found = [], [], 0
    while r.pos < len(data):
        kind = r.take(4)
        payload = r.take(int.from_bytes(r.take(4), "big"))
        if kind != b"MTrk":
            continue  # Standard MIDI readers may ignore unfamiliar chunk types.
        if found >= tracks:
            raise MidiError("more MTrk chunks than the header declares")
        track_events, end = parse_track(payload, found)
        events.extend(track_events)
        track_ends.append(end)
        found += 1
    if found != tracks:
        raise MidiError(f"header declares {tracks} tracks, but only {found} were found")
    # A sentinel preserves the declared duration, including silent final bars.
    events.append((max(track_ends), tracks, 0, "end", -1, 0, 0))
    return sorted(events), {"format":fmt, "tracks":tracks, "ppq":division}


def convert(data, channels=None):
    raw, stats = parse_midi(data)
    selected = set(range(16)) - {9} if channels is None else set(channels)
    if not selected or any(not isinstance(c, int) or not 0 <= c <= 15 for c in selected):
        raise MidiError("selected channels must be integers from 0 to 15")
    stats.update({"selected_channels":sorted(selected), "input_note_ons":0,
                  "output_note_ons":0, "merged_simultaneous_strikes":0,
                  "unmatched_note_offs_ignored":0, "out_of_range_note_ons_skipped":0,
                  "cleanup_note_offs":0, "tempo_events":0})
    depressed = defaultdict(int)  # (channel, pitch) -> source depressions
    totals = defaultdict(int)  # pitch -> depressions across selected channels
    pedals = {channel:0 for channel in selected}
    events, simultaneous_ons = [], {}
    previous_tick, tempo, seconds = 0, 500000, 0.0
    merged_pedal = 0
    for tick, track, sequence, kind, channel, pitch, value in raw:
        if tick != previous_tick:
            seconds += (tick - previous_tick) * tempo / (stats["ppq"] * 1_000_000)
            previous_tick = tick
            simultaneous_ons.clear()
        if kind == "tempo":
            tempo = value
            stats["tempo_events"] += 1
            continue
        if channel not in selected:
            continue
        if kind in ("on", "off"):
            if kind == "on":
                stats["input_note_ons"] += 1
            if not 21 <= pitch <= 108:
                if kind == "on":
                    stats["out_of_range_note_ons_skipped"] += 1
                continue
            key = channel, pitch
            if kind == "on":
                depressed[key] += 1
                totals[pitch] += 1
                if pitch in simultaneous_ons:
                    # Two tracks/channels at the same tick cannot independently
                    # strike the same physical hammer. Retain the louder strike.
                    index = simultaneous_ons[pitch]
                    events[index][3] = max(events[index][3], value)
                    stats["merged_simultaneous_strikes"] += 1
                else:
                    simultaneous_ons[pitch] = len(events)
                    events.append([seconds, "on", pitch, value])
                    stats["output_note_ons"] += 1
            elif depressed[key] > 0:
                depressed[key] -= 1
                totals[pitch] -= 1
                if totals[pitch] == 0:
                    events.append([seconds, "off", pitch, 0])
                    # An off followed by another on at this tick is a retrigger,
                    # rather than a duplicate of a strike already released.
                    simultaneous_ons.pop(pitch, None)
            else:
                stats["unmatched_note_offs_ignored"] += 1
        elif kind == "pedal":
            pedals[channel] = value
            new_pedal = max(pedals.values())
            if new_pedal != merged_pedal:
                events.append([seconds, "pedal", 0, new_pedal / 127])
                merged_pedal = new_pedal
    cleanup = seconds + 0.1
    before_cleanup = len(events)
    for pitch, count in sorted(totals.items()):
        if count:
            events.append([cleanup, "off", pitch, 0])
            stats["cleanup_note_offs"] += 1
    if merged_pedal:
        events.append([cleanup, "pedal", 0, 0.0])
    if len(events) == before_cleanup and (not events or events[-1][0] < seconds):
        # The native renderer infers score length from its last event. Preserve
        # silent closing bars without changing the shared damper state.
        events.append([seconds, "pedal", 0, merged_pedal / 127])
    stats["midi_duration_seconds"] = seconds
    stats["event_duration_seconds"] = events[-1][0] if events else 0.0
    stats["output_events"] = len(events)
    return events, stats


def format_events(events, source):
    lines = [f"# Imported MIDI: {source}",
             "# seconds kind note value; one shared grand; channels use maximum CC64."]
    for seconds, kind, pitch, value in events:
        text = f"{value:.6f}" if kind == "pedal" else str(int(value))
        lines.append(f"{seconds:.9f} {kind} {pitch} {text}")
    return "\n".join(lines) + "\n"


def self_test():
    def vlq(value):
        out = [value & 127]
        while value >> 7:
            value >>= 7
            out.insert(0, (value & 127) | 128)
        return bytes(out)

    def track(messages):
        data = b"".join(vlq(delta) + message for delta, message in messages)
        return b"MTrk" + struct.pack(">I", len(data)) + data

    def midi(tracks, fmt=1, ppq=480):
        return b"MThd\x00\x00\x00\x06" + struct.pack(">HHH", fmt, len(tracks), ppq) + b"".join(tracks)

    end = b"\xff\x2f\x00"
    tempo = track([(0,b"\xff\x51\x03\x07\xa1\x20"), (480,b"\xff\x51\x03\x0f\x42\x40"), (960,end)])
    a = track([(0,b"\x90\x3c\x40"), (240,b"\x3e\x50"), # running status
               (240,b"\x80\x3c\x00"), (0,b"\x90\x3e\x00"), # on-zero -> off
               (0,b"\xb0\x40\x40"), (0,b"\xf0\x03\x01\x02\xf7"),
               (0,b"\xff\x7f\x02\x01\x02"), (480,b"\x90\x43\x60"), (480,end)])
    b = track([(0,b"\x91\x3c\x64"), (0,b"\xb1\x40\x60"),
               (720,b"\x81\x3c\x00"), (0,b"\xb1\x40\x00"), (720,end)])
    percussion = track([(0,b"\x99\x24\x7f"), (10,b"\x89\x24\x00"), (1430,end)])
    ev, report = convert(midi([tempo,a,b,percussion]))
    assert [e for e in ev if e[1] == "on"] == [[0.0,"on",60,100],[.25,"on",62,80],[1.5,"on",67,96]]
    assert [.5,"off",62,0] in ev and [1.0,"off",60,0] in ev
    assert [2.6,"off",67,0] in ev and [2.6,"pedal",0,0.0] in ev
    assert report["merged_simultaneous_strikes"] == 1
    assert [1.0,"pedal",0,64/127] in ev  # Other channel still holds partial pedal.
    only_a, _ = convert(midi([tempo,a,b]), {0})
    assert [.5,"off",60,0] in only_a
    only_drums, _ = convert(midi([percussion], fmt=0), {9})
    assert [0.0,"on",36,127] in only_drums
    # A later overlapping strike retriggers, but an earlier source off cannot
    # damp it while another source still depresses the same pitch.
    overlap = track([(0,b"\x90\x3c\x40"),(120,b"\x90\x3c\x50"),
                     (120,b"\x80\x3c\x00"),(120,b"\x80\x3c\x00"),(0,end)])
    overlap_events, _ = convert(midi([overlap], fmt=0))
    assert overlap_events == [[0.0,"on",60,64],[.125,"on",60,80],[.375,"off",60,0]]
    trailing_rest = track([(0,b"\x90\x3c\x40"),(120,b"\x80\x3c\x00"),(1320,end)])
    rest_events, rest_info = convert(midi([trailing_rest], fmt=0))
    assert rest_events == [[0.0,"on",60,64],[.125,"off",60,0],[1.5,"pedal",0,0.0]]
    assert rest_info["event_duration_seconds"] == rest_info["midi_duration_seconds"] == 1.5
    invalid = [b"bad", midi([a],fmt=2), midi([a],ppq=0xE728), midi([a],ppq=0),
               midi([track([(0,b"\x3c\x40"),(0,end)])],fmt=0),
               midi([track([(0,b"\x90\x3c\x40"),(0,b"\xff\x01\x00"),(0,b"\x3e\x40"),(0,end)])],fmt=0),
               midi([track([(0,b"\x90\x3c\xff"),(0,end)])],fmt=0),
               midi([track([(0,b"\xff\x51\x03\x00\x00\x00"),(0,end)])],fmt=0),
               midi([a])[:-1]]
    for data in invalid:
        try:
            convert(data)
        except MidiError:
            pass
        else:
            raise AssertionError("malformed/unsupported MIDI was accepted")
    roundtrips = []
    root = Path(__file__).resolve().parents[1]
    for path in sorted((root / "scores").glob("*.mid")):
        original_path = path.with_suffix(".events")
        if not original_path.exists():
            continue
        expected = []
        for line in original_path.read_text().splitlines():
            if not line or line.startswith("#"):
                continue
            t, kind, pitch, value = line.split()
            if kind in ("on", "off"):
                expected.append([float(t),kind,int(pitch),int(value)])
        actual, info = convert(path.read_bytes())
        actual = [e for e in actual if e[1] in ("on", "off")]
        assert len(actual) == len(expected), path
        error = 0.0
        for left, right in zip(actual, expected):
            assert left[1:] == right[1:], (path,left,right)
            error = max(error, abs(left[0] - right[0]))
        assert error <= .5 / 960 + 1e-6, (path,error)
        roundtrips.append({"file":path.name,"paired_note_events":len(actual),"maximum_timing_error_seconds":error})
    return {"passed":True, "coverage":["SMF 0/1", "cross-track tempo map", "running status",
            "zero-velocity note off", "SysEx/meta skipping", "continuous merged pedal",
            "channel selection and percussion exclusion", "simultaneous duplicates",
            "overlapping-note reference counts and retriggers", "hanging-note cleanup",
            "declared end-of-track duration with trailing rests",
            "malformed inputs, format 2 and SMPTE rejection"], "malformed_cases":len(invalid),
            "score_roundtrips":roundtrips}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", nargs="?", type=Path)
    parser.add_argument("output", nargs="?", type=Path)
    parser.add_argument("--channel", type=int, choices=range(16), action="append", help="zero-based channel; may be repeated")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--report", type=Path, help="write JSON import statistics or self-test report")
    args = parser.parse_args()
    try:
        if args.self_test:
            if args.input or args.output:
                parser.error("--self-test does not take input/output paths")
            report = self_test()
        else:
            if not args.input or not args.output:
                parser.error("input.mid and output.events are required")
            events, report = convert(args.input.read_bytes(), args.channel)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(format_events(events, args.input.name))
            report.update({"input":str(args.input), "output":str(args.output)})
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
    except (MidiError, OSError) as exc:
        parser.exit(2, f"MIDI import failed: {exc}\n")


if __name__ == "__main__":
    main()
