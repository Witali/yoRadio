/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: raw_stream_parameter_setup @ ram:4300f4e4
 * Types and parameter counts are inferred; verify against disassembly. */

void raw_stream_parameter_setup(int param_1,int param_2,aac_analysis_core_t *core)

{
  int iVar1;
  aac_analysis_program_t *paVar2;

  gp = &__global_pointer_;
  paVar2 = core->program;
  iVar1 = param_2 - (uint)(param_2 != 0);
  paVar2->sample_rate_index = param_1;
  paVar2->profile = 1;
  (paVar2->front).count = 1;
  (paVar2->front).is_pair[0] = iVar1;
  paVar2->crc_absent = 0;
  (paVar2->front).tag[0] = 0;
  (paVar2->mono).present = 0;
  (paVar2->stereo).present = 0;
  (paVar2->matrix).present = 0;
  set_mc_info(&core->mc,param_1,0,iVar1,core->window_map,core->short_band_width);
  paVar2 = core->program;
  paVar2->frame_length = 0;
  paVar2->headerless_frames = 0;
  return;
}
