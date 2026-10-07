/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: ps_pwr_transient_detection @ ram:4300db1e
 * Types and parameter counts are inferred; verify against disassembly. */

void ps_pwr_transient_detection(int param_1,int param_2,int param_3,int *param_4)

{
  char *pcVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  int iVar5;
  int *piVar6;
  int iVar7;
  int *piVar8;
  int *piVar9;
  int iStack_38;
  uint uStack_34;

  gp = &__global_pointer_;
  piVar9 = param_4 + 8;
  pcVar1 = "\x03\x04\x05\x06\a\b\t\v\x0e\x12\x17#@";
  do {
    iVar7 = (int)pcVar1[1];
    if (*(int *)(param_1 + 0x14) < (int)pcVar1[1]) {
      iVar7 = *(int *)(param_1 + 0x14);
    }
    if (*pcVar1 < iVar7) {
      iVar5 = *pcVar1 * 4;
      piVar4 = (int *)(param_2 + iVar5);
      piVar6 = (int *)(iVar5 + param_3);
      iVar5 = 0;
      do {
        iVar2 = *piVar4;
        iVar3 = *piVar6;
        piVar4 = piVar4 + 1;
        piVar6 = piVar6 + 1;
        iVar5 = iVar5 + (int)((ulonglong)((longlong)iVar2 * (longlong)iVar2) >> 0x20) +
                (int)((ulonglong)((longlong)iVar3 * (longlong)iVar3) >> 0x20);
      } while ((int *)(iVar7 * 4 + param_2) != piVar4);
      iVar5 = iVar5 >> 1;
    }
    else {
      iVar5 = 0;
    }
    *piVar9 = iVar5;
    pcVar1 = pcVar1 + 1;
    piVar9 = piVar9 + 1;
  } while (pcVar1 != "@");
  piVar4 = *(int **)(param_1 + 0x1ec);
  piVar6 = *(int **)(param_1 + 0x1f0);
  piVar9 = *(int **)(param_1 + 0x1e8);
  piVar8 = *(int **)(param_1 + 0x1e4);
  iVar7 = 0;
  *param_4 = (int)((ulonglong)((longlong)*piVar6 * (longlong)*piVar6) >> 0x20) +
             (int)((ulonglong)((longlong)*piVar4 * (longlong)*piVar4) >> 0x20) +
             (int)((ulonglong)((longlong)piVar4[5] * (longlong)piVar4[5]) >> 0x20) +
             (int)((ulonglong)((longlong)piVar6[5] * (longlong)piVar6[5]) >> 0x20) >> 1;
  param_4[1] = (int)((ulonglong)((longlong)piVar6[1] * (longlong)piVar6[1]) >> 0x20) +
               (int)((ulonglong)((longlong)piVar4[1] * (longlong)piVar4[1]) >> 0x20) +
               (int)((ulonglong)((longlong)piVar4[4] * (longlong)piVar4[4]) >> 0x20) +
               (int)((ulonglong)((longlong)piVar6[4] * (longlong)piVar6[4]) >> 0x20) >> 1;
  param_4[2] = (int)((ulonglong)((longlong)piVar6[2] * (longlong)piVar6[2]) >> 0x20) +
               (int)((ulonglong)((longlong)piVar4[2] * (longlong)piVar4[2]) >> 0x20) >> 1;
  param_4[3] = (int)((ulonglong)((longlong)piVar6[3] * (longlong)piVar6[3]) >> 0x20) +
               (int)((ulonglong)((longlong)piVar4[3] * (longlong)piVar4[3]) >> 0x20) >> 1;
  param_4[5] = (int)((ulonglong)((longlong)piVar6[6] * (longlong)piVar6[6]) >> 0x20) +
               (int)((ulonglong)((longlong)piVar4[6] * (longlong)piVar4[6]) >> 0x20) >> 1;
  param_4[4] = (int)((ulonglong)((longlong)piVar6[7] * (longlong)piVar6[7]) >> 0x20) +
               (int)((ulonglong)((longlong)piVar4[7] * (longlong)piVar4[7]) >> 0x20) >> 1;
  param_4[6] = (int)((ulonglong)((longlong)piVar6[8] * (longlong)piVar6[8]) >> 0x20) +
               (int)((ulonglong)((longlong)piVar4[8] * (longlong)piVar4[8]) >> 0x20) >> 1;
  param_4[7] = (int)((ulonglong)((longlong)piVar6[9] * (longlong)piVar6[9]) >> 0x20) +
               (int)((ulonglong)((longlong)piVar4[9] * (longlong)piVar4[9]) >> 0x20) >> 1;
  do {
    while( true ) {
      iVar5 = *param_4;
      piVar4 = (int *)(*(int *)(param_1 + 0x1e0) + iVar7);
      iVar2 = *piVar9 - (*piVar9 >> 2);
      iVar3 = (int)((ulonglong)((longlong)*piVar4 * 0x6209f080) >> 0x20) * 2;
      if (iVar5 <= iVar3) {
        iVar2 = iVar2 + (iVar3 - iVar5 >> 2);
        iVar5 = iVar3;
      }
      *piVar4 = iVar5;
      *piVar9 = iVar2;
      iVar2 = (iVar2 >> 1) + iVar2;
      iVar5 = (*param_4 - *piVar8 >> 2) + *piVar8;
      *piVar8 = iVar5;
      if (iVar5 < iVar2) break;
      *param_4 = 0x7fffffff;
      iVar7 = iVar7 + 4;
      piVar8 = piVar8 + 1;
      param_4 = param_4 + 1;
      piVar9 = piVar9 + 1;
      if (iVar7 == 0x50) {
        return;
      }
    }
    pv_div(iVar5,iVar2,&iStack_38);
    iVar7 = iVar7 + 4;
    piVar8 = piVar8 + 1;
    *param_4 = (iStack_38 >> (uStack_34 & 0x1f)) << 1;
    param_4 = param_4 + 1;
    piVar9 = piVar9 + 1;
  } while (iVar7 != 0x50);
  gp = &__global_pointer_;
  return;
}
