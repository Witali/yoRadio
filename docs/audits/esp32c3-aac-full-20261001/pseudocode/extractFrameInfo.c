/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: extractFrameInfo @ ram:430060a2
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
  int iVar11;
  int iVar12;
  uint uVar13;
  uint uVar14;
  undefined4 *puVar15;
  int *piVar16;
  uint *puVar17;
  int iVar18;
  int iVar19;
  int iVar20;
  int iVar21;
  uint uVar22;
  int iVar23;
  undefined4 *puStack_d4;
  undefined4 uStack_d0;
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
  iVar20 = param_2 + 0x10;
  if (uVar2 == 2) {
    uVar14 = buf_getbits(param_1,2);
    iVar4 = buf_getbits(param_1,2);
    iVar3 = iVar4 + 1;
    piVar9 = local_ac;
    iVar18 = 0;
    iVar19 = iVar3;
    if (iVar4 < 1) {
      uVar6 = buf_getbits(param_1,*(undefined4 *)(bs_pointer_bits_tbl + iVar3 * 4));
      if (iVar3 == 1) goto LAB_ram_4300653c;
LAB_ram_430065e6:
      iVar18 = iVar3 * 4;
      auStack_70[0] = uVar14;
      iVar5 = iVar4 + 2;
      auStack_70[iVar3] = 0x10;
      uVar22 = 0x10;
    }
    else {
      do {
        iVar5 = buf_getbits(param_1,2);
        *piVar9 = (iVar5 + 1) * 2;
        iVar18 = iVar18 + 1;
        piVar9 = piVar9 + 1;
      } while (iVar4 != iVar18);
      uVar6 = buf_getbits(param_1,*(undefined4 *)(bs_pointer_bits_tbl + iVar3 * 4));
LAB_ram_4300653c:
      iVar18 = iVar3 * 4;
      puVar15 = local_58;
      iVar5 = 0;
      do {
        uVar7 = buf_getbits(param_1,1);
        *puVar15 = uVar7;
        iVar5 = iVar5 + 1;
        puVar15 = puVar15 + 1;
      } while (iVar3 != iVar5);
      if (iVar4 == 0) goto LAB_ram_430065e6;
      piVar9 = (int *)memcpy(local_ac + 9,local_ac,iVar4 << 2);
      auStack_70[0] = uVar14;
      auStack_70[iVar3] = 0x10;
      uVar22 = 0x10;
LAB_ram_43006216:
      puVar17 = auStack_70;
      piVar10 = &iStack_84;
      iVar5 = 1;
      uVar13 = uVar14;
      piVar8 = piVar9;
      do {
        do {
          piVar16 = piVar8 + 1;
          uVar13 = uVar13 + *piVar8;
          piVar8 = piVar16;
        } while (piVar10 != piVar16);
        puVar17[1] = uVar13;
        iVar5 = iVar5 + 1;
        puVar17 = puVar17 + 1;
        piVar10 = piVar10 + 1;
        uVar13 = uVar14;
        piVar8 = piVar9;
      } while (iVar5 <= iVar4);
      if (iVar3 < iVar19) {
        piVar8 = local_7c;
LAB_ram_43006240:
        piVar10 = piVar8 + (iVar19 - iVar3);
        puVar17 = auStack_70 + iVar3;
        uVar14 = uVar22;
        piVar9 = piVar8;
        do {
          do {
            piVar16 = piVar9 + 1;
            uVar14 = uVar14 - *piVar9;
            piVar9 = piVar16;
          } while (piVar10 != piVar16);
          *puVar17 = uVar14;
          iVar3 = iVar3 + 1;
          puVar17 = puVar17 + 1;
          piVar10 = piVar10 + -1;
          uVar14 = uVar22;
          piVar9 = piVar8;
        } while (iVar3 < iVar19);
      }
      uVar22 = *(uint *)((int)auStack_70 + iVar18);
      iVar5 = iVar19 + 1;
      if (uVar2 != 2) {
        if (uVar2 < 3) {
          iVar11 = iVar5;
          iVar3 = iVar19;
          if (uVar2 != 0) goto LAB_ram_4300643e;
          goto LAB_ram_43006286;
        }
        goto LAB_ram_43006432;
      }
    }
    iVar1 = 1;
    if ((uVar6 != 0) && (iVar1 = uVar6 - 1, uVar6 == 1)) {
LAB_ram_4300644a:
      iVar1 = iVar19 + -1;
    }
  }
  else if (uVar2 < 3) {
    if (uVar2 != 0) {
      iVar3 = buf_getbits(param_1,2);
      iVar4 = buf_getbits(param_1,2);
      iVar19 = iVar4 + 1;
      piVar9 = local_ac;
      iVar18 = 0;
      if (0 < iVar4) {
        do {
          iVar5 = buf_getbits(param_1,2);
          *piVar9 = (iVar5 + 1) * 2;
          iVar18 = iVar18 + 1;
          piVar9 = piVar9 + 1;
        } while (iVar4 != iVar18);
        uVar6 = buf_getbits(param_1,*(undefined4 *)(bs_pointer_bits_tbl + iVar19 * 4));
LAB_ram_4300614a:
        uVar22 = iVar3 + 0x10;
        iVar18 = iVar19 * 4;
        puVar15 = local_58 + iVar4;
        iVar5 = 0;
        do {
          uVar7 = buf_getbits(param_1,1);
          *puVar15 = uVar7;
          iVar5 = iVar5 + 1;
          puVar15 = puVar15 + -1;
        } while (iVar19 != iVar5);
        if (iVar4 == 0) goto LAB_ram_430065b0;
        piVar8 = (int *)memcpy(local_7c,local_ac,iVar4 << 2);
        auStack_70[0] = 0;
        auStack_70[iVar19] = uVar22;
        iVar3 = 1;
        goto LAB_ram_43006240;
      }
      uVar6 = buf_getbits(param_1,*(undefined4 *)(bs_pointer_bits_tbl + iVar19 * 4));
      if (iVar19 == 1) goto LAB_ram_4300614a;
LAB_ram_430065b0:
      uVar22 = iVar3 + 0x10;
      iVar18 = iVar19 * 4;
      auStack_70[0] = 0;
      auStack_70[iVar19] = uVar22;
      iVar11 = iVar4 + 2;
      goto LAB_ram_4300643e;
    }
    uVar14 = buf_getbits(param_1,2);
    local_58[0] = buf_getbits(param_1,1);
    iVar3 = 1 << (uVar14 & 0x1f);
    if (1 < iVar3) {
      iVar4 = iVar3 + -1;
      puVar15 = local_58 + 1;
      do {
        *puVar15 = local_58[0];
        puVar15 = puVar15 + 1;
      } while (puVar15 != (undefined4 *)((int)local_58 + (4 << (uVar14 & 0x1f))));
      iVar18 = iVar3 * 4;
      local_ac[9] = *(int *)(T_16_ov_bs_num_env_tbl + iVar18);
      if (iVar4 != 1) {
        iStack_84 = local_ac[9];
        if (iVar4 == 2) {
          uVar22 = 0x10;
          iVar3 = 3;
          auStack_70[0] = 0;
          auStack_70[3] = 0x10;
          uVar14 = 0;
          uVar6 = 0;
          iVar18 = 0xc;
          piVar9 = local_ac + 9;
          iVar19 = iVar3;
          goto LAB_ram_43006216;
        }
        iStack_80 = local_ac[9];
      }
      auStack_70[0] = 0;
      auStack_70[iVar3] = 0x10;
      uVar22 = 0x10;
      uVar14 = 0;
      uVar6 = 0;
      piVar9 = local_ac + 9;
      iVar19 = iVar3;
      goto LAB_ram_43006216;
    }
    iVar18 = iVar3 * 4;
    uVar22 = 0x10;
    auStack_70[0] = 0;
    auStack_70[iVar3] = 0x10;
    iVar5 = iVar3 + 1;
    uVar6 = 0;
LAB_ram_43006286:
    iVar1 = iVar3 >> 1;
    iVar19 = iVar3;
  }
  else {
    if (uVar2 != 3) {
      iVar12 = 8;
      auStack_70[0] = 0;
      uStack_d0 = 8;
      iVar23 = 8;
      uStack_b4 = 0;
      iVar21 = 0x10;
      iVar4 = 0xc;
      iVar18 = 0;
      iVar11 = 4;
      iVar19 = 0;
      uStack_cc = 0;
      uVar7 = 1;
      iVar3 = 0;
      goto LAB_ram_43006472;
    }
    uVar14 = buf_getbits(param_1,2);
    iVar11 = buf_getbits(param_1,2);
    iVar4 = buf_getbits(param_1,2);
    iVar12 = buf_getbits(param_1,2);
    iVar5 = iVar4 + iVar12;
    iVar19 = iVar5 + 1;
    piVar9 = local_ac + 3;
    iVar3 = 0;
    if (0 < iVar4) {
      do {
        iVar18 = buf_getbits(param_1,2);
        *piVar9 = (iVar18 + 1) * 2;
        iVar3 = iVar3 + 1;
        piVar9 = piVar9 + 1;
      } while (iVar4 != iVar3);
    }
    if (iVar12 < 1) {
      uVar6 = buf_getbits(param_1,*(undefined4 *)(bs_pointer_bits_tbl + iVar19 * 4));
      if (0 < iVar19) goto LAB_ram_430063b0;
      if (0 < iVar4) goto LAB_ram_430063e0;
LAB_ram_43006642:
      uVar22 = iVar11 + 0x10;
      iVar3 = iVar4 + 1;
      iVar18 = iVar19 * 4;
      auStack_70[0] = uVar14;
      auStack_70[iVar19] = uVar22;
      piVar8 = local_7c;
      iVar11 = iVar5 + 2;
      if (iVar4 < iVar5) goto LAB_ram_43006240;
      goto LAB_ram_4300643e;
    }
    piVar9 = local_ac + 6;
    iVar3 = 0;
    do {
      iVar18 = buf_getbits(param_1,2);
      *piVar9 = (iVar18 + 1) * 2;
      iVar3 = iVar3 + 1;
      piVar9 = piVar9 + 1;
    } while (iVar12 != iVar3);
    uVar6 = buf_getbits(param_1,*(undefined4 *)(bs_pointer_bits_tbl + iVar19 * 4));
    if (0 < iVar19) {
LAB_ram_430063b0:
      puVar15 = local_58;
      iVar3 = 0;
      do {
        uVar7 = buf_getbits(param_1,1);
        *puVar15 = uVar7;
        iVar3 = iVar3 + 1;
        puVar15 = puVar15 + 1;
      } while (iVar19 != iVar3);
      if (iVar4 < 1) {
        if (iVar12 < 1) goto LAB_ram_43006642;
      }
      else {
LAB_ram_430063e0:
        uVar22 = iVar11 + 0x10;
        iVar3 = iVar4 + 1;
        iVar18 = iVar19 * 4;
        piVar9 = (int *)memcpy(local_ac + 9,local_ac + 3,iVar4 << 2);
        if (iVar12 < 1) {
          auStack_70[0] = uVar14;
          auStack_70[iVar19] = uVar22;
          goto LAB_ram_43006216;
        }
      }
    }
    uVar22 = iVar11 + 0x10;
    iVar3 = iVar4 + 1;
    iVar18 = iVar19 * 4;
    piVar8 = (int *)memcpy(local_7c,local_ac + 6,iVar12 << 2);
    auStack_70[0] = uVar14;
    auStack_70[iVar19] = uVar22;
    piVar9 = local_ac + 9;
    if (0 < iVar4) goto LAB_ram_43006216;
    if (iVar3 < iVar19) goto LAB_ram_43006240;
    iVar5 = iVar5 + 2;
LAB_ram_43006432:
    iVar1 = 0;
    iVar11 = iVar19 + 1;
    if (uVar2 == 3) {
LAB_ram_4300643e:
      iVar5 = iVar11;
      iVar1 = iVar5 - uVar6;
      if (1 < uVar6) goto LAB_ram_4300628a;
      goto LAB_ram_4300644a;
    }
  }
