/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: decode_huff_cw_tab1 @ ram:430047ea
 * Types and parameter counts are inferred; verify against disassembly. */

int decode_huff_cw_tab1(aac_analysis_bits_t *bits)

{
  uint uVar1;
  byte *pbVar2;
  int iVar3;
  uint uVar4;

  gp = &__global_pointer_;
  uVar1 = bits->used_bits;
  uVar4 = bits->input_length - (uVar1 >> 3);
  pbVar2 = bits->buffer + (uVar1 >> 3);
  if (uVar4 < 3) {
    if (uVar4 == 1) {
      uVar4 = 0;
    }
    else {
      if (uVar4 != 2) goto LAB_ram_4300485c;
      uVar4 = (uint)pbVar2[1] << 8;
    }
    uVar4 = (uint)*pbVar2 << 0x10 | uVar4;
  }
  else {
    uVar4 = (uint)*pbVar2 << 0x10 | (uint)pbVar2[1] << 8 | (uint)pbVar2[2];
  }
  uVar4 = (uVar4 << (uVar1 & 7)) >> 0xd & 0x7ff;
  if ((int)uVar4 >> 10 != 0) {
    if ((uint)((int)uVar4 >> 6) < 0x18) {
      iVar3 = ((int)uVar4 >> 6) - 0x10;
    }
    else if ((uint)((int)uVar4 >> 4) < 0x78) {
      iVar3 = ((int)uVar4 >> 4) - 0x58;
    }
    else {
      iVar3 = uVar4 - 0x7a8;
      if ((uint)((int)uVar4 >> 2) < 0x1f8) {
        iVar3 = ((int)uVar4 >> 2) - 0x1c0;
      }
    }
    uVar4 = *(uint *)(huff_tab1 + iVar3 * 4);
    bits->used_bits = uVar1 + (uVar4 & 0xffff);
    return (int)uVar4 >> 0x10;
  }
LAB_ram_4300485c:
  bits->used_bits = uVar1 + 1;
  return 0x28;
}
