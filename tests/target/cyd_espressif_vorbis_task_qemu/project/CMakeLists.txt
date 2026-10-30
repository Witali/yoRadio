cmake_minimum_required(VERSION 3.16)
set(R "$ENV{CYD_VORBIS_TASK_FROZEN_ROOT}")
set(EXTRA_COMPONENT_DIRS "${R}/idf/components/native_stream"
    "${R}/idf/components/native_network_power" "$ENV{CYD_VORBIS_TASK_VENDOR}")
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(cyd_espressif_vorbis_task_qemu)
