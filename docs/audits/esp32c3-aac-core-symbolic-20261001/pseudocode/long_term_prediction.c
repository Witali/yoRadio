/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: long_term_prediction @ ram:4300a880
 * Types and parameter counts are inferred; verify against disassembly. */

int long_term_prediction
              (int param_1,int param_2,int *param_3,int param_4,int param_5,int *param_6,
              uint *param_7,int param_8)

{
  short sVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  uint *puVar5;
  int iVar6;
  short *psVar7;
  int iVar8;
  short *psVar9;
  uint uVar10;
  int iVar11;
  int iVar12;

  gp = &__global_pointer_;
  uVar2 = 0;
  if (param_1 != 2) {
    iVar3 = *param_3;
    iVar12 = param_8 * 2;
    iVar11 = *(int *)(codebook + param_2 * 4);
    iVar6 = iVar12 - iVar3;
    iVar8 = 0;
    iVar4 = iVar12;
    if (iVar3 < param_8) {
      iVar4 = iVar3 + param_8;
      iVar8 = (iVar12 - iVar4) * 4;
    }
    iVar3 = param_8 - iVar6;
    uVar2 = 0;
    if (0 < iVar3) {
      psVar7 = (short *)((iVar6 + param_5) * 2 + param_4);
      psVar9 = psVar7 + iVar3;
      puVar5 = param_7;
      do {
        sVar1 = *psVar7;
        psVar7 = psVar7 + 1;
        uVar10 = sVar1 * iVar11;
        *puVar5 = uVar10;
        uVar2 = uVar2 | (int)uVar10 >> 0x1f ^ uVar10;
        puVar5 = puVar5 + 1;
      } while (psVar7 != psVar9);
      param_7 = param_7 + iVar3;
      iVar4 = iVar4 - iVar3;
      iVar6 = param_8;
    }
    iVar3 = iVar12 - iVar6;
    if (iVar4 < iVar12 - iVar6) {
      iVar3 = iVar4;
    }
    if (0 < iVar3) {
      psVar9 = (short *)(param_4 + (iVar6 - param_5) * 2);
      psVar7 = psVar9 + iVar3;
      puVar5 = param_7;
      do {
        sVar1 = *psVar9;
        psVar9 = psVar9 + 1;
        uVar10 = sVar1 * iVar11;
        *puVar5 = uVar10;
        uVar2 = uVar2 | uVar10 ^ (int)uVar10 >> 0x1f;
        puVar5 = puVar5 + 1;
      } while (psVar9 != psVar7);
      param_7 = param_7 + iVar3;
    }
    iVar4 = iVar4 - iVar3;
    iVar6 = iVar4;
    puVar5 = param_7;
    if (0 < iVar4) {
      do {
        iVar6 = iVar6 + -1;
        uVar10 = (*param_6 >> 10) * iVar11;
        param_6 = param_6 + 1;
        *puVar5 = uVar10;
        uVar2 = uVar2 | uVar10 ^ (int)uVar10 >> 0x1f;
        puVar5 = puVar5 + 1;
      } while (iVar6 != 0);
      param_7 = param_7 + iVar4;
    }
    memset(param_7,0,iVar8);
  }
  iVar4 = pv_normalize(uVar2);
  iVar6 = 0;
  if (iVar4 < 0x11) {
    iVar6 = 0x10 - iVar4;
  }
  return iVar6;
}
