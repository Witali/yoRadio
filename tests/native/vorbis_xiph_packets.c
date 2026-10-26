/* Independent packet-allocation failures and complete fresh-header recovery.
   Exact binary32 comparisons below establish same-process identity. The
   separate original31 raw S16 capture remains the independent numeric gate. */
#include <assert.h>
#include <limits.h>
#include <math.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <ogg/ogg.h>
#include "vorbis/codec.h"
#include "codec_internal.h"
#include "backends.h"
#include "registry.h"
#include "vorbis_xiph_alloc.h"
#include "cases.h"

#define CHECK(x) do { int ok=!!(x); assert(ok); if(!ok)abort(); } while(0)

extern void *_vorbis_block_alloc(vorbis_block *,long);
extern void _vorbis_block_ripcord(vorbis_block *);

static const uint64_t guard=UINT64_C(0x69d023b8ca1f547e);
static unsigned scenarios,fatal_refusals,optional_refusals;
static unsigned floor_types,residue_types;
typedef struct { unsigned char *base,*data;const unsigned char *original;size_t size; } input_t;
typedef struct { vorbis_info info;vorbis_comment comment;vorbis_dsp_state dsp;vorbis_block block; } decoder_t;
typedef struct { unsigned char *base;float *data;size_t samples; } reference_t;

