/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: get_sbr_startfreq @ ram:42058688
 * Types and parameter counts are inferred; verify against disassembly. */

int get_sbr_startfreq(int param_1,int param_2)

{
  int iVar1;
  int iVar2;

  gp = &__global_pointer_;
  if (param_1 == 0xac44) {
    iVar2 = 4;
    iVar1 = 0xc;
    goto LAB_ram_420586e4;
  }
  if (param_1 < 0xac45) {
    if (param_1 == 24000) {
      iVar2 = 2;
      iVar1 = 0x10;
      goto LAB_ram_420586e4;
    }
    if (param_1 < 0x5dc1) {
      if (param_1 == 16000) {
        iVar2 = 0;
        iVar1 = 0x18;
        goto LAB_ram_420586e4;
      }
      if (param_1 == 0x5622) {
        iVar2 = 1;
        iVar1 = 0x11;
        goto LAB_ram_420586e4;
      }
    }
    else if (param_1 == 32000) {
      iVar2 = 3;
      iVar1 = 0x10;
      goto LAB_ram_420586e4;
    }
  }
  else {
    if (param_1 == 64000) {
      iVar2 = 4;
      iVar1 = 10;
      goto LAB_ram_420586e4;
    }
    if (param_1 < 0xfa01) {
      if (param_1 == 48000) {
        iVar2 = 4;
        iVar1 = 0xb;
        goto LAB_ram_420586e4;
      }
    }
    else if ((param_1 == 0x15888) || (param_1 == 96000)) {
      iVar2 = 5;
      iVar1 = 7;
      goto LAB_ram_420586e4;
    }
  }
  iVar2 = 6;
  iVar1 = 0;
LAB_ram_420586e4:
  return iVar1 + *(int *)(v_offset + (iVar2 * 0x10 + param_2) * 4);
}
