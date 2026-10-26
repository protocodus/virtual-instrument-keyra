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
        {
            KeyraAudioProcessor pedals;
            pedals.prepareToPlay(48000, 128);
            juce::AudioBuffer<float> audio(2, 128);
            juce::MidiBuffer midi;
            for (int note = 12; note <= 14; ++note)
                midi.addEvent(juce::MidiMessage::noteOn(1, note, 1.0f), 0);
            pedals.processBlock(audio, midi);
            require(audio.getMagnitude(0, 128) < 1e-12f, "pedal keyswitches produced piano notes");
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
        for (int i = 0; i < 255; ++i) processor.enqueueKeyboard(true, 60, .8f);
        processor.enqueueKeyboard(false, 60, 0);
        for (int i = 0; i < 375; ++i) processor.processBlock(keyboardBuffer, noMidi);
        require(keyboardBuffer.getMagnitude(0, 128) < 1e-5f, "keyboard overflow failed to release an already sounding GUI note");
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
