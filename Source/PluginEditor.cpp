#include "PluginEditor.h"
#include <cmath>
#include <vector>

namespace {
const juce::Colour ink(0xff302c26), ivory(0xffeee8dc), brass(0xffa48448), muted(0xff7c766b), footer(0xffc6ad89);
constexpr size_t tuningIndex = 2, sustainIndex = 4, softIndex = 6, mechanicsIndex = 7;
constexpr std::array<const char*, 23> ids {{ "gain", "width", "tuning", "mute", "sustain", "sostenuto", "soft", "mechanics",
    "hammer", "age", "detune", "stretch", "dynamics", "lid", "soundboard", "sympathetic", "duplex",
    "micClose", "micXY", "micLive", "micDistant", "room", "felt" }};
constexpr std::array<const char*, 23> captions {{ "OUTPUT", "WIDTH", "A4 TUNING", "FELT MUTE", "SUSTAIN", "SOSTENUTO", "SOFT", "MECHANICS",
    "HAMMER", "STRING AGE", "DETUNE", "STRETCH", "DYNAMICS", "LID", "SOUNDBOARD", "SYMPATHETIC", "DUPLEX",
    "CLOSE", "XY", "LIVE", "DISTANT", "ROOM", "PRACTICE FELT" }};
constexpr std::array<const char*, 23> hints {{
    "Output level.",
    "The stereo image: 75% as the microphone pairs hear it, 0% mono.",
    "A4 in Hz.",
    "Felt laid on the sounding strings, also on the modulation wheel (CC1). Works while keys are held.",
    "Damper pedal (CC64). Intermediate positions allow half pedalling.",
    "Sostenuto (CC66). Captures only the notes held when the pedal crosses its latch point.",
    "Soft pedal (CC67): una corda on a grand, a shorter blow on the upright.",
    "How loud the action plays: the keys landing and coming back, the dampers falling and "
    "the sustain pedal. 0% silences the action; 40% is the natural, quieter default. "
    "The upper range brings the mechanics forward. Double-click to reset.",
    "The hammers' felt, from soft and worn-in to hard and bright. Applies from the next note.",
    "The strings' age: old strings lose their upper partials' sustain and beat against themselves. "
    "Applies from the next note.",
    "How far apart the strings of each unison are tuned, from pure to a bar piano.",
    "The tuner's stretch: 0% equal temperament, 100% octaves tuned to the strings' own partials, 200% twice that.",
    "How far apart the softest and the hardest blow are. Applies from the next note.",
    "The lid: closed, on the short stick at 50%, open.",
    "How long the soundboard rings, from heavily damped to lively.",
    "How strongly the strings whose dampers are off answer the ones struck.",
    "How strongly the lengths of string behind the bridge ring with the treble.",
    "A spaced pair inside the piano, over the hammers: the pop sound. Behind an upright's soundboard.",
    "A coincident pair at the open lid, a metre off.",
    "A spaced pair in the room at 2.5 m; on the upright, the player's side.",
    "A wide pair across the room.",
    "The room's reverberation in the pairs that hear it.",
    "A practice felt between the hammers and the strings. Applies from the next note."
}};
// Each view's knobs, left to right.
constexpr std::array<const char*, 3> viewHints {{
    "The hammers and strings: hardness, age, unison detune, stretch, dynamics, practice felt and felt mute.",
    "The case: lid, soundboard, sympathetic and duplex resonance, mechanics and output.",
    "Where the piano is heard from: four microphone pairs, the room and the stereo width."
}};
const std::array<std::vector<size_t>, 3> views {{ { 8, 9, 10, 11, 12, 22, 3 }, { 13, 14, 15, 16, 7, 0 }, { 17, 18, 19, 20, 21, 1 } }};
void text(juce::Graphics& g, const juce::String& value, juce::Rectangle<int> bounds,
    float size, juce::Colour colour, int justification = juce::Justification::centredLeft, bool bold = false)
{
    g.setColour(colour);
    g.setFont(juce::Font(juce::FontOptions(size, bold ? juce::Font::bold : juce::Font::plain)));
    g.drawText(value, bounds, justification, false);
}
}

