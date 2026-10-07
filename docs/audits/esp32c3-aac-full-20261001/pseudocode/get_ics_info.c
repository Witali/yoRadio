/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: get_ics_info @ ram:43007ab6
 * Types and parameter counts are inferred; verify against disassembly. */

uint get_ics_info(int *param_1,int param_2,uint *param_3,uint *param_4,undefined4 *param_5,
                 uint *param_6,int *param_7,int param_8,int param_9)

{
  ushort uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  ushort *puVar7;
  uint uVar8;
  uint uVar9;
  int iVar10;

  gp = &__global_pointer_;
  uVar2 = param_1[1];
  iVar10 = *param_1;
  uVar9 = param_1[3] - (uVar2 >> 3);
  puVar7 = (ushort *)((uVar2 >> 3) + iVar10);
  if (uVar9 < 2) {
    if (uVar9 == 1) {
      uVar9 = (uint)(byte)*puVar7 << 8;
      goto LAB_ram_43007aec;
    }
    iVar5 = *param_7;
    param_1[1] = uVar2 + 4;
    *param_4 = 0;
    uVar2 = *(uint *)(iVar5 + 0x30);
    uVar3 = 0;
  }
  else {
    uVar1 = *puVar7;
    uVar9 = (uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 & 0xffff;
LAB_ram_43007aec:
    uVar9 = uVar9 << (uVar2 & 7);
    uVar3 = uVar9 >> 0xd & 3;
    iVar5 = param_7[uVar3];
    param_1[1] = uVar2 + 4;
    *param_4 = uVar9 >> 0xc & 1;
    uVar2 = *(uint *)(iVar5 + 0x30);
    if (uVar3 == 2) {
      uVar9 = param_1[1];
      uVar8 = param_1[3] - (uVar9 >> 3);
      puVar7 = (ushort *)(iVar10 + (uVar9 >> 3));
      if (uVar8 < 2) {
        uVar4 = 0;
        uVar6 = 0;
        if (uVar8 == 1) {
          uVar4 = (((uint)(byte)*puVar7 << 8) << (uVar9 & 7)) >> 0xc & 0xf;
          uVar6 = (uint)(uVar2 < uVar4);
        }
      }
      else {
        uVar1 = *puVar7;
        uVar4 = (((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 << (uVar9 & 7)) << 0x10) >> 0x1c;
        uVar6 = (uint)(uVar2 < uVar4);
      }
      param_1[1] = uVar9 + 4;
      getgroup(param_5,param_1);
      goto LAB_ram_43007b6c;
    }
  }
  *param_5 = 1;
  uVar9 = param_1[1];
  uVar8 = param_1[3] - (uVar9 >> 3);
  puVar7 = (ushort *)(iVar10 + (uVar9 >> 3));
  if (uVar8 < 2) {
    uVar4 = 0;
    uVar6 = 0;
    if (uVar8 == 1) {
      uVar8 = ((uint)(byte)*puVar7 << 8) << (uVar9 & 7);
      uVar4 = uVar8 >> 10 & 0x3f;
      uVar6 = (uint)(uVar2 < uVar4) | uVar8 >> 9 & 1;
    }
  }
  else {
    uVar1 = *puVar7;
    uVar8 = ((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 & 0xffff) << (uVar9 & 7);
    uVar4 = uVar8 >> 10 & 0x3f;
    uVar6 = (uint)(uVar2 < uVar4) | uVar8 >> 9 & 1;
  }
  param_1[1] = uVar9 + 7;
LAB_ram_43007b6c:
  *(undefined4 *)(param_8 + 0x224) = 0;
  if (param_2 != 0) {
    *(undefined4 *)(param_9 + 0x224) = 0;
  }
  *param_6 = uVar4;
  *param_3 = uVar3;
  return uVar6;
}
