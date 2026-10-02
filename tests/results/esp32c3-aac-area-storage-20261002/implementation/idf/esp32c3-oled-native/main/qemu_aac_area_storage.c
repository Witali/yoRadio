// Numerical probes only. Original allocations and all native DSP are retained.
// Readers, lifetimes and PS aliases: docs/ESP32C3_AAC_OTHER_ARRAYS_20261002.md.
#include "qemu_aac_packed_history.h"
#include "aac_sbr_abi.h"
#include "packed_complex_storage_check.h"
#include "esp_log.h"
#include <inttypes.h>
#include <limits.h>
#include <string.h>

enum {
    AREA_BYPASS, AREA_HIGH_QMF, AREA_HYBRID_HISTORY, AREA_IMDCT,
    AREA_SMOOTH_MANTISSA, AREA_SMOOTH_EXPONENT, AREA_PREVIOUS_MIX,
    AREA_HYBRID_OUTPUT, AREA_PS_ENERGY, AREA_EXACT,
    AREA_COUNT = AREA_EXACT, PACK_PAIRS = 4, HIGH_ROWS = 6, HIGH_BANDS = 48,
    HYBRID_BANDS = 3, HYBRID_HISTORY = 12, HYBRID_OUTPUTS = 10,
    MIX_ROWS = 4, MIX_BANDS = 22, ENERGY_BANDS = 20, OVERLAP_SAMPLES = 1024
};
static const uint32_t guard = UINT32_C(0xd173a509);
static unsigned selected, repetition, windows_mask, transform1, transform2;
typedef struct {
    uint32_t calls, pairs, changed, saturated, nonzero, max_shift, out_of_int16;
    int32_t minimum, maximum;
} area_stats_t;
static area_stats_t stats[AREA_COUNT];

static int enabled(unsigned area) { return selected == area || selected == AREA_EXACT; }
void packed_history_reset(unsigned run) {
    memset(stats, 0, sizeof(stats));
    for (unsigned a = 1; a < AREA_COUNT; ++a) {
        stats[a].minimum = INT32_MAX; stats[a].maximum = INT32_MIN;
    }
    repetition = run; selected = 0; windows_mask = transform1 = transform2 = 0;
}
void packed_history_select(unsigned variant) { assert(variant <= AREA_EXACT); selected = variant; }

static void bounds(const void *base, size_t bytes, const void *p, size_t length) {
    uintptr_t low = (uintptr_t)base, address = (uintptr_t)p;
    assert(!(address & (sizeof(int32_t)-1)) && address >= low &&
           address <= low + bytes && length <= low + bytes - address);
}
static void ps_bounds(aac_ps_abi_t *ps, const void *p, size_t bytes) {
    aac_sbr_owner_abi_t *owner = (void *)((uint8_t *)ps - offsetof(aac_sbr_owner_abi_t, embedded_ps));
    assert(owner->ps == ps);
    aac_sbr_ps_overlay_abi_t *workspace = &owner->channel[1].ps_overlay;
    bounds(workspace->peak, (uintptr_t)&workspace->relocated_ps - (uintptr_t)workspace->peak, p, bytes);
}
static void observe(area_stats_t *s, int32_t value) {
    if (repetition != 1) return;
    s->nonzero += value != 0;
    if (value < s->minimum) s->minimum = value;
    if (value > s->maximum) s->maximum = value;
}

