/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: high_freq_generation_LC @ ram:43011f1c
 * Types and parameter counts are inferred; verify against disassembly. */

void high_freq_generation_LC
               (int param_1,int param_2,int *param_3,int param_4,int param_5,int param_6,int param_7
               ,int param_8,int param_9,int param_10,int param_11,int param_12,int param_13)

{
  int *piVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  uint *puVar5;
  int iVar6;
  uint *puVar7;
  int iVar8;
  undefined4 uVar9;
  int iVar10;
  uint *puVar11;
  int *piVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  int iVar16;
  uint uVar17;
  int iVar18;
  int iVar19;
  int iVar20;
  uint uVar21;
  uint uVar22;
  uint uVar23;

  gp = &__global_pointer_;
  if (0 < param_8) {
    iVar18 = param_10 + param_9;
    param_10 = param_10 + param_11;
    iVar19 = param_2 + ((iVar18 * 0x30 - param_13) + param_7) * 4;
    param_13 = param_6 - param_13;
    puVar5 = (uint *)(((param_10 * 0x20 - param_7) + param_6) * 4 + param_1);
    iVar8 = (param_6 - param_7) * 4;
    iVar3 = 0;
    uVar9 = 0;
    iVar15 = 0;
    iVar20 = param_6;
LAB_ram_43011fca:
    *(undefined4 *)(iVar20 * 4 + param_4) = uVar9;
    piVar12 = (int *)(param_5 + iVar15);
    if (*piVar12 <= iVar20) {
      do {
        piVar1 = piVar12 + 1;
        piVar12 = piVar12 + 1;
        iVar3 = iVar3 + 1;
      } while (*piVar1 <= iVar20);
      iVar15 = iVar3 * 4;
    }
    iVar6 = *(int *)(param_12 + iVar15);
    if (iVar6 < 1) {
LAB_ram_43012110:
      puVar7 = puVar5 + (param_9 - param_11) * 0x20;
      puVar11 = (uint *)(iVar19 + iVar8);
      iVar6 = iVar18;
      if (param_9 < param_11) {
        do {
          uVar21 = *puVar7;
          iVar6 = iVar6 + 1;
          puVar7 = puVar7 + 0x20;
          *puVar11 = uVar21;
          puVar11 = puVar11 + 0x30;
        } while (iVar6 < param_10);
      }
    }
    else {
      iVar10 = *(int *)(*param_3 + iVar8);
      iVar16 = *(int *)(param_3[1] + iVar8);
      if (iVar10 == 0 && iVar16 == 0) goto LAB_ram_43012110;
      uVar17 = *(uint *)(iVar18 * 0x80 + -0x80 + iVar8 + param_1);
      iVar13 = (int)((ulonglong)((longlong)iVar6 * (longlong)iVar6) >> 0x20) * 4;
      uVar22 = *(uint *)(iVar18 * 0x80 + -0x100 + iVar8 + param_1);
      uVar21 = *(uint *)(iVar18 * 0x80 + iVar8 + param_1);
      iVar14 = (int)((ulonglong)((longlong)iVar13 * (longlong)iVar16) >> 0x20) * 0x10;
      uVar4 = ((uint)(iVar13 * iVar16) >> 0x1c) + iVar14;
      iVar10 = (int)((ulonglong)((longlong)iVar10 * (longlong)iVar6) >> 0x20) * 8 +
               ((uint)(iVar10 * iVar6) >> 0x1d);
      iVar6 = iVar18;
      if (iVar18 < param_10 + -1) {
        piVar12 = (int *)(iVar19 + iVar8);
        puVar7 = (uint *)(param_1 + iVar18 * 0x80 + 0x80 + iVar8);
        uVar2 = uVar17;
        uVar23 = uVar22;
        do {
          uVar17 = uVar21;
          uVar22 = uVar2;
          puVar11 = puVar7 + 0x20;
          *piVar12 = (uVar22 * iVar10 >> 0x1c) +
                     (int)((ulonglong)((longlong)(int)uVar22 * (longlong)iVar10) >> 0x20) * 0x10 +
                     uVar17 + (uVar23 * uVar4 >> 0x1c) +
                              (int)((ulonglong)((longlong)(int)uVar23 * (longlong)(int)uVar4) >>
                                   0x20) * 0x10;
          uVar21 = *puVar7;
          piVar12 = piVar12 + 0x30;
          puVar7 = puVar11;
          uVar2 = uVar17;
          iVar6 = param_10 + -1;
          uVar23 = uVar22;
        } while (puVar5 != puVar11);
      }
      *(uint *)((iVar6 * 0x30 + param_13) * 4 + param_2) =
           uVar21 + (uVar17 * iVar10 >> 0x1c) +
                    (int)((ulonglong)((longlong)(int)uVar17 * (longlong)iVar10) >> 0x20) * 0x10 +
           (uVar22 * uVar4 >> 0x1c) +
           ((int)((ulonglong)uVar22 * (ulonglong)uVar4 >> 0x20) +
           ((int)uVar22 >> 0x1f) * uVar4 + (iVar14 >> 0x1f) * uVar22) * 0x10;
    }
    if (iVar20 + 1 < param_6 + param_8) {
      iVar20 = iVar20 + 1;
      param_13 = param_13 + 1;
      iVar8 = iVar8 + 4;
      puVar5 = puVar5 + 1;
      uVar9 = 0;
      if (param_6 != iVar20) {
        uVar9 = *(undefined4 *)(param_4 + iVar8);
      }
      goto LAB_ram_43011fca;
    }
  }
  return;
}
