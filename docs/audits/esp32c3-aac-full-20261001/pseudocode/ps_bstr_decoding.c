/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: ps_bstr_decoding @ ram:4300c504
 * Types and parameter counts are inferred; verify against disassembly. */

void ps_bstr_decoding(int param_1)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  undefined4 *puVar5;
  int iVar6;
  uint *puVar7;
  undefined4 *puVar8;
  undefined4 *puVar9;
  undefined4 *puVar10;
  uint uVar11;
  uint uVar12;
  undefined4 *puVar13;
  int iVar14;
  int iVar15;
  undefined4 *puStack_48;

  gp = &__global_pointer_;
  if (*(int *)(param_1 + 0x1c) == 0) {
LAB_ram_4300c52a:
    puStack_48 = (undefined4 *)(param_1 + 0xb8);
    puVar13 = (undefined4 *)(param_1 + 0xaa0);
    *(undefined4 *)(param_1 + 0x14c) = 1;
    if (*(int *)(param_1 + 0x20) == 0) {
      memset(param_1 + 0x770,0,0x88);
    }
    else {
      puVar10 = (undefined4 *)(param_1 + 0x770);
      puVar9 = (undefined4 *)(param_1 + 0x30);
      do {
        puVar8 = puVar9;
        puVar5 = puVar10;
        uVar1 = *puVar8;
        uVar3 = puVar8[1];
        puVar5[2] = puVar8[2];
        *puVar5 = uVar1;
        puVar5[1] = uVar3;
        puVar9 = puVar8 + 4;
        puVar5[3] = puVar8[3];
        puVar10 = puVar5 + 4;
      } while (puVar9 != (undefined4 *)(param_1 + 0xb0));
      puVar5[4] = *puVar9;
      puVar5[5] = puVar8[5];
    }
    if (*(int *)(param_1 + 0x24) == 0) {
      memset(puVar13,0,0x88);
    }
    else {
      puVar10 = puVar13;
      puVar9 = puStack_48;
      do {
        puVar8 = puVar9;
        puVar5 = puVar10;
        uVar1 = *puVar8;
        uVar3 = puVar8[1];
        puVar5[2] = puVar8[2];
        *puVar5 = uVar1;
        puVar5[1] = uVar3;
        puVar9 = puVar8 + 4;
        puVar5[3] = puVar8[3];
        puVar10 = puVar5 + 4;
      } while (puVar9 != (undefined4 *)(param_1 + 0x138));
      puVar5[4] = *puVar9;
      puVar5[5] = puVar8[5];
    }
    puVar10 = (undefined4 *)(param_1 + 0x770);
    puVar9 = (undefined4 *)(param_1 + 0x30);
    do {
      puVar8 = puVar9;
      puVar5 = puVar10;
      uVar1 = *puVar5;
      uVar3 = puVar5[1];
      puVar8[2] = puVar5[2];
      *puVar8 = uVar1;
      puVar8[1] = uVar3;
      puVar10 = puVar5 + 4;
      puVar8[3] = puVar5[3];
      puVar9 = puVar8 + 4;
    } while (puVar10 != (undefined4 *)(param_1 + 0x7f0));
    puVar8[4] = *puVar10;
    puVar8[5] = puVar5[5];
    memmove(puStack_48,puVar13,0x88);
    *(undefined4 *)(param_1 + 0x1c) = 0;
    if (*(int *)(param_1 + 0x148) == 0) {
      *(undefined4 *)(param_1 + 0x150) = 0;
      *(undefined4 *)(param_1 + 0x154) = *(undefined4 *)(param_1 + 0x10);
      goto LAB_ram_4300c6c6;
    }
    uVar11 = 1;
  }
  else {
    iVar6 = (uint)(*(int *)(param_1 + 0x2c) != 0) * 8 + 7;
    if (*(int *)(param_1 + 0x14c) == 0) goto LAB_ram_4300c52a;
    puVar13 = (undefined4 *)(param_1 + 0x168);
    uVar12 = 0;
    iVar2 = param_1 + 0x30;
    iVar14 = param_1 + 0xb8;
    iVar15 = param_1 + 0xaa0;
    while( true ) {
      puStack_48 = (undefined4 *)(param_1 + 0xb8);
      differential_Decoding
                (*(undefined4 *)(param_1 + 0x20),iVar15 + -0x330,iVar2,*puVar13,
                 *(undefined4 *)(aNoIidBins + *(int *)(param_1 + 0x140) * 4),
                 (*(int *)(param_1 + 0x140) == 0) + '\x01',-iVar6,iVar6);
      differential_Decoding
                (*(undefined4 *)(param_1 + 0x24),iVar15,iVar14,puVar13[5],
                 *(undefined4 *)(aNoIccBins + *(int *)(param_1 + 0x144) * 4),
                 (*(int *)(param_1 + 0x144) == 0) + '\x01',0,7);
      uVar11 = *(uint *)(param_1 + 0x14c);
      uVar12 = uVar12 + 1;
      if (uVar11 <= uVar12) break;
      iVar2 = iVar15 + -0x330;
      puVar13 = puVar13 + 1;
      iVar14 = iVar15;
      iVar15 = iVar15 + 0x88;
    }
    if (uVar11 == 0) goto LAB_ram_4300c52a;
    iVar6 = (uVar11 - 1) * 0x88;
    memmove(param_1 + 0x30,iVar6 + 0x770 + param_1,0x88);
    memmove(puStack_48,iVar6 + 0xaa0 + param_1,0x88);
    *(undefined4 *)(param_1 + 0x1c) = 0;
    if (*(int *)(param_1 + 0x148) == 0) {
      *(undefined4 *)(param_1 + 0x150) = 0;
      uVar12 = *(uint *)(param_1 + 0x10);
      if (uVar11 != 1) {
        puVar7 = (uint *)(param_1 + 0x154);
        uVar4 = uVar12;
        do {
          *puVar7 = uVar4 >> (uVar11 >> 1 & 0x1f);
          puVar7 = puVar7 + 1;
          uVar4 = uVar4 + uVar12;
        } while (puVar7 != (uint *)(param_1 + 0x150 + uVar11 * 4));
      }
      *(uint *)(uVar11 * 4 + param_1 + 0x150) = uVar12;
      goto LAB_ram_4300c6c6;
    }
  }
  *(undefined4 *)(param_1 + 0x150) = 0;
  iVar6 = uVar11 * 4 + param_1;
  if (*(uint *)(iVar6 + 0x150) < *(uint *)(param_1 + 0x10)) {
    iVar2 = (uVar11 + 1) * 0x88;
    *(uint *)(param_1 + 0x14c) = uVar11 + 1;
    *(uint *)(iVar6 + 0x154) = *(uint *)(param_1 + 0x10);
    memmove(iVar2 + 0x770 + param_1,iVar2 + 0x6e8 + param_1,0x88);
    iVar6 = *(int *)(param_1 + 0x14c) * 0x88;
    memmove(iVar6 + 0xaa0 + param_1,iVar6 + 0xa18 + param_1,0x88);
  }
  uVar12 = *(uint *)(param_1 + 0x14c);
  if (uVar12 < 2) {
    if (uVar12 == 0) {
      return;
    }
  }
  else {
    uVar11 = *(uint *)(param_1 + 0x10);
    puVar7 = (uint *)(param_1 + 0x154);
    uVar12 = (uVar11 - uVar12) + 1;
    do {
      if (uVar12 < *puVar7) {
        *puVar7 = uVar12;
      }
      else if (*puVar7 < puVar7[-1] + 1) {
        *puVar7 = puVar7[-1] + 1;
      }
      uVar12 = uVar12 + 1;
      puVar7 = puVar7 + 1;
    } while (uVar11 != uVar12);
  }
LAB_ram_4300c6c6:
  iVar6 = param_1 + 0xaa0;
  uVar12 = 0;
  do {
    while( true ) {
      if (*(int *)(param_1 + 0x140) == 2) {
        map34IndexTo20(iVar6 + -0x330);
      }
      if (*(int *)(param_1 + 0x144) == 2) break;
      uVar12 = uVar12 + 1;
      iVar6 = iVar6 + 0x88;
      if (*(uint *)(param_1 + 0x14c) <= uVar12) {
        return;
      }
    }
    map34IndexTo20(iVar6);
    uVar12 = uVar12 + 1;
    iVar6 = iVar6 + 0x88;
  } while (uVar12 < *(uint *)(param_1 + 0x14c));
  return;
}
