/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: get_pulse_data @ ram:4300822a
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4 get_pulse_data(aac_analysis_pulse_t *pulse,aac_analysis_bits_t *bits)

{
  ushort uVar1;
  uint8_t *puVar2;
  int32_t *piVar3;
  ushort *puVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  uint32_t uVar9;
  uint uVar10;

  gp = &__global_pointer_;
  uVar7 = bits->used_bits;
  uVar9 = bits->input_length;
  puVar2 = bits->buffer;
  uVar10 = uVar9 - (uVar7 >> 3);
  iVar6 = 1;
  puVar4 = (ushort *)(puVar2 + (uVar7 >> 3));
  if (uVar10 < 2) {
    uVar8 = 0;
    if (uVar10 != 1) goto LAB_ram_4300826c;
    uVar10 = (uint)(byte)*puVar4 << 8;
  }
  else {
    uVar1 = *puVar4;
    uVar10 = (uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 & 0xffff;
  }
  uVar10 = uVar10 << (uVar7 & 7);
  iVar6 = (uVar10 >> 0xe & 3) + 1;
  uVar8 = uVar10 >> 8 & 0x3f;
LAB_ram_4300826c:
  uVar7 = uVar7 + 8;
  bits->used_bits = uVar7;
  pulse->count = iVar6;
  pulse->start_band = uVar8;
  piVar3 = pulse->offset;
  do {
    uVar10 = uVar9 - (uVar7 >> 3);
    puVar4 = (ushort *)(puVar2 + (uVar7 >> 3));
    if (uVar10 < 2) {
      uVar8 = 0;
      uVar5 = 0;
      if (uVar10 == 1) {
        uVar10 = (uint)(byte)*puVar4 << 8;
        goto LAB_ram_43008292;
      }
    }
    else {
      uVar1 = *puVar4;
      uVar10 = (uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 & 0xffff;
LAB_ram_43008292:
      uVar10 = uVar10 << (uVar7 & 7);
      uVar5 = uVar10 >> 0xb & 0x1f;
      uVar8 = uVar10 >> 7 & 0xf;
    }
    bits->used_bits = uVar7 + 9;
    *piVar3 = uVar5;
    piVar3[4] = uVar8;
    if (piVar3 == pulse->offset + iVar6 + -1) {
      return 0;
    }
    uVar7 = bits->used_bits;
    uVar9 = bits->input_length;
    piVar3 = piVar3 + 1;
  } while( true );
}
