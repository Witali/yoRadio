/* ------------------------------------------------------------------
 * Copyright (C) 1998-2009 PacketVideo
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied.
 * See the License for the specific language governing permissions
 * and limitations under the License.
 * -------------------------------------------------------------------
 */
/*

 Filename: ps_decorrelate.c

------------------------------------------------------------------------------
 REVISION HISTORY


 Who:                                   Date: MM/DD/YYYY
 Description:

------------------------------------------------------------------------------
 INPUT AND OUTPUT DEFINITIONS



------------------------------------------------------------------------------
 FUNCTION DESCRIPTION

  Decorrelation
  Decorrelation is achieved by means of all-pass filtering and delaying
  Sub-band samples s_k(n) are converted into de-correlated sub-bands samples
  d_k(n). k index for frequency, n time index


     _______                                              ________
    |       |                                  _______   |        |
  ->|Hybrid | LF ----                         |       |->| Hybrid |-->
    | Anal. |        |                        |       |  | Synth  |   QMF -> L
     -------         o----------------------->|       |   --------    Synth
QMF                  |                s_k(n)  |Stereo |-------------->
Anal.              -------------------------->|       |
     _______       | |                        |       |   ________
    |       | HF --o |   -----------          |Process|  |        |
  ->| Delay |      |  ->|           |-------->|       |->| Hybrid |-->
     -------       |    |decorrelate| d_k(n)  |       |  | Synth  |   QMF -> R
                   ---->|           |-------->|       |   --------    Synth
                         -----------          |_______|-------------->


  Delay is introduced to compensate QMF bands not passed through Hybrid
  Analysis

------------------------------------------------------------------------------
 REQUIREMENTS


------------------------------------------------------------------------------
 REFERENCES

SC 29 Software Copyright Licencing Disclaimer:

This software module was originally developed by
  Coding Technologies

and edited by
  -

in the course of development of the ISO/IEC 13818-7 and ISO/IEC 14496-3
standards for reference purposes and its performance may not have been
optimized. This software module is an implementation of one or more tools as
specified by the ISO/IEC 13818-7 and ISO/IEC 14496-3 standards.
ISO/IEC gives users free license to this software module or modifications
thereof for use in products claiming conformance to audiovisual and
image-coding related ITU Recommendations and/or ISO/IEC International
Standards. ISO/IEC gives users the same free license to this software module or
modifications thereof for research purposes and further ISO/IEC standardisation.
Those intending to use this software module in products are advised that its
use may infringe existing patents. ISO/IEC have no liability for use of this
software module or modifications thereof. Copyright is not released for
products that do not conform to audiovisual and image-coding related ITU
Recommendations and/or ISO/IEC International Standards.
The original developer retains full right to modify and use the code for its
own purpose, assign or donate the code to a third party and to inhibit third
parties from using the code for products that do not conform to audiovisual and
image-coding related ITU Recommendations and/or ISO/IEC International Standards.
This copyright notice must be included in all copies or derivative works.
Copyright (c) ISO/IEC 2003.

------------------------------------------------------------------------------
 PSEUDO-CODE

------------------------------------------------------------------------------
*/

// Test-only port of FAAD's packed PS-delay storage to Espressif's PacketVideo
// arithmetic. See the accompanying Apache/ISO notice and report.
// Pinned archive SHA256: 311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909.
#include "qemu_aac_packed_history.h"
#include "aac_sbr_abi.h"
#include "packed_complex14.h"
#ifdef CONFIG_YORADIO_QEMU_AAC_PC16_WRITE_TEST
#include "packed_complex16_fast.h"
#ifdef CONFIG_YORADIO_QEMU_AAC_PS_STORAGE_TEST
#include "aac_ps_storage_experiment.h"
#define PS_TEST_NAME "PSSTORAGE"
#ifdef CONFIG_YORADIO_QEMU_AAC_COMBINED_STORAGE_TEST
#include "aac_combined_storage.h"
#endif
#else
#define PS_TEST_NAME "PC16WRITE"
#endif
void aac_ps_pc16_allocate(void *,uint32_t,bool);
void aac_ps_pc16_decode(void *,void *,int32_t *,int32_t *,int32_t *,int32_t *,int32_t *);
#else
#define PS_TEST_NAME "PSPORT"
#endif
#include "esp_log.h"
#include <assert.h>
#include <inttypes.h>
#include <stddef.h>
#include <stdbool.h>
#include <string.h>

