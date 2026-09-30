/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: PVMP4AudioDecodeFrame @ ram:42026dd4
 * Types and parameter counts are inferred; verify against disassembly. */

int PVMP4AudioDecodeFrame(uint *param_1,uint *param_2)

{
  undefined2 uVar1;
  bool bVar2;
  undefined4 uVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  ushort *puVar7;
  uint *puVar8;
  uint uVar9;
  byte *pbVar10;
  uint uVar11;
  undefined2 *puVar12;
  undefined2 *puVar13;
  undefined2 *puVar14;
  undefined2 *puVar15;
  uint uVar16;
  int iVar17;
  int iVar18;
  uint **ppuVar19;
  int *piVar20;
  char cVar21;
  uint **ppuVar22;
  uint uVar23;
  uint uVar24;
  int *piStack_78;
  undefined4 uStack_4c;
  uint *local_48;
  uint *local_44 [4];

  gp = &__global_pointer_;
  uVar24 = param_2[0x95d];
  local_44[0] = param_2 + 0x969;
  local_48 = param_2 + 0x3c;
  uVar23 = param_2[0x128a];
  uVar11 = param_1[1];
  uVar6 = *param_1;
  uVar16 = param_1[10] * 8 + param_1[0xb];
  if (param_1[7] == 0) {
    param_2[7] = uVar16;
    param_2[6] = uVar6;
    param_2[9] = uVar11;
    param_2[8] = uVar11 << 3;
    if (uVar11 << 3 < uVar16) {
      byte_align(param_2 + 6);
      uVar6 = *param_2;
      iVar18 = 10;
      if (uVar6 == 0) {
        param_2[0x30] = 0;
        param_2[0x2f] = 0;
        param_2[0x2c] = 1;
        iVar18 = 10;
      }
      goto LAB_ram_42026e54;
    }
    uVar9 = param_2[0xb];
    iVar5 = *(int *)(uVar9 + 0x348);
    if (iVar5 == 0) {
      piVar20 = (int *)0x0;
      goto LAB_ram_42026f1a;
    }
    piVar20 = (int *)0x0;
LAB_ram_42026eba:
    if (*param_2 == 0) {
      iVar18 = get_adif_header(param_2,param_2[0x229d]);
      byte_align(param_2 + 6);
      uVar9 = param_2[0xb];
      if (iVar18 != 0) {
        *(undefined4 *)(uVar9 + 0x348) = 2;
        goto LAB_ram_42026ed8;
      }
      *(undefined4 *)(uVar9 + 0x348) = 1;
LAB_ram_420275ea:
      byte_align(param_2 + 6);
      if (param_1[7] != 0) {
        *piVar20 = 0;
        piVar20[1] = 0;
      }
    }
    else {
      if ((*param_2 == 1) && (iVar5 == 1)) {
        uVar11 = uVar11 - (uVar16 >> 3);
        pbVar10 = (byte *)((uVar16 >> 3) + uVar6);
        if (uVar11 < 4) {
          if (uVar11 == 2) {
            uVar6 = 0;
LAB_ram_42027a3e:
            uVar6 = (uint)pbVar10[1] << 0x10 | uVar6;
LAB_ram_420279ee:
            uVar6 = (uint)*pbVar10 << 0x18 | uVar6;
            goto LAB_ram_4202792e;
          }
          if (uVar11 == 3) {
            uVar6 = (uint)pbVar10[2] << 8;
            goto LAB_ram_42027a3e;
          }
          if (uVar11 == 1) {
            uVar6 = 0;
            goto LAB_ram_420279ee;
          }
        }
        else {
          uVar6 = (uint)*pbVar10 << 0x18 | (uint)pbVar10[1] << 0x10 | (uint)pbVar10[3] |
                  (uint)pbVar10[2] << 8;
LAB_ram_4202792e:
          param_2[7] = uVar16 + 3;
          if ((uVar6 << (uVar16 & 7)) >> 0x1d == 7) {
            byte_align(param_2 + 6);
            uVar11 = param_2[7];
            uVar6 = *param_2;
            param_1[0xb] = uVar11 & 7;
            param_1[10] = uVar11 >> 3;
            *param_2 = uVar6 + 1;
            return 0;
          }
        }
        param_2[7] = uVar16;
        goto LAB_ram_420275ea;
      }
      iVar18 = 0;
      if (iVar5 != 2) goto LAB_ram_420275ea;
LAB_ram_42026ed8:
      if (*(int *)(uVar9 + 0x34c) == 0) {
        iVar5 = get_adts_header(param_2,param_2 + 0x2299,param_2 + 0x229a,3);
        if (iVar5 == 0) {
          uVar9 = param_2[7];
          uVar6 = param_2[6];
          uVar11 = param_2[9];
          uVar4 = param_2[8];
          if (param_1[7] != 0) {
            *piVar20 = 0;
            piVar20[1] = 0;
          }
          goto LAB_ram_42026f20;
        }
        if (param_1[7] != 0) {
          *piVar20 = 0;
          piVar20[1] = 0;
        }
        iVar18 = 0x1e;
LAB_ram_42026e46:
        byte_align(param_2 + 6);
        uVar6 = *param_2;
        if (uVar6 == 0) {
          param_2[0x30] = 0;
          param_2[0x2f] = 0;
          param_2[0x2c] = 1;
        }
        goto LAB_ram_42026e54;
      }
      uVar6 = param_1[7];
      *(int *)(uVar9 + 0x34c) = *(int *)(uVar9 + 0x34c) + -1;
      if (uVar6 != 0) {
        *piVar20 = 0;
        piVar20[1] = 0;
      }
      if (iVar18 != 0) goto LAB_ram_42026e46;
    }
    uVar9 = param_2[7];
    uVar6 = param_2[6];
    uVar11 = param_2[9];
    uVar4 = param_2[8];
  }
  else {
    piVar20 = (int *)param_2[0x2298];
    param_2[7] = uVar16;
    param_2[6] = uVar6;
    param_2[9] = uVar11;
    param_2[8] = uVar11 << 3;
    if (uVar11 << 3 < uVar16) {
      *piVar20 = 0;
      piVar20[1] = 0;
      iVar18 = 10;
      goto LAB_ram_42026e46;
    }
    uVar9 = param_2[0xb];
    iVar5 = *(int *)(uVar9 + 0x348);
    if (iVar5 != 0) goto LAB_ram_42026eba;
    *piVar20 = 0;
    piVar20[1] = 0;
LAB_ram_42026f1a:
    uVar4 = uVar11 << 3;
    uVar9 = uVar16;
  }
LAB_ram_42026f20:
  puVar8 = param_2 + 6;
  bVar2 = true;
  uVar11 = uVar11 - (uVar9 >> 3);
  puVar7 = (ushort *)(uVar6 + (uVar9 >> 3));
  uVar6 = uVar9 + 3;
  if (uVar11 < 2) goto LAB_ram_42026fb4;
LAB_ram_42026f3a:
  uVar11 = (uint)(*puVar7 >> 8) + (uint)*puVar7 * 0x100 & 0xffff;
  while (param_2[7] = uVar6, uVar6 <= uVar4) {
    uVar11 = uVar11 << (uVar9 & 7);
    uVar6 = uVar11 >> 0xd & 7;
    if (uVar6 == 5) {
      if (*param_2 < 2) {
        iVar18 = get_prog_config(param_2,param_2[0x229d]);
        if (iVar18 == 0) goto LAB_ram_42026f9c;
      }
      else {
        iVar18 = 10;
      }
      goto LAB_ram_42026fc0;
    }
    if (uVar6 < 6) {
      if ((uVar11 >> 0xe & 3) == 0) goto LAB_ram_42027044;
      if (uVar6 == 4) {
        get_dse(param_2[0x229e],puVar8);
        goto LAB_ram_42026f9c;
      }
      iVar18 = -1;
      goto LAB_ram_42026fc0;
    }
    if (uVar6 != 6) {
      iVar18 = 0;
      goto LAB_ram_42026fc0;
    }
    if (((char)param_2[2] == '\0') || (24000 < *(int *)(samp_rate_info + param_2[0x2a] * 0xc))) {
      getfill(puVar8);
    }
    else {
      get_sbr_bitstream(piVar20,puVar8);
    }
LAB_ram_42026f9c:
    while( true ) {
      uVar9 = param_2[7];
      uVar11 = param_2[9] - (uVar9 >> 3);
      puVar7 = (ushort *)(param_2[6] + (uVar9 >> 3));
      uVar4 = param_2[8];
      uVar6 = uVar9 + 3;
      if (1 < uVar11) goto LAB_ram_42026f3a;
LAB_ram_42026fb4:
      if (uVar11 == 1) break;
      param_2[7] = uVar6;
      if (uVar4 < uVar6) goto LAB_ram_42026fbe;
      uVar6 = 0;
LAB_ram_42027044:
      iVar18 = huffdecode(uVar6,puVar8,param_2,&local_48);
      if (iVar18 != 0) {
        byte_align(puVar8);
        uVar6 = *param_2;
        if (uVar6 == 0) {
          param_2[0x30] = 0;
          param_2[0x2f] = 0;
          param_2[0x2c] = 1;
          goto LAB_ram_42026fe0;
        }
        if ((char)param_2[2] != '\0') goto LAB_ram_42026fe8;
        param_2[0x30] = 0;
        param_2[0x2f] = 0;
        if (piVar20 == (int *)0x0) goto LAB_ram_420274d2;
        goto LAB_ram_42026ffc;
      }
      bVar2 = false;
      if ((char)param_2[2] != '\0') {
        iVar5 = piVar20[1];
        piVar20[*piVar20 * 0x103 + 2] = uVar6;
        piVar20[1] = iVar5 + 1;
      }
    }
    uVar11 = (uint)(byte)*puVar7 << 8;
  }
LAB_ram_42026fbe:
  iVar18 = 0x14;
LAB_ram_42026fc0:
  byte_align(puVar8);
  uVar6 = *param_2;
  if (uVar6 == 0) {
    param_2[0x30] = 0;
    param_2[0x2f] = 0;
    param_2[0x2c] = 1;
  }
  if (bVar2) {
LAB_ram_42026e54:
    uVar11 = param_2[7];
    param_1[10] = uVar11 >> 3;
    param_1[0xb] = uVar11 & 7;
    *param_2 = uVar6 + 1;
    return iVar18;
  }
LAB_ram_42026fe0:
  if ((char)param_2[2] == '\0') {
    param_2[0x30] = 0;
    param_2[0x2f] = 0;
    if (piVar20 != (int *)0x0) goto LAB_ram_42026ffc;
    if (uVar6 == 0) {
      piStack_78 = (int *)0x0;
      uVar11 = 0;
      goto LAB_ram_4202744c;
    }
LAB_ram_420274d2:
    piStack_78 = (int *)0x0;
    uVar11 = 0;
joined_r0x42027454:
    if (iVar18 != 0) goto LAB_ram_42027012;
    iVar5 = 0;
    iVar18 = uVar24 + 0x8cc;
    uVar9 = param_2[local_48[0x92a] + 0x1e];
    uVar6 = param_2[4];
    pns_left(uVar9,uVar24 + 0x8ac,uVar24 + 0x6ac,uVar24 + 0x4ac,uVar24 + 0xaf4,
             *(undefined4 *)(uVar24 + 0xcf4),local_48[0x920],iVar18,param_2 + 0x22);
    if (0 < (int)param_2[0x229c]) {
      apply_ms_synt(uVar9,uVar24 + 0x8ac,param_2[0x229b],uVar24 + 0x6ac,local_48[0x920],
                    local_44[0][0x920],iVar18,uVar23 + 0x8cc);
    }
    uVar9 = param_2[0x23];
    if (0 < (int)uVar9) {
      ppuVar22 = &local_48;
      uVar4 = param_2[local_48[0x92a] + 0x1e];
      uVar9 = local_48[0x921];
      iVar17 = 0;
      puVar8 = local_48;
      ppuVar19 = ppuVar22;
      if (*(int *)(uVar9 + 0xcf4) != 0) goto LAB_ram_42027200;
      while( true ) {
        uVar9 = param_2[0x23];
        iVar17 = iVar17 + 1;
        if ((int)uVar9 <= iVar17) break;
        while( true ) {
          uVar4 = param_2[ppuVar19[1][0x92a] + 0x1e];
          ppuVar19 = ppuVar19 + 1;
          pns_intensity_right(param_2[0x229c],uVar4,uVar23 + 0x8ac,param_2[0x229b],uVar23 + 0x6ac,
                              uVar24 + 0x4ac,uVar23 + 0x4ac,uVar23 + 0xaf4,
                              *(undefined4 *)(uVar23 + 0xcf4),local_48[0x920],local_44[0][0x920],
                              iVar18,uVar23 + 0x8cc,param_2 + 0x22);
          puVar8 = *ppuVar19;
          uVar9 = puVar8[0x921];
          if (*(int *)(uVar9 + 0xcf4) == 0) break;
LAB_ram_42027200:
          uStack_4c = long_term_prediction
                                (puVar8[0x92a],*(undefined4 *)(uVar9 + 0xad0),uVar9 + 0xcf8,puVar8,
                                 param_2[0x3b],puVar8 + 0x520,param_2[0x229e],uVar6);
          puVar8 = *ppuVar19;
          iVar17 = iVar17 + 1;
          trans4m_time_2_freq_fxp
                    (param_2[0x229e],puVar8[0x92a],puVar8[0x92b],puVar8[0x92c],&uStack_4c,
                     param_2[0x229d]);
          apply_tns(param_2[0x229e],(*ppuVar19)[0x921] + 0x8cc,uVar4,(*ppuVar19)[0x921],1,
                    param_2[0x229d]);
          puVar8 = *ppuVar19;
          uVar9 = puVar8[0x921];
          long_term_synthesis(puVar8[0x92a],*(undefined4 *)(uVar9 + 0xacc),
                              *(undefined4 *)(uVar4 + 0x70),uVar9 + 0xad4,uVar9 + 0xaf4,
                              puVar8[0x920],uVar9 + 0x8cc,param_2[0x229e],uStack_4c,
                              *(undefined4 *)(uVar4 + 0x10),8,8);
          uVar9 = param_2[0x23];
          if ((int)uVar9 <= iVar17) goto LAB_ram_420272c4;
        }
      }
LAB_ram_420272c4:
      if (0 < (int)uVar9) {
        iVar18 = 0;
        do {
          puVar8 = *ppuVar22;
          uVar23 = param_2[puVar8[0x92a] + 0x1e];
          apply_tns(puVar8[0x920],puVar8[0x921] + 0x8cc,uVar23,puVar8[0x921],0,param_2[0x229d]);
          puVar8 = *ppuVar22;
          uVar3 = q_normalize(puVar8[0x921] + 0x8cc,uVar23,puVar8 + 0x922,puVar8[0x920]);
          puVar8 = *ppuVar22;
          if (((char)param_2[2] == '\0') || ((*piVar20 == 0 && (param_2[0x2c] == 1)))) {
            trans4m_freq_2_time_fxp_2
                      (puVar8[0x920],puVar8 + 0x520,puVar8[0x92a],puVar8[0x92b],puVar8[0x92c],uVar3,
                       puVar8 + 0x922,param_2[0x229d],param_1[4] + iVar18 * 2);
          }
          else {
            trans4m_freq_2_time_fxp_1
                      (puVar8[0x920],puVar8 + 0x520,(param_2[0x3b] + 0x120) * 2 + (int)puVar8,
                       puVar8[0x92a],puVar8[0x92b],puVar8[0x92c],uVar3,puVar8 + 0x922,
                       param_2[0x229d]);
          }
          puVar8 = *ppuVar22;
          uVar9 = param_2[0x23];
          iVar18 = iVar18 + 1;
          ppuVar22 = ppuVar22 + 1;
          puVar8[0x92b] = puVar8[0x92c];
        } while (iVar18 < (int)uVar9);
      }
    }
    cVar21 = (char)param_2[2];
    if (cVar21 == '\0') {
      uVar23 = param_1[9];
      param_1[0xe] = uVar9;
LAB_ram_420273c4:
      if (uVar23 == 2) {
        if (uVar9 != 2) {
          uVar11 = param_2[0x2f];
          cVar21 = '\0';
          goto LAB_ram_420276aa;
        }
LAB_ram_420274ec:
        uVar23 = param_2[0x2c];
        bVar2 = false;
        goto LAB_ram_420274f2;
      }
      if (uVar23 == 1) {
        cVar21 = '\0';
LAB_ram_42027676:
        puVar12 = (undefined2 *)param_1[4];
        uVar23 = param_2[0x2c];
        puVar15 = puVar12 + 0x800;
        puVar14 = puVar12;
        if (uVar23 == 2) {
          do {
            puVar13 = puVar14 + 2;
            *puVar12 = *puVar14;
            puVar12 = puVar12 + 1;
            puVar14 = puVar13;
          } while (puVar13 != puVar15);
          puVar15 = (undefined2 *)param_1[5];
          puVar14 = puVar15 + 0x800;
          puVar12 = puVar15;
          do {
            uVar1 = *puVar15;
            puVar15 = puVar15 + 2;
            *puVar12 = uVar1;
            puVar12 = puVar12 + 1;
          } while (puVar15 != puVar14);
        }
        else {
          do {
            puVar13 = puVar14 + 2;
            *puVar12 = *puVar14;
            puVar12 = puVar12 + 1;
            puVar14 = puVar13;
          } while (puVar13 != puVar15);
        }
      }
      else {
        if ((uVar23 != 0) || (uVar9 != 1)) goto LAB_ram_420274ec;
        cVar21 = '\0';
LAB_ram_420273da:
        puVar12 = (undefined2 *)param_1[4];
        uVar23 = param_2[0x2c];
        puVar15 = puVar12 + 0x800;
        puVar14 = puVar12;
        if (uVar23 == 2) {
          do {
            puVar13 = puVar14 + 2;
            *puVar12 = *puVar14;
            puVar12 = puVar12 + 1;
            puVar14 = puVar13;
          } while (puVar13 != puVar15);
          puVar15 = (undefined2 *)param_1[5];
          puVar14 = puVar15 + 0x800;
          puVar12 = puVar15;
          do {
            uVar1 = *puVar15;
            puVar15 = puVar15 + 2;
            *puVar12 = uVar1;
            puVar12 = puVar12 + 1;
          } while (puVar15 != puVar14);
        }
        else {
          do {
            puVar13 = puVar14 + 2;
            *puVar12 = *puVar14;
            puVar12 = puVar12 + 1;
            puVar14 = puVar13;
          } while (puVar13 != puVar15);
        }
      }
LAB_ram_420273fc:
      if (cVar21 != '\0') goto LAB_ram_42027400;
      uVar11 = *param_2;
      param_2[0x3b] = param_2[0x3b] ^ uVar6;
      if (1 < uVar11) goto LAB_ram_42027506;
      uVar24 = *(uint *)(samp_rate_info + param_2[0x2a] * 0xc);
      uVar6 = param_2[4];
      param_1[0xc] = uVar24;
      param_2[0x2b] = 1;
      param_1[0xf] = uVar6;
    }
    else {
      if (param_2[0x2f] != 0) {
        if ((*param_2 < 2) && (*piStack_78 == 0)) {
          sbr_open(*(undefined4 *)(samp_rate_info + param_2[0x2a] * 0xc),piStack_78,uVar11,
                   (char)param_2[0x2d]);
          uVar9 = param_2[0x23];
        }
        uVar24 = param_1[8];
        uVar23 = param_1[5];
        param_2[0x2c] = *(uint *)(uVar11 + 0xd4);
        iVar18 = sbr_applied(uVar11,piVar20,param_2[0x3b] * 2 + (int)local_48,
                             (int)local_44[0] + param_2[0x3b] * 2,param_1[4],uVar23,uVar24,
                             piStack_78,param_2,uVar9);
        uVar11 = param_2[2];
        if (iVar18 != 0) {
          iVar5 = 10;
        }
        uVar9 = param_2[0x23];
        uVar23 = param_1[9];
        param_1[0xe] = uVar9;
        if ((char)uVar11 == '\0') goto LAB_ram_420273c4;
        uVar24 = param_2[0x30];
        uVar11 = param_2[0x2f];
        if (uVar24 != 0) {
          param_1[0xe] = uVar9 << 1;
          if (uVar11 == 0) goto LAB_ram_42027768;
          if (uVar23 != 2) goto joined_r0x420278d6;
          goto LAB_ram_4202776e;
        }
        if (uVar11 == 0) goto LAB_ram_420275c4;
        if (uVar9 == 1) {
          if (uVar23 == 0) {
            param_1[9] = 2;
          }
          else if (uVar23 != 2) goto joined_r0x420278d6;
        }
        else {
          if (uVar23 != 2) {
joined_r0x420278d6:
            if (uVar23 != 1) goto LAB_ram_420275d8;
            goto LAB_ram_42027676;
          }
          if (uVar9 == 2) {
            uVar23 = param_2[0x2c];
            goto LAB_ram_42027400;
          }
        }
LAB_ram_420276aa:
        puVar14 = (undefined2 *)param_1[4];
        uVar23 = param_2[0x2c];
        puVar12 = puVar14;
        if (uVar23 == 2) {
          do {
            puVar15 = puVar12 + 2;
            puVar12[1] = *puVar12;
            puVar12 = puVar15;
          } while (puVar14 + 0x800 != puVar15);
          puVar14 = (undefined2 *)param_1[5];
          puVar12 = puVar14;
          do {
            puVar15 = puVar12 + 2;
            puVar12[1] = *puVar12;
            puVar12 = puVar15;
          } while (puVar15 != puVar14 + 0x800);
        }
        else {
          do {
            puVar15 = puVar12 + 2;
            puVar12[1] = *puVar12;
            puVar12 = puVar15;
          } while (puVar15 != puVar14 + 0x800);
        }
        if (uVar11 != 0) {
          param_1[0xe] = 2;
        }
        goto LAB_ram_420273fc;
      }
      uVar24 = param_2[0x30];
      param_1[0xe] = uVar9;
      uVar23 = param_1[9];
      uVar11 = 0;
      iVar5 = 0;
      if (uVar24 == 0) {
LAB_ram_420275c4:
        if (uVar23 != 2) {
LAB_ram_420275ca:
          if (uVar23 != 1) {
            if ((uVar23 != 0) || (param_1[0xe] != 1)) goto LAB_ram_420275d8;
            goto LAB_ram_420273da;
          }
          goto LAB_ram_42027676;
        }
        if (param_1[0xe] != 2) goto LAB_ram_420276aa;
        uVar23 = param_2[0x2c];
      }
      else {
        param_1[0xe] = uVar9 << 1;
        iVar5 = 0;
        uVar11 = 0;
LAB_ram_42027768:
        if (uVar23 != 2) goto LAB_ram_420275ca;
LAB_ram_4202776e:
        if (param_1[0xe] != 2) {
          if (uVar24 != 1) goto LAB_ram_420276aa;
          uVar23 = param_2[0x2c];
          goto LAB_ram_42027400;
        }
LAB_ram_420275d8:
        uVar23 = param_2[0x2c];
      }
LAB_ram_42027400:
      if ((*piVar20 == 0) && (uVar23 == 1)) {
        bVar2 = true;
LAB_ram_420274f2:
        uVar11 = *param_2;
        param_2[0x3b] = param_2[0x3b] ^ uVar6;
        if (uVar11 < 2) {
          uVar24 = *(uint *)(samp_rate_info + param_2[0x2a] * 0xc);
          uVar6 = param_2[4];
          param_1[0xc] = uVar24;
          param_2[0x2b] = 1;
          param_1[0xf] = uVar6;
          if (bVar2) goto LAB_ram_4202774e;
          goto LAB_ram_42027508;
        }
      }
      else {
        uVar11 = *param_2;
        param_2[0x3b] = param_2[0x3b] ^ uVar6 + 0x120;
        if (uVar11 < 2) {
          uVar24 = *(uint *)(samp_rate_info + param_2[0x2a] * 0xc);
          uVar6 = param_2[4];
          param_1[0xc] = uVar24;
          param_2[0x2b] = 1;
          param_1[0xf] = uVar6;
LAB_ram_4202774e:
          if (uVar23 == 2) {
            uVar24 = uVar24 << 1;
            param_1[0xc] = uVar24;
            param_1[0xf] = uVar6 << 1;
            param_1[6] = 2;
            goto LAB_ram_42027508;
          }
        }
      }
LAB_ram_42027506:
      uVar24 = param_1[0xc];
    }
LAB_ram_42027508:
    uVar6 = param_2[7];
    *param_2 = uVar11 + 1;
    iVar18 = 0;
    param_1[0xd] = (int)((uVar6 - uVar16) * uVar24 >> 10) >> (uVar23 - 1 & 0x1f);
    if (iVar5 == 0) goto LAB_ram_4202702e;
    uVar11 = param_2[0xb];
    iVar18 = 10;
    iVar5 = *(int *)(uVar11 + 0x348);
  }
  else {
LAB_ram_42026fe8:
    if (*piVar20 == 0) {
      *(undefined1 *)(param_2 + 2) = 0;
      param_2[0x30] = 0;
      param_2[0x2f] = 0;
LAB_ram_42026ffc:
      *piVar20 = 0;
      piStack_78 = (int *)0x0;
      uVar11 = 0;
LAB_ram_42027004:
      if ((uVar6 == 0) && (param_2[0x2f] == 0)) {
LAB_ram_4202744c:
        param_1[7] = 0;
        *(undefined1 *)(param_2 + 2) = 0;
      }
      goto joined_r0x42027454;
    }
    if (param_2[0x2296] == 0) {
      uVar6 = media_lib_module_calloc("AUD_Codec",1,0xd758);
      param_2[0x2296] = uVar6;
      if (uVar6 != 0) {
        if (param_2[0x2297] == 0) goto LAB_ram_420276e2;
        goto LAB_ram_42027700;
      }
LAB_ram_42027996:
      *(undefined1 *)(param_2 + 2) = 0;
      puts("Disable AAC-Plus for memory not enough, decode continue");
      if ((char)param_2[2] != '\0') goto LAB_ram_42027572;
LAB_ram_42027712:
      uVar6 = *param_2;
      param_2[0x30] = 0;
      param_2[0x2f] = 0;
      goto LAB_ram_42026ffc;
    }
    if (param_2[0x2297] == 0) {
LAB_ram_420276e2:
      uVar6 = media_lib_module_calloc("AUD_Codec",1,0x49c);
      param_2[0x2297] = uVar6;
      if (uVar6 == 0) goto LAB_ram_42027996;
      uVar6 = param_2[0x2296];
LAB_ram_42027700:
      uVar11 = param_2[2];
      *(undefined4 *)(uVar6 + 0xc980) = 1;
      if ((char)uVar11 == '\0') goto LAB_ram_42027712;
    }
LAB_ram_42027572:
    if (param_1[5] == 0) {
      return 0x28;
    }
    uVar11 = param_2[0x2296];
    piStack_78 = (int *)param_2[0x2297];
    iVar5 = *piVar20;
    *(uint *)(uVar11 + 0xc984) = uVar11 + 0xc988;
    if (iVar5 == 0) {
      uVar6 = *param_2;
      goto LAB_ram_42027004;
    }
    if (iVar5 == piVar20[1]) {
      param_2[0x2f] = 1;
      goto joined_r0x42027454;
    }
    param_2[0x2f] = 1;
    iVar18 = 10;
LAB_ram_42027012:
    uVar11 = param_2[0xb];
    uVar6 = param_2[7];
    iVar5 = *(int *)(uVar11 + 0x348);
  }
  if (iVar5 == 2) {
    *(undefined4 *)(uVar11 + 0x34c) = 0;
    iVar18 = 0x1e;
  }
  else {
    uVar11 = param_2[8];
    if (uVar11 < uVar6) {
      param_2[7] = uVar11;
      iVar18 = 0x14;
      uVar6 = uVar11;
    }
  }
LAB_ram_4202702e:
  param_1[10] = uVar6 >> 3;
  param_1[0xb] = uVar6 & 7;
  return iVar18;
}
