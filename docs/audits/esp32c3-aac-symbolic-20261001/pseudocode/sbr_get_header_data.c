/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_get_header_data @ ram:43012ed2
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4 sbr_get_header_data(aac_sbr_header_abi_t *header,undefined4 param_2,int param_3)

{
  int32_t iVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  int32_t iVar5;
  int32_t iVar6;
  int32_t *piVar7;
  aac_sbr_header_abi_t *paVar8;
  int32_t local_60 [5];
  int iStack_4c;
  int iStack_48;
  int iStack_44;
  int iStack_40;
  int iStack_3c;
  int iStack_38;

  gp = &__global_pointer_;
  if (param_3 == 2) {
    piVar7 = local_60;
    paVar8 = header;
    do {
      iVar1 = paVar8->master_status;
      iVar5 = paVar8->crc_enabled;
      iVar6 = paVar8->sample_rate_mode;
      *piVar7 = paVar8->status;
      piVar7[1] = iVar1;
      piVar7[2] = iVar5;
      piVar7[3] = iVar6;
      paVar8 = (aac_sbr_header_abi_t *)&paVar8->amplitude_resolution;
      piVar7 = piVar7 + 4;
    } while (paVar8 != header + 1);
  }
  else {
    memset(local_60,0,0x40);
  }
  iVar1 = buf_getbits(param_2,1);
  header->amplitude_resolution = iVar1;
  iVar1 = buf_getbits(param_2,4);
  header->start_frequency = iVar1;
  iVar1 = buf_getbits(param_2,4);
  header->stop_frequency = iVar1;
  iVar1 = buf_getbits(param_2,3);
  header->crossover_band = iVar1;
  buf_getbits(param_2,2);
  iVar2 = buf_getbits(param_2,1);
  iVar3 = buf_getbits(param_2,1);
  if (iVar2 == 0) {
    iVar1 = 2;
    header->frequency_scale = 2;
    header->alter_scale = 1;
  }
  else {
    iVar1 = buf_getbits(param_2,2);
    header->frequency_scale = iVar1;
    iVar1 = buf_getbits(param_2,1);
    header->alter_scale = iVar1;
    iVar1 = buf_getbits(param_2,2);
  }
  header->noise_bands = iVar1;
  if (iVar3 == 0) {
    iVar1 = 1;
    header->limiter_bands = 2;
    header->limiter_gains = 2;
    header->interpolate_frequency = 1;
  }
  else {
    iVar1 = buf_getbits(param_2,2);
    header->limiter_bands = iVar1;
    iVar1 = buf_getbits(param_2,2);
    header->limiter_gains = iVar1;
    iVar1 = buf_getbits(param_2,1);
    header->interpolate_frequency = iVar1;
    iVar1 = buf_getbits(param_2,1);
  }
  header->smoothing_mode = iVar1;
  if ((((param_3 != 2) || (header->status = 0, iStack_4c != header->start_frequency)) ||
      (iStack_48 != header->stop_frequency)) ||
     (((iStack_44 != header->crossover_band || (iStack_40 != header->frequency_scale)) ||
      ((iStack_3c != header->alter_scale || (uVar4 = 0, iStack_38 != header->noise_bands)))))) {
    uVar4 = 1;
    header->status = 1;
  }
  return uVar4;
}
