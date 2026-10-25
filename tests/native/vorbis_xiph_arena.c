// Focused optional-consolidation checks; no claim about other allocation sites.
#include <assert.h>
#include <limits.h>
#include <stdint.h>
#include <string.h>
#include "vorbis/codec.h"
#include "vorbis_xiph_alloc.h"
#ifdef NDEBUG
#error "Arena allocation tests require active assertions"
#endif

extern void *_vorbis_block_alloc(vorbis_block *block,long bytes);
extern void _vorbis_block_ripcord(vorbis_block *block);

static void fill(unsigned char *data,size_t bytes,unsigned seed){
  for(size_t i=0;i<bytes;i++)data[i]=(unsigned char)(seed+i);
}
static void retained(const unsigned char *data,size_t bytes,unsigned seed){
  for(size_t i=0;i<bytes;i++)assert(data[i]==(unsigned char)(seed+i));
}
static void empty_work(const vorbis_block *block){
  assert(block->localtop==0 && block->totaluse==0 && block->reap==NULL);
}
static void baseline(size_t live,size_t bytes){
  assert(xiph_port_test_live()==live && xiph_port_test_bytes()==bytes);
}
static void initialize(vorbis_block *block,vorbis_dsp_state *dsp){
  memset(dsp,0,sizeof(*dsp));assert(vorbis_block_init(dsp,block)==0);
}
// Produce one real reap link while retaining a separate24-byte current arena.
static unsigned char *one_reap(vorbis_block *block){
  unsigned char *old=_vorbis_block_alloc(block,16);assert(old);fill(old,16,1);
  unsigned char *current=_vorbis_block_alloc(block,24);assert(current);fill(current,24,41);
  assert(block->totaluse==16 && block->localalloc==24 && block->localtop==24 && block->reap);
  return current;
}

int xiph_arena_tests(void){
  unsigned checks=0;size_t initial_live=xiph_port_test_live(),initial_bytes=xiph_port_test_bytes();
  vorbis_dsp_state dsp;vorbis_block block;
  xiph_port_test_reset(0);initialize(&block,&dsp);

  // Empty ripcord and clear must perform no allocation, including realloc(NULL,0).
  _vorbis_block_ripcord(&block);empty_work(&block);assert(!block.localstore && !block.localalloc);
  assert(!xiph_port_test_attempts() && !xiph_port_test_realloc_attempts());baseline(initial_live,initial_bytes);checks++;
  assert(vorbis_block_clear(&block)==0 && !xiph_port_test_attempts());baseline(initial_live,initial_bytes);checks++;

  // Two real reap links are released even when optional consolidation fails.
  initialize(&block,&dsp);unsigned char *first=_vorbis_block_alloc(&block,16);assert(first);fill(first,16,3);
  unsigned char *second=_vorbis_block_alloc(&block,32);assert(second);fill(second,32,17);
  unsigned char *current=_vorbis_block_alloc(&block,64);assert(current);fill(current,64,73);
  assert(block.totaluse==48 && block.localalloc==64 && block.localtop==64 && block.reap);
  assert(xiph_port_test_live()==initial_live+5);
  xiph_port_test_reset(1);_vorbis_block_ripcord(&block);empty_work(&block);
  assert(block.localstore==current && block.localalloc==64);
  assert(xiph_port_test_attempts()==1 && xiph_port_test_realloc_attempts()==1 && xiph_port_test_failures()==1);
  baseline(initial_live+1,initial_bytes+64);retained(current,64,73);checks++;

  // Reuse after the failed grow needs no allocation and retains the old bytes.
  xiph_port_test_reset(0);unsigned char *reuse=_vorbis_block_alloc(&block,8);
  assert(reuse==current && block.localtop==8 && block.localalloc==64 && !xiph_port_test_attempts());retained(current,64,73);checks++;

  // Exercise a genuine successful grow after the earlier failed consolidation.
  current=_vorbis_block_alloc(&block,72);assert(current);fill(current,72,109);
  assert(block.totaluse==8 && block.localalloc==72 && block.reap);
  xiph_port_test_reset(0);_vorbis_block_ripcord(&block);empty_work(&block);
  assert(block.localstore && block.localalloc==80);
  assert(xiph_port_test_attempts()==1 && xiph_port_test_realloc_attempts()==1 && !xiph_port_test_failures());
  baseline(initial_live+1,initial_bytes+80);retained(block.localstore,72,109);checks++;

  // Already consolidated storage is retained without another allocation.
  current=_vorbis_block_alloc(&block,80);assert(current==block.localstore);fill(current,80,151);
  xiph_port_test_reset(0);_vorbis_block_ripcord(&block);empty_work(&block);
  assert(block.localstore==current && block.localalloc==80 && !xiph_port_test_attempts());retained(current,80,151);
  assert(vorbis_block_clear(&block)==0 && !xiph_port_test_attempts());baseline(initial_live,initial_bytes);checks++;

  // Block close frees the retained current arena after its optional grow fails.
  initialize(&block,&dsp);current=one_reap(&block);retained(current,24,41);
  xiph_port_test_reset(1);assert(vorbis_block_clear(&block)==0);
  assert(xiph_port_test_attempts()==1 && xiph_port_test_realloc_attempts()==1 && xiph_port_test_failures()==1);
  baseline(initial_live,initial_bytes);checks++;

  // Synthetic accounting boundaries check arithmetic without giant allocations.
  initialize(&block,&dsp);current=one_reap(&block);block.localalloc=LONG_MAX-7;
  xiph_port_test_reset(0);_vorbis_block_ripcord(&block);empty_work(&block);
  assert(block.localstore==current && block.localalloc==LONG_MAX-7 && !xiph_port_test_attempts());
  retained(current,24,41);baseline(initial_live+1,initial_bytes+24);block.localalloc=24;
  assert(vorbis_block_clear(&block)==0);baseline(initial_live,initial_bytes);checks++;

  // The exact LONG_MAX sum is representable; injection refuses that request.
  initialize(&block,&dsp);current=one_reap(&block);block.localalloc=LONG_MAX-16;
  xiph_port_test_reset(1);_vorbis_block_ripcord(&block);empty_work(&block);
  assert(block.localstore==current && block.localalloc==LONG_MAX-16);
  assert(xiph_port_test_attempts()==1 && xiph_port_test_realloc_attempts()==1 && xiph_port_test_failures()==1);
  retained(current,24,41);baseline(initial_live+1,initial_bytes+24);block.localalloc=24;
  xiph_port_test_reset(0);assert(vorbis_block_clear(&block)==0);baseline(initial_live,initial_bytes);checks++;

  // Defensive negative-accounting branches are not public decoder-input claims.
  for(unsigned which=0;which<2;which++){
    initialize(&block,&dsp);current=one_reap(&block);
    if(which==0)block.localalloc=-1;else block.totaluse=-1;
    xiph_port_test_reset(0);_vorbis_block_ripcord(&block);empty_work(&block);
    assert(block.localstore==current && block.localalloc==(which==0?-1:24) && !xiph_port_test_attempts());
    retained(current,24,41);baseline(initial_live+1,initial_bytes+24);block.localalloc=24;
    assert(vorbis_block_clear(&block)==0);baseline(initial_live,initial_bytes);checks++;
  }
  xiph_port_test_reset(0);baseline(initial_live,initial_bytes);assert(checks==11);return (int)checks;
}
