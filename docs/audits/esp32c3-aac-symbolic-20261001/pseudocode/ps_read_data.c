/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: ps_read_data @ ram:4300dcfe
 * Types and parameter counts are inferred; verify against disassembly. */

int ps_read_data(aac_ps_abi_t *ps,int param_2,int param_3)

{
  int iVar1;
  int iVar2;
  uint32_t uVar3;
  int32_t iVar4;
  uint uVar5;
  uint uVar6;
  undefined1 *puVar7;
  int32_t (*paiVar8) [34];
  uint32_t *puVar9;
  aac_ps_abi_t *paVar10;
  int iVar11;
  aac_ps_abi_t *paVar12;
  int32_t (*paiVar13) [34];

  gp = &__global_pointer_;
  if (ps == (aac_ps_abi_t *)0x0) {
    return 0;
  }
  iVar1 = GetNrBitsAvailable(param_2);
  iVar2 = buf_get_1bit(param_2);
  if (iVar2 == 0) {
    uVar3 = buf_get_1bit(param_2);
    (ps->parameters).frame_class = uVar3;
    if (uVar3 == 0) goto LAB_ram_4300dd46;
LAB_ram_4300dede:
    uVar5 = buf_getbits(param_2,2);
    (ps->parameters).envelope_count = uVar5 + 1;
    puVar9 = (ps->parameters).envelope_borders;
    uVar6 = 1;
    if (0xfffffffd < uVar5) goto LAB_ram_4300dd62;
    do {
      puVar9 = puVar9 + 1;
      iVar2 = buf_getbits(param_2,5);
      *puVar9 = iVar2 + 1;
      uVar6 = uVar6 + 1;
    } while (uVar6 < (ps->parameters).envelope_count + 1);
    uVar6 = (ps->parameters).iid_resolution;
  }
  else {
    uVar3 = buf_get_1bit(param_2);
    (ps->parameters).enable_iid = uVar3;
    if (uVar3 != 0) {
      uVar6 = buf_getbits(param_2,3);
      (ps->parameters).iid_resolution = uVar6;
      if (uVar6 < 3) {
        (ps->parameters).fine_iid = 0;
      }
      else {
        (ps->parameters).iid_resolution = uVar6 - 3;
        (ps->parameters).fine_iid = 1;
      }
    }
    uVar3 = buf_get_1bit(param_2);
    (ps->parameters).enable_icc = uVar3;
    if (uVar3 != 0) {
      uVar3 = buf_getbits(param_2,3);
      if (2 < uVar3) {
        uVar3 = uVar3 - 3;
      }
      (ps->parameters).icc_resolution = uVar3;
    }
    uVar3 = buf_get_1bit(param_2);
    (ps->parameters).enable_extension = uVar3;
    uVar3 = buf_get_1bit(param_2);
    (ps->parameters).frame_class = uVar3;
    if (uVar3 != 0) goto LAB_ram_4300dede;
LAB_ram_4300dd46:
    iVar2 = buf_getbits(param_2);
    (ps->parameters).envelope_count = *(uint32_t *)(aFixNoEnvDecode + iVar2 * 4);
LAB_ram_4300dd62:
    uVar6 = (ps->parameters).iid_resolution;
  }
  if ((2 < uVar6) || (2 < (ps->parameters).icc_resolution)) {
    (ps->parameters).data_available = 0;
    iVar11 = GetNrBitsAvailable(param_2);
    iVar2 = param_3 - (iVar1 - iVar11);
    if (param_3 != iVar1 - iVar11) {
      do {
        iVar11 = iVar2;
        if (8 < iVar2) {
          iVar11 = 8;
        }
        iVar2 = iVar2 - iVar11;
        buf_getbits(param_2,iVar11);
      } while (iVar2 != 0);
    }
    iVar2 = GetNrBitsAvailable(param_2);
    goto LAB_ram_4300decc;
  }
  if ((ps->parameters).enable_iid == 0) {
LAB_ram_4300de14:
    if (((ps->parameters).enable_icc != 0) && ((ps->parameters).envelope_count != 0)) {
      paiVar8 = ps->icc_index;
      puVar9 = (ps->parameters).icc_time_delta;
      uVar6 = 0;
      do {
        uVar3 = buf_get_1bit(param_2);
        iVar2 = 0x104;
        if (uVar3 == 0) {
          iVar2 = 0xe8;
        }
        iVar11 = 0;
        paiVar13 = paiVar8;
        if (0 < *(int *)(aNoIccBins + (ps->parameters).icc_resolution * 4)) {
          do {
            iVar4 = sbr_decode_huff_cw(iVar2 + 0x4301c000,param_2);
            (*paiVar13)[0] = iVar4;
            iVar11 = iVar11 + 1;
            paiVar13 = (int32_t (*) [34])(*paiVar13 + 1);
          } while (iVar11 < *(int *)(aNoIccBins + (ps->parameters).icc_resolution * 4));
        }
        *puVar9 = uVar3;
        uVar6 = uVar6 + 1;
        puVar9 = puVar9 + 1;
        paiVar8 = paiVar8 + 1;
      } while (uVar6 < (ps->parameters).envelope_count);
    }
  }
  else if ((ps->parameters).envelope_count != 0) {
    puVar9 = (ps->parameters).iid_time_delta;
    uVar6 = 0;
    paVar10 = ps;
    do {
      uVar3 = buf_get_1bit(param_2);
      iVar2 = (ps->parameters).fine_iid;
      if (uVar3 == 0) {
        puVar7 = aBookPsIidFreqDecode_googleaac;
        if (iVar2 != 0) {
          puVar7 = aBookPsIidFineFreqDecode_googleaac;
        }
      }
      else {
        puVar7 = aBookPsIidTimeDecode_googleaac;
        if (iVar2 != 0) {
          puVar7 = aBookPsIidFineTimeDecode_googleaac;
        }
      }
      iVar2 = 0;
      paVar12 = paVar10;
      if (0 < *(int *)(aNoIidBins + (ps->parameters).iid_resolution * 4)) {
        do {
          iVar4 = sbr_decode_huff_cw(puVar7,param_2);
          paVar12->iid_index[0][0] = iVar4;
          iVar2 = iVar2 + 1;
          paVar12 = (aac_ps_abi_t *)&paVar12->right_synthesis;
        } while (iVar2 < *(int *)(aNoIidBins + (ps->parameters).iid_resolution * 4));
      }
      *puVar9 = uVar3;
      uVar6 = uVar6 + 1;
      puVar9 = puVar9 + 1;
      paVar10 = (aac_ps_abi_t *)((paVar10->parameters).previous_iid + 0x16);
    } while (uVar6 < (ps->parameters).envelope_count);
    goto LAB_ram_4300de14;
  }
  if ((ps->parameters).enable_extension != 0) {
    iVar2 = buf_getbits(param_2,4);
    if (iVar2 == 0xf) {
      iVar2 = buf_getbits(param_2,8);
      iVar2 = iVar2 + 0xf;
    }
    *(int *)(param_2 + 0xc) = *(int *)(param_2 + 0xc) + iVar2 * 8;
  }
  (ps->parameters).data_available = 1;
  iVar2 = GetNrBitsAvailable(param_2);
LAB_ram_4300decc:
  return iVar1 - iVar2;
}
