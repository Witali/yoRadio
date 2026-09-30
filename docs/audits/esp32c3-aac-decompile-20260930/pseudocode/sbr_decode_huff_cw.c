/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: sbr_decode_huff_cw @ ram:4205a412
 * Types and parameter counts are inferred; verify against disassembly. */

int sbr_decode_huff_cw(int param_1,undefined4 param_2)

{
  int iVar1;
  int iVar2;

  gp = &__global_pointer_;
  iVar1 = 0;
  do {
    iVar2 = buf_get_1bit(param_2);
    iVar1 = (int)*(char *)(iVar1 * 2 + param_1 + iVar2);
  } while (-1 < iVar1);
  return (iVar1 + 0x40) * 0x1000000 >> 0x18;
}
