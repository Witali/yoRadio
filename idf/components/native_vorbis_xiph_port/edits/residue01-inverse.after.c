    int **small_partword[2];
    int ***partword=small_partword;

    if(!partwords || !look->stages)return 0; /* no residual work */
    if(ch>2){
      partword=_vorbis_block_alloc(vb,ch*sizeof(*partword));
      if(!partword)return OV_EFAULT;
    }
    for(j=0;j<ch;j++){
      partword[j]=_vorbis_block_alloc(vb,partwords*sizeof(*partword[j]));
      if(!partword[j])return OV_EFAULT;
    }
