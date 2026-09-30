/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: get_dse @ ram:42044790
 * Types and parameter counts are inferred; verify against disassembly. */

void get_dse(undefined1 *param_1,int *param_2)

{
  ushort uVar1;
  uint uVar2;
  undefined1 *puVar3;
  int iVar4;
  undefined1 uVar5;
  uint uVar6;
  ushort *puVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;

  gp = &__global_pointer_;
  iVar8 = param_2[1];
  uVar9 = param_2[3];
  iVar4 = *param_2;
  uVar6 = iVar8 + 4;
  param_2[1] = uVar6;
  uVar10 = 0;
  if (uVar6 >> 3 < uVar9) {
    uVar10 = (uint)*(byte *)((uVar6 >> 3) + iVar4) << (uVar6 & 7) & 0x80;
  }
  uVar2 = iVar8 + 5;
  uVar11 = uVar9 - (uVar2 >> 3);
  param_2[1] = uVar2;
  puVar7 = (ushort *)((uVar2 >> 3) + iVar4);
  uVar6 = iVar8 + 0xd;
  if (uVar11 < 2) {
    if (uVar11 != 1) {
      param_2[1] = uVar6;
      if (uVar10 == 0) {
        return;
      }
      byte_align(param_2);
      return;
    }
    uVar11 = (uint)(byte)*puVar7 << 8;
  }
  else {
    uVar1 = *puVar7;
    uVar11 = (uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 & 0xffff;
  }
  uVar2 = uVar2 & 7;
  uVar11 = (uVar11 << uVar2) >> 8 & 0xff;
  param_2[1] = uVar6;
  if (uVar11 == 0xff) {
    uVar12 = uVar9 - (uVar6 >> 3);
    puVar7 = (ushort *)((uVar6 >> 3) + iVar4);
    if (uVar12 < 2) {
      if (uVar12 == 1) {
        uVar11 = ((((uint)(byte)*puVar7 << 8) << uVar2) >> 8 & 0xff) + 0xff;
      }
    }
    else {
      uVar1 = *puVar7;
      uVar11 = ((((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 << uVar2) << 0x10) >> 0x18) + 0xff;
    }
    uVar6 = iVar8 + 0x15;
    param_2[1] = uVar6;
    if (uVar10 != 0) {
      byte_align(param_2);
      uVar6 = param_2[1];
      iVar4 = *param_2;
      uVar9 = param_2[3];
    }
  }
  else {
    if (uVar10 != 0) {
      byte_align(param_2);
    }
    if (uVar11 == 0) {
      return;
    }
    uVar6 = param_2[1];
    iVar4 = *param_2;
    uVar9 = param_2[3];
  }
  puVar3 = param_1 + (uVar11 - 1);
  do {
    uVar9 = uVar9 - (uVar6 >> 3);
    puVar7 = (ushort *)(iVar4 + (uVar6 >> 3));
    if (uVar9 < 2) {
      uVar5 = 0;
      if (uVar9 != 1) goto LAB_ram_4204482a;
      uVar1 = *puVar7;
      param_2[1] = uVar6 + 8;
      *param_1 = (char)((((uint)(byte)uVar1 << 8) << (uVar6 & 7)) >> 8);
    }
    else {
      uVar1 = *puVar7;
      uVar5 = (undefined1)(((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 << (uVar6 & 7)) >> 8);
LAB_ram_4204482a:
      param_2[1] = uVar6 + 8;
      *param_1 = uVar5;
    }
    if (puVar3 == param_1) {
      gp = &__global_pointer_;
      return;
    }
    uVar6 = param_2[1];
    iVar4 = *param_2;
    uVar9 = param_2[3];
    param_1 = param_1 + 1;
  } while( true );
}
