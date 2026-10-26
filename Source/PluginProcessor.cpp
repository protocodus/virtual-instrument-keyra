#include "PluginProcessor.h"
#include "PluginEditor.h"
#include <cmath>
#include <cerrno>
#include <cstdlib>

namespace {
constexpr std::array<const char*, 9> ids {{ "gain", "brightness", "resonance", "width", "tuning", "mute", "sustain", "sostenuto", "soft" }};
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
    const std::array<std::pair<const char*, float>, 4> settings {{
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
    if (programText.length() != 1 || programText[0] < '0' || programText[0] > '4') return;
    // Reject malformed or future state atomically. Never apply half a preset.
    std::array<bool, 9> seen {};
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
    for (const auto present : seen) if (!present) return;
    parameters.replaceState(state);
    currentProgram.store(programText.getIntValue(), std::memory_order_relaxed);
}

juce::AudioProcessorEditor* KeyraAudioProcessor::createEditor() { return new KeyraAudioProcessorEditor(*this); }
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter() { return new KeyraAudioProcessor(); }
