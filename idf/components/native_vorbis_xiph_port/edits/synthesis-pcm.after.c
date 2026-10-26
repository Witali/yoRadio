  vb->pcm=_vorbis_block_alloc(vb,sizeof(*vb->pcm)*vi->channels);
  if(!vb->pcm)return OV_EFAULT;
  for(i=0;i<vi->channels;i++){
    vb->pcm[i]=_vorbis_block_alloc(vb,vb->pcmend*sizeof(*vb->pcm[i]));
    if(!vb->pcm[i])return OV_EFAULT;
  }
