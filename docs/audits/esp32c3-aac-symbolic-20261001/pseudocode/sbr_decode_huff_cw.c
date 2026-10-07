/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_decode_huff_cw @ ram:4301175a
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
