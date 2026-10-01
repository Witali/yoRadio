/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: getics @ ram:43008a78
 * Types and parameter counts are inferred; verify against disassembly. */

int getics(aac_analysis_bits_t *bits,int param_2,aac_analysis_core_t *core,
          aac_analysis_core_channel_t *channel,int *param_5,int *param_6,uint *param_7,
          aac_analysis_tns_t *tns,aac_analysis_window_t **window_map,aac_analysis_pulse_t *pulse,
          aac_analysis_section_t *sections)

{
  byte bVar1;
  ushort uVar2;
  uint uVar3;
  int iVar4;
  int32_t *piVar5;
  int32_t *piVar6;
  uint uVar7;
  int *piVar8;
  int iVar9;
  undefined4 uVar10;
  aac_analysis_section_t *paVar11;
  int iVar12;
  int iVar13;
  uint uVar14;
  aac_analysis_channel_shared_t *paVar15;
  int iVar16;
  uint *puVar17;
  int32_t *piVar18;
  aac_analysis_shared_t *paVar19;
  aac_analysis_shared_t *paVar20;
  uint8_t *puVar21;
  int32_t *piVar22;
  int32_t *piVar23;
  int iVar24;
  aac_analysis_window_t *window;
  code *pcVar25;
  int iVar26;
  code *pcVar27;
  int32_t *piVar28;
  aac_analysis_window_t *window_00;
  int iStackY_78;
  int *apiStack_44 [4];

  gp = &__global_pointer_;
  uVar7 = bits->used_bits;
  uVar3 = bits->input_length - (uVar7 >> 3);
  if (uVar3 < 2) {
    uVar14 = 0;
    if (uVar3 != 1) goto LAB_ram_43008ade;
    uVar2 = *(ushort *)(bits->buffer + (uVar7 >> 3));
    bits->used_bits = uVar7 + 8;
    uVar14 = (((uint)(byte)uVar2 << 8) << (uVar7 & 7)) >> 8 & 0xff;
    if (param_2 != 0) goto LAB_ram_43008aea;
LAB_ram_43008bf8:
    apiStack_44[0] = param_6;
    iVar9 = get_ics_info(bits,param_2,(uint *)&(channel->spectrum).window,
                         (uint *)&(channel->spectrum).current_shape,param_5,(uint *)param_6,
                         window_map,&((channel->spectrum).shared)->ltp,(aac_analysis_ltp_t *)0x0);
    iVar16 = *apiStack_44[0];
    window = window_map[(channel->spectrum).window];
    if (iVar16 < 1) goto LAB_ram_43008c44;
LAB_ram_43008b00:
    iVar13 = 0;
    piVar8 = param_5;
    do {
      iVar12 = *piVar8;
      piVar8 = piVar8 + 1;
      iVar13 = iVar13 + 1;
    } while (iVar12 < window->windows);
    piVar8 = (int *)huffcb(sections,bits,(uint *)window->section_bits,
                           window->bands_per_window[0] * iVar13,window->bands_per_window[0],iVar16);
    if (piVar8 == (int *)0x0) {
      if (window->is_long != 0) {
        return 1;
      }
      calc_gsfb_table(window,param_5);
      return 1;
    }
    if (0 < (int)piVar8) {
      iVar16 = 0;
      paVar11 = sections;
      do {
        iVar13 = paVar11->end;
        iVar16 = iVar13 - iVar16;
        if (0 < iVar16) {
          uVar3 = paVar11->codebook;
          iVar12 = iVar16;
          puVar17 = param_7;
          do {
            iVar12 = iVar12 + -1;
            *puVar17 = uVar3;
            puVar17 = puVar17 + 1;
          } while (iVar12 != 0);
          param_7 = param_7 + iVar16;
        }
        paVar11 = paVar11 + 1;
        iVar16 = iVar13;
      } while (sections + (int)piVar8 != paVar11);
    }
    iVar16 = window->is_long;
    apiStack_44[0] = piVar8;
  }
  else {
    uVar2 = *(ushort *)(bits->buffer + (uVar7 >> 3));
    uVar14 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar7 & 7)) << 0x10) >> 0x18;
LAB_ram_43008ade:
    bits->used_bits = uVar7 + 8;
    if (param_2 == 0) goto LAB_ram_43008bf8;
LAB_ram_43008aea:
    iVar9 = 0;
    iVar16 = *param_6;
    window = window_map[(channel->spectrum).window];
    if (0 < iVar16) goto LAB_ram_43008b00;
