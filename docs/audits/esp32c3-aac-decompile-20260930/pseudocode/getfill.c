/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: getfill @ ram:42045090
 * Types and parameter counts are inferred; verify against disassembly. */

void getfill(int *param_1)

{
  ushort uVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  ushort *puVar5;
  uint uVar6;

  gp = &__global_pointer_;
  uVar2 = param_1[1];
  uVar6 = param_1[3] - (uVar2 >> 3);
  puVar5 = (ushort *)((uVar2 >> 3) + *param_1);
  uVar3 = uVar2 + 4;
  if (uVar6 < 2) {
    if (uVar6 != 1) goto LAB_ram_420450d4;
    uVar1 = *puVar5;
    param_1[1] = uVar3;
    uVar6 = ((uint)(byte)uVar1 << 8) << (uVar2 & 7);
  }
  else {
    uVar1 = *puVar5;
    param_1[1] = uVar3;
    uVar6 = ((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 & 0xffff) << (uVar2 & 7);
  }
  uVar6 = uVar6 >> 0xc & 0xf;
  if (uVar6 == 0xf) {
    uVar6 = param_1[3] - (uVar3 >> 3);
    puVar5 = (ushort *)(*param_1 + (uVar3 >> 3));
    if (uVar6 < 2) {
      iVar4 = 0x70;
      if (uVar6 == 1) {
        iVar4 = (((((uint)(byte)*puVar5 << 8) << (uVar3 & 7)) >> 8 & 0xff) + 0xe) * 8;
      }
    }
    else {
      uVar1 = *puVar5;
      iVar4 = (((((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 << (uVar3 & 7)) << 0x10) >> 0x18) + 0xe)
              * 8;
    }
    param_1[1] = iVar4 + uVar2 + 0xc;
    return;
  }
  uVar3 = uVar3 + uVar6 * 8;
LAB_ram_420450d4:
  param_1[1] = uVar3;
  return;
}
