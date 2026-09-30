/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: decode_huff_cw_tab8 @ ram:4205b6d6
 * Types and parameter counts are inferred; verify against disassembly. */

int decode_huff_cw_tab8(int *param_1)

{
  int iVar1;
  uint uVar2;
  byte *pbVar3;
  uint uVar4;

  gp = &__global_pointer_;
  uVar2 = param_1[1];
  uVar4 = param_1[3] - (uVar2 >> 3);
  pbVar3 = (byte *)(*param_1 + (uVar2 >> 3));
  if (uVar4 < 3) {
    if (uVar4 == 1) {
      uVar4 = 0;
    }
    else {
      if (uVar4 != 2) {
        iVar1 = (int)huff_tab8 >> 0x10;
        param_1[1] = (huff_tab8 & 0xffff) + uVar2;
        return iVar1;
      }
      uVar4 = (uint)pbVar3[1] << 8;
    }
    uVar4 = ((uint)*pbVar3 << 0x10 | uVar4) << (uVar2 & 7);
  }
  else {
    uVar4 = ((uint)*pbVar3 << 0x10 | (uint)pbVar3[1] << 8 | (uint)pbVar3[2]) << (uVar2 & 7);
  }
  uVar4 = uVar4 >> 0xe & 0x3ff;
  if ((uint)((int)uVar4 >> 5) < 0x15) {
    uVar4 = (&huff_tab8)[(int)uVar4 >> 5];
    param_1[1] = (uVar4 & 0xffff) + uVar2;
    return (int)uVar4 >> 0x10;
  }
  if ((uint)((int)uVar4 >> 3) < 0x76) {
    uVar4 = (&huff_tab8)[((int)uVar4 >> 3) - 0x3f];
    param_1[1] = (uVar4 & 0xffff) + uVar2;
    return (int)uVar4 >> 0x10;
  }
  if (0xfa < (uint)((int)uVar4 >> 2)) {
    uVar4 = (&huff_tab8)[uVar4 - 0x3a6];
    param_1[1] = (uVar4 & 0xffff) + uVar2;
    return (int)uVar4 >> 0x10;
  }
  uVar4 = (&huff_tab8)[((int)uVar4 >> 2) - 0xb5];
  param_1[1] = (uVar4 & 0xffff) + uVar2;
  return (int)uVar4 >> 0x10;
}
