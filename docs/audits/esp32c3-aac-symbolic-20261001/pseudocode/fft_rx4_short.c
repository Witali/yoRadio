/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: fft_rx4_short @ ram:43006a42
 * Types and parameter counts are inferred; verify against disassembly. */

int fft_rx4_short(int *param_1,uint *param_2)

{
  int *piVar1;
  int *piVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  uint uVar10;
  int iVar11;
  int iVar12;
  uint uVar13;
  int iVar14;
  uint uVar15;
  int iVar16;
  int iVar17;
  uint *puVar18;
  int iVar19;
  int iVar20;
  int iVar21;
  int *piVar22;
  uint uVar23;
  int iVar24;
  int iVar25;
  uint *puVar26;
  int iVar27;
  int iVar28;
  int iVar29;
  int iVar30;
  int *piVar31;
  uint uVar32;
  int *piVar33;
  int iVar34;
  uint uVar35;
  int iVar36;

  gp = &__global_pointer_;
  iVar8 = 0;
  if (0x8000 < (int)*param_2) {
    iVar8 = pv_normalize(*param_2);
    iVar8 = 8 - iVar8;
  }
  iVar14 = 2;
  iVar28 = 2;
  puVar18 = &W_64rx4;
  iVar4 = iVar8;
  iVar20 = 0x40;
  while( true ) {
    iVar16 = iVar20 >> 1;
    uVar10 = iVar4 - 2;
    iVar21 = iVar20 >> 2;
    piVar2 = param_1 + iVar16 + iVar20;
    piVar1 = param_1 + iVar16;
    piVar22 = param_1 + iVar20;
    iVar4 = 0;
    piVar33 = param_1;
    do {
      iVar9 = (*piVar33 >> iVar28) + (*piVar22 >> iVar28);
      iVar11 = (*piVar33 >> iVar28) - (*piVar22 >> iVar28);
      iVar24 = (*piVar1 >> iVar28) + (*piVar2 >> iVar28);
      iVar6 = (*piVar1 >> iVar28) - (*piVar2 >> iVar28);
      *piVar33 = iVar9 + iVar24 >> (uVar10 & 0x1f);
      *piVar22 = iVar9 - iVar24 >> (uVar10 & 0x1f);
      iVar24 = (piVar33[1] >> iVar28) + (piVar22[1] >> iVar28);
      iVar9 = (piVar33[1] >> iVar28) - (piVar22[1] >> iVar28);
      iVar25 = (piVar1[1] >> iVar28) + (piVar2[1] >> iVar28);
      iVar30 = (piVar1[1] >> iVar28) - (piVar2[1] >> iVar28);
      piVar33[1] = iVar24 + iVar25 >> (uVar10 & 0x1f);
      piVar22[1] = iVar24 - iVar25 >> (uVar10 & 0x1f);
      piVar2[1] = iVar6 + iVar9 >> (uVar10 & 0x1f);
      *piVar2 = iVar11 - iVar30 >> (uVar10 & 0x1f);
      piVar1[1] = iVar9 - iVar6 >> (uVar10 & 0x1f);
      *piVar1 = iVar11 + iVar30 >> (uVar10 & 0x1f);
      iVar4 = iVar4 + iVar20;
      piVar33 = piVar33 + iVar20 * 2;
      piVar22 = piVar22 + iVar20 * 2;
      piVar1 = piVar1 + iVar20 * 2;
      piVar2 = piVar2 + iVar20 * 2;
    } while (iVar4 < 0x40);
    if (iVar21 != 1) {
      piVar33 = param_1 + 2;
      iVar4 = 1;
      puVar26 = puVar18;
      do {
        if (iVar4 < 0x40) {
          piVar31 = piVar33 + iVar20;
          iVar24 = *puVar26 << 0x10;
          piVar2 = piVar33 + iVar16;
          iVar11 = puVar26[1] << 0x10;
          iVar9 = puVar26[2] << 0x10;
          uVar7 = *puVar26 & 0xffff0000;
          uVar5 = puVar26[1] & 0xffff0000;
          uVar3 = puVar26[2] & 0xffff0000;
          piVar22 = piVar33 + iVar16 + iVar20;
          iVar6 = iVar4;
          piVar1 = piVar33;
          do {
            iVar17 = (*piVar1 >> iVar28) + (*piVar31 >> iVar28);
            iVar19 = (*piVar1 >> iVar28) - (*piVar31 >> iVar28);
            iVar25 = (*piVar2 >> iVar28) + (*piVar22 >> iVar28);
            iVar29 = (*piVar2 >> iVar28) - (*piVar22 >> iVar28);
            *piVar1 = iVar17 + iVar25 >> (uVar10 & 0x1f);
            iVar27 = (piVar1[1] >> iVar28) + (piVar31[1] >> iVar28);
            iVar12 = (piVar1[1] >> iVar28) - (piVar31[1] >> iVar28);
            iVar30 = (piVar2[1] >> iVar28) + (piVar22[1] >> iVar28);
            iVar36 = (piVar2[1] >> iVar28) - (piVar22[1] >> iVar28);
            iVar17 = iVar17 - iVar25 >> (uVar10 & 0x1f);
            iVar34 = iVar27 - iVar30 >> (uVar10 & 0x1f);
            piVar1[1] = iVar30 + iVar27 >> (uVar10 & 0x1f);
            iVar25 = iVar19 + iVar36 >> (uVar10 & 0x1f);
            iVar27 = iVar12 - iVar29 >> (uVar10 & 0x1f);
            iVar19 = iVar19 - iVar36 >> (uVar10 & 0x1f);
            iVar30 = iVar12 + iVar29 >> (uVar10 & 0x1f);
            iVar6 = iVar6 + iVar20;
            piVar1 = piVar1 + iVar20 * 2;
            *piVar31 = ((int)((ulonglong)((longlong)iVar17 * (longlong)(int)uVar5) >> 0x20) +
                       (int)((ulonglong)((longlong)iVar34 * (longlong)iVar11) >> 0x20)) * 2;
            piVar31[1] = ((int)((ulonglong)((longlong)iVar34 * (longlong)(int)uVar5) >> 0x20) +
                         (int)((ulonglong)((longlong)-iVar17 * (longlong)iVar11) >> 0x20)) * 2;
            piVar31 = piVar31 + iVar20 * 2;
            piVar2[1] = ((int)((ulonglong)((longlong)iVar27 * (longlong)(int)uVar7) >> 0x20) +
                        (int)((ulonglong)((longlong)-iVar25 * (longlong)iVar24) >> 0x20)) * 2;
            *piVar2 = ((int)((ulonglong)((longlong)iVar25 * (longlong)(int)uVar7) >> 0x20) +
                      (int)((ulonglong)((longlong)iVar27 * (longlong)iVar24) >> 0x20)) * 2;
            piVar2 = piVar2 + iVar20 * 2;
            piVar22[1] = ((int)((ulonglong)((longlong)iVar30 * (longlong)(int)uVar3) >> 0x20) +
                         (int)((ulonglong)((longlong)-iVar19 * (longlong)iVar9) >> 0x20)) * 2;
            *piVar22 = ((int)((ulonglong)((longlong)iVar19 * (longlong)(int)uVar3) >> 0x20) +
                       (int)((ulonglong)((longlong)iVar30 * (longlong)iVar9) >> 0x20)) * 2;
            piVar22 = piVar22 + iVar20 * 2;
          } while (iVar6 < 0x40);
        }
        piVar33 = piVar33 + 2;
        iVar4 = iVar4 + 1;
        puVar26 = puVar26 + 3;
      } while (param_1 + iVar21 * 2 != piVar33);
      puVar18 = puVar18 + (iVar21 + -2) * 3 + 3;
    }
    iVar4 = 2;
    iVar28 = 0;
    if (iVar14 == 1) break;
    iVar14 = 1;
    iVar20 = iVar21;
  }
  uVar10 = 0;
  puVar18 = (uint *)(param_1 + -7);
  do {
    puVar26 = puVar18 + 8;
    iVar28 = puVar18[7] + puVar18[0xb];
    iVar4 = puVar18[9] + puVar18[0xd];
    uVar35 = iVar28 + iVar4;
    iVar14 = puVar18[10] + puVar18[0xe];
    uVar5 = iVar28 - iVar4;
    iVar28 = *puVar26 + puVar18[0xc];
    uVar3 = iVar28 + iVar14;
    uVar32 = iVar28 - iVar14;
    iVar4 = *puVar26 - puVar18[0xc];
    iVar28 = puVar18[9] - puVar18[0xd];
    uVar7 = iVar4 - iVar28;
    iVar14 = puVar18[10] - puVar18[0xe];
    uVar13 = iVar28 + iVar4;
    iVar28 = puVar18[7] - puVar18[0xb];
    uVar23 = iVar28 - iVar14;
    uVar15 = iVar28 + iVar14;
    *puVar26 = uVar3;
    puVar18[0xc] = uVar32;
    puVar18[7] = uVar35;
    puVar18[0xb] = uVar5;
    puVar18[10] = uVar7;
    puVar18[0xe] = uVar13;
    puVar18[0xd] = uVar23;
    puVar18[9] = uVar15;
    uVar10 = uVar10 | (int)uVar35 >> 0x1f ^ uVar35 | (int)uVar5 >> 0x1f ^ uVar5 |
                      (int)uVar3 >> 0x1f ^ uVar3 | (int)uVar32 >> 0x1f ^ uVar32 |
                      (int)uVar7 >> 0x1f ^ uVar7 | (int)uVar13 >> 0x1f ^ uVar13 |
                      (int)uVar23 >> 0x1f ^ uVar23 | (int)uVar15 >> 0x1f ^ uVar15;
    puVar18 = puVar26;
  } while (puVar26 != (uint *)(param_1 + 0x79));
  *param_2 = uVar10;
  return iVar8;
}
