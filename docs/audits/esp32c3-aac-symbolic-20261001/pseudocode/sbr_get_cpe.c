/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_get_cpe @ ram:43012a10
 * Types and parameter counts are inferred; verify against disassembly. */

int sbr_get_cpe(aac_sbr_frame_abi_t *left,aac_sbr_frame_abi_t *right,undefined4 param_3)

{
  int32_t *piVar1;
  int32_t *piVar2;
  int32_t *piVar3;
  int iVar4;
  int32_t iVar5;
  int32_t iVar6;
  int32_t iVar7;
  int iVar8;
  int iVar9;

  gp = &__global_pointer_;
  iVar4 = buf_getbits(param_3,1);
  if (iVar4 != 0) {
    buf_getbits(param_3,4);
    buf_getbits(param_3,4);
  }
  iVar4 = buf_getbits(param_3,1);
  iVar5 = 0;
  if (iVar4 != 0) {
    iVar5 = 2;
  }
  left->coupling = (uint)(iVar4 != 0);
  right->coupling = iVar5;
  iVar4 = extractFrameInfo(param_3,left);
  if (iVar4 == 0) {
    if (left->coupling == 0) {
      iVar9 = extractFrameInfo(param_3,right);
      if (iVar9 != 0) {
        return iVar9;
      }
      sbr_get_dir_control_data(left,param_3);
      sbr_get_dir_control_data(right,param_3);
      if (0 < (left->frame_control).noise_band_count) {
        piVar3 = (left->domain_and_inverse_filter).inverse_filter_mode;
        iVar9 = 0;
        do {
          piVar3[10] = *piVar3;
          iVar5 = buf_getbits(param_3,2);
          iVar8 = (left->frame_control).noise_band_count;
          iVar9 = iVar9 + 1;
          *piVar3 = iVar5;
          piVar3 = piVar3 + 1;
        } while (iVar9 < iVar8);
      }
      if (0 < (right->frame_control).noise_band_count) {
        piVar3 = (right->domain_and_inverse_filter).inverse_filter_mode;
        iVar9 = 0;
        do {
          piVar3[10] = *piVar3;
          iVar5 = buf_getbits(param_3,2);
          iVar8 = (right->frame_control).noise_band_count;
          iVar9 = iVar9 + 1;
          *piVar3 = iVar5;
          piVar3 = piVar3 + 1;
        } while (iVar9 < iVar8);
      }
      sbr_get_envelope(left,param_3);
      sbr_get_envelope(right,param_3);
      sbr_get_noise_floor_data(left,param_3);
    }
    else {
      piVar2 = (left->frame_control).frame_info;
      piVar3 = (right->frame_control).frame_info;
      do {
        iVar7 = piVar2[3];
        iVar5 = piVar2[1];
        iVar6 = piVar2[2];
        *piVar3 = *piVar2;
        piVar3[1] = iVar5;
        piVar3[2] = iVar6;
        piVar3[3] = iVar7;
        piVar1 = piVar2 + 4;
        piVar2 = piVar2 + 5;
        piVar3[4] = *piVar1;
        piVar3 = piVar3 + 5;
      } while (piVar2 != (left->frame_control).band_count);
      iVar5 = (left->frame_control).noise_envelope_count;
      (right->frame_control).frame_class = (left->frame_control).frame_class;
      (right->frame_control).noise_envelope_count = iVar5;
      sbr_get_dir_control_data(left,param_3);
      sbr_get_dir_control_data(right,param_3);
      if (0 < (left->frame_control).noise_band_count) {
        piVar2 = (right->domain_and_inverse_filter).inverse_filter_mode;
        iVar9 = 0;
        piVar3 = (left->domain_and_inverse_filter).inverse_filter_mode;
        do {
          piVar3[10] = *piVar3;
          iVar9 = iVar9 + 1;
          piVar2[10] = *piVar2;
          iVar5 = buf_getbits(param_3,2);
          iVar8 = (left->frame_control).noise_band_count;
          *piVar3 = iVar5;
          *piVar2 = iVar5;
          piVar2 = piVar2 + 1;
          piVar3 = piVar3 + 1;
        } while (iVar9 < iVar8);
      }
      sbr_get_envelope(left,param_3);
      sbr_get_noise_floor_data(left,param_3);
      sbr_get_envelope(right,param_3);
    }
    sbr_get_noise_floor_data(right,param_3);
    memset(&left->harmonics_and_envelopes,0,(left->frame_control).band_count[1] << 2);
    memset(&right->harmonics_and_envelopes,0,(right->frame_control).band_count[1] << 2);
    sbr_get_additional_data(left,param_3);
    sbr_get_additional_data(right,param_3);
    sbr_extract_extended_data(param_3,(aac_ps_abi_t *)0x0);
  }
  return iVar4;
}
