/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: ps_applied @ ram:4300c46e
 * Types and parameter counts are inferred; verify against disassembly. */

void ps_applied(int param_1,undefined4 param_2,undefined4 param_3,int *param_4,int *param_5,
               undefined4 param_6)

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
  int *piVar12;
  int iVar13;
  uint uVar14;
  int iVar15;

  gp = &__global_pointer_;
  ps_hybrid_analysis(param_2,param_3,*(undefined4 *)(param_1 + 0x1ec),
                     *(undefined4 *)(param_1 + 0x1f0),*(undefined4 *)(param_1 + 0x1fc));
  ps_decorrelate(param_1,param_2,param_3,param_4,param_5,param_6);
  ps_stereo_processing(param_1,param_2,param_3,param_4,param_5);
  ps_hybrid_synthesis(*(undefined4 *)(param_1 + 0x1ec),*(undefined4 *)(param_1 + 0x1f0),param_2,
                      param_3,*(undefined4 *)(param_1 + 0x1fc));
  piVar12 = *(int **)(param_1 + 0x1fc);
  if (*piVar12 < 1) {
    return;
  }
  piVar7 = (int *)piVar12[1];
  iVar6 = 0;
  piVar8 = *(int **)(param_1 + 500);
  piVar10 = *(int **)(param_1 + 0x1f8);
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
  } while (iVar6 < *piVar12);
  return;
}
