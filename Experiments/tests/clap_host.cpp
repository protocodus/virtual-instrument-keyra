// Headless integration host: exercises the built shared object through the public CLAP ABI.
#include <clap/clap.h>
#include <algorithm>
#include <array>
#include <atomic>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <future>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>
#ifdef _WIN32
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#else
#include <dlfcn.h>
#endif

namespace {
void require(bool result, const char *message) {
    if (!result) throw std::runtime_error(message);
}
struct Library {
#ifdef _WIN32
    HMODULE handle;
    explicit Library(const char *path) : handle(LoadLibraryA(path)) {}
    void *symbol(const char *name) { return reinterpret_cast<void *>(GetProcAddress(handle, name)); }
    ~Library() { if (handle) FreeLibrary(handle); }
#else
    void *handle;
    explicit Library(const char *path) : handle(dlopen(path, RTLD_NOW | RTLD_LOCAL)) {
        if (!handle) std::cerr << dlerror() << '\n';
    }
    void *symbol(const char *name) { return dlsym(handle, name); }
    ~Library() { if (handle) dlclose(handle); }
#endif
};
struct Host {
    clap_host_t interface{};
    int rescans = 0;
    int processRequests = 0;
    Host() {
        interface = {CLAP_VERSION, this, "Keyra integration host", "Keyra", "", "1",
                     getExtension, request, requestProcess, request};
    }
    static void CLAP_ABI request(const clap_host_t *) {}
    static void CLAP_ABI requestProcess(const clap_host_t *host) {
        ++static_cast<Host *>(host->host_data)->processRequests;
    }
    static void CLAP_ABI rescan(const clap_host_t *host, uint32_t flags) {
        if (flags & CLAP_PARAM_RESCAN_VALUES) ++static_cast<Host *>(host->host_data)->rescans;
    }
    static void CLAP_ABI clear(const clap_host_t *, clap_id, uint32_t) {}
    static const void *CLAP_ABI getExtension(const clap_host_t *, const char *id) {
        static const clap_host_params_t params = {rescan, clear, request};
        return std::strcmp(id, CLAP_EXT_PARAMS) == 0 ? &params : nullptr;
    }
};
struct Events {
    clap_input_events_t input{this, size, get};
    clap_output_events_t output{this, push};
    std::vector<const clap_event_header_t *> incoming;
    std::vector<clap_event_note_t> outgoing;
    static uint32_t CLAP_ABI size(const clap_input_events_t *in) {
        return static_cast<uint32_t>(static_cast<const Events *>(in->ctx)->incoming.size());
    }
    static const clap_event_header_t *CLAP_ABI get(const clap_input_events_t *in, uint32_t index) {
        return static_cast<const Events *>(in->ctx)->incoming.at(index);
    }
    static bool CLAP_ABI push(const clap_output_events_t *out, const clap_event_header_t *event) {
        if (event->type != CLAP_EVENT_NOTE_END || event->size != sizeof(clap_event_note_t)) return false;
        auto *s = static_cast<Events *>(out->ctx);
        clap_event_note_t note{};
        std::memcpy(&note, event, sizeof(note));
        s->outgoing.push_back(note);
        return true;
    }
};
struct Stream {
    std::vector<uint8_t> data;
    size_t position = 0;
    size_t chunk = 3;
    clap_ostream_t output{this, write};
    clap_istream_t input{this, read};
    static int64_t CLAP_ABI write(const clap_ostream_t *out, const void *source, uint64_t size) {
        auto &s = *static_cast<Stream *>(out->ctx);
        size = std::min<uint64_t>(size, s.chunk);
        const auto *bytes = static_cast<const uint8_t *>(source);
        s.data.insert(s.data.end(), bytes, bytes + size);
        return static_cast<int64_t>(size);
    }
    static int64_t CLAP_ABI read(const clap_istream_t *in, void *destination, uint64_t size) {
        auto &s = *static_cast<Stream *>(in->ctx);
        size = std::min<uint64_t>({size, s.chunk, s.data.size() - s.position});
        std::memcpy(destination, s.data.data() + s.position, static_cast<size_t>(size));
        s.position += static_cast<size_t>(size);
        return static_cast<int64_t>(size);
    }
};
struct Instance {
    const clap_plugin_t *plugin = nullptr;
    const clap_plugin_params_t *params = nullptr;
    const clap_plugin_state_t *state = nullptr;
    Host host;
    bool active = false;
    bool processing = false;
    explicit Instance(const clap_plugin_factory_t *factory, const char *id) {
        plugin = factory->create_plugin(factory, &host.interface, id);
        require(plugin && plugin->init(plugin), "create/init");
        params = static_cast<const clap_plugin_params_t *>(plugin->get_extension(plugin, CLAP_EXT_PARAMS));
        state = static_cast<const clap_plugin_state_t *>(plugin->get_extension(plugin, CLAP_EXT_STATE));
        require(params && state, "params/state extensions");
    }
    ~Instance() {
        if (!plugin) return;
        if (processing) plugin->stop_processing(plugin);
        if (active) plugin->deactivate(plugin);
        plugin->destroy(plugin);
    }
    void start(double rate = 48000, uint32_t max = 1024) {
        require(plugin->activate(plugin, rate, 1, max), "activate");
        active = true;
        require(plugin->start_processing(plugin), "start processing");
        processing = true;
    }
    void stop() {
        plugin->stop_processing(plugin); processing = false;
        plugin->deactivate(plugin); active = false;
    }
    double value(uint32_t id) const {
        double result = -999;
        require(params->get_value(plugin, id, &result), "get parameter");
        return result;
    }
    void set(uint32_t id, double value) {
        clap_event_param_value_t event{{sizeof(event), 0, 0, CLAP_EVENT_PARAM_VALUE, 0},
                                     id, nullptr, -1, -1, -1, -1, value};
        Events events;
        events.incoming = {&event.header};
        params->flush(plugin, &events.input, &events.output);
    }
    std::array<std::vector<float>, 2> render(uint32_t count, Events *events = nullptr) {
        std::array<std::vector<float>, 2> samples{std::vector<float>(count, -9), std::vector<float>(count, -9)};
        float *pointers[] = {samples[0].data(), samples[1].data()};
        clap_audio_buffer_t output{pointers, nullptr, 2, 0, 0};
        clap_process_t process{};
        process.frames_count = count;
        process.audio_outputs = &output;
        process.audio_outputs_count = 1;
        process.in_events = events ? &events->input : nullptr;
        process.out_events = events ? &events->output : nullptr;
        require(plugin->process(plugin, &process) != CLAP_PROCESS_ERROR, "process");
        for (const auto &channel : samples)
            for (float x : channel) require(std::isfinite(x), "nonfinite output");
        return samples;
    }
};
clap_event_note_t note(uint16_t type, uint32_t time, int key, int channel, int id = -1) {
    return {{sizeof(clap_event_note_t), time, 0, type, 0}, id, 0,
            static_cast<int16_t>(channel), static_cast<int16_t>(key), .7};
}
double energy(const std::array<std::vector<float>, 2> &samples, size_t begin = 0, size_t end = SIZE_MAX) {
    double result = 0;
    for (const auto &channel : samples)
        for (size_t i = begin; i < std::min(end, channel.size()); ++i) result += channel[i] * channel[i];
    return result;
}
void run(const clap_plugin_entry_t *entry) {
    require(entry && clap_version_is_compatible(entry->clap_version), "entry and CLAP version");
    require(entry->init("test") && entry->init("test"), "reentrant entry init");
    const auto *factory = static_cast<const clap_plugin_factory_t *>(entry->get_factory(CLAP_PLUGIN_FACTORY_ID));
    require(factory && factory->get_plugin_count(factory) == 1, "plugin factory");
    const auto *descriptor = factory->get_plugin_descriptor(factory, 0);
    require(descriptor && descriptor->id && !factory->get_plugin_descriptor(factory, 1), "descriptor indexing");
    require(!factory->create_plugin(factory, nullptr, descriptor->id), "reject null host");
    {
        Instance first(factory, descriptor->id);
        Instance second(factory, descriptor->id);
        require(first.params->count(first.plugin) == 10, "compact parameter count");
        for (uint32_t i = 0; i < first.params->count(first.plugin); ++i) {
            clap_param_info_t info{};
            require(first.params->get_info(first.plugin, i, &info), "parameter info");
            require(info.id == i && info.name[0] && info.min_value <= info.default_value &&
                    info.default_value <= info.max_value && (info.flags & CLAP_PARAM_IS_AUTOMATABLE), "parameter metadata");
            char text[128]{};
            double parsed = 0;
            require(first.params->value_to_text(first.plugin, i, info.default_value, text, sizeof(text)) &&
                    first.params->text_to_value(first.plugin, i, text, &parsed) &&
                    std::abs(parsed - info.default_value) < .00051, "parameter text roundtrip");
        }
        clap_param_info_t bad{};
        require(!first.params->get_info(first.plugin, 1000, &bad), "invalid parameter index");
        double untouched = 77;
        require(!first.params->get_value(first.plugin, 1000, &untouched) && untouched == 77, "invalid parameter id");
        const auto *audio = static_cast<const clap_plugin_audio_ports_t *>(first.plugin->get_extension(first.plugin, CLAP_EXT_AUDIO_PORTS));
        const auto *notes = static_cast<const clap_plugin_note_ports_t *>(first.plugin->get_extension(first.plugin, CLAP_EXT_NOTE_PORTS));
        clap_audio_port_info_t audioInfo{};
        clap_note_port_info_t noteInfo{};
        require(audio && audio->count(first.plugin, true) == 0 && audio->count(first.plugin, false) == 1 &&
                audio->get(first.plugin, 0, false, &audioInfo) && audioInfo.channel_count == 2 &&
                !(audioInfo.flags & CLAP_AUDIO_PORT_SUPPORTS_64BITS), "stereo float32 port");
        require(notes && notes->count(first.plugin, true) == 1 && notes->get(first.plugin, 0, true, &noteInfo) &&
                (noteInfo.supported_dialects & CLAP_NOTE_DIALECT_MIDI) &&
                (noteInfo.supported_dialects & CLAP_NOTE_DIALECT_CLAP), "note dialects");
        require(!first.plugin->get_extension(first.plugin, "no.such.extension"), "unknown extension");
        require(!first.plugin->activate(first.plugin, std::numeric_limits<double>::quiet_NaN(), 1, 64), "reject invalid rate");
        first.set(0, 2); first.set(3, .27); first.set(9, -12);
        first.set(3, std::numeric_limits<double>::quiet_NaN());
        require(first.value(3) == .27, "reject NaN parameter");
        Stream saved;
        require(first.state->save(first.plugin, &saved.output), "state partial write");
        require(saved.data.size() == 136, "portable versioned state size");
        require(second.state->load(second.plugin, &saved.input), "state partial read");
        require(second.value(0) == 2 && second.value(3) == .27 && second.value(9) == -12, "state values");
        require(second.host.rescans == 1 && second.host.processRequests == 1, "state host notifications");
        Stream broken;
        broken.data = saved.data;
        broken.data.resize(broken.data.size() - 1);
        require(!second.state->load(second.plugin, &broken.input) && second.value(3) == .27, "reject truncated state atomically");
        broken.data = saved.data; broken.position = 0; broken.data[8] = 2;
        require(!second.state->load(second.plugin, &broken.input), "reject unknown state version");
        broken.data = saved.data; broken.position = 0;
        std::fill(broken.data.begin() + 20, broken.data.begin() + 28, 255);
        require(!second.state->load(second.plugin, &broken.input), "reject nonfinite state");
        first.start(); second.start();
        require(energy(first.render(17)) == 0 && energy(second.render(1)) == 0, "initial silence and tiny blocks");
        auto on = note(CLAP_EVENT_NOTE_ON, 137, 60, 2, 1234);
        Events events;
        events.incoming = {&on.header};
        const auto played = first.render(1024, &events);
        require(energy(played, 0, 137) == 0 && energy(played, 137) > 1e-12, "sample accurate note onset");
        require(energy(second.render(1024)) == 0, "instance isolation");
        // Changing a main-thread state while activated transfers atomically on next process.
        first.set(3, .9);
        saved.position = 0;
        require(first.state->load(first.plugin, &saved.input) && first.value(3) == .27, "active state load");
        first.render(17);
        auto wrongOff = note(CLAP_EVENT_NOTE_OFF, 0, 60, 1, 1234);
        events.incoming = {&wrongOff.header};
        require(energy(first.render(257, &events)) > 1e-12, "note channel isolation");
        auto choke = note(CLAP_EVENT_NOTE_CHOKE, 0, 60, 2, 1234);
        events.incoming = {&choke.header};
        first.render(64, &events);
        require(std::any_of(events.outgoing.begin(), events.outgoing.end(), [](const auto &e) {
            return e.note_id == 1234 && e.key == 60 && e.channel == 2;
        }), "native NOTE_END after choke");
        first.plugin->reset(first.plugin);
        require(energy(first.render(257)) == 0, "reset clears voices and tails");
        require(first.value(3) == .27, "reset preserves parameters");
        // Malformed, unknown-space, out-of-block, and unsorted events cannot alter output.
        auto malformed = note(CLAP_EVENT_NOTE_ON, 0, 60, 0);
        malformed.header.size = sizeof(clap_event_header_t);
        auto otherSpace = note(CLAP_EVENT_NOTE_ON, 0, 60, 0);
        otherSpace.header.space_id = 80;
        auto outside = note(CLAP_EVENT_NOTE_ON, 64, 60, 0);
        auto invalid = note(CLAP_EVENT_NOTE_ON, 0, 60, -1);
        events.incoming = {nullptr, &malformed.header, &otherSpace.header, &outside.header, &invalid.header};
        require(energy(first.render(64, &events)) == 0, "malformed events ignored");
        auto sortedOn = note(CLAP_EVENT_NOTE_ON, 32, 60, 0, 44);
        auto unsortedChoke = note(CLAP_EVENT_NOTE_CHOKE, 16, 60, 0, 44);
        events.incoming = {&sortedOn.header, &unsortedChoke.header};
        const auto unsorted = first.render(257, &events);
        require(energy(unsorted, 0, 32) == 0 && energy(unsorted, 32) > 1e-12,
                "descending event timestamp ignored");
        first.plugin->reset(first.plugin);
        clap_event_midi_t midi{{sizeof(midi), 5, 0, CLAP_EVENT_MIDI, 0}, 0, {0x90, 64, 90}};
        events.incoming = {&midi.header};
        require(energy(first.render(257, &events), 5) > 1e-12, "MIDI note-on");
        first.plugin->reset(first.plugin);
        midi.data[2] = 0; midi.header.time = 0;
        require(energy(first.render(64, &events)) == 0, "MIDI zero velocity note-off");
        // Main-thread state loads can overlap audio processing/automation; only atomics cross.
        std::atomic<bool> begin{false};
        auto loader = std::async(std::launch::async, [&] {
            while (!begin.load(std::memory_order_acquire)) {}
            for (int i = 0; i < 200; ++i) {
                Stream restored;
                restored.data = saved.data;
                if (!first.state->load(first.plugin, &restored.input)) return false;
            }
            return true;
        });
        begin.store(true, std::memory_order_release);
        for (int i = 0; i < 200; ++i) {
            first.set(3, (i % 100) / 100.0);
            first.render(17);
        }
        require(loader.get(), "concurrent active state loads");
        // Changing sample rate requires deactivation, never a process-time allocation.
        first.stop(); first.start(44100, 257);
        require(energy(first.render(1)) == 0, "reactivation at new sample rate");
        clap_process_t missing{};
        missing.frames_count = 1;
        require(first.plugin->process(first.plugin, &missing) == CLAP_PROCESS_ERROR, "reject missing audio buffer");
    }
    entry->deinit(); entry->deinit();
}
} // namespace
int main(int argc, char **argv) {
    try {
        require(argc == 2, "usage: keyra_clap_host /path/to/Keyra.clap");
        Library library(argv[1]);
        require(library.handle != nullptr, "load shared plugin");
        run(static_cast<const clap_plugin_entry_t *>(library.symbol("clap_entry")));
        std::cout << "CLAP ABI integration: passed\n";
        return 0;
    } catch (const std::exception &error) {
        std::cerr << "CLAP ABI integration: " << error.what() << '\n';
        return 1;
    }
}
