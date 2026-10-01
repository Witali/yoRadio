/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_get_sce @ ram:43013180
 * Types and parameter counts are inferred; verify against disassembly. */

int sbr_get_sce(aac_sbr_frame_abi_t *frame,aac_analysis_sbr_bits_t *bits,aac_ps_abi_t *ps)

{
  int32_t *piVar1;
  int iVar2;
  int32_t iVar3;
  int iVar4;

  gp = &__global_pointer_;
  iVar2 = buf_getbits(bits,1);
  if (iVar2 != 0) {
    buf_getbits(bits,4);
  }
  iVar2 = extractFrameInfo(bits,frame);
  if (iVar2 == 0) {
    sbr_get_dir_control_data(frame,bits);
    if (0 < (frame->frame_control).noise_band_count) {
      piVar1 = (frame->domain_and_inverse_filter).inverse_filter_mode;
      iVar2 = 0;
      do {
        piVar1[10] = *piVar1;
        iVar3 = buf_getbits(bits,2);
        iVar4 = (frame->frame_control).noise_band_count;
        iVar2 = iVar2 + 1;
        *piVar1 = iVar3;
        piVar1 = piVar1 + 1;
      } while (iVar2 < iVar4);
    }
    sbr_get_envelope(frame,bits);
    sbr_get_noise_floor_data(frame,bits);
    memset(&frame->harmonics_and_envelopes,0,(frame->frame_control).band_count[1] << 2);
    sbr_get_additional_data(frame,bits);
    sbr_extract_extended_data(bits,ps);
    frame->coupling = 0;
    return 0;
  }
  return iVar2;
}
