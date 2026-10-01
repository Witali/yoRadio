/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: analysis_sub_band @ ram:430005f6
 * Types and parameter counts are inferred; verify against disassembly. */

void analysis_sub_band(uint *param_1,uint *param_2,uint *param_3,int param_4,uint *param_5)

{
  uint *puVar1;
  uint *puVar2;
  uint uVar3;
  uint *puVar4;
  uint *puVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  int iVar11;
  uint *puVar12;
  uint *puVar13;

  gp = &__global_pointer_;
  puVar4 = param_5;
  puVar5 = param_1;
  do {
    uVar10 = *puVar5;
    uVar9 = puVar5[1];
    puVar4[2] = puVar5[2];
    *puVar4 = uVar10;
    puVar4[1] = uVar9;
    puVar12 = puVar5 + 3;
    puVar5 = puVar5 + 4;
    puVar4[3] = *puVar12;
    puVar4 = puVar4 + 4;
  } while (puVar5 != param_1 + 0x40);
  mdst_32(param_5,param_5 + 0x40);
  mdst_32(param_5 + 0x20,param_5 + 0x40);
  mdct_32(param_1);
  mdct_32(param_1 + 0x20);
  if (0 < param_4) {
    uVar8 = *param_1;
    uVar10 = uVar8 - param_5[0x20];
    uVar9 = ((int)uVar8 >> 0x1f) - ((int)param_5[0x20] >> 0x1f);
    iVar6 = uVar9 - (uVar8 < uVar10);
    if ((iVar6 < -1) || ((iVar6 == -1 && (-1 < (int)uVar10)))) {
      uVar10 = 0x80000000;
    }
    else if ((0 < iVar6) || ((uVar9 == uVar8 < uVar10 && ((int)uVar10 < 0)))) {
      uVar10 = 0x7fffffff;
    }
    uVar9 = *param_5;
    uVar8 = param_1[0x20] + uVar9;
    iVar6 = (uint)(uVar8 < uVar9) + ((int)uVar9 >> 0x1f) + ((int)param_1[0x20] >> 0x1f);
    param_1 = param_1 + 0x21;
    if ((iVar6 < -1) || ((iVar6 == -1 && (-1 < (int)uVar8)))) {
      uVar8 = 0x80000000;
    }
    else if ((0 < iVar6) || ((iVar6 == 0 && ((int)uVar8 < 0)))) {
      uVar8 = 0x7fffffff;
    }
    iVar6 = 0;
    puVar4 = &exp_1_5_phi;
    puVar5 = param_5 + 0x21;
    puVar12 = param_2;
    puVar13 = param_3;
    do {
      uVar9 = *puVar4 & 0xffff0000;
      iVar11 = *puVar4 << 0x10;
      iVar6 = iVar6 + 2;
      iVar7 = (int)((ulonglong)((longlong)(int)uVar9 * (longlong)(int)uVar10) >> 0x20) +
              (int)((ulonglong)((longlong)(int)uVar8 * (longlong)iVar11) >> 0x20);
      uVar3 = iVar7 * 2;
      iVar11 = (int)((ulonglong)((longlong)(int)uVar8 * (longlong)(int)uVar9) >> 0x20) +
               (int)((ulonglong)((longlong)(int)-uVar10 * (longlong)iVar11) >> 0x20);
      uVar9 = iVar11 * 2;
      if (iVar7 != (int)uVar3 >> 1) {
        uVar3 = iVar7 >> 0x1f ^ 0x7fffffff;
      }
      *puVar12 = uVar3;
      if (iVar11 != (int)uVar9 >> 1) {
        uVar9 = iVar11 >> 0x1f ^ 0x7fffffff;
      }
      *puVar13 = uVar9;
      uVar10 = puVar4[1] & 0xffff0000;
      iVar7 = puVar4[1] << 0x10;
      iVar11 = (int)((ulonglong)((longlong)(int)(param_1[-0x20] + *puVar5) * (longlong)(int)uVar10)
                    >> 0x20) +
               (int)((ulonglong)((longlong)(int)(puVar5[-0x20] - *param_1) * (longlong)iVar7) >>
                    0x20);
      uVar9 = iVar11 * 2;
      iVar7 = (int)((ulonglong)((longlong)(int)uVar10 * (longlong)(int)(puVar5[-0x20] - *param_1))
                   >> 0x20) +
              (int)((ulonglong)((longlong)(int)-(param_1[-0x20] + *puVar5) * (longlong)iVar7) >>
                   0x20);
      uVar10 = iVar7 * 2;
      if (iVar11 != (int)uVar9 >> 1) {
        uVar9 = iVar11 >> 0x1f ^ 0x7fffffff;
      }
      puVar12[1] = uVar9;
      if (iVar7 != (int)uVar10 >> 1) {
        uVar10 = iVar7 >> 0x1f ^ 0x7fffffff;
      }
      puVar13[1] = uVar10;
      puVar1 = param_1 + -0x1f;
      puVar2 = param_1 + 1;
      param_1 = param_1 + 2;
      uVar10 = *puVar1 - puVar5[1];
      uVar8 = puVar5[-0x1f] + *puVar2;
      puVar4 = puVar4 + 2;
      puVar5 = puVar5 + 2;
      puVar12 = puVar12 + 2;
      puVar13 = puVar13 + 2;
    } while (iVar6 < param_4);
    if (param_4 == 0x20) {
      return;
    }
  }
  puVar5 = param_2 + param_4;
  puVar4 = param_3 + param_4;
  param_4 = 0x20 - param_4;
  if ((puVar5 < param_3 + 0x20) && (puVar4 < param_2 + 0x20)) {
    do {
      *puVar5 = 0;
      *puVar4 = 0;
      param_4 = param_4 + -1;
      puVar5 = puVar5 + 1;
      puVar4 = puVar4 + 1;
    } while (param_4 != 0);
    return;
  }
  memset(puVar5,0,param_4 * 4);
  memset(puVar4,0,param_4 * 4);
  return;
}
