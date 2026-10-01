/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: get_prog_config @ ram:43007c52
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4 get_prog_config(int param_1,uint *param_2)

{
  byte bVar1;
  ushort uVar2;
  uint *puVar3;
  undefined4 uVar4;
  ushort *puVar5;
  uint uVar6;
  undefined4 uVar7;
  int iVar8;
  uint uVar9;
  uint *puVar10;
  uint uVar11;
  uint *puVar12;
  uint uVar13;
  uint uVar14;
  uint uVar15;
  int iVar16;
  uint uVar17;

  gp = &__global_pointer_;
  uVar11 = *(uint *)(param_1 + 0x1c);
  uVar9 = *(uint *)(param_1 + 0x24);
  iVar8 = *(int *)(param_1 + 0x18);
  uVar15 = uVar9 - (uVar11 >> 3);
  puVar5 = (ushort *)((uVar11 >> 3) + iVar8);
  uVar13 = uVar11 & 7;
  if (uVar15 < 2) {
    uVar14 = 0;
    if (uVar15 != 1) goto LAB_ram_43007c84;
    uVar2 = *puVar5;
    uVar6 = uVar11 + 4;
    uVar17 = uVar9 - (uVar6 >> 3);
    *(uint *)(param_1 + 0x1c) = uVar6;
    uVar14 = (((uint)(byte)uVar2 << 8) << uVar13) >> 0xc & 0xf;
    uVar15 = uVar6 & 7;
    puVar5 = (ushort *)((uVar6 >> 3) + iVar8);
    if (1 < uVar17) goto LAB_ram_43007c9e;
LAB_ram_43007fc6:
    uVar6 = 0;
    if (uVar17 == 1) {
      uVar6 = (((uint)(byte)*puVar5 << 8) << uVar15) >> 0xe & 3;
    }
  }
  else {
    uVar2 = *puVar5;
    uVar14 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << uVar13) << 0x10) >> 0x1c;
LAB_ram_43007c84:
    uVar6 = uVar11 + 4;
    uVar17 = uVar9 - (uVar6 >> 3);
    *(uint *)(param_1 + 0x1c) = uVar6;
    uVar15 = uVar6 & 7;
    puVar5 = (ushort *)((uVar6 >> 3) + iVar8);
    if (uVar17 < 2) goto LAB_ram_43007fc6;
