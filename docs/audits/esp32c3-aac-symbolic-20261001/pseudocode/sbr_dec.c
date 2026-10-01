/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_dec @ ram:43010770
 * Types and parameter counts are inferred; verify against disassembly. */

void sbr_dec(int param_1,int *param_2,aac_sbr_frame_abi_t *frame,int param_4,
            aac_sbr_control_abi_t *control,int *param_6,aac_ps_abi_t *ps,aac_core_abi_t *core)

{
  undefined4 *puVar1;
  int32_t iVar2;
  uint8_t *puVar3;
  uint *puVar4;
  uint32_t uVar5;
  uint *puVar6;
  int iVar7;
  int32_t *piVar8;
  uint *puVar9;
  uint *puVar10;
  undefined4 uVar11;
  undefined4 uVar12;
  uint uVar13;
  int iVar14;
  uint uVar15;
  uint uVar16;
  int32_t (*paiVar17) [32];
  int *piVar18;
  uint8_t *puVar19;
  uint uVar20;
  int32_t (*paiVar21) [48];
  int iVar22;
  undefined4 *puVar23;
  undefined4 *puVar24;
  int32_t (*paiVar25) [32];
  uint8_t *puVar26;
  uint *puVar27;
  uint uVar28;
  uint *puVar29;
  int iVar30;
  aac_core_channel_abi_t *paVar31;
  int32_t *piVar32;
  int iVar33;
  int iVar34;
  int iVar35;
  int32_t iVar36;
  int32_t iStack_60;
  int32_t iStack_5c;
  int32_t iStack_58;
  int32_t iStack_54;
  int32_t iStack_50;
  int32_t iStack_4c;
  int32_t iStack_48;

  gp = &__global_pointer_;
  puVar6 = *(uint **)(core->stream_state + 0x14);
  iVar2 = 0x20;
  if (param_4 != 0) {
    iVar2 = control->low_subband;
  }
  paiVar21 = frame->high_real_history;
  memmove(frame->high_real,paiVar21,0x480);
  iVar22 = control->low_complexity;
  if (iVar22 == 0) {
    memmove(frame->high_imag,frame->high_imag_history,0x480);
    iVar22 = control->low_complexity;
  }
  iVar30 = param_1 + 0x27e;
  iVar33 = 0;
  while( true ) {
    iVar7 = control->write_offset + iVar33;
    if (iVar22 == 1) {
      calc_sbr_anafilterbank_LC(frame->low_real + iVar7,iVar30,puVar6,iVar2);
    }
    else {
      calc_sbr_anafilterbank(frame->low_real + iVar7,frame->low_imag + iVar7,iVar30,puVar6,iVar2);
    }
    if (iVar33 == 0x1f) break;
    iVar33 = iVar33 + 1;
    iVar22 = control->low_complexity;
    iVar30 = iVar30 + 0x40;
  }
  uVar13 = 0x20;
  if (*(int *)(core->channel_configuration + 0x28) == 0) {
    puVar23 = (undefined4 *)(param_1 + 0x800);
    puVar24 = (undefined4 *)(param_1 + 0xa40);
    do {
      uVar11 = *puVar23;
      uVar12 = puVar23[1];
      puVar24[2] = puVar23[2];
      *puVar24 = uVar11;
      puVar24[1] = uVar12;
      puVar1 = puVar23 + 3;
      puVar23 = puVar23 + 4;
      puVar24[3] = *puVar1;
      puVar24 = puVar24 + 4;
    } while (puVar23 != (undefined4 *)(param_1 + 0xa40));
    if (param_4 != 0) goto LAB_ram_43010876;
LAB_ram_43010dd4:
    iVar22 = 0;
    do {
      memset((int)frame->high_real + iVar22,0,0xc0);
      iVar30 = (int)frame->high_imag + iVar22;
      iVar22 = iVar22 + 0xc0;
      memset(iVar30,0,0xc0);
    } while (iVar22 != 0x1c80);
  }
  else {
    puVar23 = (undefined4 *)(param_1 + 0x800);
    puVar24 = (undefined4 *)(param_1 + -0xa40);
    do {
      uVar11 = *puVar23;
      uVar12 = puVar23[1];
      puVar24[2] = puVar23[2];
      *puVar24 = uVar11;
      puVar24[1] = uVar12;
      puVar1 = puVar23 + 3;
      puVar23 = puVar23 + 4;
      puVar24[3] = *puVar1;
      puVar24 = puVar24 + 4;
    } while (puVar23 != (undefined4 *)(param_1 + 0xa40));
    if (param_4 == 0) goto LAB_ram_43010dd4;
LAB_ram_43010876:
    iVar22 = control->read_offset;
    iVar2 = (control->remaining).noise_band_count;
    iVar36 = (control->remaining).master_band_count;
    piVar32 = (frame->frame_control).frame_info;
    if (control->low_complexity == 1) {
      sbr_generate_high_freq
                (frame->low_real + iVar22,0,frame->high_real,0,
                 (frame->domain_and_inverse_filter).inverse_filter_mode,
                 (frame->domain_and_inverse_filter).previous_inverse_filter_mode,
                 (control->remaining).noise_bands + 1,iVar2,control->low_subband,
                 (control->remaining).master_bands,iVar36,control->output_rate,piVar32,
                 frame->alias_degree,puVar6,frame->bandwidth,frame->previous_bandwidth,
                 &(control->remaining).patch_count,1,&control->high_subband);
      iStack_60 = (control->remaining).patch_count;
      iStack_5c = (control->remaining).patch_start_band[0];
      iStack_58 = (control->remaining).patch_start_band[1];
      iStack_54 = (control->remaining).patch_start_band[2];
      iStack_50 = (control->remaining).patch_start_band[3];
      iStack_4c = (control->remaining).patch_start_band[4];
      iStack_48 = (control->remaining).patch_start_band[5];
      calc_sbr_envelope(frame,frame->high_real,0,(int *)&control->remaining,
                        (control->remaining).band_count,(int)(control->remaining).noise_bands,
                        (control->remaining).noise_band_count,(frame->frame_control).reset,
                        frame->alias_degree,&(frame->harmonics_and_envelopes).harmonic_index,
                        &(frame->harmonics_and_envelopes).phase_index,
                        (int)(frame->harmonics_and_envelopes).previous_harmonics,&frame->startup,
                        (int)(control->remaining).limiter_bands,(int)(control->remaining).gate_mode,
                        (undefined4 *)0x0,(undefined4 *)0x0,(undefined4 *)0x0,(undefined4 *)0x0,
                        (int)puVar6,&iStack_60,(int)(control->remaining).sqrt_cache,
                        control->low_complexity);
    }
    else {
      sbr_generate_high_freq
                (frame->low_real + iVar22,frame->low_imag + iVar22,frame->high_real,frame->high_imag
                 ,(frame->domain_and_inverse_filter).inverse_filter_mode,
                 (frame->domain_and_inverse_filter).previous_inverse_filter_mode,
                 (control->remaining).noise_bands + 1,iVar2,control->low_subband,
                 (control->remaining).master_bands,iVar36,control->output_rate,piVar32,0,puVar6,
                 frame->bandwidth,frame->previous_bandwidth,&(control->remaining).patch_count,
                 control->low_complexity,&control->high_subband);
      iStack_60 = (control->remaining).patch_count;
      iStack_5c = (control->remaining).patch_start_band[0];
      iStack_58 = (control->remaining).patch_start_band[1];
      iStack_54 = (control->remaining).patch_start_band[2];
      iStack_50 = (control->remaining).patch_start_band[3];
      iStack_4c = (control->remaining).patch_start_band[4];
      iStack_48 = (control->remaining).patch_start_band[5];
      calc_sbr_envelope(frame,frame->high_real,frame->high_imag,(int *)&control->remaining,
                        (control->remaining).band_count,(int)(control->remaining).noise_bands,
                        (control->remaining).noise_band_count,(frame->frame_control).reset,0,
                        &(frame->harmonics_and_envelopes).harmonic_index,
                        &(frame->harmonics_and_envelopes).phase_index,
                        (int)(frame->harmonics_and_envelopes).previous_harmonics,&frame->startup,
                        (int)(control->remaining).limiter_bands,(int)(control->remaining).gate_mode,
                        (undefined4 *)(frame + 1),frame[1].domain_and_inverse_filter.envelope_domain
                        ,frame[1].harmonics_and_envelopes.add_harmonics + 0x21,
                        frame[1].harmonics_and_envelopes.add_harmonics + 0x61,(int)puVar6,&iStack_60
                        ,(int)(control->remaining).sqrt_cache,control->low_complexity);
    }
    if ((core->channels != 0) && (ps != (aac_ps_abi_t *)0x0)) {
      paVar31 = core->channel + 1;
      puVar3 = core->spectrum_and_scratch + 0x14c;
      ps->qmf_real = (int32_t (*) [64])paVar31;
      ps->qmf_imag = (int32_t (*) [64])puVar3;
      iVar22 = 0;
      do {
        if (iVar22 < (frame->frame_control).frame_info[1] << 1) {
          uVar28 = control->previous_low_subband;
        }
        else {
          uVar28 = control->low_subband;
        }
        iVar30 = control->high_subband;
        piVar32 = (int32_t *)((int)paVar31->ltp_history + iVar22 * 0x40 * 4);
        puVar3 = puVar3 + iVar22 * 0x100;
        if (iVar30 < (int)uVar28) {
          iVar33 = 0x80;
          uVar28 = uVar13;
LAB_ram_43010a24:
          iVar30 = control->read_offset + iVar22;
          paiVar25 = frame->low_real + iVar30;
          paiVar17 = frame->low_imag + iVar30;
          iVar30 = 0;
          piVar8 = piVar32;
          puVar26 = puVar3;
          do {
            iVar7 = (*paiVar25)[0];
            iVar30 = iVar30 + 1;
            paiVar25 = (int32_t (*) [32])(*paiVar25 + 1);
            uVar15 = iVar7 << 1;
            if ((int)uVar15 >> 1 != iVar7) {
              uVar15 = iVar7 >> 0x1f ^ 0x7fffffff;
            }
            *piVar8 = uVar15;
            iVar7 = (*paiVar17)[0];
            piVar8 = piVar8 + 1;
            paiVar17 = (int32_t (*) [32])(*paiVar17 + 1);
            uVar15 = iVar7 << 1;
            if ((int)uVar15 >> 1 != iVar7) {
              uVar15 = iVar7 >> 0x1f ^ 0x7fffffff;
            }
            *(uint *)puVar26 = uVar15;
            puVar26 = puVar26 + 4;
          } while (iVar30 < (int)uVar28);
          iVar30 = control->high_subband;
        }
        else {
          iVar33 = uVar28 << 2;
          if (0 < (int)uVar28) goto LAB_ram_43010a24;
        }
        memcpy((int)piVar32 + iVar33,frame->high_real + iVar22 * 0x30,(iVar30 - uVar28) * 4);
        memcpy(puVar3 + iVar33,frame->high_imag + iVar22 * 0x30,(control->high_subband - uVar28) * 4
              );
        memset(piVar32 + control->high_subband,0,(0x40 - control->high_subband) * 4);
        iVar22 = iVar22 + 1;
        memset(puVar3 + control->high_subband * 4,0,(0x40 - control->high_subband) * 4);
        paVar31 = (aac_core_channel_abi_t *)ps->qmf_real;
        puVar3 = (uint8_t *)ps->qmf_imag;
      } while (iVar22 != 0x20);
      puVar3 = puVar3 + 0x2014;
      piVar32 = paVar31->overlap + 0x2e0;
      iVar22 = 0x20;
      do {
        paiVar25 = frame->low_imag + control->read_offset + iVar22;
        piVar8 = piVar32;
        puVar26 = puVar3 + -0x14;
        do {
          puVar19 = puVar26;
          iVar30 = paiVar25[-0x28][0];
          uVar13 = iVar30 << 1;
          if ((int)uVar13 >> 1 != iVar30) {
            uVar13 = iVar30 >> 0x1f ^ 0x7fffffff;
          }
          *piVar8 = uVar13;
          iVar30 = (*paiVar25)[0];
          piVar8 = piVar8 + 1;
          paiVar25 = (int32_t (*) [32])(*paiVar25 + 1);
          uVar13 = iVar30 << 1;
          if ((int)uVar13 >> 1 != iVar30) {
            uVar13 = iVar30 >> 0x1f ^ 0x7fffffff;
          }
          *(uint *)puVar19 = uVar13;
          puVar26 = puVar19 + 4;
        } while (puVar19 + 4 != puVar3);
        iVar22 = iVar22 + 1;
        puVar3 = puVar19 + 0x104;
        piVar32 = piVar32 + 0x40;
      } while (iVar22 != 0x26);
      paiVar25 = frame->low_real;
      iVar22 = 0;
      if (0 < control->write_offset) {
        do {
          iVar30 = control->columns + iVar22;
          memmove(paiVar25,frame->low_real + iVar30,0x80);
          memmove(paiVar25 + 0x28,frame->low_imag + iVar30,0x80);
          iVar22 = iVar22 + 1;
          paiVar25 = paiVar25 + 1;
        } while (iVar22 < control->write_offset);
      }
      memmove(paiVar21,frame->high_real + 0x600,0x480);
      memmove(frame->high_imag_history,frame->high_imag + 0x600,0x480);
      puVar27 = puVar6 + 0x40;
      if (core->configuration[0xab] == 0) {
        memmove(puVar6 + 0x9c0,frame->synthesis,0x900);
      }
      else {
        memmove(puVar6 + 0x5c0,frame->synthesis,0x500);
      }
      iVar22 = 0;
      puVar4 = puVar6 + 0xcc;
      do {
        memmove(puVar4 + -0x2c,*(undefined4 *)((int)ps->hybrid->real_history + iVar22),0x30);
        puVar24 = (undefined4 *)((int)ps->hybrid->imag_history + iVar22);
        iVar22 = iVar22 + 4;
        memmove(puVar4,*puVar24,0x30);
        puVar4 = puVar4 + 0x58;
      } while (iVar22 != 0xc);
      memset(puVar6 + ps->upper_subband,0,(0x40 - ps->upper_subband) * 4);
      memset(puVar27 + ps->upper_subband,0,(0x40 - ps->upper_subband) * 4);
      puVar4 = puVar6 + 0x5a0;
      iVar30 = 0;
      uVar5 = 0;
      iVar22 = 0;
      do {
        iVar33 = iVar22;
        if ((ps->parameters).envelope_borders[iVar22] == uVar5) {
          iVar33 = iVar22 + 1;
          ps_init_stereo_mixing(ps,iVar22,control->high_subband);
        }
        ps_applied(ps,(int)*ps->qmf_real + iVar30,(int)*ps->qmf_imag + iVar30,(int *)puVar6,
                   (int *)puVar27,puVar6 + 0x80);
        iVar22 = (int)*ps->qmf_real + iVar30;
        iVar7 = (int)*ps->qmf_imag + iVar30;
        if (core->configuration[0xab] == 0) {
          if ((int)uVar5 < 0x10) {
            iVar14 = *param_2;
            iVar35 = iVar30;
          }
          else {
            iVar14 = param_2[1];
            iVar35 = iVar30 + -0x1000;
          }
          calc_sbr_synfilterbank(iVar22,iVar7,iVar14 + iVar35,(int)puVar6 + (0x2600 - iVar30),0);
        }
        else {
          calc_sbr_synfilterbank(iVar22,iVar7,uVar5 * 0x80 + *param_2,puVar4,1);
        }
        memmove((int)*ps->qmf_real + iVar30,puVar6,0x100);
        uVar5 = uVar5 + 1;
        memmove((int)*ps->qmf_imag + iVar30,puVar27,0x100);
        iVar30 = iVar30 + 0x100;
        puVar4 = puVar4 + -0x20;
        iVar22 = iVar33;
      } while (uVar5 != 0x20);
      iVar22 = 0;
      puVar27 = puVar6 + 0xec;
      do {
        memmove(*(undefined4 *)((int)ps->hybrid->real_history + iVar22),puVar27 + -0x2c,0x30);
        puVar24 = (undefined4 *)((int)ps->hybrid->imag_history + iVar22);
        iVar22 = iVar22 + 4;
        memmove(*puVar24,puVar27,0x30);
        puVar27 = puVar27 + 0x58;
      } while (iVar22 != 0xc);
      memmove(frame->synthesis,puVar6 + 0x1c0,0x900);
      if (core->configuration[0xab] == 0) {
        memmove(puVar6 + 0x940,ps->right_synthesis,0x900);
      }
      else {
        memmove(puVar6 + 0x540,ps->right_synthesis,0x500);
      }
      puVar27 = puVar6 + 0x520;
      iVar22 = 0;
      iVar30 = 0;
      do {
        iVar33 = (int)*ps->qmf_real + iVar22;
        iVar7 = (int)*ps->qmf_imag + iVar22;
        if (core->configuration[0xab] == 0) {
          if (iVar30 < 0x10) {
            iVar14 = *param_6;
            iVar35 = iVar22;
          }
          else {
            iVar14 = param_6[1];
            iVar35 = iVar22 + -0x1000;
          }
          calc_sbr_synfilterbank(iVar33,iVar7,iVar14 + iVar35,(int)puVar6 + (0x2400 - iVar22),0);
        }
        else {
          calc_sbr_synfilterbank(iVar33,iVar7,iVar30 * 0x80 + *param_6,puVar27,1);
        }
        iVar30 = iVar30 + 1;
        iVar22 = iVar22 + 0x100;
        puVar27 = puVar27 + -0x20;
      } while (iVar30 != 0x20);
      if (core->configuration[0xab] == 0) {
        memmove(ps->right_synthesis,puVar6 + 0x140,0x900);
        iVar2 = control->low_subband;
        (frame->frame_control).reset = 0;
        control->previous_low_subband = iVar2;
        return;
      }
      memmove(ps->right_synthesis,puVar6 + 0x140,0x500);
      (frame->frame_control).reset = 0;
      goto LAB_ram_4301128c;
    }
  }
  puVar27 = puVar6 + 0x40;
  if (core->configuration[0xab] == 0) {
    memmove(puVar6 + 0x880,frame->synthesis,0x900);
  }
  else {
    memmove(puVar6 + 0x480,frame->synthesis,0x500);
  }
  puVar4 = puVar6 + 0x840;
  puVar29 = puVar6 + 0x460;
  iVar22 = 0;
  iVar30 = 0;
  iVar33 = 0;
  do {
    iVar7 = control->low_complexity;
    iVar35 = control->read_offset + iVar33;
    paiVar17 = frame->low_real + iVar35;
    puVar9 = puVar6;
    paiVar25 = paiVar17;
    if (param_4 == 0) {
      control->high_subband = 0x20;
      if (iVar7 != 1) goto LAB_ram_43010ea6;
LAB_ram_4301113e:
      uVar15 = 0;
      iVar34 = 0x10;
      iVar7 = iVar34;
      uVar28 = uVar13;
LAB_ram_4301114a:
      do {
        *puVar9 = (*paiVar25)[0] >> 9;
        iVar34 = iVar34 + -1;
        puVar9[1] = (*paiVar25)[1] >> 9;
        puVar9 = puVar9 + 2;
        paiVar25 = (int32_t (*) [32])(*paiVar25 + 2);
      } while (iVar34 != 0);
      paiVar17 = (int32_t (*) [32])(*paiVar17 + iVar7 * 2);
      puVar9 = puVar6 + (iVar7 + -1) * 2 + 2;
LAB_ram_43011172:
      puVar10 = puVar9;
      if (uVar15 != 0) {
        puVar10 = puVar9 + 1;
        *puVar9 = (*paiVar17)[0] >> 9;
      }
      iVar7 = control->high_subband;
      if ((int)uVar28 < iVar7) {
        piVar18 = (int *)((int)frame->high_real + iVar22);
        puVar9 = puVar10;
        do {
          puVar10 = puVar9 + 1;
          uVar28 = uVar28 + 1;
          *puVar9 = *piVar18 << 1;
          iVar7 = control->high_subband;
          piVar18 = piVar18 + 1;
          puVar9 = puVar10;
        } while ((int)uVar28 < iVar7);
      }
      memset(puVar10,0,(0x40 - iVar7) * 4);
      if (core->configuration[0xab] == 0) {
        if (iVar33 < 0x10) {
          iVar35 = *param_2;
          iVar7 = iVar30;
        }
        else {
          iVar35 = param_2[1];
          iVar7 = iVar30 + -0x1000;
        }
        calc_sbr_synfilterbank_LC(puVar6,iVar35 + iVar7,puVar4,0);
      }
      else {
        calc_sbr_synfilterbank_LC(puVar6,iVar33 * 0x80 + *param_2,puVar29,1);
      }
    }
    else {
      if (iVar33 < (frame->frame_control).frame_info[1] << 1) {
        uVar28 = control->previous_low_subband;
      }
      else {
        uVar28 = control->low_subband;
      }
      iVar14 = control->high_subband;
      if (iVar14 < (int)uVar28) {
        if (iVar7 == 1) goto LAB_ram_4301113e;
LAB_ram_43010ea6:
        uVar15 = 0;
        iVar34 = 0x10;
        iVar7 = 0x80;
        uVar28 = uVar13;
        uVar16 = uVar13;
LAB_ram_43010eb4:
        do {
          iVar14 = (*paiVar17)[0];
          paiVar17 = (int32_t (*) [32])(*paiVar17 + 1);
          uVar28 = uVar28 - 1;
          uVar20 = iVar14 << 1;
          if ((int)uVar20 >> 1 != iVar14) {
            uVar20 = iVar14 >> 0x1f ^ 0x7fffffff;
          }
          *puVar9 = uVar20;
          puVar9 = puVar9 + 1;
        } while (uVar28 != 0);
        iVar14 = control->high_subband;
        uVar28 = uVar16;
      }
      else {
        iVar34 = (int)uVar28 >> 1;
        uVar15 = uVar28 & 1;
        if (iVar7 == 1) {
          iVar7 = iVar34;
          if (iVar34 != 0) goto LAB_ram_4301114a;
          goto LAB_ram_43011172;
        }
        iVar7 = uVar28 << 2;
        uVar16 = uVar28;
        if (uVar28 != 0) goto LAB_ram_43010eb4;
        iVar34 = 0;
        uVar15 = 0;
        iVar7 = 0;
      }
      puVar24 = (undefined4 *)((int)puVar6 + iVar7);
      if ((int)uVar28 < iVar14) {
        puVar23 = (undefined4 *)((int)frame->high_real + iVar22);
        uVar16 = uVar28;
        do {
          uVar11 = *puVar23;
          uVar16 = uVar16 + 1;
          puVar23 = puVar23 + 1;
          *puVar24 = uVar11;
          iVar14 = control->high_subband;
          puVar24 = puVar24 + 1;
        } while ((int)uVar16 < iVar14);
      }
      memset(puVar24,0,(0x40 - iVar14) * 4);
      paiVar17 = frame->low_imag + iVar35;
      iVar35 = iVar34;
      paiVar25 = paiVar17;
      puVar9 = puVar27;
      if (iVar34 != 0) {
        do {
          iVar14 = (*paiVar25)[0];
          iVar35 = iVar35 + -1;
          uVar16 = iVar14 << 1;
          if ((int)uVar16 >> 1 != iVar14) {
            uVar16 = iVar14 >> 0x1f ^ 0x7fffffff;
          }
          *puVar9 = uVar16;
          iVar14 = (*paiVar25)[1];
          uVar16 = iVar14 << 1;
          if ((int)uVar16 >> 1 != iVar14) {
            uVar16 = iVar14 >> 0x1f ^ 0x7fffffff;
          }
          puVar9[1] = uVar16;
          paiVar25 = (int32_t (*) [32])(*paiVar25 + 2);
          puVar9 = puVar9 + 2;
        } while (iVar35 != 0);
        paiVar17 = (int32_t (*) [32])(*paiVar17 + iVar34 * 2);
        puVar9 = puVar6 + (iVar34 + -1) * 2 + 0x42;
      }
      if (uVar15 != 0) {
        iVar35 = (*paiVar17)[0];
        uVar15 = iVar35 << 1;
        if (iVar35 != (int)uVar15 >> 1) {
          uVar15 = iVar35 >> 0x1f ^ 0x7fffffff;
        }
        *puVar9 = uVar15;
      }
      iVar35 = control->high_subband;
      puVar24 = (undefined4 *)((int)puVar27 + iVar7);
      if ((int)uVar28 < iVar35) {
        puVar23 = (undefined4 *)((int)frame->high_imag + iVar22);
        do {
          uVar11 = *puVar23;
          uVar28 = uVar28 + 1;
          puVar23 = puVar23 + 1;
          *puVar24 = uVar11;
          iVar35 = control->high_subband;
          puVar24 = puVar24 + 1;
        } while ((int)uVar28 < iVar35);
      }
      memset(puVar24,0,(0x40 - iVar35) * 4);
      if (core->configuration[0xab] == 0) {
        if (iVar33 < 0x10) {
          iVar35 = *param_2;
          iVar7 = iVar30;
        }
        else {
          iVar35 = param_2[1];
          iVar7 = iVar30 + -0x1000;
        }
        calc_sbr_synfilterbank(puVar6,puVar27,iVar35 + iVar7,puVar4,0);
      }
      else {
        calc_sbr_synfilterbank(puVar6,puVar27,iVar33 * 0x80 + *param_2,puVar29,1);
      }
    }
    iVar33 = iVar33 + 1;
    iVar30 = iVar30 + 0x100;
    puVar4 = puVar4 + -0x40;
    puVar29 = puVar29 + -0x20;
    iVar22 = iVar22 + 0xc0;
  } while (iVar33 != 0x20);
  if (core->configuration[0xab] == 0) {
    memmove(frame->synthesis,puVar6 + 0x80,0x900);
  }
  else {
    memmove(frame->synthesis,puVar6 + 0x80,0x500);
  }
  paiVar25 = frame->low_real;
  iVar22 = 0;
  if (0 < control->write_offset) {
    do {
      iVar30 = memmove(paiVar25,frame->low_real + control->columns + iVar22,0x80);
      iVar22 = iVar22 + 1;
      paiVar25 = (int32_t (*) [32])(iVar30 + 0x80);
    } while (iVar22 < control->write_offset);
  }
  memmove(paiVar21,frame->high_real + 0x600,0x480);
  if (control->low_complexity == 0) {
    paiVar25 = frame->low_imag;
    iVar22 = 0;
    if (0 < control->write_offset) {
      do {
        iVar30 = memmove(paiVar25,frame->low_imag + control->columns + iVar22,0x80);
        iVar22 = iVar22 + 1;
        paiVar25 = (int32_t (*) [32])(iVar30 + 0x80);
      } while (iVar22 < control->write_offset);
    }
    memmove(frame->high_imag_history,frame->high_imag + 0x600,0x480);
  }
  (frame->frame_control).reset = 0;
  if (param_4 == 0) {
    return;
  }
LAB_ram_4301128c:
  control->previous_low_subband = control->low_subband;
  return;
}
