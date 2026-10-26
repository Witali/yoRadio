/* Private checked packet floor callbacks. NULL with failure==0 remains the
   upstream unused-floor/EOP result. Required allocation failure is OV_EFAULT.
   Public headers and the original registry callback signatures are unchanged. */
#ifndef NATIVE_VORBIS_XIPH_PACKET_ERROR_H
#define NATIVE_VORBIS_XIPH_PACKET_ERROR_H
#include <ogg/ogg.h>
#include "vorbis/codec.h"
#include "codec_internal.h"
void *native_xiph_floor0_inverse1(vorbis_block *,vorbis_look_floor *,int *);
void *native_xiph_floor1_inverse1(vorbis_block *,vorbis_look_floor *,int *);
#endif
