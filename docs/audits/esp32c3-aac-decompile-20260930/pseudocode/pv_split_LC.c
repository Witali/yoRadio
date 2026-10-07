/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: pv_split_LC @ ram:42056a7a
 * Types and parameter counts are inferred; verify against disassembly. */

void pv_split_LC(int *param_1,int *param_2)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  int *piVar4;
  int iVar5;

  gp = &__global_pointer_;
  iVar3 = *param_1;
  iVar5 = param_1[0x1f];
  piVar2 = (int *)(CosTable_48 + 0x80);
  piVar4 = param_1 + 0x1e;
  do {
    iVar1 = *piVar2;
    *param_1 = iVar3 + iVar5;
    piVar2 = piVar2 + 1;
    *param_2 = ((uint)((iVar3 - iVar5) * iVar1) >> 0x1a) +
               (int)((ulonglong)((longlong)(iVar3 - iVar5) * (longlong)iVar1) >> 0x20) * 0x40;
    iVar3 = param_1[1];
    iVar5 = *piVar4;
    param_1 = param_1 + 1;
    param_2 = param_2 + 1;
    piVar4 = piVar4 + -1;
  } while (piVar2 != (int *)&digit_reverse_swap_256);
  return;
}
