#include "stream_probe.h"
#include "audio_completion.h"
#define CONFIG_YORADIO_FRAME_ROUTER 1
#define CONFIG_YORADIO_STREAM_CONFIRM 1
#define STREAM_CHUNK_SIZE 2048
#define pdMS_TO_TICKS(x) (x)
typedef enum {NATIVE_CODEC_AUTO,NATIVE_CODEC_MP3,NATIVE_CODEC_AAC,
              NATIVE_CODEC_FLAC,NATIVE_CODEC_OGG} native_codec_t;
typedef struct {uint32_t generation;native_codec_t codec;uint16_t data_size;
                uint8_t end_of_stream;uint8_t data[];} encoded_packet_t;
static adaptive_input_t *s_encoded;
static atomic_uint s_generation;
#ifdef STREAM_TARGET_CYD
static atomic_uint s_failed_generation;
static bool s_encoded_control_attached;
#endif
static int64_t clock_offset;
#define encoded_acquire adaptive_input_acquire
static atomic_uint consumed_data_packets;
static unsigned committed_data_packets, provisional_updates;
static atomic_bool decoder_metadata_published;
static BaseType_t encoded_commit(adaptive_input_t *input, void *packet) {
    bool data=((encoded_packet_t *)packet)->data_size != 0;
    BaseType_t result=adaptive_input_commit_size(input,packet,
        sizeof(encoded_packet_t)+((encoded_packet_t *)packet)->data_size);
    if (result==pdTRUE && data) {
        ++committed_data_packets;
#ifndef TEST_QUEUED_CONSUMER
        // Force the valid scheduling order that exposed the hardware race,
        // including a one-frame file published only at EOF.
        while (atomic_load(&consumed_data_packets)<committed_data_packets) sched_yield();
#endif
    }
    return result;
}
static int64_t esp_timer_get_time(void) {return (int64_t)xTaskGetTickCount()*1000+clock_offset;}
static void vTaskDelay(unsigned ticks) {struct timespec delay={ticks/1000,(ticks%1000)*1000000L};nanosleep(&delay,NULL);}
static const char *codec_name(native_codec_t codec) {(void)codec;return "codec";}
static void state_set_audio(unsigned generation,bool playing,const char *name) {
    assert(generation==42 && name);
#ifdef STREAM_TARGET_CYD
    assert(!playing);
#else
    assert(playing);
#endif
    assert(!atomic_load(&decoder_metadata_published));
    ++provisional_updates;
}
/* PRODUCTION_SEND */

