/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: huffcb @ ram:43008ff8
 * Types and parameter counts are inferred; verify against disassembly. */

uint huffcb(aac_analysis_section_t *sections,aac_analysis_bits_t *bits,uint *param_3,uint param_4,
           int param_5,int param_6)

{
  ushort uVar1;
  uint uVar2;
  uint32_t uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  uint8_t *puVar11;
  uint uVar12;
  uint uVar13;

  gp = &__global_pointer_;
  if ((int)param_4 < 1) {
    if (param_4 == 0) {
      return 0;
    }
    return 0;
  }
  uVar12 = *param_3;
  puVar11 = bits->buffer;
  uVar3 = bits->input_length;
  uVar9 = (1 << (uVar12 & 0x1f)) - 1;
  uVar13 = 0x10 - uVar12;
  uVar2 = 0;
  uVar5 = 0;
  uVar6 = 0;
  do {
    uVar4 = bits->used_bits;
    uVar10 = uVar3 - (uVar4 >> 3);
    if (uVar10 < 2) {
      uVar7 = 0;
      if (uVar10 == 1) {
        uVar7 = (((uint)(byte)*(ushort *)(puVar11 + (uVar4 >> 3)) << 8) << (uVar4 & 7)) >> 0xc & 0xf
        ;
      }
    }
    else {
      uVar1 = *(ushort *)(puVar11 + (uVar4 >> 3));
      uVar7 = (((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 << (uVar4 & 7)) << 0x10) >> 0x1c;
    }
    uVar4 = uVar4 + 4;
    bits->used_bits = uVar4;
    sections->codebook = uVar7;
    uVar10 = uVar3 - (uVar4 >> 3);
    if (uVar10 < 2) {
      uVar7 = 0;
      if (uVar10 == 1) {
        uVar7 = (((uint)(byte)*(ushort *)(puVar11 + (uVar4 >> 3)) << 8) << (uVar4 & 7) & 0xffff) >>
                (uVar13 & 0x1f);
      }
    }
    else {
      uVar1 = *(ushort *)(puVar11 + (uVar4 >> 3));
      uVar7 = ((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 << (uVar4 & 7) & 0xffff) >> (uVar13 & 0x1f);
    }
    uVar4 = uVar4 + uVar12;
    bits->used_bits = uVar4;
    if (((int)uVar6 < (int)param_4) && (uVar9 == uVar7)) {
      do {
        uVar10 = uVar3 - (uVar4 >> 3);
        uVar6 = uVar6 + uVar9;
        if (uVar10 < 2) {
          uVar7 = 0;
          if (uVar10 != 1) goto LAB_ram_430090b4;
          uVar1 = *(ushort *)(puVar11 + (uVar4 >> 3));
          bits->used_bits = uVar4 + uVar12;
          uVar7 = (((uint)(byte)uVar1 << 8) << (uVar4 & 7) & 0xffff) >> (uVar13 & 0x1f);
        }
        else {
          uVar1 = *(ushort *)(puVar11 + (uVar4 >> 3));
          uVar7 = ((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 << (uVar4 & 7) & 0xffff) >>
                  (uVar13 & 0x1f);
LAB_ram_430090b4:
          bits->used_bits = uVar4 + uVar12;
        }
      } while ((uVar9 == uVar7) && (uVar4 = uVar4 + uVar12, (int)uVar6 < (int)param_4));
    }
    uVar6 = uVar6 + uVar7;
    sections->end = uVar6;
    iVar8 = uVar6 - uVar2;
    if ((iVar8 == param_6) && (iVar8 < (int)param_4)) {
      uVar2 = uVar6 + (param_5 - param_6);
      sections[1].end = uVar2;
      sections[1].codebook = 0;
      uVar5 = uVar5 + 2;
      sections = sections + 2;
      uVar6 = uVar2;
    }
    else {
      uVar5 = uVar5 + 1;
      if (param_6 < iVar8) break;
      sections = sections + 1;
    }
    uVar4 = uVar6;
    if ((int)uVar6 < (int)uVar5) {
      uVar4 = uVar5;
    }
  } while ((int)uVar4 < (int)param_4);
  if ((uVar6 == param_4) && ((int)uVar5 <= (int)param_4)) {
    return uVar5;
  }
  return 0;
}
