/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: calc_sbr_anafilterbank @ ram:42041abe
 * Types and parameter counts are inferred; verify against disassembly. */

void calc_sbr_anafilterbank
               (undefined4 param_1,undefined4 param_2,short *param_3,int *param_4,undefined4 param_5
               )

{
  short sVar1;
  short sVar2;
  short sVar3;
  short sVar4;
  short sVar5;
  short *psVar6;
  short *psVar7;
  int *piVar8;
  int *piVar9;
  int *piVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  int iVar15;

  gp = &__global_pointer_;
  piVar10 = &sbrDecoderFilterbankCoefficients_an_filt;
  psVar7 = param_3 + -0x13f;
  *param_4 = (int)((ulonglong)((longlong)((int)param_3[-0x80] << 0x10) * 0x2e3a754) >> 0x20) +
             (int)((ulonglong)((longlong)((int)param_3[-0xc0] << 0x10) * -0x2e3a754) >> 0x20) +
             (int)((ulonglong)((longlong)((int)param_3[-0x100] << 0x10) * -0x1b2e42) >> 0x20) +
             (int)((ulonglong)((longlong)((int)param_3[-0x40] << 0x10) * 0x1b2e42) >> 0x20);
  piVar8 = param_4 + 0x3f;
  psVar6 = param_3;
  piVar9 = param_4;
  do {
    piVar9 = piVar9 + 1;
    iVar15 = piVar10[1];
    iVar14 = *piVar10;
    sVar1 = psVar7[0x40];
    sVar2 = *psVar7;
    iVar13 = piVar10[2];
    sVar3 = psVar7[0x80];
    iVar12 = piVar10[3];
    sVar4 = psVar7[0xc0];
    iVar11 = piVar10[4];
    sVar5 = psVar7[0x100];
    piVar10 = piVar10 + 5;
    psVar7 = psVar7 + 1;
    *piVar9 = (int)((ulonglong)((longlong)((int)psVar6[-0x41] << 0x10) * (longlong)iVar15) >> 0x20)
              + (int)((ulonglong)((longlong)((int)psVar6[-1] << 0x10) * (longlong)iVar14) >> 0x20) +
              (int)((ulonglong)((longlong)((int)psVar6[-0x81] << 0x10) * (longlong)iVar13) >> 0x20)
              + (int)((ulonglong)((longlong)((int)psVar6[-0xc1] << 0x10) * (longlong)iVar12) >> 0x20
                     ) +
              (int)((ulonglong)((longlong)((int)psVar6[-0x101] << 0x10) * (longlong)iVar11) >> 0x20)
    ;
    *piVar8 = (int)((ulonglong)((longlong)((int)sVar1 << 0x10) * (longlong)iVar15) >> 0x20) +
              (int)((ulonglong)((longlong)((int)sVar2 << 0x10) * (longlong)iVar14) >> 0x20) +
              (int)((ulonglong)((longlong)((int)sVar3 << 0x10) * (longlong)iVar13) >> 0x20) +
              (int)((ulonglong)((longlong)((int)sVar4 << 0x10) * (longlong)iVar12) >> 0x20) +
              (int)((ulonglong)((longlong)((int)sVar5 << 0x10) * (longlong)iVar11) >> 0x20);
    piVar8 = piVar8 + -1;
    psVar6 = psVar6 + -1;
  } while (piVar10 != &sbrDecoderFilterbankCoefficients_an_filt_LC);
  param_4[0x20] =
       (int)((ulonglong)((longlong)((int)param_3[-0x120] << 0x10) * 0x55dba) >> 0x20) +
       (int)((ulonglong)((longlong)((int)param_3[-0x20] << 0x10) * 0x55dba) >> 0x20) +
       (int)((ulonglong)((longlong)((int)param_3[-0x60] << 0x10) * 0x901566) >> 0x20) +
       (int)((ulonglong)((longlong)((int)param_3[-0xe0] << 0x10) * 0x901566) >> 0x20) +
       (int)((ulonglong)((longlong)((int)param_3[-0xa0] << 0x10) * 0x6d474e0) >> 0x20);
  analysis_sub_band(param_4,param_1,param_2,param_5,param_4 + 0x40);
  return;
}
