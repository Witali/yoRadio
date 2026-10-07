/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: deinterleave @ ram:4205bd88
 * Types and parameter counts are inferred; verify against disassembly. */

void deinterleave(void *param_1,int param_2,int param_3)

{
  int iVar1;
  int *piVar2;
  size_t n;
  int iVar3;
  int iVar4;
  void *pvVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  void *bb;

  gp = &__global_pointer_;
  iVar4 = *(int *)(param_3 + 0x294);
  iVar8 = param_3;
  if (0 < iVar4) {
    do {
      iVar6 = *(int *)(iVar8 + 0x30);
      bb = param_1;
      if (0 < iVar6) {
        piVar2 = *(int **)(param_3 + 0x90);
        iVar7 = 0;
        do {
          iVar1 = *(int *)(iVar8 + 0x298);
          iVar3 = *piVar2;
          if (0 < iVar1) {
            n = iVar3 << 1;
            pvVar5 = (void *)(iVar7 * 2 + param_2);
            do {
              pvVar5 = memcpy(pvVar5,bb,n);
              iVar3 = *piVar2;
              iVar1 = iVar1 + -1;
              pvVar5 = (void *)((int)pvVar5 + 0x100);
              n = iVar3 * 2;
              bb = (void *)((int)bb + n);
            } while (iVar1 != 0);
          }
          iVar6 = iVar6 + -1;
          piVar2 = piVar2 + 1;
          iVar7 = iVar7 + iVar3;
        } while (iVar6 != 0);
        param_2 = (int)bb + (param_2 - (int)param_1);
      }
      iVar8 = iVar8 + 4;
      param_1 = bb;
    } while (iVar8 != iVar4 * 4 + param_3);
  }
  return;
}
