/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: huffspec_fxp @ ram:43009692
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4
huffspec_fxp(aac_analysis_window_t *window,aac_analysis_bits_t *bits,int param_3,
            aac_analysis_section_t *sections,int param_5,int param_6,int param_7,int param_8,
            aac_analysis_window_t *pulse_window,aac_analysis_pulse_t *pulse,int param_11)

{
  int32_t *piVar1;
  int iVar2;
  int32_t *piVar3;
  uint *puVar4;
  undefined4 uVar5;
  int iVar6;
  uint uVar7;
  int32_t *piVar8;
  int32_t *piVar9;
  int iVar10;
  int iVar11;
  uint uVar12;
  code *pcVar13;
  int iVar14;
  code *pcVar15;
  int iVar16;
  int *piVar17;
  int iVar18;
  int iStack_78;
  uint auStack_44 [4];

  gp = &__global_pointer_;
  auStack_44[0] = 0;
  if (param_3 < 1) {
LAB_ram_430097d0:
    if (window->is_long == 0) {
      deinterleave(param_7,param_8,window);
      param_7 = param_8;
    }
    else if (pulse->present == 1) {
      pulse_nc((short *)param_7,pulse,pulse_window,(int *)auStack_44);
    }
    if (auStack_44[0] < 0x2001) {
      iVar6 = pv_normalize(auStack_44[0] *
                           (*(int *)(inverseQuantTable + ((int)auStack_44[0] >> 3) * 4 + 4) +
                            0x7ffffffU >> 0x1a));
      if (0x1b < iVar6) {
        iVar6 = 0x1b;
      }
      iStack_78 = window->windows;
      if (0 < iStack_78) {
        iVar18 = window->bands_per_window[0];
        iVar11 = 0;
        if (0 < iVar18) {
          do {
            iVar14 = 0;
            puVar4 = (uint *)(param_5 + iVar11 * 4);
            piVar17 = (int *)(iVar11 * 4 + param_11);
            iVar2 = iVar18 + iVar11;
            iVar16 = 0;
            do {
              iVar10 = (int)*(short *)((int)window->band_top[0] + iVar14);
              uVar12 = iVar10 - iVar16;
              if (0x400 < uVar12) {
                return 0xffffffff;
              }
              uVar7 = *puVar4;
              *piVar17 = iVar6;
              esc_iquant_scaling(param_7,param_6,uVar12,iVar6,
                                 *(undefined2 *)((int)&exptable + (uVar7 & 3) * 2),auStack_44[0]);
              iVar11 = iVar11 + 1;
              *piVar17 = *piVar17 - (((int)(uVar7 - 100) >> 2) + 1);
              param_7 = param_7 + uVar12 * 2;
              iVar14 = iVar14 + 2;
              puVar4 = puVar4 + 1;
              piVar17 = piVar17 + 1;
              param_6 = param_6 + uVar12 * 4;
              iVar16 = iVar10;
            } while (iVar11 != iVar2);
            iStack_78 = iStack_78 + -1;
          } while (iStack_78 != 0);
        }
      }
      return 0;
    }
  }
  else {
    uVar12 = sections->codebook;
    piVar8 = (int32_t *)0x0;
    piVar1 = window->frame_band_top;
    iVar6 = 0;
    while ((uVar12 < 0x10 && (iVar18 = sections->end, -1 < iVar18))) {
      if ((uVar12 - 1 & 0xc) == 0xc) {
        piVar1 = window->frame_band_top + iVar18;
        uVar12 = (int)piVar1[-1] - (int)piVar8;
        if (0x400 < uVar12) {
          return 0xffffffff;
        }
        memset(param_7 + (int)piVar8 * 2,0,uVar12 * 2);
        memset(param_8 + (int)piVar8 * 2,0,uVar12 * 2);
        piVar8 = (int32_t *)piVar1[-1];
      }
      else {
        if ((int)uVar12 < 5) {
          uVar7 = uVar12;
          if (hcbbook_binary.entry[uVar12].signed_codebook == 0) {
            if (uVar12 == 3) {
              pcVar13 = unpack_idx_sgn;
              pcVar15 = decode_huff_cw_tab3;
              uVar7 = 4;
            }
            else if (uVar12 == 4) {
              pcVar13 = unpack_idx_sgn;
              pcVar15 = decode_huff_cw_tab4;
            }
            else {
              pcVar13 = unpack_idx_sgn;
LAB_ram_43009890:
              if (uVar12 == 1) {
                pcVar15 = decode_huff_cw_tab1;
                uVar7 = 4;
              }
              else {
                pcVar15 = decode_huff_cw_tab2;
                uVar7 = 4;
              }
            }
          }
          else if (uVar12 == 3) {
            uVar7 = 4;
            pcVar13 = unpack_idx;
            pcVar15 = decode_huff_cw_tab3;
          }
          else {
            pcVar13 = unpack_idx;
            if (uVar12 != 4) goto LAB_ram_43009890;
            pcVar13 = unpack_idx;
            pcVar15 = decode_huff_cw_tab4;
          }
        }
        else if (uVar12 == 0xb) {
          pcVar13 = unpack_idx_esc;
          pcVar15 = decode_huff_cw_tab11;
          uVar7 = 2;
        }
        else {
          if (hcbbook_binary.entry[uVar12].signed_codebook == 0) {
            pcVar13 = unpack_idx_sgn;
          }
          else {
            pcVar13 = unpack_idx;
          }
          if (uVar12 == 6) {
            pcVar15 = decode_huff_cw_tab6;
            uVar7 = 2;
          }
          else if ((int)uVar12 < 7) {
            pcVar15 = decode_huff_cw_tab5;
            uVar7 = 2;
          }
          else if (uVar12 == 9) {
            pcVar15 = decode_huff_cw_tab9;
            uVar7 = 2;
          }
          else if ((int)uVar12 < 10) {
            if (uVar12 == 7) {
              pcVar15 = decode_huff_cw_tab7;
              uVar7 = 2;
            }
            else {
              pcVar15 = decode_huff_cw_tab8;
              uVar7 = 2;
            }
          }
          else {
            if (uVar12 != 10) {
              return 0xffffffff;
            }
            pcVar15 = decode_huff_cw_tab10;
            uVar7 = 2;
          }
        }
        if (iVar6 < iVar18) {
          iVar11 = (int)piVar8 * 2 + param_7;
          piVar3 = piVar8;
          piVar9 = piVar1;
          iVar16 = iVar6;
          do {
            piVar8 = (int32_t *)*piVar9;
            piVar9 = piVar9 + 1;
            for (iVar2 = (int)piVar8 - (int)piVar3; iVar2 - 1U < 0x3ff; iVar2 = iVar2 - uVar7) {
              uVar5 = (*pcVar15)(bits);
              (*pcVar13)(iVar11,uVar5,hcbbook_binary.entry + uVar12,bits,auStack_44);
              iVar11 = iVar11 + uVar7 * 2;
            }
            iVar16 = iVar16 + 1;
            piVar3 = piVar8;
          } while (iVar18 != iVar16);
          piVar1 = piVar1 + (iVar18 - iVar6);
        }
      }
      if (param_3 == 1) goto LAB_ram_430097d0;
      param_3 = param_3 + -1;
      sections = sections + 1;
      uVar12 = sections->codebook;
      iVar6 = iVar18;
    }
  }
  return 0xffffffff;
}
