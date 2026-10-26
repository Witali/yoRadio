static int _vorbis_unpack_comment(vorbis_comment *vc,oggpack_buffer *opb){
  int i;
  int failure=OV_EBADHEADER;
  int vendorlen=oggpack_read(opb,32);
  if(vendorlen<0)goto err_out;
  if(vendorlen>opb->storage-8)goto err_out;
  vc->vendor=_ogg_calloc(vendorlen+1,1);
  if(!vc->vendor)goto oom_out;
  _v_readstring(opb,vc->vendor,vendorlen);
  i=oggpack_read(opb,32);
  if(i<0)goto err_out;
  if(i>((opb->storage-oggpack_bytes(opb))>>2))goto err_out;
  vc->comments=i;
  vc->user_comments=_ogg_calloc(vc->comments+1,sizeof(*vc->user_comments));
  if(!vc->user_comments)goto oom_out;
  vc->comment_lengths=_ogg_calloc(vc->comments+1, sizeof(*vc->comment_lengths));
  if(!vc->comment_lengths)goto oom_out;

  for(i=0;i<vc->comments;i++){
    int len=oggpack_read(opb,32);
    if(len<0)goto err_out;
    if(len>opb->storage-oggpack_bytes(opb))goto err_out;
    vc->comment_lengths[i]=len;
    vc->user_comments[i]=_ogg_calloc(len+1,1);
    if(!vc->user_comments[i])goto oom_out;
    _v_readstring(opb,vc->user_comments[i],len);
  }
  if(oggpack_read(opb,1)!=1)goto err_out; /* EOP check */

  return(0);
 oom_out:
  failure=OV_EFAULT;
 err_out:
  vorbis_comment_clear(vc);
  return(failure);
}
