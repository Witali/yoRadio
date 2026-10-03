// Emulator-only address/lifetime oracle. Never linked into production images.
// Expected addresses follow native setters, independently of binary patches.
#include "aac_pointer_audit.h"
#include "aac_analysis_core.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_partition.h"
#include "native_aac_decoder.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <inttypes.h>
#include <stdlib.h>

enum {
    MAX_LIVE_ALLOCATIONS=96, HYBRID_BANDS=3, HYBRID_HISTORY=12,
    HYBRID_SCRATCH=8, HYBRID_OUTPUTS=10, PS_MAIN_BANDS=61,
    PS_SHORT_BANDS=20, PS_LONG_BANDS=12, PS_LONG_DELAY=14,
    PS_SERIAL_LINKS=3, QMF_ROWS=6+32, QMF_ROW_WORDS=64, QMF_HIGH_WORDS=QMF_ROWS*48,
    // Pinned native sbr_applied/sbr_dec scratch bindings, in int32 words.
    PS_HIGH_IMAG_WORD_OFFSET=920, PS_QMF_IMAG_WORD_OFFSET=83,
    NATIVE_OUTPUT_BLOCK_BYTES=4096,
};
typedef struct {
    void *pointer;
    size_t bytes;
    aac_compact_owner_t *context;
} allocation_t;
static allocation_t allocations[MAX_LIVE_ALLOCATIONS];
static unsigned checks, core_calls, frame_calls, ps_calls, smoothing_calls;
static unsigned allocations_seen, frees_seen, negative_cases;
static unsigned envelope_calls, reset_calls, io_calls, copy_calls;
static bool quiet;
typedef struct {
    aac_compact_owner_t *state;
    const void *input, *output;
    size_t input_bytes, output_bytes;
} io_t;
static io_t io_scopes[4];

static bool check(bool condition,const char *field,const void *actual,const void *expected) {
    ++checks;
    if(!condition && !quiet)
        ESP_LOGE("aac_pointer", "field=%s actual=%p expected=%p",field,actual,expected);
    return condition;
}
#define EXACT(p,e) do { if(!check((const void *)(p)==(const void *)(e),#p,p,e))return false; } while(0)
#define REQUIRE(c) do { if(!check((c),#c,NULL,NULL))return false; } while(0)

static bool span(const void *p,size_t bytes,const void *base,size_t extent,size_t alignment) {
    uintptr_t address=(uintptr_t)p, start=(uintptr_t)base;
    return p && base && !(address%alignment) && address>=start &&
           address-start<=extent && bytes<=extent-(address-start);
}
static bool live(const void *p,size_t bytes,aac_compact_owner_t *state) {
    for(unsigned i=0;i<MAX_LIVE_ALLOCATIONS;++i)
        if(allocations[i].pointer==p)
            return check(allocations[i].context==state && allocations[i].bytes==bytes,
                         "live allocation size/context",p,state);
    return check(false,"live allocation",p,NULL);
}
void aac_pointer_audit_allocate(void *p,size_t bytes,aac_compact_owner_t *state) {
    if(!p || !state)return;
    for(unsigned i=0;i<MAX_LIVE_ALLOCATIONS;++i)assert(allocations[i].pointer!=p);
    for(unsigned i=0;i<MAX_LIVE_ALLOCATIONS;++i)if(!allocations[i].pointer) {
        allocations[i]=(allocation_t){p,bytes,state};++allocations_seen;return;
    }
    assert(!"AAC pointer audit registry exhausted");
}
void aac_pointer_audit_free(void *p,aac_compact_owner_t *state) {
    if(!p)return;
    for(unsigned i=0;i<MAX_LIVE_ALLOCATIONS;++i)if(allocations[i].pointer==p) {
        assert(allocations[i].context==state);
        allocations[i]=(allocation_t){0};++frees_seen;return;
    }
}
static aac_analysis_core_t *current_core(void) {
    aac_compact_owner_t *state=aac_compact_owner_audit_context();
    for(unsigned i=0;i<MAX_LIVE_ALLOCATIONS;++i)
        if(allocations[i].context==state && allocations[i].bytes==sizeof(aac_analysis_core_t))
            return allocations[i].pointer;
    assert(!"No live AAC core in this task");return NULL;
}
void aac_pointer_audit_io(const void *input,size_t input_bytes,const void *output,size_t output_bytes) {
    aac_compact_owner_t *state=aac_compact_owner_audit_context();
    for(unsigned i=0;i<4;++i)if(io_scopes[i].state==state) {
        assert(!input && !output);io_scopes[i]=(io_t){0};return;
    }
    assert(input && output);
    for(unsigned i=0;i<4;++i)if(!io_scopes[i].state) {
        io_scopes[i]=(io_t){state,input,output,input_bytes,output_bytes};++io_calls;return;
    }
    assert(!"AAC pointer audit IO registry exhausted");
}

