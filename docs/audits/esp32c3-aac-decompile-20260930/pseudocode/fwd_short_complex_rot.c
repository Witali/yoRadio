/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: fwd_short_complex_rot @ ram:4205824c
 * Types and parameter counts are inferred; verify against disassembly. */

void fwd_short_complex_rot(int param_1,int *param_2,undefined4 param_3)

{
  short sVar1;
  uint *puVar2;
  int iVar3;
  uint uVar4;
  short *psVar5;
  uint uVar6;
  int *piVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int *piVar11;

  gp = &__global_pointer_;
  iVar3 = pv_normalize(param_3);
  uVar4 = 0x10 - iVar3;
  if (0x10 < iVar3) {
    uVar4 = 0;
  }
  puVar2 = &exp_rotation_N_256;
  psVar5 = &digit_reverse_64;
  piVar11 = param_2 + 0x7f;
  do {
    sVar1 = *psVar5;
    psVar5 = psVar5 + 1;
    piVar7 = (int *)(sVar1 * 4 + param_1);
    uVar6 = *puVar2 & 0xffff;
    iVar10 = piVar7[1] >> (uVar4 & 0x1f);
    iVar3 = *piVar7 >> (uVar4 & 0x1f);
    iVar9 = (int)*puVar2 >> 0x10;
    puVar2 = puVar2 + 1;
    iVar8 = (int)(iVar9 * iVar3 + uVar6 * iVar10) >> 0x10;
    *param_2 = -iVar8;
    iVar3 = (int)(iVar9 * iVar10 - uVar6 * iVar3) >> 0x10;
    *piVar11 = iVar3;
    param_2[0x80] = -iVar3;
    piVar11[0x80] = iVar8;
    param_2 = param_2 + 2;
    piVar11 = piVar11 + -2;
  } while (psVar5 != (short *)CosTable_16);
  return;
}
