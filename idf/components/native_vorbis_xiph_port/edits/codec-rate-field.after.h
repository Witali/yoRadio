/********************************************************************
 *                                                                  *
 * THIS FILE IS PART OF THE OggVorbis SOFTWARE CODEC SOURCE CODE.   *
 * USE, DISTRIBUTION AND REPRODUCTION OF THIS LIBRARY SOURCE IS     *
 * GOVERNED BY A BSD-STYLE SOURCE LICENSE INCLUDED WITH THIS SOURCE *
 * IN 'COPYING'. PLEASE READ THESE TERMS BEFORE DISTRIBUTING.       *
 *                                                                  *
 * THE OggVorbis SOURCE CODE IS (C) COPYRIGHT 1994-2001             *
 * by the Xiph.Org Foundation https://xiph.org/                     *

 ********************************************************************

 function: libvorbis codec headers

 ********************************************************************/

#ifndef _vorbis_codec_h_
#define _vorbis_codec_h_

#include <limits.h>
#define NATIVE_VORBIS_XIPH_RATE_API 1

/* Resource-port extension: preserve the positive unsigned32 bitstream rate.
   Layout stays that of long; consumers must use these matching headers. */
#if ULONG_MAX == 0xffffffffUL
typedef unsigned long native_xiph_sample_rate_t;
#else
typedef long native_xiph_sample_rate_t;
#endif

#ifdef __cplusplus
extern "C"
{
#endif /* __cplusplus */

#include <ogg/ogg.h>

typedef struct vorbis_info{
  int version;
  int channels;
  native_xiph_sample_rate_t rate;
