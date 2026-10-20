cmake_minimum_required(VERSION 3.16)
set(EXTRA_COMPONENT_DIRS
  "$ENV{CYD_FLAC_FROZEN_ROOT}/idf/components/custom_codec_support"
  "$ENV{CYD_FLAC_FROZEN_ROOT}/idf/components/custom_flac")
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(cyd_custom_flac_qemu)
