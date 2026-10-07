/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: pv_split_z @ ram:430042ac
 * Types and parameter counts are inferred; verify against disassembly. */

void pv_split_z(int *param_1)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  int *piVar4;
  int *piVar5;
  int iVar6;

  gp = &__global_pointer_;
  piVar1 = param_1;
  piVar2 = (int *)(CosTable_48 + 0x80);
  piVar4 = param_1 + 0x1f;
  do {
    iVar6 = *piVar2;
    iVar3 = *piVar4 - *piVar1;
    *piVar1 = *piVar4 + *piVar1;
    piVar5 = piVar4 + -2;
    *piVar4 = ((uint)(iVar3 * iVar6) >> 0x1a) +
              (int)((ulonglong)((longlong)iVar3 * (longlong)iVar6) >> 0x20) * 0x40;
    iVar6 = piVar2[1];
    iVar3 = piVar4[-1] - piVar1[1];
    piVar1[1] = piVar1[1] + piVar4[-1];
    piVar4[-1] = ((uint)(iVar3 * iVar6) >> 0x1a) +
                 (int)((ulonglong)((longlong)iVar3 * (longlong)iVar6) >> 0x20) * 0x40;
    piVar1 = piVar1 + 2;
    piVar2 = piVar2 + 2;
    piVar4 = piVar5;
  } while (piVar5 != param_1 + 0xf);
  return;
}
