/* Independent bit-at-a-time reader oracle; no upstream writer is used. */
#include <assert.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <ogg/ogg.h>

static const unsigned char patterns[6][8]={
  {0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00},
  {0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff},
  {0x80,0x00,0x00,0x00,0x80,0x00,0x00,0x00},
  {0x80,0x01,0xfe,0x91,0xf1,0x83,0xff,0x00},
  {0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80},
  {0xfe,0x7f,0xa5,0x5a,0xff,0x00,0xc3,0x81}
};
static struct {
  uint32_t before;
  unsigned char bytes[8];
  uint32_t after;
} guarded;
static int probes;

#define CHECK(expression) do { \
  int ok=!!(expression); \
  assert(ok); \
  if(!ok)abort(); \
} while(0)

static ogg_uint32_t reference(const unsigned char *bytes,size_t start,
                              unsigned width,int big){
  ogg_uint32_t value=0;
  unsigned i;
  for(i=0;i<width;i++){
    size_t position=start+i;
    unsigned shift=(unsigned)(position%8);
    unsigned bit;
    if(big)shift=7-shift;
    bit=(bytes[position/8]>>shift)&1U;
    if(big)value=(value<<1)|bit;
    else value|=(ogg_uint32_t)bit<<i;
  }
  return value;
}

static long look(oggpack_buffer *reader,int width,int big){
  return big?oggpackB_look(reader,width):oggpack_look(reader,width);
}

static long read_bits(oggpack_buffer *reader,int width,int big){
  return big?oggpackB_read(reader,width):oggpack_read(reader,width);
}

static void initialize(oggpack_buffer *reader,unsigned char *bytes,
                       size_t length,size_t start){
  oggpack_readinit(reader,bytes,(int)length);
  reader->endbyte=(long)(start/8);
  reader->endbit=(int)(start%8);
  if(bytes)reader->ptr=bytes+start/8;
}

static void failed_state(const oggpack_buffer *reader,size_t length){
  CHECK(reader->ptr==NULL);
  CHECK(reader->endbyte==(long)length);
  CHECK(reader->endbit==1);
  CHECK(reader->storage==(long)length);
}

static void probe(unsigned char *bytes,size_t length,size_t start,
                  int width,int big){
  oggpack_buffer reader,original;
  long result;
  int available=width>=0 && width<=32 && (size_t)width<=length*8-start;
  ogg_uint32_t expected=0;
  CHECK(start<=length*8);
  if(available)expected=reference(bytes,start,(unsigned)width,big);
  initialize(&reader,bytes,length,start);
  original=reader;
  result=look(&reader,width,big);
  CHECK(memcmp(&reader,&original,sizeof(reader))==0);
  if(available)CHECK((ogg_uint32_t)result==expected);
  else CHECK(result==-1L);
  result=read_bits(&reader,width,big);
  CHECK(reader.buffer==bytes);
  CHECK(reader.storage==(long)length);
  if(available){
    size_t end=start+(unsigned)width;
    CHECK((ogg_uint32_t)result==expected);
    CHECK(reader.endbyte==(long)(end/8));
    CHECK(reader.endbit==(int)(end%8));
    CHECK(reader.ptr==(bytes?bytes+end/8:NULL));
  }else{
    CHECK(result==-1L);
    failed_state(&reader,length);
    original=reader;
    result=look(&reader,0,big);
    CHECK(result==-1L);
    CHECK(memcmp(&reader,&original,sizeof(reader))==0);
    result=read_bits(&reader,0,big);
    CHECK(result==-1L);
    failed_state(&reader,length);
  }
  ++probes;
}

static void set_pattern(const unsigned char *pattern){
  guarded.before=UINT32_C(0x9357ace1);
  guarded.after=UINT32_C(0x1eca7539);
  memcpy(guarded.bytes,pattern,sizeof(guarded.bytes));
}

static void unchanged(const unsigned char *pattern){
  CHECK(guarded.before==UINT32_C(0x9357ace1));
  CHECK(guarded.after==UINT32_C(0x1eca7539));
  CHECK(memcmp(guarded.bytes,pattern,sizeof(guarded.bytes))==0);
}

static void golden(const unsigned char *pattern,size_t length,size_t start,
                   int big,ogg_uint32_t expected){
  set_pattern(pattern);
  CHECK(reference(pattern,start,32,big)==expected);
  probe(guarded.bytes,length,start,32,big);
  unchanged(pattern);
}

int xiph_bitreader_tests(void){
  static const unsigned char high_lsb[8]={0,0,0,0x80,0,0,0,0};
  static const unsigned char high_msb[8]={0x80,0,0,0,0,0,0,0};
  static const unsigned char shifted_lsb[8]={0,0,0,0,0xf1,0,0,0};
  static const unsigned char shifted_msb[8]={0xf1,0,0,0,0,0,0,0};
  int pattern,big,width;
  size_t length,start;
  probes=0;
  for(pattern=0;pattern<6;pattern++){
    set_pattern(patterns[pattern]);
    for(big=0;big<2;big++)
      for(length=0;length<=8;length++)
        /* All byte positions and all bit offsets0..7 within this extent. */
        for(start=0;start<=length*8;start++){
          for(width=0;width<=32;width++){
            probe(guarded.bytes,length,start,width,big);
            unchanged(patterns[pattern]);
          }
          probe(guarded.bytes,length,start,-1,big);
          unchanged(patterns[pattern]);
          probe(guarded.bytes,length,start,33,big);
          unchanged(patterns[pattern]);
        }
  }
  CHECK(probes==124740);
  golden(high_lsb,4,0,0,UINT32_C(0x80000000));
  golden(high_msb,4,0,1,UINT32_C(0x80000000));
  golden(patterns[1],4,0,0,UINT32_C(0xffffffff));
  golden(patterns[1],4,0,1,UINT32_C(0xffffffff));
  /* The first value directly exercises the observed241<<25 failure. */
  golden(shifted_lsb,5,7,0,UINT32_C(0xe2000000));
  golden(shifted_msb,5,7,1,UINT32_C(0x80000000));
  for(big=0;big<2;big++){
    probe(NULL,0,0,0,big);
    probe(NULL,0,0,1,big);
    probe(NULL,0,0,-1,big);
    probe(NULL,0,0,33,big);
  }
  CHECK(probes==124754);
  return probes;
}
