/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: get_tns @ ram:430085c4
 * Types and parameter counts are inferred; verify against disassembly. */

void get_tns(int param_1,int *param_2,int param_3,int param_4,int param_5,int param_6,
            undefined4 param_7)

{
  ushort uVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  uint *puVar9;
  uint uVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int *piVar14;
  uint uVar15;
  uint uVar16;
  uint uVar17;
  ushort *puVar18;
  uint uVar19;
  int iVar20;
  int iVar21;
  int *piVar22;
  int iVar23;
  uint *puVar24;
  int iVar25;
  int iVar26;
  uint uVar27;
  uint *puVar28;
  uint uStack_74;
  uint uStack_70;
  uint uStack_6c;

  gp = &__global_pointer_;
  iVar8 = *(int *)(param_5 + 0x1c);
  iVar12 = *(int *)(param_4 + 0x70);
  if (param_3 == 2) {
    iVar23 = *(int *)(tns_max_bands_tbl_short_wndw + iVar8 * 4);
    iVar5 = 1;
    uStack_70 = 7;
    iVar8 = 4;
    iVar26 = 3;
  }
  else {
    iVar23 = *(int *)(tns_max_bands_tbl_long_wndw + iVar8 * 4);
    iVar5 = 2;
    if (iVar8 < 5) {
      uStack_70 = 0xc;
      iVar8 = 6;
      iVar26 = 5;
    }
    else {
      uStack_70 = 0x14;
      iVar8 = 6;
      iVar26 = 5;
    }
  }
  if (param_1 < iVar23) {
    iVar23 = param_1;
  }
  iVar13 = *(int *)(param_4 + 0x30);
  puVar9 = (uint *)(param_6 + 0x104);
  piVar14 = (int *)(param_6 + 0x24);
  puVar24 = (uint *)(param_6 + 4);
  iVar25 = 0;
LAB_ram_43008686:
  while( true ) {
    uVar16 = param_2[1];
    uVar7 = param_2[3];
    iVar6 = *param_2;
    uVar27 = uVar7 - (uVar16 >> 3);
    puVar18 = (ushort *)(iVar6 + (uVar16 >> 3));
    uVar4 = uVar16 + iVar5;
    if (1 < uVar27) break;
    if (uVar27 == 1) {
      iVar21 = (uint)(byte)*puVar18 << 8;
      goto LAB_ram_4300865c;
    }
    param_2[1] = uVar4;
    *puVar24 = 0;
    iVar25 = iVar25 + 1;
    puVar24 = puVar24 + 1;
    if (*(int *)(param_4 + 4) <= iVar25) {
      return;
    }
  }
  uVar1 = *puVar18;
  iVar21 = (uint)(uVar1 >> 8) + (uint)uVar1 * 0x100;
LAB_ram_4300865c:
  param_2[1] = uVar4;
  uVar16 = (iVar21 << (uVar16 & 7) & 0xffffU) >> (0x10U - iVar5 & 0x1f);
  *puVar24 = uVar16;
  if (uVar16 != 0) {
    if (uVar4 >> 3 < uVar7) {
      uStack_6c = ((uint)*(byte *)((uVar4 >> 3) + iVar6) << (uVar4 & 7)) >> 7 & 1;
      uStack_74 = uStack_6c + 1;
    }
    else {
      uStack_74 = 1;
      uStack_6c = 0;
    }
    uVar4 = uVar4 + 1;
    param_2[1] = uVar4;
    piVar22 = piVar14;
    iVar21 = iVar13;
    uVar27 = uVar16;
    do {
      iVar11 = iVar23;
      if (iVar21 < iVar23) {
        iVar11 = iVar21;
      }
      iVar20 = 0;
      if (iVar11 != 0) {
        iVar20 = (int)*(short *)((iVar11 + 0x7fffffff) * 2 + iVar12);
      }
      uVar10 = uVar7 - (uVar4 >> 3);
      piVar22[1] = iVar11;
      piVar22[3] = iVar20;
      puVar18 = (ushort *)((uVar4 >> 3) + iVar6);
      if (uVar10 < 2) {
        uVar17 = 0;
        if (uVar10 == 1) {
          uVar17 = (((uint)(byte)*puVar18 << 8) << (uVar4 & 7) & 0xffff) >> (0x10U - iVar8 & 0x1f);
        }
      }
      else {
        uVar1 = *puVar18;
        uVar17 = ((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 << (uVar4 & 7) & 0xffff) >>
                 (0x10U - iVar8 & 0x1f);
      }
      uVar4 = iVar8 + uVar4;
      iVar21 = iVar21 - uVar17;
      param_2[1] = uVar4;
      iVar11 = iVar23;
      if (iVar21 < iVar23) {
        iVar11 = iVar21;
      }
      iVar3 = 0;
      if (iVar11 != 0) {
        iVar3 = (int)*(short *)((iVar11 + 0x7fffffff) * 2 + iVar12);
      }
      *piVar22 = iVar11;
      uVar10 = uVar7 - (uVar4 >> 3);
      piVar22[2] = iVar3;
      puVar18 = (ushort *)((uVar4 >> 3) + iVar6);
      uVar17 = uVar4 + iVar26;
      if (uVar10 < 2) {
        if (uVar10 == 1) {
          iVar11 = (uint)(byte)*puVar18 << 8;
          goto LAB_ram_430087b4;
        }
        param_2[1] = uVar17;
LAB_ram_430087c8:
        piVar22[4] = 0;
        puVar28 = puVar9;
      }
      else {
        uVar1 = *puVar18;
        iVar11 = (uint)uVar1 * 0x100 + (uint)(uVar1 >> 8);
LAB_ram_430087b4:
        param_2[1] = uVar17;
        uVar4 = (iVar11 << (uVar4 & 7) & 0xffffU) >> (0x10U - iVar26 & 0x1f);
        if (uVar4 == 0) goto LAB_ram_430087c8;
        uVar10 = uStack_70;
        if (uVar4 < uStack_70) {
          uVar10 = uVar4;
        }
        piVar22[4] = uVar10;
        uVar4 = 1;
        if (uVar17 >> 3 < uVar7) {
          uVar4 = (int)(((uint)*(byte *)((uVar17 >> 3) + iVar6) << (uVar17 & 7)) << 0x18) >> 0x1f |
                  1;
        }
        uVar15 = uVar17 + 1;
        param_2[1] = uVar15;
        piVar22[5] = uVar4;
        uVar4 = uStack_74;
        if (uVar15 >> 3 < uVar7) {
          uVar4 = uStack_74 - (((uint)*(byte *)((uVar15 >> 3) + iVar6) << (uVar15 & 7)) >> 7 & 1);
        }
        uVar17 = uVar17 + 2;
        param_2[1] = uVar17;
        uVar15 = uVar10;
        puVar28 = puVar9;
        do {
          uVar2 = uVar7 - (uVar17 >> 3);
          puVar18 = (ushort *)((uVar17 >> 3) + iVar6);
          if (uVar2 < 2) {
            uVar19 = 0;
            if (uVar2 == 1) {
              iVar11 = (uint)(byte)*puVar18 << 8;
              goto LAB_ram_43008860;
            }
          }
          else {
            uVar1 = *puVar18;
            iVar11 = (uint)(uVar1 >> 8) + (uint)uVar1 * 0x100;
LAB_ram_43008860:
            uVar19 = (iVar11 << (uVar17 & 7) & 0xffffU) >> (0x10 - (uVar4 + 2) & 0x1f);
            uVar19 = -(2 << (uVar4 & 0x1f) & uVar19) | uVar19;
          }
          uVar17 = uVar17 + uVar4 + 2;
          param_2[1] = uVar17;
          uVar15 = uVar15 - 1;
          *puVar28 = uVar19;
          puVar28 = puVar28 + 1;
        } while (uVar15 != 0);
        puVar28 = puVar9 + uVar10;
        if (iVar20 != iVar3) {
          iVar6 = tns_decode_coef(uVar10,uStack_6c,puVar9,param_7);
          piVar22[6] = iVar6;
        }
      }
      puVar9 = puVar28;
      if (uVar27 == 1) goto LAB_ram_430088f8;
      uVar27 = uVar27 - 1;
      uVar4 = param_2[1];
      iVar6 = *param_2;
      uVar7 = param_2[3];
      piVar22 = piVar22 + 7;
    } while( true );
  }
  goto LAB_ram_4300867a;
LAB_ram_430088f8:
  piVar14 = piVar14 + (uVar16 - 1) * 7 + 7;
LAB_ram_4300867a:
  iVar25 = iVar25 + 1;
  puVar24 = puVar24 + 1;
  if (*(int *)(param_4 + 4) <= iVar25) {
    return;
  }
  goto LAB_ram_43008686;
}
