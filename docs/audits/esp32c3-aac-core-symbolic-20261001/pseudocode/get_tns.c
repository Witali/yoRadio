/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: get_tns @ ram:430085c4
 * Types and parameter counts are inferred; verify against disassembly. */

void get_tns(int param_1,aac_analysis_bits_t *bits,int param_3,aac_analysis_window_t *window,
            aac_analysis_mc_t *mc,aac_analysis_tns_t *tns,undefined4 param_7)

{
  ushort uVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  int32_t iVar5;
  int iVar6;
  uint8_t *puVar7;
  uint uVar8;
  int32_t *piVar9;
  int iVar10;
  uint uVar11;
  int16_t *piVar12;
  int32_t iVar13;
  uint uVar14;
  uint uVar15;
  uint uVar16;
  uint uVar17;
  int iVar18;
  int iVar19;
  aac_analysis_tns_filter_t *paVar20;
  int32_t iVar21;
  int iVar22;
  int32_t *piVar23;
  int iVar24;
  int iVar25;
  uint uVar26;
  aac_analysis_tns_filter_t *paVar27;
  int32_t *piVar28;
  uint uStack_74;
  uint uStack_70;
  uint uStack_6c;

  gp = &__global_pointer_;
  iVar10 = mc->sample_rate_index;
  piVar12 = window->band_top[0];
  if (param_3 == 2) {
    iVar22 = *(int *)(tns_max_bands_tbl_short_wndw + iVar10 * 4);
    iVar6 = 1;
    uStack_70 = 7;
    iVar10 = 4;
    iVar25 = 3;
  }
  else {
    iVar22 = *(int *)(tns_max_bands_tbl_long_wndw + iVar10 * 4);
    iVar6 = 2;
    if (iVar10 < 5) {
      uStack_70 = 0xc;
      iVar10 = 6;
      iVar25 = 5;
    }
    else {
      uStack_70 = 0x14;
      iVar10 = 6;
      iVar25 = 5;
    }
  }
  if (param_1 < iVar22) {
    iVar22 = param_1;
  }
  iVar13 = window->bands_per_window[0];
  piVar9 = tns->lpc;
  paVar27 = tns->filter;
  piVar23 = tns->filter_count;
  iVar24 = 0;
LAB_ram_43008686:
  while( true ) {
    uVar15 = bits->used_bits;
    uVar8 = bits->input_length;
    puVar7 = bits->buffer;
    uVar26 = uVar8 - (uVar15 >> 3);
    uVar4 = uVar15 + iVar6;
    if (1 < uVar26) break;
    if (uVar26 == 1) {
      iVar19 = (uint)(byte)*(ushort *)(puVar7 + (uVar15 >> 3)) << 8;
      goto LAB_ram_4300865c;
    }
    bits->used_bits = uVar4;
    *piVar23 = 0;
    iVar24 = iVar24 + 1;
    piVar23 = piVar23 + 1;
    if (window->windows <= iVar24) {
      return;
    }
  }
  uVar1 = *(ushort *)(puVar7 + (uVar15 >> 3));
  iVar19 = (uint)(uVar1 >> 8) + (uint)uVar1 * 0x100;
LAB_ram_4300865c:
  bits->used_bits = uVar4;
  uVar15 = (iVar19 << (uVar15 & 7) & 0xffffU) >> (0x10U - iVar6 & 0x1f);
  *piVar23 = uVar15;
  if (uVar15 != 0) {
    if (uVar4 >> 3 < uVar8) {
      uStack_6c = ((uint)puVar7[uVar4 >> 3] << (uVar4 & 7)) >> 7 & 1;
      uStack_74 = uStack_6c + 1;
    }
    else {
      uStack_74 = 1;
      uStack_6c = 0;
    }
    uVar4 = uVar4 + 1;
    bits->used_bits = uVar4;
    paVar20 = paVar27;
    iVar21 = iVar13;
    uVar26 = uVar15;
    do {
      iVar19 = iVar22;
      if (iVar21 < iVar22) {
        iVar19 = iVar21;
      }
      iVar18 = 0;
      if (iVar19 != 0) {
        iVar18 = (int)piVar12[iVar19 + 0x7fffffff];
      }
      uVar11 = uVar8 - (uVar4 >> 3);
      paVar20->stop_band = iVar19;
      paVar20->stop_coefficient = iVar18;
      if (uVar11 < 2) {
        uVar16 = 0;
        if (uVar11 == 1) {
          uVar16 = (((uint)(byte)*(ushort *)(puVar7 + (uVar4 >> 3)) << 8) << (uVar4 & 7) & 0xffff)
                   >> (0x10U - iVar10 & 0x1f);
        }
      }
      else {
        uVar1 = *(ushort *)(puVar7 + (uVar4 >> 3));
        uVar16 = ((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 << (uVar4 & 7) & 0xffff) >>
                 (0x10U - iVar10 & 0x1f);
      }
      uVar4 = iVar10 + uVar4;
      iVar21 = iVar21 - uVar16;
      bits->used_bits = uVar4;
      iVar19 = iVar22;
      if (iVar21 < iVar22) {
        iVar19 = iVar21;
      }
      iVar3 = 0;
      if (iVar19 != 0) {
        iVar3 = (int)piVar12[iVar19 + 0x7fffffff];
      }
      paVar20->start_band = iVar19;
      uVar11 = uVar8 - (uVar4 >> 3);
      paVar20->start_coefficient = iVar3;
      uVar16 = uVar4 + iVar25;
      if (uVar11 < 2) {
        if (uVar11 == 1) {
          iVar19 = (uint)(byte)*(ushort *)(puVar7 + (uVar4 >> 3)) << 8;
          goto LAB_ram_430087b4;
        }
        bits->used_bits = uVar16;
LAB_ram_430087c8:
        paVar20->order = 0;
        piVar28 = piVar9;
      }
      else {
        uVar1 = *(ushort *)(puVar7 + (uVar4 >> 3));
        iVar19 = (uint)uVar1 * 0x100 + (uint)(uVar1 >> 8);
LAB_ram_430087b4:
        bits->used_bits = uVar16;
        uVar4 = (iVar19 << (uVar4 & 7) & 0xffffU) >> (0x10U - iVar25 & 0x1f);
        if (uVar4 == 0) goto LAB_ram_430087c8;
        uVar11 = uStack_70;
        if (uVar4 < uStack_70) {
          uVar11 = uVar4;
        }
        paVar20->order = uVar11;
        uVar4 = 1;
        if (uVar16 >> 3 < uVar8) {
          uVar4 = (int)(((uint)puVar7[uVar16 >> 3] << (uVar16 & 7)) << 0x18) >> 0x1f | 1;
        }
        uVar14 = uVar16 + 1;
        bits->used_bits = uVar14;
        paVar20->direction = uVar4;
        uVar4 = uStack_74;
        if (uVar14 >> 3 < uVar8) {
          uVar4 = uStack_74 - (((uint)puVar7[uVar14 >> 3] << (uVar14 & 7)) >> 7 & 1);
        }
        uVar16 = uVar16 + 2;
        bits->used_bits = uVar16;
        uVar14 = uVar11;
        piVar28 = piVar9;
        do {
          uVar2 = uVar8 - (uVar16 >> 3);
          if (uVar2 < 2) {
            uVar17 = 0;
            if (uVar2 == 1) {
              iVar19 = (uint)(byte)*(ushort *)(puVar7 + (uVar16 >> 3)) << 8;
              goto LAB_ram_43008860;
            }
          }
          else {
            uVar1 = *(ushort *)(puVar7 + (uVar16 >> 3));
            iVar19 = (uint)(uVar1 >> 8) + (uint)uVar1 * 0x100;
LAB_ram_43008860:
            uVar17 = (iVar19 << (uVar16 & 7) & 0xffffU) >> (0x10 - (uVar4 + 2) & 0x1f);
            uVar17 = -(2 << (uVar4 & 0x1f) & uVar17) | uVar17;
          }
          uVar16 = uVar16 + uVar4 + 2;
          bits->used_bits = uVar16;
          uVar14 = uVar14 - 1;
          *piVar28 = uVar17;
          piVar28 = piVar28 + 1;
        } while (uVar14 != 0);
        piVar28 = piVar9 + uVar11;
        if (iVar18 != iVar3) {
          iVar5 = tns_decode_coef(uVar11,uStack_6c,piVar9,param_7);
          paVar20->lpc_q = iVar5;
        }
      }
      piVar9 = piVar28;
      if (uVar26 == 1) goto LAB_ram_430088f8;
      uVar26 = uVar26 - 1;
      uVar4 = bits->used_bits;
      puVar7 = bits->buffer;
      uVar8 = bits->input_length;
      paVar20 = paVar20 + 1;
    } while( true );
  }
  goto LAB_ram_4300867a;
LAB_ram_430088f8:
  paVar27 = paVar27 + uVar15;
LAB_ram_4300867a:
  iVar24 = iVar24 + 1;
  piVar23 = piVar23 + 1;
  if (window->windows <= iVar24) {
    return;
  }
  goto LAB_ram_43008686;
}
