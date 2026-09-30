/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: intensity_right @ ram:420596c8
 * Types and parameter counts are inferred; verify against disassembly. */

void intensity_right(uint param_1,int param_2,int param_3,int param_4,int param_5,uint param_6,
                    uint param_7,int *param_8,int *param_9,int *param_10,int *param_11)

{
  int iVar1;
  int iVar2;
  int *piVar3;
  int *piVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int *piVar9;

  gp = &__global_pointer_;
  if (0 < param_4) {
    iVar8 = (int)*(short *)((int)&intensity_factor + (param_1 & 3) * 2) *
            ((param_6 & 1 ^ param_7) * 2 + -1);
    iVar1 = param_5 >> 1;
    iVar2 = iVar8 * 0x10000;
    do {
      iVar5 = *param_10;
      piVar9 = param_10 + 2;
      *param_9 = *param_8 + ((int)param_1 >> 2);
      iVar6 = param_10[1];
      if (iVar8 == 0x7fff) {
        piVar3 = param_11;
        piVar4 = piVar9;
        iVar7 = iVar1;
        if (0 < iVar1) {
          do {
            *piVar3 = iVar5;
            piVar3[1] = iVar6;
            iVar5 = *piVar4;
            iVar7 = iVar7 + -1;
            iVar6 = piVar4[1];
            piVar3 = piVar3 + 2;
            piVar4 = piVar4 + 2;
          } while (iVar7 != 0);
          goto LAB_ram_4205976a;
        }
      }
      else {
        piVar3 = param_11;
        piVar4 = piVar9;
        iVar7 = iVar1;
        if (0 < iVar1) {
          do {
            iVar7 = iVar7 + -1;
            *piVar3 = (int)((ulonglong)((longlong)iVar5 * (longlong)iVar2) >> 0x20) << 1;
            piVar3[1] = (int)((ulonglong)((longlong)iVar6 * (longlong)iVar2) >> 0x20) << 1;
            iVar5 = *piVar4;
            iVar6 = piVar4[1];
            piVar3 = piVar3 + 2;
            piVar4 = piVar4 + 2;
          } while (iVar7 != 0);
LAB_ram_4205976a:
          piVar9 = piVar9 + iVar1 * 2;
          param_11 = param_11 + iVar1 * 2;
        }
      }
      param_4 = param_4 + -1;
      param_11 = param_11 + (param_2 - param_5);
      param_10 = piVar9 + (param_2 - param_5) + -2;
      param_9 = param_9 + param_3;
      param_8 = param_8 + param_3;
    } while (param_4 != 0);
  }
  return;
}
