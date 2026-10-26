/* Header allocation failures, cleanup/reopen and error classification.
   Recovery float fingerprints establish same-process identity only; the
   retained original31 PCM comparison remains the independent numeric gate. */
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
#include "registry.h"
#include "native_vorbis_xiph_header_error.h"
#include "vorbis_xiph_alloc.h"
#include "cases.h"

#define CHECK(x) do { int ok=!!(x); assert(ok); if(!ok)abort(); } while(0)
enum { PACKED_CAPACITY=512 };
static const uint64_t guard=UINT64_C(0xb178ae3204c95fd6);
static int scenarios;
static unsigned floor_types,residue_types;
typedef struct { unsigned char *base,*data;const unsigned char *original;size_t size; } input_t;
typedef struct {
  const xiph_case_t *base;
  const unsigned char *comment,*setup;
  size_t comment_bytes,setup_bytes;
} stream_t;
typedef struct { uint64_t a,b;uint32_t packets,frames,samples; } fingerprint_t;
static struct { uint64_t before;unsigned char data[PACKED_CAPACITY];uint64_t after; } packed;
static size_t packed_bits;
static unsigned char synthetic_comment[128],synthetic_setup[PACKED_CAPACITY];
static size_t synthetic_comment_bytes,synthetic_setup_bytes;
static size_t synthetic_floor_start,synthetic_residue_start,synthetic_mapping_start;

