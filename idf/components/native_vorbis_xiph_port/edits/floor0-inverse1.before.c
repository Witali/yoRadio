static void *floor0_inverse1(vorbis_block *vb,vorbis_look_floor *i){
  vorbis_look_floor0 *look=(vorbis_look_floor0 *)i;
  vorbis_info_floor0 *info=look->vi;
  int j,k;

  int ampraw=oggpack_read(&vb->opb,info->ampbits);
  if(ampraw>0){ /* also handles the -1 out of data case */
    long maxval=(1<<info->ampbits)-1;
    float amp=(float)ampraw/maxval*info->ampdB;
    int booknum=oggpack_read(&vb->opb,ov_ilog(info->numbooks));

    if(booknum!=-1 && booknum<info->numbooks){ /* be paranoid */
      codec_setup_info  *ci=vb->vd->vi->codec_setup;
      codebook *b=ci->fullbooks+info->books[booknum];
      float last=0.f;

      /* the additional b->dim is a guard against any possible stack
         smash; b->dim is provably more than we can overflow the
         vector */
      float *lsp=_vorbis_block_alloc(vb,sizeof(*lsp)*(look->m+b->dim+1));

      if(vorbis_book_decodev_set(b,lsp,&vb->opb,look->m)==-1)goto eop;
      for(j=0;j<look->m;){
        for(k=0;j<look->m && k<b->dim;k++,j++)lsp[j]+=last;
        last=lsp[j-1];
      }

      lsp[look->m]=amp;
      return(lsp);
    }
  }
 eop:
  return(NULL);
}

