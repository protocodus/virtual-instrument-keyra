// Keyra CLAP adapter. The DSP lives in keyra_core; CLAP headers retain their MIT license.
#include <clap/clap.h>
#include <keyra/Piano.h>
#include <keyra/Parameters.h>

#include <algorithm>
#include <array>
#include <atomic>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <new>

namespace {
constexpr size_t parameterCount = static_cast<size_t>(keyra::ParamId::Count);
static_assert(parameterCount == 10, "Update state compatibility when adding parameters");
static_assert(std::atomic<double>::is_always_lock_free,
              "The CLAP adapter requires lock-free double atomics on this architecture");
const char *const features[] = {CLAP_PLUGIN_FEATURE_INSTRUMENT,
                                "piano",
                                CLAP_PLUGIN_FEATURE_STEREO, nullptr};
const clap_plugin_descriptor_t descriptor = {
    CLAP_VERSION, "io.protocodus.keyra", "Keyra", "Protocodus", "", "", "",
    "0.2.0", "Sample-free modeled piano (development preview)", features};
const char *choice(uint32_t id, int index) noexcept {
    if (id == 0 && index >= 0 && static_cast<size_t>(index) < keyra::kInstruments.size()) return keyra::kInstruments[index];
    if (id == 1 && index >= 0 && static_cast<size_t>(index) < keyra::kMaterials.size()) return keyra::kMaterials[index];
    if (id == 2 && index >= 0 && static_cast<size_t>(index) < keyra::kMicrophones.size()) return keyra::kMicrophones[index];
    return nullptr;
}

double bounded(uint32_t id, double value) noexcept {
    const auto &info = keyra::kParameters[id];
    value = std::clamp(value, info.min, info.max);
    // CLAP stepped parameters explicitly truncate, rather than round.
    return info.stepped ? std::trunc(value) : value;
}

bool writeAll(const clap_ostream_t *stream, const void *source, uint64_t size) {
    if (!stream || !stream->write) return false;
    auto *bytes = static_cast<const uint8_t *>(source);
    while (size) {
        const int64_t count = stream->write(stream, bytes, size);
        if (count <= 0 || static_cast<uint64_t>(count) > size) return false;
        bytes += count;
        size -= static_cast<uint64_t>(count);
    }
    return true;
}
bool readAll(const clap_istream_t *stream, void *destination, uint64_t size) {
    if (!stream || !stream->read) return false;
    auto *bytes = static_cast<uint8_t *>(destination);
    while (size) {
        const int64_t count = stream->read(stream, bytes, size);
        if (count <= 0 || static_cast<uint64_t>(count) > size) return false;
        bytes += count;
        size -= static_cast<uint64_t>(count);
    }
    return true;
}
void put32(uint8_t *out, uint32_t value) noexcept {
    for (int i = 0; i < 4; ++i) out[i] = static_cast<uint8_t>(value >> (8 * i));
}
uint32_t get32(const uint8_t *in) noexcept {
    uint32_t value = 0;
    for (int i = 0; i < 4; ++i) value |= static_cast<uint32_t>(in[i]) << (8 * i);
    return value;
}
void putDouble(uint8_t *out, double value) noexcept {
    static_assert(sizeof(double) == 8 && std::numeric_limits<double>::is_iec559,
                  "State uses IEEE-754 binary64");
    uint64_t bits;
    std::memcpy(&bits, &value, 8);
    for (int i = 0; i < 8; ++i) out[i] = static_cast<uint8_t>(bits >> (8 * i));
}
double getDouble(const uint8_t *in) noexcept {
    uint64_t bits = 0;
    for (int i = 0; i < 8; ++i) bits |= static_cast<uint64_t>(in[i]) << (8 * i);
    double value;
    std::memcpy(&value, &bits, 8);
    return value;
}

struct TrackedNote {
    int key = -1;
    int channel = -1;
    int32_t id = -1;
    bool active = false;
};

class Plugin {
public:
    clap_plugin_t interface{};
    const clap_host_t *host;
    const clap_host_params_t *hostParams = nullptr;
    keyra::Piano piano;
    // The main thread only touches atomics. Audio state belongs to process/flush/reset.
    std::array<std::atomic<double>, parameterCount> values;
    std::array<double, parameterCount> applied{};
    // A bounded seqlock read avoids waiting on the audio thread during a state load.
    std::atomic<uint32_t> stateGeneration{0};
    // Includes a bounded backlog for NOTE_END events rejected by a full host queue.
    std::array<TrackedNote, 256> tracked{};
    bool initialized = false;
    bool active = false;
    bool processing = false;
    uint32_t maxFrames = 0;

