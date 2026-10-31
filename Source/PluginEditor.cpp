#include "PluginEditor.h"
#include <cmath>

namespace {
const juce::Colour ink(0xff302c26), ivory(0xffeee8dc), brass(0xffa48448), muted(0xff7c766b), footer(0xffc6ad89);
constexpr std::array<const char*, 11> ids {{ "gain", "brightness", "resonance", "width", "tuning", "mute", "sustain", "sostenuto", "soft", "mechanics", "mic" }};
constexpr std::array<const char*, 11> captions {{ "OUTPUT", "BRIGHTNESS", "RESONANCE", "WIDTH", "A4 TUNING", "FELT MUTE", "SUSTAIN", "SOSTENUTO", "SOFT", "MECHANICS", "TUBE MIC" }};
// The voicing view's knobs, left to right.
constexpr std::array<int, 7> voicing {{ 1, 2, 3, 10, 9, 5, 0 }};
// The build view: a row of weights for each part, one per piano, then past a
// divider the three modifiers.
constexpr std::array<const char*, 4> partCaptions {{ "STRINGS", "HAMMERS", "SOUNDBOARD", "ACTION" }};
constexpr std::array<const char*, 4> partHints {{
    "strings, as a share of the row: their stretch and stiffness, unisons, decays and pickups. Applies from the next note.",
    "hammers, as a share of the row: how hard each partial is struck, how fast it rises and how the tone follows velocity. "
    "Applies from the next note.",
    "soundboard and case, as a share of the row: the body's modes, the strike's knock on them and the board's noise.",
    "action, as a share of the row: the knocks of keys, dampers and pedals."
}};
constexpr std::array<const char*, 3> modifierIds {{ "stiffness", "unisons", "ring" }};
constexpr std::array<const char*, 3> modifierCaptions {{ "STIFFNESS", "UNISONS", "RING" }};
constexpr std::array<const char*, 3> modifierHints {{
    "The strings' inharmonicity, from a quarter to four times as built. Applies from the next note.",
    "How far each note's unison strings sit apart, from one pitch to three times as far as built. Applies from the next note.",
    "How long the strings ring, from half to twice as long as built. Applies from the next note."
}};
constexpr int gridLeft = 176, gridPitch = 128, rowTop = 188, rowPitch = 31;
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

// The footer's Quality selector sets its text in the footer's small type.
juce::Font KeyraLookAndFeel::getComboBoxFont(juce::ComboBox& box)
{
    return box.getHeight() < 24 ? juce::Font(juce::FontOptions(11.0f)) : LookAndFeel_V4::getComboBoxFont(box);
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
    // A modifier's arc runs from its centre, where it leaves the piano as built.
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
    program.setTooltip("A factory piano: each measured piano as built, by the city it comes from, voiced several "
                       "ways, and pianos between them. It sets the build and the voicing; output, tuning, "
                       "mechanics, the tube mic and the pedals stay.");
    addAndMakeVisible(program);
    // The attachment selects item index + 1 of the choice, so the items go in first.
    quality.addItemList({ "Full", "Balanced", "Light" }, 1);
    quality.setColour(juce::ComboBox::backgroundColourId, juce::Colours::transparentBlack);
    quality.setColour(juce::ComboBox::textColourId, footer);
    quality.setColour(juce::ComboBox::outlineColourId, footer.withAlpha(.35f));
    quality.setColour(juce::ComboBox::arrowColourId, footer);
    quality.setTooltip("How much of each note plays, for CPU. Full plays every partial; Balanced and Light "
                       "leave out those 60 and 50 dB under the note's strongest. Applies from the next note.");
    addAndMakeVisible(quality);
    qualityAttachment = std::make_unique<juce::AudioProcessorValueTreeState::ComboBoxAttachment>(processor.parameters, "quality", quality);
    for (size_t i = 0; i < controls.size(); ++i) {
        auto& slider = controls[i];
        slider.setName(captions[i]);
        slider.setSliderStyle(i >= 6 && i <= 8 ? juce::Slider::LinearHorizontal : juce::Slider::RotaryHorizontalVerticalDrag);
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
        slider.setNumDecimalPlacesToDisplay(i == 4 ? 1 : 0);
        if (i != 4) {
            slider.textFromValueFunction = [](double value) { return juce::String(juce::roundToInt(value * 100)) + "%"; };
            slider.valueFromTextFunction = [](const juce::String& value) { return value.getDoubleValue() * .01; };
        } else {
            slider.textFromValueFunction = [](double value) { return juce::String(value, 1) + " Hz"; };
            slider.valueFromTextFunction = [](const juce::String& value) { return value.getDoubleValue(); };
        }
        slider.updateText();
    }
    controls[4].setSliderStyle(juce::Slider::IncDecButtons);
    controls[4].setTextBoxStyle(juce::Slider::TextBoxLeft, false, 84, 28);
    controls[4].setIncDecButtonsMode(juce::Slider::incDecButtonsDraggable_Vertical);
    controls[5].setTooltip("Continuous felt damping, also controlled by modulation wheel (CC1). Works while keys are held.");
    controls[6].setTooltip("Damper pedal (CC64). Intermediate positions allow half pedalling.");
    controls[7].setTooltip("Sostenuto (CC66). Captures only the notes held when the pedal crosses its latch point.");
    controls[8].setTooltip("Soft pedal (CC67). Changes hammer excitation and unison balance.");
    controls[9].setTooltip("How loud the action plays: the keys landing and coming back, the dampers falling and "
                           "the sustain pedal, from silent to twice as loud as calibrated.");
    controls[10].setTooltip("Where the piano is heard from: the stereo pair close over the strings, or a vintage tube "
                            "microphone at shin height, mono, its colour measured on the upright's recordings. "
                            "Between, the two are mixed.");
    const auto plain = [](juce::Slider& slider) {
        slider.setColour(juce::Slider::textBoxTextColourId, ink);
        slider.setColour(juce::Slider::textBoxBackgroundColourId, juce::Colours::transparentBlack);
        slider.setColour(juce::Slider::textBoxOutlineColourId, juce::Colours::transparentBlack);
    };
    for (size_t part = 0; part < buildParts.size(); ++part)
        for (size_t piano = 0; piano < keyra::pianoCount; ++piano) {
            auto& slider = weights[part * keyra::pianoCount + piano];
            const juce::String name = juce::String(keyra::pianoCities[piano]) + " " + keyra::pianoKinds[piano];
            slider.setName(juce::String(partCaptions[part]) + " " + keyra::pianoCities[piano]);
            slider.setSliderStyle(juce::Slider::LinearHorizontal);
            slider.setTextBoxStyle(juce::Slider::TextBoxRight, false, 40, 22);
            slider.setTooltip("The piano takes this much of the " + name + "'s " + partHints[part]);
            addChildComponent(slider);
            weightAttachments[part * keyra::pianoCount + piano] = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment>(
                processor.parameters, weightId(part, piano), slider);
            plain(slider);
            slider.textFromValueFunction = [](double x) { return juce::String(juce::roundToInt(x * 100)) + "%"; };
            slider.valueFromTextFunction = [](const juce::String& text) { return text.getDoubleValue() * .01; };
            slider.updateText();
        }
    // A modifier reads as its parameter does, the factor it scales by.
    for (size_t i = 0; i < modifiers.size(); ++i) {
        auto& slider = modifiers[i];
        slider.setName(modifierCaptions[i]);
        slider.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
        slider.setTextBoxStyle(juce::Slider::TextBoxBelow, false, 92, 22);
        slider.setRotaryParameters(juce::MathConstants<float>::pi * 1.23f,
            juce::MathConstants<float>::pi * 2.77f, true);
        slider.setDoubleClickReturnValue(true, 0.0);
        slider.setTooltip(modifierHints[i]);
        addChildComponent(slider);
        modifierAttachments[i] = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment>(processor.parameters, modifierIds[i], slider);
        plain(slider);
        slider.updateText();
    }
    voicingTab.setTooltip("Brightness, resonance, width, tube mic, mechanics, felt mute and output.");
    buildTab.setTooltip(juce::String("The piano's build: how much of each measured piano's strings, hammers, soundboard and "
                        "action it takes, a row of zeros playing the ") + keyra::pianoCities[0] + " " + keyra::pianoKinds[0]
                        + "'s, and its strings' stiffness, unisons and ring.");
    voicingTab.onClick = [this] { showBuild(false); };
    buildTab.onClick = [this] { showBuild(true); };
    addAndMakeVisible(voicingTab);
    addAndMakeVisible(buildTab);
    showBuild(processor.editorShowsBuild);
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
        controls[8 - i].setTextBoxStyle(juce::Slider::TextBoxRight, false, 38, 22);
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

void KeyraAudioProcessorEditor::showBuild(bool on)
{
    processor.editorShowsBuild = on;
    voicingTab.setToggleState(!on, juce::dontSendNotification);
    buildTab.setToggleState(on, juce::dontSendNotification);
    for (const auto i : voicing)
        controls[static_cast<size_t>(i)].setVisible(!on);
    for (auto& slider : weights)
        slider.setVisible(on);
    for (auto& slider : modifiers)
        slider.setVisible(on);
    repaint();
}

// The piano the build plays, for the header: one measured piano, every part
// its alone, or a hybrid of those the parts take (a part at zero takes the
// first piano's, as the engine plays it).
juce::String KeyraAudioProcessorEditor::pianoName() const
{
    std::array<bool, keyra::pianoCount> taken {};
    for (size_t part = 0; part < buildParts.size(); ++part) {
        bool any = false;
        for (size_t piano = 0; piano < keyra::pianoCount; ++piano)
            if (weights[part * keyra::pianoCount + piano].getValue() > 0) taken[piano] = any = true;
        if (!any) taken[0] = true;
    }
    juce::StringArray cities;
    size_t only = 0;
    for (size_t piano = 0; piano < keyra::pianoCount; ++piano)
        if (taken[piano]) { cities.add(keyra::pianoCities[piano]); only = piano; }
    if (cities.size() == 1) return (juce::String("MODELLED ") + keyra::pianoCities[only] + " " + keyra::pianoKinds[only]).toUpperCase();
    const auto last = cities[cities.size() - 1];
    cities.remove(cities.size() - 1);
    return ("MODELLED HYBRID OF " + cities.joinIntoString(", ") + " AND " + last).toUpperCase();
}

void KeyraAudioProcessorEditor::resized()
{
    for (size_t i = 0; i < voicing.size(); ++i)
        controls[static_cast<size_t>(voicing[i])].setBounds(74 + static_cast<int>(i) * 120, 170, 112, 126);
    for (size_t part = 0; part < buildParts.size(); ++part)
        for (size_t piano = 0; piano < keyra::pianoCount; ++piano)
            weights[part * keyra::pianoCount + piano].setBounds(gridLeft + static_cast<int>(piano) * gridPitch,
                rowTop + static_cast<int>(part) * rowPitch, gridPitch - 8, 26);
    for (size_t i = 0; i < modifiers.size(); ++i)
        modifiers[i].setBounds(594 + static_cast<int>(i) * 104, 170, 104, 126);
    voicingTab.setBounds(410, 138, 80, 21);
    buildTab.setBounds(490, 138, 80, 21);
    controls[4].setBounds(794, 100, 112, 28);
    program.setBounds(520, 99, 184, 30);
    for (int i = 0; i < 3; ++i) {
        const auto x = 90 + i * 282;
        pedals[static_cast<size_t>(i)].setBounds(x, 341, 70, 83);
        controls[static_cast<size_t>(8 - i)].setBounds(x + 86, 388, 164, 29);
    }
    keyboard.setBounds(54, 442, 872, 82);
    quality.setBounds(452, 535, 92, 19);
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
    text(g, pianoName(), { 74, 103, 366, 22 }, 12, muted);
    text(g, "PRESET", { 440, 102, 72, 25 }, 12, muted, juce::Justification::centredRight);
    text(g, "PROTOCODUS", { 718, 54, 188, 24 }, 15, ink, juce::Justification::centredRight, true);
    text(g, "A4", { 750, 101, 36, 25 }, 12, muted, juce::Justification::centredRight);
    // The rule under the header parts around the two views' tabs.
    g.setColour(brass.withAlpha(.4f));
    g.drawLine(74, 148, 402, 148, 1);
    g.drawLine(578, 148, 906, 148, 1);
    if (buildTab.getToggleState()) {
        // Each column a piano, over its weights' tracks; each row a part.
        for (size_t piano = 0; piano < keyra::pianoCount; ++piano)
            text(g, juce::String(keyra::pianoCities[piano]).toUpperCase(),
                { gridLeft + static_cast<int>(piano) * gridPitch, 164, gridPitch - 48, 18 }, 11, muted, juce::Justification::centred, true);
        for (size_t part = 0; part < buildParts.size(); ++part)
            text(g, partCaptions[part], { 74, rowTop + static_cast<int>(part) * rowPitch, gridLeft - 82, 26 }, 12, ink,
                juce::Justification::centredLeft, true);
        for (size_t i = 0; i < modifiers.size(); ++i)
            text(g, modifierCaptions[i], modifiers[i].getBounds().withY(301).withHeight(24), 12, ink, juce::Justification::centred, true);
        g.setColour(ink.withAlpha(.12f));
        g.drawLine(574, 182, 574, 314, 1);
    } else {
        for (const auto i : voicing) {
            const auto& knob = controls[static_cast<size_t>(i)];
            text(g, captions[static_cast<size_t>(i)], knob.getBounds().withY(301).withHeight(24), 12, ink, juce::Justification::centred, true);
        }
    }
    g.setColour(brass.withAlpha(.25f));
    g.drawLine(74, 332, 906, 332, 1);
    for (int i = 0; i < 3; ++i) {
        const auto x = 90 + i * 282;
        constexpr std::array<const char*, 3> keyLabels {{ "C0 / 12", "C#0 / 13", "D0 / 14" }};
        text(g, captions[static_cast<size_t>(8 - i)], { x + 86, 350, 164, 20 }, 12, ink, juce::Justification::centredLeft, true);
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
    text(g, "QUALITY", { 372, 536, 72, 17 }, 10, footer, juce::Justification::centredRight);
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
