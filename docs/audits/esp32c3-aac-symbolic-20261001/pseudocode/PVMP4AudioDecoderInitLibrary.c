/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: PVMP4AudioDecoderInitLibrary @ ram:4300f5ee
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4
PVMP4AudioDecoderInitLibrary
          (int param_1,aac_core_abi_t *core,undefined4 param_3,undefined4 param_4,undefined4 param_5
          )

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;

  gp = &__global_pointer_;
  memset(core,0,0x8a84);
  *(uint8_t **)core->channel[0].spectrum_and_window = core->spectrum_and_scratch;
  *(uint8_t **)core->channel[1].spectrum_and_window = core->spectrum_and_scratch + 0x2000;
  *(uint8_t **)(core->channel[0].spectrum_and_window + 4) = core->spectrum_and_scratch + 0x1000;
  *(uint8_t **)(core->channel[1].spectrum_and_window + 4) = core->spectrum_and_scratch + 0x3000;
  *(uint8_t **)(core->stream_state + 0xc) = core->spectrum_and_scratch + 0x1d18;
  iVar1 = media_lib_module_calloc("AUD_Codec",1,0x35c);
  *(int *)(core->configuration + 0x23) = iVar1;
  if (iVar1 != 0) {
    iVar1 = media_lib_module_calloc("AUD_Codec",1,0x2b8);
    *(int *)(core->configuration + 0x67) = iVar1;
    if (iVar1 != 0) {
      iVar1 = media_lib_module_calloc("AUD_Codec",1,0x2b8);
      *(int *)(core->configuration + 0x6b) = iVar1;
      if (iVar1 != 0) {
        iVar1 = *(int *)(param_1 + 0x1c);
        core->plus_enabled = iVar1 != 0;
        core->requested_plus = iVar1 != 0;
        if (iVar1 != 0) {
          iVar1 = media_lib_module_calloc("AUD_Codec",1,0x414);
          *(int *)core->stream_state = iVar1;
          if (iVar1 == 0) {
            return 10;
          }
        }
        iVar1 = media_lib_module_calloc("AUD_Codec",1,0x3000);
        *(int *)(core->stream_state + 0x1c) = iVar1;
        if (iVar1 != 0) {
          iVar2 = *(int *)(core->configuration + 0x23);
          *(int *)(core->stream_state + 0x14) = iVar1;
          *(int *)(core->stream_state + 0x18) = iVar1 + 0x1000;
          *(undefined4 *)(iVar2 + 0x348) = param_3;
          uVar4 = *(undefined4 *)(core->configuration + 0x67);
          uVar3 = *(undefined4 *)(core->configuration + 0x6b);
          *(undefined4 *)(param_1 + 0x14) = 0;
          core->configuration[3] = 0xff;
          core->configuration[4] = 0xff;
          core->configuration[5] = 0xff;
          core->configuration[6] = 0xff;
          *(undefined4 *)(core->configuration + 0x6f) = uVar4;
          *(undefined4 *)(core->configuration + 0x73) = uVar4;
          *(undefined4 *)(core->configuration + 0x7b) = uVar4;
          *(undefined4 *)(core->configuration + 0x77) = uVar3;
          core->configuration[7] = 0;
          core->configuration[8] = 4;
          core->configuration[9] = 0;
          core->configuration[10] = 0;
          core->configuration[0x9f] = 4;
          core->configuration[0xa0] = 0;
          core->configuration[0xa1] = 0;
          core->configuration[0xa2] = 0;
          core->configuration[0xa3] = 1;
          core->configuration[0xa4] = 0;
          core->configuration[0xa5] = 0;
          core->configuration[0xa6] = 0;
          infoinit(4,core->configuration + 0x6f,core->configuration + 0x27);
          iVar1 = *(int *)(core->configuration + 0x23);
          *(undefined4 *)(param_1 + 0x34) = 0;
          *(undefined4 *)(param_1 + 0x38) = 0;
          iVar1 = *(int *)(iVar1 + 0x348);
          *(undefined4 *)(param_1 + 0x30) = 0;
          *(undefined4 *)(param_1 + 0x18) = 1;
          *(undefined4 *)(param_1 + 0x28) = 0;
          if ((iVar1 != 0) || (iVar1 = raw_stream_parameter_setup(param_4,param_5,core), iVar1 == 0)
             ) {
            gp = &__global_pointer_;
            return 0;
          }
        }
      }
    }
  }
  return 10;
}
