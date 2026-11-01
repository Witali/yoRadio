cmake_minimum_required(VERSION 3.16)
set(R "$ENV{CYD_OGG_PLAYBACK_TASK_FROZEN_ROOT}")
set(EXTRA_COMPONENT_DIRS "${R}/idf/components/native_stream"
    "${R}/idf/components/native_network_power" "$ENV{CYD_OGG_PLAYBACK_TASK_VENDOR}")
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(cyd_ogg_playback_task_qemu)
