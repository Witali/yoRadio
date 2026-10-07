/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: get_ele_list @ ram:43007a10
 * Types and parameter counts are inferred; verify against disassembly. */

void get_ele_list(aac_analysis_elements_t *elements,aac_analysis_bits_t *bits,int param_3)

{
  ushort uVar1;
  int32_t *piVar2;
  ushort *puVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  uint8_t *puVar8;

  gp = &__global_pointer_;
  iVar7 = elements->count;
  if (0 < iVar7) {
    puVar8 = bits->buffer;
    piVar2 = elements->tag;
    do {
      while( true ) {
        uVar5 = 0;
        if (param_3 != 0) {
          uVar4 = bits->used_bits;
          if (uVar4 >> 3 < bits->input_length) {
            uVar5 = ((uint)puVar8[uVar4 >> 3] << (uVar4 & 7)) >> 7 & 1;
          }
          bits->used_bits = uVar4 + 1;
        }
        piVar2[-0x10] = uVar5;
        uVar4 = bits->used_bits;
        uVar5 = 0;
        uVar6 = bits->input_length - (uVar4 >> 3);
        puVar3 = (ushort *)(puVar8 + (uVar4 >> 3));
        if (1 < uVar6) break;
        if (uVar6 != 1) goto LAB_ram_43007a3c;
        uVar1 = *puVar3;
        bits->used_bits = uVar4 + 4;
        iVar7 = iVar7 + -1;
        *piVar2 = (((uint)(byte)uVar1 << 8) << (uVar4 & 7)) >> 0xc & 0xf;
        piVar2 = piVar2 + 1;
        if (iVar7 == 0) {
          gp = &__global_pointer_;
          return;
        }
      }
      uVar1 = *puVar3;
      uVar5 = (((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 << (uVar4 & 7)) << 0x10) >> 0x1c;
LAB_ram_43007a3c:
      bits->used_bits = uVar4 + 4;
      iVar7 = iVar7 + -1;
      *piVar2 = uVar5;
      piVar2 = piVar2 + 1;
    } while (iVar7 != 0);
  }
  return;
}
