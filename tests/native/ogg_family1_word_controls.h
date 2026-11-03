#ifndef DISPATCH_WORD_CONTROLS_H
#define DISPATCH_WORD_CONTROLS_H
#ifdef DISPATCH_WORD_STORAGE
static void word_owner_init(opus_family1_playback *s) {
    dispatch_word_reset();reset_backend(s);s->generation=42;s->plane_count=8;
    uint8_t head[29]={0};const uint8_t map[8]={0,6,1,2,3,4,5,7};
    memcpy(head,"OpusHead",8);head[8]=1;head[9]=8;put16(head+10,312);put32(head+12,44100);put16(head+16,1536);head[18]=1;head[19]=5;head[20]=3;memcpy(head+21,map,8);
    assert(of1_plan_header(head,sizeof(head),&s->plan)==OF1_OK && s->plan.needed==5);
    s->decoder.plan=s->plan;
    for(unsigned speaker=0;speaker<8;++speaker) {
        s->plane_for_speaker[speaker]=(uint8_t)speaker;s->plane_slot[speaker]=s->plan.speaker_slot[speaker];s->plane_channel[speaker]=s->plan.speaker_channel[speaker];
    }
}
static bool word_stage(opus_family1_playback *s,uint16_t samples) {
    dispatch_context context={0};ofp_callbacks cb={.cancelled=dispatch_cancelled,.context=&context};ofp_sink_context sink={s,&cb,OFP_OK,0};
    bool result=ofp_sink_begin(&sink,&s->decoder.plan,42,samples);
    if(result)assert(sink.error==OFP_OK && s->stage_active && s->samples==samples);
    else assert(sink.error==OFP_MEMORY && sink.detail==(int)((size_t)samples*16u) && !s->stage_active);
    return result;
}
static void word_abort(opus_family1_playback *s) {ofp_sink_context sink={.s=s};ofp_sink_abort(&sink);}
static void word_owner_clean(opus_family1_playback *s) {
    word_abort(s);ofp_free_planes(s);assert(dispatch_word_empty() && !plane_alloc.pointer && !s->capacity && !s->word_capacity && !s->word_mode);
    for(unsigned plane=0;plane<8;++plane)assert(!s->word_planes[plane]);
}
static uint32_t word_pattern(unsigned plane,size_t word) {
    return UINT32_C(0x8f12e6a3) ^ ((uint32_t)word*UINT32_C(40503)+(uint32_t)plane*UINT32_C(7919));
}
static void word_pattern_fill(opus_family1_playback *s) {
    for(unsigned plane=0;plane<8;++plane)for(size_t word=0;word<s->word_capacity/4u;++word)s->word_planes[plane][word]=word_pattern(plane,word);
}
static void word_pattern_verify(const opus_family1_playback *s) {
    for(unsigned plane=0;plane<8;++plane)for(size_t word=0;word<s->word_capacity/4u;++word)assert(s->word_planes[plane][word]==word_pattern(plane,word));
}
static void word_storage_record(const char *name,unsigned ordinal) {
    ++word_storage_controls;printf("{\"kind\":\"word-storage-control\",\"name\":\"%s\",\"ordinal\":%u,\"passed\":true,\"native_oom_qualified\":false}\n",name,ordinal);
}
static void word_reserve_refusal(unsigned mode,unsigned ordinal) {
    opus_family1_playback s={0};word_owner_init(&s);
    if(mode==1) {
        assert(word_stage(&s,960) && !s.word_mode && s.planes && s.capacity==15360);
        for(size_t byte=0;byte<s.capacity;++byte)s.planes[byte]=(uint8_t)(byte*73u+5u);
        word_abort(&s);
    }
    if(mode==2) {
        assert(word_stage(&s,1921) && s.word_mode && s.word_capacity==3844 && dispatch_words.live==8);
        word_pattern_fill(&s);word_abort(&s);
    }
    dispatch_plane_snapshot previous=dispatch_snapshot(&s);unsigned live=dispatch_words.live,calls=dispatch_words.calls,frees=dispatch_words.frees;
    dispatch_words.refuse=calls+ordinal;assert(!word_stage(&s,5760));
    assert(dispatch_words.calls==calls+ordinal && dispatch_words.frees==frees+ordinal-1u && dispatch_words.live==live);
    dispatch_snapshot_equal(&s,&previous);
    if(mode==1)for(size_t byte=0;byte<s.capacity;++byte)assert(s.planes[byte]==(uint8_t)(byte*73u+5u));
    if(mode==2)word_pattern_verify(&s);
    word_owner_clean(&s);word_storage_record(mode==0?"initial-refusal":mode==1?"byte-upgrade-refusal":"word-growth-refusal",ordinal);
}
static void word_alignment_refusal(void) {
    opus_family1_playback s={0};word_owner_init(&s);dispatch_words.misalign=4;
    assert(!word_stage(&s,5760) && dispatch_words.calls==4 && dispatch_words.frees==4 && !dispatch_words.live && !s.planes && !s.word_mode);
    word_owner_clean(&s);word_storage_record("unaligned-candidate-refusal",4);
}
static void word_successful_replacement(void) {
    opus_family1_playback s={0};word_owner_init(&s);assert(word_stage(&s,960) && s.planes && !s.word_mode);word_abort(&s);
    assert(word_stage(&s,1921) && !s.planes && !plane_alloc.pointer && s.word_mode && dispatch_words.live==8 && s.capacity==30752);
    word_pattern_fill(&s);word_abort(&s);dispatch_plane_snapshot previous=dispatch_snapshot(&s);unsigned calls=dispatch_words.calls;
    assert(word_stage(&s,1921) && dispatch_words.calls==calls);dispatch_snapshot_equal(&s,&previous);word_pattern_verify(&s);word_abort(&s);
    assert(word_stage(&s,5760) && s.word_capacity==11520 && s.capacity==92160 && dispatch_words.live==8 && dispatch_words.calls==calls+8);
    for(unsigned plane=0;plane<8;++plane) {
        assert(s.word_planes[plane]!=previous.words[plane]);
        for(size_t word=0;word<s.word_capacity/4u;++word)assert(s.word_planes[plane][word]==0);
    }
    assert(word_peak_live==16);word_owner_clean(&s);word_storage_record("atomic-replacement-reuse-and-clear",0);
}
static uint16_t gather_expected(unsigned plane,size_t sample) {
    return (uint16_t)(UINT32_C(0x8000)^((uint32_t)plane*7919u+(uint32_t)sample*97u));
}
static void word_gather_contract(void) {
    opus_family1_playback s={0};word_owner_init(&s);assert(word_stage(&s,5760));
    const uint8_t mapping[8]={7,0,7,OF1_SILENCE,1,OF1_SILENCE,6,1};memcpy(s.plane_for_speaker,mapping,sizeof(mapping));
    for(unsigned plane=0;plane<8;++plane)for(size_t sample=0;sample<s.samples;++sample)pcm_word_plane_store(s.word_planes[plane],sample,gather_expected(plane,sample));
    uint8_t output[129u*16u+2u];memset(output,0x6d,sizeof(output));size_t written=0;
    assert(ofp_gather_word_planes(&s,3,129,output+1,sizeof(output)-2u,&written) && written==129u*16u && output[0]==0x6d && output[sizeof(output)-1]==0x6d);
    for(size_t frame=0;frame<129;++frame)for(unsigned speaker=0;speaker<8;++speaker) {
        uint16_t expected=mapping[speaker]==OF1_SILENCE?0:gather_expected(mapping[speaker],frame+3);
        size_t at=1u+(frame*8u+speaker)*2u;
        assert(output[at]==(uint8_t)expected && output[at+1]==(uint8_t)(expected>>8));
    }
    written=17;assert(!ofp_gather_word_planes(&s,5761,1,output,16,&written) && written==17);
    assert(!ofp_gather_word_planes(&s,5759,2,output,32,&written) && written==17);
    assert(!ofp_gather_word_planes(&s,3,129,output+1,129u*16u-1u,&written) && written==17);
    assert(!ofp_gather_word_planes(&s,0,1,NULL,16,&written) && written==17);
    word_owner_clean(&s);word_storage_record("odd-offset-unaligned-DRAM-alias-silence-gather",0);
}
static void word_creator_odd_trim(const corpus *source) {
    const uint8_t map[8]={0,7,0,7,OF1_SILENCE,5,6,OF1_SILENCE};
    corpus v=variant(source,8,map);++v.pre_skip;--v.logical;put16(v.head+10,(int16_t)v.pre_skip);reference ref=creator_reference(&v);
    assert(v.pre_skip&1u);physical bytes=make(&v,1,431,false,false);creator_walk(&bytes,&v);dispatch_player p={0};dispatch_init(&p);
    dispatch_context c={.wrapper=&p.wrapper,.reference=&ref,.generation=42,.gain=1536,.expect_layout=true};int32_t cause=0;
    assert(dispatch_feed(&p,&c,&bytes,257,&cause)==OGP_OK && c.emitted==ref.logical_frames && !ogp_has_input(&p.wrapper) && !stats.live && dispatch_word_empty());
    assert(dispatch_words.calls==4);dispatch_clean(&p);physical_free(&bytes);free(ref.pcm);word_storage_record("complete-creator-odd-pre-skip-duplicate-silence",v.pre_skip);
}
static void word_wrapper_allocation_refusal(const corpus *source,const reference *ref,unsigned ordinal) {
    physical bytes=make(source,1,443u+ordinal,false,false);creator_walk(&bytes,source);dispatch_player p={0};dispatch_init(&p);dispatch_words.refuse=ordinal;
    dispatch_context c={.wrapper=&p.wrapper,.reference=ref,.generation=42,.gain=1536,.expect_layout=true};int32_t cause=0;
    assert(dispatch_feed(&p,&c,&bytes,257,&cause)==OGP_MEMORY && cause==92160 && !c.outputs && !c.emitted && !simple_opens);
    assert(stats.created==source->streams && stats.destroyed==stats.created && !stats.live && !stats.decodes && !stats.syntheses);
    assert(dispatch_words.calls==ordinal && dispatch_words.frees==ordinal-1u && dispatch_word_empty() && !scratch_alloc.pointer && !plane_alloc.pointer);
    assert(p.wrapper.input.ready && !p.wrapper.input.timeline.seen_eos && p.wrapper.generation==42);
    dispatch_clean(&p);physical_free(&bytes);word_storage_record("wrapper-allocation-error-and-real-handle-cleanup",ordinal);
}
static void dispatch_word_controls(const corpus *source,const reference *ref) {
    const unsigned ordinals[3]={1,4,8};
    for(unsigned mode=0;mode<3;++mode)for(unsigned index=0;index<3;++index)word_reserve_refusal(mode,ordinals[index]);
    word_alignment_refusal();word_successful_replacement();word_gather_contract();word_creator_odd_trim(source);
    for(unsigned mode=0;mode<3;++mode)dispatch_close_control(source,ref,mode,true);
    for(unsigned index=0;index<3;++index)word_wrapper_allocation_refusal(source,ref,ordinals[index]);
    assert(word_storage_controls==19 && word_peak_live==16 && dispatch_word_empty());
}
#else
static void dispatch_word_controls(const corpus *source,const reference *ref) {(void)source;(void)ref;}
#endif
#endif
