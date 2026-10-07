/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: idct_32 @ ram:43009c02
 * Types and parameter counts are inferred; verify against disassembly. */

void idct_32(int *param_1,int *param_2)

{
  int *piVar1;
  int *piVar2;
  int *piVar3;
  int *piVar4;
  int iVar5;
  int *piVar6;
  int iVar7;
  int *piVar8;
  int *piVar9;
  int *piVar10;
  int iVar11;
  int iVar12;

  gp = &__global_pointer_;
  *param_2 = *param_1;
  iVar5 = param_1[1];
  iVar7 = 0;
  piVar1 = param_1;
  piVar3 = param_2 + 1;
  piVar10 = param_1 + 2;
  do {
    *piVar1 = iVar7 + iVar5;
    piVar8 = piVar3 + 2;
    *piVar3 = *piVar10;
    iVar7 = piVar10[1];
    piVar3[1] = piVar10[2];
    piVar1[1] = iVar5 + iVar7;
    iVar5 = piVar10[3];
    piVar1 = piVar1 + 2;
    piVar3 = piVar8;
    piVar10 = piVar10 + 4;
  } while (piVar8 != param_2 + 0xf);
  param_1[0xe] = iVar7 + iVar5;
  param_2[0xf] = param_1[0x1e];
  param_1[0xf] = param_1[0x1f] + iVar5;
  idct_16(param_2,param_2 + 0x10);
  idct_16(param_1,param_2 + 0x18);
  iVar11 = (int)((ulonglong)((longlong)(param_1[0xf] << 3) * 0x51852300) >> 0x20);
  iVar7 = param_2[0xf];
  iVar12 = param_2[0xe];
  iVar5 = (int)((ulonglong)((longlong)(param_1[0xe] << 3) * 0x6d0b2100) >> 0x20);
  param_1[0xf] = iVar7 + iVar11 * 4;
  param_1[0x10] = iVar7 + iVar11 * -4;
  iVar7 = param_2[0xd];
  param_1[0x11] = iVar12 - iVar5;
  param_1[0xe] = iVar12 + iVar5;
  piVar1 = param_1 + 0x12;
  piVar3 = param_2 + 0xc;
  piVar10 = (int *)(CosTable_16 + 0x34);
  piVar8 = param_1 + 0xd;
  do {
    piVar6 = piVar10;
    iVar11 = *piVar3;
    piVar4 = piVar3 + -2;
    piVar2 = piVar1 + 2;
    piVar9 = piVar8 + -2;
    iVar5 = ((uint)(*piVar8 * *piVar6) >> 0x1d) +
            (int)((ulonglong)((longlong)*piVar8 * (longlong)*piVar6) >> 0x20) * 8;
    *piVar1 = iVar7 - iVar5;
    *piVar8 = iVar5 + iVar7;
    iVar7 = piVar3[-1];
    iVar5 = ((uint)(piVar8[-1] * piVar6[-1]) >> 0x1d) +
            (int)((ulonglong)((longlong)piVar8[-1] * (longlong)piVar6[-1]) >> 0x20) * 8;
    piVar1[1] = iVar11 - iVar5;
    piVar8[-1] = iVar11 + iVar5;
    piVar1 = piVar2;
    piVar3 = piVar4;
    piVar10 = piVar6 + -2;
    piVar8 = piVar9;
  } while (piVar4 != param_2 + 8);
  piVar1 = piVar6 + -2;
  do {
    iVar5 = *piVar4;
    iVar11 = (int)((ulonglong)((longlong)(*piVar9 << 1) * (longlong)*piVar1) >> 0x20);
    piVar3 = piVar1 + -2;
    *piVar2 = iVar7 - iVar11;
    *piVar9 = iVar11 + iVar7;
    iVar11 = (int)((ulonglong)((longlong)(piVar9[-1] << 1) * (longlong)piVar1[-1]) >> 0x20);
    iVar7 = piVar4[-1];
    piVar2[1] = iVar5 - iVar11;
    piVar9[-1] = iVar5 + iVar11;
    piVar2 = piVar2 + 2;
    piVar4 = piVar4 + -2;
    piVar1 = piVar3;
    piVar9 = piVar9 + -2;
  } while (piVar3 != piVar6 + -0xc);
  return;
}
