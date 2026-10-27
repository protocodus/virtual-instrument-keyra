#include "Keyra.h"
#include <algorithm>
#include <cmath>

namespace {
#if defined(KEYRA_EXPERIMENTAL_FULL_MODEL)
constexpr const char* names[] = {"dynamics", "humanization", "mechanicalLevel", "width", "gain"};
constexpr double defaults[] = {.5, .65, .025, .5, .75};
#else
constexpr const char* names[] = {"instrument", "material", "mic", "tone", "dynamics", "resonance", "noise", "distance", "width", "gain"};
constexpr double defaults[] = {0, 0, 0, .5, .5, .3, .1, .15, .7, 7.0/9.0};
#endif
constexpr const char* outputs[] = {"/audio_outputs/left", "/audio_outputs/right"};
bool IsFinite(double value) noexcept {
#if defined(__GNUC__) || defined(__clang__)
    return __builtin_isfinite(value);
#else
    return std::isfinite(value);
#endif
}
double number(TJBox_Value value, double fallback = 0) noexcept {
    if (JBox_GetType(value) != kJBox_Number) return fallback;
    const double result = JBox_GetNumber(value);
    return IsFinite(result) ? result : fallback;
}
bool boolean(TJBox_Value value) noexcept {
    return JBox_GetType(value) == kJBox_Boolean && JBox_GetBoolean(value) != 0;
}
int frame(const TJBox_PropertyDiff& diff) noexcept {
    // SDK 5's documented fallback for legacy indices outside a 64-frame batch.
    return diff.fAtFrameIndex > 63 ? 63 : static_cast<int>(diff.fAtFrameIndex);
}
double velocity(TJBox_Value value) noexcept { return std::clamp(number(value), 0.0, 127.0); }
}