typedef aac_ps_abi_t ps_prefix_t;

static aac_sbr_owner_abi_t *ps_owner(ps_prefix_t *ps) {
    aac_sbr_owner_abi_t *owner = (void *)((uint8_t *)ps -
        offsetof(aac_sbr_owner_abi_t, embedded_ps));
    assert(owner->ps == ps);
    return owner;
}

#ifdef CONFIG_YORADIO_QEMU_AAC_PC16_WRITE_TEST
// Test sentinels in the unused workspace immediately after packed storage.
// They must never reach the live right-channel synthesis history.
typedef struct AAC_ABI_VIEW {
#ifdef CONFIG_YORADIO_QEMU_AAC_PS_STORAGE_TEST
    aac_ps_storage_experiment_t storage;
#else
    aac_sbr_packed_ps_overlay_abi_t storage;
#endif
    uint32_t guard[4];
} packed_guard_view_t;
_Static_assert(sizeof(packed_guard_view_t) <= offsetof(aac_sbr_channel_abi_t, frame.synthesis),
               "Packed test guards overlap synthesis");
#endif

extern const int8_t groupBorders[], bins2groupMap[];
extern const int32_t aRevLinkDelaySer[3], aFractDelayPhaseFactor[], aFractDelayPhaseFactorSubQmf[];
extern const int32_t aaFractDelayPhaseFactorSerQmf[][3], aaFractDelayPhaseFactorSerSubQmf[][3];
extern const int16_t aRevLinkDecaySerCoeff[][3];
extern void ps_pwr_transient_detection(void *, int32_t *, int32_t *, int32_t *);
void __real_ps_decorrelate(void *, int32_t *, int32_t *, int32_t *, int32_t *, int32_t *);
void __real_ps_allocate_decoder(void *, uint32_t);

static unsigned selected, repetition;
#ifdef CONFIG_YORADIO_QEMU_AAC_PS_STORAGE_TEST
static pc_storage_format_t experiment_format = PC_STORAGE_SHARED16;
static bool candidate_selected(void) { return selected >= PC_STORAGE_SHARED16 && selected <= PC_STORAGE_SHARED18_FOUR; }
#else
static bool candidate_selected(void) { return selected == 1; }
#endif
static struct {
    uint32_t calls, stores, changed, maximum_shift, allocations, pairs, guards, saturations;
    uint32_t cache_hits,cache_misses,cache_bytes;
} stats;
static ps_prefix_t *owners[2];
static unsigned owner_count;
#define GUARD UINT32_C(0xd3adbeef)
static const char *TAG = "ps_port";

#ifdef CONFIG_YORADIO_QEMU_AAC_PC16_WRITE_TEST
void aac_ps_pc16_test_cache(unsigned hits,unsigned misses,unsigned bytes) {
    stats.cache_hits+=hits;stats.cache_misses+=misses;stats.cache_bytes=bytes;
}
void aac_ps_pc16_test_store(uint32_t word,unsigned exponent,int32_t re,int32_t im,unsigned clipped) {
    ++stats.stores;stats.saturations+=clipped;
    if(repetition==1) {
        int32_t a,b;
#ifdef CONFIG_YORADIO_QEMU_AAC_PS_STORAGE_TEST
        pc_storage_unpack(experiment_format,word,exponent,&a,&b);
        unsigned shift=pc_storage_max_shift(experiment_format,exponent);
#else
        pc16_unpack(word,exponent,&a,&b);
        unsigned shift=exponent+1;
#endif
        stats.changed+=(a!=re)+(b!=im);
        if(shift>stats.maximum_shift)stats.maximum_shift=shift;
    }
}
#endif

static int32_t bits(uint32_t x) { int32_t s; memcpy(&s, &x, 4); return s; }
static int32_t add(int32_t a, int32_t b) { return bits((uint32_t)a + (uint32_t)b); }
static int32_t neg(int32_t a) { return bits(0u - (uint32_t)a); }
static int32_t shl(int32_t a, unsigned n) { return bits((uint32_t)a << n); }
static int32_t mulhi(int32_t a, int32_t b) { return (int32_t)(((int64_t)a * b) >> 32); }
static int32_t complex_mul(int32_t a, int32_t b, int32_t phase) {
    return add(mulhi(a, bits((uint32_t)phase & 0xffff0000u)), mulhi(b, shl(phase, 16)));
}

