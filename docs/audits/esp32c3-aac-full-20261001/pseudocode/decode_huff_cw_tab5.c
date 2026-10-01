/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: decode_huff_cw_tab5 @ ram:43004b60
 * Types and parameter counts are inferred; verify against disassembly. */

int decode_huff_cw_tab5(int *param_1)

{
  byte *pbVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;

  gp = &__global_pointer_;
  uVar2 = param_1[1];
  uVar3 = param_1[3] - (uVar2 >> 3);
  pbVar1 = (byte *)(*param_1 + (uVar2 >> 3));
  if (uVar3 < 3) {
    if (uVar3 == 1) {
      uVar3 = 0;
    }
    else {
      if (uVar3 != 2) goto LAB_ram_43004bd6;
      uVar3 = (uint)pbVar1[1] << 8;
    }
    uVar3 = (uint)*pbVar1 << 0x10 | uVar3;
  }
  else {
    uVar3 = (uint)*pbVar1 << 0x10 | (uint)pbVar1[1] << 8 | (uint)pbVar1[2];
  }
  iVar4 = uVar3 << (uVar2 & 7);
  uVar3 = (uint)(iVar4 << 8) >> 0x13;
  if (iVar4 << 8 < 0) {
    if ((uint)((int)uVar3 >> 8) < 0x1c) {
      iVar4 = ((int)uVar3 >> 8) - 0x10;
    }
    else if ((uint)((int)uVar3 >> 5) < 0xf4) {
      iVar4 = ((int)uVar3 >> 5) - 0xd4;
    }
    else if ((uint)((int)uVar3 >> 3) < 0x3f4) {
      iVar4 = ((int)uVar3 >> 3) - 0x3b0;
    }
    else if ((uint)((int)uVar3 >> 2) < 0x7fa) {
      iVar4 = ((int)uVar3 >> 2) - 0x7a4;
    }
    else {
      iVar4 = uVar3 - 0x1f92;
    }
    uVar3 = *(uint *)(huff_tab5 + iVar4 * 4);
    param_1[1] = uVar2 + (uVar3 & 0xffff);
    return (int)uVar3 >> 0x10;
  }
LAB_ram_43004bd6:
  param_1[1] = uVar2 + 1;
  return 0x28;
}
