/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_reset_dec @ ram:4301376a
 * Types and parameter counts are inferred; verify against disassembly. */

/* WARNING: Type propagation algorithm not settling */

int sbr_reset_dec(aac_sbr_frame_abi_t *frame,aac_sbr_control_abi_t *control,int param_3)

{
  int32_t iVar1;
  int iVar2;
  int32_t iVar3;
  int32_t iVar4;
  int iVar5;
  int32_t (*paiVar6) [59];
  int32_t *piVar7;
  aac_analysis_frequency_control_t *paVar8;
  aac_analysis_frequency_control_t *paVar9;
  aac_sbr_control_abi_t *paVar10;
  int32_t *piVar11;
  uint uVar12;
  undefined4 uStack_28;
  int aiStack_24 [3];

  gp = &__global_pointer_;
  iVar3 = (frame->header).start_frequency;
  iVar4 = (frame->header).stop_frequency;
  iVar1 = control->output_rate;
  (frame->frame_control).reset = 1;
  iVar2 = sbr_find_start_andstop_band(iVar1,iVar3,iVar4,&uStack_28,aiStack_24);
  if (iVar2 != 0) {
    return iVar2;
  }
  if ((frame->header).master_status == 1) {
    sbr_update_freq_scale
              ((control->remaining).master_bands,&(control->remaining).master_band_count,uStack_28,
               aiStack_24[0],(frame->header).frequency_scale,(frame->header).alter_scale,0);
  }
  iVar5 = (frame->header).crossover_band;
  iVar2 = (control->remaining).master_band_count;
  uVar12 = iVar2 - iVar5;
  (control->remaining).band_count[1] = uVar12;
  if (iVar5 <= iVar2) {
    memcpy((control->remaining).frequency_bands + 1,(control->remaining).master_bands + iVar5,
           ((iVar2 + 1) - iVar5) * 4);
  }
  if ((uVar12 & 1) == 0) {
    iVar1 = (int)uVar12 >> 1;
    (control->remaining).band_count[0] = iVar1;
    if (-1 < iVar1) {
      paiVar6 = (control->remaining).frequency_bands + 1;
      paVar8 = &control->remaining;
      do {
        piVar7 = *paiVar6;
        paVar9 = (aac_analysis_frequency_control_t *)(paVar8->frequency_bands[0] + 1);
        paiVar6 = (int32_t (*) [59])(*paiVar6 + 2);
        paVar8->frequency_bands[0][0] = *piVar7;
        paVar8 = paVar9;
      } while ((aac_analysis_frequency_control_t *)
               ((control->remaining).frequency_bands[0] + iVar1 + 1) != paVar9);
    }
    iVar2 = (control->remaining).frequency_bands[0][0];
  }
  else {
    iVar2 = (control->remaining).frequency_bands[1][0];
    iVar1 = (int)(uVar12 + 1) >> 1;
    (control->remaining).band_count[0] = iVar1;
    (control->remaining).frequency_bands[0][0] = iVar2;
    if (0 < iVar1) {
      piVar7 = (control->remaining).frequency_bands[1] + 1;
      paVar10 = control;
      do {
        iVar3 = *piVar7;
        piVar11 = &paVar10->low_complexity;
        piVar7 = piVar7 + 2;
        (paVar10->remaining).frequency_bands[0][1] = iVar3;
        paVar10 = (aac_sbr_control_abi_t *)piVar11;
      } while (piVar11 != (int32_t *)((int)control + (uVar12 + 1) * 2));
    }
  }
  aiStack_24[0] = (control->remaining).frequency_bands[0][iVar1];
  control->low_subband = iVar2;
  control->high_subband = aiStack_24[0];
  control->subband_count = aiStack_24[0] - iVar2;
  if ((aiStack_24[0] - iVar2 < 1) || (0x20 < iVar2)) {
LAB_ram_430138ec:
    iVar2 = 6;
  }
  else {
    if ((frame->header).noise_bands == 0) {
LAB_ram_4301385e:
      iVar3 = 1;
      (control->remaining).noise_band_count = 1;
    }
    else {
      if (iVar2 == 0) goto LAB_ram_430138ec;
      iVar2 = pv_log2((aiStack_24[0] << 0x14) / iVar2);
      iVar5 = (frame->header).noise_bands;
      iVar1 = (control->remaining).band_count[0];
      iVar3 = (int)(((uint)(iVar2 * iVar5) >> 0xf) +
                    (int)((ulonglong)((longlong)iVar2 * (longlong)iVar5) >> 0x20) * 0x20000 + 0x10)
              >> 5;
      (control->remaining).noise_band_count = iVar3;
      if (iVar3 == 0) goto LAB_ram_4301385e;
    }
    (frame->header).noise_band_count = iVar3;
    sbr_downsample_lo_res((control->remaining).noise_bands,iVar3,&control->remaining,iVar1);
    iVar2 = control->low_subband;
    if (param_3 << 5 < control->low_subband) {
      iVar2 = param_3 << 5;
    }
    iVar5 = (control->remaining).band_count[0];
    control->stop_codec = iVar2;
    iVar2 = (control->remaining).band_count[1];
    iVar1 = (frame->header).noise_band_count;
    (frame->frame_control).band_count[0] = iVar5;
    (frame->frame_control).offset = iVar5 * 2 - iVar2;
    (frame->frame_control).band_count[1] = iVar2;
    (frame->frame_control).noise_band_count = iVar1;
    iVar2 = 0;
  }
  return iVar2;
}
