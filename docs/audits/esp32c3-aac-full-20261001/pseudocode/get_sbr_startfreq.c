/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: get_sbr_startfreq @ ram:430084b2
 * Types and parameter counts are inferred; verify against disassembly. */

int get_sbr_startfreq(int param_1,int param_2)

{
  int iVar1;
  int iVar2;

  gp = &__global_pointer_;
  if (param_1 == 0xac44) {
    iVar2 = 4;
    iVar1 = 0xc;
    goto LAB_ram_4300850e;
  }
  if (param_1 < 0xac45) {
    if (param_1 == 24000) {
      iVar2 = 2;
      iVar1 = 0x10;
      goto LAB_ram_4300850e;
    }
    if (param_1 < 0x5dc1) {
      if (param_1 == 16000) {
        iVar2 = 0;
        iVar1 = 0x18;
        goto LAB_ram_4300850e;
      }
      if (param_1 == 0x5622) {
        iVar2 = 1;
        iVar1 = 0x11;
        goto LAB_ram_4300850e;
      }
    }
    else if (param_1 == 32000) {
      iVar2 = 3;
      iVar1 = 0x10;
      goto LAB_ram_4300850e;
    }
  }
  else {
    if (param_1 == 64000) {
      iVar2 = 4;
      iVar1 = 10;
      goto LAB_ram_4300850e;
    }
    if (param_1 < 0xfa01) {
      if (param_1 == 48000) {
        iVar2 = 4;
        iVar1 = 0xb;
        goto LAB_ram_4300850e;
      }
    }
    else if ((param_1 == 0x15888) || (param_1 == 96000)) {
      iVar2 = 5;
      iVar1 = 7;
      goto LAB_ram_4300850e;
    }
  }
  iVar2 = 6;
  iVar1 = 0;
LAB_ram_4300850e:
  return iVar1 + *(int *)(v_offset + (iVar2 * 0x10 + param_2) * 4);
}
