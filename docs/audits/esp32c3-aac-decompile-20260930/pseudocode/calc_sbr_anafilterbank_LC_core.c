/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: calc_sbr_anafilterbank_LC_core @ ram:4204e418
 * Types and parameter counts are inferred; verify against disassembly. */

void calc_sbr_anafilterbank_LC_core(int param_1,int *param_2)

{
  short sVar1;
  short sVar2;
  short sVar3;
  short sVar4;
  short sVar5;
  short sVar6;
  short sVar7;
  short sVar8;
  short sVar9;
  short sVar10;
  short sVar11;
  short sVar12;
  short sVar13;
  short sVar14;
  short sVar15;
  longlong lVar16;
  longlong lVar17;
  longlong lVar18;
  longlong lVar19;
  longlong lVar20;
  int *piVar21;
  int *piVar22;
  short *psVar23;
  int *piVar24;
  int *piVar25;
  short *psVar26;
  int iVar27;
  int iVar28;
  int iVar29;
  int iVar30;
  int iVar31;

  gp = &__global_pointer_;
  *param_2 = (int)((ulonglong)((longlong)(*(short *)(param_1 + -0x100) * -0x10000) * -0x4160738) >>
                  0x20) +
             (int)((ulonglong)((longlong)((int)*(short *)(param_1 + -0x180) << 0x10) * -0x4160738)
                  >> 0x20) +
             (int)((ulonglong)((longlong)((int)*(short *)(param_1 + -0x200) << 0x10) * -0x267076) >>
                  0x20) +
             (int)((ulonglong)((longlong)(*(short *)(param_1 + -0x80) * -0x10000) * -0x267076) >>
                  0x20);
  piVar21 = param_2 + 1;
  piVar22 = param_2 + 0x3f;
  psVar23 = (short *)(param_1 + -0x27e);
  piVar24 = &sbrDecoderFilterbankCoefficients_an_filt_LC;
  psVar26 = (short *)(param_1 + -2);
  do {
    sVar1 = psVar23[0x40];
    sVar2 = *psVar23;
    iVar28 = piVar24[1];
    iVar27 = *piVar24;
    sVar3 = psVar23[0x80];
    iVar31 = piVar24[2];
    sVar4 = psVar23[0xc0];
    iVar30 = piVar24[3];
    sVar5 = psVar23[0x100];
    iVar29 = piVar24[4];
    sVar6 = psVar26[-1];
    sVar7 = psVar26[-0x41];
    sVar8 = psVar23[0x41];
    piVar25 = piVar24 + 10;
    sVar9 = psVar23[0x81];
    sVar10 = psVar26[-0x81];
    sVar11 = psVar23[1];
    sVar12 = psVar26[-0x101];
    sVar13 = psVar23[0xc1];
    sVar14 = psVar26[-0xc1];
    sVar15 = psVar23[0x101];
    *piVar21 = (int)((ulonglong)((longlong)((int)psVar26[-0xc0] << 0x10) * (longlong)iVar30) >> 0x20
                    ) + (int)((ulonglong)
                              ((longlong)((int)psVar26[-0x40] << 0x10) * (longlong)iVar28) >> 0x20)
                        + (int)((ulonglong)((longlong)((int)*psVar26 << 0x10) * (longlong)iVar27) >>
                               0x20) +
                        (int)((ulonglong)
                              ((longlong)((int)psVar26[-0x80] << 0x10) * (longlong)iVar31) >> 0x20)
               + (int)((ulonglong)((longlong)((int)psVar26[-0x100] << 0x10) * (longlong)iVar29) >>
                      0x20);
    *piVar22 = (int)((ulonglong)((longlong)((int)sVar3 << 0x10) * (longlong)iVar31) >> 0x20) +
               (int)((ulonglong)((longlong)((int)sVar1 << 0x10) * (longlong)iVar28) >> 0x20) +
               (int)((ulonglong)((longlong)((int)sVar2 << 0x10) * (longlong)iVar27) >> 0x20) +
               (int)((ulonglong)((longlong)((int)sVar4 << 0x10) * (longlong)iVar30) >> 0x20) +
               (int)((ulonglong)((longlong)((int)sVar5 << 0x10) * (longlong)iVar29) >> 0x20);
    iVar29 = piVar24[5];
    iVar30 = piVar24[6];
    iVar31 = piVar24[7];
    iVar27 = piVar24[8];
    iVar28 = piVar24[9];
    piVar21[1] = (int)((ulonglong)((longlong)((int)sVar7 << 0x10) * (longlong)iVar30) >> 0x20) +
                 (int)((ulonglong)((longlong)((int)sVar6 << 0x10) * (longlong)iVar29) >> 0x20) +
                 (int)((ulonglong)((longlong)((int)sVar10 << 0x10) * (longlong)iVar31) >> 0x20) +
                 (int)((ulonglong)((longlong)((int)sVar14 << 0x10) * (longlong)iVar27) >> 0x20) +
                 (int)((ulonglong)((longlong)((int)sVar12 << 0x10) * (longlong)iVar28) >> 0x20);
    piVar22[-1] = (int)((ulonglong)((longlong)((int)sVar8 << 0x10) * (longlong)iVar30) >> 0x20) +
                  (int)((ulonglong)((longlong)((int)sVar11 << 0x10) * (longlong)iVar29) >> 0x20) +
                  (int)((ulonglong)((longlong)((int)sVar9 << 0x10) * (longlong)iVar31) >> 0x20) +
                  (int)((ulonglong)((longlong)((int)sVar13 << 0x10) * (longlong)iVar27) >> 0x20) +
                  (int)((ulonglong)((longlong)((int)sVar15 << 0x10) * (longlong)iVar28) >> 0x20);
    piVar21 = piVar21 + 2;
    piVar22 = piVar22 + -2;
    psVar23 = psVar23 + 2;
    piVar24 = piVar25;
    psVar26 = psVar26 + -2;
  } while (piVar25 != &DAT_ram_3c12a780);
  sVar1 = *(short *)(param_1 + -0xbe);
  sVar2 = *(short *)(param_1 + -0x3e);
  sVar3 = *(short *)(param_1 + -0x240);
  sVar4 = *(short *)(param_1 + -0x40);
  sVar5 = *(short *)(param_1 + -0x13e);
  sVar6 = *(short *)(param_1 + -0xc0);
  lVar16 = (longlong)DAT_ram_3c12a780;
  sVar7 = *(short *)(param_1 + -0x1c0);
  lVar17 = (longlong)DAT_ram_3c12a784;
  sVar8 = *(short *)(param_1 + -0x1be);
  sVar9 = *(short *)(param_1 + -0x140);
  lVar18 = (longlong)DAT_ram_3c12a788;
  sVar10 = *(short *)(param_1 + -0x23e);
  lVar19 = (longlong)DAT_ram_3c12a78c;
  lVar20 = (longlong)DAT_ram_3c12a790;
  param_2[0x21] =
       (int)((ulonglong)
             ((longlong)((int)*(short *)(param_1 + -0x1c2) << 0x10) * (longlong)DAT_ram_3c12a784) >>
            0x20) +
       (int)((ulonglong)
             ((longlong)((int)*(short *)(param_1 + -0x242) << 0x10) * (longlong)DAT_ram_3c12a780) >>
            0x20) +
       (int)((ulonglong)
             ((longlong)((int)*(short *)(param_1 + -0x142) << 0x10) * (longlong)DAT_ram_3c12a788) >>
            0x20) +
       (int)((ulonglong)
             ((longlong)((int)*(short *)(param_1 + -0xc2) << 0x10) * (longlong)DAT_ram_3c12a78c) >>
            0x20) +
       (int)((ulonglong)
             ((longlong)((int)*(short *)(param_1 + -0x42) << 0x10) * (longlong)DAT_ram_3c12a790) >>
            0x20);
  param_2[0x1f] =
       (int)((ulonglong)(((int)sVar1 << 0x10) * lVar17) >> 0x20) +
       (int)((ulonglong)(((int)sVar2 << 0x10) * lVar16) >> 0x20) +
       (int)((ulonglong)(((int)sVar5 << 0x10) * lVar18) >> 0x20) +
       (int)((ulonglong)(((int)sVar8 << 0x10) * lVar19) >> 0x20) +
       (int)((ulonglong)(((int)sVar10 << 0x10) * lVar20) >> 0x20);
  param_2[0x20] =
       (int)((ulonglong)((longlong)((int)sVar3 << 0x10) * 0x796be) >> 0x20) +
       (int)((ulonglong)((longlong)((int)sVar4 << 0x10) * 0x796be) >> 0x20) +
       (int)((ulonglong)((longlong)((int)sVar6 << 0x10) * 0xcbc3d4) >> 0x20) +
       (int)((ulonglong)((longlong)((int)sVar7 << 0x10) * 0xcbc3d4) >> 0x20) +
       (int)((ulonglong)((longlong)((int)sVar9 << 0x10) * 0x9a8b0e0) >> 0x20);
  return;
}
