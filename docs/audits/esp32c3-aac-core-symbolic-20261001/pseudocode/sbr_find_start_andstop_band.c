/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_find_start_andstop_band @ ram:43011b7c
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
joined_r0x43011c2a:
    if (iVar3 < 0x41) goto LAB_ram_43011bca;
  }
  else if (param_3 != 0xd) {
    iVar3 = iVar2 * 3;
    if (param_3 == 0xe) {
      iVar3 = iVar2 * 2;
    }
    *param_5 = iVar3;
    goto joined_r0x43011c2a;
  }
  *param_5 = 0x40;
  iVar3 = 0x40;
LAB_ram_43011bca:
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
