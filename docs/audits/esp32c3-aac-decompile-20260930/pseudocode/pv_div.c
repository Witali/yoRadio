/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: pv_div @ ram:4204838c
 * Types and parameter counts are inferred; verify against disassembly. */

void pv_div(int param_1,int param_2,int *param_3)

{
  bool bVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  int iVar5;

  gp = &__global_pointer_;
  param_3[1] = 0;
  if (param_2 != 0) {
    bVar1 = param_2 < 0;
    if (bVar1) {
      param_2 = -param_2;
    }
    if (param_1 < 0) {
      param_1 = -param_1;
      bVar1 = !bVar1;
    }
    else if (param_1 == 0) goto LAB_ram_42048392;
    uVar2 = pv_normalize(param_1);
    uVar3 = pv_normalize(param_2);
    param_2 = param_2 << (uVar3 & 0x1f);
    iVar5 = 0x40000000 / (param_2 >> 0xf);
    param_3[1] = uVar2 - uVar3;
    iVar4 = 0x7fffffff -
            (((uint)(param_2 * iVar5) >> 0xf) +
            (int)((ulonglong)((longlong)param_2 * (longlong)iVar5) >> 0x20) * 0x20000);
    iVar5 = (int)((ulonglong)
                  ((longlong)(param_1 << (uVar2 & 0x1f)) *
                  (longlong)
                  (int)(((uint)(iVar5 * iVar4) >> 0xe) +
                       (int)((ulonglong)((longlong)iVar5 * (longlong)iVar4) >> 0x20) * 0x40000)) >>
                 0x20);
    iVar4 = iVar5 * 2;
    if (bVar1) {
      iVar4 = iVar5 * -2;
    }
    *param_3 = iVar4;
    return;
  }
LAB_ram_42048392:
  *param_3 = 0;
  return;
}
