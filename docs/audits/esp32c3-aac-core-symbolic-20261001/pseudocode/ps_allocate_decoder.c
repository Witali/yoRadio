/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: ps_allocate_decoder @ ram:4300c22c
 * Types and parameter counts are inferred; verify against disassembly. */

void ps_allocate_decoder(aac_sbr_owner_abi_t *owner,uint param_2)

{
  int32_t *piVar1;
  int32_t *piVar2;
  int32_t **ppiVar3;
  int32_t *piVar4;
  int iVar5;
  int32_t *piVar6;
  int iVar7;
  int32_t (*paiVar8) [22];
  int32_t *piVar9;
  aac_ps_abi_t *paVar10;
  int32_t *piVar11;
  int32_t *piVar12;
  int32_t *piVar13;
  uint32_t *puVar14;
  int *piVar15;
  int32_t *local_40;
  int aiStack_3c [6];

  gp = &__global_pointer_;
  paVar10 = owner->ps;
  paVar10->samples = param_2;
  aiStack_3c[2] = 2;
  local_40 = owner->channel[1].frame.low_real[1] + 0x1c;
  aiStack_3c[1] = 2;
  paVar10->peak = owner->channel[1].frame.low_real[0];
  paVar10->previous_energy = owner->channel[1].frame.low_real[0] + 0x14;
  paVar10->previous_peak_difference = owner->channel[1].frame.low_real[1] + 8;
  paVar10->inverse_samples = 0x40000000 / param_2;
  aiStack_3c[0] = 8;
  ps_hybrid_filter_bank_allocation(&paVar10->hybrid,3,aiStack_3c,&local_40);
  paVar10->hybrid_left_imag = local_40 + 10;
  paVar10->hybrid_right_real = local_40 + 0x14;
  paVar10->hybrid_right_imag = local_40 + 0x1e;
  piVar12 = owner->channel[1].frame.low_imag[4] + 0x12;
  piVar11 = owner->channel[1].frame.low_imag[6] + 0x12;
  paVar10->delay_index = 0;
  piVar6 = paVar10->delay_length;
  paVar10->hybrid_left_real = local_40;
  ppiVar3 = (int32_t **)(local_40 + 0x28);
  iVar5 = 0;
  while( true ) {
    for (; iVar5 < 0xc; iVar5 = iVar5 + 1) {
      *piVar6 = 0xe;
      piVar6 = piVar6 + 1;
    }
    *piVar6 = 1;
    iVar5 = iVar5 + 1;
    if (iVar5 == 0x29) break;
    piVar6 = piVar6 + 1;
  }
  paVar10->sub_delay_imag = (int32_t **)(local_40 + 0x32);
  paVar10->delay_real = (int32_t **)(owner->channel[1].frame.low_imag[10] + 0x12);
  paVar10->delay_imag = (int32_t **)(owner->channel[1].frame.low_imag[0x10] + 0x12);
  piVar6 = owner->channel[1].frame.low_imag[10] + 0x12;
  paVar10->sub_delay_real = ppiVar3;
  local_40 = local_40 + 0x3c;
  iVar5 = 0;
  while( true ) {
    while( true ) {
      for (; iVar5 < 0x14; iVar5 = iVar5 + 1) {
        *piVar6 = (int32_t)piVar12;
        piVar6[0xc0] = (int32_t)piVar11;
        piVar6 = piVar6 + 1;
        piVar11 = piVar11 + 2;
        piVar12 = piVar12 + 2;
      }
      *piVar6 = (int32_t)local_40;
      if (0x1f < iVar5) break;
      piVar6[0xc0] = (int32_t)(local_40 + 0xe);
      iVar5 = iVar5 + 1;
      piVar6 = piVar6 + 1;
      local_40 = local_40 + 0x1c;
    }
    piVar6[0xc0] = (int32_t)(local_40 + 1);
    iVar5 = iVar5 + 1;
    if (iVar5 == 0x3d) break;
    piVar6 = piVar6 + 1;
    local_40 = local_40 + 2;
  }
  piVar6 = local_40 + 2;
  do {
    *ppiVar3 = piVar6;
    ppiVar3[10] = piVar6 + 2;
    piVar6 = piVar6 + 4;
    ppiVar3 = ppiVar3 + 1;
  } while (piVar6 != local_40 + 0x2a);
  piVar15 = &aRevLinkDelaySer;
  puVar14 = paVar10->serial_index;
  piVar6 = owner->channel[1].frame.low_real[0x24] + 10;
  piVar12 = owner->channel[1].frame.low_real[0x14] + 0x12;
  do {
    *puVar14 = 0;
    iVar5 = *piVar15;
    puVar14[3] = (uint32_t)piVar12;
    puVar14[9] = (uint32_t)piVar6;
    piVar9 = piVar12 + iVar5;
    piVar1 = piVar6 + iVar5;
    puVar14[6] = (uint32_t)piVar9;
    puVar14[0xc] = (uint32_t)piVar1;
    piVar13 = piVar9 + iVar5;
    piVar11 = piVar1 + iVar5;
    if (0 < iVar5) {
      iVar7 = 0;
      piVar2 = piVar11;
      piVar4 = piVar13;
      do {
        *(int32_t **)((int)piVar12 + iVar7) = piVar4;
        *(int32_t **)((int)piVar9 + iVar7) = piVar4 + 0x14;
        *(int32_t **)((int)piVar6 + iVar7) = piVar2;
        *(int32_t **)((int)piVar1 + iVar7) = piVar2 + 10;
        iVar7 = iVar7 + 4;
        piVar4 = piVar4 + 0x28;
        piVar2 = piVar2 + 0x14;
      } while (iVar5 * 4 != iVar7);
      piVar11 = piVar11 + iVar5 * 0x14;
      piVar13 = piVar13 + iVar5 * 0x28;
    }
    puVar14 = puVar14 + 1;
    piVar15 = piVar15 + 1;
    piVar6 = piVar11;
    piVar12 = piVar13;
  } while (paVar10->serial_real != (int32_t ***)puVar14);
  paiVar8 = paVar10->previous_mix;
  do {
    (*paiVar8)[0] = 0x40000000;
    paiVar8[1][0] = 0x40000000;
    paiVar8 = (int32_t (*) [22])(*paiVar8 + 1);
  } while (paiVar8 != paVar10->previous_mix + 1);
  return;
}
