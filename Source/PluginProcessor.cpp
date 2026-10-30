#include "PluginProcessor.h"
#include "PluginEditor.h"
#include <cmath>
#include <cerrno>
#include <cstdlib>

namespace {
constexpr std::array<const char*, 18> ids {{ "gain", "brightness", "resonance", "width", "tuning", "mute", "sustain", "sostenuto", "soft",
    "model", "quality", "strings", "hammers", "soundboard", "action", "stiffness", "unisons", "ring" }};
// The build's seven controls follow Quality, in keyra::buildToward's order.
constexpr size_t modelIndex = 9, qualityIndex = 10, buildIndex = 11;
constexpr auto& programs = keyra::factoryPresets;
}

const juce::String KeyraAudioProcessor::getProgramName(int index)
{
    return index >= 0 && index < static_cast<int>(programs.size()) ? programs[static_cast<size_t>(index)].name : juce::String();
}

void KeyraAudioProcessor::setCurrentProgram(int index)
{
    if (index < 0 || index >= static_cast<int>(programs.size())) return;
    const auto& preset = programs[static_cast<size_t>(index)];
    // Every factory preset is one of the two measured pianos, as built.
    const std::array<std::pair<const char*, float>, 12> settings {{
        { "model", preset.piano == keyra::Piano::upright ? 1.0f : 0.0f },
        { "strings", 0.0f }, { "hammers", 0.0f }, { "soundboard", 0.0f }, { "action", 0.0f },
        { "stiffness", 0.0f }, { "unisons", 0.0f }, { "ring", 0.0f },
        { "brightness", preset.brightness }, { "resonance", preset.resonance },
        { "width", preset.width }, { "mute", preset.mute }
    }};
    for (const auto& setting : settings) {
        auto* parameter = parameters.getParameter(setting.first);
        parameter->setValueNotifyingHost(parameter->convertTo0to1(setting.second));
    }
    currentProgram.store(index, std::memory_order_relaxed);
}

