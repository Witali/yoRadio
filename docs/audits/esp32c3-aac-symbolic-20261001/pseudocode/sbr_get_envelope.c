/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_get_envelope @ ram:43012ce6
 * Types and parameter counts are inferred; verify against disassembly. */

void sbr_get_envelope(aac_sbr_frame_abi_t *frame,undefined4 param_2)

{
  int32_t *piVar1;
  int32_t iVar2;
  undefined1 *puVar3;
  int iVar4;
  int32_t *piVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  aac_analysis_inverse_filter_t *paVar10;
  int iVar11;
  undefined1 *puVar12;
  undefined1 *puVar13;
  int *piVar14;
  int iVar15;
  int *piVar16;
  undefined4 uStack_68;
  undefined4 uStack_64;
  int local_54 [8];

  gp = &__global_pointer_;
  iVar6 = frame->coupling;
  (frame->frame_control).scale_factor_count = 0;
  iVar9 = (frame->frame_control).frame_info[0];
  if (((frame->frame_control).frame_class == 0) && (iVar9 == 1)) {
    uStack_64 = 6;
    (frame->frame_control).amplitude_resolution = 0;
    uStack_68 = 7;
    iVar11 = 0;
  }
  else {
    iVar11 = (frame->header).amplitude_resolution;
    (frame->frame_control).amplitude_resolution = iVar11;
    if (iVar11 == 1) {
      uStack_64 = 5;
      uStack_68 = 6;
      if (iVar9 < 1) {
        return;
      }
    }
    else {
      if (iVar9 < 1) {
        return;
      }
      uStack_64 = 6;
      uStack_68 = 7;
    }
  }
  piVar14 = local_54;
  piVar5 = (frame->frame_control).frame_info + iVar9 + -4;
  iVar8 = 0;
  iVar4 = 0;
  piVar16 = piVar14;
  do {
    piVar1 = piVar5 + 6;
    iVar4 = iVar4 + 1;
    piVar5 = piVar5 + 1;
    iVar7 = (frame->frame_control).band_count[*piVar1];
    *piVar16 = iVar7;
    iVar8 = iVar8 + iVar7;
    piVar16 = piVar16 + 1;
  } while (iVar4 < iVar9);
  (frame->frame_control).scale_factor_count = iVar8;
  if (iVar6 == 2) {
    if (iVar11 == 0) {
      puVar12 = bookSbrEnvBalance10F;
      puVar13 = bookSbrEnvBalance10T;
      iVar9 = 1;
    }
    else {
      puVar12 = bookSbrEnvBalance11F;
      puVar13 = bookSbrEnvBalance11T;
      iVar9 = 1;
    }
  }
  else if (iVar11 == 0) {
    puVar12 = bookSbrEnvLevel10F;
    puVar13 = bookSbrEnvLevel10T;
    iVar9 = 0;
  }
  else {
    puVar12 = bookSbrEnvLevel11F;
    puVar13 = bookSbrEnvLevel11T;
    iVar9 = 0;
  }
  paVar10 = &frame->domain_and_inverse_filter;
  iVar11 = 0;
  iVar4 = 0;
  do {
    iVar8 = paVar10->envelope_domain[0];
    if (iVar8 == 0) {
      if (iVar6 == 2) {
        iVar8 = buf_getbits(param_2,uStack_64);
        (frame->envelope_and_noise).envelope_mantissa[iVar11] = iVar8 << iVar9;
        iVar8 = paVar10->envelope_domain[0];
      }
      else {
        iVar2 = buf_getbits(param_2,uStack_68);
        (frame->envelope_and_noise).envelope_mantissa[iVar11] = iVar2;
        iVar8 = paVar10->envelope_domain[0];
      }
    }
    iVar7 = *piVar14;
    iVar15 = 1 - iVar8;
    if (iVar15 < iVar7) {
      piVar16 = (int *)((int)frame + (iVar11 + iVar15) * 4 + 0x710);
      while( true ) {
        puVar3 = puVar12;
        if (iVar8 != 0) {
          puVar3 = puVar13;
        }
        iVar8 = sbr_decode_huff_cw(puVar3,param_2);
        *piVar16 = iVar8 << iVar9;
        iVar15 = iVar15 + 1;
        if (iVar15 == iVar7) break;
        iVar8 = paVar10->envelope_domain[0];
        piVar16 = piVar16 + 1;
      }
    }
    iVar4 = iVar4 + 1;
    iVar11 = iVar11 + iVar7;
    paVar10 = (aac_analysis_inverse_filter_t *)(paVar10->envelope_domain + 1);
    piVar14 = piVar14 + 1;
  } while (iVar4 < (frame->frame_control).frame_info[0]);
  return;
}
