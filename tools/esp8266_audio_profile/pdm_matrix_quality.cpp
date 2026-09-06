// Offline rate matrix only: no new firmware profile or hardware timing claim.
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
#include "rcpdm_simple.h"
#include "pdm32_original.inc"

static void check(bool ok,const char *message) {
    if(!ok) throw std::runtime_error(message);
}
struct Variant { std::string name; unsigned bits,shift,method; };
static std::vector<Variant> variants() {
    std::vector<Variant> out;
    unsigned matchedShift=2;
    for(unsigned bits:{8U,16U,32U,64U,128U}) {
        out.push_back({"pdm"+std::to_string(bits),bits,0,0});
        std::vector<unsigned> shifts{4U};
        if(matchedShift!=4) shifts.push_back(matchedShift);
        for(unsigned shift:shifts) {
            const std::string suffix=std::to_string(bits)+"-a"+std::to_string(1U<<shift);
            out.push_back({"rc"+suffix,bits,shift,1});
            out.push_back({"simple"+suffix,bits,shift,2});
        }
        ++matchedShift;
    }
    return out;
}
static uint32_t chunk(uint32_t &state,int16_t pcm,unsigned count,unsigned shift,unsigned method) {
    if(method==0) {
        if(count==32) return pdm32_original(&state,pcm);
        const uint32_t target=uint32_t(int32_t(pcm)+32768);
        uint32_t word=0;
        for(unsigned i=0;i<count;++i) {
            const uint32_t sum=state+target;
            state=sum&65535U; word=(word<<1)|(sum>>16);
        }
        return word;
    }
    rc_pdm_t p{state}; uint32_t word=0;
    if(method==2) word=rcpdm_simple_bits_c(&p,pcm,count,shift);
    else if(count==32 && shift==4) word=rc_pdm_sample(&p,pcm);
    else {
        const uint32_t step=UINT32_MAX>>shift,half=step>>1;
        const uint32_t target=rc_pdm_target(pcm),limit=target>half?target-half:0;
        for(unsigned i=0;i<count;++i) {
            p.rc-=p.rc>>shift; word<<=1;
            if(p.rc<limit) { p.rc+=step; word|=1; }
        }
    }
    state=p.rc; return word;
}
// Literal wider reference: division and candidate-distance comparison, not the
// optimized threshold expression. Retain strict ties-to-zero and truncation.
static uint32_t reference(uint32_t &state,int16_t pcm,unsigned count,unsigned shift,unsigned method) {
    const uint64_t target=uint64_t(int32_t(pcm)+32768)*(method?65536:1);
    uint64_t s=state; uint32_t word=0;
    for(unsigned bit=0;bit<count;++bit) {
        bool high;
        if(!method) { s+=target; high=s>=65536; if(high) s-=65536; }
        else {
            const uint64_t divisor=uint64_t(1)<<shift;
            const uint64_t down=s-s/divisor,up=s+(UINT32_MAX-s)/divisor;
            high=method==2?target>s:target>down+(up-down)/2;
            s=high?up:down;
        }
        check(s<=UINT32_MAX,"reference overflow");
        word=(word<<1)|unsigned(high);
    }
    state=uint32_t(s); return word;
}
static void self_test() {
    uint64_t checks=0;
    auto one=[&](const Variant &v,uint32_t seed,int16_t sample) {
        uint32_t a=v.method?seed:seed&65535U,b=a;
        for(unsigned offset=0;offset<v.bits;offset+=32) {
            const unsigned count=std::min(32U,v.bits-offset);
            const uint32_t got=chunk(a,sample,count,v.shift,v.method);
            check(got==reference(b,sample,count,v.shift,v.method) && a==b,"word/state mismatch");
            ++checks;
        }
    };
    for(const auto &v:variants()) {
        for(int pcm=-32768;pcm<=32767;++pcm) one(v,0x80000000U,int16_t(pcm));
        for(uint32_t seed:{0U,1U,15U,UINT32_MAX-15U,UINT32_MAX})
            for(int pcm:{-32768,-32767,-1,0,1,32766,32767}) one(v,seed,int16_t(pcm));
        uint32_t random=1;
        for(unsigned i=0;i<10000;++i) {
            random=random*1664525U+1013904223U; one(v,random,int16_t(random>>16));
        }
    }
    // Splitting a held sample into 8-bit groups must not repeat bits/reset state.
    unsigned grouped=0;
    for(unsigned method:{0U,1U,2U}) for(unsigned shift:{2U,3U,4U,5U,6U}) {
        uint32_t a=method?0x80000000U:0,b=a;
        for(int pcm=-32768;pcm<=32767;pcm+=257) {
            uint32_t word=0;
            for(unsigned i=0;i<4;++i) word=(word<<8)|chunk(a,int16_t(pcm),8,shift,method);
            check(word==chunk(b,int16_t(pcm),32,shift,method) && a==b,"grouping changed bits");
            ++grouped;
        }
    }
    std::cout<<"{\"pass\":true,\"variants\":"<<variants().size()
             <<",\"word_state_checks\":"<<checks<<",\"grouping_checks\":"<<grouped<<"}\n";
}
int main(int argc,char **argv) {
    try {
        if(argc==2 && std::string(argv[1])=="--self-test") { self_test(); return 0; }
        check(argc==3 || (argc==4 && std::string(argv[3])=="--matched-6144"),
              "usage: pdm-matrix-quality mono48.s16le output-prefix [--matched-6144]");
        const bool matched6144=argc==4;
        const uint16_t endian=1;
        check(*reinterpret_cast<const uint8_t*>(&endian)==1,"little-endian PCM host required");
        std::ifstream in(argv[1],std::ios::binary|std::ios::ate);
        check(bool(in),"cannot open PCM"); const auto size=in.tellg();
        check(size>0 && uint64_t(size)%2==0,"invalid PCM size");
        std::vector<int16_t> pcm(size_t(size)/2); in.seekg(0);
        check(bool(in.read(reinterpret_cast<char*>(pcm.data()),size)),"cannot read PCM");
        unsigned generated=0; uint64_t referenceChecks=0;
        for(const auto &v:variants()) {
            if(matched6144 && (v.bits!=128 || (v.method && v.shift!=6)))continue;
            ++generated;
            uint32_t state=v.method?0x80000000U:0;
            uint32_t referenceState=state;
            std::vector<uint8_t> data; data.reserve(pcm.size()*(v.bits/8));
            for(int16_t sample:pcm) for(unsigned offset=0;offset<v.bits;offset+=32) {
                const unsigned count=std::min(32U,v.bits-offset);
                const uint32_t word=chunk(state,sample,count,v.shift,v.method);
                if(matched6144) {
                    check(word==reference(referenceState,sample,count,v.shift,v.method)
                          && state==referenceState,"6144 capture reference mismatch");
                    ++referenceChecks;
                }
                // Little-endian words, chronological bits MSB first within word.
                for(unsigned byte=0;byte<count/8;++byte) data.push_back(uint8_t(word>>(8*byte)));
            }
            std::ofstream out(std::string(argv[2])+"."+v.name+".bin",std::ios::binary);
            check(bool(out.write(reinterpret_cast<const char*>(data.data()),std::streamsize(data.size()))),"write failed");
        }
        std::cout<<"{\"samples\":"<<pcm.size()<<",\"variants\":"<<generated;
        if(matched6144)std::cout<<",\"bits_per_sample\":128,\"rc_shift\":6,\"reference_word_state_checks\":"<<referenceChecks;
        std::cout<<"}\n";
    } catch(const std::exception &error) { std::cerr<<error.what()<<'\n'; return 1; }
}