LAB_ram_43007c9e:
    uVar6 = (((uint)(*puVar5 >> 8) + (uint)*puVar5 * 0x100 << uVar15) << 0x10) >> 0x1e;
  }
  uVar15 = uVar11 + 6;
  *(uint *)(param_1 + 0x1c) = uVar15;
  *param_2 = uVar6;
  uVar6 = uVar9 - (uVar15 >> 3);
  puVar5 = (ushort *)(iVar8 + (uVar15 >> 3));
  if (uVar6 < 2) {
    uVar17 = 0;
    if (uVar6 == 1) {
      uVar17 = (((uint)(byte)*puVar5 << 8) << (uVar15 & 7)) >> 0xc & 0xf;
    }
  }
  else {
    uVar2 = *puVar5;
    uVar17 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar15 & 7)) << 0x10) >> 0x1c;
  }
  iVar16 = *(int *)(param_1 + 0x14);
  uVar15 = uVar11 + 10;
  *(uint *)(param_1 + 0x1c) = uVar15;
  param_2[1] = uVar17;
  if ((iVar16 == 0) && (*(uint *)(*(int *)(param_1 + 0x2c) + 4) != uVar17)) {
    *(uint *)(param_1 + 0x1c) = uVar11;
    return 1;
  }
  uVar6 = uVar9 - (uVar15 >> 3);
  puVar5 = (ushort *)(iVar8 + (uVar15 >> 3));
  iVar16 = param_1 + 0x18;
  if (uVar6 < 2) {
    uVar17 = 0;
    if (uVar6 == 1) {
      uVar17 = (((uint)(byte)*puVar5 << 8) << (uVar15 & 7)) >> 0xc & 0xf;
    }
  }
  else {
    uVar2 = *puVar5;
    uVar17 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar15 & 7)) << 0x10) >> 0x1c;
  }
  uVar15 = uVar11 + 0xe;
  *(uint *)(param_1 + 0x1c) = uVar15;
  param_2[3] = uVar17;
  uVar6 = uVar9 - (uVar15 >> 3);
  puVar5 = (ushort *)(iVar8 + (uVar15 >> 3));
  if (uVar6 < 2) {
    uVar17 = 0;
    if (uVar6 == 1) {
      uVar17 = (((uint)(byte)*puVar5 << 8) << (uVar15 & 7)) >> 0xc & 0xf;
    }
  }
  else {
    uVar2 = *puVar5;
    uVar17 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar15 & 7)) << 0x10) >> 0x1c;
  }
  uVar15 = uVar11 + 0x12;
  *(uint *)(param_1 + 0x1c) = uVar15;
  param_2[0x24] = uVar17;
  uVar6 = uVar9 - (uVar15 >> 3);
  puVar5 = (ushort *)(iVar8 + (uVar15 >> 3));
  if (uVar6 < 2) {
    uVar17 = 0;
    if (uVar6 == 1) {
      uVar17 = (((uint)(byte)*puVar5 << 8) << (uVar15 & 7)) >> 0xc & 0xf;
    }
  }
  else {
    uVar2 = *puVar5;
    uVar17 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar15 & 7)) << 0x10) >> 0x1c;
  }
  uVar15 = uVar11 + 0x16;
  *(uint *)(param_1 + 0x1c) = uVar15;
  param_2[0x45] = uVar17;
  uVar6 = uVar9 - (uVar15 >> 3);
  puVar5 = (ushort *)((uVar15 >> 3) + iVar8);
  if (uVar6 < 2) {
    uVar17 = 0;
    if (uVar6 == 1) {
      uVar17 = (((uint)(byte)*puVar5 << 8) << (uVar15 & 7)) >> 0xe & 3;
    }
  }
  else {
    uVar2 = *puVar5;
    uVar17 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar15 & 7)) << 0x10) >> 0x1e;
  }
  *(uint *)(param_1 + 0x1c) = uVar11 + 0x18;
  uVar15 = uVar11 + 0x18 >> 3;
  param_2[0x66] = uVar17;
  uVar6 = uVar9 - uVar15;
  puVar5 = (ushort *)(iVar8 + uVar15);
  if (uVar6 < 2) {
    uVar15 = 0;
    if (uVar6 == 1) {
      uVar15 = (uint)(byte)*puVar5 << 8;
    }
  }
  else {
    uVar2 = *puVar5;
    uVar15 = (uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 & 0xffff;
  }
  uVar6 = uVar11 + 0x1b;
  *(uint *)(param_1 + 0x1c) = uVar6;
  param_2[0x87] = (uVar15 << uVar13) >> 0xd & 7;
  uVar15 = uVar9 - (uVar6 >> 3);
  puVar5 = (ushort *)(iVar8 + (uVar6 >> 3));
  if (uVar15 < 2) {
    uVar17 = 0;
    if (uVar15 == 1) {
      uVar17 = (((uint)(byte)*puVar5 << 8) << (uVar6 & 7)) >> 0xc & 0xf;
    }
  }
  else {
    uVar2 = *puVar5;
    uVar17 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar6 & 7)) << 0x10) >> 0x1c;
  }
  uVar6 = uVar11 + 0x1f;
  *(uint *)(param_1 + 0x1c) = uVar6;
  param_2[0xa8] = uVar17;
  uVar15 = uVar11 + 0x20;
  if (uVar6 >> 3 < uVar9) {
    bVar1 = *(byte *)((uVar6 >> 3) + iVar8);
    *(uint *)(param_1 + 0x1c) = uVar15;
    uVar6 = ((uint)bVar1 << (uVar6 & 7)) >> 7 & 1;
    param_2[0xc9] = uVar6;
    if (uVar6 != 0) {
      uVar6 = uVar9 - (uVar15 >> 3);
      puVar5 = (ushort *)((uVar15 >> 3) + iVar8);
      if (uVar6 < 2) {
        uVar17 = 0;
        if (uVar6 == 1) {
          uVar17 = (uint)(byte)*puVar5 << 8;
        }
      }
      else {
        uVar2 = *puVar5;
        uVar17 = (uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 & 0xffff;
      }
      uVar15 = uVar11 + 0x24;
      *(uint *)(param_1 + 0x1c) = uVar15;
      param_2[0xca] = (uVar17 << uVar13) >> 0xc & 0xf;
    }
  }
  else {
    *(uint *)(param_1 + 0x1c) = uVar15;
    param_2[0xc9] = 0;
  }
  uVar11 = uVar15 + 1;
  if (uVar15 >> 3 < uVar9) {
    bVar1 = *(byte *)((uVar15 >> 3) + iVar8);
    *(uint *)(param_1 + 0x1c) = uVar11;
    uVar13 = ((uint)bVar1 << (uVar15 & 7)) >> 7 & 1;
    param_2[0xcc] = uVar13;
    if (uVar13 != 0) {
      uVar13 = uVar9 - (uVar11 >> 3);
      puVar5 = (ushort *)(iVar8 + (uVar11 >> 3));
      if (uVar13 < 2) {
        uVar6 = 0;
        if (uVar13 == 1) {
          uVar6 = (((uint)(byte)*puVar5 << 8) << (uVar11 & 7)) >> 0xc & 0xf;
        }
      }
      else {
        uVar2 = *puVar5;
        uVar6 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar11 & 7)) << 0x10) >> 0x1c;
      }
      uVar11 = uVar15 + 5;
      *(uint *)(param_1 + 0x1c) = uVar11;
      param_2[0xcd] = uVar6;
    }
  }
  else {
    *(uint *)(param_1 + 0x1c) = uVar11;
    param_2[0xcc] = 0;
  }
  uVar13 = uVar11 + 1;
  if (uVar11 >> 3 < uVar9) {
    bVar1 = *(byte *)((uVar11 >> 3) + iVar8);
    *(uint *)(param_1 + 0x1c) = uVar13;
    uVar15 = ((uint)bVar1 << (uVar11 & 7)) >> 7 & 1;
    param_2[0xcf] = uVar15;
    if (uVar15 != 0) {
      uVar15 = uVar9 - (uVar13 >> 3);
      puVar5 = (ushort *)(iVar8 + (uVar13 >> 3));
      if (uVar15 < 2) {
        uVar6 = 0;
        if (uVar15 == 1) {
          uVar6 = (((uint)(byte)*puVar5 << 8) << (uVar13 & 7)) >> 0xe & 3;
        }
      }
      else {
        uVar2 = *puVar5;
        uVar6 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar13 & 7)) << 0x10) >> 0x1e;
      }
      uVar15 = uVar11 + 3;
      *(uint *)(param_1 + 0x1c) = uVar15;
      param_2[0xd0] = uVar6;
      uVar13 = 0;
      if (uVar15 >> 3 < uVar9) {
        uVar13 = ((uint)*(byte *)(iVar8 + (uVar15 >> 3)) << (uVar15 & 7)) >> 7 & 1;
      }
      *(uint *)(param_1 + 0x1c) = uVar11 + 4;
      param_2[0xd1] = uVar13;
    }
  }
  else {
    *(uint *)(param_1 + 0x1c) = uVar13;
    param_2[0xcf] = 0;
  }
  get_ele_list(param_2 + 3,iVar16,1);
  get_ele_list(param_2 + 0x24,iVar16,1);
  get_ele_list(param_2 + 0x45,iVar16,1);
  get_ele_list(param_2 + 0x66,iVar16,0);
  get_ele_list(param_2 + 0x87,iVar16,0);
  get_ele_list(param_2 + 0xa8,iVar16,1);
  byte_align(iVar16);
  uVar9 = *(uint *)(param_1 + 0x1c);
  uVar11 = *(int *)(param_1 + 0x24) - (uVar9 >> 3);
  puVar5 = (ushort *)(*(int *)(param_1 + 0x18) + (uVar9 >> 3));
  if (uVar11 < 2) {
    if (uVar11 == 1) {
      uVar11 = (uint)(byte)*puVar5 << 8;
      goto LAB_ram_43007f48;
    }
  }
  else {
    uVar2 = *puVar5;
    uVar11 = (uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 & 0xffff;
LAB_ram_43007f48:
    uVar11 = (uVar11 << (uVar9 & 7)) >> 8 & 0xff;
    if (uVar11 != 0) {
      *(uint *)(param_1 + 0x1c) = (uVar11 - 1) * 8 + uVar9 + 0x10;
      goto LAB_ram_43007f66;
    }
  }
  *(uint *)(param_1 + 0x1c) = uVar9 + 8;
LAB_ram_43007f66:
  if ((int)*(uint *)(param_1 + 0xc) < 0) {
    *(uint *)(param_1 + 0xc) = uVar14;
  }
  else if (uVar14 != *(uint *)(param_1 + 0xc)) {
    return 0;
  }
  puVar10 = param_2 + 0xd7;
  puVar12 = (uint *)(param_1 + 0x2c);
  do {
    uVar13 = param_2[3];
    uVar9 = param_2[1];
    uVar11 = param_2[2];
    *puVar12 = *param_2;
    puVar12[1] = uVar9;
    puVar12[2] = uVar11;
    puVar12[3] = uVar13;
    puVar3 = param_2 + 4;
    param_2 = param_2 + 5;
    puVar12[4] = *puVar3;
    puVar12 = puVar12 + 5;
  } while (param_2 != puVar10);
  iVar8 = *(int *)(param_1 + 0x2c);
  iVar16 = *(int *)(iVar8 + 0x10);
  uVar7 = *(undefined4 *)(iVar8 + 0x50);
  iVar8 = *(int *)(iVar8 + 4);
  if (*(int *)(param_1 + 0xa8) != iVar8) {
    *(int *)(param_1 + 0xa8) = iVar8;
    iVar8 = infoinit(iVar8,param_1 + 0x78,param_1 + 0x30);
    uVar4 = 1;
    if (iVar8 == 0) {
      *(undefined4 *)(param_1 + 0xc4) = uVar7;
      *(int *)(param_1 + 200) = iVar16;
      *(int *)(param_1 + 0x8c) = iVar16 + 1;
      if (iVar16 != 0) {
        *(undefined4 *)(param_1 + 0xdc) = 1;
      }
      uVar4 = 0;
    }
    return uVar4;
  }
  *(undefined4 *)(param_1 + 0xc4) = uVar7;
  *(int *)(param_1 + 200) = iVar16;
  *(int *)(param_1 + 0x8c) = iVar16 + 1;
  if (iVar16 != 0) {
    *(undefined4 *)(param_1 + 0xdc) = 1;
  }
  return 0;
}
