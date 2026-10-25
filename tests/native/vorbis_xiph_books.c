/* Focused decode-codebook port tests. No encoder, container, or PCM oracle. */
#include <assert.h>
#include <limits.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include <ogg/ogg.h>
#include "codebook.h"
#include "vorbis_xiph_alloc.h"

extern ogg_uint32_t *_make_words(char *lengths,long entries,long sparsecount);

enum { DENSE_ENTRIES=4096, PAYLOAD_BYTES=8192 };
static char dense_lengths[DENSE_ENTRIES];
static char sparse_lengths[8]={2,0,1,0,0,3,0,3};
static char singleton_lengths[8]={0,0,0,0,0,0,1,0};
static char empty_lengths[8];
static long map1_quant[2]={0,2};
static long map2_quant[24];
static struct {
  uint32_t before;
  unsigned char bytes[PAYLOAD_BYTES];
  uint32_t after;
} payload;
static size_t payload_bits;
static int checks;

#define CHECK(expression) do { \
  int ok=!!(expression); \
  assert(ok); \
  if(!ok)abort(); \
  ++checks; \
} while(0)

static const int sparse_order[4]={0,5,7,2};
static const ogg_uint32_t sparse_codes[4]={
  UINT32_C(0),UINT32_C(0x40000000),
  UINT32_C(0x60000000),UINT32_C(0x80000000)
};
static const char sparse_sorted_lengths[4]={2,3,3,1};
static const float map1_values[2][8]={
  {-3,-3, -1,-3, -1,-1, -3,-1},
  {-3,-6, -1,-4, -1,-2, -3,-4}
};
static const float map2_values[2][12]={
  {-3,-2,-1, 4,-3,-2, 2,3,4, 3,4,-3},
  {-3,-5,-6, 4,1,-1, 2,5,9, 3,7,4}
};

static void no_live_allocations(void){
  CHECK(xiph_port_test_live()==0);
  CHECK(xiph_port_test_bytes()==0);
}

static void payload_begin(void){
  payload.before=UINT32_C(0x13579bdf);
  payload.after=UINT32_C(0xfdb97531);
  memset(payload.bytes,0,sizeof(payload.bytes));
  payload_bits=0;
}

static void payload_put(unsigned value,unsigned width){
  unsigned bit;
  CHECK(width<=32);
  CHECK(payload_bits+width<=sizeof(payload.bytes)*8);
  for(bit=0;bit<width;bit++,payload_bits++)
    if((value>>bit)&1U)
      payload.bytes[payload_bits/8]|=(unsigned char)(1U<<(payload_bits%8));
}

static unsigned reversed(unsigned value,unsigned width){
  unsigned result=0;
  while(width--){
    result=(result<<1)|(value&1U);
    value>>=1;
  }
  return result;
}

static void payload_reader(oggpack_buffer *reader){
  oggpack_readinit(reader,payload.bytes,(int)((payload_bits+7)/8));
}

static void payload_guards(void){
  CHECK(payload.before==UINT32_C(0x13579bdf));
  CHECK(payload.after==UINT32_C(0xfdb97531));
}

static void sparse_payload(void){
  payload_begin();
  /* Entry order 0,2,5,7 has MSB-first words 00,1,010,011. */
  payload_put(0,2);
  payload_put(1,1);
  payload_put(2,3);
  payload_put(6,3);
}

static void verify_sparse(codebook *book,const static_codebook *source){
  static const long entries[4]={0,2,5,7};
  oggpack_buffer reader;
  int i,k;
  CHECK(book->entries==8);
  CHECK(book->used_entries==4);
  CHECK(book->dim==source->dim);
  for(i=0;i<4;i++){
    CHECK(book->dec_index[i]==sparse_order[i]);
    CHECK(book->codelist[i]==sparse_codes[i]);
    CHECK(book->dec_codelengths[i]==sparse_sorted_lengths[i]);
  }
  if(source->maptype==0){
    CHECK(book->valuelist==NULL);
  }else{
    const float *expected=source->maptype==1
      ?map1_values[source->q_sequencep]:map2_values[source->q_sequencep];
    CHECK(book->valuelist!=NULL);
    for(i=0;i<4*source->dim;i++)
      CHECK(book->valuelist[i]==expected[i]);
  }
  sparse_payload();
  payload_reader(&reader);
  for(i=0;i<4;i++){
    long decoded=vorbis_book_decode(book,&reader);
    CHECK(decoded==entries[i]);
  }
  CHECK(oggpack_bits(&reader)==9);
  if(source->maptype){
    payload_reader(&reader);
    for(i=0;i<4;i++){
      struct { float before,values[3],after; } output;
      long status;
      int sorted;
      output.before=12345;
      output.after=-12345;
      for(k=0;k<3;k++)output.values[k]=999;
      status=vorbis_book_decodev_set(book,output.values,&reader,(int)source->dim);
      CHECK(status==0);
      for(sorted=0;sorted<4;sorted++)
        if(sparse_order[sorted]==entries[i])break;
      CHECK(sorted<4);
      for(k=0;k<source->dim;k++)
        CHECK(output.values[k]==book->valuelist[sorted*source->dim+k]);
      for(k=(int)source->dim;k<3;k++)CHECK(output.values[k]==999);
      CHECK(output.before==12345);
      CHECK(output.after==-12345);
    }
    CHECK(oggpack_bits(&reader)==9);
  }
  payload_guards();
}

