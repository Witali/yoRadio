// Offline feedback/dither ablation. No firmware source or flags are changed.
// Predictive-on uses the production modulator; Simple has an independent
// 32-bit path. Both are checked against a literal 64-bit model.
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
// Historical full-amplitude control remains explicit when the selected
// firmware wrapper changes to the recommended half-amplitude dither.
static uint32_t full_control(rc_pdm_feedback_t &s,int16_t pcm) {
    uint32_t word;rc_pdm_feedback_frame(&s,pcm,&word,32,4,0,2,1);return word;
}
static uint32_t literal(rc_pdm_feedback_t &s,int16_t pcm,bool enabled,bool simple=false,bool dither=true,unsigned attenuation=0) {
    const int64_t full=INT64_C(1)<<29,limit=INT64_C(1)<<30,step=full/16;
    const int64_t previous=s.previous,target=(int64_t(pcm)+32768)*8192;
    int64_t voltage=s.rc,error=enabled?s.error:0;
    uint32_t word=0;
    for(unsigned bit=0;bit<32;++bit) {
        const int64_t desired=previous+(target-previous)*(bit+1)/32;
        int64_t noise=0;
        if(dither) {
            uint64_t r=s.random;
            r=(r^(r<<13))&UINT32_MAX;r^=r>>17;r=(r^(r<<5))&UINT32_MAX;
            s.random=uint32_t(r);
            noise=(int64_t(r%65536)+int64_t(r/65536)-65535)*(256/(1U<<attenuation));
        }
        const int64_t down=voltage-voltage/16;
        const bool high=desired+(enabled?error:0)+noise>(simple?voltage:down+step/2);
        voltage=down+(high?step:0);
        if(enabled)error=std::max(-limit,std::min(limit,error+desired-voltage));
        word=(word<<1)|unsigned(high);
    }
    s.rc=int32_t(voltage);s.previous=int32_t(target);s.error=int32_t(error);
    return word;
}
// Same scale/interpolation/dither/RC recurrence as Feedback32, but compare
// the CURRENT voltage, not the midpoint of the predicted next voltages.
// This is a new offline Simple ablation, NOT the old no-dither ASM backend.
static uint32_t simple32(rc_pdm_feedback_t &s,int16_t pcm,bool enabled,bool dither=true,unsigned attenuation=0,bool simple=true) {
    const int32_t target=(int32_t(pcm)+32768)*8192;
    const int32_t increment=(target-s.previous)/32;
    int32_t desired=s.previous;
    // Scale the positive coefficient, not a signed random value: no rounding
    // bias, and exactly the same PRNG sequence at every nonzero amplitude.
    const int32_t noiseScale=256>>attenuation;
    if(!enabled)s.error=0;
    uint32_t word=0;
    for(unsigned bit=0;bit<32;++bit) {
        desired+=increment;
        int32_t noise=0;
        if(dither) {
            const uint32_t r=rc_fb_random(&s);
            noise=(int32_t(r&65535U)+int32_t(r>>16)-65535)*noiseScale;
        }
        const int32_t threshold=simple?s.rc:s.rc-(s.rc>>4)+RC_FB_FULL/32;
        const bool high=desired+s.error+noise>threshold; // Decide before decay.
        s.rc-=s.rc>>4;
        if(high)s.rc+=RC_FB_FULL/16;
        if(enabled) {
            const int32_t error=s.error+desired-s.rc;
            s.error=std::max(-RC_FB_ERROR_LIMIT,std::min(RC_FB_ERROR_LIMIT,error));
        }
        word=(word<<1)|unsigned(high);
    }
    s.previous=target;
    return word;
}
static uint32_t predictive32(rc_pdm_feedback_t &s,int16_t pcm,bool dither,unsigned attenuation=0) {
    if(dither&&attenuation)return simple32(s,pcm,true,true,attenuation,false);
    if(dither)return full_control(s,pcm);
    uint32_t word;
    rc_pdm_feedback_frame(&s,pcm,&word,32,4,0,0,1);
    return word;
}
static unsigned attenuation_test() {
    rc_pdm_feedback_t fast[2][2][9],reference[2][2][9];
    for(unsigned method=0;method<2;++method)for(unsigned enabled=0;enabled<2;++enabled)
        for(unsigned shift=0;shift<=8;++shift) {
            rc_pdm_feedback_init(&fast[method][enabled][shift],8266);
            reference[method][enabled][shift]=fast[method][enabled][shift];
        }
    unsigned comparisons=0;uint32_t random=8266;
    auto one=[&](int16_t pcm) {
        for(unsigned method=0;method<2;++method)for(unsigned enabled=0;enabled<2;++enabled)
            for(unsigned shift=0;shift<=8;++shift) {
                auto &s=fast[method][enabled][shift],&r=reference[method][enabled][shift];
                auto production=s;
                const auto word=simple32(s,pcm,enabled!=0,true,shift,method!=0);
                check(word==literal(r,pcm,enabled!=0,method!=0,true,shift)&&same(s,r),"attenuation reference mismatch");
                if(method==0&&enabled&&shift==0)
                    check(word==full_control(production,pcm)&&same(s,production),"full amplitude differs from production");
                if(method==0&&enabled&&shift==1)
                    check(word==rc_pdm_feedback_sample(&production,pcm)&&same(s,production),"selected half amplitude differs from production");
                check(s.random==fast[0][0][0].random&&s.previous==fast[0][0][0].previous,"attenuation changes PRNG/interpolation");
                ++comparisons;
            }
    };
    for(int pcm=-32768;pcm<=32767;++pcm)one(int16_t(pcm));
    for(unsigned i=0;i<65536;++i){random=random*1664525U+1013904223U;one(int16_t(random>>16));}
    for(int level:{-32768,32767,0,1,-1})for(unsigned i=0;i<2048;++i)one(int16_t(level));
    return comparisons;
}
static void self_test() {
    rc_pdm_feedback_t prod,model,frozen,off;
    rc_pdm_feedback_init(&prod,0);model=frozen=off=prod;
    auto simpleOn=prod,simpleOff=prod,simpleModelOn=prod,simpleModelOff=prod;
    auto ndOn=prod,ndModel=prod,ndFrozen=prod,ndOff=prod;
    auto ndSimpleOn=prod,ndSimpleOff=prod,ndSimpleModel=prod,ndSimpleOffModel=prod;
    unsigned simpleChanged=0;
    uint32_t random=8266;unsigned count=0,changed=0;
    auto one=[&](int16_t pcm) {
        const uint32_t got=full_control(prod,pcm);
        check(got==literal(model,pcm,true)&&same(prod,model),"enabled differs from production");
        uint32_t frozenWord;rc_feedback_reference_frame(&frozen,pcm,&frozenWord,32,4,0,2,1);
        check(got==frozenWord&&same(prod,frozen),"frozen reference differs");
        auto ignored=off;ignored.error=(count&1)?RC_FB_ERROR_LIMIT:-RC_FB_ERROR_LIMIT;
        const uint32_t without=literal(off,pcm,false);
        check(without==literal(ignored,pcm,false)&&same(off,ignored),"off depends on feedback state");
        check(off.error==0&&off.random==prod.random&&off.previous==prod.previous,"off changes more than feedback");
        const uint32_t son=simple32(simpleOn,pcm,true),soff=simple32(simpleOff,pcm,false);
        check(son==literal(simpleModelOn,pcm,true,true)&&same(simpleOn,simpleModelOn),"Simple on reference");
        auto ignoredSimple=simpleModelOff;ignoredSimple.error=RC_FB_ERROR_LIMIT;
        check(soff==literal(simpleModelOff,pcm,false,true)&&same(simpleOff,simpleModelOff),"Simple off reference");
        check(soff==literal(ignoredSimple,pcm,false,true)&&same(simpleOff,ignoredSimple),"Simple off depends on error");
        check(simpleOn.random==prod.random&&simpleOff.random==prod.random&&simpleOn.previous==prod.previous&&simpleOff.previous==prod.previous,"Simple changes PRNG/interpolation");
        simpleChanged+=son!=soff;
        // Dither removal must remove the PRNG call as well, not only scale its
        // output to zero. All four paths still use exactly the same PCM ramp.
        const auto ndword=predictive32(ndOn,pcm,false);
        check(ndword==literal(ndModel,pcm,true,false,false)&&same(ndOn,ndModel),"no-dither predictive reference");
        uint32_t ndexpected;rc_feedback_reference_frame(&ndFrozen,pcm,&ndexpected,32,4,0,0,1);
        check(ndword==ndexpected&&same(ndOn,ndFrozen),"no-dither frozen reference");
        auto ndIgnored=ndOff;ndIgnored.error=RC_FB_ERROR_LIMIT;ndIgnored.random=1;
        check(literal(ndOff,pcm,false,false,false)==literal(ndIgnored,pcm,false,false,false),"no-dither off error/seed dependence");
        const auto nsword=simple32(ndSimpleOn,pcm,true,false);
        const auto nsoff=simple32(ndSimpleOff,pcm,false,false);
        check(nsword==literal(ndSimpleModel,pcm,true,true,false)&&same(ndSimpleOn,ndSimpleModel),"no-dither Simple on reference");
        check(nsoff==literal(ndSimpleOffModel,pcm,false,true,false)&&same(ndSimpleOff,ndSimpleOffModel),"no-dither Simple off reference");
        for(const auto *state:{&ndOn,&ndOff,&ndSimpleOn,&ndSimpleOff}) {
            check(state->random==RC_FB_DEFAULT_SEED,"disabled dither advances PRNG");
            check(state->previous==prod.previous,"disabled dither changes interpolation");
        }
        changed+=got!=without;++count;
    };
    for(int pcm=-32768;pcm<=32767;++pcm)one(int16_t(pcm));
    for(unsigned i=0;i<65536;++i){random=random*1664525U+1013904223U;one(int16_t(random>>16));}
    for(int level:{-32768,32767,0,1,-1})for(unsigned i=0;i<2048;++i)one(int16_t(level));
    check(changed>0,"feedback ablation has no effect");
    check(simpleChanged>0,"Simple feedback ablation has no effect");
    for(bool enabled:{false,true}) {
        rc_pdm_feedback_t tie;rc_pdm_feedback_init(&tie,1);
        auto rng=tie;const uint32_t r=rc_fb_random(&rng);
        tie.rc+=((int32_t(r&65535U)+int32_t(r>>16))-65535)*256;
        auto expected=tie;const auto word=simple32(tie,0,enabled);
        check((word&0x80000000U)==0,"Simple equality must choose zero");
        check(word==literal(expected,0,enabled,true)&&same(tie,expected),"Simple tie reference");
    }
    const unsigned attenuationComparisons=attenuation_test();
    std::cout<<"{\"pass\":true,\"frames\":"<<count<<",\"different_words\":"<<changed
             <<",\"simple_reference_frames\":"<<count<<",\"simple_different_words\":"<<simpleChanged
             <<",\"no_dither_frames_per_method\":"<<count<<",\"disabled_prng_unchanged\":true"
             <<",\"attenuation_reference_frames\":"<<attenuationComparisons<<",\"attenuation_max_shift\":8"
             <<",\"simple_tie_checks\":2,\"prng_and_interpolation_identical\":true,\"off_error_ignored\":true}\n";
}
int main(int argc,char **argv) {
    try {
        if(argc==2&&std::string(argv[1])=="--self-test"){self_test();return 0;}
        check(argc>=4&&argc<=6,"usage: rcpdm-feedback-ab PCM output-prefix seed [simple] [no-dither|dither-shift=0..8]; or --self-test");
        bool simple=false,dither=true;
        unsigned attenuation=0;bool amplitudeSet=false;
        for(int i=4;i<argc;++i) {
            if(std::string(argv[i])=="simple"&&!simple)simple=true;
            else if(std::string(argv[i])=="no-dither"&&dither&&!amplitudeSet)dither=false;
            else if(std::string(argv[i]).size()==14&&std::string(argv[i]).substr(0,13)=="dither-shift="&&dither&&!amplitudeSet) {
                check(argv[i][13]>='0'&&argv[i][13]<='8',"dither shift must be 0..8");
                attenuation=unsigned(argv[i][13]-'0');amplitudeSet=true;
            }
            else throw std::runtime_error("unknown or repeated option");
        }
        const uint16_t endian=1;check(*reinterpret_cast<const uint8_t*>(&endian)==1,"LE host required");
        std::ifstream input(argv[1],std::ios::binary|std::ios::ate);check(bool(input),"PCM open failed");
        const auto bytes=input.tellg();check(bytes>0&&uint64_t(bytes)%2==0,"invalid PCM length");
        std::vector<int16_t> pcm(size_t(bytes)/2);input.seekg(0);
        check(bool(input.read(reinterpret_cast<char*>(pcm.data()),bytes)),"PCM read failed");
        const auto seed=uint32_t(std::stoul(argv[3]));
        rc_pdm_feedback_t on,reference,off;rc_pdm_feedback_init(&on,seed);reference=off=on;
        auto off32=off;
        const uint32_t initialRandom=on.random;
        std::vector<uint32_t> with(pcm.size()),without(pcm.size());unsigned different=0;
        for(size_t i=0;i<pcm.size();++i) {
            with[i]=simple?simple32(on,pcm[i],true,dither,attenuation):predictive32(on,pcm[i],dither,attenuation);
            check(with[i]==literal(reference,pcm[i],true,simple,dither,attenuation)&&same(on,reference),"enabled reference mismatch");
            without[i]=literal(off,pcm[i],false,simple,dither,attenuation);
            check(without[i]==simple32(off32,pcm[i],false,dither,attenuation,simple)&&same(off,off32),"disabled reference mismatch");
            check(off.random==on.random&&off.previous==on.previous&&off.error==0,"ablation invariants");
            check(dither||on.random==initialRandom,"disabled dither advances PRNG");
            different+=with[i]!=without[i];
        }
        auto write=[&](const char *suffix,const std::vector<uint32_t> &data) {
            std::ofstream output(std::string(argv[2])+suffix,std::ios::binary);
            check(bool(output.write(reinterpret_cast<const char*>(data.data()),std::streamsize(data.size()*4))),"bitstream write failed");
        };
        write(".on.bin",with);write(".off.bin",without);
        std::cout<<"{\"frames\":"<<pcm.size()<<",\"different_words\":"<<different
                 <<",\"on_reference_frames\":"<<pcm.size()<<",\"method\":\""<<(simple?"simple":"predictive")
                 <<"\",\"dither\":"<<(dither?2:0)<<",\"dither_shift\":"<<attenuation
                 <<",\"prng_and_interpolation_identical\":true}"<<'\n';
    } catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 1;}
}
