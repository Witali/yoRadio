#include "native_vorbis_xiph_packet_error.h"

static void *(*const native_xiph_floor_inverse1[])(vorbis_block *,
                                                  vorbis_look_floor *,int *)={
  native_xiph_floor0_inverse1,native_xiph_floor1_inverse1
};
_Static_assert(sizeof(native_xiph_floor_inverse1)/sizeof(*native_xiph_floor_inverse1)
               ==VI_FLOORB,"checked packet floor dispatch matches registry");

static int mapping0_inverse(vorbis_block *vb,vorbis_info_mapping *l){
  vorbis_dsp_state     *vd=vb->vd;
  vorbis_info          *vi=vd->vi;
  codec_setup_info     *ci=vi->codec_setup;
  private_state        *b=vd->backend_state;
  vorbis_info_mapping0 *info=(vorbis_info_mapping0 *)l;

  int                   i,j;
  long                  n=vb->pcmend=ci->blocksizes[vb->W];

  /* Keep the usual mono/stereo path allocation-free here. Wider channel
     bundles use checked block storage instead of growing the task stack. */
  float *small_pcm[2];
  int small_zero[2],small_nonzero[2];
  void *small_floor[2];
  float **pcmbundle=small_pcm;
  int *zerobundle=small_zero,*nonzero=small_nonzero;
  void **floormemo=small_floor;
  if(vi->channels>2){
    pcmbundle=_vorbis_block_alloc(vb,sizeof(*pcmbundle)*vi->channels);
    if(!pcmbundle)return OV_EFAULT;
    zerobundle=_vorbis_block_alloc(vb,sizeof(*zerobundle)*vi->channels);
    if(!zerobundle)return OV_EFAULT;
    nonzero=_vorbis_block_alloc(vb,sizeof(*nonzero)*vi->channels);
    if(!nonzero)return OV_EFAULT;
    floormemo=_vorbis_block_alloc(vb,sizeof(*floormemo)*vi->channels);
    if(!floormemo)return OV_EFAULT;
  }

  /* recover the spectral envelope; store it in the PCM vector for now */
  for(i=0;i<vi->channels;i++){
    int submap=info->chmuxlist[i];
    int failure=0;
    floormemo[i]=native_xiph_floor_inverse1[ci->floor_type[info->floorsubmap[submap]]](
      vb,b->flr[info->floorsubmap[submap]],&failure);
    if(failure)return failure;
    if(floormemo[i])
      nonzero[i]=1;
    else
      nonzero[i]=0;
    memset(vb->pcm[i],0,sizeof(*vb->pcm[i])*n/2);
  }

  /* channel coupling can 'dirty' the nonzero listing */
  for(i=0;i<info->coupling_steps;i++){
    if(nonzero[info->coupling_mag[i]] ||
       nonzero[info->coupling_ang[i]]){
      nonzero[info->coupling_mag[i]]=1;
      nonzero[info->coupling_ang[i]]=1;
    }
  }

  /* recover the residue into our working vectors */
  for(i=0;i<info->submaps;i++){
    int ch_in_bundle=0;
    for(j=0;j<vi->channels;j++){
      if(info->chmuxlist[j]==i){
        if(nonzero[j])
          zerobundle[ch_in_bundle]=1;
        else
          zerobundle[ch_in_bundle]=0;
        pcmbundle[ch_in_bundle++]=vb->pcm[j];
      }
    }

    int status=_residue_P[ci->residue_type[info->residuesubmap[i]]]->
      inverse(vb,b->residue[info->residuesubmap[i]],
              pcmbundle,zerobundle,ch_in_bundle);
    if(status<0)return status;
  }

  /* channel coupling */
  for(i=info->coupling_steps-1;i>=0;i--){
    float *pcmM=vb->pcm[info->coupling_mag[i]];
    float *pcmA=vb->pcm[info->coupling_ang[i]];

    for(j=0;j<n/2;j++){
      float mag=pcmM[j];
      float ang=pcmA[j];

      if(mag>0)
        if(ang>0){
          pcmM[j]=mag;
          pcmA[j]=mag-ang;
        }else{
          pcmA[j]=mag;
          pcmM[j]=mag+ang;
        }
      else
        if(ang>0){
          pcmM[j]=mag;
          pcmA[j]=mag+ang;
        }else{
          pcmA[j]=mag;
          pcmM[j]=mag-ang;
        }
    }
  }

  /* compute and apply spectral envelope */
  for(i=0;i<vi->channels;i++){
    float *pcm=vb->pcm[i];
    int submap=info->chmuxlist[i];
    int status=_floor_P[ci->floor_type[info->floorsubmap[submap]]]->
      inverse2(vb,b->flr[info->floorsubmap[submap]],
               floormemo[i],pcm);
    if(status<0)return status;
  }

  /* transform the PCM data; takes PCM vector, vb; modifies PCM vector */
  /* only MDCT right now.... */
  for(i=0;i<vi->channels;i++){
    float *pcm=vb->pcm[i];
    mdct_backward(b->transform[vb->W][0],pcm,pcm);
  }

  /* all done! */
  return(0);
}

