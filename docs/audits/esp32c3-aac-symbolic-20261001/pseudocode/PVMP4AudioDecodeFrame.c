/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: PVMP4AudioDecodeFrame @ ram:4300e7e6
 * Types and parameter counts are inferred; verify against disassembly. */

int PVMP4AudioDecodeFrame(uint *param_1,aac_core_abi_t *core)

{
  uint8_t uVar1;
  undefined2 uVar2;
  bool bVar3;
  aac_sbr_control_abi_t *paVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  ushort *puVar9;
  aac_core_channel_abi_t *paVar10;
  uint32_t uVar11;
  int iVar12;
  byte *pbVar13;
  uint uVar14;
  undefined2 *puVar15;
  undefined2 *puVar16;
  undefined2 *puVar17;
  undefined2 *puVar18;
  uint uVar19;
  int iVar20;
  int iVar21;
  aac_core_channel_abi_t **ppaVar22;
  int *piVar23;
  uint8_t uVar24;
  aac_core_channel_abi_t **ppaVar25;
  int iVar26;
  int iVar27;
  int iVar28;
  undefined4 uVar29;
  uint8_t *puVar30;
  aac_sbr_owner_abi_t *paVar31;
  aac_sbr_control_abi_t *paStack_78;
  undefined4 uStack_4c;
  aac_core_channel_abi_t *local_48;
  aac_core_channel_abi_t *local_44 [4];

  gp = &__global_pointer_;
  iVar27 = *(int *)(core->channel[0].spectrum_and_window + 4);
  local_44[0] = core->channel + 1;
  local_48 = core->channel;
  iVar26 = *(int *)(core->channel[1].spectrum_and_window + 4);
  uVar14 = param_1[1];
  uVar8 = *param_1;
  uVar19 = param_1[10] * 8 + param_1[0xb];
  if (param_1[7] == 0) {
    *(uint *)(core->configuration + 0x13) = uVar19;
    *(uint *)(core->configuration + 0xf) = uVar8;
    *(uint *)(core->configuration + 0x1b) = uVar14;
    *(uint *)(core->configuration + 0x17) = uVar14 << 3;
    if (uVar14 << 3 < uVar19) {
      byte_align(core->configuration + 0xf);
      uVar11 = core->frame_number;
      iVar21 = 10;
      if (uVar11 == 0) {
        core->channels = 0;
        core->configuration[0xb3] = 0;
        core->configuration[0xb4] = 0;
        core->configuration[0xb5] = 0;
        core->configuration[0xb6] = 0;
        core->configuration[0xa7] = 1;
        core->configuration[0xa8] = 0;
        core->configuration[0xa9] = 0;
        core->configuration[0xaa] = 0;
        iVar21 = 10;
      }
      goto LAB_ram_4300e86a;
    }
    iVar12 = *(int *)(core->configuration + 0x23);
    iVar6 = *(int *)(iVar12 + 0x348);
    if (iVar6 == 0) {
      piVar23 = (int *)0x0;
      goto LAB_ram_4300e934;
    }
    piVar23 = (int *)0x0;
LAB_ram_4300e8d4:
    if (core->frame_number == 0) {
      iVar21 = get_adif_header(core,*(undefined4 *)(core->stream_state + 0x14));
      byte_align(core->configuration + 0xf);
      iVar12 = *(int *)(core->configuration + 0x23);
      if (iVar21 != 0) {
        *(undefined4 *)(iVar12 + 0x348) = 2;
        goto LAB_ram_4300e8f2;
      }
      *(undefined4 *)(iVar12 + 0x348) = 1;
LAB_ram_4300f050:
      byte_align(core->configuration + 0xf);
      if (param_1[7] != 0) {
        *piVar23 = 0;
        piVar23[1] = 0;
      }
    }
    else {
      if ((core->frame_number == 1) && (iVar6 == 1)) {
        uVar14 = uVar14 - (uVar19 >> 3);
        pbVar13 = (byte *)((uVar19 >> 3) + uVar8);
        if (uVar14 < 4) {
          if (uVar14 == 2) {
            uVar8 = 0;
LAB_ram_4300f4c8:
            uVar8 = (uint)pbVar13[1] << 0x10 | uVar8;
LAB_ram_4300f474:
            uVar8 = (uint)*pbVar13 << 0x18 | uVar8;
            goto LAB_ram_4300f3ac;
          }
          if (uVar14 == 3) {
            uVar8 = (uint)pbVar13[2] << 8;
            goto LAB_ram_4300f4c8;
          }
          if (uVar14 == 1) {
            uVar8 = 0;
            goto LAB_ram_4300f474;
          }
        }
        else {
          uVar8 = (uint)*pbVar13 << 0x18 | (uint)pbVar13[1] << 0x10 | (uint)pbVar13[3] |
                  (uint)pbVar13[2] << 8;
LAB_ram_4300f3ac:
          *(uint *)(core->configuration + 0x13) = uVar19 + 3;
          if ((uVar8 << (uVar19 & 7)) >> 0x1d == 7) {
            byte_align(core->configuration + 0xf);
            uVar8 = *(uint *)(core->configuration + 0x13);
            uVar11 = core->frame_number;
            param_1[0xb] = uVar8 & 7;
            param_1[10] = uVar8 >> 3;
            core->frame_number = uVar11 + 1;
            return 0;
          }
        }
        *(uint *)(core->configuration + 0x13) = uVar19;
        goto LAB_ram_4300f050;
      }
      iVar21 = 0;
      if (iVar6 != 2) goto LAB_ram_4300f050;
LAB_ram_4300e8f2:
      if (*(int *)(iVar12 + 0x34c) == 0) {
        iVar6 = get_adts_header(core,core->stream_state + 4,core->stream_state + 8,3);
        if (iVar6 == 0) {
          uVar7 = *(uint *)(core->configuration + 0x13);
          uVar8 = *(uint *)(core->configuration + 0xf);
          uVar14 = *(uint *)(core->configuration + 0x1b);
          uVar5 = *(uint *)(core->configuration + 0x17);
          if (param_1[7] != 0) {
            *piVar23 = 0;
            piVar23[1] = 0;
          }
          goto LAB_ram_4300e93a;
        }
        if (param_1[7] != 0) {
          *piVar23 = 0;
          piVar23[1] = 0;
        }
        iVar21 = 0x1e;
LAB_ram_4300e858:
        byte_align(core->configuration + 0xf);
        uVar11 = core->frame_number;
        if (uVar11 == 0) {
          core->channels = 0;
          core->configuration[0xb3] = 0;
          core->configuration[0xb4] = 0;
          core->configuration[0xb5] = 0;
          core->configuration[0xb6] = 0;
          core->configuration[0xa7] = 1;
          core->configuration[0xa8] = 0;
          core->configuration[0xa9] = 0;
          core->configuration[0xaa] = 0;
        }
        goto LAB_ram_4300e86a;
      }
      uVar8 = param_1[7];
      *(int *)(iVar12 + 0x34c) = *(int *)(iVar12 + 0x34c) + -1;
      if (uVar8 != 0) {
        *piVar23 = 0;
        piVar23[1] = 0;
      }
      if (iVar21 != 0) goto LAB_ram_4300e858;
    }
    uVar7 = *(uint *)(core->configuration + 0x13);
    uVar8 = *(uint *)(core->configuration + 0xf);
    uVar14 = *(uint *)(core->configuration + 0x1b);
    uVar5 = *(uint *)(core->configuration + 0x17);
  }
  else {
    piVar23 = *(int **)core->stream_state;
    *(uint *)(core->configuration + 0x13) = uVar19;
    *(uint *)(core->configuration + 0xf) = uVar8;
    *(uint *)(core->configuration + 0x1b) = uVar14;
    *(uint *)(core->configuration + 0x17) = uVar14 << 3;
    if (uVar14 << 3 < uVar19) {
      *piVar23 = 0;
      piVar23[1] = 0;
      iVar21 = 10;
      goto LAB_ram_4300e858;
    }
    iVar12 = *(int *)(core->configuration + 0x23);
    iVar6 = *(int *)(iVar12 + 0x348);
    if (iVar6 != 0) goto LAB_ram_4300e8d4;
    *piVar23 = 0;
    piVar23[1] = 0;
LAB_ram_4300e934:
    uVar5 = uVar14 << 3;
    uVar7 = uVar19;
  }
LAB_ram_4300e93a:
  puVar30 = core->configuration + 0xf;
  bVar3 = true;
  uVar14 = uVar14 - (uVar7 >> 3);
  puVar9 = (ushort *)(uVar8 + (uVar7 >> 3));
  uVar8 = uVar7 + 3;
  if (uVar14 < 2) goto LAB_ram_4300e9d2;
LAB_ram_4300e954:
  uVar14 = (uint)(*puVar9 >> 8) + (uint)*puVar9 * 0x100 & 0xffff;
  while (*(uint *)(core->configuration + 0x13) = uVar8, uVar8 <= uVar5) {
    uVar14 = uVar14 << (uVar7 & 7);
    uVar8 = uVar14 >> 0xd & 7;
    if (uVar8 == 5) {
      if (core->frame_number < 2) {
        iVar21 = get_prog_config(core,*(undefined4 *)(core->stream_state + 0x14));
        if (iVar21 == 0) goto LAB_ram_4300e9ba;
      }
      else {
        iVar21 = 10;
      }
      goto LAB_ram_4300e9de;
    }
    if (uVar8 < 6) {
      if ((uVar14 >> 0xe & 3) == 0) goto LAB_ram_4300ea66;
      if (uVar8 == 4) {
        get_dse(*(undefined4 *)(core->stream_state + 0x18),puVar30);
        goto LAB_ram_4300e9ba;
      }
      iVar21 = -1;
      goto LAB_ram_4300e9de;
    }
    if (uVar8 != 6) {
      iVar21 = 0;
      goto LAB_ram_4300e9de;
    }
    if ((core->plus_enabled == 0) ||
       (24000 < *(int *)(samp_rate_info + *(int *)(core->configuration + 0x9f) * 0xc))) {
      getfill(puVar30);
    }
    else {
      get_sbr_bitstream(piVar23,puVar30);
    }
LAB_ram_4300e9ba:
    while( true ) {
      uVar7 = *(uint *)(core->configuration + 0x13);
      uVar14 = *(int *)(core->configuration + 0x1b) - (uVar7 >> 3);
      puVar9 = (ushort *)(*(int *)(core->configuration + 0xf) + (uVar7 >> 3));
      uVar5 = *(uint *)(core->configuration + 0x17);
      uVar8 = uVar7 + 3;
      if (1 < uVar14) goto LAB_ram_4300e954;
LAB_ram_4300e9d2:
      if (uVar14 == 1) break;
      *(uint *)(core->configuration + 0x13) = uVar8;
      if (uVar5 < uVar8) goto LAB_ram_4300e9dc;
      uVar8 = 0;
LAB_ram_4300ea66:
      iVar21 = huffdecode(uVar8,puVar30,core,&local_48);
      if (iVar21 != 0) {
        byte_align(puVar30);
        uVar11 = core->frame_number;
        if (uVar11 == 0) {
          core->channels = 0;
          core->configuration[0xb3] = 0;
          core->configuration[0xb4] = 0;
          core->configuration[0xb5] = 0;
          core->configuration[0xb6] = 0;
          core->configuration[0xa7] = 1;
          core->configuration[0xa8] = 0;
          core->configuration[0xa9] = 0;
          core->configuration[0xaa] = 0;
          goto LAB_ram_4300ea02;
        }
        if (core->plus_enabled != 0) goto LAB_ram_4300ea0a;
        core->channels = 0;
        core->configuration[0xb3] = 0;
        core->configuration[0xb4] = 0;
        core->configuration[0xb5] = 0;
        core->configuration[0xb6] = 0;
        if (piVar23 == (int *)0x0) goto LAB_ram_4300ef30;
        goto LAB_ram_4300ea1e;
      }
      bVar3 = false;
      if (core->plus_enabled != 0) {
        iVar6 = piVar23[1];
        piVar23[*piVar23 * 0x103 + 2] = uVar8;
        piVar23[1] = iVar6 + 1;
      }
    }
    uVar14 = (uint)(byte)*puVar9 << 8;
  }
LAB_ram_4300e9dc:
  iVar21 = 0x14;
LAB_ram_4300e9de:
  byte_align(puVar30);
  uVar11 = core->frame_number;
  if (uVar11 == 0) {
    core->channels = 0;
    core->configuration[0xb3] = 0;
    core->configuration[0xb4] = 0;
    core->configuration[0xb5] = 0;
    core->configuration[0xb6] = 0;
    core->configuration[0xa7] = 1;
    core->configuration[0xa8] = 0;
    core->configuration[0xa9] = 0;
    core->configuration[0xaa] = 0;
  }
  if (bVar3) {
LAB_ram_4300e86a:
    uVar8 = *(uint *)(core->configuration + 0x13);
    param_1[10] = uVar8 >> 3;
    param_1[0xb] = uVar8 & 7;
    core->frame_number = uVar11 + 1;
    return iVar21;
  }
LAB_ram_4300ea02:
  if (core->plus_enabled == 0) {
    core->channels = 0;
    core->configuration[0xb3] = 0;
    core->configuration[0xb4] = 0;
    core->configuration[0xb5] = 0;
    core->configuration[0xb6] = 0;
    if (piVar23 != (int *)0x0) goto LAB_ram_4300ea1e;
    if (uVar11 == 0) {
      paStack_78 = (aac_sbr_control_abi_t *)0x0;
      paVar31 = (aac_sbr_owner_abi_t *)0x0;
      goto LAB_ram_4300ee9a;
    }
LAB_ram_4300ef30:
    paStack_78 = (aac_sbr_control_abi_t *)0x0;
    paVar31 = (aac_sbr_owner_abi_t *)0x0;
joined_r0x4300eea2:
    if (iVar21 != 0) goto LAB_ram_4300ea34;
    iVar6 = 0;
    iVar12 = iVar27 + 0x8cc;
    uVar29 = *(undefined4 *)
              (core->channel_configuration +
              *(int *)(local_48->spectrum_and_window + 0x28) * 4 + -0x4c);
    uVar8 = *(uint *)(core->configuration + 7);
    pns_left(uVar29,iVar27 + 0x8ac,iVar27 + 0x6ac,iVar27 + 0x4ac,iVar27 + 0xaf4,
             *(undefined4 *)(iVar27 + 0xcf4),*(undefined4 *)local_48->spectrum_and_window,iVar12,
             core->configuration + 0x7f);
    if (0 < *(int *)(core->stream_state + 0x10)) {
      apply_ms_synt(uVar29,iVar27 + 0x8ac,*(undefined4 *)(core->stream_state + 0xc),iVar27 + 0x6ac,
                    *(undefined4 *)local_48->spectrum_and_window,
                    *(undefined4 *)local_44[0]->spectrum_and_window,iVar12,iVar26 + 0x8cc);
    }
    uVar14 = *(uint *)(core->configuration + 0x83);
    if (0 < (int)uVar14) {
      ppaVar25 = &local_48;
      iVar28 = *(int *)(core->channel_configuration +
                       *(int *)(local_48->spectrum_and_window + 0x28) * 4 + -0x4c);
      iVar21 = *(int *)(local_48->spectrum_and_window + 4);
      iVar20 = 0;
      paVar10 = local_48;
      ppaVar22 = ppaVar25;
      if (*(int *)(iVar21 + 0xcf4) != 0) goto LAB_ram_4300ec32;
      while( true ) {
        uVar14 = *(uint *)(core->configuration + 0x83);
        iVar20 = iVar20 + 1;
        if ((int)uVar14 <= iVar20) break;
        while( true ) {
          iVar28 = *(int *)(core->channel_configuration +
                           *(int *)(ppaVar22[1]->spectrum_and_window + 0x28) * 4 + -0x4c);
          ppaVar22 = ppaVar22 + 1;
          pns_intensity_right(*(undefined4 *)(core->stream_state + 0x10),iVar28,iVar26 + 0x8ac,
                              *(undefined4 *)(core->stream_state + 0xc),iVar26 + 0x6ac,
                              iVar27 + 0x4ac,iVar26 + 0x4ac,iVar26 + 0xaf4,
                              *(undefined4 *)(iVar26 + 0xcf4),
                              *(undefined4 *)local_48->spectrum_and_window,
                              *(undefined4 *)local_44[0]->spectrum_and_window,iVar12,iVar26 + 0x8cc,
                              core->configuration + 0x7f);
          paVar10 = *ppaVar22;
          iVar21 = *(int *)(paVar10->spectrum_and_window + 4);
          if (*(int *)(iVar21 + 0xcf4) == 0) break;
LAB_ram_4300ec32:
          uStack_4c = long_term_prediction
                                (*(undefined4 *)(paVar10->spectrum_and_window + 0x28),
                                 *(undefined4 *)(iVar21 + 0xad0),iVar21 + 0xcf8,paVar10,
                                 *(undefined4 *)(core->channel_configuration + 0x28),
                                 paVar10->overlap,*(undefined4 *)(core->stream_state + 0x18),uVar8);
          paVar10 = *ppaVar22;
          iVar20 = iVar20 + 1;
          trans4m_time_2_freq_fxp
                    (*(undefined4 *)(core->stream_state + 0x18),
                     *(undefined4 *)(paVar10->spectrum_and_window + 0x28),
                     *(undefined4 *)(paVar10->spectrum_and_window + 0x2c),
                     *(undefined4 *)(paVar10->spectrum_and_window + 0x30),&uStack_4c,
                     *(undefined4 *)(core->stream_state + 0x14));
          apply_tns(*(undefined4 *)(core->stream_state + 0x18),
                    *(int *)((*ppaVar22)->spectrum_and_window + 4) + 0x8cc,iVar28,
                    *(int *)((*ppaVar22)->spectrum_and_window + 4),1,
                    *(undefined4 *)(core->stream_state + 0x14));
          paVar10 = *ppaVar22;
          iVar21 = *(int *)(paVar10->spectrum_and_window + 4);
          long_term_synthesis(*(undefined4 *)(paVar10->spectrum_and_window + 0x28),
                              *(undefined4 *)(iVar21 + 0xacc),*(undefined4 *)(iVar28 + 0x70),
                              iVar21 + 0xad4,iVar21 + 0xaf4,
                              *(undefined4 *)paVar10->spectrum_and_window,iVar21 + 0x8cc,
                              *(undefined4 *)(core->stream_state + 0x18),uStack_4c,
                              *(undefined4 *)(iVar28 + 0x10),8,8);
          uVar14 = *(uint *)(core->configuration + 0x83);
          if ((int)uVar14 <= iVar20) goto LAB_ram_4300ed06;
        }
      }
LAB_ram_4300ed06:
      if (0 < (int)uVar14) {
        iVar26 = 0;
        do {
          paVar10 = *ppaVar25;
          uVar29 = *(undefined4 *)
                    (core->channel_configuration +
                    *(int *)(paVar10->spectrum_and_window + 0x28) * 4 + -0x4c);
          apply_tns(*(undefined4 *)paVar10->spectrum_and_window,
                    *(int *)(paVar10->spectrum_and_window + 4) + 0x8cc,uVar29,
                    *(int *)(paVar10->spectrum_and_window + 4),0,
                    *(undefined4 *)(core->stream_state + 0x14));
          paVar10 = *ppaVar25;
          uVar29 = q_normalize(*(int *)(paVar10->spectrum_and_window + 4) + 0x8cc,uVar29,
                               paVar10->spectrum_and_window + 8,
                               *(undefined4 *)paVar10->spectrum_and_window);
          paVar10 = *ppaVar25;
          if ((core->plus_enabled == 0) ||
             ((*piVar23 == 0 && (*(int *)(core->configuration + 0xa7) == 1)))) {
            trans4m_freq_2_time_fxp_2
                      (*(undefined4 *)paVar10->spectrum_and_window,paVar10->overlap,
                       *(undefined4 *)(paVar10->spectrum_and_window + 0x28),
                       *(undefined4 *)(paVar10->spectrum_and_window + 0x2c),
                       *(undefined4 *)(paVar10->spectrum_and_window + 0x30),uVar29,
                       paVar10->spectrum_and_window + 8,*(undefined4 *)(core->stream_state + 0x14),
                       param_1[4] + iVar26 * 2);
          }
          else {
            trans4m_freq_2_time_fxp_1
                      (*(undefined4 *)paVar10->spectrum_and_window,paVar10->overlap,
                       paVar10->ltp_history + *(int *)(core->channel_configuration + 0x28) + 0x120,
                       *(undefined4 *)(paVar10->spectrum_and_window + 0x28),
                       *(undefined4 *)(paVar10->spectrum_and_window + 0x2c),
                       *(undefined4 *)(paVar10->spectrum_and_window + 0x30),uVar29,
                       paVar10->spectrum_and_window + 8,*(undefined4 *)(core->stream_state + 0x14));
          }
          paVar10 = *ppaVar25;
          uVar14 = *(uint *)(core->configuration + 0x83);
          iVar26 = iVar26 + 1;
          ppaVar25 = ppaVar25 + 1;
          *(undefined4 *)(paVar10->spectrum_and_window + 0x2c) =
               *(undefined4 *)(paVar10->spectrum_and_window + 0x30);
        } while (iVar26 < (int)uVar14);
      }
    }
    uVar24 = core->plus_enabled;
    if (uVar24 == 0) {
      uVar7 = param_1[9];
      param_1[0xe] = uVar14;
LAB_ram_4300ee12:
      if (uVar7 == 2) {
        if (uVar14 != 2) {
          iVar26 = *(int *)(core->configuration + 0xb3);
          uVar24 = 0;
          goto LAB_ram_4300f118;
        }
LAB_ram_4300ef4e:
        iVar27 = *(int *)(core->configuration + 0xa7);
        bVar3 = false;
        goto LAB_ram_4300ef54;
      }
      if (uVar7 == 1) {
        uVar24 = 0;
LAB_ram_4300f0e4:
        puVar15 = (undefined2 *)param_1[4];
        iVar27 = *(int *)(core->configuration + 0xa7);
        puVar18 = puVar15 + 0x800;
        puVar17 = puVar15;
        if (iVar27 == 2) {
          do {
            puVar16 = puVar17 + 2;
            *puVar15 = *puVar17;
            puVar15 = puVar15 + 1;
            puVar17 = puVar16;
          } while (puVar16 != puVar18);
          puVar18 = (undefined2 *)param_1[5];
          puVar17 = puVar18 + 0x800;
          puVar15 = puVar18;
          do {
            uVar2 = *puVar18;
            puVar18 = puVar18 + 2;
            *puVar15 = uVar2;
            puVar15 = puVar15 + 1;
          } while (puVar18 != puVar17);
        }
        else {
          do {
            puVar16 = puVar17 + 2;
            *puVar15 = *puVar17;
            puVar15 = puVar15 + 1;
            puVar17 = puVar16;
          } while (puVar16 != puVar18);
        }
      }
      else {
        if ((uVar7 != 0) || (uVar14 != 1)) goto LAB_ram_4300ef4e;
        uVar24 = 0;
LAB_ram_4300ee28:
        puVar15 = (undefined2 *)param_1[4];
        iVar27 = *(int *)(core->configuration + 0xa7);
        puVar18 = puVar15 + 0x800;
        puVar17 = puVar15;
        if (iVar27 == 2) {
          do {
            puVar16 = puVar17 + 2;
            *puVar15 = *puVar17;
            puVar15 = puVar15 + 1;
            puVar17 = puVar16;
          } while (puVar16 != puVar18);
          puVar18 = (undefined2 *)param_1[5];
          puVar17 = puVar18 + 0x800;
          puVar15 = puVar18;
          do {
            uVar2 = *puVar18;
            puVar18 = puVar18 + 2;
            *puVar15 = uVar2;
            puVar15 = puVar15 + 1;
          } while (puVar18 != puVar17);
        }
        else {
          do {
            puVar16 = puVar17 + 2;
            *puVar15 = *puVar17;
            puVar15 = puVar15 + 1;
            puVar17 = puVar16;
          } while (puVar16 != puVar18);
        }
      }
LAB_ram_4300ee4a:
      if (uVar24 != 0) goto LAB_ram_4300ee4e;
      uVar14 = core->frame_number;
      *(uint *)(core->channel_configuration + 0x28) =
           *(uint *)(core->channel_configuration + 0x28) ^ uVar8;
      if (1 < uVar14) goto LAB_ram_4300ef68;
      uVar7 = *(uint *)(samp_rate_info + *(int *)(core->configuration + 0x9f) * 0xc);
      uVar8 = *(uint *)(core->configuration + 7);
      param_1[0xc] = uVar7;
      core->configuration[0xa3] = 1;
      core->configuration[0xa4] = 0;
      core->configuration[0xa5] = 0;
      core->configuration[0xa6] = 0;
      param_1[0xf] = uVar8;
    }
    else {
      if (*(int *)(core->configuration + 0xb3) != 0) {
        if ((core->frame_number < 2) && (paStack_78->output_rate == 0)) {
          sbr_open(*(int *)(samp_rate_info + *(int *)(core->configuration + 0x9f) * 0xc),paStack_78,
                   paVar31,(uint)core->configuration[0xab]);
          uVar14 = *(uint *)(core->configuration + 0x83);
        }
        iVar26 = *(int *)(core->channel_configuration + 0x28);
        uVar5 = param_1[8];
        uVar7 = param_1[5];
        *(int32_t *)(core->configuration + 0xa7) = paVar31->channel[0].frame.header.sample_rate_mode
        ;
        iVar26 = sbr_applied(paVar31,piVar23,local_48->ltp_history + iVar26,
                             local_44[0]->ltp_history + iVar26,param_1[4],uVar7,uVar5,paStack_78,
                             core,uVar14);
        uVar1 = core->plus_enabled;
        if (iVar26 != 0) {
          iVar6 = 10;
        }
        uVar14 = *(uint *)(core->configuration + 0x83);
        uVar7 = param_1[9];
        param_1[0xe] = uVar14;
        if (uVar1 == 0) goto LAB_ram_4300ee12;
        iVar27 = core->channels;
        iVar26 = *(int *)(core->configuration + 0xb3);
        if (iVar27 != 0) {
          param_1[0xe] = uVar14 << 1;
          if (iVar26 == 0) goto LAB_ram_4300f1da;
          if (uVar7 != 2) goto joined_r0x4300f354;
          goto LAB_ram_4300f1e0;
        }
        if (iVar26 == 0) goto LAB_ram_4300f02a;
        if (uVar14 == 1) {
          if (uVar7 == 0) {
            param_1[9] = 2;
          }
          else if (uVar7 != 2) goto joined_r0x4300f354;
        }
        else {
          if (uVar7 != 2) {
joined_r0x4300f354:
            if (uVar7 != 1) goto LAB_ram_4300f03e;
            goto LAB_ram_4300f0e4;
          }
          if (uVar14 == 2) {
            iVar27 = *(int *)(core->configuration + 0xa7);
            goto LAB_ram_4300ee4e;
          }
        }
LAB_ram_4300f118:
        puVar17 = (undefined2 *)param_1[4];
        iVar27 = *(int *)(core->configuration + 0xa7);
        puVar15 = puVar17;
        if (iVar27 == 2) {
          do {
            puVar18 = puVar15 + 2;
            puVar15[1] = *puVar15;
            puVar15 = puVar18;
          } while (puVar17 + 0x800 != puVar18);
          puVar17 = (undefined2 *)param_1[5];
          puVar15 = puVar17;
          do {
            puVar18 = puVar15 + 2;
            puVar15[1] = *puVar15;
            puVar15 = puVar18;
          } while (puVar18 != puVar17 + 0x800);
        }
        else {
          do {
            puVar18 = puVar15 + 2;
            puVar15[1] = *puVar15;
            puVar15 = puVar18;
          } while (puVar18 != puVar17 + 0x800);
        }
        if (iVar26 != 0) {
          param_1[0xe] = 2;
        }
        goto LAB_ram_4300ee4a;
      }
      iVar27 = core->channels;
      param_1[0xe] = uVar14;
      uVar7 = param_1[9];
      iVar26 = 0;
      iVar6 = 0;
      if (iVar27 == 0) {
LAB_ram_4300f02a:
        if (uVar7 != 2) {
LAB_ram_4300f030:
          if (uVar7 != 1) {
            if ((uVar7 != 0) || (param_1[0xe] != 1)) goto LAB_ram_4300f03e;
            goto LAB_ram_4300ee28;
          }
          goto LAB_ram_4300f0e4;
        }
        if (param_1[0xe] != 2) goto LAB_ram_4300f118;
        iVar27 = *(int *)(core->configuration + 0xa7);
      }
      else {
        param_1[0xe] = uVar14 << 1;
        iVar6 = 0;
        iVar26 = 0;
LAB_ram_4300f1da:
        if (uVar7 != 2) goto LAB_ram_4300f030;
LAB_ram_4300f1e0:
        if (param_1[0xe] != 2) {
          if (iVar27 != 1) goto LAB_ram_4300f118;
          iVar27 = *(int *)(core->configuration + 0xa7);
          goto LAB_ram_4300ee4e;
        }
LAB_ram_4300f03e:
        iVar27 = *(int *)(core->configuration + 0xa7);
      }
LAB_ram_4300ee4e:
      if ((*piVar23 == 0) && (iVar27 == 1)) {
        bVar3 = true;
LAB_ram_4300ef54:
        uVar14 = core->frame_number;
        *(uint *)(core->channel_configuration + 0x28) =
             *(uint *)(core->channel_configuration + 0x28) ^ uVar8;
        if (uVar14 < 2) {
          uVar7 = *(uint *)(samp_rate_info + *(int *)(core->configuration + 0x9f) * 0xc);
          uVar8 = *(uint *)(core->configuration + 7);
          param_1[0xc] = uVar7;
          core->configuration[0xa3] = 1;
          core->configuration[0xa4] = 0;
          core->configuration[0xa5] = 0;
          core->configuration[0xa6] = 0;
          param_1[0xf] = uVar8;
          if (bVar3) goto LAB_ram_4300f1c0;
          goto LAB_ram_4300ef6a;
        }
      }
      else {
        uVar14 = core->frame_number;
        *(uint *)(core->channel_configuration + 0x28) =
             *(uint *)(core->channel_configuration + 0x28) ^ uVar8 + 0x120;
        if (uVar14 < 2) {
          uVar7 = *(uint *)(samp_rate_info + *(int *)(core->configuration + 0x9f) * 0xc);
          uVar8 = *(uint *)(core->configuration + 7);
          param_1[0xc] = uVar7;
          core->configuration[0xa3] = 1;
          core->configuration[0xa4] = 0;
          core->configuration[0xa5] = 0;
          core->configuration[0xa6] = 0;
          param_1[0xf] = uVar8;
LAB_ram_4300f1c0:
          if (iVar27 == 2) {
            uVar7 = uVar7 << 1;
            param_1[0xc] = uVar7;
            param_1[0xf] = uVar8 << 1;
            param_1[6] = 2;
            goto LAB_ram_4300ef6a;
          }
        }
      }
LAB_ram_4300ef68:
      uVar7 = param_1[0xc];
    }
LAB_ram_4300ef6a:
    uVar8 = *(uint *)(core->configuration + 0x13);
    core->frame_number = uVar14 + 1;
    iVar21 = 0;
    param_1[0xd] = (int)((uVar8 - uVar19) * uVar7 >> 10) >> (iVar27 - 1U & 0x1f);
    if (iVar6 == 0) goto LAB_ram_4300ea50;
    iVar26 = *(int *)(core->configuration + 0x23);
    iVar21 = 10;
    iVar27 = *(int *)(iVar26 + 0x348);
  }
  else {
LAB_ram_4300ea0a:
    if (*piVar23 == 0) {
      core->plus_enabled = 0;
      core->channels = 0;
      core->configuration[0xb3] = 0;
      core->configuration[0xb4] = 0;
      core->configuration[0xb5] = 0;
      core->configuration[0xb6] = 0;
LAB_ram_4300ea1e:
      *piVar23 = 0;
      paStack_78 = (aac_sbr_control_abi_t *)0x0;
      paVar31 = (aac_sbr_owner_abi_t *)0x0;
LAB_ram_4300ea26:
      if ((uVar11 == 0) && (*(int *)(core->configuration + 0xb3) == 0)) {
LAB_ram_4300ee9a:
        param_1[7] = 0;
        core->plus_enabled = 0;
      }
      goto joined_r0x4300eea2;
    }
    if (core->sbr == (aac_sbr_owner_abi_t *)0x0) {
      paVar31 = (aac_sbr_owner_abi_t *)media_lib_module_calloc("AUD_Codec",1,0xd758);
      core->sbr = paVar31;
      if (paVar31 != (aac_sbr_owner_abi_t *)0x0) {
        if (core->sbr_control == (aac_sbr_control_abi_t *)0x0) goto LAB_ram_4300f150;
        goto LAB_ram_4300f172;
      }
LAB_ram_4300f418:
      core->plus_enabled = 0;
      puts("Disable AAC-Plus for memory not enough, decode continue");
      if (core->plus_enabled != 0) goto LAB_ram_4300efd8;
LAB_ram_4300f184:
      uVar11 = core->frame_number;
      core->channels = 0;
      core->configuration[0xb3] = 0;
      core->configuration[0xb4] = 0;
      core->configuration[0xb5] = 0;
      core->configuration[0xb6] = 0;
      goto LAB_ram_4300ea1e;
    }
    if (core->sbr_control == (aac_sbr_control_abi_t *)0x0) {
LAB_ram_4300f150:
      paVar4 = (aac_sbr_control_abi_t *)media_lib_module_calloc("AUD_Codec",1,0x49c);
      core->sbr_control = paVar4;
      if (paVar4 == (aac_sbr_control_abi_t *)0x0) goto LAB_ram_4300f418;
      paVar31 = core->sbr;
LAB_ram_4300f172:
      uVar24 = core->plus_enabled;
      paVar31->initialize_ps = 1;
      if (uVar24 == 0) goto LAB_ram_4300f184;
    }
LAB_ram_4300efd8:
    if (param_1[5] == 0) {
      return 0x28;
    }
    paVar31 = core->sbr;
    paStack_78 = core->sbr_control;
    iVar6 = *piVar23;
    paVar31->ps = &paVar31->embedded_ps;
    if (iVar6 == 0) {
      uVar11 = core->frame_number;
      goto LAB_ram_4300ea26;
    }
    if (iVar6 == piVar23[1]) {
      core->configuration[0xb3] = 1;
      core->configuration[0xb4] = 0;
      core->configuration[0xb5] = 0;
      core->configuration[0xb6] = 0;
      goto joined_r0x4300eea2;
    }
    core->configuration[0xb3] = 1;
    core->configuration[0xb4] = 0;
    core->configuration[0xb5] = 0;
    core->configuration[0xb6] = 0;
    iVar21 = 10;
LAB_ram_4300ea34:
    iVar26 = *(int *)(core->configuration + 0x23);
    uVar8 = *(uint *)(core->configuration + 0x13);
    iVar27 = *(int *)(iVar26 + 0x348);
  }
  if (iVar27 == 2) {
    *(undefined4 *)(iVar26 + 0x34c) = 0;
    iVar21 = 0x1e;
  }
  else {
    uVar14 = *(uint *)(core->configuration + 0x17);
    if (uVar14 < uVar8) {
      *(uint *)(core->configuration + 0x13) = uVar14;
      iVar21 = 0x14;
      uVar8 = uVar14;
    }
  }
LAB_ram_4300ea50:
  param_1[10] = uVar8 >> 3;
  param_1[0xb] = uVar8 & 7;
  return iVar21;
}