static void no_owners(void){CHECK(xiph_port_test_live()==0 && xiph_port_test_bytes()==0);}
static input_t input_create(const unsigned char *bytes,size_t size){
  input_t input={0};CHECK(bytes && size<=LONG_MAX && size<=SIZE_MAX-16);
  input.base=malloc(size+16);CHECK(input.base);input.data=input.base+8;
  input.original=bytes;input.size=size;memcpy(input.base,&guard,8);
  memcpy(input.data,bytes,size);memcpy(input.data+size,&guard,8);return input;
}
static void input_check(const input_t *input){
  uint64_t first,last;memcpy(&first,input->base,8);memcpy(&last,input->data+input->size,8);
  CHECK(first==guard && last==guard && memcmp(input->data,input->original,input->size)==0);
}
static void input_destroy(input_t *input){input_check(input);free(input->base);}
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
static const unsigned char *header_data(const stream_t *stream,int number,size_t *bytes){
  if(number==0){*bytes=stream->base->identification_bytes;return stream->base->identification;}
  if(number==1){*bytes=stream->comment_bytes;return stream->comment;}
  *bytes=stream->setup_bytes;return stream->setup;
}
static int stream_open(const stream_t *stream,vorbis_info *info,vorbis_comment *comment){
  vorbis_info_init(info);vorbis_comment_init(comment);
  for(int h=0;h<3;h++){
    size_t bytes;const unsigned char *data=header_data(stream,h,&bytes);
    int status=header_read(info,comment,data,bytes,h);if(status)return status;
  }
  return 0;
}
static void graph_check(const stream_t *stream,const vorbis_info *info,const vorbis_comment *comment){
  const codec_setup_info *ci=info->codec_setup;const xiph_case_t *test=stream->base;
  CHECK(ci && info->rate==(long)test->rate && info->channels==(int)test->channels);
  CHECK(vorbis_info_blocksize((vorbis_info *)info,0)==(int)test->short_block);
  CHECK(vorbis_info_blocksize((vorbis_info *)info,1)==(int)test->long_block);
  CHECK(comment->vendor && comment->comments>=0 && comment->user_comments && comment->comment_lengths);
  CHECK(ci->books>=1 && ci->books<=256 && ci->fullbooks==NULL);
  CHECK(ci->floors>=1 && ci->floors<=64 && ci->residues>=1 && ci->residues<=64);
  CHECK(ci->maps>=1 && ci->maps<=64 && ci->modes>=1 && ci->modes<=64);
  for(int i=0;i<ci->books;i++){
    const static_codebook *book=ci->book_param[i];CHECK(book && book->allocedp==1);
    CHECK(book->entries>=0 && book->dim>=0 && book->maptype>=0 && book->maptype<=2);
    CHECK(book->entries==0 || book->lengthlist);
  }
  for(int i=0;i<ci->floors;i++){
    CHECK(ci->floor_type[i]>=0 && ci->floor_type[i]<VI_FLOORB && ci->floor_param[i]);
    floor_types|=1U<<(unsigned)ci->floor_type[i];
  }
  for(int i=0;i<ci->residues;i++){
    CHECK(ci->residue_type[i]>=0 && ci->residue_type[i]<VI_RESB && ci->residue_param[i]);
    residue_types|=1U<<(unsigned)ci->residue_type[i];
  }
  for(int i=0;i<ci->maps;i++)CHECK(ci->map_type[i]==0 && ci->map_param[i]);
  for(int i=0;i<ci->modes;i++){
    const vorbis_info_mode *mode=ci->mode_param[i];CHECK(mode);
    CHECK((mode->blockflag==0 || mode->blockflag==1) && mode->windowtype==0 && mode->transformtype==0);
    CHECK(mode->mapping>=0 && mode->mapping<ci->maps);
  }
}
static void stream_close(vorbis_info *info,vorbis_comment *comment){
  vorbis_info zero_info;vorbis_comment zero_comment;
  memset(&zero_info,0,sizeof(zero_info));memset(&zero_comment,0,sizeof(zero_comment));
  vorbis_comment_clear(comment);vorbis_info_clear(info);no_owners();
  CHECK(memcmp(info,&zero_info,sizeof(*info))==0 && memcmp(comment,&zero_comment,sizeof(*comment))==0);
  vorbis_comment_clear(comment);vorbis_info_clear(info);no_owners();
}
static void header_sweep(const stream_t *stream){
  vorbis_info info;vorbis_comment comment;no_owners();xiph_port_test_reset(0);
  CHECK(stream_open(stream,&info,&comment)==0);graph_check(stream,&info,&comment);
  size_t attempts=xiph_port_test_attempts();CHECK(attempts>0 && xiph_port_test_failures()==0);
  CHECK(xiph_port_test_realloc_attempts()==0);stream_close(&info,&comment);scenarios++;
  for(size_t ordinal=1;ordinal<=attempts;ordinal++){
    xiph_port_test_reset(ordinal);int status=stream_open(stream,&info,&comment);
    CHECK(status==OV_EFAULT && xiph_port_test_failures()==1 && xiph_port_test_attempts()==ordinal);
    CHECK(xiph_port_test_realloc_attempts()==0);stream_close(&info,&comment);scenarios++;
    xiph_port_test_reset(0);CHECK(stream_open(stream,&info,&comment)==0);
    CHECK(xiph_port_test_attempts()==attempts && xiph_port_test_failures()==0);
    graph_check(stream,&info,&comment);stream_close(&info,&comment);scenarios++;
  }
}
static fingerprint_t decode_fingerprint(const stream_t *stream){
  const xiph_case_t *test=stream->base;vorbis_info info;vorbis_comment comment;
  vorbis_dsp_state dsp;vorbis_block block;memset(&dsp,0,sizeof(dsp));memset(&block,0,sizeof(block));
  fingerprint_t result={UINT64_C(14695981039346656037),UINT64_C(0x93af5427e106c8bd),0,0,0};
  no_owners();xiph_port_test_reset(0);CHECK(stream_open(stream,&info,&comment)==0);
  graph_check(stream,&info,&comment);CHECK(vorbis_synthesis_init(&dsp,&info)==0);
  CHECK(vorbis_block_init(&dsp,&block)==0);
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
        result.b=((result.b<<7)|(result.b>>57))^((uint64_t)bits+result.samples);
        result.samples++;
      }
      frames+=(uint32_t)available;CHECK(vorbis_synthesis_read(&dsp,available)==0);
    }
    CHECK(available==0 && frames==test->frames[p]);result.frames+=frames;result.packets++;
    CHECK(memcmp(&value,&before,sizeof(value))==0);input_destroy(&input);
  }
  CHECK(result.packets==14 && result.samples*2==test->pcm_bytes);
  CHECK(vorbis_block_clear(&block)==0);vorbis_dsp_clear(&dsp);stream_close(&info,&comment);
  scenarios++;return result;
}
static void malformed_controls(const stream_t *stream){
  for(int h=0;h<3;h++)for(int kind=0;kind<2;kind++){
    vorbis_info info;vorbis_comment comment;xiph_port_test_reset(0);
    vorbis_info_init(&info);vorbis_comment_init(&comment);
    for(int prior=0;prior<h;prior++){
      size_t bytes;const unsigned char *data=header_data(stream,prior,&bytes);
      CHECK(header_read(&info,&comment,data,bytes,prior)==0);
    }
    size_t bytes;const unsigned char *data=header_data(stream,h,&bytes);CHECK(bytes>7);
    /* Preserve a complete version=0 in ID truncations: the upstream API
       otherwise reports OV_EVERSION before reaching its EOP checks. */
    CHECK(header_read(&info,&comment,data,kind?bytes-1:(h==0?11U:7U),h)==OV_EBADHEADER);
    CHECK(xiph_port_test_failures()==0);stream_close(&info,&comment);scenarios++;
  }
}
static void packed_begin(void){
  packed.before=packed.after=guard;memset(packed.data,0,sizeof(packed.data));packed_bits=0;
}
static void put(uint32_t value,unsigned width){
  CHECK(width<=32 && packed_bits+width<=PACKED_CAPACITY*8);
  for(unsigned bit=0;bit<width;bit++,packed_bits++)
    if((value>>bit)&1U)packed.data[packed_bits/8]|=(unsigned char)(1U<<(packed_bits%8));
}
static void text_bytes(const char *text){for(size_t i=0;i<strlen(text);i++)put((unsigned char)text[i],8);}
static void book_body(int ordered,int entries,int dim){
  put(UINT32_C(0x564342),24);put((uint32_t)dim,16);put((uint32_t)entries,24);put((uint32_t)ordered,1);
  if(ordered){put(0,5);if(entries)put((uint32_t)entries,entries==2?2U:1U);}
  else{put(0,1);for(int entry=0;entry<entries;entry++)put(0,5);}
  put(2,4);put(UINT32_C(0xe0380000),32);put(UINT32_C(0x60100000),32);put(3,4);put(0,1);
  for(int i=0;i<entries*dim;i++)put((uint32_t)i%4,4);
}
static void check_book(const static_codebook *book,int entries,int dim){
  CHECK(book && book->entries==entries && book->dim==dim && book->maptype==2 && book->allocedp==1);
  CHECK((uint32_t)book->q_min==UINT32_C(0xe0380000) && (uint32_t)book->q_delta==UINT32_C(0x60100000));
  CHECK(book->q_quant==4 && book->q_sequencep==0);
  for(int i=0;i<entries;i++)CHECK(book->lengthlist[i]==1);
  for(int i=0;i<entries*dim;i++)CHECK(book->quantlist[i]==i%4);
}
static void book_call(int checked,int entries,int dim,int zero_null,size_t ordinal){
  oggpack_buffer reader;int failure=0;no_owners();xiph_port_test_reset(ordinal);xiph_port_test_zero_null(zero_null);
  oggpack_readinit(&reader,packed.data,(int)((packed_bits+7)/8));
  static_codebook *book=checked?native_xiph_staticbook_unpack(&reader,&failure):vorbis_staticbook_unpack(&reader);
  int required=ordinal==1 || (ordinal==2 && entries>0) || (ordinal==3 && entries*dim>0);
  if(required){CHECK(book==NULL);if(checked)CHECK(failure==OV_EFAULT);CHECK(xiph_port_test_attempts()==ordinal);}
  else{check_book(book,entries,dim);CHECK(failure==0 && oggpack_bits(&reader)==(long)packed_bits);}
  CHECK(xiph_port_test_failures()==(ordinal?1U:0U));CHECK(packed.before==guard && packed.after==guard);
  if(book){vorbis_staticbook_destroy(book);}
  no_owners();scenarios++;
}
static void book_controls(void){
  static const int shapes[][2]={{2,1},{2,0},{0,1}};
  for(int ordered=0;ordered<2;ordered++)for(unsigned shape=0;shape<sizeof(shapes)/sizeof(*shapes);shape++){
    int entries=shapes[shape][0],dim=shapes[shape][1];packed_begin();book_body(ordered,entries,dim);
    for(int checked=0;checked<2;checked++)for(int zero=0;zero<2;zero++)
      for(size_t ordinal=0;ordinal<=3;ordinal++)book_call(checked,entries,dim,zero,ordinal);
  }
  packed_begin();book_body(0,2,1);packed.data[0]^=1;
  oggpack_buffer reader;int failure=0;xiph_port_test_reset(0);
  oggpack_readinit(&reader,packed.data,(int)((packed_bits+7)/8));
  CHECK(native_xiph_staticbook_unpack(&reader,&failure)==NULL && failure==0);
  CHECK(xiph_port_test_failures()==0);no_owners();scenarios++;
}
static void synthetic_build(int floor_type,int residue_type){
  packed_begin();put(3,8);text_bytes("vorbis");put(11,32);text_bytes("OOM fixture");put(3,32);
  put(17,32);text_bytes("ARTIST=allocation");put(0,32);put(12,32);text_bytes("TITLE=reopen");put(1,1);
  synthetic_comment_bytes=(packed_bits+7)/8;CHECK(synthetic_comment_bytes<=sizeof(synthetic_comment));
  memcpy(synthetic_comment,packed.data,synthetic_comment_bytes);
  packed_begin();put(5,8);text_bytes("vorbis");put(0,8);book_body(0,2,1);
  put(0,6);put(0,16); /* One time backend. */
  put(0,6);put((uint32_t)floor_type,16);synthetic_floor_start=packed_bits;
  if(floor_type==0){put(1,8);put(8000,16);put(8,16);put(3,6);put(60,8);put(0,4);put(0,8);}
  else{put(0,5);put(0,2);put(3,4);}
  put(0,6);put((uint32_t)residue_type,16);synthetic_residue_start=packed_bits;
  put(0,24);put(4,24);put(0,24);put(0,6);put(0,8);put(1,3);put(0,1);put(0,8);
  put(0,6);put(0,16);synthetic_mapping_start=packed_bits;
  put(0,1);put(0,1);put(0,2);put(0,8);put(0,8);put(0,8);
  put(0,6);put(0,1);put(0,16);put(0,16);put(0,8);put(1,1);
  synthetic_setup_bytes=(packed_bits+7)/8;memcpy(synthetic_setup,packed.data,synthetic_setup_bytes);
  CHECK(packed.before==guard && packed.after==guard);
}
static void wrapper_control(vorbis_info *info,const unsigned char *bytes,size_t length,size_t offset,
    void *(*unpack)(vorbis_info *,oggpack_buffer *),void (*release)(void *)){
  for(size_t ordinal=0;ordinal<=1;ordinal++){
    input_t input=input_create(bytes,length);oggpack_buffer reader;
    oggpack_readinit(&reader,input.data,(int)length);oggpack_adv(&reader,(int)offset);
    size_t live=xiph_port_test_live(),allocated=xiph_port_test_bytes();xiph_port_test_reset(ordinal);
    void *value=unpack(info,&reader);CHECK(ordinal?(value==NULL):(value!=NULL));
    CHECK(xiph_port_test_attempts()==1 && xiph_port_test_failures()==ordinal);
    if(value){release(value);}
    CHECK(xiph_port_test_live()==live && xiph_port_test_bytes()==allocated);
    input_destroy(&input);scenarios++;
  }
}
static void synthetic_controls(void){
  for(int floor_type=0;floor_type<2;floor_type++)for(int residue_type=0;residue_type<3;residue_type++){
    synthetic_build(floor_type,residue_type);
    stream_t stream={&xiph_cases[0],synthetic_comment,synthetic_setup,synthetic_comment_bytes,synthetic_setup_bytes};
    header_sweep(&stream);vorbis_info info;vorbis_comment comment;xiph_port_test_reset(0);
    CHECK(stream_open(&stream,&info,&comment)==0);graph_check(&stream,&info,&comment);
    CHECK(comment.comments==3 && comment.comment_lengths[0]==17 && comment.comment_lengths[1]==0 && comment.comment_lengths[2]==12);
    CHECK(!strcmp(comment.user_comments[0],"ARTIST=allocation") && !strcmp(comment.user_comments[1],"") && !strcmp(comment.user_comments[2],"TITLE=reopen"));
    wrapper_control(&info,synthetic_setup,synthetic_setup_bytes,synthetic_floor_start,_floor_P[floor_type]->unpack,_floor_P[floor_type]->free_info);
    wrapper_control(&info,synthetic_setup,synthetic_setup_bytes,synthetic_residue_start,_residue_P[residue_type]->unpack,_residue_P[residue_type]->free_info);
    wrapper_control(&info,synthetic_setup,synthetic_setup_bytes,synthetic_mapping_start,_mapping_P[0]->unpack,_mapping_P[0]->free_info);
    stream_close(&info,&comment);malformed_controls(&stream);
  }
}
int xiph_header_tests(void){
  _Static_assert(sizeof(float)==4,"Recovery fingerprints read binary32 storage");
  scenarios=0;floor_types=residue_types=0;no_owners();
  for(unsigned i=0;i<XIPH_CASE_COUNT;i++){
    const xiph_case_t *test=&xiph_cases[i];
    stream_t stream={test,test->comment,test->setup,test->comment_bytes,test->setup_bytes};
    fingerprint_t baseline=decode_fingerprint(&stream);header_sweep(&stream);
    fingerprint_t reopened=decode_fingerprint(&stream);
    CHECK(baseline.a==reopened.a && baseline.b==reopened.b && baseline.packets==reopened.packets);
    CHECK(baseline.frames==reopened.frames && baseline.samples==reopened.samples);
    malformed_controls(&stream);
  }
  synthetic_controls();book_controls();CHECK(floor_types==3 && residue_types==7);
  no_owners();xiph_port_test_reset(0);return scenarios;
}