double CKeyra::SanitizeSampleRate(double rate) noexcept {
#if defined(KEYRA_EXPERIMENTAL_FULL_MODEL)
    // No resampler exists here. Refuse an unsupported host rate rather than
    // running a 44.1 kHz instrument under a different host clock.
    return rate == 44100 || rate == 48000 || rate == 88200 || rate == 96000 ? rate : 0;
#else
    return IsFinite(rate) && rate >= 8000 && rate <= 384000 ? rate : 44100;
#endif
}
CKeyra::CKeyra(double rate) {
    (void)fPiano.prepare(SanitizeSampleRate(rate));
    fCustom = JBox_GetMotherboardObjectRef("/custom_properties");
    fNotes = JBox_GetMotherboardObjectRef("/note_states");
    fTransport = JBox_GetMotherboardObjectRef("/transport");
    for (int i = 0; i < kParameterCount; ++i) {
        fProperties[i] = JBox_MakePropertyRef(fCustom, names[i]);
        fValues[i] = defaults[i];
    }
    fSustainRef = JBox_MakePropertyRef(fCustom, "sustainPedal");
    for (int i = 0; i < 2; ++i) {
        fOutputs[i] = JBox_GetMotherboardObjectRef(outputs[i]);
        fConnectedRefs[i] = JBox_MakePropertyRef(fOutputs[i], "connected");
    }
    // CreateNativeObject may resolve references, but it must not read the MOM.
}
void CKeyra::Snapshot() noexcept {
    for (int i = 0; i < kParameterCount; ++i)
        fValues[i] = number(JBox_LoadMOMProperty(fProperties[i]), defaults[i]);
    fSustain = std::clamp(number(JBox_LoadMOMProperty(fSustainRef)), 0.0, 1.0);
    for (int i = 0; i < 2; ++i) fConnected[i] = boolean(JBox_LoadMOMProperty(fConnectedRefs[i]));
}
bool CKeyra::Apply(const TJBox_PropertyDiff& diff, bool previous) noexcept {
    const auto value = previous ? diff.fPreviousValue : diff.fCurrentValue;
    if (diff.fObjectRef == fCustom) {
        for (int i = 0; i < kParameterCount; ++i) {
            if (JBox_IsReferencingSameProperty(diff.fPropertyRef, fProperties[i]) != 0) {
                fValues[i] = number(value, fValues[i]);
                return true;
            }
        }
        if (JBox_IsReferencingSameProperty(diff.fPropertyRef, fSustainRef) != 0) {
            fSustain = std::clamp(number(value), 0.0, 1.0);
            return true;
        }
    }
    for (int i = 0; i < 2; ++i)
        if (diff.fObjectRef == fOutputs[i] && JBox_IsReferencingSameProperty(diff.fPropertyRef, fConnectedRefs[i]) != 0)
            fConnected[i] = boolean(value);
    return false;
}
void CKeyra::Parameters() noexcept {
#if defined(KEYRA_EXPERIMENTAL_FULL_MODEL)
    keyra::FullInstrumentParameters parameters;
    parameters.dynamics = std::clamp(fValues[0], 0.0, 1.0);
    parameters.humanization = std::clamp(fValues[1], 0.0, 1.0);
    parameters.mechanicalLevel = std::clamp(fValues[2], 0.0, 1.0);
    parameters.stereoWidth = 2 * std::clamp(fValues[3], 0.0, 1.0);
    parameters.gainDb = -60 + 72 * std::clamp(fValues[4], 0.0, 1.0);
    // The experimental source contract applies controls at event offsets.
    // Large gain/width jumps need host-side smoothing before product release.
    (void)fPiano.setParameters(parameters);
#else
    for (int i = 0; i < kParameterCount; ++i) {
        double value = fValues[i];
        if (i == 9) value = -48 + 54 * std::clamp(value, 0.0, 1.0);
        fPiano.setParameter(static_cast<keyra::ParamId>(i), value);
    }
#endif
    fPiano.sustain(fSustain);
}
void CKeyra::RenderRange(int first, int last) noexcept {
    if (last <= first) return;
#if defined(KEYRA_EXPERIMENTAL_FULL_MODEL)
    if (!fPiano.process(fScratch[0] + first, fScratch[1] + first, static_cast<unsigned>(last - first))) {
        fInvalid = true; return;
    }
#else
    fPiano.process(fScratch[0] + first, fScratch[1] + first, static_cast<unsigned>(last - first));
#endif
    for (int i = first; i < last; ++i) {
        const float l = fScratch[0][i], r = fScratch[1][i];
        if (!IsFinite(l) || !IsFinite(r)) { fInvalid = true; continue; }
        if (fConnected[0] && fConnected[1]) {
            fAudio[0][i] = l; fAudio[1][i] = r;
        } else if (fConnected[0] || fConnected[1]) {
            fAudio[fConnected[0] ? 0 : 1][i] = .5f * (l + r);
        }
    }
    for (int i = 0; i < 2; ++i) fUsed[i] = fUsed[i] || fConnected[i];
}
void CKeyra::WriteOutputs() noexcept {
    if (fInvalid) { fPiano.reset(); return; }
    for (int output = 0; output < 2; ++output) {
        if (!fUsed[output]) continue;
        bool audible = false;
        for (float sample : fAudio[output])
            if (sample >= kJBox_SilentThreshold || sample <= -kJBox_SilentThreshold) { audible = true; break; }
        if (!audible) continue; // An unwritten Reason output is silent.
        const auto buffer = JBox_LoadMOMPropertyByTag(fOutputs[output], kJBox_AudioOutputBuffer);
        JBox_SetDSPBufferData(buffer, 0, kFrames, fAudio[output]);
    }
}
void CKeyra::RenderBatch(const TJBox_PropertyDiff diffs[], TJBox_UInt32 count) noexcept {
    if (!diffs) count = 0;
    const double reset = JBox_LoadMOMPropertyAsNumber(fTransport, kJBox_TransportRequestResetAudio);
    if (IsFinite(reset) && reset != 0 && reset != fResetCounter) {
        fResetCounter = reset;
        fPiano.reset(); fHeld.fill(false); fLoaded = false;
    }
    if (!fLoaded) {
        Snapshot();
        // MOM holds the end-of-batch state. Reverse later diffs before playing
        // frame zero; replay them once at their own frame below.
        for (TJBox_UInt32 i = count; i > 0; --i)
            if (frame(diffs[i - 1]) > 0) Apply(diffs[i - 1], true);
        Parameters();
        fPiano.reset(); // Saved controls start settled, not gliding from defaults.
        fPiano.sustain(fSustain);
        fLoaded = true;
    }
    for (auto& channel : fAudio) for (auto& sample : channel) sample = 0;
    fUsed.fill(false); fInvalid = false;
    int cursor = 0;
    TJBox_UInt32 index = 0;
    while (index < count) {
        const int at = frame(diffs[index]);
        if (at < cursor) { ++index; continue; } // Defensive malformed ordering.
        RenderRange(cursor, at); cursor = at;
        TJBox_UInt32 end = index + 1;
        while (end < count && frame(diffs[end]) == at) ++end;
        bool changed = false;
        for (TJBox_UInt32 i = index; i < end; ++i)
            if (diffs[i].fObjectRef != fNotes) changed = Apply(diffs[i], false) || changed;
        if (changed) Parameters(); // Controls and pedal precede same-frame strikes.
        std::array<unsigned, 128> pendingOff{};
        for (TJBox_UInt32 i = index; i < end; ++i) {
            const auto& diff = diffs[i];
            if (diff.fObjectRef != fNotes || static_cast<unsigned>(diff.fPropertyTag) > 127 || velocity(diff.fCurrentValue) > 0) continue;
            const auto note = static_cast<unsigned>(diff.fPropertyTag);
            if (fHeld[note]) { fPiano.noteOff(static_cast<int>(note)); fHeld[note] = false; }
            else ++pendingOff[note];
        }
        for (TJBox_UInt32 i = index; i < end; ++i) {
            const auto& diff = diffs[i];
            if (diff.fObjectRef != fNotes || static_cast<unsigned>(diff.fPropertyTag) > 127) continue;
            const double speed = velocity(diff.fCurrentValue);
            if (speed <= 0) continue;
            const auto note = static_cast<unsigned>(diff.fPropertyTag);
#if defined(KEYRA_EXPERIMENTAL_FULL_MODEL)
            // Acceptance may queue a strike until this key's hammer separates.
            // The shared physical core owns its string and hammer history.
            fHeld[note] = fPiano.noteOn(static_cast<int>(note), speed / 127.0);
#else
            fPiano.noteOn(static_cast<int>(note), speed / 127.0); fHeld[note] = true;
#endif
            if (pendingOff[note]) { --pendingOff[note]; fPiano.noteOff(static_cast<int>(note)); fHeld[note] = false; }
        }
        index = end;
    }
    RenderRange(cursor, kFrames);
    WriteOutputs();
}
