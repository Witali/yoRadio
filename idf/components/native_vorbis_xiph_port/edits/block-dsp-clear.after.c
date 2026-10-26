void vorbis_dsp_clear(vorbis_dsp_state *v){
  int i;
  if(v){
    vorbis_info *vi=v->vi;
    codec_setup_info *ci=(vi?vi->codec_setup:NULL);
    private_state *b=v->backend_state;

    if(b){

      if(b->ve){
        _ve_envelope_clear(b->ve);
        _ogg_free(b->ve);
      }

      if(b->transform[0]){
        mdct_clear(b->transform[0][0]);
        _ogg_free(b->transform[0][0]);
        _ogg_free(b->transform[0]);
      }
      if(b->transform[1]){
        mdct_clear(b->transform[1][0]);
        _ogg_free(b->transform[1][0]);
        _ogg_free(b->transform[1]);
      }

      if(b->flr){
        if(ci)
          for(i=0;i<ci->floors;i++)
            _floor_P[ci->floor_type[i]]->
              free_look(b->flr[i]);
        _ogg_free(b->flr);
      }
      if(b->residue){
        if(ci)
          for(i=0;i<ci->residues;i++)
            _residue_P[ci->residue_type[i]]->
              free_look(b->residue[i]);
        _ogg_free(b->residue);
      }
      if(b->psy){
        if(ci)
          for(i=0;i<ci->psys;i++)
            _vp_psy_clear(b->psy+i);
        _ogg_free(b->psy);
      }

      if(b->psy_g_look)_vp_global_free(b->psy_g_look);
      vorbis_bitrate_clear(&b->bms);

      drft_clear(&b->fft_look[0]);
      drft_clear(&b->fft_look[1]);

    }

    if(v->pcm){
      if(vi)
        for(i=0;i<vi->channels;i++)
          if(v->pcm[i])_ogg_free(v->pcm[i]);
      _ogg_free(v->pcm);
    }
    if(v->pcmret)_ogg_free(v->pcmret);

    if(b){
      /* free header, header1, header2 */
      if(b->header)_ogg_free(b->header);
      if(b->header1)_ogg_free(b->header1);
      if(b->header2)_ogg_free(b->header2);
      _ogg_free(b);
    }

    memset(v,0,sizeof(*v));
  }
}
