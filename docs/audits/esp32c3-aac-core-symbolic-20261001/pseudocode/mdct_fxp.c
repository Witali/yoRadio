/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: mdct_fxp @ ram:4300b2b0
 * Types and parameter counts are inferred; verify against disassembly. */

int mdct_fxp(int *param_1,uint *param_2,int param_3)

{
  int *piVar1;
  int *piVar2;
  uint *puVar3;
  int *piVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  uint uVar8;
  int iVar9;
  int iVar10;
  int *piVar11;
  int *piVar12;
  int iVar13;
  int *piVar14;
  uint auStack_24 [4];

  gp = &__global_pointer_;
  if (param_3 == 0x100) {
    piVar4 = &exp_rotation_N_256;
  }
  else {
    if (param_3 != 0x800) {
      return 10;
    }
    piVar4 = &exp_rotation_N_2048;
  }
  iVar13 = param_3 >> 2;
  piVar2 = param_1 + iVar13 * 3 + -1;
  piVar14 = param_1 + iVar13 * 3;
  piVar1 = param_1 + iVar13 + -1;
  piVar12 = param_1 + iVar13;
  piVar11 = piVar4 + (param_3 >> 3);
  auStack_24[0] = 0;
  puVar3 = param_2;
  do {
    iVar7 = *piVar12 - *piVar1 >> 1;
    iVar10 = (int)(short)*piVar4;
    iVar5 = *piVar4 >> 0x10;
    iVar13 = *piVar14 + *piVar2 >> 1;
    piVar4 = piVar4 + 1;
    piVar14 = piVar14 + 2;
    piVar2 = piVar2 + -2;
    piVar12 = piVar12 + 2;
    piVar1 = piVar1 + -2;
    uVar6 = iVar5 * iVar7 - iVar10 * iVar13;
    uVar8 = iVar5 * iVar13 + iVar10 * iVar7;
    *puVar3 = uVar8;
    puVar3[1] = uVar6;
    auStack_24[0] = auStack_24[0] | (int)uVar8 >> 0x1f ^ uVar8 | (int)uVar6 >> 0x1f ^ uVar6;
    puVar3 = puVar3 + 2;
  } while (piVar4 != piVar11);
  iVar13 = (param_3 >> 3) + -1;
  piVar11 = param_1 + param_3 + 0x3fffffff;
  iVar5 = (int)(param_2 + iVar13 * 2) + (int)piVar11;
  piVar14 = param_1 + (param_3 >> 1) + 0x40000000;
  piVar2 = piVar14 + iVar13 * 2 + 2;
  piVar12 = param_1 + (param_3 >> 1) + 0x3fffffff;
  piVar1 = param_1;
  do {
    iVar9 = *piVar11 + *piVar14 >> 1;
    iVar13 = (int)(short)*piVar4;
    iVar10 = *piVar4 >> 0x10;
    iVar7 = *piVar12 - *piVar1 >> 1;
    puVar3 = (uint *)((iVar5 + 8) - (int)piVar11);
    piVar14 = piVar14 + 2;
    piVar4 = piVar4 + 1;
    piVar12 = piVar12 + -2;
    piVar1 = piVar1 + 2;
    piVar11 = piVar11 + -2;
    uVar6 = iVar10 * iVar9 - iVar13 * iVar7;
    puVar3[1] = uVar6;
    uVar8 = iVar10 * iVar7 + iVar13 * iVar9;
    *puVar3 = uVar8;
    auStack_24[0] = auStack_24[0] | (int)uVar6 >> 0x1f ^ uVar6 | (int)uVar8 >> 0x1f ^ uVar8;
  } while (piVar14 != piVar2);
  iVar13 = 0x2b;
  if (auStack_24[0] != 0) {
    if (param_3 == 0x100) {
      iVar13 = fft_rx4_short(param_2,auStack_24);
      iVar5 = fwd_short_complex_rot(param_2,param_1,auStack_24[0]);
      return 0xc - (iVar13 + iVar5);
    }
    iVar13 = mix_radix_fft();
    iVar5 = fwd_long_complex_rot(param_2,param_1,auStack_24[0]);
    iVar13 = 0xc - (iVar13 + iVar5);
  }
  return iVar13;
}
