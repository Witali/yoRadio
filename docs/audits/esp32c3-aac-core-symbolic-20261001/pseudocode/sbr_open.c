/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_open @ ram:430134a8
 * Types and parameter counts are inferred; verify against disassembly. */

void sbr_open(int param_1,aac_sbr_control_abi_t *control,aac_sbr_owner_abi_t *owner,int param_4)

{
  aac_sbr_owner_abi_t *paVar1;
  int32_t iVar2;
  int32_t iVar3;
  int32_t iVar4;
  aac_sbr_header_abi_t *paVar5;
  int32_t *piVar6;

  gp = &__global_pointer_;
  paVar1 = owner;
  do {
    memset(paVar1,0,0x64c0);
    piVar6 = &defaultHeader;
    paVar5 = &paVar1->channel[0].frame.header;
    do {
      iVar2 = piVar6[1];
      iVar3 = piVar6[2];
      iVar4 = ((aac_analysis_sample_rate_t *)(piVar6 + 3))->rate;
      paVar5->status = *piVar6;
      paVar5->master_status = iVar2;
      paVar5->crc_enabled = iVar3;
      paVar5->sample_rate_mode = iVar4;
      piVar6 = piVar6 + 4;
      paVar5 = (aac_sbr_header_abi_t *)&paVar5->amplitude_resolution;
    } while ((aac_analysis_sample_rates_t *)piVar6 != &samp_rate_info);
    if (param_4 != 0 || 24000 < param_1) {
      paVar1->channel[0].frame.header.sample_rate_mode = 1;
    }
    iVar2 = init_sbr_dec(param_1,owner->channel[0].frame.header.sample_rate_mode,control,
                         &paVar1->channel[0].frame);
    paVar1->channel[0].frame_size = iVar2;
    paVar1->channel[0].sync_state = 1;
    paVar1->channel[0].frame.startup = 1;
    paVar1 = (aac_sbr_owner_abi_t *)(paVar1->channel + 1);
  } while (paVar1 != (aac_sbr_owner_abi_t *)&owner->initialize_ps);
  return;
}