// Stride 1 means Re/Im arrays; stride 2 pairs adjacent REAL scalars.
// The latter is block-floating storage of real coefficients, not complex DSP.
static void roundtrip(unsigned area, int32_t *real, int32_t *imag, unsigned pairs, unsigned stride) {
    assert(enabled(area) && pairs && (stride == 1 || stride == 2));
    area_stats_t *s = stats + area;
    ++s->calls; s->pairs += pairs;
    for (unsigned base = 0; base < pairs; base += PACK_PAIRS) {
        unsigned count = pairs-base < PACK_PAIRS ? pairs-base : PACK_PAIRS;
        struct { uint32_t before, words[PACK_PAIRS + 1], after; } packed = {.before=guard, .after=guard};
        struct { uint32_t before, word, after; } meta = {guard, 0, guard};
        packed.words[count] = guard;
        for (unsigned i = 0; i < count; ++i) {
            unsigned index = (base+i)*stride;
            int32_t r = real[index], q = imag[index];
            observe(s,r); observe(s,q);
            if (selected == AREA_EXACT) continue;
            unsigned metadata, saturated;
            packed.words[i] = pc18_pack(r,q,&metadata,&saturated);
            pc_storage_store_metadata(PC_STORAGE_SHARED18_FOUR,&meta.word,i,metadata);
            if (repetition == 1) s->saturated += saturated;
            unsigned shift = metadata & PC_EXPONENT_MASK;
            if (shift > s->max_shift) s->max_shift = shift;
        }
        for (unsigned i = 0; i < count && selected != AREA_EXACT; ++i) {
            unsigned index = (base+i)*stride;
            int32_t r,q;
            pc18_unpack(packed.words[i],pc_storage_load_metadata(PC_STORAGE_SHARED18_FOUR,&meta.word,i),&r,&q);
            s->changed += (r != real[index]) + (q != imag[index]);
            real[index]=r; imag[index]=q;
        }
        assert(packed.before==guard && packed.after==guard && packed.words[count]==guard);
        assert(meta.before==guard && meta.after==guard);
    }
}
static void real_roundtrip(unsigned area, int32_t *values, unsigned count) {
    assert(!(count & 1u)); roundtrip(area,values,values+1,count/2,2);
}
static void exponent_roundtrip(int32_t *values, unsigned count) {
    area_stats_t *s = stats + AREA_SMOOTH_EXPONENT;
    ++s->calls; s->pairs += count/2;
    for (unsigned i = 0; i < count; ++i) {
        int32_t value = values[i]; observe(s,value);
        if (value < INT16_MIN || value > INT16_MAX) { ++s->out_of_int16; continue; }
        // Out-of-range values are reported, never silently truncated.
        if (selected != AREA_EXACT) { volatile int16_t compact = value; values[i] = compact; }
    }
}

void __real_sbr_dec(int16_t *, void *, void *, int32_t, int32_t *, void *, void *, void *);
void __wrap_sbr_dec(int16_t *input, void *output, void *frame, int32_t apply,
                    int32_t *control, void *other_output, void *ps_ptr, void *core) {
    __real_sbr_dec(input,output,frame,apply,control,other_output,ps_ptr,core);
    if (!selected) return;
    aac_sbr_frame_abi_t *f = frame;
    aac_sbr_control_abi_t *config = (void *)control;
    assert(config->columns == 32 && config->write_offset == 8);
    if (enabled(AREA_HIGH_QMF) && !config->low_complexity)
        for (unsigned row=0;row<HIGH_ROWS;++row)
            roundtrip(AREA_HIGH_QMF,f->high_real_history[row],f->high_imag_history[row],HIGH_BANDS,1);
    if (enabled(AREA_SMOOTH_MANTISSA) || enabled(AREA_SMOOTH_EXPONENT))
        for (unsigned row=0;row<AAC_SBR_ROWS;++row) {
            if (enabled(AREA_SMOOTH_MANTISSA)) {
                real_roundtrip(AREA_SMOOTH_MANTISSA,f->gain_mantissa[row],AAC_SBR_BANDS);
                real_roundtrip(AREA_SMOOTH_MANTISSA,f->noise_mantissa[row],AAC_SBR_BANDS);
            }
            if (enabled(AREA_SMOOTH_EXPONENT)) {
                exponent_roundtrip(f->gain_exponent[row],AAC_SBR_BANDS);
                exponent_roundtrip(f->noise_exponent[row],AAC_SBR_BANDS);
            }
        }
    aac_ps_abi_t *ps = ps_ptr;
    if (!ps) return;
    aac_sbr_owner_abi_t *owner = (void *)((uint8_t *)frame - offsetof(aac_sbr_owner_abi_t,channel[0].frame));
    assert(ps == &owner->embedded_ps && owner->ps == ps);
    if (enabled(AREA_HYBRID_HISTORY)) {
        aac_hybrid_abi_t *h = ps->hybrid;
        ps_bounds(ps,h,sizeof(*h));
        assert(h->bands == HYBRID_BANDS && h->history_length == HYBRID_HISTORY);
        ps_bounds(ps,h->real_history,HYBRID_BANDS*sizeof(void *));
        ps_bounds(ps,h->imag_history,HYBRID_BANDS*sizeof(void *));
        for (unsigned band=0;band<HYBRID_BANDS;++band) {
            ps_bounds(ps,h->real_history[band],HYBRID_HISTORY*sizeof(int32_t));
            ps_bounds(ps,h->imag_history[band],HYBRID_HISTORY*sizeof(int32_t));
            roundtrip(AREA_HYBRID_HISTORY,h->real_history[band],h->imag_history[band],HYBRID_HISTORY,1);
        }
    }
    if (enabled(AREA_PREVIOUS_MIX))
        for (unsigned row=0;row<MIX_ROWS;++row)
            real_roundtrip(AREA_PREVIOUS_MIX,ps->previous_mix[row],MIX_BANDS);
}