static void load(const int32_t *r, const int32_t *i, int32_t *re, int32_t *im) {
    if (selected == 1) {
        if (repetition == 1) assert((uint32_t)*i == GUARD);
        pc14_unpack((uint32_t)*r, PC14_MIDPOINT, re, im);
    } else { *re = *r; *im = *i; }
}

static void save(int32_t *r, int32_t *i, int32_t re, int32_t im) {
    ++stats.stores;
    if (selected == 1) {
        unsigned clipped;
        uint32_t word = pc14_pack(re, im, PC14_MIDPOINT, &clipped);
        assert(!clipped); // Midpoint cell-index packing covers every int32 pair.
        *r = bits(word); // One real-array word owns the complete complex pair.
        if (repetition == 1) {
            assert((uint32_t)*i == GUARD);
            int32_t a, b; pc14_unpack(word, PC14_MIDPOINT, &a, &b);
            stats.changed += (a != re) + (b != im);
            unsigned shift = (word >> 28) + 3;
            if (shift > stats.maximum_shift) stats.maximum_shift = shift;
        }
    } else { *r = re; *i = im; }
}

// Only the four delay families are compacted. Hybrid analysis, energy, mixing,
// phase coefficients, SBR QMF and native arithmetic remain unchanged.
#ifndef CONFIG_YORADIO_QEMU_AAC_PC16_WRITE_TEST
static void visit_span(aac_sbr_owner_abi_t *owner, int32_t *r, int32_t *i, unsigned n, bool initialize) {
    aac_sbr_ps_overlay_abi_t *workspace = &owner->channel[1].ps_overlay;
    uintptr_t low = (uintptr_t)workspace->peak, high = (uintptr_t)&workspace->relocated_ps;
    assert((uintptr_t)r >= low && (uintptr_t)r + 4*n <= high && !((uintptr_t)r & 3));
    assert((uintptr_t)i >= low && (uintptr_t)i + 4*n <= high && !((uintptr_t)i & 3));
    assert((uintptr_t)r + 4*n <= (uintptr_t)i || (uintptr_t)i + 4*n <= (uintptr_t)r);
    for (unsigned k = 0; k < n; ++k) {
        if (initialize) {
            unsigned clipped;
            r[k] = bits(pc14_pack(r[k], i[k], PC14_MIDPOINT, &clipped));
            assert(!clipped); i[k] = bits(GUARD);
        } else { assert((uint32_t)i[k] == GUARD); ++stats.guards; }
    }
    if (initialize) stats.pairs += n;
}
#endif

static void visit_delays(ps_prefix_t *ps, bool initialize) {
    aac_sbr_owner_abi_t *owner = ps_owner(ps);
#ifdef CONFIG_YORADIO_QEMU_AAC_PC16_WRITE_TEST
    bool seen[AAC_PS_PACKED_PAIRS]={0};unsigned pairs=0;
    uint32_t *mantissas = owner->channel[1].packed_ps.mantissas;
#define CHECK_SPAN(r,i,n) do { \
    assert((r)==(i)); \
    assert((uintptr_t)(r) >= (uintptr_t)mantissas); \
    size_t delta=(uintptr_t)(r)-(uintptr_t)mantissas; \
    assert(delta % sizeof(*mantissas) == 0); \
    size_t begin=delta/sizeof(*mantissas); \
    assert(begin+(n)<=AAC_PS_PACKED_PAIRS); \
    for(unsigned k=0;k<(n);++k){assert(!seen[begin+k]);seen[begin+k]=true;++pairs;} \
} while(0)
    for(unsigned b=0;b<61;++b){unsigned n=b<20?2:b<32?14:1;CHECK_SPAN(ps->delay_real[b],ps->delay_imag[b],n);}
    for(unsigned b=0;b<10;++b)CHECK_SPAN(ps->sub_delay_real[b],ps->sub_delay_imag[b],2);
    for(unsigned link=0;link<3;++link)for(unsigned row=0;row<link+3;++row){
        CHECK_SPAN(ps->serial_real[link][row],ps->serial_imag[link][row],20);
        CHECK_SPAN(ps->sub_serial_real[link][row],ps->sub_serial_imag[link][row],10);
    }
