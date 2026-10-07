/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: decode_noise_floorlevels @ ram:430054e4
 * Types and parameter counts are inferred; verify against disassembly. */

void decode_noise_floorlevels(aac_sbr_frame_abi_t *frame)

{
  aac_analysis_inverse_filter_t *paVar1;
  int32_t *piVar2;
  int32_t *piVar3;
  int32_t *piVar4;
  int iVar5;
  int iVar6;
  int32_t iVar7;
  int32_t *piVar8;
  int32_t *piVar9;
  int32_t *piVar10;
  aac_sbr_frame_abi_t *paVar11;
  aac_sbr_frame_abi_t *paVar12;
  int iVar13;

  gp = &__global_pointer_;
  iVar5 = (frame->frame_control).frame_info[(frame->frame_control).frame_info[0] * 2 + 3];
  if (iVar5 < 1) {
    return;
  }
  iVar13 = (frame->frame_control).noise_band_count;
  piVar2 = (frame->frame_control).frame_info + iVar5 + -4;
  piVar8 = (frame->envelope_and_noise).noise_mantissa;
  paVar11 = frame;
LAB_ram_43005522:
  if ((paVar11->domain_and_inverse_filter).noise_domain[0] != 0) {
    paVar12 = paVar11;
    if (0 < iVar13) goto LAB_ram_43005568;
    do {
      if (&(paVar12->frame_control).noise_factor_count == piVar2) {
        return;
      }
      if ((paVar12->domain_and_inverse_filter).noise_domain[1] == 0) {
        iVar7 = *piVar8;
        piVar8 = piVar8 + 1;
        frame->previous_noise[0] = iVar7;
      }
      if (piVar2 == &(paVar12->frame_control).crc_checksum) {
        return;
      }
      paVar11 = (aac_sbr_frame_abi_t *)&(paVar12->frame_control).crc_checksum;
      paVar1 = &paVar12->domain_and_inverse_filter;
      paVar12 = paVar11;
    } while (paVar1->noise_domain[2] != 0);
  }
  do {
    frame->previous_noise[0] = *piVar8;
    piVar3 = piVar8 + 1;
    piVar4 = piVar8;
    paVar12 = paVar11;
    while( true ) {
      piVar8 = piVar3;
      if (iVar13 < 2) {
        paVar11 = (aac_sbr_frame_abi_t *)&(paVar12->frame_control).noise_factor_count;
        if (paVar11 == (aac_sbr_frame_abi_t *)piVar2) {
          return;
        }
        goto LAB_ram_43005522;
      }
      piVar3 = frame->previous_noise;
      piVar9 = piVar8;
      do {
        piVar3 = piVar3 + 1;
        iVar5 = *piVar9;
        piVar10 = piVar9 + 1;
        *piVar9 = iVar5 + piVar9[-1];
        *piVar3 = iVar5 + piVar9[-1];
        piVar9 = piVar10;
      } while (piVar10 != piVar4 + iVar13);
      paVar11 = (aac_sbr_frame_abi_t *)&(paVar12->frame_control).noise_factor_count;
      if (paVar11 == (aac_sbr_frame_abi_t *)piVar2) {
        return;
      }
      piVar8 = piVar8 + iVar13 + -1;
      if ((paVar12->domain_and_inverse_filter).noise_domain[1] == 0) break;
LAB_ram_43005568:
      do {
        piVar3 = piVar8 + iVar13;
        piVar4 = frame->previous_noise;
        do {
          piVar9 = piVar8;
          iVar6 = *piVar9;
          iVar5 = *piVar4;
          piVar8 = piVar9 + 1;
          *piVar9 = iVar6 + iVar5;
          *piVar4 = iVar6 + iVar5;
          piVar4 = piVar4 + 1;
        } while (piVar8 != piVar3);
        paVar12 = (aac_sbr_frame_abi_t *)&(paVar11->frame_control).noise_factor_count;
        if ((aac_sbr_frame_abi_t *)piVar2 == paVar12) {
          return;
        }
        paVar1 = &paVar11->domain_and_inverse_filter;
        paVar11 = paVar12;
      } while (paVar1->noise_domain[1] != 0);
      frame->previous_noise[0] = *piVar8;
      piVar3 = piVar9 + 2;
      piVar4 = piVar8;
    }
  } while( true );
}
