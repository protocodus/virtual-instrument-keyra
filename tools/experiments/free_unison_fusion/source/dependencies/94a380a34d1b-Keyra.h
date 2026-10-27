#pragma once
#include "Jukebox.h"
#if defined(KEYRA_EXPERIMENTAL_FULL_MODEL)
#include <keyra/FullInstrument.h>
#else
#include <keyra/Piano.h>
#endif
#include <array>

// Thin MOM/event/audio adapter. The canonical Keyra engine owns all synthesis.
class CKeyra {
public:
    static constexpr int kFrames = 64;
#if defined(KEYRA_EXPERIMENTAL_FULL_MODEL)
    static constexpr int kParameterCount = 5;
    keyra::FullInstrumentDiagnostics FullDiagnostics() const noexcept { return fPiano.diagnostics(); }
#else
    static constexpr int kParameterCount = 10;
#endif
    static double SanitizeSampleRate(double rate) noexcept;
    explicit CKeyra(double rate);
    void RenderBatch(const TJBox_PropertyDiff diffs[], TJBox_UInt32 count) noexcept;
private:
#if defined(KEYRA_EXPERIMENTAL_FULL_MODEL)
    keyra::FullInstrument fPiano;
#else
    keyra::Piano fPiano;
#endif
    TJBox_ObjectRef fCustom{}, fNotes{}, fTransport{};
    std::array<TJBox_PropertyRef, kParameterCount> fProperties{};
    TJBox_PropertyRef fSustainRef{};
    std::array<TJBox_ObjectRef, 2> fOutputs{};
    std::array<TJBox_PropertyRef, 2> fConnectedRefs{};
    std::array<double, kParameterCount> fValues{};
    std::array<bool, 2> fConnected{}, fUsed{};
    std::array<bool, 128> fHeld{};
    float fAudio[2][kFrames]{};
    float fScratch[2][kFrames]{};
    double fSustain = 0, fResetCounter = 0;
    bool fLoaded = false, fInvalid = false;
    void Snapshot() noexcept;
    bool Apply(const TJBox_PropertyDiff&, bool previous) noexcept;
    void Parameters() noexcept;
    void RenderRange(int first, int last) noexcept;
    void WriteOutputs() noexcept;
};