// Roundtrip the IMDCT overlap at its producer boundary. In PS mode the inactive
// right core channel is reused as QMF workspace: never sweep both core arrays.
#define TRANSFORM_ARGS uintptr_t a, int32_t *overlap, uintptr_t c, uintptr_t d, uintptr_t e, uintptr_t f, uintptr_t g, uintptr_t h, uintptr_t i
#define TRANSFORM_CALL a,overlap,c,d,e,f,g,h,i
void __real_trans4m_freq_2_time_fxp_1(TRANSFORM_ARGS);
void __real_trans4m_freq_2_time_fxp_2(TRANSFORM_ARGS);
static void overlap_probe(int32_t *overlap, unsigned window, unsigned transform) {
    if (!enabled(AREA_IMDCT)) return;
    assert(window < 4);
    windows_mask |= 1u << window;
    if (transform == 1) ++transform1; else ++transform2;
    real_roundtrip(AREA_IMDCT,overlap,OVERLAP_SAMPLES);
}
void __wrap_trans4m_freq_2_time_fxp_1(TRANSFORM_ARGS) {
    __real_trans4m_freq_2_time_fxp_1(TRANSFORM_CALL); overlap_probe(overlap,d,1);
}
void __wrap_trans4m_freq_2_time_fxp_2(TRANSFORM_ARGS) {
    __real_trans4m_freq_2_time_fxp_2(TRANSFORM_CALL); overlap_probe(overlap,c,2);
}

void __real_ps_hybrid_analysis(void *,void *,int32_t *,int32_t *,aac_hybrid_abi_t *,void *,unsigned);
void __wrap_ps_hybrid_analysis(void *r,void *i,int32_t *out_r,int32_t *out_i,aac_hybrid_abi_t *h,void *scratch,unsigned slot) {
    __real_ps_hybrid_analysis(r,i,out_r,out_i,h,scratch,slot);
    if (enabled(AREA_HYBRID_OUTPUT)) {
        assert(h->bands==HYBRID_BANDS && h->resolution[0]==8 && h->resolution[1]==2 && h->resolution[2]==2);
        roundtrip(AREA_HYBRID_OUTPUT,out_r,out_i,HYBRID_OUTPUTS,1);
    }
}
void __real_ps_pwr_transient_detection(aac_ps_abi_t *,void *,void *,void *);
void __wrap_ps_pwr_transient_detection(aac_ps_abi_t *ps,void *r,void *i,void *scratch) {
    __real_ps_pwr_transient_detection(ps,r,i,scratch);
    if (enabled(AREA_PS_ENERGY)) {
        int32_t *areas[] = {ps->peak,ps->previous_energy,ps->previous_peak_difference};
        for (unsigned a=0;a<sizeof(areas)/sizeof(areas[0]);++a) {
            ps_bounds(ps,areas[a],ENERGY_BANDS*sizeof(int32_t));
            real_roundtrip(AREA_PS_ENERGY,areas[a],ENERGY_BANDS);
        }
    }
}

void packed_history_report(const char *name,unsigned variant,unsigned run,uint32_t *rows,uint32_t *changed,unsigned *shift) {
    *rows=*changed=*shift=0;
    for (unsigned a=1;a<AREA_COUNT;++a) {
        area_stats_t *s=stats+a;
        *rows+=s->calls; *changed+=s->changed;
        if(s->max_shift>*shift)*shift=s->max_shift;
        ESP_LOGI("aac_areas","AREASTORAGE_AREA case=%s variant=%u run=%u area=%u calls=%"PRIu32
            " pairs=%"PRIu32" changed=%"PRIu32" saturated=%"PRIu32" nonzero=%"PRIu32
            " minimum=%"PRId32" maximum=%"PRId32" max_shift=%"PRIu32" out_of_int16=%"PRIu32,
            name,variant,run,a,s->calls,s->pairs,s->changed,s->saturated,s->nonzero,
            s->calls && run==1?s->minimum:0,s->calls && run==1?s->maximum:0,s->max_shift,s->out_of_int16);
    }
    ESP_LOGI("aac_areas","AREASTORAGE_WINDOWS case=%s variant=%u run=%u mask=%u transform1=%u transform2=%u",
             name,variant,run,windows_mask,transform1,transform2);
}
void packed_history_arithmetic_tests(void) {
    pc_storage_check(10000);
    ESP_LOGI("aac_areas","AREASTORAGE_ARITHMETIC_PASS format=shared18_four probes=8 control=9");
}