juce::AudioProcessorValueTreeState::ParameterLayout KeyraAudioProcessor::createLayout()
{
    juce::AudioProcessorValueTreeState::ParameterLayout layout;
    const auto add = [&layout](const char* id, const char* name, float lo, float hi, float initial) {
        layout.add(std::make_unique<juce::AudioParameterFloat>(juce::ParameterID { id, 1 }, name,
            juce::NormalisableRange<float>(lo, hi), initial));
    };
    add("gain", "Output", 0.0f, 1.0f, .7f);
    add("brightness", "Hammer brightness", 0.0f, 1.0f, .5f);
    add("resonance", "Sympathetic resonance", 0.0f, 1.0f, .25f);
    add("width", "Stereo width", 0.0f, 1.0f, .75f);
    add("tuning", "Concert tuning", 415.0f, 466.0f, 440.0f);
    add("mute", "Felt mute", 0.0f, 1.0f, 0.0f);
    add("sustain", "Sustain pedal", 0.0f, 1.0f, 0.0f);
    add("sostenuto", "Sostenuto pedal", 0.0f, 1.0f, 0.0f);
    add("soft", "Soft pedal", 0.0f, 1.0f, 0.0f);
    // The instrument, not a performance control: the piano is chosen for a
    // part, not played, so it is not offered for automation.
    layout.add(std::make_unique<juce::AudioParameterChoice>(juce::ParameterID { "model", 1 }, "Piano",
        juce::StringArray { "Grand", "Upright" }, 0, juce::AudioParameterChoiceAttributes().withAutomatable(false)));
    // A CPU setting, which presets leave alone; it applies from the next strike.
    layout.add(std::make_unique<juce::AudioParameterChoice>(juce::ParameterID { "quality", 1 }, "Quality",
        juce::StringArray { "Full", "Balanced", "Light" }, 0, juce::AudioParameterChoiceAttributes().withAutomatable(false)));
    // The piano's build (keyra::buildToward): each part moved toward the
    // other piano's, from 0 (the piano's own) to 1 (the other's), and three
    // modifiers from -1 to 1. Part of the instrument like the piano, so not
    // offered for automation either.
    const auto part = [&layout](const char* id, const char* name) {
        layout.add(std::make_unique<juce::AudioParameterFloat>(juce::ParameterID { id, 1 }, name,
            juce::NormalisableRange<float>(0.0f, 1.0f), 0.0f, juce::AudioParameterFloatAttributes().withAutomatable(false)));
    };
    part("strings", "Strings");
    part("hammers", "Hammers");
    part("soundboard", "Soundboard");
    part("action", "Action");
    // A modifier reads as the factor it scales the build by: stiffness 4^x,
    // unisons 1 + x below 0 and 1 + 2x above, ring 2^x. Two decimals give a
    // host back the value it read; seven, the default, do not on -1..1 once
    // the range's scaling rounds (clap-validator's param-conversions). The
    // number is read from its first digit: clap-juce-extensions hands a
    // host's text back as ASCII, so the × arrives as two other characters.
    const auto modifier = [&layout](const char* id, const char* name, double (*factor)(double), double (*fromFactor)(double)) {
        layout.add(std::make_unique<juce::AudioParameterFloat>(juce::ParameterID { id, 1 }, name,
            juce::NormalisableRange<float>(-1.0f, 1.0f), 0.0f, juce::AudioParameterFloatAttributes()
                .withAutomatable(false)
                .withStringFromValueFunction([factor](float x, int length) {
                    const auto text = juce::String(juce::CharPointer_UTF8("\xc3\x97")) + juce::String(factor(x), 2);
                    return length > 0 ? text.substring(0, length) : text;
                })
                .withValueFromStringFunction([fromFactor](const juce::String& text) {
                    return static_cast<float>(fromFactor(text.substring(text.indexOfAnyOf("0123456789.")).getDoubleValue()));
                })));
    };
    modifier("stiffness", "Stiffness", [](double x) { return std::pow(4.0, x); },
        [](double f) { return f > 0 ? std::log(f) / std::log(4.0) : -1.0; });
    modifier("unisons", "Unisons", [](double x) { return x < 0 ? 1 + x : 1 + 2 * x; },
        [](double f) { return f < 1 ? f - 1 : (f - 1) / 2; });
    modifier("ring", "Ring", [](double x) { return std::pow(2.0, x); },
        [](double f) { return f > 0 ? std::log2(f) : -1.0; });
    return layout;
}

KeyraAudioProcessor::KeyraAudioProcessor()
    : AudioProcessor(BusesProperties().withOutput("Piano", juce::AudioChannelSet::stereo(), true)),
      parameters(*this, nullptr, "KeyraState", createLayout())
{
    for (size_t i = 0; i < ids.size(); ++i)
        values[i] = parameters.getRawParameterValue(ids[i]);
}

void KeyraAudioProcessor::prepareToPlay(double sampleRate, int)
{
    prepared = std::isfinite(sampleRate) && sampleRate >= 22050.0 && sampleRate <= 192000.0;
    if (prepared) engine.prepare(sampleRate);
    setLatencySamples(engine.outputLatencySamples());
    reset();
}

void KeyraAudioProcessor::reset()
{
    engine.reset();
    keyboardRead.store(keyboardWrite.load(std::memory_order_acquire), std::memory_order_release);
    keyboardOverflow.store(false, std::memory_order_relaxed);
    keyboardHeld.fill(false);
    outputPeak.store(0.0f, std::memory_order_relaxed);
    noteActivity.store(false, std::memory_order_relaxed);
    publishPedals();
}

bool KeyraAudioProcessor::isBusesLayoutSupported(const BusesLayout& layout) const
{
    return layout.getMainInputChannelSet().isDisabled()
        && layout.getMainOutputChannelSet() == juce::AudioChannelSet::stereo();
}

