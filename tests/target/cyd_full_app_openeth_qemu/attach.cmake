# Loaded only by the dedicated QEMU build through CMAKE_PROJECT_<name>_INCLUDE.
function(cyd_attach_openeth_probe)
  if(NOT CONFIG_IDF_TARGET_ESP32 OR NOT CONFIG_ETH_USE_OPENETH OR CONFIG_FREERTOS_UNICORE)
    message(FATAL_ERROR "CYD OpenETH probe requires the dual-core ESP32 and OpenETH")
  endif()
  idf_component_get_property(app main COMPONENT_LIB)
  target_sources(${app} PRIVATE "${CMAKE_CURRENT_FUNCTION_LIST_DIR}/network.c")
  target_link_libraries(${app} PRIVATE idf::esp_eth)
  target_link_options(${app} INTERFACE "-Wl,--wrap=network_service_start")
endfunction()

cmake_language(DEFER CALL cyd_attach_openeth_probe)
