/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_extract_extended_data @ ram:43011ab8
 * Types and parameter counts are inferred; verify against disassembly. */

void sbr_extract_extended_data(undefined4 param_1,int *param_2)

{
  uint uVar1;
  int iVar2;

  gp = &__global_pointer_;
  iVar2 = buf_get_1bit();
  if (iVar2 == 0) {
    return;
  }
  iVar2 = buf_getbits(param_1,4);
  if (iVar2 == 0xf) {
    iVar2 = buf_getbits(param_1,8);
    iVar2 = iVar2 + 0xf;
  }
  uVar1 = iVar2 << 3;
LAB_ram_43011b0c:
  if (7 < (int)uVar1) {
    iVar2 = buf_getbits(param_1,2);
    uVar1 = uVar1 - 2;
    if (iVar2 == 2) {
      if (param_2 != (int *)0x0) {
        if (*param_2 == 0) {
          *param_2 = 1;
        }
        iVar2 = ps_read_data(param_2,param_1,uVar1);
        uVar1 = uVar1 - iVar2;
      }
      goto LAB_ram_43011b0c;
    }
    if ((int)uVar1 >> 3 != 0) {
      iVar2 = 0;
      do {
        iVar2 = iVar2 + 1;
        buf_getbits(param_1,8);
      } while ((int)uVar1 >> 3 != iVar2);
    }
    uVar1 = uVar1 & 7;
  }
  buf_getbits(param_1,uVar1);
  return;
}
