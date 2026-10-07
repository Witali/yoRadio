/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: buf_getbits @ ram:42040ec0
 * Types and parameter counts are inferred; verify against disassembly. */

uint buf_getbits(undefined4 *param_1,uint param_2)

{
  byte bVar1;
  byte *pbVar2;
  uint uVar3;
  uint uVar4;

  gp = &__global_pointer_;
  uVar3 = param_1[1];
  uVar4 = param_1[2];
  if (uVar3 < 0x11) {
    pbVar2 = (byte *)*param_1;
    uVar3 = uVar3 + 0x10;
    *param_1 = pbVar2 + 1;
    bVar1 = *pbVar2;
    *param_1 = pbVar2 + 2;
    uVar4 = (uint)bVar1 << 8 | uVar4 << 0x10;
    param_1[2] = uVar4;
    uVar4 = pbVar2[1] | uVar4;
    param_1[2] = uVar4;
  }
  param_1[1] = uVar3 - param_2;
  param_1[3] = param_2 + param_1[3];
  return (1 << (param_2 & 0x1f)) - 1U & uVar4 >> (uVar3 - param_2 & 0x1f);
}
