/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: pv_sine @ ram:4300e5de
 * Types and parameter counts are inferred; verify against disassembly. */

int pv_sine(int param_1)

{
  bool bVar1;
  int iVar2;
  int *piVar3;
  int iVar4;

  gp = &__global_pointer_;
  if (param_1 < 0) {
    if (-0x189376 < param_1) {
      gp = &__global_pointer_;
      return param_1;
    }
    param_1 = -param_1;
    bVar1 = true;
  }
  else {
    if (param_1 < 0x189376) {
      return param_1;
    }
    bVar1 = false;
  }
  piVar3 = (int *)(sin_table + 4);
  iVar2 = (int)((ulonglong)((longlong)param_1 * 0x4857) >> 0x20) * 4 +
          ((uint)(param_1 * 0x4857) >> 0x1e);
  do {
    iVar4 = *piVar3;
    piVar3 = piVar3 + 1;
    iVar2 = (int)((ulonglong)((longlong)(iVar4 + iVar2) * (longlong)param_1) >> 0x20) * 4 +
            ((uint)((iVar4 + iVar2) * param_1) >> 0x1e);
  } while (piVar3 != (int *)(sin_table + 0x20));
  if (bVar1) {
    iVar2 = -iVar2;
  }
  return iVar2;
}
