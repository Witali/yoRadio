/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: ps_decorrelate @ ram:42047432
 * Types and parameter counts are inferred; verify against disassembly. */

void ps_decorrelate(int param_1,int param_2,int param_3,int param_4,int param_5,int param_6)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int *piVar4;
  int iVar5;
  int *piVar6;
  int *piVar7;
  int iVar8;
  int *piVar9;
  int iVar10;
  undefined4 *puVar11;
  int iVar12;
  char *pcVar13;
  undefined4 *puVar14;
  char *pcVar15;
  int *piVar16;
  int iVar17;
  int *piVar18;
  int iVar19;
  int *piVar20;
  int iVar21;
  int *piVar22;
  int iVar23;
  int *piVar24;
  int iVar25;

  gp = &__global_pointer_;
  ps_pwr_transient_detection();
  iVar8 = *(int *)(param_1 + 0x1f8);
  pcVar15 = "\x04\x05";
  iVar25 = *(int *)(param_1 + 0x1ec);
  iVar23 = *(int *)(param_1 + 0x1f0);
  iVar21 = *(int *)(param_1 + 500);
  iVar19 = *(int *)(param_1 + 0x1d8);
  iVar17 = *(int *)(param_1 + 0x1dc);
  pcVar13 = "\x01";
  do {
    iVar3 = (int)*pcVar15;
    iVar10 = iVar3 * 4;
    iVar1 = *(int *)(iVar23 + iVar10);
    iVar5 = *(int *)(param_1 + 400) * 4;
    piVar9 = (int *)(*(int *)(iVar17 + iVar10) + iVar5);
    piVar4 = (int *)(*(int *)(iVar19 + iVar10) + iVar5);
    iVar12 = *piVar9;
    iVar5 = *piVar4;
    *piVar4 = *(int *)(iVar25 + iVar10);
    *piVar9 = iVar1;
    iVar12 = iVar12 >> 1;
    iVar1 = *(uint *)(aFractDelayPhaseFactorSubQmf + iVar10) << 0x10;
    iVar5 = iVar5 >> 1;
    uVar2 = *(uint *)(aFractDelayPhaseFactorSubQmf + iVar10) & 0xffff0000;
    piVar4 = (int *)(iVar21 + iVar10);
    pcVar15 = pcVar15 + 1;
    piVar9 = (int *)(iVar8 + iVar10);
    *piVar4 = (int)((ulonglong)((longlong)iVar5 * (longlong)(int)uVar2) >> 0x20) +
              (int)((ulonglong)((longlong)-iVar12 * (longlong)iVar1) >> 0x20);
    *piVar9 = (int)((ulonglong)((longlong)iVar12 * (longlong)(int)uVar2) >> 0x20) +
              (int)((ulonglong)((longlong)iVar5 * (longlong)iVar1) >> 0x20);
    ps_all_pass_fract_delay_filter_type_I
              (param_1 + 0x194,iVar3,aaFractDelayPhaseFactorSerSubQmf + iVar3 * 0xc,param_1 + 0x1b8,
               param_1 + 0x1c4,piVar4,piVar9);
    iVar1 = *(int *)(*pcVar13 * 4 + param_6);
    if (iVar1 != 0x7fffffff) {
      *piVar4 = (int)((ulonglong)((longlong)iVar1 * (longlong)*piVar4) >> 0x20) << 1;
      *piVar9 = (int)((ulonglong)((longlong)iVar1 * (longlong)*piVar9) >> 0x20) << 1;
    }
    pcVar13 = pcVar13 + 1;
  } while (pcVar15 != "\x03\x04\x05\x06\a\b\t\v\x0e\x12\x17#@");
  iVar17 = *(int *)(param_1 + 0x1d0);
  iVar19 = *(int *)(param_1 + 0x1d4);
  iVar8 = *(int *)(param_1 + 0x14);
  pcVar13 = "\x04\x05\x06\a\b\t\v\x0e\x12\x17#@";
  piVar4 = (int *)(param_6 + 0x20);
  do {
    iVar21 = (int)*pcVar13;
    if (iVar8 < *pcVar13) {
      iVar21 = iVar8;
    }
    iVar23 = (int)pcVar13[-1];
    if (iVar23 < iVar21) {
      iVar8 = iVar23 * 4;
      piVar24 = (int *)(iVar19 + -0xc + iVar8);
      piVar22 = (int *)(iVar17 + -0xc + iVar8);
      piVar18 = (int *)(param_2 + iVar8);
      piVar16 = (int *)(param_3 + iVar8);
      piVar9 = (int *)(param_4 + iVar8);
      piVar20 = (int *)(iVar8 + param_5);
      iVar8 = iVar23 + -3;
      do {
        iVar25 = *piVar16;
        iVar23 = *(int *)(param_1 + 400) * 4;
        piVar6 = (int *)(*piVar22 + iVar23);
        piVar7 = (int *)(*piVar24 + iVar23);
        iVar3 = *piVar6;
        iVar23 = *piVar7;
        *piVar6 = *piVar18;
        *piVar7 = iVar25;
        iVar23 = iVar23 >> 1;
        iVar3 = iVar3 >> 1;
        iVar1 = (&aFractDelayPhaseFactor)[iVar8] << 0x10;
        uVar2 = (&aFractDelayPhaseFactor)[iVar8] & 0xffff0000;
        piVar22 = piVar22 + 1;
        *piVar9 = (int)((ulonglong)((longlong)iVar3 * (longlong)(int)uVar2) >> 0x20) +
                  (int)((ulonglong)((longlong)-iVar23 * (longlong)iVar1) >> 0x20);
        iVar25 = iVar8 + 1;
        *piVar20 = (int)((ulonglong)((longlong)iVar23 * (longlong)(int)uVar2) >> 0x20) +
                   (int)((ulonglong)((longlong)iVar3 * (longlong)iVar1) >> 0x20);
        ps_all_pass_fract_delay_filter_type_II
                  (param_1 + 0x194,iVar8,aaFractDelayPhaseFactorSerQmf + iVar8 * 0xc,param_1 + 0x1a0
                   ,param_1 + 0x1ac,piVar9,piVar20,iVar8 + 3);
        iVar8 = *piVar4;
        if (iVar8 != 0x7fffffff) {
          *piVar9 = (int)((ulonglong)((longlong)iVar8 * (longlong)*piVar9) >> 0x20) << 1;
          *piVar20 = (int)((ulonglong)((longlong)iVar8 * (longlong)*piVar20) >> 0x20) << 1;
        }
        piVar24 = piVar24 + 1;
        piVar18 = piVar18 + 1;
        piVar16 = piVar16 + 1;
        piVar9 = piVar9 + 1;
        piVar20 = piVar20 + 1;
        iVar8 = iVar25;
      } while (iVar21 + -3 != iVar25);
      iVar8 = *(int *)(param_1 + 0x14);
    }
    pcVar13 = pcVar13 + 1;
    piVar4 = piVar4 + 1;
  } while (pcVar13 != "#@");
  if (0x17 < iVar8) {
    if (0x23 < iVar8) {
      iVar8 = 0x23;
    }
    iVar21 = *(int *)(param_6 + 0x48);
    piVar22 = (int *)(param_4 + 0x5c);
    piVar24 = (int *)(param_1 + 0x628);
    piVar20 = (int *)(param_5 + 0x5c);
    piVar16 = (int *)(iVar17 + 0x50);
    piVar4 = (int *)(iVar19 + 0x50);
    piVar9 = (int *)(param_2 + 0x5c);
    iVar23 = 0x17;
    piVar18 = (int *)(param_3 + 0x5c);
    do {
      iVar25 = *piVar24 * 4;
      iVar1 = *piVar24 + 1;
      iVar23 = iVar23 + 1;
      piVar6 = (int *)(*piVar16 + iVar25);
      piVar7 = (int *)(*piVar4 + iVar25);
      if (0xd < iVar1) {
        iVar1 = 0;
      }
      *piVar24 = iVar1;
      iVar25 = *piVar6;
      iVar1 = *piVar7;
      if (*(int *)(param_6 + 0x48) != 0x7fffffff) {
        iVar25 = (int)((ulonglong)((longlong)iVar25 * (longlong)iVar21) >> 0x20) << 1;
        iVar1 = (int)((ulonglong)((longlong)iVar1 * (longlong)iVar21) >> 0x20) << 1;
      }
      *piVar22 = iVar25;
      *piVar20 = iVar1;
      iVar25 = *piVar18;
      piVar24 = piVar24 + 1;
      *piVar6 = *piVar9;
      *piVar7 = iVar25;
      piVar16 = piVar16 + 1;
      piVar4 = piVar4 + 1;
      piVar22 = piVar22 + 1;
      piVar20 = piVar20 + 1;
      piVar9 = piVar9 + 1;
      piVar18 = piVar18 + 1;
    } while (iVar23 < iVar8);
    iVar8 = *(int *)(param_1 + 0x14);
    if (0x23 < iVar8) {
      if (0x40 < iVar8) {
        iVar8 = 0x40;
      }
      puVar11 = (undefined4 *)(iVar19 + 0x80);
      piVar4 = (int *)(param_4 + 0x8c);
      puVar14 = (undefined4 *)(iVar17 + 0x80);
      piVar9 = (int *)(param_5 + 0x8c);
      iVar17 = 0x23;
      piVar16 = (int *)(param_2 + 0x8c);
      piVar24 = (int *)(param_3 + 0x8c);
      do {
        piVar20 = (int *)*puVar14;
        piVar18 = (int *)*puVar11;
        iVar17 = iVar17 + 1;
        puVar14 = puVar14 + 1;
        puVar11 = puVar11 + 1;
        *piVar4 = *piVar20;
        *piVar9 = *piVar18;
        if (*(int *)(param_6 + 0x4c) != 0x7fffffff) {
          *piVar4 = (int)((ulonglong)((longlong)*(int *)(param_6 + 0x4c) * (longlong)*piVar4) >>
                         0x20) << 1;
          *piVar9 = (int)((ulonglong)((longlong)*piVar9 * (longlong)*(int *)(param_6 + 0x4c)) >>
                         0x20) << 1;
        }
        piVar4 = piVar4 + 1;
        piVar9 = piVar9 + 1;
        *piVar20 = *piVar16;
        iVar19 = *piVar24;
        piVar16 = piVar16 + 1;
        piVar24 = piVar24 + 1;
        *piVar18 = iVar19;
      } while (iVar17 < iVar8);
    }
  }
  iVar8 = *(int *)(param_1 + 400) + 1;
  if (1 < iVar8) {
    iVar8 = 0;
  }
  *(int *)(param_1 + 400) = iVar8;
  uVar2 = *(int *)(param_1 + 0x194) + 1;
  if (2 < uVar2) {
    uVar2 = 0;
  }
  *(uint *)(param_1 + 0x194) = uVar2;
  uVar2 = *(int *)(param_1 + 0x198) + 1;
  if (3 < uVar2) {
    uVar2 = 0;
  }
  *(uint *)(param_1 + 0x198) = uVar2;
  uVar2 = *(int *)(param_1 + 0x19c) + 1;
  if (4 < uVar2) {
    uVar2 = 0;
  }
  *(uint *)(param_1 + 0x19c) = uVar2;
  return;
}
