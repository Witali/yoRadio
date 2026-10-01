/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: init_sbr_dec @ ram:4300a376
 * Types and parameter counts are inferred; verify against disassembly. */

int init_sbr_dec(int param_1,int param_2,aac_sbr_control_abi_t *control,aac_sbr_frame_abi_t *frame)

{
  int32_t (*paiVar1) [64];
  aac_sbr_frame_abi_t *paVar2;
  int32_t iVar3;

  gp = &__global_pointer_;
  iVar3 = (frame->header).noise_band_count;
  control->output_rate = param_1 << 1;
  control->stop_codec = param_2 << 5;
  control->previous_low_subband = param_2 << 5;
  (frame->frame_control).noise_band_count = iVar3;
  (frame->frame_control).band_count[0] = 0;
  (frame->frame_control).band_count[1] = 0;
  (frame->frame_control).offset = 0;
  (frame->frame_control).previous_short_envelope = -1;
  paiVar1 = frame->gain_mantissa;
  paVar2 = frame + 1;
  do {
    (paVar2->frame_control).scale_factor_count = (int32_t)paiVar1;
    (paVar2->domain_and_inverse_filter).envelope_domain[0] = (int32_t)(paiVar1 + 10);
    (paVar2->harmonics_and_envelopes).add_harmonics[0x61] = (int32_t)(paiVar1 + 0xf);
    (paVar2->harmonics_and_envelopes).add_harmonics[0x21] = (int32_t)(paiVar1 + 5);
    paVar2 = (aac_sbr_frame_abi_t *)&(paVar2->frame_control).noise_factor_count;
    paiVar1 = paiVar1 + 1;
  } while (paVar2 != (aac_sbr_frame_abi_t *)(frame[1].frame_control.frame_info + 1));
  (frame->domain_and_inverse_filter).previous_inverse_filter_mode[0] = 0;
  (frame->domain_and_inverse_filter).previous_inverse_filter_mode[1] = 0;
  (frame->domain_and_inverse_filter).previous_inverse_filter_mode[2] = 0;
  (frame->domain_and_inverse_filter).previous_inverse_filter_mode[3] = 0;
  (frame->domain_and_inverse_filter).previous_inverse_filter_mode[4] = 0;
  (frame->domain_and_inverse_filter).previous_inverse_filter_mode[5] = 0;
  (frame->domain_and_inverse_filter).previous_inverse_filter_mode[6] = 0;
  (frame->domain_and_inverse_filter).previous_inverse_filter_mode[7] = 0;
  (frame->domain_and_inverse_filter).previous_inverse_filter_mode[8] = 0;
  (frame->domain_and_inverse_filter).previous_inverse_filter_mode[9] = 0;
  control->start_index = 0;
  control->columns = 0x20;
  control->low_subband = 0x20;
  control->write_offset = 8;
  control->read_offset = 2;
  control->qmf_buffer_length = 0x28;
  control->low_band_samples = 0x120;
  return param_2 << 10;
}
