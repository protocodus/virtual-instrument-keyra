#!/usr/bin/env python3
"""Generate native Keyra Shop copy and thumbnail from the actual editor render.

Requires Pillow. Render the native editor first using keyra_editor_preview.
Native Keyra has one editor, so its second view shows real pedal travel; no
fictional rear panel is authored for the DAW front end.
"""
from pathlib import Path
import argparse
import math
import re
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / "Docs/screenshots"


def thumbnail():
    image = Image.new("RGB", (800, 800))
    pixels = image.load()
    for y in range(800):
        for x in range(800):
            green = math.exp(-((x - 140) ** 2 + (y - 210) ** 2) / 340 ** 2)
            gold = math.exp(-((x - 760) ** 2 + (y - 570) ** 2) / 310 ** 2)
            pixels[x, y] = tuple(round(base + green * a + gold * b)
                for base, a, b in zip((13, 14, 18), (8, 23, 20), (20, 14, 4)))
    image = image.convert("RGBA")
    editor = Image.open(SHOTS / "keyra.png").convert("RGBA")
    editor.thumbnail((728, 500), Image.Resampling.LANCZOS)
    shadow = Image.new("RGBA", image.size)
    ImageDraw.Draw(shadow).rounded_rectangle((30, 254, 770, 254 + editor.height + 14),
        radius=16, fill=(0, 0, 0, 190))
    image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(20)))
    image.alpha_composite(editor, ((800 - editor.width) // 2, 260))
    font_path = ROOT / "Assets/Fonts/LiberationSans-Bold.ttf"
    title = ImageFont.truetype(str(font_path), 96)
    small = ImageFont.truetype(str(font_path), 18)
    # The title sits over the actual editor, with a restrained dark halo.
    shade = Image.new("RGBA", image.size)
    ImageDraw.Draw(shade).text((400, 366), "KEYRA", font=title, anchor="mm",
        fill=(0, 0, 0, 180), stroke_width=6, stroke_fill=(0, 0, 0, 180))
    image.alpha_composite(shade.filter(ImageFilter.GaussianBlur(8)))
    draw = ImageDraw.Draw(image)
    draw.text((400, 366), "KEYRA", font=title, anchor="mm", fill=(244, 237, 217),
        stroke_width=1, stroke_fill=(37, 34, 28))
    draw.text((400, 173), "MODELLED GRAND PIANO", font=small, anchor="mm", fill=(219, 213, 194))
    logo = Image.open(ROOT / "Assets/Brand/Protocodus-logo.png").convert("RGBA")
    logo.thumbnail((92, 92), Image.Resampling.LANCZOS)
    image.alpha_composite(logo, ((800 - logo.width) // 2, 692))
    return image.convert("RGB")


def metadata(version):
    return f"""# Tagline

Keyra Modelled Grand Piano.

# Top features

* Sample-free, continuously voiced piano
* Three pedals with dedicated keyswitches
* Felt muting from the modulation wheel

# Intro

Keyra brings a continuously voiced, sample-free grand piano into a walnut-and-ivory instrument interface, with three visible brass pedals and direct control over the touch, resonance and stereo image.

# Product desc

Keyra generates its tone from tuned, dispersive modes with detuned unisons and separate prompt and late decay components. Numerical voicing comes from acoustic piano recordings; the sound engine does not play back recorded notes or impulse responses.

The soft, sostenuto and sustain pedals can be held on screen or played from MIDI. Dedicated momentary keyswitches sit below the piano range: C0 / MIDI 12 for soft, C#0 / MIDI 13 for sostenuto and D0 / MIDI 14 for sustain, using C4 = MIDI 60. Continuous sliders and standard CC67, CC66 and CC64 messages provide pedal depth, with visible pedal travel following the effective performance state.

The felt mute adds smooth damping even while keys remain held. Move the modulation wheel to bring it in during a phrase, or set its depth directly. Hammer brightness, sympathetic resonance, stereo width, concert tuning and output level shape the instrument around a performance.

Five authored presets offer concert, studio, warm, felt and open-string starting points. The DAW front end provides VST3 and CLAP plug-ins, an Audio Unit on macOS and a standalone instrument, sample-accurate MIDI scheduling, persistent panel parameters and a playable on-screen keyboard. Momentary pedal performances remain separate from the saved panel settings.

## Version history

### {version}

Native instrument with a real-time modal core, five presets, three visible pedals, momentary pedal keyswitches, continuous pedal depth and modulation-wheel felt muting, now as VST3, CLAP, Audio Unit and standalone builds.

# Images

![Native editor](../screenshots/keyra.png)

![Pedals held by MIDI keyswitches](../screenshots/keyra-editor-pedals-down.png)

![Product thumbnail](../screenshots/Keyra_Native_Thumbnail_800.png)
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    version = re.search(r"project\(Keyra VERSION ([0-9.]+)",
        (ROOT / "CMakeLists.txt").read_text()).group(1)
    copy = metadata(version)
    features = copy.split("# Top features\n\n")[1].split("\n\n# Intro")[0].splitlines()
    assert len(features) == 3 and all(len(line[2:]) <= 50 for line in features)
    for name in ("keyra.png", "keyra-editor-pedals-down.png"):
        assert (SHOTS / name).is_file(), f"Render {name} first"
    generated = thumbnail()
    destination = SHOTS / "Keyra_Native_Thumbnail_800.png"
    if args.check:
        assert (ROOT / "Docs/release/shop-copy.md").read_text() == copy, "Shop metadata is stale"
        assert Image.open(destination).convert("RGB").tobytes() == generated.tobytes(), "Shop thumbnail is stale"
    else:
        generated.save(destination)
        (ROOT / "Docs/release/shop-copy.md").write_text(copy)
    print(f"Native Shop metadata and thumbnail: {'checked' if args.check else 'generated'}")


if __name__ == "__main__":
    main()
