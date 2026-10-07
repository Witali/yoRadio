/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: ps_decorrelate @ ram:4300ce3a
 * Types and parameter counts are inferred; verify against disassembly. */

void ps_decorrelate(aac_ps_abi_t *ps,int param_2,int param_3,int param_4,int param_5,int param_6)

{
  int32_t **ppiVar1;
  int32_t **ppiVar2;
  int32_t iVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int32_t *piVar9;
  int32_t *piVar10;
  uint32_t uVar11;
  int iVar12;
  char *pcVar13;
  char *pcVar14;
  int *piVar15;
  int32_t **ppiVar16;
  int32_t **ppiVar17;
  int *piVar18;
  int32_t *piVar19;
  int32_t *piVar20;
  int32_t *piVar21;
  int *piVar22;
  int *piVar23;
  int iVar24;
  int32_t *piVar25;

  gp = &__global_pointer_;
  ps_pwr_transient_detection(ps,param_2,param_3,(int *)param_6);
  piVar9 = ps->hybrid_right_imag;
  pcVar14 = "\x04\x05";
  piVar21 = ps->hybrid_left_real;
  piVar20 = ps->hybrid_left_imag;
  piVar19 = ps->hybrid_right_real;
  ppiVar17 = ps->sub_delay_real;
  ppiVar16 = ps->sub_delay_imag;
  pcVar13 = "\x01";
  do {
    iVar5 = (int)*pcVar14;
    iVar7 = ps->delay_index;
    piVar10 = ppiVar16[iVar5];
    iVar3 = piVar20[iVar5];
    iVar12 = piVar10[iVar7];
    iVar8 = ppiVar17[iVar5][iVar7];
    ppiVar17[iVar5][iVar7] = piVar21[iVar5];
    piVar10[iVar7] = iVar3;
    iVar12 = iVar12 >> 1;
    iVar7 = *(uint *)(aFractDelayPhaseFactorSubQmf + iVar5 * 4) << 0x10;
    iVar8 = iVar8 >> 1;
    uVar4 = *(uint *)(aFractDelayPhaseFactorSubQmf + iVar5 * 4) & 0xffff0000;
    piVar10 = piVar19 + iVar5;
    pcVar14 = pcVar14 + 1;
    piVar25 = piVar9 + iVar5;
    *piVar10 = (int)((ulonglong)((longlong)iVar8 * (longlong)(int)uVar4) >> 0x20) +
               (int)((ulonglong)((longlong)-iVar12 * (longlong)iVar7) >> 0x20);
    *piVar25 = (int)((ulonglong)((longlong)iVar12 * (longlong)(int)uVar4) >> 0x20) +
               (int)((ulonglong)((longlong)iVar8 * (longlong)iVar7) >> 0x20);
    ps_all_pass_fract_delay_filter_type_I
              (ps->serial_index,iVar5,aaFractDelayPhaseFactorSerSubQmf + iVar5 * 0xc,
               ps->sub_serial_real,ps->sub_serial_imag,piVar10,piVar25);
    iVar7 = *(int *)(*pcVar13 * 4 + param_6);
    if (iVar7 != 0x7fffffff) {
      *piVar10 = (int)((ulonglong)((longlong)iVar7 * (longlong)*piVar10) >> 0x20) << 1;
      *piVar25 = (int)((ulonglong)((longlong)iVar7 * (longlong)*piVar25) >> 0x20) << 1;
    }
    pcVar13 = pcVar13 + 1;
  } while (pcVar14 != "\x03\x04\x05\x06\a\b\t\v\x0e\x12\x17#@");
  ppiVar16 = ps->delay_real;
  ppiVar17 = ps->delay_imag;
  iVar7 = ps->upper_subband;
  pcVar13 = "\x04\x05\x06\a\b\t\v\x0e\x12\x17#@";
  piVar23 = (int *)(param_6 + 0x20);
  do {
    iVar5 = (int)*pcVar13;
    if (iVar7 < *pcVar13) {
      iVar5 = iVar7;
    }
    iVar8 = (int)pcVar13[-1];
    if (iVar8 < iVar5) {
      iVar7 = iVar8 * 4;
      ppiVar1 = ppiVar17 + iVar8 + -3;
      ppiVar2 = ppiVar16 + iVar8 + -3;
      piVar9 = (int32_t *)(param_2 + iVar7);
      piVar15 = (int *)(param_3 + iVar7);
      piVar22 = (int *)(param_4 + iVar7);
      piVar18 = (int *)(iVar7 + param_5);
      iVar7 = iVar8 + -3;
      do {
        iVar6 = ps->delay_index;
        piVar19 = *ppiVar1;
        iVar12 = *piVar15;
        iVar24 = (*ppiVar2)[iVar6];
        iVar8 = piVar19[iVar6];
        (*ppiVar2)[iVar6] = *piVar9;
        piVar19[iVar6] = iVar12;
        iVar8 = iVar8 >> 1;
        iVar24 = iVar24 >> 1;
        iVar6 = (&aFractDelayPhaseFactor)[iVar7] << 0x10;
        uVar4 = (&aFractDelayPhaseFactor)[iVar7] & 0xffff0000;
        ppiVar2 = ppiVar2 + 1;
        *piVar22 = (int)((ulonglong)((longlong)iVar24 * (longlong)(int)uVar4) >> 0x20) +
                   (int)((ulonglong)((longlong)-iVar8 * (longlong)iVar6) >> 0x20);
        iVar12 = iVar7 + 1;
        *piVar18 = (int)((ulonglong)((longlong)iVar8 * (longlong)(int)uVar4) >> 0x20) +
                   (int)((ulonglong)((longlong)iVar24 * (longlong)iVar6) >> 0x20);
        ps_all_pass_fract_delay_filter_type_II
                  (ps->serial_index,iVar7,aaFractDelayPhaseFactorSerQmf + iVar7 * 0xc,
                   ps->serial_real,ps->serial_imag,piVar22,piVar18,iVar7 + 3);
        iVar7 = *piVar23;
        if (iVar7 != 0x7fffffff) {
          *piVar22 = (int)((ulonglong)((longlong)iVar7 * (longlong)*piVar22) >> 0x20) << 1;
          *piVar18 = (int)((ulonglong)((longlong)iVar7 * (longlong)*piVar18) >> 0x20) << 1;
        }
        ppiVar1 = ppiVar1 + 1;
        piVar9 = piVar9 + 1;
        piVar15 = piVar15 + 1;
        piVar22 = piVar22 + 1;
        piVar18 = piVar18 + 1;
        iVar7 = iVar12;
      } while (iVar5 + -3 != iVar12);
      iVar7 = ps->upper_subband;
    }
    pcVar13 = pcVar13 + 1;
    piVar23 = piVar23 + 1;
  } while (pcVar13 != "#@");
  if (0x17 < iVar7) {
    if (0x23 < iVar7) {
      iVar7 = 0x23;
    }
    iVar5 = *(int *)(param_6 + 0x48);
    piVar22 = (int *)(param_4 + 0x5c);
    piVar19 = ps->long_index;
    piVar23 = (int *)(param_5 + 0x5c);
    ppiVar2 = ppiVar16 + 0x14;
    ppiVar1 = ppiVar17 + 0x14;
    piVar9 = (int32_t *)(param_2 + 0x5c);
    iVar8 = 0x17;
    piVar20 = (int32_t *)(param_3 + 0x5c);
    do {
      iVar12 = *piVar19;
      piVar21 = *ppiVar2;
      piVar10 = *ppiVar1;
      iVar3 = iVar12 + 1;
      iVar8 = iVar8 + 1;
      if (0xd < iVar3) {
        iVar3 = 0;
      }
      *piVar19 = iVar3;
      iVar6 = piVar21[iVar12];
      iVar24 = piVar10[iVar12];
      if (*(int *)(param_6 + 0x48) != 0x7fffffff) {
        iVar6 = (int)((ulonglong)((longlong)iVar6 * (longlong)iVar5) >> 0x20) << 1;
        iVar24 = (int)((ulonglong)((longlong)iVar24 * (longlong)iVar5) >> 0x20) << 1;
      }
      *piVar22 = iVar6;
      *piVar23 = iVar24;
      iVar3 = *piVar20;
      piVar19 = piVar19 + 1;
      piVar21[iVar12] = *piVar9;
      piVar10[iVar12] = iVar3;
      ppiVar2 = ppiVar2 + 1;
      ppiVar1 = ppiVar1 + 1;
      piVar22 = piVar22 + 1;
      piVar23 = piVar23 + 1;
      piVar9 = piVar9 + 1;
      piVar20 = piVar20 + 1;
    } while (iVar8 < iVar7);
    iVar7 = ps->upper_subband;
    if (0x23 < iVar7) {
      if (0x40 < iVar7) {
        iVar7 = 0x40;
      }
      ppiVar17 = ppiVar17 + 0x20;
      piVar9 = (int32_t *)(param_4 + 0x8c);
      ppiVar16 = ppiVar16 + 0x20;
      piVar19 = (int32_t *)(param_5 + 0x8c);
      iVar5 = 0x23;
      piVar20 = (int32_t *)(param_2 + 0x8c);
      piVar21 = (int32_t *)(param_3 + 0x8c);
      do {
        piVar25 = *ppiVar16;
        piVar10 = *ppiVar17;
        iVar5 = iVar5 + 1;
        ppiVar16 = ppiVar16 + 1;
        ppiVar17 = ppiVar17 + 1;
        *piVar9 = *piVar25;
        *piVar19 = *piVar10;
        if (*(int *)(param_6 + 0x4c) != 0x7fffffff) {
          *piVar9 = (int)((ulonglong)((longlong)*(int *)(param_6 + 0x4c) * (longlong)*piVar9) >>
                         0x20) << 1;
          *piVar19 = (int)((ulonglong)((longlong)*piVar19 * (longlong)*(int *)(param_6 + 0x4c)) >>
                          0x20) << 1;
        }
        piVar9 = piVar9 + 1;
        piVar19 = piVar19 + 1;
        *piVar25 = *piVar20;
        iVar3 = *piVar21;
        piVar20 = piVar20 + 1;
        piVar21 = piVar21 + 1;
        *piVar10 = iVar3;
      } while (iVar5 < iVar7);
    }
  }
  iVar3 = ps->delay_index + 1;
  if (1 < iVar3) {
    iVar3 = 0;
  }
  ps->delay_index = iVar3;
  uVar11 = ps->serial_index[0] + 1;
  if (2 < uVar11) {
    uVar11 = 0;
  }
  ps->serial_index[0] = uVar11;
  uVar11 = ps->serial_index[1] + 1;
  if (3 < uVar11) {
    uVar11 = 0;
  }
  ps->serial_index[1] = uVar11;
  uVar11 = ps->serial_index[2] + 1;
  if (4 < uVar11) {
    uVar11 = 0;
  }
  ps->serial_index[2] = uVar11;
  return;
}
