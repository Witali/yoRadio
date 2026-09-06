#include <cstdint>
#include <fstream>
#include <iostream>
#include <vector>
#include <string>
#include <stdexcept>
#include "rcpdm8.h"
#include "rcpdm_simple.h"
#include "rcpdm_simple_reference.h"
#include "pdm32_original.inc"

static void check(bool value,const char *message) {
    if(!value) throw std::runtime_error(message);
}
// Independent, literal direct comparator: update only the chosen candidate.
static uint32_t reference(rc_pdm_t &p,int16_t pcm,unsigned count,unsigned shift) {
    const uint64_t target=uint64_t(int32_t(pcm)+32768)*65536;
    uint64_t state=p.rc; uint32_t word=0;
    for(unsigned i=0;i<count;++i) {
        const bool high=target>state;
        if(high) state+=(UINT32_MAX-state)/(uint64_t(1)<<shift);
        else state-=state/(uint64_t(1)<<shift);
        check(state<=UINT32_MAX,"reference overflow");
        word=(word<<1)|uint32_t(high);
    }
    p.rc=uint32_t(state); return word;
}
static uint8_t pdm8(uint32_t &acc,int16_t pcm) {
    uint8_t word=0;
    for(unsigned i=0;i<8;++i) {
        acc+=uint32_t(int32_t(pcm)+32768);
        const bool high=acc>=65536;
        if(high) acc-=65536;
        word=uint8_t((word<<1)|unsigned(high));
    }
    return word;
}
static void self_test() {
    uint64_t comparisons=0;
    auto one=[&](uint32_t seed,int16_t pcm) {
        for(unsigned shift:{2U,4U}) for(unsigned count:{8U,32U}) {
            rc_pdm_t a{seed},b{seed};
            check(rcpdm_simple_bits(&a,pcm,count,shift)==reference(b,pcm,count,shift)
                  && a.rc==b.rc,"direct comparator mismatch"); ++comparisons;
        }
    };
    for(uint32_t seed:{0U,1U,15U,0x80000000U,UINT32_MAX-15U,UINT32_MAX})
        for(int pcm=-32768;pcm<=32767;++pcm) one(seed,int16_t(pcm));
    uint32_t random=1;
    for(unsigned i=0;i<100000;++i) {
        random=random*1664525U+1013904223U; one(random,int16_t(random>>16));
    }
    // Exact equality and order are part of the new algorithm's contract.
    for(int pcm:{-32768,-1,0,1,32767}) {
        rc_pdm_t p{rc_pdm_target(int16_t(pcm))};
        const uint32_t seed=p.rc;
        check(rcpdm_simple_bits(&p,int16_t(pcm),1,4)==0 && p.rc==seed-(seed>>4),"tie must select zero");
    }
    rc_pdm_t simple,old; rc_pdm_init(&simple); rc_pdm_init(&old);
    check(rcpdm_simple_sample(&simple,0)==0x55555555U,"zero must alternate low first");
    check(rc_pdm_sample(&old,0)==0xaaaaaaaaU,"predictive control changed");
    uint64_t continuity=0;
    for(unsigned shift:{2U,4U}) {
        rc_pdm_t a,b; rc_pdm_init(&a); rc_pdm_init(&b);
        for(unsigned i=0;i<10000;++i) {
            random=random*1664525U+1013904223U;
            const int16_t pcm=int16_t(random>>16); uint32_t grouped=0;
            for(unsigned j=0;j<4;++j) grouped=(grouped<<8)|rcpdm_simple_bits(&a,pcm,8,shift);
            check(grouped==rcpdm_simple_bits(&b,pcm,32,shift) && a.rc==b.rc,"state continuity mismatch");
            ++continuity;
        }
    }
    unsigned batchWords=0;
    for(unsigned channels:{1U,2U}) {
        rc_pdm_t a,b; rc_pdm_init(&a); rc_pdm_init(&b);
        for(unsigned block=0;block<128;++block) {
            int16_t pcm[34]; uint32_t words[17];
            for(auto &value:pcm) { random=random*1664525U+1013904223U; value=int16_t(random>>16); }
            const unsigned count=block%18U;
            rcpdm_simple_fill(&a,words,pcm,count,channels);
            for(unsigned i=0;i<count;++i) {
                int32_t mono=pcm[i*channels];
                if(channels==2) mono=(mono+pcm[i*channels+1])/2;
                check(words[i]==rcpdm_simple_reference(&b,int16_t(mono)),"batch reference mismatch");
                ++batchWords;
            }
            check(a.rc==b.rc,"batch state mismatch");
        }
    }
    std::cout<<"{\"pass\":true,\"word_state_comparisons\":"<<comparisons
             <<",\"continuity_checks\":"<<continuity<<",\"tie_checks\":5,\"batch_word_checks\":"<<batchWords<<"}\n";
}
template<class T> static void save(const std::string &file,const std::vector<T> &data) {
    std::ofstream out(file,std::ios::binary);
    check(bool(out.write(reinterpret_cast<const char*>(data.data()),std::streamsize(data.size()*sizeof(T)))),"write failed");
}
int main(int argc,char **argv) {
    try {
        const uint16_t endian=1; check(*reinterpret_cast<const uint8_t*>(&endian)==1,"little-endian host required");
        if(argc==2 && std::string(argv[1])=="--self-test") { self_test(); return 0; }
        check(argc==3,"usage: rcpdm-simple-quality mono48.s16le output-prefix");
        std::ifstream in(argv[1],std::ios::binary|std::ios::ate);
        check(bool(in),"cannot open PCM"); const auto length=in.tellg();
        check(length>0 && uint64_t(length)%2==0,"invalid PCM length");
        in.seekg(0); std::vector<int16_t> pcm(size_t(length)/2);
        check(bool(in.read(reinterpret_cast<char*>(pcm.data()),length)),"cannot read PCM");
        const std::string prefix=argv[2];
        for(unsigned config=0;config<3;++config) {
            const unsigned count=config==2?32:8,shift=config==1?2:4;
            const std::string name=config==2?"rc32":(config==1?"rc8-a4":"rc8-a16");
            rc_pdm_t a,b; rc_pdm_init(&a); rc_pdm_init(&b);
            std::vector<uint32_t> predictive,simple;
            predictive.reserve(pcm.size()); simple.reserve(pcm.size());
            for(int16_t sample:pcm) {
                predictive.push_back(count==32?rc_pdm_sample(&a,sample):
                                     (shift==4?rcpdm8_shift<4>(&a,sample):rcpdm8_shift<2>(&a,sample)));
                simple.push_back(rcpdm_simple_bits(&b,sample,count,shift));
            }
            if(count==32) { save(prefix+"."+name+".bin",predictive); save(prefix+"."+name+"-simple.bin",simple); }
            else {
                std::vector<uint8_t> pa,sa; pa.reserve(pcm.size()); sa.reserve(pcm.size());
                for(size_t i=0;i<pcm.size();++i) { pa.push_back(uint8_t(predictive[i])); sa.push_back(uint8_t(simple[i])); }
                save(prefix+"."+name+".bin",pa); save(prefix+"."+name+"-simple.bin",sa);
            }
        }
        uint32_t a8=0,a32=0; std::vector<uint8_t> out8; std::vector<uint32_t> out32;
        out8.reserve(pcm.size()); out32.reserve(pcm.size());
        for(int16_t sample:pcm) { out8.push_back(pdm8(a8,sample)); out32.push_back(pdm32_original(&a32,sample)); }
        save(prefix+".pdm8.bin",out8); save(prefix+".pdm32.bin",out32);
        std::cout<<"{\"samples\":"<<pcm.size()<<"}\n";
    } catch(const std::exception &e) { std::cerr<<e.what()<<'\n'; return 1; }
}
