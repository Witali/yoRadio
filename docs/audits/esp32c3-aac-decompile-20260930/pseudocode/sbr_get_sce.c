/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: sbr_get_sce @ ram:420496ce
 * Types and parameter counts are inferred; verify against disassembly. */

int sbr_get_sce(int param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;

  gp = &__global_pointer_;
  iVar2 = buf_getbits(param_2,1);
  if (iVar2 != 0) {
    buf_getbits(param_2,4);
  }
  iVar2 = extractFrameInfo(param_2,param_1);
  if (iVar2 == 0) {
    sbr_get_dir_control_data(param_1,param_2);
    if (0 < *(int *)(param_1 + 0xa4)) {
      puVar1 = (undefined4 *)(param_1 + 0x128);
      iVar2 = 0;
      do {
        puVar1[10] = *puVar1;
        uVar3 = buf_getbits(param_2,2);
        iVar4 = *(int *)(param_1 + 0xa4);
        iVar2 = iVar2 + 1;
        *puVar1 = uVar3;
        puVar1 = puVar1 + 1;
      } while (iVar2 < iVar4);
    }
    sbr_get_envelope(param_1,param_2);
    sbr_get_noise_floor_data(param_1,param_2);
    memset(param_1 + 0x17c,0,*(int *)(param_1 + 0xa0) << 2);
    sbr_get_additional_data(param_1,param_2);
    sbr_extract_extended_data(param_2,param_3);
    *(undefined4 *)(param_1 + 0x178) = 0;
    return 0;
  }
  return iVar2;
}
