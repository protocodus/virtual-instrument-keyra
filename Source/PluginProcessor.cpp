#include "PluginProcessor.h"
#include "PluginEditor.h"
#include <cmath>
#include <cerrno>
#include <cstdlib>

namespace {
// The parameters, the engine's Parameters in the order processBlock reads
// them: the eight a 1.x session saved too, then the piano's.
constexpr std::array<const char*, 24> ids {{ "gain", "width", "tuning", "mute", "sustain", "sostenuto", "soft", "mechanics",
    "body", "hammer", "age", "detune", "stretch", "dynamics", "lid", "soundboard", "sympathetic", "duplex",
    "micClose", "micXY", "micLive", "micDistant", "room", "felt" }};
constexpr size_t savedBefore = 8, bodyIndex = 8, micIndex = 18;
constexpr auto& programs = keyra::factoryPresets;
// A saved value: one finite decimal number and nothing after it.
bool parse(const juce::String& text, float& value)
{
    const auto* begin = text.toRawUTF8();
    char* end = nullptr;
    errno = 0;
    const auto parsed = std::strtod(begin, &end);
    if (begin == end || end == nullptr || *end != '\0' || errno == ERANGE) return false;
    value = static_cast<float>(parsed);
    return std::isfinite(value);
}
}

const juce::String KeyraAudioProcessor::getProgramName(int index)
{
    return index >= 0 && index < static_cast<int>(programs.size()) ? programs[static_cast<size_t>(index)].name : juce::String();
}

void KeyraAudioProcessor::setCurrentProgram(int index)
{
    if (index < 0 || index >= static_cast<int>(programs.size())) return;
    const auto& preset = programs[static_cast<size_t>(index)];
    const auto set = [this](const char* id, float value) {
        auto* parameter = parameters.getParameter(id);
        parameter->setValueNotifyingHost(parameter->convertTo0to1(value));
    };
    set("body", static_cast<float>(preset.body));
    set("hammer", preset.hammer);
    set("age", preset.age);
    set("detune", preset.detune);
    set("stretch", preset.stretch);
    set("dynamics", preset.dynamics);
    set("lid", preset.lid);
    set("soundboard", preset.soundboard);
    set("sympathetic", preset.sympathetic);
    set("duplex", preset.duplex);
    for (size_t i = 0; i < keyra::model::micCount; ++i) set(ids[micIndex + i], preset.mic[i]);
    set("room", preset.room);
    set("width", preset.width);
    set("felt", preset.felt);
    currentProgram.store(index, std::memory_order_relaxed);
}