static void verify_dense(codebook *book){
  oggpack_buffer reader;
  int i;
  CHECK(book->entries==DENSE_ENTRIES);
  CHECK(book->used_entries==DENSE_ENTRIES);
  CHECK(book->dim==1);
  CHECK(book->valuelist==NULL);
  CHECK(book->dec_firsttablen==8);
  payload_begin();
  for(i=0;i<DENSE_ENTRIES;i++){
    CHECK(book->dec_index[i]==i);
    CHECK(book->dec_codelengths[i]==12);
    CHECK(book->codelist[i]==(ogg_uint32_t)i<<20);
    payload_put(reversed((unsigned)i,12),12);
  }
  payload_reader(&reader);
  for(i=0;i<DENSE_ENTRIES;i++){
    long decoded=vorbis_book_decode(book,&reader);
    CHECK(decoded==i);
  }
  CHECK(oggpack_bits(&reader)==DENSE_ENTRIES*12);
  /* MSB-first 100000000000 is entry2048. It reaches an upper first-table
     hint whose construction formerly shifted a signed int into its sign. */
  payload_begin();
  payload_put(1,12);
  payload_reader(&reader);
  {
    long decoded=vorbis_book_decode(book,&reader);
    CHECK(decoded==2048);
  }
  CHECK(oggpack_bits(&reader)==12);
  payload_guards();
}

static void verify_singleton(codebook *book,const static_codebook *source){
  oggpack_buffer reader;
  int bit;
  CHECK(book->entries==8);
  CHECK(book->used_entries==1);
  CHECK(book->dec_index[0]==6);
  CHECK(book->codelist[0]==0);
  CHECK(book->dec_codelengths[0]==1);
  CHECK(book->dec_firsttablen==1);
  CHECK(book->dec_firsttable[0]==1 && book->dec_firsttable[1]==1);
  if(source->maptype){
    CHECK(book->valuelist!=NULL);
    CHECK(book->valuelist[0]==-1);
    CHECK(book->valuelist[1]==0);
    CHECK(book->valuelist[2]==1);
  }else{
    CHECK(book->valuelist==NULL);
  }
  for(bit=0;bit<2;bit++){
    long decoded;
    payload_begin();
    payload_put((unsigned)bit,1);
    payload_reader(&reader);
    decoded=vorbis_book_decode(book,&reader);
    CHECK(decoded==6);
    CHECK(oggpack_bits(&reader)==1);
    payload_guards();
  }
}

static void verify_book(codebook *book,const static_codebook *source,int kind){
  if(kind==0)verify_dense(book);
  else if(kind==1)verify_sparse(book,source);
  else verify_singleton(book,source);
}

static void failure_sweep(const static_codebook *source,int kind){
  codebook book,zero;
  size_t attempts,ordinal;
  int status;
  memset(&zero,0,sizeof(zero));
  no_live_allocations();
  xiph_port_test_reset(0);
  status=vorbis_book_init_decode(&book,source);
  CHECK(status==0);
  attempts=xiph_port_test_attempts();
  CHECK(attempts==(source->maptype?8U:7U));
  CHECK(xiph_port_test_realloc_attempts()==0);
  CHECK(xiph_port_test_failures()==0);
  verify_book(&book,source,kind);
  CHECK(xiph_port_test_attempts()==attempts);
  vorbis_book_clear(&book);
  CHECK(memcmp(&book,&zero,sizeof(book))==0);
  no_live_allocations();
  for(ordinal=1;ordinal<=attempts;ordinal++){
    xiph_port_test_reset(ordinal);
    memset(&book,0xa5,sizeof(book));
    status=vorbis_book_init_decode(&book,source);
    CHECK(status==-1);
    CHECK(xiph_port_test_failures()==1);
    CHECK(xiph_port_test_attempts()==ordinal);
    CHECK(xiph_port_test_realloc_attempts()==0);
    CHECK(memcmp(&book,&zero,sizeof(book))==0);
    no_live_allocations();
    vorbis_book_clear(&book);
    no_live_allocations();
    xiph_port_test_reset(0);
    status=vorbis_book_init_decode(&book,source);
    CHECK(status==0);
    CHECK(xiph_port_test_attempts()==attempts);
    CHECK(xiph_port_test_failures()==0);
    verify_book(&book,source,kind);
    vorbis_book_clear(&book);
    no_live_allocations();
  }
}

