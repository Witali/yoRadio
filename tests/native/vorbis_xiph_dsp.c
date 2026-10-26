/* DSP/MDCT allocation failure, partial cleanup and fresh-header recovery.
   Float/table fingerprints prove same-process recovery identity only; the
   retained original31 PCM gate remains the independent numerical comparison. */
#include <assert.h>
#include <limits.h>
#include <math.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <ogg/ogg.h>
#include "vorbis/codec.h"
#include "codebook.h"
#include "codec_internal.h"
#include "backends.h"
#include "mdct.h"
#include "native_vorbis_xiph_dsp_error.h"
#include "vorbis_xiph_alloc.h"
#include "cases.h"

#define CHECK(x) do { int ok=!!(x); assert(ok); if(!ok)abort(); } while(0)
enum { PACKED_CAPACITY=1024 };
static const uint64_t guard=UINT64_C(0x475d19a630e2bf84);
static int scenarios;
static unsigned floor_types,residue_types;

typedef struct { unsigned char *base,*data;const unsigned char *original;size_t size; } input_t;
typedef struct {
  const xiph_case_t *base;
  const unsigned char *identification,*comment,*setup;
  size_t identification_bytes,comment_bytes,setup_bytes;
  int channels,short_block,long_block,synthetic;
} stream_t;
typedef struct { uint64_t a,b;uint32_t packets,frames,samples; } fingerprint_t;
static struct { uint64_t before;unsigned char data[PACKED_CAPACITY];uint64_t after; } packed;
static size_t packed_bits;
static unsigned char synthetic_id[64],synthetic_comment[64],synthetic_setup[PACKED_CAPACITY];
static size_t synthetic_comment_bytes,synthetic_setup_bytes;