void KeyraAudioProcessor::dispatch(const juce::MidiMessage& message) noexcept
{
    const auto channel = message.getChannel();
    if (message.isNoteOn()) {
        engine.noteOn(message.getNoteNumber(), message.getFloatVelocity(), channel);
        if (message.getNoteNumber() >= 21 && message.getNoteNumber() <= 108)
            noteActivity.store(true, std::memory_order_relaxed);
    } else if (message.isNoteOff()) {
        engine.noteOff(message.getNoteNumber(), channel);
    } else if (message.isController()) {
        const auto controller = message.getControllerNumber();
        // Channel-wide release also cancels the GUI presses owned on channel 1.
        // Forget their bookkeeping now: a later mouse-up must not consume a
        // fresh host-owned press of the same piano key or pedal keyswitch.
        if (channel == 1 && (controller == 120 || controller == 123))
            keyboardHeld.fill(false);
        engine.controlChange(controller, message.getControllerValue(), channel);
    } else if (message.isPitchWheel()) {
        const auto wheel = message.getPitchWheelValue();
        engine.pitchBend(2.0f * (wheel - 8192) / (wheel < 8192 ? 8192.0f : 8191.0f), channel);
    }
}

void KeyraAudioProcessor::processBlock(juce::AudioBuffer<float>& audio, juce::MidiBuffer& midi)
{
    juce::ScopedNoDenormals noDenormals;
    audio.clear();
    if (!prepared || audio.getNumChannels() < 2) { midi.clear(); return; }
    keyra::Parameters p;
    p.gain = values[0]->load(std::memory_order_relaxed);
    p.brightness = values[1]->load(std::memory_order_relaxed);
    p.resonance = values[2]->load(std::memory_order_relaxed);
    p.width = values[3]->load(std::memory_order_relaxed);
    p.tuning = values[4]->load(std::memory_order_relaxed);
    p.mute = values[5]->load(std::memory_order_relaxed);
    p.sustain = values[6]->load(std::memory_order_relaxed);
    p.sostenuto = values[7]->load(std::memory_order_relaxed);
    p.soft = values[8]->load(std::memory_order_relaxed);
    const auto build = [this](size_t i) { return values[buildIndex + i]->load(std::memory_order_relaxed); };
    p.build = keyra::buildToward(values[modelIndex]->load(std::memory_order_relaxed) >= .5f ? keyra::Piano::upright : keyra::Piano::grand,
        build(0), build(1), build(2), build(3), build(4), build(5), build(6));
    p.quality = static_cast<keyra::Quality>(juce::jlimit(0, 2, juce::roundToInt(values[qualityIndex]->load(std::memory_order_relaxed))));
    engine.setParameters(p);
    auto read = keyboardRead.load(std::memory_order_relaxed);
    auto write = keyboardWrite.load(std::memory_order_acquire);
    if (keyboardOverflow.exchange(false, std::memory_order_acquire)) {
        // Balance exactly the GUI-owned presses. Host channel-1 presses and
        // pedals retain their state, and GUI notes share those performance
        // controllers just like an ordinary channel-1 keyboard.
        for (size_t note = 0; note < keyboardHeld.size(); ++note)
            if (keyboardHeld[note]) engine.noteOff(static_cast<int>(note) + 12, 1);
        keyboardHeld.fill(false);
        write = keyboardWrite.load(std::memory_order_acquire);
        read = write;
    }
    while (read != write) {
        const auto event = keyboardQueue[read];
        if ((event.note >= 12 && event.note <= 14) || (event.note >= 21 && event.note <= 108)) {
            auto& held = keyboardHeld[static_cast<size_t>(event.note - 12)];
            if (event.down && !held) { engine.noteOn(event.note, event.velocity, 1); held = true; }
            else if (!event.down && held) { engine.noteOff(event.note, 1); held = false; }
        }
        read = (read + 1) % keyboardQueue.size();
    }
    keyboardRead.store(read, std::memory_order_release);
    auto* left = audio.getWritePointer(0);
    auto* right = audio.getWritePointer(1);
    const auto count = audio.getNumSamples();
    int cursor = 0;
    // Render up to each event before dispatch. Equal-timestamp MIDI retains
    // source order; a pedal edge at a note boundary therefore has one meaning
    // in offline export and live playback, independent of host block size.
    for (const auto metadata : midi) {
        const auto frame = juce::jlimit(cursor, count, metadata.samplePosition);
        if (frame > cursor) engine.process(left + cursor, right + cursor, frame - cursor);
        cursor = frame;
        // Non-channel messages (notably arbitrarily long SysEx) are ignored
        // before constructing MidiMessage, whose long-message path allocates.
        if (metadata.numBytes > 0 && metadata.numBytes <= 3
            && metadata.data[0] >= 0x80 && metadata.data[0] < 0xf0) {
            const auto status = metadata.data[0] & 0xf0;
            const auto expectedBytes = status == 0xc0 || status == 0xd0 ? 2 : 3;
            if (metadata.numBytes == expectedBytes) dispatch(metadata.getMessage());
        }
    }
    if (cursor < count) engine.process(left + cursor, right + cursor, count - cursor);
    float peak = 0;
    for (int i = 0; i < count; ++i)
        peak = juce::jmax(peak, std::abs(left[i]), std::abs(right[i]));
    outputPeak.store(peak, std::memory_order_relaxed);
    publishPedals();
    midi.clear();
}

