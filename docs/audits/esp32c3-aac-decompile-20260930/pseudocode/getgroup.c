/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: getgroup @ ram:4205879a
 * Types and parameter counts are inferred; verify against disassembly. */

void getgroup(int *param_1,int *param_2)

{
  ushort uVar1;
  uint uVar2;
  ushort *puVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;

  gp = &__global_pointer_;
  uVar5 = param_2[1];
  uVar4 = param_2[3] - (uVar5 >> 3);
  puVar3 = (ushort *)(*param_2 + (uVar5 >> 3));
  if (uVar4 < 2) {
    uVar2 = 0;
    if (uVar4 == 1) {
      uVar2 = (((uint)(byte)*puVar3 << 8) << (uVar5 & 7)) >> 9 & 0x7f;
    }
  }
  else {
    uVar1 = *puVar3;
    uVar2 = (((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 << (uVar5 & 7)) << 0x10) >> 0x19;
  }
  param_2[1] = uVar5 + 7;
  uVar4 = 0x40;
  iVar6 = 1;
  do {
    if ((uVar4 & uVar2) == 0) {
      *param_1 = iVar6;
      param_1 = param_1 + 1;
    }
    iVar6 = iVar6 + 1;
    uVar4 = uVar4 >> 1;
  } while (iVar6 != 8);
  *param_1 = 8;
  return;
}
