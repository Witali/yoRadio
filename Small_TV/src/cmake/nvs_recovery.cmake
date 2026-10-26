# Generate a consistent local component: private cleanup return types must agree
# in every NVS translation unit, including headers included by other headers.
idf_component_get_property(small_tv_nvs_lib nvs_flash COMPONENT_LIB)
idf_build_get_property(small_tv_nvs_python PYTHON)
file(TO_CMAKE_PATH "$ENV{IDF_PATH}/components/nvs_flash" small_tv_nvs_original)
set(small_tv_nvs_overlay "${CMAKE_BINARY_DIR}/sdk/nvs")
set(small_tv_nvs_patcher "${CMAKE_CURRENT_LIST_DIR}/../tools/prepare_nvs_component.py")
file(GLOB_RECURSE small_tv_nvs_vendor CONFIGURE_DEPENDS
    "${small_tv_nvs_original}/src/*" "${small_tv_nvs_original}/include/*"
    "${small_tv_nvs_original}/private_include/*")
file(GLOB small_tv_nvs_fragments CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/../storage/nvs/*.inc")
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
    ${small_tv_nvs_vendor} ${small_tv_nvs_fragments} "${small_tv_nvs_patcher}"
    "${CMAKE_CURRENT_LIST_DIR}/../tools/patch_nvs_page.py"
    "${CMAKE_CURRENT_LIST_DIR}/../tools/nvs_component_sources.json")
execute_process(COMMAND "${small_tv_nvs_python}" -B "${small_tv_nvs_patcher}"
    --component "${small_tv_nvs_original}" --output "${small_tv_nvs_overlay}"
    --reports "${CMAKE_BINARY_DIR}" RESULT_VARIABLE small_tv_nvs_status OUTPUT_QUIET)
if(NOT small_tv_nvs_status EQUAL 0)
    message(FATAL_ERROR "Small TV NVS source qualification/overlay failed")
endif()
get_target_property(small_tv_nvs_sources ${small_tv_nvs_lib} SOURCES)
set(small_tv_nvs_updated "")
foreach(small_tv_nvs_source IN LISTS small_tv_nvs_sources)
    get_filename_component(small_tv_nvs_absolute "${small_tv_nvs_source}" ABSOLUTE
        BASE_DIR "${small_tv_nvs_original}")
    file(RELATIVE_PATH small_tv_nvs_relative "${small_tv_nvs_original}/src" "${small_tv_nvs_absolute}")
    if(small_tv_nvs_relative MATCHES "[/\\\\]" OR NOT EXISTS "${small_tv_nvs_overlay}/${small_tv_nvs_relative}")
        message(FATAL_ERROR "Unexpected source in NVS component: ${small_tv_nvs_source}")
    endif()
    list(APPEND small_tv_nvs_updated "${small_tv_nvs_overlay}/${small_tv_nvs_relative}")
endforeach()
set_property(TARGET ${small_tv_nvs_lib} PROPERTY SOURCES "${small_tv_nvs_updated}")
target_include_directories(${small_tv_nvs_lib} BEFORE PRIVATE "${small_tv_nvs_overlay}")
