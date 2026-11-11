#include "PluginProcessor.h"
#include <juce_gui_basics/juce_gui_basics.h>
#include <cmath>
#include <iostream>
#include <stdexcept>
#include <cstdlib>
#include <new>
#include <string>
#include <vector>

namespace allocationProbe { thread_local bool active = false; thread_local unsigned count = 0; }
void* operator new(std::size_t bytes)
{
    if (allocationProbe::active) ++allocationProbe::count;
    if (auto* memory = std::malloc(bytes == 0 ? 1 : bytes)) return memory;
    throw std::bad_alloc();
}
void* operator new[](std::size_t bytes) { return ::operator new(bytes); }
void operator delete(void* memory) noexcept { std::free(memory); }
void operator delete[](void* memory) noexcept { std::free(memory); }
void operator delete(void* memory, std::size_t) noexcept { std::free(memory); }
void operator delete[](void* memory, std::size_t) noexcept { std::free(memory); }

namespace {
void require(bool condition, const char* message) { if (!condition) throw std::runtime_error(message); }
void set(KeyraAudioProcessor& processor, const char* id, float value)
{
    auto* parameter = processor.parameters.getParameter(id);
    parameter->setValueNotifyingHost(parameter->convertTo0to1(value));
}
float raw(KeyraAudioProcessor& processor, const char* id)
{
    return processor.parameters.getRawParameterValue(id)->load();
}
// A session as Keyra 1.x saved it: schema 1 and its own parameters, the
// measured pianos' weights ("strings1" the grand's, "strings2" the
// upright's), Brightness and Resonance among them.
juce::MemoryBlock session1(int program, std::initializer_list<std::pair<const char*, const char*>> values)
{
    juce::XmlElement xml("KeyraState");
    xml.setAttribute("schemaVersion", 1);
    xml.setAttribute("program", program);
    for (const auto& [id, value] : values) {
        auto* parameter = xml.createNewChildElement("PARAM");
        parameter->setAttribute("id", id);
        parameter->setAttribute("value", value);
    }
    juce::MemoryBlock result;
    juce::AudioProcessor::copyXmlToBinary(xml, result);
    return result;
}
// A saved state without the removed parameters and with the added ones, as
// an earlier or a later version would save it.
juce::MemoryBlock edited(const juce::MemoryBlock& state, const juce::StringArray& removed,
    std::initializer_list<std::pair<const char*, const char*>> added)
{
    auto xml = juce::AudioProcessor::getXmlFromBinary(state.getData(), static_cast<int>(state.getSize()));
    for (const auto& id : removed)
        for (auto* parameter : xml->getChildIterator())
            if (parameter->getStringAttribute("id") == id) { xml->removeChildElement(parameter, true); break; }
    for (const auto& [id, value] : added) {
        auto* parameter = xml->createNewChildElement("PARAM");
        parameter->setAttribute("id", id);
        parameter->setAttribute("value", value);
    }
    juce::MemoryBlock result;
    juce::AudioProcessor::copyXmlToBinary(*xml, result);
    return result;
}

void mechanicsStateCompatibility()
{
    KeyraAudioProcessor processor;
    auto* parameter = processor.parameters.getParameter("mechanics");
    const auto raw = [&] { return processor.parameters.getRawParameterValue("mechanics")->load(); };
    require(raw() == .175f, "fresh Mechanics gain is not the chosen quieter default");
    require(parameter->getDefaultValue() == .0875f, "Mechanics host default is not raw gain .175");
    require(parameter->getNormalisableRange().start == 0 && parameter->getNormalisableRange().end == 2,
        "Mechanics host range changed");
    for (int i = 0; i <= 100; ++i) {
        const auto normalised = static_cast<float>(i) / 100;
        require(std::abs(parameter->convertFrom0to1(normalised) - 2 * normalised) < 1e-7f
            && std::abs(parameter->convertTo0to1(2 * normalised) - normalised) < 1e-7f,
            "Mechanics GUI taper changed legacy host automation mapping");
        parameter->setValueNotifyingHost(normalised);
        require(raw() == 2 * normalised, "Mechanics host automation no longer sets raw gain");
    }

    juce::MemoryBlock state;
    processor.getStateInformation(state);
    const auto xml = juce::AudioProcessor::getXmlFromBinary(state.getData(), static_cast<int>(state.getSize()));
    require(xml != nullptr && xml->getIntAttribute("schemaVersion") == 2,
        "the saved-state schema is not the physical piano's");
    // Explicit values in 1.x sessions are physical gains, not knob
    // positions. Include both previous and current default values.
    for (const auto* value : { "0", "0.175", "0.35", "0.5", "1", "2" }) {
        const auto legacy = session1(0, { { "brightness", "0.82" }, { "mechanics", value } });
        set(processor, "mechanics", .63f);
        processor.setStateInformation(legacy.getData(), static_cast<int>(legacy.getSize()));
        require(raw() == juce::String(value).getFloatValue(), "explicit legacy Mechanics gain was reinterpreted");
    }
    const auto missing = session1(0, { { "brightness", "0.82" } });
    for (const auto previous : { 0.0f, .175f, .35f, 2.0f }) {
        set(processor, "mechanics", previous);
        set(processor, "hammer", .1f);
        processor.setStateInformation(missing.getData(), static_cast<int>(missing.getSize()));
        require(raw() == 1, "state without Mechanics did not restore historical gain 1");
        require(std::abs(processor.parameters.getRawParameterValue("hammer")->load() - .64f) < 1e-6f,
            "legacy Mechanics migration prevented the rest of the state restoring");
    }
    set(processor, "mechanics", .35f);
    for (int program = 0; program < processor.getNumPrograms(); ++program) {
        processor.setCurrentProgram(program);
        require(raw() == .35f, "factory preset overwrote the user's Mechanics balance");
    }
}

juce::Slider* mechanicsSlider(juce::Component& component)
{
    if (auto* slider = dynamic_cast<juce::Slider*>(&component); slider != nullptr && slider->getName() == "MECHANICS")
        return slider;
    for (auto* child : component.getChildren())
        if (auto* slider = mechanicsSlider(*child)) return slider;
    return nullptr;
}

void mechanicsEditorMapping()
{
    KeyraAudioProcessor processor;
    auto& parameter = *processor.parameters.getParameter("mechanics");
    struct HostEvents final : juce::AudioProcessorParameter::Listener {
        explicit HostEvents(juce::AudioProcessorParameter& p) : parameter(p) { parameter.addListener(this); }
        ~HostEvents() override { parameter.removeListener(this); }
        void parameterValueChanged(int, float) override { ++values; }
        void parameterGestureChanged(int, bool starting) override { if (starting) ++starts; else ++ends; }
        juce::AudioProcessorParameter& parameter;
        int values = 0, starts = 0, ends = 0;
    } events(parameter);
    std::unique_ptr<juce::AudioProcessorEditor> editor(processor.createEditor());
    require(editor != nullptr, "Mechanics editor could not be created");
    auto* slider = mechanicsSlider(*editor);
    require(slider != nullptr, "Mechanics slider is not exposed in the editor");
    require(events.values == 0 && events.starts == 0 && events.ends == 0,
        "opening the editor wrote Mechanics automation");
    require(slider->getMinimum() == 0 && slider->getMaximum() == 2 && slider->getValue() == .175f,
        "Mechanics slider lost the physical gain range or fresh default");
    require(std::abs(slider->valueToProportionOfLength(slider->getValue()) - .4) < 1e-6
        && slider->getTextFromValue(slider->getValue()) == "40%"
        && std::abs(slider->getValueFromText("40%") - .175) < 1e-6,
        "Mechanics fresh gain does not display and parse as 40 percent");
    require(slider->proportionOfLengthToValue(0) == 0 && slider->proportionOfLengthToValue(1) == 2,
        "Mechanics knob no longer reaches both physical gain endpoints");

    // A host still writes its old linear value; the editor alone uses the
    // perceptual travel. Host feedback must not restore the linear GUI range.
    parameter.setValueNotifyingHost(.5f);
    require(slider->getValue() == 1 && parameter.getValue() == .5f
        && std::abs(slider->valueToProportionOfLength(1) - .770502939) < 1e-6
        && slider->getTextFromValue(1) == "77%",
        "host automation changed the Mechanics gain or discarded its GUI taper");
    slider->setValue(slider->proportionOfLengthToValue(.4), juce::sendNotificationSync);
    require(std::abs(parameter.convertFrom0to1(parameter.getValue()) - .175f) < 1e-6f
        && std::abs(parameter.getValue() - .0875f) < 1e-6f,
        "40 percent Mechanics knob movement did not write physical gain .175");

    set(processor, "mechanics", 1);
    require(slider->isDoubleClickReturnEnabled() && slider->getDoubleClickReturnValue() == .175f,
        "Mechanics double-click is not configured for the chosen default");
    const auto valuesBefore = events.values, startsBefore = events.starts, endsBefore = events.ends;
    const juce::MouseEvent doubleClick(juce::Desktop::getInstance().getMainMouseSource(), {}, {},
        0, 0, 0, 0, 0, slider, slider, {}, {}, {}, 2, false);
    slider->mouseDoubleClick(doubleClick);
    require(parameter.getValue() == .0875f && slider->getTextFromValue(slider->getValue()) == "40%",
        "Mechanics double-click did not restore the quieter default");
    require(events.values == valuesBefore + 1 && events.starts == startsBefore + 1 && events.ends == endsBefore + 1,
        "Mechanics double-click did not notify the host with one balanced gesture");

    editor.reset();
    set(processor, "mechanics", .35f);
    const auto reopenValues = events.values, reopenStarts = events.starts, reopenEnds = events.ends;
    editor.reset(processor.createEditor());
    slider = mechanicsSlider(*editor);
    require(slider != nullptr && slider->getValue() == .35f && parameter.getValue() == .175f
        && slider->getTextFromValue(slider->getValue()) == "52%"
        && std::abs(slider->valueToProportionOfLength(slider->getValue()) - .519141433) < 1e-6,
        "reopening the editor reinterpreted a stored Mechanics gain");
    require(events.values == reopenValues && events.starts == reopenStarts && events.ends == reopenEnds,
        "reopening the editor wrote Mechanics automation");
}

std::vector<float> render(int block)
{
    KeyraAudioProcessor processor;
    processor.prepareToPlay(48000, block);
    struct Event { int frame; juce::MidiMessage message; };
    const std::array<Event, 13> events {{
        { 0, juce::MidiMessage::noteOn(1, 12, 1.0f) },
        { 37, juce::MidiMessage::controllerEvent(1, 64, 90) },
        { 37, juce::MidiMessage::noteOn(1, 14, 1.0f) },
        { 37, juce::MidiMessage::noteOn(1, 60, .7f) },
        { 123, juce::MidiMessage::noteOn(1, 67, .5f) },
        { 1001, juce::MidiMessage::noteOff(1, 60) },
        { 1179, juce::MidiMessage::noteOn(1, 13, 1.0f) },
        { 2031, juce::MidiMessage::noteOff(1, 67) },
        { 4057, juce::MidiMessage::controllerEvent(1, 64, 0) },
        { 4101, juce::MidiMessage::noteOff(1, 14) },
        { 5001, juce::MidiMessage::noteOff(1, 13) },
        { 6001, juce::MidiMessage::controllerEvent(1, 1, 100) },
        { 7000, juce::MidiMessage::noteOff(1, 12) }
    }};
    std::vector<float> result(16384);
    for (int frame = 0; frame < 8192; frame += block) {
        const auto size = std::min(block, 8192 - frame);
        juce::AudioBuffer<float> buffer(2, size);
        juce::MidiBuffer midi;
        for (const auto& event : events)
            if (event.frame >= frame && event.frame < frame + size)
                midi.addEvent(event.message, event.frame - frame);
        const auto allocationCount = allocationProbe::count;
        allocationProbe::active = true;
        processor.processBlock(buffer, midi);
        allocationProbe::active = false;
        require(allocationProbe::count == allocationCount, "plugin allocated while rendering MIDI/pedals");
        require(midi.isEmpty(), "synth leaked input MIDI");
        for (int i = 0; i < size; ++i) {
            result[static_cast<size_t>((frame + i) * 2)] = buffer.getSample(0, i);
            result[static_cast<size_t>((frame + i) * 2 + 1)] = buffer.getSample(1, i);
        }
    }
    return result;
}

double sostenutoOrder(bool pedalFirst)
{
    KeyraAudioProcessor processor;
    processor.prepareToPlay(48000, 24000);
    juce::AudioBuffer<float> audio(2, 24000);
    juce::MidiBuffer midi;
    const auto note = juce::MidiMessage::noteOn(1, 60, .8f);
    const auto pedal = juce::MidiMessage::noteOn(1, 13, 1.0f);
    midi.addEvent(pedalFirst ? pedal : note, 8);
    midi.addEvent(pedalFirst ? note : pedal, 8);
    midi.addEvent(juce::MidiMessage::noteOff(1, 60), 96);
    processor.processBlock(audio, midi);
    return audio.getRMSLevel(0, 20000, 4000);
}

void channelWideReleaseOwnership(int controller, int note, int releaseChannel)
{
    KeyraAudioProcessor guiRelease, reference;
    guiRelease.prepareToPlay(48000, 256);
    reference.prepareToPlay(48000, 256);
    juce::AudioBuffer<float> actual(2, 256), expected(2, 256);
    juce::MidiBuffer actualMidi, expectedMidi;
    guiRelease.enqueueKeyboard(true, note, .8f);
    reference.enqueueKeyboard(true, note, .8f);
    guiRelease.processBlock(actual, actualMidi);
    reference.processBlock(expected, expectedMidi);

    const auto channelRelease = juce::MidiMessage::controllerEvent(releaseChannel, controller, 0);
    actualMidi.addEvent(channelRelease, 16);
    expectedMidi.addEvent(channelRelease, 16);
    if (releaseChannel == 1) {
        // The panic removed the GUI-owned press. A new host press of the
        // same key must not be consumed by the old GUI mouse-up afterwards.
        const auto hostPress = juce::MidiMessage::noteOn(1, note, .8f);
        actualMidi.addEvent(hostPress, 64);
        expectedMidi.addEvent(hostPress, 64);
    }
    guiRelease.processBlock(actual, actualMidi);
    reference.processBlock(expected, expectedMidi);

    guiRelease.enqueueKeyboard(false, note, 0);
    if (releaseChannel == 2) {
        // Another channel's panic leaves GUI ownership intact. Its GUI
        // mouse-up must still deliver the normal channel-1 note-off.
        expectedMidi.addEvent(juce::MidiMessage::noteOff(1, note), 0);
    }
    guiRelease.processBlock(actual, actualMidi);
    reference.processBlock(expected, expectedMidi);

    for (int channel = 0; channel < 2; ++channel)
        for (int frame = 0; frame < 256; ++frame)
            require(actual.getSample(channel, frame) == expected.getSample(channel, frame),
                "channel-wide MIDI release corrupted GUI/host piano ownership");
    require(guiRelease.softLevel.load() == reference.softLevel.load()
        && guiRelease.sostenutoLevel.load() == reference.sostenutoLevel.load()
        && guiRelease.sustainLevel.load() == reference.sustainLevel.load(),
        "channel-wide MIDI release corrupted GUI/host pedal ownership");
    if (note == 60)
        require(expected.getMagnitude(0, 256) > 1e-8f, "ownership piano witness was silent");
    else {
        const auto depth = note == 12 ? reference.softLevel.load()
            : note == 13 ? reference.sostenutoLevel.load() : reference.sustainLevel.load();
        require(releaseChannel == 1 ? depth > .99f : depth < .001f,
            "ownership pedal witness did not reach its expected state");
    }
}

// An overflowing GUI queue must release the GUI's sounding note exactly as
// its key-up would. Silence is no witness: after a key-up the strike's body
// knock and board noise ring on at their own decay, near -100 dBFS a second
// later. A held copy shows that a stuck note would differ.
void keyboardOverflowRelease()
{
    enum class Ending { overflow, keyUp, held };
    const auto play = [](Ending ending) {
        KeyraAudioProcessor gui;
        gui.prepareToPlay(48000, 128);
        set(gui, "sympathetic", 0);
        juce::AudioBuffer<float> audio(2, 128);
        juce::MidiBuffer midi;
        gui.enqueueKeyboard(true, 60, .8f);
        gui.processBlock(audio, midi);
        if (ending == Ending::overflow)
            for (int i = 0; i < 255; ++i) gui.enqueueKeyboard(true, 60, .8f);
        if (ending != Ending::held) gui.enqueueKeyboard(false, 60, 0);
        std::vector<float> result;
        for (int block = 0; block < 375; ++block) {
            gui.processBlock(audio, midi);
            for (int channel = 0; channel < 2; ++channel)
                for (int frame = 0; frame < 128; ++frame) result.push_back(audio.getSample(channel, frame));
        }
        return result;
    };
    const auto overflowed = play(Ending::overflow), keyUp = play(Ending::keyUp), held = play(Ending::held);
    require(held != keyUp, "keyboard overflow witness ignored its key-up");
    require(overflowed == keyUp, "keyboard overflow failed to release an already sounding GUI note");
}
}

