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

// Source PS storage port for the pinned Espressif 2.6.2 RV32 decoder.
// Arithmetic is int32; only decorrelation delay storage uses 16+16 plus nibbles.
#include "sdkconfig.h"
#include "packed_complex16_fast.h"
#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
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

static int32_t bits(uint32_t x) { int32_t s; memcpy(&s, &x, 4); return s; }
static int32_t add(int32_t a, int32_t b) { return bits((uint32_t)a + (uint32_t)b); }
static int32_t neg(int32_t a) { return bits(0u - (uint32_t)a); }
static int32_t shl(int32_t a, unsigned n) { return bits((uint32_t)a << n); }
static int32_t mulhi(int32_t a, int32_t b) { return (int32_t)(((int64_t)a * b) >> 32); }
static int32_t complex_mul(int32_t a, int32_t b, int32_t phase) {
    return add(mulhi(a, bits((uint32_t)phase & 0xffff0000u)), mulhi(b, shl(phase, 16)));
}


#define PC16_DATA 0x7b24u
#define PC16_EXPONENTS 0x84c8u
#define PC16_END 0x8600u
#define PAIRS 617u
_Static_assert(PC16_DATA+4*PAIRS==PC16_EXPONENTS,"Contiguous mantissas");
_Static_assert(PC16_EXPONENTS+4*((PAIRS+7)/8)==PC16_END,"Packed exponent words");
_Static_assert(PC16_END<0x93b4,"Packed history must precede relocated PS control");
typedef struct { uint32_t *mantissas,*exponents; } storage_t;
#ifdef CONFIG_YORADIO_QEMU_AAC_PC16_WRITE_TEST
void aac_ps_pc16_test_store(uint32_t,unsigned,int32_t,int32_t,unsigned);
#endif
static void load(const storage_t *s,const int32_t *r,const int32_t *i,int32_t *re,int32_t *im) {
    (void)i;size_t n=(const uint32_t*)r-s->mantissas;assert(n<PAIRS);
    pc16_load(s->mantissas,s->exponents,n,re,im);
}
static void save(const storage_t *s,int32_t *r,int32_t *i,int32_t re,int32_t im) {
    (void)i;size_t n=(uint32_t*)r-s->mantissas;assert(n<PAIRS);
    unsigned exponent,clipped,bit=(n&7u)*4u;
    uint32_t packed=pc16_pack_fast(re,im,&exponent,&clipped);
    s->mantissas[n]=packed;
    s->exponents[n/8u]=(s->exponents[n/8u]&~(15u<<bit))|(exponent<<bit);
#ifdef CONFIG_YORADIO_QEMU_AAC_PC16_WRITE_TEST
    aac_ps_pc16_test_store(packed,exponent,re,im,clipped);
#endif
}

int ps_hybrid_filter_bank_allocation(void **,int,const int32_t *,void **);
void aac_ps_pc16_allocate(void *owner,uint32_t samples,bool initialize) {
    assert(samples==32); // Pinned controller always requests 32 QMF slots.
    uint8_t *base=owner;ps_prefix_t *ps;memcpy(&ps,base+0xc984,4);
    ((uint32_t*)ps)[4]=samples;((uint32_t*)ps)[2]=0x40000000u/samples;
    ps->peak=(int32_t*)(base+0x7678);
    ps->previous_energy=ps->peak+20;ps->previous_peak_difference=ps->peak+40;
    void *cursor=base+0x7768;const int32_t resolution[3]={8,2,2};
    int result=ps_hybrid_filter_bank_allocation(&ps->hybrid,3,resolution,&cursor);
    assert(!result);
    (void)result;
    ps->hybrid_left_real=cursor;ps->hybrid_left_imag=ps->hybrid_left_real+10;
    ps->hybrid_right_real=ps->hybrid_left_real+20;ps->hybrid_right_imag=ps->hybrid_left_real+30;
    int32_t **table=(int32_t**)(ps->hybrid_left_real+40);
    ps->delay_real=ps->delay_imag=table;table+=61;
    ps->sub_delay_real=ps->sub_delay_imag=table;table+=10;
    for(unsigned link=0;link<3;++link){ps->serial_real[link]=ps->serial_imag[link]=table;table+=link+3;}
    for(unsigned link=0;link<3;++link){ps->sub_serial_real[link]=ps->sub_serial_imag[link]=table;table+=link+3;}
    assert((uint8_t*)table==base+PC16_DATA);
    int32_t *data=(int32_t*)table;
    for(unsigned b=0;b<61;++b){ps->delay_real[b]=data;data+=b<20?2:b<32?14:1;}
    for(unsigned b=0;b<10;++b){ps->sub_delay_real[b]=data;data+=2;}
    for(unsigned link=0;link<3;++link)for(unsigned row=0;row<link+3;++row){ps->serial_real[link][row]=data;data+=20;}
    for(unsigned link=0;link<3;++link)for(unsigned row=0;row<link+3;++row){ps->sub_serial_real[link][row]=data;data+=10;}
    assert((uint8_t*)data==base+PC16_EXPONENTS);
    if(initialize)memset(base+PC16_DATA,0,PC16_END-PC16_DATA);
    ps->delay_index=0;
    for(unsigned link=0;link<3;++link)ps->serial_index[link]=0;
    uint32_t *lengths=(uint32_t*)((uint8_t*)ps+0x6cc);
    for(unsigned b=0;b<41;++b)lengths[b]=b<12?14:1;
    int32_t *mix=(int32_t*)((uint8_t*)ps+0x200);
    for(unsigned b=0;b<22;++b){mix[b]=0x40000000;mix[b+22]=0x40000000;}
}
static void allpass(const storage_t *storage,ps_prefix_t *ps, unsigned band, bool hybrid, int32_t *r, int32_t *i) {
    const int32_t *phase = hybrid ? aaFractDelayPhaseFactorSerSubQmf[band] : aaFractDelayPhaseFactorSerQmf[band];
    static const int16_t hybrid_decay[3] = {0x5362, 0x4849, 0x7d53};
    const int16_t *decay = hybrid ? hybrid_decay : aRevLinkDecaySerCoeff[band + 3];
    for (unsigned link = 0; link < 3; ++link) {
        unsigned row = ps->serial_index[link]; assert(row < link + 3);
        int32_t *pr = hybrid ? &ps->sub_serial_real[link][row][band] : &ps->serial_real[link][row][band];
        int32_t *pi = hybrid ? &ps->sub_serial_imag[link][row][band] : &ps->serial_imag[link][row][band];
        int32_t dr, di; load(storage,pr, pi, &dr, &di);
        dr = shl(dr, 1); di = shl(di, 1);
        int32_t rr = complex_mul(dr, neg(di), phase[link]);
        int32_t ii = complex_mul(di, dr, phase[link]);
        int32_t coefficient = shl((int32_t)decay[link], 16);
        unsigned shift = link < 2 ? 1 : 0;
        rr = add(rr, mulhi(shl(neg(*r), shift), coefficient));
        ii = add(ii, mulhi(shl(neg(*i), shift), coefficient));
        int32_t next_r = add(*r, mulhi(shl(rr, shift), coefficient));
        int32_t next_i = add(*i, mulhi(shl(ii, shift), coefficient));
        save(storage,pr, pi, next_r, next_i);
        *r = link < 2 ? rr : shl(rr, 2);
        *i = link < 2 ? ii : shl(ii, 2);
    }
}

