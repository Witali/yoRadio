/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: ps_stereo_processing @ ram:4300e03a
 * Types and parameter counts are inferred; verify against disassembly. */

void ps_stereo_processing(aac_ps_abi_t *ps,int param_2,int param_3,int param_4,int param_5)

{
  char cVar1;
  int iVar2;
  int32_t *piVar3;
  char *pcVar4;
  int *piVar5;
  int *piVar6;
  int iVar7;
  int32_t (*paiVar8) [22];
  uint uVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  int *piVar15;
  uint uVar16;
  uint uVar17;
  uint uVar18;
  int iVar19;
  int32_t *piVar20;
  int32_t *piVar21;
  int32_t *piVar22;

  gp = &__global_pointer_;
  iVar2 = ps->upper_subband;
  piVar22 = ps->hybrid_left_real;
  piVar21 = ps->hybrid_left_imag;
  piVar20 = ps->hybrid_right_real;
  piVar3 = ps->hybrid_right_imag;
  pcVar4 = "\x04\x05";
  paiVar8 = ps->mix;
  do {
    uVar17 = paiVar8[5][0] + paiVar8[1][0];
    uVar18 = (*paiVar8)[0] + paiVar8[4][0];
    uVar16 = paiVar8[7][0] + paiVar8[3][0];
    paiVar8[1][0] = uVar17;
    uVar9 = paiVar8[2][0] + paiVar8[6][0];
    (*paiVar8)[0] = uVar18;
    paiVar8[3][0] = uVar16;
    paiVar8[2][0] = uVar9;
    cVar1 = *pcVar4;
    uVar18 = uVar18 & 0xffff0000;
    uVar9 = uVar9 & 0xffff0000;
    uVar17 = uVar17 & 0xffff0000;
    iVar19 = piVar22[cVar1] << 1;
    iVar11 = piVar20[cVar1] << 1;
    uVar16 = uVar16 & 0xffff0000;
    pcVar4 = pcVar4 + 1;
    paiVar8 = (int32_t (*) [22])(*paiVar8 + 1);
    piVar22[cVar1] =
         ((int)((ulonglong)((longlong)iVar19 * (longlong)(int)uVar18) >> 0x20) +
         (int)((ulonglong)((longlong)iVar11 * (longlong)(int)uVar9) >> 0x20)) * 2;
    piVar20[cVar1] =
         ((int)((ulonglong)((longlong)(int)uVar16 * (longlong)iVar11) >> 0x20) +
         (int)((ulonglong)((longlong)(int)uVar17 * (longlong)iVar19) >> 0x20)) * 2;
    iVar11 = piVar21[cVar1] << 1;
    iVar19 = piVar3[cVar1] << 1;
    piVar21[cVar1] =
         ((int)((ulonglong)((longlong)iVar19 * (longlong)(int)uVar9) >> 0x20) +
         (int)((ulonglong)((longlong)iVar11 * (longlong)(int)uVar18) >> 0x20)) * 2;
    piVar3[cVar1] =
         ((int)((ulonglong)((longlong)iVar11 * (longlong)(int)uVar17) >> 0x20) +
         (int)((ulonglong)((longlong)iVar19 * (longlong)(int)uVar16) >> 0x20)) * 2;
  } while (pcVar4 != "\x03\x04\x05\x06\a\b\t\v\x0e\x12\x17#@");
  uVar18 = ps->delta_mix[1][10] + ps->mix[1][10];
  uVar17 = ps->mix[0][10] + ps->delta_mix[0][10];
  iVar19 = ps->delta_mix[2][10];
  iVar11 = ps->mix[2][10];
  uVar9 = ps->delta_mix[3][10] + ps->mix[3][10];
  ps->mix[1][10] = uVar18;
  uVar16 = iVar11 + iVar19;
  ps->mix[0][10] = uVar17;
  ps->mix[3][10] = uVar9;
  ps->mix[2][10] = uVar16;
  uVar16 = uVar16 & 0xffff0000;
  iVar19 = *(int *)(param_2 + 0xc) << 1;
  iVar11 = *(int *)(param_4 + 0xc) << 1;
  uVar17 = uVar17 & 0xffff0000;
  uVar18 = uVar18 & 0xffff0000;
  uVar9 = uVar9 & 0xffff0000;
  piVar3 = ps->mix[0] + 0xb;
  pcVar4 = "\x04\x05\x06\a\b\t\v\x0e\x12\x17#@";
  *(int *)(param_2 + 0xc) =
       ((int)((ulonglong)((longlong)iVar11 * (longlong)(int)uVar16) >> 0x20) +
       (int)((ulonglong)((longlong)iVar19 * (longlong)(int)uVar17) >> 0x20)) * 2;
  *(int *)(param_4 + 0xc) =
       ((int)((ulonglong)((longlong)(int)uVar9 * (longlong)iVar11) >> 0x20) +
       (int)((ulonglong)((longlong)(int)uVar18 * (longlong)iVar19) >> 0x20)) * 2;
  iVar19 = *(int *)(param_3 + 0xc) << 1;
  iVar11 = *(int *)(param_5 + 0xc) << 1;
  *(int *)(param_3 + 0xc) =
       ((int)((ulonglong)((longlong)iVar11 * (longlong)(int)uVar16) >> 0x20) +
       (int)((ulonglong)((longlong)iVar19 * (longlong)(int)uVar17) >> 0x20)) * 2;
  *(int *)(param_5 + 0xc) =
       ((int)((ulonglong)((longlong)iVar11 * (longlong)(int)uVar9) >> 0x20) +
       (int)((ulonglong)((longlong)iVar19 * (longlong)(int)uVar18) >> 0x20)) * 2;
  do {
    iVar19 = piVar3[0x16];
    iVar12 = *piVar3;
    iVar10 = piVar3[0x2c];
    iVar7 = piVar3[0x42];
    piVar3[0x16] = piVar3[0x6e] + iVar19;
    *piVar3 = iVar12 + piVar3[0x58];
    piVar3[0x42] = piVar3[0x9a] + iVar7;
    piVar3[0x2c] = iVar10 + piVar3[0x84];
    iVar13 = (int)*pcVar4;
    iVar11 = iVar2;
    if (pcVar4[1] < iVar2) {
      iVar11 = (int)pcVar4[1];
    }
    if (iVar13 < iVar11) {
      iVar14 = iVar13 * 4;
      uVar16 = iVar10 + piVar3[0x84] & 0xffff0000;
      uVar17 = iVar12 + piVar3[0x58] & 0xffff0000;
      uVar9 = piVar3[0x9a] + iVar7 & 0xffff0000;
      uVar18 = piVar3[0x6e] + iVar19 & 0xffff0000;
      piVar6 = (int *)(param_2 + iVar14);
      piVar15 = (int *)(param_4 + iVar14);
      do {
        iVar19 = *piVar6;
        iVar7 = *piVar15;
        piVar5 = piVar6 + 1;
        *piVar6 = ((int)((ulonglong)((longlong)(iVar7 << 1) * (longlong)(int)uVar16) >> 0x20) +
                  (int)((ulonglong)((longlong)(iVar19 << 1) * (longlong)(int)uVar17) >> 0x20)) * 2;
        *piVar15 = ((int)((ulonglong)((longlong)(iVar7 << 1) * (longlong)(int)uVar9) >> 0x20) +
                   (int)((ulonglong)((longlong)(iVar19 << 1) * (longlong)(int)uVar18) >> 0x20)) * 2;
        piVar6 = piVar5;
        piVar15 = piVar15 + 1;
      } while (piVar5 != (int *)(param_2 + iVar14) + (iVar11 - iVar13));
      piVar6 = (int *)(param_3 + iVar14);
      piVar15 = (int *)(iVar14 + param_5);
      do {
        iVar19 = *piVar6;
        iVar7 = *piVar15;
        piVar5 = piVar6 + 1;
        *piVar6 = ((int)((ulonglong)((longlong)(iVar7 << 1) * (longlong)(int)uVar16) >> 0x20) +
                  (int)((ulonglong)((longlong)(iVar19 << 1) * (longlong)(int)uVar17) >> 0x20)) * 2;
        *piVar15 = ((int)((ulonglong)((longlong)(iVar7 << 1) * (longlong)(int)uVar9) >> 0x20) +
                   (int)((ulonglong)((longlong)(iVar19 << 1) * (longlong)(int)uVar18) >> 0x20)) * 2;
        piVar6 = piVar5;
        piVar15 = piVar15 + 1;
      } while (piVar5 != (int *)(param_3 + iVar14) + (iVar11 - iVar13));
    }
    pcVar4 = pcVar4 + 1;
    piVar3 = piVar3 + 1;
  } while (pcVar4 != "@");
  return;
}
