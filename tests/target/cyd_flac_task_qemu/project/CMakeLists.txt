cmake_minimum_required(VERSION 3.16)
set(R "$ENV{CYD_FLAC_TASK_FROZEN_ROOT}")
set(EXTRA_COMPONENT_DIRS "${R}/idf/components/native_stream" "${R}/idf/components/native_network_power"
 "${R}/idf/components/custom_flac"
 "${R}/idf/components/custom_codec_support" "$ENV{CYD_FLAC_TASK_VENDOR}")
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(cyd_flac_task_qemu)
