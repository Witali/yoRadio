// Host only: same greedy RC decision and rails; change numerical precision,
// NOT alpha, input-error feedback, bit rate, quantization or filtering.
#include <cstdint>
#include <cmath>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <stdexcept>
#include <string>
#include <vector>
#include "rcpdm8.h"
#include "pdm32_original.inc"

static constexpr uint64_t rail48 = uint64_t(UINT32_MAX) << 16;
static constexpr uint64_t initial48 = uint64_t(0x80000000U) << 16;
static void check(bool value,const char *message) {
    if(!value) throw std::runtime_error(message);
}
static uint32_t fixed48(uint64_t &state,int16_t pcm,unsigned bits,unsigned shift) {
    const uint64_t target=uint64_t(rc_pdm_target(pcm))<<16;
    uint32_t word=0;
    for(unsigned i=0;i<bits;++i) {
        const uint64_t down=state-(state>>shift);
        const uint64_t up=state+((rail48-state)>>shift);
        // The scaled rail ends in zeros: fixed32's constant-step identity
        // cannot be reused. Both candidates retain all 16 additional bits.
        const bool high=target>down+((up-down)>>1);
        state=high?up:down; word=(word<<1)|uint32_t(high);
    }
    return word;
}
static uint32_t floating64(double &state,int16_t pcm,unsigned bits,unsigned shift) {
    const double alpha=1.0/(1U<<shift),target=rc_pdm_target(pcm);
    uint32_t word=0;
    for(unsigned i=0;i<bits;++i) {
        const double down=state-state*alpha;
        const double up=state+(double(UINT32_MAX)-state)*alpha;
        const bool high=target>down+(up-down)*0.5;
        state=high?up:down; word=(word<<1)|uint32_t(high);
    }
    return word;
}
static uint32_t reference48(uint64_t &state,int16_t pcm,unsigned bits,unsigned shift) {
    const int64_t target=int64_t(rc_pdm_target(pcm))<<16;
    uint32_t word=0;
    for(unsigned i=0;i<bits;++i) {
        const int64_t down=int64_t(state-state/(uint64_t(1)<<shift));
        const int64_t up=int64_t(state+(rail48-state)/(uint64_t(1)<<shift));
        const int64_t d0=target-down,d1=target-up;
        const bool high=(d1<0?-d1:d1)<(d0<0?-d0:d0);
        state=uint64_t(high?up:down); word=(word<<1)|uint32_t(high);
    }
    return word;
}
static void self_test() {
    uint64_t comparisons=0,quietChecks=0;
    for(uint64_t seed : {uint64_t(0),uint64_t(1),initial48,rail48-1,rail48})
        for(int pcm=-32768;pcm<=32767;++pcm) for(unsigned shift : {2U,4U}) {
            uint64_t a=seed,b=seed;
            check(fixed48(a,int16_t(pcm),8,shift)==reference48(b,int16_t(pcm),8,shift)
                  && a==b,"fixed48 nearest-candidate mismatch"); ++comparisons;
        }
    uint32_t random=1;
    uint64_t a=initial48,b=a;
    double d=double(0x80000000U),e=d;
    for(unsigned i=0;i<10000;++i) {
        random=random*1664525U+1013904223U;
        const int16_t pcm=int16_t(random>>16);
        uint32_t grouped=0,groupedDouble=0;
        for(unsigned j=0;j<4;++j) {
            grouped=(grouped<<8)|fixed48(a,pcm,8,4);
            groupedDouble=(groupedDouble<<8)|floating64(d,pcm,8,4);
        }
        check(grouped==fixed48(b,pcm,32,4) && a==b,"fixed48 block continuity");
        check(groupedDouble==floating64(e,pcm,32,4) && d==e,"double block continuity");
        comparisons+=2;
    }
    // Force SAME bits into the double model to measure integration rounding.
    // This bound does not apply to independently chosen bit sequences.
    double maximumError=0;
    for(unsigned shift : {2U,4U}) {
        rc_pdm_t p; rc_pdm_init(&p);
        double shadow=p.rc,alpha=1.0/(1U<<shift);
        for(unsigned i=0;i<100000;++i) {
            random=random*1664525U+1013904223U;
            const int16_t pcm=int16_t(random>>16);
            const uint32_t word=shift==4?rcpdm8_shift<4>(&p,pcm):rcpdm8_shift<2>(&p,pcm);
            for(int bit=7;bit>=0;--bit)
                shadow+=((word>>bit)&1)?(double(UINT32_MAX)-shadow)*alpha:-shadow*alpha;
            const double error=std::abs(double(p.rc)-shadow);
            if(error>maximumError) maximumError=error;
            check(error<(1U<<shift)+0.001,"forced-bit integration error bound");
        }
    }
    for(unsigned shift : {2U,4U}) for(unsigned bits : {8U,32U}) {
        uint64_t wide=initial48; double exact=double(0x80000000U);
        const double peak=shift==2?3276.7:327.67;
        const uint32_t idle=bits==8?0xaaU:0xaaaaaaaaU;
        for(unsigned i=0;i<48000;++i) {
            const int16_t pcm=int16_t(std::lround(peak*std::sin(2*3.141592653589793*1000*i/48000)));
            check(fixed48(wide,pcm,bits,shift)==idle,"fixed48 quiet tone no longer idle");
            check(floating64(exact,pcm,bits,shift)==idle,"double quiet tone no longer idle");
            quietChecks+=2;
        }
    }
    std::cout<<std::setprecision(12)<<"{\"pass\":true,\"comparisons\":"<<comparisons
             <<",\"quiet_tone_checks\":"<<quietChecks
             <<",\"forced_bit_max_error_pcm\":"<<maximumError/65536
             <<",\"forced_bit_bound_pcm\":"<<16.0/65536<<"}\n";
}
template<class T> static void save(const std::string &file,const std::vector<T> &data) {
    std::ofstream out(file,std::ios::binary);
    check(bool(out.write(reinterpret_cast<const char*>(data.data()),std::streamsize(data.size()*sizeof(T)))),"write failed");
}
int main(int argc,char **argv) {
    try {
        const uint16_t endian=1; check(*reinterpret_cast<const uint8_t*>(&endian)==1,"little-endian host required");
        if(argc==2 && std::string(argv[1])=="--self-test") { self_test(); return 0; }
        check(argc==3,"usage: rcpdm-precision mono48.s16le output-prefix");
        std::ifstream in(argv[1],std::ios::binary|std::ios::ate);
        check(bool(in),"cannot open PCM"); const auto length=in.tellg();
        check(length>0 && uint64_t(length)%2==0,"invalid PCM size");
        in.seekg(0); std::vector<int16_t> pcm(size_t(length)/2);
        check(bool(in.read(reinterpret_cast<char*>(pcm.data()),length)),"cannot read PCM");
        const std::string prefix=argv[2];
        for(unsigned config=0;config<3;++config) {
            const unsigned bits=config==2?32:8,shift=config==1?2:4;
            const std::string name=config==2?"rc32-a16":(config==1?"rc8-a4":"rc8-a16");
            rc_pdm_t original; rc_pdm_init(&original);
            uint64_t wide=initial48; double exact=double(0x80000000U);
            std::vector<uint32_t> out[3]; for(auto &v:out) v.reserve(pcm.size());
            for(int16_t sample:pcm) {
                out[0].push_back(bits==32?rc_pdm_sample(&original,sample):
                                (shift==4?rcpdm8_shift<4>(&original,sample):rcpdm8_shift<2>(&original,sample)));
                out[1].push_back(fixed48(wide,sample,bits,shift));
                out[2].push_back(floating64(exact,sample,bits,shift));
            }
            for(unsigned p=0;p<3;++p) {
                const std::string file=prefix+"."+name+"-"+(p==0?"fixed32":(p==1?"fixed48":"double"))+".bin";
                if(bits==32) save(file,out[p]);
                else {
                    std::vector<uint8_t> bytes; bytes.reserve(out[p].size());
                    for(uint32_t word:out[p]) bytes.push_back(uint8_t(word));
                    save(file,bytes);
                }
            }
        }
        uint32_t accumulator=0; std::vector<uint32_t> pdm; pdm.reserve(pcm.size());
        for(int16_t sample:pcm) pdm.push_back(pdm32_original(&accumulator,sample));
        save(prefix+".pdm32.bin",pdm);
        std::cout<<"{\"samples\":"<<pcm.size()<<"}\n";
    } catch(const std::exception &e) { std::cerr<<e.what()<<'\n'; return 1; }
}
