/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: pns_intensity_right @ ram:42046840
 * Types and parameter counts are inferred; verify against disassembly. */

void pns_intensity_right(uint param_1,int param_2,int *param_3,uint *param_4,int *param_5,
                        int *param_6,int *param_7,int param_8,uint param_9,int param_10,int param_11
                        ,int param_12,int param_13,undefined4 param_14)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 *puVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  uint uVar10;
  uint uVar11;
  int iVar12;
  int iVar13;
  uint *puVar14;
  int iVar15;
  int iVar16;
  short *psVar17;
  int *piVar18;
  undefined4 *puVar19;
  uint *puVar20;
  int *piVar21;
  int *piVar22;
  int iVar23;

  gp = &__global_pointer_;
  iVar23 = *(int *)(param_2 + 0x10);
  iVar1 = *(int *)(param_2 + 0x30);
  iVar2 = 0;
  iVar8 = 0;
  do {
    iVar6 = *param_3;
    iVar3 = iVar6 - iVar8;
    if (0 < iVar1) {
      puVar19 = (undefined4 *)(param_12 + iVar2 * 4);
      puVar14 = (uint *)(param_8 + iVar2 * 4);
      iVar16 = iVar1 + iVar2;
      iVar15 = 0;
      psVar17 = *(short **)(iVar8 * 4 + param_2 + 0x70);
      piVar18 = param_5;
      puVar20 = param_4;
      piVar21 = param_6;
      piVar22 = param_7;
      do {
        while( true ) {
          iVar9 = *piVar18;
          iVar13 = (int)*psVar17;
          piVar18 = piVar18 + 1;
          iVar8 = iVar13 - iVar15;
          uVar11 = *puVar20;
          if (iVar9 == 0xd) break;
          if (0xd < iVar9) {
            intensity_right(*piVar22,iVar23,iVar1,iVar3,iVar8,iVar9,uVar11 & param_1,puVar19,
                            iVar2 * 4 + param_13,iVar15 * 4 + param_10,param_11 + iVar15 * 4);
          }
LAB_ram_420468e4:
          iVar2 = iVar2 + 1;
          piVar21 = piVar21 + 1;
          piVar22 = piVar22 + 1;
          puVar19 = puVar19 + 1;
          puVar14 = puVar14 + 1;
          iVar15 = iVar13;
          psVar17 = psVar17 + 1;
          puVar20 = puVar20 + 1;
          if (iVar2 == iVar16) goto LAB_ram_42046960;
        }
        uVar10 = *puVar14;
        *puVar14 = uVar10 & param_9;
        if ((uVar10 & param_9) != 0) goto LAB_ram_420468e4;
        iVar9 = param_11 + iVar15 * 4;
        if ((uVar11 & param_1) == 0) {
          if (0 < iVar3) {
            puVar4 = (undefined4 *)(param_13 + iVar2 * 4);
            iVar15 = iVar3;
            do {
              uVar5 = gen_rand_vector(iVar9,iVar8,param_14,*piVar22);
              *puVar4 = uVar5;
              iVar15 = iVar15 + -1;
              iVar9 = iVar9 + iVar23 * 4;
              puVar4 = puVar4 + iVar1;
            } while (iVar15 != 0);
          }
          goto LAB_ram_420468e4;
        }
        iVar7 = *piVar21;
        iVar12 = iVar2 * 4;
        iVar2 = iVar2 + 1;
        piVar21 = piVar21 + 1;
        pns_corr(*piVar22 - iVar7,iVar23,iVar1,iVar3,iVar8,*puVar19,iVar12 + param_13,
                 param_10 + iVar15 * 4,iVar9);
        piVar22 = piVar22 + 1;
        puVar19 = puVar19 + 1;
        puVar14 = puVar14 + 1;
        iVar15 = iVar13;
        psVar17 = psVar17 + 1;
        puVar20 = puVar20 + 1;
      } while (iVar2 != iVar16);
LAB_ram_42046960:
      param_7 = param_7 + iVar1;
      param_6 = param_6 + iVar1;
      param_4 = param_4 + iVar1;
      param_5 = param_5 + iVar1;
      iVar2 = iVar16;
    }
    iVar8 = (iVar3 + -1) * iVar1;
    param_7 = param_7 + iVar8;
    iVar2 = iVar8 + iVar2;
    param_6 = param_6 + iVar8;
    iVar8 = iVar23 * iVar3 * 4;
    param_11 = param_11 + iVar8;
    param_10 = param_10 + iVar8;
    iVar8 = iVar6;
    param_3 = param_3 + 1;
    if (*(int *)(param_2 + 4) <= iVar6) {
      return;
    }
  } while( true );
}
