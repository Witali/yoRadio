/* NEW integrated wrapper gate. The immutable lower-component harness supplies
 * real creator-backed raw handles and exact independent multistream references.
 * Its main is not executed and no byte of that canonical source is changed.
 */
#ifdef DISPATCH_WORD_STORAGE
#include <stddef.h>
static void *dispatch_word_alloc(size_t);
static void dispatch_word_free(void *);
#define OFP_WORD_ALLOC dispatch_word_alloc
#define OFP_WORD_FREE dispatch_word_free
#endif
#define main frozen_family1_component_main
#include "opus_family1_playback_host.c"
#undef main
#include "ogg_playback.h"
#include "ogg_family1_word_allocator.h"

typedef struct {
    ogg_sync_state sync;ogg_stream_state stream;bool stream_ready;
    OpusDecoder *decoder;uint8_t channels;unsigned packets;
    uint8_t *pending;size_t pending_bytes;
    esp_audio_simple_dec_info_t info;
} dispatch_simple;
static unsigned simple_opens,simple_closes,simple_calls,simple_live,dispatch_cases,dispatch_controls,layout_chunks,legacy_chunks;
static unsigned word_storage_controls;
static ogg_playback *current_wrapper;
esp_audio_err_t esp_audio_simple_dec_open(esp_audio_simple_dec_cfg_t *cfg,esp_audio_simple_dec_handle_t *out) {
    assert(cfg && out && !*out && cfg->dec_type==ESP_AUDIO_SIMPLE_DEC_TYPE_OGG && !cfg->dec_cfg && !cfg->cfg_size && !cfg->use_frame_dec && !stats.live);
    dispatch_simple *s=calloc(1,sizeof(*s));assert(s && !ogg_sync_init(&s->sync));*out=s;++simple_opens;++simple_live;return ESP_AUDIO_ERR_OK;
}
esp_audio_err_t esp_audio_simple_dec_get_info(esp_audio_simple_dec_handle_t handle,esp_audio_simple_dec_info_t *info) {
    dispatch_simple *s=handle;assert(s && info && s->decoder);*info=s->info;return ESP_AUDIO_ERR_OK;
}
void esp_audio_simple_dec_close(esp_audio_simple_dec_handle_t handle) {
    dispatch_simple *s=handle;assert(s && simple_live);if(s->decoder)opus_decoder_destroy(s->decoder);if(s->stream_ready)assert(!ogg_stream_clear(&s->stream));
    assert(!ogg_sync_clear(&s->sync));free(s->pending);free(s);--simple_live;++simple_closes;
}
esp_audio_err_t esp_audio_simple_dec_process(esp_audio_simple_dec_handle_t handle,esp_audio_simple_dec_raw_t *raw,esp_audio_simple_dec_out_t *out) {
    dispatch_simple *s=handle;assert(s && raw && out && current_wrapper->input.ready && current_wrapper->input.event.crc_verified && !stats.live);++simple_calls;
    if(s->pending)assert(!raw->len); /* Real creator output was cached; never refeed a page. */
    if(raw->len) {
        char *buffer=ogg_sync_buffer(&s->sync,raw->len);assert(buffer);memcpy(buffer,raw->buffer,raw->len);assert(!ogg_sync_wrote(&s->sync,raw->len));raw->consumed=raw->len;
        for(;;) {
            ogg_page page;int status=ogg_sync_pageout(&s->sync,&page);assert(status>=0);if(!status)break;
            if(!s->stream_ready){assert(!ogg_stream_init(&s->stream,ogg_page_serialno(&page)));s->stream_ready=true;}
            assert(!ogg_stream_pagein(&s->stream,&page));
            for(;;) {
                ogg_packet packet;status=ogg_stream_packetout(&s->stream,&packet);assert(status>=0);if(!status)break;
                if(!s->packets) {
                    assert(packet.bytes>=19 && !memcmp(packet.packet,"OpusHead",8) && packet.packet[18]==0 && packet.packet[9]==2);
                    s->channels=packet.packet[9];int error=0;s->decoder=opus_decoder_create(48000,s->channels,&error);assert(s->decoder && !error);
                    s->info=(esp_audio_simple_dec_info_t){.sample_rate=48000,.channel=s->channels,.bits_per_sample=16};
                } else if(s->packets==1)assert(packet.bytes>=16 && !memcmp(packet.packet,"OpusTags",8));
                else {
                    float *pcm=malloc(5760u*s->channels*sizeof(float));assert(pcm);int frames=opus_decode_float(s->decoder,packet.packet,(int32_t)packet.bytes,pcm,5760,0);assert(frames>0 && frames<=5760);
                    size_t before=s->pending_bytes,bytes=(size_t)frames*s->channels*2u;s->pending=realloc(s->pending,before+bytes);assert(s->pending);
                    for(size_t i=0;i<(size_t)frames*s->channels;++i)put16(s->pending+before+i*2u,rounded(pcm[i]));
                    s->pending_bytes+=bytes;free(pcm);
                }
                ++s->packets;
            }
        }
    }
    if(s->pending_bytes>out->len){out->needed_size=(uint32_t)s->pending_bytes;return ESP_AUDIO_ERR_BUFF_NOT_ENOUGH;}
    if(s->pending_bytes){memcpy(out->buffer,s->pending,s->pending_bytes);out->decoded_size=(uint32_t)s->pending_bytes;free(s->pending);s->pending=NULL;s->pending_bytes=0;}
    return ESP_AUDIO_ERR_OK;
}
typedef struct {
    ogg_playback *wrapper;const reference *reference;uint32_t generation;int16_t gain;size_t emitted;
    bool expect_layout,cancelled,close_witness,cancel_at_close;
    unsigned outputs,yields,output_fail,cancel_output,cancel_yield;
#ifdef DISPATCH_WORD_STORAGE
    unsigned fallback_word_planes,fallback_word_witnesses;
    size_t fallback_word_capacity;
#endif
} dispatch_context;
static bool dispatch_cancelled(void *opaque){return ((dispatch_context *)opaque)->cancelled;}
static void dispatch_yield(void *opaque) {
    dispatch_context *c=opaque;++c->yields;
    if(c->cancel_yield==c->yields)c->cancelled=true;
    opus_family1_playback *f=&c->wrapper->family1;
    if(f->phase==OFP_EOS_CLOSE && ofd_has_handles(&f->decoder)) {
        assert(c->wrapper->input.ready && c->wrapper->input.event.flags&OOPT_LINK_END && !c->wrapper->input.timeline.seen_eos &&
            dispatch_planes_present(f) && f->packets.prefix && opk_page_exhausted(&f->packets) && f->trim.raw_position==f->trim.total && stats.live==1);
        bool found=false;for(unsigned i=0;i<8;++i)if(f->decoder.handle[i]) {cfg_stable(f->decoder.handle[i]);found=true;}assert(found);c->close_witness=true;
        if(c->cancel_at_close)c->cancelled=true;
    }
}
static bool dispatch_pcm(dispatch_context *c,const esp_audio_simple_dec_info_t *info,const uint8_t *pcm,size_t bytes,int16_t gain,bool layout) {
    const reference *r=c->reference;assert(c->wrapper->input.ready && c->wrapper->input.event.crc_verified && c->wrapper->generation==c->generation &&
        info->sample_rate==48000 && info->channel==r->channels && info->bits_per_sample==16 && gain==c->gain && layout==c->expect_layout && bytes && bytes%(r->channels*2u)==0);
    size_t frames=bytes/(r->channels*2u);assert(c->emitted<=r->logical_frames && frames<=r->logical_frames-c->emitted &&
        !memcmp(pcm,r->pcm+(r->pre_skip+c->emitted)*r->channels*2u,bytes));
    if(layout) {
        opus_family1_playback *f=&c->wrapper->family1;assert(bytes<=128u*r->channels*2u && f->plan.header_gain_q8==gain && !simple_live);
        if(f->plan.needed)assert(pcm==f->decoder.scratch && f->decoder.capacity>=bytes && stats.live);else assert(pcm==ofp_zero_chunk && !stats.live);
#ifdef DISPATCH_WORD_STORAGE
        if(c->fallback_word_planes) {
            assert(f->word_mode && !f->planes && f->plane_count==c->fallback_word_planes && f->word_capacity==c->fallback_word_capacity &&
                dispatch_words.live==c->fallback_word_planes && plane_alloc.calls==1 && plane_alloc.refuse==1 && !plane_alloc.pointer);
            ++c->fallback_word_witnesses;
        }
#endif
    } else assert(simple_live && !stats.live);
    ++c->outputs;
    if(c->outputs==c->cancel_output){c->cancelled=true;return false;}
    if(c->outputs==c->output_fail)return false;
    c->emitted+=frames;compared_samples+=bytes/2u;if(layout)++layout_chunks;else ++legacy_chunks;return true;
}
static bool dispatch_legacy_output(void *opaque,const esp_audio_simple_dec_info_t *info,const uint8_t *pcm,size_t bytes,int16_t gain) {return dispatch_pcm(opaque,info,pcm,bytes,gain,false);}
static bool dispatch_layout_output(void *opaque,const esp_audio_simple_dec_info_t *info,const uint8_t *pcm,size_t bytes,int16_t gain,pcm_channel_layout layout) {
    assert(layout==PCM_CHANNEL_LAYOUT_VORBIS);return dispatch_pcm(opaque,info,pcm,bytes,gain,true);
}
static ogg_playback_callbacks dispatch_callbacks(dispatch_context *c){return (ogg_playback_callbacks){dispatch_cancelled,dispatch_legacy_output,dispatch_yield,c,dispatch_layout_output};}
static physical dispatch_family0(const corpus *source,unsigned serial,int16_t gain) {
    assert(source->channels==2 && source->streams==1 && source->coupled==1);physical p={.serial=serial,.head_bytes=19,.tags_bytes=16};p.head=calloc(19,1);p.tags=calloc(16,1);assert(p.head && p.tags);
    memcpy(p.head,source->head,19);p.head[18]=0;put16(p.head+16,gain);memcpy(p.tags,"OpusTags",8);uint8_t table[255];unsigned n=laces(table,19);page(&p,2,0,table,n,p.head,19);n=laces(table,16);page(&p,0,0,table,n,p.tags,16);uint64_t raw=0;
    for(unsigned i=0;i<source->count;++i){int frames=opus_packet_get_nb_samples(source->packet[i],(int32_t)source->bytes[i],48000);assert(frames>0);raw+=(unsigned)frames;bool final=i+1==source->count;n=laces(table,source->bytes[i]);page(&p,final?4u:0u,final?source->pre_skip+source->logical:raw,table,n,source->packet[i],source->bytes[i]);}
    return p;
}
typedef struct {ogg_playback wrapper;esp_audio_simple_dec_handle_t decoder;uint8_t *pcm;size_t capacity;decoder_pending_input_t pending;} dispatch_player;
static void dispatch_init(dispatch_player *p) {
    assert(!simple_live);assert(ogp_reset(&p->wrapper,42));dispatch_word_reset();reset_backend(&p->wrapper.family1);current_wrapper=&p->wrapper;simple_opens=simple_closes=simple_calls=0;
}
static ogg_playback_status dispatch_feed(dispatch_player *p,dispatch_context *c,const physical *bytes,size_t chunk,int32_t *cause) {
    ogg_playback_callbacks cb=dispatch_callbacks(c);ogg_playback_status status=OGP_OK;
    for(size_t at=0;at<bytes->size && status==OGP_OK;) {size_t n=bytes->size-at;if(chunk && n>chunk)n=chunk;status=ogp_feed(&p->wrapper,bytes->data+at,n,false,&p->decoder,&p->pcm,&p->capacity,&p->pending,&cb,cause);at+=n;}
    if(status==OGP_OK)status=ogp_feed(&p->wrapper,NULL,0,true,&p->decoder,&p->pcm,&p->capacity,&p->pending,&cb,cause);
    return status;
}
static void dispatch_clean(dispatch_player *p) {
    if(p->decoder)esp_audio_simple_dec_close(p->decoder);
    p->decoder=NULL;free(p->pcm);p->pcm=NULL;p->capacity=0;decoder_pending_input_clear(&p->pending);assert(ogp_reset(&p->wrapper,43) && !ogp_has_input(&p->wrapper) && !simple_live && !stats.live && stats.created==stats.destroyed &&
        !plane_alloc.pointer && !scratch_alloc.pointer && !packet_alloc.pointer && dispatch_word_empty());
}
static void dispatch_positive(const corpus *source,const reference *ref,unsigned style,size_t chunk,bool cached,int16_t gain,bool prepared) {
    physical bytes=make(source,style,source->channels+200u,false,false);put16(bytes.head+16,gain);
    size_t header=27u+bytes.data[26],size=header+bytes.head_bytes;memcpy(bytes.data+header,bytes.head,bytes.head_bytes);ogg_page fixed={.header=bytes.data,.header_len=(long)header,.body=bytes.data+header,.body_len=(long)bytes.head_bytes};ogg_page_checksum_set(&fixed);assert(size<=bytes.size);creator_walk(&bytes,source);
    dispatch_player p={0};dispatch_init(&p);stats.cache_full=cached;
    if(prepared) {esp_audio_simple_dec_cfg_t cfg={.dec_type=ESP_AUDIO_SIMPLE_DEC_TYPE_OGG};assert(esp_audio_simple_dec_open(&cfg,&p.decoder)==ESP_AUDIO_ERR_OK);p.capacity=12288;p.pcm=malloc(p.capacity);assert(p.pcm);}
    dispatch_context c={.wrapper=&p.wrapper,.reference=ref,.generation=42,.gain=gain,.expect_layout=true};int32_t cause=0;assert(dispatch_feed(&p,&c,&bytes,chunk,&cause)==OGP_OK &&
        c.emitted==ref->logical_frames && !ogp_has_input(&p.wrapper) && !p.decoder && !p.pcm && !p.capacity && simple_opens==simple_closes && simple_opens==(unsigned)prepared && !stats.live);
    dispatch_clean(&p);physical_free(&bytes);++dispatch_cases;
    printf("{\"kind\":\"family1\",\"case\":%u,\"channels\":%u,\"style\":%u,\"chunk\":%zu,\"cached\":%u,\"gain\":%d,\"prepared_simple\":%u,\"frames\":%zu,\"raw_created\":%u,\"raw_destroyed\":%u,\"simple_opens\":%u,\"simple_closes\":%u,\"passed\":true}\n",
        dispatch_cases,source->channels,style,chunk,(unsigned)cached,(int)gain,(unsigned)prepared,c.emitted,stats.created,stats.destroyed,simple_opens,simple_closes);
}
static void dispatch_chain(const corpus *sources,const reference *refs,size_t chunk,bool legacy_first) {
    dispatch_player p={0};dispatch_init(&p);
    for(unsigned link=0;link<3;++link) {
        bool legacy=legacy_first?link!=1:link==1;unsigned index=legacy?3:link==0?0:2;const corpus *source=sources+index;const reference *ref=refs+index;int16_t gain=link==0?-1536:link==1?0:1536;
        physical bytes=legacy?dispatch_family0(source,300u+link,gain):make(source,1,300u+link,false,false);
        if(!legacy){put16(bytes.head+16,gain);size_t head=27u+bytes.data[26];memcpy(bytes.data+head,bytes.head,bytes.head_bytes);ogg_page fixed={bytes.data,(long)head,bytes.data+head,(long)bytes.head_bytes};ogg_page_checksum_set(&fixed);}
        creator_walk(&bytes,source);dispatch_context c={.wrapper=&p.wrapper,.reference=ref,.generation=42,.gain=gain,.expect_layout=!legacy};int32_t cause=0;
        assert(dispatch_feed(&p,&c,&bytes,chunk,&cause)==OGP_OK && c.emitted==ref->logical_frames && !p.decoder && !ogp_has_input(&p.wrapper) && !stats.live && !simple_live);
        physical_free(&bytes);
    }
    assert(simple_opens==simple_closes && simple_opens==(legacy_first?2u:1u));dispatch_clean(&p);++dispatch_cases;
    printf("{\"kind\":\"chain\",\"case\":%u,\"chunk\":%zu,\"legacy_first\":%u,\"links\":3,\"simple_opens\":%u,\"simple_closes\":%u,\"passed\":true}\n",dispatch_cases,chunk,(unsigned)legacy_first,simple_opens,simple_closes);
}
static void dispatch_close_control(const corpus *source,const reference *ref,unsigned mode,bool word_control) {
    physical bytes=make(source,1,401,false,false);creator_walk(&bytes,source);dispatch_player p={0};dispatch_init(&p);stats.close_refuse=2;
    dispatch_context c={.wrapper=&p.wrapper,.reference=ref,.generation=42,.gain=1536,.expect_layout=true,.cancel_at_close=mode==1};ogg_playback_callbacks cb=dispatch_callbacks(&c);if(mode==2)cb.yield=NULL;
    int32_t cause=0;ogg_playback_status status=ogp_feed(&p.wrapper,bytes.data,bytes.size,true,&p.decoder,&p.pcm,&p.capacity,&p.pending,&cb,&cause);
    if(!mode) {
        assert(status==OGP_OK && c.close_witness && c.emitted==ref->logical_frames && stats.closes==source->streams+1u && !stats.live && !p.wrapper.input.ready && p.wrapper.input.timeline.seen_eos);
    } else {
        assert(status==(mode==1?OGP_CANCELLED:OGP_DECODER) && c.emitted==ref->logical_frames && p.wrapper.input.ready && p.wrapper.input.event.flags&OOPT_LINK_END &&
            !p.wrapper.input.timeline.seen_eos && stats.live==1 && dispatch_planes_present(&p.wrapper.family1) && p.wrapper.family1.packets.prefix && p.wrapper.generation==42);
        dispatch_plane_snapshot planes=dispatch_snapshot(&p.wrapper.family1);
        uint8_t *page=p.wrapper.input.page,*prefix=p.wrapper.family1.packets.prefix;size_t held=p.wrapper.input.size;uint64_t token=p.wrapper.input.event.token;unsigned published=c.outputs;
        uint8_t *saved=malloc(held);assert(saved);memcpy(saved,page,held);stats.close_refuse=stats.closes+1u;
        assert(!ogp_reset(&p.wrapper,77) && p.wrapper.generation==42 && p.wrapper.input.page==page && p.wrapper.input.size==held && p.wrapper.input.ready && p.wrapper.input.event.token==token &&
            p.wrapper.family1.packets.prefix==prefix && !memcmp(page,saved,held) && stats.live==1 && c.outputs==published);
        dispatch_snapshot_equal(&p.wrapper.family1,&planes);
        for(unsigned i=0;i<8;++i)if(p.wrapper.family1.decoder.handle[i])cfg_stable(p.wrapper.family1.decoder.handle[i]);
        stats.close_refuse=0;assert(ogp_reset(&p.wrapper,43) && !stats.live && !p.wrapper.input.page && !dispatch_planes_present(&p.wrapper.family1) && !p.wrapper.family1.packets.prefix && p.wrapper.generation==43 && c.outputs==published);free(saved);
    }
    dispatch_clean(&p);physical_free(&bytes);if(word_control)++word_storage_controls;else ++dispatch_controls;
    printf("{\"kind\":\"%sclose-control\",\"mode\":%u,\"status\":%d,\"close_witness\":%u,\"raw_created\":%u,\"raw_destroyed\":%u,\"close_calls\":%u,\"published_frames\":%zu,\"passed\":true}\n",word_control?"word-":"",mode,(int)status,(unsigned)c.close_witness,stats.created,stats.destroyed,stats.closes,c.emitted);
}
static void dispatch_failure(const corpus *source,const reference *ref,unsigned mode) {
    physical bytes=make(source,1,411,false,false);dispatch_player p={0};dispatch_init(&p);dispatch_context c={.wrapper=&p.wrapper,.reference=ref,.generation=42,.gain=1536,.expect_layout=true};ogg_playback_callbacks cb=dispatch_callbacks(&c);ogg_playback_status expected=OGP_OK;
    if(mode==0){c.output_fail=3;expected=OGP_OUTPUT;}
    if(mode==1){c.cancel_output=3;expected=OGP_CANCELLED;}
    if(mode==2){c.cancel_yield=1;expected=OGP_CANCELLED;}
    if(mode==3){stats.open_refuse=2;expected=OGP_MEMORY;}
    if(mode==4){plane_alloc.refuse=1;expected=OGP_MEMORY;
#ifdef DISPATCH_WORD_STORAGE
        /* With a word fallback, a fatal allocation control must exhaust both
         * independent HOST allocators. The byte-only baseline is unchanged. */
        dispatch_words.refuse=1;
#endif
    }
    if(mode==5){scratch_alloc.refuse=1;expected=OGP_MEMORY;}
    if(mode==6){cb.output_layout=NULL;expected=OGP_INFO;}
    if(mode==7) {
        size_t at=0;for(unsigned page_id=0;page_id<4;++page_id){unsigned count=bytes.data[at+26];size_t n=27u+count;for(unsigned i=0;i<count;++i)n+=bytes.data[at+27+i];at+=n;}
        /* First packet's completed page follows HEAD/TAGS/partial/nil. */
        bytes.data[at+22]^=1;expected=OGP_CONTAINER;
    }
    int32_t cause=0;ogg_playback_status status=ogp_feed(&p.wrapper,bytes.data,bytes.size,true,&p.decoder,&p.pcm,&p.capacity,&p.pending,&cb,&cause);assert(status==expected && !simple_opens);
    if(mode<=1)assert(c.outputs==3 && c.emitted==256 && !stats.live && p.wrapper.input.ready && p.wrapper.family1.trim.raw_position==960);
    if(mode==2)assert(!c.outputs && !stats.live && p.wrapper.input.ready);
    if(mode==3)assert(stats.opens==2 && stats.created==1 && stats.destroyed==1 && !stats.live && !c.outputs && p.wrapper.input.ready);
    if(mode==4 || mode==5)assert(!stats.syntheses && !stats.live && !c.outputs && p.wrapper.input.ready && cause==(mode==4?15360:11520));
#ifdef DISPATCH_WORD_STORAGE
    if(mode==4)assert(dispatch_words.calls==1 && dispatch_word_empty());
#endif
    if(mode==6)assert(!stats.opens && !c.outputs && p.wrapper.input.ready && p.wrapper.input.event.flags&OOPT_HEAD);
    if(mode==7)assert(!stats.decodes && !c.outputs && !p.wrapper.input.ready && p.wrapper.family1.packets.prefix_size==255 && stats.live==source->streams);
    dispatch_clean(&p);physical_free(&bytes);++dispatch_controls;
    printf("{\"kind\":\"failure-control\",\"mode\":%u,\"status\":%d,\"expected\":%d,\"cause\":%" PRId32 ",\"published_frames\":%zu,\"passed\":true}\n",mode,(int)status,(int)expected,cause,c.emitted);
}
static void dispatch_bad_tags(const corpus *source,const reference *ref) {
    physical bytes=make(source,1,419,true,false);put32(bytes.tags+8,UINT32_MAX);replace_tags(&bytes);creator_walk(&bytes,source);dispatch_player p={0};dispatch_init(&p);
    dispatch_context c={.wrapper=&p.wrapper,.reference=ref,.generation=42,.gain=1536,.expect_layout=true};int32_t cause=0;
    assert(dispatch_feed(&p,&c,&bytes,257,&cause)==OGP_CONTAINER && cause==OTS_INVALID && !stats.opens && !simple_opens && !c.outputs && p.wrapper.input.ready && p.wrapper.family1.tags.parser.bytes==65025);
    dispatch_clean(&p);physical_free(&bytes);++dispatch_controls;
    printf("{\"kind\":\"tag-control\",\"public_raw_opens\":%u,\"public_simple_opens\":%u,\"cause\":%" PRId32 ",\"passed\":true}\n",stats.opens,simple_opens,cause);
}
#include "ogg_family1_word_controls.h"
int main(int argc,char **argv) {
    assert(argc==6);corpus sources[5];reference refs[5];for(unsigned i=0;i<5;++i){sources[i]=load(argv[i+1]);refs[i]=creator_reference(sources+i);}
    for(unsigned fixture=0;fixture<3;++fixture)for(unsigned style=0;style<3;++style)for(unsigned feed=0;feed<2;++feed)dispatch_positive(sources+fixture,refs+fixture,style,feed?257:0,false,1536,false);
    const uint8_t maps[8][8]={{7},{6,0},{5,5,255},{7,0,6,1},{255,255,255,255,255},{0,1,2,3,4,5},{7,7,6,5,0,255,1},{0,7,0,7,255,5,6,255}};
    for(unsigned channels=1;channels<=8;++channels){corpus v=variant(sources+2,channels,maps[channels-1]);reference r=creator_reference(&v);dispatch_positive(&v,&r,channels%3u,257,false,1536,false);free(r.pcm);}
    for(unsigned fixture=3;fixture<5;++fixture)for(unsigned style=0;style<2;++style)for(unsigned cached=0;cached<2;++cached)dispatch_positive(sources+fixture,refs+fixture,style,257,cached!=0,1536,false);
    const int16_t gains[4]={-1536,0,-32768,32767};for(unsigned i=0;i<4;++i)dispatch_positive(sources,refs,1,257,false,gains[i],false);
    dispatch_positive(sources+2,refs+2,1,257,false,1536,true);
    for(unsigned feed=0;feed<2;++feed)for(unsigned order=0;order<2;++order)dispatch_chain(sources,refs,feed?257:0,order!=0);
    for(unsigned mode=0;mode<3;++mode)dispatch_close_control(sources+2,refs+2,mode,false);
    for(unsigned mode=0;mode<8;++mode)dispatch_failure(sources+2,refs+2,mode);
    dispatch_bad_tags(sources+2,refs+2);
    assert(dispatch_cases==43 && dispatch_controls==12 && compared_samples==UINT64_C(12983296));
    uint64_t base_samples=compared_samples;
    unsigned base_layout_chunks=layout_chunks,base_legacy_chunks=legacy_chunks;
    dispatch_word_controls(sources+4,refs+4,sources+2,refs+2);
    for(unsigned i=0;i<5;++i){free(refs[i].pcm);corpus_free(sources+i);}
    assert(!stats.live && !simple_live && !plane_alloc.pointer && !scratch_alloc.pointer && !packet_alloc.pointer);
    printf("{\"suite\":\"ogg-family1-dispatch\",\"passed\":true,\"positive_schedules\":%u,\"host_controls\":%u,\"creator_pcm_samples_exact\":%" PRIu64
        ",\"family1_output_chunks\":%u,\"legacy_output_chunks\":%u,\"gain_layout_forwarded\":true,\"close_retry_preserves_cfg_page_planes\":true,\"native_oom_qualified\":false,\"production_task_executed\":false}\n",
        dispatch_cases,dispatch_controls,base_samples,base_layout_chunks,base_legacy_chunks);
    printf("{\"suite\":\"ogg-family1-word-storage\",\"passed\":true,\"enabled\":%u,\"controls\":%u,\"creator_pcm_samples_exact\":%" PRIu64 ",\"peak_live_planes\":%u,\"allocation_attempts\":%u,\"native_oom_qualified\":false,\"native_word_access_qualified\":false}\n",dispatch_word_enabled(),word_storage_controls,compared_samples-base_samples,dispatch_word_peak(),dispatch_word_attempts());return 0;
}
