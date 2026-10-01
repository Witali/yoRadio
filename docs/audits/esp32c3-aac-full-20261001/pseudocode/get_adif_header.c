/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: get_adif_header @ ram:430072f2
 * Types and parameter counts are inferred; verify against disassembly. */

int get_adif_header(int param_1,undefined4 param_2)

{
  ushort uVar1;
  uint uVar2;
  int iVar3;
  ushort *puVar4;
  uint uVar5;
  byte *pbVar6;
  uint uVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;

  gp = &__global_pointer_;
  uVar9 = *(uint *)(param_1 + 0x1c);
  uVar5 = *(uint *)(param_1 + 0x24);
  iVar3 = *(int *)(param_1 + 0x18);
  uVar2 = uVar5 - (uVar9 >> 3);
  pbVar6 = (byte *)(iVar3 + (uVar9 >> 3));
  uVar10 = uVar9 & 7;
  if (uVar2 < 3) {
    if (uVar2 == 1) {
      uVar2 = 0;
    }
    else {
      uVar7 = 0;
      if (uVar2 != 2) goto LAB_ram_43007338;
      uVar2 = (uint)pbVar6[1] << 8;
    }
    uVar7 = (((uint)*pbVar6 << 0x10 | uVar2) << uVar10) << 8;
  }
  else {
    uVar7 = ((((uint)*pbVar6 << 0x10 | (uint)pbVar6[1] << 8 | (uint)pbVar6[2]) << uVar10) >> 8) <<
            0x10;
  }
LAB_ram_43007338:
  uVar2 = uVar9 + 0x10 >> 3;
  *(uint *)(param_1 + 0x1c) = uVar9 + 0x10;
  uVar11 = uVar5 - uVar2;
  pbVar6 = (byte *)(iVar3 + uVar2);
  if (uVar11 < 3) {
    if (uVar11 == 1) {
      uVar2 = 0;
    }
    else {
      if (uVar11 != 2) goto LAB_ram_43007536;
      uVar2 = (uint)pbVar6[1] << 8;
    }
    uVar2 = (uint)*pbVar6 << 0x10 | uVar2;
  }
  else {
    uVar2 = (uint)*pbVar6 << 0x10 | (uint)pbVar6[1] << 8 | (uint)pbVar6[2];
  }
  *(uint *)(param_1 + 0x1c) = uVar9 + 0x20;
  if ((uVar7 | ((uVar2 << uVar10) << 8) >> 0x10) != 0x41444946) {
LAB_ram_43007536:
    *(uint *)(param_1 + 0x1c) = uVar9;
    return -1;
  }
  uVar2 = uVar9 + 0x20 >> 3;
  iVar8 = uVar9 + 0x21;
  if ((uVar2 < uVar5) && (((uint)*(byte *)(uVar2 + iVar3) << uVar10 & 0x80) != 0)) {
    iVar8 = uVar9 + 0x69;
  }
  uVar2 = iVar8 + 2;
  *(uint *)(param_1 + 0x1c) = uVar2;
  uVar9 = 0;
  if (uVar2 >> 3 < uVar5) {
    uVar9 = (uint)*(byte *)((uVar2 >> 3) + iVar3) << (uVar2 & 7) & 0x80;
  }
  uVar2 = iVar8 + 3;
  uVar10 = uVar5 - (uVar2 >> 3);
  *(uint *)(param_1 + 0x1c) = uVar2;
  pbVar6 = (byte *)((uVar2 >> 3) + iVar3);
  if (3 < uVar10) {
    uVar2 = (((uint)*pbVar6 << 0x18 | (uint)pbVar6[1] << 0x10 | (uint)pbVar6[3] |
             (uint)pbVar6[2] << 8) << (uVar2 & 7)) >> 9;
    goto LAB_ram_4300741a;
  }
  if (uVar10 == 2) {
    uVar10 = 0;
LAB_ram_43007548:
    uVar10 = (uint)pbVar6[1] << 0x10 | uVar10;
  }
  else {
    if (uVar10 == 3) {
      uVar10 = (uint)pbVar6[2] << 8;
      goto LAB_ram_43007548;
    }
    if (uVar10 != 1) {
      uVar2 = 0;
      goto LAB_ram_4300741a;
    }
    uVar10 = 0;
  }
  uVar2 = (((uint)*pbVar6 << 0x18 | uVar10) << (uVar2 & 7)) >> 9;
LAB_ram_4300741a:
  uVar10 = iVar8 + 0x1a;
  *(uint *)(param_1 + 0x1c) = uVar10;
  *(uint *)(*(int *)(param_1 + 0x8a74) + 0x24) = uVar2;
  uVar5 = uVar5 - (uVar10 >> 3);
  puVar4 = (ushort *)(iVar3 + (uVar10 >> 3));
  if (uVar5 < 2) {
    uVar2 = 0;
    if (uVar5 == 1) {
      uVar2 = (((uint)(byte)*puVar4 << 8) << (uVar10 & 7)) >> 0xc & 0xf;
    }
  }
  else {
    uVar1 = *puVar4;
    uVar2 = (((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 << (uVar10 & 7)) << 0x10) >> 0x1c;
  }
  *(int *)(param_1 + 0x1c) = iVar8 + 0x1e;
  do {
    if (uVar9 == 0) {
      *(undefined4 *)(param_1 + 0x14) = 1;
      *(int *)(param_1 + 0x1c) = *(int *)(param_1 + 0x1c) + 0x14;
      iVar3 = get_prog_config();
    }
    else {
      *(undefined4 *)(param_1 + 0x14) = 1;
      iVar3 = get_prog_config(param_1,param_2);
    }
  } while ((uVar2 != 0) && (uVar2 = uVar2 - 1, iVar3 == 0));
  return iVar3;
}
