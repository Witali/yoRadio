/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: esp_aac_dec_parse_frame @ ram:42025c1a
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4 esp_aac_dec_parse_frame(undefined4 *param_1,uint *param_2)

{
  byte bVar1;
  byte bVar2;
  uint32_t uVar3;
  uint uVar4;
  uint uVar5;
  byte *pbVar6;
  ushort uVar7;
  uint uVar8;

  gp = &__global_pointer_;
  uVar8 = param_1[1];
  if (uVar8 < 4) {
    return 0xfffffffc;
  }
  pbVar6 = (byte *)*param_1;
  bVar1 = pbVar6[3];
  bVar2 = pbVar6[2];
  uVar4 = (uint)bVar2 << 8;
  if (((((uint)*pbVar6 << 0x18 | (pbVar6[1] & 0xfff6) << 0x10) == 0xfff00000) && (uVar4 >> 0xe != 3)
      ) && (uVar4 = (uVar4 & 0x3c00) >> 10, uVar4 < 0xc)) {
    uVar5 = (uint)pbVar6[4] << 3 | (uint)(pbVar6[5] >> 5) | (bVar1 & 3) << 0xb;
    *param_2 = uVar5;
    if (uVar8 < uVar5 + 4) {
LAB_ram_42025c90:
      uVar7 = CONCAT11(bVar2,bVar1) >> 6 & 7;
      if (uVar7 < 3) {
        uVar8 = *(uint *)(samp_rate_info_0 + uVar4 * 4);
        *(char *)((int)param_2 + 0x21) = (char)uVar7;
        param_2[10] = 0x400;
        param_2[7] = uVar8;
        *(undefined1 *)(param_2 + 8) = 0x10;
        param_2[9] = uVar8 * uVar5 >> 7;
        return 0;
      }
      uVar3 = esp_log_timestamp();
      esp_log(1,"AUD_Dec_Parse","E (%lu) %s: AAC only support 1-2 channel\n",uVar3);
      return 0xfffffffa;
    }
    pbVar6 = pbVar6 + uVar5;
    if ((((uint)*pbVar6 << 0x18 | (pbVar6[1] & 0xfff6) << 0x10) == 0xfff00000) &&
       (((uint)pbVar6[2] << 8) >> 0xe != 3)) {
      if (((uint)pbVar6[2] << 8 & 0x3c00) >> 10 < 0xc) goto LAB_ram_42025c90;
      *param_2 = 0;
    }
    else {
      *param_2 = 0;
    }
  }
  return 0xfffffffb;
}