extern const int16_t sfb_8_1024[],sfb_16_1024[],sfb_24_1024[],sfb_32_1024[],
                     sfb_48_1024[],sfb_64_1024[],sfb_96_1024[];
extern const int16_t sfb_8_128[],sfb_16_128[],sfb_24_128[],sfb_48_128[],sfb_64_128[];
extern const aac_analysis_sample_rates_t samp_rate_info;
static bool window_addresses(aac_analysis_core_t *core) {
    REQUIRE(core->mc.sample_rate_index>=0 && core->mc.sample_rate_index<12);
    const int16_t *long_top=NULL,*short_top=NULL;
    switch(samp_rate_info.entry[core->mc.sample_rate_index].rate) {
    case 8000: long_top=sfb_8_1024;short_top=sfb_8_128;break;
    case 11025:case 12000:case 16000: long_top=sfb_16_1024;short_top=sfb_16_128;break;
    case 22050:case 24000: long_top=sfb_24_1024;short_top=sfb_24_128;break;
    case 32000: long_top=sfb_32_1024;short_top=sfb_48_128;break;
    case 44100:case 48000: long_top=sfb_48_1024;short_top=sfb_48_128;break;
    case 64000: long_top=sfb_64_1024;short_top=sfb_64_128;break;
    case 88200:case 96000: long_top=sfb_96_1024;short_top=sfb_64_128;break;
    default:REQUIRE(false);
    }
    EXACT(core->long_window->band_top[0],long_top);
    for(unsigned i=0;i<8;++i)EXACT(core->short_window->band_top[i],short_top);
    return true;
}

// Exact layout built by ps_hybrid_filter_bank_allocation, followed by the
// output vectors, pointer tables, long/short delay lines and sub-QMF delays.
typedef struct {
    aac_hybrid_abi_t hybrid;
    int32_t resolution[HYBRID_BANDS];
    int32_t *real_history[HYBRID_BANDS], *imag_history[HYBRID_BANDS];
    int32_t history[HYBRID_BANDS][2][HYBRID_HISTORY];
    int32_t scratch[2][HYBRID_SCRATCH];
    aac_ps_hybrid_outputs_abi_t outputs;
    int32_t *sub_real[HYBRID_OUTPUTS], *sub_imag[HYBRID_OUTPUTS];
    int32_t long_delay[PS_LONG_BANDS][2][PS_LONG_DELAY];
    int32_t short_delay[PS_MAIN_BANDS-PS_SHORT_BANDS-PS_LONG_BANDS][2];
    int32_t sub_delay[HYBRID_OUTPUTS][2][2];
} hybrid_storage_t;
_Static_assert(sizeof(hybrid_storage_t)==sizeof(((aac_sbr_ps_overlay_abi_t *)0)->hybrid_and_long_delays),
               "Hybrid/delay cursor must finish at the allpass workspace");

