/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: sbr_get_dir_control_data @ ram:42049212
 * Types and parameter counts are inferred; verify against disassembly. */

void sbr_get_dir_control_data(int param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 *puVar2;
  undefined4 uVar3;

  gp = &__global_pointer_;
  if (*(int *)(param_1 + 0x10) < 2) {
    *(undefined4 *)(param_1 + 0xb0) = 1;
    if (*(int *)(param_1 + 0x10) != 1) goto LAB_ram_42049254;
  }
  else {
    *(undefined4 *)(param_1 + 0xb0) = 2;
  }
  puVar2 = (undefined4 *)(param_1 + 0x100);
  iVar1 = 0;
  do {
    uVar3 = buf_getbits(param_2,1);
    *puVar2 = uVar3;
    iVar1 = iVar1 + 1;
    puVar2 = puVar2 + 1;
  } while (iVar1 < *(int *)(param_1 + 0x10));
  if (*(int *)(param_1 + 0xb0) < 1) {
    return;
  }
LAB_ram_42049254:
  puVar2 = (undefined4 *)(param_1 + 0x114);
  iVar1 = 0;
  do {
    uVar3 = buf_getbits(param_2,1);
    *puVar2 = uVar3;
    iVar1 = iVar1 + 1;
    puVar2 = puVar2 + 1;
  } while (iVar1 < *(int *)(param_1 + 0xb0));
  return;
}
