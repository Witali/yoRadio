/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: energy_estimation @ ram:4204318c
 * Types and parameter counts are inferred; verify against disassembly. */

void energy_estimation(int param_1,int param_2,int param_3,int param_4,int param_5,int param_6,
                      int param_7,int param_8,int param_9)

{
  longlong lVar1;
  longlong lVar2;
  longlong lVar3;
  longlong lVar4;
  int iVar5;
  int iVar6;
  int *piVar7;
  int iVar8;
  int *piVar9;
  int iVar10;
  uint uVar11;
  int iVar12;
  uint uVar13;
  uint uVar14;
  int iVar15;
  int iVar16;
  int *piVar17;

  gp = &__global_pointer_;
  iVar10 = *(int *)(param_5 + param_6 * 4 + 8);
  iVar12 = (param_9 * 0x30 + param_7) * 4;
  iVar8 = iVar10 * 2;
  iVar16 = param_9 + 1;
  iVar5 = *(int *)(param_1 + iVar12);
  iVar15 = *(int *)(param_2 + iVar12);
  if (iVar16 < iVar8) {
    uVar11 = 0;
    iVar6 = 0;
    piVar7 = (int *)(param_2 + 0xc0 + iVar12);
    piVar9 = (int *)(param_1 + 0xc0 + iVar12);
    do {
      uVar13 = iVar5 * iVar5;
      piVar17 = piVar9 + 0x30;
      lVar1 = (longlong)iVar5;
      lVar3 = (longlong)iVar5;
      uVar14 = uVar13 + uVar11;
      iVar5 = *piVar9;
      lVar2 = (longlong)iVar15;
      lVar4 = (longlong)iVar15;
      uVar11 = iVar15 * iVar15 + uVar14;
      iVar15 = *piVar7;
      iVar6 = (uint)(uVar11 < uVar14) +
              (uint)(uVar14 < uVar13) + (int)((ulonglong)(lVar1 * lVar3) >> 0x20) + iVar6 +
              (int)((ulonglong)(lVar2 * lVar4) >> 0x20);
      piVar7 = piVar7 + 0x30;
      piVar9 = piVar17;
    } while ((int *)(param_1 + (iVar10 * 0x60 + param_7) * 4) != piVar17);
    iVar16 = (iVar8 + iVar16 + -1) - param_9;
  }
  else {
    uVar11 = 0;
    iVar6 = 0;
  }
  piVar7 = (int *)(param_4 + param_8 * 4);
  piVar9 = (int *)(param_3 + param_8 * 4);
  uVar11 = uVar11 + iVar5 * iVar5;
  uVar13 = iVar15 * iVar15 + uVar11;
  iVar5 = (uint)(uVar13 < uVar11) +
          (uint)(uVar11 < (uint)(iVar5 * iVar5)) +
          (int)((ulonglong)((longlong)iVar5 * (longlong)iVar5) >> 0x20) + iVar6 +
          (int)((ulonglong)((longlong)iVar15 * (longlong)iVar15) >> 0x20);
  if (iVar5 < 0) {
    uVar13 = 0x3fffffff;
  }
  else {
    if (uVar13 == 0 && iVar5 == 0) {
      *piVar9 = 0;
      *piVar7 = -100;
      return;
    }
    if (iVar5 != 0) {
      iVar8 = pv_normalize(iVar5);
      if (iVar8 == 0) {
        iVar5 = iVar5 >> 1;
        iVar8 = 0x21;
      }
      else {
        uVar11 = iVar8 - 1;
        if ((int)(iVar8 - 0x21U) < 0) {
          iVar5 = (iVar5 << (uVar11 & 0x1f)) + ((uVar13 >> 1) >> (0x1f - uVar11 & 0x1f));
        }
        else {
          iVar5 = uVar13 << (iVar8 - 0x21U & 0x1f);
        }
        iVar5 = iVar5 >> 1;
        iVar8 = 0x21 - uVar11;
      }
      goto LAB_ram_420432ca;
    }
    uVar13 = uVar13 >> 1;
  }
  uVar11 = pv_normalize(uVar13);
  iVar5 = uVar13 << (uVar11 & 0x1f);
  iVar8 = 1 - uVar11;
LAB_ram_420432ca:
  uVar11 = iVar16 - param_9;
  *piVar7 = iVar8;
  if ((param_9 - iVar16 & uVar11) != uVar11) {
    *piVar9 = (int)((ulonglong)
                    ((longlong)((int)*(short *)(pow2 + uVar11 * 2) << 0x10) * (longlong)iVar5) >>
                   0x20);
    return;
  }
  *piVar9 = iVar5 >> ((int)*(short *)(pow2 + uVar11 * 2) & 0x1fU);
  return;
}