LAB_ram_43008c44:
    memset(param_7,0,0x200);
    iVar16 = window->is_long;
    apiStack_44[0] = (int *)0x0;
  }
  if (iVar16 == 0) {
    calc_gsfb_table(window,param_5);
  }
  if (iVar9 != 0) {
    return iVar9;
  }
  iVar9 = hufffac(window,bits,param_5,(int)apiStack_44[0],sections,uVar14,
                  (uint *)((channel->spectrum).shared)->factors,core->scratch->words);
  if (iVar9 != 0) {
    return iVar9;
  }
  uVar3 = bits->used_bits;
  uVar14 = bits->input_length;
  puVar21 = bits->buffer;
  uVar7 = uVar3 + 1;
  if (uVar3 >> 3 < uVar14) {
    bVar1 = puVar21[uVar3 >> 3];
    bits->used_bits = uVar7;
    uVar3 = ((uint)bVar1 << (uVar3 & 7)) >> 7 & 1;
    pulse->present = uVar3;
    if (uVar3 != 0) {
      if (window->is_long != 1) {
        return 1;
      }
      iVar9 = get_pulse_data(pulse,bits);
      if (iVar9 != 0) {
        return iVar9;
      }
      uVar7 = bits->used_bits;
      puVar21 = bits->buffer;
      uVar14 = bits->input_length;
    }
  }
  else {
    bits->used_bits = uVar7;
    pulse->present = 0;
  }
  if (uVar7 >> 3 < uVar14) {
    bVar1 = puVar21[uVar7 >> 3];
    bits->used_bits = uVar7 + 1;
    uVar3 = ((uint)bVar1 << (uVar7 & 7)) >> 7 & 1;
    tns->present = uVar3;
    if (uVar3 != 0) {
      get_tns(((channel->spectrum).shared)->max_band,bits,(channel->spectrum).window,window,
              &core->mc,tns,core->scratch);
      puVar21 = bits->buffer;
      uVar14 = bits->input_length;
      piVar8 = apiStack_44[0];
      goto LAB_ram_43008cbe;
    }
  }
  else {
    bits->used_bits = uVar7 + 1;
    tns->present = 0;
  }
  piVar8 = apiStack_44[0];
  if (0 < window->windows) {
    memset(tns->filter_count,0,window->windows << 2);
    piVar8 = apiStack_44[0];
  }
