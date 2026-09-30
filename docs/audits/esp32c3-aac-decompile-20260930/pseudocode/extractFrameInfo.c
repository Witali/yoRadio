/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: extractFrameInfo @ ram:42057268
 * Types and parameter counts are inferred; verify against disassembly. */

uint extractFrameInfo(undefined4 param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  undefined4 uVar7;
  int *piVar8;
  int *piVar9;
  int *piVar10;
  size_t n;
  uint uVar11;
  uint uVar12;
  undefined4 *puVar13;
  int *piVar14;
  uint *puVar15;
  int iVar16;
  size_t n_00;
  int iVar17;
  int iVar18;
  int iVar19;
  uint uVar20;
  int iVar21;
  undefined4 *puStack_d4;
  size_t sStack_d0;
  uint uStack_cc;
  uint uStack_b8;
  uint uStack_b4;
  uint uStack_b0;
  int local_ac [10];
  int iStack_84;
  int iStack_80;
  int local_7c [3];
  uint auStack_70 [6];
  undefined4 local_58 [9];

  gp = &__global_pointer_;
  uVar2 = buf_getbits(param_1,2);
  *(uint *)(param_2 + 0xc) = uVar2;
  iVar18 = param_2 + 0x10;
  if (uVar2 == 2) {
    uVar12 = buf_getbits(param_1,2);
    iVar4 = buf_getbits(param_1,2);
    iVar3 = iVar4 + 1;
    piVar9 = local_ac;
    iVar16 = 0;
    iVar17 = iVar3;
    if (iVar4 < 1) {
      uVar6 = buf_getbits(param_1,*(undefined4 *)(bs_pointer_bits_tbl + iVar3 * 4));
      if (iVar3 == 1) goto LAB_ram_420576b2;
LAB_ram_42057750:
      n_00 = iVar3 * 4;
      auStack_70[0] = uVar12;
      iVar16 = iVar4 + 2;
      auStack_70[iVar3] = 0x10;
      uVar20 = 0x10;
    }
    else {
      do {
        iVar5 = buf_getbits(param_1,2);
        *piVar9 = (iVar5 + 1) * 2;
        iVar16 = iVar16 + 1;
        piVar9 = piVar9 + 1;
      } while (iVar4 != iVar16);
      uVar6 = buf_getbits(param_1,*(undefined4 *)(bs_pointer_bits_tbl + iVar3 * 4));
LAB_ram_420576b2:
      n_00 = iVar3 * 4;
      puVar13 = local_58;
      iVar16 = 0;
      do {
        uVar7 = buf_getbits(param_1,1);
        *puVar13 = uVar7;
        iVar16 = iVar16 + 1;
        puVar13 = puVar13 + 1;
      } while (iVar3 != iVar16);
      if (iVar4 == 0) goto LAB_ram_42057750;
      piVar9 = memcpy(local_ac + 9,local_ac,iVar4 << 2);
      auStack_70[0] = uVar12;
      auStack_70[iVar3] = 0x10;
      uVar20 = 0x10;
LAB_ram_420573bc:
      puVar15 = auStack_70;
      piVar10 = &iStack_84;
      iVar16 = 1;
      uVar11 = uVar12;
      piVar8 = piVar9;
      do {
        do {
          piVar14 = piVar8 + 1;
          uVar11 = uVar11 + *piVar8;
          piVar8 = piVar14;
        } while (piVar10 != piVar14);
        puVar15[1] = uVar11;
        iVar16 = iVar16 + 1;
        puVar15 = puVar15 + 1;
        piVar10 = piVar10 + 1;
        uVar11 = uVar12;
        piVar8 = piVar9;
      } while (iVar16 <= iVar4);
      if (iVar3 < iVar17) {
        piVar8 = local_7c;
LAB_ram_420573e6:
        piVar10 = piVar8 + (iVar17 - iVar3);
        puVar15 = auStack_70 + iVar3;
        uVar12 = uVar20;
        piVar9 = piVar8;
        do {
          do {
            piVar14 = piVar9 + 1;
            uVar12 = uVar12 - *piVar9;
            piVar9 = piVar14;
          } while (piVar10 != piVar14);
          *puVar15 = uVar12;
          iVar3 = iVar3 + 1;
          puVar15 = puVar15 + 1;
          piVar10 = piVar10 + -1;
          uVar12 = uVar20;
          piVar9 = piVar8;
        } while (iVar3 < iVar17);
      }
      uVar20 = *(uint *)((int)auStack_70 + n_00);
      iVar16 = iVar17 + 1;
      if (uVar2 != 2) {
        if (uVar2 < 3) {
          iVar5 = iVar16;
          iVar3 = iVar17;
          if (uVar2 != 0) goto LAB_ram_420575c4;
          goto LAB_ram_4205742c;
        }
        goto LAB_ram_420575b8;
      }
    }
    iVar1 = 1;
    if ((uVar6 != 0) && (iVar1 = uVar6 - 1, uVar6 == 1)) {
LAB_ram_420575d0:
      iVar1 = iVar17 + -1;
    }
  }
  else if (uVar2 < 3) {
    if (uVar2 != 0) {
      iVar3 = buf_getbits(param_1,2);
      iVar4 = buf_getbits(param_1,2);
      iVar17 = iVar4 + 1;
      piVar9 = local_ac;
      iVar16 = 0;
      if (0 < iVar4) {
        do {
          iVar5 = buf_getbits(param_1,2);
          *piVar9 = (iVar5 + 1) * 2;
          iVar16 = iVar16 + 1;
          piVar9 = piVar9 + 1;
        } while (iVar4 != iVar16);
        uVar6 = buf_getbits(param_1,*(undefined4 *)(bs_pointer_bits_tbl + iVar17 * 4));
LAB_ram_420572fc:
        uVar20 = iVar3 + 0x10;
        n_00 = iVar17 * 4;
        puVar13 = local_58 + iVar4;
        iVar16 = 0;
        do {
          uVar7 = buf_getbits(param_1,1);
          *puVar13 = uVar7;
          iVar16 = iVar16 + 1;
          puVar13 = puVar13 + -1;
        } while (iVar17 != iVar16);
        if (iVar4 == 0) goto LAB_ram_4205771e;
        piVar8 = memcpy(local_7c,local_ac,iVar4 << 2);
        auStack_70[0] = 0;
        auStack_70[iVar17] = uVar20;
        iVar3 = 1;
        goto LAB_ram_420573e6;
      }
      uVar6 = buf_getbits(param_1,*(undefined4 *)(bs_pointer_bits_tbl + iVar17 * 4));
      if (iVar17 == 1) goto LAB_ram_420572fc;
LAB_ram_4205771e:
      uVar20 = iVar3 + 0x10;
      n_00 = iVar17 * 4;
      auStack_70[0] = 0;
      auStack_70[iVar17] = uVar20;
      iVar5 = iVar4 + 2;
      goto LAB_ram_420575c4;
    }
    uVar12 = buf_getbits(param_1,2);
    local_58[0] = buf_getbits(param_1,1);
    iVar3 = 1 << (uVar12 & 0x1f);
    if (1 < iVar3) {
      iVar4 = iVar3 + -1;
      puVar13 = local_58 + 1;
      do {
        *puVar13 = local_58[0];
        puVar13 = puVar13 + 1;
      } while (puVar13 != (undefined4 *)((int)local_58 + (4 << (uVar12 & 0x1f))));
      n_00 = iVar3 * 4;
      local_ac[9] = *(int *)(T_16_ov_bs_num_env_tbl + n_00);
      if (iVar4 != 1) {
        iStack_84 = local_ac[9];
        if (iVar4 == 2) {
          uVar20 = 0x10;
          iVar3 = 3;
          auStack_70[0] = 0;
          auStack_70[3] = 0x10;
          uVar12 = 0;
          uVar6 = 0;
          n_00 = 0xc;
          piVar9 = local_ac + 9;
          iVar17 = iVar3;
          goto LAB_ram_420573bc;
        }
        iStack_80 = local_ac[9];
      }
      auStack_70[0] = 0;
      auStack_70[iVar3] = 0x10;
      uVar20 = 0x10;
      uVar12 = 0;
      uVar6 = 0;
      piVar9 = local_ac + 9;
      iVar17 = iVar3;
      goto LAB_ram_420573bc;
    }
    n_00 = iVar3 * 4;
    uVar20 = 0x10;
    auStack_70[0] = 0;
    auStack_70[iVar3] = 0x10;
    iVar16 = iVar3 + 1;
    uVar6 = 0;
LAB_ram_4205742c:
    iVar1 = iVar3 >> 1;
    iVar17 = iVar3;
  }
  else {
    if (uVar2 != 3) {
      iVar5 = 8;
      auStack_70[0] = 0;
      sStack_d0 = 8;
      iVar21 = 8;
      uStack_b4 = 0;
      iVar19 = 0x10;
      iVar4 = 0xc;
      n_00 = 0;
      n = 4;
      iVar17 = 0;
      uStack_cc = 0;
      uVar7 = 1;
      iVar3 = 0;
      goto LAB_ram_420575f8;
    }
    uVar12 = buf_getbits(param_1,2);
    iVar5 = buf_getbits(param_1,2);
    iVar4 = buf_getbits(param_1,2);
    iVar19 = buf_getbits(param_1,2);
    iVar16 = iVar4 + iVar19;
    iVar17 = iVar16 + 1;
    piVar9 = local_ac + 3;
    iVar3 = 0;
    if (0 < iVar4) {
      do {
        iVar21 = buf_getbits(param_1,2);
        *piVar9 = (iVar21 + 1) * 2;
        iVar3 = iVar3 + 1;
        piVar9 = piVar9 + 1;
      } while (iVar4 != iVar3);
    }
    if (iVar19 < 1) {
      uVar6 = buf_getbits(param_1,*(undefined4 *)(bs_pointer_bits_tbl + iVar17 * 4));
      if (0 < iVar17) goto LAB_ram_4205753a;
      if (0 < iVar4) goto LAB_ram_42057566;
LAB_ram_420577a8:
      uVar20 = iVar5 + 0x10;
      iVar3 = iVar4 + 1;
      n_00 = iVar17 * 4;
      auStack_70[0] = uVar12;
      auStack_70[iVar17] = uVar20;
      piVar8 = local_7c;
      iVar5 = iVar16 + 2;
      if (iVar4 < iVar16) goto LAB_ram_420573e6;
      goto LAB_ram_420575c4;
    }
    piVar9 = local_ac + 6;
    iVar3 = 0;
    do {
      iVar21 = buf_getbits(param_1,2);
      *piVar9 = (iVar21 + 1) * 2;
      iVar3 = iVar3 + 1;
      piVar9 = piVar9 + 1;
    } while (iVar19 != iVar3);
    uVar6 = buf_getbits(param_1,*(undefined4 *)(bs_pointer_bits_tbl + iVar17 * 4));
    if (0 < iVar17) {
LAB_ram_4205753a:
      puVar13 = local_58;
      iVar3 = 0;
      do {
        uVar7 = buf_getbits(param_1,1);
        *puVar13 = uVar7;
        iVar3 = iVar3 + 1;
        puVar13 = puVar13 + 1;
      } while (iVar17 != iVar3);
      if (iVar4 < 1) {
        if (iVar19 < 1) goto LAB_ram_420577a8;
      }
      else {
LAB_ram_42057566:
        uVar20 = iVar5 + 0x10;
        iVar3 = iVar4 + 1;
        n_00 = iVar17 * 4;
        piVar9 = memcpy(local_ac + 9,local_ac + 3,iVar4 << 2);
        if (iVar19 < 1) {
          auStack_70[0] = uVar12;
          auStack_70[iVar17] = uVar20;
          goto LAB_ram_420573bc;
        }
      }
    }
    uVar20 = iVar5 + 0x10;
    iVar3 = iVar4 + 1;
    n_00 = iVar17 * 4;
    piVar8 = memcpy(local_7c,local_ac + 6,iVar19 << 2);
    auStack_70[0] = uVar12;
    auStack_70[iVar17] = uVar20;
    piVar9 = local_ac + 9;
    if (0 < iVar4) goto LAB_ram_420573bc;
    if (iVar3 < iVar17) goto LAB_ram_420573e6;
    iVar16 = iVar16 + 2;
LAB_ram_420575b8:
    iVar1 = 0;
    iVar5 = iVar17 + 1;
    if (uVar2 == 3) {
LAB_ram_420575c4:
      iVar16 = iVar5;
      iVar1 = iVar16 - uVar6;
      if (1 < uVar6) goto LAB_ram_42057430;
      goto LAB_ram_420575d0;
    }
  }
LAB_ram_42057430:
  iVar5 = iVar16 * 8;
  uVar7 = 1;
  iVar21 = (iVar17 + 2) * 4;
  iVar4 = iVar5 + 4;
  iVar19 = iVar5 + 8;
  n = iVar16 << 2;
  if (iVar17 < 2) {
    sStack_d0 = 8;
    uStack_b4 = uVar20;
  }
  else {
    sStack_d0 = 0xc;
    uStack_b4 = auStack_70[iVar1];
    uVar7 = 2;
    uStack_b0 = uVar20;
  }
  uStack_cc = -(auStack_70[0] >> 0x1f | (uint)((int)uVar20 < (int)auStack_70[0])) & 0xe;
  if (uVar2 == 2) {
    iVar3 = -1;
    if (1 < uVar6) {
      iVar3 = uVar6 - 1;
    }
  }
  else {
    if (uVar2 < 3) {
      iVar3 = -1;
      if (uVar2 == 0) goto LAB_ram_420575f8;
    }
    else {
      iVar3 = 0;
      if (uVar2 != 3) goto LAB_ram_420575f8;
    }
    if (uVar6 == 0) {
      iVar3 = -1;
    }
    else {
      iVar3 = iVar16 - uVar6;
    }
  }
LAB_ram_420575f8:
  puStack_d4 = local_58;
  *(int *)(param_2 + 0x10) = iVar17;
  uStack_b8 = auStack_70[0];
  memcpy((void *)(param_2 + 0x14),auStack_70,n);
  memcpy((void *)(iVar18 + iVar21),puStack_d4,n_00);
  *(int *)(iVar5 + iVar18) = iVar3;
  *(undefined4 *)(iVar18 + iVar4) = uVar7;
  memcpy((void *)(iVar18 + iVar19),&uStack_b8,sStack_d0);
  return uStack_cc;
}
