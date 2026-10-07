/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_get_noise_floor_data @ ram:43013052
 * Types and parameter counts are inferred; verify against disassembly. */

void sbr_get_noise_floor_data(aac_sbr_frame_abi_t *frame,undefined4 param_2)

{
  int iVar1;
  int32_t iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  int32_t *piVar6;
  undefined1 *puVar7;
  undefined1 *puVar8;
  int iVar9;
  int32_t *piVar10;
  int iVar11;
  int32_t *piVar12;

  gp = &__global_pointer_;
  iVar4 = frame->coupling;
  iVar1 = (frame->frame_control).noise_band_count;
  if (iVar4 == 2) {
    puVar8 = bookSbrNoiseBalance11T;
    puVar7 = bookSbrEnvBalance11F;
  }
  else {
    puVar8 = bookSbrNoiseLevel11T;
    puVar7 = bookSbrEnvLevel11F;
  }
  uVar5 = (uint)(iVar4 == 2);
  iVar3 = (frame->frame_control).noise_envelope_count;
  (frame->frame_control).noise_factor_count =
       (frame->frame_control).frame_info[(frame->frame_control).frame_info[0] * 2 + 3] * iVar1;
  if (0 < iVar3) {
    piVar6 = (frame->envelope_and_noise).noise_mantissa;
    piVar10 = (frame->domain_and_inverse_filter).noise_domain;
    iVar9 = 0;
    do {
      if (*piVar10 == 0) {
        if (iVar4 == 2) {
          iVar3 = buf_getbits(param_2,5);
          iVar2 = iVar3 << 1;
        }
        else {
          iVar2 = buf_getbits();
        }
        *piVar6 = iVar2;
        piVar6[10] = 0;
        iVar3 = 1;
        piVar12 = piVar6;
        if (1 < iVar1) {
          do {
            iVar11 = sbr_decode_huff_cw(puVar7,param_2);
            piVar12[0xb] = 0;
            piVar12[1] = iVar11 << uVar5;
            iVar3 = iVar3 + 1;
            piVar12 = piVar12 + 1;
          } while (iVar1 != iVar3);
        }
LAB_ram_430130ec:
        iVar3 = (frame->frame_control).noise_envelope_count;
      }
      else {
        iVar11 = 0;
        piVar12 = piVar6;
        if (0 < iVar1) {
          do {
            iVar3 = sbr_decode_huff_cw(puVar8,param_2);
            piVar12[10] = 0;
            *piVar12 = iVar3 << uVar5;
            iVar11 = iVar11 + 1;
            piVar12 = piVar12 + 1;
          } while (iVar1 != iVar11);
          goto LAB_ram_430130ec;
        }
      }
      iVar9 = iVar9 + 1;
      piVar10 = piVar10 + 1;
      piVar6 = piVar6 + iVar1;
    } while (iVar9 < iVar3);
  }
  return;
}
