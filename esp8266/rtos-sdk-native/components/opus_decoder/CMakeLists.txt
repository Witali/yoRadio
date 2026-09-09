if(CONFIG_YORADIO_OGG_OPUS)
  option(YORADIO_OPUS_WORD_ASM "A/B: private Opus LX106 word accesses without volatile-C MEMW" OFF)
  file(GLOB OPUS_SOURCES upstream/src/*.c upstream/celt/*.c
       upstream/silk/*.c upstream/silk/fixed/*.c)
  idf_component_register(SRCS ${OPUS_SOURCES}
      opus_memory.c ogg_opus_demux.c native_opus.c
      INCLUDE_DIRS . upstream/include
      PRIV_INCLUDE_DIRS upstream/celt upstream/silk upstream/silk/fixed upstream/src)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE YORADIO_OPUS_BOUNDED=1)
  if(YORADIO_OPUS_WORD_ASM)
    target_compile_definitions(${COMPONENT_LIB} PRIVATE YORADIO_OPUS_WORD_ASM=1)
  endif()
  target_compile_options(${COMPONENT_LIB} PRIVATE -O3 -fwrapv -fstack-usage)
else()
  idf_component_register()
endif()
