# Reuse the complete original component declaration and public driver seams.
include("${CMAKE_CURRENT_LIST_DIR}/../../../shared-family1/project/main/CMakeLists.txt")
if(CMAKE_BUILD_EARLY_EXPANSION)
    return()
endif()
foreach(symbol native_audio_normalizer_configure native_audio_normalizer_reset
    native_audio_normalizer_process_block native_audio_normalizer_process_multichannel_block)
    target_link_options(${COMPONENT_LIB} INTERFACE "-Wl,--wrap=${symbol}")
endforeach()
