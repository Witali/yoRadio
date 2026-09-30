/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: high_freq_generation @ ram:42029eea
 * Types and parameter counts are inferred; verify against disassembly. */

void high_freq_generation
               (int param_1,int param_2,int param_3,int param_4,int *param_5,int *param_6,
               int param_7,int param_8,int param_9,int param_10,int param_11,int param_12,
               int param_13,int param_14,int param_15)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  uint *puVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  uint *puVar10;
  int iVar11;
  uint uVar12;
  uint *puVar13;
  uint uVar14;
  uint *puVar15;
  int iVar16;
  uint uVar17;
  uint *puVar18;
  uint uVar19;
  int iVar20;
  int *piVar21;
  int iVar22;
  uint uVar23;
  uint *puVar24;
  int iVar25;
  int iVar26;
  int iVar27;
  int iVar28;
  int iVar29;
  int iVar30;
  uint uVar31;
  uint uVar32;
  uint *local_70;
  int iStack_6c;

  gp = &__global_pointer_;
  if (0 < param_10) {
    iVar20 = param_11 + param_12;
    iVar16 = ((iVar20 * 0x20 - param_9) + param_8) * 4;
    iVar7 = iVar20 * 0x80;
    iVar2 = (param_8 - param_9) * 4;
    puVar18 = (uint *)(param_1 + iVar16);
    local_70 = (uint *)(iVar16 + param_2);
    param_10 = param_8 + param_10;
    iVar16 = (iVar20 * 0x30 - param_15) + param_8;
    puVar4 = (uint *)(param_3 + iVar16 * 4);
    iVar28 = 0;
    iStack_6c = 0;
    do {
      piVar21 = (int *)(param_7 + iStack_6c);
      if (*piVar21 <= param_8) {
        do {
          piVar1 = piVar21 + 1;
          piVar21 = piVar21 + 1;
          iVar28 = iVar28 + 1;
        } while (*piVar1 <= param_8);
        iStack_6c = iVar28 * 4;
      }
      iVar22 = *(int *)(param_14 + iStack_6c);
      if (iVar22 < 0) {
LAB_ram_4202a1b4:
        if (param_11 < param_13) {
          puVar24 = (uint *)(iVar16 * 4 + param_4);
          puVar10 = local_70;
          puVar13 = puVar4;
          puVar15 = puVar18;
          iVar22 = iVar20;
          do {
            uVar5 = *puVar15;
            iVar22 = iVar22 + 1;
            puVar15 = puVar15 + 0x20;
            *puVar13 = uVar5;
            uVar5 = *puVar10;
            puVar13 = puVar13 + 0x30;
            puVar10 = puVar10 + 0x20;
            *puVar24 = uVar5;
            puVar24 = puVar24 + 0x30;
          } while (iVar22 < param_12 + param_13);
        }
      }
      else {
        iVar29 = *(int *)(*param_5 + iVar2);
        iVar27 = *(int *)(param_5[1] + iVar2);
        iVar8 = *(int *)(*param_6 + iVar2);
        iVar25 = *(int *)(param_6[1] + iVar2);
        if (((iVar29 == 0 && iVar27 == 0) && iVar8 == 0) && iVar25 == 0) goto LAB_ram_4202a1b4;
        if (param_11 < param_13) {
          iVar11 = iVar7 + -0x80 + iVar2;
          iVar30 = iVar7 + -0x100 + iVar2;
          iVar3 = ((uint)(iVar22 * iVar22) >> 0x1e) +
                  (int)((ulonglong)((longlong)iVar22 * (longlong)iVar22) >> 0x20) * 4;
          iVar26 = (int)((ulonglong)((longlong)iVar3 * (longlong)iVar25) >> 0x20) * 0x10 +
                   ((uint)(iVar3 * iVar25) >> 0x1c);
          iVar25 = (int)((ulonglong)((longlong)iVar27 * (longlong)iVar3) >> 0x20) * 0x10 +
                   ((uint)(iVar27 * iVar3) >> 0x1c);
          iVar8 = (int)((ulonglong)((longlong)iVar8 * (longlong)iVar22) >> 0x20) * 8 +
                  ((uint)(iVar8 * iVar22) >> 0x1d);
          iVar27 = (int)((ulonglong)((longlong)iVar29 * (longlong)iVar22) >> 0x20) * 8 +
                   ((uint)(iVar29 * iVar22) >> 0x1d);
          piVar21 = (int *)(iVar16 * 4 + param_4);
          uVar5 = *(uint *)(param_1 + iVar11);
          uVar6 = *(uint *)(iVar11 + param_2);
          uVar14 = *(uint *)(param_1 + iVar7 + iVar2);
          uVar17 = *(uint *)(iVar7 + iVar2 + param_2);
          iVar22 = iVar20;
          puVar10 = puVar4;
          puVar13 = puVar18;
          puVar15 = local_70;
          uVar31 = *(uint *)(iVar30 + param_2);
          uVar32 = *(uint *)(param_1 + iVar30);
          do {
            uVar12 = uVar6;
            uVar9 = uVar5;
            iVar22 = iVar22 + 1;
            puVar13 = puVar13 + 0x20;
            puVar15 = puVar15 + 0x20;
            uVar23 = uVar9 * iVar27 + uVar14 * 0x10000000;
            uVar5 = uVar12 * -iVar8 + uVar23;
            uVar19 = uVar32 * iVar25 + uVar5;
            uVar6 = uVar31 * -iVar26 + uVar19;
            *puVar10 = (uVar6 >> 0x1c) +
                       ((uint)(uVar6 < uVar19) +
                       (uint)(uVar19 < uVar5) +
                       (uint)(uVar5 < uVar23) +
                       (uVar14 >> 4) +
                       (int)((ulonglong)((longlong)(int)uVar9 * (longlong)iVar27) >> 0x20) +
                       (uint)(uVar23 < uVar14 * 0x10000000) +
                       (int)((ulonglong)((longlong)(int)uVar12 * (longlong)-iVar8) >> 0x20) +
                       (int)((ulonglong)((longlong)(int)uVar32 * (longlong)iVar25) >> 0x20) +
                       (int)((ulonglong)((longlong)(int)uVar31 * (longlong)-iVar26) >> 0x20)) * 0x10
            ;
            uVar23 = uVar9 * iVar8 + uVar17 * 0x10000000;
            uVar6 = uVar12 * iVar27 + uVar23;
            uVar19 = uVar32 * iVar26 + uVar6;
            uVar5 = uVar31 * iVar25 + uVar19;
            *piVar21 = (uVar5 >> 0x1c) +
                       ((uint)(uVar5 < uVar19) +
                       (uint)(uVar19 < uVar6) +
                       (int)((ulonglong)((longlong)(int)uVar32 * (longlong)iVar26) >> 0x20) +
                       (uint)(uVar6 < uVar23) +
                       (uint)(uVar23 < uVar17 * 0x10000000) +
                       (int)((ulonglong)((longlong)(int)uVar9 * (longlong)iVar8) >> 0x20) +
                       (uVar17 >> 4) +
                       (int)((ulonglong)((longlong)(int)uVar12 * (longlong)iVar27) >> 0x20) +
                       (int)((ulonglong)((longlong)(int)uVar31 * (longlong)iVar25) >> 0x20)) * 0x10;
            piVar21 = piVar21 + 0x30;
            uVar5 = uVar14;
            uVar6 = uVar17;
            uVar14 = *puVar13;
            uVar17 = *puVar15;
            puVar10 = puVar10 + 0x30;
            uVar31 = uVar12;
            uVar32 = uVar9;
          } while (iVar22 < param_12 + param_13);
        }
      }
      param_8 = param_8 + 1;
      iVar16 = iVar16 + 1;
      local_70 = local_70 + 1;
      puVar18 = puVar18 + 1;
      puVar4 = puVar4 + 1;
      iVar2 = iVar2 + 4;
    } while (param_8 < param_10);
  }
  return;
}
