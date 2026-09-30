/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: pv_cosine @ ram:4204869c
 * Types and parameter counts are inferred; verify against disassembly. */

int pv_cosine(uint param_1)

{
  int iVar1;

  gp = &__global_pointer_;
  iVar1 = ((int)param_1 >> 0x1f ^ param_1) - ((int)param_1 >> 0x1f);
  if (0x189375 < iVar1) {
    iVar1 = pv_sine(0x6487ed51 - iVar1);
    return iVar1;
  }
  return 0x3fffffff -
         ((int)(((uint)(iVar1 * iVar1) >> 0x1e) +
               (int)((ulonglong)((longlong)iVar1 * (longlong)iVar1) >> 0x20) * 4) >> 1);
}