    explicit Plugin(const clap_host_t *h) : host(h) {
        for (size_t i = 0; i < parameterCount; ++i) {
            values[i].store(keyra::kParameters[i].defaultValue, std::memory_order_relaxed);
            applied[i] = std::numeric_limits<double>::quiet_NaN();
        }
        interface = {&descriptor, this, init, destroy, activate, deactivate,
                     startProcessing, stopProcessing, reset, process, getExtension, onMainThread};
    }
    static Plugin &self(const clap_plugin_t *plugin) noexcept {
        return *static_cast<Plugin *>(plugin->plugin_data);
    }
    void synchronize() noexcept {
        const uint32_t before = stateGeneration.load(std::memory_order_acquire);
        if (before & 1u) return;
        std::array<double, parameterCount> snapshot{};
        for (size_t i = 0; i < parameterCount; ++i)
            snapshot[i] = values[i].load(std::memory_order_relaxed);
        std::atomic_thread_fence(std::memory_order_acquire);
        if (stateGeneration.load(std::memory_order_relaxed) != before) return;
        for (size_t i = 0; i < parameterCount; ++i) {
            if (snapshot[i] == applied[i]) continue;
            piano.setParameter(static_cast<keyra::ParamId>(i), snapshot[i]);
            applied[i] = snapshot[i];
        }
    }
    void setValue(uint32_t id, double value) noexcept {
        if (id >= parameterCount || !std::isfinite(value)) return;
        value = bounded(id, value);
        values[id].store(value, std::memory_order_relaxed);
        // Called on the audio thread when active; on main only when deactivated.
        if (active) {
            piano.setParameter(static_cast<keyra::ParamId>(id), value);
            applied[id] = value;
        }
    }
    void track(const clap_event_note_t &note, const clap_output_events_t *out) noexcept {
        // A repeated tuple replaces its host voice. Distinct IDs remain independent.
        for (auto &item : tracked) {
            if (item.active && item.key == note.key && item.channel == note.channel && item.id == note.note_id) {
                return; // Same host tuple continues; do not end its replacement.
            }
        }
        for (auto &item : tracked) {
            if (!item.active) {
                item = {note.key, note.channel, note.note_id, true};
                return;
            }
        }
        // Reclaim stolen voices before admitting a new tracked tuple.
        finishNotes(note.header.time, out);
        for (auto &item : tracked) {
            if (!item.active) {
                item = {note.key, note.channel, note.note_id, true};
                return;
            }
        }
        // Defensive bound. Host receives an end instead of retaining an orphan voice.
        TrackedNote overflow{note.key, note.channel, note.note_id, true};
        emitEnd(overflow, note.header.time, out);
    }
    static bool emitEnd(const TrackedNote &note, uint32_t time,
                        const clap_output_events_t *out) noexcept {
        if (!out || !out->try_push) return false;
        const clap_event_note_t event = {{sizeof(clap_event_note_t), time,
                                         CLAP_CORE_EVENT_SPACE_ID, CLAP_EVENT_NOTE_END, 0},
                                        note.id, 0, static_cast<int16_t>(note.channel),
                                        static_cast<int16_t>(note.key), 0};
        return out->try_push(out, &event.header);
    }
    void finishNotes(uint32_t time, const clap_output_events_t *out) noexcept {
        for (auto &item : tracked) {
            if (item.active && !piano.noteActive(item.key, item.channel, item.id)) {
                if (emitEnd(item, time, out)) item.active = false;
            }
        }
    }
    void event(const clap_event_header_t *header, const clap_output_events_t *out,
               bool parametersOnly = false) noexcept {
        if (!header || header->size < sizeof(clap_event_header_t) ||
            header->space_id != CLAP_CORE_EVENT_SPACE_ID) return;
        if (header->type == CLAP_EVENT_PARAM_VALUE && header->size >= sizeof(clap_event_param_value_t)) {
            clap_event_param_value_t param;
            std::memcpy(&param, header, sizeof(param));
            if (param.note_id == -1 && param.port_index == -1 && param.channel == -1 && param.key == -1)
                setValue(param.param_id, param.value);
            return;
        }
        if (parametersOnly) return;
        if ((header->type == CLAP_EVENT_NOTE_ON || header->type == CLAP_EVENT_NOTE_OFF ||
             header->type == CLAP_EVENT_NOTE_CHOKE) && header->size >= sizeof(clap_event_note_t)) {
            clap_event_note_t note;
            std::memcpy(&note, header, sizeof(note));
            if (note.port_index < -1 || note.port_index > 0 || note.channel < -1 || note.channel > 15 ||
                note.key < -1 || note.key > 127 || note.note_id < -1) return;
            if (header->type == CLAP_EVENT_NOTE_ON) {
                if (note.port_index != 0 || note.channel < 0 || note.key < 0 ||
                    !std::isfinite(note.velocity) || note.velocity < 0 || note.velocity > 1) return;
                if (note.key < 21 || note.key > 108) {
                    track(note, out);
                    finishNotes(note.header.time, out);
                    return;
                }
                // Native CLAP zero velocity is still a note-on, unlike MIDI 1.0.
                piano.noteOn(note.key, std::max(note.velocity, 1.0 / 127.0), note.channel, note.note_id);
                track(note, out);
            } else if (header->type == CLAP_EVENT_NOTE_OFF) {
                piano.noteOff(note.key, note.channel, note.note_id);
            } else {
                piano.noteChoke(note.key, note.channel, note.note_id);
                finishNotes(header->time, out);
            }
        } else if (header->type == CLAP_EVENT_MIDI && header->size >= sizeof(clap_event_midi_t)) {
            clap_event_midi_t midi;
            std::memcpy(&midi, header, sizeof(midi));
            if (midi.port_index != 0 || midi.data[1] > 127 || midi.data[2] > 127) return;
            const int channel = midi.data[0] & 15;
            switch (midi.data[0] & 0xf0) {
            case 0x90:
                if (midi.data[2]) piano.noteOn(midi.data[1], midi.data[2] / 127.0, channel);
                else piano.noteOff(midi.data[1], channel);
                break;
            case 0x80: piano.noteOff(midi.data[1], channel); break;
            case 0xb0:
                if (midi.data[1] == 64) piano.sustain(midi.data[2] / 127.0, channel);
                else if (midi.data[1] == 123) piano.allNotesOff(channel);
                else if (midi.data[1] == 120) piano.allSoundOff(channel);
                else if (midi.data[1] == 121) piano.sustain(0, channel);
                break;
            default: break;
            }
        }
    }

