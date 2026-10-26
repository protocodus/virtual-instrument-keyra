set(KEYRA_JUCE_PATH "" CACHE PATH "Local JUCE 8.0.14 checkout; avoids downloading JUCE")
if(KEYRA_JUCE_PATH)
    if(NOT EXISTS "${KEYRA_JUCE_PATH}/CMakeLists.txt")
        message(FATAL_ERROR "KEYRA_JUCE_PATH must contain JUCE's CMakeLists.txt")
    endif()
    add_subdirectory("${KEYRA_JUCE_PATH}" "${CMAKE_BINARY_DIR}/JUCE" EXCLUDE_FROM_ALL)
else()
    include(FetchContent)
    FetchContent_Declare(juce GIT_REPOSITORY https://github.com/juce-framework/JUCE.git
        GIT_TAG 2cdfca8feb300fb424002ba2c2751569e5bacb64 GIT_SHALLOW TRUE)
    FetchContent_MakeAvailable(juce)
endif()

set(KEYRA_PLUGIN_FORMATS VST3 Standalone)
if(APPLE)
    list(APPEND KEYRA_PLUGIN_FORMATS AU)
endif()
juce_add_plugin(Keyra
    COMPANY_NAME Protocodus
    COMPANY_WEBSITE https://protocodus.com
    BUNDLE_ID cz.protocodus.keyra
    PLUGIN_MANUFACTURER_CODE Ptoc
    PLUGIN_CODE Kyra
    PRODUCT_NAME Keyra
    DESCRIPTION "Modelled grand piano"
    IS_SYNTH TRUE
    NEEDS_MIDI_INPUT TRUE
    NEEDS_MIDI_OUTPUT FALSE
    IS_MIDI_EFFECT FALSE
    EDITOR_WANTS_KEYBOARD_FOCUS TRUE
    COPY_PLUGIN_AFTER_BUILD FALSE
    FORMATS ${KEYRA_PLUGIN_FORMATS})
target_sources(Keyra PRIVATE
    "${PROJECT_SOURCE_DIR}/Source/PluginProcessor.cpp"
    "${PROJECT_SOURCE_DIR}/Source/PluginEditor.cpp")
target_include_directories(Keyra PRIVATE "${PROJECT_SOURCE_DIR}/Source")
target_compile_definitions(Keyra PUBLIC
    JUCE_WEB_BROWSER=0 JUCE_USE_CURL=0
    JUCE_VST3_CAN_REPLACE_VST2=0)
target_link_libraries(Keyra PRIVATE KeyraDSP juce::juce_audio_utils juce::juce_gui_extra
    PUBLIC juce::juce_recommended_config_flags juce::juce_recommended_warning_flags)

if(BUILD_TESTING)
    add_executable(keyra_plugin_tests)
    set_target_properties(keyra_plugin_tests PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/keyra_plugin_tests_artefacts/$<CONFIG>")
    target_sources(keyra_plugin_tests PRIVATE "${PROJECT_SOURCE_DIR}/Tests/plugin_tests.cpp")
    target_link_libraries(keyra_plugin_tests PRIVATE Keyra)
    target_include_directories(keyra_plugin_tests PRIVATE "${PROJECT_SOURCE_DIR}/Source"
        "$<TARGET_PROPERTY:Keyra,INCLUDE_DIRECTORIES>")
    target_compile_definitions(keyra_plugin_tests PRIVATE JUCE_GLOBAL_MODULE_SETTINGS_INCLUDED=1)
    add_test(NAME plugin_state_and_midi COMMAND keyra_plugin_tests)
endif()

add_executable(keyra_editor_preview)
set_target_properties(keyra_editor_preview PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/keyra_editor_preview_artefacts/$<CONFIG>")
target_sources(keyra_editor_preview PRIVATE "${PROJECT_SOURCE_DIR}/Tools/editor_preview.cpp")
target_link_libraries(keyra_editor_preview PRIVATE Keyra)
target_include_directories(keyra_editor_preview PRIVATE "${PROJECT_SOURCE_DIR}/Source"
    "$<TARGET_PROPERTY:Keyra,INCLUDE_DIRECTORIES>")
target_compile_definitions(keyra_editor_preview PRIVATE JUCE_GLOBAL_MODULE_SETTINGS_INCLUDED=1)
