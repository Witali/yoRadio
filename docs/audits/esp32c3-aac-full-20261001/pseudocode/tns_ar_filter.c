/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: tns_ar_filter @ ram:430140ce
 * Types and parameter counts are inferred; verify against disassembly. */

void tns_ar_filter(int *param_1,int param_2,int param_3,int *param_4,int param_5,int param_6)

{
  int iVar1;
  uint uVar2;
  int *piVar3;
  int *piVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int *piVar8;
  int iVar9;
  uint uVar10;

  gp = &__global_pointer_;
  uVar10 = 0x10 - param_5;
  if (param_6 < 0x10) {
    iVar1 = 0;
    iVar5 = param_6;
    do {
      iVar5 = iVar5 << 1;
      iVar1 = iVar1 + 1;
    } while (iVar5 < 0x10);
    uVar2 = (uVar10 - iVar1) + 4;
    if (param_3 == -1) {
      param_1 = param_1 + param_2 + -1;
      if (param_6 == 0) {
        piVar4 = (int *)0x0;
        if (param_2 < 1) {
          return;
        }
        goto LAB_ram_43014202;
      }
LAB_ram_430141c0:
      piVar4 = param_1;
      piVar3 = (int *)0x0;
      iVar5 = param_6;
      while( true ) {
        piVar8 = piVar4;
        iVar7 = *piVar8 >> (uVar2 & 0x1f);
        iVar1 = param_6;
        piVar4 = param_4;
        if (iVar5 < param_6) {
          do {
            iVar6 = *piVar3;
            iVar1 = iVar1 + -1;
            piVar3 = piVar3 + 1;
            iVar7 = iVar7 - ((int)((ulonglong)((longlong)iVar6 * (longlong)*piVar4) >> 0x20) <<
                            (uVar10 & 0x1f));
            piVar4 = piVar4 + 1;
          } while (iVar1 != iVar5);
        }
        *piVar8 = iVar7;
        iVar5 = iVar5 + -1;
        if (iVar5 == 0) break;
        piVar4 = piVar8 + -1;
        piVar3 = piVar8;
      }
      piVar4 = param_1 + -(param_6 + -1);
      param_1 = piVar4 + -1;
      if (param_2 <= param_6) {
        return;
      }
LAB_ram_43014202:
      param_2 = param_2 - param_6;
      iVar1 = *param_1 >> (uVar2 & 0x1f);
      iVar5 = param_6;
      piVar3 = param_4;
      if (param_6 != 0) {
        while( true ) {
          do {
            iVar5 = iVar5 + -1;
            iVar1 = iVar1 - ((int)((ulonglong)((longlong)*piVar4 * (longlong)*piVar3) >> 0x20) <<
                            (uVar10 & 0x1f));
            piVar4 = piVar4 + 1;
            piVar3 = piVar3 + 1;
          } while (iVar5 != 0);
          *param_1 = iVar1;
          param_2 = param_2 + -1;
          if (param_2 == 0) break;
          iVar1 = param_1[-1] >> (uVar2 & 0x1f);
          piVar4 = param_1;
          iVar5 = param_6;
          piVar3 = param_4;
          param_1 = param_1 + -1;
        }
        return;
      }
      while( true ) {
        *param_1 = iVar1;
        if (param_2 == 1) {
          return;
        }
        param_1[-1] = param_1[-1] >> (uVar2 & 0x1f);
        if (param_2 + -2 == 0) break;
        iVar1 = param_1[-2] >> (uVar2 & 0x1f);
        param_2 = param_2 + -2;
        param_1 = param_1 + -2;
      }
      return;
    }
    if (param_6 == 0) {
      piVar4 = (int *)0x0;
      goto LAB_ram_4301415e;
    }
  }
  else {
    uVar2 = 0x14 - param_5;
    if (param_3 == -1) {
      param_1 = param_1 + param_2 + -1;
      goto LAB_ram_430141c0;
    }
  }
  *param_1 = *param_1 >> (uVar2 & 0x1f);
  piVar4 = param_1;
  iVar5 = param_6;
  while (iVar5 = iVar5 + -1, iVar5 != 0) {
    piVar3 = piVar4 + 1;
    iVar1 = 0;
    if (iVar5 < param_6) {
      iVar1 = 0;
      iVar7 = param_6;
      piVar8 = param_4;
      do {
        iVar6 = *piVar4;
        iVar9 = *piVar8;
        iVar7 = iVar7 + -1;
        piVar4 = piVar4 + -1;
        piVar8 = piVar8 + 1;
        iVar1 = iVar1 - (int)((ulonglong)((longlong)iVar6 * (longlong)iVar9) >> 0x20);
      } while (iVar5 != iVar7);
      iVar1 = iVar1 << (uVar10 & 0x1f);
    }
    *piVar3 = (*piVar3 >> (uVar2 & 0x1f)) + iVar1;
    piVar4 = piVar3;
  }
  piVar4 = param_1 + param_6 + -1;
  param_1 = param_1 + param_6;
LAB_ram_4301415e:
  iVar5 = param_2 - param_6;
  if (param_6 < param_2) {
    while( true ) {
      iVar7 = 0;
      iVar1 = param_6;
      piVar3 = param_4;
      if (param_6 != 0) {
        do {
          iVar9 = *piVar4;
          iVar6 = *piVar3;
          iVar1 = iVar1 + -1;
          piVar4 = piVar4 + -1;
          piVar3 = piVar3 + 1;
          iVar7 = iVar7 - (int)((ulonglong)((longlong)iVar9 * (longlong)iVar6) >> 0x20);
        } while (iVar1 != 0);
        iVar7 = iVar7 << (uVar10 & 0x1f);
      }
      iVar5 = iVar5 + -1;
      *param_1 = (*param_1 >> (uVar2 & 0x1f)) + iVar7;
      if (iVar5 == 0) break;
      piVar4 = param_1;
      param_1 = param_1 + 1;
    }
  }
  return;
}
