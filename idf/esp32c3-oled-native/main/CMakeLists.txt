get_filename_component(YORADIO_ROOT
  "${CMAKE_CURRENT_LIST_DIR}/../../../yoRadio" ABSOLUTE)

function(yoradio_vorbis_repair)
  if(NOT CONFIG_YORADIO_VORBIS_REPAIR)
    return()
  endif()
  foreach(archive codec simple_dec)
    file(SHA256 "$ENV{YORADIO_AUDIO_CODEC_COMPONENT}/lib/esp32c3/libesp_audio_${archive}.a" vorbis_sha)
    if(archive STREQUAL "codec")
      set(expected "311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909")
    else()
      set(expected "232650ec81ae5e10ecbe1b2c86de2d1adf8f1b793f5ef343241c6e510db3e71f")
    endif()
    if(NOT vorbis_sha STREQUAL expected)
      message(FATAL_ERROR "Vorbis lifecycle test requires the audited ${archive} archive")
    endif()
  endforeach()
  target_sources(${COMPONENT_LIB} PRIVATE "vorbis_repair/setup.c" "vorbis_repair/simple.c" "vorbis_repair/output.c")
    target_link_options(${COMPONENT_LIB} INTERFACE
    "-Wl,--wrap=esp_vorbis_dec_open" "-Wl,--wrap=esp_vorbis_dec_register"
    "-Wl,--wrap=esp_vorbis_dec_decode"
    "-Wl,--wrap=esp_audio_simple_dec_open" "-Wl,--wrap=esp_audio_simple_dec_process"
    "-Wl,--wrap=esp_audio_simple_dec_reset"
      "-Wl,--wrap=esp_es_parse_frame" "-Wl,--wrap=esp_ogg_parse_frame"
      "-Wl,--wrap=media_lib_module_realloc")
endfunction()

if(CONFIG_YORADIO_QEMU_VORBIS_LIFECYCLE)
  foreach(archive codec simple_dec)
    file(SHA256 "$ENV{YORADIO_AUDIO_CODEC_COMPONENT}/lib/esp32c3/libesp_audio_${archive}.a" vorbis_sha)
    if(archive STREQUAL "codec")
      set(expected "311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909")
    else()
      set(expected "232650ec81ae5e10ecbe1b2c86de2d1adf8f1b793f5ef343241c6e510db3e71f")
    endif()
    if(NOT vorbis_sha STREQUAL expected)
      message(FATAL_ERROR "Vorbis lifecycle test requires the audited ${archive} archive")
    endif()
  endforeach()
  idf_component_register(SRCS "qemu_vorbis_lifecycle.c" "decoder_registration.c" INCLUDE_DIRS "."
    REQUIRES esp_audio_codec esp_partition esp_system esp_rom mbedtls)
  target_compile_options(${COMPONENT_LIB} PRIVATE -O2)
  target_link_options(${COMPONENT_LIB} INTERFACE "-Wl,--wrap=vorbis_dsp_synthesis")
  yoradio_vorbis_repair()
  return()
endif()

function(yoradio_aac_profile)
  file(SHA256 "$ENV{YORADIO_AUDIO_CODEC_COMPONENT}/lib/esp32c3/libesp_audio_codec.a" AAC_PROFILE_SHA256)
  if(NOT AAC_PROFILE_SHA256 STREQUAL "311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909")
    message(FATAL_ERROR "AAC profile metadata requires the audited ESP32-C3 AAC archive")
  endif()
  target_sources(${COMPONENT_LIB} PRIVATE "aac_profile.c" "aac_fill_parser.c" "aac_fill_wrappers.c")
  target_compile_definitions(${COMPONENT_LIB} PRIVATE YORADIO_AAC_PROFILE_METADATA=1)
  target_link_options(${COMPONENT_LIB} INTERFACE "-Wl,--wrap=PVMP4AudioDecodeFrame")
  target_link_options(${COMPONENT_LIB} INTERFACE "-Wl,--wrap=getfill" "-Wl,--wrap=get_sbr_bitstream")
  # The vendor archive can be scanned after libmain. Pull in the wrapper
  # object even when only that later archive refers to the wrapped symbols.
  target_link_options(${COMPONENT_LIB} INTERFACE
    "-Wl,-u,__wrap_getfill" "-Wl,-u,__wrap_get_sbr_bitstream")
