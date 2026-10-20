cmake_minimum_required(VERSION 3.16)
set(EXTRA_COMPONENT_DIRS "$ENV{YORADIO_AUDIO_CODEC_COMPONENT}")
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(cyd_vorbis_port_probe)
