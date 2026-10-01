/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_crc_check @ ram:43010420
 * Types and parameter counts are inferred; verify against disassembly. */

bool sbr_crc_check(aac_analysis_sbr_bits_t *bits,uint param_2)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  aac_analysis_crc_t aStack_3c;
  aac_analysis_sbr_bits_t aStack_34;

  gp = &__global_pointer_;
  uVar2 = buf_getbits(bits,10);
  aStack_34.read_bits = bits->read_bits;
  aStack_34.total_bits = bits->total_bits;
  aStack_34.cursor = bits->cursor;
  aStack_34.cache = bits->cache;
  aStack_34.cached_bits = bits->cached_bits;
  uVar4 = aStack_34.total_bits - aStack_34.read_bits;
  if (param_2 < aStack_34.total_bits - aStack_34.read_bits) {
    uVar4 = param_2;
  }
  aStack_3c.value = 0;
  aStack_3c.top_bit = 0x200;
  aStack_3c.polynomial = 0x233;
  if (uVar4 >> 4 != 0) {
    uVar1 = 0;
    do {
      uVar3 = buf_getbits(&aStack_34,0x10);
      uVar1 = uVar1 + 1;
      check_crc(&aStack_3c,uVar3,0x10);
    } while (uVar4 >> 4 != uVar1);
  }
  uVar1 = buf_getbits(&aStack_34,uVar4 & 0xf);
  check_crc(&aStack_3c,uVar1,uVar4 & 0xf);
  return (aStack_3c._0_4_ & 0x3ff) == uVar2;
}
