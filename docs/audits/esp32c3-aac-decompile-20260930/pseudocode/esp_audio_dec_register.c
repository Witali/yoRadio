/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: esp_audio_dec_register @ ram:420262b0
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4 esp_audio_dec_register(int param_1,int *param_2)

{
  uint32_t uVar1;
  undefined4 uVar2;
  int *piVar3;
  int *piVar4;
  int *piVar5;

  gp = &__global_pointer_;
  if ((param_2 == (int *)0x0) || (param_1 == 0)) {
    uVar1 = esp_log_timestamp();
    esp_log(3,"AUD_CODEC_REG","I (%lu) %s: Invalid input, dec_type:%d lib:%p\n",uVar1,
            "AUD_CODEC_REG",param_1,param_2);
    uVar2 = 0xfffffffb;
  }
  else if (((*param_2 == 0) || (param_2[1] == 0)) || (piVar3 = audio_dec_libs, param_2[3] == 0)) {
    uVar1 = esp_log_timestamp();
    esp_log(1,"AUD_CODEC_REG","E (%lu) %s: Decoder missing APIs, open:%p decode:%p close:%p\n",uVar1
            ,"AUD_CODEC_REG",*param_2,param_2[1],param_2[3]);
    uVar2 = 0xfffffffb;
  }
  else {
    for (; piVar3 != (int *)0x0; piVar3 = (int *)piVar3[2]) {
      if (param_1 == *piVar3) {
        if (param_2 != (int *)piVar3[1]) {
          uVar1 = esp_log_timestamp();
          esp_log(3,"AUD_CODEC_REG","I (%lu) %s: Overwrite codec library for %d\n",uVar1,
                  "AUD_CODEC_REG",param_1);
        }
        goto LAB_ram_4202631c;
      }
    }
    piVar3 = (int *)media_lib_module_calloc("AUD_Codec",1,0xc);
    if (piVar3 == (int *)0x0) {
      uVar2 = codec_register_part_0();
      return uVar2;
    }
    piVar5 = audio_dec_libs;
    if (audio_dec_libs == (int *)0x0) {
      audio_dec_libs = piVar3;
      *piVar3 = param_1;
    }
    else {
      do {
        piVar4 = piVar5;
        piVar5 = (int *)piVar4[2];
      } while (piVar5 != (int *)0x0);
      piVar4[2] = (int)piVar3;
      *piVar3 = param_1;
    }
LAB_ram_4202631c:
    piVar3[1] = (int)param_2;
    uVar2 = 0;
  }
  return uVar2;
}
