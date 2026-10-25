#include <limits.h>

void _vorbis_block_ripcord(vorbis_block *vb){
  /* reap the chain */
  struct alloc_chain *reap=vb->reap;
  while(reap){
    struct alloc_chain *next=reap->next;
    _ogg_free(reap->ptr);
    memset(reap,0,sizeof(*reap));
    _ogg_free(reap);
    reap=next;
  }
  /* Consolidation is optional. Keep the current arena usable on failure. */
  if(vb->totaluse>0 && vb->localalloc>=0 &&
     vb->totaluse<=LONG_MAX-vb->localalloc){
    long wanted=vb->localalloc+vb->totaluse;
    size_t bytes=(size_t)wanted;
    if((long)bytes==wanted){
      void *grown=_ogg_realloc(vb->localstore,bytes);
      if(grown){
        vb->localstore=grown;
        vb->localalloc=wanted;
      }
    }
  }

  vb->totaluse=0;
  vb->localtop=0;
  vb->reap=NULL;
}