static bool serial_tables(aac_ps_abi_t *ps,aac_sbr_ps_overlay_abi_t *overlay) {
    uint8_t *q=overlay->allpass_qmf,*s=overlay->allpass_sub_qmf;
    for(unsigned link=0;link<PS_SERIAL_LINKS;++link) {
        unsigned rows=link+3;
        int32_t **qr=(void *)q,**qi=qr+rows;
        int32_t **sr=(void *)s,**si=sr+rows;
        EXACT(ps->serial_real[link],qr);EXACT(ps->serial_imag[link],qi);
        EXACT(ps->sub_serial_real[link],sr);EXACT(ps->sub_serial_imag[link],si);
        int32_t *qd=(void *)(qi+rows),*sd=(void *)(si+rows);
        for(unsigned row=0;row<rows;++row) {
            EXACT(qr[row],qd);EXACT(qi[row],qd+PS_SHORT_BANDS);
            EXACT(sr[row],sd);EXACT(si[row],sd+HYBRID_OUTPUTS);
            qd+=2*PS_SHORT_BANDS;sd+=2*HYBRID_OUTPUTS;
        }
        REQUIRE(ps->serial_index[link]<rows);
        q=(void *)qd;s=(void *)sd;
    }
    EXACT(q,overlay->allpass_qmf+sizeof(overlay->allpass_qmf));
    EXACT(s,overlay->allpass_sub_qmf+sizeof(overlay->allpass_sub_qmf));
    return true;
}
static bool ps_addresses(aac_high_owner_t *owner,aac_ps_abi_t *ps,
                         aac_analysis_core_t *core,bool after) {
    aac_sbr_ps_overlay_abi_t *overlay=&owner->channel[1].ps_overlay;
    EXACT(ps,&overlay->relocated_ps);
    EXACT(ps->peak,overlay->peak);EXACT(ps->previous_energy,overlay->previous_energy);
    EXACT(ps->previous_peak_difference,overlay->previous_peak_difference);
    EXACT(ps->right_synthesis,owner->channel[1].frame.synthesis);
    hybrid_storage_t *h=(void *)overlay->hybrid_and_long_delays;
    EXACT(ps->hybrid,&h->hybrid);
    REQUIRE(h->hybrid.bands==HYBRID_BANDS && h->hybrid.history_length==HYBRID_HISTORY);
    EXACT(h->hybrid.resolution,h->resolution);
    EXACT(h->hybrid.real_history,h->real_history);EXACT(h->hybrid.imag_history,h->imag_history);
    EXACT(h->hybrid.real_scratch,h->scratch[0]);EXACT(h->hybrid.imag_scratch,h->scratch[1]);
    for(unsigned band=0;band<HYBRID_BANDS;++band) {
        REQUIRE(h->resolution[band]==(band?2:8));
        EXACT(h->real_history[band],h->history[band][0]);
        EXACT(h->imag_history[band],h->history[band][1]);
    }
    EXACT(ps->hybrid_left_real,h->outputs.left_real);EXACT(ps->hybrid_left_imag,h->outputs.left_imag);
    EXACT(ps->hybrid_right_real,h->outputs.right_real);EXACT(ps->hybrid_right_imag,h->outputs.right_imag);
    EXACT(ps->sub_delay_real,h->sub_real);EXACT(ps->sub_delay_imag,h->sub_imag);
    EXACT(ps->delay_real,overlay->delay_real);EXACT(ps->delay_imag,overlay->delay_imag);
    for(unsigned band=0;band<PS_MAIN_BANDS;++band) {
        int32_t *r,*i;
        if(band<PS_SHORT_BANDS) {
            r=overlay->main_delay_real+band*2;i=overlay->main_delay_imag+band*2;
        } else if(band<PS_SHORT_BANDS+PS_LONG_BANDS) {
            r=h->long_delay[band-PS_SHORT_BANDS][0];i=h->long_delay[band-PS_SHORT_BANDS][1];
        } else {
            r=&h->short_delay[band-PS_SHORT_BANDS-PS_LONG_BANDS][0];
            i=&h->short_delay[band-PS_SHORT_BANDS-PS_LONG_BANDS][1];
        }
        EXACT(ps->delay_real[band],r);EXACT(ps->delay_imag[band],i);
        if(band>=PS_SHORT_BANDS) {
            unsigned index=band-PS_SHORT_BANDS, length=index<PS_LONG_BANDS?PS_LONG_DELAY:1;
            REQUIRE(ps->delay_length[index]==length);
            REQUIRE(ps->long_index[index]>=0 && ps->long_index[index]<length);
        }
    }
    for(unsigned band=0;band<HYBRID_OUTPUTS;++band) {
        EXACT(ps->sub_delay_real[band],h->sub_delay[band][0]);
        EXACT(ps->sub_delay_imag[band],h->sub_delay[band][1]);
    }
    REQUIRE(ps->delay_index>=0 && ps->delay_index<2);
    if(!serial_tables(ps,overlay))return false;
    if(after) {
        EXACT(ps->qmf_real,&core->channel[1]);
        EXACT(ps->qmf_imag,core->spectral[0].coefficients+PS_QMF_IMAG_WORD_OFFSET);
        REQUIRE(span(ps->qmf_real,QMF_ROWS*QMF_ROW_WORDS*sizeof(int32_t),core,sizeof(*core),4));
        REQUIRE(span(ps->qmf_imag,QMF_ROWS*QMF_ROW_WORDS*sizeof(int32_t),core,sizeof(*core),4));
    }
    return true;
}

