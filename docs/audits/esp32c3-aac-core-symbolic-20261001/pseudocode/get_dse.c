/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: get_dse @ ram:43007884
 * Types and parameter counts are inferred; verify against disassembly. */

void get_dse(undefined1 *param_1,aac_analysis_bits_t *bits)

{
  ushort uVar1;
  uint uVar2;
  undefined1 *puVar3;
  uint8_t *puVar4;
  undefined1 uVar5;
  uint uVar6;
  uint32_t uVar7;
  uint32_t uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;

  gp = &__global_pointer_;
  uVar7 = bits->used_bits;
  uVar8 = bits->input_length;
  puVar4 = bits->buffer;
  uVar6 = uVar7 + 4;
  bits->used_bits = uVar6;
  uVar9 = 0;
  if (uVar6 >> 3 < uVar8) {
    uVar9 = (uint)puVar4[uVar6 >> 3] << (uVar6 & 7) & 0x80;
  }
  uVar2 = uVar7 + 5;
  uVar10 = uVar8 - (uVar2 >> 3);
  bits->used_bits = uVar2;
  uVar6 = uVar7 + 0xd;
  if (uVar10 < 2) {
    if (uVar10 != 1) {
      bits->used_bits = uVar6;
      if (uVar9 == 0) {
        return;
      }
      bits->used_bits = bits->used_bits + 7 & 0xfffffff8;
      return;
    }
    uVar10 = (uint)(byte)*(ushort *)(puVar4 + (uVar2 >> 3)) << 8;
  }
  else {
    uVar1 = *(ushort *)(puVar4 + (uVar2 >> 3));
    uVar10 = (uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 & 0xffff;
  }
  uVar2 = uVar2 & 7;
  uVar10 = (uVar10 << uVar2) >> 8 & 0xff;
  bits->used_bits = uVar6;
  if (uVar10 == 0xff) {
    uVar11 = uVar8 - (uVar6 >> 3);
    if (uVar11 < 2) {
      if (uVar11 == 1) {
        uVar10 = ((((uint)(byte)*(ushort *)(puVar4 + (uVar6 >> 3)) << 8) << uVar2) >> 8 & 0xff) +
                 0xff;
      }
    }
    else {
      uVar1 = *(ushort *)(puVar4 + (uVar6 >> 3));
      uVar10 = ((((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 << uVar2) << 0x10) >> 0x18) + 0xff;
    }
    uVar6 = uVar7 + 0x15;
    bits->used_bits = uVar6;
    if (uVar9 != 0) {
      byte_align(bits);
      uVar6 = bits->used_bits;
      puVar4 = bits->buffer;
      uVar8 = bits->input_length;
    }
  }
  else {
    if (uVar9 != 0) {
      byte_align(bits);
    }
    if (uVar10 == 0) {
      return;
    }
    uVar6 = bits->used_bits;
    puVar4 = bits->buffer;
    uVar8 = bits->input_length;
  }
  puVar3 = param_1 + (uVar10 - 1);
  do {
    uVar9 = uVar8 - (uVar6 >> 3);
    if (uVar9 < 2) {
      uVar5 = 0;
      if (uVar9 != 1) goto LAB_ram_4300791e;
      uVar1 = *(ushort *)(puVar4 + (uVar6 >> 3));
      bits->used_bits = uVar6 + 8;
      *param_1 = (char)((((uint)(byte)uVar1 << 8) << (uVar6 & 7)) >> 8);
    }
    else {
      uVar1 = *(ushort *)(puVar4 + (uVar6 >> 3));
      uVar5 = (undefined1)(((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 << (uVar6 & 7)) >> 8);
LAB_ram_4300791e:
      bits->used_bits = uVar6 + 8;
      *param_1 = uVar5;
    }
    if (puVar3 == param_1) {
      gp = &__global_pointer_;
      return;
    }
    uVar6 = bits->used_bits;
    puVar4 = bits->buffer;
    uVar8 = bits->input_length;
    param_1 = param_1 + 1;
  } while( true );
}
