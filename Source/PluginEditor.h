#pragma once
#include "PluginProcessor.h"
#include <juce_gui_extra/juce_gui_extra.h>
#include <juce_audio_utils/juce_audio_utils.h>

class KeyraLookAndFeel final : public juce::LookAndFeel_V4
{
public:
    KeyraLookAndFeel();
    void drawRotarySlider(juce::Graphics&, int, int, int, int, float, float, float, juce::Slider&) override;
    void drawLinearSlider(juce::Graphics&, int, int, int, int, float, float, float,
        juce::Slider::SliderStyle, juce::Slider&) override;
    juce::Font getComboBoxFont(juce::ComboBox&) override;
};

// One of the two views above the pedals: the voicing knobs or the build's.
class KeyraTab final : public juce::Button
{
public:
    explicit KeyraTab(const juce::String& name);
    void paintButton(juce::Graphics&, bool highlighted, bool down) override;
};

class KeyraPedal final : public juce::Button
{
public:
    KeyraPedal();
    void setTravel(float value);
    std::function<void(bool)> onHold;
    void paintButton(juce::Graphics&, bool highlighted, bool down) override;
private:
    float travel = 0;
    bool held = false;
};

// The painted KEYRA title's About box: transparent, so the panel is unchanged.
class KeyraAboutArea final : public juce::Component, public juce::SettableTooltipClient
{
public:
    std::function<void()> onClick;
    void mouseUp(const juce::MouseEvent& event) override
    {
        if (getLocalBounds().contains(event.getPosition()) && onClick)
            onClick();
    }
};

class KeyraAudioProcessorEditor final : public juce::AudioProcessorEditor, private juce::Timer,
    private juce::MidiKeyboardState::Listener
{
public:
    explicit KeyraAudioProcessorEditor(KeyraAudioProcessor&);
    ~KeyraAudioProcessorEditor() override;
    void paint(juce::Graphics&) override;
    void resized() override;
private:
    void timerCallback() override;
    void handleNoteOn(juce::MidiKeyboardState*, int, int note, float velocity) override;
    void handleNoteOff(juce::MidiKeyboardState*, int, int note, float) override;
    void showBuild(bool);
    float value(const char* id) const;
    KeyraAudioProcessor& processor;
    KeyraLookAndFeel look;
    juce::ComboBox program, piano, quality;
    std::unique_ptr<juce::AudioProcessorValueTreeState::ComboBoxAttachment> pianoAttachment, qualityAttachment;
    std::array<juce::Slider, 10> controls;
    std::array<KeyraPedal, 3> pedals; // physical order: soft, sostenuto, sustain
    std::array<std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment>, 10> attachments;
    KeyraTab voicingTab { "VOICING" }, buildTab { "BUILD" };
    std::array<juce::Slider, 7> build; // keyra::buildToward's order
    std::array<std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment>, 7> buildAttachments;
    bool upright = false;
    juce::MidiKeyboardState keyboardState;
    juce::MidiKeyboardComponent keyboard { keyboardState, juce::MidiKeyboardComponent::horizontalKeyboard };
    juce::TooltipWindow tooltips { this, 750 };
    KeyraAboutArea about;
    juce::ScopedMessageBox aboutMessageBox;
    float level = 0;
    bool activity = false;
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(KeyraAudioProcessorEditor)
};
