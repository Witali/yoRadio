/* Public libopus declarations only. No installed development headers required.
 * Signatures: https://opus-codec.org/docs/opus_api-1.5/group__opus__multistream.html
 * ABI is pinned to the measured installed libopus. Structures stay opaque.
 */
#ifndef TEST_OPUS_FAMILY1_PUBLIC_H
#define TEST_OPUS_FAMILY1_PUBLIC_H
#include <stdint.h>
typedef struct OpusMSEncoder OpusMSEncoder;
typedef struct OpusMSDecoder OpusMSDecoder;
extern OpusMSEncoder *opus_multistream_surround_encoder_create(int32_t,int,int,int *,int *,unsigned char *,int,int *);
extern int opus_multistream_encoder_ctl(OpusMSEncoder *,int,...);
extern int opus_multistream_encode_float(OpusMSEncoder *,const float *,int,unsigned char *,int32_t);
extern void opus_multistream_encoder_destroy(OpusMSEncoder *);
extern OpusMSDecoder *opus_multistream_decoder_create(int32_t,int,int,int,const unsigned char *,int *);
extern int opus_multistream_decode_float(OpusMSDecoder *,const unsigned char *,int32_t,float *,int,int);
extern void opus_multistream_decoder_destroy(OpusMSDecoder *);
extern const char *opus_get_version_string(void);
enum { PUBLIC_OPUS_APPLICATION_AUDIO=2049, PUBLIC_OPUS_SET_BITRATE_REQUEST=4002,
       PUBLIC_OPUS_GET_LOOKAHEAD_REQUEST=4027 };
#endif
