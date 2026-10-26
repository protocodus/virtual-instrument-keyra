#include "PluginProcessor.h"
#include <juce_gui_extra/juce_gui_extra.h>
#include <juce_graphics/juce_graphics.h>
#include <iostream>

int main(int argc, char** argv)
{
    juce::ScopedJuceInitialiser_GUI initialiser;
    KeyraAudioProcessor processor;
    std::unique_ptr<juce::AudioProcessorEditor> editor(processor.createEditor());
    const auto mode = argc > 2 ? juce::String(argv[2]) : juce::String();
    if (mode == "--pedals-down" || mode == "--half-sustain") {
        processor.prepareToPlay(48000, 256);
        juce::AudioBuffer<float> audio(2, 256);
        juce::MidiBuffer midi;
        if (mode == "--pedals-down") {
            for (int note = 12; note <= 14; ++note)
                midi.addEvent(juce::MidiMessage::noteOn(1, note, 1.0f), 0);
        } else midi.addEvent(juce::MidiMessage::controllerEvent(1, 64, 64), 0);
        processor.processBlock(audio, midi);
        // Exercise the live render-thread snapshot -> editor timer path on
        // an already-created editor, exactly as external MIDI does in a host.
        juce::Timer::callAfterDelay(80, [] { juce::MessageManager::getInstance()->stopDispatchLoop(); });
        juce::MessageManager::getInstance()->runDispatchLoop();
    }
    const auto snapshot = editor->createComponentSnapshot(editor->getLocalBounds(), true, 1.0f);
    const juce::File output(argc > 1 ? juce::String(argv[1])
        : juce::File::getCurrentWorkingDirectory().getChildFile("keyra-editor.png").getFullPathName());
    output.getParentDirectory().createDirectory();
    juce::FileOutputStream stream(output);
    juce::PNGImageFormat png;
    if (!stream.openedOk() || !stream.setPosition(0) || stream.truncate().failed()
        || !png.writeImageToStream(snapshot, stream)) return 1;
    std::cout << output.getFullPathName() << '\n';
}