LAB_ram_4300628a:
  iVar12 = iVar5 * 8;
  uVar7 = 1;
  iVar23 = (iVar19 + 2) * 4;
  iVar4 = iVar12 + 4;
  iVar21 = iVar12 + 8;
  iVar11 = iVar5 << 2;
  if (iVar19 < 2) {
    uStack_d0 = 8;
    uStack_b4 = uVar22;
  }
  else {
    uStack_d0 = 0xc;
    uStack_b4 = auStack_70[iVar1];
    uVar7 = 2;
    uStack_b0 = uVar22;
  }
  uStack_cc = -(auStack_70[0] >> 0x1f | (uint)((int)uVar22 < (int)auStack_70[0])) & 0xe;
  if (uVar2 == 2) {
    iVar3 = -1;
    if (1 < uVar6) {
      iVar3 = uVar6 - 1;
    }
  }
  else {
    if (uVar2 < 3) {
      iVar3 = -1;
      if (uVar2 == 0) goto LAB_ram_43006472;
    }
    else {
      iVar3 = 0;
      if (uVar2 != 3) goto LAB_ram_43006472;
    }
    if (uVar6 == 0) {
      iVar3 = -1;
    }
    else {
      iVar3 = iVar5 - uVar6;
    }
  }
LAB_ram_43006472:
  puStack_d4 = local_58;
  *(int *)(param_2 + 0x10) = iVar19;
  uStack_b8 = auStack_70[0];
  memcpy(param_2 + 0x14,auStack_70,iVar11);
  memcpy(iVar20 + iVar23,puStack_d4,iVar18);
  *(int *)(iVar12 + iVar20) = iVar3;
  *(undefined4 *)(iVar20 + iVar4) = uVar7;
  memcpy(iVar20 + iVar21,&uStack_b8,uStack_d0);
  return uStack_cc;
}
