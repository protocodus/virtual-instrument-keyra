"""Read the numeric initializers emitted by the modal header formatter.

This deliberately restricted importer recovers exported measurements, not raw
fit statistics. A caller must roundtrip the result through the original header
formatter before using it as an immutable calibration baseline.
"""
from pathlib import Path
import ast
import re


def require(condition, message):
    if not condition:
        raise ValueError(message)


def array(value):
    require(isinstance(value, list) and len(value) == 1
            and isinstance(value[0], list), "expected double-braced array")
    return value[0]


def parse(path: Path):
    result = {}
    declarations = re.finditer(
        r"constexpr\s+(std::array<[^>]+>|float|int|Damper)\s+(\w+)\s*(.*?);",
        path.read_text(encoding='utf-8'), re.S)
    for declaration in declarations:
        kind, name, initializer = declaration.groups()
        initializer = re.sub(r"//[^\n]*", "", initializer).strip().lstrip("=")
        initializer = re.sub(r"(?<=[0-9.])f\b", "", initializer)
        require(not re.search(r"[^0-9eE+.,\-{}\s]", initializer),
                f"unsupported initializer for {name}")
        require(name not in result, f"duplicate initializer: {name}")
        value = ast.literal_eval(initializer.replace("{", "[").replace("}", "]"))
        result[name] = array(value) if kind.startswith("std::array") else value
    return result


def load(path: Path):
    values = parse(path)
    grid = values["layerVelocity"]
    layer_count = len(grid)
    require(layer_count == values["layers"], "velocity layer count differs")

    def lane(row):
        require(len(row) == 7, "invalid modal lane")
        rate, offset, left, real, imag, levels, phases = row
        levels, phases = array(levels), array(phases)
        require(len(levels) == len(phases) == layer_count, "lane layer count differs")
        return dict(rate=rate, offset_hz=offset, left=left,
                    right=complex(real, imag), level_db=levels, phase=phases)

    partials = [dict(order=p[0], cents=p[1], rise_seconds=p[2], rise_slope=p[3],
                     lanes=[lane(q) for q in array(p[4])]) for p in values["partials"]]
    extras = [dict(order=p[0], cents=p[1], lanes=[lane(p[2])])
              for p in values["extras"]]
    anchors = []
    first_partial = first_extra = 0
    for row in values["anchors"]:
        note, f1, stiffness, rise, start, count, extra_start, extra_count = row
        require(start == first_partial and extra_start == first_extra,
                "anchor ranges are not contiguous")
        require(count >= 0 and extra_count >= 0, "negative anchor range")
        anchors.append(dict(note=note, f1=f1, B=stiffness, onset_rise=array(rise),
                            partials=partials[start:start + count],
                            extras=extras[extra_start:extra_start + extra_count],
                            velocities=grid))
        first_partial += count
        first_extra += extra_count
    require(first_partial == len(partials) and first_extra == len(extras),
            "anchor ranges do not cover the exported modes")

    anchor_count = len(anchors)
    modes = len(values["bodyModes"])
    strings = len(values["haloStrings"])
    bands = len(values["noiseBands"])
    for name, width in (("knocks", modes), ("releaseKnocks", modes),
                        ("haloLevels", strings), ("noise", bands)):
        require(len(values[name]) == anchor_count * width,
                f"{name} anchor count differs")

    halo = dict(
        keys=list(range(89, 89 + strings)),
        cents=[v[0] for v in values["haloStrings"]],
        rates=[v[1] for v in values["haloStrings"]],
        prompts=[v[2] for v in values["haloStrings"]],
        pickups=[[v[3], complex(v[4], v[5])] for v in values["haloStrings"]],
        slope=values["haloSlopeDb"], rise=values["haloSlopeRiseDb"],
        prompt_rate=values["haloPromptRate"],
        levels=[values["haloLevels"][i * strings:(i + 1) * strings]
                for i in range(anchor_count)])
    body_keys = ("level_db", "slope_db", "phase", "slow_level_db", "slow_slope_db", "slow_phase")
    body = dict(
        hz=[v[0] for v in values["bodyModes"]],
        rates=[v[1] for v in values["bodyModes"]],
        slow_rates=[v[2] for v in values["bodyModes"]],
        shapes=[[complex(v[3]), complex(v[4], v[5])] for v in values["bodyModes"]],
        rise=values["bodyRise"],
        anchors=[[dict(zip(body_keys, v))
                  for v in values["knocks"][i * modes:(i + 1) * modes]]
                 for i in range(anchor_count)])

    def action_knock(row):
        return dict(level_db=row[0], phase=row[1])

    action = dict(
        rise=values["actionRise"], decay=values["actionDecay"],
        releases=[[action_knock(v)
                   for v in values["releaseKnocks"][i * modes:(i + 1) * modes]]
                  for i in range(anchor_count)])
    for source, destination in (("pedalDown", "pedal_down"), ("pedalUp", "pedal_up")):
        if source in values:
            action[destination] = [action_knock(v) for v in values[source]]

    noise = dict(hz=[v[0] for v in values["noiseBands"]],
                 coherence=[v[1] for v in values["noiseBands"]], anchors=[])
    for i in range(anchor_count):
        row = []
        for value in values["noise"][i * bands:(i + 1) * bands]:
            require(len(value) == 8, "invalid noise band")
            row.append(dict(
                decay_db_s=-value[0] * 8.685889638, balance_db=value[1],
                level_db=array(value[2]), slow_decay_db_s=-value[3] * 8.685889638,
                slow_db=array(value[4]), knock_decay_db_s=-value[5] * 8.685889638,
                knock_balance_db=value[6], knock_db=array(value[7])))
        noise["anchors"].append(row)
    open_strings = (dict(rate=values["openStringRate"], slope=values["openStringRateSlope"],
                         lift_db=values["openStringLiftDb"])
                    if "openStringRate" in values else None)
    damper = dict(law=values["damper"]) if "damper" in values else None
    return dict(grid=grid, layer_level=values["layerLevelDb"], anchors=anchors,
                halo=halo, body=body, noise=noise, action=action,
                damper=damper, open_strings=open_strings)
