/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: calc_sbr_synfilterbank @ ram:43016896
 * Types and parameter counts are inferred; verify against disassembly. */

void calc_sbr_synfilterbank
               (int *param_1,undefined4 param_2,ushort *param_3,short *param_4,int param_5)

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
  int *piVar12;
  ushort uVar13;
  int iVar14;
  int iVar15;
  int iVar16;
  int iVar17;
  int iVar18;
  int *piVar19;
  int iVar20;
  int iVar21;
  int iVar22;
  int iVar23;
  int *piVar24;

  gp = &__global_pointer_;
  if (param_5 != 0) {
    synthesis_sub_band_down_sampled(param_1,param_2,param_4);
    piVar24 = param_1 + 0x20;
    piVar9 = param_1;
    do {
      *piVar9 = 0;
      piVar9[1] = 0;
      piVar9[2] = 0;
      piVar9[3] = 0;
      piVar9 = piVar9 + 4;
    } while (piVar9 != piVar24);
    piVar9 = (int *)&UNK_ram_4301c76c;
    do {
      piVar12 = piVar9 + -0x20;
      psVar5 = param_4;
      piVar10 = param_1;
      piVar4 = piVar9 + -0x10;
      psVar11 = param_4 + 0x60;
      do {
        piVar19 = piVar4;
        iVar14 = *piVar12;
        iVar16 = *piVar19;
        sVar1 = *psVar5;
        sVar2 = psVar5[1];
        sVar3 = psVar11[1];
        psVar5 = psVar5 + 2;
        piVar12 = piVar12 + 1;
        *piVar10 = ((iVar16 >> 0x10) * (int)*psVar11 + (iVar14 >> 0x10) * (int)sVar1 >> 5) +
                   *piVar10;
        piVar10[1] = ((int)sVar3 * (int)(short)iVar16 + (int)(short)iVar14 * (int)sVar2 >> 5) +
                     piVar10[1];
        piVar10 = piVar10 + 2;
        piVar4 = piVar19 + 1;
        psVar11 = psVar11 + 2;
      } while (piVar19 + 1 != piVar9);
      piVar9 = piVar19 + 0x21;
      param_4 = param_4 + 0x80;
    } while (piVar9 != (int *)&UNK_ram_4301c9ec);
    do {
      iVar14 = *param_1;
      param_1 = param_1 + 1;
      *param_3 = (ushort)(iVar14 + 0x200 >> 10);
      param_3 = param_3 + 2;
    } while (param_1 != piVar24);
    return;
  }
  synthesis_sub_band(param_1,param_2,param_4);
  iVar14 = param_4[0x2c0] * 0x796c + 0x9000 + param_4[0x300] * -0x335d +
           ((int)((uint)(ushort)param_4[0x200] * -0x10000) >> 0x10) * -0x335d +
           param_4[0x3c0] * 0xa01 + param_4[0x1c0] * 0xa01 + param_4[0x400] * -0x1e3 +
           ((int)((uint)(ushort)param_4[0x100] * -0x10000) >> 0x10) * -0x1e3 + param_4[0xc0] * 0x5f
           + param_4[0x4c0] * 0x5f;
  iVar14 = iVar14 - (iVar14 >> 2);
  iVar16 = param_4[0x20] * -0x18 + 0x9000 + param_4[0x4e0] * -0x18 + param_4[0xe0] * 0xc0 +
           param_4[0x420] * 0xc0 + param_4[0x3e0] * 0x855 + param_4[0x120] * 0x855 +
           param_4[0x1e0] * -0x84d + param_4[800] * -0x84d + param_4[0x2e0] * 0x63e0 +
           param_4[0x220] * 0x63e0;
  if (iVar14 >> 0x1d == iVar14 >> 0x1f) {
    *param_3 = (ushort)(iVar14 >> 0xe);
    iVar16 = iVar16 - (iVar16 >> 2);
    iVar14 = iVar16 >> 0x1f;
    if (iVar16 >> 0x1d == iVar14) goto LAB_ram_43016cca;
  }
  else {
    *param_3 = (ushort)(iVar14 >> 0x1f) ^ 0x7fff;
    iVar16 = iVar16 - (iVar16 >> 2);
    iVar14 = iVar16 >> 0x1f;
    if (iVar16 >> 0x1d == iVar14) {
LAB_ram_43016cca:
      uVar13 = (ushort)(iVar16 >> 0xe);
      goto LAB_ram_43016a26;
    }
  }
  uVar13 = (ushort)iVar14 ^ 0x7fff;
LAB_ram_43016a26:
  param_3[0x40] = uVar13;
  puVar8 = param_3 + 0x7e;
  piVar9 = &sbrDecoderFilterbankCoefficients;
  psVar5 = param_4 + 0x401;
  psVar11 = param_4 + 0x43f;
  do {
    param_3 = param_3 + 2;
    iVar14 = *piVar9 >> 0x10;
    iVar23 = (int)(short)*piVar9;
    iVar16 = piVar9[1] >> 0x10;
    iVar7 = (int)(short)piVar9[1];
    iVar22 = piVar9[2] >> 0x10;
    iVar21 = (int)(short)piVar9[2];
    piVar24 = piVar9 + 4;
    iVar18 = piVar9[3] >> 0x10;
    iVar20 = (int)(short)piVar9[3];
    piVar9 = piVar9 + 5;
    iVar17 = *piVar24 >> 0x10;
    iVar6 = (int)(short)*piVar24;
    iVar15 = psVar5[-0x200] * iVar22 +
             psVar5[-0x400] * iVar14 + 0x9000 + psVar5[-0x340] * iVar23 + psVar5[-0x300] * iVar16 +
             psVar5[-0x240] * iVar7 + psVar5[-0x140] * iVar21 + psVar5[-0x100] * iVar18 +
             psVar5[-0x40] * iVar20 + *psVar5 * iVar17 + psVar5[0xc0] * iVar6;
    iVar15 = iVar15 - (iVar15 >> 2);
    uVar13 = (ushort)(iVar15 >> 0x1f) ^ 0x7fff;
    iVar14 = psVar11[0xc0] * iVar14 + 0x9000 + *psVar11 * iVar23 + psVar11[-0x40] * iVar16 +
             psVar11[-0x100] * iVar7 + psVar11[-0x140] * iVar22 + psVar11[-0x200] * iVar21 +
             psVar11[-0x240] * iVar18 + psVar11[-0x300] * iVar20 + psVar11[-0x340] * iVar17 +
             psVar11[-0x400] * iVar6;
    iVar14 = iVar14 - (iVar14 >> 2);
    if (iVar15 >> 0x1f == iVar15 >> 0x1d) {
      uVar13 = (ushort)(iVar15 >> 0xe);
    }
    *param_3 = uVar13;
    uVar13 = (ushort)(iVar14 >> 0x1f) ^ 0x7fff;
    if (iVar14 >> 0x1f == iVar14 >> 0x1d) {
      uVar13 = (ushort)(iVar14 >> 0xe);
    }
    *puVar8 = uVar13;
    puVar8 = puVar8 + -2;
    psVar5 = psVar5 + 1;
    psVar11 = psVar11 + -1;
  } while (piVar9 != (int *)bookSbrNoiseBalance11T);
  return;
}
