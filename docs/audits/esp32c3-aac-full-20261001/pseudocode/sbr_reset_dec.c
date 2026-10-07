/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_reset_dec @ ram:4301376a
 * Types and parameter counts are inferred; verify against disassembly. */

int sbr_reset_dec(int param_1,undefined4 *param_2,int param_3)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  undefined4 *puVar4;
  undefined4 *puVar5;
  undefined4 *puVar6;
  uint uVar7;
  undefined4 uStack_28;
  int aiStack_24 [3];

  gp = &__global_pointer_;
  uVar1 = *param_2;
  *(undefined4 *)(param_1 + 0xbc) = 1;
  iVar2 = sbr_find_start_andstop_band
                    (uVar1,*(undefined4 *)(param_1 + 0xd4),*(undefined4 *)(param_1 + 0xd8),
                     &uStack_28,aiStack_24);
  if (iVar2 != 0) {
    return iVar2;
  }
  if (*(int *)(param_1 + 0xc4) == 1) {
    sbr_update_freq_scale
              (param_2 + 0x89,param_2 + 199,uStack_28,aiStack_24[0],*(undefined4 *)(param_1 + 0xe0),
               *(undefined4 *)(param_1 + 0xe4),0);
  }
  iVar3 = *(int *)(param_1 + 0xdc);
  iVar2 = param_2[199];
  uVar7 = iVar2 - iVar3;
  param_2[0xc5] = uVar7;
  if (iVar3 <= iVar2) {
    memcpy(param_2 + 0x48,param_2 + iVar3 + 0x89,((iVar2 + 1) - iVar3) * 4);
  }
  if ((uVar7 & 1) == 0) {
    iVar3 = (int)uVar7 >> 1;
    param_2[0xc4] = iVar3;
    if (-1 < iVar3) {
      puVar4 = param_2 + 0x48;
      puVar6 = param_2 + 0xd;
      do {
        uVar1 = *puVar4;
        puVar5 = puVar6 + 1;
        puVar4 = puVar4 + 2;
        *puVar6 = uVar1;
        puVar6 = puVar5;
      } while (param_2 + iVar3 + 0xe != puVar5);
    }
    iVar2 = param_2[0xd];
  }
  else {
    iVar2 = param_2[0x48];
    iVar3 = (int)(uVar7 + 1) >> 1;
    param_2[0xc4] = iVar3;
    param_2[0xd] = iVar2;
    if (0 < iVar3) {
      puVar4 = param_2 + 0x49;
      puVar6 = param_2;
      do {
        uVar1 = *puVar4;
        puVar5 = puVar6 + 1;
        puVar4 = puVar4 + 2;
        puVar6[0xe] = uVar1;
        puVar6 = puVar5;
      } while (puVar5 != (undefined4 *)((int)param_2 + (uVar7 + 1) * 2));
    }
  }
  aiStack_24[0] = param_2[iVar3 + 0xd];
  param_2[9] = iVar2;
  param_2[0xb] = aiStack_24[0];
  param_2[0xc] = aiStack_24[0] - iVar2;
  if ((aiStack_24[0] - iVar2 < 1) || (0x20 < iVar2)) {
LAB_ram_430138ec:
    iVar2 = 6;
  }
  else {
    if (*(int *)(param_1 + 0xe8) == 0) {
LAB_ram_4301385e:
      iVar2 = 1;
      param_2[0xc6] = 1;
    }
    else {
      if (iVar2 == 0) goto LAB_ram_430138ec;
      iVar2 = pv_log2((aiStack_24[0] << 0x14) / iVar2);
      iVar3 = param_2[0xc4];
      iVar2 = (int)(((uint)(iVar2 * *(int *)(param_1 + 0xe8)) >> 0xf) +
                    (int)((ulonglong)((longlong)iVar2 * (longlong)*(int *)(param_1 + 0xe8)) >> 0x20)
                    * 0x20000 + 0x10) >> 5;
      param_2[0xc6] = iVar2;
      if (iVar2 == 0) goto LAB_ram_4301385e;
    }
    *(int *)(param_1 + 0xec) = iVar2;
    sbr_downsample_lo_res(param_2 + 0x83,iVar2,param_2 + 0xd,iVar3);
    iVar2 = param_2[9];
    if (param_3 << 5 < (int)param_2[9]) {
      iVar2 = param_3 << 5;
    }
    iVar3 = param_2[0xc4];
    param_2[8] = iVar2;
    iVar2 = param_2[0xc5];
    *(int *)(param_1 + 0x9c) = iVar3;
    *(int *)(param_1 + 0xa8) = iVar3 * 2 - iVar2;
    *(int *)(param_1 + 0xa0) = iVar2;
    *(undefined4 *)(param_1 + 0xa4) = *(undefined4 *)(param_1 + 0xec);
    iVar2 = 0;
  }
  return iVar2;
}
