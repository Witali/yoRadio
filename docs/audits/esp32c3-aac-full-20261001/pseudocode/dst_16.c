/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: dst_16 @ ram:43005704
 * Types and parameter counts are inferred; verify against disassembly. */

void dst_16(int *param_1,int *param_2)

{
  int iVar1;
  int iVar2;
  int *piVar3;
  int *piVar4;
  int iVar5;
  int *piVar6;
  int *piVar7;
  int iVar8;
  int *piVar9;

  gp = &__global_pointer_;
  iVar2 = param_1[0xf];
  *param_2 = *param_1;
  *param_1 = param_1[1];
  piVar4 = param_1 + 1;
  piVar3 = param_2 + 1;
  piVar6 = param_1 + 2;
  iVar1 = param_1[1];
  do {
    piVar9 = piVar3 + 2;
    *piVar3 = *piVar6;
    iVar5 = piVar6[1];
    piVar3[1] = piVar6[2];
    iVar8 = piVar6[3];
    *piVar4 = iVar1 + iVar5;
    piVar4[1] = iVar5 + iVar8;
    piVar4 = piVar4 + 2;
    piVar3 = piVar9;
    piVar6 = piVar6 + 4;
    iVar1 = iVar8;
  } while (piVar9 != param_2 + 7);
  param_2[7] = param_1[0xe];
  param_1[7] = param_1[0xf] + iVar8;
  dst_8(param_2);
  dst_8(param_1);
  iVar1 = param_2[7];
  piVar3 = param_1 + 8;
  piVar6 = param_2 + 6;
  piVar4 = (int *)(CosTable_8 + 0x1c);
  piVar9 = param_1 + 7;
  do {
    iVar5 = *piVar6;
    iVar8 = *piVar9 - (iVar2 >> 1);
    piVar7 = piVar6 + -2;
    iVar8 = ((uint)(iVar8 * *piVar4) >> 0x1c) +
            (int)((ulonglong)((longlong)iVar8 * (longlong)*piVar4) >> 0x20) * 0x10;
    *piVar9 = iVar8 + iVar1;
    *piVar3 = iVar8 - iVar1;
    iVar1 = piVar6[-1];
    iVar8 = piVar9[-1] + (iVar2 >> 1);
    iVar8 = ((uint)(iVar8 * piVar4[-1]) >> 0x1c) +
            (int)((ulonglong)((longlong)iVar8 * (longlong)piVar4[-1]) >> 0x20) * 0x10;
    piVar3[1] = iVar8 - iVar5;
    piVar9[-1] = iVar5 + iVar8;
    piVar3 = piVar3 + 2;
    piVar6 = piVar7;
    piVar4 = piVar4 + -2;
    piVar9 = piVar9 + -2;
  } while (piVar7 != param_2 + -2);
  return;
}
