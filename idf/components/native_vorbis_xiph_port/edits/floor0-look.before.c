static vorbis_look_floor *floor0_look(vorbis_dsp_state *vd,
                                      vorbis_info_floor *i){
  vorbis_info_floor0 *info=(vorbis_info_floor0 *)i;
  vorbis_look_floor0 *look=_ogg_calloc(1,sizeof(*look));

  (void)vd;

  look->m=info->order;
  look->ln=info->barkmap;
  look->vi=info;

  look->linearmap=_ogg_calloc(2,sizeof(*look->linearmap));

  return look;
}
