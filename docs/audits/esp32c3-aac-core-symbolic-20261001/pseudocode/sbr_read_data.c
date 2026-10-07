/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_read_data @ ram:4301356c
 * Types and parameter counts are inferred; verify against disassembly. */

int sbr_read_data(aac_sbr_owner_abi_t *owner,aac_sbr_control_abi_t *control,
                 aac_analysis_sbr_stream_t *stream)

{
  int32_t *piVar1;
  aac_sbr_frame_abi_t *frame;
  int iVar2;
  int32_t iVar3;
  aac_sbr_header_abi_t *paVar4;
  int iVar5;
  aac_sbr_header_abi_t *paVar6;
  int32_t iVar7;
  aac_analysis_sbr_bits_t aStack_34;

  gp = &__global_pointer_;
  aStack_34.total_bits = stream->element[0].payload_bytes << 3;
  aStack_34.cursor = stream->element[0].payload;
  aStack_34.cache = 0;
  aStack_34.cached_bits = 0;
  aStack_34.read_bits = 0;
  buf_getbits(&aStack_34,4);
  if ((stream->element[0].extension_type == 0xe) &&
     (iVar2 = sbr_crc_check(&aStack_34,stream->element[0].payload_bytes * 8 - 0xe), iVar2 == 0)) {
    iVar2 = 0;
    goto LAB_ram_430135bc;
  }
  iVar2 = buf_getbits(&aStack_34,1);
  if (iVar2 == 0) {
    iVar2 = stream->element[0].element_id;
    if (iVar2 == 0) {
LAB_ram_43013680:
      if (owner->channel[0].sync_state != 2) {
        iVar2 = 0;
        goto LAB_ram_430135bc;
      }
LAB_ram_430136c8:
      iVar2 = sbr_get_sce(&owner->channel[0].frame,&aStack_34,owner->ps);
      goto LAB_ram_430135bc;
    }
    if (iVar2 == 1) {
LAB_ram_4301365e:
      iVar2 = 0;
LAB_ram_43013660:
      if (owner->channel[0].sync_state == 2) {
        iVar2 = sbr_get_cpe(&owner->channel[0].frame,&owner->channel[1].frame,&aStack_34);
      }
      goto LAB_ram_430135bc;
    }
  }
  else {
    iVar2 = sbr_get_header_data(&owner->channel[0].frame.header,&aStack_34,
                                owner->channel[0].sync_state);
    iVar5 = stream->element[0].element_id;
    if (iVar5 == 0) {
      if (iVar2 != 1) goto LAB_ram_43013680;
      iVar2 = sbr_reset_dec(&owner->channel[0].frame,control,
                            owner->channel[0].frame.header.sample_rate_mode);
      if (iVar2 != 0) goto LAB_ram_430135bc;
      owner->channel[0].sync_state = 2;
      goto LAB_ram_430136c8;
    }
    if (iVar5 == 1) {
      paVar6 = &owner->channel[0].frame.header;
      paVar4 = &owner->channel[1].frame.header;
      do {
        iVar7 = paVar6->status;
        iVar3 = paVar6->master_status;
        paVar4->crc_enabled = paVar6->crc_enabled;
        paVar4->status = iVar7;
        paVar4->master_status = iVar3;
        piVar1 = &paVar6->sample_rate_mode;
        paVar6 = (aac_sbr_header_abi_t *)&paVar6->amplitude_resolution;
        paVar4->sample_rate_mode = *piVar1;
        paVar4 = (aac_sbr_header_abi_t *)&paVar4->amplitude_resolution;
      } while ((aac_analysis_inverse_filter_t *)paVar6 !=
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
  if (aStack_34.total_bits < (-aStack_34.read_bits & 7) + aStack_34.read_bits) {
    iVar2 = 0xe;
  }
  return iVar2;
}
