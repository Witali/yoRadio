/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: ps_all_pass_fract_delay_filter_type_II @ ram:42059cb4
 * Types and parameter counts are inferred; verify against disassembly. */

void ps_all_pass_fract_delay_filter_type_II
               (int *param_1,int param_2,uint *param_3,int *param_4,int *param_5,int *param_6,
               int *param_7,int param_8)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  int *piVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  int iVar10;
  int iVar11;
  int iVar12;

  gp = &__global_pointer_;
  param_2 = param_2 * 4;
  piVar4 = (int *)(*(int *)(*param_4 + *param_1 * 4) + param_2);
  piVar5 = (int *)(*(int *)(*param_1 * 4 + *param_5) + param_2);
  iVar3 = *piVar5;
  iVar1 = *param_3 << 0x10;
  iVar11 = *piVar4 << 1;
  uVar9 = *param_3 & 0xffff0000;
  param_8 = param_8 * 6;
  iVar7 = param_4[1];
  iVar8 = param_5[1];
  iVar2 = param_4[2];
  iVar6 = (int)*(short *)(aRevLinkDecaySerCoeff + param_8) << 0x10;
  iVar12 = (int)*(short *)(aRevLinkDecaySerCoeff + param_8 + 2) << 0x10;
  iVar10 = (int)((ulonglong)((longlong)(iVar3 * 2) * (longlong)(int)uVar9) >> 0x20) +
           (int)((ulonglong)((longlong)iVar11 * (longlong)iVar1) >> 0x20) +
           (int)((ulonglong)((longlong)(*param_7 * -2) * (longlong)iVar6) >> 0x20);
  *piVar5 = (int)((ulonglong)((longlong)(iVar10 * 2) * (longlong)iVar6) >> 0x20) + *param_7;
  *param_7 = iVar10;
  iVar1 = (int)((ulonglong)((longlong)iVar11 * (longlong)(int)uVar9) >> 0x20) +
          (int)((ulonglong)((longlong)(iVar3 * -2) * (longlong)iVar1) >> 0x20) +
          (int)((ulonglong)((longlong)(*param_6 * -2) * (longlong)iVar6) >> 0x20);
  *piVar4 = *param_6 + (int)((ulonglong)((longlong)(iVar1 * 2) * (longlong)iVar6) >> 0x20);
  *param_6 = iVar1;
  iVar3 = param_3[1] << 0x10;
  piVar5 = (int *)(*(int *)(iVar7 + param_1[1] * 4) + param_2);
  piVar4 = (int *)(*(int *)(iVar8 + param_1[1] * 4) + param_2);
  iVar7 = *piVar4;
  uVar9 = param_3[1] & 0xffff0000;
  iVar1 = *piVar5 << 1;
  iVar6 = (int)((ulonglong)((longlong)(iVar7 * 2) * (longlong)(int)uVar9) >> 0x20) +
          (int)((ulonglong)((longlong)iVar1 * (longlong)iVar3) >> 0x20) +
          (int)((ulonglong)((longlong)(*param_7 * -2) * (longlong)iVar12) >> 0x20);
  *piVar4 = (int)((ulonglong)((longlong)(iVar6 * 2) * (longlong)iVar12) >> 0x20) + *param_7;
  *param_7 = iVar6;
  iVar6 = param_5[2];
  iVar1 = (int)((ulonglong)((longlong)(*param_6 * -2) * (longlong)iVar12) >> 0x20) +
          (int)((ulonglong)((longlong)iVar1 * (longlong)(int)uVar9) >> 0x20) +
          (int)((ulonglong)((longlong)(iVar7 * -2) * (longlong)iVar3) >> 0x20);
  *piVar5 = *param_6 + (int)((ulonglong)((longlong)(iVar1 * 2) * (longlong)iVar12) >> 0x20);
  *param_6 = iVar1;
  piVar5 = (int *)(*(int *)(iVar6 + param_1[2] * 4) + param_2);
  piVar4 = (int *)(*(int *)(iVar2 + param_1[2] * 4) + param_2);
  iVar3 = *piVar5;
  iVar2 = param_3[2] << 0x10;
  uVar9 = param_3[2] & 0xffff0000;
  iVar7 = *piVar4 << 1;
  iVar6 = (int)*(short *)(aRevLinkDecaySerCoeff + param_8 + 4) << 0x10;
  iVar1 = (int)((ulonglong)((longlong)(iVar3 * 2) * (longlong)(int)uVar9) >> 0x20) +
          (int)((ulonglong)((longlong)iVar7 * (longlong)iVar2) >> 0x20) +
          (int)((ulonglong)((longlong)-*param_7 * (longlong)iVar6) >> 0x20);
  *piVar5 = *param_7 + (int)((ulonglong)((longlong)iVar1 * (longlong)iVar6) >> 0x20);
  *param_7 = iVar1 * 4;
  iVar1 = (int)((ulonglong)((longlong)iVar7 * (longlong)(int)uVar9) >> 0x20) +
          (int)((ulonglong)((longlong)(iVar3 * -2) * (longlong)iVar2) >> 0x20) +
          (int)((ulonglong)((longlong)-*param_6 * (longlong)iVar6) >> 0x20);
  *piVar4 = *param_6 + (int)((ulonglong)((longlong)iVar1 * (longlong)iVar6) >> 0x20);
  *param_6 = iVar1 * 4;
  return;
}
