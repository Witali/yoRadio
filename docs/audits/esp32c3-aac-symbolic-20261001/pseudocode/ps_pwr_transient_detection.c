/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: ps_pwr_transient_detection @ ram:4300db1e
 * Types and parameter counts are inferred; verify against disassembly. */

void ps_pwr_transient_detection(aac_ps_abi_t *ps,int param_2,int param_3,int *param_4)

{
  char *pcVar1;
  int32_t *piVar2;
  int *piVar3;
  int iVar4;
  int32_t *piVar5;
  int iVar6;
  int *piVar7;
  int iVar8;
  int *piVar9;
  int iVar10;
  int32_t *piVar11;
  int32_t *piVar12;
  int iStack_38;
  uint uStack_34;

  gp = &__global_pointer_;
  piVar3 = param_4 + 8;
  pcVar1 = "\x03\x04\x05\x06\a\b\t\v\x0e\x12\x17#@";
  do {
    iVar10 = (int)pcVar1[1];
    if (ps->upper_subband < (int)pcVar1[1]) {
      iVar10 = ps->upper_subband;
    }
    if (*pcVar1 < iVar10) {
      iVar8 = *pcVar1 * 4;
      piVar7 = (int *)(param_2 + iVar8);
      piVar9 = (int *)(iVar8 + param_3);
      iVar8 = 0;
      do {
        iVar4 = *piVar7;
        iVar6 = *piVar9;
        piVar7 = piVar7 + 1;
        piVar9 = piVar9 + 1;
        iVar8 = iVar8 + (int)((ulonglong)((longlong)iVar4 * (longlong)iVar4) >> 0x20) +
                (int)((ulonglong)((longlong)iVar6 * (longlong)iVar6) >> 0x20);
      } while ((int *)(iVar10 * 4 + param_2) != piVar7);
      iVar8 = iVar8 >> 1;
    }
    else {
      iVar8 = 0;
    }
    *piVar3 = iVar8;
    pcVar1 = pcVar1 + 1;
    piVar3 = piVar3 + 1;
  } while (pcVar1 != "@");
  piVar2 = ps->hybrid_left_real;
  piVar5 = ps->hybrid_left_imag;
  piVar12 = ps->previous_peak_difference;
  piVar11 = ps->previous_energy;
  iVar10 = 0;
  *param_4 = (int)((ulonglong)((longlong)*piVar5 * (longlong)*piVar5) >> 0x20) +
             (int)((ulonglong)((longlong)*piVar2 * (longlong)*piVar2) >> 0x20) +
             (int)((ulonglong)((longlong)piVar2[5] * (longlong)piVar2[5]) >> 0x20) +
             (int)((ulonglong)((longlong)piVar5[5] * (longlong)piVar5[5]) >> 0x20) >> 1;
  param_4[1] = (int)((ulonglong)((longlong)piVar5[1] * (longlong)piVar5[1]) >> 0x20) +
               (int)((ulonglong)((longlong)piVar2[1] * (longlong)piVar2[1]) >> 0x20) +
               (int)((ulonglong)((longlong)piVar2[4] * (longlong)piVar2[4]) >> 0x20) +
               (int)((ulonglong)((longlong)piVar5[4] * (longlong)piVar5[4]) >> 0x20) >> 1;
  param_4[2] = (int)((ulonglong)((longlong)piVar5[2] * (longlong)piVar5[2]) >> 0x20) +
               (int)((ulonglong)((longlong)piVar2[2] * (longlong)piVar2[2]) >> 0x20) >> 1;
  param_4[3] = (int)((ulonglong)((longlong)piVar5[3] * (longlong)piVar5[3]) >> 0x20) +
               (int)((ulonglong)((longlong)piVar2[3] * (longlong)piVar2[3]) >> 0x20) >> 1;
  param_4[5] = (int)((ulonglong)((longlong)piVar5[6] * (longlong)piVar5[6]) >> 0x20) +
               (int)((ulonglong)((longlong)piVar2[6] * (longlong)piVar2[6]) >> 0x20) >> 1;
  param_4[4] = (int)((ulonglong)((longlong)piVar5[7] * (longlong)piVar5[7]) >> 0x20) +
               (int)((ulonglong)((longlong)piVar2[7] * (longlong)piVar2[7]) >> 0x20) >> 1;
  param_4[6] = (int)((ulonglong)((longlong)piVar5[8] * (longlong)piVar5[8]) >> 0x20) +
               (int)((ulonglong)((longlong)piVar2[8] * (longlong)piVar2[8]) >> 0x20) >> 1;
  param_4[7] = (int)((ulonglong)((longlong)piVar5[9] * (longlong)piVar5[9]) >> 0x20) +
               (int)((ulonglong)((longlong)piVar2[9] * (longlong)piVar2[9]) >> 0x20) >> 1;
  do {
    while( true ) {
      iVar8 = *param_4;
      piVar3 = (int *)((int)ps->peak + iVar10);
      iVar4 = *piVar12 - (*piVar12 >> 2);
      iVar6 = (int)((ulonglong)((longlong)*piVar3 * 0x6209f080) >> 0x20) * 2;
      if (iVar8 <= iVar6) {
        iVar4 = iVar4 + (iVar6 - iVar8 >> 2);
        iVar8 = iVar6;
      }
      *piVar3 = iVar8;
      *piVar12 = iVar4;
      iVar4 = (iVar4 >> 1) + iVar4;
      iVar8 = (*param_4 - *piVar11 >> 2) + *piVar11;
      *piVar11 = iVar8;
      if (iVar8 < iVar4) break;
      *param_4 = 0x7fffffff;
      iVar10 = iVar10 + 4;
      piVar11 = piVar11 + 1;
      param_4 = param_4 + 1;
      piVar12 = piVar12 + 1;
      if (iVar10 == 0x50) {
        return;
      }
    }
    pv_div(iVar8,iVar4,&iStack_38);
    iVar10 = iVar10 + 4;
    piVar11 = piVar11 + 1;
    *param_4 = (iStack_38 >> (uStack_34 & 0x1f)) << 1;
    param_4 = param_4 + 1;
    piVar12 = piVar12 + 1;
  } while (iVar10 != 0x50);
  gp = &__global_pointer_;
  return;
}
