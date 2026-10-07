/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: ps_all_pass_fract_delay_filter_type_I @ ram:4300be8e
 * Types and parameter counts are inferred; verify against disassembly. */

void ps_all_pass_fract_delay_filter_type_I
               (int *param_1,int param_2,uint *param_3,int *param_4,int *param_5,int *param_6,
               int *param_7)

{
  int iVar1;
  int iVar2;
  int *piVar3;
  int *piVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;

  gp = &__global_pointer_;
  param_2 = param_2 * 4;
  piVar3 = (int *)(*(int *)(*param_4 + *param_1 * 4) + param_2);
  piVar4 = (int *)(*(int *)(*param_1 * 4 + *param_5) + param_2);
  iVar2 = *piVar4;
  iVar10 = *param_3 << 0x10;
  iVar9 = *piVar3 << 1;
  uVar5 = *param_3 & 0xffff0000;
  iVar8 = param_5[1];
  iVar1 = param_4[2];
  iVar7 = param_4[1];
  iVar11 = param_5[2];
  iVar6 = (int)((ulonglong)((longlong)(iVar2 * 2) * (longlong)(int)uVar5) >> 0x20) +
          (int)((ulonglong)((longlong)iVar9 * (longlong)iVar10) >> 0x20) +
          (int)((ulonglong)((longlong)(*param_7 * -2) * 0x53620000) >> 0x20);
  *piVar4 = (int)((ulonglong)((longlong)(iVar6 * 2) * 0x53620000) >> 0x20) + *param_7;
  *param_7 = iVar6;
  iVar2 = (int)((ulonglong)((longlong)iVar9 * (longlong)(int)uVar5) >> 0x20) +
          (int)((ulonglong)((longlong)(iVar2 * -2) * (longlong)iVar10) >> 0x20) +
          (int)((ulonglong)((longlong)(*param_6 * -2) * 0x53620000) >> 0x20);
  *piVar3 = *param_6 + (int)((ulonglong)((longlong)(iVar2 * 2) * 0x53620000) >> 0x20);
  *param_6 = iVar2;
  iVar2 = param_3[1] << 0x10;
  piVar4 = (int *)(*(int *)(iVar7 + param_1[1] * 4) + param_2);
  piVar3 = (int *)(*(int *)(iVar8 + param_1[1] * 4) + param_2);
  iVar8 = *piVar3;
  uVar5 = param_3[1] & 0xffff0000;
  iVar6 = *piVar4 << 1;
  iVar7 = (int)((ulonglong)((longlong)(iVar8 * 2) * (longlong)(int)uVar5) >> 0x20) +
          (int)((ulonglong)((longlong)iVar6 * (longlong)iVar2) >> 0x20) +
          (int)((ulonglong)((longlong)(*param_7 * -2) * 0x48490000) >> 0x20);
  *piVar3 = (int)((ulonglong)((longlong)(iVar7 * 2) * 0x48490000) >> 0x20) + *param_7;
  *param_7 = iVar7;
  iVar2 = (int)((ulonglong)((longlong)(*param_6 * -2) * 0x48490000) >> 0x20) +
          (int)((ulonglong)((longlong)iVar6 * (longlong)(int)uVar5) >> 0x20) +
          (int)((ulonglong)((longlong)(iVar8 * -2) * (longlong)iVar2) >> 0x20);
  *piVar4 = *param_6 + (int)((ulonglong)((longlong)(iVar2 * 2) * 0x48490000) >> 0x20);
  *param_6 = iVar2;
  uVar5 = param_3[2] & 0xffff0000;
  iVar2 = param_3[2] << 0x10;
  piVar3 = (int *)(*(int *)(iVar1 + param_1[2] * 4) + param_2);
  piVar4 = (int *)(param_2 + *(int *)(iVar11 + param_1[2] * 4));
  iVar1 = *piVar4;
  iVar7 = *piVar3 << 1;
  iVar6 = (int)((ulonglong)((longlong)(iVar1 * 2) * (longlong)(int)uVar5) >> 0x20) +
          (int)((ulonglong)((longlong)iVar7 * (longlong)iVar2) >> 0x20) +
          (int)((ulonglong)((longlong)-*param_7 * 0x7d530000) >> 0x20);
  *piVar4 = *param_7 + (int)((ulonglong)((longlong)iVar6 * 0x7d530000) >> 0x20);
  *param_7 = iVar6 * 4;
  iVar1 = (int)((ulonglong)((longlong)iVar7 * (longlong)(int)uVar5) >> 0x20) +
          (int)((ulonglong)((longlong)(iVar1 * -2) * (longlong)iVar2) >> 0x20) +
          (int)((ulonglong)((longlong)-*param_6 * 0x7d530000) >> 0x20);
  *piVar3 = *param_6 + (int)((ulonglong)((longlong)iVar1 * 0x7d530000) >> 0x20);
  *param_6 = iVar1 * 4;
  return;
}