juce::AudioProcessorValueTreeState::ParameterLayout KeyraAudioProcessor::createLayout()
{
    juce::AudioProcessorValueTreeState::ParameterLayout layout;
    // Version hint 1 is the parameters 1.x had, 2 the physical piano's. The
    // piano's read to two decimals, which give a host back the value it
    // read; seven, the default, do not on -1..1 once the range's scaling
    // rounds (clap-validator's param-conversions).
    const auto add = [&layout](const char* id, const char* name, float lo, float hi, float initial, int version = 2) {
        juce::AudioParameterFloatAttributes attributes;
        if (version == 2)
            attributes = attributes.withStringFromValueFunction([](float x, int length) {
                // Adding zero keeps a value that rounds to nothing from reading "-0.00".
                const auto text = juce::String(std::round(x * 100.0f) / 100.0f + 0.0f, 2);
                return length > 0 ? text.substring(0, length) : text;
            });
        layout.add(std::make_unique<juce::AudioParameterFloat>(juce::ParameterID { id, version }, name,
            juce::NormalisableRange<float>(lo, hi), initial, attributes));
    };
    const keyra::Parameters initial;
    add("gain", "Output", 0.0f, 1.0f, initial.gain, 1);
    add("width", "Stereo width", 0.0f, 1.0f, initial.width, 1);
    add("tuning", "Concert tuning", 415.0f, 466.0f, initial.tuning, 1);
    add("mute", "Felt mute", 0.0f, 1.0f, 0.0f, 1);
    add("sustain", "Sustain pedal", 0.0f, 1.0f, 0.0f, 1);
    add("sostenuto", "Sostenuto pedal", 0.0f, 1.0f, 0.0f, 1);
    add("soft", "Soft pedal", 0.0f, 1.0f, 0.0f, 1);
    // How loud the action plays, from silent to twice as loud as calibrated
    // (keyra::Parameters::mechanics). A preset leaves it, as it leaves the
    // output. Keep this raw range linear: existing host automation and saved
    // values are physical gain. Only the editor's knob travel uses the taper.
    add("mechanics", "Mechanics", 0.0f, keyra::maximumMechanicsGain, keyra::defaultMechanicsGain, 1);
    // The piano itself is chosen for a part, not played: a change designs
    // nothing anew but takes the next strike to be heard whole, so it is not
    // offered for automation.
    layout.add(std::make_unique<juce::AudioParameterChoice>(juce::ParameterID { "body", 2 }, "Piano",
        juce::StringArray(keyra::bodyNames.data(), static_cast<int>(keyra::bodyNames.size())), 0,
        juce::AudioParameterChoiceAttributes().withAutomatable(false)));
    add("hammer", "Hammer hardness", -1.0f, 1.0f, initial.hammer);
    add("age", "String age", 0.0f, 1.0f, initial.age);
    add("detune", "Unison detune", 0.0f, 1.0f, initial.detune);
    add("stretch", "Stretch tuning", 0.0f, 2.0f, initial.stretch);
    add("dynamics", "Dynamic range", 0.0f, 1.0f, initial.dynamics);
    add("lid", "Lid", 0.0f, 1.0f, initial.lid);
    add("soundboard", "Soundboard resonance", 0.0f, 1.0f, initial.soundboard);
    add("sympathetic", "Sympathetic resonance", 0.0f, 1.0f, initial.sympathetic);
    add("duplex", "Duplex resonance", 0.0f, 1.0f, initial.duplex);
    add("micClose", "Close mics", 0.0f, 1.0f, initial.mic[keyra::model::micClose]);
    add("micXY", "XY mics", 0.0f, 1.0f, initial.mic[keyra::model::micXY]);
    add("micLive", "Live mics", 0.0f, 1.0f, initial.mic[keyra::model::micLive]);
    add("micDistant", "Distant mics", 0.0f, 1.0f, initial.mic[keyra::model::micDistant]);
    add("room", "Room", 0.0f, 1.0f, initial.room);
    add("felt", "Practice felt", 0.0f, 1.0f, initial.felt);
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
    const auto value = [this](size_t i) { return values[i]->load(std::memory_order_relaxed); };
    keyra::Parameters p;
    p.gain = value(0);
    p.width = value(1);
    p.tuning = value(2);
    p.mute = value(3);
    p.sustain = value(4);
    p.sostenuto = value(5);
    p.soft = value(6);
    p.mechanics = value(7);
    p.body = static_cast<keyra::model::Body>(juce::jlimit(0, keyra::model::bodyCount - 1, juce::roundToInt(value(bodyIndex))));
    p.hammer = value(9);
    p.age = value(10);
    p.detune = value(11);
    p.stretch = value(12);
    p.dynamics = value(13);
    p.lid = value(14);
    p.soundboard = value(15);
    p.sympathetic = value(16);
    p.duplex = value(17);
    for (size_t i = 0; i < keyra::model::micCount; ++i) p.mic[i] = value(micIndex + i);
    p.room = value(22);
    p.felt = value(23);
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
    state.setProperty("schemaVersion", 2, nullptr);
    state.setProperty("program", getCurrentProgram(), nullptr);
    if (auto xml = state.createXml()) copyXmlToBinary(*xml, destination);
}

