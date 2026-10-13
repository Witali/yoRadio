#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdatomic.h>
#include <stdio.h>
#include "audio_completion.h"

#define ESP_LOGE(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
enum { ESP_AUDIO_ERR_OK, ESP_AUDIO_ERR_BUFF_NOT_ENOUGH, ESP_AUDIO_ERR_FAIL };
enum { NATIVE_CODEC_MP3, NATIVE_CODEC_AAC };
typedef int esp_audio_err_t;
typedef struct { uint8_t *buffer; size_t len, consumed; bool eos; } esp_audio_simple_dec_raw_t;
typedef struct { uint8_t *buffer; size_t len, needed_size, decoded_size; } esp_audio_simple_dec_out_t;
typedef struct { unsigned sample_rate, channel, bits_per_sample, bitrate; } esp_audio_simple_dec_info_t;
typedef struct { uint64_t decode_us; unsigned calls, max_call_us, input_bytes; } decode_stats_t;
typedef struct { unsigned generation, end_of_stream; uint8_t *data; size_t data_size; } encoded_packet_t;
typedef struct { unsigned call, produced; } fake_decoder_t;
static atomic_uint s_generation;
static unsigned closes, returned, end_markers, pcm_frames, error_status, scenario;
static uint8_t captured[8];
static void *s_encoded;
static uint64_t esp_timer_get_time(void) { static uint64_t now;return ++now; }
static void vTaskDelay(unsigned n) { (void)n; }
static void state_set_audio(unsigned generation,bool playing,const char *status) {
    (void)generation;(void)status;assert(!playing);++error_status;
}
static void state_set_decoder_bitrate(unsigned generation,unsigned bitrate) {(void)generation;(void)bitrate;}
static bool decoder_pcm_resize(uint8_t **output,size_t *size,size_t needed) {
    *output=realloc(*output,needed);assert(*output);*size=needed;return true;
}
static esp_audio_err_t esp_audio_simple_dec_process(fake_decoder_t *d,
        esp_audio_simple_dec_raw_t *raw,esp_audio_simple_dec_out_t *out) {
    assert(d);++d->call;
    if(scenario==2) {atomic_fetch_add(&s_generation,1);return ESP_AUDIO_ERR_OK;}
    if(scenario==3)return ESP_AUDIO_ERR_FAIL;
    if(out->len<4) {out->needed_size=4;return ESP_AUDIO_ERR_BUFF_NOT_ENOUGH;}
    raw->consumed=raw->len;
    if(d->produced<(raw->eos?2U:1U)) {
        memset(out->buffer,0x30+d->produced,4);out->decoded_size=4;++d->produced;
    }
    return ESP_AUDIO_ERR_OK;
}
#define native_aac_decoder_process esp_audio_simple_dec_process
static esp_audio_err_t esp_audio_simple_dec_get_info(fake_decoder_t *d,esp_audio_simple_dec_info_t *info) {
    assert(d);*info=(esp_audio_simple_dec_info_t){48000,2,16,128000};return ESP_AUDIO_ERR_OK;
}
#define native_aac_decoder_get_info esp_audio_simple_dec_get_info
static const char *native_aac_decoder_label(fake_decoder_t *d,const esp_audio_simple_dec_info_t *info,bool *pcm) {
    (void)d;(void)info;*pcm=true;return "AAC";
}
static unsigned native_aac_decoder_source_channels(fake_decoder_t *d) {(void)d;return 2;}
static const char *codec_name(int codec) {(void)codec;return "codec";}
static bool update_stream_info(unsigned generation,const char *label,
        const esp_audio_simple_dec_info_t *latest,esp_audio_simple_dec_info_t *current,
        bool *ready,unsigned source_rate,unsigned source_channels,bool core,bool pcm) {
    (void)generation;(void)label;(void)ready;(void)source_rate;(void)source_channels;(void)core;(void)pcm;
    *current=*latest;return true;
}
static void log_runtime_memory(const char *s) {(void)s;}
static void decode_stats_add_audio(decode_stats_t *s,const esp_audio_simple_dec_info_t *info,size_t bytes) {
    (void)s;(void)info;(void)bytes;
}
static void decode_stats_report(decode_stats_t *s,uint64_t now) {(void)s;(void)now;}
static bool send_pcm(decode_stats_t *s,unsigned generation,const esp_audio_simple_dec_info_t *info,
        const uint8_t *pcm,size_t bytes) {
    (void)s;assert(generation==atomic_load(&s_generation));assert(info->sample_rate==48000);
    assert(!closes && bytes==4 && pcm_frames<2);memcpy(captured+4*pcm_frames,pcm,4);++pcm_frames;return true;
}
static void decoder_resources_release(fake_decoder_t **sdk,fake_decoder_t **aac,uint8_t **out,size_t *size) {
    assert(!(*sdk && *aac));free(*sdk);free(*aac);*sdk=*aac=NULL;
    free(*out);*out=NULL;*size=0;++closes;
}
static void encoded_return(void *queue,encoded_packet_t *packet) {(void)queue;(void)packet;++returned;}
static bool send_pcm_end(unsigned generation,unsigned reason) {
    if(generation!=atomic_load(&s_generation))return false;
    assert(audio_completion_is_terminal(reason));
    assert(closes==1 && pcm_frames==2);++end_markers;return true;
}
static void return_decoded_packet(encoded_packet_t *packet,
                                  uint32_t failed_generation) {
    if (audio_completion_is_terminal(packet->end_of_stream) &&
        packet->generation != failed_generation) {
        send_pcm_end(packet->generation, packet->end_of_stream);
    }
    encoded_return(s_encoded, packet);
}


