/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: fft_rx4_long @ ram:430066fa
 * Types and parameter counts are inferred; verify against disassembly. */

void fft_rx4_long(int *param_1,uint *param_2)

{
  int *piVar1;
  uint uVar2;
  int iVar3;
  int *piVar4;
  uint uVar5;
  int *piVar6;
  int iVar7;
  uint *puVar8;
  uint uVar9;
  int iVar10;
  uint uVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  uint uVar16;
  int iVar17;
  int *piVar18;
  uint uVar19;
  int iVar20;
  int iVar21;
  int *piVar22;
  int iVar23;
  int iVar24;
  uint *puVar25;
  int iVar26;
  int iVar27;
  int iVar28;
  int iVar29;
  uint uVar30;
  int iVar31;
  uint uVar32;
  uint uVar33;

  gp = &__global_pointer_;
  puVar8 = &W_256rx4;
  iVar12 = 3;
  iVar13 = 0x100;
  do {
    iVar10 = iVar13 >> 1;
    iVar14 = iVar13 >> 2;
    piVar6 = param_1 + iVar13 + iVar10;
    piVar4 = param_1 + iVar10;
    piVar1 = param_1 + iVar13;
    iVar7 = 0;
    piVar22 = param_1;
    do {
      iVar7 = iVar7 + iVar13;
      iVar17 = *piVar22 + *piVar1;
      iVar15 = *piVar22 - *piVar1;
      iVar3 = *piVar4 + *piVar6;
      iVar31 = *piVar4 - *piVar6;
      *piVar22 = iVar17 + iVar3;
      *piVar1 = iVar17 - iVar3;
      iVar17 = piVar22[1];
      iVar21 = piVar1[1];
      iVar3 = piVar4[1];
      iVar24 = piVar6[1];
      iVar20 = iVar17 - iVar21;
      piVar4[1] = iVar20 - iVar31;
      iVar17 = iVar17 + iVar21;
      iVar21 = iVar3 + iVar24;
      piVar6[1] = iVar31 + iVar20;
      piVar22[1] = iVar17 + iVar21;
      iVar3 = iVar3 - iVar24;
      piVar1[1] = iVar17 - iVar21;
      *piVar6 = iVar15 - iVar3;
      *piVar4 = iVar15 + iVar3;
      piVar22 = piVar22 + iVar13 * 2;
      piVar1 = piVar1 + iVar13 * 2;
      piVar4 = piVar4 + iVar13 * 2;
      piVar6 = piVar6 + iVar13 * 2;
    } while (iVar7 < 0x100);
    if (iVar14 != 1) {
      piVar22 = param_1 + 2;
      iVar7 = 1;
      puVar25 = puVar8;
      do {
        if (iVar7 < 0x100) {
          piVar18 = piVar22 + iVar13;
          iVar20 = *puVar25 << 0x10;
          piVar6 = piVar22 + iVar10;
          iVar17 = puVar25[1] << 0x10;
          iVar15 = puVar25[2] << 0x10;
          uVar5 = *puVar25 & 0xffff0000;
          uVar2 = puVar25[1] & 0xffff0000;
          uVar32 = puVar25[2] & 0xffff0000;
          piVar4 = piVar22 + iVar13 + iVar10;
          piVar1 = piVar22;
          iVar3 = iVar7;
          do {
            iVar3 = iVar3 + iVar13;
            iVar29 = *piVar1 + *piVar18;
            iVar31 = *piVar1 - *piVar18;
            iVar21 = *piVar6 + *piVar4;
            iVar27 = *piVar6 - *piVar4;
            *piVar1 = iVar29 + iVar21;
            iVar29 = iVar29 - iVar21;
            iVar26 = piVar18[1] + piVar1[1];
            iVar21 = piVar1[1] - piVar18[1];
            iVar28 = piVar6[1] + piVar4[1];
            iVar24 = piVar6[1] - piVar4[1];
            iVar23 = (iVar26 - iVar28) * 2;
            piVar1[1] = iVar26 + iVar28;
            iVar26 = iVar31 + iVar24;
            iVar31 = iVar31 - iVar24;
            iVar24 = (iVar21 - iVar27) * 2;
            iVar21 = (iVar21 + iVar27) * 2;
            piVar1 = piVar1 + iVar13 * 2;
            *piVar18 = (int)((ulonglong)((longlong)(iVar29 * 2) * (longlong)(int)uVar2) >> 0x20) +
                       (int)((ulonglong)((longlong)iVar23 * (longlong)iVar17) >> 0x20);
            piVar18[1] = (int)((ulonglong)((longlong)(iVar29 * -2) * (longlong)iVar17) >> 0x20) +
                         (int)((ulonglong)((longlong)iVar23 * (longlong)(int)uVar2) >> 0x20);
            piVar18 = piVar18 + iVar13 * 2;
            piVar6[1] = (int)((ulonglong)((longlong)iVar24 * (longlong)(int)uVar5) >> 0x20) +
                        (int)((ulonglong)((longlong)(iVar26 * -2) * (longlong)iVar20) >> 0x20);
            *piVar6 = (int)((ulonglong)((longlong)(iVar26 * 2) * (longlong)(int)uVar5) >> 0x20) +
                      (int)((ulonglong)((longlong)iVar24 * (longlong)iVar20) >> 0x20);
            piVar6 = piVar6 + iVar13 * 2;
            piVar4[1] = (int)((ulonglong)((longlong)iVar21 * (longlong)(int)uVar32) >> 0x20) +
                        (int)((ulonglong)((longlong)(iVar31 * -2) * (longlong)iVar15) >> 0x20);
            *piVar4 = (int)((ulonglong)((longlong)(iVar31 * 2) * (longlong)(int)uVar32) >> 0x20) +
                      (int)((ulonglong)((longlong)iVar21 * (longlong)iVar15) >> 0x20);
            piVar4 = piVar4 + iVar13 * 2;
          } while (iVar3 < 0x100);
        }
        piVar22 = piVar22 + 2;
        iVar7 = iVar7 + 1;
        puVar25 = puVar25 + 3;
      } while (param_1 + iVar14 * 2 != piVar22);
      puVar8 = puVar8 + (iVar14 + -2) * 3 + 3;
    }
    iVar12 = iVar12 + -1;
    iVar13 = iVar14;
  } while (iVar12 != 0);
  uVar2 = 0;
  puVar8 = (uint *)(param_1 + -7);
  do {
    puVar25 = puVar8 + 8;
    iVar7 = puVar8[7] + puVar8[0xb];
    iVar13 = puVar8[9] + puVar8[0xd];
    uVar30 = iVar7 + iVar13;
    iVar12 = puVar8[10] + puVar8[0xe];
    uVar19 = iVar7 - iVar13;
    iVar13 = puVar8[0xc] + *puVar25;
    uVar33 = iVar13 + iVar12;
    uVar32 = iVar13 - iVar12;
    iVar7 = *puVar25 - puVar8[0xc];
    iVar12 = puVar8[9] - puVar8[0xd];
    uVar5 = iVar7 - iVar12;
    iVar13 = puVar8[10] - puVar8[0xe];
    uVar9 = iVar12 + iVar7;
    iVar12 = puVar8[7] - puVar8[0xb];
    uVar16 = iVar12 - iVar13;
    uVar11 = iVar12 + iVar13;
    *puVar25 = uVar33;
    puVar8[0xc] = uVar32;
    puVar8[7] = uVar30;
    puVar8[0xb] = uVar19;
    puVar8[10] = uVar5;
    puVar8[0xe] = uVar9;
    puVar8[0xd] = uVar16;
    puVar8[9] = uVar11;
    uVar2 = uVar2 | (int)uVar30 >> 0x1f ^ uVar30 | (int)uVar19 >> 0x1f ^ uVar19 |
                    (int)uVar33 >> 0x1f ^ uVar33 | (int)uVar32 >> 0x1f ^ uVar32 |
                    (int)uVar5 >> 0x1f ^ uVar5 | (int)uVar9 >> 0x1f ^ uVar9 |
                    (int)uVar16 >> 0x1f ^ uVar16 | (int)uVar11 >> 0x1f ^ uVar11;
    puVar8 = puVar25;
  } while (puVar25 != (uint *)(param_1 + 0x1f9));
  *param_2 = uVar2;
  return;
}
