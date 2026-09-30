/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: dst_32 @ ram:420570ca
 * Types and parameter counts are inferred; verify against disassembly. */

void dst_32(int *param_1,int *param_2)

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
  int *piVar10;
  int *piVar11;
  int *piVar12;
  int iVar13;

  gp = &__global_pointer_;
  iVar1 = param_1[0x1f] >> 1;
  iVar8 = 0;
  piVar3 = param_1;
  piVar6 = param_2;
  piVar12 = param_1;
  do {
    piVar10 = piVar6 + 3;
    *piVar6 = *piVar12;
    iVar2 = piVar12[1];
    piVar6[1] = piVar12[2];
    iVar5 = piVar12[3];
    piVar6[2] = piVar12[4];
    *piVar3 = iVar8 + iVar2;
    piVar3[1] = iVar2 + iVar5;
    iVar8 = piVar12[5];
    piVar3[2] = iVar5 + iVar8;
    piVar3 = piVar3 + 3;
    piVar6 = piVar10;
    piVar12 = piVar12 + 6;
  } while (piVar10 != param_2 + 0xf);
  param_2[0xf] = param_1[0x1e];
  param_1[0xf] = param_1[0x1f] + iVar8;
  dst_16(param_2,param_2 + 0x10);
  dst_16(param_1,param_2 + 0x18);
  iVar2 = param_2[0xf];
  iVar13 = param_2[0xe];
  iVar8 = (int)((ulonglong)((longlong)((param_1[0xe] + iVar1) * 8) * 0x6d0b2100) >> 0x20);
  iVar5 = (int)((ulonglong)((longlong)((param_1[0xf] - iVar1) * 8) * 0x51852300) >> 0x20) * 4;
  param_1[0xf] = iVar2 + iVar5;
  param_1[0x10] = iVar5 - iVar2;
  iVar2 = param_2[0xd];
  param_1[0x11] = iVar8 - iVar13;
  param_1[0xe] = iVar13 + iVar8;
  piVar3 = param_1 + 0x12;
  piVar6 = param_2 + 0xc;
  piVar12 = (int *)(CosTable_16 + 0x34);
  piVar10 = param_1 + 0xd;
  do {
    piVar9 = piVar12;
    iVar8 = *piVar6;
    piVar7 = piVar6 + -2;
    piVar11 = piVar10 + -2;
    piVar4 = piVar3 + 2;
    iVar5 = ((uint)((*piVar10 - iVar1) * *piVar9) >> 0x1d) +
            (int)((ulonglong)((longlong)(*piVar10 - iVar1) * (longlong)*piVar9) >> 0x20) * 8;
    *piVar10 = iVar5 + iVar2;
    *piVar3 = iVar5 - iVar2;
    iVar2 = piVar6[-1];
    iVar5 = ((uint)((piVar10[-1] + iVar1) * piVar9[-1]) >> 0x1d) +
            (int)((ulonglong)((longlong)(piVar10[-1] + iVar1) * (longlong)piVar9[-1]) >> 0x20) * 8;
    piVar10[-1] = iVar8 + iVar5;
    piVar3[1] = iVar5 - iVar8;
    piVar3 = piVar4;
    piVar6 = piVar7;
    piVar12 = piVar9 + -2;
    piVar10 = piVar11;
  } while (piVar7 != param_2 + 8);
  piVar3 = piVar9 + -2;
  do {
    iVar8 = *piVar7;
    iVar5 = (int)((ulonglong)((longlong)((*piVar11 - iVar1) * 2) * (longlong)*piVar3) >> 0x20);
    piVar6 = piVar3 + -2;
    *piVar11 = iVar5 + iVar2;
    *piVar4 = iVar5 - iVar2;
    iVar5 = (int)((ulonglong)((longlong)((piVar11[-1] + iVar1) * 2) * (longlong)piVar3[-1]) >> 0x20)
    ;
    iVar2 = piVar7[-1];
    piVar11[-1] = iVar8 + iVar5;
    piVar4[1] = iVar5 - iVar8;
    piVar4 = piVar4 + 2;
    piVar7 = piVar7 + -2;
    piVar3 = piVar6;
    piVar11 = piVar11 + -2;
  } while (piVar6 != piVar9 + -0xc);
  return;
}
