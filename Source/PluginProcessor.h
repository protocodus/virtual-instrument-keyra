#pragma once

#include <juce_audio_processors/juce_audio_processors.h>
#include "DSP/KeyraEngine.h"
#include "DSP/KeyraPresets.h"
#include <array>
#include <atomic>

class KeyraAudioProcessor final : public juce::AudioProcessor
{
public:
    KeyraAudioProcessor();
    void prepareToPlay(double sampleRate, int samplesPerBlock) override;
    void releaseResources() override { reset(); }
    void reset() override;
    bool isBusesLayoutSupported(const BusesLayout&) const override;
    void processBlock(juce::AudioBuffer<float>&, juce::MidiBuffer&) override;
    using AudioProcessor::processBlock;
    juce::AudioProcessorEditor* createEditor() override;
    bool hasEditor() const override { return true; }
    const juce::String getName() const override { return "Keyra"; }
    bool acceptsMidi() const override { return true; }
    bool producesMidi() const override { return false; }
    bool isMidiEffect() const override { return false; }
    double getTailLengthSeconds() const override { return 60.0; }
    int getNumPrograms() override { return static_cast<int>(keyra::factoryPresets.size()); }
    int getCurrentProgram() override { return currentProgram.load(std::memory_order_relaxed); }
    void setCurrentProgram(int) override;
    const juce::String getProgramName(int) override;
    void changeProgramName(int, const juce::String&) override {}
    void getStateInformation(juce::MemoryBlock&) override;
    void setStateInformation(const void*, int) override;
    juce::AudioProcessorValueTreeState parameters;
    std::atomic<float> outputPeak { 0.0f };
    std::atomic<bool> noteActivity { false };
    // Render-thread snapshots for pedal travel. Performance CC/keyswitch
    // values never enter persistent parameter state just to animate the UI.
    std::atomic<float> softLevel { 0.0f }, sostenutoLevel { 0.0f }, sustainLevel { 0.0f };
    // Single GUI producer, single audio consumer; keyboard gestures never
    // acquire a message-thread lock or grow a MIDI buffer on the audio thread.
    void enqueueKeyboard(bool down, int note, float velocity) noexcept;

private:
    static juce::AudioProcessorValueTreeState::ParameterLayout createLayout();
    void dispatch(const juce::MidiMessage&) noexcept;
    void publishPedals() noexcept;
    keyra::Engine engine;
    std::array<std::atomic<float>*, 10> values {};
    bool prepared = false;
    std::atomic<int> currentProgram { 0 };
    struct KeyboardEvent { bool down; int note; float velocity; };
    std::array<KeyboardEvent, 256> keyboardQueue {};
    std::atomic<unsigned> keyboardWrite { 0 }, keyboardRead { 0 };
    std::atomic<bool> keyboardOverflow { false };
    std::array<bool, 97> keyboardHeld {}; // MIDI 12..108, including pedal keyswitches
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(KeyraAudioProcessor)
};