endfunction()

if(YORADIO_HARDWARE_CACHE_TEST OR YORADIO_HARDWARE_FLASH_TEST)
  idf_component_register(
    SRCS "hardware_cache_test.c" "native_aac_decoder.c" "codec_memory_trace.c"
    INCLUDE_DIRS "."
    REQUIRES esp_audio_codec esp_timer esp_hw_support esp_system hal riscv soc
             esp_hal_mspi app_update bootloader_support esp_partition spi_flash)
  yoradio_aac_profile()
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
  "stream_http_reader.c"
  "icy_title.c"
  "decoder_registration.c"
  "native_aac_decoder.c"
  "aac_sbr_reserve.c"
  "aac_scratch_reserve.c"
  "aac_compact_owner.c"
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

if(CONFIG_YORADIO_NETWORK_HEAP_PROFILE)
  list(APPEND NATIVE_SRCS "network_heap_profile.c")
endif()

if(CONFIG_YORADIO_QEMU)
  list(APPEND NATIVE_SRCS "native_audio_output_qemu.c")
  if(CONFIG_YORADIO_QEMU_AAC_TEST)
    list(APPEND NATIVE_SRCS "qemu_aac_test.c" "qemu_aac_metadata.c" "qemu_aac_fill.c")
    if(CONFIG_YORADIO_QEMU_AAC_LATE_SBR_TEST)
      list(APPEND NATIVE_SRCS "qemu_aac_late_sbr.c" "qemu_aac_sbr_gap.c" "qemu_aac_recording.c" "qemu_aac_faults.c")
      if(CONFIG_YORADIO_QEMU_AAC_HIGH_HISTORY_PC19_SIDECAR OR CONFIG_YORADIO_AAC_HIGH_HISTORY_PC19)
        list(APPEND NATIVE_SRCS "qemu_aac_pc19.c")
      endif()
    endif()
    if(CONFIG_YORADIO_QEMU_AAC_COMPACT_ADAPTER_TEST)
      list(APPEND NATIVE_SRCS "qemu_aac_compact_adapter.c")
    endif()
    if(CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT)
      list(APPEND NATIVE_SRCS "aac_pointer_audit.c")
      set_source_files_properties(aac_pointer_audit.c PROPERTIES COMPILE_OPTIONS "-fno-strict-aliasing")
    endif()
    if(CONFIG_YORADIO_QEMU_AAC_LOW_LIFETIME)
      list(APPEND NATIVE_SRCS "qemu_aac_low_lifetime.c")
    endif()
    if(CONFIG_YORADIO_QEMU_AAC_BFP16_TEST OR CONFIG_YORADIO_QEMU_AAC_PACKED_HISTORY_TEST)
      list(APPEND NATIVE_SRCS "qemu_aac_bfp16.c")
    endif()
    if(CONFIG_YORADIO_QEMU_AAC_PACKED_HISTORY_TEST)
      if(CONFIG_YORADIO_QEMU_AAC_COMBINED_STORAGE_TEST)
        list(APPEND NATIVE_SRCS "qemu_aac_area_storage.c" "qemu_aac_ps_history_port.c")
        set_source_files_properties(qemu_aac_ps_history_port.c PROPERTIES COMPILE_DEFINITIONS
          "packed_history_reset=ps_storage_reset;packed_history_select=ps_storage_select;packed_history_report=ps_storage_report;packed_history_arithmetic_tests=ps_storage_arithmetic_tests")
      elseif(CONFIG_YORADIO_QEMU_AAC_AREA_STORAGE_TEST)
        list(APPEND NATIVE_SRCS "qemu_aac_area_storage.c")
      elseif(CONFIG_YORADIO_QEMU_AAC_SBR_LAYOUT_TEST)
        if(CONFIG_YORADIO_QEMU_AAC_SMOOTHING_TEST)
          list(APPEND NATIVE_SRCS "qemu_aac_smoothing.c" "qemu_aac_smoothing_fir.c")
        else()
          list(APPEND NATIVE_SRCS "qemu_aac_sbr_layout.c")
        endif()
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
  if(CONFIG_YORADIO_DIRECT_DMA_PCM)
    list(APPEND NATIVE_SRCS "native_audio_output_dma.c")
  else()
    list(APPEND NATIVE_SRCS "native_audio_output.c")
  endif()
