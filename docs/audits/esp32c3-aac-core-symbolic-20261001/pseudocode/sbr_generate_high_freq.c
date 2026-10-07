/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_generate_high_freq @ ram:430126fa
 * Types and parameter counts are inferred; verify against disassembly. */

void sbr_generate_high_freq
               (undefined4 param_1,undefined4 param_2,int param_3,int param_4,undefined4 param_5,
               undefined4 param_6,undefined4 param_7,int param_8,int param_9,int *param_10,
               int param_11,int param_12,int *param_13,int param_14,int param_15,undefined4 param_16
               ,undefined4 param_17,int *param_18,int param_19,int *param_20)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  int *piVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int *piStack_6c;
  int iStack_50;
  int iStack_4c;
  int iStack_48;
  int iStack_44;

  gp = &__global_pointer_;
  piVar4 = param_10 + param_11;
  iStack_4c = param_15 + 0x100;
  iStack_48 = param_15 + 0x200;
  iStack_44 = param_15 + 0x300;
  iVar12 = param_13[1];
  iVar7 = param_13[*param_13 + 1];
  iVar1 = *piVar4;
  iVar11 = *param_10;
  iStack_50 = param_15;
  sbr_inv_filt_levelemphasis(param_5,param_6,param_8,param_16,param_17);
  iVar9 = (iVar7 * 2 + iVar12 * -2) * 0xc0;
  if (param_19 == 1) {
    memset(param_3 + iVar12 * 0x180,0,iVar9);
    high_freq_coeff_LC(param_1,&iStack_50,param_14,param_10,param_15 + 0x400);
  }
  else {
    memset();
    memset(param_4 + iVar12 * 0x180,0,iVar9);
    high_freq_coeff(param_1,param_2,&iStack_50,&iStack_48,param_10);
  }
  if (param_12 == 24000) {
    iVar9 = 0x55;
  }
  else if (param_12 < 0x5dc1) {
    iVar9 = 0x80;
    if ((param_12 != 16000) && (iVar9 = 0x2e, param_12 == 0x5622)) {
      iVar9 = 0x5d;
    }
  }
  else {
    iVar9 = 0x40;
    if ((param_12 != 32000) && (iVar9 = 0x2e, param_12 == 48000)) {
      iVar9 = 0x2b;
    }
  }
  piStack_6c = &iStack_50;
  iVar13 = *param_10;
  if ((iVar13 < iVar9) && (iVar13 = *piVar4, piVar2 = param_10, iVar9 < iVar13)) {
    do {
      iVar13 = piVar2[1];
      piVar2 = piVar2 + 1;
    } while (iVar13 < iVar9);
  }
  if (param_9 < iVar1) {
    iVar3 = (param_9 - iVar11) + 1;
    iVar9 = 0;
    iVar5 = param_9;
    iVar8 = iVar13;
    do {
      param_18[iVar9 + 1] = iVar5;
      iVar6 = iVar8 - iVar5;
      iVar13 = iVar1;
      if (iVar11 - iVar3 <= iVar6) {
        iVar10 = *param_10;
        iVar13 = (iVar5 - iVar3 & 0xfffffffeU) + iVar11;
        if (iVar10 < iVar13) {
          iVar10 = *piVar4;
          for (piVar2 = piVar4; (iVar13 < iVar10 && (iVar10 = piVar2[-1], iVar13 < iVar10));
              piVar2 = piVar2 + -2) {
            iVar10 = piVar2[-2];
          }
        }
        iVar3 = iVar8 - iVar10;
        iVar6 = iVar10 - iVar5;
        iVar13 = iVar8;
        iVar8 = iVar10;
        if (iVar3 < 3) {
          iVar13 = iVar1;
        }
      }
      if ((iVar6 < 3) && (iVar9 != 0)) {
        if (param_19 == 1) {
          memset(param_14 + iVar5 * 4,0,iVar6 << 2);
        }
        break;
      }
      if (0 < iVar6) {
        if (param_19 == 1) {
          high_freq_generation_LC(param_1,param_3,piStack_6c,param_14,param_7);
        }
        else {
          high_freq_generation
                    (param_1,param_2,param_3,param_4,piStack_6c,&iStack_48,param_7,iVar5,
                     (iVar8 - iVar11) + 1U & 0xfffffffe,iVar6,iVar12 * 2,0,iVar7 * 2,param_16,
                     param_9);
        }
        iVar9 = iVar9 + 1;
        iVar5 = iVar8;
      }
      iVar3 = 1;
      iVar8 = iVar13;
    } while (iVar5 < iVar1);
  }
  else {
    iVar9 = 0;
  }
  *param_18 = iVar9;
  memmove(param_17,param_16,param_8 << 2);
  *param_20 = iVar13;
  return;
}
