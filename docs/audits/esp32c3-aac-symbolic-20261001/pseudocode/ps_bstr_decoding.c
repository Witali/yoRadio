/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: ps_bstr_decoding @ ram:4300c504
 * Types and parameter counts are inferred; verify against disassembly. */

/* WARNING: Type propagation algorithm not settling */

void ps_bstr_decoding(aac_ps_abi_t *ps)

{
  int32_t iVar1;
  int32_t iVar2;
  uint32_t uVar3;
  int32_t (*paiVar4) [34];
  uint32_t uVar5;
  uint uVar6;
  uint32_t *puVar7;
  int32_t *piVar8;
  int32_t *piVar9;
  uint uVar10;
  int32_t (*paiVar11) [34];
  int iVar12;
  int32_t *piVar13;
  int32_t (*paiVar14) [34];
  int32_t *piStack_48;

  gp = &__global_pointer_;
  if ((ps->parameters).data_available == 0) {
LAB_ram_4300c52a:
    piStack_48 = (ps->parameters).previous_icc;
    paiVar4 = ps->icc_index;
    piVar13 = (ps->parameters).previous_iid;
    (ps->parameters).envelope_count = 1;
    if ((ps->parameters).enable_iid == 0) {
      memset(ps->iid_index,0,0x88);
    }
    else {
      paiVar11 = ps->iid_index;
      piVar9 = piVar13;
      do {
        piVar8 = piVar9;
        paiVar14 = paiVar11;
        iVar1 = *piVar8;
        iVar2 = piVar8[1];
        (*paiVar14)[2] = piVar8[2];
        (*paiVar14)[0] = iVar1;
        (*paiVar14)[1] = iVar2;
        piVar9 = piVar8 + 4;
        (*paiVar14)[3] = piVar8[3];
        paiVar11 = (int32_t (*) [34])(*paiVar14 + 4);
      } while (piVar9 != (ps->parameters).previous_iid + 0x20);
      (*(int32_t (*) [34])(*paiVar14 + 4))[0] = *piVar9;
      (*paiVar14)[5] = piVar8[5];
    }
    if ((ps->parameters).enable_icc == 0) {
      memset(paiVar4,0,0x88);
    }
    else {
      paiVar11 = paiVar4;
      piVar9 = piStack_48;
      do {
        piVar8 = piVar9;
        paiVar14 = paiVar11;
        iVar1 = *piVar8;
        iVar2 = piVar8[1];
        (*paiVar14)[2] = piVar8[2];
        (*paiVar14)[0] = iVar1;
        (*paiVar14)[1] = iVar2;
        piVar9 = piVar8 + 4;
        (*paiVar14)[3] = piVar8[3];
        paiVar11 = (int32_t (*) [34])(*paiVar14 + 4);
      } while (piVar9 != (ps->parameters).previous_icc + 0x20);
      (*(int32_t (*) [34])(*paiVar14 + 4))[0] = *piVar9;
      (*paiVar14)[5] = piVar8[5];
    }
    paiVar11 = ps->iid_index;
    do {
      piVar9 = piVar13;
      paiVar14 = paiVar11;
      iVar1 = (*paiVar14)[0];
      iVar2 = (*paiVar14)[1];
      piVar9[2] = (*paiVar14)[2];
      *piVar9 = iVar1;
      piVar9[1] = iVar2;
      paiVar11 = (int32_t (*) [34])(*paiVar14 + 4);
      piVar9[3] = (*paiVar14)[3];
      piVar13 = piVar9 + 4;
    } while (paiVar11 != (int32_t (*) [34])(ps->iid_index[0] + 0x20));
    piVar9[4] = (*paiVar11)[0];
    piVar9[5] = (*paiVar14)[5];
    memmove(piStack_48,paiVar4,0x88);
    (ps->parameters).data_available = 0;
    if ((ps->parameters).frame_class == 0) {
      uVar3 = ps->samples;
      (ps->parameters).envelope_borders[0] = 0;
      (ps->parameters).envelope_borders[1] = uVar3;
      goto LAB_ram_4300c6c6;
    }
    uVar10 = 1;
  }
  else {
    iVar12 = (uint)((ps->parameters).fine_iid != 0) * 8 + 7;
    piVar13 = (ps->parameters).previous_iid;
    if ((ps->parameters).envelope_count == 0) goto LAB_ram_4300c52a;
    puVar7 = (ps->parameters).iid_time_delta;
    uVar6 = 0;
    paiVar4 = &piVar13;
    paiVar11 = &(ps->parameters).previous_icc;
    paiVar14 = ps->icc_index;
    while( true ) {
      piStack_48 = (ps->parameters).previous_icc;
      uVar3 = (ps->parameters).iid_resolution;
      differential_Decoding
                ((ps->parameters).enable_iid,paiVar14 + -6,paiVar4,*puVar7,
                 *(undefined4 *)(aNoIidBins + uVar3 * 4),(uVar3 == 0) + '\x01',-iVar12,iVar12);
      uVar3 = (ps->parameters).icc_resolution;
      differential_Decoding
                ((ps->parameters).enable_icc,paiVar14,paiVar11,puVar7[5],
                 *(undefined4 *)(aNoIccBins + uVar3 * 4),(uVar3 == 0) + '\x01',0,7);
      uVar10 = (ps->parameters).envelope_count;
      uVar6 = uVar6 + 1;
      if (uVar10 <= uVar6) break;
      paiVar4 = paiVar14 + -6;
      puVar7 = puVar7 + 1;
      paiVar11 = paiVar14;
      paiVar14 = paiVar14 + 1;
    }
    if (uVar10 == 0) goto LAB_ram_4300c52a;
    memmove(piVar13,ps->delay_length + uVar10 * 0x22 + 7,0x88);
    memmove(piStack_48,ps->iid_index + uVar10 + 5,0x88);
    (ps->parameters).data_available = 0;
    if ((ps->parameters).frame_class == 0) {
      (ps->parameters).envelope_borders[0] = 0;
      uVar3 = ps->samples;
      if (uVar10 != 1) {
        puVar7 = (ps->parameters).envelope_borders + 1;
        uVar5 = uVar3;
        do {
          *puVar7 = uVar5 >> (uVar10 >> 1 & 0x1f);
          puVar7 = puVar7 + 1;
          uVar5 = uVar5 + uVar3;
        } while (puVar7 != (ps->parameters).envelope_borders + uVar10);
      }
      (ps->parameters).envelope_borders[uVar10] = uVar3;
      goto LAB_ram_4300c6c6;
    }
  }
  (ps->parameters).envelope_borders[0] = 0;
  uVar6 = ps->samples;
  if ((ps->parameters).envelope_borders[uVar10] < uVar6) {
    (ps->parameters).envelope_count = uVar10 + 1;
    (ps->parameters).envelope_borders[uVar10 + 1] = uVar6;
    memmove(ps->iid_index + uVar10 + 1,ps->iid_index + uVar10,0x88);
    uVar3 = (ps->parameters).envelope_count;
    memmove(ps->icc_index + uVar3,ps->iid_index + uVar3 + 5,0x88);
  }
  uVar6 = (ps->parameters).envelope_count;
  if (uVar6 < 2) {
    if (uVar6 == 0) {
      return;
    }
  }
  else {
    uVar3 = ps->samples;
    puVar7 = (ps->parameters).envelope_borders;
    uVar6 = (uVar3 - uVar6) + 1;
    do {
      puVar7 = puVar7 + 1;
      if (uVar6 < *puVar7) {
        *puVar7 = uVar6;
      }
      else if (*puVar7 < puVar7[-1] + 1) {
        *puVar7 = puVar7[-1] + 1;
      }
      uVar6 = uVar6 + 1;
    } while (uVar3 != uVar6);
  }
LAB_ram_4300c6c6:
  paiVar4 = ps->icc_index;
  uVar6 = 0;
  do {
    while( true ) {
      if ((ps->parameters).iid_resolution == 2) {
        map34IndexTo20(paiVar4 + -6);
      }
      if ((ps->parameters).icc_resolution == 2) break;
      uVar6 = uVar6 + 1;
      paiVar4 = paiVar4 + 1;
      if ((ps->parameters).envelope_count <= uVar6) {
        return;
      }
    }
    map34IndexTo20(paiVar4);
    uVar6 = uVar6 + 1;
    paiVar4 = paiVar4 + 1;
  } while (uVar6 < (ps->parameters).envelope_count);
  return;
}
