/* Vorbis I 8.6.3 scatter and 8.6.2 complete-word EOP frontier.
   The oracle uses literal Huffman words and original-entry quantizer values,
   independently of packed entry order and the implementation's scatter loop. */
#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <ogg/ogg.h>
#include "codebook.h"
#include "vorbis_xiph_alloc.h"

enum { MAX_N=4608, MAX_DIM=255, PAYLOAD_BYTES=4096 };
static struct { uint32_t before; float values[MAX_N]; uint32_t after; } output;
static float expected[MAX_N];
static struct { uint32_t before; unsigned char bytes[PAYLOAD_BYTES]; uint32_t after; } input;
static unsigned char input_copy[PAYLOAD_BYTES];
static long quantizers[8*MAX_DIM];
static char dense_lengths[8]={3,3,3,3,3,3,3,3};
static char sparse_lengths[8]={2,0,1,0,0,3,0,3};
static char singleton_lengths[1]={1};
static int scenarios;
#define CHECK(x) do { int ok=!!(x); assert(ok); if(!ok)abort(); } while(0)

static int original_entry(int family,int word){
  static const int sparse[4]={0,2,5,7};
  if(family==0)return (word*5+3)%8;
  if(family==1)return sparse[(word*3+1)%4];
  return 0;
}
static unsigned word_width(int family,int word){
  int entry=original_entry(family,word);
  if(family==0)return 3;
  if(family==2)return 1;
  return entry==0?2U:entry==2?1U:3U;
}
static unsigned word_code(int family,int word){
  int entry=original_entry(family,word);
  if(family==0)return (unsigned)entry;
  /* Both singleton bit values decode its sole entry. Alternate them. */
  if(family==2)return (unsigned)word%2;
  return entry==0?0U:entry==2?1U:entry==5?2U:3U;
}
static int quantized(int entry,int component){return (entry*7+component*3)%8;}
static float initial_value(int index){return (float)(index%33-16)*0.125f;}
static int stream_bits(int family,int words){
  int bits=0;
  for(int word=0;word<words;word++)bits+=(int)word_width(family,word);
  return bits;
}
static void bit_put(int position,unsigned value){
  CHECK(position>=0 && position<PAYLOAD_BYTES*8 && value<=1);
  if(value)input.bytes[position/8]|=(unsigned char)(1U<<(position%8));
}
static void run_case(codebook *book,int family,int sequence,int n,int cut,int pad){
  CHECK(n>=0 && n<=MAX_N && book->dim>0 && pad>=0 && pad<8);
  int dim=(int)book->dim,words=n/dim,bits=stream_bits(family,words),cursor=pad;
  CHECK(cut>=0 && cut<=bits && (cut==bits || (pad+cut)%8==0));
  input.before=UINT32_C(0x72657330);input.after=UINT32_C(0x10293847);
  memset(input.bytes,0,sizeof(input.bytes));
  for(int bit=0;bit<pad;bit++)bit_put(bit,(unsigned)bit%2);
  for(int word=0;word<words;word++){
    unsigned width=word_width(family,word),code=word_code(family,word);
    for(unsigned bit=0;bit<width;bit++)bit_put(cursor++,(code>>(width-1-bit))&1U);
  }
  memcpy(input_copy,input.bytes,sizeof(input_copy));
  output.before=UINT32_C(0x5c17ab93);output.after=UINT32_C(0x93ba71c5);
  for(int i=0;i<MAX_N;i++)output.values[i]=expected[i]=initial_value(i);
  int consumed=0,complete=0;
  for(int word=0;word<words;word++){
    int width=(int)word_width(family,word);
    if(consumed+width>cut)break;
    consumed+=width;complete++;
  }
  /* Destination-major oracle: invert scatter to find each destination's
     original word/component, then use original quantizers, not valuelist. */
  for(int destination=0;destination<dim*words;destination++){
    int word=destination%words,component=destination/words;
    if(word<complete){
      int value=0,entry=original_entry(family,word);
      if(sequence){
        for(int c=0;c<=component;c++)value+=quantized(entry,c)-3;
      }else value=quantized(entry,component)-3;
      expected[destination]+=(float)value;
    }
  }
  oggpack_buffer reader,scalar;
  int bytes=(pad+cut+7)/8;
  oggpack_readinit(&reader,input.bytes,bytes);oggpack_adv(&reader,pad);scalar=reader;
  for(int word=0;word<words;word++){
    long entry=vorbis_book_decode(book,&scalar);
    if(word<complete)CHECK(entry==original_entry(family,word));
    else {CHECK(entry==-1);break;}
  }
  codebook unchanged=*book;
  size_t live=xiph_port_test_live(),allocated=xiph_port_test_bytes();
  xiph_port_test_reset(1);
  long status=vorbis_book_decodevs_add(book,output.values,&reader,n);
  CHECK(status==(complete==words?0:-1));
  CHECK(xiph_port_test_attempts()==0 && xiph_port_test_failures()==0);
  CHECK(xiph_port_test_live()==live && xiph_port_test_bytes()==allocated);
  CHECK(memcmp(&unchanged,book,sizeof(*book))==0);
  CHECK(reader.endbyte==scalar.endbyte && reader.endbit==scalar.endbit);
  CHECK(reader.ptr==scalar.ptr && reader.buffer==scalar.buffer && reader.storage==scalar.storage);
  CHECK(memcmp(output.values,expected,sizeof(expected))==0);
  CHECK(output.before==UINT32_C(0x5c17ab93) && output.after==UINT32_C(0x93ba71c5));
  CHECK(input.before==UINT32_C(0x72657330) && input.after==UINT32_C(0x10293847));
  CHECK(memcmp(input.bytes,input_copy,sizeof(input_copy))==0);
  scenarios++;
}
static void run_shape(codebook *book,int family,int sequence,int words,int tail){
  int n=words*(int)book->dim+tail,bits=stream_bits(family,words);
  for(int pad=0;pad<8;pad++)run_case(book,family,sequence,n,bits,pad);
  /* Align each cutoff to a real byte boundary by varying the initial offset.
     This tests every prefix bit, including cuts inside variable-length words. */
  for(int cut=0;cut<bits;cut++)run_case(book,family,sequence,n,cut,(8-cut%8)%8);
}
static void no_op_controls(void){
  codebook empty;memset(&empty,0,sizeof(empty));
  /* The pre-existing empty-book branch must not divide by dim=0. */
  oggpack_buffer reader,unchanged;oggpack_readinit(&reader,input.bytes,0);unchanged=reader;
  for(int i=0;i<MAX_N;i++)output.values[i]=expected[i]=initial_value(i);
  xiph_port_test_reset(1);
  CHECK(vorbis_book_decodevs_add(&empty,output.values,&reader,4096)==0);
  CHECK(memcmp(&reader,&unchanged,sizeof(reader))==0);
  CHECK(memcmp(output.values,expected,sizeof(expected))==0);
  CHECK(xiph_port_test_attempts()==0 && xiph_port_test_failures()==0);
  scenarios++;
}
int xiph_residue_tests(void){
  static const int dimensions[]={1,2,3,7,16,255};
  static const int word_counts[]={0,1,2,5,17};
  scenarios=0;
  CHECK(xiph_port_test_live()==0 && xiph_port_test_bytes()==0);
  for(int family=0;family<3;family++)for(int sequence=0;sequence<2;sequence++){
    for(unsigned d=0;d<sizeof(dimensions)/sizeof(*dimensions);d++){
      int dim=dimensions[d],entries=family==2?1:8;
      for(int entry=0;entry<entries;entry++)for(int c=0;c<dim;c++)
        quantizers[entry*dim+c]=quantized(entry,c);
      static_codebook source={dim,entries,family==0?dense_lengths:family==1?sparse_lengths:singleton_lengths,
        2,-533200896L,1611661312L,4,sequence,quantizers,0};
      codebook book;xiph_port_test_reset(0);
      CHECK(vorbis_book_init_decode(&book,&source)==0);
      for(unsigned w=0;w<sizeof(word_counts)/sizeof(*word_counts);w++)
        run_shape(&book,family,sequence,word_counts[w],0);
      if(dim>1)run_shape(&book,family,sequence,5,dim-1);
      if(dim==1){
        /* The original two ILP32 arrays require 32768 stack bytes here. */
        int bits=stream_bits(family,4096);
        run_case(&book,family,sequence,4096,bits,0);
        for(int word=0;word<4096;word+=127){
          int cut=stream_bits(family,word);
          run_case(&book,family,sequence,4096,cut,(8-cut%8)%8);
        }
      }
      xiph_port_test_reset(0);vorbis_book_clear(&book);
      CHECK(xiph_port_test_live()==0 && xiph_port_test_bytes()==0);
    }
  }
  no_op_controls();xiph_port_test_reset(0);
  CHECK(xiph_port_test_live()==0 && xiph_port_test_bytes()==0);
  return scenarios;
}
