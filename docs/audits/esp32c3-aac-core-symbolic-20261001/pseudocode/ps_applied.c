/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: ps_applied @ ram:4300c46e
 * Types and parameter counts are inferred; verify against disassembly. */

void ps_applied(aac_ps_abi_t *ps,int param_2,int param_3,int *param_4,int *param_5,int param_6)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  int *piVar7;
  int *piVar8;
  int *piVar9;
  int *piVar10;
  int *piVar11;
  aac_hybrid_abi_t *paVar12;
  int iVar13;
  int in_a6;
  uint uVar14;
  int iVar15;

  gp = &__global_pointer_;
  ps_hybrid_analysis(param_2,param_3,(int)ps->hybrid_left_real,(int)ps->hybrid_left_imag,ps->hybrid,
                     param_6,in_a6);
  ps_decorrelate(ps,param_2,param_3,(int)param_4,(int)param_5,param_6);
  ps_stereo_processing(ps,param_2,param_3,(int)param_4,(int)param_5);
  ps_hybrid_synthesis(ps->hybrid_left_real,ps->hybrid_left_imag,param_2,param_3,ps->hybrid);
  paVar12 = ps->hybrid;
  if (paVar12->bands < 1) {
    return;
  }
  piVar7 = paVar12->resolution;
  iVar6 = 0;
  piVar8 = ps->hybrid_right_real;
  piVar10 = ps->hybrid_right_imag;
  do {
    iVar4 = *piVar7;
    iVar15 = *piVar8 + piVar8[1];
    piVar9 = piVar8 + 2;
    iVar13 = *piVar10 + piVar10[1];
    piVar11 = piVar10 + 2;
    if (6 < iVar4) {
      iVar4 = 6;
    }
    uVar5 = iVar4 - 2U >> 1;
    uVar14 = uVar5;
    if (uVar5 != 0) {
      do {
        iVar3 = *piVar9;
        iVar4 = *piVar11;
        uVar14 = uVar14 - 1;
        piVar1 = piVar9 + 1;
        piVar2 = piVar11 + 1;
        piVar9 = piVar9 + 2;
        piVar11 = piVar11 + 2;
        iVar15 = iVar3 + iVar15 + *piVar1;
        iVar13 = iVar13 + iVar4 + *piVar2;
      } while (uVar14 != 0);
      piVar11 = piVar10 + (uVar5 - 1) * 2 + 4;
      piVar9 = piVar8 + (uVar5 - 1) * 2 + 4;
    }
    *param_4 = iVar15;
    *param_5 = iVar13;
    iVar6 = iVar6 + 1;
    param_4 = param_4 + 1;
    param_5 = param_5 + 1;
    piVar7 = piVar7 + 1;
    piVar8 = piVar9;
    piVar10 = piVar11;
  } while (iVar6 < paVar12->bands);
  return;
}