void KeyraAudioProcessor::publishPedals() noexcept
{
    const auto state = engine.pedalState();
    softLevel.store(state.soft, std::memory_order_relaxed);
    sostenutoLevel.store(state.sostenuto, std::memory_order_relaxed);
    sustainLevel.store(state.sustain, std::memory_order_relaxed);
}

void KeyraAudioProcessor::enqueueKeyboard(bool down, int note, float velocity) noexcept
{
    const auto write = keyboardWrite.load(std::memory_order_relaxed);
    const auto next = static_cast<unsigned>((write + 1) % keyboardQueue.size());
    if (next == keyboardRead.load(std::memory_order_acquire)) {
        keyboardOverflow.store(true, std::memory_order_release);
        return;
    }
    keyboardQueue[write] = { down, note, velocity };
    keyboardWrite.store(next, std::memory_order_release);
}

void KeyraAudioProcessor::getStateInformation(juce::MemoryBlock& destination)
{
    auto state = parameters.copyState();
    state.setProperty("schemaVersion", 1, nullptr);
    state.setProperty("program", getCurrentProgram(), nullptr);
    if (auto xml = state.createXml()) copyXmlToBinary(*xml, destination);
}

void KeyraAudioProcessor::setStateInformation(const void* data, int bytes)
{
    if (data == nullptr || bytes <= 0 || bytes > 1024 * 1024) return;
    const auto xml = getXmlFromBinary(data, bytes);
    if (xml == nullptr || !xml->hasTagName("KeyraState")) return;
    auto state = juce::ValueTree::fromXml(*xml);
    if (!state.isValid() || state.getProperty("schemaVersion", 1).toString() != "1") return;
    const auto programText = state.getProperty("program", 0).toString();
    if (programText.length() != 1 || programText[0] < '0'
        || programText[0] >= '0' + static_cast<int>(programs.size())) return;
    // Reject malformed or future state atomically. Never apply half a preset.
    std::array<bool, ids.size()> seen {};
    for (const auto child : state) {
        if (!child.hasType("PARAM")) return;
        const auto id = child.getProperty("id").toString();
        size_t index = 0;
        while (index < ids.size() && id != ids[index]) ++index;
        if (index == ids.size() || seen[index] || !child.hasProperty("value")) return;
        const auto valueText = child.getProperty("value").toString();
        const auto* begin = valueText.toRawUTF8();
        char* end = nullptr;
        errno = 0;
        const auto parsed = std::strtod(begin, &end);
        if (begin == end || end == nullptr || *end != '\0' || errno == ERANGE) return;
        const auto value = static_cast<float>(parsed);
        const auto* parameter = dynamic_cast<juce::RangedAudioParameter*>(parameters.getParameter(id));
        if (parameter == nullptr || !std::isfinite(value)
            || value < parameter->getNormalisableRange().start
            || value > parameter->getNormalisableRange().end) return;
        seen[index] = true;
    }
    // Sessions saved before the piano, quality and build controls existed
    // lack them and keep their defaults: the grand they were made with, at
    // full quality, as it was built.
    for (size_t i = 0; i < modelIndex; ++i)
        if (!seen[i]) return;
    parameters.replaceState(state);
    currentProgram.store(programText.getIntValue(), std::memory_order_relaxed);
}

juce::AudioProcessorEditor* KeyraAudioProcessor::createEditor() { return new KeyraAudioProcessorEditor(*this); }
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter() { return new KeyraAudioProcessor(); }
