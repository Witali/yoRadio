/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: media_lib_module_malloc @ ram:42024378
 * Types and parameter counts are inferred; verify against disassembly. */

void media_lib_module_malloc(undefined4 param_1,size_t param_2)

{
  gp = &__global_pointer_;
  malloc(param_2);
  return;
}
