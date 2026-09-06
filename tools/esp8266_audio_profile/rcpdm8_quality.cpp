#include <cstdint>
#include <fstream>
#include <iostream>
#include <vector>
#include <string>
#include <stdexcept>
#include <climits>
#include <cmath>
#include "rcpdm8.h"
#include "pdm32_original.inc"

static void check(bool ok,const char *message) { if(!ok) throw std::runtime_error(message); }
static uint32_t pdm_reference(uint32_t *acc,int16_t pcm,unsigned count) {
    uint32_t word=0;
    for(unsigned i=0;i<count;++i) {
        *acc+=(uint32_t)((int32_t)pcm+32768);
        const bool high=*acc>=65536;
        if(high) *acc-=65536;
        word=(word<<1)|high;
    }
    return word;
}
static uint32_t rc_reference(rc_pdm_t *p,int16_t pcm,unsigned count,unsigned shift) {
    const uint64_t target=rc_pdm_target(pcm);
    uint32_t word=0;
    for(unsigned i=0;i<count;++i) {
        const uint64_t down=p->rc-(p->rc>>shift);
        const uint64_t up=p->rc+((uint64_t)(UINT32_MAX-p->rc)>>shift);
        const uint64_t e0=target>down ? target-down : down-target;
        const uint64_t e1=target>up ? target-up : up-target;
        const bool high=e1<e0;
        p->rc=(uint32_t)(high ? up : down); word=(word<<1)|high;
    }
    return word;
}
static uint8_t rc_q16_reference(rc_pdm_t *p,int16_t pcm,uint32_t alpha) {
    const uint64_t target=rc_pdm_target(pcm); uint8_t word=0;
    for(unsigned i=0;i<8;++i) {
        const uint64_t down=p->rc-((uint64_t)p->rc*alpha/65536);
        const uint64_t up=p->rc+((uint64_t)(UINT32_MAX-p->rc)*alpha/65536);
        const uint64_t e0=target>down ? target-down : down-target;
        const uint64_t e1=target>up ? target-up : up-target;
        const bool high=e1<e0;
        p->rc=(uint32_t)(high ? up : down); word=(uint8_t)((word<<1)|high);
    }
    return word;
}
static uint32_t matched_alpha() { return (uint32_t)std::lround((1-std::exp(-1/(384000.0*1e-5)))*65536); }
static void self_test() {
    uint64_t count=0; const uint32_t alpha=matched_alpha();
    auto one=[&](uint32_t seed,int16_t pcm) {
        uint32_t acc=seed&65535,ref=acc;
        check(pdm32_original(&acc,pcm)==pdm_reference(&ref,pcm,32) && acc==ref,"PDM32 mismatch"); ++count;
        for(unsigned shift : {2U,4U}) {
            rc_pdm_t a{seed},b{seed};
            const uint32_t out=shift==2 ? rcpdm8_shift<2>(&a,pcm) : rcpdm8_shift<4>(&a,pcm);
            check(out==rc_reference(&b,pcm,8,shift) && a.rc==b.rc,"RCPDM8 mismatch"); ++count;
        }
        rc_pdm_t a{seed},b{seed};
        check(rcpdm8_q16(&a,pcm,alpha)==rc_q16_reference(&b,pcm,alpha) && a.rc==b.rc,"Q16 mismatch"); ++count;
        a.rc=b.rc=seed;
        check(rc_pdm_sample(&a,pcm)==rc_reference(&b,pcm,32,4) && a.rc==b.rc,"RCPDM32 mismatch"); ++count;
        // Eight-bit groups at 192k PCM/s (4 identical held inputs per original
        // 48k sample) are exactly RCPDM32, not a cheaper high-carrier RCPDM8.
        a.rc=b.rc=seed; uint32_t grouped=0;
        for(unsigned i=0;i<4;++i) grouped=(grouped<<8)|rcpdm8_shift<4>(&a,pcm);
        check(grouped==rc_pdm_sample(&b,pcm) && a.rc==b.rc,"4x RCPDM8 differs from RCPDM32"); ++count;
    };
    for(uint32_t seed : {0U,1U,15U,0x80000000U,UINT32_MAX-15U,UINT32_MAX})
        for(int pcm=-32768;pcm<=32767;++pcm) one(seed,(int16_t)pcm);
    uint32_t random=1;
    for(unsigned i=0;i<100000;++i) { random=random*1664525U+1013904223U; one(random,(int16_t)(random>>8)); }
    rc_pdm_t quiet4,quiet16; rc_pdm_init(&quiet4); rc_pdm_init(&quiet16);
    for(unsigned i=0;i<48000;++i) {
        const double sine=std::sin(2*3.141592653589793*1000*i/48000);
        check(rcpdm8_shift<2>(&quiet4,(int16_t)std::lround(3276.7*sine))==0xaa,"alpha1/4 -20dB idle regression");
        check(rcpdm8_shift<4>(&quiet16,(int16_t)std::lround(327.67*sine))==0xaa,"alpha1/16 -40dB idle regression");
    }
    std::cout<<"{\"pass\":true,\"comparisons\":"<<count<<",\"quietToneChecks\":96000,\"matchedAlphaQ16\":"<<alpha<<"}\n";
}
template<class T> static void save(const std::string &name,const std::vector<T> &data) {
    std::ofstream output(name,std::ios::binary);
    check((bool)output.write((const char*)data.data(),(std::streamsize)(data.size()*sizeof(T))),"cannot write bits");
}
int main(int argc,char **argv) {
    try {
        const uint16_t endian=1; check(*(const uint8_t*)&endian==1,"requires little-endian host");
        if(argc==2 && std::string(argv[1])=="--self-test") { self_test(); return 0; }
        check(argc==3,"usage: rcpdm8-quality mono48.s16le output-prefix");
        std::ifstream input(argv[1],std::ios::binary|std::ios::ate); check((bool)input,"cannot open PCM");
        const auto length=input.tellg(); check(length>0 && (uint64_t)length%2==0,"invalid PCM length");
        input.seekg(0); std::vector<int16_t> pcm((size_t)length/2);
        check((bool)input.read((char*)pcm.data(),length),"cannot read PCM");
        std::vector<uint8_t> pdm8(pcm.size()),rc8a16(pcm.size()),rc8a4(pcm.size()),rc8matched(pcm.size());
        std::vector<uint32_t> pdm32(pcm.size()),rc32(pcm.size());
        uint32_t a8=0,a32=0; rc_pdm_t r16,r4,rq,r32;
        rc_pdm_init(&r16); rc_pdm_init(&r4); rc_pdm_init(&rq); rc_pdm_init(&r32);
        const uint32_t alpha=matched_alpha();
        for(size_t i=0;i<pcm.size();++i) {
            pdm8[i]=(uint8_t)pdm_reference(&a8,pcm[i],8);
            pdm32[i]=pdm32_original(&a32,pcm[i]);
            rc8a16[i]=rcpdm8_shift<4>(&r16,pcm[i]);
            rc8a4[i]=rcpdm8_shift<2>(&r4,pcm[i]);
            rc8matched[i]=rcpdm8_q16(&rq,pcm[i],alpha);
            rc32[i]=rc_pdm_sample(&r32,pcm[i]);
        }
        const std::string prefix=argv[2];
        save(prefix+".pdm8.bin",pdm8); save(prefix+".pdm32.bin",pdm32);
        save(prefix+".rc8-a16.bin",rc8a16); save(prefix+".rc8-a4.bin",rc8a4);
        save(prefix+".rc8-matched.bin",rc8matched); save(prefix+".rc32.bin",rc32);
        std::cout<<"{\"samples\":"<<pcm.size()<<",\"matchedAlphaQ16\":"<<alpha<<"}\n";
    } catch(const std::exception &e) { std::cerr<<e.what()<<'\n';return 1; }
}
