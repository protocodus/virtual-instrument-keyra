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
project(Keyra VERSION 0.3.0 LANGUAGES C CXX)

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
option(KEYRA_BUILD_LIBFUZZER "Build KeyraDspFuzz as a Clang libFuzzer target" OFF)
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
    Source/DSP/KeyraPresets.h
    Source/DSP/MeasuredModalData.h)

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

    target_compile_definitions(Keyra
        PUBLIC
            JUCE_WEB_BROWSER=0
            JUCE_USE_CURL=0
            JUCE_VST3_CAN_REPLACE_VST2=0)

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
endif()

if(BUILD_TESTING)
    find_package(Python3 COMPONENTS Interpreter)

    add_executable(KeyraEngineTests Tests/engine_tests.cpp)
    target_link_libraries(KeyraEngineTests PRIVATE KeyraDSP)
    add_test(NAME Keyra.Engine COMMAND KeyraEngineTests)

    add_executable(KeyraParameterExtremesTests Tests/parameter_extremes.cpp)
    target_link_libraries(KeyraParameterExtremesTests PRIVATE KeyraDSP)
    add_test(NAME Keyra.ParameterExtremes COMMAND KeyraParameterExtremesTests)

    # U4 input fuzzing. With KEYRA_BUILD_LIBFUZZER (Clang) it is a libFuzzer
    # target over coverage-instrumented DSP; otherwise FuzzHarness.h supplies
    # a main that replays Tests/Fixtures/fuzz/ and then seeded inputs.
    add_executable(KeyraDspFuzz Tests/DspFuzz.cpp)
    target_include_directories(KeyraDspFuzz PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/Source")
    if(KEYRA_BUILD_LIBFUZZER)
        if(NOT CMAKE_CXX_COMPILER_ID MATCHES "Clang")
            message(FATAL_ERROR "KEYRA_BUILD_LIBFUZZER requires Clang")
        endif()
        target_sources(KeyraDspFuzz PRIVATE ${KEYRA_DSP_SOURCES})
        target_compile_options(KeyraDspFuzz PRIVATE
            -fsanitize=fuzzer,address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer)
        target_link_options(KeyraDspFuzz PRIVATE -fsanitize=fuzzer,address,undefined)
    else()
        target_link_libraries(KeyraDspFuzz PRIVATE KeyraDSP)
        target_compile_definitions(KeyraDspFuzz PRIVATE PROTOCODUS_FUZZ_MAIN)
    endif()
    file(GLOB KEYRA_FUZZ_REGRESSIONS CONFIGURE_DEPENDS
         "${CMAKE_CURRENT_SOURCE_DIR}/Tests/Fixtures/fuzz/*")
    add_test(NAME Keyra.DspFuzz
             COMMAND KeyraDspFuzz -seed=1 -runs=300 ${KEYRA_FUZZ_REGRESSIONS})
    set_tests_properties(Keyra.DspFuzz PROPERTIES TIMEOUT 600 LABELS fuzz)

    if(Python3_Interpreter_FOUND)
        add_test(NAME Keyra.RecordingParityPaths
                 COMMAND "${Python3_EXECUTABLE}" -B
                         "${CMAKE_CURRENT_SOURCE_DIR}/Tests/test_recording_parity_paths.py")
    endif()

    if(KEYRA_BUILD_TOOLS)
        # Every preset demo renders finite, audible, under the ceiling, 10-20 s
        # long and bit-identical on a second render.
        add_test(NAME Keyra.AudioDemos
                 COMMAND RenderKeyraPresetDemos --jobs 4 --check
                         "${CMAKE_CURRENT_SOURCE_DIR}/Docs/audio/midi")
        set_tests_properties(Keyra.AudioDemos PROPERTIES TIMEOUT 300 LABELS audio)
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
