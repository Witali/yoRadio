# Call after idf_component_register(). Private ABI is pinned to these ESP32
# objects; the target header must independently assert every consumed layout.
function(native_enable_vorbis_repair)
    if(CMAKE_BUILD_EARLY_EXPANSION OR NOT CONFIG_YORADIO_VORBIS_REPAIR)
        return()
    endif()
    if(NOT IDF_TARGET STREQUAL "esp32" OR NOT CONFIG_IDF_TARGET_ESP32)
        message(FATAL_ERROR "Vorbis repair requires classic ESP32 Xtensa")
    endif()
    if(NOT DEFINED IDF_VERSION_MAJOR OR NOT DEFINED IDF_VERSION_MINOR OR
       NOT DEFINED IDF_VERSION_PATCH OR NOT "${IDF_VERSION_MAJOR}" STREQUAL "6" OR
       NOT "${IDF_VERSION_MINOR}" STREQUAL "0" OR NOT "${IDF_VERSION_PATCH}" STREQUAL "2")
        message(FATAL_ERROR "Vorbis repair requires pinned ESP-IDF 6.0.2")
    endif()
    if(NOT DEFINED COMPONENT_LIB OR NOT TARGET "${COMPONENT_LIB}")
        message(FATAL_ERROR "Vorbis repair requires registered component target")
    endif()
    if("$ENV{YORADIO_AUDIO_CODEC_COMPONENT}" STREQUAL "")
        message(FATAL_ERROR "Vorbis repair requires pinned codec component directory")
    endif()
    foreach(archive codec simple_dec)
        set(path "$ENV{YORADIO_AUDIO_CODEC_COMPONENT}/lib/esp32/libesp_audio_${archive}.a")
        if(NOT EXISTS "${path}" OR IS_DIRECTORY "${path}")
            message(FATAL_ERROR "Vorbis repair missing ${archive} archive")
        endif()
        file(SHA256 "${path}" actual)
        if(archive STREQUAL "codec")
            set(expected "92ba997358f50994d41422438c78bf2d7ee86dc1efc265f5356a66e221ae2e58")
        else()
            set(expected "ca3b95dfc83b6984ae91c509bf859e4334fcc74654d2fe8b68bfc34f06126cc6")
        endif()
        if(NOT actual STREQUAL expected)
            message(FATAL_ERROR "Vorbis repair requires audited ESP32 ${archive} archive")
        endif()
    endforeach()
    get_filename_component(main "${CMAKE_CURRENT_FUNCTION_LIST_DIR}/../.." ABSOLUTE)
    foreach(source setup.c simple.c output.c floor1_render.h)
        if(NOT EXISTS "${main}/vorbis_repair/${source}")
            message(FATAL_ERROR "Vorbis repair missing canonical ${source}")
        endif()
    endforeach()
    if(NOT EXISTS "${main}/vorbis_repair_abi.h")
        message(FATAL_ERROR "Vorbis repair missing canonical ABI header")
    endif()
    target_sources(${COMPONENT_LIB} PRIVATE
        "${main}/vorbis_repair/setup.c"
        "${main}/vorbis_repair/simple.c"
        "${main}/vorbis_repair/output.c")
    target_link_options(${COMPONENT_LIB} INTERFACE
        "-Wl,--wrap=esp_vorbis_dec_open"
        "-Wl,--wrap=esp_vorbis_dec_register"
        "-Wl,--wrap=esp_vorbis_dec_decode"
        "-Wl,--wrap=floor1_inverse2"
        "-Wl,--wrap=esp_audio_simple_dec_open"
        "-Wl,--wrap=esp_audio_simple_dec_process"
        "-Wl,--wrap=esp_audio_simple_dec_reset"
        "-Wl,--wrap=esp_es_parse_frame"
        "-Wl,--wrap=esp_ogg_parse_frame"
        "-Wl,--wrap=media_lib_module_realloc")
endfunction()
