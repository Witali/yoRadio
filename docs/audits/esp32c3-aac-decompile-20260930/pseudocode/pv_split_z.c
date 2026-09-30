/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: pv_split_z @ ram:42056b2c
 * Types and parameter counts are inferred; verify against disassembly. */

void pv_split_z(int *param_1)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  int *piVar4;
  int *piVar5;
  int iVar6;

  gp = &__global_pointer_;
  piVar1 = param_1;
  piVar2 = (int *)(CosTable_48 + 0x80);
  piVar4 = param_1 + 0x1f;
  do {
    iVar6 = *piVar2;
    iVar3 = *piVar4 - *piVar1;
    *piVar1 = *piVar4 + *piVar1;
    piVar5 = piVar4 + -2;
    *piVar4 = ((uint)(iVar3 * iVar6) >> 0x1a) +
              (int)((ulonglong)((longlong)iVar3 * (longlong)iVar6) >> 0x20) * 0x40;
    iVar6 = piVar2[1];
    iVar3 = piVar4[-1] - piVar1[1];
    piVar1[1] = piVar1[1] + piVar4[-1];
    piVar4[-1] = ((uint)(iVar3 * iVar6) >> 0x1a) +
                 (int)((ulonglong)((longlong)iVar3 * (longlong)iVar6) >> 0x20) * 0x40;
    piVar1 = piVar1 + 2;
    piVar2 = piVar2 + 2;
    piVar4 = piVar5;
  } while (piVar5 != param_1 + 0xf);
  return;
}
