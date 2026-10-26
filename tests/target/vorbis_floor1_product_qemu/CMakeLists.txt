cmake_minimum_required(VERSION 3.16)
set(EXTRA_COMPONENT_DIRS
    "$ENV{F1_COMPONENTS}/native_vorbis_numeric"
    "$ENV{F1_COMPONENTS}/native_vorbis_packet_frame"
    "$ENV{F1_COMPONENTS}/native_vorbis_floor1_product")
set(COMPONENTS main native_vorbis_floor1_product)
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(vorbis_floor1_product_qemu)