KeyraLookAndFeel::KeyraLookAndFeel()
{
    setColour(juce::Slider::textBoxTextColourId, ink);
    setColour(juce::Slider::textBoxOutlineColourId, juce::Colours::transparentBlack);
    setColour(juce::Slider::textBoxBackgroundColourId, juce::Colours::transparentBlack);
    setColour(juce::Slider::textBoxHighlightColourId, brass.withAlpha(.25f));
    setColour(juce::TextEditor::highlightColourId, brass.withAlpha(.25f));
    setColour(juce::TextEditor::textColourId, ink);
}

void KeyraLookAndFeel::drawRotarySlider(juce::Graphics& g, int x, int y, int width, int height,
    float position, float start, float end, juce::Slider& slider)
{
    const auto radius = juce::jmin(width, height) * .38f;
    const auto cx = x + width * .5f, cy = y + height * .5f;
    const auto bounds = juce::Rectangle<float>(cx - radius, cy - radius, radius * 2, radius * 2);
    juce::Path ring;
    ring.addCentredArc(cx, cy, radius + 7, radius + 7, 0, start, end, true);
    g.setColour(ink.withAlpha(.16f));
    g.strokePath(ring, juce::PathStrokeType(2));
    // A two-sided knob's arc runs from its centre.
    const auto from = slider.getMinimum() < 0 ? (start + end) * .5f : start, to = start + position * (end - start);
    juce::Path active;
    active.addCentredArc(cx, cy, radius + 7, radius + 7, 0, juce::jmin(from, to), juce::jmax(from, to), true);
    g.setColour(brass);
    g.strokePath(active, juce::PathStrokeType(2));
    g.setColour(juce::Colours::black.withAlpha(.12f));
    g.fillEllipse(bounds.translated(0, 3).expanded(2));
    g.setGradientFill(juce::ColourGradient(juce::Colour(0xfffefcf5), cx - radius, cy - radius,
        juce::Colour(0xffc6bdac), cx + radius, cy + radius, false));
    g.fillEllipse(bounds);
    g.setColour(juce::Colour(0xffb6aa95));
    g.drawEllipse(bounds, 1);
    g.setColour(juce::Colours::white.withAlpha(.7f));
    g.drawEllipse(bounds.reduced(2), 1);
    const auto angle = start + position * (end - start);
    g.setColour(ink);
    g.drawLine(cx + std::sin(angle) * radius * .47f, cy - std::cos(angle) * radius * .47f,
        cx + std::sin(angle) * radius * .83f, cy - std::cos(angle) * radius * .83f, 2.4f);
}

void KeyraLookAndFeel::drawLinearSlider(juce::Graphics& g, int x, int y, int width, int height,
    float position, float, float, juce::Slider::SliderStyle, juce::Slider&)
{
    const auto cy = y + height * .5f;
    g.setColour(ink.withAlpha(.19f));
    g.fillRoundedRectangle(static_cast<float>(x), cy - 2, static_cast<float>(width), 4, 2);
    g.setColour(brass);
    g.fillRoundedRectangle(static_cast<float>(x), cy - 2, juce::jmax(0.0f, position - x), 4, 2);
    g.setColour(juce::Colours::black.withAlpha(.12f));
    g.fillRoundedRectangle(position - 7, cy - 8, 16, 19, 3);
    g.setGradientFill(juce::ColourGradient(juce::Colour(0xfffbf7eb), position - 7, cy - 10,
        juce::Colour(0xffc9bea7), position + 7, cy + 8, false));
    g.fillRoundedRectangle(position - 7, cy - 10, 14, 18, 3);
    g.setColour(brass.darker());
    g.drawRoundedRectangle(position - 7, cy - 10, 14, 18, 3, 1);
}