endif()

if(CONFIG_YORADIO_AAC_PS_PC16 OR CONFIG_YORADIO_QEMU_AAC_PC16_WRITE_TEST)
  list(APPEND NATIVE_SRCS "aac_ps_pc16.c")
endif()

if(CONFIG_YORADIO_AAC_HIGH_HISTORY OR CONFIG_YORADIO_QEMU_AAC_HIGH_HISTORY_TEST)
  list(APPEND NATIVE_SRCS "aac_high_history.c")
endif()
if(CONFIG_YORADIO_QEMU_AAC_HIGH_HISTORY_PC19 OR CONFIG_YORADIO_AAC_HIGH_HISTORY_PC19)
  # All ABI consumers, including those that include the layout header directly.
  add_compile_definitions(AAC_HIGH_HISTORY_PC19=1)
endif()
if(CONFIG_YORADIO_QEMU_AAC_HIGH_HISTORY_PC19_SIDECAR OR CONFIG_YORADIO_AAC_HIGH_HISTORY_PC19)
  add_compile_definitions(AAC_HIGH_HISTORY_PC19_SIDECAR=1)
endif()
if(CONFIG_YORADIO_AAC_SMOOTHING_HISTORY OR CONFIG_YORADIO_QEMU_AAC_SMOOTHING_HISTORY_TEST)
  list(APPEND NATIVE_SRCS "aac_smoothing_history.c")
  add_compile_definitions(AAC_SMOOTHING_HISTORY_FOUR=1)
endif()
if(CONFIG_YORADIO_AAC_LOW_WORKSPACE OR CONFIG_YORADIO_QEMU_AAC_LOW_WORKSPACE)
  add_compile_definitions(AAC_LOW_WORKSPACE=1)
endif()
if(CONFIG_YORADIO_AAC_ASYMMETRIC_OWNER OR CONFIG_YORADIO_QEMU_AAC_ASYMMETRIC_OWNER)
  add_compile_definitions(AAC_ASYMMETRIC_OWNER=1)
endif()
if(CONFIG_YORADIO_QEMU_AAC_SMOOTHING_HISTORY_TEST)
  list(APPEND NATIVE_SRCS "qemu_aac_smoothing_history.c")
endif()

if(CONFIG_YORADIO_HEAP_LAYOUT_DIAGNOSTICS)
  list(APPEND NATIVE_SRCS "heap_layout_diagnostic.c")
endif()

if(CONFIG_YORADIO_TCP_ALLOCATION_DIAGNOSTICS)
  list(APPEND NATIVE_SRCS "tcp_allocation_diagnostic.c")
endif()

if(CONFIG_YORADIO_TCP_PCB_POOL)
  list(APPEND NATIVE_SRCS "tcp_pcb_pool.c")
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
    esp-tls
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

yoradio_aac_profile()
yoradio_vorbis_repair()
if(CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER)
  target_sources(${COMPONENT_LIB} PRIVATE "adaptive_input.c")
endif()
if(CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER OR CONFIG_YORADIO_TLS_LARGE_BLOCK_RESERVE)
  target_sources(${COMPONENT_LIB} PRIVATE "tls_input_reserve.c")
  target_link_options(${COMPONENT_LIB} INTERFACE
    "-Wl,--wrap=esp_mbedtls_mem_calloc"
    "-Wl,--undefined=__wrap_esp_mbedtls_mem_calloc")
endif()
if(CONFIG_YORADIO_TLS_LARGE_BLOCK_RESERVE)
  idf_component_get_property(tls_reserve_mbedtls_dir mbedtls COMPONENT_DIR)
  target_sources(${COMPONENT_LIB} PRIVATE "tls_large_reserve.c")
  target_include_directories(${COMPONENT_LIB} PRIVATE "${tls_reserve_mbedtls_dir}/port/dynamic")
  target_link_options(${COMPONENT_LIB} INTERFACE
    "-Wl,--wrap=esp_mbedtls_mem_free" "-Wl,--undefined=__wrap_esp_mbedtls_mem_free")
