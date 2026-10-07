/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: long_term_synthesis @ ram:42045dc4
 * Types and parameter counts are inferred; verify against disassembly. */

void long_term_synthesis(int param_1,int param_2,short *param_3,int *param_4,int *param_5,
                        int param_6,int *param_7,int param_8,int param_9,int param_10,int param_11,
                        int param_12)

{
  short sVar1;
  int *piVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  uint *puVar6;
  int *piVar7;
  int *piVar8;
  int iVar9;
  uint uVar10;
  int iVar11;
  uint *puVar12;
  uint *puVar13;
  int iVar14;
  short *psVar15;

  gp = &__global_pointer_;
  if (param_1 == 2) {
    if (0 < param_11) {
      piVar7 = param_4 + param_11;
      param_10 = param_10 * 4;
      do {
        while ((*param_4 == 0 || (param_12 < 1))) {
          param_4 = param_4 + 1;
          param_8 = param_8 + param_10;
          param_6 = param_6 + param_10;
          param_7 = param_7 + param_2;
          if (piVar7 == param_4) {
            return;
          }
        }
        piVar2 = param_7;
        psVar15 = param_3;
        iVar3 = 0;
        do {
          sVar1 = *psVar15;
          iVar9 = sVar1 - iVar3;
          if (0 < iVar9) {
            puVar12 = (uint *)(param_8 + iVar3 * 4);
            uVar10 = 0;
            puVar6 = puVar12;
            do {
              uVar4 = *puVar6;
              puVar6 = puVar6 + 1;
              uVar10 = uVar10 | (int)uVar4 >> 0x1f ^ uVar4;
            } while (puVar6 != puVar12 + iVar9);
            if (uVar10 != 0) {
              piVar8 = (int *)(param_6 + iVar3 * 4);
              iVar9 = iVar9 >> 2;
              if (uVar10 < 0x40000000) {
                uVar4 = 0;
                do {
                  uVar5 = uVar4;
                  uVar10 = uVar10 << 1;
                  uVar4 = uVar5 + 1;
                } while (uVar10 < 0x40000000);
                iVar14 = *piVar2;
                iVar3 = param_9 + uVar4;
                uVar10 = iVar14 - iVar3;
                if (uVar10 < 0x1f) {
                  if (iVar9 != 0) {
                    uVar10 = uVar10 + 1;
                    puVar6 = puVar12;
                    do {
                      *piVar8 = (*puVar6 << (uVar5 & 0x1f)) + (*piVar8 >> (uVar10 & 0x1f));
                      piVar8[1] = (puVar6[1] << (uVar5 & 0x1f)) + (piVar8[1] >> (uVar10 & 0x1f));
                      puVar13 = puVar6 + 4;
                      piVar8[2] = (puVar6[2] << (uVar5 & 0x1f)) + (piVar8[2] >> (uVar10 & 0x1f));
                      piVar8[3] = (puVar6[3] << (uVar5 & 0x1f)) + (piVar8[3] >> (uVar10 & 0x1f));
                      piVar8 = piVar8 + 4;
                      puVar6 = puVar13;
                    } while (puVar13 != puVar12 + iVar9 * 4);
                  }
LAB_ram_4204600c:
                  *piVar2 = iVar3 + -1;
                }
                else if ((int)uVar10 < 0x1f) {
                  if (0xffffffe1 < uVar10) {
                    uVar5 = uVar5 + uVar10;
                    if ((int)uVar5 < 0) goto LAB_ram_42046152;
                    puVar6 = puVar12;
                    if (iVar9 != 0) {
                      do {
                        *piVar8 = (*puVar6 << (uVar5 & 0x1f)) + (*piVar8 >> 1);
                        piVar8[1] = (puVar6[1] << (uVar5 & 0x1f)) + (piVar8[1] >> 1);
                        puVar13 = puVar6 + 4;
                        piVar8[2] = (puVar6[2] << (uVar5 & 0x1f)) + (piVar8[2] >> 1);
                        piVar8[3] = (puVar6[3] << (uVar5 & 0x1f)) + (piVar8[3] >> 1);
                        piVar8 = piVar8 + 4;
                        puVar6 = puVar13;
                      } while (puVar13 != puVar12 + iVar9 * 4);
                    }
LAB_ram_42046088:
                    *piVar2 = iVar14 + -1;
                  }
                }
                else {
LAB_ram_42046094:
                  puVar6 = puVar12;
                  if (iVar9 != 0) {
                    do {
                      puVar13 = puVar6 + 4;
                      *piVar8 = *puVar6 << (uVar4 & 0x1f);
                      piVar8[1] = puVar6[1] << (uVar4 & 0x1f);
                      piVar8[2] = puVar6[2] << (uVar4 & 0x1f);
                      piVar8[3] = puVar6[3] << (uVar4 & 0x1f);
                      piVar8 = piVar8 + 4;
                      puVar6 = puVar13;
                    } while (puVar13 != puVar12 + iVar9 * 4);
                  }
                  *piVar2 = iVar3;
                }
              }
              else {
                iVar14 = *piVar2;
                uVar10 = iVar14 - param_9;
                iVar3 = param_9;
                if (uVar10 < 0x1f) {
                  uVar10 = uVar10 + 1;
                  puVar6 = puVar12;
                  if (iVar9 != 0) {
                    do {
                      *piVar8 = ((int)*puVar6 >> 1) + (*piVar8 >> (uVar10 & 0x1f));
                      piVar8[1] = ((int)puVar6[1] >> 1) + (piVar8[1] >> (uVar10 & 0x1f));
                      puVar13 = puVar6 + 4;
                      piVar8[2] = ((int)puVar6[2] >> 1) + (piVar8[2] >> (uVar10 & 0x1f));
                      piVar8[3] = ((int)puVar6[3] >> 1) + (piVar8[3] >> (uVar10 & 0x1f));
                      piVar8 = piVar8 + 4;
                      puVar6 = puVar13;
                    } while (puVar13 != puVar12 + iVar9 * 4);
                  }
                  goto LAB_ram_4204600c;
                }
                if (0x1e < (int)uVar10) {
                  uVar4 = 0;
                  goto LAB_ram_42046094;
                }
                if (0xffffffe1 < uVar10) {
                  uVar4 = 0;
LAB_ram_42046152:
                  uVar4 = (1 - uVar10) - uVar4;
                  puVar6 = puVar12;
                  if (iVar9 == 0) goto LAB_ram_42046088;
                  do {
                    *piVar8 = ((int)*puVar6 >> (uVar4 & 0x1f)) + (*piVar8 >> 1);
                    piVar8[1] = ((int)puVar6[1] >> (uVar4 & 0x1f)) + (piVar8[1] >> 1);
                    puVar13 = puVar6 + 4;
                    piVar8[2] = ((int)puVar6[2] >> (uVar4 & 0x1f)) + (piVar8[2] >> 1);
                    piVar8[3] = ((int)puVar6[3] >> (uVar4 & 0x1f)) + (piVar8[3] >> 1);
                    piVar8 = piVar8 + 4;
                    puVar6 = puVar13;
                  } while (puVar13 != puVar12 + iVar9 * 4);
                  *piVar2 = iVar14 + -1;
                }
              }
            }
          }
          psVar15 = psVar15 + 1;
          piVar2 = piVar2 + 1;
          iVar3 = (int)sVar1;
        } while (psVar15 != param_3 + param_12);
        param_4 = param_4 + 1;
        param_8 = param_8 + param_10;
        param_6 = param_6 + param_10;
        param_7 = param_7 + param_2;
        if (piVar7 == param_4) {
          return;
        }
      } while( true );
    }
  }
  else if (0 < param_2) {
    psVar15 = param_3 + param_2;
    iVar3 = 0;
    do {
      while( true ) {
        iVar9 = *param_5;
        param_5 = param_5 + 1;
        iVar14 = (int)*param_3;
        if ((iVar9 != 0) && (iVar9 = iVar14 - iVar3, 0 < iVar9)) break;
LAB_ram_42045de0:
        param_3 = param_3 + 1;
        param_7 = param_7 + 1;
        iVar3 = iVar14;
        if (param_3 == psVar15) {
          return;
        }
      }
      puVar12 = (uint *)(param_8 + iVar3 * 4);
      uVar10 = 0;
      puVar6 = puVar12;
      do {
        uVar4 = *puVar6;
        puVar6 = puVar6 + 1;
        uVar10 = uVar10 | (int)uVar4 >> 0x1f ^ uVar4;
      } while (puVar6 != puVar12 + iVar9);
      if (uVar10 == 0) goto LAB_ram_42045de0;
      piVar7 = (int *)(param_6 + iVar3 * 4);
      iVar9 = iVar9 >> 2;
      if (0x3fffffff < uVar10) {
        iVar11 = *param_7;
        uVar10 = iVar11 - param_9;
        iVar3 = param_9;
        if (uVar10 < 0x1f) {
          uVar10 = uVar10 + 1;
          puVar6 = puVar12;
          if (iVar9 != 0) {
            do {
              *piVar7 = ((int)*puVar6 >> 1) + (*piVar7 >> (uVar10 & 0x1f));
              piVar7[1] = ((int)puVar6[1] >> 1) + (piVar7[1] >> (uVar10 & 0x1f));
              puVar13 = puVar6 + 4;
              piVar7[2] = ((int)puVar6[2] >> 1) + (piVar7[2] >> (uVar10 & 0x1f));
              piVar7[3] = ((int)puVar6[3] >> 1) + (piVar7[3] >> (uVar10 & 0x1f));
              piVar7 = piVar7 + 4;
              puVar6 = puVar13;
            } while (puVar13 != puVar12 + iVar9 * 4);
          }
          goto LAB_ram_42045eb8;
        }
        if (0x1e < (int)uVar10) {
          uVar4 = 0;
          goto LAB_ram_4204624c;
        }
        if (0xffffffe1 < uVar10) {
          uVar4 = 0;
LAB_ram_4204629a:
          uVar4 = (1 - uVar10) - uVar4;
          puVar6 = puVar12;
          if (iVar9 != 0) {
            do {
              *piVar7 = ((int)*puVar6 >> (uVar4 & 0x1f)) + (*piVar7 >> 1);
              piVar7[1] = ((int)puVar6[1] >> (uVar4 & 0x1f)) + (piVar7[1] >> 1);
              puVar13 = puVar6 + 4;
              piVar7[2] = ((int)puVar6[2] >> (uVar4 & 0x1f)) + (piVar7[2] >> 1);
              piVar7[3] = ((int)puVar6[3] >> (uVar4 & 0x1f)) + (piVar7[3] >> 1);
              piVar7 = piVar7 + 4;
              puVar6 = puVar13;
            } while (puVar13 != puVar12 + iVar9 * 4);
          }
          goto LAB_ram_42046144;
        }
        goto LAB_ram_42045de0;
      }
      uVar4 = 0;
      do {
        uVar5 = uVar4;
        uVar10 = uVar10 << 1;
        uVar4 = uVar5 + 1;
      } while (uVar10 < 0x40000000);
      iVar11 = *param_7;
      iVar3 = param_9 + uVar4;
      uVar10 = iVar11 - iVar3;
      if (0x1e < uVar10) {
        if ((int)uVar10 < 0x1f) {
          if (0xffffffe1 < uVar10) {
            uVar5 = uVar5 + uVar10;
            if ((int)uVar5 < 0) goto LAB_ram_4204629a;
            puVar6 = puVar12;
            if (iVar9 != 0) {
              do {
                *piVar7 = (*puVar6 << (uVar5 & 0x1f)) + (*piVar7 >> 1);
                piVar7[1] = (puVar6[1] << (uVar5 & 0x1f)) + (piVar7[1] >> 1);
                puVar13 = puVar6 + 4;
                piVar7[2] = (puVar6[2] << (uVar5 & 0x1f)) + (piVar7[2] >> 1);
                piVar7[3] = (puVar6[3] << (uVar5 & 0x1f)) + (piVar7[3] >> 1);
                piVar7 = piVar7 + 4;
                puVar6 = puVar13;
              } while (puVar13 != puVar12 + iVar9 * 4);
            }
LAB_ram_42046144:
            *param_7 = iVar11 + -1;
          }
        }
        else {
LAB_ram_4204624c:
          puVar6 = puVar12;
          if (iVar9 != 0) {
            do {
              puVar13 = puVar6 + 4;
              *piVar7 = *puVar6 << (uVar4 & 0x1f);
              piVar7[1] = puVar6[1] << (uVar4 & 0x1f);
              piVar7[2] = puVar6[2] << (uVar4 & 0x1f);
              piVar7[3] = puVar6[3] << (uVar4 & 0x1f);
              piVar7 = piVar7 + 4;
              puVar6 = puVar13;
            } while (puVar13 != puVar12 + iVar9 * 4);
          }
          *param_7 = iVar3;
        }
        goto LAB_ram_42045de0;
      }
      if (iVar9 != 0) {
        uVar10 = uVar10 + 1;
        puVar6 = puVar12;
        do {
          *piVar7 = (*puVar6 << (uVar5 & 0x1f)) + (*piVar7 >> (uVar10 & 0x1f));
          piVar7[1] = (puVar6[1] << (uVar5 & 0x1f)) + (piVar7[1] >> (uVar10 & 0x1f));
          puVar13 = puVar6 + 4;
          piVar7[2] = (puVar6[2] << (uVar5 & 0x1f)) + (piVar7[2] >> (uVar10 & 0x1f));
          piVar7[3] = (puVar6[3] << (uVar5 & 0x1f)) + (piVar7[3] >> (uVar10 & 0x1f));
          piVar7 = piVar7 + 4;
          puVar6 = puVar13;
        } while (puVar13 != puVar12 + iVar9 * 4);
      }
LAB_ram_42045eb8:
      *param_7 = iVar3 + -1;
      param_3 = param_3 + 1;
      param_7 = param_7 + 1;
      iVar3 = iVar14;
    } while (param_3 != psVar15);
  }
  return;
}
