/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: infoinit @ ram:4204566c
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4 infoinit(int param_1,int *param_2,int *param_3)

{
  short sVar1;
  undefined1 *puVar2;
  int iVar3;
  short *psVar4;
  int iVar5;
  int iVar6;
  int *piVar7;
  undefined1 *puVar8;
  int iVar9;
  undefined4 *puVar10;
  int *piVar11;
  int iVar12;
  short *psVar13;
  int *piVar14;
  undefined4 *puVar15;
  int iVar16;
  int *piVar17;
  undefined4 uVar18;

  gp = &__global_pointer_;
  iVar9 = *(int *)(samp_rate_info + param_1 * 0xc);
  if (iVar9 == 32000) {
    puVar8 = (undefined1 *)&sfb_48_128;
    puVar2 = sfb_32_1024;
  }
  else if (iVar9 < 0x7d01) {
    if (iVar9 != 12000) {
      if (iVar9 < 0x2ee1) {
        if (iVar9 == 8000) {
          puVar8 = sfb_8_128;
          puVar2 = sfb_8_1024;
          goto LAB_ram_420456ec;
        }
        if (iVar9 != 0x2b11) {
LAB_ram_42045788:
          gp = &__global_pointer_;
          return 0xffffffff;
        }
      }
      else {
        if ((iVar9 == 0x5622) || (iVar9 == 24000)) {
          puVar8 = sfb_24_128;
          puVar2 = sfb_24_1024;
          goto LAB_ram_420456ec;
        }
        if (iVar9 != 16000) goto LAB_ram_42045788;
      }
    }
    puVar8 = sfb_16_128;
    puVar2 = sfb_16_1024;
  }
  else if (iVar9 == 64000) {
    puVar8 = sfb_64_128;
    puVar2 = sfb_64_1024;
  }
  else if (iVar9 < 0xfa01) {
    if ((iVar9 != 0xac44) && (iVar9 != 48000)) goto LAB_ram_42045788;
    puVar8 = (undefined1 *)&sfb_48_128;
    puVar2 = sfb_48_1024;
  }
  else {
    if ((iVar9 != 0x15888) && (iVar9 != 96000)) {
      gp = &__global_pointer_;
      return 0xffffffff;
    }
    puVar8 = sfb_64_128;
    puVar2 = sfb_96_1024;
  }
LAB_ram_420456ec:
  uVar18 = *(undefined4 *)(samp_rate_info + param_1 * 0xc + 4);
  puVar10 = (undefined4 *)*param_2;
  puVar15 = (undefined4 *)param_2[2];
  iVar9 = *(int *)(samp_rate_info + param_1 * 0xc + 8);
  *puVar10 = 1;
  puVar10[1] = 1;
  puVar10[0xa5] = 1;
  puVar10[0xa6] = 1;
  puVar10[2] = 0x400;
  puVar10[0xc] = uVar18;
  puVar10[0x1c] = puVar2;
  puVar10[0x24] = 0;
  puVar10[0x14] = 5;
  puVar15[2] = 0x400;
  puVar15[1] = 8;
  *puVar15 = 0;
  piVar11 = puVar15 + 0xc;
  do {
    *piVar11 = iVar9;
    piVar11[8] = 3;
    piVar11[0x10] = (int)puVar8;
    piVar11 = piVar11 + 1;
  } while (piVar11 != puVar15 + 0x14);
  puVar15[0x24] = param_3;
  if (0 < iVar9) {
    psVar4 = (short *)((int)puVar8 + iVar9 * 2);
    iVar9 = 0;
    do {
      sVar1 = *(short *)puVar8;
      puVar8 = (undefined1 *)((int)puVar8 + 2);
      *param_3 = sVar1 - iVar9;
      param_3 = param_3 + 1;
      iVar9 = (int)sVar1;
    } while ((short *)puVar8 != psVar4);
  }
  piVar11 = param_2 + 4;
  do {
    iVar9 = *param_2;
    if (iVar9 != 0) {
      iVar12 = *(int *)(iVar9 + 4);
      *(undefined4 *)(iVar9 + 0xc) = 0;
      if (0 < iVar12) {
        piVar14 = (int *)(iVar9 + 0x10);
        iVar3 = *(int *)(iVar9 + 8) / iVar12;
        piVar17 = piVar14 + iVar12;
        iVar5 = 0;
        iVar12 = 0;
        do {
          iVar6 = piVar14[8];
          *piVar14 = iVar3;
          iVar16 = iVar12 + iVar6;
          if (0 < iVar6) {
            psVar13 = (short *)piVar14[0x18];
            psVar4 = psVar13 + iVar6;
            piVar7 = (int *)(iVar12 * 4 + iVar9 + 0x94);
            do {
              sVar1 = *psVar13;
              psVar13 = psVar13 + 1;
              *piVar7 = sVar1 + iVar5;
              piVar7 = piVar7 + 1;
            } while (psVar4 != psVar13);
          }
          piVar14 = piVar14 + 1;
          iVar5 = iVar5 + iVar3;
          iVar12 = iVar16;
        } while (piVar14 != piVar17);
        *(int *)(iVar9 + 0xc) = iVar16;
      }
    }
    param_2 = param_2 + 1;
  } while (param_2 != piVar11);
  return 0;
}
