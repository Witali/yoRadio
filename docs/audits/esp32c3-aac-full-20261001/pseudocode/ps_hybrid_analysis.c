/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: ps_hybrid_analysis @ ram:4300d48e
 * Types and parameter counts are inferred; verify against disassembly. */

void ps_hybrid_analysis(int param_1,int param_2,int param_3,int param_4,int *param_5,int param_6,
                       int param_7)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined4 *puVar8;
  undefined4 *puVar9;

  gp = &__global_pointer_;
  if (*param_5 < 1) {
    return;
  }
  iVar1 = (param_7 + 0x20) * 4 + param_6;
  puVar9 = (undefined4 *)(param_1 + 0x600);
  puVar8 = (undefined4 *)(param_2 + 0x600);
  iVar6 = 0;
  iVar7 = 0;
  do {
    while( true ) {
      iVar2 = param_5[1];
      *(undefined4 *)(iVar1 + 0x30) = *puVar9;
      *(undefined4 *)(iVar1 + 0xe0) = *puVar8;
      iVar4 = *(int *)(iVar2 + iVar7 * 4);
      iVar5 = param_3 + iVar6 * 4;
      iVar2 = iVar6 * 4 + param_4;
      if (iVar4 != 2) break;
      two_ch_filtering(iVar1,iVar1 + 0xb0,iVar5,iVar2);
      iVar7 = iVar7 + 1;
      iVar6 = iVar6 + 2;
      iVar1 = iVar1 + 0x160;
      puVar9 = puVar9 + 1;
      puVar8 = puVar8 + 1;
      if (*param_5 <= iVar7) {
        gp = &__global_pointer_;
        return;
      }
    }
    if (iVar4 == 8) {
      iVar6 = iVar6 + 6;
      eight_ch_filtering(iVar1,iVar1 + 0xb0,param_5[5],param_5[6],param_6);
      memmove(iVar5,param_5[5],0x10);
      iVar3 = param_5[5];
      iVar4 = param_5[6];
      *(int *)(iVar5 + 8) = *(int *)(iVar5 + 8) + *(int *)(iVar3 + 0x14);
      *(int *)(iVar5 + 0xc) = *(int *)(iVar5 + 0xc) + *(int *)(iVar3 + 0x10);
      *(undefined4 *)(iVar5 + 0x10) = *(undefined4 *)(iVar3 + 0x18);
      *(undefined4 *)(iVar5 + 0x14) = *(undefined4 *)(iVar3 + 0x1c);
      memmove(iVar2,iVar4,0x10);
      iVar4 = param_5[6];
      *(int *)(iVar2 + 8) = *(int *)(iVar2 + 8) + *(int *)(iVar4 + 0x14);
      *(int *)(iVar2 + 0xc) = *(int *)(iVar2 + 0xc) + *(int *)(iVar4 + 0x10);
      *(undefined4 *)(iVar2 + 0x10) = *(undefined4 *)(iVar4 + 0x18);
      *(undefined4 *)(iVar2 + 0x14) = *(undefined4 *)(iVar4 + 0x1c);
    }
    iVar7 = iVar7 + 1;
    iVar1 = iVar1 + 0x160;
    puVar9 = puVar9 + 1;
    puVar8 = puVar8 + 1;
  } while (iVar7 < *param_5);
  return;
}
