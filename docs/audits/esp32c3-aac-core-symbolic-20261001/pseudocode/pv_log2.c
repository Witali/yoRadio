/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: pv_log2 @ ram:4300e3f4
 * Types and parameter counts are inferred; verify against disassembly. */

int pv_log2(int param_1)

{
  int iVar1;
  int iVar2;
  int *piVar3;
  int iVar4;

  gp = &__global_pointer_;
  if (param_1 < 0x200001) {
    iVar1 = 0;
    iVar4 = 0;
    if (0xfffff < param_1) goto LAB_ram_4300e40a;
    do {
      iVar1 = iVar4 + -1;
      iVar2 = param_1 << 1;
      if (0xfffff < param_1 << 1) break;
      param_1 = param_1 << 2;
      iVar4 = iVar4 + -2;
      iVar1 = iVar4;
      iVar2 = param_1;
    } while (param_1 < 0x100000);
  }
  else {
    iVar1 = 0;
    do {
      param_1 = param_1 >> 1;
      iVar1 = iVar1 + 1;
      iVar2 = param_1;
    } while (0x200000 < param_1);
  }
  iVar1 = iVar1 << 0x14;
  param_1 = iVar2;
LAB_ram_4300e40a:
  if (param_1 != 0x100000) {
    piVar3 = (int *)(log_table + 4);
    iVar4 = (int)((ulonglong)((longlong)param_1 * -0x240a) >> 0x20) * 0x1000 +
            ((uint)(param_1 * -0x240a) >> 0x14);
    do {
      iVar2 = *piVar3;
      piVar3 = piVar3 + 1;
      iVar4 = (int)((ulonglong)((longlong)(iVar4 + iVar2) * (longlong)param_1) >> 0x20) * 0x1000 +
              ((uint)((iVar4 + iVar2) * param_1) >> 0x14);
    } while (piVar3 != (int *)(log_table + 0x20));
    iVar1 = iVar1 + iVar4 + -0x36aea2;
  }
  return iVar1;
}
