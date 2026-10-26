    int **partword=_vorbis_block_alloc(vb,partwords*sizeof(*partword));

    for(i=0;i<ch;i++)if(nonzero[i])break;
    if(i==ch)return(0); /* no nonzero vectors */
