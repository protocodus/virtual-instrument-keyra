#include "PluginProcessor.h"
#include <cmath>
#include <iostream>
#include <stdexcept>
#include <cstdlib>
#include <new>

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
juce::StringArray weightIds()
{
    juce::StringArray result;
    for (size_t part = 0; part < buildParts.size(); ++part)
        for (size_t piano = 0; piano < keyra::pianoCount; ++piano) result.add(weightId(part, piano));
    return result;
}
// Whether one part's weights, or every part's, are the mix.
bool weightsAre(KeyraAudioProcessor& processor, const keyra::Mix& mix, int only = -1)
{
    for (size_t part = 0; part < buildParts.size(); ++part)
        if (only < 0 || part == static_cast<size_t>(only))
            for (size_t piano = 0; piano < keyra::pianoCount; ++piano)
                if (std::abs(processor.parameters.getRawParameterValue(weightId(part, piano))->load() - mix[piano]) > 1e-6f)
                    return false;
    return true;
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
        set(gui, "resonance", 0);
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
        KeyraAudioProcessor processor;
        set(processor, "brightness", .83f);
        set(processor, "mute", .37f);
        set(processor, "tuning", 442.3f);
        juce::MemoryBlock state;
        processor.getStateInformation(state);
        KeyraAudioProcessor restored;
        restored.setStateInformation(state.getData(), static_cast<int>(state.getSize()));
        require(std::abs(restored.parameters.getRawParameterValue("brightness")->load() - .83f) < 1e-5f, "brightness not restored");
        require(std::abs(restored.parameters.getRawParameterValue("tuning")->load() - 442.3f) < 1e-3f, "tuning not restored");
        const auto before = restored.parameters.copyState().toXmlString();
        const auto bad = [&state](const char* value) {
            auto xml = juce::AudioProcessor::getXmlFromBinary(state.getData(), static_cast<int>(state.getSize()));
            for (auto* parameter : xml->getChildIterator())
                if (parameter->getStringAttribute("id") == "brightness") parameter->setAttribute("value", value);
            juce::MemoryBlock result;
            juce::AudioProcessor::copyXmlToBinary(*xml, result);
            return result;
        };
        for (const auto* value : { "NaN", "900", "-1", "garbage", "0.5junk" }) {
            const auto data = bad(value);
            restored.setStateInformation(data.getData(), static_cast<int>(data.getSize()));
            require(restored.parameters.copyState().toXmlString() == before, "invalid state changed parameters");
        }
        {
            // An upright preset takes every part from the upright, which the
            // session keeps. A session saved before the piano choice existed
            // has no weights: it loads, and plays the grand it was made with.
            KeyraAudioProcessor upright;
            upright.setCurrentProgram(5);
            require(weightsAre(upright, keyra::only(keyra::Piano::upright)), "an upright preset did not take the upright's parts");
            juce::MemoryBlock saved;
            upright.getStateInformation(saved);
            KeyraAudioProcessor reopened;
            reopened.setStateInformation(saved.getData(), static_cast<int>(saved.getSize()));
            require(weightsAre(reopened, keyra::only(keyra::Piano::upright)), "the upright was not restored");
            const auto older = edited(state, weightIds(), {});
            reopened.setStateInformation(older.getData(), static_cast<int>(older.getSize()));
            require(weightsAre(reopened, keyra::only(keyra::Piano::grand))
                && std::abs(reopened.parameters.getRawParameterValue("brightness")->load() - .83f) < 1e-5f,
                "a session saved before the piano choice did not load as the grand");
            // A session saved when the build chose a piano and moved each
            // part toward the other's loads as the same mixes, and one past
            // the eighth preset keeps its program.
            const auto chosen = edited(state, weightIds(), {
                { "model", "1" }, { "strings", "0.25" }, { "hammers", "0" }, { "soundboard", "1" }, { "action", "0.5" } });
            reopened.setStateInformation(chosen.getData(), static_cast<int>(chosen.getSize()));
            const auto toward = keyra::buildToward(keyra::Piano::upright, keyra::Piano::grand, .25f, 0, 1, .5f, 0, 0, 0);
            require(weightsAre(reopened, toward.strings, 0) && weightsAre(reopened, toward.hammers, 1)
                && weightsAre(reopened, toward.soundboard, 2) && weightsAre(reopened, toward.action, 3),
                "a session saved with a piano and its parts did not load as the same mixes");
            const auto future = edited(state, {}, { { "model", "1" } });
            reopened.setStateInformation(future.getData(), static_cast<int>(future.getSize()));
            require(weightsAre(reopened, toward.strings, 0), "a session with both a piano and the weights was not refused");
            KeyraAudioProcessor thirds;
            const auto last = static_cast<int>(keyra::factoryPresets.size()) - 1;
            thirds.setCurrentProgram(last);
            juce::MemoryBlock lastSaved;
            thirds.getStateInformation(lastSaved);
            reopened.setStateInformation(lastSaved.getData(), static_cast<int>(lastSaved.getSize()));
            require(reopened.getCurrentProgram() == last, "a program past the eighth was not restored");
        }
        {
            // Quality stays with the session, not with presets, and a session
            // saved before the choice existed loads at full quality.
            KeyraAudioProcessor light;
            set(light, "quality", 2.0f);
            light.setCurrentProgram(1);
            require(light.parameters.getRawParameterValue("quality")->load() == 2, "a preset changed the quality");
            juce::MemoryBlock saved;
            light.getStateInformation(saved);
            KeyraAudioProcessor reopened;
            reopened.setStateInformation(saved.getData(), static_cast<int>(saved.getSize()));
            require(reopened.parameters.getRawParameterValue("quality")->load() == 2, "the quality was not restored");
            auto xml = juce::AudioProcessor::getXmlFromBinary(saved.getData(), static_cast<int>(saved.getSize()));
            for (auto* parameter : xml->getChildIterator())
                if (parameter->getStringAttribute("id") == "quality") { xml->removeChildElement(parameter, true); break; }
            juce::MemoryBlock older;
            juce::AudioProcessor::copyXmlToBinary(*xml, older);
            reopened.setStateInformation(older.getData(), static_cast<int>(older.getSize()));
            require(reopened.parameters.getRawParameterValue("quality")->load() == 0,
                "a session saved before the quality choice did not load at full quality");
        }
        {
            // A part plays each piano at its share of the part's weights: the
            // upright preset with every part's weight moved to the grand is the
            // grand, sample for sample. A preset puts the build back to its
            // own, the session keeps it, and a session saved before the
            // build's controls existed loads its piano as built. Mechanics and
            // Tube Mic reach the engine, a preset leaves them, and a session
            // saved before they existed loads the action as calibrated, heard
            // from the pair.
            const auto play = [](KeyraAudioProcessor& processor) {
                processor.prepareToPlay(48000, 128);
                juce::AudioBuffer<float> audio(2, 128);
                juce::MidiBuffer midi;
                midi.addEvent(juce::MidiMessage::noteOn(1, 60, .8f), 0);
                std::vector<float> result;
                for (int block = 0; block < 100; ++block) {
                    processor.processBlock(audio, midi);
                    midi.clear();
                    for (int channel = 0; channel < 2; ++channel)
                        for (int frame = 0; frame < 128; ++frame) result.push_back(audio.getSample(channel, frame));
                }
                return result;
            };
            KeyraAudioProcessor grand, rebuilt, upright;
            grand.setCurrentProgram(0);
            rebuilt.setCurrentProgram(5);
            upright.setCurrentProgram(5);
            for (size_t part = 0; part < buildParts.size(); ++part) {
                set(rebuilt, weightId(part, 0).toRawUTF8(), 1.0f);
                set(rebuilt, weightId(part, 1).toRawUTF8(), 0.0f);
            }
            const auto rebuiltPlays = play(rebuilt);
            require(play(grand) == rebuiltPlays, "the upright with every part the grand's did not play the grand");
            require(play(upright) != rebuiltPlays, "the build's controls did not reach the engine");
            KeyraAudioProcessor silentAction;
            silentAction.setCurrentProgram(0);
            set(silentAction, "mechanics", 0);
            require(play(silentAction) != rebuiltPlays, "Mechanics did not reach the engine");
            KeyraAudioProcessor tube;
            tube.setCurrentProgram(0);
            set(tube, "mic", 1);
            require(play(tube) != rebuiltPlays, "Tube Mic did not reach the engine");
            set(rebuilt, "soundboard3", .4f);
            set(rebuilt, "ring", -.5f);
            set(rebuilt, "mechanics", .5f);
            set(rebuilt, "mic", .3f);
            juce::MemoryBlock saved;
            rebuilt.getStateInformation(saved);
            KeyraAudioProcessor reopened;
            reopened.setStateInformation(saved.getData(), static_cast<int>(saved.getSize()));
            require(std::abs(reopened.parameters.getRawParameterValue("soundboard3")->load() - .4f) < 1e-5f
                && std::abs(reopened.parameters.getRawParameterValue("ring")->load() + .5f) < 1e-5f
                && std::abs(reopened.parameters.getRawParameterValue("mechanics")->load() - .5f) < 1e-5f
                && std::abs(reopened.parameters.getRawParameterValue("mic")->load() - .3f) < 1e-5f,
                "the build, mechanics and mic were not restored");
            rebuilt.setCurrentProgram(1);
            require(weightsAre(rebuilt, keyra::only(keyra::Piano::grand)), "a preset left the parts changed");
            for (const auto* id : { "stiffness", "unisons", "ring" })
                require(rebuilt.parameters.getRawParameterValue(id)->load() == 0, "a preset left the build changed");
            require(std::abs(rebuilt.parameters.getRawParameterValue("mic")->load() - .3f) < 1e-5f,
                "a preset moved Tube Mic");
            auto removed = weightIds();
            for (const auto* id : { "stiffness", "unisons", "ring", "mechanics", "mic" }) removed.add(id);
            const auto older = edited(saved, removed, { { "model", "1" } });
            reopened.setStateInformation(older.getData(), static_cast<int>(older.getSize()));
            require(weightsAre(reopened, keyra::only(keyra::Piano::upright)),
                "a session saved before the build controls lost its piano");
            for (const auto* id : { "stiffness", "unisons", "ring" })
                require(reopened.parameters.getRawParameterValue(id)->load() == 0,
                    "a session saved before the build controls did not load the piano as built");
            require(reopened.parameters.getRawParameterValue("mechanics")->load() == 1,
                "a session saved before Mechanics did not load the action as calibrated");
            require(reopened.parameters.getRawParameterValue("mic")->load() == 0,
                "a session saved before Tube Mic did not load the pair");
            // A host reads a parameter's text, gives it back and reads again
            // (clap-validator's param-conversions): every value must read the
            // same both times, also when the text comes back as the CLAP
            // wrapper passes it, its UTF-8 read as ASCII. The modifiers read
            // as their factors.
            for (auto* parameter : reopened.getParameters())
                for (int step = 0; step <= 2000; ++step) {
                    const auto value = static_cast<float>((step + .37) / 2000.37);
                    const auto text = parameter->getText(value, 0);
                    const juce::String asClap(juce::CharPointer_ASCII(text.toRawUTF8()));
                    require(parameter->getText(parameter->getValueForText(text), 0) == text
                        && parameter->getText(parameter->getValueForText(asClap), 0) == text,
                        "a parameter's text did not give back the value it read");
                }
            const auto read = [&reopened](const char* id, float value) {
                auto* parameter = reopened.parameters.getParameter(id);
                return parameter->getText(parameter->convertTo0to1(value), 0);
            };
            const juce::String times(juce::CharPointer_UTF8("\xc3\x97"));
            require(read("stiffness", -1) == times + "0.25" && read("unisons", 0) == times + "1.00"
                && read("unisons", 1) == times + "3.00" && read("ring", 1) == times + "2.00",
                "a modifier did not read as its factor");
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
        set(processor, "resonance", 0);
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
