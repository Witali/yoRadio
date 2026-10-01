/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: esp_aac_dec_open @ ram:4300027c
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4 esp_aac_dec_open(int *param_1,uint param_2,int *param_3)

{
  char cVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  aac_core_abi_t *core;
  int iVar4;
  uint uVar5;
  int iVar6;
  int *piVar7;

  gp = &__global_pointer_;
  if ((param_3 == (int *)0x0) || ((param_2 & 0xfffffff7) != 0)) {
    uVar3 = esp_log_timestamp();
    esp_log(1,"ESP_AAC_DEC","E (%lu) %s: Invalid argument, decoder:%p cfg_sz:%d\n",uVar3,
            "ESP_AAC_DEC",param_3,param_2);
    uVar3 = 0xfffffffb;
  }
  else {
    puVar2 = (undefined4 *)media_lib_module_calloc("AUD_Codec",1,0x54);
    if (puVar2 != (undefined4 *)0x0) {
      uVar3 = PVMP4AudioDecoderGetMemRequirements();
      core = (aac_core_abi_t *)media_lib_module_calloc("AUD_Codec",1,uVar3);
      *puVar2 = core;
      if (core == (aac_core_abi_t *)0x0) {
        uVar3 = esp_log_timestamp();
        esp_log(1,"ESP_AAC_DEC","E (%lu) %s: There is no enough memory for AAC buffer\n",uVar3);
        uVar3 = 0xfffffffe;
      }
      else {
        if (param_1 == (int *)0x0) {
          puVar2[3] = 0x1000;
          puVar2[7] = 1;
          puVar2[0xe] = 0;
          puVar2[0xf] = 0;
          puVar2[0x13] = 0;
          *(undefined1 *)(puVar2 + 0x14) = 0;
          uVar5 = 0;
          iVar4 = 0;
          uVar3 = 0xffffffff;
        }
        else {
          if (*(char *)((int)param_1 + 6) != '\0') {
            piVar7 = &sample_rates_2;
            iVar4 = 0;
            do {
              iVar6 = *piVar7;
              piVar7 = piVar7 + 1;
              if (*param_1 == iVar6) {
                uVar5 = (uint)*(byte *)(param_1 + 1);
                uVar3 = 0;
                goto LAB_ram_430002e0;
              }
              iVar4 = iVar4 + 1;
            } while (iVar4 != 0xc);
            uVar3 = esp_log_timestamp();
            esp_log(1,"ESP_AAC_DEC","E (%lu) %s: Sample rate:%d not supported\n",uVar3,"ESP_AAC_DEC"
                    ,*param_1);
            uVar3 = 0xfffffffb;
            goto LAB_ram_4300039e;
          }
          uVar5 = 0;
          iVar4 = 0;
          uVar3 = 0xffffffff;
LAB_ram_430002e0:
          cVar1 = *(char *)((int)param_1 + 7);
          puVar2[0xe] = 0;
          puVar2[0xf] = 0;
          puVar2[0x13] = 0;
          *(undefined1 *)(puVar2 + 0x14) = 0;
          puVar2[3] = 0x1000;
          puVar2[7] = 1;
          if (cVar1 != '\0') {
            puVar2[0xb] = 1;
            *(undefined1 *)(puVar2 + 0x14) = 1;
          }
        }
        iVar4 = PVMP4AudioDecoderInitLibrary((int)(puVar2 + 4),core,uVar3,iVar4,uVar5);
        if (iVar4 == 0) {
          *param_3 = (int)puVar2;
          gp = &__global_pointer_;
          return 0;
        }
        uVar3 = esp_log_timestamp();
        esp_log(1,"ESP_AAC_DEC","E (%lu) %s: Fail to init AAC library %d\n",uVar3,"ESP_AAC_DEC",
                0xfffffffe);
        uVar3 = 0xffffffff;
      }
LAB_ram_4300039e:
      esp_aac_dec_close(puVar2);
      return uVar3;
    }
    uVar3 = esp_log_timestamp();
    esp_log(1,"ESP_AAC_DEC","E (%lu) %s: There is no enough memory for AAC decoder\n",uVar3);
    uVar3 = 0xfffffffe;
  }
  return uVar3;
}