endif()
if(CONFIG_ESP_TLS_USING_MBEDTLS)
  target_sources(${COMPONENT_LIB} PRIVATE "tls_stream_eof.c")
  # The SDK already owns __wrap_mbedtls_ssl_read for dynamic RX buffers.
  # Redirect only its ESP-TLS caller, preserving the SDK's wrapper chain.
  idf_component_get_property(tls_dir esp-tls COMPONENT_DIR)
  idf_component_get_property(tls_lib esp-tls COMPONENT_LIB)
  set_property(SOURCE "${tls_dir}/esp_tls_mbedtls.c" TARGET_DIRECTORY ${tls_lib}
    APPEND PROPERTY COMPILE_DEFINITIONS "mbedtls_ssl_read=yoradio_mbedtls_ssl_read")
  # ESP-TLS may appear after libmain in the link order; retain the entry point.
  target_link_options(${COMPONENT_LIB} INTERFACE "-Wl,--undefined=yoradio_mbedtls_ssl_read")
endif()
if(CONFIG_YORADIO_HEAP_FRAGMENT_PROBE)
  target_sources(${COMPONENT_LIB} PRIVATE "heap_fragment_probe.c")
  target_link_options(${COMPONENT_LIB} INTERFACE
    "-Wl,--wrap=heap_caps_free" "-Wl,--wrap=heap_caps_realloc_base"
    "-Wl,--undefined=esp_heap_trace_alloc_hook" "-Wl,--undefined=esp_heap_trace_free_hook")
endif()
if(CONFIG_YORADIO_RX_BUFFER_DIAGNOSTICS)
  target_sources(${COMPONENT_LIB} PRIVATE "rx_buffer_diagnostic.c")
  target_link_options(${COMPONENT_LIB} INTERFACE
    "-Wl,--wrap=esp_pbuf_allocate" "-Wl,--wrap=esp_netif_free_rx_buffer")
endif()
if(CONFIG_YORADIO_DIRECT_DMA_PCM AND NOT CONFIG_YORADIO_QEMU)
  # The generator uses the installed driver's typed DMA state. Refuse an
  # unaudited driver update rather than guessing its private ABI/ownership.
  idf_component_get_property(i2s_dir esp_driver_i2s COMPONENT_DIR)
  idf_component_get_property(i2s_lib esp_driver_i2s COMPONENT_LIB)
  file(SHA256 "${i2s_dir}/i2s_common.c" i2s_common_sha)
  file(SHA256 "${i2s_dir}/i2s_private.h" i2s_private_sha)
  if(NOT i2s_common_sha STREQUAL "1728238e257a29020297c13b5fe41dd7de03488f77d43b87160ca211cbee0641" OR
     NOT i2s_private_sha STREQUAL "6348b15be7461b39eecbff263f500cfbb5fa1e0c149d5597c7ae6902ba59a087")
    message(FATAL_ERROR "Direct PCM generation requires the audited ESP-IDF 6.0.2 I2S driver")
  endif()
  target_sources(${i2s_lib} PRIVATE "${CMAKE_CURRENT_LIST_DIR}/native_i2s_generator.c")
  target_include_directories(${i2s_lib} PRIVATE "${CMAKE_CURRENT_LIST_DIR}" "${i2s_dir}")
endif()
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

if(CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT OR CONFIG_YORADIO_AAC_LATE_SBR)
  target_include_directories(${COMPONENT_LIB} PRIVATE "${YORADIO_ROOT}/../tools/codec_benchmark")
endif()
if(CONFIG_YORADIO_HEAP_LAYOUT_DIAGNOSTICS)
  target_link_options(${COMPONENT_LIB} INTERFACE
    "-Wl,--wrap=cpu_profiler_memory" "-Wl,--wrap=media_lib_module_malloc"
    "-Wl,--wrap=media_lib_module_calloc")
