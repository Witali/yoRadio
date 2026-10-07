/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: init_sbr_dec @ ram:4300a376
 * Types and parameter counts are inferred; verify against disassembly. */

int init_sbr_dec(int param_1,int param_2,int *param_3,int param_4)

{
  int iVar1;
  int *piVar2;
  undefined4 uVar3;

  gp = &__global_pointer_;
  uVar3 = *(undefined4 *)(param_4 + 0xec);
  *param_3 = param_1 << 1;
  param_3[8] = param_2 << 5;
  param_3[10] = param_2 << 5;
  *(undefined4 *)(param_4 + 0xa4) = uVar3;
  *(undefined4 *)(param_4 + 0x9c) = 0;
  *(undefined4 *)(param_4 + 0xa0) = 0;
  *(undefined4 *)(param_4 + 0xa8) = 0;
  *(undefined4 *)(param_4 + 0xb8) = 0xffffffff;
  iVar1 = param_4 + 0x4cb8;
  piVar2 = (int *)(param_4 + 0x60b8);
  do {
    *piVar2 = iVar1;
    piVar2[0x40] = iVar1 + 0xa00;
    piVar2[0xc0] = iVar1 + 0xf00;
    piVar2[0x80] = iVar1 + 0x500;
    piVar2 = piVar2 + 1;
    iVar1 = iVar1 + 0x100;
  } while (piVar2 != (int *)(param_4 + 0x60cc));
  *(undefined4 *)(param_4 + 0x150) = 0;
  *(undefined4 *)(param_4 + 0x154) = 0;
  *(undefined4 *)(param_4 + 0x158) = 0;
  *(undefined4 *)(param_4 + 0x15c) = 0;
  *(undefined4 *)(param_4 + 0x160) = 0;
  *(undefined4 *)(param_4 + 0x164) = 0;
  *(undefined4 *)(param_4 + 0x168) = 0;
  *(undefined4 *)(param_4 + 0x16c) = 0;
  *(undefined4 *)(param_4 + 0x170) = 0;
  *(undefined4 *)(param_4 + 0x174) = 0;
  param_3[2] = 0;
  param_3[4] = 0x20;
  param_3[9] = 0x20;
  param_3[6] = 8;
  param_3[7] = 2;
  param_3[5] = 0x28;
  param_3[3] = 0x120;
  return param_2 << 10;
}
