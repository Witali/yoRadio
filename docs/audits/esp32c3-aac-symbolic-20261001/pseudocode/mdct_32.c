/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: mdct_32 @ ram:4300b5d4
 * Types and parameter counts are inferred; verify against disassembly. */

void mdct_32(int *param_1)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int *piVar7;
  int iVar8;
  int *piVar9;
  int iVar10;

  gp = &__global_pointer_;
  piVar1 = &CosTable_32;
  piVar7 = param_1;
  do {
    piVar9 = piVar7 + 4;
    *piVar7 = (int)((ulonglong)((longlong)(*piVar7 << 1) * (longlong)*piVar1) >> 0x20);
    piVar7[1] = (int)((ulonglong)((longlong)(piVar7[1] << 1) * (longlong)piVar1[1]) >> 0x20);
    piVar7[2] = (int)((ulonglong)((longlong)(piVar7[2] << 1) * (longlong)piVar1[2]) >> 0x20);
    piVar7[3] = (int)((ulonglong)((longlong)(piVar7[3] << 1) * (longlong)piVar1[3]) >> 0x20);
    piVar1 = piVar1 + 4;
    piVar7 = piVar9;
  } while (piVar9 != param_1 + 0x14);
  piVar1 = &DAT_ram_4301bbd0;
  piVar7 = param_1 + 0x14;
  do {
    piVar9 = piVar7 + 4;
    *piVar7 = ((uint)(*piVar7 * *piVar1) >> 0x1b) +
              (int)((ulonglong)((longlong)*piVar7 * (longlong)*piVar1) >> 0x20) * 0x20;
    piVar7[1] = ((uint)(piVar7[1] * piVar1[1]) >> 0x1b) +
                (int)((ulonglong)((longlong)piVar7[1] * (longlong)piVar1[1]) >> 0x20) * 0x20;
    piVar7[2] = ((uint)(piVar7[2] * piVar1[2]) >> 0x1b) +
                (int)((ulonglong)((longlong)piVar7[2] * (longlong)piVar1[2]) >> 0x20) * 0x20;
    iVar5 = ((uint)(piVar7[3] * piVar1[3]) >> 0x1b) +
            (int)((ulonglong)((longlong)piVar7[3] * (longlong)piVar1[3]) >> 0x20) * 0x20;
    piVar7[3] = iVar5;
    piVar1 = piVar1 + 4;
    piVar7 = piVar9;
  } while (piVar9 != param_1 + 0x20);
  param_1[0x1f] = iVar5 * 2;
  pv_split();
  dct_16(param_1 + 0x10,0);
  dct_16(param_1,1);
  pv_merge_in_place_N32(param_1);
  iVar5 = param_1[0x1f];
  piVar1 = param_1 + 0x1e;
  do {
    iVar2 = *piVar1;
    iVar3 = piVar1[-1];
    iVar4 = piVar1[-2];
    iVar6 = piVar1[-3];
    iVar8 = piVar1[-4];
    iVar10 = iVar2 + iVar5;
    iVar5 = piVar1[-5];
    *piVar1 = iVar10;
    piVar1[-1] = iVar2 + iVar3;
    piVar1[-2] = iVar3 + iVar4;
    piVar1[-3] = iVar4 + iVar6;
    piVar1[-4] = iVar6 + iVar8;
    piVar7 = piVar1 + -6;
    piVar1[-5] = iVar8 + iVar5;
    piVar1 = piVar7;
  } while (param_1 != piVar7);
  *param_1 = *param_1 + iVar5;
  return;
}