unsigned xiph_packet_fatal_count(void){return fatal_refusals;}
unsigned xiph_packet_optional_count(void){return optional_refusals;}
static void reset_counts(void){scenarios=fatal_refusals=optional_refusals=0;floor_types=residue_types=0;}
static void no_owners(void){CHECK(xiph_port_test_live()==0 && xiph_port_test_bytes()==0);}
static void policy(size_t ordinal,int zero_null){xiph_port_test_reset(ordinal);xiph_port_test_zero_null(zero_null);}
static input_t input_create(const unsigned char *bytes,size_t size){
  input_t input={0};CHECK(bytes && size>0 && size<=LONG_MAX && size<=SIZE_MAX-16);
  input.base=malloc(size+16);CHECK(input.base);input.data=input.base+8;
  input.original=bytes;input.size=size;memcpy(input.base,&guard,8);
  memcpy(input.data,bytes,size);memcpy(input.data+size,&guard,8);return input;
}
static void input_destroy(input_t *input){
  uint64_t before,after;memcpy(&before,input->base,8);memcpy(&after,input->data+input->size,8);
  CHECK(before==guard && after==guard && memcmp(input->data,input->original,input->size)==0);
  free(input->base);
}
static ogg_packet make_packet(input_t *input,int number,int64_t granule,int bos,int eos){
  ogg_packet result;memset(&result,0,sizeof(result));result.packet=input->data;
  result.bytes=(long)input->size;result.packetno=number;result.granulepos=granule;
  result.b_o_s=bos;result.e_o_s=eos;return result;
}
static void decoder_open(const xiph_case_t *stream,decoder_t *decoder,int zero_null){
  no_owners();memset(decoder,0,sizeof(*decoder));policy(0,zero_null);
  vorbis_info_init(&decoder->info);vorbis_comment_init(&decoder->comment);
  const unsigned char *headers[]={stream->identification,stream->comment,stream->setup};
  const size_t sizes[]={stream->identification_bytes,stream->comment_bytes,stream->setup_bytes};
  for(int h=0;h<3;h++){
    input_t input=input_create(headers[h],sizes[h]);ogg_packet value=make_packet(&input,h,0,h==0,0),before=value;
    CHECK(vorbis_synthesis_headerin(&decoder->info,&decoder->comment,&value)==0);
    CHECK(memcmp(&value,&before,sizeof(value))==0);input_destroy(&input);
  }
  CHECK(decoder->info.channels==(int)stream->channels && decoder->info.rate==(long)stream->rate);
  CHECK(vorbis_info_blocksize(&decoder->info,0)==(long)stream->short_block);
  CHECK(vorbis_info_blocksize(&decoder->info,1)==(long)stream->long_block);
  codec_setup_info *ci=decoder->info.codec_setup;CHECK(ci);
  for(int f=0;f<ci->floors;f++){CHECK(ci->floor_type[f]>=0 && ci->floor_type[f]<2);floor_types|=1U<<(unsigned)ci->floor_type[f];}
  for(int r=0;r<ci->residues;r++){CHECK(ci->residue_type[r]>=0 && ci->residue_type[r]<3);residue_types|=1U<<(unsigned)ci->residue_type[r];}
  CHECK(vorbis_synthesis_init(&decoder->dsp,&decoder->info)==0);
  CHECK(vorbis_block_init(&decoder->dsp,&decoder->block)==0 && xiph_port_test_failures()==0);
}
static void decoder_close(decoder_t *decoder){
  /* Close is not another injected scenario; its optional consolidation may
     succeed. All partial packet owners must remain reachable until here. */
  policy(0,0);CHECK(vorbis_block_clear(&decoder->block)==0);
  CHECK(vorbis_block_clear(&decoder->block)==0);vorbis_dsp_clear(&decoder->dsp);
  vorbis_dsp_clear(&decoder->dsp);vorbis_comment_clear(&decoder->comment);vorbis_info_clear(&decoder->info);
  vorbis_comment_clear(&decoder->comment);vorbis_info_clear(&decoder->info);no_owners();
}
static reference_t reference_create(const xiph_case_t *stream){
  reference_t result={0};CHECK(stream->pcm_bytes>0 && stream->pcm_bytes%2==0);
  result.samples=stream->pcm_bytes/2;CHECK(result.samples<=(SIZE_MAX-16)/sizeof(float));
  result.base=malloc(result.samples*sizeof(float)+16);CHECK(result.base);result.data=(float *)(void *)(result.base+8);
  memcpy(result.base,&guard,8);memcpy(result.base+8+result.samples*sizeof(float),&guard,8);return result;
}
static void reference_destroy(reference_t *reference){
  uint64_t before,after;memcpy(&before,reference->base,8);
  memcpy(&after,reference->base+8+reference->samples*sizeof(float),8);
  CHECK(before==guard && after==guard);free(reference->base);
}
static int decode_packet(const xiph_case_t *stream,decoder_t *decoder,uint32_t index,
                         reference_t *reference,size_t *cursor,int capture){
  CHECK(index<stream->packet_count);uint32_t start=stream->offsets[index],end=stream->offsets[index+1];
  CHECK(start<end && end<=stream->audio_bytes);input_t input=input_create(stream->audio+start,end-start);
  ogg_packet packet=make_packet(&input,(int)index+3,stream->granules[index],0,index+1==stream->packet_count),before=packet;
  int status=vorbis_synthesis(&decoder->block,&packet);
  CHECK(memcmp(&packet,&before,sizeof(packet))==0);input_destroy(&input);
  if(status)return status; /* Never publish a failed, partially filled block. */
  CHECK(vorbis_synthesis_blockin(&decoder->dsp,&decoder->block)==0);
  int available;float **pcm=NULL;uint32_t frames=0;
  while((available=vorbis_synthesis_pcmout(&decoder->dsp,&pcm))>0){
    CHECK(pcm && available<=8192);
    for(int frame=0;frame<available;frame++)for(int channel=0;channel<decoder->info.channels;channel++){
      float sample=pcm[channel][frame];CHECK(isfinite(sample) && *cursor<reference->samples);
      if(capture)memcpy(reference->data+*cursor,&sample,sizeof(sample));
      else CHECK(memcmp(reference->data+*cursor,&sample,sizeof(sample))==0);
      (*cursor)++;
    }
    frames+=(uint32_t)available;CHECK(vorbis_synthesis_read(&decoder->dsp,available)==0);
  }
  CHECK(available==0 && frames==stream->frames[index]);return 0;
}
static void complete_stream(const xiph_case_t *stream,reference_t *reference,int capture,int zero_null){
  decoder_t decoder;size_t cursor=0;decoder_open(stream,&decoder,zero_null);policy(0,zero_null);
  for(uint32_t p=0;p<stream->packet_count;p++)CHECK(decode_packet(stream,&decoder,p,reference,&cursor,capture)==0);
  CHECK(cursor==reference->samples && xiph_port_test_failures()==0);decoder_close(&decoder);scenarios++;
}
static size_t target_trial(const xiph_case_t *stream,reference_t *reference,uint32_t target,
                           int cold,int zero_null,size_t ordinal){
  decoder_t decoder;size_t cursor=0;decoder_open(stream,&decoder,zero_null);policy(0,zero_null);
  for(uint32_t p=0;p<target;p++)CHECK(decode_packet(stream,&decoder,p,reference,&cursor,0)==0);
  if(cold){CHECK(vorbis_block_clear(&decoder.block)==0);CHECK(vorbis_block_init(&decoder.dsp,&decoder.block)==0);}
  /* The only optional allocation in vorbis_synthesis is the first ripcord
     consolidation. An allocation elsewhere must not be silently ignored. */
  int optional_first=decoder.block.totaluse>0;
  policy(ordinal,zero_null);int status=decode_packet(stream,&decoder,target,reference,&cursor,0);
  size_t attempts=xiph_port_test_attempts(),failures=xiph_port_test_failures();
  if(ordinal){
    CHECK(failures==1 && attempts>=ordinal);
    if(optional_first && ordinal==1){CHECK(status==0 && xiph_port_test_realloc_attempts()==1);optional_refusals++;}
    else{CHECK(status==OV_EFAULT && attempts==ordinal);fatal_refusals++;}
  }else CHECK(status==0 && failures==0);
  if(status==0){
    policy(0,zero_null);
    for(uint32_t p=target+1;p<stream->packet_count;p++)CHECK(decode_packet(stream,&decoder,p,reference,&cursor,0)==0);
    CHECK(cursor==reference->samples && xiph_port_test_failures()==0);
  }
  decoder_close(&decoder);scenarios++;
  /* Every injected refusal gets a complete fresh instance and all three
     original headers; compare every output float, including final drain. */
  if(ordinal)complete_stream(stream,reference,0,zero_null);
  return attempts;
}
static void stream_sweep(const xiph_case_t *stream){
  reference_t reference=reference_create(stream);complete_stream(stream,&reference,1,0);
  for(int zero=0;zero<2;zero++)for(int cold=0;cold<2;cold++)for(uint32_t target=0;target<stream->packet_count;target++){
    size_t attempts=target_trial(stream,&reference,target,cold,zero,0);
    for(size_t ordinal=1;ordinal<=attempts;ordinal++)target_trial(stream,&reference,target,cold,zero,ordinal);
  }
  reference_destroy(&reference);no_owners();
}
static void fill(unsigned char *bytes,size_t count,unsigned seed){
  for(size_t i=0;i<count;i++)bytes[i]=(unsigned char)(seed+i);
}
static void retained(const unsigned char *bytes,size_t count,unsigned seed){
  for(size_t i=0;i<count;i++)CHECK(bytes[i]==(unsigned char)(seed+i));
}
static void arena_initialize(vorbis_block *block,vorbis_dsp_state *dsp){
  memset(dsp,0,sizeof(*dsp));CHECK(vorbis_block_init(dsp,block)==0);
}
static void arena_unchanged(const vorbis_block *before,const vorbis_block *block,size_t live,size_t bytes){
  CHECK(memcmp(before,block,sizeof(*block))==0);
  CHECK(xiph_port_test_live()==live && xiph_port_test_bytes()==bytes);
}
static void arena_controls(void){
  vorbis_dsp_state dsp;vorbis_block block;no_owners();policy(0,0);arena_initialize(&block,&dsp);
  const long rejected[]={-1,LONG_MIN,LONG_MAX,LONG_MAX-1,LONG_MAX-6};
  for(unsigned i=0;i<sizeof(rejected)/sizeof(*rejected);i++){
    vorbis_block before=block;policy(1,0);CHECK(_vorbis_block_alloc(&block,rejected[i])==NULL);
    CHECK(xiph_port_test_attempts()==0 && xiph_port_test_failures()==0);arena_unchanged(&before,&block,0,0);scenarios++;
  }
  for(int zero=0;zero<2;zero++){
    policy(1,zero);vorbis_block before=block;CHECK(_vorbis_block_alloc(&block,0)==NULL);
    CHECK(xiph_port_test_attempts()==0 && xiph_port_test_failures()==0);arena_unchanged(&before,&block,0,0);scenarios++;
  }
  vorbis_block before=block;policy(1,0);CHECK(_vorbis_block_alloc(&block,16)==NULL);
  CHECK(xiph_port_test_attempts()==1 && xiph_port_test_failures()==1);arena_unchanged(&before,&block,0,0);scenarios++;
  policy(1,0);CHECK(_vorbis_block_alloc(&block,LONG_MAX-7)==NULL);
  CHECK(xiph_port_test_attempts()==1 && xiph_port_test_failures()==1);arena_unchanged(&before,&block,0,0);scenarios++;
  policy(0,0);unsigned char *first=_vorbis_block_alloc(&block,16);CHECK(first);fill(first,16,31);
  CHECK(block.localalloc==16 && block.localtop==16 && block.totaluse==0 && !block.reap);
  for(int zero=0;zero<2;zero++){
    policy(1,zero);before=block;CHECK(_vorbis_block_alloc(&block,0)==first+16);
    CHECK(!xiph_port_test_attempts());arena_unchanged(&before,&block,1,16);retained(first,16,31);scenarios++;
  }
  for(size_t ordinal=1;ordinal<=2;ordinal++){
    before=block;policy(ordinal,0);CHECK(_vorbis_block_alloc(&block,24)==NULL);
    CHECK(xiph_port_test_attempts()==ordinal && xiph_port_test_failures()==1);
    arena_unchanged(&before,&block,1,16);retained(first,16,31);scenarios++;
  }
  policy(0,0);unsigned char *second=_vorbis_block_alloc(&block,24);CHECK(second);fill(second,24,67);
  CHECK(block.localalloc==24 && block.localtop==24 && block.totaluse==16 && block.reap);
  CHECK(block.reap->ptr==first && block.reap->next==NULL);
  size_t live=xiph_port_test_live(),bytes=xiph_port_test_bytes();struct alloc_chain saved=*block.reap;
  for(size_t ordinal=1;ordinal<=2;ordinal++){
    before=block;policy(ordinal,0);CHECK(_vorbis_block_alloc(&block,32)==NULL);
    CHECK(xiph_port_test_attempts()==ordinal && xiph_port_test_failures()==1);
    arena_unchanged(&before,&block,live,bytes);CHECK(memcmp(block.reap,&saved,sizeof(saved))==0);
    retained(first,16,31);retained(second,24,67);scenarios++;
  }
  policy(0,0);unsigned char *third=_vorbis_block_alloc(&block,32);CHECK(third);fill(third,32,103);
  CHECK(block.totaluse==40 && block.localalloc==32 && block.localtop==32);
  CHECK(block.reap && block.reap->ptr==second && block.reap->next && block.reap->next->ptr==first);
  retained(first,16,31);retained(second,24,67);retained(third,32,103);scenarios++;
  /* Accounting checks use real small owners; no giant buffer is allocated or
     dereferenced. Restore valid accounting before closing those owners. */
  const long old_top=block.localtop,old_total=block.totaluse,old_alloc=block.localalloc;
  for(unsigned kind=0;kind<5;kind++){
    if(kind==0)block.localtop=LONG_MAX-7;
    if(kind==1)block.totaluse=LONG_MAX-7;
    if(kind==2)block.localtop=-1;
    if(kind==3)block.localalloc=-1;
    if(kind==4)block.totaluse=-1;
    before=block;live=xiph_port_test_live();bytes=xiph_port_test_bytes();policy(1,0);
    CHECK(_vorbis_block_alloc(&block,40)==NULL && xiph_port_test_attempts()==0);
    arena_unchanged(&before,&block,live,bytes);retained(first,16,31);retained(second,24,67);retained(third,32,103);
    block.localtop=old_top;block.totaluse=old_total;block.localalloc=old_alloc;scenarios++;
  }
  policy(0,0);CHECK(vorbis_block_clear(&block)==0 && vorbis_block_clear(&block)==0);no_owners();scenarios++;
  /* Alignment and in-place zero allocation at an interior position. */
  arena_initialize(&block,&dsp);policy(0,0);first=_vorbis_block_alloc(&block,16);CHECK(first);
  _vorbis_block_ripcord(&block);CHECK(_vorbis_block_alloc(&block,1)==first && block.localtop==8);
  before=block;CHECK(_vorbis_block_alloc(&block,0)==first+8);arena_unchanged(&before,&block,1,16);scenarios++;
  CHECK(vorbis_block_clear(&block)==0);no_owners();
}

