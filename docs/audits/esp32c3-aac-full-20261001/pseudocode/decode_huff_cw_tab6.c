/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: decode_huff_cw_tab6 @ ram:43004c34
 * Types and parameter counts are inferred; verify against disassembly. */

int decode_huff_cw_tab6(int *param_1)

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
        iVar1 = (int)huff_tab6 >> 0x10;
        param_1[1] = (huff_tab6 & 0xffff) + uVar2;
        return iVar1;
      }
      uVar4 = (uint)pbVar3[1] << 8;
    }
    uVar4 = ((uint)*pbVar3 << 0x10 | uVar4) << (uVar2 & 7);
  }
  else {
    uVar4 = ((uint)*pbVar3 << 0x10 | (uint)pbVar3[1] << 8 | (uint)pbVar3[2]) << (uVar2 & 7);
  }
  uVar4 = uVar4 >> 0xd & 0x7ff;
  if ((uint)((int)uVar4 >> 7) < 9) {
    uVar4 = (&huff_tab6)[(int)uVar4 >> 7];
    param_1[1] = (uVar4 & 0xffff) + uVar2;
    return (int)uVar4 >> 0x10;
  }
  if ((uint)((int)uVar4 >> 4) < 0x75) {
    uVar4 = (&huff_tab6)[((int)uVar4 >> 4) - 0x3f];
    param_1[1] = (uVar4 & 0xffff) + uVar2;
    return (int)uVar4 >> 0x10;
  }
  if (0x1fa < (uint)((int)uVar4 >> 2)) {
    uVar4 = (&huff_tab6)[uVar4 - 0x78f];
    param_1[1] = (uVar4 & 0xffff) + uVar2;
    return (int)uVar4 >> 0x10;
  }
  uVar4 = (&huff_tab6)[((int)uVar4 >> 2) - 0x19e];
  param_1[1] = (uVar4 & 0xffff) + uVar2;
  return (int)uVar4 >> 0x10;
}
