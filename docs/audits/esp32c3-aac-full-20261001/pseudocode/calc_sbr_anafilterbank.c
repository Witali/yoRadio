/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: calc_sbr_anafilterbank @ ram:43001826
 * Types and parameter counts are inferred; verify against disassembly. */

void calc_sbr_anafilterbank(uint *param_1,uint *param_2,short *param_3,uint *param_4,int param_5)

{
  short sVar1;
  short sVar2;
  short sVar3;
  short sVar4;
  short sVar5;
  uint *puVar6;
  uint *puVar7;
  short *psVar8;
  short *psVar9;
  uint uVar10;
  uint *puVar11;
  uint *puVar12;
  uint uVar13;
  uint uVar14;
  uint *puVar15;
  uint uVar16;
  int *piVar17;
  int iVar18;
  int iVar19;
  int iVar20;
  int iVar21;
  int iVar22;
  uint *puVar23;
  uint *puVar24;

  gp = &__global_pointer_;
  piVar17 = &sbrDecoderFilterbankCoefficients_an_filt;
  psVar9 = param_3 + -0x13f;
  *param_4 = (int)((ulonglong)((longlong)((int)param_3[-0x80] << 0x10) * 0x2e3a754) >> 0x20) +
             (int)((ulonglong)((longlong)((int)param_3[-0xc0] << 0x10) * -0x2e3a754) >> 0x20) +
             (int)((ulonglong)((longlong)((int)param_3[-0x100] << 0x10) * -0x1b2e42) >> 0x20) +
             (int)((ulonglong)((longlong)((int)param_3[-0x40] << 0x10) * 0x1b2e42) >> 0x20);
  puVar12 = param_4 + 0x3f;
  psVar8 = param_3;
  puVar11 = param_4;
  do {
    puVar11 = puVar11 + 1;
    iVar22 = piVar17[1];
    iVar21 = *piVar17;
    sVar1 = psVar9[0x40];
    sVar2 = *psVar9;
    iVar20 = piVar17[2];
    sVar3 = psVar9[0x80];
    iVar19 = piVar17[3];
    sVar4 = psVar9[0xc0];
    iVar18 = piVar17[4];
    sVar5 = psVar9[0x100];
    piVar17 = piVar17 + 5;
    psVar9 = psVar9 + 1;
    *puVar11 = (int)((ulonglong)((longlong)((int)psVar8[-0x41] << 0x10) * (longlong)iVar22) >> 0x20)
               + (int)((ulonglong)((longlong)((int)psVar8[-1] << 0x10) * (longlong)iVar21) >> 0x20)
               + (int)((ulonglong)((longlong)((int)psVar8[-0x81] << 0x10) * (longlong)iVar20) >>
                      0x20) +
               (int)((ulonglong)((longlong)((int)psVar8[-0xc1] << 0x10) * (longlong)iVar19) >> 0x20)
               + (int)((ulonglong)((longlong)((int)psVar8[-0x101] << 0x10) * (longlong)iVar18) >>
                      0x20);
    *puVar12 = (int)((ulonglong)((longlong)((int)sVar1 << 0x10) * (longlong)iVar22) >> 0x20) +
               (int)((ulonglong)((longlong)((int)sVar2 << 0x10) * (longlong)iVar21) >> 0x20) +
               (int)((ulonglong)((longlong)((int)sVar3 << 0x10) * (longlong)iVar20) >> 0x20) +
               (int)((ulonglong)((longlong)((int)sVar4 << 0x10) * (longlong)iVar19) >> 0x20) +
               (int)((ulonglong)((longlong)((int)sVar5 << 0x10) * (longlong)iVar18) >> 0x20);
    puVar12 = puVar12 + -1;
    psVar8 = psVar8 + -1;
  } while (piVar17 != &sbrDecoderFilterbankCoefficients_an_filt_LC);
  puVar15 = param_4 + 0x40;
  param_4[0x20] =
       (int)((ulonglong)((longlong)((int)param_3[-0x120] << 0x10) * 0x55dba) >> 0x20) +
       (int)((ulonglong)((longlong)((int)param_3[-0x20] << 0x10) * 0x55dba) >> 0x20) +
       (int)((ulonglong)((longlong)((int)param_3[-0x60] << 0x10) * 0x901566) >> 0x20) +
       (int)((ulonglong)((longlong)((int)param_3[-0xe0] << 0x10) * 0x901566) >> 0x20) +
       (int)((ulonglong)((longlong)((int)param_3[-0xa0] << 0x10) * 0x6d474e0) >> 0x20);
  puVar11 = puVar15;
  puVar12 = param_4;
  do {
    uVar16 = *puVar12;
    uVar14 = puVar12[1];
    puVar11[2] = puVar12[2];
    *puVar11 = uVar16;
    puVar11[1] = uVar14;
    puVar23 = puVar12 + 3;
    puVar12 = puVar12 + 4;
    puVar11[3] = *puVar23;
    puVar11 = puVar11 + 4;
  } while (puVar12 != param_4 + 0x40);
  mdst_32(puVar15,param_4 + 0x80);
  mdst_32(param_4 + 0x60,param_4 + 0x80);
  mdct_32(param_4);
  mdct_32(param_4 + 0x20);
  if (0 < param_5) {
    uVar13 = *param_4;
    uVar16 = uVar13 - param_4[0x60];
    uVar14 = ((int)uVar13 >> 0x1f) - ((int)param_4[0x60] >> 0x1f);
    iVar18 = uVar14 - (uVar13 < uVar16);
    if ((iVar18 < -1) || ((iVar18 == -1 && (-1 < (int)uVar16)))) {
      uVar16 = 0x80000000;
    }
    else if ((0 < iVar18) || ((uVar14 == uVar13 < uVar16 && ((int)uVar16 < 0)))) {
      uVar16 = 0x7fffffff;
    }
    uVar14 = *puVar15;
    uVar13 = param_4[0x20] + uVar14;
    iVar18 = (uint)(uVar13 < uVar14) + ((int)uVar14 >> 0x1f) + ((int)param_4[0x20] >> 0x1f);
    puVar11 = param_4 + 0x21;
    if ((iVar18 < -1) || ((iVar18 == -1 && (-1 < (int)uVar13)))) {
      uVar13 = 0x80000000;
    }
    else if ((0 < iVar18) || ((iVar18 == 0 && ((int)uVar13 < 0)))) {
      uVar13 = 0x7fffffff;
    }
    iVar18 = 0;
    puVar12 = &exp_1_5_phi;
    puVar15 = param_4 + 0x61;
    puVar23 = param_1;
    puVar24 = param_2;
    do {
      uVar14 = *puVar12 & 0xffff0000;
      iVar20 = *puVar12 << 0x10;
      iVar18 = iVar18 + 2;
      iVar19 = (int)((ulonglong)((longlong)(int)uVar14 * (longlong)(int)uVar16) >> 0x20) +
               (int)((ulonglong)((longlong)(int)uVar13 * (longlong)iVar20) >> 0x20);
      uVar10 = iVar19 * 2;
      iVar20 = (int)((ulonglong)((longlong)(int)uVar13 * (longlong)(int)uVar14) >> 0x20) +
               (int)((ulonglong)((longlong)(int)-uVar16 * (longlong)iVar20) >> 0x20);
      uVar14 = iVar20 * 2;
      if (iVar19 != (int)uVar10 >> 1) {
        uVar10 = iVar19 >> 0x1f ^ 0x7fffffff;
      }
      *puVar23 = uVar10;
      if (iVar20 != (int)uVar14 >> 1) {
        uVar14 = iVar20 >> 0x1f ^ 0x7fffffff;
      }
      *puVar24 = uVar14;
      uVar16 = puVar12[1] & 0xffff0000;
      iVar19 = puVar12[1] << 0x10;
      iVar20 = (int)((ulonglong)((longlong)(int)(puVar11[-0x20] + *puVar15) * (longlong)(int)uVar16)
                    >> 0x20) +
               (int)((ulonglong)((longlong)(int)(puVar15[-0x20] - *puVar11) * (longlong)iVar19) >>
                    0x20);
      uVar14 = iVar20 * 2;
      iVar19 = (int)((ulonglong)((longlong)(int)uVar16 * (longlong)(int)(puVar15[-0x20] - *puVar11))
                    >> 0x20) +
               (int)((ulonglong)((longlong)(int)-(puVar11[-0x20] + *puVar15) * (longlong)iVar19) >>
                    0x20);
      uVar16 = iVar19 * 2;
      if (iVar20 != (int)uVar14 >> 1) {
        uVar14 = iVar20 >> 0x1f ^ 0x7fffffff;
      }
      puVar23[1] = uVar14;
      if (iVar19 != (int)uVar16 >> 1) {
        uVar16 = iVar19 >> 0x1f ^ 0x7fffffff;
      }
      puVar24[1] = uVar16;
      puVar6 = puVar11 + -0x1f;
      puVar7 = puVar11 + 1;
      puVar11 = puVar11 + 2;
      uVar16 = *puVar6 - puVar15[1];
      uVar13 = puVar15[-0x1f] + *puVar7;
      puVar12 = puVar12 + 2;
      puVar15 = puVar15 + 2;
      puVar23 = puVar23 + 2;
      puVar24 = puVar24 + 2;
    } while (iVar18 < param_5);
    if (param_5 == 0x20) {
      return;
    }
  }
  puVar12 = param_1 + param_5;
  puVar11 = param_2 + param_5;
  param_5 = 0x20 - param_5;
  if ((puVar12 < param_2 + 0x20) && (puVar11 < param_1 + 0x20)) {
    do {
      *puVar12 = 0;
      *puVar11 = 0;
      param_5 = param_5 + -1;
      puVar12 = puVar12 + 1;
      puVar11 = puVar11 + 1;
    } while (param_5 != 0);
    return;
  }
  memset(puVar12,0,param_5 * 4);
  memset(puVar11,0,param_5 * 4);
  return;
}
