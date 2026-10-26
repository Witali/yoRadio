    int **partword;

    for(i=0;i<ch;i++)if(nonzero[i])break;
    if(i==ch || !partwords || !look->stages)return(0); /* no residual work */
    partword=_vorbis_block_alloc(vb,partwords*sizeof(*partword));
    if(!partword)return OV_EFAULT;
