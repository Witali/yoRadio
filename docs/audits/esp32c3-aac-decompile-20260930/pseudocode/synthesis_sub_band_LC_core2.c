/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: synthesis_sub_band_LC_core2 @ ram:4204e6d2
 * Types and parameter counts are inferred; verify against disassembly. */

void synthesis_sub_band_LC_core2(int *param_1,int *param_2,int *param_3)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  int *piVar4;
  int iVar5;
  int *piVar6;
  int *piVar7;
  int iVar8;

  gp = &__global_pointer_;
  iVar5 = param_2[0x3f];
  piVar1 = param_1;
  piVar2 = param_2;
  piVar6 = param_3;
  piVar7 = param_2 + 0x3e;
  do {
    iVar3 = *piVar2;
    iVar8 = *piVar6;
    piVar4 = piVar2 + 1;
    *piVar2 = iVar3 + iVar5;
    piVar6 = piVar6 + 1;
    *piVar1 = (int)((ulonglong)((longlong)(iVar3 - iVar5) * (longlong)iVar8) >> 0x20) << 1;
    iVar5 = *piVar7;
    piVar1 = piVar1 + 1;
    piVar2 = piVar4;
    piVar7 = piVar7 + -1;
  } while (piVar4 != param_2 + 0x14);
  param_3 = param_3 + 0x14;
  piVar1 = param_2 + 0x2a;
  piVar2 = param_1 + 0x14;
  piVar6 = param_2 + 0x14;
  do {
    iVar8 = *param_3;
    piVar7 = piVar6 + 1;
    iVar3 = *piVar6 - iVar5;
    *piVar6 = *piVar6 + iVar5;
    param_3 = param_3 + 1;
    *piVar2 = ((uint)(iVar3 * iVar8) >> 0x1a) +
              (int)((ulonglong)((longlong)iVar3 * (longlong)iVar8) >> 0x20) * 0x40;
    iVar5 = *piVar1;
    piVar1 = piVar1 + -1;
    piVar2 = piVar2 + 1;
    piVar6 = piVar7;
  } while (piVar7 != param_2 + 0x20);
  return;
}