endif()

if(CONFIG_YORADIO_TCP_ALLOCATION_DIAGNOSTICS)
  target_link_options(${COMPONENT_LIB} INTERFACE
    "-Wl,--wrap=memp_malloc" "-Wl,--wrap=memp_free"
    "-Wl,--undefined=__wrap_memp_malloc")
endif()

if(CONFIG_YORADIO_TCP_PCB_POOL)
  target_link_options(${COMPONENT_LIB} INTERFACE
    "-Wl,--wrap=memp_malloc" "-Wl,--wrap=memp_free"
    "-Wl,--undefined=__wrap_memp_malloc")
endif()

if(CONFIG_YORADIO_AAC_EARLY_SBR_RESERVE OR CONFIG_YORADIO_AAC_EARLY_SCRATCH_RESERVE)
  file(SHA256 "$ENV{YORADIO_AUDIO_CODEC_COMPONENT}/lib/esp32c3/libesp_audio_codec.a" AAC_RESERVE_SHA256)
  if(NOT AAC_RESERVE_SHA256 STREQUAL "311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909")
    message(FATAL_ERROR "AAC reservation requires the audited ESP32-C3 AAC archive")
  endif()
  target_link_options(${COMPONENT_LIB} INTERFACE "-Wl,--wrap=media_lib_module_calloc")
endif()

if(CONFIG_YORADIO_AAC_RELOCATE_PS)
  target_link_options(${COMPONENT_LIB} INTERFACE
    "-Wl,--wrap=media_lib_free" "-Wl,--wrap=sbr_applied" "-Wl,--wrap=ps_read_data")
endif()

if(CONFIG_YORADIO_AAC_PS_PC16)
  target_link_options(${COMPONENT_LIB} INTERFACE
    "-Wl,--wrap=ps_allocate_decoder" "-Wl,--wrap=ps_decorrelate")
endif()

