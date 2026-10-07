/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_requantize_envelope_data @ ram:430136e2
 * Types and parameter counts are inferred; verify against disassembly. */

void sbr_requantize_envelope_data(aac_sbr_frame_abi_t *frame)

{
  int32_t *piVar1;
  int32_t *piVar2;
  int32_t *piVar3;
  int32_t iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  aac_analysis_envelope_t *paVar8;

  gp = &__global_pointer_;
  iVar6 = (frame->frame_control).scale_factor_count;
  iVar5 = (frame->frame_control).noise_factor_count;
  if ((frame->frame_control).amplitude_resolution == 0) {
    paVar8 = &frame->envelope_and_noise;
    piVar2 = paVar8->envelope_mantissa;
    if (0 < iVar6) {
      do {
        iVar4 = 0x40000000;
        paVar8->envelope_exponent[0] = (paVar8->envelope_mantissa[0] >> 1) + 6;
        if ((paVar8->envelope_mantissa[0] & 1U) != 0) {
          iVar4 = 0x5a827980;
        }
        paVar8->envelope_mantissa[0] = iVar4;
        paVar8 = (aac_analysis_envelope_t *)(paVar8->envelope_mantissa + 1);
      } while (paVar8 != (aac_analysis_envelope_t *)(piVar2 + iVar6));
    }
  }
  else if (0 < iVar6) {
    paVar8 = &frame->envelope_and_noise;
    do {
      iVar7 = paVar8->envelope_mantissa[0];
      paVar8->envelope_mantissa[0] = 0x40000000;
      piVar2 = paVar8->envelope_mantissa;
      paVar8->envelope_exponent[0] = iVar7 + 6;
      paVar8 = (aac_analysis_envelope_t *)(piVar2 + 1);
    } while ((aac_analysis_envelope_t *)(piVar2 + 1) !=
             (aac_analysis_envelope_t *)((frame->envelope_and_noise).envelope_mantissa + iVar6));
  }
  if (0 < iVar5) {
    piVar1 = (frame->envelope_and_noise).noise_mantissa;
    piVar2 = piVar1;
    do {
      iVar6 = *piVar2;
      *piVar2 = 0x40000000;
      piVar3 = piVar2 + 1;
      piVar2[10] = 6 - iVar6;
      piVar2 = piVar3;
    } while (piVar1 + iVar5 != piVar3);
  }
  return;
}
