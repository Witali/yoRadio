// Exact owned-VQ adapter. This test reads actual packets and captures raw outputs.
#include "native_vorbis_quant.h"
#include <assert.h>
#include <float.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

_Static_assert(sizeof(double)==8 && DBL_MANT_DIG==53, "IEEE binary64 capture");
_Static_assert(sizeof(native_vorbis_affine_t)==16, "four exact uint32 fields");
static const uint64_t CANARY=UINT64_C(0x71a50c389d42ef06);
static uint64_t get(FILE *f,unsigned n) { uint64_t x=0;for(unsigned i=0;i<n;i++){int c=fgetc(f);assert(c!=EOF);x|=(uint64_t)(unsigned)c<<(8*i);}return x; }
static void put(FILE *f,uint64_t x,unsigned n) {for(unsigned i=0;i<n;i++)assert(fputc((int)((x>>(8*i))&255),f)!=EOF);}
static uint64_t bits(double x) {uint64_t b;memcpy(&b,&x,8);return b;}
static void affine_put(FILE *f,native_vorbis_affine_t x) {put(f,x.minimum_bits,4);put(f,x.delta_bits,4);put(f,x.minimum_multiplier,4);put(f,x.delta_multiplier,4);}
static native_vorbis_affine_t affine_get(FILE *f) {native_vorbis_affine_t x;x.minimum_bits=(uint32_t)get(f,4);x.delta_bits=(uint32_t)get(f,4);x.minimum_multiplier=(uint32_t)get(f,4);x.delta_multiplier=(uint32_t)get(f,4);return x;}
static void layout_put(FILE *f,native_vorbis_quant_layout_t x) {
    put(f,x.dimensions,4);put(f,x.entries,4);put(f,x.lookup_type,4);put(f,x.minimum_bits,4);
    put(f,x.delta_bits,4);put(f,x.value_bits,4);put(f,x.sequence_p,4);put(f,x.multiplicand_count,8);
    put(f,x.start_bit,8);put(f,x.multiplicand_bit,8);put(f,x.end_bit,8);
}
static void write_bits(uint8_t *p,uint64_t *at,uint32_t x,unsigned n) {for(unsigned i=0;i<n;i++,(*at)++)if((x>>i)&1)p[*at/8]|=(uint8_t)(1u<<(*at%8));}
static unsigned controls(void) {
    unsigned n=0;uint64_t required=CANARY;
#define CHECK(call,code,object) do { unsigned char saved[sizeof(object)];memcpy(saved,&(object),sizeof(object));assert((call)==(code));assert(!memcmp(saved,&(object),sizeof(object)));n++;}while(0)
    CHECK(native_vorbis_quantization_count(65536,1,1,&required),NATIVE_VORBIS_NUMERIC_INVALID,required);
    CHECK(native_vorbis_quantization_count(1,0x1000000,1,&required),NATIVE_VORBIS_NUMERIC_INVALID,required);
    CHECK(native_vorbis_quantization_count(0,1,1,&required),NATIVE_VORBIS_NUMERIC_INVALID,required);
    CHECK(native_vorbis_quantization_count(1,1,3,&required),NATIVE_VORBIS_NUMERIC_INVALID,required);
    assert(native_vorbis_quantization_count(65535,0xffffff,2,&required)==0 && required==UINT64_C(1099494785025));n++;
    assert(native_vorbis_quantization_count(65535,2,1,&required)==0 && required==1);n++;
    assert(native_vorbis_quantization_count(0,0,2,&required)==0 && required==0);n++;
    CHECK(native_vorbis_quantization_count(1,1,1,NULL),NATIVE_VORBIS_NUMERIC_INVALID,required);
    uint8_t packet[16]={0};uint64_t end=5;write_bits(packet,&end,2,4);write_bits(packet,&end,0x80000000,32);
    write_bits(packet,&end,UINT32_C(0x62800001),32);write_bits(packet,&end,2,4);write_bits(packet,&end,1,1);
    for(unsigned i=1;i<=6;i++)write_bits(packet,&end,i,3);
    struct {uint64_t a;native_vorbis_quant_layout_t x;uint64_t z;} l;memset(&l,0xa5,sizeof(l));l.a=l.z=CANARY;
    assert(native_vorbis_quantization_measure(packet,sizeof(packet),end,5,3,2,&l.x)==0);n++;
    native_vorbis_quant_layout_t layout=l.x;
    assert(layout.multiplicand_count==6 && layout.minimum_bits==0x80000000 && layout.delta_bits==UINT32_C(0x62800001));
    for(uint64_t cut=9;cut<end;cut++)CHECK(native_vorbis_quantization_measure(packet,sizeof(packet),cut,5,3,2,&l.x),NATIVE_VORBIS_NUMERIC_TRUNCATED,l);
    CHECK(native_vorbis_quantization_measure(packet,sizeof(packet),129,5,3,2,&l.x),NATIVE_VORBIS_NUMERIC_INVALID,l);
    CHECK(native_vorbis_quantization_measure(NULL,sizeof(packet),end,5,3,2,&l.x),NATIVE_VORBIS_NUMERIC_INVALID,l);
    CHECK(native_vorbis_quantization_measure(packet,sizeof(packet),end,5,3,2,NULL),NATIVE_VORBIS_NUMERIC_INVALID,l);
    struct {uint64_t a;uint16_t x[6];uint64_t z;} s;memset(&s,0xa5,sizeof(s));s.a=s.z=CANARY;
    struct {uint64_t a;native_vorbis_quantization_t x;uint64_t z;} b;memset(&b,0xa5,sizeof(b));b.a=b.z=CANARY;
    unsigned char ss[sizeof(s)];memcpy(ss,&s,sizeof(s));
    CHECK(native_vorbis_quantization_materialize(packet,sizeof(packet),end,&layout,s.x,5,&b.x),NATIVE_VORBIS_NUMERIC_CAPACITY,b);assert(!memcmp(ss,&s,sizeof(s)));
    CHECK(native_vorbis_quantization_materialize(packet,sizeof(packet),end-1,&layout,NULL,0,&b.x),NATIVE_VORBIS_NUMERIC_TRUNCATED,b);assert(!memcmp(ss,&s,sizeof(s)));
    native_vorbis_quant_layout_t wrong=layout;wrong.minimum_bits^=1;
    CHECK(native_vorbis_quantization_materialize(packet,sizeof(packet),end,&wrong,s.x,6,&b.x),NATIVE_VORBIS_NUMERIC_INVALID,b);assert(!memcmp(ss,&s,sizeof(s)));
    assert(native_vorbis_quantization_materialize(packet,sizeof(packet),end,&layout,s.x,6,&b.x)==0);n++;
    for(unsigned i=0;i<6;i++)assert(s.x[i]==i+1);
    native_vorbis_quantization_t book=b.x;
    struct {uint64_t a;native_vorbis_affine_t x[255];uint64_t z;} out;memset(&out,0xa5,sizeof(out));out.a=out.z=CANARY;
    CHECK(native_vorbis_quantization_vector(&book,2,1,out.x,255),NATIVE_VORBIS_NUMERIC_INVALID,out);
    CHECK(native_vorbis_quantization_vector(&book,0,4,out.x,255),NATIVE_VORBIS_NUMERIC_INVALID,out);
    CHECK(native_vorbis_quantization_vector(&book,0,3,out.x,2),NATIVE_VORBIS_NUMERIC_CAPACITY,out);
    CHECK(native_vorbis_quantization_vector(&book,0,1,NULL,1),NATIVE_VORBIS_NUMERIC_INVALID,out);
    assert(native_vorbis_quantization_vector(&book,0,0,NULL,0)==0);n++;
    CHECK(native_vorbis_quantization_scalar(&book,0,3,&out.x[0]),NATIVE_VORBIS_NUMERIC_INVALID,out);
    CHECK(native_vorbis_quantization_scalar(&book,2,0,&out.x[0]),NATIVE_VORBIS_NUMERIC_INVALID,out);
    CHECK(native_vorbis_quantization_scalar(&book,0,0,NULL),NATIVE_VORBIS_NUMERIC_INVALID,out);
    CHECK(native_vorbis_quantization_scalar(NULL,0,0,&out.x[0]),NATIVE_VORBIS_NUMERIC_INVALID,out);
    assert(native_vorbis_quantization_scalar(&book,0,2,&out.x[0])==0);n++;
    uint8_t no_packet=0;native_vorbis_quant_layout_t no_layout;native_vorbis_quantization_t no_book;
    assert(native_vorbis_quantization_count(0,0,0,&required)==0 && required==0);n++;
    assert(native_vorbis_quantization_measure(&no_packet,1,4,0,0,0,&no_layout)==0);n++;
    assert(native_vorbis_quantization_materialize(&no_packet,1,4,&no_layout,NULL,0,&no_book)==0);n++;
    CHECK(native_vorbis_quantization_vector(&no_book,0,0,NULL,0),NATIVE_VORBIS_NUMERIC_NO_LOOKUP,out);
    CHECK(native_vorbis_quantization_scalar(&no_book,0,0,&out.x[0]),NATIVE_VORBIS_NUMERIC_NO_LOOKUP,out);
    CHECK(native_vorbis_floor0_lsp_from_entries(&no_book,NULL,0,1,out.x,255),NATIVE_VORBIS_NUMERIC_NO_LOOKUP,out);
    for(uint8_t lookup=3;lookup<16;lookup++)CHECK(native_vorbis_quantization_measure(&lookup,1,4,0,1,1,&l.x),NATIVE_VORBIS_NUMERIC_INVALID,l);
    s.x[5]=8;
    assert(native_vorbis_quantization_vector(&book,1,1,out.x,255)==0);n++;
    CHECK(native_vorbis_quantization_vector(&book,1,3,out.x,255),NATIVE_VORBIS_NUMERIC_INVALID,out);
    uint32_t entries[2]={0,1};
    assert(native_vorbis_floor0_lsp_from_entries(&book,entries,2,4,out.x,255)==0);n++;
    CHECK(native_vorbis_floor0_lsp_from_entries(&book,entries,2,6,out.x,255),NATIVE_VORBIS_NUMERIC_INVALID,out);
    s.x[5]=6;entries[1]=2;
    CHECK(native_vorbis_floor0_lsp_from_entries(&book,entries,2,4,out.x,255),NATIVE_VORBIS_NUMERIC_INVALID,out);
    entries[1]=1;
    CHECK(native_vorbis_floor0_lsp_from_entries(&book,entries,1,4,out.x,255),NATIVE_VORBIS_NUMERIC_INVALID,out);
    CHECK(native_vorbis_floor0_lsp_from_entries(&book,entries,2,4,out.x,3),NATIVE_VORBIS_NUMERIC_CAPACITY,out);
    CHECK(native_vorbis_floor0_lsp_from_entries(&book,NULL,2,4,out.x,255),NATIVE_VORBIS_NUMERIC_INVALID,out);
    CHECK(native_vorbis_floor0_lsp_from_entries(&book,entries,0,0,out.x,255),NATIVE_VORBIS_NUMERIC_INVALID,out);
    CHECK(native_vorbis_floor0_lsp_from_entries(&book,entries,2,256,out.x,255),NATIVE_VORBIS_NUMERIC_INVALID,out);
    native_vorbis_affine_t angle={0,0,UINT32_MAX,UINT32_MAX};
    struct {uint64_t a;native_vorbis_scaled_t x;uint64_t z;} d;memset(&d,0xa5,sizeof(d));d.a=d.z=CANARY;
    struct {uint64_t a;native_vorbis_floor0_gain_t x;uint64_t z;} g;memset(&g,0xa5,sizeof(g));g.a=g.z=CANARY;
    native_vorbis_floor0_amplitude_t amp={1,1,255},absent={0,0,255};
    CHECK(native_vorbis_floor0_denominator_from_affine(NULL,1,0,1,&d.x),NATIVE_VORBIS_NUMERIC_INVALID,d);
    CHECK(native_vorbis_floor0_denominator_from_affine(&angle,0,0,1,&d.x),NATIVE_VORBIS_NUMERIC_INVALID,d);
    CHECK(native_vorbis_floor0_denominator_from_affine(&angle,256,0,1,&d.x),NATIVE_VORBIS_NUMERIC_INVALID,d);
    CHECK(native_vorbis_floor0_denominator_from_affine(&angle,1,0,0,&d.x),NATIVE_VORBIS_NUMERIC_INVALID,d);
    CHECK(native_vorbis_floor0_denominator_from_affine(&angle,1,0,65536,&d.x),NATIVE_VORBIS_NUMERIC_INVALID,d);
    CHECK(native_vorbis_floor0_denominator_from_affine(&angle,1,1,1,&d.x),NATIVE_VORBIS_NUMERIC_INVALID,d);
    CHECK(native_vorbis_floor0_denominator_from_affine(&angle,1,0,1,NULL),NATIVE_VORBIS_NUMERIC_INVALID,d);
    CHECK(native_vorbis_floor0_gain_from_affine(&amp,NULL,1,0,1,&g.x),NATIVE_VORBIS_NUMERIC_INVALID,g);
    CHECK(native_vorbis_floor0_gain_from_affine(NULL,&angle,1,0,1,&g.x),NATIVE_VORBIS_NUMERIC_INVALID,g);
    assert(native_vorbis_floor0_gain_from_affine(&absent,NULL,1,0,1,&g.x)==0 && g.x.kind==NATIVE_VORBIS_FLOOR0_ABSENT);n++;
    assert(l.a==CANARY && l.z==CANARY && s.a==CANARY && s.z==CANARY && b.a==CANARY && b.z==CANARY);
    assert(out.a==CANARY && out.z==CANARY && d.a==CANARY && d.z==CANARY && g.a==CANARY && g.z==CANARY);
#undef CHECK
    return n;
}
static void *guarded(size_t bytes) {uint8_t *p=malloc(bytes+16);assert(p);memcpy(p,&CANARY,8);memset(p+8,0xa5,bytes);memcpy(p+8+bytes,&CANARY,8);return p+8;}
static void guard_check(const void *p,size_t bytes) {uint64_t a,z;memcpy(&a,(const uint8_t *)p-8,8);memcpy(&z,(const uint8_t *)p+bytes,8);assert(a==CANARY && z==CANARY);}
static void guard_free(void *p) {free((uint8_t *)p-8);}
int main(int argc,char **argv) {
    assert(argc==3);FILE *in=fopen(argv[1],"rb"),*out=fopen(argv[2],"wb");assert(in&&out);
    uint8_t magic[8];assert(fread(magic,1,8,in)==8 && !memcmp(magic,"VQTEST01",8));
    uint32_t count=(uint32_t)get(in,4);assert(count>0 && count<=100000);
    assert(fwrite("VQOUT001",1,8,out)==8);put(out,count,4);put(out,controls(),4);
    for(uint32_t i=0;i<count;i++) {
        uint32_t names=(uint32_t)get(in,4);assert(names>=1 && names<=63);
        for(uint32_t j=0;j<names;j++){unsigned c=(unsigned)get(in,1);assert((c>='A'&&c<='Z')||(c>='a'&&c<='z')||(c>='0'&&c<='9')||c=='_'||c=='-');}
        uint32_t op=(uint32_t)get(in,4),dim=(uint32_t)get(in,4),total=(uint32_t)get(in,4);
        uint64_t packet_bits=get(in,8),start=get(in,8);uint32_t bytes=(uint32_t)get(in,4);assert(bytes<=131100);
        uint8_t *packet=guarded(bytes),*packet_copy=malloc(bytes?bytes:1);assert(packet_copy);
        assert(fread(packet,1,bytes,in)==bytes);memcpy(packet_copy,packet,bytes);
        uint32_t entry_count=(uint32_t)get(in,4);assert(entry_count<=255);
        uint32_t *entries=guarded((size_t)entry_count*4),entry_copy[255];
        for(uint32_t j=0;j<entry_count;j++)entry_copy[j]=entries[j]=(uint32_t)get(in,4);
        uint32_t length=(uint32_t)get(in,4),component=(uint32_t)get(in,4),provided=(uint32_t)get(in,4);assert(length<=65535 && provided<=255);
        native_vorbis_affine_t direct[255];for(uint32_t j=0;j<provided;j++)direct[j]=affine_get(in);
        uint32_t bridge=(uint32_t)get(in,4);uint64_t raw=get(in,8);
        uint32_t abits=(uint32_t)get(in,4),offset=(uint32_t)get(in,4),bin=(uint32_t)get(in,4),map=(uint32_t)get(in,4);
        native_vorbis_floor0_amplitude_t amplitude={raw,abits,offset},amplitude_copy=amplitude;
        native_vorbis_affine_t *values=guarded((size_t)length*sizeof(*values));
        native_vorbis_quant_layout_t layout;memset(&layout,0,sizeof(layout));
        native_vorbis_quantization_t book;memset(&book,0,sizeof(book));
        uint16_t *storage=NULL,*storage_copy=NULL;uint32_t stored=0;int ms=-99,mt=-99,vs=-99;
        native_vorbis_quantization_t book_copy;memset(&book_copy,0,sizeof(book_copy));
        if(op==1 || op==2 || op==4) {
            ms=native_vorbis_quantization_measure(packet,bytes,packet_bits,start,dim,total,&layout);assert(ms==0);
            assert(layout.multiplicand_count<=65535);stored=(uint32_t)layout.multiplicand_count;
            storage=guarded((size_t)stored*2);mt=native_vorbis_quantization_materialize(packet,bytes,packet_bits,&layout,storage,stored,&book);assert(mt==0);
            storage_copy=malloc(stored?stored*2:1);assert(storage_copy);memcpy(storage_copy,storage,(size_t)stored*2);
            memcpy(&book_copy,&book,sizeof(book));
            if(op==1){assert(entry_count==1);vs=native_vorbis_quantization_vector(&book,entries[0],length,values,length);}
            else if(op==2)vs=native_vorbis_floor0_lsp_from_entries(&book,entries,entry_count,length,values,length);
            else {assert(entry_count==1 && length==1);vs=native_vorbis_quantization_scalar(&book,entries[0],component,values);}
            assert(vs==0 && book.storage_count==stored);
        } else {assert(op==3 && provided==length);memcpy(values,direct,(size_t)length*sizeof(*values));}
        native_vorbis_affine_t *value_copy=malloc(length?length*sizeof(*values):1);assert(value_copy);memcpy(value_copy,values,(size_t)length*sizeof(*values));
        native_vorbis_scaled_t d={0,0};native_vorbis_floor0_gain_t g={0,{0,0}};int ds=-99,gs=-99;
        if(bridge){assert(length>=1 && length<=255);ds=native_vorbis_floor0_denominator_from_affine(values,length,bin,map,&d);gs=native_vorbis_floor0_gain_from_affine(&amplitude,values,length,bin,map,&g);assert(ds==0 && gs==0);
            native_vorbis_floor0_gain_t repeated;assert(native_vorbis_floor0_gain_from_denominator(&amplitude,&d,&repeated)==0);
            assert(repeated.kind==g.kind && bits(repeated.log2_gain.mantissa)==bits(g.log2_gain.mantissa) && repeated.log2_gain.exponent==g.log2_gain.exponent);}
        assert(!memcmp(packet,packet_copy,bytes) && !memcmp(entries,entry_copy,(size_t)entry_count*4));
        assert(!memcmp(values,value_copy,(size_t)length*sizeof(*values)) && !memcmp(&amplitude,&amplitude_copy,sizeof(amplitude)));
        if(storage)assert(!memcmp(storage,storage_copy,(size_t)stored*2) && !memcmp(&book,&book_copy,sizeof(book)));
        guard_check(packet,bytes);guard_check(entries,(size_t)entry_count*4);guard_check(values,(size_t)length*sizeof(*values));if(storage)guard_check(storage,(size_t)stored*2);
        put(out,i,4);put(out,(uint32_t)ms,4);put(out,(uint32_t)mt,4);put(out,(uint32_t)vs,4);layout_put(out,layout);
        put(out,stored,4);for(uint32_t j=0;j<stored;j++)put(out,storage[j],2);
        put(out,length,4);for(uint32_t j=0;j<length;j++)affine_put(out,values[j]);
        put(out,(uint32_t)ds,4);put(out,(uint32_t)gs,4);put(out,bridge?(uint32_t)g.kind:(uint32_t)-99,4);put(out,bits(d.mantissa),8);put(out,(uint32_t)d.exponent,4);
        put(out,bits(g.log2_gain.mantissa),8);put(out,(uint32_t)g.log2_gain.exponent,4);put(out,7,4);
        free(value_copy);free(storage_copy);free(packet_copy);guard_free(packet);guard_free(entries);guard_free(values);if(storage)guard_free(storage);
    }
    assert(fgetc(in)==EOF && !fclose(in) && !fclose(out));return 0;
}
