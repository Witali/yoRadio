/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: decode_huff_cw_tab9 @ ram:43004f58
 * Types and parameter counts are inferred; verify against disassembly. */

int decode_huff_cw_tab9(int *param_1)

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
        iVar6 = (int)huff_tab9 >> 0x10;
        param_1[1] = (huff_tab9 & 0xffff) + uVar1;
        return iVar6;
      }
      uVar5 = (uint)pbVar2[1] << 8;
    }
    iVar6 = ((uint)*pbVar2 << 0x10 | uVar5) << (uVar1 & 7);
  }
  else {
    iVar6 = ((uint)*pbVar2 << 0x10 | (uint)pbVar2[1] << 8 | (uint)pbVar2[2]) << (uVar1 & 7);
  }
  uVar5 = (uint)(iVar6 << 8) >> 0x11;
  uVar4 = (int)uVar5 >> 0xb;
  if (0xc < uVar4) {
    if ((uint)((int)uVar5 >> 8) < 0x73) {
      puVar3 = &huff_tab9 + (((int)uVar5 >> 8) - 0x5b);
    }
    else {
      if ((uint)((int)uVar5 >> 6) < 0x1e7) {
        uVar5 = (&huff_tab9)[((int)uVar5 >> 6) - 0x1b4];
        param_1[1] = (uVar5 & 0xffff) + uVar1;
        return (int)uVar5 >> 0x10;
      }
      if ((uint)((int)uVar5 >> 5) < 0x3e2) {
        puVar3 = &huff_tab9 + (((int)uVar5 >> 5) - 0x39b);
      }
      else if ((uint)((int)uVar5 >> 4) < 0x7e3) {
        puVar3 = &huff_tab9 + (((int)uVar5 >> 4) - 0x77d);
      }
      else if ((uint)((int)uVar5 >> 3) < 0xfec) {
        puVar3 = &huff_tab9 + (((int)uVar5 >> 3) - 0xf60);
      }
      else {
        if ((uint)((int)uVar5 >> 2) < 0x1ff8) {
          uVar4 = ((int)uVar5 >> 2) - 0x1f4c;
          goto LAB_ram_43004ffc;
        }
        puVar3 = &huff_tab9 + (uVar5 - 0x7f34);
      }
    }
    uVar5 = *puVar3;
    param_1[1] = (uVar5 & 0xffff) + uVar1;
    return (int)uVar5 >> 0x10;
  }
LAB_ram_43004ffc:
  uVar5 = (&huff_tab9)[uVar4];
  param_1[1] = (uVar5 & 0xffff) + uVar1;
  return (int)uVar5 >> 0x10;
}
