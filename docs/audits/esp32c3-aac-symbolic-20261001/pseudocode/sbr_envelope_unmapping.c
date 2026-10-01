/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_envelope_unmapping @ ram:430117e8
 * Types and parameter counts are inferred; verify against disassembly. */

void sbr_envelope_unmapping(aac_sbr_frame_abi_t *left,aac_sbr_frame_abi_t *right)

{
  aac_analysis_envelope_t *paVar1;
  int32_t *piVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int32_t *piVar7;
  int iVar8;
  int32_t iVar9;

  gp = &__global_pointer_;
  iVar6 = (left->frame_control).scale_factor_count;
  if ((right->frame_control).amplitude_resolution == 0) {
    if (0 < iVar6) {
      piVar2 = (right->envelope_and_noise).envelope_exponent;
      piVar7 = (left->envelope_and_noise).envelope_exponent;
      iVar6 = 0;
      do {
        uVar4 = ((aac_analysis_envelope_t *)(piVar7 + -0x122))->envelope_mantissa[0];
        uVar3 = ((aac_analysis_envelope_t *)(piVar2 + -0x122))->envelope_mantissa[0];
        iVar9 = 0x40000000;
        *piVar7 = ((int)uVar4 >> 1) + 7;
        if ((uVar4 & 1) != 0) {
          iVar9 = 0x5a827980;
        }
        iVar8 = (int)uVar3 >> 1;
        ((aac_analysis_envelope_t *)(piVar7 + -0x122))->envelope_mantissa[0] = iVar9;
        uVar4 = iVar8 - 0xc;
        *piVar2 = uVar4;
        if ((uVar3 & 1) == 0) {
          ((aac_analysis_envelope_t *)(piVar2 + -0x122))->envelope_mantissa[0] = 0x40000000;
          if ((int)uVar4 < 0) {
            if (-0xb < (int)uVar4) {
              iVar9 = 0x40000000 - *(int *)(InvFiltFactors + iVar8 * -4 + 4);
              goto LAB_ram_43011874;
            }
            *piVar2 = *piVar7;
            *piVar7 = 0;
          }
          else {
            if ((int)uVar4 < 0xb) {
              iVar9 = *(int32_t *)(one_over_one_plus_two_to_n + uVar4 * 4);
            }
            else {
              iVar9 = 0x40000000 - (0x40000000 >> (uVar4 & 0x1f));
            }
LAB_ram_43011874:
            ((aac_analysis_envelope_t *)(piVar2 + -0x122))->envelope_mantissa[0] = iVar9;
            *piVar2 = *piVar7 - uVar4;
          }
          iVar8 = ((aac_analysis_envelope_t *)(piVar7 + -0x122))->envelope_mantissa[0];
          iVar9 = ((aac_analysis_envelope_t *)(piVar2 + -0x122))->envelope_mantissa[0];
          if (iVar8 != 0x40000000) {
            iVar9 = ((uint)(iVar8 * iVar9) >> 0x1e) +
                    (int)((ulonglong)((longlong)iVar8 * (longlong)iVar9) >> 0x20) * 4;
            ((aac_analysis_envelope_t *)(piVar2 + -0x122))->envelope_mantissa[0] = iVar9;
          }
          ((aac_analysis_envelope_t *)(piVar7 + -0x122))->envelope_mantissa[0] = iVar9;
        }
        else if ((int)uVar4 < 0) {
          if ((int)uVar4 < -0xb) {
            ((aac_analysis_envelope_t *)(piVar2 + -0x122))->envelope_mantissa[0] = 0x40000000;
            *piVar2 = 0;
            uVar4 = 0;
            goto LAB_ram_430119e6;
          }
          ((aac_analysis_envelope_t *)(piVar2 + -0x122))->envelope_mantissa[0] =
               0x40000000 - *(int *)(one_over_one_plus_two_to_n + iVar8 * -4);
          iVar8 = ((aac_analysis_envelope_t *)(piVar2 + -0x122))->envelope_mantissa[0];
          *piVar2 = *piVar7 - uVar4;
          iVar5 = ((aac_analysis_envelope_t *)(piVar7 + -0x122))->envelope_mantissa[0];
          if (iVar5 == 0x40000000) goto LAB_ram_43011a4a;
LAB_ram_430119fc:
          ((aac_analysis_envelope_t *)(piVar2 + -0x122))->envelope_mantissa[0] =
               ((uint)(iVar5 * iVar8) >> 0x1e) +
               (int)((ulonglong)((longlong)iVar5 * (longlong)iVar8) >> 0x20) * 4;
          iVar5 = *piVar7;
          ((aac_analysis_envelope_t *)(piVar7 + -0x122))->envelope_mantissa[0] = iVar8;
          *piVar7 = iVar5 + 1;
        }
        else {
          if ((int)uVar4 < 0xc) {
            ((aac_analysis_envelope_t *)(piVar2 + -0x122))->envelope_mantissa[0] =
                 *(int32_t *)(one_over_one_plus_sq_2_by_two_to_n + uVar4 * 4);
          }
          else {
            ((aac_analysis_envelope_t *)(piVar2 + -0x122))->envelope_mantissa[0] =
                 0x40000000 - (0x40000000 >> (uVar4 & 0x1f));
          }
LAB_ram_430119e6:
          iVar8 = ((aac_analysis_envelope_t *)(piVar2 + -0x122))->envelope_mantissa[0];
          *piVar2 = *piVar7 - uVar4;
          iVar5 = ((aac_analysis_envelope_t *)(piVar7 + -0x122))->envelope_mantissa[0];
          if (iVar5 != 0x40000000) goto LAB_ram_430119fc;
LAB_ram_43011a4a:
          ((aac_analysis_envelope_t *)(piVar7 + -0x122))->envelope_mantissa[0] =
               ((uint)(iVar8 * 0x5a827980) >> 0x1e) +
               (int)((ulonglong)((longlong)iVar8 * 0x5a827980) >> 0x20) * 4;
        }
        iVar6 = iVar6 + 1;
        piVar2 = piVar2 + 1;
        piVar7 = piVar7 + 1;
      } while (iVar6 < (left->frame_control).scale_factor_count);
    }
  }
  else if (0 < iVar6) {
    piVar7 = (right->envelope_and_noise).envelope_exponent;
    piVar2 = (left->envelope_and_noise).envelope_exponent;
    iVar6 = 0;
    do {
      iVar8 = ((aac_analysis_envelope_t *)(piVar7 + -0x122))->envelope_mantissa[0];
      *piVar2 = ((aac_analysis_envelope_t *)(piVar2 + -0x122))->envelope_mantissa[0] + 7;
      uVar3 = iVar8 - 0xc;
      ((aac_analysis_envelope_t *)(piVar7 + -0x122))->envelope_mantissa[0] = 0x40000000;
      *piVar7 = uVar3;
      if ((int)uVar3 < 0) {
        if (-0xb < (int)uVar3) {
          iVar8 = *(int *)(one_over_one_plus_two_to_n + (0xc - iVar8) * 4);
LAB_ram_430119cc:
          iVar9 = 0x40000000 - iVar8;
          goto LAB_ram_43011984;
        }
        *piVar7 = *piVar2;
        *piVar2 = 0;
      }
      else {
        iVar8 = 0x40000000 >> (uVar3 & 0x1f);
        if (10 < (int)uVar3) goto LAB_ram_430119cc;
        iVar9 = *(int32_t *)(one_over_one_plus_two_to_n + uVar3 * 4);
LAB_ram_43011984:
        ((aac_analysis_envelope_t *)(piVar7 + -0x122))->envelope_mantissa[0] = iVar9;
        *piVar7 = *piVar2 - uVar3;
      }
      paVar1 = (aac_analysis_envelope_t *)(piVar7 + -0x122);
      iVar6 = iVar6 + 1;
      piVar7 = piVar7 + 1;
      ((aac_analysis_envelope_t *)(piVar2 + -0x122))->envelope_mantissa[0] =
           paVar1->envelope_mantissa[0];
      piVar2 = piVar2 + 1;
    } while (iVar6 < (left->frame_control).scale_factor_count);
  }
  if ((left->frame_control).noise_factor_count < 1) {
    return;
  }
  piVar2 = (right->envelope_and_noise).noise_mantissa;
  piVar7 = (left->envelope_and_noise).noise_mantissa;
  iVar6 = 0;
  do {
    piVar7[10] = 7 - *piVar7;
    uVar3 = *piVar2 - 0xc;
    piVar2[10] = uVar3;
    if ((int)uVar3 < 0) {
      if ((int)uVar3 < -10) {
        *piVar2 = 0x40000000;
        piVar2[10] = 0;
        uVar3 = 0;
      }
      else {
        iVar8 = *(int *)(one_over_one_plus_two_to_n + (0xc - *piVar2) * 4);
LAB_ram_43011934:
        *piVar2 = 0x40000000 - iVar8;
      }
    }
    else {
      iVar8 = 0x40000000 >> (uVar3 & 0x1f);
      if (10 < (int)uVar3) goto LAB_ram_43011934;
      *piVar2 = *(int32_t *)(one_over_one_plus_two_to_n + uVar3 * 4);
    }
    iVar6 = iVar6 + 1;
    piVar2[10] = piVar7[10] - uVar3;
    *piVar7 = *piVar2;
    piVar7 = piVar7 + 1;
    piVar2 = piVar2 + 1;
    if ((left->frame_control).noise_factor_count <= iVar6) {
      return;
    }
  } while( true );
}
