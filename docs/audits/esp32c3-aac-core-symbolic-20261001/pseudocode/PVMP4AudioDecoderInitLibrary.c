/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: PVMP4AudioDecoderInitLibrary @ ram:4300f5ee
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4
PVMP4AudioDecoderInitLibrary
          (aac_analysis_external_t *external,aac_analysis_core_t *core,int32_t param_3,
          undefined4 param_4,int param_5)

{
  aac_analysis_program_t *paVar1;
  aac_analysis_window_t *paVar2;
  aac_analysis_sbr_stream_t *paVar3;
  aac_analysis_scratch_t *paVar4;
  int iVar5;
  aac_analysis_window_t *paVar6;

  gp = &__global_pointer_;
  memset(core,0,0x8a84);
  core->channel[0].spectrum.coefficients = core->spectral[0].coefficients;
  core->channel[1].spectrum.coefficients = core->spectral[1].coefficients;
  core->channel[0].spectrum.shared = &core->spectral[0].shared;
  core->channel[1].spectrum.shared = &core->spectral[1].shared;
  core->mask = core->spectral[0].mask;
  paVar1 = (aac_analysis_program_t *)media_lib_module_calloc("AUD_Codec",1,0x35c);
  core->program = paVar1;
  if (paVar1 != (aac_analysis_program_t *)0x0) {
    paVar2 = (aac_analysis_window_t *)media_lib_module_calloc("AUD_Codec",1,0x2b8);
    core->long_window = paVar2;
    if (paVar2 != (aac_analysis_window_t *)0x0) {
      paVar2 = (aac_analysis_window_t *)media_lib_module_calloc("AUD_Codec",1,0x2b8);
      core->short_window = paVar2;
      if (paVar2 != (aac_analysis_window_t *)0x0) {
        iVar5 = external->plus_enabled;
        core->plus_enabled = iVar5 != 0;
        core->requested_plus = iVar5 != 0;
        if (iVar5 != 0) {
          paVar3 = (aac_analysis_sbr_stream_t *)media_lib_module_calloc("AUD_Codec",1,0x414);
          core->sbr_stream = paVar3;
          if (paVar3 == (aac_analysis_sbr_stream_t *)0x0) {
            return 10;
          }
        }
        paVar4 = (aac_analysis_scratch_t *)media_lib_module_calloc("AUD_Codec",1,0x3000);
        core->workspace = (aac_analysis_workspace_t *)paVar4;
        if (paVar4 != (aac_analysis_scratch_t *)0x0) {
          core->scratch = paVar4;
          core->shared = (aac_analysis_shared_t *)(paVar4 + 1);
          core->program->file_is_adts = param_3;
          paVar6 = core->long_window;
          paVar2 = core->short_window;
          external->output_plus = (int16_t *)0x0;
          core->current_program = -1;
          core->window_map[0] = paVar6;
          core->window_map[1] = paVar6;
          core->window_map[3] = paVar6;
          core->window_map[2] = paVar2;
          core->frame_length = 0x400;
          (core->mc).sample_rate_index = 4;
          (core->mc).implicit_channels = 1;
          infoinit(4,core->window_map,core->short_band_width);
          paVar1 = core->program;
          external->bitrate = 0;
          external->encoded_channels = 0;
          iVar5 = paVar1->file_is_adts;
          external->sample_rate = 0;
          external->reposition = 1;
          external->consumed_bytes = 0;
          if ((iVar5 != 0) || (iVar5 = raw_stream_parameter_setup(param_4,param_5,core), iVar5 == 0)
             ) {
            gp = &__global_pointer_;
            return 0;
          }
        }
      }
    }
  }
  return 10;
}
