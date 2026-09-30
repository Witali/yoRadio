/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: PVMP4AudioDecoderDeInit @ ram:42027ab0
 * Types and parameter counts are inferred; verify against disassembly. */

void PVMP4AudioDecoderDeInit(undefined4 param_1,int param_2)

{
  gp = &__global_pointer_;
  if (param_2 != 0) {
    if (*(int *)(param_2 + 0x2c) != 0) {
      media_lib_free();
    }
    if (*(int *)(param_2 + 0x70) != 0) {
      media_lib_free();
      *(undefined4 *)(param_2 + 0x70) = 0;
    }
    if (*(int *)(param_2 + 0x74) != 0) {
      media_lib_free();
      *(undefined4 *)(param_2 + 0x74) = 0;
    }
    if (*(int *)(param_2 + 0x8a58) != 0) {
      media_lib_free();
      *(undefined4 *)(param_2 + 0x8a58) = 0;
    }
    if (*(int *)(param_2 + 0x8a5c) != 0) {
      media_lib_free();
      *(undefined4 *)(param_2 + 0x8a5c) = 0;
    }
    if (*(int *)(param_2 + 0x8a60) != 0) {
      media_lib_free();
      *(undefined4 *)(param_2 + 0x8a60) = 0;
    }
    if (*(int *)(param_2 + 0x8a7c) != 0) {
      media_lib_free();
      *(undefined4 *)(param_2 + 0x8a7c) = 0;
    }
    media_lib_free(param_2);
    return;
  }
  return;
}
