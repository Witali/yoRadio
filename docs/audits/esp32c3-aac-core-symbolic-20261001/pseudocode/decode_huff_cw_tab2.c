/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: decode_huff_cw_tab2 @ ram:430048a2
 * Types and parameter counts are inferred; verify against disassembly. */

int decode_huff_cw_tab2(aac_analysis_bits_t *bits)

{
  ushort uVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;

  gp = &__global_pointer_;
  uVar2 = bits->used_bits;
  uVar4 = bits->input_length - (uVar2 >> 3);
  if (uVar4 < 2) {
    if (uVar4 != 1) goto LAB_ram_4300492c;
    uVar4 = (uint)(byte)*(ushort *)(bits->buffer + (uVar2 >> 3)) << 8;
  }
  else {
    uVar1 = *(ushort *)(bits->buffer + (uVar2 >> 3));
    uVar4 = (uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 & 0xffff;
  }
  uVar4 = (uVar4 << (uVar2 & 7)) >> 7 & 0x1ff;
  if ((int)uVar4 >> 6 != 0) {
    if ((uint)((int)uVar4 >> 3) < 0x32) {
      iVar3 = ((int)uVar4 >> 3) - 8;
    }
    else if ((uint)((int)uVar4 >> 2) < 0x73) {
      iVar3 = ((int)uVar4 >> 2) - 0x3a;
    }
    else {
      iVar3 = uVar4 - 0x1a6;
      if ((uint)((int)uVar4 >> 1) < 0xf9) {
        iVar3 = ((int)uVar4 >> 1) - 0xad;
      }
    }
    uVar4 = *(uint *)(huff_tab2 + iVar3 * 4);
    bits->used_bits = uVar2 + (uVar4 & 0xffff);
    return (int)uVar4 >> 0x10;
  }
LAB_ram_4300492c:
  bits->used_bits = uVar2 + 3;
  return 0x28;
}
