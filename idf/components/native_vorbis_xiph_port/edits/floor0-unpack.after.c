#include "native_vorbis_xiph_header_error.h"

vorbis_info_floor *native_xiph_floor0_unpack(vorbis_info *vi,oggpack_buffer *opb,int *failure){
  codec_setup_info     *ci=vi->codec_setup;
  int j;

  vorbis_info_floor0 *info=_ogg_malloc(sizeof(*info));
  if(!info){
    *failure=OV_EFAULT;
    return(NULL);
  }
  info->order=oggpack_read(opb,8);
  info->rate=oggpack_read(opb,16);
  info->barkmap=oggpack_read(opb,16);
  info->ampbits=oggpack_read(opb,6);
  info->ampdB=oggpack_read(opb,8);
  info->numbooks=oggpack_read(opb,4)+1;

  if(info->order<1)goto err_out;
  if(info->rate<1)goto err_out;
  if(info->barkmap<1)goto err_out;
  if(info->numbooks<1)goto err_out;

  for(j=0;j<info->numbooks;j++){
    info->books[j]=oggpack_read(opb,8);
    if(info->books[j]<0 || info->books[j]>=ci->books)goto err_out;
    if(ci->book_param[info->books[j]]->maptype==0)goto err_out;
    if(ci->book_param[info->books[j]]->dim<1)goto err_out;
  }
  return(info);

 err_out:
  floor0_free_info(info);
  return(NULL);
}

static vorbis_info_floor *floor0_unpack (vorbis_info *vi,oggpack_buffer *opb){
  int failure=0;
  return(native_xiph_floor0_unpack(vi,opb,&failure));
}