LAB_ram_43008cbe:
  uVar3 = bits->used_bits;
  if (uVar3 >> 3 < uVar14) {
    bVar1 = puVar21[uVar3 >> 3];
    bits->used_bits = uVar3 + 1;
    if (((uint)bVar1 << (uVar3 & 7) & 0x80) != 0) {
      return 1;
    }
  }
  else {
    bits->used_bits = uVar3 + 1;
  }
  paVar15 = (channel->spectrum).shared;
  window_00 = *window_map;
  piVar18 = (channel->spectrum).coefficients;
  paVar20 = (aac_analysis_shared_t *)core->scratch;
  paVar19 = core->shared;
  apiStack_44[0] = (int *)0x0;
  if ((int)piVar8 < 1) {
LAB_ram_430097d0:
    if (window->is_long == 0) {
      deinterleave((int)paVar19,(int)paVar20,window);
      paVar19 = paVar20;
    }
    else if (pulse->present == 1) {
      pulse_nc((short *)paVar19->predicted_samples,pulse,window_00,(int *)apiStack_44);
    }
    if (apiStack_44[0] < (int *)0x2001) {
      iVar9 = pv_normalize((int)apiStack_44[0] *
                           (*(int *)(inverseQuantTable + ((int)apiStack_44[0] >> 3) * 4 + 4) +
                            0x7ffffffU >> 0x1a));
      if (0x1b < iVar9) {
        iVar9 = 0x1b;
      }
      iStackY_78 = window->windows;
      if (0 < iStackY_78) {
        iVar16 = window->bands_per_window[0];
        iVar13 = 0;
        if (0 < iVar16) {
          do {
            iVar26 = 0;
            piVar6 = paVar15->factors + iVar13;
            piVar28 = paVar15->q_format + iVar13;
            iVar4 = iVar16 + iVar13;
            iVar12 = 0;
            do {
              iVar24 = (int)*(short *)((int)window->band_top[0] + iVar26);
              uVar3 = iVar24 - iVar12;
              if (0x400 < uVar3) {
                return -1;
              }
              uVar7 = *piVar6;
              *piVar28 = iVar9;
              esc_iquant_scaling(paVar19,piVar18,uVar3,iVar9,
                                 *(undefined2 *)((int)&exptable + (uVar7 & 3) * 2),apiStack_44[0]);
              iVar13 = iVar13 + 1;
              *piVar28 = *piVar28 - (((int)(uVar7 - 100) >> 2) + 1);
              paVar19 = (aac_analysis_shared_t *)((int)paVar19 + uVar3 * 2);
              iVar26 = iVar26 + 2;
              piVar6 = piVar6 + 1;
              piVar28 = piVar28 + 1;
              piVar18 = piVar18 + uVar3;
              iVar12 = iVar24;
            } while (iVar13 != iVar4);
            iStackY_78 = iStackY_78 + -1;
          } while (iStackY_78 != 0);
        }
      }
      return 0;
    }
  }
  else {
    uVar3 = sections->codebook;
    piVar6 = window->frame_band_top;
    piVar22 = (int32_t *)0x0;
    piVar28 = piVar6;
    iVar9 = 0;
    while ((uVar3 < 0x10 && (iVar16 = sections->end, -1 < iVar16))) {
      if ((uVar3 - 1 & 0xc) == 0xc) {
        piVar6 = piVar28 + iVar16;
        uVar3 = (int)piVar6[-1] - (int)piVar22;
        if (0x400 < uVar3) {
          return -1;
        }
        memset((int)paVar19 + (int)piVar22 * 2,0,uVar3 * 2);
        memset((int)paVar20 + (int)piVar22 * 2,0,uVar3 * 2);
        piVar22 = (int32_t *)piVar6[-1];
      }
      else {
        if ((int)uVar3 < 5) {
          uVar7 = uVar3;
          if (hcbbook_binary.entry[uVar3].signed_codebook == 0) {
            if (uVar3 == 3) {
              pcVar25 = unpack_idx_sgn;
              pcVar27 = decode_huff_cw_tab3;
              uVar7 = 4;
            }
            else if (uVar3 == 4) {
              pcVar25 = unpack_idx_sgn;
              pcVar27 = decode_huff_cw_tab4;
            }
            else {
              pcVar25 = unpack_idx_sgn;
LAB_ram_43009890:
              if (uVar3 == 1) {
                pcVar27 = decode_huff_cw_tab1;
                uVar7 = 4;
              }
              else {
                pcVar27 = decode_huff_cw_tab2;
                uVar7 = 4;
              }
            }
          }
          else if (uVar3 == 3) {
            uVar7 = 4;
            pcVar25 = unpack_idx;
            pcVar27 = decode_huff_cw_tab3;
          }
          else {
            pcVar25 = unpack_idx;
            if (uVar3 != 4) goto LAB_ram_43009890;
            pcVar25 = unpack_idx;
            pcVar27 = decode_huff_cw_tab4;
          }
        }
        else if (uVar3 == 0xb) {
          pcVar25 = unpack_idx_esc;
          pcVar27 = decode_huff_cw_tab11;
          uVar7 = 2;
        }
        else {
          if (hcbbook_binary.entry[uVar3].signed_codebook == 0) {
            pcVar25 = unpack_idx_sgn;
          }
          else {
            pcVar25 = unpack_idx;
          }
          if (uVar3 == 6) {
            pcVar27 = decode_huff_cw_tab6;
            uVar7 = 2;
          }
          else if ((int)uVar3 < 7) {
            pcVar27 = decode_huff_cw_tab5;
            uVar7 = 2;
          }
          else if (uVar3 == 9) {
            pcVar27 = decode_huff_cw_tab9;
            uVar7 = 2;
          }
          else if ((int)uVar3 < 10) {
            if (uVar3 == 7) {
              pcVar27 = decode_huff_cw_tab7;
              uVar7 = 2;
            }
            else {
              pcVar27 = decode_huff_cw_tab8;
              uVar7 = 2;
            }
          }
          else {
            if (uVar3 != 10) {
              return -1;
            }
            pcVar27 = decode_huff_cw_tab10;
            uVar7 = 2;
          }
        }
        if (iVar9 < iVar16) {
          iVar13 = (int)piVar22 * 2 + (int)paVar19;
          piVar5 = piVar22;
          piVar23 = piVar6;
          iVar12 = iVar9;
          do {
            piVar22 = (int32_t *)*piVar23;
            piVar23 = piVar23 + 1;
            for (iVar4 = (int)piVar22 - (int)piVar5; iVar4 - 1U < 0x3ff; iVar4 = iVar4 - uVar7) {
              uVar10 = (*pcVar27)(bits);
              (*pcVar25)(iVar13,uVar10,hcbbook_binary.entry + uVar3,bits,apiStack_44);
              iVar13 = iVar13 + uVar7 * 2;
            }
            iVar12 = iVar12 + 1;
            piVar5 = piVar22;
          } while (iVar16 != iVar12);
          piVar6 = piVar6 + (iVar16 - iVar9);
        }
      }
      if (piVar8 == (int *)0x1) goto LAB_ram_430097d0;
      piVar8 = (int *)((int)piVar8 + -1);
      sections = sections + 1;
      uVar3 = sections->codebook;
      iVar9 = iVar16;
    }
  }
  return -1;
}
