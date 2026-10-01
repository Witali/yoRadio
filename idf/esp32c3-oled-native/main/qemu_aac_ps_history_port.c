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
#include "packed_complex14.h"
#include "esp_log.h"
#include <assert.h>
#include <inttypes.h>
#include <stddef.h>
#include <stdbool.h>
#include <string.h>

typedef struct {
    uint8_t parameters[0x190];
    int32_t delay_index;
    uint32_t serial_index[3];
    int32_t **serial_real[3], **serial_imag[3];
    int32_t **sub_serial_real[3], **sub_serial_imag[3];
    int32_t **delay_real, **delay_imag, **sub_delay_real, **sub_delay_imag;
    int32_t *peak, *previous_energy, *previous_peak_difference;
    int32_t *hybrid_left_real, *hybrid_left_imag, *hybrid_right_real, *hybrid_right_imag;
    void *hybrid;
    uint8_t mixing_and_qmf_pointers[0x428];
    int32_t long_index[41];
} ps_prefix_t;
_Static_assert(sizeof(void *) == 4, "Only the pinned RV32 ABI is supported");
_Static_assert(offsetof(ps_prefix_t, serial_real) == 0x1a0, "PS serial ABI");
_Static_assert(offsetof(ps_prefix_t, delay_real) == 0x1d0, "PS delay ABI");
_Static_assert(offsetof(ps_prefix_t, hybrid) == 0x1fc, "PS hybrid ABI");
_Static_assert(offsetof(ps_prefix_t, long_index) == 0x628, "PS delay index ABI");

extern const int8_t groupBorders[], bins2groupMap[];
extern const int32_t aRevLinkDelaySer[3], aFractDelayPhaseFactor[], aFractDelayPhaseFactorSubQmf[];
extern const int32_t aaFractDelayPhaseFactorSerQmf[][3], aaFractDelayPhaseFactorSerSubQmf[][3];
extern const int16_t aRevLinkDecaySerCoeff[][3];
extern void ps_pwr_transient_detection(void *, int32_t *, int32_t *, int32_t *);
void __real_ps_decorrelate(void *, int32_t *, int32_t *, int32_t *, int32_t *, int32_t *);
void __real_ps_allocate_decoder(void *, uint32_t);

static unsigned selected, repetition;
static struct {
    uint32_t calls, stores, changed, maximum_shift, allocations, pairs, guards;
} stats;
static ps_prefix_t *owners[2];
static unsigned owner_count;
#define GUARD UINT32_C(0xd3adbeef)
static const char *TAG = "ps_port";

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
static void visit_span(uint8_t *owner, int32_t *r, int32_t *i, unsigned n, bool initialize) {
    uintptr_t low = (uintptr_t)owner + 0x7678, high = (uintptr_t)owner + 0x93b4;
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

static void visit_delays(ps_prefix_t *ps, bool initialize) {
    uint8_t *owner = (uint8_t *)ps - 0xc988;
    void *declared; memcpy(&declared, owner + 0xc984, 4); assert(declared == ps);
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
}

void __wrap_ps_allocate_decoder(void *owner, uint32_t samples) {
    __real_ps_allocate_decoder(owner, samples);
    if (selected != 1) return;
    ps_prefix_t *ps; memcpy(&ps, (uint8_t *)owner + 0xc984, 4);
    // The harness resets owner tracking between independent decoder lifetimes.
    // Reinitializing the same live PS object retains its already packed delays.
    for (unsigned n = 0; n < owner_count; ++n) if (owners[n] == ps) {
        visit_delays(ps, false); return;
    }
    assert(owner_count < 2); owners[owner_count++] = ps;
    visit_delays(ps, true); ++stats.allocations;
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
    assert(selected == 1 || selected == 7);
    assert(ps->delay_index >= 0 && ps->delay_index < 2);
    int32_t usb; memcpy(&usb, (uint8_t *)state + 0x14, 4); assert(usb >= 0 && usb <= 64);
    ++stats.calls;
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
void packed_history_select(unsigned variant) { assert(variant == 0 || variant == 1 || variant == 7); selected = variant; }
void packed_history_report(const char *name, unsigned variant, unsigned run, uint32_t *rows, uint32_t *changed, unsigned *shift) {
    for (unsigned n = 0; n < owner_count; ++n) visit_delays(owners[n], false);
    assert(stats.pairs == stats.allocations * 617u && stats.guards >= stats.pairs);
    *rows = stats.calls; *changed = stats.changed; *shift = stats.maximum_shift;
    ESP_LOGI(TAG, "PSPORT_STORAGE case=%s variant=%u run=%u calls=%" PRIu32 " stores=%" PRIu32
             " allocations=%" PRIu32 " pairs=%" PRIu32 " guards=%" PRIu32
             " native_payload=4936 packed_payload=2468 heap_saved=0",
             name, variant, run, stats.calls, stats.stores, stats.allocations, stats.pairs, stats.guards);
}
void packed_history_arithmetic_tests(void) {
    assert(mulhi(INT32_MIN, INT32_MIN) == 0x40000000);
    assert(add(INT32_MAX, 1) == INT32_MIN && shl(INT32_MIN, 1) == 0);
    uint32_t rng = 0x50535031;
    for (unsigned n = 0; n < 100000; ++n) {
        rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5; int32_t re = bits(rng);
        rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5; int32_t im = bits(rng);
        unsigned clipped; uint32_t word = pc14_pack(re, im, PC14_MIDPOINT, &clipped);
        assert(!clipped);
        unsigned s = (word >> 28) + 3;
        uint32_t expected = ((uint32_t)(re >> s) & 0x3fff) | (((uint32_t)(im >> s) & 0x3fff) << 14) | ((s-3) << 28);
        assert(word == expected);
    }
    ESP_LOGI(TAG, "PSPORT_ARITHMETIC_PASS pairs=100000 midpoint storage");
}
