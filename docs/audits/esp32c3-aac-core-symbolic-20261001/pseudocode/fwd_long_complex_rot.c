/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: fwd_long_complex_rot @ ram:43006fe6
 * Types and parameter counts are inferred; verify against disassembly. */

int fwd_long_complex_rot(int *param_1,int *param_2,undefined4 param_3)

{
  int iVar1;
  uint uVar2;
  uint *puVar3;
  uint *puVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  int *piVar9;
  int *piVar10;
  int *piVar11;
  int iVar12;

  gp = &__global_pointer_;
  iVar1 = pv_normalize(param_3);
  if (iVar1 < 0x11) {
    uVar2 = 0x10 - iVar1;
    iVar1 = 0x11 - iVar1;
  }
  else {
    iVar1 = 1;
    uVar2 = 0;
  }
  puVar3 = &exp_rotation_N_2048;
  piVar9 = param_2 + 0x7ff;
  piVar10 = param_2 + 0x3ff;
  piVar11 = param_2 + 0x400;
  do {
    iVar12 = *puVar3 << 0x10;
    iVar5 = *param_1 >> (uVar2 & 0x1f);
    iVar8 = param_1[1] >> (uVar2 & 0x1f);
    uVar7 = *puVar3 & 0xffff0000;
    puVar4 = puVar3 + 2;
    iVar6 = (int)((ulonglong)((longlong)iVar5 * (longlong)(int)uVar7) >> 0x20) +
            (int)((ulonglong)((longlong)iVar8 * (longlong)iVar12) >> 0x20);
    *param_2 = -iVar6;
    iVar5 = (int)((ulonglong)((longlong)(int)uVar7 * (longlong)iVar8) >> 0x20) +
            (int)((ulonglong)((longlong)-iVar5 * (longlong)iVar12) >> 0x20);
    *piVar10 = iVar5;
    *piVar11 = -iVar5;
    *piVar9 = iVar6;
    uVar7 = puVar3[1] & 0xffff0000;
    iVar5 = param_1[0x200] >> (uVar2 & 0x1f);
    iVar6 = puVar3[1] << 0x10;
    iVar12 = param_1[0x201] >> (uVar2 & 0x1f);
    iVar8 = (int)((ulonglong)((longlong)iVar5 * (longlong)(int)uVar7) >> 0x20) +
            (int)((ulonglong)((longlong)iVar12 * (longlong)iVar6) >> 0x20);
    param_2[2] = -iVar8;
    iVar5 = (int)((ulonglong)((longlong)(int)uVar7 * (longlong)iVar12) >> 0x20) +
            (int)((ulonglong)((longlong)-iVar5 * (longlong)iVar6) >> 0x20);
    piVar10[-2] = iVar5;
    piVar11[2] = -iVar5;
    piVar9[-2] = iVar8;
    param_1 = param_1 + 2;
    param_2 = param_2 + 4;
    puVar3 = puVar4;
    piVar9 = piVar9 + -4;
    piVar10 = piVar10 + -4;
    piVar11 = piVar11 + 4;
  } while (puVar4 != &exp_rotation_N_256);
  return iVar1;
}
