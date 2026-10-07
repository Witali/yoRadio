/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: ps_bstr_decoding @ ram:42046e6e
 * Types and parameter counts are inferred; verify against disassembly. */

void ps_bstr_decoding(int param_1)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 uVar3;
  void *pvVar4;
  uint uVar5;
  undefined4 *puVar6;
  int iVar7;
  uint *puVar8;
  undefined4 *puVar9;
  undefined4 *puVar10;
  undefined4 *puVar11;
  uint uVar12;
  uint uVar13;
  undefined4 *puVar14;
  int iVar15;
  undefined4 *puStack_48;

  gp = &__global_pointer_;
  if (*(int *)(param_1 + 0x1c) == 0) {
LAB_ram_42046e94:
    puStack_48 = (undefined4 *)(param_1 + 0xb8);
    puVar14 = (undefined4 *)(param_1 + 0xaa0);
    *(undefined4 *)(param_1 + 0x14c) = 1;
    if (*(int *)(param_1 + 0x20) == 0) {
      memset(param_1 + 0x770,0,0x88);
    }
    else {
      puVar11 = (undefined4 *)(param_1 + 0x770);
      puVar10 = (undefined4 *)(param_1 + 0x30);
      do {
        puVar9 = puVar10;
        puVar6 = puVar11;
        uVar1 = *puVar9;
        uVar3 = puVar9[1];
        puVar6[2] = puVar9[2];
        *puVar6 = uVar1;
        puVar6[1] = uVar3;
        puVar10 = puVar9 + 4;
        puVar6[3] = puVar9[3];
        puVar11 = puVar6 + 4;
      } while (puVar10 != (undefined4 *)(param_1 + 0xb0));
      puVar6[4] = *puVar10;
      puVar6[5] = puVar9[5];
    }
    if (*(int *)(param_1 + 0x24) == 0) {
      memset(puVar14,0,0x88);
    }
    else {
      puVar11 = puVar14;
      puVar10 = puStack_48;
      do {
        puVar9 = puVar10;
        puVar6 = puVar11;
        uVar1 = *puVar9;
        uVar3 = puVar9[1];
        puVar6[2] = puVar9[2];
        *puVar6 = uVar1;
        puVar6[1] = uVar3;
        puVar10 = puVar9 + 4;
        puVar6[3] = puVar9[3];
        puVar11 = puVar6 + 4;
      } while (puVar10 != (undefined4 *)(param_1 + 0x138));
      puVar6[4] = *puVar10;
      puVar6[5] = puVar9[5];
    }
    puVar11 = (undefined4 *)(param_1 + 0x770);
    puVar10 = (undefined4 *)(param_1 + 0x30);
    do {
      puVar9 = puVar10;
      puVar6 = puVar11;
      uVar1 = *puVar6;
      uVar3 = puVar6[1];
      puVar9[2] = puVar6[2];
      *puVar9 = uVar1;
      puVar9[1] = uVar3;
      puVar11 = puVar6 + 4;
      puVar9[3] = puVar6[3];
      puVar10 = puVar9 + 4;
    } while (puVar11 != (undefined4 *)(param_1 + 0x7f0));
    puVar9[4] = *puVar11;
    puVar9[5] = puVar6[5];
    memmove(puStack_48,puVar14,0x88);
    *(undefined4 *)(param_1 + 0x1c) = 0;
    if (*(int *)(param_1 + 0x148) == 0) {
      *(undefined4 *)(param_1 + 0x150) = 0;
      *(undefined4 *)(param_1 + 0x154) = *(undefined4 *)(param_1 + 0x10);
      goto LAB_ram_42047024;
    }
    uVar12 = 1;
  }
  else {
    iVar7 = (uint)(*(int *)(param_1 + 0x2c) != 0) * 8 + 7;
    if (*(int *)(param_1 + 0x14c) == 0) goto LAB_ram_42046e94;
    puVar14 = (undefined4 *)(param_1 + 0x168);
    uVar13 = 0;
    pvVar4 = (void *)(param_1 + 0x30);
    iVar2 = param_1 + 0xb8;
    iVar15 = param_1 + 0xaa0;
    while( true ) {
      puStack_48 = (undefined4 *)(param_1 + 0xb8);
      differential_Decoding
                (*(undefined4 *)(param_1 + 0x20),iVar15 + -0x330,pvVar4,*puVar14,
                 *(undefined4 *)(aNoIidBins + *(int *)(param_1 + 0x140) * 4),
                 (*(int *)(param_1 + 0x140) == 0) + '\x01',-iVar7,iVar7);
      differential_Decoding
                (*(undefined4 *)(param_1 + 0x24),iVar15,iVar2,puVar14[5],
                 *(undefined4 *)(aNoIccBins + *(int *)(param_1 + 0x144) * 4),
                 (*(int *)(param_1 + 0x144) == 0) + '\x01',0,7);
      uVar12 = *(uint *)(param_1 + 0x14c);
      uVar13 = uVar13 + 1;
      if (uVar12 <= uVar13) break;
      pvVar4 = (void *)(iVar15 + -0x330);
      puVar14 = puVar14 + 1;
      iVar2 = iVar15;
      iVar15 = iVar15 + 0x88;
    }
    if (uVar12 == 0) goto LAB_ram_42046e94;
    iVar7 = (uVar12 - 1) * 0x88;
    memmove((void *)(param_1 + 0x30),(void *)(iVar7 + 0x770 + param_1),0x88);
    memmove(puStack_48,(void *)(iVar7 + 0xaa0 + param_1),0x88);
    *(undefined4 *)(param_1 + 0x1c) = 0;
    if (*(int *)(param_1 + 0x148) == 0) {
      *(undefined4 *)(param_1 + 0x150) = 0;
      uVar13 = *(uint *)(param_1 + 0x10);
      if (uVar12 != 1) {
        puVar8 = (uint *)(param_1 + 0x154);
        uVar5 = uVar13;
        do {
          *puVar8 = uVar5 >> (uVar12 >> 1 & 0x1f);
          puVar8 = puVar8 + 1;
          uVar5 = uVar5 + uVar13;
        } while (puVar8 != (uint *)(param_1 + 0x150 + uVar12 * 4));
      }
      *(uint *)(uVar12 * 4 + param_1 + 0x150) = uVar13;
      goto LAB_ram_42047024;
    }
  }
  *(undefined4 *)(param_1 + 0x150) = 0;
  iVar7 = uVar12 * 4 + param_1;
  if (*(uint *)(iVar7 + 0x150) < *(uint *)(param_1 + 0x10)) {
    iVar2 = (uVar12 + 1) * 0x88;
    *(uint *)(param_1 + 0x14c) = uVar12 + 1;
    *(uint *)(iVar7 + 0x154) = *(uint *)(param_1 + 0x10);
    memmove((void *)(iVar2 + 0x770 + param_1),(void *)(iVar2 + 0x6e8 + param_1),0x88);
    iVar7 = *(int *)(param_1 + 0x14c) * 0x88;
    memmove((void *)(iVar7 + 0xaa0 + param_1),(void *)(iVar7 + 0xa18 + param_1),0x88);
  }
  uVar13 = *(uint *)(param_1 + 0x14c);
  if (uVar13 < 2) {
    if (uVar13 == 0) {
      return;
    }
  }
  else {
    uVar12 = *(uint *)(param_1 + 0x10);
    puVar8 = (uint *)(param_1 + 0x154);
    uVar13 = (uVar12 - uVar13) + 1;
    do {
      if (uVar13 < *puVar8) {
        *puVar8 = uVar13;
      }
      else if (*puVar8 < puVar8[-1] + 1) {
        *puVar8 = puVar8[-1] + 1;
      }
      uVar13 = uVar13 + 1;
      puVar8 = puVar8 + 1;
    } while (uVar12 != uVar13);
  }
LAB_ram_42047024:
  iVar7 = param_1 + 0xaa0;
  uVar13 = 0;
  do {
    while( true ) {
      if (*(int *)(param_1 + 0x140) == 2) {
        map34IndexTo20(iVar7 + -0x330);
      }
      if (*(int *)(param_1 + 0x144) == 2) break;
      uVar13 = uVar13 + 1;
      iVar7 = iVar7 + 0x88;
      if (*(uint *)(param_1 + 0x14c) <= uVar13) {
        return;
      }
    }
    map34IndexTo20(iVar7);
    uVar13 = uVar13 + 1;
    iVar7 = iVar7 + 0x88;
  } while (uVar13 < *(uint *)(param_1 + 0x14c));
  return;
}