static void no_owners(void){CHECK(xiph_port_test_live()==0 && xiph_port_test_bytes()==0);}
static void zero_bytes(const void *value,size_t bytes){
  const unsigned char *raw=value;for(size_t i=0;i<bytes;i++)CHECK(raw[i]==0);
}
static input_t input_create(const unsigned char *bytes,size_t size){
  input_t input={0};CHECK(bytes && size<=LONG_MAX && size<=SIZE_MAX-16);
  input.base=malloc(size+16);CHECK(input.base);input.data=input.base+8;
  input.original=bytes;input.size=size;memcpy(input.base,&guard,8);
  memcpy(input.data,bytes,size);memcpy(input.data+size,&guard,8);return input;
}
static void input_destroy(input_t *input){
  uint64_t first,last;memcpy(&first,input->base,8);memcpy(&last,input->data+input->size,8);
  CHECK(first==guard && last==guard && memcmp(input->data,input->original,input->size)==0);
  free(input->base);
}
static ogg_packet packet(input_t *input,int number,int64_t granule,int bos,int eos){
  ogg_packet result;memset(&result,0,sizeof(result));result.packet=input->data;
  result.bytes=(long)input->size;result.packetno=number;result.granulepos=granule;
  result.b_o_s=bos;result.e_o_s=eos;return result;
}
static int header_read(vorbis_info *info,vorbis_comment *comment,const unsigned char *data,size_t bytes,int number){
  input_t input=input_create(data,bytes);ogg_packet value=packet(&input,number,0,number==0,0),before=value;
  int status=vorbis_synthesis_headerin(info,comment,&value);
  CHECK(memcmp(&value,&before,sizeof(value))==0);input_destroy(&input);return status;
}
static void stream_open(const stream_t *stream,vorbis_info *info,vorbis_comment *comment){
  xiph_port_test_reset(0);no_owners();vorbis_info_init(info);vorbis_comment_init(comment);
  CHECK(header_read(info,comment,stream->identification,stream->identification_bytes,0)==0);
  CHECK(header_read(info,comment,stream->comment,stream->comment_bytes,1)==0);
  CHECK(header_read(info,comment,stream->setup,stream->setup_bytes,2)==0);
  CHECK(info->codec_setup && info->channels==stream->channels && info->rate==(long)stream->base->rate);
  CHECK(vorbis_info_blocksize(info,0)==stream->short_block && vorbis_info_blocksize(info,1)==stream->long_block);
  const codec_setup_info *ci=info->codec_setup;CHECK(ci->fullbooks==NULL);
  for(int i=0;i<ci->books;i++)CHECK(ci->book_param[i]!=NULL);
  CHECK(xiph_port_test_failures()==0);
}
static void stream_close(vorbis_info *info,vorbis_comment *comment){
  vorbis_comment_clear(comment);vorbis_info_clear(info);no_owners();
  zero_bytes(info,sizeof(*info));zero_bytes(comment,sizeof(*comment));
  vorbis_comment_clear(comment);vorbis_info_clear(info);no_owners();
}
static void dsp_clear(vorbis_dsp_state *dsp){
  vorbis_dsp_clear(dsp);zero_bytes(dsp,sizeof(*dsp));
  vorbis_dsp_clear(dsp);zero_bytes(dsp,sizeof(*dsp));
}
static void dsp_check(const stream_t *stream,vorbis_info *info,vorbis_dsp_state *dsp){
  codec_setup_info *ci=info->codec_setup;private_state *backend=dsp->backend_state;
  CHECK(dsp->vi==info && backend && dsp->analysisp==0 && dsp->pcm && dsp->pcmret);
  CHECK(dsp->pcm_storage==stream->long_block && ci->fullbooks);
  for(int i=0;i<info->channels;i++){
    CHECK(dsp->pcm[i]);
    for(int sample=0;sample<dsp->pcm_storage;sample++)CHECK(dsp->pcm[i][sample]==0.f);
  }
  for(int block=0;block<2;block++){
    CHECK(backend->transform[block] && backend->transform[block][0]);
    const mdct_lookup *lookup=backend->transform[block][0];
    CHECK(lookup->n==ci->blocksizes[block] && lookup->trig && lookup->bitrev);
  }
  for(int i=0;i<ci->books;i++)CHECK(ci->book_param[i]==NULL);
  CHECK(backend->flr && backend->residue);
  for(int i=0;i<ci->floors;i++){
    CHECK(ci->floor_type[i]>=0 && ci->floor_type[i]<2 && backend->flr[i]);
    floor_types|=1U<<(unsigned)ci->floor_type[i];
  }
  for(int i=0;i<ci->residues;i++){
    CHECK(ci->residue_type[i]>=0 && ci->residue_type[i]<3 && backend->residue[i]);
    residue_types|=1U<<(unsigned)ci->residue_type[i];
  }
  if(stream->synthetic){
    CHECK(info->channels==4 && ci->books==3 && ci->floors==2 && ci->residues==2);
    CHECK(ci->fullbooks[0].dim==2 && ci->fullbooks[0].entries==4);
    for(int i=0;i<2;i++){
      const vorbis_info_residue0 *residue=ci->residue_param[i];
      CHECK(residue->partitions==2 && residue->partvals==4 && residue->groupbook==0);
      CHECK(residue->secondstages[0]==5 && residue->secondstages[1]==11);
    }
  }
}
static void dsp_sweep(const stream_t *stream){
  vorbis_info info;vorbis_comment comment;vorbis_dsp_state dsp;
  stream_open(stream,&info,&comment);memset(&dsp,0,sizeof(dsp));xiph_port_test_reset(0);
  CHECK(vorbis_synthesis_init(&dsp,&info)==0);
  size_t attempts=xiph_port_test_attempts();CHECK(attempts>0 && xiph_port_test_failures()==0);
  CHECK(xiph_port_test_realloc_attempts()==0);dsp_check(stream,&info,&dsp);
  dsp_clear(&dsp);stream_close(&info,&comment);scenarios++;
  for(size_t ordinal=1;ordinal<=attempts;ordinal++){
    stream_open(stream,&info,&comment);memset(&dsp,0,sizeof(dsp));xiph_port_test_reset(ordinal);
    CHECK(vorbis_synthesis_init(&dsp,&info)==1);
    CHECK(xiph_port_test_failures()==1 && xiph_port_test_attempts()==ordinal);
    CHECK(xiph_port_test_realloc_attempts()==0);zero_bytes(&dsp,sizeof(dsp));dsp_clear(&dsp);
    stream_close(&info,&comment);scenarios++;
    stream_open(stream,&info,&comment);memset(&dsp,0,sizeof(dsp));xiph_port_test_reset(0);
    CHECK(vorbis_synthesis_init(&dsp,&info)==0 && xiph_port_test_attempts()==attempts);
    CHECK(xiph_port_test_failures()==0);dsp_check(stream,&info,&dsp);
    dsp_clear(&dsp);stream_close(&info,&comment);scenarios++;
  }
}
static fingerprint_t decode_fingerprint(const stream_t *stream){
  const xiph_case_t *test=stream->base;vorbis_info info;vorbis_comment comment;
  vorbis_dsp_state dsp;vorbis_block block;memset(&dsp,0,sizeof(dsp));memset(&block,0,sizeof(block));
  fingerprint_t result={UINT64_C(14695981039346656037),UINT64_C(0x973e5108bc24ad6f),0,0,0};
  stream_open(stream,&info,&comment);xiph_port_test_reset(0);
  CHECK(vorbis_synthesis_init(&dsp,&info)==0 && vorbis_block_init(&dsp,&block)==0);
  for(uint32_t p=0;p<test->packet_count;p++){
    uint32_t start=test->offsets[p],end=test->offsets[p+1];CHECK(start<end && end<=test->audio_bytes);
    input_t input=input_create(test->audio+start,end-start);
    ogg_packet value=packet(&input,(int)p+3,test->granules[p],0,p+1==test->packet_count),before=value;
    CHECK(vorbis_synthesis(&block,&value)==0 && vorbis_synthesis_blockin(&dsp,&block)==0);
    int available;float **pcm=NULL;uint32_t frames=0;
    while((available=vorbis_synthesis_pcmout(&dsp,&pcm))>0){
      CHECK(pcm && available<=8192);
      for(int frame=0;frame<available;frame++)for(int channel=0;channel<info.channels;channel++){
        float sample=pcm[channel][frame];uint32_t bits;CHECK(isfinite(sample));memcpy(&bits,&sample,4);
        result.a=(result.a^bits)*UINT64_C(1099511628211);
        result.b=((result.b<<11)|(result.b>>53))^((uint64_t)bits+result.samples);result.samples++;
      }
      frames+=(uint32_t)available;CHECK(vorbis_synthesis_read(&dsp,available)==0);
    }
    CHECK(available==0 && frames==test->frames[p]);result.frames+=frames;result.packets++;
    CHECK(memcmp(&value,&before,sizeof(value))==0);input_destroy(&input);
  }
  CHECK(result.packets==14 && result.samples*2==test->pcm_bytes);
  CHECK(vorbis_block_clear(&block)==0);dsp_clear(&dsp);stream_close(&info,&comment);
  scenarios++;return result;
}
static void packed_begin(void){packed.before=packed.after=guard;memset(packed.data,0,sizeof(packed.data));packed_bits=0;}
static void put(uint32_t value,unsigned width){
  CHECK(width<=32 && packed_bits+width<=PACKED_CAPACITY*8);
  for(unsigned bit=0;bit<width;bit++,packed_bits++)
    if((value>>bit)&1U)packed.data[packed_bits/8]|=(unsigned char)(1U<<(packed_bits%8));
}
static void text_bytes(const char *text){for(size_t i=0;i<strlen(text);i++)put((unsigned char)text[i],8);}
static void book(int entries,int dimensions,int lookup){
  put(UINT32_C(0x564342),24);put((uint32_t)dimensions,16);put((uint32_t)entries,24);
  put(0,1);put(0,1);for(int entry=0;entry<entries;entry++)put(entries==4?1U:0U,5);
  put((uint32_t)lookup,4);
  if(lookup){
    put(UINT32_C(0xe0380000),32);put(UINT32_C(0x60100000),32);put(3,4);put(0,1);
    for(int value=0;value<entries*dimensions;value++)put((uint32_t)value%8,4);
  }
}
static void synthetic_build(int floor_type,int residue_type){
  const xiph_case_t *base=&xiph_cases[0];CHECK(base->identification_bytes==30);
  memcpy(synthetic_id,base->identification,30);synthetic_id[11]=4;synthetic_id[28]=UINT8_C(0x66);
  packed_begin();put(3,8);text_bytes("vorbis");put(7,32);text_bytes("DSP OOM");put(0,32);put(1,1);
  synthetic_comment_bytes=(packed_bits+7)/8;CHECK(synthetic_comment_bytes<=sizeof(synthetic_comment));
  memcpy(synthetic_comment,packed.data,synthetic_comment_bytes);
  packed_begin();put(5,8);text_bytes("vorbis");put(2,8);
  book(4,2,0);book(2,1,2);book(4,2,2);
  put(0,6);put(0,16); /* One time backend. */
  put(1,6); /* Two floor instances. */
  for(int floor=0;floor<2;floor++){
    put((uint32_t)floor_type,16);
    if(floor_type==0){put(2,8);put(8000,16);put(8,16);put(3,6);put(60,8);put(0,4);put(2,8);}
    else{put(0,5);put(0,2);put(3,4);}
  }
  put(1,6); /* Two residue instances, each with four decodemap rows. */
  for(int residue=0;residue<2;residue++){
    put((uint32_t)residue_type,16);put(0,24);put(16,24);put(1,24);put(1,6);put(0,8);
    put(5,3);put(0,1); /* Classification0: stages0/2, three pointer slots. */
    put(3,3);put(1,1);put(1,5); /* Classification1: stages0/1/3, four slots. */
    put(1,8);put(2,8);put(2,8);put(1,8);put(2,8);
  }
  put(0,6);put(0,16); /* One mapping, two submaps, four uncoupled channels. */
  put(1,1);put(1,4);put(0,1);put(0,2);
  for(int channel=0;channel<4;channel++)put((uint32_t)channel%2,4);
  for(int submap=0;submap<2;submap++){put(0,8);put((uint32_t)submap,8);put((uint32_t)submap,8);}
  put(0,6);put(0,1);put(0,16);put(0,16);put(0,8);put(1,1);
  synthetic_setup_bytes=(packed_bits+7)/8;memcpy(synthetic_setup,packed.data,synthetic_setup_bytes);
  CHECK(packed.before==guard && packed.after==guard);
}
static void synthetic_controls(void){
  for(int floor=0;floor<2;floor++)for(int residue=0;residue<3;residue++){
    synthetic_build(floor,residue);
    stream_t stream={&xiph_cases[0],synthetic_id,synthetic_comment,synthetic_setup,
      30,synthetic_comment_bytes,synthetic_setup_bytes,4,64,64,1};
    dsp_sweep(&stream);
  }
}
static uint64_t mix(uint64_t hash,uint32_t value){return (hash^value)*UINT64_C(1099511628211);}
static void mdct_zero(const mdct_lookup *lookup){
  CHECK(lookup->n==0 && lookup->log2n==0 && lookup->trig==NULL && lookup->bitrev==NULL && lookup->scale==0.f);
}
static uint64_t mdct_fingerprint(const mdct_lookup *lookup,int n){
  CHECK(lookup->n==n && lookup->trig && lookup->bitrev && isfinite(lookup->scale));
  int logarithm=0;for(int length=n;length>1;length>>=1)logarithm++;
  CHECK(lookup->log2n==logarithm && lookup->scale==4.f/(float)n);
  uint32_t bits;memcpy(&bits,&lookup->scale,4);
  uint64_t hash=mix(UINT64_C(14695981039346656037),bits);
  for(int i=0;i<n+n/4;i++){
    CHECK(isfinite(lookup->trig[i]));memcpy(&bits,&lookup->trig[i],4);hash=mix(hash,bits);
  }
  for(int i=0;i<n/4;i++){CHECK(lookup->bitrev[i]>=0 && lookup->bitrev[i]<n/2);hash=mix(hash,(uint32_t)lookup->bitrev[i]);}
  return hash;
}
static void mdct_controls(void){
  static const int sizes[]={32,64,128,512,8192};
  for(unsigned index=0;index<sizeof(sizes)/sizeof(*sizes);index++){
    int n=sizes[index];struct { uint64_t before;mdct_lookup lookup;uint64_t after; } guarded;
    guarded.before=guarded.after=guard;memset(&guarded.lookup,0,sizeof(guarded.lookup));
    no_owners();xiph_port_test_reset(0);CHECK(native_xiph_mdct_init(&guarded.lookup,n)==0);
    CHECK(xiph_port_test_attempts()==2 && xiph_port_test_failures()==0);
    uint64_t baseline=mdct_fingerprint(&guarded.lookup,n);mdct_clear(&guarded.lookup);
    mdct_zero(&guarded.lookup);mdct_clear(&guarded.lookup);no_owners();scenarios++;
    for(int checked=0;checked<2;checked++)for(size_t ordinal=0;ordinal<=2;ordinal++){
      memset(&guarded.lookup,0xa5,sizeof(guarded.lookup));xiph_port_test_reset(ordinal);
      int status=0;
      if(checked)status=native_xiph_mdct_init(&guarded.lookup,n);else mdct_init(&guarded.lookup,n);
      CHECK(guarded.before==guard && guarded.after==guard);
      CHECK(xiph_port_test_attempts()==(ordinal?ordinal:2U) && xiph_port_test_failures()==(ordinal?1U:0U));
      if(ordinal){if(checked)CHECK(status!=0);mdct_zero(&guarded.lookup);}
      else{CHECK(status==0 && mdct_fingerprint(&guarded.lookup,n)==baseline);}
      mdct_clear(&guarded.lookup);mdct_clear(&guarded.lookup);mdct_zero(&guarded.lookup);no_owners();scenarios++;
      xiph_port_test_reset(0);CHECK(native_xiph_mdct_init(&guarded.lookup,n)==0);
      CHECK(mdct_fingerprint(&guarded.lookup,n)==baseline && xiph_port_test_attempts()==2);
      mdct_clear(&guarded.lookup);mdct_zero(&guarded.lookup);no_owners();scenarios++;
    }
  }
}
static void invalid_controls(void){
  vorbis_dsp_state dsp;vorbis_info info;vorbis_comment comment;
  no_owners();xiph_port_test_reset(0);memset(&dsp,0xa5,sizeof(dsp));
  CHECK(vorbis_synthesis_init(&dsp,NULL)==1);zero_bytes(&dsp,sizeof(dsp));dsp_clear(&dsp);no_owners();scenarios++;
  memset(&info,0,sizeof(info));memset(&dsp,0xa5,sizeof(dsp));
  CHECK(vorbis_synthesis_init(&dsp,&info)==1);zero_bytes(&dsp,sizeof(dsp));dsp_clear(&dsp);no_owners();scenarios++;
  for(int headers=0;headers<3;headers++){
    xiph_port_test_reset(0);vorbis_info_init(&info);vorbis_comment_init(&comment);
    const xiph_case_t *test=&xiph_cases[0];
    if(headers>0)CHECK(header_read(&info,&comment,test->identification,test->identification_bytes,0)==0);
    if(headers>1)CHECK(header_read(&info,&comment,test->comment,test->comment_bytes,1)==0);
    size_t live=xiph_port_test_live(),bytes=xiph_port_test_bytes();memset(&dsp,0xa5,sizeof(dsp));xiph_port_test_reset(1);
    CHECK(vorbis_synthesis_init(&dsp,&info)==1 && xiph_port_test_attempts()==0 && xiph_port_test_failures()==0);
    zero_bytes(&dsp,sizeof(dsp));dsp_clear(&dsp);
    CHECK(xiph_port_test_live()==live && xiph_port_test_bytes()==bytes);stream_close(&info,&comment);scenarios++;
  }
  xiph_port_test_reset(0);memset(&dsp,0,sizeof(dsp));
  dsp.pcmret=xiph_port_test_malloc(3*sizeof(*dsp.pcmret));CHECK(dsp.pcmret && !dsp.pcm && !dsp.vi);
  CHECK(xiph_port_test_live()==1);dsp_clear(&dsp);no_owners();scenarios++;
}
int xiph_dsp_tests(void){
  _Static_assert(sizeof(float)==4 && sizeof(int)==4,"Table/recovery fingerprints use32bit words");
  scenarios=0;floor_types=residue_types=0;no_owners();
  for(unsigned i=0;i<XIPH_CASE_COUNT;i++){
    const xiph_case_t *test=&xiph_cases[i];
    stream_t stream={test,test->identification,test->comment,test->setup,
      test->identification_bytes,test->comment_bytes,test->setup_bytes,
      (int)test->channels,(int)test->short_block,(int)test->long_block,0};
    fingerprint_t baseline=decode_fingerprint(&stream);dsp_sweep(&stream);
    fingerprint_t reopened=decode_fingerprint(&stream);
    CHECK(baseline.a==reopened.a && baseline.b==reopened.b && baseline.packets==reopened.packets);
    CHECK(baseline.frames==reopened.frames && baseline.samples==reopened.samples);
  }
  synthetic_controls();mdct_controls();invalid_controls();CHECK(floor_types==3 && residue_types==7);
  no_owners();xiph_port_test_reset(0);return scenarios;
}
