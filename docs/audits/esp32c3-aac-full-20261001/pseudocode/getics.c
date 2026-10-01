/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: getics @ ram:43008a78
 * Types and parameter counts are inferred; verify against disassembly. */

int getics(int *param_1,int param_2,int param_3,int param_4,int *param_5,int *param_6,uint *param_7,
          uint *param_8,undefined4 *param_9,uint *param_10,uint *param_11)

{
  byte bVar1;
  short sVar2;
  ushort uVar3;
  uint uVar4;
  int *piVar5;
  int iVar6;
  uint *puVar7;
  uint uVar8;
  int *piVar9;
  int iVar10;
  undefined4 uVar11;
  int iVar12;
  int iVar13;
  uint uVar14;
  uint *puVar15;
  int iVar16;
  int iVar17;
  int iVar18;
  int *piVar19;
  int iVar20;
  int *piVar21;
  uint uVar22;
  code *pcVar23;
  int iVar24;
  code *pcVar25;
  uint uVar26;
  ushort *puVar27;
  undefined4 uVar28;
  int iStackY_78;
  int *piVar29;
  int *apiStack_44 [4];

  gp = &__global_pointer_;
  uVar8 = param_1[1];
  uVar4 = param_1[3] - (uVar8 >> 3);
  puVar27 = (ushort *)(*param_1 + (uVar8 >> 3));
  if (uVar4 < 2) {
    uVar14 = 0;
    if (uVar4 != 1) goto LAB_ram_43008ade;
    uVar3 = *puVar27;
    param_1[1] = uVar8 + 8;
    uVar14 = (((uint)(byte)uVar3 << 8) << (uVar8 & 7)) >> 8 & 0xff;
    if (param_2 != 0) goto LAB_ram_43008aea;
LAB_ram_43008bf8:
    apiStack_44[0] = param_6;
    iVar10 = get_ics_info(param_1,param_2,param_4 + 0x24a8,param_4 + 0x24b0,param_5,param_6,param_9,
                          *(int *)(param_4 + 0x2484) + 0xad0,0);
    piVar21 = (int *)param_9[*(int *)(param_4 + 0x24a8)];
    if (*apiStack_44[0] < 1) goto LAB_ram_43008c44;
LAB_ram_43008b00:
    iVar13 = 0;
    piVar9 = param_5;
    do {
      iVar12 = *piVar9;
      piVar9 = piVar9 + 1;
      iVar13 = iVar13 + 1;
    } while (iVar12 < piVar21[1]);
    piVar9 = (int *)huffcb(param_11,param_1,piVar21 + 0x14,piVar21[0xc] * iVar13);
    if (piVar9 == (int *)0x0) {
      if (*piVar21 != 0) {
        return 1;
      }
      calc_gsfb_table(piVar21,param_5);
      return 1;
    }
    if (0 < (int)piVar9) {
      uVar4 = 0;
      puVar7 = param_11;
      do {
        uVar8 = puVar7[1];
        iVar13 = uVar8 - uVar4;
        if (0 < iVar13) {
          uVar4 = *puVar7;
          iVar12 = iVar13;
          puVar15 = param_7;
          do {
            iVar12 = iVar12 + -1;
            *puVar15 = uVar4;
            puVar15 = puVar15 + 1;
          } while (iVar12 != 0);
          param_7 = param_7 + iVar13;
        }
        puVar7 = puVar7 + 2;
        uVar4 = uVar8;
      } while (param_11 + (int)piVar9 * 2 != puVar7);
    }
    iVar13 = *piVar21;
    apiStack_44[0] = piVar9;
  }
  else {
    uVar3 = *puVar27;
    uVar14 = (((uint)(uVar3 >> 8) + (uint)uVar3 * 0x100 << (uVar8 & 7)) << 0x10) >> 0x18;
LAB_ram_43008ade:
    param_1[1] = uVar8 + 8;
    if (param_2 == 0) goto LAB_ram_43008bf8;
LAB_ram_43008aea:
    iVar10 = 0;
    piVar21 = (int *)param_9[*(int *)(param_4 + 0x24a8)];
    if (0 < *param_6) goto LAB_ram_43008b00;
LAB_ram_43008c44:
    memset(param_7,0,0x200);
    iVar13 = *piVar21;
    apiStack_44[0] = (int *)0x0;
  }
  if (iVar13 == 0) {
    calc_gsfb_table(piVar21,param_5);
  }
  if (iVar10 != 0) {
    return iVar10;
  }
  iVar10 = hufffac(piVar21,param_1,param_5,apiStack_44[0],param_11,uVar14,
                   *(int *)(param_4 + 0x2484) + 0x4ac,*(undefined4 *)(param_3 + 0x8a74));
  if (iVar10 != 0) {
    return iVar10;
  }
  uVar4 = param_1[1];
  uVar14 = param_1[3];
  iVar10 = *param_1;
  uVar8 = uVar4 + 1;
  if (uVar4 >> 3 < uVar14) {
    bVar1 = *(byte *)((uVar4 >> 3) + iVar10);
    param_1[1] = uVar8;
    uVar4 = ((uint)bVar1 << (uVar4 & 7)) >> 7 & 1;
    *param_10 = uVar4;
    if (uVar4 != 0) {
      if (*piVar21 != 1) {
        return 1;
      }
      iVar10 = get_pulse_data(param_10,param_1);
      if (iVar10 != 0) {
        return iVar10;
      }
      uVar8 = param_1[1];
      iVar10 = *param_1;
      uVar14 = param_1[3];
    }
  }
  else {
    param_1[1] = uVar8;
    *param_10 = 0;
  }
  if (uVar8 >> 3 < uVar14) {
    bVar1 = *(byte *)((uVar8 >> 3) + iVar10);
    param_1[1] = uVar8 + 1;
    uVar4 = ((uint)bVar1 << (uVar8 & 7)) >> 7 & 1;
    *param_8 = uVar4;
    if (uVar4 != 0) {
      get_tns(*(undefined4 *)(*(int *)(param_4 + 0x2484) + 0xacc),param_1,
              *(undefined4 *)(param_4 + 0x24a8),piVar21,param_3 + 0x8c,param_8,
              *(undefined4 *)(param_3 + 0x8a74));
      iVar10 = *param_1;
      uVar14 = param_1[3];
      piVar9 = apiStack_44[0];
      goto LAB_ram_43008cbe;
    }
  }
  else {
    param_1[1] = uVar8 + 1;
    *param_8 = 0;
  }
  piVar9 = apiStack_44[0];
  if (0 < piVar21[1]) {
    memset(param_8 + 1,0,piVar21[1] << 2);
    piVar9 = apiStack_44[0];
  }
LAB_ram_43008cbe:
  uVar4 = param_1[1];
  if (uVar4 >> 3 < uVar14) {
    bVar1 = *(byte *)(iVar10 + (uVar4 >> 3));
    param_1[1] = uVar4 + 1;
    if (((uint)bVar1 << (uVar4 & 7) & 0x80) != 0) {
      return 1;
    }
  }
  else {
    param_1[1] = uVar4 + 1;
  }
  iVar13 = *(int *)(param_4 + 0x2484);
  uVar28 = *param_9;
  iVar12 = *(int *)(param_4 + 0x2480);
  iVar17 = *(int *)(param_3 + 0x8a74);
  iVar10 = *(int *)(param_3 + 0x8a78);
  apiStack_44[0] = (int *)0x0;
  if ((int)piVar9 < 1) {
LAB_ram_430097d0:
    if (*piVar21 == 0) {
      deinterleave(iVar10,iVar17,piVar21);
      iVar10 = iVar17;
    }
    else if (*param_10 == 1) {
      pulse_nc(iVar10,param_10,uVar28,apiStack_44);
    }
    if (apiStack_44[0] < (int *)0x2001) {
      iVar17 = pv_normalize((int)apiStack_44[0] *
                            (*(int *)(inverseQuantTable + ((int)apiStack_44[0] >> 3) * 4 + 4) +
                             0x7ffffffU >> 0x1a));
      if (0x1b < iVar17) {
        iVar17 = 0x1b;
      }
      iStackY_78 = piVar21[1];
      if (0 < iStackY_78) {
        iVar18 = piVar21[0xc];
        iVar6 = 0;
        if (0 < iVar18) {
          do {
            iVar24 = 0;
            puVar7 = (uint *)(iVar13 + 0x4ac + iVar6 * 4);
            piVar9 = (int *)(iVar6 * 4 + iVar13 + 0x8cc);
            iVar16 = iVar18 + iVar6;
            iVar20 = 0;
            do {
              sVar2 = *(short *)(piVar21[0x1c] + iVar24);
              uVar4 = sVar2 - iVar20;
              if (0x400 < uVar4) {
                return -1;
              }
              uVar8 = *puVar7;
              *piVar9 = iVar17;
              esc_iquant_scaling(iVar10,iVar12,uVar4,iVar17,
                                 *(undefined2 *)((int)&exptable + (uVar8 & 3) * 2),apiStack_44[0]);
              iVar6 = iVar6 + 1;
              *piVar9 = *piVar9 - (((int)(uVar8 - 100) >> 2) + 1);
              iVar10 = iVar10 + uVar4 * 2;
              iVar24 = iVar24 + 2;
              puVar7 = puVar7 + 1;
              piVar9 = piVar9 + 1;
              iVar12 = iVar12 + uVar4 * 4;
              iVar20 = (int)sVar2;
            } while (iVar6 != iVar16);
            iStackY_78 = iStackY_78 + -1;
          } while (iStackY_78 != 0);
        }
      }
      return 0;
    }
  }
  else {
    uVar4 = *param_11;
    piVar5 = piVar21 + 0x25;
    iVar18 = 0;
    piVar29 = piVar5;
    uVar8 = 0;
    while ((uVar4 < 0x10 && (uVar14 = param_11[1], -1 < (int)uVar14))) {
      if ((uVar4 - 1 & 0xc) == 0xc) {
        piVar5 = piVar29 + uVar14;
        uVar4 = piVar5[-1] - iVar18;
        if (0x400 < uVar4) {
          return -1;
        }
        memset(iVar10 + iVar18 * 2,0,uVar4 * 2);
        memset(iVar17 + iVar18 * 2,0,uVar4 * 2);
        iVar18 = piVar5[-1];
      }
      else {
        if ((int)uVar4 < 5) {
          uVar22 = uVar4;
          if (*(int *)(hcbbook_binary + uVar4 * 0x14 + 0x10) == 0) {
            if (uVar4 == 3) {
              pcVar23 = unpack_idx_sgn;
              pcVar25 = decode_huff_cw_tab3;
              uVar22 = 4;
            }
            else if (uVar4 == 4) {
              pcVar23 = unpack_idx_sgn;
              pcVar25 = decode_huff_cw_tab4;
            }
            else {
              pcVar23 = unpack_idx_sgn;
LAB_ram_43009890:
              if (uVar4 == 1) {
                pcVar25 = decode_huff_cw_tab1;
                uVar22 = 4;
              }
              else {
                pcVar25 = decode_huff_cw_tab2;
                uVar22 = 4;
              }
            }
          }
          else if (uVar4 == 3) {
            uVar22 = 4;
            pcVar23 = unpack_idx;
            pcVar25 = decode_huff_cw_tab3;
          }
          else {
            pcVar23 = unpack_idx;
            if (uVar4 != 4) goto LAB_ram_43009890;
            pcVar23 = unpack_idx;
            pcVar25 = decode_huff_cw_tab4;
          }
        }
        else if (uVar4 == 0xb) {
          pcVar23 = unpack_idx_esc;
          pcVar25 = decode_huff_cw_tab11;
          uVar22 = 2;
        }
        else {
          if (*(int *)(hcbbook_binary + uVar4 * 0x14 + 0x10) == 0) {
            pcVar23 = unpack_idx_sgn;
          }
          else {
            pcVar23 = unpack_idx;
          }
          if (uVar4 == 6) {
            pcVar25 = decode_huff_cw_tab6;
            uVar22 = 2;
          }
          else if ((int)uVar4 < 7) {
            pcVar25 = decode_huff_cw_tab5;
            uVar22 = 2;
          }
          else if (uVar4 == 9) {
            pcVar25 = decode_huff_cw_tab9;
            uVar22 = 2;
          }
          else if ((int)uVar4 < 10) {
            if (uVar4 == 7) {
              pcVar25 = decode_huff_cw_tab7;
              uVar22 = 2;
            }
            else {
              pcVar25 = decode_huff_cw_tab8;
              uVar22 = 2;
            }
          }
          else {
            if (uVar4 != 10) {
              return -1;
            }
            pcVar25 = decode_huff_cw_tab10;
            uVar22 = 2;
          }
        }
        if ((int)uVar8 < (int)uVar14) {
          iVar20 = iVar18 * 2 + iVar10;
          iVar6 = iVar18;
          piVar19 = piVar5;
          uVar26 = uVar8;
          do {
            iVar18 = *piVar19;
            piVar19 = piVar19 + 1;
            for (iVar6 = iVar18 - iVar6; iVar6 - 1U < 0x3ff; iVar6 = iVar6 - uVar22) {
              uVar11 = (*pcVar25)(param_1);
              (*pcVar23)(iVar20,uVar11,hcbbook_binary + uVar4 * 0x14,param_1,apiStack_44);
              iVar20 = iVar20 + uVar22 * 2;
            }
            uVar26 = uVar26 + 1;
            iVar6 = iVar18;
          } while (uVar14 != uVar26);
          piVar5 = piVar5 + (uVar14 - uVar8);
        }
      }
      if (piVar9 == (int *)0x1) goto LAB_ram_430097d0;
      piVar9 = (int *)((int)piVar9 + -1);
      param_11 = param_11 + 2;
      uVar4 = *param_11;
      uVar8 = uVar14;
    }
  }
  return -1;
}
