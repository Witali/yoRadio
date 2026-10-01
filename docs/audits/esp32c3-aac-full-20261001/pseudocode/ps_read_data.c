/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: ps_read_data @ ram:4300dcfe
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
    if (iVar2 == 0) goto LAB_ram_4300dd46;
LAB_ram_4300dede:
    uVar5 = buf_getbits(param_2,2);
    *(uint *)(param_1 + 0x14c) = uVar5 + 1;
    piVar9 = (int *)(param_1 + 0x154);
    uVar6 = 1;
    if (0xfffffffd < uVar5) goto LAB_ram_4300dd62;
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
    if (iVar2 != 0) goto LAB_ram_4300dede;
LAB_ram_4300dd46:
    iVar2 = buf_getbits(param_2);
    *(undefined4 *)(param_1 + 0x14c) = *(undefined4 *)(aFixNoEnvDecode + iVar2 * 4);
LAB_ram_4300dd62:
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
    goto LAB_ram_4300decc;
  }
  if (*(int *)(param_1 + 0x20) == 0) {
LAB_ram_4300de14:
    if ((*(int *)(param_1 + 0x24) != 0) && (*(int *)(param_1 + 0x14c) != 0)) {
      puVar8 = (undefined4 *)(param_1 + 0xaa0);
      piVar9 = (int *)(param_1 + 0x17c);
      uVar6 = 0;
      do {
        iVar3 = buf_get_1bit(param_2);
        iVar2 = 0x104;
        if (iVar3 == 0) {
          iVar2 = 0xe8;
        }
        iVar11 = 0;
        puVar12 = puVar8;
        if (0 < *(int *)(aNoIccBins + *(int *)(param_1 + 0x144) * 4)) {
          do {
            uVar4 = sbr_decode_huff_cw(iVar2 + 0x4301c000,param_2);
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
    goto LAB_ram_4300de14;
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
LAB_ram_4300decc:
  return iVar1 - iVar2;
}
