/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: pv_sqrt @ ram:420486da
 * Types and parameter counts are inferred; verify against disassembly. */

void pv_sqrt(int param_1,uint param_2,int *param_3,int *param_4)

{
  int *piVar1;
  int *piVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  undefined1 *puVar6;

  gp = &__global_pointer_;
  if ((*param_4 == param_1) && (param_4[1] == param_2)) {
    iVar5 = param_4[2];
    *param_3 = iVar5;
    param_3[1] = (int)(short)param_4[3];
    param_4[2] = iVar5;
    param_4[3] = param_3[1];
    return;
  }
  *param_4 = param_1;
  param_4[1] = param_2;
  if (param_1 < 1) {
    param_3[1] = 0;
    *param_3 = 0;
    param_4[2] = 0;
    param_4[3] = param_3[1];
    return;
  }
  if (param_1 < 0x10000000) {
    for (; iVar5 = param_1, uVar3 = param_2, param_1 < 0x8000000; param_1 = param_1 << 2) {
      iVar5 = param_1 << 1;
      uVar3 = param_2 - 1;
      if (0x7ffffff < iVar5) break;
      param_2 = param_2 - 2;
    }
  }
  else if (param_1 >> 1 < 0x10000001) {
    iVar5 = param_1 >> 1;
    uVar3 = param_2 + 1;
  }
  else if (param_1 >> 2 < 0x10000001) {
    iVar5 = param_1 >> 2;
    uVar3 = param_2 + 2;
  }
  else {
    iVar5 = param_1 >> 3;
    uVar3 = param_2 + 3;
  }
  puVar6 = sqrt_table;
  iVar4 = (int)((ulonglong)((longlong)iVar5 * -0x2367758) >> 0x20) * 0x10 +
          ((uint)(iVar5 * -0x2367758) >> 0x1c);
  do {
    piVar1 = (int *)(puVar6 + 4);
    piVar2 = (int *)(puVar6 + 8);
    puVar6 = puVar6 + 8;
    iVar4 = ((uint)((iVar4 + *piVar1) * iVar5) >> 0x1c) +
            (int)((ulonglong)((longlong)(iVar4 + *piVar1) * (longlong)iVar5) >> 0x20) * 0x10 +
            *piVar2;
    iVar4 = ((uint)(iVar4 * iVar5) >> 0x1c) +
            (int)((ulonglong)((longlong)iVar4 * (longlong)iVar5) >> 0x20) * 0x10;
  } while (puVar6 != (undefined1 *)0x3c12a2b0);
  iVar5 = ((uint)((iVar4 + 0x1dc9e260) * iVar5) >> 0x1c) +
          (int)((ulonglong)((longlong)(iVar4 + 0x1dc9e260) * (longlong)iVar5) >> 0x20) * 0x10 +
          0x2a5826c;
  if ((int)uVar3 < 0) {
    if ((uVar3 & 1) != 0) {
      iVar5 = (int)((ulonglong)((longlong)iVar5 * 0xb504f30) >> 0x20) * 0x10 +
              ((uint)(iVar5 * 0xb504f30) >> 0x1c);
    }
    iVar4 = -0x1d - ((int)-uVar3 >> 1);
  }
  else {
    iVar4 = ((int)uVar3 >> 1) + -0x1d;
    if ((uVar3 & 1) != 0) {
      iVar4 = ((int)uVar3 >> 1) + -0x1c;
      iVar5 = (int)((ulonglong)((longlong)iVar5 * 0x16a09e60) >> 0x20) * 8 +
              ((uint)(iVar5 * 0x16a09e60) >> 0x1d);
    }
  }
  param_3[1] = iVar4;
  *param_3 = iVar5;
  param_4[2] = iVar5;
  param_4[3] = param_3[1];
  return;
}
