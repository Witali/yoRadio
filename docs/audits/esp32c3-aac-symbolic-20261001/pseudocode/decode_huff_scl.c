/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: decode_huff_scl @ ram:430053c4
 * Types and parameter counts are inferred; verify against disassembly. */

int decode_huff_scl(int *param_1)

{
  byte *pbVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;

  gp = &__global_pointer_;
  uVar3 = param_1[1];
  uVar4 = param_1[3] - (uVar3 >> 3);
  pbVar1 = (byte *)(*param_1 + (uVar3 >> 3));
  if (uVar4 < 4) {
    if (uVar4 == 2) {
      uVar4 = 0;
LAB_ram_43005480:
      uVar4 = (uint)pbVar1[1] << 0x10 | uVar4;
    }
    else {
      if (uVar4 == 3) {
        uVar4 = (uint)pbVar1[2] << 8;
        goto LAB_ram_43005480;
      }
      if (uVar4 != 1) goto LAB_ram_4300546e;
      uVar4 = 0;
    }
    uVar4 = (uint)*pbVar1 << 0x18 | uVar4;
  }
  else {
    uVar4 = (uint)*pbVar1 << 0x18 | (uint)pbVar1[1] << 0x10 | (uint)pbVar1[3] | (uint)pbVar1[2] << 8
    ;
  }
  uVar4 = uVar4 << (uVar3 & 7);
  uVar2 = uVar4 >> 0xd;
  if ((int)uVar4 < 0) {
    if ((uint)((int)uVar2 >> 0xd) < 0x3c) {
      iVar5 = ((int)uVar2 >> 0xd) - 0x20;
    }
    else if ((uint)((int)uVar2 >> 10) < 0x1fa) {
      iVar5 = ((int)uVar2 >> 10) - 0x1c4;
    }
    else if ((uint)((int)uVar2 >> 7) < 0xffa) {
      iVar5 = ((int)uVar2 >> 7) - 0xf9a;
    }
    else if ((uint)((int)uVar2 >> 5) < 0x3ffa) {
      iVar5 = ((int)uVar2 >> 5) - 0x3f88;
    }
    else if ((uint)((int)uVar2 >> 3) < 0xfff7) {
      iVar5 = ((int)uVar2 >> 3) - 0xff76;
    }
    else if ((uint)((int)uVar2 >> 1) < 0x3ffe9) {
      iVar5 = ((int)uVar2 >> 1) - 0x3ff5b;
    }
    else {
      iVar5 = uVar2 - 0x7ff44;
    }
    uVar4 = *(uint *)(huff_tab_scl + iVar5 * 4);
    param_1[1] = uVar3 + (uVar4 & 0xffff);
    return (int)uVar4 >> 0x10;
  }
LAB_ram_4300546e:
  param_1[1] = uVar3 + 1;
  return 0x3c;
}
