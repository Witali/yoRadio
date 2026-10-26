#include "native_vorbis_xiph_header_error.h"

static int _vorbis_unpack_books(vorbis_info *vi,oggpack_buffer *opb){
  codec_setup_info     *ci=vi->codec_setup;
  int i,failure=0;
  static vorbis_info_floor *(*const floor_unpack[])(vorbis_info *,oggpack_buffer *,int *)={
    native_xiph_floor0_unpack,native_xiph_floor1_unpack
  };
  static vorbis_info_residue *(*const residue_unpack[])(vorbis_info *,oggpack_buffer *,int *)={
    native_xiph_residue_unpack,native_xiph_residue_unpack,native_xiph_residue_unpack
  };
  static vorbis_info_mapping *(*const mapping_unpack[])(vorbis_info *,oggpack_buffer *,int *)={
    native_xiph_mapping_unpack
  };
  _Static_assert(sizeof(floor_unpack)/sizeof(*floor_unpack)==VI_FLOORB,"pinned floor registry");
  _Static_assert(sizeof(residue_unpack)/sizeof(*residue_unpack)==VI_RESB,"pinned residue registry");
  _Static_assert(sizeof(mapping_unpack)/sizeof(*mapping_unpack)==VI_MAPB,"pinned mapping registry");

  /* codebooks */
  ci->books=oggpack_read(opb,8)+1;
  if(ci->books<=0)goto err_out;
  for(i=0;i<ci->books;i++){
    ci->book_param[i]=native_xiph_staticbook_unpack(opb,&failure);
    if(!ci->book_param[i])goto err_out;
  }

  /* time backend settings; hooks are unused */
  {
    int times=oggpack_read(opb,6)+1;
    if(times<=0)goto err_out;
    for(i=0;i<times;i++){
      int test=oggpack_read(opb,16);
      if(test<0 || test>=VI_TIMEB)goto err_out;
    }
  }

  /* floor backend settings */
  ci->floors=oggpack_read(opb,6)+1;
  if(ci->floors<=0)goto err_out;
  for(i=0;i<ci->floors;i++){
    ci->floor_type[i]=oggpack_read(opb,16);
    if(ci->floor_type[i]<0 || ci->floor_type[i]>=VI_FLOORB)goto err_out;
    ci->floor_param[i]=floor_unpack[ci->floor_type[i]](vi,opb,&failure);
    if(!ci->floor_param[i])goto err_out;
  }

  /* residue backend settings */
  ci->residues=oggpack_read(opb,6)+1;
  if(ci->residues<=0)goto err_out;
  for(i=0;i<ci->residues;i++){
    ci->residue_type[i]=oggpack_read(opb,16);
    if(ci->residue_type[i]<0 || ci->residue_type[i]>=VI_RESB)goto err_out;
    ci->residue_param[i]=residue_unpack[ci->residue_type[i]](vi,opb,&failure);
    if(!ci->residue_param[i])goto err_out;
  }

  /* map backend settings */
  ci->maps=oggpack_read(opb,6)+1;
  if(ci->maps<=0)goto err_out;
  for(i=0;i<ci->maps;i++){
    ci->map_type[i]=oggpack_read(opb,16);
    if(ci->map_type[i]<0 || ci->map_type[i]>=VI_MAPB)goto err_out;
    ci->map_param[i]=mapping_unpack[ci->map_type[i]](vi,opb,&failure);
    if(!ci->map_param[i])goto err_out;
  }

  /* mode settings */
  ci->modes=oggpack_read(opb,6)+1;
  if(ci->modes<=0)goto err_out;
  for(i=0;i<ci->modes;i++){
    ci->mode_param[i]=_ogg_calloc(1,sizeof(*ci->mode_param[i]));
    if(!ci->mode_param[i]){failure=OV_EFAULT;goto err_out;}
    ci->mode_param[i]->blockflag=oggpack_read(opb,1);
    ci->mode_param[i]->windowtype=oggpack_read(opb,16);
    ci->mode_param[i]->transformtype=oggpack_read(opb,16);
    ci->mode_param[i]->mapping=oggpack_read(opb,8);

    if(ci->mode_param[i]->windowtype>=VI_WINDOWB)goto err_out;
    if(ci->mode_param[i]->transformtype>=VI_WINDOWB)goto err_out;
    if(ci->mode_param[i]->mapping>=ci->maps)goto err_out;
    if(ci->mode_param[i]->mapping<0)goto err_out;
  }

  if(oggpack_read(opb,1)!=1)goto err_out; /* top level EOP check */

  return(0);
 err_out:
  vorbis_info_clear(vi);
  return(failure?failure:OV_EBADHEADER);
}
