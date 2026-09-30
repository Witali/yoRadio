/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: ms_synt @ ram:4204671c
 * Types and parameter counts are inferred; verify against disassembly. */

void ms_synt(int param_1,int param_2,int param_3,uint param_4,int *param_5,int *param_6,int *param_7
            ,int *param_8)

{
  int *piVar1;
  int iVar2;
  void *pvVar3;
  int iVar4;
  int *piVar5;
  int iVar6;
  int *piVar7;
  int iVar8;
  int iVar9;

  gp = &__global_pointer_;
  if (0x400 < param_4) {
    return;
  }
  if (0 < param_1) {
    do {
      iVar6 = *param_8;
      iVar4 = *param_7;
      if (iVar6 < 0x1f) {
        iVar8 = iVar4 - iVar6;
        iVar2 = *param_5;
        iVar9 = *param_6;
        if (iVar8 < 1) {
          *param_7 = iVar4 + -1;
          *param_8 = iVar4 + -1;
          if (param_4 != 0) {
            iVar9 = iVar9 >> (1U - iVar8 & 0x1f);
            piVar7 = param_5 + param_4;
            piVar5 = param_6;
            do {
              *param_5 = (iVar2 >> 1) + iVar9;
              *piVar5 = (iVar2 >> 1) - iVar9;
              iVar2 = param_5[1];
              param_5 = param_5 + 1;
              iVar9 = piVar5[1] >> (1U - iVar8 & 0x1f);
              piVar5 = piVar5 + 1;
            } while (param_5 != piVar7);
            goto LAB_ram_420467b4;
          }
        }
        else {
          *param_8 = iVar6 + -1;
          *param_7 = iVar6 + -1;
          if (param_4 != 0) {
            iVar2 = iVar2 >> (iVar8 + 1U & 0x1f);
            piVar7 = param_5 + param_4;
            piVar5 = param_6;
            do {
              *param_5 = iVar2 + (iVar9 >> 1);
              *piVar5 = iVar2 - (iVar9 >> 1);
              iVar9 = piVar5[1];
              piVar1 = param_5 + 1;
              param_5 = param_5 + 1;
              iVar2 = *piVar1 >> (iVar8 + 1U & 0x1f);
              piVar5 = piVar5 + 1;
            } while (param_5 != piVar7);
LAB_ram_420467b4:
            param_6 = param_6 + param_4;
          }
        }
      }
      else {
        *param_8 = iVar4;
        pvVar3 = memcpy(param_6,param_5,param_4 * 4);
        param_6 = (int *)((int)pvVar3 + param_4 * 4);
        param_5 = param_5 + param_4;
      }
      param_1 = param_1 + -1;
      param_5 = param_5 + (param_2 - param_4);
      param_6 = param_6 + (param_2 - param_4);
      param_8 = param_8 + param_3;
      param_7 = param_7 + param_3;
    } while (param_1 != 0);
  }
  return;
}
