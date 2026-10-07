/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: decode_huff_cw_tab7 @ ram:43004d5a
 * Types and parameter counts are inferred; verify against disassembly. */

int decode_huff_cw_tab7(aac_analysis_bits_t *bits)

{
  byte *pbVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;

  gp = &__global_pointer_;
  uVar2 = bits->used_bits;
  uVar3 = bits->input_length - (uVar2 >> 3);
  pbVar1 = bits->buffer + (uVar2 >> 3);
  if (uVar3 < 3) {
    if (uVar3 == 1) {
      uVar3 = 0;
    }
    else {
      if (uVar3 != 2) goto LAB_ram_43004df8;
      uVar3 = (uint)pbVar1[1] << 8;
    }
    iVar4 = ((uint)*pbVar1 << 0x10 | uVar3) << (uVar2 & 7);
  }
  else {
    iVar4 = ((uint)*pbVar1 << 0x10 | (uint)pbVar1[1] << 8 | (uint)pbVar1[2]) << (uVar2 & 7);
  }
  if (iVar4 << 8 < 0) {
    uVar3 = (uint)(iVar4 << 8) >> 0x14;
    if ((uint)((int)uVar3 >> 6) < 0x38) {
      iVar4 = ((int)uVar3 >> 6) - 0x20;
    }
    else if ((uint)((int)uVar3 >> 4) < 0xf4) {
      iVar4 = ((int)uVar3 >> 4) - 200;
    }
    else if ((uint)((int)uVar3 >> 2) < 0x3fb) {
      iVar4 = ((int)uVar3 >> 2) - 0x3a4;
    }
    else {
      iVar4 = uVar3 - 0xf95;
    }
    uVar3 = *(uint *)(huff_tab7 + iVar4 * 4);
    bits->used_bits = uVar2 + (uVar3 & 0xffff);
    return (int)uVar3 >> 0x10;
  }
LAB_ram_43004df8:
  bits->used_bits = uVar2 + 1;
  return 0;
}