void KeyraAudioProcessor::setStateInformation(const void* data, int bytes)
{
    if (data == nullptr || bytes <= 0 || bytes > 1024 * 1024) return;
    const auto xml = getXmlFromBinary(data, bytes);
    if (xml == nullptr || !xml->hasTagName("KeyraState")) return;
    auto state = juce::ValueTree::fromXml(*xml);
    if (!state.isValid()) return;
    const auto schema = state.getProperty("schemaVersion", 1).toString();
    if (schema != "1" && schema != "2") return;
    const auto programText = state.getProperty("program", 0).toString();
    if (programText.isEmpty() || programText.length() > 3 || !programText.containsOnly("0123456789")) return;
    auto program = programText.getIntValue();
    if (schema == "1") {
        // A 1.x session played measured pianos this engine does not have. It
        // keeps the controls that still mean what they did and loads the
        // nearest piano: the upright where its strings were mostly the
        // upright's ("strings2", or the older "model"), the concert grand
        // otherwise; Brightness becomes the hammers' hardness and Resonance,
        // whose default was a quarter, the sympathetic strings'. Its program
        // number keeps its place in the bank.
        juce::ValueTree converted("KeyraState");
        const auto put = [&converted](const juce::String& id, float value) {
            juce::ValueTree child("PARAM");
            child.setProperty("id", id, nullptr);
            child.setProperty("value", value, nullptr);
            converted.appendChild(child, nullptr);
        };
        float upright = 0, others = 0;
        bool mechanics = false;
        for (const auto child : state) {
            if (!child.hasType("PARAM")) return;
            const auto id = child.getProperty("id").toString();
            float value = 0;
            if (!parse(child.getProperty("value").toString(), value)) return;
            size_t index = 0;
            while (index < savedBefore && id != ids[index]) ++index;
            if (index < savedBefore) {
                const auto range = parameters.getParameter(id)->getNormalisableRange();
                if (value < range.start || value > range.end) return;
                put(id, value);
                mechanics = mechanics || id == "mechanics";
            } else if (id == "brightness") put("hammer", juce::jlimit(-1.0f, 1.0f, 2 * value - 1));
            else if (id == "resonance") put("sympathetic", juce::jlimit(0.0f, 1.0f, 2 * value));
            else if (id == "strings2" || id == "model") upright = juce::jmax(upright, value);
            else if (id.startsWith("strings")) others = juce::jmax(others, value);
        }
        put("body", static_cast<float>(upright > others || (upright >= .5f && others == 0) ? keyra::model::Body::upright
                                                                                              : keyra::model::Body::concertGrand));
        // Sessions older than the Mechanics control played the action at
        // gain 1; the quieter default is for new instruments.
        if (!mechanics) put("mechanics", keyra::legacyMechanicsGain);
        if (program >= static_cast<int>(programs.size())) program = 0;
        parameters.replaceState(converted);
        currentProgram.store(program, std::memory_order_relaxed);
        return;
    }
    if (program >= static_cast<int>(programs.size())) return;
    // Reject malformed or future state atomically. Never apply half a preset.
    std::array<bool, ids.size()> seen {};
    for (const auto child : state) {
        if (!child.hasType("PARAM")) return;
        const auto id = child.getProperty("id").toString();
        size_t index = 0;
        while (index < ids.size() && id != ids[index]) ++index;
        if (index == ids.size() || seen[index] || !child.hasProperty("value")) return;
        float value = 0;
        const auto* parameter = parameters.getParameter(id);
        if (parameter == nullptr || !parse(child.getProperty("value").toString(), value)
            || value < parameter->getNormalisableRange().start
            || value > parameter->getNormalisableRange().end) return;
        seen[index] = true;
    }
    for (const auto present : seen)
        if (!present) return;
    parameters.replaceState(state);
    currentProgram.store(program, std::memory_order_relaxed);
}

juce::AudioProcessorEditor* KeyraAudioProcessor::createEditor() { return new KeyraAudioProcessorEditor(*this); }
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter() { return new KeyraAudioProcessor(); }
