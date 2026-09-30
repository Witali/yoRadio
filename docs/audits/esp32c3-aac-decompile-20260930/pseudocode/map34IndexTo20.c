/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: map34IndexTo20 @ ram:42047312
 * Types and parameter counts are inferred; verify against disassembly. */

void map34IndexTo20(int *param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;

  gp = &__global_pointer_;
  iVar4 = param_1[1];
  iVar3 = param_1[5];
  iVar2 = param_1[4];
  param_1[1] = (param_1[2] * 2 + iVar4) / 3;
  iVar1 = param_1[10];
  param_1[2] = (param_1[3] * 2 + iVar2) / 3;
  *param_1 = (*param_1 * 2 + iVar4) / 3;
  param_1[4] = param_1[6] + param_1[7] >> 1;
  param_1[5] = param_1[8] + param_1[9] >> 1;
  param_1[7] = param_1[0xb];
  param_1[8] = param_1[0xc] + param_1[0xd] >> 1;
  param_1[9] = param_1[0xe] + param_1[0xf] >> 1;
  param_1[3] = (iVar3 * 2 + iVar2) / 3;
  param_1[10] = param_1[0x10];
  param_1[0xb] = param_1[0x11];
  param_1[6] = iVar1;
  param_1[0xc] = param_1[0x12];
  param_1[0xd] = param_1[0x13];
  param_1[0xe] = param_1[0x14] + param_1[0x15] >> 1;
  param_1[0xf] = param_1[0x16] + param_1[0x17] >> 1;
  param_1[0x10] = param_1[0x18] + param_1[0x19] >> 1;
  param_1[0x11] = param_1[0x1a] + param_1[0x1b] >> 1;
  param_1[0x12] = param_1[0x1c] + param_1[0x1d] + param_1[0x1e] + param_1[0x1f] >> 2;
  param_1[0x13] = param_1[0x20] + param_1[0x21] >> 1;
  return;
}
