/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: imdct_fxp @ ram:420453b6
 * Types and parameter counts are inferred; verify against disassembly. */

int imdct_fxp(uint *param_1,uint *param_2,int param_3,int param_4,uint param_5)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  uint *puVar7;
  uint *puVar8;
  uint uVar9;
  int iVar10;
  uint uVar11;
  uint uVar12;
  uint uVar13;
  uint uVar14;
  uint uVar15;
  uint *puVar16;
  uint *puVar17;
  int iVar18;
  uint *puVar19;
  uint uVar20;
  uint uStack_24;

  gp = &__global_pointer_;
  if (param_5 == 0) {
    return 0x1f;
  }
  if (param_3 == 0x100) {
    puVar16 = &exp_rotation_N_256;
    iVar18 = 0x15;
  }
  else {
    if (param_3 != 0x800) {
      return 10;
    }
    puVar16 = &exp_rotation_N_2048;
    iVar18 = 0x18;
  }
  puVar8 = param_1 + (param_3 >> 1) + 0x3fffffff;
  uStack_24 = param_5;
  iVar5 = pv_normalize(param_5);
  uVar6 = iVar5 - 1;
  uVar9 = *param_1;
  uVar1 = *puVar8;
  if ((int)uVar6 < 0) {
    puVar19 = puVar16 + (param_3 >> 3);
    uStack_24 = 0;
    puVar7 = param_1 + 1;
    puVar8 = puVar8 + -1;
    puVar17 = puVar16 + (param_3 >> 2) + 0x3fffffff;
    do {
      uVar13 = *puVar8;
      uVar12 = *puVar16 & 0xffff0000;
      iVar5 = *puVar16 << 0x10;
      uVar20 = *puVar7;
      puVar16 = puVar16 + 1;
      uVar11 = -((int)((ulonglong)((longlong)((int)uVar9 >> 1) * (longlong)(int)uVar12) >> 0x20) +
                (int)((ulonglong)((longlong)((int)uVar1 >> 1) * (longlong)iVar5) >> 0x20));
      *puVar7 = uVar11;
      uVar14 = (int)((ulonglong)((longlong)((int)uVar1 >> 1) * (longlong)(int)uVar12) >> 0x20) +
               (int)((ulonglong)((longlong)-((int)uVar9 >> 1) * (longlong)iVar5) >> 0x20);
      puVar7[-1] = uVar14;
      uVar12 = *puVar17 & 0xffff0000;
      iVar5 = *puVar17 << 0x10;
      uVar9 = puVar7[1];
      uVar1 = puVar8[-1];
      uVar15 = -((int)((ulonglong)((longlong)((int)uVar13 >> 1) * (longlong)(int)uVar12) >> 0x20) +
                (int)((ulonglong)((longlong)((int)uVar20 >> 1) * (longlong)iVar5) >> 0x20));
      puVar8[1] = uVar15;
      uVar12 = (int)((ulonglong)((longlong)((int)uVar20 >> 1) * (longlong)(int)uVar12) >> 0x20) +
               (int)((ulonglong)((longlong)-((int)uVar13 >> 1) * (longlong)iVar5) >> 0x20);
      *puVar8 = uVar12;
      uStack_24 = uStack_24 |
                  (int)uVar14 >> 0x1f ^ uVar14 | uVar11 ^ (int)uVar11 >> 0x1f |
                  (int)uVar12 >> 0x1f ^ uVar12 | (int)uVar15 >> 0x1f ^ uVar15;
      puVar7 = puVar7 + 2;
      puVar8 = puVar8 + -2;
      puVar17 = puVar17 + -1;
    } while (puVar16 != puVar19);
  }
  else {
    puVar19 = puVar16 + (param_3 >> 3);
    iVar10 = uVar9 << (uVar6 & 0x1f);
    iVar5 = uVar1 << (uVar6 & 0x1f);
    uStack_24 = 0;
    puVar7 = param_1 + 1;
    puVar8 = puVar8 + -1;
    puVar17 = puVar16 + (param_3 >> 2) + 0x3fffffff;
    do {
      uVar1 = *puVar16 & 0xffff0000;
      iVar2 = *puVar16 << 0x10;
      iVar3 = *puVar8 << (uVar6 & 0x1f);
      iVar4 = *puVar7 << (uVar6 & 0x1f);
      puVar16 = puVar16 + 1;
      uVar9 = -((int)((ulonglong)((longlong)iVar10 * (longlong)(int)uVar1) >> 0x20) +
               (int)((ulonglong)((longlong)iVar5 * (longlong)iVar2) >> 0x20));
      *puVar7 = uVar9;
      uVar12 = (int)((ulonglong)((longlong)iVar5 * (longlong)(int)uVar1) >> 0x20) +
               (int)((ulonglong)((longlong)-iVar10 * (longlong)iVar2) >> 0x20);
      puVar7[-1] = uVar12;
      uVar1 = *puVar17 & 0xffff0000;
      iVar2 = *puVar17 << 0x10;
      iVar10 = puVar7[1] << (uVar6 & 0x1f);
      iVar5 = puVar8[-1] << (uVar6 & 0x1f);
      uVar13 = -((int)((ulonglong)((longlong)iVar3 * (longlong)(int)uVar1) >> 0x20) +
                (int)((ulonglong)((longlong)iVar4 * (longlong)iVar2) >> 0x20));
      puVar8[1] = uVar13;
      uVar1 = (int)((ulonglong)((longlong)iVar4 * (longlong)(int)uVar1) >> 0x20) +
              (int)((ulonglong)((longlong)-iVar3 * (longlong)iVar2) >> 0x20);
      *puVar8 = uVar1;
      uStack_24 = uStack_24 |
                  (int)uVar12 >> 0x1f ^ uVar12 | (int)uVar9 >> 0x1f ^ uVar9 |
                  (int)uVar1 >> 0x1f ^ uVar1 | (int)uVar13 >> 0x1f ^ uVar13;
      puVar7 = puVar7 + 2;
      puVar8 = puVar8 + -2;
      puVar17 = puVar17 + -1;
    } while (puVar19 != puVar16);
  }
  if (param_3 == 0x100) {
    iVar5 = fft_rx4_short(param_1,&uStack_24);
    iVar10 = inv_short_complex_rot(param_1,param_2,uStack_24);
    puVar16 = param_2 + 0x80;
    do {
      uVar1 = *param_2;
      uVar9 = param_2[1];
      param_1[2] = param_2[2];
      *param_1 = uVar1;
      param_1[1] = uVar9;
      puVar8 = param_2 + 3;
      param_2 = param_2 + 4;
      param_1[3] = *puVar8;
      param_1 = param_1 + 4;
    } while (param_2 != puVar16);
  }
  else {
    iVar5 = mix_radix_fft();
    iVar10 = inv_long_complex_rot(param_1,uStack_24);
  }
  return ((iVar18 - iVar5) - iVar10) + uVar6 + param_4 + -0x10;
}
