/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: get_prog_config @ ram:42044910
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4 get_prog_config(int param_1,uint *param_2)

{
  byte bVar1;
  ushort uVar2;
  uint *puVar3;
  undefined4 uVar4;
  ushort *puVar5;
  uint uVar6;
  int iVar7;
  uint uVar8;
  uint *puVar9;
  uint uVar10;
  uint *puVar11;
  uint uVar12;
  uint uVar13;
  uint uVar14;
  int iVar15;
  uint uVar16;

  gp = &__global_pointer_;
  uVar10 = *(uint *)(param_1 + 0x1c);
  uVar8 = *(uint *)(param_1 + 0x24);
  iVar7 = *(int *)(param_1 + 0x18);
  uVar14 = uVar8 - (uVar10 >> 3);
  puVar5 = (ushort *)((uVar10 >> 3) + iVar7);
  uVar12 = uVar10 & 7;
  if (uVar14 < 2) {
    uVar13 = 0;
    if (uVar14 != 1) goto LAB_ram_42044942;
    uVar2 = *puVar5;
    uVar6 = uVar10 + 4;
    uVar16 = uVar8 - (uVar6 >> 3);
    *(uint *)(param_1 + 0x1c) = uVar6;
    uVar13 = (((uint)(byte)uVar2 << 8) << uVar12) >> 0xc & 0xf;
    uVar14 = uVar6 & 7;
    puVar5 = (ushort *)((uVar6 >> 3) + iVar7);
    if (uVar16 < 2) goto LAB_ram_42044c68;
LAB_ram_4204495c:
    uVar6 = (((uint)(*puVar5 >> 8) + (uint)*puVar5 * 0x100 << uVar14) << 0x10) >> 0x1e;
  }
  else {
    uVar2 = *puVar5;
    uVar13 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << uVar12) << 0x10) >> 0x1c;
LAB_ram_42044942:
    uVar6 = uVar10 + 4;
    uVar16 = uVar8 - (uVar6 >> 3);
    *(uint *)(param_1 + 0x1c) = uVar6;
    uVar14 = uVar6 & 7;
    puVar5 = (ushort *)((uVar6 >> 3) + iVar7);
    if (1 < uVar16) goto LAB_ram_4204495c;
