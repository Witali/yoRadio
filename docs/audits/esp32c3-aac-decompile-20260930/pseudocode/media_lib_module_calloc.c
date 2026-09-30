/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: media_lib_module_calloc @ ram:42024382
 * Types and parameter counts are inferred; verify against disassembly. */

void media_lib_module_calloc(undefined4 param_1,size_t param_2,size_t param_3)

{
  gp = &__global_pointer_;
  calloc(param_2,param_3);
  return;
}
