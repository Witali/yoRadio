/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_get_additional_data @ ram:430129bc
 * Types and parameter counts are inferred; verify against disassembly. */

void sbr_get_additional_data(int param_1,undefined4 param_2)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;

  gp = &__global_pointer_;
  iVar2 = buf_getbits(param_2,1);
  if ((iVar2 != 0) && (0 < *(int *)(param_1 + 0xa0))) {
    iVar2 = 0;
    puVar1 = (undefined4 *)(param_1 + 0x17c);
    do {
      uVar3 = buf_getbits(param_2,1);
      *puVar1 = uVar3;
      iVar2 = iVar2 + 1;
      puVar1 = puVar1 + 1;
    } while (iVar2 < *(int *)(param_1 + 0xa0));
  }
  return;
}
