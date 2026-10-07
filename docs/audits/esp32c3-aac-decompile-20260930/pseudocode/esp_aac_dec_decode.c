/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: esp_aac_dec_decode @ ram:42026966
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4
esp_aac_dec_decode(undefined4 *param_1,int *param_2,undefined4 *param_3,undefined4 *param_4)

{
  void *aa;
  uint32_t uVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;

  gp = &__global_pointer_;
  if ((((param_1 == (undefined4 *)0x0) || (param_2 == (int *)0x0)) || (*param_2 == 0)) ||
     ((param_3 == (undefined4 *)0x0 || (aa = (void *)*param_3, aa == (void *)0x0)))) {
    uVar1 = esp_log_timestamp();
    esp_log(1,"ESP_AAC_DEC",
            "E (%lu) %s: Invalid parameter, handle(%p), in_frame(%p), in_frame_buf(%p), out_frame(%p), out_frame_buf(%p) on %s\n"
            ,uVar1,"ESP_AAC_DEC",param_1,param_2,*param_2,param_3,*param_3,"esp_aac_dec_decode");
    uVar2 = 0xfffffffb;
  }
  else if (param_4 == (undefined4 *)0x0) {
    uVar1 = esp_log_timestamp();
    esp_log(1,"ESP_AAC_DEC","E (%lu) %s: Invalid parameter \'%s\' on %s\n",uVar1,"ESP_AAC_DEC",
            "aac information","esp_aac_dec_decode");
    uVar2 = 0xfffffffb;
  }
  else {
    uVar4 = param_1[3];
    uVar8 = param_3[1];
    if (uVar4 <= uVar8) {
      if (param_1[2] == 0) {
        iVar5 = *param_2;
        iVar6 = param_2[1];
        iVar3 = param_2[1];
        param_1[8] = aa;
        param_1[4] = iVar5;
        param_1[5] = iVar6;
        param_1[6] = iVar3;
        param_1[0xe] = 0;
        iVar3 = (int)aa + uVar4;
        if (uVar4 << 1 <= uVar8) goto LAB_ram_420269c6;
        param_1[9] = param_1[1];
        iVar3 = PVMP4AudioDecodeFrame(param_1 + 4,*param_1);
        while (iVar3 != 0) {
          if (iVar3 != 0x28) {
            uVar1 = esp_log_timestamp();
            esp_log(1,"ESP_AAC_DEC","E (%lu) %s: Failed to decode aac frame, error:%d.\n",uVar1,
                    "ESP_AAC_DEC",iVar3);
            return 0xffffffff;
          }
          if (param_1[1] != 0) {
            return 0xffffffff;
          }
          iVar3 = media_lib_module_malloc("AUD_Codec",param_1[3]);
          param_1[1] = iVar3;
          if (iVar3 == 0) {
            uVar1 = esp_log_timestamp();
            esp_log(1,"ESP_AAC_DEC","E (%lu) %s: No memory for AAC-Plus output\n",uVar1);
            return 0xfffffffe;
          }
LAB_ram_420269c6:
          param_1[9] = iVar3;
          iVar3 = PVMP4AudioDecodeFrame(param_1 + 4,*param_1);
        }
        uVar7 = param_1[0xd];
        *param_4 = param_1[0x10];
        if (uVar7 == 0) {
          uVar7 = param_1[0x12];
        }
        *(char *)((int)param_4 + 5) = (char)uVar7;
        *(undefined1 *)(param_4 + 1) = 0x10;
        iVar6 = param_1[0x13];
        uVar7 = uVar7 & 0xff;
        iVar5 = iVar6 * uVar7;
        iVar3 = param_1[0xe];
        param_4[2] = param_1[0x11];
        param_3[3] = iVar5 * 2;
        param_2[2] = iVar3;
        if ((0x400 < iVar6) && (uVar8 < uVar4 << 1)) {
          param_3[3] = uVar7 << 0xb;
          param_1[2] = (iVar5 + uVar7 * -0x400) * 2;
          param_2[2] = 0;
        }
      }
      else {
        memcpy(aa,(void *)param_1[1],param_1[2]);
        iVar3 = param_1[0xe];
        param_3[3] = param_1[2];
        param_2[2] = iVar3;
        param_1[2] = 0;
      }
      return 0;
    }
    param_3[2] = uVar4;
    param_3[3] = 0;
    uVar2 = 0xfffffff8;
  }
  return uVar2;
}
