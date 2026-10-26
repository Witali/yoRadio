#include "native_vorbis_xiph_header_error.h"

vorbis_info_floor *native_xiph_floor1_unpack(vorbis_info *vi,oggpack_buffer *opb,int *failure){
  codec_setup_info     *ci=vi->codec_setup;
  int j,k,count=0,maxclass=-1,rangebits;

  vorbis_info_floor1 *info=_ogg_calloc(1,sizeof(*info));
  if(!info){
    *failure=OV_EFAULT;
    return(NULL);
  }
  /* read partitions */
  info->partitions=oggpack_read(opb,5); /* only 0 to 31 legal */
  for(j=0;j<info->partitions;j++){
    info->partitionclass[j]=oggpack_read(opb,4); /* only 0 to 15 legal */
    if(info->partitionclass[j]<0)goto err_out;
    if(maxclass<info->partitionclass[j])maxclass=info->partitionclass[j];
  }

  /* read partition classes */
  for(j=0;j<maxclass+1;j++){
    info->class_dim[j]=oggpack_read(opb,3)+1; /* 1 to 8 */
    info->class_subs[j]=oggpack_read(opb,2); /* 0,1,2,3 bits */
    if(info->class_subs[j]<0)
      goto err_out;
    if(info->class_subs[j])info->class_book[j]=oggpack_read(opb,8);
    if(info->class_book[j]<0 || info->class_book[j]>=ci->books)
      goto err_out;
    for(k=0;k<(1<<info->class_subs[j]);k++){
      info->class_subbook[j][k]=oggpack_read(opb,8)-1;
      if(info->class_subbook[j][k]<-1 || info->class_subbook[j][k]>=ci->books)
        goto err_out;
    }
  }

  /* read the post list */
  info->mult=oggpack_read(opb,2)+1;     /* only 1,2,3,4 legal now */
  rangebits=oggpack_read(opb,4);
  if(rangebits<0)goto err_out;

  for(j=0,k=0;j<info->partitions;j++){
    count+=info->class_dim[info->partitionclass[j]];
    if(count>VIF_POSIT) goto err_out;
    for(;k<count;k++){
      int t=info->postlist[k+2]=oggpack_read(opb,rangebits);
      if(t<0 || t>=(1<<rangebits))
        goto err_out;
    }
  }
  info->postlist[0]=0;
  info->postlist[1]=1<<rangebits;

  /* don't allow repeated values in post list as they'd result in
     zero-length segments */
  {
    int *sortpointer[VIF_POSIT+2];
    for(j=0;j<count+2;j++)sortpointer[j]=info->postlist+j;
    qsort(sortpointer,count+2,sizeof(*sortpointer),icomp);

    for(j=1;j<count+2;j++)
      if(*sortpointer[j-1]==*sortpointer[j])goto err_out;
  }

  return(info);

 err_out:
  floor1_free_info(info);
  return(NULL);
}

static vorbis_info_floor *floor1_unpack (vorbis_info *vi,oggpack_buffer *opb){
  int failure=0;
  return(native_xiph_floor1_unpack(vi,opb,&failure));
}
