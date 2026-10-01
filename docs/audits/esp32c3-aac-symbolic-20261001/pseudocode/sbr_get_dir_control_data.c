/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_get_dir_control_data @ ram:43012c68
 * Types and parameter counts are inferred; verify against disassembly. */

void sbr_get_dir_control_data(aac_sbr_frame_abi_t *frame,undefined4 param_2)

{
  aac_analysis_inverse_filter_t *paVar1;
  int32_t *piVar2;
  int32_t iVar3;
  int iVar4;

  gp = &__global_pointer_;
  iVar4 = (frame->frame_control).frame_info[0];
  if (iVar4 < 2) {
    (frame->frame_control).noise_envelope_count = 1;
    if (iVar4 != 1) goto LAB_ram_43012cae;
  }
  else {
    (frame->frame_control).noise_envelope_count = 2;
  }
  paVar1 = &frame->domain_and_inverse_filter;
  iVar4 = 0;
  do {
    iVar3 = buf_getbits(param_2,1);
    paVar1->envelope_domain[0] = iVar3;
    iVar4 = iVar4 + 1;
    paVar1 = (aac_analysis_inverse_filter_t *)(paVar1->envelope_domain + 1);
  } while (iVar4 < (frame->frame_control).frame_info[0]);
  if ((frame->frame_control).noise_envelope_count < 1) {
    return;
  }
LAB_ram_43012cae:
  piVar2 = (frame->domain_and_inverse_filter).noise_domain;
  iVar4 = 0;
  do {
    iVar3 = buf_getbits(param_2,1);
    *piVar2 = iVar3;
    iVar4 = iVar4 + 1;
    piVar2 = piVar2 + 1;
  } while (iVar4 < (frame->frame_control).noise_envelope_count);
  return;
}
