get_filename_component(YORADIO_ROOT
  "${CMAKE_CURRENT_LIST_DIR}/../../../yoRadio" ABSOLUTE)

if(YORADIO_HARDWARE_CACHE_TEST OR YORADIO_HARDWARE_FLASH_TEST)
  idf_component_register(
    SRCS "hardware_cache_test.c" "native_aac_decoder.c" "codec_memory_trace.c"
    INCLUDE_DIRS "."
    REQUIRES esp_audio_codec esp_timer esp_hw_support esp_system hal riscv soc
             esp_hal_mspi app_update bootloader_support esp_partition spi_flash)
  target_compile_options(${COMPONENT_LIB} PRIVATE -O3)
  if(YORADIO_HARDWARE_FLASH_TEST)
    target_compile_definitions(${COMPONENT_LIB} PRIVATE YORADIO_HARDWARE_FLASH_TEST=1)
  endif()
  foreach(FIXTURE lc-48000-stereo he-48000-stereo hev2-44100-stereo)
    configure_file("${YORADIO_ROOT}/../tests/fixtures/aac_stream_format/${FIXTURE}.aac"
                   "${CMAKE_CURRENT_BINARY_DIR}/${FIXTURE}.aac" COPYONLY)
    target_add_binary_data(${COMPONENT_LIB}
                          "${CMAKE_CURRENT_BINARY_DIR}/${FIXTURE}.aac" BINARY)
  endforeach()
  return()
endif()

if(YORADIO_OVERCLOCK_EXPERIMENT)
  idf_component_register(
    SRCS "overclock_experiment.c"
    INCLUDE_DIRS "."
    REQUIRES
      esp_driver_gpio esp_hal_clock esp_hal_wdt esp_hw_support esp_system hal
      riscv soc)
  target_include_directories(${COMPONENT_LIB} PRIVATE
    "$ENV{IDF_PATH}/components/esp_hal_clock/esp32c3/include"
    "$ENV{IDF_PATH}/components/esp_hal_wdt/include"
    "$ENV{IDF_PATH}/components/esp_hal_wdt/esp32c3/include")
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_OVERCLOCK_EXPERIMENT=1)
  target_compile_options(${COMPONENT_LIB} PRIVATE -O3)
  return()
endif()

set(NATIVE_SRCS
  "app_main.c"
  "codec_memory_trace.c"
  "audio_service.c"
  "native_aac_decoder.c"
  "cpu_profiler.c"
  "display_settings.c"
  "deep_sleep_clock.c"
  "rtc_wake_stub_clock.c"
  "encoder_input.c"
  "native_audio_normalizer.cpp"
  "native_state.c"
  "network_service.c"
  "oled_display.c"
  "ota_upload.c"
  "radio_control.c"
  "runtime_settings.c"
  "time_service.c"
  "web_pages_bridge.cpp"
  "web_service.c"
  "web_ota.c"
  "websocket_service.c")

if(CONFIG_YORADIO_QEMU)
  list(APPEND NATIVE_SRCS "native_audio_output_qemu.c")
  if(CONFIG_YORADIO_QEMU_AAC_TEST)
    list(APPEND NATIVE_SRCS "qemu_aac_test.c")
    if(CONFIG_YORADIO_QEMU_AAC_BFP16_TEST OR CONFIG_YORADIO_QEMU_AAC_PACKED_HISTORY_TEST)
      list(APPEND NATIVE_SRCS "qemu_aac_bfp16.c")
    endif()
    if(CONFIG_YORADIO_QEMU_AAC_PACKED_HISTORY_TEST)
      if(CONFIG_YORADIO_QEMU_AAC_SBR_LAYOUT_TEST)
        list(APPEND NATIVE_SRCS "qemu_aac_sbr_layout.c")
        if(CONFIG_YORADIO_QEMU_AAC_RESET_TEST)
          list(APPEND NATIVE_SRCS "qemu_aac_reset.c")
        endif()
      elseif(CONFIG_YORADIO_QEMU_AAC_PS_HISTORY_PORT_TEST)
        list(APPEND NATIVE_SRCS "qemu_aac_ps_history_port.c")
      else()
        list(APPEND NATIVE_SRCS "qemu_aac_packed_history.c")
      endif()
    endif()
    if(CONFIG_YORADIO_QEMU_CACHE_TEST)
      list(APPEND NATIVE_SRCS "qemu_cache_test.c")
    endif()
    if(CONFIG_YORADIO_QEMU_AAC_PROFILE)
      list(APPEND NATIVE_SRCS "qemu_aac_calibration.c" "qemu_codec_calibration.c")
    endif()
  endif()
else()
  list(APPEND NATIVE_SRCS "native_audio_output.c")
endif()

idf_component_register(
  SRCS ${NATIVE_SRCS}
  INCLUDE_DIRS "."
  REQUIRES
    app_update
    bootloader_support
    efuse
    esp_adc
    esp_driver_gpio
    esp_driver_i2c
    esp_driver_i2s
    esp_event
    esp_http_client
    esp_http_server
    esp_hw_support
    esp_hal_mspi
    esp_hal_rtc_timer
    esp_lcd
    esp_netif
    esp_partition
    esp_timer
    esp_wifi
    esp_ringbuf
    lwip
    mbedtls
    nvs_flash
    spiffs
    spi_flash
    audio_level_led
    native_audio_settings
    custom_flac
    custom_legacy_codecs
    esp_audio_codec)

