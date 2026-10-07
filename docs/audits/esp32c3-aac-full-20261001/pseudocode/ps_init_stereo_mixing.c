/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: ps_init_stereo_mixing @ ram:4300d72a
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4 ps_init_stereo_mixing(int param_1,int param_2,int param_3)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  char *pcVar9;
  int iVar10;
  int iVar11;
  undefined1 *puVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  int iVar16;

  gp = &__global_pointer_;
  if (*(int *)(param_1 + 0x2c) == 0) {
    puVar12 = scaleFactors;
    iVar13 = 7;
  }
  else {
    puVar12 = scaleFactorsFine;
    iVar13 = 0xf;
  }
  if (param_2 == 0) {
    iVar4 = *(int *)(param_1 + 0x14);
    *(int *)(param_1 + 0x14) = param_3;
    *(int *)(param_1 + 0x18) = iVar4;
    if ((iVar4 != 0) && (iVar4 != param_3)) {
      return 0xffffffff;
    }
  }
  iVar4 = param_2 * 4 + param_1;
  iVar4 = *(int *)(iVar4 + 0x154) - *(int *)(iVar4 + 0x150);
  if (iVar4 == *(int *)(param_1 + 0x10)) {
    iVar4 = *(int *)(param_1 + 8);
  }
  else {
    iVar4 = 0x40000000 / iVar4;
  }
  if (iVar4 == 0x20) {
    pcVar9 = "\x01";
    piVar2 = (int *)(param_1 + 0x200);
    do {
      iVar4 = ((int)*pcVar9 + param_2 * 0x22) * 4 + param_1;
      iVar5 = *(int *)(iVar4 + 0x770);
      iVar8 = *(int *)(puVar12 + (iVar13 + iVar5) * 4);
      iVar4 = *(int *)(iVar4 + 0xaa0) * 4;
      iVar10 = *(int *)(puVar12 + (iVar13 - iVar5) * 4);
      piVar1 = piVar2 + 1;
      iVar11 = *(int *)(cos_alphas + iVar4);
      iVar14 = *(int *)(sin_alphas + iVar4);
      pcVar9 = pcVar9 + 1;
      iVar4 = ((uint)((iVar8 - iVar10) * *(int *)(scaled_alphas + iVar4)) >> 0x1e) +
              (int)((ulonglong)
                    ((longlong)(iVar8 - iVar10) * (longlong)*(int *)(scaled_alphas + iVar4)) >> 0x20
                   ) * 4;
      iVar5 = pv_cosine(iVar4);
      iVar3 = pv_sine(iVar4);
      iVar15 = *piVar2;
      piVar2[0x58] = iVar15;
      piVar2[0x84] = piVar2[0x2c];
      iVar4 = piVar2[0x16];
      piVar2[0x9a] = piVar2[0x42];
      piVar2[0x6e] = iVar4;
      iVar6 = ((uint)(iVar3 * iVar14) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar3 * (longlong)iVar14) >> 0x20) * 4;
      iVar7 = ((uint)(iVar5 * iVar11) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar5 * (longlong)iVar11) >> 0x20) * 4;
      iVar16 = iVar7 - iVar6;
      iVar6 = iVar6 + iVar7;
      iVar3 = ((uint)(iVar3 * iVar11) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar3 * (longlong)iVar11) >> 0x20) * 4;
      iVar5 = ((uint)(iVar14 * iVar5) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar14 * (longlong)iVar5) >> 0x20) * 4;
      iVar7 = iVar3 + iVar5;
      iVar3 = iVar3 - iVar5;
      iVar5 = ((uint)(iVar16 * iVar10) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar16 * (longlong)iVar10) >> 0x20) * 4;
      *piVar2 = iVar5;
      piVar2[0xb0] = iVar5 - iVar15 >> 5;
      iVar5 = ((uint)(iVar7 * iVar10) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar7 * (longlong)iVar10) >> 0x20) * 4;
      piVar2[0xdc] = iVar5 - piVar2[0x2c] >> 5;
      piVar2[0x2c] = iVar5;
      iVar5 = ((uint)(iVar6 * iVar8) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar6 * (longlong)iVar8) >> 0x20) * 4;
      piVar2[0x16] = iVar5;
      piVar2[0xc6] = iVar5 - iVar4 >> 5;
      iVar4 = ((uint)(iVar3 * iVar8) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar3 * (longlong)iVar8) >> 0x20) * 4;
      piVar2[0xf2] = iVar4 - piVar2[0x42] >> 5;
      piVar2[0x42] = iVar4;
      piVar2 = piVar1;
    } while ((int *)(param_1 + 600) != piVar1);
  }
  else {
    pcVar9 = "\x01";
    piVar2 = (int *)(param_1 + 0x200);
    do {
      piVar1 = piVar2 + 1;
      iVar5 = ((int)*pcVar9 + param_2 * 0x22) * 4 + param_1;
      iVar3 = *(int *)(iVar5 + 0x770);
      iVar10 = *(int *)(puVar12 + (iVar13 + iVar3) * 4);
      iVar5 = *(int *)(iVar5 + 0xaa0) * 4;
      iVar7 = *(int *)(puVar12 + (iVar13 - iVar3) * 4);
      iVar8 = *(int *)(cos_alphas + iVar5);
      iVar11 = *(int *)(sin_alphas + iVar5);
      pcVar9 = pcVar9 + 1;
      iVar3 = ((uint)((iVar10 - iVar7) * *(int *)(scaled_alphas + iVar5)) >> 0x1e) +
              (int)((ulonglong)
                    ((longlong)(iVar10 - iVar7) * (longlong)*(int *)(scaled_alphas + iVar5)) >> 0x20
                   ) * 4;
      iVar5 = pv_cosine(iVar3);
      iVar3 = pv_sine(iVar3);
      piVar2[0x84] = piVar2[0x2c];
      piVar2[0x58] = *piVar2;
      piVar2[0x6e] = piVar2[0x16];
      piVar2[0x9a] = piVar2[0x42];
      iVar6 = ((uint)(iVar3 * iVar11) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar3 * (longlong)iVar11) >> 0x20) * 4;
      iVar16 = ((uint)(iVar5 * iVar8) >> 0x1e) +
               (int)((ulonglong)((longlong)iVar5 * (longlong)iVar8) >> 0x20) * 4;
      iVar14 = iVar16 - iVar6;
      iVar6 = iVar6 + iVar16;
      iVar8 = ((uint)(iVar3 * iVar8) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar3 * (longlong)iVar8) >> 0x20) * 4;
      iVar5 = ((uint)(iVar11 * iVar5) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar11 * (longlong)iVar5) >> 0x20) * 4;
      iVar11 = iVar5 + iVar8;
      iVar8 = iVar8 - iVar5;
      iVar5 = ((uint)(iVar14 * iVar7) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar14 * (longlong)iVar7) >> 0x20) * 4;
      iVar3 = iVar5 - *piVar2;
      *piVar2 = iVar5;
      iVar5 = ((uint)(iVar6 * iVar10) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar6 * (longlong)iVar10) >> 0x20) * 4;
      iVar6 = iVar5 - piVar2[0x16];
      piVar2[0x16] = iVar5;
      iVar5 = ((uint)(iVar11 * iVar7) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar11 * (longlong)iVar7) >> 0x20) * 4;
      iVar7 = iVar5 - piVar2[0x2c];
      piVar2[0x2c] = iVar5;
      iVar5 = ((uint)(iVar8 * iVar10) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar8 * (longlong)iVar10) >> 0x20) * 4;
      iVar8 = iVar5 - piVar2[0x42];
      piVar2[0x42] = iVar5;
      piVar2[0xb0] = ((uint)(iVar3 * iVar4) >> 0x1e) +
                     (int)((ulonglong)((longlong)iVar3 * (longlong)iVar4) >> 0x20) * 4;
      piVar2[0xc6] = ((uint)(iVar6 * iVar4) >> 0x1e) +
                     (int)((ulonglong)((longlong)iVar6 * (longlong)iVar4) >> 0x20) * 4;
      piVar2[0xdc] = ((uint)(iVar7 * iVar4) >> 0x1e) +
                     (int)((ulonglong)((longlong)iVar7 * (longlong)iVar4) >> 0x20) * 4;
      piVar2[0xf2] = ((uint)(iVar8 * iVar4) >> 0x1e) +
                     (int)((ulonglong)((longlong)iVar8 * (longlong)iVar4) >> 0x20) * 4;
      piVar2 = piVar1;
    } while ((int *)(param_1 + 600) != piVar1);
  }
  return 0;
}
