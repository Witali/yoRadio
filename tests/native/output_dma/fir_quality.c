// The actual application output C is compiled before this independent oracle.
#include <math.h>

static int16_t saturate_reference(double sample) {
    long value = lround(sample);
    return value > INT16_MAX ? INT16_MAX : value < INT16_MIN ? INT16_MIN : (int16_t)value;
}

static void reference_coefficients(double fraction, double *weights) {
    double sum = 0;
    for(int tap=0;tap<32;++tap) {
        double x=tap-15-fraction;
        double pi=3.14159265358979323846;
        double sinc=x==0 ? 1 : sin(pi*x)/(pi*x);
        double w=.42+.5*cos(pi*x/16)+.08*cos(2*pi*x/16);
        weights[tap]=sinc*w;sum+=weights[tap];
    }
    for(int tap=0;tap<32;++tap)weights[tap]/=sum;
}

static void check_case(unsigned rate,unsigned frames,unsigned tone,int full_scale) {
    assert(native_audio_output_configure(rate)==ESP_OK);
    native_audio_output_discard_pcm();
    int16_t *input=malloc((size_t)frames*4);assert(input);
    uint32_t rng=0x14578c3;
    for(unsigned i=0;i<frames;++i) {
        rng^=rng<<13;rng^=rng>>17;rng^=rng<<5;
        input[2*i]=tone ? (int16_t)lround(20000*sin(2*3.141592653589793*tone*i/rate))
                          : full_scale ? (i%2 ? INT16_MAX : INT16_MIN) : (int16_t)rng;
        input[2*i+1]=tone ? -input[2*i] : (int16_t)(rng>>16);
    }
    capture=tmpfile();assert(capture);captured=0;
    for(unsigned i=0;i<frames;++i)
        assert(pdm_write_resampled(input[2*i],input[2*i+1])==ESP_OK);
    assert(native_audio_output_flush_pcm()==ESP_OK && !s_pcm_fir.valid);
    uint64_t expected=1+(uint64_t)(frames-1)*625000/(rate*13);
    assert(captured/4==(expected+511)/512*512);
    size_t first=captured;
    assert(native_audio_output_flush_pcm()==ESP_OK && captured==first);
    rewind(capture);
    int max_error=0;unsigned clips=0;
    double energy=0,ideal_energy=0,error_energy=0;
    for(uint64_t j=0;j<captured/4;++j) {
        int16_t pcm[2];assert(fread(pcm,4,1,capture)==1);
        if(j>=expected){assert(!pcm[0]&&!pcm[1]);continue;}
        uint64_t coordinate=j*rate*13;
        uint64_t center=coordinate/625000;
        double fraction=(coordinate%625000)/625000.0,weights[32];
        reference_coefficients(fraction,weights);
        for(unsigned ch=0;ch<2;++ch) {
            double reference=0;
            for(int k=0;k<32;++k) {
                int64_t index=(int64_t)center+k-15;
                if(index<0)index=0;
                if(index>=frames)index=frames-1;
                reference+=input[2*index+ch]*weights[k];
            }
            if(reference>32767.5||reference<-32768.5)++clips;
            int delta=abs(pcm[ch]-saturate_reference(reference));
            if(delta>max_error)max_error=delta;
            if(delta>3){fprintf(stderr,"bad PCM rate=%u frames=%u j=%llu ch=%u actual=%d reference=%.9f delta=%d\n",rate,frames,(unsigned long long)j,ch,pcm[ch],reference,delta);abort();}
        }
        if(tone && center>=32 && center+32<frames) {
            double ideal=20000*sin(2*3.141592653589793*tone*(double)j*13/625000);
            energy+=(double)pcm[0]*pcm[0];ideal_energy+=ideal*ideal;
            error_energy+=(pcm[0]-ideal)*(pcm[0]-ideal);
        }
    }
    printf("{\"rate\":%u,\"frames\":%u,\"output_frames\":%llu,\"tone\":%u,\"full_scale\":%d,\"max_reference_lsb\":%d,\"saturated_samples\":%u",
           rate,frames,(unsigned long long)expected,tone,full_scale,max_error,clips);
    if(tone)printf(",\"gain_db\":%.8f,\"ideal_error_db\":%.8f",10*log10(energy/ideal_energy),10*log10(error_energy/ideal_energy));
    puts("}");
    fclose(capture);capture=NULL;free(input);
}

int main(void) {
    _Static_assert(sizeof(pcm_fir_state_t)==136,"Unexpected FIR state growth");
    assert(native_audio_output_init()==ESP_OK);
    const unsigned rates[]={8000,11025,12000,16000,22050,24000,32000,44100,44101,48000};
    const unsigned lengths[]={1,2,15,16,17,31,32,511,512,513,2500};
    for(unsigned r=0;r<10;++r)for(unsigned n=0;n<11;++n)check_case(rates[r],lengths[n],0,0);
    check_case(48000,2500,0,1);check_case(44100,2500,0,1);
    const unsigned tones[]={100,1000,10000,18000,20000};
    for(unsigned r=0;r<2;++r)for(unsigned t=0;t<5;++t)check_case(r ? 48000 : 44100,96000,tones[t],0);
    assert(pcm_fir_round_saturate(INT64_C(1)<<40)==INT16_MAX);
    assert(pcm_fir_round_saturate(-(INT64_C(1)<<40))==INT16_MIN);
    return 0;
}
