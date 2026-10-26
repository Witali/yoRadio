#include "native_vorbis_xiph_header_error.h"

static_codebook *native_xiph_staticbook_unpack(oggpack_buffer *opb,int *failure){
  long i,j;
  static_codebook *s=_ogg_calloc(1,sizeof(*s));
  if(!s){
    *failure=OV_EFAULT;
    return(NULL);
  }
  s->allocedp=1;

  /* make sure alignment is correct */
  if(oggpack_read(opb,24)!=0x564342)goto _eofout;

  /* first the basic parameters */
  s->dim=oggpack_read(opb,16);
  s->entries=oggpack_read(opb,24);
  if(s->entries==-1)goto _eofout;

  if(ov_ilog(s->dim)+ov_ilog(s->entries)>24)goto _eofout;

  /* codeword ordering.... length ordered or unordered? */
  switch((int)oggpack_read(opb,1)){
  case 0:{
    long unused;
    /* allocated but unused entries? */
    unused=oggpack_read(opb,1);
    if((s->entries*(unused?1:5)+7)>>3>opb->storage-oggpack_bytes(opb))
      goto _eofout;
    /* unordered */
    s->lengthlist=_ogg_malloc(sizeof(*s->lengthlist)*s->entries);
    if(s->entries && !s->lengthlist){
      *failure=OV_EFAULT;
      goto _eofout;
    }

    /* allocated but unused entries? */
    if(unused){
      /* yes, unused entries */

      for(i=0;i<s->entries;i++){
        if(oggpack_read(opb,1)){
          long num=oggpack_read(opb,5);
          if(num==-1)goto _eofout;
          s->lengthlist[i]=num+1;
        }else
          s->lengthlist[i]=0;
      }
    }else{
      /* all entries used; no tagging */
      for(i=0;i<s->entries;i++){
        long num=oggpack_read(opb,5);
        if(num==-1)goto _eofout;
        s->lengthlist[i]=num+1;
      }
    }

    break;
  }
  case 1:
    /* ordered */
    {
      long length=oggpack_read(opb,5)+1;
      if(length==0)goto _eofout;
      s->lengthlist=_ogg_malloc(sizeof(*s->lengthlist)*s->entries);
      if(s->entries && !s->lengthlist){
        *failure=OV_EFAULT;
        goto _eofout;
      }

      for(i=0;i<s->entries;){
        long num=oggpack_read(opb,ov_ilog(s->entries-i));
        if(num==-1)goto _eofout;
        if(length>32 || num>s->entries-i ||
           (num>0 && (num-1)>>(length-1)>1)){
          goto _errout;
        }
        if(length>32)goto _errout;
        for(j=0;j<num;j++,i++)
          s->lengthlist[i]=length;
        length++;
      }
    }
    break;
  default:
    /* EOF */
    goto _eofout;
  }

  /* Do we have a mapping to unpack? */
  switch((s->maptype=oggpack_read(opb,4))){
  case 0:
    /* no mapping */
    break;
  case 1: case 2:
    /* implicitly populated value mapping */
    /* explicitly populated value mapping */

    s->q_min=oggpack_read(opb,32);
    s->q_delta=oggpack_read(opb,32);
    s->q_quant=oggpack_read(opb,4)+1;
    s->q_sequencep=oggpack_read(opb,1);
    if(s->q_sequencep==-1)goto _eofout;

    {
      int quantvals=0;
      switch(s->maptype){
      case 1:
        quantvals=(s->dim==0?0:_book_maptype1_quantvals(s));
        break;
      case 2:
        quantvals=s->entries*s->dim;
        break;
      }

      /* quantized values */
      if(((quantvals*s->q_quant+7)>>3)>opb->storage-oggpack_bytes(opb))
        goto _eofout;
      s->quantlist=_ogg_malloc(sizeof(*s->quantlist)*quantvals);
      if(quantvals && !s->quantlist){
        *failure=OV_EFAULT;
        goto _eofout;
      }
      for(i=0;i<quantvals;i++)
        s->quantlist[i]=oggpack_read(opb,s->q_quant);

      if(quantvals&&s->quantlist[quantvals-1]==-1)goto _eofout;
    }
    break;
  default:
    goto _errout;
  }

  /* all set */
  return(s);

 _errout:
 _eofout:
  vorbis_staticbook_destroy(s);
  return(NULL);
}

static_codebook *vorbis_staticbook_unpack(oggpack_buffer *opb){
  int failure=0;
  return(native_xiph_staticbook_unpack(opb,&failure));
}
