/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: ps_hybrid_analysis @ ram:4300d48e
 * Types and parameter counts are inferred; verify against disassembly. */

void ps_hybrid_analysis(int param_1,int param_2,int param_3,int param_4,aac_hybrid_abi_t *hybrid,
                       int param_6,int param_7)

{
  int iVar1;
  int iVar2;
  int32_t *piVar3;
  int32_t *piVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined4 *puVar8;
  undefined4 *puVar9;

  gp = &__global_pointer_;
  if (hybrid->bands < 1) {
    return;
  }
  iVar1 = (param_7 + 0x20) * 4 + param_6;
  puVar9 = (undefined4 *)(param_1 + 0x600);
  puVar8 = (undefined4 *)(param_2 + 0x600);
  iVar6 = 0;
  iVar7 = 0;
  do {
    while( true ) {
      piVar3 = hybrid->resolution;
      *(undefined4 *)(iVar1 + 0x30) = *puVar9;
      *(undefined4 *)(iVar1 + 0xe0) = *puVar8;
      iVar5 = param_3 + iVar6 * 4;
      iVar2 = iVar6 * 4 + param_4;
      if (piVar3[iVar7] != 2) break;
      two_ch_filtering(iVar1,iVar1 + 0xb0,iVar5,iVar2);
      iVar7 = iVar7 + 1;
      iVar6 = iVar6 + 2;
      iVar1 = iVar1 + 0x160;
      puVar9 = puVar9 + 1;
      puVar8 = puVar8 + 1;
      if (hybrid->bands <= iVar7) {
        gp = &__global_pointer_;
        return;
      }
    }
    if (piVar3[iVar7] == 8) {
      iVar6 = iVar6 + 6;
      eight_ch_filtering(iVar1,iVar1 + 0xb0,hybrid->real_scratch,hybrid->imag_scratch,param_6);
      memmove(iVar5,hybrid->real_scratch,0x10);
      piVar4 = hybrid->real_scratch;
      piVar3 = hybrid->imag_scratch;
      *(int *)(iVar5 + 8) = *(int *)(iVar5 + 8) + piVar4[5];
      *(int *)(iVar5 + 0xc) = *(int *)(iVar5 + 0xc) + piVar4[4];
      *(int32_t *)(iVar5 + 0x10) = piVar4[6];
      *(int32_t *)(iVar5 + 0x14) = piVar4[7];
      memmove(iVar2,piVar3,0x10);
      piVar3 = hybrid->imag_scratch;
      *(int *)(iVar2 + 8) = *(int *)(iVar2 + 8) + piVar3[5];
      *(int *)(iVar2 + 0xc) = *(int *)(iVar2 + 0xc) + piVar3[4];
      *(int32_t *)(iVar2 + 0x10) = piVar3[6];
      *(int32_t *)(iVar2 + 0x14) = piVar3[7];
    }
    iVar7 = iVar7 + 1;
    iVar1 = iVar1 + 0x160;
    puVar9 = puVar9 + 1;
    puVar8 = puVar8 + 1;
  } while (iVar7 < hybrid->bands);
  return;
}
