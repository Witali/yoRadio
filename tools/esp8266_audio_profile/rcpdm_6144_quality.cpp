// Offline, 128 NEW bits/sample: ordinary PDM and predictive RC error feedback.
// Firmware is not changed. Full dither uses the actual production generic
// routine; half amplitude is checked against independent 64-bit arithmetic.
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
#include "rc_pdm_feedback.h"
#include "rcpdm_feedback_reference.h"
#include "pdm32_original.inc"

static void check(bool ok,const char *why) { if(!ok)throw std::runtime_error(why); }
static bool same(const rc_pdm_feedback_t &a,const rc_pdm_feedback_t &b) {
    return a.rc==b.rc&&a.error==b.error&&a.previous==b.previous&&a.random==b.random;
}
static void pdm128(uint32_t &state,int16_t pcm,uint32_t *out) {
    // Four consecutive accumulator runs, not four copies of the first word.
    for(unsigned word=0;word<4;++word)out[word]=pdm32_original(&state,pcm);
}
static void pdm_reference(uint32_t &state,int16_t pcm,uint32_t *out) {
    uint64_t accumulator=state,target=uint64_t(int64_t(pcm)+32768);
    for(unsigned word=0;word<4;++word) {
        uint32_t packed=0;
        for(unsigned bit=0;bit<32;++bit) {
            accumulator+=target;
            const bool high=accumulator>=65536;
            if(high)accumulator-=65536;
            packed=(packed<<1)|unsigned(high);
        }
        out[word]=packed;
    }
    state=uint32_t(accumulator);
}
static void offline_rc(rc_pdm_feedback_t &state,int16_t pcm,uint32_t *out,bool simple=false,int32_t noiseScale=32) {
    const int32_t target=(int32_t(pcm)+32768)*8192;
    const int32_t increment=(target-state.previous)/128;
    int32_t desired=state.previous;
    for(unsigned word=0;word<4;++word) {
        uint32_t packed=0;
        for(unsigned bit=0;bit<32;++bit) {
            desired+=increment;
            const uint32_t r=rc_fb_random(&state);
            // Full dither scale at RC shift 6 is 64; half is exactly 32.
            const int32_t noise=(int32_t(r&65535U)+int32_t(r>>16)-65535)*noiseScale;
            const int32_t down=state.rc-(state.rc>>6);
            const bool high=desired+state.error+noise>(simple?state.rc:down+RC_FB_FULL/128);
            state.rc=down+(high?RC_FB_FULL/64:0);
            const int32_t error=state.error+desired-state.rc;
            state.error=std::max(-RC_FB_ERROR_LIMIT,std::min(RC_FB_ERROR_LIMIT,error));
            packed=(packed<<1)|unsigned(high);
        }
        out[word]=packed;
    }
    state.previous=target;
}
static void offline_reference(rc_pdm_feedback_t &state,int16_t pcm,uint32_t *out,bool simple=false,int64_t noiseScale=32) {
    const int64_t full=INT64_C(1)<<29,bound=INT64_C(1)<<30;
    const int64_t previous=state.previous,target=(int64_t(pcm)+32768)*8192;
    int64_t voltage=state.rc,error=state.error;
    uint32_t packed=0;
    for(unsigned bit=0;bit<128;++bit) {
        const int64_t desired=previous+(target-previous)*(bit+1)/128;
        uint64_t r=state.random;
        r=(r^(r<<13))&UINT32_MAX;r^=r>>17;r=(r^(r<<5))&UINT32_MAX;
        state.random=uint32_t(r);
        const int64_t noise=(int64_t(r%65536)+int64_t(r/65536)-65535)*noiseScale;
        const int64_t down=voltage-voltage/64,up=down+full/64;
        const bool high=desired+error+noise>(simple?voltage:(up+down)/2);
        voltage=high?up:down;
        error=std::max(-bound,std::min(bound,error+desired-voltage));
        packed=(packed<<1)|unsigned(high);
        if((bit+1)%32==0) {out[bit/32]=packed;packed=0;}
    }
    state.rc=int32_t(voltage);state.error=int32_t(error);state.previous=int32_t(target);
}
struct Models {
    uint32_t pdm=0,pdmRef=0;
    rc_pdm_feedback_t full,fullRef,half,halfRef,simpleFull,simpleFullRef,simpleHalf,simpleHalfRef;
    explicit Models(uint32_t seed) {
        rc_pdm_feedback_init(&full,seed);fullRef=half=halfRef=simpleFull=simpleFullRef=simpleHalf=simpleHalfRef=full;
    }
    void frame(int16_t pcm,uint32_t words[5][4]) {
        uint32_t expected[4];
        pdm128(pdm,pcm,words[0]);pdm_reference(pdmRef,pcm,expected);
        check(std::equal(expected,expected+4,words[0])&&pdm==pdmRef,"PDM reference mismatch");
        rc_pdm_feedback_frame(&full,pcm,words[1],128,6,0,2,1);
        rc_feedback_reference_frame(&fullRef,pcm,expected,128,6,0,2,1);
        check(std::equal(expected,expected+4,words[1])&&same(full,fullRef),"full dither reference mismatch");
        auto halfFast=half;
        rc_pdm_feedback_frame(&half,pcm,words[2],128,6,0,4,1);
        offline_rc(halfFast,pcm,expected);
        check(std::equal(expected,expected+4,words[2])&&same(half,halfFast),"production half dither mismatch");
        offline_reference(halfRef,pcm,expected);
        check(std::equal(expected,expected+4,words[2])&&same(half,halfRef),"half dither reference mismatch");
        check(full.random==half.random&&full.previous==half.previous,"dither changes PRNG/interpolation");
        offline_rc(simpleFull,pcm,words[3],true,64);offline_reference(simpleFullRef,pcm,expected,true,64);
        check(std::equal(expected,expected+4,words[3])&&same(simpleFull,simpleFullRef),"Simple full reference mismatch");
        offline_rc(simpleHalf,pcm,words[4],true,32);offline_reference(simpleHalfRef,pcm,expected,true,32);
        check(std::equal(expected,expected+4,words[4])&&same(simpleHalf,simpleHalfRef),"Simple half reference mismatch");
        for(const auto *p:{&simpleFull,&simpleHalf})
            check(p->random==full.random&&p->previous==full.previous,"Simple changes PRNG/interpolation");
    }
};
static void self_test() {
    Models models(8266);uint32_t words[5][4],random=8266;unsigned count=0;
    auto one=[&](int16_t pcm){models.frame(pcm,words);++count;};
    for(int pcm=-32768;pcm<=32767;++pcm)one(int16_t(pcm));
    for(unsigned i=0;i<65536;++i){random=random*1664525U+1013904223U;one(int16_t(random>>16));}
    for(int level:{-32768,32767,0,1,-1})for(unsigned i=0;i<2048;++i)one(int16_t(level));
    std::cout<<"{\"pass\":true,\"frames_per_variant\":"<<count
             <<",\"word_state_checks\":"<<count*5*4
             <<",\"bits_per_sample\":128,\"rc_shift\":6,\"rc_state_bytes\":"<<sizeof(models.full)
             <<",\"pdm_state_bytes\":"<<sizeof(models.pdm)<<",\"same_prng\":true}\n";
}
int main(int argc,char **argv) {
    try {
        if(argc==2&&std::string(argv[1])=="--self-test"){self_test();return 0;}
        check(argc==4,"usage: rcpdm-6144-quality PCM output-prefix seed; or --self-test");
        const uint16_t endian=1;check(*reinterpret_cast<const uint8_t*>(&endian)==1,"LE host required");
        std::ifstream input(argv[1],std::ios::binary|std::ios::ate);check(bool(input),"PCM open failed");
        const auto bytes=input.tellg();check(bytes>0&&uint64_t(bytes)%2==0,"invalid PCM length");
        std::vector<int16_t> pcm(size_t(bytes)/2);input.seekg(0);
        check(bool(input.read(reinterpret_cast<char*>(pcm.data()),bytes)),"PCM read failed");
        Models models(uint32_t(std::stoul(argv[3])));std::vector<uint32_t> outputs[5];
        for(auto &out:outputs)out.reserve(pcm.size()*4);
        for(int16_t sample:pcm) {
            uint32_t words[5][4];models.frame(sample,words);
            for(unsigned variant=0;variant<5;++variant)outputs[variant].insert(outputs[variant].end(),words[variant],words[variant]+4);
        }
        const char *names[]={"pdm128","rc128-full","rc128-half","simple128-full","simple128-half"};
        for(unsigned variant=0;variant<5;++variant) {
            std::ofstream output(std::string(argv[2])+"."+names[variant]+".bin",std::ios::binary);
            check(bool(output.write(reinterpret_cast<const char*>(outputs[variant].data()),std::streamsize(outputs[variant].size()*4))),"write failed");
        }
        std::cout<<"{\"frames\":"<<pcm.size()<<",\"reference_frames_per_variant\":"<<pcm.size()
                 <<",\"variants\":5,\"bits_per_sample\":128,\"rc_shift\":6,\"same_prng\":true}\n";
    } catch(const std::exception &error){std::cerr<<error.what()<<'\n';return 1;}
}