#undef CHECK_SPAN
    assert(pairs==AAC_PS_PACKED_PAIRS);
#ifdef CONFIG_YORADIO_QEMU_AAC_PS_STORAGE_TEST
    uint32_t *guard=(void *)((uint8_t *)&owner->channel[1] +
        offsetof(aac_ps_storage_experiment_t,mantissas) +
        pc_storage_bytes(experiment_format,AAC_PS_PACKED_PAIRS));
#else
    uint32_t *guard=((packed_guard_view_t *)&owner->channel[1])->guard;
#endif
    for(unsigned n=0;n<4;++n){if(initialize)guard[n]=GUARD;else assert(guard[n]==GUARD);}
    if(initialize)stats.pairs+=pairs;else stats.guards+=pairs;
#else
    for (unsigned b = 0; b < 61; ++b)
        visit_span(owner, ps->delay_real[b], ps->delay_imag[b], b < 20 ? 2 : b < 32 ? 14 : 1, initialize);
    for (unsigned b = 0; b < 10; ++b)
        visit_span(owner, ps->sub_delay_real[b], ps->sub_delay_imag[b], 2, initialize);
    for (unsigned link = 0; link < 3; ++link) {
        assert(aRevLinkDelaySer[link] == link + 3);
        for (unsigned row = 0; row < link + 3; ++row) {
            visit_span(owner, ps->serial_real[link][row], ps->serial_imag[link][row], 20, initialize);
            visit_span(owner, ps->sub_serial_real[link][row], ps->sub_serial_imag[link][row], 10, initialize);
        }
    }
#endif
}

void __wrap_ps_allocate_decoder(void *owner, uint32_t samples) {
#ifdef CONFIG_YORADIO_QEMU_AAC_PC16_WRITE_TEST
    if(!candidate_selected()){__real_ps_allocate_decoder(owner,samples);return;}
    ps_prefix_t *ps=((aac_sbr_owner_abi_t *)owner)->ps;
    bool initialize=true;
    for(unsigned n=0;n<owner_count;++n)if(owners[n]==ps)initialize=false;
    aac_ps_pc16_allocate(owner,samples,initialize);
    if(!initialize){visit_delays(ps,false);return;}
    assert(owner_count<2);owners[owner_count++]=ps;
    visit_delays(ps,true);++stats.allocations;
#else
    __real_ps_allocate_decoder(owner, samples);
    if (selected != 1) return;
    ps_prefix_t *ps=((aac_sbr_owner_abi_t *)owner)->ps;
    // The harness resets owner tracking between independent decoder lifetimes.
    // Reinitializing the same live PS object retains its already packed delays.
    for (unsigned n = 0; n < owner_count; ++n) if (owners[n] == ps) {
        visit_delays(ps, false); return;
    }
    assert(owner_count < 2); owners[owner_count++] = ps;
    visit_delays(ps, true); ++stats.allocations;
#endif
}

static void allpass(ps_prefix_t *ps, unsigned band, bool hybrid, int32_t *r, int32_t *i) {
    const int32_t *phase = hybrid ? aaFractDelayPhaseFactorSerSubQmf[band] : aaFractDelayPhaseFactorSerQmf[band];
    static const int16_t hybrid_decay[3] = {0x5362, 0x4849, 0x7d53};
    const int16_t *decay = hybrid ? hybrid_decay : aRevLinkDecaySerCoeff[band + 3];
    for (unsigned link = 0; link < 3; ++link) {
        unsigned row = ps->serial_index[link]; assert(row < link + 3);
        int32_t *pr = hybrid ? &ps->sub_serial_real[link][row][band] : &ps->serial_real[link][row][band];
        int32_t *pi = hybrid ? &ps->sub_serial_imag[link][row][band] : &ps->serial_imag[link][row][band];
        int32_t dr, di; load(pr, pi, &dr, &di);
        dr = shl(dr, 1); di = shl(di, 1);
        int32_t rr = complex_mul(dr, neg(di), phase[link]);
        int32_t ii = complex_mul(di, dr, phase[link]);
        int32_t coefficient = shl((int32_t)decay[link], 16);
        unsigned shift = link < 2 ? 1 : 0;
        rr = add(rr, mulhi(shl(neg(*r), shift), coefficient));
        ii = add(ii, mulhi(shl(neg(*i), shift), coefficient));
        int32_t next_r = add(*r, mulhi(shl(rr, shift), coefficient));
        int32_t next_i = add(*i, mulhi(shl(ii, shift), coefficient));
        save(pr, pi, next_r, next_i);
        *r = link < 2 ? rr : shl(rr, 2);
        *i = link < 2 ? ii : shl(ii, 2);
    }
}

