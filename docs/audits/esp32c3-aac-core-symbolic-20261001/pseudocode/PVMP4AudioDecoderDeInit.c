/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: PVMP4AudioDecoderDeInit @ ram:4300f53e
 * Types and parameter counts are inferred; verify against disassembly. */

void PVMP4AudioDecoderDeInit(aac_analysis_external_t *external,aac_analysis_core_t *core)

{
  gp = &__global_pointer_;
  if (core != (aac_analysis_core_t *)0x0) {
    if (core->program != (aac_analysis_program_t *)0x0) {
      media_lib_free();
    }
    if (core->long_window != (aac_analysis_window_t *)0x0) {
      media_lib_free();
      core->long_window = (aac_analysis_window_t *)0x0;
    }
    if (core->short_window != (aac_analysis_window_t *)0x0) {
      media_lib_free();
      core->short_window = (aac_analysis_window_t *)0x0;
    }
    if (core->sbr != (aac_sbr_owner_abi_t *)0x0) {
      media_lib_free();
      core->sbr = (aac_sbr_owner_abi_t *)0x0;
    }
    if (core->sbr_control != (aac_sbr_control_abi_t *)0x0) {
      media_lib_free();
      core->sbr_control = (aac_sbr_control_abi_t *)0x0;
    }
    if (core->sbr_stream != (aac_analysis_sbr_stream_t *)0x0) {
      media_lib_free();
      core->sbr_stream = (aac_analysis_sbr_stream_t *)0x0;
    }
    if (core->workspace != (aac_analysis_workspace_t *)0x0) {
      media_lib_free();
      core->workspace = (aac_analysis_workspace_t *)0x0;
    }
    media_lib_free(core);
    return;
  }
  return;
}