target_sources(${COMPONENT_LIB} PRIVATE
  "${YORADIO_ROOT}/src/audioI2S/AudioNormalizer.cpp")
target_include_directories(${COMPONENT_LIB} PRIVATE
  "${YORADIO_ROOT}/src/audioI2S")

target_compile_definitions(${COMPONENT_LIB} PRIVATE YORADIO_ESP_IDF_NATIVE=1)
if(YORADIO_CODEC_BENCHMARK)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_CODEC_BENCHMARK=1)
endif()
target_compile_options(${COMPONENT_LIB} PRIVATE -O3)

if(CONFIG_YORADIO_QEMU_AAC_BFP16_TEST)
  target_link_options(${COMPONENT_LIB} INTERFACE
    "-Wl,--wrap=calc_sbr_anafilterbank"
    "-Wl,--wrap=calc_sbr_anafilterbank_LC")
endif()

if(CONFIG_YORADIO_QEMU_AAC_PACKED_HISTORY_TEST)
  if(CONFIG_YORADIO_QEMU_AAC_PS_HISTORY_PORT_TEST OR CONFIG_YORADIO_QEMU_AAC_SBR_LAYOUT_TEST)
    set(PINNED_AAC_ARCHIVE "$ENV{YORADIO_AUDIO_CODEC_COMPONENT}/lib/esp32c3/libesp_audio_codec.a")
    file(SHA256 "${PINNED_AAC_ARCHIVE}" AAC_ARCHIVE_SHA256)
    if(NOT AAC_ARCHIVE_SHA256 STREQUAL "311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909")
      message(FATAL_ERROR "PS storage port requires the audited ESP32-C3 AAC archive")
    endif()
    if(CONFIG_YORADIO_QEMU_AAC_SBR_LAYOUT_TEST)
      target_link_options(${COMPONENT_LIB} INTERFACE "-Wl,--wrap=media_lib_module_calloc"
        "-Wl,--wrap=media_lib_free" "-Wl,--wrap=sbr_applied" "-Wl,--wrap=ps_read_data")
      if(CONFIG_YORADIO_QEMU_AAC_RESET_TEST)
        target_link_options(${COMPONENT_LIB} INTERFACE "-Wl,--wrap=PVMP4AudioDecoderResetBuffer" "-Wl,--wrap=sbr_open")
      endif()
    else()
      target_link_options(${COMPONENT_LIB} INTERFACE "-Wl,--wrap=ps_decorrelate" "-Wl,--wrap=ps_allocate_decoder")
    endif()
  else()
    target_link_options(${COMPONENT_LIB} INTERFACE "-Wl,--wrap=sbr_dec")
  endif()
endif()

if(CONFIG_YORADIO_QEMU_AAC_TEST)
  foreach(FIXTURE lc-44100-stereo lc-22050-mono lc-48000-stereo
                  he-44100-stereo he-48000-stereo hev2-44100-stereo)
    configure_file("${YORADIO_ROOT}/../tests/fixtures/aac_stream_format/${FIXTURE}.aac"
                   "${CMAKE_CURRENT_BINARY_DIR}/${FIXTURE}.aac" COPYONLY)
    target_add_binary_data(${COMPONENT_LIB}
                          "${CMAKE_CURRENT_BINARY_DIR}/${FIXTURE}.aac" BINARY)
  endforeach()
endif()

# Keep the original physical-board fixture byte-for-byte for timing calibration.
if(CONFIG_YORADIO_QEMU_AAC_PROFILE)
  configure_file("${YORADIO_ROOT}/../tests/fixtures/esp32c3_calibration/aac-lc-320.aac"
                 "${CMAKE_CURRENT_BINARY_DIR}/aac-lc-320.aac" COPYONLY)
  target_add_binary_data(${COMPONENT_LIB}
                        "${CMAKE_CURRENT_BINARY_DIR}/aac-lc-320.aac" BINARY)
endif()

# Ship the same shared WebUI script with application OTA, including capability
# labels and upload error handling, without rewriting users' SPIFFS contents.
configure_file("${YORADIO_ROOT}/data/www/script.js.gz"
               "${CMAKE_CURRENT_BINARY_DIR}/native-script.js.gz" COPYONLY)
target_add_binary_data(${COMPONENT_LIB}
                      "${CMAKE_CURRENT_BINARY_DIR}/native-script.js.gz" BINARY)

set(NATIVE_SPIFFS_ROOT "${CMAKE_CURRENT_BINARY_DIR}/spiffs-root")
file(REMOVE_RECURSE "${NATIVE_SPIFFS_ROOT}")
file(MAKE_DIRECTORY "${NATIVE_SPIFFS_ROOT}")
file(COPY "${YORADIO_ROOT}/data/" DESTINATION "${NATIVE_SPIFFS_ROOT}")
configure_file("${YORADIO_ROOT}/../playlist.csv"
               "${NATIVE_SPIFFS_ROOT}/data/playlist.csv" COPYONLY)

spiffs_create_partition_image(spiffs "${NATIVE_SPIFFS_ROOT}" FLASH_IN_PROJECT)
