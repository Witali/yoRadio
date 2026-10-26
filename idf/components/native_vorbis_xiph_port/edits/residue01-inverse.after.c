    int ***partword=alloca(ch*sizeof(*partword));

    if(!partwords || !look->stages)return 0; /* no residual work */
    for(j=0;j<ch;j++){
      partword[j]=_vorbis_block_alloc(vb,partwords*sizeof(*partword[j]));
      if(!partword[j])return OV_EFAULT;
    }
