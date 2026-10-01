/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: apply_ms_synt @ ram:43000874
 * Types and parameter counts are inferred; verify against disassembly. */

void apply_ms_synt(int param_1,int *param_2,int *param_3,int *param_4,int param_5,int param_6,
                  int param_7,int param_8)

{
  int iVar1;
  short *psVar2;
  short *psVar3;
  int *piVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  short *psVar11;
  int *piVar12;
  int iVar13;
  int iVar14;
  int iVar15;

  gp = &__global_pointer_;
  iVar10 = *(int *)(param_1 + 0x30);
  iVar1 = *(int *)(param_1 + 0x10);
  iVar14 = 0;
  iVar15 = 0;
  do {
    iVar9 = *param_2;
    iVar13 = iVar9 - iVar15;
    if (0 < iVar10) {
      psVar2 = *(short **)(iVar15 * 4 + param_1 + 0x70);
      iVar8 = param_7 + iVar14 * 4;
      psVar11 = psVar2 + iVar10;
      iVar6 = iVar14 * 4 + param_8;
      piVar4 = param_4;
      iVar15 = 0;
      piVar12 = param_3;
      do {
        while( true ) {
          iVar5 = *piVar4;
          psVar3 = psVar2 + 1;
          piVar4 = piVar4 + 1;
          iVar7 = (int)*psVar2;
          psVar2 = psVar3;
          if ((0xc < iVar5) || (*piVar12 == 0)) break;
          ms_synt(iVar13,iVar1,iVar10,iVar7 - iVar15,iVar15 * 4 + param_5,param_6 + iVar15 * 4,iVar8
                  ,iVar6);
          iVar8 = iVar8 + 4;
          iVar6 = iVar6 + 4;
          iVar15 = iVar7;
          piVar12 = piVar12 + 1;
          if (psVar3 == psVar11) goto LAB_ram_43000946;
        }
        iVar8 = iVar8 + 4;
        iVar6 = iVar6 + 4;
        iVar15 = iVar7;
        piVar12 = piVar12 + 1;
      } while (psVar3 != psVar11);
LAB_ram_43000946:
      iVar14 = iVar14 + iVar10;
      param_3 = param_3 + iVar10;
      param_4 = param_4 + iVar10;
    }
    iVar15 = iVar1 * iVar13 * 4;
    param_6 = param_6 + iVar15;
    param_5 = param_5 + iVar15;
    iVar14 = iVar14 + (iVar13 + -1) * iVar10;
    iVar15 = iVar9;
    param_2 = param_2 + 1;
    if (*(int *)(param_1 + 4) <= iVar9) {
      return;
    }
  } while( true );
}
