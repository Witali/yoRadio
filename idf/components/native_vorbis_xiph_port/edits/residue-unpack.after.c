#include "native_vorbis_xiph_header_error.h"

vorbis_info_residue *native_xiph_residue_unpack(vorbis_info *vi,oggpack_buffer *opb,int *failure){
  int j,acc=0;
  vorbis_info_residue0 *info=_ogg_calloc(1,sizeof(*info));
  codec_setup_info     *ci=vi->codec_setup;
  if(!info){
    *failure=OV_EFAULT;
    return(NULL);
  }

  info->begin=oggpack_read(opb,24);
  info->end=oggpack_read(opb,24);
  info->grouping=oggpack_read(opb,24)+1;
  info->partitions=oggpack_read(opb,6)+1;
  info->groupbook=oggpack_read(opb,8);

  /* check for premature EOP */
  if(info->groupbook<0)goto errout;

  for(j=0;j<info->partitions;j++){
    int cascade=oggpack_read(opb,3);
    int cflag=oggpack_read(opb,1);
    if(cflag<0) goto errout;
    if(cflag){
      int c=oggpack_read(opb,5);
      if(c<0) goto errout;
      cascade|=(c<<3);
    }
    info->secondstages[j]=cascade;

    acc+=icount(cascade);
  }
  for(j=0;j<acc;j++){
    int book=oggpack_read(opb,8);
    if(book<0) goto errout;
    info->booklist[j]=book;
  }

  if(info->groupbook>=ci->books)goto errout;
  for(j=0;j<acc;j++){
    if(info->booklist[j]>=ci->books)goto errout;
    if(ci->book_param[info->booklist[j]]->maptype==0)goto errout;
  }

  /* verify the phrasebook is not specifying an impossible or
     inconsistent partitioning scheme. */
  /* modify the phrasebook ranging check from r16327; an early beta
     encoder had a bug where it used an oversized phrasebook by
     accident.  These files should continue to be playable, but don't
     allow an exploit */
  {
    int entries = ci->book_param[info->groupbook]->entries;
    int dim = ci->book_param[info->groupbook]->dim;
    int partvals = 1;
    if (dim<1) goto errout;
    while(dim>0){
      partvals *= info->partitions;
      if(partvals > entries) goto errout;
      dim--;
    }
    info->partvals = partvals;
  }

  return(info);
 errout:
  res0_free_info(info);
  return(NULL);
}

vorbis_info_residue *res0_unpack(vorbis_info *vi,oggpack_buffer *opb){
  int failure=0;
  return(native_xiph_residue_unpack(vi,opb,&failure));
}
