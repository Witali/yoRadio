/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: esp_aac_dec_open @ ram:4300027c
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4 esp_aac_dec_open(int *param_1,uint param_2,int *param_3)

{
  char cVar1;
  int *piVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  undefined1 uVar6;
  int iVar7;
  int *piVar8;

  gp = &__global_pointer_;
  if ((param_3 == (int *)0x0) || ((param_2 & 0xfffffff7) != 0)) {
    uVar3 = esp_log_timestamp();
    esp_log(1,"ESP_AAC_DEC","E (%lu) %s: Invalid argument, decoder:%p cfg_sz:%d\n",uVar3,
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
        uVar3 = esp_log_timestamp();
        esp_log(1,"ESP_AAC_DEC","E (%lu) %s: There is no enough memory for AAC buffer\n",uVar3);
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
          uVar6 = 0;
          iVar5 = 0;
          uVar3 = 0xffffffff;
        }
        else {
          if (*(char *)((int)param_1 + 6) != '\0') {
            piVar8 = &sample_rates_2;
            iVar5 = 0;
            do {
              iVar7 = *piVar8;
              piVar8 = piVar8 + 1;
              if (*param_1 == iVar7) {
                uVar6 = (undefined1)param_1[1];
                uVar3 = 0;
                goto LAB_ram_430002e0;
              }
              iVar5 = iVar5 + 1;
            } while (iVar5 != 0xc);
            uVar3 = esp_log_timestamp();
            esp_log(1,"ESP_AAC_DEC","E (%lu) %s: Sample rate:%d not supported\n",uVar3,"ESP_AAC_DEC"
                    ,*param_1);
            uVar3 = 0xfffffffb;
            goto LAB_ram_4300039e;
          }
          uVar6 = 0;
          iVar5 = 0;
          uVar3 = 0xffffffff;
LAB_ram_430002e0:
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
        iVar4 = PVMP4AudioDecoderInitLibrary(piVar2 + 4,iVar4,uVar3,iVar5,uVar6);
        if (iVar4 == 0) {
          *param_3 = (int)piVar2;
          gp = &__global_pointer_;
          return 0;
        }
        uVar3 = esp_log_timestamp();
        esp_log(1,"ESP_AAC_DEC","E (%lu) %s: Fail to init AAC library %d\n",uVar3,"ESP_AAC_DEC",
                0xfffffffe);
        uVar3 = 0xffffffff;
      }
LAB_ram_4300039e:
      esp_aac_dec_close(piVar2);
      return uVar3;
    }
    uVar3 = esp_log_timestamp();
    esp_log(1,"ESP_AAC_DEC","E (%lu) %s: There is no enough memory for AAC decoder\n",uVar3);
    uVar3 = 0xfffffffe;
  }
  return uVar3;
}
