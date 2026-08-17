get_filename_component(YORADIO_ROOT
  "${CMAKE_CURRENT_LIST_DIR}/../../../yoRadio" ABSOLUTE)
file(TO_CMAKE_PATH "$ENV{YORADIO_ARDUINO_LIBRARIES}" ARDUINO_LIBRARIES)

set(YORADIO_SRCS
  "${YORADIO_ROOT}/src/main.cpp"
  "${YORADIO_ROOT}/src/core/commandhandler.cpp"
  "${YORADIO_ROOT}/src/core/config.cpp"
  "${YORADIO_ROOT}/src/core/controls.cpp"
  "${YORADIO_ROOT}/src/core/display.cpp"
  "${YORADIO_ROOT}/src/core/netserver.cpp"
  "${YORADIO_ROOT}/src/core/network.cpp"
  "${YORADIO_ROOT}/src/core/player.cpp"
  "${YORADIO_ROOT}/src/core/rtcsupport.cpp"
  "${YORADIO_ROOT}/src/core/sdmanager.cpp"
  "${YORADIO_ROOT}/src/core/telnet.cpp"
  "${YORADIO_ROOT}/src/core/timekeeper.cpp"
  "${YORADIO_ROOT}/src/core/touchscreen.cpp"

  "${YORADIO_ROOT}/src/AsyncWebServer/AsyncEventSource.cpp"
  "${YORADIO_ROOT}/src/AsyncWebServer/AsyncTCP.cpp"
  "${YORADIO_ROOT}/src/AsyncWebServer/AsyncWebSocket.cpp"
  "${YORADIO_ROOT}/src/AsyncWebServer/SPIFFSEditor.cpp"
  "${YORADIO_ROOT}/src/AsyncWebServer/WebAuthentication.cpp"
  "${YORADIO_ROOT}/src/AsyncWebServer/WebHandlers.cpp"
  "${YORADIO_ROOT}/src/AsyncWebServer/WebRequest.cpp"
  "${YORADIO_ROOT}/src/AsyncWebServer/WebResponses.cpp"
  "${YORADIO_ROOT}/src/AsyncWebServer/WebServer.cpp"

  "${YORADIO_ROOT}/src/audioI2S/Audio.cpp"
  "${YORADIO_ROOT}/src/audioI2S/AudioNormalizer.cpp"
  "${YORADIO_ROOT}/src/audioI2S/CodecMemoryArena.cpp"
  "${YORADIO_ROOT}/src/audioI2S/OggDecoder.cpp"
  "${YORADIO_ROOT}/src/audioI2S/aac_decoder/aac_decoder.cpp"
  "${YORADIO_ROOT}/src/audioI2S/flac_decoder/flac_decoder.cpp"
  "${YORADIO_ROOT}/src/audioI2S/mp3_decoder/mp3_decoder.cpp"
  "${YORADIO_ROOT}/src/audioI2S/mp3_decoder/Mp3DecoderSelector.cpp"

  "${YORADIO_ROOT}/src/displays/displayST7789.cpp"
  "${YORADIO_ROOT}/src/displays/fonts/yofont10x14.c"
  "${YORADIO_ROOT}/src/displays/fonts/yofont5x7.c"
  "${YORADIO_ROOT}/src/displays/tools/utf8Rus.cpp"
  "${YORADIO_ROOT}/src/displays/widgets/pages.cpp"
  "${YORADIO_ROOT}/src/displays/widgets/widgets.cpp"
  "${YORADIO_ROOT}/src/OneButton/OneButton.cpp"
  "${YORADIO_ROOT}/src/pluginsManager/pluginsManager.cpp"
  "${YORADIO_ROOT}/src/yoEncoder/yoEncoder.cpp"

  "${ARDUINO_LIBRARIES}/Adafruit_BusIO/Adafruit_BusIO_Register.cpp"
  "${ARDUINO_LIBRARIES}/Adafruit_BusIO/Adafruit_GenericDevice.cpp"
  "${ARDUINO_LIBRARIES}/Adafruit_BusIO/Adafruit_I2CDevice.cpp"
  "${ARDUINO_LIBRARIES}/Adafruit_BusIO/Adafruit_SPIDevice.cpp"
  "${ARDUINO_LIBRARIES}/Adafruit_GFX_Library/Adafruit_GFX.cpp"
  "${ARDUINO_LIBRARIES}/Adafruit_GFX_Library/Adafruit_GrayOLED.cpp"
  "${ARDUINO_LIBRARIES}/Adafruit_GFX_Library/Adafruit_SPITFT.cpp"
  "${ARDUINO_LIBRARIES}/Adafruit_ST7735_and_ST7789_Library/Adafruit_ST77xx.cpp"
  "${ARDUINO_LIBRARIES}/Adafruit_ST7735_and_ST7789_Library/Adafruit_ST7789.cpp"
  "${ARDUINO_LIBRARIES}/XPT2046_Touchscreen/XPT2046_Touchscreen.cpp")