KeyraTab::KeyraTab(const juce::String& name) : Button(name)
{
    setClickingTogglesState(true);
    setRadioGroupId(1);
    setMouseCursor(juce::MouseCursor::PointingHandCursor);
}

void KeyraTab::paintButton(juce::Graphics& g, bool highlighted, bool)
{
    const auto on = getToggleState();
    ::text(g, getName(), getLocalBounds().withTrimmedBottom(4), 11, on ? ink : highlighted ? brass : muted,
        juce::Justification::centred, true);
    if (on) {
        g.setColour(brass);
        g.fillRoundedRectangle(getWidth() * .5f - 16, getHeight() - 3.0f, 32, 2, 1);
    }
}

KeyraPedal::KeyraPedal() : Button("Piano pedal")
{
    setMouseCursor(juce::MouseCursor::PointingHandCursor);
    onStateChange = [this] {
        const auto pressed = isDown();
        if (pressed == held) return;
        held = pressed;
        if (onHold) onHold(pressed);
        repaint();
    };
}

void KeyraPedal::setTravel(float value)
{
    value = juce::jlimit(0.0f, 1.0f, value);
    if (std::abs(travel - value) < .001f) return;
    travel = value;
    repaint();
}

void KeyraPedal::paintButton(juce::Graphics& g, bool highlighted, bool down)
{
    const auto amount = juce::jmax(travel, down ? 1.0f : 0.0f);
    const auto cx = getWidth() * .5f;
    g.setColour(juce::Colour(0xff574a37));
    g.fillRoundedRectangle(cx - 12, 5, 24, 11, 4);
    g.setGradientFill(juce::ColourGradient(juce::Colour(0xffbdad88), cx - 11, 5,
        juce::Colour(0xff665336), cx + 11, 15, false));
    g.fillRoundedRectangle(cx - 10, 6, 20, 9, 3);
    // An elongated brass foot plate and narrow pivot stem, seen from above.
    // Compression lowers the toe toward the deck while the hinge stays put.
    const auto toe = 70.0f - 8.0f * amount;
    juce::Path plate;
    plate.startNewSubPath(cx - 7, 10);
    plate.lineTo(cx + 7, 10);
    plate.cubicTo(cx + 7, 27, cx + 24, 35, cx + 24, toe - 11);
    plate.cubicTo(cx + 24, toe + 3, cx - 24, toe + 3, cx - 24, toe - 11);
    plate.cubicTo(cx - 24, 35, cx - 7, 27, cx - 7, 10);
    plate.closeSubPath();
    g.setColour(juce::Colours::black.withAlpha(.14f - amount * .05f));
    g.fillPath(plate, juce::AffineTransform::translation(1.5f, 4.0f - 2.0f * amount));
    g.setColour(juce::Colour(0xff805c23));
    g.fillPath(plate, juce::AffineTransform::translation(0, 2));
    juce::ColourGradient metal(juce::Colour(0xffead395), cx - 21, 25,
        juce::Colour(0xff98702d), cx + 24, toe, false);
    metal.addColour(.32, juce::Colour(highlighted ? 0xfff5e1a7 : 0xffdec181));
    metal.addColour(.58, juce::Colour(0xffc4a15a));
    g.setGradientFill(metal);
    g.fillPath(plate);
    g.setColour(juce::Colour(0xff89652e));
    g.strokePath(plate, juce::PathStrokeType(1));
    juce::Path shine;
    shine.startNewSubPath(cx - 5, 15);
    shine.cubicTo(cx - 5, 32, cx - 20, 39, cx - 20, toe - 11);
    g.setColour(juce::Colour(0xfffff0c5).withAlpha(.8f));
    g.strokePath(shine, juce::PathStrokeType(1));
    g.setColour(juce::Colour(0xfffcf0cb).withAlpha(.5f));
    g.drawLine(cx - 15, toe - 6, cx + 13, toe - 6, 1);
    // Travel indicator is tied to the effective engine pedal state, including
    // external CCs and keyswitches, not just the local mouse button.
    g.setColour(amount > .01f ? juce::Colour(0xff597b62) : ink.withAlpha(.18f));
    g.fillEllipse(cx - 2, 77, 4, 4);
}

