/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: dct_32 @ ram:4300b732
 * Types and parameter counts are inferred; verify against disassembly. */

void dct_32(int param_1)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  int iVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  undefined4 uVar10;

  gp = &__global_pointer_;
  pv_split();
  dct_16(param_1 + 0x40,0);
  dct_16(param_1,1);
  uVar6 = *(undefined4 *)(param_1 + 0x20);
  iVar2 = *(int *)(param_1 + 0x40);
  uVar1 = *(undefined4 *)(param_1 + 0x18);
  *(undefined4 *)(param_1 + 0x20) = *(undefined4 *)(param_1 + 0x10);
  *(undefined4 *)(param_1 + 0x40) = uVar6;
  *(undefined4 *)(param_1 + 0x18) = *(undefined4 *)(param_1 + 0xc);
  uVar9 = *(undefined4 *)(param_1 + 0x38);
  uVar6 = *(undefined4 *)(param_1 + 0x28);
  *(undefined4 *)(param_1 + 0x38) = *(undefined4 *)(param_1 + 0x1c);
  *(undefined4 *)(param_1 + 0x28) = *(undefined4 *)(param_1 + 0x14);
  uVar10 = *(undefined4 *)(param_1 + 0x30);
  *(undefined4 *)(param_1 + 0x10) = *(undefined4 *)(param_1 + 8);
  *(undefined4 *)(param_1 + 0x30) = uVar1;
  *(undefined4 *)(param_1 + 8) = *(undefined4 *)(param_1 + 4);
  *(int *)(param_1 + 4) = iVar2 + *(int *)(param_1 + 0x44);
  *(int *)(param_1 + 0xc) = *(int *)(param_1 + 0x44) + *(int *)(param_1 + 0x48);
  *(int *)(param_1 + 0x14) = *(int *)(param_1 + 0x48) + *(int *)(param_1 + 0x4c);
  *(undefined4 *)(param_1 + 0x48) = *(undefined4 *)(param_1 + 0x24);
  *(int *)(param_1 + 0x1c) = *(int *)(param_1 + 0x4c) + *(int *)(param_1 + 0x50);
  *(int *)(param_1 + 0x24) = *(int *)(param_1 + 0x50) + *(int *)(param_1 + 0x54);
  iVar7 = *(int *)(param_1 + 0x58);
  iVar3 = *(int *)(param_1 + 0x60);
  iVar4 = *(int *)(param_1 + 0x68);
  iVar5 = *(int *)(param_1 + 0x70);
  iVar2 = *(int *)(param_1 + 0x78);
  *(undefined4 *)(param_1 + 0x58) = *(undefined4 *)(param_1 + 0x2c);
  *(int *)(param_1 + 0x2c) = *(int *)(param_1 + 0x54) + iVar7;
  uVar8 = *(undefined4 *)(param_1 + 0x3c);
  uVar1 = *(undefined4 *)(param_1 + 0x34);
  *(undefined4 *)(param_1 + 0x50) = uVar6;
  *(undefined4 *)(param_1 + 0x60) = uVar10;
  *(undefined4 *)(param_1 + 0x70) = uVar9;
  *(int *)(param_1 + 0x34) = iVar7 + *(int *)(param_1 + 0x5c);
  *(int *)(param_1 + 0x3c) = *(int *)(param_1 + 0x5c) + iVar3;
  *(undefined4 *)(param_1 + 0x68) = uVar1;
  *(undefined4 *)(param_1 + 0x78) = uVar8;
  *(int *)(param_1 + 0x44) = iVar3 + *(int *)(param_1 + 100);
  *(int *)(param_1 + 0x4c) = *(int *)(param_1 + 100) + iVar4;
  *(int *)(param_1 + 0x54) = iVar4 + *(int *)(param_1 + 0x6c);
  *(int *)(param_1 + 0x5c) = *(int *)(param_1 + 0x6c) + iVar5;
  *(int *)(param_1 + 100) = iVar5 + *(int *)(param_1 + 0x74);
  *(int *)(param_1 + 0x6c) = *(int *)(param_1 + 0x74) + iVar2;
  *(int *)(param_1 + 0x74) = *(int *)(param_1 + 0x7c) + iVar2;
  return;
}
