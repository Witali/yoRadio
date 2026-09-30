/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: dct_32 @ ram:42059a40
 * Types and parameter counts are inferred; verify against disassembly. */

void dct_32(int param_1)

{
  gp = &__global_pointer_;
  pv_split();
  dct_16(param_1 + 0x40,0);
  dct_16(param_1,1);
  pv_merge_in_place_N32(param_1);
  return;
}