KeyraAudioProcessorEditor::KeyraAudioProcessorEditor(KeyraAudioProcessor& p)
    : AudioProcessorEditor(p), processor(p)
{
    setLookAndFeel(&look);
    for (int i = 0; i < processor.getNumPrograms(); ++i) program.addItem(processor.getProgramName(i), i + 1);
    program.setSelectedId(processor.getCurrentProgram() + 1, juce::dontSendNotification);
    program.setColour(juce::ComboBox::backgroundColourId, ivory.withAlpha(.55f));
    program.setColour(juce::ComboBox::textColourId, ink);
    program.setColour(juce::ComboBox::outlineColourId, brass.withAlpha(.35f));
    program.setColour(juce::ComboBox::arrowColourId, brass);
    program.onChange = [this] { processor.setCurrentProgram(program.getSelectedId() - 1); };
    program.setTooltip("A factory piano: a body, how its hammers and strings are kept and where it is heard from. "
                       "Output, tuning, mechanics, felt mute and the pedals stay.");
    addAndMakeVisible(program);
    // The attachment selects item index + 1 of the choice, so the items go in first.
    for (size_t i = 0; i < keyra::bodyNames.size(); ++i) body.addItem(keyra::bodyNames[i], static_cast<int>(i) + 1);
    body.setColour(juce::ComboBox::backgroundColourId, ivory.withAlpha(.55f));
    body.setColour(juce::ComboBox::textColourId, ink);
    body.setColour(juce::ComboBox::outlineColourId, brass.withAlpha(.35f));
    body.setColour(juce::ComboBox::arrowColourId, brass);
    body.setTooltip("The piano: its string scale, hammers, soundboard and case. A physical model of each kind of "
                    "piano at a typical size, not one maker's instrument.");
    addAndMakeVisible(body);
    bodyAttachment = std::make_unique<juce::AudioProcessorValueTreeState::ComboBoxAttachment>(processor.parameters, "body", body);
    for (size_t i = 0; i < controls.size(); ++i) {
        auto& slider = controls[i];
        slider.setName(captions[i]);
        slider.setSliderStyle(i >= sustainIndex && i <= softIndex ? juce::Slider::LinearHorizontal : juce::Slider::RotaryHorizontalVerticalDrag);
        slider.setTextBoxStyle(juce::Slider::TextBoxBelow, false, 92, 22);
        slider.setRotaryParameters(juce::MathConstants<float>::pi * 1.23f,
            juce::MathConstants<float>::pi * 2.77f, true);
        addAndMakeVisible(slider);
        attachments[i] = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment>(processor.parameters, ids[i], slider);
        // Attachments install their own generic float formatter. Apply the
        // product's units afterwards, and rebuild the editable label after
        // the slider inherits this editor's light-surface look and feel.
        slider.setColour(juce::Slider::textBoxTextColourId, ink);
        slider.setColour(juce::Slider::textBoxBackgroundColourId, juce::Colours::transparentBlack);
        slider.setColour(juce::Slider::textBoxOutlineColourId, juce::Colours::transparentBlack);
        slider.setNumDecimalPlacesToDisplay(i == tuningIndex ? 1 : 0);
        slider.setTooltip(hints[i]);
        if (i == mechanicsIndex) {
            // The attachment and host retain physical gain 0..2. Change only
            // knob travel and its readout, so old automation plays unchanged.
            // Install after SliderAttachment: its constructor sets the range.
            slider.setNormalisableRange(juce::NormalisableRange<double>(0.0, keyra::maximumMechanicsGain,
                [](double, double, double position) { return keyra::mechanicsGainFromPosition(static_cast<float>(position)); },
                [](double, double, double gain) { return keyra::mechanicsPositionFromGain(static_cast<float>(gain)); }));
            slider.textFromValueFunction = [](double gain) {
                return juce::String(juce::roundToInt(100 * keyra::mechanicsPositionFromGain(static_cast<float>(gain)))) + "%";
            };
            slider.valueFromTextFunction = [](const juce::String& value) {
                return keyra::mechanicsGainFromPosition(static_cast<float>(value.getDoubleValue() * .01));
            };
            slider.setDoubleClickReturnValue(true, keyra::defaultMechanicsGain);
        } else if (i != tuningIndex) {
            slider.textFromValueFunction = [](double value) { return juce::String(juce::roundToInt(value * 100)) + "%"; };
            slider.valueFromTextFunction = [](const juce::String& value) { return value.getDoubleValue() * .01; };
        } else {
            slider.textFromValueFunction = [](double value) { return juce::String(value, 1) + " Hz"; };
            slider.valueFromTextFunction = [](const juce::String& value) { return value.getDoubleValue(); };
        }
        slider.updateText();
    }
    controls[tuningIndex].setSliderStyle(juce::Slider::IncDecButtons);
    controls[tuningIndex].setTextBoxStyle(juce::Slider::TextBoxLeft, false, 84, 28);
    controls[tuningIndex].setIncDecButtonsMode(juce::Slider::incDecButtonsDraggable_Vertical);
    for (size_t i = 0; i < tabs.size(); ++i) {
        tabs[i].setTooltip(viewHints[i]);
        tabs[i].onClick = [this, i] { showView(static_cast<int>(i)); };
        addAndMakeVisible(tabs[i]);
    }
    showView(processor.editorView);
    constexpr std::array<const char*, 3> pedalNames {{ "Soft pedal", "Sostenuto pedal", "Sustain pedal" }};
    constexpr std::array<const char*, 3> pedalHints {{
        "Hold to press the soft pedal. Keyswitch C0 / MIDI 12; controller CC67. Slider sets continuous pedal depth.",
        "Hold to press sostenuto and capture held notes. Keyswitch C#0 / MIDI 13; controller CC66.",
        "Hold to lift the dampers. Keyswitch D0 / MIDI 14; controller CC64. Slider allows half pedalling."
    }};
    const std::array<float, 3> initialTravel {{ processor.softLevel.load(std::memory_order_relaxed),
        processor.sostenutoLevel.load(std::memory_order_relaxed), processor.sustainLevel.load(std::memory_order_relaxed) }};
    for (size_t i = 0; i < pedals.size(); ++i) {
        auto& pedal = pedals[i];
        pedal.setName(pedalNames[i]);
        pedal.setTooltip(pedalHints[i]);
        pedal.setTravel(initialTravel[i]);
        pedal.onHold = [this, i](bool down) { processor.enqueueKeyboard(down, 12 + static_cast<int>(i), 1.0f); };
        addAndMakeVisible(pedal);
        controls[softIndex - i].setTextBoxStyle(juce::Slider::TextBoxRight, false, 38, 22);
    }
    keyboard.setAvailableRange(21, 108);
    keyboard.setLowestVisibleKey(36);
    keyboard.setKeyWidth(19);
    keyboard.setColour(juce::MidiKeyboardComponent::whiteNoteColourId, ivory.brighter(.06f));
    keyboard.setColour(juce::MidiKeyboardComponent::blackNoteColourId, ink);
    keyboard.setColour(juce::MidiKeyboardComponent::keySeparatorLineColourId, juce::Colour(0xffa99d89));
    keyboard.setColour(juce::MidiKeyboardComponent::mouseOverKeyOverlayColourId, brass.withAlpha(.25f));
    keyboard.setColour(juce::MidiKeyboardComponent::keyDownOverlayColourId, brass.withAlpha(.55f));
    keyboardState.addListener(this);
    addAndMakeVisible(keyboard);
    // The build identity stays off the panel so the committed screenshot does
    // not change with every build.
    about.setTooltip("About Keyra " KEYRA_BUILD_IDENTITY);
    about.setMouseCursor(juce::MouseCursor::PointingHandCursor);
    about.onClick = [this] {
        aboutMessageBox = juce::AlertWindow::showScopedAsync(
            juce::MessageBoxOptions().withTitle("About Keyra")
                .withMessage("Keyra " KEYRA_BUILD_IDENTITY)
                .withButton("OK")
                .withAssociatedComponent(this), nullptr);
    };
    addAndMakeVisible(about);
    setSize(980, 560);
    startTimerHz(24);
}