if(CONFIG_YORADIO_AAC_COMPACT_SBR OR CONFIG_YORADIO_QEMU_AAC_SMOOTHING_TEST)
  set(PINNED_AAC_ARCHIVE "$ENV{YORADIO_AUDIO_CODEC_COMPONENT}/lib/esp32c3/libesp_audio_codec.a")
  set(COMPACT5_DIR "${CMAKE_CURRENT_BINARY_DIR}/compact5")
  file(MAKE_DIRECTORY "${COMPACT5_DIR}")
  set(AAC_LAYOUT_SOURCE aac_abi_layout.c)
  set(AAC_LAYOUT_PATCHER compact_sbr_tables.py)
  set(AAC_LAYOUT_FLAGS "")
  if(CONFIG_YORADIO_AAC_HIGH_HISTORY OR CONFIG_YORADIO_QEMU_AAC_HIGH_HISTORY_TEST)
    set(AAC_LAYOUT_SOURCE aac_high_abi_layout.c)
    set(AAC_LAYOUT_PATCHER compact_high_history.py)
    if(CONFIG_YORADIO_QEMU_AAC_HIGH_HISTORY_PC16)
      list(APPEND AAC_LAYOUT_FLAGS -DAAC_HIGH_HISTORY_PC16=1)
    endif()
    if(CONFIG_YORADIO_QEMU_AAC_HIGH_HISTORY_PC19 OR CONFIG_YORADIO_AAC_HIGH_HISTORY_PC19)
      list(APPEND AAC_LAYOUT_FLAGS -DAAC_HIGH_HISTORY_PC19=1)
    endif()
    if(CONFIG_YORADIO_QEMU_AAC_HIGH_HISTORY_PC19_SIDECAR OR CONFIG_YORADIO_AAC_HIGH_HISTORY_PC19)
      list(APPEND AAC_LAYOUT_FLAGS -DAAC_HIGH_HISTORY_PC19_SIDECAR=1)
    endif()
    target_link_options(${COMPONENT_LIB} INTERFACE "-Wl,--wrap=compact5_sbr_dec")
  endif()
  if(CONFIG_YORADIO_AAC_SMOOTHING_HISTORY OR CONFIG_YORADIO_QEMU_AAC_SMOOTHING_HISTORY_TEST)
    set(AAC_LAYOUT_SOURCE aac_smoothing_history_layout.c)
    set(AAC_LAYOUT_PATCHER compact_smoothing_history.py)
    list(APPEND AAC_LAYOUT_FLAGS -DAAC_SMOOTHING_HISTORY_FOUR=1)
    target_link_options(${COMPONENT_LIB} INTERFACE "-Wl,--wrap=compact5_init_sbr_dec")
  endif()
  if(CONFIG_YORADIO_AAC_LOW_WORKSPACE OR CONFIG_YORADIO_QEMU_AAC_LOW_WORKSPACE)
    set(AAC_LAYOUT_SOURCE aac_low_workspace_layout.c)
    set(AAC_LAYOUT_PATCHER compact_low_workspace.py)
    list(APPEND AAC_LAYOUT_FLAGS -DAAC_LOW_WORKSPACE=1)
  endif()
  if(CONFIG_YORADIO_AAC_ASYMMETRIC_OWNER OR CONFIG_YORADIO_QEMU_AAC_ASYMMETRIC_OWNER)
    set(AAC_LAYOUT_SOURCE aac_asymmetric_owner_layout.c)
    set(AAC_LAYOUT_PATCHER compact_asymmetric_owner.py)
    list(APPEND AAC_LAYOUT_FLAGS -DAAC_ASYMMETRIC_OWNER=1)
  endif()
  execute_process(COMMAND "${CMAKE_C_COMPILER}" -std=c11 -march=rv32imc -mabi=ilp32 ${AAC_LAYOUT_FLAGS}
    -I "${CMAKE_CURRENT_LIST_DIR}" -c "${YORADIO_ROOT}/../tools/codec_benchmark/${AAC_LAYOUT_SOURCE}"
    -o "${COMPACT5_DIR}/layout.o" RESULT_VARIABLE COMPACT5_LAYOUT_RESULT)
  if(NOT COMPACT5_LAYOUT_RESULT EQUAL 0)
    message(FATAL_ERROR "AAC compiler ABI layout checks failed")
  endif()
  execute_process(COMMAND "${PYTHON}" "${YORADIO_ROOT}/../tools/codec_benchmark/${AAC_LAYOUT_PATCHER}"
    --archive "${PINNED_AAC_ARCHIVE}" --output "${COMPACT5_DIR}"
    --ar "${CMAKE_AR}" --objcopy "${CMAKE_OBJCOPY}"
    --layout-object "${COMPACT5_DIR}/layout.o"
    RESULT_VARIABLE COMPACT5_RESULT)
  if(NOT COMPACT5_RESULT EQUAL 0)
    message(FATAL_ERROR "Compact SBR table ABI patch failed")
  endif()
  if(CONFIG_YORADIO_AAC_LATE_SBR)
    execute_process(COMMAND "${PYTHON}" "${YORADIO_ROOT}/../tools/codec_benchmark/patch_aac_late_sbr.py"
      --native "${COMPACT5_DIR}/pvmp4audiodecoderframe.c.obj"
      --bridge "${CMAKE_CURRENT_LIST_DIR}/aac_late_sbr_bridge.S"
      --cc "${CMAKE_C_COMPILER}" --linker "${CMAKE_LINKER}" --objcopy "${CMAKE_OBJCOPY}"
      RESULT_VARIABLE AAC_LATE_SBR_RESULT)
    if(NOT AAC_LATE_SBR_RESULT EQUAL 0)
      message(FATAL_ERROR "Late SBR branch verification failed")
    endif()
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
      "${YORADIO_ROOT}/../tools/codec_benchmark/patch_aac_late_sbr.py"
      "${CMAKE_CURRENT_LIST_DIR}/aac_late_sbr_bridge.S")
  endif()
  foreach(FUNC init_sbr_dec sbr_open sbr_read_data sbr_applied ps_allocate_decoder sbr_dec pvmp4audiodecoderframe)
    target_sources(${COMPONENT_LIB} PRIVATE "${COMPACT5_DIR}/${FUNC}.c.obj")
  endforeach()
  set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
    "${YORADIO_ROOT}/../tools/codec_benchmark/compact_sbr_tables.py"
    "${YORADIO_ROOT}/../tools/codec_benchmark/aac_abi_layout.c"
    "${CMAKE_CURRENT_LIST_DIR}/aac_sbr_abi.h"
    "${CMAKE_CURRENT_LIST_DIR}/aac_high_history_abi.h"
    "${YORADIO_ROOT}/../tools/codec_benchmark/aac_high_abi_layout.c"
    "${YORADIO_ROOT}/../tools/codec_benchmark/compact_high_history.py"
    "${YORADIO_ROOT}/../tools/codec_benchmark/aac_smoothing_history_layout.c"
    "${YORADIO_ROOT}/../tools/codec_benchmark/compact_smoothing_history.py"
    "${YORADIO_ROOT}/../tools/codec_benchmark/aac_low_workspace_layout.c"
    "${YORADIO_ROOT}/../tools/codec_benchmark/compact_low_workspace.py"
    "${YORADIO_ROOT}/../tools/codec_benchmark/aac_asymmetric_owner_layout.c"
    "${YORADIO_ROOT}/../tools/codec_benchmark/compact_asymmetric_owner.py")
