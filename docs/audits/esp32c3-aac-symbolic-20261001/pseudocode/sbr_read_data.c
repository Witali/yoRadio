/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_read_data @ ram:4301356c
 * Types and parameter counts are inferred; verify against disassembly. */

int sbr_read_data(aac_sbr_owner_abi_t *owner,aac_sbr_control_abi_t *control,int param_3)

{
  int32_t *piVar1;
  aac_sbr_frame_abi_t *frame;
  int iVar2;
  int32_t iVar3;
  aac_sbr_header_abi_t *paVar4;
  aac_sbr_header_abi_t *paVar5;
  int32_t iVar6;
  int aiStack_34 [8];

  gp = &__global_pointer_;
  aiStack_34[4] = *(int *)(param_3 + 0x10) << 3;
  aiStack_34[0] = param_3 + 0x14;
  aiStack_34[2] = 0;
  aiStack_34[1] = 0;
  aiStack_34[3] = 0;
  buf_getbits(aiStack_34,4);
  if ((*(int *)(param_3 + 0xc) == 0xe) &&
     (iVar2 = sbr_crc_check(aiStack_34,*(int *)(param_3 + 0x10) * 8 + -0xe), iVar2 == 0)) {
    iVar2 = 0;
    goto LAB_ram_430135bc;
  }
  iVar2 = buf_getbits(aiStack_34,1);
  if (iVar2 == 0) {
    if (*(int *)(param_3 + 8) == 0) {
LAB_ram_43013680:
      if (owner->channel[0].sync_state != 2) {
        iVar2 = 0;
        goto LAB_ram_430135bc;
      }
LAB_ram_430136c8:
      iVar2 = sbr_get_sce(&owner->channel[0].frame,aiStack_34,owner->ps);
      goto LAB_ram_430135bc;
    }
    if (*(int *)(param_3 + 8) == 1) {
LAB_ram_4301365e:
      iVar2 = 0;
LAB_ram_43013660:
      if (owner->channel[0].sync_state == 2) {
        iVar2 = sbr_get_cpe(&owner->channel[0].frame,&owner->channel[1].frame,aiStack_34);
      }
      goto LAB_ram_430135bc;
    }
  }
  else {
    iVar2 = sbr_get_header_data(&owner->channel[0].frame.header,aiStack_34,
                                owner->channel[0].sync_state);
    if (*(int *)(param_3 + 8) == 0) {
      if (iVar2 != 1) goto LAB_ram_43013680;
      iVar2 = sbr_reset_dec(&owner->channel[0].frame,control,
                            owner->channel[0].frame.header.sample_rate_mode);
      if (iVar2 != 0) goto LAB_ram_430135bc;
      owner->channel[0].sync_state = 2;
      goto LAB_ram_430136c8;
    }
    if (*(int *)(param_3 + 8) == 1) {
      paVar5 = &owner->channel[0].frame.header;
      paVar4 = &owner->channel[1].frame.header;
      do {
        iVar6 = paVar5->status;
        iVar3 = paVar5->master_status;
        paVar4->crc_enabled = paVar5->crc_enabled;
        paVar4->status = iVar6;
        paVar4->master_status = iVar3;
        piVar1 = &paVar5->sample_rate_mode;
        paVar5 = (aac_sbr_header_abi_t *)&paVar5->amplitude_resolution;
        paVar4->sample_rate_mode = *piVar1;
        paVar4 = (aac_sbr_header_abi_t *)&paVar4->amplitude_resolution;
      } while ((aac_analysis_inverse_filter_t *)paVar5 !=
               &owner->channel[0].frame.domain_and_inverse_filter);
      if (iVar2 == 1) {
        frame = &owner->channel[0].frame;
        do {
          iVar2 = sbr_reset_dec(frame,control,owner->channel[0].frame.header.sample_rate_mode);
          if (iVar2 != 0) goto LAB_ram_43013660;
          frame[-1].noise_exponent[4][0x3f] = 2;
          frame = (aac_sbr_frame_abi_t *)(frame[1].harmonics_and_envelopes.add_harmonics + 0xa3);
        } while ((aac_sbr_frame_abi_t *)&owner->embedded_ps != frame);
      }
      goto LAB_ram_4301365e;
    }
  }
  iVar2 = 10;
LAB_ram_430135bc:
  if ((uint)aiStack_34[4] < (-aiStack_34[3] & 7U) + aiStack_34[3]) {
    iVar2 = 0xe;
  }
  return iVar2;
}
