/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: pv_cosine @ ram:4300e652
 * Types and parameter counts are inferred; verify against disassembly. */

int pv_cosine(uint param_1)

{
  bool bVar1;
  int iVar2;
  int *piVar3;
  int iVar4;
  int iVar5;

  gp = &__global_pointer_;
  iVar5 = ((int)param_1 >> 0x1f ^ param_1) - ((int)param_1 >> 0x1f);
  if (iVar5 < 0x189376) {
    return 0x3fffffff -
           ((int)(((uint)(iVar5 * iVar5) >> 0x1e) +
                 (int)((ulonglong)((longlong)iVar5 * (longlong)iVar5) >> 0x20) * 4) >> 1);
  }
  iVar5 = 0x6487ed51 - iVar5;
  if (iVar5 < 0) {
    if (-0x189376 < iVar5) {
      gp = &__global_pointer_;
      return iVar5;
    }
    iVar5 = -iVar5;
    bVar1 = true;
  }
  else {
    if (iVar5 < 0x189376) {
      return iVar5;
    }
    bVar1 = false;
  }
  piVar3 = (int *)(sin_table + 4);
  iVar2 = (int)((ulonglong)((longlong)iVar5 * 0x4857) >> 0x20) * 4 +
          ((uint)(iVar5 * 0x4857) >> 0x1e);
  do {
    iVar4 = *piVar3;
    piVar3 = piVar3 + 1;
    iVar2 = (int)((ulonglong)((longlong)(iVar4 + iVar2) * (longlong)iVar5) >> 0x20) * 4 +
            ((uint)((iVar4 + iVar2) * iVar5) >> 0x1e);
  } while (piVar3 != (int *)(sin_table + 0x20));
  if (bVar1) {
    iVar2 = -iVar2;
  }
  return iVar2;
}