LAB_ram_42044c68:
    uVar6 = 0;
    if (uVar16 == 1) {
      uVar6 = (((uint)(byte)*puVar5 << 8) << uVar14) >> 0xe & 3;
    }
  }
  uVar14 = uVar10 + 6;
  *(uint *)(param_1 + 0x1c) = uVar14;
  *param_2 = uVar6;
  uVar6 = uVar8 - (uVar14 >> 3);
  puVar5 = (ushort *)(iVar7 + (uVar14 >> 3));
  if (uVar6 < 2) {
    uVar16 = 0;
    if (uVar6 == 1) {
      uVar16 = (((uint)(byte)*puVar5 << 8) << (uVar14 & 7)) >> 0xc & 0xf;
    }
  }
  else {
    uVar2 = *puVar5;
    uVar16 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar14 & 7)) << 0x10) >> 0x1c;
  }
  iVar15 = *(int *)(param_1 + 0x14);
  uVar14 = uVar10 + 10;
  *(uint *)(param_1 + 0x1c) = uVar14;
  param_2[1] = uVar16;
  if ((iVar15 == 0) && (*(uint *)(*(int *)(param_1 + 0x2c) + 4) != uVar16)) {
    *(uint *)(param_1 + 0x1c) = uVar10;
    return 1;
  }
  uVar6 = uVar8 - (uVar14 >> 3);
  puVar5 = (ushort *)(iVar7 + (uVar14 >> 3));
  iVar15 = param_1 + 0x18;
  if (uVar6 < 2) {
    uVar16 = 0;
    if (uVar6 == 1) {
      uVar16 = (((uint)(byte)*puVar5 << 8) << (uVar14 & 7)) >> 0xc & 0xf;
    }
  }
  else {
    uVar2 = *puVar5;
    uVar16 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar14 & 7)) << 0x10) >> 0x1c;
  }
  uVar14 = uVar10 + 0xe;
  *(uint *)(param_1 + 0x1c) = uVar14;
  param_2[3] = uVar16;
  uVar6 = uVar8 - (uVar14 >> 3);
  puVar5 = (ushort *)(iVar7 + (uVar14 >> 3));
  if (uVar6 < 2) {
    uVar16 = 0;
    if (uVar6 == 1) {
      uVar16 = (((uint)(byte)*puVar5 << 8) << (uVar14 & 7)) >> 0xc & 0xf;
    }
  }
  else {
    uVar2 = *puVar5;
    uVar16 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar14 & 7)) << 0x10) >> 0x1c;
  }
  uVar14 = uVar10 + 0x12;
  *(uint *)(param_1 + 0x1c) = uVar14;
  param_2[0x24] = uVar16;
  uVar6 = uVar8 - (uVar14 >> 3);
  puVar5 = (ushort *)(iVar7 + (uVar14 >> 3));
  if (uVar6 < 2) {
    uVar16 = 0;
    if (uVar6 == 1) {
      uVar16 = (((uint)(byte)*puVar5 << 8) << (uVar14 & 7)) >> 0xc & 0xf;
    }
  }
  else {
    uVar2 = *puVar5;
    uVar16 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar14 & 7)) << 0x10) >> 0x1c;
  }
  uVar14 = uVar10 + 0x16;
  *(uint *)(param_1 + 0x1c) = uVar14;
  param_2[0x45] = uVar16;
  uVar6 = uVar8 - (uVar14 >> 3);
  puVar5 = (ushort *)((uVar14 >> 3) + iVar7);
  if (uVar6 < 2) {
    uVar16 = 0;
    if (uVar6 == 1) {
      uVar16 = (((uint)(byte)*puVar5 << 8) << (uVar14 & 7)) >> 0xe & 3;
    }
  }
  else {
    uVar2 = *puVar5;
    uVar16 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar14 & 7)) << 0x10) >> 0x1e;
  }
  *(uint *)(param_1 + 0x1c) = uVar10 + 0x18;
  uVar14 = uVar10 + 0x18 >> 3;
  param_2[0x66] = uVar16;
  uVar6 = uVar8 - uVar14;
  puVar5 = (ushort *)(iVar7 + uVar14);
  if (uVar6 < 2) {
    uVar14 = 0;
    if (uVar6 == 1) {
      uVar14 = (uint)(byte)*puVar5 << 8;
    }
  }
  else {
    uVar2 = *puVar5;
    uVar14 = (uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 & 0xffff;
  }
  uVar6 = uVar10 + 0x1b;
  *(uint *)(param_1 + 0x1c) = uVar6;
  param_2[0x87] = (uVar14 << uVar12) >> 0xd & 7;
  uVar14 = uVar8 - (uVar6 >> 3);
  puVar5 = (ushort *)(iVar7 + (uVar6 >> 3));
  if (uVar14 < 2) {
    uVar16 = 0;
    if (uVar14 == 1) {
      uVar16 = (((uint)(byte)*puVar5 << 8) << (uVar6 & 7)) >> 0xc & 0xf;
    }
  }
  else {
    uVar2 = *puVar5;
    uVar16 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar6 & 7)) << 0x10) >> 0x1c;
  }
  uVar6 = uVar10 + 0x1f;
  *(uint *)(param_1 + 0x1c) = uVar6;
  param_2[0xa8] = uVar16;
  uVar14 = uVar10 + 0x20;
  if (uVar6 >> 3 < uVar8) {
    bVar1 = *(byte *)((uVar6 >> 3) + iVar7);
    *(uint *)(param_1 + 0x1c) = uVar14;
    uVar6 = ((uint)bVar1 << (uVar6 & 7)) >> 7 & 1;
    param_2[0xc9] = uVar6;
    if (uVar6 != 0) {
      uVar6 = uVar8 - (uVar14 >> 3);
      puVar5 = (ushort *)((uVar14 >> 3) + iVar7);
      if (uVar6 < 2) {
        uVar16 = 0;
        if (uVar6 == 1) {
          uVar16 = (uint)(byte)*puVar5 << 8;
        }
      }
      else {
        uVar2 = *puVar5;
        uVar16 = (uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 & 0xffff;
      }
      uVar14 = uVar10 + 0x24;
      *(uint *)(param_1 + 0x1c) = uVar14;
      param_2[0xca] = (uVar16 << uVar12) >> 0xc & 0xf;
    }
  }
  else {
    *(uint *)(param_1 + 0x1c) = uVar14;
    param_2[0xc9] = 0;
  }
  uVar10 = uVar14 + 1;
  if (uVar14 >> 3 < uVar8) {
    bVar1 = *(byte *)((uVar14 >> 3) + iVar7);
    *(uint *)(param_1 + 0x1c) = uVar10;
    uVar12 = ((uint)bVar1 << (uVar14 & 7)) >> 7 & 1;
    param_2[0xcc] = uVar12;
    if (uVar12 != 0) {
      uVar12 = uVar8 - (uVar10 >> 3);
      puVar5 = (ushort *)(iVar7 + (uVar10 >> 3));
      if (uVar12 < 2) {
        uVar6 = 0;
        if (uVar12 == 1) {
          uVar6 = (((uint)(byte)*puVar5 << 8) << (uVar10 & 7)) >> 0xc & 0xf;
        }
      }
      else {
        uVar2 = *puVar5;
        uVar6 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar10 & 7)) << 0x10) >> 0x1c;
      }
      uVar10 = uVar14 + 5;
      *(uint *)(param_1 + 0x1c) = uVar10;
      param_2[0xcd] = uVar6;
    }
  }
  else {
    *(uint *)(param_1 + 0x1c) = uVar10;
    param_2[0xcc] = 0;
  }
  uVar12 = uVar10 + 1;
  if (uVar10 >> 3 < uVar8) {
    bVar1 = *(byte *)((uVar10 >> 3) + iVar7);
    *(uint *)(param_1 + 0x1c) = uVar12;
    uVar14 = ((uint)bVar1 << (uVar10 & 7)) >> 7 & 1;
    param_2[0xcf] = uVar14;
    if (uVar14 != 0) {
      uVar14 = uVar8 - (uVar12 >> 3);
      puVar5 = (ushort *)(iVar7 + (uVar12 >> 3));
      if (uVar14 < 2) {
        uVar6 = 0;
        if (uVar14 == 1) {
          uVar6 = (((uint)(byte)*puVar5 << 8) << (uVar12 & 7)) >> 0xe & 3;
        }
      }
      else {
        uVar2 = *puVar5;
        uVar6 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar12 & 7)) << 0x10) >> 0x1e;
      }
      uVar14 = uVar10 + 3;
      *(uint *)(param_1 + 0x1c) = uVar14;
      param_2[0xd0] = uVar6;
      uVar12 = 0;
      if (uVar14 >> 3 < uVar8) {
        uVar12 = ((uint)*(byte *)(iVar7 + (uVar14 >> 3)) << (uVar14 & 7)) >> 7 & 1;
      }
      *(uint *)(param_1 + 0x1c) = uVar10 + 4;
      param_2[0xd1] = uVar12;
    }
  }
  else {
    *(uint *)(param_1 + 0x1c) = uVar12;
    param_2[0xcf] = 0;
  }
  get_ele_list(param_2 + 3,iVar15,1);
  get_ele_list(param_2 + 0x24,iVar15,1);
  get_ele_list(param_2 + 0x45,iVar15,1);
  get_ele_list(param_2 + 0x66,iVar15,0);
  get_ele_list(param_2 + 0x87,iVar15,0);
  get_ele_list(param_2 + 0xa8,iVar15,1);
  byte_align(iVar15);
  uVar8 = *(uint *)(param_1 + 0x1c);
  uVar10 = *(int *)(param_1 + 0x24) - (uVar8 >> 3);
  puVar5 = (ushort *)(*(int *)(param_1 + 0x18) + (uVar8 >> 3));
  if (uVar10 < 2) {
    if (uVar10 == 1) {
      uVar10 = (uint)(byte)*puVar5 << 8;
      goto LAB_ram_42044bea;
    }
  }
  else {
    uVar2 = *puVar5;
    uVar10 = (uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 & 0xffff;
LAB_ram_42044bea:
    uVar10 = (uVar10 << (uVar8 & 7)) >> 8 & 0xff;
    if (uVar10 != 0) {
      *(uint *)(param_1 + 0x1c) = (uVar10 - 1) * 8 + uVar8 + 0x10;
      goto LAB_ram_42044c08;
    }
  }
  *(uint *)(param_1 + 0x1c) = uVar8 + 8;
LAB_ram_42044c08:
  if ((int)*(uint *)(param_1 + 0xc) < 0) {
    *(uint *)(param_1 + 0xc) = uVar13;
  }
  else if (uVar13 != *(uint *)(param_1 + 0xc)) {
    return 0;
  }
  puVar9 = param_2 + 0xd7;
  puVar11 = (uint *)(param_1 + 0x2c);
  do {
    uVar12 = param_2[3];
    uVar8 = param_2[1];
    uVar10 = param_2[2];
    *puVar11 = *param_2;
    puVar11[1] = uVar8;
    puVar11[2] = uVar10;
    puVar11[3] = uVar12;
    puVar3 = param_2 + 4;
    param_2 = param_2 + 5;
    puVar11[4] = *puVar3;
    puVar11 = puVar11 + 5;
  } while (param_2 != puVar9);
  iVar7 = *(int *)(param_1 + 0x2c);
  uVar4 = set_mc_info(param_1 + 0x8c,*(undefined4 *)(iVar7 + 4),*(undefined4 *)(iVar7 + 0x50),
                      *(undefined4 *)(iVar7 + 0x10),param_1 + 0x78,param_1 + 0x30);
  return uVar4;
}
