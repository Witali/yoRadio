/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: calc_gsfb_table @ ram:43001760
 * Types and parameter counts are inferred; verify against disassembly. */

void calc_gsfb_table(aac_analysis_window_t *window,int *param_2)

{
  int *piVar1;
  int iVar2;
  int32_t *piVar3;
  int iVar4;
  int iVar5;
  int32_t *piVar6;
  int iVar7;
  int iVar8;
  int *piVar9;
  int iVar10;
  int32_t *piVar11;

  gp = &__global_pointer_;
  piVar1 = (int *)memset(window->frame_band_top,0,0x200);
  iVar5 = 0;
  piVar3 = window->group_length;
  iVar8 = 0;
  do {
    iVar7 = iVar8;
    *piVar3 = *param_2 - iVar5;
    iVar5 = *param_2;
    iVar8 = iVar7 + 1;
    param_2 = param_2 + 1;
    piVar3 = piVar3 + 1;
  } while (iVar5 < 8);
  piVar11 = window->short_band_width;
  window->groups = iVar8;
  piVar3 = window->bands_per_window;
  iVar8 = 0;
  do {
    iVar5 = *piVar3;
    if (0 < iVar5) {
      iVar2 = piVar3[0x9a];
      iVar4 = iVar5;
      piVar6 = piVar11;
      piVar9 = piVar1;
      do {
        iVar10 = *piVar6;
        iVar4 = iVar4 + -1;
        piVar6 = piVar6 + 1;
        iVar8 = iVar8 + iVar2 * iVar10;
        *piVar9 = iVar8;
        piVar9 = piVar9 + 1;
      } while (iVar4 != 0);
      piVar1 = piVar1 + iVar5;
    }
    piVar3 = piVar3 + 1;
  } while (piVar3 != window->bands_per_window + iVar7 + 1);
  return;
}
