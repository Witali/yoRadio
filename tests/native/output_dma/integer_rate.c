// Included after the unchanged production source, with guarded driver stubs.
#include <math.h>

static int64_t round_ratio(int64_t value, uint32_t denominator) {
    return value >= 0 ? (value + denominator/2)/denominator
                      : -((-value + denominator/2)/denominator);
}

static void run_rate(unsigned rate, unsigned count, unsigned tone_hz) {
    assert(native_audio_output_configure(rate) == ESP_OK);
    native_audio_output_discard_pcm();
    int16_t *input = malloc((size_t)count*4); assert(input);
    uint32_t rng = 0x73a04b15;
    for (unsigned i=0;i<count;++i) {
        rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5;
        input[2*i] = tone_hz ? (int16_t)lround(20000.0*sin(2.0*3.141592653589793*tone_hz*i/rate)) : (int16_t)rng;
        input[2*i+1] = tone_hz ? -input[2*i] : (int16_t)(rng >> 16);
    }
    capture = tmpfile(); assert(capture); captured=0;
    for (unsigned i=0;i<count;++i)
        assert(pdm_write_resampled(input[2*i],input[2*i+1]) == ESP_OK);
    uint64_t expected = 1+(uint64_t)(count-1)*625000/(rate*13);
    assert(captured/4+s_buffered_frames == expected);
    assert(native_audio_output_flush_pcm() == ESP_OK);
    assert(captured/4 == (expected+511)/512*512);
    size_t after_flush=captured;
    assert(native_audio_output_flush_pcm() == ESP_OK && captured==after_flush);
    rewind(capture);
    int max_error=0;
    double ideal_energy=0, difference_energy=0, actual_energy=0;
    for (uint64_t j=0;j<captured/4;++j) {
        int16_t pcm[2]; assert(fread(pcm,4,1,capture)==1);
        if(j>=expected) { assert(pcm[0]==0 && pcm[1]==0); continue; }
        uint64_t position=j*rate*13;
        uint64_t left=j ? (position-1)/625000 : 0;
        uint32_t remainder=j ? (uint32_t)(position-left*625000) : 0;
        assert(left<count && (!j || left+1<count));
        for(unsigned ch=0;ch<2;++ch) {
            int previous=input[2*left+ch];
            int64_t reference=previous;
            if(j) reference+=round_ratio((int64_t)(input[2*(left+1)+ch]-previous)*remainder,625000);
            int error=abs((int)pcm[ch]-(int)reference);
            if(error>max_error)max_error=error;
            assert(error<=2);
        }
        if(tone_hz) {
            double ideal=20000.0*sin(2.0*3.141592653589793*tone_hz*(double)j*13/625000);
            ideal_energy+=ideal*ideal;
            actual_energy+=(double)pcm[0]*pcm[0];
            difference_energy+=(pcm[0]-ideal)*(pcm[0]-ideal);
        }
    }
    printf("{\"rate\":%u,\"input_frames\":%u,\"output_frames\":%llu,\"tone_hz\":%u,\"linear_reference_max_lsb\":%d",
           rate,count,(unsigned long long)expected,tone_hz,max_error);
    if(tone_hz) printf(",\"rms_gain_db\":%.6f,\"ideal_sine_error_db\":%.6f",
                      10*log10(actual_energy/ideal_energy),10*log10(difference_energy/ideal_energy));
    puts("}");
    fclose(capture);capture=NULL;free(input);
    native_audio_output_discard_pcm();
    assert(!s_resampler_has_previous && !s_buffered_frames);
}

int main(void) {
    assert(native_audio_output_init()==ESP_OK);
    assert(native_audio_output_configure(7999)==ESP_ERR_INVALID_ARG);
    assert(native_audio_output_configure(48001)==ESP_ERR_INVALID_ARG);
    const unsigned rates[]={8000,11025,12000,16000,22050,24000,32000,44100,48000};
    for(unsigned i=0;i<sizeof(rates)/sizeof(rates[0]);++i) {
        run_rate(rates[i],1,0);
        run_rate(rates[i],513,0);
        run_rate(rates[i],rates[i]*2,0);
    }
    // An odd legal rate exercises every rational phase over one full period.
    run_rate(44101,625001,0);
    for(unsigned i=0;i<5;++i) {
        const unsigned tones[]={100,1000,10000,18000,20000};
        run_rate(48000,96000,tones[i]);
    }
    // Count ten minutes without file I/O. The same production resampler runs;
    // only the fake SDK consumes its blocks immediately.
    for(unsigned rate=44100;rate<=48000;rate+=3900) {
        native_audio_output_configure(rate);native_audio_output_discard_pcm();
        s_dma_write_profile.written_bytes=0;
        for(unsigned i=0;i<rate*600;++i) assert(pdm_write_resampled(0,0)==ESP_OK);
        uint64_t frames=s_dma_write_profile.written_bytes/4+s_buffered_frames;
        assert(frames==1+(uint64_t)(rate*600-1)*625000/(rate*13));
        printf("{\"rate\":%u,\"seconds\":600,\"output_frames\":%llu,\"count_pass\":true}\n",rate,(unsigned long long)frames);
    }
}
