/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: decode_huff_cw_tab4 @ ram:43004a32
 * Types and parameter counts are inferred; verify against disassembly. */

int decode_huff_cw_tab4(aac_analysis_bits_t *bits)

{
  uint uVar1;
  byte *pbVar2;
  uint uVar3;
  int iVar4;

  gp = &__global_pointer_;
  uVar1 = bits->used_bits;
  uVar3 = bits->input_length - (uVar1 >> 3);
  pbVar2 = bits->buffer + (uVar1 >> 3);
  if (uVar3 < 3) {
    if (uVar3 == 1) {
      uVar3 = 0;
    }
    else {
      if (uVar3 != 2) {
        iVar4 = (int)huff_tab4 >> 0x10;
        bits->used_bits = (huff_tab4 & 0xffff) + uVar1;
        return iVar4;
      }
      uVar3 = (uint)pbVar2[1] << 8;
    }
    iVar4 = ((uint)*pbVar2 << 0x10 | uVar3) << (uVar1 & 7);
  }
  else {
    iVar4 = ((uint)*pbVar2 << 0x10 | (uint)pbVar2[1] << 8 | (uint)pbVar2[2]) << (uVar1 & 7);
  }
  uVar3 = (uint)(iVar4 << 8) >> 0x14;
  if ((uint)((int)uVar3 >> 7) < 0x1a) {
    uVar3 = (&huff_tab4)[(int)uVar3 >> 7];
    bits->used_bits = (uVar3 & 0xffff) + uVar1;
    return (int)uVar3 >> 0x10;
  }
  if ((uint)((int)uVar3 >> 4) < 0xf7) {
    uVar3 = (&huff_tab4)[((int)uVar3 >> 4) - 0xb6];
    bits->used_bits = (uVar3 & 0xffff) + uVar1;
    return (int)uVar3 >> 0x10;
  }
  if (0x3f9 < (uint)((int)uVar3 >> 2)) {
    uVar3 = (&huff_tab4)[uVar3 - 0xf89];
    bits->used_bits = (uVar3 & 0xffff) + uVar1;
    return (int)uVar3 >> 0x10;
  }
  uVar3 = (&huff_tab4)[((int)uVar3 >> 2) - 0x39b];
  bits->used_bits = (uVar3 & 0xffff) + uVar1;
  return (int)uVar3 >> 0x10;
}