KeyraAudioProcessorEditor::~KeyraAudioProcessorEditor()
{
    aboutMessageBox = {};
    for (size_t i = 0; i < pedals.size(); ++i) {
        processor.enqueueKeyboard(false, 12 + static_cast<int>(i), 0);
        pedals[i].onHold = nullptr;
    }
    keyboardState.allNotesOff(1);
    keyboardState.removeListener(this);
    setLookAndFeel(nullptr);
}

void KeyraAudioProcessorEditor::showView(int view)
{
    view = juce::jlimit(0, static_cast<int>(views.size()) - 1, view);
    processor.editorView = view;
    for (size_t i = 0; i < views.size(); ++i) {
        tabs[i].setToggleState(static_cast<int>(i) == view, juce::dontSendNotification);
        for (const auto knob : views[i])
            controls[knob].setVisible(static_cast<int>(i) == view);
    }
    repaint();
}

void KeyraAudioProcessorEditor::resized()
{
    for (const auto& view : views)
        for (size_t i = 0; i < view.size(); ++i)
            controls[view[i]].setBounds(74 + static_cast<int>(i) * 120 + static_cast<int>(7 - view.size()) * 60, 170, 112, 126);
    for (size_t i = 0; i < tabs.size(); ++i)
        tabs[i].setBounds(370 + static_cast<int>(i) * 80, 138, 80, 21);
    controls[tuningIndex].setBounds(794, 100, 112, 28);
    body.setBounds(74, 100, 190, 28);
    program.setBounds(520, 99, 184, 30);
    for (int i = 0; i < 3; ++i) {
        const auto x = 90 + i * 282;
        pedals[static_cast<size_t>(i)].setBounds(x, 341, 70, 83);
        controls[softIndex - static_cast<size_t>(i)].setBounds(x + 86, 388, 164, 29);
    }
    keyboard.setBounds(54, 442, 872, 82);
    about.setBounds(70, 52, 300, 50); // where paint() draws the title
}

