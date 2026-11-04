cmake_minimum_required(VERSION 3.22)

if(POLICY CMP0135)
    cmake_policy(SET CMP0135 NEW)
endif()

option(KEYRA_BUILD_UNIVERSAL "Build arm64 and x86_64 slices on macOS" ON)

# These must be established before project() so CMake's compiler checks use the
# same deployment target and architectures as the final plug-in.
if(CMAKE_HOST_SYSTEM_NAME STREQUAL "Darwin")
    if(NOT DEFINED CMAKE_OSX_DEPLOYMENT_TARGET)
        set(CMAKE_OSX_DEPLOYMENT_TARGET "11.0" CACHE STRING
            "Minimum supported macOS version")
    endif()

    if(KEYRA_BUILD_UNIVERSAL AND NOT DEFINED CMAKE_OSX_ARCHITECTURES)
        set(CMAKE_OSX_ARCHITECTURES "arm64;x86_64" CACHE STRING
            "macOS architectures")
    endif()
endif()

# C is required in addition to C++: JUCE's macOS plug-in wrappers (AU and
# Standalone) compile C/Objective-C sources with non-Xcode generators too.
project(Keyra VERSION 0.4.19 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# The full physical piano research in Experiments/ is its own project and is
# not built here: `cmake -S Experiments -B Experiments/build`.
option(KEYRA_BUILD_PLUGIN "Build the JUCE plug-in and standalone app" ON)
option(KEYRA_BUILD_CLAP "Build the CLAP format through clap-juce-extensions" ON)
option(KEYRA_BUILD_TOOLS "Build the offline renderers" ON)
set(KEYRA_JUCE_PATH "" CACHE PATH
    "Optional path to a local JUCE 8.0.14 checkout (avoids downloading JUCE)")
set(KEYRA_CLAP_JUCE_EXTENSIONS_PATH "" CACHE PATH
    "Optional path to a local clap-juce-extensions checkout with submodules")

include(CTest)

option(KEYRA_ENABLE_SANITIZERS "Instrument development builds with ASan and UBSan" OFF)
option(KEYRA_BUILD_FUZZER "Build KeyraDspFuzz as a Clang libFuzzer target" OFF)
option(KEYRA_REQUIRE_PYTHON_TESTS "Fail to configure without the interpreter the Python checks need" OFF)
option(KEYRA_ENABLE_MODEL_VALIDATION_TESTS
       "Require numerical model, generated-mask and native-probe checks (NumPy/SciPy, GCC/Clang)" OFF)
if(KEYRA_ENABLE_MODEL_VALIDATION_TESTS AND NOT BUILD_TESTING)
    message(FATAL_ERROR "KEYRA_ENABLE_MODEL_VALIDATION_TESTS requires BUILD_TESTING=ON")
endif()
# The keyboard network (Tools/keyboard_network.py) is an offline experiment
# that needs PyTorch, which CI does not install; its `all` stage runs this
# self-test first.
option(KEYRA_ENABLE_NETWORK_TESTS "Require the keyboard network's self-test (NumPy, SciPy, PyTorch)" OFF)
if(KEYRA_ENABLE_NETWORK_TESTS AND NOT BUILD_TESTING)
    message(FATAL_ERROR "KEYRA_ENABLE_NETWORK_TESTS requires BUILD_TESTING=ON")
endif()
if(KEYRA_ENABLE_SANITIZERS)
    if(NOT CMAKE_CXX_COMPILER_ID MATCHES "Clang|GNU")
        message(FATAL_ERROR "KEYRA_ENABLE_SANITIZERS requires Clang or GCC")
    endif()
    add_compile_options(-fsanitize=address,undefined,float-cast-overflow
                        -fno-sanitize-recover=all -fno-omit-frame-pointer)
    add_link_options(-fsanitize=address,undefined,float-cast-overflow)
endif()

set(KEYRA_DSP_SOURCES Source/DSP/KeyraEngine.cpp)
set(KEYRA_DSP_HEADERS
    Source/DSP/KeyraEngine.h
    Source/DSP/MechanicsControl.h
    Source/DSP/KeyraPresets.h
    Source/DSP/MeasuredTypes.h
    Source/DSP/MeasuredMicData.h
    Source/DSP/MeasuredModalData.h
    Source/DSP/MeasuredUprightData.h
    Source/DSP/MeasuredVelocityInterpolation.h
    Source/DSP/OutputStage.h)

add_library(KeyraDSP STATIC ${KEYRA_DSP_SOURCES} ${KEYRA_DSP_HEADERS})
target_include_directories(KeyraDSP PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/Source")
target_compile_features(KeyraDSP PUBLIC cxx_std_20)
set_target_properties(KeyraDSP PROPERTIES POSITION_INDEPENDENT_CODE ON)
if(MSVC)
    target_compile_options(KeyraDSP PRIVATE /W4 /permissive-)
else()
    target_compile_options(KeyraDSP PRIVATE -Wall -Wextra -Wpedantic)
endif()

# The Rack Extension toolchain is C++17. Compiling the shipping engine at that
# standard here keeps Source/DSP portable for the Rack adapter.
if(NOT MSVC)
    add_library(KeyraDSPCxx17 OBJECT ${KEYRA_DSP_SOURCES})
    target_include_directories(KeyraDSPCxx17
        PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/Source")
    set_target_properties(KeyraDSPCxx17 PROPERTIES
        CXX_STANDARD 17
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF)
    target_compile_options(KeyraDSPCxx17 PRIVATE -Wall -Wextra -Wpedantic)
endif()

if(KEYRA_BUILD_PLUGIN)
    if(KEYRA_JUCE_PATH)
        if(NOT EXISTS "${KEYRA_JUCE_PATH}/CMakeLists.txt")
            message(FATAL_ERROR
                "KEYRA_JUCE_PATH does not contain a JUCE CMakeLists.txt: ${KEYRA_JUCE_PATH}")
        endif()
        add_subdirectory("${KEYRA_JUCE_PATH}"
                         "${CMAKE_CURRENT_BINARY_DIR}/JUCE" EXCLUDE_FROM_ALL)
    else()
        include(FetchContent)
        FetchContent_Declare(
            JUCE
            # JUCE 8.0.14, pinned to its immutable release commit and archive
            # checksum so automated release builds cannot follow a moved tag.
            URL https://github.com/juce-framework/JUCE/archive/2cdfca8feb300fb424002ba2c2751569e5bacb64.tar.gz
            URL_HASH SHA256=814019716960a16f8f850a1593eeb56e2f21910aff2d673f7d3513b4ebaf251d)
        FetchContent_MakeAvailable(JUCE)
    endif()

    if(KEYRA_BUILD_CLAP)
        if(KEYRA_CLAP_JUCE_EXTENSIONS_PATH)
            foreach(required_file IN ITEMS CMakeLists.txt
                    clap-libs/clap/CMakeLists.txt
                    clap-libs/clap-helpers/CMakeLists.txt)
                if(NOT EXISTS "${KEYRA_CLAP_JUCE_EXTENSIONS_PATH}/${required_file}")
                    message(FATAL_ERROR
                        "KEYRA_CLAP_JUCE_EXTENSIONS_PATH is missing ${required_file}; "
                        "use a checkout with git submodule update --init --recursive")
                endif()
            endforeach()
            add_subdirectory("${KEYRA_CLAP_JUCE_EXTENSIONS_PATH}"
                             "${CMAKE_CURRENT_BINARY_DIR}/clap-juce-extensions"
                             EXCLUDE_FROM_ALL)
        else()
            include(FetchContent)
            FetchContent_Declare(
                clap_juce_extensions
                GIT_REPOSITORY https://github.com/free-audio/clap-juce-extensions.git
                GIT_TAG c1a5ad025f95d01e03267857fa8276ebeed16500
                # Archive downloads omit these gitlinks. Fetch both dependencies
                # at the immutable revisions recorded by the wrapper commit.
                GIT_SUBMODULES clap-libs/clap clap-libs/clap-helpers
                GIT_SUBMODULES_RECURSE TRUE)
            FetchContent_MakeAvailable(clap_juce_extensions)
        endif()
    endif()

    if(APPLE)
        set(KEYRA_PLUGIN_FORMATS VST3 AU Standalone)
    else()
        set(KEYRA_PLUGIN_FORMATS VST3 Standalone)
    endif()

    # PLUGIN_MANUFACTURER_CODE and PLUGIN_CODE are the ones the 0.2.0 builds
    # shipped with: hosts recall sessions by them.
    juce_add_plugin(Keyra
        VERSION ${PROJECT_VERSION}
        COMPANY_NAME "Protocodus"
        COMPANY_WEBSITE "https://protocodus.cz"
        COMPANY_EMAIL "protocodus@proton.me"
        COMPANY_COPYRIGHT "Copyright (c) 2026 Protocodus"
        BUNDLE_ID "cz.protocodus.keyra"
        PLUGIN_MANUFACTURER_CODE Ptoc
        PLUGIN_CODE Kyra
        PRODUCT_NAME "Keyra"
        DESCRIPTION "Modelled grand piano"
        FORMATS ${KEYRA_PLUGIN_FORMATS}
        VST3_CATEGORIES Instrument Piano
        AU_MAIN_TYPE kAudioUnitType_MusicDevice
        IS_SYNTH TRUE
        NEEDS_MIDI_INPUT TRUE
        NEEDS_MIDI_OUTPUT FALSE
        IS_MIDI_EFFECT FALSE
        EDITOR_WANTS_KEYBOARD_FOCUS TRUE
        AU_SANDBOX_SAFE TRUE
        COPY_PLUGIN_AFTER_BUILD FALSE)

    if(KEYRA_BUILD_CLAP)
        # CLAP is supplied by the JUCE extension, outside JUCE's FORMATS list.
        # Its wrapper inherits Keyra's product name, version and artefacts
        # directory.
        clap_juce_extensions_plugin(TARGET Keyra
            CLAP_ID "cz.protocodus.keyra"
            CLAP_FEATURES instrument piano stereo)
    endif()

    target_sources(Keyra PRIVATE
        Source/PluginProcessor.cpp
        Source/PluginProcessor.h
        Source/PluginEditor.cpp
        Source/PluginEditor.h)

    target_link_libraries(Keyra
        PRIVATE
            KeyraDSP
            juce::juce_audio_utils
            juce::juce_gui_extra
        PUBLIC
            juce::juce_recommended_config_flags
            juce::juce_recommended_lto_flags
            juce::juce_recommended_warning_flags)

    # The About box names the package this binary ships in, with the build
    # number read the way scripts/release_metadata.py reads it.
    if(NOT "$ENV{BUILD_NUMBER}" STREQUAL "")
        set(KEYRA_BUILD_NUMBER "$ENV{BUILD_NUMBER}")
    elseif(NOT "$ENV{GITHUB_RUN_NUMBER}" STREQUAL "")
        set(KEYRA_BUILD_NUMBER "$ENV{GITHUB_RUN_NUMBER}")
    else()
        set(KEYRA_BUILD_NUMBER "local")
    endif()

    target_compile_definitions(Keyra
        PUBLIC
            JUCE_WEB_BROWSER=0
            JUCE_USE_CURL=0
            JUCE_VST3_CAN_REPLACE_VST2=0
        PRIVATE
            KEYRA_BUILD_IDENTITY="${PROJECT_VERSION}-build.${KEYRA_BUILD_NUMBER}")

    # The editor preview renders the README screenshot and the Shop images.
    add_executable(keyra_editor_preview Tools/editor_preview.cpp)
    target_link_libraries(keyra_editor_preview PRIVATE Keyra)
    target_include_directories(keyra_editor_preview PRIVATE
        "${CMAKE_CURRENT_SOURCE_DIR}/Source"
        "$<TARGET_PROPERTY:Keyra,INCLUDE_DIRECTORIES>")
    target_compile_definitions(keyra_editor_preview PRIVATE JUCE_GLOBAL_MODULE_SETTINGS_INCLUDED=1)
endif()

if(KEYRA_BUILD_TOOLS)
    # The research renderer the recording comparisons under Tools/ drive.
    add_executable(keyra_render Tools/render.cpp)
    target_link_libraries(keyra_render PRIVATE KeyraDSP)

    # One README demo per factory preset from Docs/audio/midi (Tools/
    # PresetDemoRenderer.h is the shared portfolio copy; do not edit it here).
    add_executable(RenderKeyraPresetDemos Tools/RenderPresetDemos.cpp)
    find_package(Threads REQUIRED)
    target_link_libraries(RenderKeyraPresetDemos PRIVATE KeyraDSP Threads::Threads)
    if(MSVC)
        target_compile_options(RenderKeyraPresetDemos PRIVATE /W4 /permissive-)
    else()
        target_compile_options(RenderKeyraPresetDemos PRIVATE -Wall -Wextra -Wpedantic)
    endif()

    # Every preset's level on Reason's channel meter, and each piano's
    # outputScale calibration (Tools/KeyraLevels.cpp).
    add_executable(KeyraLevels Tools/KeyraLevels.cpp)
    target_link_libraries(KeyraLevels PRIVATE KeyraDSP Threads::Threads)
endif()

if(BUILD_TESTING)
    # CI requires the interpreter, so a missing one cannot silently register
    # fewer tests.
    if(KEYRA_REQUIRE_PYTHON_TESTS OR KEYRA_ENABLE_MODEL_VALIDATION_TESTS OR KEYRA_ENABLE_NETWORK_TESTS)
        find_package(Python3 COMPONENTS Interpreter REQUIRED)
    else()
        find_package(Python3 COMPONENTS Interpreter)
    endif()

    add_executable(KeyraEngineTests Tests/engine_tests.cpp)
    target_link_libraries(KeyraEngineTests PRIVATE KeyraDSP)
    add_test(NAME Keyra.Engine COMMAND KeyraEngineTests)

    add_executable(KeyraForteOutputTests Tests/forte_output_tests.cpp)
    target_include_directories(KeyraForteOutputTests PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/Source")
    target_compile_features(KeyraForteOutputTests PRIVATE cxx_std_17)
    add_test(NAME Keyra.ForteOutput COMMAND KeyraForteOutputTests)
    set_tests_properties(Keyra.ForteOutput PROPERTIES LABELS unit)

    # Observe both ends of the shared damper in one test translation unit.
    add_executable(KeyraDamperInteractionTests Tests/damper_interaction_tests.cpp)
    target_include_directories(KeyraDamperInteractionTests PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/Source")
    target_compile_features(KeyraDamperInteractionTests PRIVATE cxx_std_17)
    add_test(NAME Keyra.DamperInteraction COMMAND KeyraDamperInteractionTests)

    # Every key between two recorded pitches against them, from the partials
    # a strike plays, in one test translation unit.
    add_executable(KeyraPitchBlendTests Tests/pitch_blend_tests.cpp)
    target_include_directories(KeyraPitchBlendTests PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/Source")
    target_compile_features(KeyraPitchBlendTests PRIVATE cxx_std_17)
    # It includes KeyraEngine.cpp to read the series a strike plays, so GCC
    # finds the engine's internal-linkage types in an included file and warns
    # about every class that holds one.
    target_compile_options(KeyraPitchBlendTests PRIVATE $<$<CXX_COMPILER_ID:GNU>:-Wno-subobject-linkage>)
    add_test(NAME Keyra.PitchBlend COMMAND KeyraPitchBlendTests)

    # The phantom partials' square against the lines it makes, and each
    # key's gain and gate in the engine, in one test translation unit.
    add_executable(KeyraPhantomTests Tests/phantom_tests.cpp)
    target_include_directories(KeyraPhantomTests PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/Source")
    target_compile_features(KeyraPhantomTests PRIVATE cxx_std_17)
    target_compile_options(KeyraPhantomTests PRIVATE $<$<CXX_COMPILER_ID:GNU>:-Wno-subobject-linkage>)
    add_test(NAME Keyra.Phantoms COMMAND KeyraPhantomTests)

    # Each key's pitch glide in the engine and its voices' tuning to it, in
    # one test translation unit.
    add_executable(KeyraGlideTests Tests/glide_tests.cpp)
    target_include_directories(KeyraGlideTests PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/Source")
    target_compile_features(KeyraGlideTests PRIVATE cxx_std_17)
    target_compile_options(KeyraGlideTests PRIVATE $<$<CXX_COMPILER_ID:GNU>:-Wno-subobject-linkage>)
    add_test(NAME Keyra.Glide COMMAND KeyraGlideTests)

    add_executable(KeyraParameterExtremesTests Tests/parameter_extremes.cpp)
    target_link_libraries(KeyraParameterExtremesTests PRIVATE KeyraDSP)
    add_test(NAME Keyra.ParameterExtremes COMMAND KeyraParameterExtremesTests)

    # U4/U8 input fuzzing, one harness built twice. KeyraDspFuzzReplay (any
    # compiler, FuzzHarness.h's main) replays the fixed crashes committed in
    # Tests/Fixtures/fuzz/ and then seeded inputs as a unit test;
    # KeyraDspFuzz (KEYRA_BUILD_FUZZER, Clang) is the libFuzzer target over
    # coverage-instrumented DSP.
    add_executable(KeyraDspFuzzReplay Tests/DspFuzz.cpp)
    target_include_directories(KeyraDspFuzzReplay PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/Source")
    target_link_libraries(KeyraDspFuzzReplay PRIVATE KeyraDSP)
    target_compile_definitions(KeyraDspFuzzReplay PRIVATE PROTOCODUS_FUZZ_MAIN)
    file(GLOB KEYRA_FUZZ_REPRODUCERS CONFIGURE_DEPENDS
         "${CMAKE_CURRENT_SOURCE_DIR}/Tests/Fixtures/fuzz/*")
    add_test(NAME Keyra.DspFuzzReplay
             COMMAND KeyraDspFuzzReplay -seed=1 -runs=300 ${KEYRA_FUZZ_REPRODUCERS})
    set_tests_properties(Keyra.DspFuzzReplay PROPERTIES TIMEOUT 600 LABELS unit)
    if(KEYRA_BUILD_FUZZER)
        if(NOT CMAKE_CXX_COMPILER_ID MATCHES "Clang")
            message(FATAL_ERROR "KEYRA_BUILD_FUZZER requires Clang")
        endif()
        add_executable(KeyraDspFuzz Tests/DspFuzz.cpp ${KEYRA_DSP_SOURCES})
        target_include_directories(KeyraDspFuzz PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/Source")
        target_compile_options(KeyraDspFuzz PRIVATE
            -fsanitize=fuzzer,address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer)
        target_link_options(KeyraDspFuzz PRIVATE -fsanitize=fuzzer,address,undefined)
        file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/fuzz-corpus")
        add_test(NAME Keyra.DspFuzz
                 COMMAND KeyraDspFuzz -seed=1 -max_total_time=120 -max_len=4096 -timeout=30 -rss_limit_mb=2048
                         "${CMAKE_CURRENT_BINARY_DIR}/fuzz-corpus")
        set_tests_properties(Keyra.DspFuzz PROPERTIES TIMEOUT 600 LABELS fuzz)
    endif()

    if(Python3_Interpreter_FOUND)
        add_test(NAME Keyra.RecordingParityPaths
                 COMMAND "${Python3_EXECUTABLE}" -B
                         "${CMAKE_CURRENT_SOURCE_DIR}/Tests/test_recording_parity_paths.py")
        # The committed demo phrases are what the writer writes (G3a).
        add_test(NAME Keyra.DemoMidiSources
                 COMMAND "${Python3_EXECUTABLE}" -B
                         "${CMAKE_CURRENT_SOURCE_DIR}/Tools/write_preset_midi.py" --check)
        add_test(NAME Keyra.YamahaCorpusImport
                 COMMAND "${Python3_EXECUTABLE}" -B
                         "${CMAKE_CURRENT_SOURCE_DIR}/Tests/test_yamaha_c3_import.py")
        add_test(NAME Keyra.FactoryDynamicsContract
                 COMMAND "${Python3_EXECUTABLE}" -B
                         "${CMAKE_CURRENT_SOURCE_DIR}/Tests/test_factory_dynamics.py")
        set_tests_properties(Keyra.FactoryDynamicsContract PROPERTIES LABELS unit TIMEOUT 60)
    endif()

    # Required in the primary Linux CI job. An explicit option keeps the
    # portable DSP/plugin tiers independent of scientific Python and a second
    # compiler driver; enabling this tier never silently skips a dependency.
    if(KEYRA_ENABLE_MODEL_VALIDATION_TESTS)
        if(NOT CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
            message(FATAL_ERROR "Model validation native probes require a GCC/Clang compiler driver")
        endif()
        find_program(KEYRA_MODEL_CXX NAMES c++ REQUIRED)
        find_program(KEYRA_MODEL_FFMPEG NAMES ffmpeg REQUIRED)
        find_program(KEYRA_MODEL_FFPROBE NAMES ffprobe REQUIRED)
        execute_process(COMMAND "${Python3_EXECUTABLE}" -c "import numpy; import scipy"
                        RESULT_VARIABLE KEYRA_MODEL_PYTHON_RESULT
                        ERROR_VARIABLE KEYRA_MODEL_PYTHON_ERROR
                        OUTPUT_QUIET)
        if(NOT KEYRA_MODEL_PYTHON_RESULT EQUAL 0)
            message(FATAL_ERROR
                "Model validation needs NumPy/SciPy in ${Python3_EXECUTABLE}. "
                "Install Tools/requirements-model-validation.txt. ${KEYRA_MODEL_PYTHON_ERROR}")
        endif()
        add_test(NAME Keyra.VelocityInterpolation
                 COMMAND "${Python3_EXECUTABLE}" -B
                         "${CMAKE_CURRENT_SOURCE_DIR}/Tests/test_velocity_interpolation.py")
        add_test(NAME Keyra.VelocityInterpolationFreshness
                 COMMAND "${Python3_EXECUTABLE}" -B
                         "${CMAKE_CURRENT_SOURCE_DIR}/Tools/generate_velocity_interpolation.py" --check)
        # The phantom gains are the ones their receipt gives, for the
        # recorded pitches the engine has, and the receipt is the current
        # fit's on the current modal data, split and corpus.
        add_test(NAME Keyra.MeasuredPhantoms
                 COMMAND "${Python3_EXECUTABLE}" -B
                         "${CMAKE_CURRENT_SOURCE_DIR}/Tools/fit_phantoms.py" --check)
        # The glide is the one its receipt gives, and the receipt is the
        # current fit's on the current modal data, split and corpus.
        add_test(NAME Keyra.MeasuredGlide
                 COMMAND "${Python3_EXECUTABLE}" -B
                         "${CMAKE_CURRENT_SOURCE_DIR}/Tools/fit_glide.py" --check)
        add_test(NAME Keyra.RateInterpolation
                 COMMAND "${Python3_EXECUTABLE}" -B
                         "${CMAKE_CURRENT_SOURCE_DIR}/Tests/test_rate_interpolation.py")
        add_test(NAME Keyra.ComponentWarmStart
                 COMMAND "${Python3_EXECUTABLE}" -B
                         "${CMAKE_CURRENT_SOURCE_DIR}/Tests/test_component_warm_start.py")
        add_test(NAME Keyra.IncrementalMeasurements
                 COMMAND "${Python3_EXECUTABLE}" -B
                         "${CMAKE_CURRENT_SOURCE_DIR}/Tests/test_incremental_measurements.py")
        add_test(NAME Keyra.MeasurementSourceProvenance
                 COMMAND "${Python3_EXECUTABLE}" -B
                         "${CMAKE_CURRENT_SOURCE_DIR}/Tests/test_source_provenance.py"
                         --decoder-dir "${CMAKE_CURRENT_SOURCE_DIR}/Tools")
        add_test(NAME Keyra.MeasurementSnapshots
                 COMMAND "${Python3_EXECUTABLE}" -B
                         "${CMAKE_CURRENT_SOURCE_DIR}/Tests/test_measurement_snapshots.py")
        add_test(NAME Keyra.MeasurementOutputSafety
                 COMMAND "${Python3_EXECUTABLE}" -B
                         "${CMAKE_CURRENT_SOURCE_DIR}/Tests/test_measurement_output_safety.py")
        add_test(NAME Keyra.SoftLaneContinuity
                 COMMAND "${Python3_EXECUTABLE}" -B
                         "${CMAKE_CURRENT_SOURCE_DIR}/Tests/test_soft_lane_continuity.py")
        add_test(NAME Keyra.LiveControlSmoothing
                 COMMAND "${Python3_EXECUTABLE}" -B
                         "${CMAKE_CURRENT_SOURCE_DIR}/Tests/test_live_control_smoothing.py")
        add_test(NAME Keyra.BuildControlSmoothing
                 COMMAND "${Python3_EXECUTABLE}" -B
                         "${CMAKE_CURRENT_SOURCE_DIR}/Tests/test_build_control_smoothing.py")
        add_test(NAME Keyra.QualityAuditContract
                 COMMAND "${Python3_EXECUTABLE}" -B
                         "${CMAKE_CURRENT_SOURCE_DIR}/Tests/test_quality_audit.py")
        add_test(NAME Keyra.QualityRetention
                 COMMAND "${Python3_EXECUTABLE}" -B
                         "${CMAKE_CURRENT_SOURCE_DIR}/Tests/test_quality_retention.py")
        add_test(NAME Keyra.ReleaseBalance
                 COMMAND "${Python3_EXECUTABLE}" -B
                         "${CMAKE_CURRENT_SOURCE_DIR}/Tests/test_release_balance.py")
        add_test(NAME Keyra.RecordingReferenceCache
                 COMMAND "${Python3_EXECUTABLE}" -B
                         "${CMAKE_CURRENT_SOURCE_DIR}/Tests/test_recording_reference_cache.py")
        add_test(NAME Keyra.BenchmarkComparison
                 COMMAND "${Python3_EXECUTABLE}" -B
                         "${CMAKE_CURRENT_SOURCE_DIR}/Tests/test_benchmark_comparison.py")
        add_test(NAME Keyra.KeyboardMetricContract
                 COMMAND "${Python3_EXECUTABLE}" -B
                         "${CMAKE_CURRENT_SOURCE_DIR}/Tools/benchmark_keyboard.py" --self-check)
        set_tests_properties(Keyra.VelocityInterpolation Keyra.VelocityInterpolationFreshness Keyra.MeasuredPhantoms Keyra.MeasuredGlide
                             Keyra.RateInterpolation Keyra.ComponentWarmStart
                             Keyra.IncrementalMeasurements Keyra.MeasurementSourceProvenance
                             Keyra.MeasurementSnapshots Keyra.MeasurementOutputSafety
                             Keyra.SoftLaneContinuity
                             Keyra.LiveControlSmoothing Keyra.BuildControlSmoothing
                             Keyra.QualityAuditContract Keyra.QualityRetention Keyra.ReleaseBalance
                             Keyra.RecordingReferenceCache Keyra.BenchmarkComparison
                             Keyra.KeyboardMetricContract
                             PROPERTIES TIMEOUT 600
                             ENVIRONMENT "CXX=${KEYRA_MODEL_CXX};KEYRA_MODEL_FFMPEG=${KEYRA_MODEL_FFMPEG};KEYRA_MODEL_FFPROBE=${KEYRA_MODEL_FFPROBE};OPENBLAS_NUM_THREADS=1;OMP_NUM_THREADS=1")
    else()
        message(STATUS "Numerical model validation disabled; enable KEYRA_ENABLE_MODEL_VALIDATION_TESTS for the required Linux CI tier")
    endif()

    if(KEYRA_ENABLE_NETWORK_TESTS)
        execute_process(COMMAND "${Python3_EXECUTABLE}" -c "import numpy; import scipy; import torch"
                        RESULT_VARIABLE KEYRA_NETWORK_PYTHON_RESULT
                        ERROR_VARIABLE KEYRA_NETWORK_PYTHON_ERROR
                        OUTPUT_QUIET)
        if(NOT KEYRA_NETWORK_PYTHON_RESULT EQUAL 0)
            message(FATAL_ERROR
                "The keyboard network's self-test needs NumPy, SciPy and PyTorch in ${Python3_EXECUTABLE}. "
                "${KEYRA_NETWORK_PYTHON_ERROR}")
        endif()
        add_test(NAME Keyra.KeyboardNetwork
                 COMMAND "${Python3_EXECUTABLE}" -B "${CMAKE_CURRENT_SOURCE_DIR}/Tests/test_keyboard_network.py")
        set_tests_properties(Keyra.KeyboardNetwork PROPERTIES LABELS unit TIMEOUT 300
                             ENVIRONMENT "OPENBLAS_NUM_THREADS=1;OMP_NUM_THREADS=1")
    endif()

    if(KEYRA_BUILD_TOOLS)
        # Every preset demo renders finite, audible, under the ceiling, 8-12 s
        # long and bit-identical on a second render.
        add_test(NAME Keyra.AudioDemos
                 COMMAND RenderKeyraPresetDemos --jobs 4 --check
                         "${CMAKE_CURRENT_SOURCE_DIR}/Docs/audio/midi")
        set_tests_properties(Keyra.AudioDemos PROPERTIES TIMEOUT 300 LABELS audio)
        # Typical playing at -9 VU on Reason's meter and the loudest chords
        # out of the red (Tools/KeyraLevels.cpp).
        add_test(NAME Keyra.Levels COMMAND KeyraLevels --check --jobs 4)
        set_tests_properties(Keyra.Levels PROPERTIES TIMEOUT 900 LABELS audio)
        if(KEYRA_ENABLE_MODEL_VALIDATION_TESTS)
            # Run a single fresh factory audit in the required Linux audio
            # tier, retaining the same CSV the row-by-row checker inspected.
            add_test(NAME Keyra.FactoryDynamics
                     COMMAND "${Python3_EXECUTABLE}" -B
                             "${CMAKE_CURRENT_SOURCE_DIR}/Tools/check_factory_dynamics.py"
                             --renderer "$<TARGET_FILE:KeyraLevels>" --jobs 4
                             --output "${CMAKE_CURRENT_BINARY_DIR}/factory-dynamics.csv")
            set_tests_properties(Keyra.FactoryDynamics PROPERTIES LABELS audio TIMEOUT 900)
        endif()
        # U7: the preset demos timed on one thread against the budget in
        # Tools/RenderPresetDemos.cpp. Timing means nothing instrumented.
        if(CMAKE_BUILD_TYPE STREQUAL "Release" AND NOT KEYRA_ENABLE_SANITIZERS)
            add_test(NAME Keyra.CpuBudget
                     COMMAND RenderKeyraPresetDemos --cpu --json "${CMAKE_BINARY_DIR}/cpu.json"
                             "${CMAKE_CURRENT_SOURCE_DIR}/Docs/audio/midi")
            set_tests_properties(Keyra.CpuBudget PROPERTIES LABELS perf RUN_SERIAL TRUE TIMEOUT 1800)
        endif()
    endif()

    if(KEYRA_BUILD_PLUGIN)
        add_executable(KeyraPluginProcessorTests Tests/plugin_tests.cpp)
        target_link_libraries(KeyraPluginProcessorTests PRIVATE Keyra)
        target_include_directories(KeyraPluginProcessorTests PRIVATE
            "${CMAKE_CURRENT_SOURCE_DIR}/Source"
            "$<TARGET_PROPERTY:Keyra,INCLUDE_DIRECTORIES>")
        target_compile_definitions(KeyraPluginProcessorTests PRIVATE JUCE_GLOBAL_MODULE_SETTINGS_INCLUDED=1)
        add_test(NAME Keyra.PluginProcessor COMMAND KeyraPluginProcessorTests)

        add_executable(KeyraParameterMatrixTests Tests/ParameterMatrixTests.cpp)
        target_link_libraries(KeyraParameterMatrixTests PRIVATE Keyra)
        target_include_directories(KeyraParameterMatrixTests PRIVATE
            "${CMAKE_CURRENT_SOURCE_DIR}/Source"
            "$<TARGET_PROPERTY:Keyra,INCLUDE_DIRECTORIES>")
        target_compile_definitions(KeyraParameterMatrixTests PRIVATE JUCE_GLOBAL_MODULE_SETTINGS_INCLUDED=1)
        # Each case at one rate and block size; the main build's nightly run
        # covers every case at all nine.
        add_test(NAME Keyra.ParameterMatrix
                 COMMAND KeyraParameterMatrixTests --rotation --jobs 4)
        set_tests_properties(Keyra.ParameterMatrix PROPERTIES TIMEOUT 1800 LABELS fuzz)

        if(Python3_Interpreter_FOUND)
            add_test(NAME Keyra.EditorRender
                     COMMAND "${Python3_EXECUTABLE}" -B
                             "${CMAKE_CURRENT_SOURCE_DIR}/Tests/EditorRenderTests.py"
                             --editor-preview "$<TARGET_FILE:keyra_editor_preview>")
            set_tests_properties(Keyra.EditorRender PROPERTIES TIMEOUT 600 LABELS render)
        endif()
    endif()

    # Every test carries exactly one tier label so CI selects tiers with
    # `ctest -L`; tests not labelled above are unit contracts.
    get_property(KEYRA_TESTS DIRECTORY PROPERTY TESTS)
    foreach(test IN LISTS KEYRA_TESTS)
        get_test_property(${test} LABELS test_labels)
        if(NOT test_labels)
            set_tests_properties(${test} PROPERTIES LABELS unit)
        endif()
    endforeach()
endif()
