/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: infoinit @ ram:4300a158
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4 infoinit(int param_1,aac_analysis_window_t **window_map,int *param_3)

{
  short sVar1;
  undefined1 *puVar2;
  int iVar3;
  short *psVar4;
  int iVar5;
  int iVar6;
  int32_t *piVar7;
  undefined1 *puVar8;
  int iVar9;
  aac_analysis_window_t *paVar10;
  int32_t *piVar11;
  short *psVar12;
  aac_analysis_window_t *paVar13;
  int iVar14;
  int32_t *piVar15;
  int32_t iVar16;
  aac_analysis_window_t **ppaVar17;

  gp = &__global_pointer_;
  iVar9 = samp_rate_info.entry[param_1].rate;
  if (iVar9 == 32000) {
    puVar8 = (undefined1 *)&sfb_48_128;
    puVar2 = sfb_32_1024;
  }
  else if (iVar9 < 0x7d01) {
    if (iVar9 != 12000) {
      if (iVar9 < 0x2ee1) {
        if (iVar9 == 8000) {
          puVar8 = sfb_8_128;
          puVar2 = sfb_8_1024;
          goto LAB_ram_4300a1d8;
        }
        if (iVar9 != 0x2b11) {
LAB_ram_4300a274:
          gp = &__global_pointer_;
          return 0xffffffff;
        }
      }
      else {
        if ((iVar9 == 0x5622) || (iVar9 == 24000)) {
          puVar8 = sfb_24_128;
          puVar2 = sfb_24_1024;
          goto LAB_ram_4300a1d8;
        }
        if (iVar9 != 16000) goto LAB_ram_4300a274;
      }
    }
    puVar8 = sfb_16_128;
    puVar2 = sfb_16_1024;
  }
  else if (iVar9 == 64000) {
    puVar8 = sfb_64_128;
    puVar2 = sfb_64_1024;
  }
  else if (iVar9 < 0xfa01) {
    if ((iVar9 != 0xac44) && (iVar9 != 48000)) goto LAB_ram_4300a274;
    puVar8 = (undefined1 *)&sfb_48_128;
    puVar2 = sfb_48_1024;
  }
  else {
    if ((iVar9 != 0x15888) && (iVar9 != 96000)) {
      gp = &__global_pointer_;
      return 0xffffffff;
    }
    puVar8 = sfb_64_128;
    puVar2 = sfb_96_1024;
  }
LAB_ram_4300a1d8:
  iVar16 = samp_rate_info.entry[param_1].long_bands;
  paVar10 = *window_map;
  paVar13 = window_map[2];
  iVar9 = samp_rate_info.entry[param_1].short_bands;
  paVar10->is_long = 1;
  paVar10->windows = 1;
  paVar10->groups = 1;
  paVar10->group_length[0] = 1;
  paVar10->coefficients_per_frame = 0x400;
  paVar10->bands_per_window[0] = iVar16;
  paVar10->band_top[0] = (int16_t *)puVar2;
  paVar10->short_band_width = (int32_t *)0x0;
  paVar10->section_bits[0] = 5;
  paVar13->coefficients_per_frame = 0x400;
  paVar13->windows = 8;
  paVar13->is_long = 0;
  piVar11 = paVar13->bands_per_window;
  do {
    *piVar11 = iVar9;
    piVar11[8] = 3;
    piVar11[0x10] = (int32_t)puVar8;
    piVar11 = piVar11 + 1;
  } while (piVar11 != paVar13->section_bits);
  paVar13->short_band_width = param_3;
  if (0 < iVar9) {
    psVar4 = (short *)((int)puVar8 + iVar9 * 2);
    iVar9 = 0;
    do {
      sVar1 = *(short *)puVar8;
      puVar8 = (undefined1 *)((int)puVar8 + 2);
      *param_3 = sVar1 - iVar9;
      param_3 = param_3 + 1;
      iVar9 = (int)sVar1;
    } while ((short *)puVar8 != psVar4);
  }
  ppaVar17 = window_map + 4;
  do {
    paVar10 = *window_map;
    if (paVar10 != (aac_analysis_window_t *)0x0) {
      iVar9 = paVar10->windows;
      paVar10->bands_per_frame = 0;
      if (0 < iVar9) {
        piVar11 = paVar10->coefficients_per_window;
        iVar3 = paVar10->coefficients_per_frame / iVar9;
        piVar15 = piVar11 + iVar9;
        iVar5 = 0;
        iVar9 = 0;
        do {
          iVar6 = piVar11[8];
          *piVar11 = iVar3;
          iVar14 = iVar9 + iVar6;
          if (0 < iVar6) {
            psVar12 = (short *)piVar11[0x18];
            psVar4 = psVar12 + iVar6;
            piVar7 = paVar10->frame_band_top + iVar9;
            do {
              sVar1 = *psVar12;
              psVar12 = psVar12 + 1;
              *piVar7 = sVar1 + iVar5;
              piVar7 = piVar7 + 1;
            } while (psVar4 != psVar12);
          }
          piVar11 = piVar11 + 1;
          iVar5 = iVar5 + iVar3;
          iVar9 = iVar14;
        } while (piVar11 != piVar15);
        paVar10->bands_per_frame = iVar14;
      }
    }
    window_map = window_map + 1;
  } while (window_map != ppaVar17);
  return 0;
}
