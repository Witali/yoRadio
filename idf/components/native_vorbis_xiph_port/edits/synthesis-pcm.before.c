  vb->pcm=_vorbis_block_alloc(vb,sizeof(*vb->pcm)*vi->channels);
  for(i=0;i<vi->channels;i++)
    vb->pcm[i]=_vorbis_block_alloc(vb,vb->pcmend*sizeof(*vb->pcm[i]));
