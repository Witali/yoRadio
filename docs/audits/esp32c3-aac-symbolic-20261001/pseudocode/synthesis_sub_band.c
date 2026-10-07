/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: synthesis_sub_band @ ram:43013ec2
 * Types and parameter counts are inferred; verify against disassembly. */

void synthesis_sub_band(int *param_1,int *param_2,undefined2 *param_3)

{
  undefined2 *puVar1;
  undefined2 *puVar2;
  int iVar3;
  int iVar4;
  int *piVar5;
  undefined2 *puVar6;
  int *piVar7;
  int *piVar8;
  int *piVar9;
  int *piVar10;
  int *piVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  int iVar16;
  int iVar17;

  gp = &__global_pointer_;
  iVar3 = *param_1;
  piVar5 = param_2 + 0x3f;
  piVar7 = param_1 + 0x3f;
  piVar8 = param_2;
  piVar9 = param_1;
  piVar10 = &CosTable_64;
  do {
    iVar13 = *piVar10;
    iVar16 = *piVar5;
    piVar11 = piVar10 + 2;
    *piVar9 = (int)((ulonglong)((longlong)iVar3 * (longlong)iVar13) >> 0x20);
    iVar14 = *piVar8;
    *piVar8 = (int)((ulonglong)((longlong)iVar16 * (longlong)iVar13) >> 0x20);
    iVar13 = piVar10[1];
    iVar3 = *piVar7;
    *piVar5 = (int)((ulonglong)((longlong)iVar13 * (longlong)iVar14) >> 0x20);
    *piVar7 = (int)((ulonglong)((longlong)iVar3 * (longlong)iVar13) >> 0x20);
    iVar3 = piVar9[1];
    piVar5 = piVar5 + -1;
    piVar7 = piVar7 + -1;
    piVar8 = piVar8 + 1;
    piVar9 = piVar9 + 1;
    piVar10 = piVar11;
  } while (piVar11 != (int *)tns_table);
  dct_64(param_1,param_3);
  dct_64(param_2,param_3);
  iVar16 = *param_1;
  iVar14 = param_1[1];
  iVar13 = *param_2;
  iVar3 = param_2[1];
  puVar1 = param_3;
  puVar6 = param_3 + 0x7f;
  do {
    iVar17 = iVar13 - iVar16;
    iVar12 = iVar14 + iVar3;
    iVar15 = iVar16 + iVar13;
    iVar16 = param_1[2];
    iVar13 = param_2[2];
    iVar4 = iVar14 - iVar3;
    puVar2 = puVar1 + 2;
    iVar14 = param_1[3];
    iVar3 = param_2[3];
    *puVar1 = (short)((ulonglong)((longlong)iVar17 * 0x624dd3) >> 0x20);
    puVar1[1] = (short)((ulonglong)((longlong)-iVar12 * 0x624dd3) >> 0x20);
    *puVar6 = (short)((ulonglong)((longlong)iVar15 * 0x624dd3) >> 0x20);
    puVar6[-1] = (short)((ulonglong)((longlong)iVar4 * 0x624dd3) >> 0x20);
    puVar1 = puVar2;
    puVar6 = puVar6 + -2;
    param_2 = param_2 + 2;
    param_1 = param_1 + 2;
  } while (puVar2 != param_3 + 0x40);
  return;
}
