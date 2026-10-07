/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: unpack_idx_sgn @ ram:4205a60e
 * Types and parameter counts are inferred; verify against disassembly. */

void unpack_idx_sgn(undefined2 *param_1,int param_2,int param_3,int *param_4,int *param_5)

{
  byte bVar1;
  uint uVar2;
  undefined2 *puVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  int iVar9;

  gp = &__global_pointer_;
  iVar7 = *(int *)(param_3 + 8);
  iVar4 = *(int *)(param_3 + 0xc);
  puVar3 = param_1;
  if (*(int *)(param_3 + 4) == 4) {
    iVar6 = param_2 * 0x13 >> 9;
    uVar8 = iVar6 - iVar4;
    param_2 = iVar6 * -0x1b + param_2;
    if (iVar6 == iVar4) {
      *param_1 = 0;
    }
    else {
      uVar5 = param_4[1];
      uVar2 = uVar8;
      if (uVar5 >> 3 < (uint)param_4[3]) {
        bVar1 = *(byte *)((uVar5 >> 3) + *param_4);
        param_4[1] = uVar5 + 1;
        if (((uint)bVar1 << (uVar5 & 7) & 0x80) != 0) {
          uVar2 = -uVar8;
        }
      }
      else {
        param_4[1] = uVar5 + 1;
      }
      iVar9 = *param_5;
      *param_1 = (short)uVar2;
      iVar6 = ((int)uVar8 >> 0x1f ^ uVar8) - ((int)uVar8 >> 0x1f);
      if (iVar9 < iVar6) {
        *param_5 = iVar6;
      }
    }
    iVar6 = param_2 * 0x39 >> 9;
    param_2 = param_2 + iVar6 * -9;
    puVar3 = param_1 + 2;
    uVar8 = iVar6 - iVar4;
    if (iVar6 == iVar4) {
      param_1[1] = 0;
    }
    else {
      uVar5 = param_4[1];
      uVar2 = uVar8;
      if (uVar5 >> 3 < (uint)param_4[3]) {
        bVar1 = *(byte *)((uVar5 >> 3) + *param_4);
        param_4[1] = uVar5 + 1;
        if (((uint)bVar1 << (uVar5 & 7) & 0x80) != 0) {
          uVar2 = -uVar8;
        }
      }
      else {
        param_4[1] = uVar5 + 1;
      }
      iVar9 = *param_5;
      param_1[1] = (short)uVar2;
      iVar6 = ((int)uVar8 >> 0x1f ^ uVar8) - ((int)uVar8 >> 0x1f);
      if (iVar9 < iVar6) {
        *param_5 = iVar6;
      }
    }
  }
  iVar6 = param_2 * *(int *)(div_mod + iVar7 * 4) >> 0xd;
  uVar8 = iVar6 - iVar4;
  param_2 = param_2 - iVar7 * iVar6;
  if (iVar6 == iVar4) {
    *puVar3 = 0;
  }
  else {
    uVar5 = param_4[1];
    uVar2 = uVar8;
    if (uVar5 >> 3 < (uint)param_4[3]) {
      bVar1 = *(byte *)((uVar5 >> 3) + *param_4);
      param_4[1] = uVar5 + 1;
      if (((uint)bVar1 << (uVar5 & 7) & 0x80) != 0) {
        uVar2 = -uVar8;
      }
    }
    else {
      param_4[1] = uVar5 + 1;
    }
    iVar7 = *param_5;
    *puVar3 = (short)uVar2;
    iVar6 = ((int)uVar8 >> 0x1f ^ uVar8) - ((int)uVar8 >> 0x1f);
    if (iVar7 < iVar6) {
      *param_5 = iVar6;
    }
  }
  uVar8 = param_2 - iVar4;
  if (param_2 == iVar4) {
    puVar3[1] = 0;
  }
  else {
    uVar5 = param_4[1];
    uVar2 = uVar8;
    if (uVar5 >> 3 < (uint)param_4[3]) {
      bVar1 = *(byte *)((uVar5 >> 3) + *param_4);
      param_4[1] = uVar5 + 1;
      if (((uint)bVar1 << (uVar5 & 7) & 0x80) != 0) {
        uVar2 = -uVar8;
      }
    }
    else {
      param_4[1] = uVar5 + 1;
    }
    iVar4 = *param_5;
    puVar3[1] = (short)uVar2;
    iVar7 = (uVar8 ^ (int)uVar8 >> 0x1f) - ((int)uVar8 >> 0x1f);
    if (iVar4 < iVar7) {
      *param_5 = iVar7;
      return;
    }
  }
  return;
}