static void exercise(bool native,unsigned reason,unsigned mode) {
    scenario=mode;closes=returned=end_markers=pcm_frames=error_status=0;
    memset(captured,0,sizeof(captured));atomic_store(&s_generation,7);
    fake_decoder_t *allocated=calloc(1,sizeof(*allocated));assert(allocated);
    fake_decoder_t *decoder=native?NULL:allocated,*aac_decoder=native?allocated:NULL;
    uint8_t *output=malloc(mode==1?1:4);size_t output_size=mode==1?1:4;
    uint8_t data=0xff;
    encoded_packet_t input={7,reason,&data,reason?0:1},*packet=&input;
    unsigned generation=7,failed_generation=0;
    int codec=native?NATIVE_CODEC_AAC:NATIVE_CODEC_MP3;
    decode_stats_t stats={0};esp_audio_simple_dec_info_t stream_info={0};
    bool stream_info_ready=false,first_frame_memory_logged=false;
    do {
        if (!decoder && !aac_decoder) {
            encoded_return(s_encoded, packet);
            continue;
        }
        esp_audio_simple_dec_raw_t raw = {
            .buffer = packet->data,
            .len = packet->data_size,
            .eos = packet->end_of_stream,
        };
        bool retry_pcm = false;
        while (raw.len || raw.eos || retry_pcm) {
            retry_pcm = false;
            esp_audio_simple_dec_out_t frame = {
                .buffer = output,
                .len = output_size,
            };
            raw.consumed = 0;
            int64_t decode_started_us = esp_timer_get_time();
            esp_audio_err_t result = aac_decoder
                ? native_aac_decoder_process(aac_decoder, &raw, &frame)
                : esp_audio_simple_dec_process(decoder, &raw, &frame);
            uint32_t decode_call_us =
                (uint32_t)(esp_timer_get_time() - decode_started_us);
            stats.decode_us += decode_call_us;
            ++stats.calls;
            if (decode_call_us > stats.max_call_us) {
                stats.max_call_us = decode_call_us;
            }
            // PCM backpressure normally blocks this task every few frames.
            // Keep a bounded fallback yield for malformed streams that keep
            // consuming input without producing PCM.
            if ((stats.calls & 31U) == 0U) vTaskDelay(1);
            if (generation != atomic_load(&s_generation)) break;
            if (result == ESP_AUDIO_ERR_BUFF_NOT_ENOUGH) {
                if (aac_decoder) {
                    stats.input_bytes += raw.consumed;
                    raw.buffer += raw.consumed;
                    raw.len -= raw.consumed;
                }
                if (frame.needed_size <= output_size ||
                    !decoder_pcm_resize(&output, &output_size,
                                        frame.needed_size)) {
                    state_set_audio(generation, false, "PCM allocation failed");
                    failed_generation = generation;
                    break;
                }
                retry_pcm = true;
                continue;
            }
            if (result != ESP_AUDIO_ERR_OK) {
                ESP_LOGW(TAG, "%s decode error: %d", codec_name(codec),
                         result);
                state_set_audio(generation, false, "decode failed");
                failed_generation = generation;
                break;
            }
            if (raw.consumed > raw.len) {
                ESP_LOGE(TAG, "%s decoder consumed invalid input size %lu/%lu",
                         codec_name(codec), (unsigned long)raw.consumed,
                         (unsigned long)raw.len);
                state_set_audio(generation, false, "decoder input error");
                failed_generation = generation;
                break;
            }
            stats.input_bytes += (uint32_t)raw.consumed;
            raw.buffer += raw.consumed;
            raw.len -= raw.consumed;
            if (frame.decoded_size) {
                esp_audio_simple_dec_info_t latest_info = {0};
                esp_audio_err_t info_result = aac_decoder
                    ? native_aac_decoder_get_info(aac_decoder, &latest_info)
                    : esp_audio_simple_dec_get_info(decoder, &latest_info);
                if (info_result == ESP_AUDIO_ERR_OK) {
                    bool format_is_pcm = codec == NATIVE_CODEC_AAC;
                    const char *label = aac_decoder
                        ? native_aac_decoder_label(aac_decoder, &latest_info,
                                                   &format_is_pcm)
                        : codec_name(codec);
                    stream_info_ready = update_stream_info(
                        generation, label, &latest_info,
                        &stream_info, &stream_info_ready, 0,
                        aac_decoder && !format_is_pcm ? native_aac_decoder_source_channels(aac_decoder) : 0, false,
                        format_is_pcm);
                    state_set_decoder_bitrate(generation, latest_info.bitrate);
                } else {
                    // Never send a frame with another frame's stale layout.
                    stream_info_ready = false;
                }
                if (stream_info_ready) {
#ifdef YORADIO_CODEC_BENCHMARK
                    if (!first_frame_memory_reported) {
                        benchmark_log_memory("first-frame", codec,
                                             decoder_heap_before, 0);
                        first_frame_memory_reported = true;
                    }
#endif
                    if (!first_frame_memory_logged) {
                        log_runtime_memory("after first decoded frame");
                        first_frame_memory_logged = true;
                    }
                    decode_stats_add_audio(&stats, &stream_info,
                                           frame.decoded_size);
                    if (!send_pcm(&stats, generation, &stream_info, output,
                                  frame.decoded_size)) {
                        ESP_LOGW(TAG, "PCM buffer stalled");
                        break;
                    }
                }
            }
            decode_stats_report(&stats, esp_timer_get_time());
            if (!raw.consumed && !frame.decoded_size && !raw.eos) {
                ESP_LOGE(TAG, "%s decoder made no input progress",
                         codec_name(codec));
                state_set_audio(generation, false, "decoder stalled");
                failed_generation = generation;
                break;
            }
            // EOF can drain several cached Ogg packets. Keep the decoder and
            // its PCM workspace alive until a successful call yields no PCM.
            if (raw.eos ? (!raw.len && !frame.decoded_size) : raw.len == 0) break;
        }
        if (packet->end_of_stream || failed_generation == generation) {
            decoder_resources_release(&decoder, &aac_decoder, &output, &output_size);
        }
        return_decoded_packet(packet, failed_generation);
    } while(false);
    assert(returned==1);
    if(mode==2 || mode==3) {
        assert(!pcm_frames && !end_markers);
        assert(error_status==(mode==3));
    } else {
        unsigned expected=reason?2:1;
        assert(pcm_frames==expected && !error_status);
        assert(end_markers==(unsigned)audio_completion_is_terminal(reason));
        for(unsigned i=0;i<expected*4;++i)assert(captured[i]==0x30+i/4);
    }
    assert(closes==((reason || mode==3)?1U:0U));
    if(decoder || aac_decoder)decoder_resources_release(&decoder,&aac_decoder,&output,&output_size);
    assert(!decoder && !aac_decoder && !output && !output_size);
}
int main(void) {
    for(unsigned native=0;native<2;++native)
        for(unsigned mode=0;mode<4;++mode) {
            exercise(native,AUDIO_DRAIN_CODEC,mode);
            exercise(native,AUDIO_END_EOF,mode);
            exercise(native,AUDIO_CONTINUE,mode);
        }
    puts("PASS 24 actual decoder-loop cases: cached PCM drain, resize, EOF, cancellation, errors; DSP mocked");
}