// Tables rotate: check a permutation of the exact row starts, not merely an
// address anywhere in the containing allocation. The stack row is call-local.
static bool smoothing_addresses(aac_high_channel_t *ch,int32_t **tables[4],
                                 aac_smoothing_scratch_t *scratch,unsigned phase) {
    int32_t (*matrix[4])[AAC_SBR_BANDS]={ch->frame.gain_mantissa,ch->frame.gain_exponent,
                                       ch->frame.noise_mantissa,ch->frame.noise_exponent};
    for(unsigned t=0;t<4;++t) {
        EXACT(tables[t],ch->smoothing[t]);
        unsigned seen=0;
        for(unsigned row=0;row<AAC_SBR_ROWS;++row) {
            if(!phase && row==AAC_SMOOTHING_PAST_ROWS) { EXACT(tables[t][row],NULL);continue; }
            unsigned target=0;
            while(target<AAC_SMOOTHING_PAST_ROWS && tables[t][row]!=matrix[t][target])++target;
            if(target==AAC_SMOOTHING_PAST_ROWS) {
                REQUIRE(phase && scratch);
                EXACT(tables[t][row],scratch->current[t]);
            }
            REQUIRE(!(seen&(1U<<target)));seen|=1U<<target;
        }
        REQUIRE(seen==((1U<<(phase?AAC_SBR_ROWS:AAC_SMOOTHING_PAST_ROWS))-1));
    }
    return true;
}
void aac_pointer_audit_smoothing(void *frame,int32_t **tables[4],
                                aac_smoothing_scratch_t *scratch,unsigned phase) {
    aac_compact_owner_t *state=aac_compact_owner_audit_context();
    aac_high_owner_t *owner=state->owner;
    assert(live(owner,sizeof(*owner),state));
    aac_high_channel_t *ch=frame==&owner->channel[0].frame?&owner->channel[0]:&owner->channel[1];
    assert(frame==&ch->frame);
    if(scratch) {
        void *base=(void *)xTaskGetStackStart(NULL);
        assert(span(scratch,sizeof(*scratch),base,heap_caps_get_allocated_size(base),4));
    }
    assert(smoothing_addresses(ch,tables,scratch,phase));++smoothing_calls;
}

