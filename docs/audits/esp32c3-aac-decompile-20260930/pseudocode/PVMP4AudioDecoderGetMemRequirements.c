/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: PVMP4AudioDecoderGetMemRequirements @ ram:42027a52
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4 PVMP4AudioDecoderGetMemRequirements(void)

{
  gp = &__global_pointer_;
  return 0x8a84;
}