static uint8_t capture[1024*1024];
static size_t captured;
static unsigned terminal,drains,control_packets;
static size_t drain_offsets[16],search_remaining_before_end;
static native_codec_t drain_codecs[16];
static void *consume(void *unused) {
    (void)unused;
    while (true) {
        size_t size;encoded_packet_t *p=adaptive_input_receive(s_encoded,&size,5000);assert(p);
        if((void *)p==s_start_control) ++control_packets;
        assert(size>=sizeof(*p) && p->data_size<=size-sizeof(*p));
        assert(captured+p->data_size<=sizeof(capture));
        if(p->data_size)memcpy(capture+captured,p->data,p->data_size);
        captured+=p->data_size;
        if(p->data_size) {
            atomic_store(&decoder_metadata_published,true);
            atomic_fetch_add(&consumed_data_packets,1);
        }
        bool end=audio_completion_is_terminal(p->end_of_stream);
        if(end)terminal=p->end_of_stream;
        if(p->end_of_stream==AUDIO_DRAIN_CODEC) {
            assert(drains<16);
            drain_offsets[drains]=captured;drain_codecs[drains++]=p->codec;
        }
        assert(adaptive_input_return(s_encoded,p));
        if(end)return NULL;
    }
}
static void begin(void) {
    clock_offset=0;captured=terminal=drains=control_packets=0;atomic_store(&s_generation,42);
    committed_data_packets=provisional_updates=0;
    atomic_store(&consumed_data_packets,0);atomic_store(&decoder_metadata_published,false);
    size_t capacity=sizeof(encoded_packet_t)+STREAM_CHUNK_SIZE;
    s_encoded=adaptive_input_create(4*capacity,4*capacity,capacity);assert(s_encoded);
    s_start_control_attached=false;stream_transport_reset();
#ifdef STREAM_TARGET_CYD
    atomic_store(&s_failed_generation,0);
    assert(adaptive_input_attach_control(s_encoded,s_start_control,sizeof(s_start_control)));
    s_encoded_control_attached=s_start_control_attached=true;
#endif
    atomic_store(&fail_after,0);
}
static void finish(void) {
    assert(!s_stream_start.active && !adaptive_input_stats(s_encoded).occupied);
    adaptive_input_destroy(s_encoded);assert(!atomic_load(&live_allocations));
    atomic_store(&fail_after,-1);
}
static void run_case(const uint8_t *input,size_t bytes,const uint8_t *expected,
        size_t expected_bytes,unsigned expected_end,size_t chunk,native_codec_t initial) {
    begin();pthread_t thread;assert(!pthread_create(&thread,NULL,consume,NULL));
    native_codec_t codec=initial;bool first=true;stream_probe_t probe={0};
    uint8_t end=AUDIO_END_EOF;
    for(size_t pos=0;pos<bytes;) {
        size_t n=bytes-pos;if(n>chunk)n=chunk;
        if(!send_stream_audio(42,&codec,input+pos,n,&first,&probe)) {end=AUDIO_END_BUFFER_STALLED;break;}
        pos+=n;
    }
    search_remaining_before_end=s_stream_start.search_left;
    end=finish_stream_audio(42,&codec,&first,end);
    assert(send_encoded(42,codec,NULL,0,end));assert(!pthread_join(thread,NULL));
    if(terminal!=expected_end || captured!=expected_bytes)
        fprintf(stderr,"input=%zu chunk=%zu initial=%u terminal=%u expected=%u bytes=%zu expected_bytes=%zu\n",
                bytes,chunk,initial,terminal,expected_end,captured,expected_bytes);
    assert(terminal==expected_end && captured==expected_bytes);
    assert(provisional_updates==(expected_bytes ? 1u : 0u));
    if(expected_bytes)assert(!memcmp(capture,expected,expected_bytes));
    finish();
}
int main(int argc,char **argv) {
    const size_t chunks[]={1,7,2048};
#ifdef STREAM_TARGET_CYD
    if (argc==1) {
        begin();atomic_store(&s_failed_generation,42);
        native_codec_t codec=NATIVE_CODEC_AUTO;bool first=true;stream_probe_t probe={0};
        const uint8_t data[]={0xff,0xf1,0x4c,0x80,0x01,0x9f,0xfc,1,2,3,4,5};
        assert(!send_stream_audio(42,&codec,data,sizeof(data),&first,&probe));
        assert(!adaptive_input_stats(s_encoded).occupied);finish();
    }
#endif
    if(argc==3 || argc==4 || argc==5) {
        FILE *file=fopen(argv[1],"rb");assert(file);assert(!fseek(file,0,SEEK_END));
        long size=ftell(file);assert(size>0);rewind(file);uint8_t *data=malloc(size);assert(data);
        assert(fread(data,1,size,file)==(size_t)size);fclose(file);
        size_t discard=argc==5 ? 0 : strtoul(argv[2],NULL,10);assert(discard<(size_t)size);
        uint8_t *expected=data+discard;size_t expected_size=size-discard;
        if(argc==5) {
            assert(!strcmp(argv[2],"--expected"));
            FILE *clean=fopen(argv[3],"rb");assert(clean);assert(!fseek(clean,0,SEEK_END));
            long n=ftell(clean);assert(n>0);rewind(clean);expected_size=n;
            expected=malloc(expected_size);assert(expected);
            assert(fread(expected,1,expected_size,clean)==expected_size);fclose(clean);
        }
        for(unsigned i=0;i<3;++i) {
            run_case(data,size,expected,expected_size,AUDIO_END_EOF,chunks[i],NATIVE_CODEC_AUTO);
            if(argc==5)assert(drains==strtoul(argv[4],NULL,10));
            if(argc==4) {
                assert(!strcmp(argv[3],"require-control") && control_packets);
                printf("CONTROL chunk=%zu packets=%u\n",chunks[i],control_packets);
            }
        }
        if(argc==5)free(expected);
        free(data);puts("PASS startup corpus: exact replay and clean EOF, chunks 1/7/2048");return 0;
    }
    assert(argc==1);
    uint8_t mp3[417];memset(mp3,0x55,sizeof(mp3));memcpy(mp3,"\xff\xfb\x90\0",4);
    uint8_t aac[12]={0xff,0xf1,0x4c,0x80,1,0x9f,0xfc,1,2,3,4,5};
    uint8_t mixed[441];memcpy(mixed,mp3,417);memcpy(mixed+417,aac,12);memcpy(mixed+429,aac,12);
    uint8_t tail[417+128]={0};memcpy(tail,mp3,417);memcpy(tail+417,"TAG",3);
    uint8_t tagged[441+10];memcpy(tagged,mixed,417);memcpy(tagged+417,"ID3\4\0\0\0\0\0\0",10);memcpy(tagged+427,mixed+417,24);
    uint8_t duplicate[417+256];memcpy(duplicate,tail,sizeof(tail));memcpy(duplicate+sizeof(tail),tail+417,128);
    const uint8_t oversized[]={'I','D','3',4,0,0,0,64,0,0};
    const uint8_t free_format[]={0xff,0xfb,0,0,1,2,3};
    const uint8_t flac[]={'f','L','a','C',0,0,0,34,1,2,3};
    const uint8_t ogg[]={'O','g','g','S',0,1,2,3};
    for(unsigned i=0;i<3;++i) {
        run_case(NULL,0,NULL,0,AUDIO_END_FORMAT_UNKNOWN,chunks[i],NATIVE_CODEC_AUTO);
        run_case(duplicate,sizeof(duplicate),NULL,0,AUDIO_END_FORMAT_UNKNOWN,chunks[i],NATIVE_CODEC_AUTO);
        run_case(oversized,sizeof(oversized),NULL,0,AUDIO_END_FORMAT_UNKNOWN,chunks[i],NATIVE_CODEC_AUTO);
        run_case(free_format,sizeof(free_format),free_format,sizeof(free_format),AUDIO_END_EOF,chunks[i],NATIVE_CODEC_AUTO);
        run_case(flac,sizeof(flac),flac,sizeof(flac),AUDIO_END_EOF,chunks[i],NATIVE_CODEC_AUTO);
        run_case(ogg,sizeof(ogg),ogg,sizeof(ogg),AUDIO_END_EOF,chunks[i],NATIVE_CODEC_AUTO);
        run_case(mixed,sizeof(mixed),mixed,sizeof(mixed),AUDIO_END_EOF,chunks[i],NATIVE_CODEC_AUTO);
        assert(drains==1);
        run_case(mixed,sizeof(mixed),mixed,sizeof(mixed),AUDIO_END_EOF,chunks[i],NATIVE_CODEC_AAC); // Wrong MIME hint corrected.
        run_case(mp3,sizeof(mp3),mp3,sizeof(mp3),AUDIO_END_EOF,chunks[i],NATIVE_CODEC_AUTO);
        run_case(aac,sizeof(aac),aac,sizeof(aac),AUDIO_END_EOF,chunks[i],NATIVE_CODEC_AUTO);
        run_case(mp3,300,NULL,0,AUDIO_END_FRAME_TRUNCATED,chunks[i],NATIVE_CODEC_AUTO);
        run_case(tail,sizeof(tail),mp3,sizeof(mp3),AUDIO_END_EOF,chunks[i],NATIVE_CODEC_AUTO);
        run_case(tagged,sizeof(tagged),mixed,sizeof(mixed),AUDIO_END_EOF,chunks[i],NATIVE_CODEC_AUTO);
        for(unsigned n=1;n<128;++n)
            run_case(tail,417+n,NULL,0,AUDIO_END_FRAME_TRUNCATED,chunks[i],NATIVE_CODEC_AUTO);
    }
    uint8_t large_tag[10010+441];memset(large_tag,0xff,sizeof(large_tag));
    memcpy(large_tag,"ID3\4\0\0\0\0\x4e\x10",10); // Synchsafe 10000 bytes.
    memcpy(large_tag+10010,mixed,441);
    run_case(large_tag,sizeof(large_tag),mixed,441,AUDIO_END_EOF,7,NATIVE_CODEC_AUTO);
    uint8_t maximum[8191+12];memset(maximum,0x55,sizeof(maximum));memcpy(maximum,aac,7);
    maximum[3]|=3;maximum[4]=255;maximum[5]|=0xe0;memcpy(maximum+8191,aac,12);
    run_case(maximum,sizeof(maximum),maximum,sizeof(maximum),AUDIO_END_EOF,2048,NATIVE_CODEC_AUTO);
    // A false AAC length after two real MP3 frames must not change decoder
    // family before the following boundary is confirmed. Recover inside that
    // false candidate; an embedded container signature is not a family switch.
    uint8_t recovered[2*417+2*12],damaged[sizeof(recovered)+32];
    memcpy(recovered,mp3,417);memcpy(recovered+417,mp3,417);
    memcpy(recovered+834,aac,12);memcpy(recovered+846,aac,12);
    memcpy(damaged,recovered,834);memset(damaged+834,0,32);
    memcpy(damaged+834,maximum,7);memcpy(damaged+846,"fLaC",4);
    memcpy(damaged+866,recovered+834,24);
    for(unsigned i=0;i<3;++i) {
        run_case(damaged,sizeof(damaged),recovered,sizeof(recovered),AUDIO_END_EOF,chunks[i],NATIVE_CODEC_AUTO);
        assert(drains==1 && drain_offsets[0]==834 && drain_codecs[0]==NATIVE_CODEC_MP3);
    }
    // Confirm every changed family, not just the first transition. The fake
    // header and its 25-byte body must never reach either decoder.
    uint8_t twice[834+32+24+32+834],twice_expected[834+24+834];
    memcpy(twice,damaged,866); // Two MP3 frames plus the first false candidate.
    memcpy(twice+834,aac,7); // Resolve both false 12-byte candidates before EOF.
    memcpy(twice+866,recovered+834,24);
    memset(twice+890,0,32);memcpy(twice+890,aac,7);
    memcpy(twice+922,recovered,834);
    memcpy(twice_expected,recovered,sizeof(recovered));memcpy(twice_expected+858,recovered,834);
    run_case(twice,sizeof(twice),twice_expected,sizeof(twice_expected),AUDIO_END_EOF,2048,NATIVE_CODEC_AUTO);
    assert(drains==2 && drain_offsets[0]==834 && drain_offsets[1]==858);
    assert(drain_codecs[0]==NATIVE_CODEC_MP3 && drain_codecs[1]==NATIVE_CODEC_AAC);
    assert(search_remaining_before_end==STREAM_PROBE_SEARCH_BYTES-64);
    // Exhaustion after confirmed frames preserves that prefix, even when all
    // bytes arrive in one call and its coalesced output has not been committed.
    uint8_t junk[834+32+STREAM_PROBE_SEARCH_BYTES+24];
    memcpy(junk,recovered,834);memset(junk+834,0,sizeof(junk)-834);
    memcpy(junk+834,aac,7);memcpy(junk+sizeof(junk)-24,recovered+834,24);
    run_case(junk,sizeof(junk),recovered,834,AUDIO_END_BUFFER_STALLED,sizeof(junk),NATIVE_CODEC_AUTO);
    assert(!drains);
    // Coalesce tiny frames within a network read: one lease per AAC frame
    // would silently reduce the useful compressed-input queue capacity.
    uint8_t tiny[12*500];for(unsigned n=0;n<500;++n)memcpy(tiny+12*n,aac,12);
    run_case(tiny,sizeof(tiny),tiny,sizeof(tiny),AUDIO_END_EOF,2048,NATIVE_CODEC_AUTO);
    assert(committed_data_packets<=6);
    // Cancellation, I/O failure and the independent confirmation deadline also
    // apply after playback starts (station watchdog may be disabled).
    for(unsigned action=0;action<4;++action) {
        begin();pthread_t thread;assert(!pthread_create(&thread,NULL,consume,NULL));
        native_codec_t codec=NATIVE_CODEC_AUTO;bool first=true;stream_probe_t probe={0};
        assert(send_stream_audio(42,&codec,damaged,866,&first,&probe));
        assert(!first && s_stream_start.active && s_stream_start.published);
        if(action==0) {atomic_store(&s_generation,43);stream_transport_reset();}
        if(action==1) assert(finish_stream_audio(42,&codec,&first,AUDIO_END_READ_FAILED)==AUDIO_END_READ_FAILED);
        if(action==2) {
            clock_offset=(int64_t)STREAM_PROBE_TIMEOUT_MS*1000;
            assert(stream_confirmation_expired());
            assert(!send_stream_audio(42,&codec,damaged+866,1,&first,&probe));
        }
        if(action==3) {atomic_store(&s_generation,43);assert(!send_stream_audio(42,&codec,damaged+866,1,&first,&probe));}
#ifdef STREAM_TARGET_CYD
        if(action==0 || action==3) {
            // CYD rejects stale terminal sends even when acquisition would
            // succeed immediately. End this capture worker with the new ID.
            assert(!send_encoded(42,codec,NULL,0,AUDIO_END_READ_FAILED));
            assert(send_encoded(43,codec,NULL,0,AUDIO_END_READ_FAILED));
        } else
#endif
        assert(send_encoded(42,codec,NULL,0,AUDIO_END_READ_FAILED));
        assert(!pthread_join(thread,NULL));
        assert(captured==834 && !memcmp(capture,recovered,834) && !drains);
        finish();
    }
    // Live lifetime paths before any candidate was published.
    for(unsigned action=0;action<4;++action) {
        begin();native_codec_t codec=NATIVE_CODEC_AUTO;bool first=true;stream_probe_t probe={0};
        assert(send_stream_audio(42,&codec,mp3,200,&first,&probe));
        assert(first && s_stream_start.active && adaptive_input_stats(s_encoded).occupied);
        if(action==0) {atomic_store(&s_generation,43);stream_transport_reset();}
        if(action==1) assert(finish_stream_audio(42,&codec,&first,AUDIO_END_READ_FAILED)==AUDIO_END_READ_FAILED);
        if(action==2) {
            clock_offset=(int64_t)STREAM_PROBE_TIMEOUT_MS*1000;
            assert(!send_stream_audio(42,&codec,mp3+200,1,&first,&probe));
        }
        if(action==3) {atomic_store(&s_generation,43);assert(!send_stream_audio(42,&codec,mp3+200,1,&first,&probe));}
        finish();
    }
    puts("PASS startup: continuous confirmation, two midstream false headers, exact ordered drain offsets, shared search budget, retained valid prefix on exhaustion, tiny-frame coalescing, mid-play Stop/reset/read-failure/deadline; mono-frame EOF, wrong MIME, MP3/AAC transition, ID3 streaming and all 127 truncated tails, duplicate/oversized metadata, FLAC/Ogg/free-format passthrough, empty input, max ADTS; ASan/UBSan");
}