void KeyraAudioProcessorEditor::paint(juce::Graphics& g)
{
    g.fillAll(juce::Colour(0xff251810));
    // Authored vector material: a restrained quarter-sawn walnut frame under
    // a single top-left light. No photographed or third-party texture.
    g.setGradientFill(juce::ColourGradient(juce::Colour(0xff68452b), 0, 0,
        juce::Colour(0xff2d2018), 980, 560, false));
    g.fillRoundedRectangle(4, 4, 972, 552, 10);
    for (int i = 0; i < 105; ++i) {
        const auto y = 5.0f + i * 5.3f;
        juce::Path grain;
        grain.startNewSubPath(8, y);
        grain.cubicTo(270, y + std::sin(i * .37f) * 6, 640, y - std::cos(i * .21f) * 5, 972, y + 1);
        g.setColour(juce::Colour(0xffbd8954).withAlpha(i % 3 == 0 ? .07f : .035f));
        g.strokePath(grain, juce::PathStrokeType(i % 4 == 0 ? 1.5f : .7f));
    }
    g.setColour(juce::Colours::black.withAlpha(.3f));
    g.fillRoundedRectangle(34, 29, 912, 511, 6);
    g.setGradientFill(juce::ColourGradient(juce::Colour(0xfff6f1e6), 40, 30,
        juce::Colour(0xffe3dbcb), 900, 530, false));
    g.fillRoundedRectangle(38, 28, 904, 504, 4);
    g.setColour(juce::Colours::white.withAlpha(.65f));
    g.drawRoundedRectangle(39, 29, 902, 502, 4, 1);
    text(g, "KEYRA", { 70, 52, 300, 50 }, 43, ink, juce::Justification::centredLeft, true);
    text(g, "PRESET", { 440, 102, 72, 25 }, 12, muted, juce::Justification::centredRight);
    text(g, "PROTOCODUS", { 718, 54, 188, 24 }, 15, ink, juce::Justification::centredRight, true);
    text(g, "A4", { 750, 101, 36, 25 }, 12, muted, juce::Justification::centredRight);
    // The rule under the header parts around the views' tabs.
    g.setColour(brass.withAlpha(.4f));
    g.drawLine(74, 148, 362, 148, 1);
    g.drawLine(618, 148, 906, 148, 1);
    for (const auto i : views[static_cast<size_t>(processor.editorView)])
        text(g, captions[i], controls[i].getBounds().withY(301).withHeight(24), 12, ink, juce::Justification::centred, true);
    g.setColour(brass.withAlpha(.25f));
    g.drawLine(74, 332, 906, 332, 1);
    for (int i = 0; i < 3; ++i) {
        const auto x = 90 + i * 282;
        constexpr std::array<const char*, 3> keyLabels {{ "C0 / 12", "C#0 / 13", "D0 / 14" }};
        text(g, captions[softIndex - static_cast<size_t>(i)], { x + 86, 350, 164, 20 }, 12, ink, juce::Justification::centredLeft, true);
        text(g, keyLabels[static_cast<size_t>(i)], { x + 86, 371, 164, 18 }, 11, muted);
        if (i < 2) {
            g.setColour(ink.withAlpha(.12f));
            g.drawLine(static_cast<float>(x + 261), 350, static_cast<float>(x + 261), 416, 1);
        }
    }
    g.setColour(ink);
    g.fillRect(54, 434, 872, 8);
    g.setColour(brass.withAlpha(.8f));
    g.fillRect(54, 434, 872, 1);
    text(g, "88 KEYS", { 56, 536, 140, 17 }, 10, footer);
    text(g, "MOD WHEEL  /  FELT MUTE", { 620, 536, 304, 17 }, 10, footer, juce::Justification::centredRight);
    g.setColour(activity ? brass : ink.withAlpha(.22f));
    g.fillEllipse(887, 137, 5, 5);
    g.setColour(ink.withAlpha(.15f));
    g.fillRoundedRectangle(854, 77, 52, 3, 1.5f);
    g.setColour(brass);
    g.fillRoundedRectangle(854, 77, 52 * juce::jlimit(0.0f, 1.0f, level), 3, 1.5f);
}

void KeyraAudioProcessorEditor::timerCallback()
{
    pedals[0].setTravel(processor.softLevel.load(std::memory_order_relaxed));
    pedals[1].setTravel(processor.sostenutoLevel.load(std::memory_order_relaxed));
    pedals[2].setTravel(processor.sustainLevel.load(std::memory_order_relaxed));
    level = juce::jmax(processor.outputPeak.load(std::memory_order_relaxed), level * .8f);
    activity = processor.noteActivity.exchange(false, std::memory_order_relaxed);
    program.setSelectedId(processor.getCurrentProgram() + 1, juce::dontSendNotification);
    repaint();
}

void KeyraAudioProcessorEditor::handleNoteOn(juce::MidiKeyboardState*, int, int note, float velocity)
{
    processor.enqueueKeyboard(true, note, velocity);
}
void KeyraAudioProcessorEditor::handleNoteOff(juce::MidiKeyboardState*, int, int note, float)
{
    processor.enqueueKeyboard(false, note, 0);
}
