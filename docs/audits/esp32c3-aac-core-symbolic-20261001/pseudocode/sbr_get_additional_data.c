/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_get_additional_data @ ram:430129bc
 * Types and parameter counts are inferred; verify against disassembly. */

void sbr_get_additional_data(aac_sbr_frame_abi_t *frame,aac_analysis_sbr_bits_t *bits)

{
  aac_analysis_harmonics_t *paVar1;
  int iVar2;
  int32_t iVar3;

  gp = &__global_pointer_;
  iVar2 = buf_getbits(bits,1);
  if ((iVar2 != 0) && (0 < (frame->frame_control).band_count[1])) {
    iVar2 = 0;
    paVar1 = &frame->harmonics_and_envelopes;
    do {
      iVar3 = buf_getbits(bits,1);
      paVar1->add_harmonics[0] = iVar3;
      iVar2 = iVar2 + 1;
      paVar1 = (aac_analysis_harmonics_t *)(paVar1->add_harmonics + 1);
    } while (iVar2 < (frame->frame_control).band_count[1]);
  }
  return;
}
