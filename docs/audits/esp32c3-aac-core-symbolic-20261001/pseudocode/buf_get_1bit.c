/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: buf_get_1bit @ ram:43000bca
 * Types and parameter counts are inferred; verify against disassembly. */

uint buf_get_1bit(aac_analysis_sbr_bits_t *bits)

{
  byte bVar1;
  uint uVar2;
  byte *pbVar3;
  uint uVar4;

  gp = &__global_pointer_;
  uVar4 = bits->cached_bits;
  uVar2 = bits->cache;
  if (uVar4 < 0x11) {
    pbVar3 = bits->cursor;
    uVar4 = uVar4 + 0x10;
    bits->cursor = pbVar3 + 1;
    bVar1 = *pbVar3;
    bits->cursor = pbVar3 + 2;
    uVar2 = (uint)bVar1 << 8 | uVar2 << 0x10;
    bits->cache = uVar2;
    uVar2 = pbVar3[1] | uVar2;
    bits->cache = uVar2;
  }
  bits->cached_bits = uVar4 - 1;
  bits->read_bits = bits->read_bits + 1;
  return uVar2 >> (uVar4 - 1 & 0x1f) & 1;
}
