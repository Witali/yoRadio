/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: deinterleave @ ram:430055e4
 * Types and parameter counts are inferred; verify against disassembly. */

void deinterleave(int param_1,int param_2,aac_analysis_window_t *window)

{
  int iVar1;
  int32_t *piVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  aac_analysis_window_t *paVar9;
  int iVar10;

  gp = &__global_pointer_;
  iVar5 = window->groups;
  paVar9 = window;
  if (0 < iVar5) {
    do {
      iVar7 = paVar9->bands_per_window[0];
      iVar10 = param_1;
      if (0 < iVar7) {
        piVar2 = window->short_band_width;
        iVar8 = 0;
        do {
          iVar1 = paVar9->group_length[0];
          iVar4 = *piVar2;
          if (0 < iVar1) {
            iVar3 = iVar4 << 1;
            iVar6 = iVar8 * 2 + param_2;
            do {
              iVar6 = memcpy(iVar6,iVar10,iVar3);
              iVar4 = *piVar2;
              iVar1 = iVar1 + -1;
              iVar6 = iVar6 + 0x100;
              iVar3 = iVar4 * 2;
              iVar10 = iVar10 + iVar3;
            } while (iVar1 != 0);
          }
          iVar7 = iVar7 + -1;
          piVar2 = piVar2 + 1;
          iVar8 = iVar8 + iVar4;
        } while (iVar7 != 0);
        param_2 = param_2 + (iVar10 - param_1);
      }
      paVar9 = (aac_analysis_window_t *)&paVar9->windows;
      param_1 = iVar10;
    } while (paVar9 != (aac_analysis_window_t *)(window->coefficients_per_window + iVar5 + -4));
  }
  return;
}
