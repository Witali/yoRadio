/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: pns_left @ ram:4300bd26
 * Types and parameter counts are inferred; verify against disassembly. */

void pns_left(int param_1,int *param_2,int *param_3,undefined4 *param_4,int param_5,uint param_6,
             int param_7,int param_8,undefined4 param_9)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  short *psVar4;
  int iVar5;
  int iVar6;
  undefined4 *puVar7;
  int iVar8;
  int iVar9;
  short *psVar10;
  short *psVar11;
  int *piVar12;
  int iVar13;
  int iVar14;
  int iVar15;

  gp = &__global_pointer_;
  iVar6 = 0;
  iVar8 = 0;
  iVar2 = 0;
  do {
    iVar6 = iVar6 * 4 + param_1;
    iVar5 = *(int *)(iVar6 + 0x30);
    psVar4 = *(short **)(iVar6 + 0x70);
    iVar6 = *param_2;
    iVar15 = iVar2 * 4 + param_1;
    param_2 = param_2 + 1;
    psVar11 = psVar4 + iVar5;
    puVar7 = param_4;
    iVar9 = iVar2;
    do {
      if (0 < iVar5) {
        puVar1 = puVar7;
        psVar10 = psVar4;
        piVar12 = param_3;
        iVar13 = 0;
        do {
          while (iVar14 = (int)*psVar10, *piVar12 != 0xd) {
            iVar8 = iVar8 + 1;
LAB_ram_4300bdba:
            psVar10 = psVar10 + 1;
            piVar12 = piVar12 + 1;
            puVar1 = puVar1 + 1;
            iVar13 = iVar14;
            if (psVar10 == psVar11) goto LAB_ram_4300be16;
          }
          if ((param_6 & *(uint *)(param_5 + iVar8 * 4)) != 0) goto LAB_ram_4300bdba;
          uVar3 = gen_rand_vector(iVar13 * 4 + param_7,iVar14 - iVar13,param_9,*puVar1);
          *(undefined4 *)(param_8 + iVar8 * 4) = uVar3;
          psVar10 = psVar10 + 1;
          iVar8 = iVar8 + 1;
          piVar12 = piVar12 + 1;
          puVar1 = puVar1 + 1;
          iVar13 = iVar14;
        } while (psVar10 != psVar11);
      }
LAB_ram_4300be16:
      iVar9 = iVar9 + 1;
      param_7 = param_7 + *(int *)(iVar15 + 0x10) * 4;
      puVar7 = puVar7 + iVar5;
      iVar15 = iVar15 + 4;
    } while (iVar9 < iVar6);
    iVar9 = 0;
    if (iVar2 < iVar6) {
      iVar9 = (iVar6 - iVar2) + -1;
    }
    param_3 = param_3 + *(int *)((iVar9 + iVar2) * 4 + param_1 + 0x30);
    param_4 = (undefined4 *)((int)param_4 + iVar5 * 4 * iVar9 + iVar5 * 4);
    iVar2 = iVar2 + 1 + iVar9;
    if (*(int *)(param_1 + 4) <= iVar6) {
      return;
    }
  } while( true );
}
