/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: esp_aac_dec_open @ ram:42026bb2
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4 esp_aac_dec_open(int *param_1,uint param_2,int *param_3)

{
  char cVar1;
  int *piVar2;
  undefined4 uVar3;
  int iVar4;
  uint32_t uVar5;
  int iVar6;
  undefined1 uVar7;
  int iVar8;
  int *piVar9;

  gp = &__global_pointer_;
  if ((param_3 == (int *)0x0) || ((param_2 & 0xfffffff7) != 0)) {
    uVar5 = esp_log_timestamp();
    esp_log(1,"ESP_AAC_DEC","E (%lu) %s: Invalid argument, decoder:%p cfg_sz:%d\n",uVar5,
            "ESP_AAC_DEC",param_3,param_2);
    uVar3 = 0xfffffffb;
  }
  else {
    piVar2 = (int *)media_lib_module_calloc("AUD_Codec",1,0x54);
    if (piVar2 != (int *)0x0) {
      uVar3 = PVMP4AudioDecoderGetMemRequirements();
      iVar4 = media_lib_module_calloc("AUD_Codec",1,uVar3);
      *piVar2 = iVar4;
      if (iVar4 == 0) {
        uVar5 = esp_log_timestamp();
        esp_log(1,"ESP_AAC_DEC","E (%lu) %s: There is no enough memory for AAC buffer\n",uVar5);
        uVar3 = 0xfffffffe;
      }
      else {
        if (param_1 == (int *)0x0) {
          piVar2[3] = 0x1000;
          piVar2[7] = 1;
          piVar2[0xe] = 0;
          piVar2[0xf] = 0;
          piVar2[0x13] = 0;
          *(undefined1 *)(piVar2 + 0x14) = 0;
          uVar7 = 0;
          iVar6 = 0;
          uVar3 = 0xffffffff;
        }
        else {
          if (*(char *)((int)param_1 + 6) != '\0') {
            piVar9 = &sample_rates_2;
            iVar6 = 0;
            do {
              iVar8 = *piVar9;
              piVar9 = piVar9 + 1;
              if (*param_1 == iVar8) {
                uVar7 = (undefined1)param_1[1];
                uVar3 = 0;
                goto LAB_ram_42026c0a;
              }
              iVar6 = iVar6 + 1;
            } while (iVar6 != 0xc);
            uVar5 = esp_log_timestamp();
            esp_log(1,"ESP_AAC_DEC","E (%lu) %s: Sample rate:%d not supported\n",uVar5,"ESP_AAC_DEC"
                    ,*param_1);
            uVar3 = 0xfffffffb;
            goto LAB_ram_42026cbc;
          }
          uVar7 = 0;
          iVar6 = 0;
          uVar3 = 0xffffffff;
LAB_ram_42026c0a:
          cVar1 = *(char *)((int)param_1 + 7);
          piVar2[0xe] = 0;
          piVar2[0xf] = 0;
          piVar2[0x13] = 0;
          *(undefined1 *)(piVar2 + 0x14) = 0;
          piVar2[3] = 0x1000;
          piVar2[7] = 1;
          if (cVar1 != '\0') {
            piVar2[0xb] = 1;
            *(undefined1 *)(piVar2 + 0x14) = 1;
          }
        }
        iVar4 = PVMP4AudioDecoderInitLibrary(piVar2 + 4,iVar4,uVar3,iVar6,uVar7);
        if (iVar4 == 0) {
          *param_3 = (int)piVar2;
          gp = &__global_pointer_;
          return 0;
        }
        uVar5 = esp_log_timestamp();
        esp_log(1,"ESP_AAC_DEC","E (%lu) %s: Fail to init AAC library %d\n",uVar5,"ESP_AAC_DEC",
                0xfffffffe);
        uVar3 = 0xffffffff;
      }
LAB_ram_42026cbc:
      esp_aac_dec_close(piVar2);
      return uVar3;
    }
    uVar5 = esp_log_timestamp();
    esp_log(1,"ESP_AAC_DEC","E (%lu) %s: There is no enough memory for AAC decoder\n",uVar5);
    uVar3 = 0xfffffffe;
  }
  return uVar3;
}
