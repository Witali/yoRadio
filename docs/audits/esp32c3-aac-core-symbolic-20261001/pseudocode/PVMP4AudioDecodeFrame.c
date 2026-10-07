/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: PVMP4AudioDecodeFrame @ ram:4300e7e6
 * Types and parameter counts are inferred; verify against disassembly. */

int PVMP4AudioDecodeFrame(aac_analysis_external_t *external,aac_analysis_core_t *core)

{
  uint8_t uVar1;
  int16_t iVar2;
  bool bVar3;
  int32_t iVar4;
  undefined4 uVar5;
  aac_sbr_control_abi_t *paVar6;
  uint uVar7;
  int iVar8;
  aac_analysis_channel_shared_t *paVar9;
  int32_t iVar10;
  int iVar11;
  uint8_t *puVar12;
  ushort *puVar13;
  aac_analysis_core_channel_t *paVar14;
  aac_analysis_program_t *paVar15;
  uint uVar16;
  uint uVar17;
  byte *pbVar18;
  uint32_t uVar19;
  uint uVar20;
  int16_t *piVar21;
  int16_t *piVar22;
  int16_t *piVar23;
  int16_t *piVar24;
  uint uVar25;
  int iVar26;
  int iVar27;
  aac_analysis_core_channel_t **ppaVar28;
  int iVar29;
  aac_analysis_sbr_stream_t *stream;
  uint8_t uVar30;
  aac_analysis_core_channel_t **ppaVar31;
  aac_analysis_channel_shared_t *paVar32;
  aac_analysis_channel_shared_t *paVar33;
  aac_analysis_window_t *paVar34;
  aac_analysis_bits_t *bits;
  aac_sbr_owner_abi_t *paVar35;
  int32_t *piVar36;
  int32_t iVar37;
  aac_sbr_control_abi_t *paStack_78;
  undefined4 uStack_4c;
  aac_analysis_core_channel_t *local_48;
  aac_analysis_core_channel_t *local_44 [4];

  gp = &__global_pointer_;
  paVar33 = core->channel[0].spectrum.shared;
  local_44[0] = core->channel + 1;
  local_48 = core->channel;
  paVar32 = core->channel[1].spectrum.shared;
  uVar19 = external->input_length;
  puVar12 = external->input;
  uVar25 = external->consumed_bytes * 8 + external->remainder_bits;
  if (external->plus_enabled == 0) {
    (core->input).used_bits = uVar25;
    (core->input).buffer = puVar12;
    (core->input).input_length = uVar19;
    (core->input).available_bits = uVar19 << 3;
    if (uVar19 << 3 < uVar25) {
      byte_align(&core->input);
      uVar19 = core->frame_number;
      iVar27 = 10;
      if (uVar19 == 0) {
        (core->mc).ps_present = 0;
        (core->mc).sbr_present = 0;
        (core->mc).upsampling = 1;
        iVar27 = 10;
      }
      goto LAB_ram_4300e86a;
    }
    paVar15 = core->program;
    iVar8 = paVar15->file_is_adts;
    if (iVar8 == 0) {
      stream = (aac_analysis_sbr_stream_t *)0x0;
      goto LAB_ram_4300e934;
    }
    stream = (aac_analysis_sbr_stream_t *)0x0;
LAB_ram_4300e8d4:
    if (core->frame_number == 0) {
      iVar27 = get_adif_header(core,&core->scratch->adif);
      byte_align(&core->input);
      paVar15 = core->program;
      if (iVar27 != 0) {
        paVar15->file_is_adts = 2;
        goto LAB_ram_4300e8f2;
      }
      paVar15->file_is_adts = 1;
LAB_ram_4300f050:
      byte_align(&core->input);
      if (external->plus_enabled != 0) {
        stream->elements = 0;
        stream->core_elements = 0;
      }
    }
    else {
      if ((core->frame_number == 1) && (iVar8 == 1)) {
        uVar17 = uVar19 - (uVar25 >> 3);
        pbVar18 = puVar12 + (uVar25 >> 3);
        if (uVar17 < 4) {
          if (uVar17 == 2) {
            uVar17 = 0;
LAB_ram_4300f4c8:
            uVar17 = (uint)pbVar18[1] << 0x10 | uVar17;
LAB_ram_4300f474:
            uVar17 = (uint)*pbVar18 << 0x18 | uVar17;
            goto LAB_ram_4300f3ac;
          }
          if (uVar17 == 3) {
            uVar17 = (uint)pbVar18[2] << 8;
            goto LAB_ram_4300f4c8;
          }
          if (uVar17 == 1) {
            uVar17 = 0;
            goto LAB_ram_4300f474;
          }
        }
        else {
          uVar17 = (uint)*pbVar18 << 0x18 | (uint)pbVar18[1] << 0x10 | (uint)pbVar18[3] |
                   (uint)pbVar18[2] << 8;
LAB_ram_4300f3ac:
          (core->input).used_bits = uVar25 + 3;
          if ((uVar17 << (uVar25 & 7)) >> 0x1d == 7) {
            byte_align(&core->input);
            uVar25 = (core->input).used_bits;
            uVar19 = core->frame_number;
            external->remainder_bits = uVar25 & 7;
            external->consumed_bytes = uVar25 >> 3;
            core->frame_number = uVar19 + 1;
            return 0;
          }
        }
        (core->input).used_bits = uVar25;
        goto LAB_ram_4300f050;
      }
      iVar27 = 0;
      if (iVar8 != 2) goto LAB_ram_4300f050;
LAB_ram_4300e8f2:
      if (paVar15->headerless_frames == 0) {
        iVar8 = get_adts_header(core,&core->syncword,&core->invoke,3);
        if (iVar8 == 0) {
          uVar17 = (core->input).used_bits;
          puVar12 = (core->input).buffer;
          uVar19 = (core->input).input_length;
          uVar7 = (core->input).available_bits;
          if (external->plus_enabled != 0) {
            stream->elements = 0;
            stream->core_elements = 0;
          }
          goto LAB_ram_4300e93a;
        }
        if (external->plus_enabled != 0) {
          stream->elements = 0;
          stream->core_elements = 0;
        }
        iVar27 = 0x1e;
LAB_ram_4300e858:
        byte_align(&core->input);
        uVar19 = core->frame_number;
        if (uVar19 == 0) {
          (core->mc).ps_present = 0;
          (core->mc).sbr_present = 0;
          (core->mc).upsampling = 1;
        }
        goto LAB_ram_4300e86a;
      }
      iVar8 = external->plus_enabled;
      paVar15->headerless_frames = paVar15->headerless_frames + -1;
      if (iVar8 != 0) {
        stream->elements = 0;
        stream->core_elements = 0;
      }
      if (iVar27 != 0) goto LAB_ram_4300e858;
    }
    uVar17 = (core->input).used_bits;
    puVar12 = (core->input).buffer;
    uVar19 = (core->input).input_length;
    uVar7 = (core->input).available_bits;
  }
  else {
    stream = core->sbr_stream;
    (core->input).used_bits = uVar25;
    (core->input).buffer = puVar12;
    (core->input).input_length = uVar19;
    (core->input).available_bits = uVar19 << 3;
    if (uVar19 << 3 < uVar25) {
      stream->elements = 0;
      stream->core_elements = 0;
      iVar27 = 10;
      goto LAB_ram_4300e858;
    }
    paVar15 = core->program;
    iVar8 = paVar15->file_is_adts;
    if (iVar8 != 0) goto LAB_ram_4300e8d4;
    stream->elements = 0;
    stream->core_elements = 0;
LAB_ram_4300e934:
    uVar7 = uVar19 << 3;
    uVar17 = uVar25;
  }
LAB_ram_4300e93a:
  bits = &core->input;
  bVar3 = true;
  uVar20 = uVar19 - (uVar17 >> 3);
  puVar13 = (ushort *)(puVar12 + (uVar17 >> 3));
  uVar16 = uVar17 + 3;
  if (uVar20 < 2) goto LAB_ram_4300e9d2;
LAB_ram_4300e954:
  uVar20 = (uint)(*puVar13 >> 8) + (uint)*puVar13 * 0x100 & 0xffff;
  while ((core->input).used_bits = uVar16, uVar16 <= uVar7) {
    uVar20 = uVar20 << (uVar17 & 7);
    uVar17 = uVar20 >> 0xd & 7;
    if (uVar17 == 5) {
      if (core->frame_number < 2) {
        iVar27 = get_prog_config(core,&core->scratch->program);
        if (iVar27 == 0) goto LAB_ram_4300e9ba;
      }
      else {
        iVar27 = 10;
      }
      goto LAB_ram_4300e9de;
    }
    if (uVar17 < 6) {
      if ((uVar20 >> 0xe & 3) == 0) goto LAB_ram_4300ea66;
      if (uVar17 == 4) {
        get_dse(core->shared->data_stream,bits);
        goto LAB_ram_4300e9ba;
      }
      iVar27 = -1;
      goto LAB_ram_4300e9de;
    }
    if (uVar17 != 6) {
      iVar27 = 0;
      goto LAB_ram_4300e9de;
    }
    if ((core->plus_enabled == 0) ||
       (24000 < samp_rate_info.entry[(core->mc).sample_rate_index].rate)) {
      getfill(bits);
    }
    else {
      get_sbr_bitstream(stream,bits);
    }
LAB_ram_4300e9ba:
    while( true ) {
      uVar17 = (core->input).used_bits;
      uVar20 = (core->input).input_length - (uVar17 >> 3);
      puVar13 = (ushort *)((core->input).buffer + (uVar17 >> 3));
      uVar7 = (core->input).available_bits;
      uVar16 = uVar17 + 3;
      if (1 < uVar20) goto LAB_ram_4300e954;
LAB_ram_4300e9d2:
      if (uVar20 == 1) break;
      (core->input).used_bits = uVar16;
      if (uVar7 < uVar16) goto LAB_ram_4300e9dc;
      uVar17 = 0;
LAB_ram_4300ea66:
      iVar27 = huffdecode(uVar17,bits,core,&local_48);
      if (iVar27 != 0) {
        byte_align(bits);
        uVar19 = core->frame_number;
        if (uVar19 == 0) {
          (core->mc).ps_present = 0;
          (core->mc).sbr_present = 0;
          (core->mc).upsampling = 1;
          goto LAB_ram_4300ea02;
        }
        if (core->plus_enabled != 0) goto LAB_ram_4300ea0a;
        (core->mc).ps_present = 0;
        (core->mc).sbr_present = 0;
        if (stream == (aac_analysis_sbr_stream_t *)0x0) goto LAB_ram_4300ef30;
        goto LAB_ram_4300ea1e;
      }
      bVar3 = false;
      if (core->plus_enabled != 0) {
        iVar8 = stream->core_elements;
        stream->element[stream->elements].element_id = uVar17;
        stream->core_elements = iVar8 + 1;
      }
    }
    uVar20 = (uint)(byte)*puVar13 << 8;
  }
LAB_ram_4300e9dc:
  iVar27 = 0x14;
LAB_ram_4300e9de:
  byte_align(bits);
  uVar19 = core->frame_number;
  if (uVar19 == 0) {
    (core->mc).ps_present = 0;
    (core->mc).sbr_present = 0;
    (core->mc).upsampling = 1;
  }
  if (bVar3) {
LAB_ram_4300e86a:
    uVar25 = (core->input).used_bits;
    external->consumed_bytes = uVar25 >> 3;
    external->remainder_bits = uVar25 & 7;
    core->frame_number = uVar19 + 1;
    return iVar27;
  }
LAB_ram_4300ea02:
  if (core->plus_enabled == 0) {
    (core->mc).ps_present = 0;
    (core->mc).sbr_present = 0;
    if (stream != (aac_analysis_sbr_stream_t *)0x0) goto LAB_ram_4300ea1e;
    if (uVar19 == 0) {
      paStack_78 = (aac_sbr_control_abi_t *)0x0;
      paVar35 = (aac_sbr_owner_abi_t *)0x0;
      goto LAB_ram_4300ee9a;
    }
LAB_ram_4300ef30:
    paStack_78 = (aac_sbr_control_abi_t *)0x0;
    paVar35 = (aac_sbr_owner_abi_t *)0x0;
joined_r0x4300eea2:
    if (iVar27 != 0) goto LAB_ram_4300ea34;
    iVar8 = 0;
    piVar36 = paVar33->q_format;
    paVar34 = core->window_map[(local_48->spectrum).window];
    uVar17 = core->frame_length;
    pns_left(paVar34,paVar33->groups,paVar33->codebook,paVar33->factors,
             (int)(paVar33->ltp).band_prediction,(paVar33->ltp).present,
             (int)(local_48->spectrum).coefficients,(int)piVar36,&core->noise_state);
    if (0 < core->has_mask) {
      apply_ms_synt(paVar34,paVar33->groups,core->mask,paVar33->codebook,
                    (int)(local_48->spectrum).coefficients,(int)(local_44[0]->spectrum).coefficients
                    ,(int)piVar36,(int)paVar32->q_format);
    }
    iVar27 = (core->mc).channels;
    if (0 < iVar27) {
      ppaVar31 = &local_48;
      paVar34 = core->window_map[(local_48->spectrum).window];
      paVar9 = (local_48->spectrum).shared;
      iVar26 = 0;
      paVar14 = local_48;
      ppaVar28 = ppaVar31;
      if ((paVar9->ltp).present != 0) goto LAB_ram_4300ec32;
      while( true ) {
        iVar27 = (core->mc).channels;
        iVar26 = iVar26 + 1;
        if (iVar27 <= iVar26) break;
        while( true ) {
          paVar34 = core->window_map[(ppaVar28[1]->spectrum).window];
          ppaVar28 = ppaVar28 + 1;
          pns_intensity_right(core->has_mask,paVar34,paVar32->groups,(uint *)core->mask,
                              paVar32->codebook,paVar33->factors,paVar32->factors,
                              (int)(paVar32->ltp).band_prediction,(paVar32->ltp).present,
                              (int)(local_48->spectrum).coefficients,
                              (int)(local_44[0]->spectrum).coefficients,(int)piVar36,
                              (int)paVar32->q_format,&core->noise_state);
          paVar14 = *ppaVar28;
          paVar9 = (paVar14->spectrum).shared;
          if ((paVar9->ltp).present == 0) break;
LAB_ram_4300ec32:
          uStack_4c = long_term_prediction
                                ((paVar14->spectrum).window,(paVar9->ltp).weight,(paVar9->ltp).delay
                                 ,paVar14,core->ltp_buffer_state,paVar14->overlap,core->shared,
                                 uVar17);
          paVar14 = *ppaVar28;
          iVar26 = iVar26 + 1;
          trans4m_time_2_freq_fxp
                    (core->shared,(paVar14->spectrum).window,(paVar14->spectrum).previous_shape,
                     (paVar14->spectrum).current_shape,&uStack_4c,core->scratch);
          paVar9 = ((*ppaVar28)->spectrum).shared;
          apply_tns((int)core->shared,(int)paVar9->q_format,paVar34,&paVar9->tns,1,core->scratch);
          paVar14 = *ppaVar28;
          paVar9 = (paVar14->spectrum).shared;
          long_term_synthesis((paVar14->spectrum).window,paVar9->max_band,paVar34->band_top[0],
                              (paVar9->ltp).window_prediction,(paVar9->ltp).band_prediction,
                              (paVar14->spectrum).coefficients,paVar9->q_format,core->shared,
                              uStack_4c,paVar34->coefficients_per_window[0],8,8);
          iVar27 = (core->mc).channels;
          if (iVar27 <= iVar26) goto LAB_ram_4300ed06;
        }
      }
LAB_ram_4300ed06:
      if (0 < iVar27) {
        iVar26 = 0;
        do {
          paVar14 = *ppaVar31;
          paVar32 = (paVar14->spectrum).shared;
          paVar34 = core->window_map[(paVar14->spectrum).window];
          apply_tns((int)(paVar14->spectrum).coefficients,(int)paVar32->q_format,paVar34,
                    &paVar32->tns,0,core->scratch);
          paVar14 = *ppaVar31;
          uVar5 = q_normalize(((paVar14->spectrum).shared)->q_format,paVar34,
                              (paVar14->spectrum).absolute_maximum,(paVar14->spectrum).coefficients)
          ;
          paVar14 = *ppaVar31;
          piVar36 = (paVar14->spectrum).coefficients;
          iVar10 = (paVar14->spectrum).window;
          iVar37 = (paVar14->spectrum).previous_shape;
          iVar4 = (paVar14->spectrum).current_shape;
          if ((core->plus_enabled == 0) || ((stream->elements == 0 && ((core->mc).upsampling == 1)))
             ) {
            trans4m_freq_2_time_fxp_2
                      (piVar36,paVar14->overlap,iVar10,iVar37,iVar4,uVar5,
                       (paVar14->spectrum).absolute_maximum,core->scratch,external->output + iVar26)
            ;
          }
          else {
            trans4m_freq_2_time_fxp_1
                      (piVar36,paVar14->overlap,
                       paVar14->ltp_history + core->ltp_buffer_state + 0x120,iVar10,iVar37,iVar4,
                       uVar5,(paVar14->spectrum).absolute_maximum,core->scratch);
          }
          paVar14 = *ppaVar31;
          iVar27 = (core->mc).channels;
          iVar26 = iVar26 + 1;
          ppaVar31 = ppaVar31 + 1;
          (paVar14->spectrum).previous_shape = (paVar14->spectrum).current_shape;
        } while (iVar26 < iVar27);
      }
    }
    uVar30 = core->plus_enabled;
    if (uVar30 == 0) {
      iVar26 = external->requested_channels;
      external->encoded_channels = iVar27;
LAB_ram_4300ee12:
      if (iVar26 == 2) {
        if (iVar27 != 2) {
          iVar11 = (core->mc).sbr_present;
          uVar30 = 0;
          goto LAB_ram_4300f118;
        }
LAB_ram_4300ef4e:
        iVar26 = (core->mc).upsampling;
        bVar3 = false;
        goto LAB_ram_4300ef54;
      }
      if (iVar26 == 1) {
        uVar30 = 0;
LAB_ram_4300f0e4:
        piVar21 = external->output;
        iVar26 = (core->mc).upsampling;
        piVar24 = piVar21 + 0x800;
        piVar23 = piVar21;
        if (iVar26 == 2) {
          do {
            piVar22 = piVar23 + 2;
            *piVar21 = *piVar23;
            piVar21 = piVar21 + 1;
            piVar23 = piVar22;
          } while (piVar22 != piVar24);
          piVar24 = external->output_plus;
          piVar23 = piVar24 + 0x800;
          piVar21 = piVar24;
          do {
            iVar2 = *piVar24;
            piVar24 = piVar24 + 2;
            *piVar21 = iVar2;
            piVar21 = piVar21 + 1;
          } while (piVar24 != piVar23);
        }
        else {
          do {
            piVar22 = piVar23 + 2;
            *piVar21 = *piVar23;
            piVar21 = piVar21 + 1;
            piVar23 = piVar22;
          } while (piVar22 != piVar24);
        }
      }
      else {
        if ((iVar26 != 0) || (iVar27 != 1)) goto LAB_ram_4300ef4e;
        uVar30 = 0;
LAB_ram_4300ee28:
        piVar21 = external->output;
        iVar26 = (core->mc).upsampling;
        piVar24 = piVar21 + 0x800;
        piVar23 = piVar21;
        if (iVar26 == 2) {
          do {
            piVar22 = piVar23 + 2;
            *piVar21 = *piVar23;
            piVar21 = piVar21 + 1;
            piVar23 = piVar22;
          } while (piVar22 != piVar24);
          piVar24 = external->output_plus;
          piVar23 = piVar24 + 0x800;
          piVar21 = piVar24;
          do {
            iVar2 = *piVar24;
            piVar24 = piVar24 + 2;
            *piVar21 = iVar2;
            piVar21 = piVar21 + 1;
          } while (piVar24 != piVar23);
        }
        else {
          do {
            piVar22 = piVar23 + 2;
            *piVar21 = *piVar23;
            piVar21 = piVar21 + 1;
            piVar23 = piVar22;
          } while (piVar22 != piVar24);
        }
      }
LAB_ram_4300ee4a:
      if (uVar30 != 0) goto LAB_ram_4300ee4e;
      uVar7 = core->frame_number;
      core->ltp_buffer_state = core->ltp_buffer_state ^ uVar17;
      if (1 < uVar7) goto LAB_ram_4300ef68;
      uVar19 = samp_rate_info.entry[(core->mc).sample_rate_index].rate;
      iVar4 = core->frame_length;
      external->sample_rate = uVar19;
      (core->mc).implicit_channels = 1;
      external->frame_length = iVar4;
    }
    else {
      if ((core->mc).sbr_present != 0) {
        if ((core->frame_number < 2) && (paStack_78->output_rate == 0)) {
          sbr_open(samp_rate_info.entry[(core->mc).sample_rate_index].rate,paStack_78,paVar35,
                   (uint)(core->mc).downsampled_sbr);
          iVar27 = (core->mc).channels;
        }
        iVar26 = core->ltp_buffer_state;
        iVar11 = external->requested_he_level;
        piVar21 = external->output_plus;
        (core->mc).upsampling = paVar35->channel[0].frame.header.sample_rate_mode;
        iVar27 = sbr_applied(paVar35,stream,local_48->ltp_history + iVar26,
                             local_44[0]->ltp_history + iVar26,(int)external->output,(int)piVar21,
                             iVar11,paStack_78,core,iVar27);
        uVar1 = core->plus_enabled;
        if (iVar27 != 0) {
          iVar8 = 10;
        }
        iVar27 = (core->mc).channels;
        iVar26 = external->requested_channels;
        external->encoded_channels = iVar27;
        if (uVar1 == 0) goto LAB_ram_4300ee12;
        iVar29 = (core->mc).ps_present;
        iVar11 = (core->mc).sbr_present;
        if (iVar29 != 0) {
          external->encoded_channels = iVar27 << 1;
          if (iVar11 == 0) goto LAB_ram_4300f1da;
          if (iVar26 != 2) goto joined_r0x4300f354;
          goto LAB_ram_4300f1e0;
        }
        if (iVar11 == 0) goto LAB_ram_4300f02a;
        if (iVar27 == 1) {
          if (iVar26 == 0) {
            external->requested_channels = 2;
          }
          else if (iVar26 != 2) goto joined_r0x4300f354;
        }
        else {
          if (iVar26 != 2) {
joined_r0x4300f354:
            if (iVar26 != 1) goto LAB_ram_4300f03e;
            goto LAB_ram_4300f0e4;
          }
          if (iVar27 == 2) {
            iVar26 = (core->mc).upsampling;
            goto LAB_ram_4300ee4e;
          }
        }
LAB_ram_4300f118:
        piVar23 = external->output;
        iVar26 = (core->mc).upsampling;
        piVar21 = piVar23;
        if (iVar26 == 2) {
          do {
            piVar24 = piVar21 + 2;
            piVar21[1] = *piVar21;
            piVar21 = piVar24;
          } while (piVar23 + 0x800 != piVar24);
          piVar23 = external->output_plus;
          piVar21 = piVar23;
          do {
            piVar24 = piVar21 + 2;
            piVar21[1] = *piVar21;
            piVar21 = piVar24;
          } while (piVar24 != piVar23 + 0x800);
        }
        else {
          do {
            piVar24 = piVar21 + 2;
            piVar21[1] = *piVar21;
            piVar21 = piVar24;
          } while (piVar24 != piVar23 + 0x800);
        }
        if (iVar11 != 0) {
          external->encoded_channels = 2;
        }
        goto LAB_ram_4300ee4a;
      }
      iVar29 = (core->mc).ps_present;
      external->encoded_channels = iVar27;
      iVar26 = external->requested_channels;
      iVar11 = 0;
      iVar8 = 0;
      if (iVar29 == 0) {
LAB_ram_4300f02a:
        if (iVar26 != 2) {
LAB_ram_4300f030:
          if (iVar26 != 1) {
            if ((iVar26 != 0) || (external->encoded_channels != 1)) goto LAB_ram_4300f03e;
            goto LAB_ram_4300ee28;
          }
          goto LAB_ram_4300f0e4;
        }
        if (external->encoded_channels != 2) goto LAB_ram_4300f118;
        iVar26 = (core->mc).upsampling;
      }
      else {
        external->encoded_channels = iVar27 << 1;
        iVar8 = 0;
        iVar11 = 0;
LAB_ram_4300f1da:
        if (iVar26 != 2) goto LAB_ram_4300f030;
LAB_ram_4300f1e0:
        if (external->encoded_channels != 2) {
          if (iVar29 != 1) goto LAB_ram_4300f118;
          iVar26 = (core->mc).upsampling;
          goto LAB_ram_4300ee4e;
        }
LAB_ram_4300f03e:
        iVar26 = (core->mc).upsampling;
      }
LAB_ram_4300ee4e:
      if ((stream->elements == 0) && (iVar26 == 1)) {
        bVar3 = true;
LAB_ram_4300ef54:
        uVar7 = core->frame_number;
        core->ltp_buffer_state = core->ltp_buffer_state ^ uVar17;
        if (uVar7 < 2) {
          uVar19 = samp_rate_info.entry[(core->mc).sample_rate_index].rate;
          iVar27 = core->frame_length;
          external->sample_rate = uVar19;
          (core->mc).implicit_channels = 1;
          external->frame_length = iVar27;
          if (bVar3) goto LAB_ram_4300f1c0;
          goto LAB_ram_4300ef6a;
        }
      }
      else {
        uVar7 = core->frame_number;
        core->ltp_buffer_state = core->ltp_buffer_state ^ uVar17 + 0x120;
        if (uVar7 < 2) {
          uVar19 = samp_rate_info.entry[(core->mc).sample_rate_index].rate;
          iVar27 = core->frame_length;
          external->sample_rate = uVar19;
          (core->mc).implicit_channels = 1;
          external->frame_length = iVar27;
LAB_ram_4300f1c0:
          if (iVar26 == 2) {
            uVar19 = uVar19 << 1;
            external->sample_rate = uVar19;
            external->frame_length = iVar27 << 1;
            external->reposition = 2;
            goto LAB_ram_4300ef6a;
          }
        }
      }
LAB_ram_4300ef68:
      uVar19 = external->sample_rate;
    }
LAB_ram_4300ef6a:
    uVar17 = (core->input).used_bits;
    core->frame_number = uVar7 + 1;
    iVar27 = 0;
    external->bitrate = (int)((uVar17 - uVar25) * uVar19 >> 10) >> (iVar26 - 1U & 0x1f);
    if (iVar8 == 0) goto LAB_ram_4300ea50;
    paVar15 = core->program;
    iVar27 = 10;
    iVar8 = paVar15->file_is_adts;
  }
  else {
LAB_ram_4300ea0a:
    if (stream->elements == 0) {
      core->plus_enabled = 0;
      (core->mc).ps_present = 0;
      (core->mc).sbr_present = 0;
LAB_ram_4300ea1e:
      stream->elements = 0;
      paStack_78 = (aac_sbr_control_abi_t *)0x0;
      paVar35 = (aac_sbr_owner_abi_t *)0x0;
LAB_ram_4300ea26:
      if ((uVar19 == 0) && ((core->mc).sbr_present == 0)) {
LAB_ram_4300ee9a:
        external->plus_enabled = 0;
        core->plus_enabled = 0;
      }
      goto joined_r0x4300eea2;
    }
    if (core->sbr == (aac_sbr_owner_abi_t *)0x0) {
      paVar35 = (aac_sbr_owner_abi_t *)media_lib_module_calloc("AUD_Codec",1,0xd758);
      core->sbr = paVar35;
      if (paVar35 != (aac_sbr_owner_abi_t *)0x0) {
        if (core->sbr_control == (aac_sbr_control_abi_t *)0x0) goto LAB_ram_4300f150;
        goto LAB_ram_4300f172;
      }
LAB_ram_4300f418:
      core->plus_enabled = 0;
      puts("Disable AAC-Plus for memory not enough, decode continue");
      if (core->plus_enabled != 0) goto LAB_ram_4300efd8;
LAB_ram_4300f184:
      uVar19 = core->frame_number;
      (core->mc).ps_present = 0;
      (core->mc).sbr_present = 0;
      goto LAB_ram_4300ea1e;
    }
    if (core->sbr_control == (aac_sbr_control_abi_t *)0x0) {
LAB_ram_4300f150:
      paVar6 = (aac_sbr_control_abi_t *)media_lib_module_calloc("AUD_Codec",1,0x49c);
      core->sbr_control = paVar6;
      if (paVar6 == (aac_sbr_control_abi_t *)0x0) goto LAB_ram_4300f418;
      paVar35 = core->sbr;
LAB_ram_4300f172:
      uVar30 = core->plus_enabled;
      paVar35->initialize_ps = 1;
      if (uVar30 == 0) goto LAB_ram_4300f184;
    }
LAB_ram_4300efd8:
    if (external->output_plus == (int16_t *)0x0) {
      return 0x28;
    }
    paVar35 = core->sbr;
    paStack_78 = core->sbr_control;
    iVar8 = stream->elements;
    paVar35->ps = &paVar35->embedded_ps;
    if (iVar8 == 0) {
      uVar19 = core->frame_number;
      goto LAB_ram_4300ea26;
    }
    if (iVar8 == stream->core_elements) {
      (core->mc).sbr_present = 1;
      goto joined_r0x4300eea2;
    }
    (core->mc).sbr_present = 1;
    iVar27 = 10;
LAB_ram_4300ea34:
    paVar15 = core->program;
    uVar17 = (core->input).used_bits;
    iVar8 = paVar15->file_is_adts;
  }
  if (iVar8 == 2) {
    paVar15->headerless_frames = 0;
    iVar27 = 0x1e;
  }
  else {
    uVar25 = (core->input).available_bits;
    if (uVar25 < uVar17) {
      (core->input).used_bits = uVar25;
      iVar27 = 0x14;
      uVar17 = uVar25;
    }
  }
LAB_ram_4300ea50:
  external->consumed_bytes = uVar17 >> 3;
  external->remainder_bits = uVar17 & 7;
  return iVar27;
}
