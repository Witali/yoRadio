/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: buf_getbits @ ram:43000b7e
 * Types and parameter counts are inferred; verify against disassembly. */

uint buf_getbits(aac_analysis_sbr_bits_t *bits,uint param_2)

{
  byte bVar1;
  byte *pbVar2;
  uint uVar3;
  uint uVar4;

  gp = &__global_pointer_;
  uVar3 = bits->cached_bits;
  uVar4 = bits->cache;
  if (uVar3 < 0x11) {
    pbVar2 = bits->cursor;
    uVar3 = uVar3 + 0x10;
    bits->cursor = pbVar2 + 1;
    bVar1 = *pbVar2;
    bits->cursor = pbVar2 + 2;
    uVar4 = (uint)bVar1 << 8 | uVar4 << 0x10;
    bits->cache = uVar4;
    uVar4 = pbVar2[1] | uVar4;
    bits->cache = uVar4;
  }
  bits->cached_bits = uVar3 - param_2;
  bits->read_bits = param_2 + bits->read_bits;
  return (1 << (param_2 & 0x1f)) - 1U & uVar4 >> (uVar3 - param_2 & 0x1f);
}
