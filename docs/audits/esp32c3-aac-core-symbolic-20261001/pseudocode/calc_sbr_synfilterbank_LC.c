/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: calc_sbr_synfilterbank_LC @ ram:4301645a
 * Types and parameter counts are inferred; verify against disassembly. */

void calc_sbr_synfilterbank_LC(int *param_1,ushort *param_2,short *param_3,int param_4)

{
  short sVar1;
  short sVar2;
  short sVar3;
  int *piVar4;
  short *psVar5;
  int iVar6;
  int iVar7;
  ushort *puVar8;
  int *piVar9;
  int *piVar10;
  short *psVar11;
  ushort uVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  int iVar16;
  int iVar17;
  int *piVar18;
  int iVar19;
  int iVar20;
  int iVar21;
  int iVar22;
  int *piVar23;
  int *piVar24;

  gp = &__global_pointer_;
  if (param_4 != 0) {
    synthesis_sub_band_LC_down_sampled(param_1,param_3);
    piVar24 = param_1 + 0x20;
    piVar10 = param_1;
    do {
      *piVar10 = 0;
      piVar10[1] = 0;
      piVar10[2] = 0;
      piVar10[3] = 0;
      piVar10 = piVar10 + 4;
    } while (piVar10 != piVar24);
    piVar10 = (int *)&UNK_ram_4301c76c;
    do {
      piVar23 = piVar10 + -0x20;
      psVar5 = param_3;
      piVar9 = param_1;
      piVar4 = piVar10 + -0x10;
      psVar11 = param_3 + 0x60;
      do {
        piVar18 = piVar4;
        iVar13 = *piVar23;
        iVar15 = *piVar18;
        sVar1 = *psVar5;
        sVar2 = psVar5[1];
        sVar3 = psVar11[1];
        psVar5 = psVar5 + 2;
        piVar23 = piVar23 + 1;
        *piVar9 = ((iVar15 >> 0x10) * (int)*psVar11 + (iVar13 >> 0x10) * (int)sVar1 >> 5) + *piVar9;
        piVar9[1] = ((int)sVar3 * (int)(short)iVar15 + (int)(short)iVar13 * (int)sVar2 >> 5) +
                    piVar9[1];
        piVar9 = piVar9 + 2;
        piVar4 = piVar18 + 1;
        psVar11 = psVar11 + 2;
      } while (piVar18 + 1 != piVar10);
      piVar10 = piVar18 + 0x21;
      param_3 = param_3 + 0x80;
    } while (piVar10 != (int *)&UNK_ram_4301c9ec);
    do {
      iVar13 = *param_1;
      param_1 = param_1 + 1;
      *param_2 = (ushort)(iVar13 + 0x200 >> 10);
      param_2 = param_2 + 2;
    } while (param_1 != piVar24);
    return;
  }
  synthesis_sub_band_LC(param_1,param_3);
  iVar13 = param_3[0x2c0] * 0x796c + 0x9000 + param_3[0x300] * -0x335d +
           ((int)((uint)(ushort)param_3[0x200] * -0x10000) >> 0x10) * -0x335d +
           param_3[0x3c0] * 0xa01 + param_3[0x1c0] * 0xa01 + param_3[0x400] * -0x1e3 +
           ((int)((uint)(ushort)param_3[0x100] * -0x10000) >> 0x10) * -0x1e3 + param_3[0xc0] * 0x5f
           + param_3[0x4c0] * 0x5f;
  iVar13 = iVar13 - (iVar13 >> 2);
  iVar15 = param_3[0x20] * -0x18 + 0x9000 + param_3[0x4e0] * -0x18 + param_3[0xe0] * 0xc0 +
           param_3[0x420] * 0xc0 + param_3[0x3e0] * 0x855 + param_3[0x120] * 0x855 +
           param_3[0x1e0] * -0x84d + param_3[800] * -0x84d + param_3[0x2e0] * 0x63e0 +
           param_3[0x220] * 0x63e0;
  if (iVar13 >> 0x1d == iVar13 >> 0x1f) {
    *param_2 = (ushort)(iVar13 >> 0xe);
    iVar15 = iVar15 - (iVar15 >> 2);
    iVar13 = iVar15 >> 0x1f;
    if (iVar15 >> 0x1d == iVar13) goto LAB_ram_43016890;
  }
  else {
    *param_2 = (ushort)(iVar13 >> 0x1f) ^ 0x7fff;
    iVar15 = iVar15 - (iVar15 >> 2);
    iVar13 = iVar15 >> 0x1f;
    if (iVar15 >> 0x1d == iVar13) {
LAB_ram_43016890:
      uVar12 = (ushort)(iVar15 >> 0xe);
      goto LAB_ram_430165ea;
    }
  }
  uVar12 = (ushort)iVar13 ^ 0x7fff;
LAB_ram_430165ea:
  param_2[0x40] = uVar12;
  puVar8 = param_2 + 0x7e;
  piVar10 = &sbrDecoderFilterbankCoefficients;
  psVar5 = param_3 + 0x401;
  psVar11 = param_3 + 0x43f;
  do {
    param_2 = param_2 + 2;
    iVar13 = *piVar10 >> 0x10;
    iVar22 = (int)(short)*piVar10;
    iVar15 = piVar10[1] >> 0x10;
    iVar7 = (int)(short)piVar10[1];
    iVar21 = piVar10[2] >> 0x10;
    iVar20 = (int)(short)piVar10[2];
    piVar24 = piVar10 + 4;
    iVar17 = piVar10[3] >> 0x10;
    iVar19 = (int)(short)piVar10[3];
    piVar10 = piVar10 + 5;
    iVar16 = *piVar24 >> 0x10;
    iVar6 = (int)(short)*piVar24;
    iVar14 = psVar5[-0x200] * iVar21 +
             psVar5[-0x400] * iVar13 + 0x9000 + psVar5[-0x340] * iVar22 + psVar5[-0x300] * iVar15 +
             psVar5[-0x240] * iVar7 + psVar5[-0x140] * iVar20 + psVar5[-0x100] * iVar17 +
             psVar5[-0x40] * iVar19 + *psVar5 * iVar16 + psVar5[0xc0] * iVar6;
    iVar14 = iVar14 - (iVar14 >> 2);
    uVar12 = (ushort)(iVar14 >> 0x1f) ^ 0x7fff;
    iVar13 = psVar11[0xc0] * iVar13 + 0x9000 + *psVar11 * iVar22 + psVar11[-0x40] * iVar15 +
             psVar11[-0x100] * iVar7 + psVar11[-0x140] * iVar21 + psVar11[-0x200] * iVar20 +
             psVar11[-0x240] * iVar17 + psVar11[-0x300] * iVar19 + psVar11[-0x340] * iVar16 +
             psVar11[-0x400] * iVar6;
    iVar13 = iVar13 - (iVar13 >> 2);
    if (iVar14 >> 0x1f == iVar14 >> 0x1d) {
      uVar12 = (ushort)(iVar14 >> 0xe);
    }
    *param_2 = uVar12;
    uVar12 = (ushort)(iVar13 >> 0x1f) ^ 0x7fff;
    if (iVar13 >> 0x1f == iVar13 >> 0x1d) {
      uVar12 = (ushort)(iVar13 >> 0xe);
    }
    *puVar8 = uVar12;
    puVar8 = puVar8 + -2;
    psVar5 = psVar5 + 1;
    psVar11 = psVar11 + -1;
  } while (piVar10 != (int *)bookSbrNoiseBalance11T);
  return;
}
