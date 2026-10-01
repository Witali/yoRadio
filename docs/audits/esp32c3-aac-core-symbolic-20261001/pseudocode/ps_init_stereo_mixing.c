/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: ps_init_stereo_mixing @ ram:4300d72a
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4 ps_init_stereo_mixing(aac_ps_abi_t *ps,int param_2,int param_3)

{
  int32_t *piVar1;
  int32_t (*paiVar2) [22];
  int iVar3;
  int iVar4;
  int iVar5;
  uint32_t uVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  char *pcVar10;
  int iVar11;
  int iVar12;
  undefined1 *puVar13;
  int iVar14;
  int iVar15;
  int iVar16;
  int iVar17;

  gp = &__global_pointer_;
  if ((ps->parameters).fine_iid == 0) {
    puVar13 = scaleFactors;
    iVar14 = 7;
  }
  else {
    puVar13 = scaleFactorsFine;
    iVar14 = 0xf;
  }
  if (param_2 == 0) {
    iVar5 = ps->upper_subband;
    ps->upper_subband = param_3;
    (ps->parameters).previous_upper_subband = iVar5;
    if ((iVar5 != 0) && (iVar5 != param_3)) {
      return 0xffffffff;
    }
  }
  uVar6 = (ps->parameters).envelope_borders[param_2 + 1] -
          (ps->parameters).envelope_borders[param_2];
  if (uVar6 == ps->samples) {
    iVar5 = ps->inverse_samples;
  }
  else {
    iVar5 = 0x40000000 / (int)uVar6;
  }
  if (iVar5 == 0x20) {
    pcVar10 = "\x01";
    paiVar2 = ps->previous_mix;
    do {
      iVar3 = ps->iid_index[param_2][*pcVar10];
      iVar9 = *(int *)(puVar13 + (iVar14 + iVar3) * 4);
      iVar5 = ps->icc_index[param_2][*pcVar10] * 4;
      iVar11 = *(int *)(puVar13 + (iVar14 - iVar3) * 4);
      piVar1 = *paiVar2;
      iVar12 = *(int *)(cos_alphas + iVar5);
      iVar15 = *(int *)(sin_alphas + iVar5);
      pcVar10 = pcVar10 + 1;
      iVar5 = ((uint)((iVar9 - iVar11) * *(int *)(scaled_alphas + iVar5)) >> 0x1e) +
              (int)((ulonglong)
                    ((longlong)(iVar9 - iVar11) * (longlong)*(int *)(scaled_alphas + iVar5)) >> 0x20
                   ) * 4;
      iVar3 = pv_cosine(iVar5);
      iVar4 = pv_sine(iVar5);
      iVar16 = (*paiVar2)[0];
      paiVar2[4][0] = iVar16;
      paiVar2[6][0] = paiVar2[2][0];
      iVar5 = paiVar2[1][0];
      paiVar2[7][0] = paiVar2[3][0];
      paiVar2[5][0] = iVar5;
      iVar7 = ((uint)(iVar4 * iVar15) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar4 * (longlong)iVar15) >> 0x20) * 4;
      iVar8 = ((uint)(iVar3 * iVar12) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar3 * (longlong)iVar12) >> 0x20) * 4;
      iVar17 = iVar8 - iVar7;
      iVar7 = iVar7 + iVar8;
      iVar4 = ((uint)(iVar4 * iVar12) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar4 * (longlong)iVar12) >> 0x20) * 4;
      iVar3 = ((uint)(iVar15 * iVar3) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar15 * (longlong)iVar3) >> 0x20) * 4;
      iVar8 = iVar4 + iVar3;
      iVar4 = iVar4 - iVar3;
      iVar3 = ((uint)(iVar17 * iVar11) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar17 * (longlong)iVar11) >> 0x20) * 4;
      (*paiVar2)[0] = iVar3;
      paiVar2[8][0] = iVar3 - iVar16 >> 5;
      iVar3 = ((uint)(iVar8 * iVar11) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar8 * (longlong)iVar11) >> 0x20) * 4;
      paiVar2[10][0] = iVar3 - paiVar2[2][0] >> 5;
      paiVar2[2][0] = iVar3;
      iVar3 = ((uint)(iVar7 * iVar9) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar7 * (longlong)iVar9) >> 0x20) * 4;
      paiVar2[1][0] = iVar3;
      paiVar2[9][0] = iVar3 - iVar5 >> 5;
      iVar5 = ((uint)(iVar4 * iVar9) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar4 * (longlong)iVar9) >> 0x20) * 4;
      paiVar2[0xb][0] = iVar5 - paiVar2[3][0] >> 5;
      paiVar2[3][0] = iVar5;
      paiVar2 = (int32_t (*) [22])(piVar1 + 1);
    } while (ps->previous_mix + 1 != (int32_t (*) [22])(piVar1 + 1));
  }
  else {
    pcVar10 = "\x01";
    paiVar2 = ps->previous_mix;
    do {
      piVar1 = *paiVar2;
      iVar4 = ps->iid_index[param_2][*pcVar10];
      iVar11 = *(int *)(puVar13 + (iVar14 + iVar4) * 4);
      iVar3 = ps->icc_index[param_2][*pcVar10] * 4;
      iVar8 = *(int *)(puVar13 + (iVar14 - iVar4) * 4);
      iVar9 = *(int *)(cos_alphas + iVar3);
      iVar12 = *(int *)(sin_alphas + iVar3);
      pcVar10 = pcVar10 + 1;
      iVar4 = ((uint)((iVar11 - iVar8) * *(int *)(scaled_alphas + iVar3)) >> 0x1e) +
              (int)((ulonglong)
                    ((longlong)(iVar11 - iVar8) * (longlong)*(int *)(scaled_alphas + iVar3)) >> 0x20
                   ) * 4;
      iVar3 = pv_cosine(iVar4);
      iVar4 = pv_sine(iVar4);
      paiVar2[6][0] = paiVar2[2][0];
      paiVar2[4][0] = (*paiVar2)[0];
      paiVar2[5][0] = paiVar2[1][0];
      paiVar2[7][0] = paiVar2[3][0];
      iVar7 = ((uint)(iVar4 * iVar12) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar4 * (longlong)iVar12) >> 0x20) * 4;
      iVar17 = ((uint)(iVar3 * iVar9) >> 0x1e) +
               (int)((ulonglong)((longlong)iVar3 * (longlong)iVar9) >> 0x20) * 4;
      iVar15 = iVar17 - iVar7;
      iVar7 = iVar7 + iVar17;
      iVar9 = ((uint)(iVar4 * iVar9) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar4 * (longlong)iVar9) >> 0x20) * 4;
      iVar3 = ((uint)(iVar12 * iVar3) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar12 * (longlong)iVar3) >> 0x20) * 4;
      iVar12 = iVar3 + iVar9;
      iVar9 = iVar9 - iVar3;
      iVar3 = ((uint)(iVar15 * iVar8) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar15 * (longlong)iVar8) >> 0x20) * 4;
      iVar4 = iVar3 - (*paiVar2)[0];
      (*paiVar2)[0] = iVar3;
      iVar3 = ((uint)(iVar7 * iVar11) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar7 * (longlong)iVar11) >> 0x20) * 4;
      iVar7 = iVar3 - paiVar2[1][0];
      paiVar2[1][0] = iVar3;
      iVar3 = ((uint)(iVar12 * iVar8) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar12 * (longlong)iVar8) >> 0x20) * 4;
      iVar8 = iVar3 - paiVar2[2][0];
      paiVar2[2][0] = iVar3;
      iVar3 = ((uint)(iVar9 * iVar11) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar9 * (longlong)iVar11) >> 0x20) * 4;
      iVar9 = iVar3 - paiVar2[3][0];
      paiVar2[3][0] = iVar3;
      paiVar2[8][0] =
           ((uint)(iVar4 * iVar5) >> 0x1e) +
           (int)((ulonglong)((longlong)iVar4 * (longlong)iVar5) >> 0x20) * 4;
      paiVar2[9][0] =
           ((uint)(iVar7 * iVar5) >> 0x1e) +
           (int)((ulonglong)((longlong)iVar7 * (longlong)iVar5) >> 0x20) * 4;
      paiVar2[10][0] =
           ((uint)(iVar8 * iVar5) >> 0x1e) +
           (int)((ulonglong)((longlong)iVar8 * (longlong)iVar5) >> 0x20) * 4;
      paiVar2[0xb][0] =
           ((uint)(iVar9 * iVar5) >> 0x1e) +
           (int)((ulonglong)((longlong)iVar9 * (longlong)iVar5) >> 0x20) * 4;
      paiVar2 = (int32_t (*) [22])(piVar1 + 1);
    } while (ps->previous_mix + 1 != (int32_t (*) [22])(piVar1 + 1));
  }
  return 0;
}
