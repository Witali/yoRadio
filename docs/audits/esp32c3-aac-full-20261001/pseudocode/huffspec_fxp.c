/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: huffspec_fxp @ ram:43009692
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4
huffspec_fxp(int *param_1,undefined4 param_2,int param_3,uint *param_4,int param_5,int param_6,
            int param_7,int param_8,undefined4 param_9,int *param_10,int param_11)

{
  short sVar1;
  int iVar2;
  uint *puVar3;
  undefined4 uVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  int *piVar8;
  int iVar9;
  int iVar10;
  uint uVar11;
  uint uVar12;
  code *pcVar13;
  int iVar14;
  code *pcVar15;
  uint uVar16;
  int *piVar17;
  uint uVar18;
  int iStack_78;
  uint auStack_44 [4];

  gp = &__global_pointer_;
  auStack_44[0] = 0;
  if (param_3 < 1) {
LAB_ram_430097d0:
    if (*param_1 == 0) {
      deinterleave(param_7,param_8,param_1);
      param_7 = param_8;
    }
    else if (*param_10 == 1) {
      pulse_nc(param_7,param_10,param_9,auStack_44);
    }
    if (auStack_44[0] < 0x2001) {
      iVar7 = pv_normalize(auStack_44[0] *
                           (*(int *)(inverseQuantTable + ((int)auStack_44[0] >> 3) * 4 + 4) +
                            0x7ffffffU >> 0x1a));
      if (0x1b < iVar7) {
        iVar7 = 0x1b;
      }
      iStack_78 = param_1[1];
      if (0 < iStack_78) {
        iVar2 = param_1[0xc];
        iVar10 = 0;
        if (0 < iVar2) {
          do {
            iVar14 = 0;
            puVar3 = (uint *)(param_5 + iVar10 * 4);
            piVar17 = (int *)(iVar10 * 4 + param_11);
            iVar5 = iVar2 + iVar10;
            iVar9 = 0;
            do {
              sVar1 = *(short *)(param_1[0x1c] + iVar14);
              uVar11 = sVar1 - iVar9;
              if (0x400 < uVar11) {
                return 0xffffffff;
              }
              uVar6 = *puVar3;
              *piVar17 = iVar7;
              esc_iquant_scaling(param_7,param_6,uVar11,iVar7,
                                 *(undefined2 *)((int)&exptable + (uVar6 & 3) * 2),auStack_44[0]);
              iVar10 = iVar10 + 1;
              *piVar17 = *piVar17 - (((int)(uVar6 - 100) >> 2) + 1);
              param_7 = param_7 + uVar11 * 2;
              iVar14 = iVar14 + 2;
              puVar3 = puVar3 + 1;
              piVar17 = piVar17 + 1;
              param_6 = param_6 + uVar11 * 4;
              iVar9 = (int)sVar1;
            } while (iVar10 != iVar5);
            iStack_78 = iStack_78 + -1;
          } while (iStack_78 != 0);
        }
      }
      return 0;
    }
  }
  else {
    uVar11 = *param_4;
    iVar7 = 0;
    piVar17 = param_1 + 0x25;
    uVar6 = 0;
    while ((uVar11 < 0x10 && (uVar18 = param_4[1], -1 < (int)uVar18))) {
      if ((uVar11 - 1 & 0xc) == 0xc) {
        piVar17 = param_1 + 0x25 + uVar18;
        uVar11 = piVar17[-1] - iVar7;
        if (0x400 < uVar11) {
          return 0xffffffff;
        }
        memset(param_7 + iVar7 * 2,0,uVar11 * 2);
        memset(param_8 + iVar7 * 2,0,uVar11 * 2);
        iVar7 = piVar17[-1];
      }
      else {
        if ((int)uVar11 < 5) {
          uVar12 = uVar11;
          if (*(int *)(hcbbook_binary + uVar11 * 0x14 + 0x10) == 0) {
            if (uVar11 == 3) {
              pcVar13 = unpack_idx_sgn;
              pcVar15 = decode_huff_cw_tab3;
              uVar12 = 4;
            }
            else if (uVar11 == 4) {
              pcVar13 = unpack_idx_sgn;
              pcVar15 = decode_huff_cw_tab4;
            }
            else {
              pcVar13 = unpack_idx_sgn;
LAB_ram_43009890:
              if (uVar11 == 1) {
                pcVar15 = decode_huff_cw_tab1;
                uVar12 = 4;
              }
              else {
                pcVar15 = decode_huff_cw_tab2;
                uVar12 = 4;
              }
            }
          }
          else if (uVar11 == 3) {
            uVar12 = 4;
            pcVar13 = unpack_idx;
            pcVar15 = decode_huff_cw_tab3;
          }
          else {
            pcVar13 = unpack_idx;
            if (uVar11 != 4) goto LAB_ram_43009890;
            pcVar13 = unpack_idx;
            pcVar15 = decode_huff_cw_tab4;
          }
        }
        else if (uVar11 == 0xb) {
          pcVar13 = unpack_idx_esc;
          pcVar15 = decode_huff_cw_tab11;
          uVar12 = 2;
        }
        else {
          if (*(int *)(hcbbook_binary + uVar11 * 0x14 + 0x10) == 0) {
            pcVar13 = unpack_idx_sgn;
          }
          else {
            pcVar13 = unpack_idx;
          }
          if (uVar11 == 6) {
            pcVar15 = decode_huff_cw_tab6;
            uVar12 = 2;
          }
          else if ((int)uVar11 < 7) {
            pcVar15 = decode_huff_cw_tab5;
            uVar12 = 2;
          }
          else if (uVar11 == 9) {
            pcVar15 = decode_huff_cw_tab9;
            uVar12 = 2;
          }
          else if ((int)uVar11 < 10) {
            if (uVar11 == 7) {
              pcVar15 = decode_huff_cw_tab7;
              uVar12 = 2;
            }
            else {
              pcVar15 = decode_huff_cw_tab8;
              uVar12 = 2;
            }
          }
          else {
            if (uVar11 != 10) {
              return 0xffffffff;
            }
            pcVar15 = decode_huff_cw_tab10;
            uVar12 = 2;
          }
        }
        if ((int)uVar6 < (int)uVar18) {
          iVar10 = iVar7 * 2 + param_7;
          iVar2 = iVar7;
          piVar8 = piVar17;
          uVar16 = uVar6;
          do {
            iVar7 = *piVar8;
            piVar8 = piVar8 + 1;
            for (iVar2 = iVar7 - iVar2; iVar2 - 1U < 0x3ff; iVar2 = iVar2 - uVar12) {
              uVar4 = (*pcVar15)(param_2);
              (*pcVar13)(iVar10,uVar4,hcbbook_binary + uVar11 * 0x14,param_2,auStack_44);
              iVar10 = iVar10 + uVar12 * 2;
            }
            uVar16 = uVar16 + 1;
            iVar2 = iVar7;
          } while (uVar18 != uVar16);
          piVar17 = piVar17 + (uVar18 - uVar6);
        }
      }
      if (param_3 == 1) goto LAB_ram_430097d0;
      param_3 = param_3 + -1;
      param_4 = param_4 + 2;
      uVar11 = *param_4;
      uVar6 = uVar18;
    }
  }
  return 0xffffffff;
}
