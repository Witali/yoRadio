#include "native_vorbis_xiph_dsp_error.h"

static int _vds_shared_init(vorbis_dsp_state *v,vorbis_info *vi,int encp){
  int i;
  codec_setup_info *ci=vi?vi->codec_setup:NULL;
  private_state *b=NULL;
  int hs;

  if(!v)return 1;
  memset(v,0,sizeof(*v));
  if(ci==NULL||
     ci->modes<=0||
     ci->blocksizes[0]<64||
     ci->blocksizes[1]<ci->blocksizes[0]){
    return 1;
  }
  hs=ci->halfrate_flag;

  v->vi=vi;
  b=v->backend_state=_ogg_calloc(1,sizeof(*b));
  if(!b)goto abort_init;
  b->modebits=ov_ilog(ci->modes-1);

  b->transform[0]=_ogg_calloc(VI_TRANSFORMB,sizeof(*b->transform[0]));
  if(!b->transform[0])goto abort_init;
  b->transform[1]=_ogg_calloc(VI_TRANSFORMB,sizeof(*b->transform[1]));
  if(!b->transform[1])goto abort_init;

  /* MDCT is tranform 0 */

  b->transform[0][0]=_ogg_calloc(1,sizeof(mdct_lookup));
  if(!b->transform[0][0])goto abort_init;
  b->transform[1][0]=_ogg_calloc(1,sizeof(mdct_lookup));
  if(!b->transform[1][0])goto abort_init;
  if(native_xiph_mdct_init(b->transform[0][0],ci->blocksizes[0]>>hs))goto abort_init;
  if(native_xiph_mdct_init(b->transform[1][0],ci->blocksizes[1]>>hs))goto abort_init;

  /* Vorbis I uses only window type 0 */
  /* note that the correct computation below is technically:
       b->window[0]=ov_ilog(ci->blocksizes[0]-1)-6;
       b->window[1]=ov_ilog(ci->blocksizes[1]-1)-6;
    but since blocksizes are always powers of two,
    the below is equivalent.
   */
  b->window[0]=ov_ilog(ci->blocksizes[0])-7;
  b->window[1]=ov_ilog(ci->blocksizes[1])-7;

  if(encp){ /* encode/decode differ here */

    /* analysis always needs an fft */
    drft_init(&b->fft_look[0],ci->blocksizes[0]);
    drft_init(&b->fft_look[1],ci->blocksizes[1]);

    /* finish the codebooks */
    if(!ci->fullbooks){
      ci->fullbooks=_ogg_calloc(ci->books,sizeof(*ci->fullbooks));
      if(!ci->fullbooks)goto abort_init;
      for(i=0;i<ci->books;i++)
        vorbis_book_init_encode(ci->fullbooks+i,ci->book_param[i]);
    }

    b->psy=_ogg_calloc(ci->psys,sizeof(*b->psy));
    for(i=0;i<ci->psys;i++){
      _vp_psy_init(b->psy+i,
                   ci->psy_param[i],
                   &ci->psy_g_param,
                   ci->blocksizes[ci->psy_param[i]->blockflag]/2,
                   vi->rate);
    }

    v->analysisp=1;
  }else{
    /* finish the codebooks */
    if(!ci->fullbooks){
      ci->fullbooks=_ogg_calloc(ci->books,sizeof(*ci->fullbooks));
      if(!ci->fullbooks)goto abort_init;
      for(i=0;i<ci->books;i++){
        if(ci->book_param[i]==NULL)
          goto abort_books;
        if(vorbis_book_init_decode(ci->fullbooks+i,ci->book_param[i]))
          goto abort_books;
        /* decode codebooks are now standalone after init */
        vorbis_staticbook_destroy(ci->book_param[i]);
        ci->book_param[i]=NULL;
      }
    }
  }

  /* initialize the storage vectors. blocksize[1] is small for encode,
     but the correct size for decode */
  v->pcm_storage=ci->blocksizes[1];
  v->pcm=_ogg_calloc(vi->channels,sizeof(*v->pcm));
  if(!v->pcm)goto abort_init;
  v->pcmret=_ogg_malloc(vi->channels*sizeof(*v->pcmret));
  if(!v->pcmret)goto abort_init;
  {
    int i;
    for(i=0;i<vi->channels;i++){
      v->pcm[i]=_ogg_calloc(v->pcm_storage,sizeof(*v->pcm[i]));
      if(!v->pcm[i])goto abort_init;
    }
  }

  /* all 1 (large block) or 0 (small block) */
  /* explicitly set for the sake of clarity */
  v->lW=0; /* previous window size */
  v->W=0;  /* current window size */

  /* all vector indexes */
  v->centerW=ci->blocksizes[1]/2;

  v->pcm_current=v->centerW;

  /* initialize all the backend lookups */
  b->flr=_ogg_calloc(ci->floors,sizeof(*b->flr));
  if(!b->flr)goto abort_init;
  b->residue=_ogg_calloc(ci->residues,sizeof(*b->residue));
  if(!b->residue)goto abort_init;

  for(i=0;i<ci->floors;i++){
    b->flr[i]=_floor_P[ci->floor_type[i]]->
      look(v,ci->floor_param[i]);
    if(!b->flr[i])goto abort_init;
  }

  for(i=0;i<ci->residues;i++){
    b->residue[i]=_residue_P[ci->residue_type[i]]->
      look(v,ci->residue_param[i]);
    if(!b->residue[i])goto abort_init;
  }

  return 0;
 abort_books:
  for(i=0;i<ci->books;i++){
    if(ci->book_param[i]!=NULL){
      vorbis_staticbook_destroy(ci->book_param[i]);
      ci->book_param[i]=NULL;
    }
  }
 abort_init:
  vorbis_dsp_clear(v);
  return -1;
}
