cmake_minimum_required(VERSION 3.16)
project(small_tv_jpeg_probe C)

# The parent library remains a separate, pinned build; no production dependency.
if(NOT JPEG_SOURCE OR NOT JPEG_BUILD OR NOT JPEG_LIBRARY)
  message(FATAL_ERROR "Specify JPEG_SOURCE, JPEG_BUILD and JPEG_LIBRARY")
endif()
add_executable(jpeg_probe probe.c probe_memory.c)
target_include_directories(jpeg_probe PRIVATE "${JPEG_SOURCE}/src" "${JPEG_BUILD}")
target_compile_definitions(jpeg_probe PRIVATE JPEG_STATIC _CRT_SECURE_NO_WARNINGS)
target_compile_features(jpeg_probe PRIVATE c_std_11)
if(MSVC)
  target_compile_options(jpeg_probe PRIVATE /W4)
  # Match upstream WITH_CRT_DLL=OFF: FILE pointers cross the library boundary.
  set_property(TARGET jpeg_probe PROPERTY MSVC_RUNTIME_LIBRARY
    "MultiThreaded$<$<CONFIG:Debug>:Debug>")
else()
  target_compile_options(jpeg_probe PRIVATE -Wall -Wextra)
endif()
# The probe memory object supplies jmemsys; the archive's jmemnobs stays unused.
target_link_libraries(jpeg_probe PRIVATE "${JPEG_LIBRARY}")
