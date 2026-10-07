/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: pv_pow2 @ ram:4300e548
 * Types and parameter counts are inferred; verify against disassembly. */

int pv_pow2(uint param_1)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;

  gp = &__global_pointer_;
  uVar6 = 4;
  if (0x8000000 < (int)param_1) {
    uVar6 = 4 - ((int)param_1 >> 0x1b);
    param_1 = param_1 & 0x7ffffff;
  }
  iVar5 = 0;
  if ((int)param_1 < 0x4000000) {
    param_1 = param_1 + 0x4000000;
    iVar5 = 0x16a09e60;
  }
  iVar3 = param_1 * 4;
  piVar2 = (int *)(pow2_table + 4);
  iVar4 = (int)((ulonglong)((longlong)iVar3 * 0x126456) >> 0x20) * 8 + (param_1 * 0x499158 >> 0x1d);
  do {
    iVar1 = *piVar2;
    piVar2 = piVar2 + 1;
    iVar4 = (int)((ulonglong)((longlong)(iVar4 + iVar1) * (longlong)iVar3) >> 0x20) * 8 +
            ((uint)((iVar4 + iVar1) * iVar3) >> 0x1d);
  } while (piVar2 != (int *)(pow2_table + 0x14));
  iVar4 = iVar4 + 0x1fffb360;
  if (iVar5 != 0) {
    iVar4 = (int)((ulonglong)((longlong)iVar4 * 0x16a09e60) >> 0x20) * 8 +
            ((uint)(iVar4 * 0x16a09e60) >> 0x1d);
  }
  return iVar4 >> (uVar6 & 0x1f);
}
