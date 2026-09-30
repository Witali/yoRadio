/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: synthesis_sub_band_down_sampled @ ram:420499a0
 * Types and parameter counts are inferred; verify against disassembly. */

void synthesis_sub_band_down_sampled(int *param_1,int *param_2,int *param_3)

{
  int *piVar1;
  int iVar2;
  int *piVar3;
  int *piVar4;
  int iVar5;
  uint uVar6;
  uint *puVar7;
  int *piVar8;
  int iVar9;

  gp = &__global_pointer_;
  puVar7 = &exp_m0_25_phi;
  piVar1 = param_2;
  piVar3 = param_1;
  piVar8 = param_3 + 0x1f;
  do {
    iVar2 = *piVar3;
    iVar9 = *piVar1;
    uVar6 = *puVar7 & 0xffff0000;
    iVar5 = *puVar7 << 0x10;
    puVar7 = puVar7 + 1;
    piVar1 = piVar1 + 1;
    *piVar3 = (int)((ulonglong)((longlong)-iVar2 * (longlong)(int)uVar6) >> 0x20) +
              (int)((ulonglong)((longlong)iVar9 * (longlong)iVar5) >> 0x20);
    *piVar8 = (int)((ulonglong)((longlong)(int)uVar6 * (longlong)iVar9) >> 0x20) +
              (int)((ulonglong)((longlong)iVar2 * (longlong)iVar5) >> 0x20);
    piVar3 = piVar3 + 1;
    piVar8 = piVar8 + -1;
  } while (puVar7 != &CosTable_64);
  mdct_32(param_1);
  mdct_32(param_3);
  piVar1 = param_3;
  piVar3 = param_2;
  do {
    iVar2 = *piVar1;
    piVar1 = piVar1 + 1;
    *piVar3 = iVar2;
    piVar3 = piVar3 + 1;
  } while (param_3 + 0x20 != piVar1);
  piVar1 = param_1;
  piVar3 = param_3;
  piVar8 = param_2;
  do {
    iVar5 = piVar1[1];
    iVar2 = piVar8[1];
    *(short *)piVar3 = (short)(*piVar1 + *piVar8 >> 0xe);
    piVar4 = piVar3 + 1;
    *(short *)((int)piVar3 + 2) = (short)(iVar5 - iVar2 >> 0xe);
    piVar1 = piVar1 + 2;
    piVar8 = piVar8 + 2;
    piVar3 = piVar4;
  } while (piVar4 != param_3 + 0x10);
  param_1 = param_1 + 0x1e;
  param_2 = param_2 + 0x1e;
  piVar1 = param_3 + 0x10;
  do {
    iVar5 = *param_2;
    iVar2 = *param_1;
    *(short *)piVar1 = (short)(-(param_1[1] + param_2[1]) >> 0xe);
    piVar3 = piVar1 + 1;
    *(short *)((int)piVar1 + 2) = (short)(iVar5 - iVar2 >> 0xe);
    param_2 = param_2 + -2;
    param_1 = param_1 + -2;
    piVar1 = piVar3;
  } while (piVar3 != param_3 + 0x20);
  return;
}
