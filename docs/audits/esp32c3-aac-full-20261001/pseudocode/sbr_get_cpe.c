/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_get_cpe @ ram:43012a10
 * Types and parameter counts are inferred; verify against disassembly. */

int sbr_get_cpe(int param_1,int param_2,undefined4 param_3)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined4 *puVar7;
  int iVar8;
  int iVar9;

  gp = &__global_pointer_;
  iVar3 = buf_getbits(param_3,1);
  if (iVar3 != 0) {
    buf_getbits(param_3,4);
    buf_getbits(param_3,4);
  }
  iVar3 = buf_getbits(param_3,1);
  uVar4 = 0;
  if (iVar3 != 0) {
    uVar4 = 2;
  }
  *(uint *)(param_1 + 0x178) = (uint)(iVar3 != 0);
  *(undefined4 *)(param_2 + 0x178) = uVar4;
  iVar3 = extractFrameInfo(param_3,param_1);
  if (iVar3 == 0) {
    if (*(int *)(param_1 + 0x178) == 0) {
      iVar9 = extractFrameInfo(param_3,param_2);
      if (iVar9 != 0) {
        return iVar9;
      }
      sbr_get_dir_control_data(param_1,param_3);
      sbr_get_dir_control_data(param_2,param_3);
      if (0 < *(int *)(param_1 + 0xa4)) {
        puVar2 = (undefined4 *)(param_1 + 0x128);
        iVar9 = 0;
        do {
          puVar2[10] = *puVar2;
          uVar4 = buf_getbits(param_3,2);
          iVar8 = *(int *)(param_1 + 0xa4);
          iVar9 = iVar9 + 1;
          *puVar2 = uVar4;
          puVar2 = puVar2 + 1;
        } while (iVar9 < iVar8);
      }
      if (0 < *(int *)(param_2 + 0xa4)) {
        puVar2 = (undefined4 *)(param_2 + 0x128);
        iVar9 = 0;
        do {
          puVar2[10] = *puVar2;
          uVar4 = buf_getbits(param_3,2);
          iVar8 = *(int *)(param_2 + 0xa4);
          iVar9 = iVar9 + 1;
          *puVar2 = uVar4;
          puVar2 = puVar2 + 1;
        } while (iVar9 < iVar8);
      }
      sbr_get_envelope(param_1,param_3);
      sbr_get_envelope(param_2,param_3);
      sbr_get_noise_floor_data(param_1,param_3);
    }
    else {
      puVar7 = (undefined4 *)(param_1 + 0x10);
      puVar2 = (undefined4 *)(param_2 + 0x10);
      do {
        uVar6 = puVar7[3];
        uVar4 = puVar7[1];
        uVar5 = puVar7[2];
        *puVar2 = *puVar7;
        puVar2[1] = uVar4;
        puVar2[2] = uVar5;
        puVar2[3] = uVar6;
        puVar1 = puVar7 + 4;
        puVar7 = puVar7 + 5;
        puVar2[4] = *puVar1;
        puVar2 = puVar2 + 5;
      } while (puVar7 != (undefined4 *)(param_1 + 0x9c));
      uVar4 = *(undefined4 *)(param_1 + 0xb0);
      *(undefined4 *)(param_2 + 0xc) = *(undefined4 *)(param_1 + 0xc);
      *(undefined4 *)(param_2 + 0xb0) = uVar4;
      sbr_get_dir_control_data(param_1,param_3);
      sbr_get_dir_control_data(param_2,param_3);
      if (0 < *(int *)(param_1 + 0xa4)) {
        puVar7 = (undefined4 *)(param_2 + 0x128);
        iVar9 = 0;
        puVar2 = (undefined4 *)(param_1 + 0x128);
        do {
          puVar2[10] = *puVar2;
          iVar9 = iVar9 + 1;
          puVar7[10] = *puVar7;
          uVar4 = buf_getbits(param_3,2);
          iVar8 = *(int *)(param_1 + 0xa4);
          *puVar2 = uVar4;
          *puVar7 = uVar4;
          puVar7 = puVar7 + 1;
          puVar2 = puVar2 + 1;
        } while (iVar9 < iVar8);
      }
      sbr_get_envelope(param_1,param_3);
      sbr_get_noise_floor_data(param_1,param_3);
      sbr_get_envelope(param_2,param_3);
    }
    sbr_get_noise_floor_data(param_2,param_3);
    memset(param_1 + 0x17c,0,*(int *)(param_1 + 0xa0) << 2);
    memset(param_2 + 0x17c,0,*(int *)(param_2 + 0xa0) << 2);
    sbr_get_additional_data(param_1,param_3);
    sbr_get_additional_data(param_2,param_3);
    sbr_extract_extended_data(param_3,0);
  }
  return iVar3;
}
