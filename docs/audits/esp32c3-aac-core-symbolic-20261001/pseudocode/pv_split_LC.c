/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: pv_split_LC @ ram:430041fa
 * Types and parameter counts are inferred; verify against disassembly. */

void pv_split_LC(int *param_1,int *param_2)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  int *piVar4;
  int iVar5;

  gp = &__global_pointer_;
  iVar3 = *param_1;
  iVar5 = param_1[0x1f];
  piVar2 = (int *)(CosTable_48 + 0x80);
  piVar4 = param_1 + 0x1e;
  do {
    iVar1 = *piVar2;
    *param_1 = iVar3 + iVar5;
    piVar2 = piVar2 + 1;
    *param_2 = ((uint)((iVar3 - iVar5) * iVar1) >> 0x1a) +
               (int)((ulonglong)((longlong)(iVar3 - iVar5) * (longlong)iVar1) >> 0x20) * 0x40;
    iVar3 = param_1[1];
    iVar5 = *piVar4;
    param_1 = param_1 + 1;
    param_2 = param_2 + 1;
    piVar4 = piVar4 + -1;
  } while (piVar2 != (int *)&digit_reverse_swap_256);
  return;
}
