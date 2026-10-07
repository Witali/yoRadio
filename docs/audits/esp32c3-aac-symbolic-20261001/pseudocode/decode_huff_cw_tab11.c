/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: decode_huff_cw_tab11 @ ram:4300525a
 * Types and parameter counts are inferred; verify against disassembly. */

int decode_huff_cw_tab11(int *param_1)

{
  uint uVar1;
  byte *pbVar2;
  uint *puVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;

  gp = &__global_pointer_;
  uVar1 = param_1[1];
  uVar5 = param_1[3] - (uVar1 >> 3);
  pbVar2 = (byte *)(*param_1 + (uVar1 >> 3));
  if (uVar5 < 3) {
    if (uVar5 == 1) {
      uVar5 = 0;
    }
    else {
      if (uVar5 != 2) {
        iVar6 = (int)huff_tab11 >> 0x10;
        param_1[1] = (huff_tab11 & 0xffff) + uVar1;
        return iVar6;
      }
      uVar5 = (uint)pbVar2[1] << 8;
    }
    iVar6 = ((uint)*pbVar2 << 0x10 | uVar5) << (uVar1 & 7);
  }
  else {
    iVar6 = ((uint)*pbVar2 << 0x10 | (uint)pbVar2[1] << 8 | (uint)pbVar2[2]) << (uVar1 & 7);
  }
  uVar5 = (uint)(iVar6 << 8) >> 0x14;
  uVar4 = (int)uVar5 >> 6;
  if (0x1a < uVar4) {
    if ((uint)((int)uVar5 >> 5) < 0x46) {
      puVar3 = &huff_tab11 + (((int)uVar5 >> 5) - 0x1b);
    }
    else {
      if ((uint)((int)uVar5 >> 4) < 199) {
        uVar5 = (&huff_tab11)[((int)uVar5 >> 4) - 0x61];
        param_1[1] = (uVar5 & 0xffff) + uVar1;
        return (int)uVar5 >> 0x10;
      }
      if ((uint)((int)uVar5 >> 3) < 0x1c5) {
        puVar3 = &huff_tab11 + (((int)uVar5 >> 3) - 0x128);
      }
      else if ((uint)((int)uVar5 >> 2) < 0x3e9) {
        puVar3 = &huff_tab11 + (((int)uVar5 >> 2) - 0x2ed);
      }
      else {
        if ((uint)((int)uVar5 >> 1) < 0x7fd) {
          uVar4 = ((int)uVar5 >> 1) - 0x6d6;
          goto LAB_ram_430052fc;
        }
        puVar3 = &huff_tab11 + (uVar5 - 0xed3);
      }
    }
    uVar5 = *puVar3;
    param_1[1] = (uVar5 & 0xffff) + uVar1;
    return (int)uVar5 >> 0x10;
  }
LAB_ram_430052fc:
  uVar5 = (&huff_tab11)[uVar4];
  param_1[1] = (uVar5 & 0xffff) + uVar1;
  return (int)uVar5 >> 0x10;
}