static bool core_addresses(aac_analysis_core_t *core,aac_analysis_external_t *external,bool after) {
    aac_compact_owner_t *state=aac_compact_owner_audit_context();
    REQUIRE(live(core,sizeof(*core),state));
    REQUIRE(live(core->program,sizeof(*core->program),state));
    REQUIRE(live(core->long_window,sizeof(*core->long_window),state));
    REQUIRE(live(core->short_window,sizeof(*core->short_window),state));
    REQUIRE(core->long_window!=core->short_window);
    REQUIRE(live(core->workspace,sizeof(*core->workspace),state));
    EXACT(core->scratch,&core->workspace->scratch);EXACT(core->shared,&core->workspace->shared);
    EXACT(core->mask,core->spectral[0].mask);
    for(unsigned ch=0;ch<2;++ch) {
        // PS reuses the inactive right core channel as a QMF workspace.
        if(ch && core->mc.ps_present)continue;
        EXACT(core->channel[ch].spectrum.coefficients,core->spectral[ch].coefficients);
        EXACT(core->channel[ch].spectrum.shared,&core->spectral[ch].shared);
    }
    for(unsigned w=0;w<4;++w)EXACT(core->window_map[w],w==2?core->short_window:core->long_window);
    EXACT(core->long_window->short_band_width,NULL);
    EXACT(core->short_window->short_band_width,core->short_band_width);
    if(!window_addresses(core))return false;
    if(core->sbr_stream)REQUIRE(live(core->sbr_stream,sizeof(*core->sbr_stream),state));
    if(core->sbr) {
        EXACT(core->sbr,state->owner);
        REQUIRE(live(core->sbr,sizeof(aac_high_owner_t),state));
        aac_high_owner_t *owner=state->owner;
        if(owner->ps)EXACT(owner->ps,state->ps_initialized?
                           (void *)&owner->channel[1].ps_overlay.relocated_ps:(void *)&owner->inactive_ps);
    }
    if(core->sbr_control)REQUIRE(live(core->sbr_control,sizeof(*core->sbr_control),state));
    if(after) {
        EXACT(core->input.buffer,external->input);
        REQUIRE(core->input.input_length<=external->input_capacity);
    }
    if(external) {
        // external is a field inside the still-live SDK wrapper allocation.
        void *wrapper=(uint8_t *)external - offsetof(aac_analysis_decoder_t,external);
        REQUIRE(live(wrapper,sizeof(aac_analysis_decoder_t),state));
        EXACT(((aac_analysis_decoder_t *)wrapper)->core,core);
        // The native adapter always supplies both 4 KiB output halves.
        EXACT(((aac_analysis_decoder_t *)wrapper)->extra_output,NULL);
        bool found=false;
        for(unsigned i=0;i<4;++i)if(io_scopes[i].state==state) {
            io_t *io=&io_scopes[i];found=true;
            EXACT(external->input,io->input);
            REQUIRE(external->input_length==io->input_bytes);
            EXACT(external->output,io->output);
            REQUIRE(span(external->output,NATIVE_OUTPUT_BLOCK_BYTES,io->output,io->output_bytes,2));
            if(external->output_plus) {
                EXACT(external->output_plus,(const uint8_t *)io->output+NATIVE_OUTPUT_BLOCK_BYTES);
                REQUIRE(span(external->output_plus,NATIVE_OUTPUT_BLOCK_BYTES,io->output,io->output_bytes,2));
            }
        }
        REQUIRE(found);
    }
    return true;
}
void aac_pointer_audit_core(void *core,void *external,bool after) {
    assert(core_addresses(core,external,after));++core_calls;
}
void aac_pointer_audit_reset(void *core) {
    assert(core_addresses(core,NULL,false));
    aac_analysis_core_t *c=core;
    aac_compact_owner_t *state=aac_compact_owner_audit_context();
    aac_high_owner_t *owner=state->owner;
    if(owner && !owner->initialize_ps && c->plus_enabled && c->mc.ps_present==1 && state->ps_initialized)
        assert(ps_addresses(owner,owner->ps,c,true));
    ++reset_calls;
}
static bool workspace_span(const void *p,size_t bytes,aac_analysis_core_t *core,
                            aac_high_owner_t *owner,aac_high_frame_t *frame) {
    // Live regions used by the non-history memmoves in sbr_dec. A successful
    // heap-wide range check alone would admit unrelated fields and stale views.
    struct { const void *base; size_t bytes, alignment; } regions[]={
        {frame->low_real,sizeof(frame->low_real),_Alignof(int32_t)},
        {frame->low_imag,sizeof(frame->low_imag),_Alignof(int32_t)},
        {frame->high_real,QMF_HIGH_WORDS*sizeof(int32_t),_Alignof(int32_t)},
        {frame->high_imag,QMF_HIGH_WORDS*sizeof(int32_t),_Alignof(int32_t)},
        {frame->synthesis,sizeof(frame->synthesis),_Alignof(int16_t)},
        {owner->channel[1].frame.synthesis,sizeof(owner->channel[1].frame.synthesis),_Alignof(int16_t)},
        {core->workspace,sizeof(*core->workspace),_Alignof(int32_t)},
    };
    for(unsigned i=0;i<sizeof(regions)/sizeof(regions[0]);++i)
        if(span(p,bytes,regions[i].base,regions[i].bytes,regions[i].alignment))return true;
    if(core->mc.ps_present) {
        // sbr_dec loads/saves all six 12-word hybrid history vectors around PS.
        hybrid_storage_t *hybrid=(void *)owner->channel[1].ps_overlay.hybrid_and_long_delays;
        for(unsigned band=0;band<HYBRID_BANDS;++band)
            for(unsigned part=0;part<2;++part)
                if(span(p,bytes,hybrid->history[band][part],sizeof(hybrid->history[band][part]),4))return true;
        if(span(p,bytes,&core->channel[1],QMF_ROWS*QMF_ROW_WORDS*sizeof(int32_t),4))return true;
        if(span(p,bytes,core->spectral[0].coefficients+PS_QMF_IMAG_WORD_OFFSET,
                QMF_ROWS*QMF_ROW_WORDS*sizeof(int32_t),4))return true;
    }
    return false;
}
void aac_pointer_audit_copy(const void *dest,const void *source,size_t bytes) {
    aac_analysis_core_t *core=current_core();
    aac_compact_owner_t *state=aac_compact_owner_audit_context();
    assert(state->high_history.frame && core->sbr==state->owner);
    assert(check(workspace_span(dest,bytes,core,state->owner,state->high_history.frame),"sbr_dec memmove destination",dest,NULL));
    assert(check(workspace_span(source,bytes,core,state->owner,state->high_history.frame),"sbr_dec memmove source",source,NULL));
    ++copy_calls;
}
static bool envelope_addresses(AAC_POINTER_ENVELOPE_ARGS) {
    aac_analysis_core_t *core=current_core();
    aac_high_owner_t *owner=(void *)core->sbr;
    aac_high_channel_t *ch=frame==&owner->channel[0].frame?&owner->channel[0]:&owner->channel[1];
    EXACT(frame,&ch->frame);
    aac_high_frame_t *f=frame;
    aac_analysis_frequency_control_t *fc=(void *)core->sbr_control->remaining;
    aac_analysis_harmonics_t *harmonics=(void *)f->harmonics_and_envelopes;
    aac_analysis_frame_control_t *frame_control=(void *)f->frame_control;
    EXACT(real,f->high_real);EXACT(imag,real_only?NULL:f->high_imag);
    EXACT(frequency,fc->frequency_bands);EXACT(frequency_count,fc->band_count);
    EXACT(noise_frequency,fc->noise_bands);
    REQUIRE(noise_bands==fc->noise_band_count && reset==frame_control->reset);
    EXACT(alias,real_only?f->alias_degree:NULL);
    EXACT(harmonic_index,&harmonics->harmonic_index);EXACT(noise_index,&harmonics->phase_index);
    EXACT(previous_harmonics,harmonics->previous_harmonics);EXACT(startup,&f->startup);
    EXACT(limiter_bands,fc->limiter_bands);EXACT(gate_mode,fc->gate_mode);
    EXACT(gain,real_only?NULL:ch->smoothing[0]);EXACT(gain_exp,real_only?NULL:ch->smoothing[1]);
    EXACT(noise,real_only?NULL:ch->smoothing[2]);EXACT(noise_exp,real_only?NULL:ch->smoothing[3]);
    EXACT(workspace,core->scratch);EXACT(sqrt_cache,fc->sqrt_cache);
    void *base=(void *)xTaskGetStackStart(NULL);
    REQUIRE(span(patch,sizeof(aac_analysis_patch_t),base,heap_caps_get_allocated_size(base),4));
    REQUIRE(real_only==core->sbr_control->low_complexity);
    return true;
}
void aac_pointer_audit_envelope(AAC_POINTER_ENVELOPE_ARGS) {
    assert(envelope_addresses(frame,real,imag,frequency,frequency_count,noise_frequency,noise_bands,
        reset,alias,harmonic_index,noise_index,previous_harmonics,startup,limiter_bands,gate_mode,
        gain,gain_exp,noise,noise_exp,workspace,patch,sqrt_cache,real_only));++envelope_calls;
}
void aac_pointer_audit_frame(void *opaque,void *frame,void *control,void *ps,bool after) {
    aac_analysis_core_t *core=opaque;
    aac_compact_owner_t *state=aac_compact_owner_audit_context();
    aac_high_owner_t *owner=state->owner;
    assert(live(owner,sizeof(*owner),state) && core->sbr==(void *)owner);
    assert(control==core->sbr_control && live(control,sizeof(*core->sbr_control),state));
    aac_high_frame_t *f=frame;
    assert(f==&owner->channel[0].frame || (!ps && f==&owner->channel[1].frame));
    if(ps) {
        assert(f==&owner->channel[0].frame && state->ps_initialized && owner->ps==ps);
        assert(f->high_real==(void *)core->shared);
        assert(f->high_imag==core->spectral[0].coefficients+PS_HIGH_IMAG_WORD_OFFSET);
        assert(span(f->high_real,QMF_HIGH_WORDS*4,core->shared,sizeof(*core->shared),4));
        assert(span(f->high_imag,QMF_HIGH_WORDS*4,core->spectral,sizeof(core->spectral),4));
        assert(ps_addresses(owner,ps,core,after));++ps_calls;
    } else {
        assert(f->high_real==core->spectral[0].coefficients);
        assert(f->high_imag==core->spectral[1].coefficients);
        assert(span(f->high_real,QMF_HIGH_WORDS*4,&core->spectral[0],sizeof(core->spectral[0]),4));
        assert(span(f->high_imag,QMF_HIGH_WORDS*4,&core->spectral[1],sizeof(core->spectral[1]),4));
    }
    aac_high_channel_t *ch=(void *)((uint8_t *)frame - offsetof(aac_high_channel_t,frame));
    int32_t **tables[4]={ch->smoothing[0],ch->smoothing[1],ch->smoothing[2],ch->smoothing[3]};
    assert(smoothing_addresses(ch,tables,NULL,0));++frame_calls;
    // Deliberately corrupt a pointer without running DSP. The oracle must reject
    // an in-bounds address belonging to the wrong region, then restore it.
    if(ps && !negative_cases) {
        aac_ps_abi_t *p=ps;int32_t *saved=p->delay_real[0];
        quiet=true;p->delay_real[0]=p->delay_imag[0];
        assert(!ps_addresses(owner,p,core,after));++negative_cases;p->delay_real[0]=saved;
        saved=tables[0][0];tables[0][0]=tables[1][0];
        assert(!smoothing_addresses(ch,tables,NULL,0));++negative_cases;tables[0][0]=saved;
        tables[0][0]=saved+1;
        assert(!smoothing_addresses(ch,tables,NULL,0));++negative_cases;tables[0][0]=saved;
        tables[0][0]=tables[0][1];
        assert(!smoothing_addresses(ch,tables,NULL,0));++negative_cases;tables[0][0]=saved;
        tables[0][0]=NULL;
        assert(!smoothing_addresses(ch,tables,NULL,0));++negative_cases;tables[0][0]=saved;
        assert(!live(core,sizeof(*core),NULL));++negative_cases;
        assert(!live(core,sizeof(*core)-4,state));++negative_cases;
        assert(!span((uint8_t *)core+sizeof(*core),4,core,sizeof(*core),4));++negative_cases;
        assert(!span((uint8_t *)core+1,4,core,sizeof(*core),4));++negative_cases;
        int16_t *flash_saved=core->short_window->band_top[0];
        core->short_window->band_top[0]=core->long_window->band_top[0];
        assert(!window_addresses(core));++negative_cases;
        core->short_window->band_top[0]=flash_saved;
        quiet=false;
    }
}
static void captured_stream(void) {
    // Same disposable app1 test envelope as run_aac_bfp16.py; never used on a board.
    const esp_partition_t *partition=esp_partition_find_first(ESP_PARTITION_TYPE_APP,ESP_PARTITION_SUBTYPE_APP_OTA_1,NULL);
    assert(partition);
    uint32_t header[8];
    assert(esp_partition_read(partition,0,header,sizeof(header))==ESP_OK);
    if(header[0]!=UINT32_C(0x31504642))return;
    assert(header[1] && header[1]<=partition->size-sizeof(header));
    const void *mapped;esp_partition_mmap_handle_t handle;
    assert(esp_partition_mmap(partition,0,sizeof(header)+header[1],ESP_PARTITION_MMAP_DATA,&mapped,&handle)==ESP_OK);
    const uint8_t *p=(const uint8_t *)mapped+sizeof(header),*end=p+header[1];
    native_aac_decoder_t *decoder=native_aac_decoder_create();assert(decoder);
    uint8_t *pcm=malloc(2*NATIVE_OUTPUT_BLOCK_BYTES);assert(pcm);
    unsigned samples=0,frames=0;uint32_t hash=2166136261u;
    unsigned checks_before=checks;
    while(p<end) {
        unsigned bytes=end-p;if(bytes>997)bytes=997;
        esp_audio_simple_dec_raw_t raw={.buffer=(uint8_t *)p,.len=bytes};
        esp_audio_simple_dec_out_t out={.buffer=pcm,.len=2*NATIVE_OUTPUT_BLOCK_BYTES};
        assert(native_aac_decoder_process(decoder,&raw,&out)==ESP_AUDIO_ERR_OK);
        assert(raw.consumed<=bytes && (raw.consumed || out.decoded_size));p+=raw.consumed;
        if(out.decoded_size) {
            esp_audio_simple_dec_info_t info;
            assert(native_aac_decoder_get_info(decoder,&info)==ESP_AUDIO_ERR_OK);
            assert(info.sample_rate==header[2] && info.channel==header[3] && info.bits_per_sample==16);
            assert(out.decoded_size<=2*NATIVE_OUTPUT_BLOCK_BYTES);
            for(unsigned i=0;i<out.decoded_size;++i)hash=(hash^pcm[i])*16777619u;
            samples+=out.decoded_size/2;++frames;
        }
        if(frames%32==0)vTaskDelay(1);
    }
    native_aac_decoder_destroy(decoder);free(pcm);esp_partition_munmap(handle);
    assert(samples && frames && heap_caps_check_integrity_all(true));
    ESP_LOGI("aac_pointer","AAC_POINTER_CAPTURE bytes=%u rate=%u channels=%u samples=%u frames=%u pcm_hash=%08" PRIx32 " checks=%u",
             (unsigned)header[1],(unsigned)header[2],(unsigned)header[3],samples,frames,hash,checks-checks_before);
}
void aac_pointer_audit_report(void) {
    captured_stream();
    for(unsigned i=0;i<MAX_LIVE_ALLOCATIONS;++i)assert(!allocations[i].pointer);
    for(unsigned i=0;i<4;++i)assert(!io_scopes[i].state);
    assert(core_calls && frame_calls && ps_calls && smoothing_calls && envelope_calls && reset_calls && io_calls && copy_calls && negative_cases==10);
    assert(allocations_seen==frees_seen);
    ESP_LOGI("aac_pointer","AAC_POINTER_PASS checks=%u core=%u frames=%u ps=%u smoothing=%u allocations=%u frees=%u negative_cases=%u envelopes=%u resets=%u io=%u copies=%u",
             checks,core_calls,frame_calls,ps_calls,smoothing_calls,allocations_seen,frees_seen,negative_cases,envelope_calls,reset_calls,io_calls,copy_calls);
}
