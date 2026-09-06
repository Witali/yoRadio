// Offline ablation: only accumulated-error feedback differs. No firmware flag
// or production source is modified. On uses the real selected hardware wrapper;
// the independent 64-bit model validates on and generates the off control.
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
#include "rc_pdm_feedback.h"
#include "rcpdm_feedback_reference.h"

static void check(bool ok,const char *why) {if(!ok)throw std::runtime_error(why);}
static bool same(const rc_pdm_feedback_t &a,const rc_pdm_feedback_t &b) {
    return a.rc==b.rc&&a.error==b.error&&a.previous==b.previous&&a.random==b.random;
}
static uint32_t literal(rc_pdm_feedback_t &s,int16_t pcm,bool enabled) {
    const int64_t full=INT64_C(1)<<29,limit=INT64_C(1)<<30,step=full/16;
    const int64_t previous=s.previous,target=(int64_t(pcm)+32768)*8192;
    int64_t voltage=s.rc,error=enabled?s.error:0;
    uint32_t word=0;
    for(unsigned bit=0;bit<32;++bit) {
        const int64_t desired=previous+(target-previous)*(bit+1)/32;
        uint64_t r=s.random;
        r=(r^(r<<13))&UINT32_MAX;r^=r>>17;r=(r^(r<<5))&UINT32_MAX;
        s.random=uint32_t(r);
        const int64_t noise=(int64_t(r%65536)+int64_t(r/65536)-65535)*256;
        const int64_t down=voltage-voltage/16;
        const bool high=desired+(enabled?error:0)+noise>down+step/2;
        voltage=down+(high?step:0);
        if(enabled)error=std::max(-limit,std::min(limit,error+desired-voltage));
        word=(word<<1)|unsigned(high);
    }
    s.rc=int32_t(voltage);s.previous=int32_t(target);s.error=int32_t(error);
    return word;
}
static void self_test() {
    rc_pdm_feedback_t prod,model,frozen,off;
    rc_pdm_feedback_init(&prod,0);model=frozen=off=prod;
    uint32_t random=8266;unsigned count=0,changed=0;
    auto one=[&](int16_t pcm) {
        const uint32_t got=rc_pdm_feedback_sample(&prod,pcm);
        check(got==literal(model,pcm,true)&&same(prod,model),"enabled differs from production");
        check(got==rc_feedback_reference_sample(&frozen,pcm)&&same(prod,frozen),"frozen reference differs");
        auto ignored=off;ignored.error=(count&1)?RC_FB_ERROR_LIMIT:-RC_FB_ERROR_LIMIT;
        const uint32_t without=literal(off,pcm,false);
        check(without==literal(ignored,pcm,false)&&same(off,ignored),"off depends on feedback state");
        check(off.error==0&&off.random==prod.random&&off.previous==prod.previous,"off changes more than feedback");
        changed+=got!=without;++count;
    };
    for(int pcm=-32768;pcm<=32767;++pcm)one(int16_t(pcm));
    for(unsigned i=0;i<65536;++i){random=random*1664525U+1013904223U;one(int16_t(random>>16));}
    for(int level:{-32768,32767,0,1,-1})for(unsigned i=0;i<2048;++i)one(int16_t(level));
    check(changed>0,"feedback ablation has no effect");
    std::cout<<"{\"pass\":true,\"frames\":"<<count<<",\"different_words\":"<<changed
             <<",\"prng_and_interpolation_identical\":true,\"off_error_ignored\":true}\n";
}
int main(int argc,char **argv) {
    try {
        if(argc==2&&std::string(argv[1])=="--self-test"){self_test();return 0;}
        check(argc==4,"usage: rcpdm-feedback-ab PCM output-prefix seed; or --self-test");
        const uint16_t endian=1;check(*reinterpret_cast<const uint8_t*>(&endian)==1,"LE host required");
        std::ifstream input(argv[1],std::ios::binary|std::ios::ate);check(bool(input),"PCM open failed");
        const auto bytes=input.tellg();check(bytes>0&&uint64_t(bytes)%2==0,"invalid PCM length");
        std::vector<int16_t> pcm(size_t(bytes)/2);input.seekg(0);
        check(bool(input.read(reinterpret_cast<char*>(pcm.data()),bytes)),"PCM read failed");
        const auto seed=uint32_t(std::stoul(argv[3]));
        rc_pdm_feedback_t on,reference,off;rc_pdm_feedback_init(&on,seed);reference=off=on;
        std::vector<uint32_t> with(pcm.size()),without(pcm.size());unsigned different=0;
        for(size_t i=0;i<pcm.size();++i) {
            with[i]=rc_pdm_feedback_sample(&on,pcm[i]);
            check(with[i]==literal(reference,pcm[i],true)&&same(on,reference),"enabled model/production mismatch");
            without[i]=literal(off,pcm[i],false);
            check(off.random==on.random&&off.previous==on.previous&&off.error==0,"ablation invariants");
            different+=with[i]!=without[i];
        }
        auto write=[&](const char *suffix,const std::vector<uint32_t> &data) {
            std::ofstream output(std::string(argv[2])+suffix,std::ios::binary);
            check(bool(output.write(reinterpret_cast<const char*>(data.data()),std::streamsize(data.size()*4))),"bitstream write failed");
        };
        write(".on.bin",with);write(".off.bin",without);
        std::cout<<"{\"frames\":"<<pcm.size()<<",\"different_words\":"<<different
                 <<",\"on_reference_frames\":"<<pcm.size()<<",\"prng_and_interpolation_identical\":true}\n";
    } catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 1;}
}