/* Six independently constructed floor/residue combinations. Four
   channels force every per-channel allocation; short and long modes in the
   original31 additionally exercise both floor0 map cache entries. */
enum { PACKED_CAPACITY=1024,SYNTHETIC_PACKETS=4 };
static struct { uint64_t before;unsigned char bytes[PACKED_CAPACITY];uint64_t after; } packed;
static size_t bits;
static unsigned char synthetic_id[30],synthetic_setup[PACKED_CAPACITY],synthetic_audio[PACKED_CAPACITY];
static uint32_t synthetic_offsets[SYNTHETIC_PACKETS+1],synthetic_frames[SYNTHETIC_PACKETS];
static int64_t synthetic_granules[SYNTHETIC_PACKETS];
static uint8_t synthetic_modes[SYNTHETIC_PACKETS];
static void packed_begin(void){packed.before=packed.after=guard;memset(packed.bytes,0,sizeof(packed.bytes));bits=0;}
static void put(uint32_t value,unsigned width){
  CHECK(width<=32 && bits+width<=PACKED_CAPACITY*8);
  for(unsigned bit=0;bit<width;bit++,bits++)if((value>>bit)&1U)packed.bytes[bits/8]|=(unsigned char)(1U<<(bits%8));
}
static void text_bytes(const char *value){for(size_t i=0;i<strlen(value);i++)put((unsigned char)value[i],8);}
static size_t packed_copy(unsigned char *destination){
  CHECK(packed.before==guard && packed.after==guard);size_t bytes=(bits+7)/8;memcpy(destination,packed.bytes,bytes);return bytes;
}
static void synthetic_book(int vector){
  put(UINT32_C(0x564342),24);put(1,16);put(2,24);put(0,1);put(0,1);put(0,5);put(0,5);
  put(vector?2U:0U,4);
  if(vector){put(0,32);put(UINT32_C(0x60100000),32);put(1,4);put(0,1);put(1,2);put(2,2);}
}
static xiph_case_t synthetic_build(int floor_type,int residue_type,int shape){
  xiph_case_t stream=xiph_cases[0];CHECK(stream.identification_bytes==sizeof(synthetic_id));
  memcpy(synthetic_id,stream.identification,sizeof(synthetic_id));synthetic_id[11]=4;synthetic_id[28]=0x66;
  packed_begin();put(5,8);text_bytes("vorbis");put(1,8);synthetic_book(0);synthetic_book(1);
  put(0,6);put(0,16);put(0,6);put((uint32_t)floor_type,16);
  if(floor_type==0){put(1,8);put(8000,16);put(8,16);put(3,6);put(60,8);put(0,4);put(1,8);}
  else{put(0,5);put(0,2);put(5,4);}
  put(0,6);put((uint32_t)residue_type,16);put(0,24);put(residue_type==2?32U:8U,24);
  put(shape==2?63U:3U,24);put(0,6);put(0,8);put(shape==3?0U:1U,3);put(0,1);
  if(shape!=3)put(1,8);
  put(0,6);put(0,16);put(0,1);put(0,1);put(0,2);put(0,8);put(0,8);put(0,8);
  put(0,6);put(0,1);put(0,16);put(0,16);put(0,8);put(1,1);
  size_t setup_bytes=packed_copy(synthetic_setup);size_t audio_bytes=0;
  for(unsigned p=0;p<SYNTHETIC_PACKETS;p++){
    packed_begin();put(0,1);
    if(shape==5){
      /* Stop inside the floor section. Padding may complete an early floor0
         value, but the following channel sees EOP; this remains nominal. */
      put(floor_type==0?5U:1U,floor_type==0?3U:1U);
    }else for(unsigned channel=0;channel<4;channel++){
      if(floor_type==0){put(shape==1?0U:5U,3);if(shape!=1){put(0,1);put(p%2,1);}}
      else{put(shape==1?0U:1U,1);if(shape!=1){put(160+p,8);put(180-p,8);}}
    }
    if(shape==0){
      unsigned groups=residue_type==2?8U:2U,channels=residue_type==2?1U:4U;
      for(unsigned group=0;group<groups;group++){
        for(unsigned channel=0;channel<channels;channel++)put(0,1);
        for(unsigned channel=0;channel<channels;channel++)for(unsigned sample=0;sample<4;sample++)put((p+group+channel+sample)%2,1);
      }
    }
    CHECK((bits+7)/8<=sizeof(synthetic_audio)-audio_bytes);
    synthetic_offsets[p]=(uint32_t)audio_bytes;audio_bytes+=packed_copy(synthetic_audio+audio_bytes);
    CHECK(audio_bytes<=sizeof(synthetic_audio));synthetic_frames[p]=p?32U:0U;
    synthetic_granules[p]=(int64_t)p*32;synthetic_modes[p]=0;
  }
  synthetic_offsets[SYNTHETIC_PACKETS]=(uint32_t)audio_bytes;
  stream.id="synthetic-packet-oom";stream.channels=4;stream.short_block=stream.long_block=64;
  stream.identification=synthetic_id;stream.setup=synthetic_setup;stream.setup_bytes=(uint32_t)setup_bytes;
  stream.audio=synthetic_audio;stream.audio_bytes=(uint32_t)audio_bytes;stream.offsets=synthetic_offsets;
  stream.frames=synthetic_frames;stream.granules=synthetic_granules;stream.modes=synthetic_modes;
  stream.packet_count=SYNTHETIC_PACKETS;stream.pcm_bytes=(SYNTHETIC_PACKETS-1)*32*4*2;return stream;
}
static void residue_no_work_controls(void){
  /* Enter the real registered callback with an empty arena. A generic public
     decode sweep cannot prove that no-work paths allocate no scratch: an
     unwanted allocation could otherwise become another accepted OOM case. */
  for(int floor_type=0;floor_type<2;floor_type++)for(int residue_type=0;residue_type<3;residue_type++)
    for(int kind=0;kind<4;kind++)for(int zero=0;zero<2;zero++){
      int shape=kind==0?2:(kind==1?3:0);
      xiph_case_t stream=synthetic_build(floor_type,residue_type,shape);
      decoder_t decoder;decoder_open(&stream,&decoder,zero);
      codec_setup_info *ci=decoder.info.codec_setup;private_state *backend=decoder.dsp.backend_state;
      CHECK(ci && ci->residues==1 && ci->residue_type[0]==residue_type);
      CHECK(backend && backend->residue && backend->residue[0]);
      vorbis_info_residue0 *info=(vorbis_info_residue0 *)ci->residue_param[0];CHECK(info);
      long saved_end=info->end;
      if(kind==3)info->end=info->begin; /* n<=0, after a normal valid DSP open. */
      decoder.block.pcmend=64;
      CHECK(!decoder.block.localstore && decoder.block.localalloc==0 && decoder.block.localtop==0);
      CHECK(decoder.block.totaluse==0 && !decoder.block.reap);
      input_t packet=input_create(stream.audio,stream.offsets[1]);
      oggpack_readinit(&decoder.block.opb,packet.data,(int)packet.size);
      struct { uint64_t before;float samples[4][32];uint64_t after; } pcm;
      memset(&pcm,0,sizeof(pcm));pcm.before=pcm.after=guard;
      float *vectors[4],*saved_vectors[4];int nonzero[4],saved_nonzero[4];
      for(int channel=0;channel<4;channel++){
        vectors[channel]=pcm.samples[channel];nonzero[channel]=kind==2?0:1;
        for(int sample=0;sample<32;sample++)pcm.samples[channel][sample]=(float)(channel*32+sample-64)/16.f;
      }
      unsigned char saved_pcm[sizeof(pcm)],saved_block[sizeof(decoder.block)],saved_info[sizeof(*info)];
      memcpy(saved_pcm,&pcm,sizeof(pcm));memcpy(saved_block,&decoder.block,sizeof(decoder.block));
      memcpy(saved_info,info,sizeof(*info));memcpy(saved_vectors,vectors,sizeof(vectors));
      memcpy(saved_nonzero,nonzero,sizeof(nonzero));
      size_t live=xiph_port_test_live(),bytes=xiph_port_test_bytes();policy(1,zero);
      CHECK(_residue_P[residue_type]->inverse(&decoder.block,backend->residue[0],vectors,nonzero,4)==0);
      CHECK(xiph_port_test_attempts()==0 && xiph_port_test_failures()==0);
      CHECK(xiph_port_test_live()==live && xiph_port_test_bytes()==bytes);
      CHECK(memcmp(saved_block,&decoder.block,sizeof(decoder.block))==0);
      CHECK(memcmp(saved_pcm,&pcm,sizeof(pcm))==0 && memcmp(saved_info,info,sizeof(*info))==0);
      CHECK(memcmp(saved_vectors,vectors,sizeof(vectors))==0 && memcmp(saved_nonzero,nonzero,sizeof(nonzero))==0);
      /* The no-work callback must leave the first refusal armed. This real,
         positive allocation proves it did not consume or reset that hook. */
      CHECK(_vorbis_block_alloc(&decoder.block,8)==NULL);
      CHECK(xiph_port_test_attempts()==1 && xiph_port_test_failures()==1);
      CHECK(xiph_port_test_live()==live && xiph_port_test_bytes()==bytes);
      CHECK(memcmp(saved_block,&decoder.block,sizeof(decoder.block))==0);
      CHECK(memcmp(saved_pcm,&pcm,sizeof(pcm))==0 && memcmp(saved_info,info,sizeof(*info))==0);
      CHECK(memcmp(saved_vectors,vectors,sizeof(vectors))==0 && memcmp(saved_nonzero,nonzero,sizeof(nonzero))==0);
      info->end=saved_end;input_destroy(&packet);decoder_close(&decoder);scenarios++;
    }
}
int xiph_packet_arena_tests(void){reset_counts();arena_controls();policy(0,0);return (int)scenarios;}
int xiph_packet_case_tests(unsigned index){
  _Static_assert(sizeof(float)==4,"Recovery compares binary32 storage");
  CHECK(index<XIPH_CASE_COUNT);reset_counts();stream_sweep(&xiph_cases[index]);policy(0,0);return (int)scenarios;
}
int xiph_packet_synthetic_tests(void){
  reset_counts();
  for(int f=0;f<2;f++)for(int r=0;r<3;r++)for(int shape=0;shape<6;shape++){
    xiph_case_t stream=synthetic_build(f,r,shape);stream_sweep(&stream);
  }
  residue_no_work_controls();
  CHECK(floor_types==3 && residue_types==7);no_owners();policy(0,0);return (int)scenarios;
}
int xiph_packet_tests(void){
  reset_counts();arena_controls();
  for(unsigned i=0;i<XIPH_CASE_COUNT;i++)stream_sweep(&xiph_cases[i]);
  for(int f=0;f<2;f++)for(int r=0;r<3;r++)for(int shape=0;shape<6;shape++){
    xiph_case_t stream=synthetic_build(f,r,shape);stream_sweep(&stream);
  }
  residue_no_work_controls();
  CHECK(floor_types==3 && residue_types==7);no_owners();policy(0,0);return (int)scenarios;
}
