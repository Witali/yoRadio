/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: get_ics_info @ ram:43007ab6
 * Types and parameter counts are inferred; verify against disassembly. */

uint get_ics_info(aac_analysis_bits_t *bits,int param_2,uint *param_3,uint *param_4,
                 undefined4 *param_5,uint *param_6,aac_analysis_window_t **window_map,
                 aac_analysis_ltp_t *left_ltp,aac_analysis_ltp_t *right_ltp)

{
  ushort uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  aac_analysis_window_t *paVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint8_t *puVar9;

  gp = &__global_pointer_;
  uVar2 = bits->used_bits;
  puVar9 = bits->buffer;
  uVar8 = bits->input_length - (uVar2 >> 3);
  if (uVar8 < 2) {
    if (uVar8 == 1) {
      uVar8 = (uint)(byte)*(ushort *)(puVar9 + (uVar2 >> 3)) << 8;
      goto LAB_ram_43007aec;
    }
    paVar5 = *window_map;
    bits->used_bits = uVar2 + 4;
    *param_4 = 0;
    uVar2 = paVar5->bands_per_window[0];
    uVar3 = 0;
  }
  else {
    uVar1 = *(ushort *)(puVar9 + (uVar2 >> 3));
    uVar8 = (uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 & 0xffff;
LAB_ram_43007aec:
    uVar8 = uVar8 << (uVar2 & 7);
    uVar3 = uVar8 >> 0xd & 3;
    paVar5 = window_map[uVar3];
    bits->used_bits = uVar2 + 4;
    *param_4 = uVar8 >> 0xc & 1;
    uVar2 = paVar5->bands_per_window[0];
    if (uVar3 == 2) {
      uVar8 = bits->used_bits;
      uVar7 = bits->input_length - (uVar8 >> 3);
      if (uVar7 < 2) {
        uVar4 = 0;
        uVar6 = 0;
        if (uVar7 == 1) {
          uVar4 = (((uint)(byte)*(ushort *)(puVar9 + (uVar8 >> 3)) << 8) << (uVar8 & 7)) >> 0xc &
                  0xf;
          uVar6 = (uint)(uVar2 < uVar4);
        }
      }
      else {
        uVar1 = *(ushort *)(puVar9 + (uVar8 >> 3));
        uVar4 = (((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 << (uVar8 & 7)) << 0x10) >> 0x1c;
        uVar6 = (uint)(uVar2 < uVar4);
      }
      bits->used_bits = uVar8 + 4;
      getgroup(param_5,bits);
      goto LAB_ram_43007b6c;
    }
  }
  *param_5 = 1;
  uVar8 = bits->used_bits;
  uVar7 = bits->input_length - (uVar8 >> 3);
  if (uVar7 < 2) {
    uVar4 = 0;
    uVar6 = 0;
    if (uVar7 == 1) {
      uVar7 = ((uint)(byte)*(ushort *)(puVar9 + (uVar8 >> 3)) << 8) << (uVar8 & 7);
      uVar4 = uVar7 >> 10 & 0x3f;
      uVar6 = (uint)(uVar2 < uVar4) | uVar7 >> 9 & 1;
    }
  }
  else {
    uVar1 = *(ushort *)(puVar9 + (uVar8 >> 3));
    uVar7 = ((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 & 0xffff) << (uVar8 & 7);
    uVar4 = uVar7 >> 10 & 0x3f;
    uVar6 = (uint)(uVar2 < uVar4) | uVar7 >> 9 & 1;
  }
  bits->used_bits = uVar8 + 7;
LAB_ram_43007b6c:
  left_ltp->present = 0;
  if (param_2 != 0) {
    right_ltp->present = 0;
  }
  *param_6 = uVar4;
  *param_3 = uVar3;
  return uVar6;
}
