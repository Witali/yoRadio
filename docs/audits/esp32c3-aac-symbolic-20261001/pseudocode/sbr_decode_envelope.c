/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_decode_envelope @ ram:43011572
 * Types and parameter counts are inferred; verify against disassembly. */

void sbr_decode_envelope(aac_sbr_frame_abi_t *frame)

{
  int iVar1;
  int32_t *piVar2;
  int32_t iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  aac_analysis_envelope_t *paVar7;
  aac_analysis_envelope_t *paVar8;
  int iVar9;
  aac_analysis_inverse_filter_t *paVar10;
  int iVar11;
  int32_t *piVar12;
  int32_t *piVar13;
  int32_t *piVar14;
  int iVar15;

  gp = &__global_pointer_;
  iVar6 = (frame->frame_control).frame_info[0];
  if (iVar6 < 1) {
    return;
  }
  iVar1 = (frame->frame_control).offset;
  piVar2 = (frame->envelope_and_noise).previous_energy;
  paVar7 = &frame->envelope_and_noise;
  paVar10 = &frame->domain_and_inverse_filter;
  iVar9 = 0;
  do {
    while( true ) {
      iVar11 = (frame->frame_control).frame_info[iVar9 + iVar6 + 2];
      iVar15 = (frame->frame_control).band_count[iVar11];
      if (paVar10->envelope_domain[0] != 0) break;
      if (iVar11 == 0) {
        mapLowResEnergyVal_part_0(paVar7->envelope_mantissa[0],piVar2,iVar1);
      }
      else {
        (frame->envelope_and_noise).previous_energy[0] = paVar7->envelope_mantissa[0];
      }
      paVar8 = (aac_analysis_envelope_t *)(paVar7->envelope_mantissa + 1);
      if (iVar15 < 2) goto LAB_ram_4301165e;
      piVar12 = (frame->envelope_and_noise).previous_energy + 1;
      iVar6 = 1;
      do {
        while( true ) {
          iVar4 = paVar8->envelope_mantissa[0] + *(int *)((int)(paVar8 + -1) + 0xa44);
          paVar8->envelope_mantissa[0] = iVar4;
          if (iVar11 == 0) break;
          *piVar12 = iVar4;
          iVar6 = iVar6 + 1;
          paVar8 = (aac_analysis_envelope_t *)(paVar8->envelope_mantissa + 1);
          piVar12 = piVar12 + 1;
          if (iVar15 == iVar6) goto LAB_ram_43011700;
        }
        iVar5 = iVar6 + 1;
        mapLowResEnergyVal_part_0(iVar4,piVar2,iVar1,iVar6);
        paVar8 = (aac_analysis_envelope_t *)(paVar8->envelope_mantissa + 1);
        piVar12 = piVar12 + 1;
        iVar6 = iVar5;
      } while (iVar15 != iVar5);
LAB_ram_43011700:
      iVar6 = (frame->frame_control).frame_info[0];
      iVar9 = iVar9 + 1;
      paVar7 = (aac_analysis_envelope_t *)(paVar7->envelope_mantissa + iVar15);
      paVar10 = (aac_analysis_inverse_filter_t *)(paVar10->envelope_domain + 1);
      if (iVar6 <= iVar9) {
        return;
      }
    }
    if (0 < iVar15) {
      piVar12 = piVar2 + -iVar1;
      piVar13 = piVar2;
      piVar14 = piVar2;
      iVar6 = 0;
      paVar8 = paVar7;
      do {
        while (iVar4 = paVar8->envelope_mantissa[0], iVar11 != 0) {
          iVar5 = *piVar13;
          iVar6 = iVar6 + 1;
          paVar8->envelope_mantissa[0] = iVar4 + iVar5;
          *piVar13 = iVar4 + iVar5;
          piVar14 = piVar14 + 3;
          piVar13 = piVar13 + 1;
          piVar12 = piVar12 + 2;
          paVar8 = (aac_analysis_envelope_t *)(paVar8->envelope_mantissa + 1);
          if (iVar15 == iVar6) goto LAB_ram_43011658;
        }
        if (iVar1 < 0) {
          if (-iVar1 <= iVar6) goto LAB_ram_43011688;
          iVar3 = iVar4 + *piVar14;
        }
        else if (iVar6 < iVar1) {
          iVar3 = iVar4 + *piVar13;
        }
        else {
LAB_ram_43011688:
          iVar3 = iVar4 + *piVar12;
        }
        paVar8->envelope_mantissa[0] = iVar3;
        iVar4 = iVar6 + 1;
        mapLowResEnergyVal_part_0(iVar3,piVar2,iVar1,iVar6);
        paVar8 = (aac_analysis_envelope_t *)(paVar8->envelope_mantissa + 1);
        piVar13 = piVar13 + 1;
        piVar14 = piVar14 + 3;
        piVar12 = piVar12 + 2;
        iVar6 = iVar4;
      } while (iVar15 != iVar4);
LAB_ram_43011658:
      paVar8 = (aac_analysis_envelope_t *)(paVar7->envelope_mantissa + iVar15);
LAB_ram_4301165e:
      iVar6 = (frame->frame_control).frame_info[0];
      paVar7 = paVar8;
    }
    iVar9 = iVar9 + 1;
    paVar10 = (aac_analysis_inverse_filter_t *)(paVar10->envelope_domain + 1);
    if (iVar6 <= iVar9) {
      return;
    }
  } while( true );
}
