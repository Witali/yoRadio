// Actual staged/direct output functions are compiled before this harness.
static unsigned outstanding;
#ifndef BASELINE
typedef struct { native_audio_pcm_lease_t lease; int16_t pcm[]; } boundary_item_t;
static void release_boundary(native_audio_pcm_lease_t *lease) {
    assert(!binary_lock.held && !mutex_lock.held && outstanding);
    --outstanding; free(lease);
}
#endif

static void submit_constant(size_t frames, unsigned channels, int16_t value) {
#ifdef BASELINE
    int16_t *pcm=malloc(frames*channels*2);assert(pcm);
#else
    boundary_item_t *item=calloc(1,sizeof(*item)+frames*channels*2);assert(item);
    ++outstanding;int16_t *pcm=item->pcm;
#endif
    for(size_t i=0;i<frames;++i) {
        pcm[i*channels]=value;
        if(channels==2) pcm[i*channels+1]=-value;
    }
#ifdef BASELINE
    assert(native_audio_output_write_pcm((uint8_t *)pcm,frames*channels*2,16,channels)==ESP_OK);
    free(pcm);
#else
    assert(native_audio_output_submit_pcm(&item->lease,(uint8_t *)pcm,
        frames*channels*2,16,channels,release_boundary)==ESP_OK);
#endif
}

static size_t expected_frames(size_t frames, unsigned rate) {
#ifdef CONFIG_YORADIO_PDM_INTEGER_RATE_COMPENSATION
    return 1+(frames-1)*625000/(13*rate);
#else
    return 1+(frames-1)*48000/rate;
#endif
}

static void verify_constant(size_t begin,size_t frames,unsigned channels,int16_t value) {
    size_t padded=(frames+511)/512*512;
    assert(captured-begin==padded*4);
    assert(fflush(capture)==0 && fseek(capture,(long)begin,SEEK_SET)==0);
    for(size_t i=0;i<padded;++i) {
        int16_t pair[2];assert(fread(pair,sizeof(pair),1,capture)==1);
        int16_t left=i<frames?value:0;
        int16_t right=i<frames?(channels==2?-value:value):0;
        assert(pair[0]==left && pair[1]==right);
    }
    assert(fseek(capture,0,SEEK_END)==0);
}

static void fresh_stream(unsigned rate) {
    native_audio_output_discard_pcm();assert(!outstanding);
    assert(native_audio_output_configure(rate)==ESP_OK);
    channel.dma.curr_ptr=NULL;channel.dma.rw_pos=0;queue.spaces=4;
}

int main(int argc,char **argv) {
    assert(argc==2 && native_audio_output_init()==ESP_OK);
    capture=fopen(argv[1],"w+b");assert(capture);
    const unsigned rates[]={8000,11025,12000,16000,22050,24000,32000,44100,48000};
    const size_t sizes[]={1,127,511,512,513};
    unsigned cases=0;
    for(unsigned r=0;r<9;++r) for(unsigned ch=1;ch<=2;++ch) for(unsigned n=0;n<5;++n) {
        fresh_stream(rates[r]);size_t begin=captured;
        submit_constant(sizes[n],ch,1234);
        assert(native_audio_output_flush_pcm()==ESP_OK && !outstanding);
        verify_constant(begin,expected_frames(sizes[n],rates[r]),ch,1234);
        size_t once=captured;
        assert(native_audio_output_flush_pcm()==ESP_OK && captured==once);
        ++cases;
    }
    // Stop/new generation must discard software samples, including when
    // the new stream has the same rate and configure does not reset state.
    fresh_stream(48000);size_t begin=captured;
    submit_constant(128,2,1234);native_audio_output_discard_pcm();assert(!outstanding);
    assert(native_audio_output_configure(48000)==ESP_OK);
    submit_constant(384,2,-2345);assert(native_audio_output_flush_pcm()==ESP_OK);
    verify_constant(begin,384,2,-2345);++cases;

    // At 8 kHz, a leaked previous sample/phase would generate interpolated
    // old/new frames. A fresh one-frame stream must emit exactly one sample.
    fresh_stream(8000);begin=captured;
    submit_constant(2,1,1234);native_audio_output_discard_pcm();assert(!outstanding);
    submit_constant(1,1,-2345);assert(native_audio_output_flush_pcm()==ESP_OK);
    verify_constant(begin,1,1,-2345);++cases;

    fresh_stream(48000);begin=captured;
    submit_constant(128,2,1234);
    assert(native_audio_output_configure(44100)==ESP_OK && !outstanding);
    verify_constant(begin,128,2,1234);begin=captured;
    submit_constant(127,2,-2345);assert(native_audio_output_flush_pcm()==ESP_OK);
    verify_constant(begin,expected_frames(127,44100),2,-2345);++cases;

    fresh_stream(48000);begin=captured;
    submit_constant(20,1,1234);queue.fail=true;
    assert(native_audio_output_flush_pcm()==ESP_ERR_TIMEOUT && !outstanding);
    queue.fail=false;
    assert(native_audio_output_flush_pcm()==ESP_OK && captured==begin);
    submit_constant(1,1,-2345);assert(native_audio_output_flush_pcm()==ESP_OK);
    verify_constant(begin,1,1,-2345);++cases;
#ifdef BASELINE
    // The stock staged driver can report success with a short write.
    fresh_stream(48000);begin=captured;
    submit_constant(20,1,1234);test_short_write_bytes=1024;
    assert(native_audio_output_flush_pcm()==ESP_FAIL);
    test_short_write_bytes=0;
    assert(native_audio_output_flush_pcm()==ESP_OK && captured==begin);
    ++cases;
#endif
    assert(!outstanding);fclose(capture);capture=NULL;
    printf("PASS output boundaries cases=%u pcm_bytes=%zu\n",cases,captured);
}
