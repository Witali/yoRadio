/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: ms_synt @ ram:4300b962
 * Types and parameter counts are inferred; verify against disassembly. */

void ms_synt(int param_1,int param_2,int param_3,uint param_4,int *param_5,int *param_6,int *param_7
            ,int *param_8)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  int iVar5;
  int *piVar6;
  int iVar7;
  int iVar8;

  gp = &__global_pointer_;
  if (0x400 < param_4) {
    return;
  }
  if (0 < param_1) {
    do {
      iVar5 = *param_8;
      iVar3 = *param_7;
      if (iVar5 < 0x1f) {
        iVar7 = iVar3 - iVar5;
        iVar2 = *param_5;
        iVar8 = *param_6;
        if (iVar7 < 1) {
          *param_7 = iVar3 + -1;
          *param_8 = iVar3 + -1;
          if (param_4 != 0) {
            iVar8 = iVar8 >> (1U - iVar7 & 0x1f);
            piVar6 = param_5 + param_4;
            piVar4 = param_6;
            do {
              *param_5 = (iVar2 >> 1) + iVar8;
              *piVar4 = (iVar2 >> 1) - iVar8;
              iVar2 = param_5[1];
              param_5 = param_5 + 1;
              iVar8 = piVar4[1] >> (1U - iVar7 & 0x1f);
              piVar4 = piVar4 + 1;
            } while (param_5 != piVar6);
            goto LAB_ram_4300b9fa;
          }
        }
        else {
          *param_8 = iVar5 + -1;
          *param_7 = iVar5 + -1;
          if (param_4 != 0) {
            iVar2 = iVar2 >> (iVar7 + 1U & 0x1f);
            piVar6 = param_5 + param_4;
            piVar4 = param_6;
            do {
              *param_5 = iVar2 + (iVar8 >> 1);
              *piVar4 = iVar2 - (iVar8 >> 1);
              iVar8 = piVar4[1];
              piVar1 = param_5 + 1;
              param_5 = param_5 + 1;
              iVar2 = *piVar1 >> (iVar7 + 1U & 0x1f);
              piVar4 = piVar4 + 1;
            } while (param_5 != piVar6);
LAB_ram_4300b9fa:
            param_6 = param_6 + param_4;
          }
        }
      }
      else {
        *param_8 = iVar3;
        iVar3 = memcpy(param_6,param_5,param_4 * 4);
        param_6 = (int *)(iVar3 + param_4 * 4);
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