static void transient(int32_t factor, int32_t *r, int32_t *i) {
    if (factor != INT32_MAX) {
        *r = shl(mulhi(factor, *r), 1); *i = shl(mulhi(factor, *i), 1);
    }
}

void __wrap_ps_decorrelate(void *state, int32_t *lr, int32_t *li, int32_t *rr, int32_t *ri, int32_t *scratch) {
    if (!selected) { __real_ps_decorrelate(state, lr, li, rr, ri, scratch); return; }
    ps_prefix_t *ps = state;
    assert(candidate_selected() || selected == 7);
    assert(ps->delay_index >= 0 && ps->delay_index < 2);
    int32_t usb=ps->upper_subband; assert(usb >= 0 && usb <= 64);
    ++stats.calls;
#ifdef CONFIG_YORADIO_QEMU_AAC_PC16_WRITE_TEST
    if(candidate_selected()){aac_ps_pc16_decode(ps_owner(ps),state,lr,li,rr,ri,scratch);return;}
#endif
    ps_pwr_transient_detection(state, lr, li, scratch);
    for (unsigned gr = 0; gr < 10; ++gr) {
        unsigned band = (unsigned)groupBorders[gr]; assert(band < 10);
        int32_t *pr = &ps->sub_delay_real[band][ps->delay_index], *pi = &ps->sub_delay_imag[band][ps->delay_index];
        int32_t a, b; load(pr, pi, &a, &b);
        save(pr, pi, ps->hybrid_left_real[band], ps->hybrid_left_imag[band]);
        a >>= 1; b >>= 1;
        int32_t r = complex_mul(a, neg(b), aFractDelayPhaseFactorSubQmf[band]);
        int32_t i = complex_mul(b, a, aFractDelayPhaseFactorSubQmf[band]);
        allpass(ps, band, true, &r, &i);
        transient(scratch[(unsigned)bins2groupMap[gr]], &r, &i);
        ps->hybrid_right_real[band] = r; ps->hybrid_right_imag[band] = i;
    }
    for (unsigned gr = 10; gr < 20; ++gr) {
        unsigned end = usb < groupBorders[gr+1] ? (unsigned)usb : (unsigned)groupBorders[gr+1];
        for (unsigned band = (unsigned)groupBorders[gr]; band < end; ++band) {
            unsigned index = band - 3;
            int32_t *pr = &ps->delay_real[index][ps->delay_index], *pi = &ps->delay_imag[index][ps->delay_index];
            int32_t a, b; load(pr, pi, &a, &b); save(pr, pi, lr[band], li[band]);
            a >>= 1; b >>= 1;
            int32_t r = complex_mul(a, neg(b), aFractDelayPhaseFactor[index]);
            int32_t i = complex_mul(b, a, aFractDelayPhaseFactor[index]);
            allpass(ps, index, false, &r, &i); transient(scratch[gr-2], &r, &i);
            rr[band] = r; ri[band] = i;
        }
    }
    for (unsigned band = 23; band < (unsigned)usb; ++band) {
        unsigned index = band - 3, row = 0;
        if (band < 35) {
            assert(ps->long_index[band-23] >= 0 && ps->long_index[band-23] < 14);
            row = (unsigned)ps->long_index[band-23];
            ps->long_index[band-23] = (row + 1) % 14;
        }
        int32_t *pr = &ps->delay_real[index][row], *pi = &ps->delay_imag[index][row];
        int32_t r, i; load(pr, pi, &r, &i); save(pr, pi, lr[band], li[band]);
        transient(scratch[band < 35 ? 18 : 19], &r, &i); rr[band] = r; ri[band] = i;
    }
    ps->delay_index = (ps->delay_index + 1) & 1;
    for (unsigned link = 0; link < 3; ++link)
        ps->serial_index[link] = (ps->serial_index[link] + 1) % (link + 3);
}