if(YORADIO_DAC_BACKEND STREQUAL "legacy")
  if(NOT DEFINED ENV{YORADIO_LEGACY_IDF})
    message(FATAL_ERROR "YORADIO_LEGACY_IDF is not set; use build.ps1")
  endif()
  file(TO_CMAKE_PATH "$ENV{YORADIO_LEGACY_IDF}" LEGACY_IDF)
  list(APPEND YORADIO_SRCS
    "compat/idf5_legacy_dac_backend.cpp"
    "${LEGACY_IDF}/components/driver/deprecated/i2s_legacy.c")
  set_source_files_properties(
    "${LEGACY_IDF}/components/driver/deprecated/i2s_legacy.c"
    PROPERTIES COMPILE_OPTIONS
      "-include;hal/i2s_periph.h;-Wno-error=unused-but-set-parameter")
elseif(YORADIO_DAC_BACKEND STREQUAL "pdm")
  list(APPEND YORADIO_SRCS
    "${YORADIO_ROOT}/src/audioI2S/PdmOutput.cpp")
else()
  list(APPEND YORADIO_SRCS "compat/idf6_i2s_compat.cpp")
endif()

idf_component_register(
  SRCS ${YORADIO_SRCS}
  INCLUDE_DIRS
    "${YORADIO_ROOT}"
    "${YORADIO_ROOT}/src"
    "compat"
    "${ARDUINO_LIBRARIES}/Adafruit_BusIO"
    "${ARDUINO_LIBRARIES}/Adafruit_GFX_Library"
    "${ARDUINO_LIBRARIES}/Adafruit_ST7735_and_ST7789_Library"
    "${ARDUINO_LIBRARIES}/XPT2046_Touchscreen"
  REQUIRES
    arduino
    efuse
    esp_adc
    esp_driver_dac
    esp_driver_i2s
    esp_driver_gpio
    esp_driver_sdmmc
    esp_driver_sdspi
    esp_hw_support
    esp_netif
    esp_pm
    esp_ringbuf
    esp_wifi
    mbedtls
    esp_audio_codec
    wear_levelling)

if(YORADIO_DAC_BACKEND STREQUAL "legacy")
  target_include_directories(${COMPONENT_LIB} BEFORE PRIVATE
    "${LEGACY_IDF}/components/driver/deprecated"
    "${LEGACY_IDF}/components/esp_driver_i2s/include")
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_DAC_BACKEND_LEGACY=1
    CONFIG_I2S_SUPPRESS_DEPRECATE_WARN=1
    I2S_MODE_ADC_BUILT_IN=32
    SOC_I2S_NUM=2
    SOC_I2S_SUPPORTS_ADC_DAC=1
    SOC_I2S_SUPPORTS_ADC=0
    SOC_I2S_SUPPORTS_DAC=1)
elseif(YORADIO_DAC_BACKEND STREQUAL "pdm")
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_AUDIO_BACKEND_PDM=1
    I2S_INTERNAL_OUTPUT=1)
else()
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_DAC_BACKEND_CONTINUOUS=1)
endif()

# Give this build an explicit identity without changing the Arduino branch.
target_compile_definitions(${COMPONENT_LIB} PRIVATE
  YORADIO_ESP_IDF_MINIMAL=1)
target_compile_options(${COMPONENT_LIB} PRIVATE
  -Wno-unused-variable
  -Wno-unused-function)

spiffs_create_partition_image(spiffs "${YORADIO_ROOT}/data" FLASH_IN_PROJECT)