static void empty_and_range_checks(void){
  codebook book,zero;
  static_codebook source={3,8,empty_lengths,0,0,0,0,0,NULL,0};
  oggpack_buffer reader;
  ogg_uint32_t *words;
  float *values;
  long decoded;
  int status;
  memset(&zero,0,sizeof(zero));
  xiph_port_test_reset(0);
  status=vorbis_book_init_decode(&book,&source);
  CHECK(status==0);
  CHECK(book.entries==8 && book.used_entries==0 && book.dim==3);
  CHECK(xiph_port_test_attempts()==0);
  payload_begin();
  payload_put(1,1);
  payload_reader(&reader);
  decoded=vorbis_book_decode(&book,&reader);
  CHECK(decoded==-1);
  CHECK(oggpack_bits(&reader)==0);
  vorbis_book_clear(&book);
  CHECK(memcmp(&book,&zero,sizeof(book))==0);
  no_live_allocations();
  words=_make_words(dense_lengths,-1,0);
  CHECK(words==NULL);
  words=_make_words(dense_lengths,1,2);
  CHECK(words==NULL);
  words=_make_words(dense_lengths,LONG_MAX,0);
  CHECK(words==NULL);
  source.maptype=2;
  source.dim=LONG_MAX;
  values=_book_unquantize(&source,INT_MAX,NULL);
  CHECK(values==NULL);
  values=_book_unquantize(&source,-1,NULL);
  CHECK(values==NULL);
  CHECK(xiph_port_test_attempts()==0);
  no_live_allocations();
}

static void zero_dimension_scalar_checks(void){
  static const long entries[4]={0,2,5,7};
  static_codebook source={0,8,sparse_lengths,2,
    -533200896L,1611661312L,4,0,map2_quant,0};
  codebook book;
  oggpack_buffer reader;
  int mode,i,status;
  for(mode=0;mode<2;mode++){
    no_live_allocations();
    xiph_port_test_reset(0);
    xiph_port_test_zero_null(mode);
    status=vorbis_book_init_decode(&book,&source);
    CHECK(status==0);
    CHECK(book.entries==8 && book.used_entries==4 && book.dim==0);
    if(mode)CHECK(book.valuelist==NULL);
    for(i=0;i<4;i++){
      CHECK(book.dec_index[i]==sparse_order[i]);
      CHECK(book.codelist[i]==sparse_codes[i]);
      CHECK(book.dec_codelengths[i]==sparse_sorted_lengths[i]);
    }
    sparse_payload();
    payload_reader(&reader);
    for(i=0;i<4;i++){
      long decoded=vorbis_book_decode(&book,&reader);
      CHECK(decoded==entries[i]);
    }
    CHECK(oggpack_bits(&reader)==9);
    CHECK(xiph_port_test_failures()==0);
    payload_guards();
    vorbis_book_clear(&book);
    no_live_allocations();
  }
  xiph_port_test_zero_null(0);
}

int xiph_book_tests(void){
  static_codebook source={1,DENSE_ENTRIES,dense_lengths,0,0,0,0,0,NULL,0};
  int entry,coordinate,maptype,sequence;
  checks=0;
  no_live_allocations();
  xiph_port_test_zero_null(0);
  memset(dense_lengths,12,sizeof(dense_lengths));
  for(entry=0;entry<8;entry++)
    for(coordinate=0;coordinate<3;coordinate++)
      map2_quant[entry*3+coordinate]=(entry*3+coordinate)%8;
  failure_sweep(&source,0);
  source.entries=8;
  source.lengthlist=sparse_lengths;
  source.dim=3;
  failure_sweep(&source,1);
  source.q_min=-533200896L; /* Exact -3, matching upstream's static test. */
  source.q_delta=1611661312L; /* Exact 1. */
  source.q_quant=4;
  for(maptype=1;maptype<=2;maptype++){
    source.maptype=maptype;
    source.dim=maptype==1?2:3;
    source.quantlist=maptype==1?map1_quant:map2_quant;
    for(sequence=0;sequence<2;sequence++){
      source.q_sequencep=sequence;
      failure_sweep(&source,1);
    }
  }
  source.lengthlist=singleton_lengths;
  source.q_sequencep=0;
  failure_sweep(&source,2);
  source.maptype=0;
  failure_sweep(&source,2);
  empty_and_range_checks();
  zero_dimension_scalar_checks();
  no_live_allocations();
  xiph_port_test_reset(0);
  return checks;
}
