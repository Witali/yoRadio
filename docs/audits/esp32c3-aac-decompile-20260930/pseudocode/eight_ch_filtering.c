/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: eight_ch_filtering @ ram:42059f24
 * Types and parameter counts are inferred; verify against disassembly. */

void eight_ch_filtering(int *param_1,int *param_2,int *param_3,int *param_4,undefined4 param_5)

{
  int iVar1;
  int iVar2;

  gp = &__global_pointer_;
  iVar1 = ((uint)(param_1[4] * -0x23c9b4c) >> 0x1d) +
          (int)((ulonglong)((longlong)param_1[4] * -0x23c9b4c) >> 0x20) * 8 +
          (int)((ulonglong)((longlong)param_1[0xc] * 0x159bdee) >> 0x20);
  iVar2 = ((uint)(param_2[4] * -0x23c9b4c) >> 0x1d) +
          (int)((ulonglong)((longlong)param_2[4] * -0x23c9b4c) >> 0x20) * 8 +
          (int)((ulonglong)((longlong)param_2[0xc] * 0x159bdee) >> 0x20);
  param_3[2] = iVar2 - iVar1;
  param_4[2] = -(iVar2 + iVar1);
  iVar1 = ((uint)(param_1[3] * -0x2533d74) >> 0x1d) +
          (int)((ulonglong)((longlong)param_1[3] * -0x2533d74) >> 0x20) * 8 +
          (int)((ulonglong)((longlong)param_1[0xb] * 0x5cff170) >> 0x20);
  iVar2 = ((uint)(param_2[3] * -0x2533d74) >> 0x1d) +
          (int)((ulonglong)((longlong)param_2[3] * -0x2533d74) >> 0x20) * 8 +
          (int)((ulonglong)((longlong)param_2[0xb] * 0x5cff170) >> 0x20);
  param_3[3] = ((uint)(iVar2 * 0x1d906bc0) >> 0x1d) +
               (int)((ulonglong)((longlong)iVar2 * 0x1d906bc0) >> 0x20) * 8 +
               ((uint)(iVar1 * -0xc3ef150) >> 0x1d) +
               (int)((ulonglong)((longlong)iVar1 * -0xc3ef150) >> 0x20) * 8;
  param_4[3] = ((uint)(iVar2 * -0xc3ef150) >> 0x1d) +
               (int)((ulonglong)((longlong)iVar2 * -0xc3ef150) >> 0x20) * 8 +
               ((uint)(iVar1 * -0x1d906bc0) >> 0x1d) +
               (int)((ulonglong)((longlong)iVar1 * -0x1d906bc0) >> 0x20) * 8;
  param_4[4] = (int)((ulonglong)((longlong)(param_1[2] - param_1[10]) * 0xba3d580) >> 0x20);
  param_3[4] = (int)((ulonglong)((longlong)(param_2[10] - param_2[2]) * 0xba3d580) >> 0x20);
  iVar2 = ((uint)(param_1[1] * -0xb9fe2e) >> 0x1d) +
          (int)((ulonglong)((longlong)param_1[1] * -0xb9fe2e) >> 0x20) * 8 +
          (int)((ulonglong)((longlong)param_1[9] * 0x1299eba0) >> 0x20);
  iVar1 = ((uint)(param_2[1] * -0xb9fe2e) >> 0x1d) +
          (int)((ulonglong)((longlong)param_2[1] * -0xb9fe2e) >> 0x20) * 8 +
          (int)((ulonglong)((longlong)param_2[9] * 0x1299eba0) >> 0x20);
  param_3[5] = ((uint)(iVar1 * 0x1d906bc0) >> 0x1d) +
               (int)((ulonglong)((longlong)iVar1 * 0x1d906bc0) >> 0x20) * 8 +
               (int)((ulonglong)((longlong)iVar2 * 0x61f78a80) >> 0x20);
  param_4[5] = ((uint)(iVar2 * -0x1d906bc0) >> 0x1d) +
               (int)((ulonglong)((longlong)iVar2 * -0x1d906bc0) >> 0x20) * 8 +
               (int)((ulonglong)((longlong)iVar1 * 0x61f78a80) >> 0x20);
  iVar2 = ((uint)(*param_1 * -0x2b37be) >> 0x1d) +
          (int)((ulonglong)((longlong)*param_1 * -0x2b37be) >> 0x20) * 8 +
          (int)((ulonglong)((longlong)param_1[8] * 0x11e4da60) >> 0x20);
  iVar1 = ((uint)(*param_2 * -0x2b37be) >> 0x1d) +
          (int)((ulonglong)((longlong)*param_2 * -0x2b37be) >> 0x20) * 8 +
          (int)((ulonglong)((longlong)param_2[8] * 0x11e4da60) >> 0x20);
  param_3[6] = iVar1 + iVar2;
  param_4[6] = iVar1 - iVar2;
  param_3[7] = (int)((ulonglong)((longlong)param_2[7] * 0xb8dcf00) >> 0x20) +
               (int)((ulonglong)((longlong)param_1[7] * 0x1be4c800) >> 0x20);
  param_4[7] = ((uint)(param_1[7] * -0x171b9e0) >> 0x1d) +
               (int)((ulonglong)((longlong)param_1[7] * -0x171b9e0) >> 0x20) * 8 +
               (int)((ulonglong)((longlong)param_2[7] * 0x1be4c800) >> 0x20);
  *param_3 = param_1[6] >> 3;
  *param_4 = param_2[6] >> 3;
  param_3[1] = ((uint)(param_2[5] * -0x171b9e0) >> 0x1d) +
               (int)((ulonglong)((longlong)param_2[5] * -0x171b9e0) >> 0x20) * 8 +
               (int)((ulonglong)((longlong)param_1[5] * 0x1be4c800) >> 0x20);
  param_4[1] = (int)((ulonglong)((longlong)param_2[5] * 0x1be4c800) >> 0x20) +
               (int)((ulonglong)((longlong)param_1[5] * 0xb8dcf00) >> 0x20);
  ps_fft_rx8(param_3,param_4,param_5);
  return;
}
