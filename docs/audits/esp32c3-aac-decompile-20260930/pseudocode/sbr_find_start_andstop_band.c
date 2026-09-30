/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: sbr_find_start_andstop_band @ ram:42048f76
 * Types and parameter counts are inferred; verify against disassembly. */

byte sbr_find_start_andstop_band
               (int param_1,undefined4 param_2,int param_3,int *param_4,int *param_5)

{
  byte bVar1;
  int iVar2;
  int iVar3;

  gp = &__global_pointer_;
  iVar2 = get_sbr_startfreq();
  *param_4 = iVar2;
  if (iVar2 == 0) {
    return 6;
  }
  if (param_3 < 0xd) {
    iVar3 = get_sbr_stopfreq(param_1,param_3);
    *param_5 = iVar3;
joined_r0x4204901c:
    if (iVar3 < 0x41) goto LAB_ram_42048fc0;
  }
  else if (param_3 != 0xd) {
    iVar3 = iVar2 * 3;
    if (param_3 == 0xe) {
      iVar3 = iVar2 * 2;
    }
    *param_5 = iVar3;
    goto joined_r0x4204901c;
  }
  *param_5 = 0x40;
  iVar3 = 0x40;
LAB_ram_42048fc0:
  bVar1 = 0xe;
  iVar3 = iVar3 - *param_4;
  if (iVar3 < 0x31) {
    if (param_1 == 0xac44) {
      return -(0x23 < iVar3) & 0xe;
    }
    if ((iVar3 < 0x21) || (param_1 < 48000)) {
      bVar1 = 0;
    }
  }
  return bVar1;
}
