#include <limits.h>

void *_vorbis_block_alloc(vorbis_block *vb,long bytes){
  struct alloc_chain *link=NULL;
  void *store;
  long aligned;

  if(!vb || bytes<0 || bytes>LONG_MAX-(WORD_ALIGN-1) ||
     vb->localtop<0 || vb->localalloc<0 || vb->totaluse<0 ||
     vb->localtop>vb->localalloc ||
     (!vb->localstore && (vb->localtop || vb->localalloc)))return NULL;
  aligned=(bytes+(WORD_ALIGN-1)) & ~(WORD_ALIGN-1);
  if((long)(size_t)aligned!=aligned)return NULL;

  /* Zero bytes need no owner, and NULL must never enter pointer arithmetic. */
  if(!aligned)return vb->localstore ? (char *)vb->localstore+vb->localtop : NULL;
  if(aligned<=vb->localalloc-vb->localtop){
    store=(char *)vb->localstore+vb->localtop;
    vb->localtop+=aligned;
    return store;
  }

  /* Existing borrowed pointers stay live until the next ripcord. Prepare
     both new owners before changing any arena accounting or links. */
  if(vb->localstore){
    if(vb->totaluse>LONG_MAX-vb->localtop)return NULL;
    link=_ogg_malloc(sizeof(*link));
    if(!link)return NULL;
  }
  store=_ogg_malloc((size_t)aligned);
  if(!store){
    _ogg_free(link);
    return NULL;
  }
  if(link){
    link->next=vb->reap;
    link->ptr=vb->localstore;
    vb->reap=link;
    vb->totaluse+=vb->localtop;
  }
  vb->localstore=store;
  vb->localalloc=aligned;
  vb->localtop=aligned;
  return store;
}

