/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_applied @ ram:430100f4
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4
sbr_applied(aac_sbr_owner_abi_t *owner,int *param_2,int param_3,int param_4,int param_5,int param_6,
           int param_7,aac_sbr_control_abi_t *control,aac_core_abi_t *core,int param_10)

{
  aac_sbr_frame_abi_t *paVar1;
  int iVar2;
  aac_ps_abi_t *ps;
  int32_t *piVar3;
  aac_sbr_frame_abi_t *frame;
  int iStack_30;
  int iStack_2c;
  int iStack_28;
  int iStack_24;

  gp = &__global_pointer_;
  if (*param_2 == 0) goto LAB_ram_4301011a;
  iVar2 = sbr_read_data(owner,control,(int)param_2);
  if (iVar2 == 0) {
    iVar2 = owner->channel[0].sync_state;
    if ((iVar2 != 2) || (owner->initialize_ps == 0)) goto LAB_ram_43010248;
    owner->initialize_ps = 0;
    if (param_7 != 2) {
      iVar2 = owner->ps->detected;
      core->channels = iVar2;
      if (iVar2 == 0) goto LAB_ram_430102bc;
      ps_allocate_decoder(owner,0x20);
      iVar2 = owner->channel[0].sync_state;
      control->low_complexity = 0;
      goto LAB_ram_43010260;
    }
    owner->ps->detected = 0;
    core->channels = 0;
    control->low_complexity = 1;
LAB_ram_430102bc:
    if (param_2[2] != 1) goto LAB_ram_4301039e;
LAB_ram_430102c6:
    frame = &owner->channel[0].frame;
    sbr_decode_envelope(frame);
    decode_noise_floorlevels(frame);
    if (owner->channel[0].frame.coupling == 0) {
      sbr_requantize_envelope_data(frame);
    }
    paVar1 = &owner->channel[1].frame;
    sbr_decode_envelope(paVar1);
    decode_noise_floorlevels(paVar1);
    if (owner->channel[1].frame.coupling != 0) {
      sbr_envelope_unmapping(frame,paVar1);
      goto LAB_ram_4301011a;
    }
  }
  else {
    iVar2 = 1;
    owner->channel[0].sync_state = 1;
LAB_ram_43010248:
    if (param_7 == 2) {
      control->low_complexity = 1;
    }
    else if ((param_7 == 1) || (*(int *)(core->configuration + 0x83) < 2)) {
      control->low_complexity = 0;
    }
    else {
      control->low_complexity = 1;
    }
LAB_ram_43010260:
    if (param_2[2] == 1) {
      if (iVar2 != 2) {
        init_sbr_dec(control->output_rate >> 1,*(int *)(core->configuration + 0xa7),control,
                     &owner->channel[0].frame);
        if (owner->channel[1].sync_state != 2) {
          init_sbr_dec(control->output_rate >> 1,*(int *)(core->configuration + 0xa7),control,
                       &owner->channel[1].frame);
        }
        goto LAB_ram_4301011a;
      }
      goto LAB_ram_430102c6;
    }
    if (iVar2 != 2) {
      init_sbr_dec(control->output_rate >> 1,*(int *)(core->configuration + 0xa7),control,
                   &owner->channel[0].frame);
      goto LAB_ram_4301011a;
    }
LAB_ram_4301039e:
    paVar1 = &owner->channel[0].frame;
    sbr_decode_envelope(paVar1);
    decode_noise_floorlevels(paVar1);
    if (owner->channel[0].frame.coupling != 0) goto LAB_ram_4301011a;
  }
  sbr_requantize_envelope_data(paVar1);
LAB_ram_4301011a:
  paVar1 = &owner->channel[0].frame;
  iStack_28 = param_5 + 2;
  iStack_24 = param_6 + 2;
  iStack_30 = param_5;
  iStack_2c = param_6;
  if (core->channels == 0) {
    iVar2 = owner->channel[0].sync_state;
    owner->channel[0].frame.high_real = (int32_t *)core->spectrum_and_scratch;
    owner->channel[0].frame.high_imag = (int32_t *)(core->spectrum_and_scratch + 0x2000);
    sbr_dec(param_3,&iStack_30,paVar1,(uint)(iVar2 == 2),control,(int *)0x0,(aac_ps_abi_t *)0x0,core
           );
    if (param_10 == 2) {
      iVar2 = owner->channel[1].sync_state;
      owner->channel[1].frame.high_real = (int32_t *)core->spectrum_and_scratch;
      owner->channel[1].frame.high_imag = (int32_t *)(core->spectrum_and_scratch + 0x2000);
      sbr_dec(param_4,&iStack_28,&owner->channel[1].frame,(uint)(iVar2 == 2),control,(int *)0x0,
              (aac_ps_abi_t *)0x0,core);
    }
  }
  else {
    ps_bstr_decoding(owner->ps);
    ps = owner->ps;
    iVar2 = owner->channel[0].sync_state;
    piVar3 = *(int32_t **)(core->stream_state + 0x18);
    ps->right_synthesis = owner->channel[1].frame.synthesis;
    owner->channel[0].frame.high_real = piVar3;
    owner->channel[0].frame.high_imag = (int32_t *)(core->spectrum_and_scratch + 0xe60);
    sbr_dec(param_3,&iStack_30,paVar1,(uint)(iVar2 == 2),control,&iStack_28,ps,core);
  }
  return 0;
}
