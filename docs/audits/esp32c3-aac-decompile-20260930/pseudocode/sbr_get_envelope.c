/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: sbr_get_envelope @ ram:42049288
 * Types and parameter counts are inferred; verify against disassembly. */

void sbr_get_envelope(int *param_1,undefined4 param_2)

{
  int *piVar1;
  undefined1 *puVar2;
  int *piVar3;
  int iVar4;
  int *piVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  undefined1 *puVar11;
  undefined1 *puVar12;
  int *piVar13;
  int iVar14;
  undefined4 uStack_68;
  undefined4 uStack_64;
  int local_54 [8];

  gp = &__global_pointer_;
  iVar6 = param_1[0x5e];
  *param_1 = 0;
  iVar9 = param_1[4];
  if ((param_1[3] == 0) && (iVar9 == 1)) {
    uStack_64 = 6;
    param_1[0x2b] = 0;
    uStack_68 = 7;
    iVar10 = 0;
  }
  else {
    iVar10 = param_1[0x34];
    param_1[0x2b] = iVar10;
    if (iVar10 == 1) {
      uStack_64 = 5;
      uStack_68 = 6;
      if (iVar9 < 1) {
        return;
      }
    }
    else {
      if (iVar9 < 1) {
        return;
      }
      uStack_64 = 6;
      uStack_68 = 7;
    }
  }
  piVar13 = local_54;
  piVar5 = param_1 + iVar9;
  iVar8 = 0;
  iVar4 = 0;
  piVar3 = piVar13;
  do {
    piVar1 = piVar5 + 6;
    iVar4 = iVar4 + 1;
    piVar5 = piVar5 + 1;
    iVar7 = param_1[*piVar1 + 0x27];
    *piVar3 = iVar7;
    iVar8 = iVar8 + iVar7;
    piVar3 = piVar3 + 1;
  } while (iVar4 < iVar9);
  *param_1 = iVar8;
  if (iVar6 == 2) {
    if (iVar10 == 0) {
      puVar11 = bookSbrEnvBalance10F;
      puVar12 = bookSbrEnvBalance10T;
      iVar9 = 1;
    }
    else {
      puVar11 = bookSbrEnvBalance11F;
      puVar12 = bookSbrEnvBalance11T;
      iVar9 = 1;
    }
  }
  else if (iVar10 == 0) {
    puVar11 = bookSbrEnvLevel10F;
    puVar12 = bookSbrEnvLevel10T;
    iVar9 = 0;
  }
  else {
    puVar11 = bookSbrEnvLevel11F;
    puVar12 = bookSbrEnvLevel11T;
    iVar9 = 0;
  }
  piVar3 = param_1 + 0x40;
  iVar10 = 0;
  iVar4 = 0;
  do {
    iVar8 = *piVar3;
    if (iVar8 == 0) {
      if (iVar6 == 2) {
        iVar8 = buf_getbits(param_2,uStack_64);
        param_1[iVar10 + 0x1c4] = iVar8 << iVar9;
        iVar8 = *piVar3;
      }
      else {
        iVar8 = buf_getbits(param_2,uStack_68);
        param_1[iVar10 + 0x1c4] = iVar8;
        iVar8 = *piVar3;
      }
    }
    iVar7 = *piVar13;
    iVar14 = 1 - iVar8;
    if (iVar14 < iVar7) {
      piVar5 = param_1 + iVar10 + iVar14 + 0x1c4;
      while( true ) {
        puVar2 = puVar11;
        if (iVar8 != 0) {
          puVar2 = puVar12;
        }
        iVar8 = sbr_decode_huff_cw(puVar2,param_2);
        *piVar5 = iVar8 << iVar9;
        iVar14 = iVar14 + 1;
        if (iVar14 == iVar7) break;
        iVar8 = *piVar3;
        piVar5 = piVar5 + 1;
      }
    }
    iVar4 = iVar4 + 1;
    iVar10 = iVar10 + iVar7;
    piVar3 = piVar3 + 1;
    piVar13 = piVar13 + 1;
  } while (iVar4 < param_1[4]);
  return;
}
