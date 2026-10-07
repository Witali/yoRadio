/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: trans4m_freq_2_time_fxp_1 @ ram:43014548
 * Types and parameter counts are inferred; verify against disassembly. */

void trans4m_freq_2_time_fxp_1
               (int param_1,int *param_2,ushort *param_3,int param_4,int param_5,int param_6,
               undefined4 param_7,undefined4 *param_8,undefined4 param_9)

{
  short sVar1;
  short sVar2;
  short sVar3;
  short sVar4;
  ushort *puVar5;
  int iVar6;
  int *piVar7;
  int *piVar8;
  ushort *puVar9;
  short *psVar10;
  undefined4 uVar11;
  uint uVar12;
  int *piVar13;
  int *piVar14;
  short *psVar15;
  ushort uVar16;
  int iVar17;
  int *piVar18;
  undefined1 *puVar19;
  short *psVar20;
  int iVar21;
  undefined4 *puVar22;
  ushort *puVar23;
  ushort *puVar24;
  short *psVar25;
  short *psVar26;
  int iVar27;
  uint uVar28;
  undefined1 *apuStack_50 [7];

  gp = &__global_pointer_;
  apuStack_50[0] = Long_Window_sine_fxp;
  apuStack_50[1] = Long_Window_KBD_fxp;
  apuStack_50[2] = Short_Window_sine_fxp;
  apuStack_50[3] = Short_Window_KBD_fxp;
  if (param_4 == 2) {
    memset(param_1 + 0x1700,0,0x200);
    piVar14 = (int *)(param_1 + 0x1900);
    puVar22 = param_8 + 7;
    do {
      piVar7 = piVar14 + -0x2c0;
      iVar6 = imdct_fxp(piVar7,param_9,0x100,param_7,*puVar22);
      if (iVar6 < 0x10) {
        psVar15 = (short *)apuStack_50[param_6 + 2];
        psVar10 = psVar15 + 0x7f;
        piVar18 = piVar14 + -0x80;
        do {
          piVar8 = piVar7 + 0x40;
          sVar1 = *psVar10;
          sVar2 = *psVar15;
          iVar17 = *piVar7;
          piVar13 = piVar18 + 1;
          psVar10 = psVar10 + -1;
          psVar15 = psVar15 + 1;
          piVar7 = (int *)((int)piVar7 + 2);
          *piVar18 = ((int)sVar1 * (int)(short)*piVar8 >> (iVar6 + 5U & 0x1f)) + *piVar18;
          piVar18[-0x80] = (int)sVar2 * (int)(short)iVar17 >> (iVar6 + 5U & 0x1f);
          piVar18 = piVar13;
        } while (piVar13 != piVar14);
      }
      else {
        memset(piVar14 + -0x100,0,0x200);
      }
      piVar14 = piVar14 + -0x80;
      puVar22 = puVar22 + -1;
    } while (piVar14 != (int *)(param_1 + 0x1300));
    iVar6 = imdct_fxp(param_1 + 0x800,param_9,0x100,param_7,param_8[4]);
    piVar7 = (int *)(param_1 + 0x1f00);
    piVar14 = (int *)(param_1 + 0x1000);
    if (iVar6 < 0x10) {
      psVar15 = (short *)apuStack_50[param_6 + 2];
      iVar21 = (int)*(short *)(param_1 + 0x800);
      iVar17 = (int)*psVar15;
      uVar12 = iVar6 + 5;
      psVar20 = (short *)(param_1 + 0x802);
      psVar10 = psVar15 + 1;
      piVar18 = piVar7;
      do {
        iVar6 = iVar17 * iVar21;
        iVar21 = (int)*psVar20;
        psVar25 = psVar10 + 1;
        iVar17 = (int)*psVar10;
        psVar20 = psVar20 + 1;
        *piVar18 = iVar6 >> (uVar12 & 0x1f);
        psVar10 = psVar25;
        piVar18 = piVar18 + 1;
      } while (psVar25 != psVar15 + 0x41);
      psVar20 = (short *)(param_1 + 0x882);
      psVar10 = psVar15 + 0x41;
      piVar18 = piVar14;
      do {
        iVar6 = iVar17 * iVar21;
        iVar21 = (int)*psVar20;
        psVar25 = psVar10 + 1;
        iVar17 = (int)*psVar10;
        psVar20 = psVar20 + 1;
        *piVar18 = iVar6 >> (uVar12 & 0x1f);
        psVar10 = psVar25;
        piVar18 = piVar18 + 1;
      } while (psVar25 != psVar15 + 0x81);
      iVar6 = *(int *)(param_1 + 0x1100);
      sVar1 = *(short *)(param_1 + 0x900);
      sVar2 = psVar15[0x7f];
      psVar20 = (short *)(param_1 + 0x902);
      psVar10 = psVar15 + 0x7e;
      piVar18 = (int *)(param_1 + 0x1100);
      do {
        iVar21 = (int)sVar1;
        iVar17 = (int)sVar2;
        sVar1 = *psVar20;
        psVar25 = psVar10 + -1;
        sVar2 = *psVar10;
        psVar20 = psVar20 + 1;
        *piVar18 = (iVar17 * iVar21 >> (uVar12 & 0x1f)) + iVar6;
        iVar6 = piVar18[1];
        psVar10 = psVar25;
        piVar18 = piVar18 + 1;
      } while (psVar25 != psVar15 + -2);
    }
    else {
      memset(piVar7,0,0x100);
      memset(piVar14,0,0x100);
    }
    piVar18 = (int *)(param_1 + 0x1d00);
    iVar6 = imdct_fxp(param_1 + 0x600,param_9,0x100,param_7,param_8[3]);
    puVar5 = param_3 + 0x3c0;
    if (iVar6 < 0x10) {
      psVar15 = (short *)apuStack_50[param_6 + 2];
      uVar12 = iVar6 + 5;
      sVar1 = *(short *)(param_1 + 0x600);
      sVar2 = *psVar15;
      piVar13 = param_2 + 0x3c0;
      psVar20 = (short *)(param_1 + 0x602);
      piVar8 = piVar18;
      psVar10 = psVar15 + 1;
      do {
        iVar17 = (int)sVar2;
        iVar6 = (int)sVar1;
        sVar1 = *psVar20;
        psVar25 = psVar10 + 1;
        sVar2 = *psVar10;
        psVar20 = psVar20 + 1;
        *piVar8 = iVar17 * iVar6 >> (uVar12 & 0x1f);
        piVar8 = piVar8 + 1;
        psVar10 = psVar25;
      } while (psVar25 != psVar15 + 0x81);
      iVar6 = (int)*(short *)(param_1 + 0x700);
      iVar17 = (int)psVar15[0x7f];
      psVar20 = (short *)(param_1 + 0x702);
      psVar10 = psVar15 + 0x7e;
      puVar9 = puVar5;
      do {
        iVar27 = *piVar7;
        iVar21 = *piVar13;
        piVar7 = piVar7 + 1;
        piVar13 = piVar13 + 1;
        psVar25 = psVar10 + -1;
        iVar6 = (iVar17 * iVar6 >> (uVar12 & 0x1f)) + iVar27 + iVar21 + 0x200;
        uVar16 = (ushort)(iVar6 >> 10);
        if (iVar6 >> 0x19 != iVar6 >> 0x1f) {
          uVar16 = (ushort)(iVar6 >> 0x1f) ^ 0x7fff;
        }
        *puVar9 = uVar16;
        iVar6 = (int)*psVar20;
        iVar17 = (int)*psVar10;
        psVar20 = psVar20 + 1;
        psVar10 = psVar25;
        puVar9 = puVar9 + 1;
      } while (psVar15 + 0x3e != psVar25);
      psVar20 = (short *)(param_1 + 0x782);
      piVar7 = piVar14;
      psVar10 = psVar15 + 0x3e;
      do {
        iVar21 = iVar17 * iVar6;
        iVar6 = (int)*psVar20;
        psVar25 = psVar10 + -1;
        iVar17 = (int)*psVar10;
        psVar20 = psVar20 + 1;
        *piVar7 = *piVar7 + (iVar21 >> (uVar12 & 0x1f));
        piVar7 = piVar7 + 1;
        psVar10 = psVar25;
      } while (psVar25 != psVar15 + -2);
    }
    else {
      memset(piVar18,0,0x200);
      iVar6 = *(int *)(param_1 + 0x1f00);
      piVar7 = (int *)(param_1 + 0x1f04);
      puVar9 = puVar5;
      do {
        iVar6 = iVar6 + 0x200;
        puVar23 = puVar9 + 1;
        uVar16 = (ushort)(iVar6 >> 10);
        if (iVar6 >> 0x19 != iVar6 >> 0x1f) {
          uVar16 = (ushort)(iVar6 >> 0x1f) ^ 0x7fff;
        }
        *puVar9 = uVar16;
        iVar6 = *piVar7;
        piVar7 = piVar7 + 1;
        puVar9 = puVar23;
      } while (param_3 + 0x400 != puVar23);
    }
    psVar10 = (short *)(param_1 + 0x500);
    param_8 = param_8 + 2;
    piVar7 = param_2 + 0x340;
    iVar6 = 2;
    do {
      iVar17 = imdct_fxp(psVar10 + -0x80,param_9,0x100,param_7,*param_8);
      puVar9 = puVar5 + -0x80;
      iVar21 = *(int *)(param_1 + 0x1d00);
      if (iVar17 < 0x10) {
        psVar20 = (short *)apuStack_50[param_6 + 2];
        psVar15 = psVar20;
        if (iVar6 == 0) {
          psVar15 = (short *)apuStack_50[param_5 + 2];
        }
        sVar1 = *psVar10;
        sVar2 = psVar20[0x7f];
        psVar20 = psVar20 + 0x7e;
        piVar8 = piVar18;
        piVar13 = piVar7;
        puVar5 = puVar9;
        psVar25 = psVar10 + -0x80;
        do {
          iVar27 = *piVar13;
          sVar3 = *psVar25;
          sVar4 = *psVar15;
          piVar13 = piVar13 + 1;
          psVar26 = psVar25 + 1;
          psVar15 = psVar15 + 1;
          iVar21 = ((int)sVar2 * (int)sVar1 >> (iVar17 + 5U & 0x1f)) + iVar21 + iVar27 + 0x200;
          uVar16 = (ushort)(iVar21 >> 10);
          if (iVar21 >> 0x19 != iVar21 >> 0x1f) {
            uVar16 = (ushort)(iVar21 >> 0x1f) ^ 0x7fff;
          }
          *puVar5 = uVar16;
          sVar1 = psVar25[0x81];
          sVar2 = *psVar20;
          *piVar8 = (int)sVar4 * (int)sVar3 >> (iVar17 + 5U & 0x1f);
          iVar21 = piVar8[1];
          psVar20 = psVar20 + -1;
          piVar8 = piVar8 + 1;
          puVar5 = puVar5 + 1;
          psVar25 = psVar26;
        } while (psVar26 != psVar10);
      }
      else {
        iVar17 = *piVar7;
        piVar13 = piVar18;
        puVar23 = puVar9;
        piVar8 = piVar7;
        do {
          piVar8 = piVar8 + 1;
          iVar17 = iVar17 + iVar21 + 0x200;
          puVar24 = puVar23 + 1;
          uVar16 = (ushort)(iVar17 >> 10);
          if (iVar17 >> 0x19 != iVar17 >> 0x1f) {
            uVar16 = (ushort)(iVar17 >> 0x1f) ^ 0x7fff;
          }
          *puVar23 = uVar16;
          *piVar13 = 0;
          iVar17 = *piVar8;
          iVar21 = piVar13[1];
          piVar13 = piVar13 + 1;
          puVar23 = puVar24;
        } while (puVar24 != puVar5);
      }
      iVar6 = iVar6 + -1;
      param_8 = param_8 + -1;
      piVar7 = piVar7 + -0x80;
      psVar10 = psVar10 + -0x100;
      puVar5 = puVar9;
    } while (iVar6 != -1);
    iVar6 = *(int *)(param_1 + 0x1d00);
    iVar17 = param_2[0x1c0];
    piVar7 = param_2 + 0x1c1;
    piVar18 = (int *)(param_1 + 0x1d04);
    puVar5 = param_3 + 0x1c0;
    do {
      iVar6 = iVar17 + iVar6 + 0x200;
      puVar9 = puVar5 + 1;
      uVar16 = (ushort)(iVar6 >> 10);
      if (iVar6 >> 0x19 != iVar6 >> 0x1f) {
        uVar16 = (ushort)(iVar6 >> 0x1f) ^ 0x7fff;
      }
      *puVar5 = uVar16;
      iVar6 = *piVar18;
      iVar17 = *piVar7;
      piVar7 = piVar7 + 1;
      piVar18 = piVar18 + 1;
      puVar5 = puVar9;
    } while (param_3 + 0x240 != puVar9);
    iVar6 = *param_2;
    puVar5 = param_3;
    piVar7 = param_2;
    do {
      piVar7 = piVar7 + 1;
      iVar6 = iVar6 + 0x200;
      puVar9 = puVar5 + 1;
      uVar16 = (ushort)(iVar6 >> 10);
      if (iVar6 >> 0x19 != iVar6 >> 0x1f) {
        uVar16 = (ushort)(iVar6 >> 0x1f) ^ 0x7fff;
      }
      *puVar5 = uVar16;
      iVar6 = *piVar7;
      puVar5 = puVar9;
    } while (param_3 + 0x1c0 != puVar9);
    piVar7 = param_2;
    do {
      iVar6 = *piVar14;
      piVar14 = piVar14 + 1;
      *piVar7 = iVar6;
      piVar7 = piVar7 + 1;
    } while ((int *)(param_1 + 0x1900) != piVar14);
    param_2 = param_2 + 0x240;
    uVar11 = 0x700;
  }
  else {
    iVar6 = imdct_fxp(param_1,param_9,0x800,param_7,*param_8);
    if (iVar6 < 0x10) {
      piVar14 = (int *)(param_1 + 0x800);
      uVar12 = iVar6 + 5;
      if (param_4 != 1) {
        if (param_4 == 3) {
          uVar28 = iVar6 - 10;
          iVar21 = param_2[0x240];
          iVar17 = (int)*(short *)(param_1 + 0x480);
          piVar7 = param_2 + 0x241;
          puVar5 = param_3 + 0x240;
          psVar10 = (short *)(param_1 + 0x482);
          if ((int)uVar28 < 1) {
            if (uVar28 == 0) {
              puVar9 = puVar5;
              do {
                iVar6 = iVar17 + iVar21 + 0x200;
                psVar15 = psVar10 + 1;
                uVar16 = (ushort)(iVar6 >> 10);
                if (iVar6 >> 0x19 != iVar6 >> 0x1f) {
                  uVar16 = (ushort)(iVar6 >> 0x1f) ^ 0x7fff;
                }
                *puVar9 = uVar16;
                iVar17 = (int)*psVar10;
                iVar21 = *piVar7;
                puVar9 = puVar9 + 1;
                psVar10 = psVar15;
                piVar7 = piVar7 + 1;
              } while (psVar15 != (short *)(param_1 + 0x802));
            }
            else {
              iVar17 = iVar17 << (10U - iVar6 & 0x1f);
              puVar9 = puVar5;
              do {
                iVar17 = iVar17 + iVar21 + 0x200;
                puVar23 = puVar9 + 1;
                uVar16 = (ushort)(iVar17 >> 10);
                if (iVar17 >> 0x1f != iVar17 >> 0x19) {
                  uVar16 = (ushort)(iVar17 >> 0x1f) ^ 0x7fff;
                }
                *puVar9 = uVar16;
                iVar21 = *piVar7;
                iVar17 = (int)*psVar10 << (10U - iVar6 & 0x1f);
                puVar9 = puVar23;
                psVar10 = psVar10 + 1;
                piVar7 = piVar7 + 1;
              } while (puVar23 != param_3 + 0x400);
            }
          }
          else {
            iVar17 = iVar17 >> (uVar28 & 0x1f);
            puVar9 = puVar5;
            do {
              iVar6 = iVar17 + iVar21 + 0x200;
              puVar23 = puVar9 + 1;
              uVar16 = (ushort)(iVar6 >> 10);
              if (iVar6 >> 0x1f != iVar6 >> 0x19) {
                uVar16 = (ushort)(iVar6 >> 0x1f) ^ 0x7fff;
              }
              *puVar9 = uVar16;
              iVar21 = *piVar7;
              iVar17 = (int)*psVar10 >> (uVar28 & 0x1f);
              puVar9 = puVar23;
              psVar10 = psVar10 + 1;
              piVar7 = piVar7 + 1;
            } while (puVar23 != param_3 + 0x400);
          }
          psVar10 = (short *)(apuStack_50[param_5 + 2] + 0x80);
          puVar9 = param_3 + 0x200;
          piVar7 = param_2 + 0x200;
          psVar15 = (short *)(param_1 + 0x400);
          do {
            iVar6 = ((int)psVar10[-0x40] * (int)psVar15[-0x40] >> (uVar12 & 0x1f)) + piVar7[-0x40] +
                    0x200;
            uVar16 = (ushort)(iVar6 >> 10);
            if (iVar6 >> 0x1f != iVar6 >> 0x19) {
              uVar16 = (ushort)(iVar6 >> 0x1f) ^ 0x7fff;
            }
            puVar9[-0x40] = uVar16;
            puVar23 = puVar9 + 1;
            iVar6 = ((int)*psVar10 * (int)*psVar15 >> (uVar12 & 0x1f)) + *piVar7 + 0x200;
            uVar16 = (ushort)(iVar6 >> 10);
            if (iVar6 >> 0x1f != iVar6 >> 0x19) {
              uVar16 = (ushort)(iVar6 >> 0x1f) ^ 0x7fff;
            }
            *puVar9 = uVar16;
            psVar10 = psVar10 + 1;
            puVar9 = puVar23;
            piVar7 = piVar7 + 1;
            psVar15 = psVar15 + 1;
          } while (puVar23 != puVar5);
          puVar19 = apuStack_50[param_6];
          puVar5 = param_3;
          psVar10 = (short *)(puVar19 + 0x7fe);
          piVar7 = param_2;
          do {
            iVar17 = *piVar7 + 0x200;
            puVar9 = puVar5 + 1;
            uVar16 = (ushort)(iVar17 >> 10);
            sVar1 = *psVar10;
            iVar6 = *piVar14;
            if (iVar17 >> 0x1f != iVar17 >> 0x19) {
              uVar16 = (ushort)(iVar17 >> 0x1f) ^ 0x7fff;
            }
            *puVar5 = uVar16;
            *piVar7 = (int)sVar1 * (int)(short)iVar6 >> (uVar12 & 0x1f);
            puVar5 = puVar9;
            piVar14 = (int *)((int)piVar14 + 2);
            psVar10 = psVar10 + -1;
            piVar7 = piVar7 + 1;
          } while (puVar9 != param_3 + 0x1c0);
          psVar10 = (short *)(puVar19 + 0x47e);
          psVar15 = (short *)(param_1 + 0xb80);
          piVar14 = param_2 + 0x1c0;
          do {
            sVar1 = *psVar15;
            sVar2 = *psVar10;
            psVar15 = psVar15 + 1;
            psVar10 = psVar10 + -1;
            *piVar14 = (int)sVar2 * (int)sVar1 >> (uVar12 & 0x1f);
            piVar14 = piVar14 + 1;
          } while ((short *)(param_1 + 0x1000) != psVar15);
        }
        else {
          piVar7 = (int *)apuStack_50[param_5];
          psVar10 = (short *)(apuStack_50[param_6] + 0x7fe);
          do {
            iVar17 = *piVar7;
            piVar7 = piVar7 + 1;
            piVar18 = piVar14 + 1;
            iVar6 = ((int)(short)iVar17 * (int)(short)piVar14[-0x200] >> (uVar12 & 0x1f)) + *param_2
                    + 0x200;
            uVar16 = (ushort)(iVar6 >> 10);
            iVar17 = ((iVar17 >> 0x10) * (piVar14[-0x200] >> 0x10) >> (uVar12 & 0x1f)) + param_2[1]
                     + 0x200;
            if (iVar6 >> 0x1f != iVar6 >> 0x19) {
              uVar16 = (ushort)(iVar6 >> 0x1f) ^ 0x7fff;
            }
            *param_3 = uVar16;
            uVar16 = (ushort)(iVar17 >> 10);
            if (iVar17 >> 0x1f != iVar17 >> 0x19) {
              uVar16 = (ushort)(iVar17 >> 0x1f) ^ 0x7fff;
            }
            iVar6 = *piVar14;
            param_3[1] = uVar16;
            sVar1 = *psVar10;
            sVar2 = psVar10[-1];
            psVar10 = psVar10 + -2;
            *param_2 = (int)sVar1 * (int)(short)iVar6 >> (uVar12 & 0x1f);
            param_2[1] = (int)sVar2 * (iVar6 >> 0x10) >> (uVar12 & 0x1f);
            param_3 = param_3 + 2;
            piVar14 = piVar18;
            param_2 = param_2 + 2;
          } while (piVar18 != (int *)(param_1 + 0x1000));
        }
        return;
      }
      psVar15 = (short *)(param_1 + 0x400);
      puVar5 = param_3 + 0x200;
      piVar7 = param_2 + 0x200;
      psVar10 = (short *)(apuStack_50[param_5] + 0x400);
      do {
        psVar20 = psVar15 + -0x200;
        sVar1 = *psVar15;
        psVar15 = psVar15 + 1;
        iVar17 = ((int)psVar10[-0x200] * (int)*psVar20 >> (uVar12 & 0x1f)) + piVar7[-0x200] + 0x200;
        uVar16 = (ushort)(iVar17 >> 10);
        if (iVar17 >> 0x1f != iVar17 >> 0x19) {
          uVar16 = (ushort)(iVar17 >> 0x1f) ^ 0x7fff;
        }
        iVar17 = ((int)*psVar10 * (int)sVar1 >> (uVar12 & 0x1f)) + *piVar7 + 0x200;
        puVar5[-0x200] = uVar16;
        puVar9 = puVar5 + 1;
        uVar16 = (ushort)(iVar17 >> 10);
        if (iVar17 >> 0x1f != iVar17 >> 0x19) {
          uVar16 = (ushort)(iVar17 >> 0x1f) ^ 0x7fff;
        }
        *puVar5 = uVar16;
        puVar5 = puVar9;
        piVar7 = piVar7 + 1;
        psVar10 = psVar10 + 1;
      } while (puVar9 != param_3 + 0x400);
      uVar28 = iVar6 - 10;
      if ((int)uVar28 < 0) {
        piVar7 = param_2;
        do {
          piVar18 = piVar14 + 1;
          sVar1 = *(short *)((int)piVar14 + 2);
          *piVar7 = (int)(short)*piVar14 << (10U - iVar6 & 0x1f);
          piVar7[1] = (int)sVar1 << (10U - iVar6 & 0x1f);
          piVar14 = piVar18;
          piVar7 = piVar7 + 2;
        } while ((int *)(param_1 + 0xb80) != piVar18);
      }
      else {
        piVar7 = param_2;
        do {
          piVar18 = piVar14 + 1;
          sVar1 = *(short *)((int)piVar14 + 2);
          *piVar7 = (int)(short)*piVar14 >> (uVar28 & 0x1f);
          piVar7[1] = (int)sVar1 >> (uVar28 & 0x1f);
          piVar14 = piVar18;
          piVar7 = piVar7 + 2;
        } while ((int *)(param_1 + 0xb80) != piVar18);
      }
      psVar15 = (short *)(param_1 + 0xb80);
      psVar10 = (short *)(apuStack_50[param_6 + 2] + 0xfe);
      piVar14 = param_2 + 0x1c0;
      do {
        psVar20 = psVar15 + 0x40;
        psVar25 = psVar10 + -0x40;
        sVar1 = *psVar15;
        sVar2 = *psVar10;
        psVar15 = psVar15 + 1;
        psVar10 = psVar10 + -1;
        piVar14[0x40] = (int)*psVar25 * (int)*psVar20 >> (uVar12 & 0x1f);
        *piVar14 = (int)sVar2 * (int)sVar1 >> (uVar12 & 0x1f);
        piVar14 = piVar14 + 1;
      } while ((short *)(param_1 + 0xc00) != psVar15);
      param_2 = param_2 + 0x240;
      uVar11 = 0x700;
    }
    else {
      iVar6 = *param_2;
      piVar14 = param_2 + 1;
      do {
        iVar6 = iVar6 + 0x200;
        piVar7 = piVar14 + 1;
        uVar16 = (ushort)(iVar6 >> 10);
        if (iVar6 >> 0x19 != iVar6 >> 0x1f) {
          uVar16 = (ushort)(iVar6 >> 0x1f) ^ 0x7fff;
        }
        *param_3 = uVar16;
        iVar6 = *piVar14;
        param_3 = param_3 + 1;
        piVar14 = piVar7;
      } while (param_2 + 0x401 != piVar7);
      uVar11 = 0x1000;
    }
  }
  memset(param_2,0,uVar11);
  return;
}
