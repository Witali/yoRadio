#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <cstring>
#include <vector>
#include <algorithm>
#include "rc_pdm_feedback.h"
#include "rcpdm_feedback_reference.h"
static void check(bool value,const char *message) {if(!value)throw std::runtime_error(message);}
static bool same(const rc_pdm_feedback_t &a,const rc_pdm_feedback_t &b) {
    return a.rc==b.rc&&a.error==b.error&&a.previous==b.previous&&a.random==b.random;
}
int main() {
    try {
        uint64_t count=0,selected=0;uint32_t random=8266;
        auto one=[&](rc_pdm_feedback_t &a,rc_pdm_feedback_t &b,int16_t sample,
                     unsigned bits,unsigned shift,unsigned gain,unsigned dither,int interp){
            uint32_t got[6],want[6];
            std::fill_n(got,6,0xa5a5a5a5U);std::fill_n(want,6,0xa5a5a5a5U);
            auto fast=a;
            rc_pdm_feedback_frame(&a,sample,got+1,bits,shift,gain,dither,interp);
            rc_feedback_reference_frame(&b,sample,want+1,bits,shift,gain,dither,interp);
            check(std::equal(got,got+6,want)&&same(a,b),"word/state/canary reference mismatch");
            if(bits==32&&shift==4&&gain==0&&dither==2&&interp) {
                check(rc_pdm_feedback_sample(&fast,sample)==want[1]&&same(fast,b),"constant profile mismatch");
                ++selected;
            }
            check(a.rc>=0&&a.rc<=RC_FB_FULL&&a.error>=-RC_FB_ERROR_LIMIT&&a.error<=RC_FB_ERROR_LIMIT,"state bound");
            ++count;
        };
        rc_pdm_feedback_t a,b;
        rc_pdm_feedback_init(&a,0);rc_pdm_feedback_init(&b,RC_FB_DEFAULT_SEED);
        check(same(a,b),"zero seed fallback");
        for(int pcm=-32768;pcm<=32767;++pcm)one(a,b,int16_t(pcm),32,4,0,2,1);
        // Include worst-case positive raw noise (shift=2, TPDF full-step)
        // and both error limits, not only the frequency-matched diagonal.
        for(unsigned bits:{8U,16U,32U,64U,128U})for(unsigned shift=2;shift<=6;++shift) {
            for(unsigned gain=0;gain<=6;++gain)for(unsigned dither=0;dither<=3;++dither)for(int interp:{0,1}) {
                rc_pdm_feedback_init(&a,random);b=a;
                for(unsigned i=0;i<1024;++i) {
                    random=random*1664525U+1013904223U;
                    one(a,b,int16_t(random>>16),bits,shift,gain,dither,interp);
                }
                for(int32_t rc:{0,1,RC_FB_FULL/2,RC_FB_FULL-1,RC_FB_FULL})
                    for(int32_t error:{-RC_FB_ERROR_LIMIT,0,RC_FB_ERROR_LIMIT})
                        for(int pcm:{-32768,-1,0,1,32767}) {
                            a={rc,error,RC_FB_FULL,uint32_t(random)};b=a;
                            one(a,b,int16_t(pcm),bits,shift,gain,dither,interp);
                        }
            }
        }
        // No intermediate buffer, and no discontinuity at DMA/chunk edges.
        unsigned batches=0;
        for(unsigned channels:{1U,2U}) {
            std::vector<int16_t> pcm(2051*channels);
            for(auto &s:pcm){random=random*1664525U+1013904223U;s=int16_t(random>>16);}
            std::vector<uint32_t> baseline(2051),chunked(2051);
            rc_pdm_feedback_init(&a,1);rc_pdm_feedback_fill(&a,baseline.data(),pcm.data(),2051,channels);
            rc_pdm_feedback_init(&b,1);
            for(unsigned i=0;i<2051;++i) {
                int32_t mono=pcm[i*channels];
                if(channels==2)mono=(mono+pcm[i*channels+1])/2;
                check(baseline[i]==rc_feedback_reference_sample(&b,int16_t(mono)),"batch reference word");
            }
            check(same(a,b),"batch reference state");
            for(unsigned chunk:{1U,31U,32U,33U,64U,128U,512U,576U}) {
                rc_pdm_feedback_init(&b,1);
                for(unsigned start=0;start<2051;start+=chunk)
                    rc_pdm_feedback_fill(&b,chunked.data()+start,pcm.data()+start*channels,std::min(chunk,2051-start),channels);
                check(chunked==baseline&&same(a,b),"chunk continuity");++batches;
            }
            const auto saved=a;rc_pdm_feedback_fill(&a,nullptr,nullptr,0,channels);check(same(a,saved),"empty batch changed state");
        }
        // Full-scale, DC and recovery from a deliberately wound-up state.
        for(int16_t level:{int16_t(-32768),int16_t(32767),int16_t(0),int16_t(1),int16_t(-1)}) {
            a={RC_FB_FULL,RC_FB_ERROR_LIMIT,RC_FB_FULL,1};b=a;
            for(unsigned i=0;i<10000;++i)one(a,b,level,32,4,0,2,1);
            // Exact lower rail may clamp: integer exponential decay retains
            // sub-PCM-LSB residue. It must recover promptly when PCM returns
            // to audio zero, not remain stuck after leaving the rail.
            for(unsigned i=0;i<32;++i)one(a,b,0,32,4,0,2,1);
            check(a.error!=RC_FB_ERROR_LIMIT&&a.error!=-RC_FB_ERROR_LIMIT,"persistent windup after rail release");
        }
        std::cout<<"{\"pass\":true,\"word_state_frames\":"<<count<<",\"batch_cases\":"<<batches
                 <<",\"selected_frames\":"<<selected
                 <<",\"state_bytes\":"<<sizeof(a)<<"}\n";
    } catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 1;}
}
