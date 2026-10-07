/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: two_ch_filtering @ ram:4300c890
 * Types and parameter counts are inferred; verify against disassembly. */

void two_ch_filtering(int param_1,int param_2,int *param_3,int *param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;

  gp = &__global_pointer_;
  iVar7 = *(int *)(param_2 + 0x2c);
  iVar2 = *(int *)(param_2 + 0x24);
  iVar1 = *(int *)(param_2 + 0xc);
  iVar6 = *(int *)(param_2 + 4);
  iVar3 = *(int *)(param_2 + 0x1c);
  iVar8 = *(int *)(param_2 + 0x14);
  iVar5 = *(int *)(param_1 + 0x18) >> 1;
  iVar4 = ((int)((ulonglong)
                 ((longlong)(*(int *)(param_1 + 4) + *(int *)(param_1 + 0x2c)) * 0x4dcd920) >> 0x20)
          - (int)((ulonglong)
                  ((longlong)(*(int *)(param_1 + 0xc) + *(int *)(param_1 + 0x24)) * 0x12aba1c0) >>
                 0x20)) +
          (int)((ulonglong)
                ((longlong)(*(int *)(param_1 + 0x14) + *(int *)(param_1 + 0x1c)) * 0x4e53cf00) >>
               0x20);
  *param_3 = iVar5 + iVar4;
  param_3[1] = iVar5 - iVar4;
  iVar4 = *(int *)(param_2 + 0x18) >> 1;
  iVar1 = ((int)((ulonglong)((longlong)(iVar6 + iVar7) * 0x4dcd920) >> 0x20) -
          (int)((ulonglong)((longlong)(iVar1 + iVar2) * 0x12aba1c0) >> 0x20)) +
          (int)((ulonglong)((longlong)(iVar8 + iVar3) * 0x4e53cf00) >> 0x20);
  *param_4 = iVar1 + iVar4;
  param_4[1] = iVar4 - iVar1;
  return;
}
