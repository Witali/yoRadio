/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: sbr_applied @ ram:42028246
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4
sbr_applied(int param_1,int *param_2,undefined4 param_3,undefined4 param_4,int param_5,int param_6,
           int param_7,int *param_8,int param_9,int param_10)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iStack_30;
  int iStack_2c;
  int iStack_28;
  int iStack_24;

  gp = &__global_pointer_;
  if (*param_2 == 0) goto LAB_ram_4202826c;
  iVar1 = sbr_read_data(param_1,param_8,param_2);
  if (iVar1 == 0) {
    iVar1 = *(int *)(param_1 + 4);
    if ((iVar1 != 2) || (*(int *)(param_1 + 0xc980) == 0)) goto LAB_ram_42028380;
    *(undefined4 *)(param_1 + 0xc980) = 0;
    if (param_7 != 2) {
      iVar1 = **(int **)(param_1 + 0xc984);
      *(int *)(param_9 + 0xc0) = iVar1;
      if (iVar1 == 0) goto LAB_ram_420283f0;
      ps_allocate_decoder(param_1,0x20);
      iVar1 = *(int *)(param_1 + 4);
      param_8[1] = 0;
      goto LAB_ram_42028398;
    }
    **(int **)(param_1 + 0xc984) = 0;
    *(undefined4 *)(param_9 + 0xc0) = 0;
    param_8[1] = 1;
LAB_ram_420283f0:
    if (param_2[2] != 1) goto LAB_ram_420284b6;
LAB_ram_420283fa:
    iVar2 = param_1 + 8;
    sbr_decode_envelope(iVar2);
    decode_noise_floorlevels(iVar2);
    if (*(int *)(param_1 + 0x180) == 0) {
      sbr_requantize_envelope_data(iVar2);
    }
    iVar1 = param_1 + 0x64c8;
    sbr_decode_envelope();
    decode_noise_floorlevels(iVar1);
    if (*(int *)(param_1 + 0x6640) != 0) {
      sbr_envelope_unmapping(iVar2,iVar1);
      goto LAB_ram_4202826c;
    }
  }
  else {
    iVar1 = 1;
    *(undefined4 *)(param_1 + 4) = 1;
LAB_ram_42028380:
    if (param_7 == 2) {
      param_8[1] = 1;
    }
    else if ((param_7 == 1) || (*(int *)(param_9 + 0x8c) < 2)) {
      param_8[1] = 0;
    }
    else {
      param_8[1] = 1;
    }
LAB_ram_42028398:
    if (param_2[2] == 1) {
      if (iVar1 != 2) {
        init_sbr_dec(*param_8 >> 1,*(undefined4 *)(param_9 + 0xb0),param_8,param_1 + 8);
        if (*(int *)(param_1 + 0x64c4) != 2) {
          init_sbr_dec(*param_8 >> 1,*(undefined4 *)(param_9 + 0xb0),param_8,param_1 + 0x64c8);
        }
        goto LAB_ram_4202826c;
      }
      goto LAB_ram_420283fa;
    }
    if (iVar1 != 2) {
      init_sbr_dec(*param_8 >> 1,*(undefined4 *)(param_9 + 0xb0),param_8,param_1 + 8);
      goto LAB_ram_4202826c;
    }
LAB_ram_420284b6:
    iVar1 = param_1 + 8;
    sbr_decode_envelope(iVar1);
    decode_noise_floorlevels(iVar1);
    if (*(int *)(param_1 + 0x180) != 0) goto LAB_ram_4202826c;
  }
  sbr_requantize_envelope_data(iVar1);
LAB_ram_4202826c:
  iStack_28 = param_5 + 2;
  iStack_24 = param_6 + 2;
  iStack_30 = param_5;
  iStack_2c = param_6;
  if (*(int *)(param_9 + 0xc0) == 0) {
    *(int *)(param_1 + 0x3e3c) = param_9 + 0x4a58;
    *(int *)(param_1 + 0x39b8) = param_9 + 0x6a58;
    sbr_dec(param_3,&iStack_30,param_1 + 8,*(int *)(param_1 + 4) == 2,param_8,0,0,param_9);
    if (param_10 == 2) {
      *(int *)(param_1 + 0xa2fc) = param_9 + 0x4a58;
      *(int *)(param_1 + 0x9e78) = param_9 + 0x6a58;
      sbr_dec(param_4,&iStack_28,param_1 + 0x64c8,*(int *)(param_1 + 0x64c4) == 2,param_8,0,0,
              param_9);
    }
  }
  else {
    ps_bstr_decoding(*(undefined4 *)(param_1 + 0xc984));
    iVar2 = *(int *)(param_1 + 0xc984);
    iVar1 = *(int *)(param_1 + 4);
    uVar3 = *(undefined4 *)(param_9 + 0x8a78);
    *(int *)(iVar2 + 4) = param_1 + 0xa780;
    *(undefined4 *)(param_1 + 0x3e3c) = uVar3;
    *(int *)(param_1 + 0x39b8) = param_9 + 0x58b8;
    sbr_dec(param_3,&iStack_30,param_1 + 8,iVar1 == 2,param_8,&iStack_28,iVar2,param_9);
  }
  return 0;
}