int main()
{
    try {
        juce::ScopedJuceInitialiser_GUI initialise;
        mechanicsStateCompatibility();
        mechanicsEditorMapping();
        KeyraAudioProcessor processor;
        set(processor, "hammer", .83f);
        set(processor, "mute", .37f);
        set(processor, "tuning", 442.3f);
        juce::MemoryBlock state;
        processor.getStateInformation(state);
        KeyraAudioProcessor restored;
        restored.setStateInformation(state.getData(), static_cast<int>(state.getSize()));
        require(std::abs(raw(restored, "hammer") - .83f) < 1e-5f, "the hammers were not restored");
        require(std::abs(raw(restored, "tuning") - 442.3f) < 1e-3f, "tuning not restored");
        const auto before = restored.parameters.copyState().toXmlString();
        const auto bad = [&state](const char* value) {
            auto xml = juce::AudioProcessor::getXmlFromBinary(state.getData(), static_cast<int>(state.getSize()));
            for (auto* parameter : xml->getChildIterator())
                if (parameter->getStringAttribute("id") == "hammer") parameter->setAttribute("value", value);
            juce::MemoryBlock result;
            juce::AudioProcessor::copyXmlToBinary(*xml, result);
            return result;
        };
        for (const auto* value : { "NaN", "900", "-2", "garbage", "0.5junk" }) {
            const auto data = bad(value);
            restored.setStateInformation(data.getData(), static_cast<int>(data.getSize()));
            require(restored.parameters.copyState().toXmlString() == before, "invalid state changed parameters");
        }
        // A state missing a parameter, or with one this version does not
        // have, is refused whole.
        for (const auto& data : { edited(state, { "lid" }, {}), edited(state, {}, { { "pedalNoise", "0.5" } }) }) {
            restored.setStateInformation(data.getData(), static_cast<int>(data.getSize()));
            require(restored.parameters.copyState().toXmlString() == before, "an incomplete or unknown state changed parameters");
        }
        {
            // A preset is a piano, how it is kept and where it is heard from:
            // it sets all of that and leaves the output, the tuning, the
            // action's level, the felt mute and the pedals. The session keeps
            // it, and its program.
            KeyraAudioProcessor chosen;
            set(chosen, "gain", .5f);
            set(chosen, "tuning", 443.0f);
            set(chosen, "mechanics", .5f);
            set(chosen, "mute", .2f);
            set(chosen, "sustain", .6f);
            for (int program = 0; program < chosen.getNumPrograms(); ++program) {
                // From any other piano, so every field is seen to be set.
                chosen.setCurrentProgram((program + 5) % chosen.getNumPrograms());
                chosen.setCurrentProgram(program);
                const auto& preset = keyra::factoryPresets[static_cast<size_t>(program)];
                const std::pair<const char*, float> expected[] {
                    { "body", static_cast<float>(preset.body) }, { "hammer", preset.hammer }, { "age", preset.age },
                    { "detune", preset.detune }, { "stretch", preset.stretch }, { "dynamics", preset.dynamics },
                    { "lid", preset.lid }, { "soundboard", preset.soundboard }, { "sympathetic", preset.sympathetic },
                    { "duplex", preset.duplex }, { "micClose", preset.mic[0] }, { "micXY", preset.mic[1] },
                    { "micLive", preset.mic[2] }, { "micDistant", preset.mic[3] }, { "room", preset.room },
                    { "width", preset.width }, { "felt", preset.felt } };
                for (const auto& [id, value] : expected)
                    require(std::abs(raw(chosen, id) - value) < 1e-6f, "a preset did not set one of its controls");
                require(chosen.getProgramName(program) == preset.name, "a program is not named as its preset");
            }
            require(raw(chosen, "gain") == .5f && raw(chosen, "tuning") == 443.0f && raw(chosen, "mechanics") == .5f
                && raw(chosen, "mute") == .2f && raw(chosen, "sustain") == .6f,
                "a preset moved the output, the tuning, the action, the mute or a pedal");
            chosen.setCurrentProgram(5);
            require(raw(chosen, "body") == static_cast<float>(keyra::model::Body::upright), "program 6 is not the upright");
            juce::MemoryBlock saved;
            chosen.getStateInformation(saved);
            KeyraAudioProcessor reopened;
            reopened.setStateInformation(saved.getData(), static_cast<int>(saved.getSize()));
            require(raw(reopened, "body") == static_cast<float>(keyra::model::Body::upright) && reopened.getCurrentProgram() == 5
                && raw(reopened, "gain") == .5f, "the upright and its program were not restored");
            const auto last = chosen.getNumPrograms() - 1;
            chosen.setCurrentProgram(last);
            chosen.getStateInformation(saved);
            reopened.setStateInformation(saved.getData(), static_cast<int>(saved.getSize()));
            require(reopened.getCurrentProgram() == last, "the last program was not restored");
            chosen.setCurrentProgram(-1);
            chosen.setCurrentProgram(chosen.getNumPrograms());
            require(chosen.getCurrentProgram() == last, "a program that does not exist was taken");
        }
        {
            // A 1.x session played measured pianos this engine does not have.
            // It keeps the controls that mean what they did, takes the
            // nearest piano, and everything 1.x did not have at its default.
            KeyraAudioProcessor reopened;
            set(reopened, "age", .9f);
            set(reopened, "micDistant", 1.0f);
            const auto grand = session1(2, { { "gain", "0.6" }, { "brightness", "0.75" }, { "resonance", "0.25" }, { "width", "0.5" },
                { "tuning", "442" }, { "mute", "0.1" }, { "sustain", "0" }, { "sostenuto", "0" }, { "soft", "0" }, { "quality", "2" },
                { "strings1", "1" }, { "strings2", "0" }, { "hammers1", "1" }, { "stiffness", "0.5" }, { "mechanics", "0.35" }, { "mic", "0.3" } });
            reopened.setStateInformation(grand.getData(), static_cast<int>(grand.getSize()));
            require(std::abs(raw(reopened, "gain") - .6f) < 1e-6f && raw(reopened, "width") == .5f && raw(reopened, "tuning") == 442.0f
                && std::abs(raw(reopened, "mute") - .1f) < 1e-6f && std::abs(raw(reopened, "mechanics") - .35f) < 1e-6f,
                "a 1.x session lost a control that still means what it did");
            require(std::abs(raw(reopened, "hammer") - .5f) < 1e-6f && std::abs(raw(reopened, "sympathetic") - .5f) < 1e-6f,
                "a 1.x session's Brightness and Resonance did not become the hammers and the sympathetic strings");
            require(raw(reopened, "body") == static_cast<float>(keyra::model::Body::concertGrand) && reopened.getCurrentProgram() == 2,
                "a 1.x session of the grand did not load the concert grand and its program");
            const keyra::Parameters initial;
            require(raw(reopened, "age") == initial.age && raw(reopened, "micDistant") == initial.mic[keyra::model::micDistant]
                && raw(reopened, "detune") == initial.detune && raw(reopened, "lid") == initial.lid,
                "a 1.x session left a control it did not have off its default");
            // The upright where its strings were mostly the upright's, by the
            // weights or by the older piano choice.
            for (const auto& upright : { session1(5, { { "strings1", "0.2" }, { "strings2", "0.8" } }), session1(5, { { "model", "1" } }) }) {
                set(reopened, "body", 0);
                reopened.setStateInformation(upright.getData(), static_cast<int>(upright.getSize()));
                require(raw(reopened, "body") == static_cast<float>(keyra::model::Body::upright) && reopened.getCurrentProgram() == 5,
                    "a 1.x session of the upright did not load the upright");
            }
            const auto third = session1(8, { { "strings3", "1" }, { "strings2", "0.4" } });
            reopened.setStateInformation(third.getData(), static_cast<int>(third.getSize()));
            require(raw(reopened, "body") == static_cast<float>(keyra::model::Body::concertGrand),
                "a 1.x session of another grand did not load the concert grand");
            // What is not a 1.x session is refused whole.
            const auto kept = reopened.parameters.copyState().toXmlString();
            for (const auto& data : { session1(0, { { "gain", "7" } }), session1(0, { { "tuning", "abc" } }),
                                      session1(1000, { { "gain", "0.5" } }) }) {
                reopened.setStateInformation(data.getData(), static_cast<int>(data.getSize()));
                require(reopened.parameters.copyState().toXmlString() == kept, "a malformed 1.x session changed parameters");
            }
        }
        {
            // Every control reaches the engine: a strike under it plays
            // otherwise than the default's.
            const auto play = [](KeyraAudioProcessor& processor) {
                processor.prepareToPlay(48000, 128);
                juce::AudioBuffer<float> audio(2, 128);
                juce::MidiBuffer midi;
                midi.addEvent(juce::MidiMessage::noteOn(1, 60, .8f), 0);
                midi.addEvent(juce::MidiMessage::noteOn(1, 84, .8f), 0);
                std::vector<float> result;
                for (int block = 0; block < 100; ++block) {
                    if (block == 50) midi.addEvent(juce::MidiMessage::noteOff(1, 60), 0);
                    processor.processBlock(audio, midi);
                    midi.clear();
                    for (int channel = 0; channel < 2; ++channel)
                        for (int frame = 0; frame < 128; ++frame) result.push_back(audio.getSample(channel, frame));
                }
                return result;
            };
            KeyraAudioProcessor plain;
            const auto reference = play(plain);
            const std::pair<const char*, float> changes[] {
                { "gain", .3f }, { "width", .2f }, { "tuning", 446.0f }, { "mute", .6f }, { "sustain", 1.0f }, { "soft", 1.0f },
                { "mechanics", 0.0f }, { "body", 3.0f }, { "hammer", .8f }, { "age", .9f }, { "detune", .9f }, { "stretch", 0.0f },
                { "dynamics", 1.0f }, { "lid", 0.0f }, { "soundboard", 1.0f }, { "sympathetic", 1.0f }, { "duplex", 1.0f },
                { "micClose", .4f }, { "micXY", .8f }, { "micLive", .8f }, { "micDistant", .8f }, { "room", 1.0f }, { "felt", .8f } };
            for (const auto& [id, value] : changes) {
                KeyraAudioProcessor changed;
                set(changed, id, value);
                if (play(changed) == reference) throw std::runtime_error(std::string(id) + " did not reach the engine");
            }
            // A host reads a parameter's text, gives it back and reads again
            // (clap-validator's param-conversions): every value must read the
            // same both times, also when the text comes back as the CLAP
            // wrapper passes it, its UTF-8 read as ASCII.
            for (auto* parameter : plain.getParameters())
                for (int step = 0; step <= 2000; ++step) {
                    const auto value = static_cast<float>((step + .37) / 2000.37);
                    const auto text = parameter->getText(value, 0);
                    const juce::String asClap(juce::CharPointer_ASCII(text.toRawUTF8()));
                    if (parameter->getText(parameter->getValueForText(text), 0) != text
                        || parameter->getText(parameter->getValueForText(asClap), 0) != text)
                        throw std::runtime_error((parameter->getName(64) + "'s text " + text + " did not give back the value it read").toStdString());
                }
        }
        const auto large = render(8192), small = render(97);
        require(large == small, "MIDI/pedal render depends on host block size");
        double energy = 0;
        for (size_t i = 0; i < large.size(); ++i) {
            require(std::isfinite(large[i]), "nonfinite plugin output");
            if (i < 74) require(large[i] == 0, "MIDI note played before its sample position");
            energy += large[i] * large[i];
        }
        require(energy > 1e-8, "plugin is silent");
        require(sostenutoOrder(false) > sostenutoOrder(true) * 20,
            "same-sample sostenuto keyswitch source ordering did not determine capture");
        for (const auto controller : { 120, 123 })
            for (const auto note : { 60, 12, 13, 14 })
                for (const auto releaseChannel : { 1, 2 })
                    channelWideReleaseOwnership(controller, note, releaseChannel);
        {
            KeyraAudioProcessor pedals;
            pedals.prepareToPlay(48000, 128);
            juce::AudioBuffer<float> audio(2, 128);
            juce::MidiBuffer midi;
            for (int note = 12; note <= 14; ++note)
                midi.addEvent(juce::MidiMessage::noteOn(1, note, 1.0f), 0);
            pedals.processBlock(audio, midi);
            // The sustain switch moves the pedal as CC64 does, which sounds
            // going down; no switch plays a note.
            KeyraAudioProcessor sustained;
            sustained.prepareToPlay(48000, 128);
            juce::AudioBuffer<float> pedalAudio(2, 128);
            juce::MidiBuffer pedalMidi;
            pedalMidi.addEvent(juce::MidiMessage::controllerEvent(1, 64, 127), 0);
            sustained.processBlock(pedalAudio, pedalMidi);
            for (int channel = 0; channel < 2; ++channel)
                for (int i = 0; i < 128; ++i)
                    require(audio.getSample(channel, i) == pedalAudio.getSample(channel, i),
                        "pedal keyswitches produced piano notes");
            require(pedals.softLevel.load() > .99f && pedals.sostenutoLevel.load() > .99f
                && pedals.sustainLevel.load() > .99f, "keyswitch state was not published for visible pedals");
            require(pedals.parameters.getRawParameterValue("soft")->load() < .001f
                && pedals.parameters.getRawParameterValue("sostenuto")->load() < .001f
                && pedals.parameters.getRawParameterValue("sustain")->load() < .001f,
                "performance keyswitch changed persistent pedal parameters");
            for (int note = 12; note <= 14; ++note)
                midi.addEvent(juce::MidiMessage::noteOff(1, note), 0);
            midi.addEvent(juce::MidiMessage::controllerEvent(1, 64, 90), 0);
            pedals.processBlock(audio, midi);
            require(pedals.softLevel.load() < .001f && pedals.sostenutoLevel.load() < .001f
                && std::abs(pedals.sustainLevel.load() - 90.0f / 127.0f) < 1e-5f,
                "keyswitch release did not preserve independent MIDI sustain");
            midi.addEvent(juce::MidiMessage::controllerEvent(1, 64, 0), 0);
            pedals.processBlock(audio, midi);
            pedals.enqueueKeyboard(true, 12, 1);
            pedals.enqueueKeyboard(true, 13, 1);
            pedals.enqueueKeyboard(true, 14, 1);
            pedals.processBlock(audio, midi);
            require(pedals.softLevel.load() > .99f && pedals.sostenutoLevel.load() > .99f
                && pedals.sustainLevel.load() > .99f, "visible pedal holds were not delivered");
            for (int note = 12; note <= 14; ++note) pedals.enqueueKeyboard(false, note, 0);
            pedals.processBlock(audio, midi);
            require(pedals.softLevel.load() < .001f && pedals.sostenutoLevel.load() < .001f
                && pedals.sustainLevel.load() < .001f, "visible pedal releases were not delivered");
        }
        processor.prepareToPlay(48000, 128);
        processor.enqueueKeyboard(true, 60, .8f);
        processor.reset();
        juce::AudioBuffer<float> keyboardBuffer(2, 128);
        juce::MidiBuffer noMidi;
        processor.processBlock(keyboardBuffer, noMidi);
        require(keyboardBuffer.getMagnitude(0, 128) == 0, "reset retained queued keyboard note");
        for (int i = 0; i < 255; ++i) processor.enqueueKeyboard(true, 60, .8f);
        processor.enqueueKeyboard(false, 60, 0);
        processor.processBlock(keyboardBuffer, noMidi);
        require(keyboardBuffer.getMagnitude(0, 128) == 0, "keyboard overflow left queued keys sounding");
        set(processor, "mute", 0);
        set(processor, "sympathetic", 0);
        processor.enqueueKeyboard(true, 60, .8f);
        processor.processBlock(keyboardBuffer, noMidi);
        require(keyboardBuffer.getMagnitude(0, 128) > 1e-8f, "keyboard overflow recovery witness did not sound");
        keyboardOverflowRelease();
        std::array<juce::uint8, 4096> sysex {};
        noMidi.addEvent(juce::MidiMessage::createSysExMessage(sysex.data(), static_cast<int>(sysex.size())), 0);
        const auto allocationCount = allocationProbe::count;
        allocationProbe::active = true;
        processor.processBlock(keyboardBuffer, noMidi);
        allocationProbe::active = false;
        require(allocationProbe::count == allocationCount, "ignored SysEx allocated in callback");
        std::cout << "Plugin state validation, sample-accurate pedal/MIDI, block invariance: pass\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
