# Replace only Small TV's NVS Page translation unit after IDF creates its target.
idf_component_get_property(small_tv_nvs_lib nvs_flash COMPONENT_LIB)
idf_build_get_property(small_tv_nvs_python PYTHON)
file(TO_CMAKE_PATH "$ENV{IDF_PATH}/components/nvs_flash/src/nvs_page.cpp"
    small_tv_nvs_original)
set(small_tv_nvs_fixed "${CMAKE_BINARY_DIR}/sdk/nvs_page.cpp")
set(small_tv_nvs_patcher "${CMAKE_CURRENT_LIST_DIR}/../tools/patch_nvs_page.py")
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
    "${small_tv_nvs_original}" "${small_tv_nvs_patcher}")
execute_process(COMMAND "${small_tv_nvs_python}" -B "${small_tv_nvs_patcher}"
    --source "${small_tv_nvs_original}" --output "${small_tv_nvs_fixed}"
    --report "${CMAKE_BINARY_DIR}/nvs-recovery.json"
    RESULT_VARIABLE small_tv_nvs_patch_status OUTPUT_QUIET)
if(NOT small_tv_nvs_patch_status EQUAL 0)
    message(FATAL_ERROR "Small TV NVS source qualification/patch failed")
endif()
get_target_property(small_tv_nvs_sources ${small_tv_nvs_lib} SOURCES)
set(small_tv_nvs_replaced 0)
set(small_tv_nvs_updated "")
foreach(small_tv_nvs_source IN LISTS small_tv_nvs_sources)
    if(small_tv_nvs_source STREQUAL small_tv_nvs_original)
        list(APPEND small_tv_nvs_updated "${small_tv_nvs_fixed}")
        math(EXPR small_tv_nvs_replaced "${small_tv_nvs_replaced} + 1")
    else()
        list(APPEND small_tv_nvs_updated "${small_tv_nvs_source}")
    endif()
endforeach()
if(NOT small_tv_nvs_replaced EQUAL 1)
    message(FATAL_ERROR "Expected exactly one original NVS Page translation unit")
endif()
set_property(TARGET ${small_tv_nvs_lib} PROPERTY SOURCES "${small_tv_nvs_updated}")
# Quoted private headers were previously resolved next to the vendor source.
target_include_directories(${small_tv_nvs_lib} PRIVATE
    "$ENV{IDF_PATH}/components/nvs_flash/src")
