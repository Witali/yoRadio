#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
#include "rc_pdm_feedback.h"

static void check(bool value,const char *message) { if(!value) throw std::runtime_error(message); }
int main(int argc,char **argv) {
    try {
        check(argc==9,"usage: rcpdm-feedback-quality PCM output bits rc-shift feedback-shift dither interpolate seed");
        const unsigned bits=unsigned(std::stoul(argv[3])),shift=unsigned(std::stoul(argv[4]));
        const unsigned feedback=unsigned(std::stoul(argv[5])),dither=unsigned(std::stoul(argv[6]));
        const int interpolate=std::stoi(argv[7]); const auto seed=uint32_t(std::stoul(argv[8]));
        check((bits==8||bits==16||bits==32||bits==64||bits==128)&&shift>=2&&shift<=6&&feedback<=6&&dither<=3,"invalid configuration");
        const uint16_t endian=1;check(*reinterpret_cast<const uint8_t*>(&endian)==1,"LE host required");
        std::ifstream in(argv[1],std::ios::binary|std::ios::ate);check(bool(in),"cannot open PCM");
        const auto size=in.tellg();check(size>0&&uint64_t(size)%2==0,"invalid PCM length");
        std::vector<int16_t> pcm(size_t(size)/2);in.seekg(0);
        check(bool(in.read(reinterpret_cast<char*>(pcm.data()),size)),"PCM read failed");
        std::vector<uint8_t> bytes;bytes.reserve(pcm.size()*bits/8);
        rc_pdm_feedback_t state;rc_pdm_feedback_init(&state,seed);
        for(auto sample:pcm) {
            uint32_t words[4];rc_pdm_feedback_frame(&state,sample,words,bits,shift,feedback,dither,interpolate);
            const unsigned width=bits<32?bits:32;
            for(unsigned offset=0;offset<bits/width;++offset)
                for(unsigned byte=0;byte<width/8;++byte) bytes.push_back(uint8_t(words[offset]>>(8*byte)));
            check(state.rc>=0&&state.rc<=RC_FB_FULL,"RC out of range");
        }
        std::ofstream out(argv[2],std::ios::binary);
        check(bool(out.write(reinterpret_cast<const char*>(bytes.data()),std::streamsize(bytes.size()))),"output write failed");
        std::cout<<"{\"frames\":"<<pcm.size()<<",\"state_bytes\":"<<sizeof(state)<<",\"error\":"<<state.error<<"}\n";
    } catch(const std::exception &e) { std::cerr<<e.what()<<'\n'; return 1; }
}
