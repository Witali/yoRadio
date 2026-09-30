/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: ps_read_data @ ram:4205ccde
 * Types and parameter counts are inferred; verify against disassembly. */

int ps_read_data(int param_1,int param_2,int param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  undefined1 *puVar7;
  undefined4 *puVar8;
  int *piVar9;
  int iVar10;
  int iVar11;
  undefined4 *puVar12;

  gp = &__global_pointer_;
  if (param_1 == 0) {
    return 0;
  }
  iVar1 = GetNrBitsAvailable(param_2);
  iVar2 = buf_get_1bit(param_2);
  if (iVar2 == 0) {
    iVar2 = buf_get_1bit(param_2);
    *(int *)(param_1 + 0x148) = iVar2;
    if (iVar2 == 0) goto LAB_ram_4205cd1a;
LAB_ram_4205ce9a:
    uVar5 = buf_getbits(param_2,2);
    *(uint *)(param_1 + 0x14c) = uVar5 + 1;
    piVar9 = (int *)(param_1 + 0x154);
    uVar6 = 1;
    if (0xfffffffd < uVar5) goto LAB_ram_4205cd32;
    do {
      iVar2 = buf_getbits(param_2,5);
      *piVar9 = iVar2 + 1;
      uVar6 = uVar6 + 1;
      piVar9 = piVar9 + 1;
    } while (uVar6 < *(int *)(param_1 + 0x14c) + 1U);
    uVar6 = *(uint *)(param_1 + 0x140);
  }
  else {
    iVar2 = buf_get_1bit(param_2);
    *(int *)(param_1 + 0x20) = iVar2;
    if (iVar2 != 0) {
      uVar6 = buf_getbits(param_2,3);
      *(uint *)(param_1 + 0x140) = uVar6;
      if (uVar6 < 3) {
        *(undefined4 *)(param_1 + 0x2c) = 0;
      }
      else {
        *(uint *)(param_1 + 0x140) = uVar6 - 3;
        *(undefined4 *)(param_1 + 0x2c) = 1;
      }
    }
    iVar2 = buf_get_1bit(param_2);
    *(int *)(param_1 + 0x24) = iVar2;
    if (iVar2 != 0) {
      uVar6 = buf_getbits(param_2,3);
      if (2 < uVar6) {
        uVar6 = uVar6 - 3;
      }
      *(uint *)(param_1 + 0x144) = uVar6;
    }
    uVar4 = buf_get_1bit(param_2);
    *(undefined4 *)(param_1 + 0x28) = uVar4;
    iVar2 = buf_get_1bit(param_2);
    *(int *)(param_1 + 0x148) = iVar2;
    if (iVar2 != 0) goto LAB_ram_4205ce9a;
LAB_ram_4205cd1a:
    iVar2 = buf_getbits(param_2,2);
    *(undefined4 *)(param_1 + 0x14c) = *(undefined4 *)(aFixNoEnvDecode + iVar2 * 4);
LAB_ram_4205cd32:
    uVar6 = *(uint *)(param_1 + 0x140);
  }
  if ((2 < uVar6) || (2 < *(uint *)(param_1 + 0x144))) {
    *(undefined4 *)(param_1 + 0x1c) = 0;
    iVar3 = GetNrBitsAvailable(param_2);
    iVar2 = param_3 - (iVar1 - iVar3);
    if (param_3 != iVar1 - iVar3) {
      do {
        iVar3 = iVar2;
        if (8 < iVar2) {
          iVar3 = 8;
        }
        iVar2 = iVar2 - iVar3;
        buf_getbits(param_2,iVar3);
      } while (iVar2 != 0);
    }
    iVar2 = GetNrBitsAvailable(param_2);
    goto LAB_ram_4205ce88;
  }
  if (*(int *)(param_1 + 0x20) == 0) {
LAB_ram_4205cddc:
    if ((*(int *)(param_1 + 0x24) != 0) && (*(int *)(param_1 + 0x14c) != 0)) {
      puVar8 = (undefined4 *)(param_1 + 0xaa0);
      piVar9 = (int *)(param_1 + 0x17c);
      uVar6 = 0;
      do {
        iVar3 = buf_get_1bit(param_2);
        iVar2 = 0x6d8;
        if (iVar3 == 0) {
          iVar2 = 0x6bc;
        }
        iVar11 = 0;
        puVar12 = puVar8;
        if (0 < *(int *)(aNoIccBins + *(int *)(param_1 + 0x144) * 4)) {
          do {
            uVar4 = sbr_decode_huff_cw(iVar2 + 0x3c132000,param_2);
            *puVar12 = uVar4;
            iVar11 = iVar11 + 1;
            puVar12 = puVar12 + 1;
          } while (iVar11 < *(int *)(aNoIccBins + *(int *)(param_1 + 0x144) * 4));
        }
        *piVar9 = iVar3;
        uVar6 = uVar6 + 1;
        piVar9 = piVar9 + 1;
        puVar8 = puVar8 + 0x22;
      } while (uVar6 < *(uint *)(param_1 + 0x14c));
    }
  }
  else if (*(int *)(param_1 + 0x14c) != 0) {
    piVar9 = (int *)(param_1 + 0x168);
    uVar6 = 0;
    iVar2 = param_1;
    do {
      iVar3 = buf_get_1bit(param_2);
      if (iVar3 == 0) {
        puVar7 = aBookPsIidFreqDecode_googleaac;
        if (*(int *)(param_1 + 0x2c) != 0) {
          puVar7 = aBookPsIidFineFreqDecode_googleaac;
        }
      }
      else {
        puVar7 = aBookPsIidTimeDecode_googleaac;
        if (*(int *)(param_1 + 0x2c) != 0) {
          puVar7 = aBookPsIidFineTimeDecode_googleaac;
        }
      }
      iVar10 = 0;
      iVar11 = iVar2;
      if (0 < *(int *)(aNoIidBins + *(int *)(param_1 + 0x140) * 4)) {
        do {
          uVar4 = sbr_decode_huff_cw(puVar7,param_2);
          *(undefined4 *)(iVar11 + 0x770) = uVar4;
          iVar10 = iVar10 + 1;
          iVar11 = iVar11 + 4;
        } while (iVar10 < *(int *)(aNoIidBins + *(int *)(param_1 + 0x140) * 4));
      }
      *piVar9 = iVar3;
      uVar6 = uVar6 + 1;
      piVar9 = piVar9 + 1;
      iVar2 = iVar2 + 0x88;
    } while (uVar6 < *(uint *)(param_1 + 0x14c));
    goto LAB_ram_4205cddc;
  }
  if (*(int *)(param_1 + 0x28) != 0) {
    iVar2 = buf_getbits(param_2,4);
    if (iVar2 == 0xf) {
      iVar2 = buf_getbits(param_2,8);
      iVar2 = iVar2 + 0xf;
    }
    *(int *)(param_2 + 0xc) = *(int *)(param_2 + 0xc) + iVar2 * 8;
  }
  *(undefined4 *)(param_1 + 0x1c) = 1;
  iVar2 = GetNrBitsAvailable(param_2);
LAB_ram_4205ce88:
  return iVar1 - iVar2;
}