    static bool CLAP_ABI init(const clap_plugin_t *p) {
        auto &s = self(p);
        if (s.initialized) return false;
        if (s.host->get_extension)
            s.hostParams = static_cast<const clap_host_params_t *>(s.host->get_extension(s.host, CLAP_EXT_PARAMS));
        s.initialized = true;
        return true;
    }
    static void CLAP_ABI destroy(const clap_plugin_t *p) { delete &self(p); }
    static bool CLAP_ABI activate(const clap_plugin_t *p, double rate, uint32_t min, uint32_t max) {
        auto &s = self(p);
        if (!s.initialized || s.active || !std::isfinite(rate) || rate < 22050 || rate > 192000 ||
            min < 1 || max < min || max > static_cast<uint32_t>(INT32_MAX)) return false;
        try {
            s.applied.fill(std::numeric_limits<double>::quiet_NaN());
            s.synchronize();
            // prepare snaps smoothing to saved values before the first strike.
            if (!s.piano.prepare(rate)) return false;
            s.tracked.fill({});
            s.maxFrames = max;
            s.active = true;
            return true;
        } catch (...) { return false; }
    }
    static void CLAP_ABI deactivate(const clap_plugin_t *p) {
        auto &s = self(p);
        s.processing = false;
        s.active = false;
        s.piano.reset();
        s.tracked.fill({});
    }
    static bool CLAP_ABI startProcessing(const clap_plugin_t *p) {
        auto &s = self(p);
        if (!s.active || s.processing) return false;
        s.processing = true;
        return true;
    }
    static void CLAP_ABI stopProcessing(const clap_plugin_t *p) { self(p).processing = false; }
    static void CLAP_ABI reset(const clap_plugin_t *p) {
        auto &s = self(p);
        s.synchronize();
        s.piano.reset();
        s.tracked.fill({});
    }
    static clap_process_status CLAP_ABI process(const clap_plugin_t *p, const clap_process_t *block) {
        auto &s = self(p);
        if (!s.active || !s.processing || !block || block->frames_count < 1 ||
            block->frames_count > s.maxFrames || block->audio_inputs_count != 0 ||
            block->audio_outputs_count != 1 || !block->audio_outputs) return CLAP_PROCESS_ERROR;
        auto &audio = block->audio_outputs[0];
        if (audio.channel_count != 2 || !audio.data32 || !audio.data32[0] || !audio.data32[1])
            return CLAP_PROCESS_ERROR;
        audio.constant_mask = 0;
        s.synchronize();
        uint32_t cursor = 0;
        if (block->in_events && block->in_events->size && block->in_events->get) {
            const uint32_t count = block->in_events->size(block->in_events);
            for (uint32_t i = 0; i < count; ++i) {
                const auto *item = block->in_events->get(block->in_events, i);
                if (!item || item->size < sizeof(clap_event_header_t) ||
                    item->time < cursor || item->time >= block->frames_count) continue;
                if (item->time > cursor) {
                    s.piano.process(audio.data32[0] + cursor, audio.data32[1] + cursor, item->time - cursor);
                    s.finishNotes(item->time, block->out_events);
                    cursor = item->time;
                }
                s.event(item, block->out_events);
            }
        }
        s.piano.process(audio.data32[0] + cursor, audio.data32[1] + cursor, block->frames_count - cursor);
        s.finishNotes(block->frames_count - 1, block->out_events);
        // Keep processing acoustic tails and pending NOTE_END retries even with no held keys.
        return CLAP_PROCESS_CONTINUE;
    }
    static const void *CLAP_ABI getExtension(const clap_plugin_t *, const char *id);
    static void CLAP_ABI onMainThread(const clap_plugin_t *) {}
};

uint32_t CLAP_ABI audioCount(const clap_plugin_t *, bool input) { return input ? 0 : 1; }
bool CLAP_ABI audioGet(const clap_plugin_t *, uint32_t index, bool input, clap_audio_port_info_t *out) {
    if (input || index != 0 || !out) return false;
    *out = {};
    out->id = 0;
    std::snprintf(out->name, sizeof(out->name), "Piano Stereo");
    out->flags = CLAP_AUDIO_PORT_IS_MAIN;
    out->channel_count = 2;
    out->port_type = CLAP_PORT_STEREO;
    out->in_place_pair = CLAP_INVALID_ID;
    return true;
}
uint32_t CLAP_ABI noteCount(const clap_plugin_t *, bool input) { return input ? 1 : 0; }
bool CLAP_ABI noteGet(const clap_plugin_t *, uint32_t index, bool input, clap_note_port_info_t *out) {
    if (!input || index != 0 || !out) return false;
    *out = {};
    out->id = 0;
    out->supported_dialects = CLAP_NOTE_DIALECT_CLAP | CLAP_NOTE_DIALECT_MIDI;
    out->preferred_dialect = CLAP_NOTE_DIALECT_CLAP;
    std::snprintf(out->name, sizeof(out->name), "Piano Notes");
    return true;
}
uint32_t CLAP_ABI paramCount(const clap_plugin_t *) { return static_cast<uint32_t>(parameterCount); }
bool CLAP_ABI paramGetInfo(const clap_plugin_t *, uint32_t index, clap_param_info_t *out) {
    if (index >= parameterCount || !out) return false;
    const auto &p = keyra::kParameters[index];
    *out = {};
    out->id = index;
    out->flags = CLAP_PARAM_IS_AUTOMATABLE | CLAP_PARAM_REQUIRES_PROCESS;
    if (p.stepped) out->flags |= CLAP_PARAM_IS_STEPPED | CLAP_PARAM_IS_ENUM;
    std::snprintf(out->name, sizeof(out->name), "%s", p.name);
    std::snprintf(out->module, sizeof(out->module), "%s", index <= 1 ? "Piano" : index == 2 || index == 7 || index == 8 ? "Microphones" : "Performance");
    out->min_value = p.min;
    out->max_value = p.max;
    out->default_value = p.defaultValue;
    return true;
}
bool CLAP_ABI paramGetValue(const clap_plugin_t *p, clap_id id, double *out) {
    if (id >= parameterCount || !out) return false;
    *out = Plugin::self(p).values[id].load(std::memory_order_relaxed);
    return true;
}
bool CLAP_ABI paramToText(const clap_plugin_t *, clap_id id, double value, char *out, uint32_t capacity) {
    if (id >= parameterCount || !std::isfinite(value) || !out || capacity == 0) return false;
    value = bounded(id, value);
    const char *label = choice(id, static_cast<int>(value));
    const int length = label ? std::snprintf(out, capacity, "%s", label) :
        id == 9 ? std::snprintf(out, capacity, "%.1f dB", value) :
                  std::snprintf(out, capacity, "%.1f %%", value * 100);
    return length >= 0 && static_cast<uint32_t>(length) < capacity;
}
bool CLAP_ABI paramFromText(const clap_plugin_t *, clap_id id, const char *text, double *out) {
    if (id >= parameterCount || !text || !out) return false;
    for (int i = 0; const char *label = choice(id, i); ++i) {
        if (std::strcmp(text, label) == 0) { *out = i; return true; }
    }
    char *end = nullptr;
    double value = std::strtod(text, &end);
    if (end == text || !std::isfinite(value)) return false;
    while (*end == ' ') ++end;
    if (id == 9 && std::strcmp(end, "dB") == 0) end += 2;
    else if (id > 2 && id < 9) {
        if (*end == '%') ++end;
        value /= 100;
    }
    while (*end == ' ') ++end;
    if (*end || value < keyra::kParameters[id].min || value > keyra::kParameters[id].max) return false;
    *out = bounded(id, value);
    return true;
}
void CLAP_ABI paramFlush(const clap_plugin_t *p, const clap_input_events_t *in,
                       const clap_output_events_t *out) {
    auto &s = Plugin::self(p);
    if (s.active) s.synchronize();
    if (!in || !in->size || !in->get) return;
    const uint32_t count = in->size(in);
    for (uint32_t i = 0; i < count; ++i) s.event(in->get(in, i), out, true);
}
bool CLAP_ABI stateSave(const clap_plugin_t *p, const clap_ostream_t *stream) {
    const auto &s = Plugin::self(p);
    std::array<uint8_t, 16 + parameterCount * 12> data{};
    std::memcpy(data.data(), "KEYRACL1", 8);
    put32(data.data() + 8, 1);
    put32(data.data() + 12, static_cast<uint32_t>(parameterCount));
    for (uint32_t i = 0; i < parameterCount; ++i) {
        put32(data.data() + 16 + 12 * i, i);
        putDouble(data.data() + 20 + 12 * i, s.values[i].load(std::memory_order_relaxed));
    }
    return writeAll(stream, data.data(), data.size());
}
bool CLAP_ABI stateLoad(const clap_plugin_t *p, const clap_istream_t *stream) {
    auto &s = Plugin::self(p);
    std::array<uint8_t, 16> header{};
    if (!readAll(stream, header.data(), header.size()) || std::memcmp(header.data(), "KEYRACL1", 8) ||
        get32(header.data() + 8) != 1) return false;
    const uint32_t count = get32(header.data() + 12);
    if (count > 1024) return false;
    std::array<double, parameterCount> snapshot{};
    std::array<bool, parameterCount> seen{};
    for (size_t i = 0; i < parameterCount; ++i) snapshot[i] = keyra::kParameters[i].defaultValue;
    for (uint32_t i = 0; i < count; ++i) {
        std::array<uint8_t, 12> record{};
        if (!readAll(stream, record.data(), record.size())) return false;
        const uint32_t id = get32(record.data());
        const double value = getDouble(record.data() + 4);
        if (!std::isfinite(value)) return false;
        if (id >= parameterCount) continue; // Future IDs do not invalidate known values.
        const auto &info = keyra::kParameters[id];
        if (seen[id] || value < info.min || value > info.max || (info.stepped && value != std::trunc(value)))
            return false;
        seen[id] = true;
        snapshot[id] = value;
    }
    s.stateGeneration.fetch_add(1, std::memory_order_acq_rel);
    for (size_t i = 0; i < parameterCount; ++i) s.values[i].store(snapshot[i], std::memory_order_relaxed);
    s.stateGeneration.fetch_add(1, std::memory_order_release);
    if (s.hostParams && s.hostParams->rescan) s.hostParams->rescan(s.host, CLAP_PARAM_RESCAN_VALUES);
    if (s.host->request_process) s.host->request_process(s.host);
    return true;
}
uint32_t CLAP_ABI latencyGet(const clap_plugin_t *) { return 0; }
const clap_plugin_audio_ports_t audioExtension = {audioCount, audioGet};
const clap_plugin_note_ports_t noteExtension = {noteCount, noteGet};
const clap_plugin_params_t paramsExtension = {paramCount, paramGetInfo, paramGetValue, paramToText, paramFromText, paramFlush};
const clap_plugin_state_t stateExtension = {stateSave, stateLoad};
const clap_plugin_latency_t latencyExtension = {latencyGet};
const void *CLAP_ABI Plugin::getExtension(const clap_plugin_t *, const char *id) {
    if (!id) return nullptr;
    if (std::strcmp(id, CLAP_EXT_AUDIO_PORTS) == 0) return &audioExtension;
    if (std::strcmp(id, CLAP_EXT_NOTE_PORTS) == 0) return &noteExtension;
    if (std::strcmp(id, CLAP_EXT_PARAMS) == 0) return &paramsExtension;
    if (std::strcmp(id, CLAP_EXT_STATE) == 0) return &stateExtension;
    if (std::strcmp(id, CLAP_EXT_LATENCY) == 0) return &latencyExtension;
    return nullptr;
}
uint32_t CLAP_ABI factoryCount(const clap_plugin_factory_t *) { return 1; }
const clap_plugin_descriptor_t *CLAP_ABI factoryDescriptor(const clap_plugin_factory_t *, uint32_t index) {
    return index == 0 ? &descriptor : nullptr;
}
const clap_plugin_t *CLAP_ABI factoryCreate(const clap_plugin_factory_t *, const clap_host_t *host, const char *id) {
    if (!host || !id || std::strcmp(id, descriptor.id) || !clap_version_is_compatible(host->clap_version)) return nullptr;
    try { return &(new Plugin(host))->interface; } catch (...) { return nullptr; }
}
const clap_plugin_factory_t factory = {factoryCount, factoryDescriptor, factoryCreate};
bool CLAP_ABI entryInit(const char *) { return true; }
void CLAP_ABI entryDeinit() {}
const void *CLAP_ABI entryFactory(const char *id) {
    return id && std::strcmp(id, CLAP_PLUGIN_FACTORY_ID) == 0 ? &factory : nullptr;
}
} // namespace
extern "C" CLAP_EXPORT const clap_plugin_entry_t clap_entry = {CLAP_VERSION, entryInit, entryDeinit, entryFactory};
