/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: sbr_update_freq_scale @ ram:4202abe6
 * Types and parameter counts are inferred; verify against disassembly. */

void sbr_update_freq_scale
               (int param_1,uint *param_2,int param_3,int param_4,int param_5,int param_6,
               int param_7)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  int *piVar5;
  int *piVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iStack_238;
  undefined1 auStack_234 [200];
  int local_16c [79];

  gp = &__global_pointer_;
  if (0 < param_5) {
    uVar1 = 0xc;
    if ((param_5 != 1) && (uVar1 = 8, param_5 == 2)) {
      uVar1 = 10;
    }
    iVar9 = 0x189d89e0;
    if (param_6 == 0) {
      iVar9 = 0x20000000;
    }
    if ((int)(((uint)(param_3 * 0x23eb1c43) >> 0x1c) +
             (int)((ulonglong)((longlong)param_3 * 0x23eb1c43) >> 0x20) * 0x10) < param_4) {
      iVar7 = param_3 << 1;
      iVar8 = 2;
    }
    else {
      iVar8 = 1;
      iVar7 = param_4;
    }
    *param_2 = 0;
    iVar3 = pv_log2((iVar7 << 0x14) / param_3);
    iVar3 = (int)((iVar3 * uVar1 >> 0xf) +
                  (int)((ulonglong)((longlong)iVar3 * (longlong)(int)uVar1) >> 0x20) * 0x20000 +
                 0x20) >> 6;
    iVar2 = iVar3 * 2;
    CalcBands(auStack_234,param_3,iVar7,iVar2);
    shellsort(auStack_234,iVar2);
    uVar4 = *param_2;
    if (0 < iVar2) {
      cumSum_part_0(param_3 - param_7,auStack_234,iVar2,uVar4 * 4 + param_1);
      uVar4 = *param_2;
    }
    *param_2 = uVar4 + iVar2;
    if (iVar8 != 2) {
      return;
    }
    iVar8 = pv_log2((param_4 << 0x14) / iVar7);
    iVar2 = (int)((ulonglong)((longlong)iVar8 * (longlong)iVar9) >> 0x20);
    uVar4 = ((uint)(iVar8 * iVar9) >> 0x1e) + iVar2 * 4;
    iVar9 = ((int)((uVar4 * uVar1 >> 0xf) +
                   ((iVar2 >> 0x1e) * uVar1 + (int)((ulonglong)uVar4 * (ulonglong)uVar1 >> 0x20)) *
                   0x20000 + 0x10) >> 5) * 2;
    CalcBands(local_16c,iVar7,param_4,iVar9);
    shellsort(local_16c,iVar9);
    if (local_16c[0] < (&iStack_238)[iVar3 * 2]) {
      iVar3 = (&iStack_238)[iVar3 * 2] - local_16c[0];
      iVar8 = local_16c[iVar9 + -1] - local_16c[0] >> 1;
      if (iVar3 < iVar8) {
        iVar8 = iVar3;
      }
      local_16c[0] = local_16c[0] + iVar8;
      piVar6 = local_16c + iVar9 + -1;
      *piVar6 = *piVar6 - iVar8;
      shellsort(local_16c,iVar9);
    }
    uVar1 = *param_2;
    if (0 < iVar9) {
      cumSum_part_0(iVar7 - param_7,local_16c,iVar9,uVar1 * 4 + param_1);
      uVar1 = *param_2;
    }
    *param_2 = iVar9 + uVar1;
    return;
  }
  if (param_6 == 0) {
    uVar4 = param_4 - param_3 & 0xfffffffe;
    uVar1 = uVar4 << 1;
    iVar9 = 2;
  }
  else {
    uVar4 = param_4 - param_3 >> 1;
    iVar9 = 1;
    uVar1 = uVar4;
  }
  param_4 = param_4 - (param_3 + uVar1);
  if ((int)uVar4 < 1) {
    if (param_4 < 0) goto LAB_ram_4202ae3c;
    if (param_4 != 0) goto LAB_ram_4202adb6;
LAB_ram_4202add4:
    *param_2 = uVar4;
  }
  else {
    piVar5 = local_16c;
    piVar6 = piVar5 + uVar4;
    do {
      *piVar5 = iVar9;
      piVar5 = piVar5 + 1;
    } while (piVar6 != piVar5);
    if (param_4 < 0) {
LAB_ram_4202ae3c:
      iVar9 = 1;
      iVar8 = 0;
LAB_ram_4202adbc:
      piVar6 = local_16c + iVar8;
      do {
        param_4 = param_4 + iVar9;
        *piVar6 = *piVar6 - iVar9;
        piVar6 = piVar6 + iVar9;
      } while (param_4 != 0);
      if ((int)uVar4 < 1) goto LAB_ram_4202add4;
    }
    else if (param_4 != 0) {
LAB_ram_4202adb6:
      iVar8 = uVar4 - 1;
      iVar9 = -1;
      goto LAB_ram_4202adbc;
    }
    cumSum_part_0(param_3,local_16c,uVar4,param_1);
    *param_2 = uVar4;
  }
  return;
}
