/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: synthesis_sub_band_LC_down_sampled @ ram:43013e58
 * Types and parameter counts are inferred; verify against disassembly. */

void synthesis_sub_band_LC_down_sampled(int *param_1,undefined2 *param_2)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  undefined2 *puVar5;
  int *piVar6;

  gp = &__global_pointer_;
  dct_32();
  piVar1 = param_1 + 0x10;
  piVar4 = param_1;
  puVar5 = param_2;
  piVar6 = piVar1;
  do {
    iVar2 = *piVar4;
    iVar3 = piVar4[0x10];
    *puVar5 = (short)(*piVar6 >> 5);
    puVar5[0x10] = (short)(iVar2 >> 5);
    puVar5[0x20] = (short)(iVar3 >> 5);
    piVar4 = piVar4 + 1;
    piVar6 = piVar6 + -1;
    puVar5 = puVar5 + 1;
  } while (piVar4 != piVar1);
  param_1 = param_1 + 0x1f;
  puVar5 = param_2 + 0x31;
  do {
    iVar2 = *param_1;
    param_1 = param_1 + -1;
    *puVar5 = (short)(-iVar2 >> 5);
    puVar5 = puVar5 + 1;
  } while (piVar1 != param_1);
  param_2[0x30] = 0;
  return;
}