void packed_history_reset(unsigned run) {
    memset(&stats, 0, sizeof(stats)); memset(owners, 0, sizeof(owners));
    owner_count = selected = 0; repetition = run;
}
void packed_history_select(unsigned variant) {
    selected = variant;
    assert(variant == 0 || candidate_selected() || variant == 7);
#ifdef CONFIG_YORADIO_QEMU_AAC_PS_STORAGE_TEST
    if(candidate_selected()) {
        experiment_format=(pc_storage_format_t)variant;
        aac_ps_storage_select(experiment_format);
    }
#endif
}
void packed_history_report(const char *name, unsigned variant, unsigned run, uint32_t *rows, uint32_t *changed, unsigned *shift) {
    for (unsigned n = 0; n < owner_count; ++n) visit_delays(owners[n], false);
    assert(stats.pairs == stats.allocations * 617u && stats.guards >= stats.pairs);
    *rows = stats.calls; *changed = stats.changed; *shift = stats.maximum_shift;
    ESP_LOGI(TAG, PS_TEST_NAME "_STORAGE case=%s variant=%u run=%u calls=%" PRIu32 " stores=%" PRIu32
             " allocations=%" PRIu32 " pairs=%" PRIu32 " guards=%" PRIu32 " saturations=%" PRIu32
             " cache_bytes=%" PRIu32 " cache_hits=%" PRIu32 " cache_misses=%" PRIu32
#ifdef CONFIG_YORADIO_QEMU_AAC_PS_STORAGE_TEST
             " native_payload=4936 packed_payload=%u heap_saved=0",
#elif defined(CONFIG_YORADIO_QEMU_AAC_PC16_WRITE_TEST)
             " native_payload=4936 packed_payload=2780 heap_saved=0",
#else
             " native_payload=4936 packed_payload=2468 heap_saved=0",
#endif
             name, variant, run, stats.calls, stats.stores, stats.allocations, stats.pairs, stats.guards, stats.saturations,
             stats.cache_bytes,stats.cache_hits,stats.cache_misses
#ifdef CONFIG_YORADIO_QEMU_AAC_PS_STORAGE_TEST
             #ifdef CONFIG_YORADIO_QEMU_AAC_COMBINED_STORAGE_TEST
             ,(unsigned)pc_storage_bytes(aac_combined_ps_format(variant),AAC_PS_PACKED_PAIRS)
#else
             ,(unsigned)pc_storage_bytes(variant>=PC_STORAGE_SHARED16 && variant<=PC_STORAGE_SHARED18_FOUR ? (pc_storage_format_t)variant : PC_STORAGE_SHARED16,AAC_PS_PACKED_PAIRS)
#endif
#endif
             );
}
void packed_history_arithmetic_tests(void) {
    assert(mulhi(INT32_MIN, INT32_MIN) == 0x40000000);
    assert(add(INT32_MAX, 1) == INT32_MIN && shl(INT32_MIN, 1) == 0);
    uint32_t rng = 0x50535031;
    for (unsigned n = 0; n < 100000; ++n) {
        rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5; int32_t re = bits(rng);
        rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5; int32_t im = bits(rng);
#ifdef CONFIG_YORADIO_QEMU_AAC_PC16_WRITE_TEST
        unsigned ea,eb,ca,cb;
        assert(pc16_pack_fast(re,im,&ea,&ca)==pc16_pack(re,im,&eb,&cb));
        assert(ea==eb && ca==cb);
#endif
        unsigned clipped; uint32_t word = pc14_pack(re, im, PC14_MIDPOINT, &clipped);
        assert(!clipped);
        unsigned s = (word >> 28) + 3;
        uint32_t expected = ((uint32_t)(re >> s) & 0x3fff) | (((uint32_t)(im >> s) & 0x3fff) << 14) | ((s-3) << 28);
        assert(word == expected);
    }
    ESP_LOGI(TAG, PS_TEST_NAME "_ARITHMETIC_PASS pairs=100000 storage control");
}
