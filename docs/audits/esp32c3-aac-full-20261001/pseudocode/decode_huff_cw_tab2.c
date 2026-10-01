/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: decode_huff_cw_tab2 @ ram:430048a2
 * Types and parameter counts are inferred; verify against disassembly. */

int decode_huff_cw_tab2(int *param_1)

{
  ushort uVar1;
  uint uVar2;
  ushort *puVar3;
  int iVar4;
  uint uVar5;

  gp = &__global_pointer_;
  uVar2 = param_1[1];
  uVar5 = param_1[3] - (uVar2 >> 3);
  puVar3 = (ushort *)(*param_1 + (uVar2 >> 3));
  if (uVar5 < 2) {
    if (uVar5 != 1) goto LAB_ram_4300492c;
    uVar5 = (uint)(byte)*puVar3 << 8;
  }
  else {
    uVar1 = *puVar3;
    uVar5 = (uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 & 0xffff;
  }
  uVar5 = (uVar5 << (uVar2 & 7)) >> 7 & 0x1ff;
  if ((int)uVar5 >> 6 != 0) {
    if ((uint)((int)uVar5 >> 3) < 0x32) {
      iVar4 = ((int)uVar5 >> 3) - 8;
    }
    else if ((uint)((int)uVar5 >> 2) < 0x73) {
      iVar4 = ((int)uVar5 >> 2) - 0x3a;
    }
    else {
      iVar4 = uVar5 - 0x1a6;
      if ((uint)((int)uVar5 >> 1) < 0xf9) {
        iVar4 = ((int)uVar5 >> 1) - 0xad;
      }
    }
    uVar5 = *(uint *)(huff_tab2 + iVar4 * 4);
    param_1[1] = uVar2 + (uVar5 & 0xffff);
    return (int)uVar5 >> 0x10;
  }
LAB_ram_4300492c:
  param_1[1] = uVar2 + 3;
  return 0x28;
}
