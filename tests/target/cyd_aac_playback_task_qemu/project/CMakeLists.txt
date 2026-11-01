cmake_minimum_required(VERSION 3.16)
set(R "$ENV{CYD_AAC_PLAYBACK_TASK_FROZEN_ROOT}")
set(EXTRA_COMPONENT_DIRS "${R}/idf/components/native_stream"
    "${R}/idf/components/native_network_power" "${R}/idf/components/native_audio_settings" "${R}/idf/components/native_audio_normalizer" "$ENV{CYD_AAC_PLAYBACK_TASK_VENDOR}")
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(cyd_aac_playback_task_qemu)