endif()

if(CONFIG_YORADIO_AAC_LATE_SBR)
  set_source_files_properties(aac_compact_owner.c PROPERTIES COMPILE_OPTIONS "-fno-strict-aliasing")
endif()

if(CONFIG_YORADIO_AAC_COMPACT_SBR)
  target_link_options(${COMPONENT_LIB} INTERFACE
    "-Wl,--wrap=media_lib_module_calloc" "-Wl,--wrap=media_lib_free"
    "-Wl,--wrap=PVMP4AudioDecodeFrame" "-Wl,--wrap=PVMP4AudioDecoderResetBuffer"
    "-Wl,--wrap=compact5_sbr_applied" "-Wl,--wrap=compact5_sbr_open"
    "-Wl,--wrap=ps_read_data")
endif()

if(CONFIG_YORADIO_QEMU_AAC_BFP16_TEST)
  target_link_options(${COMPONENT_LIB} INTERFACE
    "-Wl,--wrap=calc_sbr_anafilterbank"
    "-Wl,--wrap=calc_sbr_anafilterbank_LC")
endif()

if(CONFIG_YORADIO_QEMU_AAC_PACKED_HISTORY_TEST)
  if(CONFIG_YORADIO_QEMU_AAC_COMBINED_STORAGE_TEST)
    target_link_options(${COMPONENT_LIB} INTERFACE
      "-Wl,--wrap=sbr_dec" "-Wl,--wrap=calc_sbr_anafilterbank" "-Wl,--wrap=calc_sbr_anafilterbank_LC")
  endif()
  if(CONFIG_YORADIO_QEMU_AAC_AREA_STORAGE_TEST OR CONFIG_YORADIO_QEMU_AAC_COMBINED_STORAGE_TEST)
    target_link_options(${COMPONENT_LIB} INTERFACE
      "-Wl,--wrap=trans4m_freq_2_time_fxp_1" "-Wl,--wrap=trans4m_freq_2_time_fxp_2"
      "-Wl,--wrap=ps_hybrid_analysis" "-Wl,--wrap=ps_pwr_transient_detection")
  endif()
  if(CONFIG_YORADIO_QEMU_AAC_PS_HISTORY_PORT_TEST OR CONFIG_YORADIO_QEMU_AAC_SBR_LAYOUT_TEST)
    set(PINNED_AAC_ARCHIVE "$ENV{YORADIO_AUDIO_CODEC_COMPONENT}/lib/esp32c3/libesp_audio_codec.a")
    file(SHA256 "${PINNED_AAC_ARCHIVE}" AAC_ARCHIVE_SHA256)
    if(NOT AAC_ARCHIVE_SHA256 STREQUAL "311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909")
      message(FATAL_ERROR "PS storage port requires the audited ESP32-C3 AAC archive")
    endif()
    if(CONFIG_YORADIO_QEMU_AAC_SBR_LAYOUT_TEST)
      target_link_options(${COMPONENT_LIB} INTERFACE "-Wl,--wrap=media_lib_module_calloc"
        "-Wl,--wrap=media_lib_free" "-Wl,--wrap=ps_read_data")
      if(CONFIG_YORADIO_QEMU_AAC_SMOOTHING_TEST)
        target_link_options(${COMPONENT_LIB} INTERFACE "-Wl,--wrap=PVMP4AudioDecodeFrame"
          "-Wl,--wrap=PVMP4AudioDecoderResetBuffer")
        if(CONFIG_YORADIO_QEMU_AAC_COMPACT_OWNER_TEST)
          target_link_options(${COMPONENT_LIB} INTERFACE "-Wl,--wrap=compact5_sbr_applied")
        endif()

      else()
        target_link_options(${COMPONENT_LIB} INTERFACE "-Wl,--wrap=sbr_applied")
      endif()
      if(CONFIG_YORADIO_QEMU_AAC_RESET_TEST)
        target_link_options(${COMPONENT_LIB} INTERFACE "-Wl,--wrap=PVMP4AudioDecoderResetBuffer")
        if(CONFIG_YORADIO_QEMU_AAC_COMPACT_OWNER_TEST)
          target_link_options(${COMPONENT_LIB} INTERFACE "-Wl,--wrap=compact5_sbr_open")
        else()
          target_link_options(${COMPONENT_LIB} INTERFACE "-Wl,--wrap=sbr_open")
        endif()
      endif()
    else()
      target_link_options(${COMPONENT_LIB} INTERFACE "-Wl,--wrap=ps_decorrelate" "-Wl,--wrap=ps_allocate_decoder")
    endif()
  else()
    target_link_options(${COMPONENT_LIB} INTERFACE "-Wl,--wrap=sbr_dec")
  endif()
