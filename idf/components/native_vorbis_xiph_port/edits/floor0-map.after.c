static int floor0_map_lazy_init(vorbis_block      *vb,
                                 vorbis_info_floor *infoX,
                                 vorbis_look_floor0 *look){
  if(!look->linearmap[vb->W]){
    vorbis_dsp_state   *vd=vb->vd;
    vorbis_info        *vi=vd->vi;
    codec_setup_info   *ci=vi->codec_setup;
    vorbis_info_floor0 *info=(vorbis_info_floor0 *)infoX;
    int W=vb->W;
    int n=ci->blocksizes[W]/2,j;

    /* we choose a scaling constant so that:
       floor(bark(rate/2-1)*C)=mapped-1
     floor(bark(rate/2)*C)=mapped */
    float scale=look->ln/toBARK(info->rate/2.f);

    /* the mapping from a linear scale to a smaller bark scale is
       straightforward.  We do *not* make sure that the linear mapping
       does not skip bark-scale bins; the decoder simply skips them and
       the encoder may do what it wishes in filling them.  They're
       necessary in some mapping combinations to keep the scale spacing
       accurate */
    look->linearmap[W]=_ogg_malloc((n+1)*sizeof(**look->linearmap));
    if(!look->linearmap[W])return OV_EFAULT;
    for(j=0;j<n;j++){
      int val=floor( toBARK((info->rate/2.f)/n*j)
                     *scale); /* bark numbers represent band edges */
      if(val>=look->ln)val=look->ln-1; /* guard against the approximation */
      look->linearmap[W][j]=val;
    }
    look->linearmap[W][j]=-1;
    look->n[W]=n;
  }
  return 0;
}

