/* Private checked entry points for the source-built Xiph port.
   Public codec.h and original registry callback signatures remain unchanged.
   Each caller initializes its own failure=0; only a required allocation
   refusal sets OV_EFAULT. Malformed input leaves that status unchanged. */
#ifndef NATIVE_VORBIS_XIPH_HEADER_ERROR_H
#define NATIVE_VORBIS_XIPH_HEADER_ERROR_H
#include <ogg/ogg.h>
#include "vorbis/codec.h"
#include "codec_internal.h"
static_codebook *native_xiph_staticbook_unpack(oggpack_buffer *,int *);
vorbis_info_floor *native_xiph_floor0_unpack(vorbis_info *,oggpack_buffer *,int *);
vorbis_info_floor *native_xiph_floor1_unpack(vorbis_info *,oggpack_buffer *,int *);
vorbis_info_residue *native_xiph_residue_unpack(vorbis_info *,oggpack_buffer *,int *);
vorbis_info_mapping *native_xiph_mapping_unpack(vorbis_info *,oggpack_buffer *,int *);
#endif
