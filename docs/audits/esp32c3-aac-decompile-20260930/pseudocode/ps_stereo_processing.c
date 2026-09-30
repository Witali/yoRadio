/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: ps_stereo_processing @ ram:420480ee
 * Types and parameter counts are inferred; verify against disassembly. */

void ps_stereo_processing(int param_1,int param_2,int param_3,int param_4,int param_5)

{
  int iVar1;
  int iVar2;
  char *pcVar3;
  uint *puVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  int *piVar8;
  uint uVar9;
  uint uVar10;
  int iVar11;
  int *piVar12;
  int *piVar13;
  int iVar14;
  int iVar15;
  int iVar16;
  uint uVar17;
  int iVar18;
  int *piVar19;

  gp = &__global_pointer_;
  iVar1 = *(int *)(param_1 + 0x14);
  iVar16 = *(int *)(param_1 + 0x1ec);
  iVar15 = *(int *)(param_1 + 0x1f0);
  iVar14 = *(int *)(param_1 + 500);
  iVar2 = *(int *)(param_1 + 0x1f8);
  pcVar3 = "\x04\x05";
  puVar4 = (uint *)(param_1 + 0x360);
  do {
    uVar6 = puVar4[0x16];
    uVar9 = *puVar4;
    uVar17 = puVar4[0x42];
    uVar5 = puVar4[0x2c];
    puVar4[0x16] = puVar4[0x6e] + uVar6;
    *puVar4 = uVar9 + puVar4[0x58];
    puVar4[0x42] = puVar4[0x9a] + uVar17;
    puVar4[0x2c] = uVar5 + puVar4[0x84];
    uVar10 = uVar9 + puVar4[0x58] & 0xffff0000;
    uVar5 = uVar5 + puVar4[0x84] & 0xffff0000;
    iVar18 = *pcVar3 * 4;
    piVar13 = (int *)(iVar16 + iVar18);
    piVar12 = (int *)(iVar14 + iVar18);
    uVar9 = puVar4[0x6e] + uVar6 & 0xffff0000;
    iVar11 = *piVar13 << 1;
    iVar7 = *piVar12 << 1;
    uVar6 = puVar4[0x9a] + uVar17 & 0xffff0000;
    piVar8 = (int *)(iVar15 + iVar18);
    piVar19 = (int *)(iVar18 + iVar2);
    pcVar3 = pcVar3 + 1;
    puVar4 = puVar4 + 1;
    *piVar13 = ((int)((ulonglong)((longlong)iVar11 * (longlong)(int)uVar10) >> 0x20) +
               (int)((ulonglong)((longlong)iVar7 * (longlong)(int)uVar5) >> 0x20)) * 2;
    *piVar12 = ((int)((ulonglong)((longlong)(int)uVar6 * (longlong)iVar7) >> 0x20) +
               (int)((ulonglong)((longlong)(int)uVar9 * (longlong)iVar11) >> 0x20)) * 2;
    iVar7 = *piVar8 << 1;
    iVar11 = *piVar19 << 1;
    *piVar8 = ((int)((ulonglong)((longlong)iVar11 * (longlong)(int)uVar5) >> 0x20) +
              (int)((ulonglong)((longlong)iVar7 * (longlong)(int)uVar10) >> 0x20)) * 2;
    *piVar19 = ((int)((ulonglong)((longlong)iVar7 * (longlong)(int)uVar9) >> 0x20) +
               (int)((ulonglong)((longlong)iVar11 * (longlong)(int)uVar6) >> 0x20)) * 2;
  } while (pcVar3 != "\x03\x04\x05\x06\a\b\t\v\x0e\x12\x17#@");
  uVar10 = *(int *)(param_1 + 0x540) + *(int *)(param_1 + 0x3e0);
  uVar9 = *(int *)(param_1 + 0x388) + *(int *)(param_1 + 0x4e8);
  uVar5 = *(int *)(param_1 + 0x5f0) + *(int *)(param_1 + 0x490);
  *(uint *)(param_1 + 0x3e0) = uVar10;
  uVar6 = *(int *)(param_1 + 0x438) + *(int *)(param_1 + 0x598);
  *(uint *)(param_1 + 0x388) = uVar9;
  *(uint *)(param_1 + 0x490) = uVar5;
  *(uint *)(param_1 + 0x438) = uVar6;
  uVar6 = uVar6 & 0xffff0000;
  iVar14 = *(int *)(param_2 + 0xc) << 1;
  iVar2 = *(int *)(param_4 + 0xc) << 1;
  uVar9 = uVar9 & 0xffff0000;
  uVar10 = uVar10 & 0xffff0000;
  uVar5 = uVar5 & 0xffff0000;
  puVar4 = (uint *)(param_1 + 0x38c);
  pcVar3 = "\x04\x05\x06\a\b\t\v\x0e\x12\x17#@";
  *(int *)(param_2 + 0xc) =
       ((int)((ulonglong)((longlong)iVar2 * (longlong)(int)uVar6) >> 0x20) +
       (int)((ulonglong)((longlong)iVar14 * (longlong)(int)uVar9) >> 0x20)) * 2;
  *(int *)(param_4 + 0xc) =
       ((int)((ulonglong)((longlong)(int)uVar5 * (longlong)iVar2) >> 0x20) +
       (int)((ulonglong)((longlong)(int)uVar10 * (longlong)iVar14) >> 0x20)) * 2;
  iVar14 = *(int *)(param_3 + 0xc) << 1;
  iVar2 = *(int *)(param_5 + 0xc) << 1;
  *(int *)(param_3 + 0xc) =
       ((int)((ulonglong)((longlong)iVar2 * (longlong)(int)uVar6) >> 0x20) +
       (int)((ulonglong)((longlong)iVar14 * (longlong)(int)uVar9) >> 0x20)) * 2;
  *(int *)(param_5 + 0xc) =
       ((int)((ulonglong)((longlong)iVar2 * (longlong)(int)uVar5) >> 0x20) +
       (int)((ulonglong)((longlong)iVar14 * (longlong)(int)uVar10) >> 0x20)) * 2;
  do {
    uVar5 = puVar4[0x16];
    uVar10 = *puVar4;
    uVar9 = puVar4[0x2c];
    uVar6 = puVar4[0x42];
    puVar4[0x16] = puVar4[0x6e] + uVar5;
    *puVar4 = uVar10 + puVar4[0x58];
    puVar4[0x42] = puVar4[0x9a] + uVar6;
    puVar4[0x2c] = uVar9 + puVar4[0x84];
    iVar14 = (int)*pcVar3;
    iVar2 = iVar1;
    if (pcVar3[1] < iVar1) {
      iVar2 = (int)pcVar3[1];
    }
    if (iVar14 < iVar2) {
      iVar15 = iVar14 * 4;
      uVar9 = uVar9 + puVar4[0x84] & 0xffff0000;
      uVar10 = uVar10 + puVar4[0x58] & 0xffff0000;
      uVar6 = puVar4[0x9a] + uVar6 & 0xffff0000;
      uVar5 = puVar4[0x6e] + uVar5 & 0xffff0000;
      piVar8 = (int *)(param_2 + iVar15);
      piVar12 = (int *)(param_4 + iVar15);
      do {
        iVar16 = *piVar8;
        iVar7 = *piVar12;
        piVar13 = piVar8 + 1;
        *piVar8 = ((int)((ulonglong)((longlong)(iVar7 << 1) * (longlong)(int)uVar9) >> 0x20) +
                  (int)((ulonglong)((longlong)(iVar16 << 1) * (longlong)(int)uVar10) >> 0x20)) * 2;
        *piVar12 = ((int)((ulonglong)((longlong)(iVar7 << 1) * (longlong)(int)uVar6) >> 0x20) +
                   (int)((ulonglong)((longlong)(iVar16 << 1) * (longlong)(int)uVar5) >> 0x20)) * 2;
        piVar8 = piVar13;
        piVar12 = piVar12 + 1;
      } while (piVar13 != (int *)(param_2 + iVar15) + (iVar2 - iVar14));
      piVar8 = (int *)(param_3 + iVar15);
      piVar12 = (int *)(iVar15 + param_5);
      do {
        iVar16 = *piVar8;
        iVar7 = *piVar12;
        piVar13 = piVar8 + 1;
        *piVar8 = ((int)((ulonglong)((longlong)(iVar7 << 1) * (longlong)(int)uVar9) >> 0x20) +
                  (int)((ulonglong)((longlong)(iVar16 << 1) * (longlong)(int)uVar10) >> 0x20)) * 2;
        *piVar12 = ((int)((ulonglong)((longlong)(iVar7 << 1) * (longlong)(int)uVar6) >> 0x20) +
                   (int)((ulonglong)((longlong)(iVar16 << 1) * (longlong)(int)uVar5) >> 0x20)) * 2;
        piVar8 = piVar13;
        piVar12 = piVar12 + 1;
      } while (piVar13 != (int *)(param_3 + iVar15) + (iVar2 - iVar14));
    }
    pcVar3 = pcVar3 + 1;
    puVar4 = puVar4 + 1;
  } while (pcVar3 != "@");
  return;
}
