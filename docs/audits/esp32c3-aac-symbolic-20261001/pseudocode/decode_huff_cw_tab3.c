/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: decode_huff_cw_tab3 @ ram:43004944
 * Types and parameter counts are inferred; verify against disassembly. */

int decode_huff_cw_tab3(int *param_1)

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
      if (uVar3 != 2) goto LAB_ram_430049e2;
      uVar3 = (uint)pbVar1[1] << 8;
    }
    iVar4 = ((uint)*pbVar1 << 0x10 | uVar3) << (uVar2 & 7);
  }
  else {
    iVar4 = ((uint)*pbVar1 << 0x10 | (uint)pbVar1[1] << 8 | (uint)pbVar1[2]) << (uVar2 & 7);
  }
  if (iVar4 << 8 < 0) {
    uVar3 = (uint)(iVar4 << 8) >> 0x10;
    if ((uint)((int)uVar3 >> 10) < 0x3a) {
      iVar4 = ((int)uVar3 >> 10) - 0x20;
    }
    else if ((uint)((int)uVar3 >> 7) < 0x1f5) {
      iVar4 = ((int)uVar3 >> 7) - 0x1b6;
    }
    else if ((uint)((int)uVar3 >> 6) < 0x3f9) {
      iVar4 = ((int)uVar3 >> 6) - 0x3ab;
    }
    else if ((uint)((int)uVar3 >> 4) < 0xffd) {
      iVar4 = ((int)uVar3 >> 4) - 0xf96;
    }
    else {
      iVar4 = uVar3 - 0xff69;
    }
    uVar3 = *(uint *)(huff_tab3 + iVar4 * 4);
    param_1[1] = uVar2 + (uVar3 & 0xffff);
    return (int)uVar3 >> 0x10;
  }
LAB_ram_430049e2:
  param_1[1] = uVar2 + 1;
  return 0;
}
