/* Opaque public libopus ABI only; no implementation layouts or private CTLs.
 * https://opus-codec.org/docs/opus_api-1.5/group__opus__encoder.html
 * https://opus-codec.org/docs/opus_api-1.5/group__opus__decoder.html
 * https://opus-codec.org/docs/opus_api-1.5/group__opus__repacketizer.html
 */
#ifndef TEST_OPUS_PACKET_MODES_PUBLIC_H
#define TEST_OPUS_PACKET_MODES_PUBLIC_H
#include <stdint.h>
typedef struct OpusEncoder OpusEncoder;
typedef struct OpusDecoder OpusDecoder;
typedef struct OpusRepacketizer OpusRepacketizer;
extern OpusEncoder *opus_encoder_create(int32_t,int,int,int *);
extern int opus_encoder_ctl(OpusEncoder *,int,...);
extern int opus_encode_float(OpusEncoder *,const float *,int,unsigned char *,int32_t);
extern void opus_encoder_destroy(OpusEncoder *);
extern OpusDecoder *opus_decoder_create(int32_t,int,int *);
extern int opus_decode(OpusDecoder *,const unsigned char *,int32_t,int16_t *,int,int);
extern void opus_decoder_destroy(OpusDecoder *);
extern int opus_packet_parse(const unsigned char *,int32_t,unsigned char *,const unsigned char **,int16_t *,int *);
extern int opus_packet_get_nb_samples(const unsigned char *,int32_t,int32_t);
extern int opus_packet_get_nb_channels(const unsigned char *);
extern int opus_packet_get_samples_per_frame(const unsigned char *,int32_t);
extern int opus_packet_get_nb_frames(const unsigned char *,int32_t);
extern OpusRepacketizer *opus_repacketizer_create(void);
extern OpusRepacketizer *opus_repacketizer_init(OpusRepacketizer *);
extern int opus_repacketizer_cat(OpusRepacketizer *,const unsigned char *,int32_t);
extern int32_t opus_repacketizer_out(OpusRepacketizer *,unsigned char *,int32_t);
extern void opus_repacketizer_destroy(OpusRepacketizer *);
extern int opus_packet_pad(unsigned char *,int32_t,int32_t);
extern int32_t opus_packet_unpad(unsigned char *,int32_t);
extern const char *opus_get_version_string(void);
enum { PM_APPLICATION_VOIP=2048, PM_APPLICATION_RESTRICTED_LOWDELAY=2051,
       PM_SET_BITRATE=4002, PM_SET_VBR=4006, PM_SET_BANDWIDTH=4008,
       PM_SET_SIGNAL=4024, PM_GET_LOOKAHEAD=4027,
       PM_BANDWIDTH_WIDEBAND=1103, PM_BANDWIDTH_SUPERWIDEBAND=1104,
       PM_BANDWIDTH_FULLBAND=1105, PM_SIGNAL_VOICE=3001 };
#endif
