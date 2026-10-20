#ifndef SMALL_TV_JPEG_DECODER_INTERNAL_H
#define SMALL_TV_JPEG_DECODER_INTERNAL_H
#define JPEG_INTERNALS
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "jpeglib.h"
#include "jmemsys.h"
#include "jpeg_decoder.h"
#include "color_convert.h"
#include <setjmp.h>

#define JPEG_DECODER_FILES 16u
struct jpeg_decoder {
    struct jpeg_decompress_struct codec;
    struct jpeg_error_mgr error;
    jmp_buf jump;
    jpeg_decoder_config_t config;
    jpeg_decode_request_t request;
    jpeg_decode_diagnostic_t diagnostic;
    struct jpeg_source_mgr source;
    uint8_t input[1024];
    uint16_t samples[240*4],rgb565[240];
    uint32_t position;
    size_t pool_current;
    uint64_t backing_current;
    jpeg_decode_status_t allocation_status;
    uint64_t allocation_required;
    struct {backing_store_ptr owner;uint64_t handle;uint32_t bytes;} files[JPEG_DECODER_FILES];
    jvirt_sarray_ptr (*request_samples)(j_common_ptr,int,boolean,JDIMENSION,JDIMENSION,JDIMENSION);
    jvirt_barray_ptr (*request_blocks)(j_common_ptr,int,boolean,JDIMENSION,JDIMENSION,JDIMENSION);
    void (*realize_arrays)(j_common_ptr);
    unsigned sample_arrays,backing_files;
    bool created,active;
};

void jpeg_decoder_fail(jpeg_decoder_t *decoder,jpeg_decode_status_t status,uint64_t required,uint64_t available);
void jpeg_decoder_checkpoint(jpeg_decoder_t *decoder);
void jpeg_decoder_callback_error(jpeg_decoder_t *decoder,jpeg_decode_status_t status,int error);
void jpeg_decoder_install_memory(jpeg_decoder_t *decoder);
void jpeg_decoder_release_backing(jpeg_decoder_t *decoder);
#endif
