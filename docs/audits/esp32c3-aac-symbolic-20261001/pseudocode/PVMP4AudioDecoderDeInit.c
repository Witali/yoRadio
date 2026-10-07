/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: PVMP4AudioDecoderDeInit @ ram:4300f53e
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
