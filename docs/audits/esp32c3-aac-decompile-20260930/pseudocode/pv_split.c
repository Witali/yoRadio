/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: pv_split @ ram:42056ac8
 * Types and parameter counts are inferred; verify against disassembly. */

void pv_split(int *param_1)

{
  int *piVar1;
  int *piVar2;
  int *piVar3;
  int *piVar4;
  int iVar5;
  int iVar6;

  gp = &__global_pointer_;
  piVar1 = param_1;
  piVar3 = (int *)(CosTable_48 + 0xbc);
  piVar4 = param_1 + -1;
  do {
    iVar6 = *piVar3;
    iVar5 = *piVar4 - *piVar1;
    *piVar4 = *piVar1 + *piVar4;
    piVar2 = piVar1 + 2;
    *piVar1 = ((uint)(iVar5 * iVar6) >> 0x1a) +
              (int)((ulonglong)((longlong)iVar5 * (longlong)iVar6) >> 0x20) * 0x40;
    iVar6 = piVar3[-1];
    iVar5 = piVar4[-1] - piVar1[1];
    piVar4[-1] = piVar4[-1] + piVar1[1];
    piVar1[1] = ((uint)(iVar5 * iVar6) >> 0x1a) +
                (int)((ulonglong)((longlong)iVar5 * (longlong)iVar6) >> 0x20) * 0x40;
    piVar1 = piVar2;
    piVar3 = piVar3 + -2;
    piVar4 = piVar4 + -2;
  } while (piVar2 != param_1 + 0x10);
  return;
}
