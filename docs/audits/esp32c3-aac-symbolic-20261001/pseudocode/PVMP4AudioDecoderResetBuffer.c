/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: PVMP4AudioDecoderResetBuffer @ ram:4300f77e
 * Types and parameter counts are inferred; verify against disassembly. */

void PVMP4AudioDecoderResetBuffer(aac_core_abi_t *core)

{
  aac_sbr_owner_abi_t *paVar1;
  int iVar2;
  int32_t (*paiVar3) [64];
  aac_sbr_control_abi_t *paVar4;
  aac_ps_abi_t *paVar5;
  int32_t (*paiVar6) [32];
  undefined4 *puVar7;
  int32_t (*paiVar8) [64];

  gp = &__global_pointer_;
  memset(core->channel[0].overlap,0,0x1000);
  memset(core->channel[1].overlap,0,0x1000);
  paVar1 = core->sbr;
  if (((paVar1 != (aac_sbr_owner_abi_t *)0x0) && (paVar1->initialize_ps == 0)) &&
     (core->plus_enabled != 0)) {
    core[2].channel[1].overlap[300] = (int32_t)&paVar1->embedded_ps;
    memset(core->channel,0,0x240);
    memset(core->channel[0].ltp_history + 0x520,0,0x240);
    memset(paVar1->channel[0].frame.synthesis,0,0x900);
    paVar1->channel[0].frame.previous_noise[0] = 0;
    paVar1->channel[0].frame.previous_noise[1] = 0;
    paVar1->channel[0].frame.previous_noise[2] = 0;
    paVar1->channel[0].frame.previous_noise[3] = 0;
    paVar1->channel[0].frame.previous_noise[4] = 0;
    paVar1->channel[0].frame.previous_noise[5] = 0;
    paVar1->channel[0].frame.previous_noise[6] = 0;
    paVar1->channel[0].frame.previous_noise[7] = 0;
    paVar1->channel[0].frame.previous_noise[8] = 0;
    paVar1->channel[0].frame.previous_noise[9] = 0;
    memset(core->channel + 1,0,0x240);
    memset(core->channel[1].ltp_history + 0x520,0,0x240);
    memset(paVar1->channel[1].frame.synthesis,0,0x900);
    paVar1->channel[1].frame.previous_noise[0] = 0;
    paVar1->channel[1].frame.previous_noise[1] = 0;
    paVar1->channel[1].frame.previous_noise[2] = 0;
    paVar1->channel[1].frame.previous_noise[3] = 0;
    paVar1->channel[1].frame.previous_noise[4] = 0;
    paVar1->channel[1].frame.previous_noise[5] = 0;
    paVar1->channel[1].frame.previous_noise[6] = 0;
    paVar1->channel[1].frame.previous_noise[7] = 0;
    paVar1->channel[1].frame.previous_noise[8] = 0;
    paVar1->channel[1].frame.previous_noise[9] = 0;
    paiVar6 = paVar1->channel[0].frame.low_real;
    do {
      iVar2 = memset(paiVar6,0,0x80);
      paiVar6 = (int32_t (*) [32])(iVar2 + 0x80);
    } while (paiVar6 != paVar1->channel[0].frame.low_real + 8);
    paVar1->channel[0].frame.previous_bandwidth[0] = 0;
    paVar1->channel[0].frame.previous_bandwidth[1] = 0;
    paVar1->channel[0].frame.previous_bandwidth[2] = 0;
    paVar1->channel[0].frame.previous_bandwidth[3] = 0;
    paVar1->channel[0].frame.previous_bandwidth[4] = 0;
    paVar1->channel[0].frame.previous_bandwidth[5] = 0;
    paiVar8 = paVar1->channel[0].frame.gain_mantissa;
    do {
      memset(paiVar8,0,0x100);
      paiVar3 = paiVar8 + 5;
      paiVar8 = paiVar8 + 1;
      memset(paiVar3,0,0x100);
    } while (paVar1->channel[0].frame.noise_mantissa != paiVar8);
    memset(paVar1->channel[0].frame.high_real_history,0,0x480);
    memset(paVar1->channel[0].frame.high_imag_history,0,0x480);
    paVar4 = core->sbr_control;
    if (paVar4->low_complexity == 1) {
      paiVar6 = paVar1->channel[1].frame.low_real;
      do {
        iVar2 = memset(paiVar6,0,0x80);
        paiVar6 = (int32_t (*) [32])(iVar2 + 0x80);
      } while (paVar1->channel[1].frame.low_real + 8 != paiVar6);
      memset(paVar1->channel[1].frame.high_real_history,0,0x480);
      paiVar8 = paVar1->channel[1].frame.gain_mantissa;
      paVar1->channel[1].frame.previous_bandwidth[0] = 0;
      paVar1->channel[1].frame.previous_bandwidth[1] = 0;
      paVar1->channel[1].frame.previous_bandwidth[2] = 0;
      paVar1->channel[1].frame.previous_bandwidth[3] = 0;
      paVar1->channel[1].frame.previous_bandwidth[4] = 0;
      paVar1->channel[1].frame.previous_bandwidth[5] = 0;
      do {
        memset(paiVar8,0,0x100);
        paiVar3 = paiVar8 + 5;
        paiVar8 = paiVar8 + 1;
        memset(paiVar3,0,0x100);
      } while (paVar1->channel[1].frame.noise_mantissa != paiVar8);
      paVar4 = core->sbr_control;
    }
    else if (core->channels == 1) {
      iVar2 = 0;
      do {
        puVar7 = *(undefined4 **)
                  (*(int *)(*(int *)(core[2].channel[1].overlap[300] + 0x1fc) + 0xc) + iVar2);
        *puVar7 = 0;
        puVar7[4] = 0;
        puVar7[1] = 0;
        puVar7[2] = 0;
        puVar7[3] = 0;
        puVar7[5] = 0;
        puVar7[6] = 0;
        puVar7[7] = 0;
        puVar7[8] = 0;
        puVar7[9] = 0;
        puVar7[10] = 0;
        puVar7[0xb] = 0;
        puVar7 = *(undefined4 **)
                  (*(int *)(*(int *)(core[2].channel[1].overlap[300] + 0x1fc) + 0x10) + iVar2);
        iVar2 = iVar2 + 4;
        *puVar7 = 0;
        puVar7[1] = 0;
        puVar7[2] = 0;
        puVar7[3] = 0;
        puVar7[4] = 0;
        puVar7[5] = 0;
        puVar7[6] = 0;
        puVar7[7] = 0;
        puVar7[8] = 0;
        puVar7[9] = 0;
        puVar7[10] = 0;
        puVar7[0xb] = 0;
      } while (iVar2 != 0xc);
      paVar4 = core->sbr_control;
    }
    paVar1 = core->sbr;
    paVar1->channel[0].sync_state = 1;
    paVar1->channel[1].sync_state = 1;
    paVar5 = paVar1->ps;
    paVar4->output_rate = 0;
    paVar1->initialize_ps = 1;
    paVar5->detected = 0;
  }
  core->frame_number = 0;
  core->plus_enabled = core->requested_plus;
  return;
}