endif()

if(CONFIG_YORADIO_QEMU_AAC_TEST)
  configure_file("${YORADIO_ROOT}/../tests/fixtures/aac_sbr_gap/source-he-32000-mono.aac"
                 "${CMAKE_CURRENT_BINARY_DIR}/he_mono_metadata.aac" COPYONLY)
  target_add_binary_data(${COMPONENT_LIB} "${CMAKE_CURRENT_BINARY_DIR}/he_mono_metadata.aac" BINARY)
  foreach(FIXTURE lc-44100-stereo lc-22050-mono lc-48000-stereo
                  he-44100-stereo he-48000-stereo hev2-44100-stereo)
    configure_file("${YORADIO_ROOT}/../tests/fixtures/aac_stream_format/${FIXTURE}.aac"
                   "${CMAKE_CURRENT_BINARY_DIR}/${FIXTURE}.aac" COPYONLY)
    target_add_binary_data(${COMPONENT_LIB}
                          "${CMAKE_CURRENT_BINARY_DIR}/${FIXTURE}.aac" BINARY)
  endforeach()
  if(CONFIG_YORADIO_QEMU_AAC_LATE_SBR_TEST)
    foreach(FIXTURE header-only sbr-truncated sbr-count-overrun fill-count-overrun)
      configure_file("${YORADIO_ROOT}/../tests/fixtures/aac_faults/${FIXTURE}.aac"
                     "${CMAKE_CURRENT_BINARY_DIR}/${FIXTURE}.aac" COPYONLY)
      target_add_binary_data(${COMPONENT_LIB} "${CMAKE_CURRENT_BINARY_DIR}/${FIXTURE}.aac" BINARY)
    endforeach()
    foreach(FIXTURE he-44100-stereo he-48000-stereo hev2-44100-stereo he-32000-mono)
      foreach(KIND source missing)
        configure_file("${YORADIO_ROOT}/../tests/fixtures/aac_sbr_gap/${KIND}-${FIXTURE}.aac"
                       "${CMAKE_CURRENT_BINARY_DIR}/${KIND}-${FIXTURE}.aac" COPYONLY)
        target_add_binary_data(${COMPONENT_LIB}
                              "${CMAKE_CURRENT_BINARY_DIR}/${KIND}-${FIXTURE}.aac" BINARY)
      endforeach()
    endforeach()
  endif()
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
