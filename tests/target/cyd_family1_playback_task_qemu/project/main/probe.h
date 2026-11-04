#ifndef FAMILY1_PLAYBACK_PROBE_H
#define FAMILY1_PLAYBACK_PROBE_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "esp_opus_dec.h"
#include "psa/crypto.h"
extern const uint8_t af_blob[] asm("_binary_fixtures_bin_start");
extern const uint8_t af_blob_end[] asm("_binary_fixtures_bin_end");
typedef struct {
    uint32_t id,channels,streams,coupled,pre_skip,logical,raw,packets,table,whole,whole_bytes,whole_pages,split,split_bytes,split_pages,needed,gain,reserved;
    uint8_t mapping[8];
} af_fixture;
typedef struct {
    unsigned kind,id,schedule,opens,calls,closes,close_errors,outputs,geometry_errors;
    uint64_t consumed,decoded,frames[8];
    void *handles[8];uint8_t stream[8],width[8];
} af_observation;
typedef struct {
    psa_hash_operation_t hash;
    uint64_t bytes;
    unsigned chunks,max_chunk;
    bool lifetime;
} af_output;
extern af_observation af_obs;
void af_begin(unsigned kind,unsigned id,unsigned schedule);
esp_audio_err_t af_open(void *,uint32_t,void **);
esp_audio_err_t af_decode(void *,esp_audio_dec_in_raw_t *,esp_audio_dec_out_frame_t *,esp_audio_dec_info_t *);
esp_audio_err_t af_close(void *);
unsigned af_live(void);
void af_hash_begin(af_output *);
void af_hash_add(af_output *,const uint8_t *,size_t);
void af_hash_finish(af_output *,char [65]);
bool af_reference(const af_fixture *,af_output *,int *);
static inline uint32_t af_le32(const uint8_t *p){return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
_Static_assert(sizeof(af_fixture)==80,"independent data-only transport ABI");
#endif
