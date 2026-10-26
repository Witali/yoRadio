    int ***partword=alloca(ch*sizeof(*partword));

    for(j=0;j<ch;j++)
      partword[j]=_vorbis_block_alloc(vb,partwords*sizeof(*partword[j]));
