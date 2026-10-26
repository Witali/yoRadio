#include "native_vorbis_xiph_packet_error.h"

void *native_xiph_floor1_inverse1(vorbis_block *vb,vorbis_look_floor *in,
                                  int *failure){
  vorbis_look_floor1 *look=(vorbis_look_floor1 *)in;
  vorbis_info_floor1 *info=look->vi;
  codec_setup_info   *ci=vb->vd->vi->codec_setup;

  int i,j,k;
  codebook *books=ci->fullbooks;

  /* unpack wrapped/predicted values from stream */
  if(oggpack_read(&vb->opb,1)==1){
    int *fit_value=_vorbis_block_alloc(vb,(look->posts)*sizeof(*fit_value));
    if(!fit_value){*failure=OV_EFAULT;return NULL;}

    fit_value[0]=oggpack_read(&vb->opb,ov_ilog(look->quant_q-1));
    fit_value[1]=oggpack_read(&vb->opb,ov_ilog(look->quant_q-1));

    /* partition by partition */
    for(i=0,j=2;i<info->partitions;i++){
      int class=info->partitionclass[i];
      int cdim=info->class_dim[class];
      int csubbits=info->class_subs[class];
      int csub=1<<csubbits;
      int cval=0;

      /* decode the partition's first stage cascade value */
      if(csubbits){
        cval=vorbis_book_decode(books+info->class_book[class],&vb->opb);

        if(cval==-1)goto eop;
      }

      for(k=0;k<cdim;k++){
        int book=info->class_subbook[class][cval&(csub-1)];
        cval>>=csubbits;
        if(book>=0){
          if((fit_value[j+k]=vorbis_book_decode(books+book,&vb->opb))==-1)
            goto eop;
        }else{
          fit_value[j+k]=0;
        }
      }
      j+=cdim;
    }

    /* unwrap positive values and reconsitute via linear interpolation */
    for(i=2;i<look->posts;i++){
      int predicted=render_point(info->postlist[look->loneighbor[i-2]],
                                 info->postlist[look->hineighbor[i-2]],
                                 fit_value[look->loneighbor[i-2]],
                                 fit_value[look->hineighbor[i-2]],
                                 info->postlist[i]);
      int hiroom=look->quant_q-predicted;
      int loroom=predicted;
      int room=(hiroom<loroom?hiroom:loroom)<<1;
      int val=fit_value[i];

      if(val){
        if(val>=room){
          if(hiroom>loroom){
            val = val-loroom;
          }else{
            val = -1-(val-hiroom);
          }
        }else{
          if(val&1){
            val= -((val+1)>>1);
          }else{
            val>>=1;
          }
        }

        fit_value[i]=(val+predicted)&0x7fff;
        fit_value[look->loneighbor[i-2]]&=0x7fff;
        fit_value[look->hineighbor[i-2]]&=0x7fff;

      }else{
        fit_value[i]=predicted|0x8000;
      }

    }

    return(fit_value);
  }
 eop:
  return(NULL);
}

static void *floor1_inverse1(vorbis_block *vb,vorbis_look_floor *in){
  int failure=0;
  return native_xiph_floor1_inverse1(vb,in,&failure);
}

