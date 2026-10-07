/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: ps_allocate_decoder @ ram:4300c22c
 * Types and parameter counts are inferred; verify against disassembly. */

/* WARNING: Type propagation algorithm not settling */

void ps_allocate_decoder(int param_1,uint param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 *puVar5;
  int iVar6;
  int iVar7;
  int *piVar8;
  int iVar9;
  int *piVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  int local_40 [7];

  gp = &__global_pointer_;
  iVar13 = *(int *)(param_1 + 0xc984);
  *(uint *)(iVar13 + 0x10) = param_2;
  local_40[3] = 2;
  local_40[0] = param_1 + 0x7768;
  local_40[2] = 2;
  *(int *)(iVar13 + 0x1e0) = param_1 + 0x7678;
  *(int *)(iVar13 + 0x1e4) = param_1 + 0x76c8;
  *(int *)(iVar13 + 0x1e8) = param_1 + 0x7718;
  *(uint *)(iVar13 + 8) = 0x40000000 / param_2;
  local_40[1] = 8;
  ps_hybrid_filter_bank_allocation(iVar13 + 0x1fc,3,local_40 + 1,local_40);
  *(int *)(iVar13 + 0x1f0) = local_40[0] + 0x28;
  *(int *)(iVar13 + 500) = local_40[0] + 0x50;
  *(int *)(iVar13 + 0x1f8) = local_40[0] + 0x78;
  iVar2 = param_1 + 0x8cc0;
  iVar12 = param_1 + 0x8dc0;
  *(undefined4 *)(iVar13 + 400) = 0;
  puVar5 = (undefined4 *)(iVar13 + 0x6cc);
  *(int *)(iVar13 + 0x1ec) = local_40[0];
  piVar10 = (int *)(local_40[0] + 0xa0);
  iVar7 = 0;
  while( true ) {
    for (; iVar7 < 0xc; iVar7 = iVar7 + 1) {
      *puVar5 = 0xe;
      puVar5 = puVar5 + 1;
    }
    *puVar5 = 1;
    iVar7 = iVar7 + 1;
    if (iVar7 == 0x29) break;
    puVar5 = puVar5 + 1;
  }
  *(int *)(iVar13 + 0x1dc) = local_40[0] + 200;
  *(int *)(iVar13 + 0x1d0) = param_1 + 0x8fc0;
  *(int *)(iVar13 + 0x1d4) = param_1 + 0x92c0;
  piVar8 = (int *)(param_1 + 0x8fc0);
  *(int **)(iVar13 + 0x1d8) = piVar10;
  local_40[0] = local_40[0] + 0xf0;
  iVar7 = 0;
  while( true ) {
    while( true ) {
      for (; iVar7 < 0x14; iVar7 = iVar7 + 1) {
        *piVar8 = iVar2;
        piVar8[0xc0] = iVar12;
        piVar8 = piVar8 + 1;
        iVar12 = iVar12 + 8;
        iVar2 = iVar2 + 8;
      }
      *piVar8 = local_40[0];
      if (0x1f < iVar7) break;
      piVar8[0xc0] = local_40[0] + 0x38;
      iVar7 = iVar7 + 1;
      piVar8 = piVar8 + 1;
      local_40[0] = local_40[0] + 0x70;
    }
    piVar8[0xc0] = local_40[0] + 4;
    iVar7 = iVar7 + 1;
    if (iVar7 == 0x3d) break;
    piVar8 = piVar8 + 1;
    local_40[0] = local_40[0] + 8;
  }
  iVar7 = local_40[0] + 8;
  do {
    *piVar10 = iVar7;
    piVar10[10] = iVar7 + 8;
    iVar7 = iVar7 + 0x10;
    piVar10 = piVar10 + 1;
  } while (iVar7 != local_40[0] + 0xa8);
  piVar10 = &aRevLinkDelaySer;
  puVar5 = (undefined4 *)(iVar13 + 0x194);
  iVar7 = param_1 + 0x88a0;
  iVar2 = param_1 + 0x80c0;
  do {
    *puVar5 = 0;
    iVar14 = *piVar10;
    puVar5[3] = iVar2;
    puVar5[9] = iVar7;
    iVar3 = iVar14 * 4;
    iVar11 = iVar2 + iVar3;
    iVar1 = iVar7 + iVar3;
    puVar5[6] = iVar11;
    puVar5[0xc] = iVar1;
    iVar15 = iVar11 + iVar3;
    iVar12 = iVar1 + iVar3;
    if (0 < iVar14) {
      iVar9 = 0;
      iVar4 = iVar12;
      iVar6 = iVar15;
      do {
        *(int *)(iVar2 + iVar9) = iVar6;
        *(int *)(iVar11 + iVar9) = iVar6 + 0x50;
        *(int *)(iVar7 + iVar9) = iVar4;
        *(int *)(iVar1 + iVar9) = iVar4 + 0x28;
        iVar9 = iVar9 + 4;
        iVar6 = iVar6 + 0xa0;
        iVar4 = iVar4 + 0x50;
      } while (iVar3 != iVar9);
      iVar12 = iVar14 * 0x50 + iVar12;
      iVar15 = iVar15 + iVar14 * 0xa0;
    }
    puVar5 = puVar5 + 1;
    piVar10 = piVar10 + 1;
    iVar7 = iVar12;
    iVar2 = iVar15;
  } while ((undefined4 *)(iVar13 + 0x1a0) != puVar5);
  puVar5 = (undefined4 *)(iVar13 + 0x200);
  do {
    *puVar5 = 0x40000000;
    puVar5[0x16] = 0x40000000;
    puVar5 = puVar5 + 1;
  } while (puVar5 != (undefined4 *)(iVar13 + 600));
  return;
}
