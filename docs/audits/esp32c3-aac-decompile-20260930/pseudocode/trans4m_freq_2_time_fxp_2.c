/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: trans4m_freq_2_time_fxp_2 @ ram:4202b956
 * Types and parameter counts are inferred; verify against disassembly. */

void trans4m_freq_2_time_fxp_2
               (int param_1,int *param_2,int param_3,int param_4,int param_5,undefined4 param_6,
               undefined4 *param_7,undefined4 param_8,ushort *param_9)

{
  short sVar1;
  short sVar2;
  short sVar3;
  short sVar4;
  uint uVar5;
  ushort *puVar6;
  int iVar7;
  int *piVar8;
  int *piVar9;
  short *psVar10;
  undefined1 *puVar11;
  undefined4 uVar12;
  uint uVar13;
  int *piVar14;
  int *piVar15;
  short *psVar16;
  ushort uVar17;
  int iVar18;
  int *piVar19;
  short *psVar20;
  int iVar21;
  short *psVar22;
  short *psVar23;
  undefined4 *puVar24;
  ushort *puVar25;
  ushort *puVar26;
  int iVar27;
  undefined1 *apuStack_50 [7];

  gp = &__global_pointer_;
  apuStack_50[0] = Long_Window_sine_fxp;
  apuStack_50[1] = Long_Window_KBD_fxp;
  apuStack_50[2] = Short_Window_sine_fxp;
  apuStack_50[3] = Short_Window_KBD_fxp;
  if (param_3 == 2) {
    memset(param_1 + 0x1700,0,0x200);
    piVar15 = (int *)(param_1 + 0x1900);
    puVar24 = param_7 + 7;
    do {
      piVar8 = piVar15 + -0x2c0;
      iVar7 = imdct_fxp(piVar8,param_8,0x100,param_6,*puVar24);
      if (iVar7 < 0x10) {
        psVar16 = (short *)apuStack_50[param_5 + 2];
        psVar10 = psVar16 + 0x7f;
        piVar19 = piVar15 + -0x80;
        do {
          piVar9 = piVar8 + 0x40;
          sVar1 = *psVar10;
          sVar2 = *psVar16;
          iVar18 = *piVar8;
          piVar14 = piVar19 + 1;
          psVar10 = psVar10 + -1;
          psVar16 = psVar16 + 1;
          piVar8 = (int *)((int)piVar8 + 2);
          *piVar19 = ((int)sVar1 * (int)(short)*piVar9 >> (iVar7 + 5U & 0x1f)) + *piVar19;
          piVar19[-0x80] = (int)sVar2 * (int)(short)iVar18 >> (iVar7 + 5U & 0x1f);
          piVar19 = piVar14;
        } while (piVar14 != piVar15);
      }
      else {
        memset(piVar15 + -0x100,0,0x200);
      }
      piVar15 = piVar15 + -0x80;
      puVar24 = puVar24 + -1;
    } while (piVar15 != (int *)(param_1 + 0x1300));
    iVar7 = imdct_fxp(param_1 + 0x800,param_8,0x100,param_6,param_7[4]);
    piVar8 = (int *)(param_1 + 0x1f00);
    piVar15 = (int *)(param_1 + 0x1000);
    if (iVar7 < 0x10) {
      psVar16 = (short *)apuStack_50[param_5 + 2];
      iVar21 = (int)*(short *)(param_1 + 0x800);
      iVar18 = (int)*psVar16;
      uVar13 = iVar7 + 5;
      psVar20 = (short *)(param_1 + 0x802);
      psVar10 = psVar16 + 1;
      piVar19 = piVar8;
      do {
        iVar7 = iVar18 * iVar21;
        iVar21 = (int)*psVar20;
        psVar22 = psVar10 + 1;
        iVar18 = (int)*psVar10;
        psVar20 = psVar20 + 1;
        *piVar19 = iVar7 >> (uVar13 & 0x1f);
        psVar10 = psVar22;
        piVar19 = piVar19 + 1;
      } while (psVar22 != psVar16 + 0x41);
      psVar20 = (short *)(param_1 + 0x882);
      psVar10 = psVar16 + 0x41;
      piVar19 = piVar15;
      do {
        iVar7 = iVar18 * iVar21;
        iVar21 = (int)*psVar20;
        psVar22 = psVar10 + 1;
        iVar18 = (int)*psVar10;
        psVar20 = psVar20 + 1;
        *piVar19 = iVar7 >> (uVar13 & 0x1f);
        psVar10 = psVar22;
        piVar19 = piVar19 + 1;
      } while (psVar22 != psVar16 + 0x81);
      iVar7 = *(int *)(param_1 + 0x1100);
      sVar1 = *(short *)(param_1 + 0x900);
      sVar2 = psVar16[0x7f];
      psVar20 = (short *)(param_1 + 0x902);
      psVar10 = psVar16 + 0x7e;
      piVar19 = (int *)(param_1 + 0x1100);
      do {
        iVar21 = (int)sVar1;
        iVar18 = (int)sVar2;
        sVar1 = *psVar20;
        psVar22 = psVar10 + -1;
        sVar2 = *psVar10;
        psVar20 = psVar20 + 1;
        *piVar19 = (iVar18 * iVar21 >> (uVar13 & 0x1f)) + iVar7;
        iVar7 = piVar19[1];
        psVar10 = psVar22;
        piVar19 = piVar19 + 1;
      } while (psVar22 != psVar16 + -2);
    }
    else {
      memset(piVar8,0,0x100);
      memset(piVar15,0,0x100);
    }
    piVar19 = (int *)(param_1 + 0x1d00);
    iVar7 = imdct_fxp(param_1 + 0x600,param_8,0x100,param_6,param_7[3]);
    puVar6 = param_9 + 0x780;
    if (iVar7 < 0x10) {
      psVar16 = (short *)apuStack_50[param_5 + 2];
      uVar13 = iVar7 + 5;
      sVar1 = *(short *)(param_1 + 0x600);
      sVar2 = *psVar16;
      piVar14 = param_2 + 0x3c0;
      psVar20 = (short *)(param_1 + 0x602);
      piVar9 = piVar19;
      psVar10 = psVar16 + 1;
      do {
        iVar18 = (int)sVar1;
        iVar7 = (int)sVar2;
        sVar1 = *psVar20;
        psVar22 = psVar10 + 1;
        sVar2 = *psVar10;
        psVar20 = psVar20 + 1;
        *piVar9 = iVar7 * iVar18 >> (uVar13 & 0x1f);
        piVar9 = piVar9 + 1;
        psVar10 = psVar22;
      } while (psVar22 != psVar16 + 0x81);
      iVar18 = (int)*(short *)(param_1 + 0x700);
      iVar7 = (int)psVar16[0x7f];
      psVar20 = (short *)(param_1 + 0x702);
      psVar10 = psVar16 + 0x7e;
      puVar25 = puVar6;
      do {
        iVar27 = *piVar8;
        iVar21 = *piVar14;
        piVar8 = piVar8 + 1;
        piVar14 = piVar14 + 1;
        psVar22 = psVar10 + -1;
        iVar7 = (iVar7 * iVar18 >> (uVar13 & 0x1f)) + iVar27 + iVar21 + 0x200;
        uVar17 = (ushort)(iVar7 >> 10);
        if (iVar7 >> 0x19 != iVar7 >> 0x1f) {
          uVar17 = (ushort)(iVar7 >> 0x1f) ^ 0x7fff;
        }
        *puVar25 = uVar17;
        iVar18 = (int)*psVar20;
        iVar7 = (int)*psVar10;
        puVar25 = puVar25 + 2;
        psVar20 = psVar20 + 1;
        psVar10 = psVar22;
      } while (psVar16 + 0x3e != psVar22);
      psVar20 = (short *)(param_1 + 0x782);
      piVar8 = piVar15;
      psVar10 = psVar16 + 0x3e;
      do {
        iVar21 = iVar7 * iVar18;
        iVar18 = (int)*psVar20;
        psVar22 = psVar10 + -1;
        iVar7 = (int)*psVar10;
        psVar20 = psVar20 + 1;
        *piVar8 = *piVar8 + (iVar21 >> (uVar13 & 0x1f));
        piVar8 = piVar8 + 1;
        psVar10 = psVar22;
      } while (psVar22 != psVar16 + -2);
    }
    else {
      memset(piVar19,0,0x200);
      iVar7 = *(int *)(param_1 + 0x1f00);
      piVar8 = (int *)(param_1 + 0x1f04);
      puVar25 = puVar6;
      do {
        iVar7 = iVar7 + 0x200;
        uVar17 = (ushort)(iVar7 >> 10);
        if (iVar7 >> 0x19 != iVar7 >> 0x1f) {
          uVar17 = (ushort)(iVar7 >> 0x1f) ^ 0x7fff;
        }
        *puVar25 = uVar17;
        puVar25 = puVar25 + 2;
        iVar7 = *piVar8;
        piVar8 = piVar8 + 1;
      } while (param_9 + 0x800 != puVar25);
    }
    param_7 = param_7 + 2;
    piVar8 = param_2 + 0x340;
    iVar7 = 2;
    psVar10 = (short *)(param_1 + 0x500);
    do {
      iVar21 = imdct_fxp(psVar10 + -0x80,param_8,0x100,param_6,*param_7);
      puVar25 = puVar6 + -0x100;
      iVar18 = *(int *)(param_1 + 0x1d00);
      if (iVar21 < 0x10) {
        psVar20 = (short *)apuStack_50[param_5 + 2];
        psVar16 = psVar20;
        if (iVar7 == 0) {
          psVar16 = (short *)apuStack_50[param_4 + 2];
        }
        sVar1 = *psVar10;
        sVar2 = psVar20[0x7f];
        psVar20 = psVar20 + 0x7e;
        piVar9 = piVar19;
        psVar22 = psVar10 + -0x80;
        piVar14 = piVar8;
        puVar6 = puVar25;
        do {
          iVar27 = *piVar14;
          sVar3 = *psVar22;
          sVar4 = *psVar16;
          piVar14 = piVar14 + 1;
          psVar23 = psVar22 + 1;
          psVar16 = psVar16 + 1;
          iVar18 = ((int)sVar2 * (int)sVar1 >> (iVar21 + 5U & 0x1f)) + iVar18 + iVar27 + 0x200;
          uVar17 = (ushort)(iVar18 >> 10);
          if (iVar18 >> 0x19 != iVar18 >> 0x1f) {
            uVar17 = (ushort)(iVar18 >> 0x1f) ^ 0x7fff;
          }
          *puVar6 = uVar17;
          sVar1 = psVar22[0x81];
          *piVar9 = (int)sVar4 * (int)sVar3 >> (iVar21 + 5U & 0x1f);
          iVar18 = piVar9[1];
          sVar2 = *psVar20;
          puVar6 = puVar6 + 2;
          psVar20 = psVar20 + -1;
          piVar9 = piVar9 + 1;
          psVar22 = psVar23;
        } while (psVar23 != psVar10);
      }
      else {
        iVar21 = *piVar8;
        piVar14 = piVar19;
        puVar26 = puVar25;
        piVar9 = piVar8;
        do {
          piVar9 = piVar9 + 1;
          iVar18 = iVar21 + iVar18 + 0x200;
          uVar17 = (ushort)(iVar18 >> 10);
          if (iVar18 >> 0x19 != iVar18 >> 0x1f) {
            uVar17 = (ushort)(iVar18 >> 0x1f) ^ 0x7fff;
          }
          *puVar26 = uVar17;
          *piVar14 = 0;
          puVar26 = puVar26 + 2;
          iVar21 = *piVar9;
          iVar18 = piVar14[1];
          piVar14 = piVar14 + 1;
        } while (puVar26 != puVar6);
      }
      iVar7 = iVar7 + -1;
      param_7 = param_7 + -1;
      piVar8 = piVar8 + -0x80;
      psVar10 = psVar10 + -0x100;
      puVar6 = puVar25;
    } while (iVar7 != -1);
    iVar7 = *(int *)(param_1 + 0x1d00);
    iVar18 = param_2[0x1c0];
    puVar25 = param_9 + 0x380;
    piVar8 = param_2 + 0x1c1;
    piVar19 = (int *)(param_1 + 0x1d04);
    puVar6 = puVar25;
    do {
      iVar7 = iVar18 + iVar7 + 0x200;
      uVar17 = (ushort)(iVar7 >> 10);
      if (iVar7 >> 0x19 != iVar7 >> 0x1f) {
        uVar17 = (ushort)(iVar7 >> 0x1f) ^ 0x7fff;
      }
      *puVar6 = uVar17;
      puVar6 = puVar6 + 2;
      iVar7 = *piVar19;
      iVar18 = *piVar8;
      piVar8 = piVar8 + 1;
      piVar19 = piVar19 + 1;
    } while (param_9 + 0x480 != puVar6);
    iVar7 = *param_2;
    piVar8 = param_2;
    do {
      piVar8 = piVar8 + 1;
      iVar7 = iVar7 + 0x200;
      uVar17 = (ushort)(iVar7 >> 10);
      if (iVar7 >> 0x19 != iVar7 >> 0x1f) {
        uVar17 = (ushort)(iVar7 >> 0x1f) ^ 0x7fff;
      }
      *param_9 = uVar17;
      param_9 = param_9 + 2;
      iVar7 = *piVar8;
    } while (puVar25 != param_9);
    piVar8 = param_2;
    do {
      iVar7 = *piVar15;
      piVar15 = piVar15 + 1;
      *piVar8 = iVar7;
      piVar8 = piVar8 + 1;
    } while ((int *)(param_1 + 0x1900) != piVar15);
    param_2 = param_2 + 0x240;
    uVar12 = 0x700;
  }
  else {
    iVar7 = imdct_fxp(param_1,param_8,0x800,param_6,*param_7);
    if (iVar7 < 0x10) {
      piVar15 = (int *)(param_1 + 0x800);
      uVar13 = iVar7 + 5;
      if (param_3 != 1) {
        if (param_3 == 3) {
          uVar5 = iVar7 - 10;
          iVar21 = param_2[0x240];
          puVar6 = param_9 + 0x480;
          iVar18 = (int)*(short *)(param_1 + 0x480);
          piVar8 = param_2 + 0x241;
          psVar10 = (short *)(param_1 + 0x482);
          if ((int)uVar5 < 1) {
            if (uVar5 == 0) {
              do {
                iVar7 = iVar18 + iVar21 + 0x200;
                psVar16 = psVar10 + 1;
                uVar17 = (ushort)(iVar7 >> 10);
                if (iVar7 >> 0x19 != iVar7 >> 0x1f) {
                  uVar17 = (ushort)(iVar7 >> 0x1f) ^ 0x7fff;
                }
                *puVar6 = uVar17;
                iVar18 = (int)*psVar10;
                iVar21 = *piVar8;
                puVar6 = puVar6 + 2;
                psVar10 = psVar16;
                piVar8 = piVar8 + 1;
              } while (psVar16 != (short *)(param_1 + 0x802));
            }
            else {
              iVar18 = iVar18 << (10U - iVar7 & 0x1f);
              do {
                iVar18 = iVar18 + iVar21 + 0x200;
                uVar17 = (ushort)(iVar18 >> 10);
                if (iVar18 >> 0x1f != iVar18 >> 0x19) {
                  uVar17 = (ushort)(iVar18 >> 0x1f) ^ 0x7fff;
                }
                *puVar6 = uVar17;
                puVar6 = puVar6 + 2;
                iVar21 = *piVar8;
                iVar18 = (int)*psVar10 << (10U - iVar7 & 0x1f);
                psVar10 = psVar10 + 1;
                piVar8 = piVar8 + 1;
              } while (puVar6 != param_9 + 0x800);
            }
          }
          else {
            iVar18 = iVar18 >> (uVar5 & 0x1f);
            do {
              iVar7 = iVar18 + iVar21 + 0x200;
              uVar17 = (ushort)(iVar7 >> 10);
              if (iVar7 >> 0x1f != iVar7 >> 0x19) {
                uVar17 = (ushort)(iVar7 >> 0x1f) ^ 0x7fff;
              }
              *puVar6 = uVar17;
              puVar6 = puVar6 + 2;
              iVar21 = *piVar8;
              iVar18 = (int)*psVar10 >> (uVar5 & 0x1f);
              psVar10 = psVar10 + 1;
              piVar8 = piVar8 + 1;
            } while (puVar6 != param_9 + 0x800);
          }
          puVar25 = param_9 + 0x380;
          piVar8 = param_2 + 0x200;
          puVar6 = puVar25;
          psVar10 = (short *)(apuStack_50[param_4 + 2] + 0x80);
          psVar16 = (short *)(param_1 + 0x400);
          do {
            iVar7 = ((int)psVar10[-0x40] * (int)psVar16[-0x40] >> (uVar13 & 0x1f)) + piVar8[-0x40] +
                    0x200;
            uVar17 = (ushort)(iVar7 >> 10);
            if (iVar7 >> 0x1f != iVar7 >> 0x19) {
              uVar17 = (ushort)(iVar7 >> 0x1f) ^ 0x7fff;
            }
            *puVar6 = uVar17;
            puVar26 = puVar6 + 2;
            iVar7 = ((int)*psVar10 * (int)*psVar16 >> (uVar13 & 0x1f)) + *piVar8 + 0x200;
            uVar17 = (ushort)(iVar7 >> 10);
            if (iVar7 >> 0x1f != iVar7 >> 0x19) {
              uVar17 = (ushort)(iVar7 >> 0x1f) ^ 0x7fff;
            }
            puVar6[0x80] = uVar17;
            piVar8 = piVar8 + 1;
            puVar6 = puVar26;
            psVar10 = psVar10 + 1;
            psVar16 = psVar16 + 1;
          } while (puVar26 != param_9 + 0x400);
          puVar11 = apuStack_50[param_5];
          psVar10 = (short *)(puVar11 + 0x7fe);
          piVar8 = param_2;
          do {
            iVar18 = *piVar8 + 0x200;
            uVar17 = (ushort)(iVar18 >> 10);
            sVar1 = *psVar10;
            iVar7 = *piVar15;
            if (iVar18 >> 0x1f != iVar18 >> 0x19) {
              uVar17 = (ushort)(iVar18 >> 0x1f) ^ 0x7fff;
            }
            *param_9 = uVar17;
            param_9 = param_9 + 2;
            *piVar8 = (int)sVar1 * (int)(short)iVar7 >> (uVar13 & 0x1f);
            piVar15 = (int *)((int)piVar15 + 2);
            psVar10 = psVar10 + -1;
            piVar8 = piVar8 + 1;
          } while (param_9 != puVar25);
          psVar10 = (short *)(puVar11 + 0x47e);
          psVar16 = (short *)(param_1 + 0xb80);
          piVar15 = param_2 + 0x1c0;
          do {
            sVar1 = *psVar16;
            sVar2 = *psVar10;
            psVar16 = psVar16 + 1;
            psVar10 = psVar10 + -1;
            *piVar15 = (int)sVar2 * (int)sVar1 >> (uVar13 & 0x1f);
            piVar15 = piVar15 + 1;
          } while ((short *)(param_1 + 0x1000) != psVar16);
        }
        else {
          piVar8 = (int *)apuStack_50[param_4];
          psVar10 = (short *)(apuStack_50[param_5] + 0x7fe);
          piVar19 = piVar8 + 0x200;
          do {
            iVar18 = *piVar8;
            piVar8 = piVar8 + 1;
            iVar7 = ((int)(short)iVar18 * (int)(short)piVar15[-0x200] >> (uVar13 & 0x1f)) + *param_2
                    + 0x200;
            uVar17 = (ushort)(iVar7 >> 10);
            iVar18 = ((iVar18 >> 0x10) * (piVar15[-0x200] >> 0x10) >> (uVar13 & 0x1f)) + param_2[1]
                     + 0x200;
            if (iVar7 >> 0x1f != iVar7 >> 0x19) {
              uVar17 = (ushort)(iVar7 >> 0x1f) ^ 0x7fff;
            }
            *param_9 = uVar17;
            uVar17 = (ushort)(iVar18 >> 10);
            if (iVar18 >> 0x1f != iVar18 >> 0x19) {
              uVar17 = (ushort)(iVar18 >> 0x1f) ^ 0x7fff;
            }
            iVar7 = *piVar15;
            param_9[2] = uVar17;
            sVar1 = *psVar10;
            sVar2 = psVar10[-1];
            psVar10 = psVar10 + -2;
            param_9 = param_9 + 4;
            *param_2 = (int)sVar1 * (int)(short)iVar7 >> (uVar13 & 0x1f);
            param_2[1] = (int)sVar2 * (iVar7 >> 0x10) >> (uVar13 & 0x1f);
            piVar15 = piVar15 + 1;
            param_2 = param_2 + 2;
          } while (piVar8 != piVar19);
        }
        return;
      }
      psVar16 = (short *)(param_1 + 0x400);
      puVar6 = param_9;
      piVar8 = param_2 + 0x200;
      psVar10 = (short *)(apuStack_50[param_4] + 0x400);
      do {
        psVar20 = psVar16 + -0x200;
        sVar1 = *psVar16;
        psVar16 = psVar16 + 1;
        iVar18 = ((int)psVar10[-0x200] * (int)*psVar20 >> (uVar13 & 0x1f)) + piVar8[-0x200] + 0x200;
        uVar17 = (ushort)(iVar18 >> 10);
        if (iVar18 >> 0x1f != iVar18 >> 0x19) {
          uVar17 = (ushort)(iVar18 >> 0x1f) ^ 0x7fff;
        }
        iVar18 = ((int)*psVar10 * (int)sVar1 >> (uVar13 & 0x1f)) + *piVar8 + 0x200;
        *puVar6 = uVar17;
        puVar25 = puVar6 + 2;
        uVar17 = (ushort)(iVar18 >> 10);
        if (iVar18 >> 0x1f != iVar18 >> 0x19) {
          uVar17 = (ushort)(iVar18 >> 0x1f) ^ 0x7fff;
        }
        puVar6[0x400] = uVar17;
        puVar6 = puVar25;
        piVar8 = piVar8 + 1;
        psVar10 = psVar10 + 1;
      } while (puVar25 != param_9 + 0x400);
      uVar5 = iVar7 - 10;
      if ((int)uVar5 < 0) {
        piVar8 = param_2;
        do {
          piVar19 = piVar15 + 1;
          sVar1 = *(short *)((int)piVar15 + 2);
          *piVar8 = (int)(short)*piVar15 << (10U - iVar7 & 0x1f);
          piVar8[1] = (int)sVar1 << (10U - iVar7 & 0x1f);
          piVar15 = piVar19;
          piVar8 = piVar8 + 2;
        } while ((int *)(param_1 + 0xb80) != piVar19);
      }
      else {
        piVar8 = param_2;
        do {
          piVar19 = piVar15 + 1;
          sVar1 = *(short *)((int)piVar15 + 2);
          *piVar8 = (int)(short)*piVar15 >> (uVar5 & 0x1f);
          piVar8[1] = (int)sVar1 >> (uVar5 & 0x1f);
          piVar15 = piVar19;
          piVar8 = piVar8 + 2;
        } while ((int *)(param_1 + 0xb80) != piVar19);
      }
      psVar16 = (short *)(param_1 + 0xb80);
      psVar10 = (short *)(apuStack_50[param_5 + 2] + 0xfe);
      piVar15 = param_2 + 0x1c0;
      do {
        psVar20 = psVar16 + 0x40;
        psVar22 = psVar10 + -0x40;
        sVar1 = *psVar16;
        sVar2 = *psVar10;
        psVar16 = psVar16 + 1;
        psVar10 = psVar10 + -1;
        piVar15[0x40] = (int)*psVar22 * (int)*psVar20 >> (uVar13 & 0x1f);
        *piVar15 = (int)sVar2 * (int)sVar1 >> (uVar13 & 0x1f);
        piVar15 = piVar15 + 1;
      } while ((short *)(param_1 + 0xc00) != psVar16);
      param_2 = param_2 + 0x240;
      uVar12 = 0x700;
    }
    else {
      iVar7 = *param_2;
      piVar15 = param_2 + 1;
      do {
        iVar7 = iVar7 + 0x200;
        piVar8 = piVar15 + 1;
        uVar17 = (ushort)(iVar7 >> 10);
        if (iVar7 >> 0x19 != iVar7 >> 0x1f) {
          uVar17 = (ushort)(iVar7 >> 0x1f) ^ 0x7fff;
        }
        *param_9 = uVar17;
        iVar7 = *piVar15;
        param_9 = param_9 + 2;
        piVar15 = piVar8;
      } while (param_2 + 0x401 != piVar8);
      uVar12 = 0x1000;
    }
  }
  memset(param_2,0,uVar12);
  return;
}