static void transient(int32_t factor, int32_t *r, int32_t *i) {
    if (factor != INT32_MAX) {
        *r = shl(mulhi(factor, *r), 1); *i = shl(mulhi(factor, *i), 1);
    }
}

void aac_ps_pc16_decode(void *owner,void *state,int32_t *lr,int32_t *li,int32_t *rr,int32_t *ri,int32_t *scratch) {
    ps_prefix_t *ps=state;
    storage_t storage={(uint32_t*)((uint8_t*)owner+PC16_DATA),(uint32_t*)((uint8_t*)owner+PC16_EXPONENTS)};
    assert(ps->delay_index >= 0 && ps->delay_index < 2);
    int32_t usb; memcpy(&usb, (uint8_t *)state + 0x14, 4); assert(usb >= 0 && usb <= 64);
    ps_pwr_transient_detection(state, lr, li, scratch);
    for (unsigned gr = 0; gr < 10; ++gr) {
        unsigned band = (unsigned)groupBorders[gr]; assert(band < 10);
        int32_t *pr = &ps->sub_delay_real[band][ps->delay_index], *pi = &ps->sub_delay_imag[band][ps->delay_index];
        int32_t a, b; load(&storage,pr, pi, &a, &b);
        save(&storage,pr, pi, ps->hybrid_left_real[band], ps->hybrid_left_imag[band]);
        a >>= 1; b >>= 1;
        int32_t r = complex_mul(a, neg(b), aFractDelayPhaseFactorSubQmf[band]);
        int32_t i = complex_mul(b, a, aFractDelayPhaseFactorSubQmf[band]);
        allpass(&storage,ps, band, true, &r, &i);
        transient(scratch[(unsigned)bins2groupMap[gr]], &r, &i);
        ps->hybrid_right_real[band] = r; ps->hybrid_right_imag[band] = i;
    }
    for (unsigned gr = 10; gr < 20; ++gr) {
        unsigned end = usb < groupBorders[gr+1] ? (unsigned)usb : (unsigned)groupBorders[gr+1];
        for (unsigned band = (unsigned)groupBorders[gr]; band < end; ++band) {
            unsigned index = band - 3;
            int32_t *pr = &ps->delay_real[index][ps->delay_index], *pi = &ps->delay_imag[index][ps->delay_index];
            int32_t a, b; load(&storage,pr, pi, &a, &b); save(&storage,pr, pi, lr[band], li[band]);
            a >>= 1; b >>= 1;
            int32_t r = complex_mul(a, neg(b), aFractDelayPhaseFactor[index]);
            int32_t i = complex_mul(b, a, aFractDelayPhaseFactor[index]);
            allpass(&storage,ps, index, false, &r, &i); transient(scratch[gr-2], &r, &i);
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
        int32_t r, i; load(&storage,pr, pi, &r, &i); save(&storage,pr, pi, lr[band], li[band]);
        transient(scratch[band < 35 ? 18 : 19], &r, &i); rr[band] = r; ri[band] = i;
    }
    ps->delay_index = (ps->delay_index + 1) & 1;
    for (unsigned link = 0; link < 3; ++link)
        ps->serial_index[link] = (ps->serial_index[link] + 1) % (link + 3);
}
