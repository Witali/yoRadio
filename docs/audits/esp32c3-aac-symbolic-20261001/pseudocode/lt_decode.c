/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: lt_decode @ ram:4300af4e
 * Types and parameter counts are inferred; verify against disassembly. */

void lt_decode(int param_1,int *param_2,int param_3,uint *param_4)

{
  byte bVar1;
  ushort uVar2;
  int iVar3;
  uint *puVar4;
  int iVar5;
  uint uVar6;
  uint *puVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  int iVar11;
  uint *puVar12;
  byte *pbVar13;
  uint *puVar14;
  uint uVar15;
  ushort *puVar16;
  uint uVar17;
  int iVar18;
  uint *puVar19;
  int iVar20;

  gp = &__global_pointer_;
  uVar8 = param_2[1];
  iVar3 = *param_2;
  uVar15 = param_2[3] - (uVar8 >> 3);
  pbVar13 = (byte *)(iVar3 + (uVar8 >> 3));
  puVar14 = param_4 + 9;
  if (uVar15 < 3) {
    if (uVar15 == 1) {
      uVar15 = 0;
    }
    else {
      uVar10 = 0;
      if (uVar15 != 2) goto LAB_ram_4300af96;
      uVar15 = (uint)pbVar13[1] << 8;
    }
    uVar10 = (((uint)*pbVar13 << 0x10 | uVar15) << (uVar8 & 7)) >> 0xd & 0x7ff;
  }
  else {
    uVar10 = (((uint)*pbVar13 << 0x10 | (uint)pbVar13[1] << 8 | (uint)pbVar13[2]) << (uVar8 & 7)) >>
             0xd & 0x7ff;
  }
LAB_ram_4300af96:
  param_2[1] = uVar8 + 0xb;
  param_4[0x8a] = uVar10;
  uVar8 = param_2[1];
  uVar15 = param_2[3];
  uVar10 = uVar15 - (uVar8 >> 3);
  puVar16 = (ushort *)(iVar3 + (uVar8 >> 3));
  if (uVar10 < 2) {
    uVar9 = 0;
    if (uVar10 == 1) {
      uVar2 = *puVar16;
      param_2[1] = uVar8 + 3;
      *param_4 = (((uint)(byte)uVar2 << 8) << (uVar8 & 7)) >> 0xd & 7;
      goto joined_r0x4300b08a;
    }
  }
  else {
    uVar2 = *puVar16;
    uVar9 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar8 & 7)) << 0x10) >> 0x1d;
  }
  param_2[1] = uVar8 + 3;
  *param_4 = uVar9;
joined_r0x4300b08a:
  if (param_1 != 2) {
    uVar8 = uVar8 + 3;
    iVar20 = param_3;
    if (0x28 < param_3) {
      iVar20 = 0x28;
    }
    puVar4 = puVar14;
    iVar18 = iVar20;
    if (0 < param_3) {
      while( true ) {
        uVar10 = 0;
        if (uVar8 >> 3 < uVar15) {
          uVar10 = ((uint)*(byte *)(iVar3 + (uVar8 >> 3)) << (uVar8 & 7)) >> 7 & 1;
        }
        param_2[1] = uVar8 + 1;
        *puVar4 = uVar10;
        if (iVar18 + -1 == 0) break;
        uVar8 = param_2[1];
        uVar15 = param_2[3];
        puVar4 = puVar4 + 1;
        iVar18 = iVar18 + -1;
      }
      puVar14 = puVar14 + iVar20;
    }
    if (param_3 - iVar20 < 1) {
      return;
    }
    memset(puVar14,0,(param_3 - iVar20) * 4);
    return;
  }
  uVar9 = uVar8 + 3;
  uVar10 = uVar9 >> 3;
  uVar17 = param_4[0x8a];
  param_4 = param_4 + 0x8a;
  iVar18 = 7;
  iVar20 = uVar8 + 4;
  if (uVar15 <= uVar10) goto LAB_ram_4300b0ec;
  while( true ) {
    bVar1 = *(byte *)(iVar3 + uVar10);
    param_2[1] = iVar20;
    uVar8 = ((uint)bVar1 << (uVar9 & 7)) >> 7 & 1;
    param_4[-0x89] = uVar8;
    if (uVar8 != 0) break;
    while( true ) {
      if (iVar18 == 0) {
        return;
      }
      uVar9 = param_2[1];
      param_4 = param_4 + 1;
      uVar10 = uVar9 >> 3;
      puVar14 = puVar14 + param_3;
      iVar18 = iVar18 + -1;
      iVar20 = uVar9 + 1;
      if (uVar10 < (uint)param_2[3]) break;
LAB_ram_4300b0ec:
      param_2[1] = iVar20;
      param_4[-0x89] = 0;
    }
  }
  iVar20 = param_3;
  if (0xd < param_3) {
    iVar20 = 0xd;
  }
  *param_4 = uVar17;
  puVar4 = puVar14;
  iVar11 = iVar20;
  if (0 < param_3) {
    do {
      iVar11 = iVar11 + -1;
      *puVar4 = 1;
      puVar4 = puVar4 + 1;
    } while (iVar11 != 0);
    puVar14 = puVar14 + iVar20;
  }
  iVar11 = param_3 - iVar20;
  if (0 < iVar11) {
    iVar5 = memset(puVar14,0,iVar11 * 4);
    puVar14 = (uint *)(iVar5 + iVar11 * 4);
  }
  if (iVar18 != 0) {
    puVar4 = param_4 + 2;
    puVar19 = puVar4 + iVar18;
    uVar8 = uVar17 + 0x10;
    iVar18 = 0;
    if (0 < param_3) {
      iVar18 = (iVar20 + -1) * 4;
    }
    puVar12 = param_4 + -0x88;
    do {
      uVar15 = param_2[1];
      if (uVar15 >> 3 < (uint)param_2[3]) {
        bVar1 = *(byte *)((uVar15 >> 3) + iVar3);
        param_2[1] = uVar15 + 1;
        uVar15 = ((uint)bVar1 << (uVar15 & 7)) >> 7 & 1;
        *puVar12 = uVar15;
        if (uVar15 == 0) goto LAB_ram_4300b1be;
        uVar9 = param_2[1];
        uVar10 = uVar9 + 1;
        uVar15 = uVar17;
        if (uVar9 >> 3 < (uint)param_2[3]) {
          bVar1 = *(byte *)((uVar9 >> 3) + iVar3);
          param_2[1] = uVar10;
          if (((uint)bVar1 << (uVar9 & 7) & 0x80) != 0) {
            uVar6 = param_2[3] - (uVar10 >> 3);
            puVar16 = (ushort *)(iVar3 + (uVar10 >> 3));
            if (uVar6 < 2) {
              uVar15 = uVar8;
              if (uVar6 == 1) {
                uVar15 = uVar8 - ((((uint)(byte)*puVar16 << 8) << (uVar10 & 7)) >> 0xb & 0x1f);
              }
            }
            else {
              uVar2 = *puVar16;
              uVar15 = uVar8 - ((((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar10 & 7)) << 0x10)
                               >> 0x1b);
            }
            param_2[1] = uVar9 + 6;
          }
        }
        else {
          param_2[1] = uVar10;
        }
        puVar4[-1] = uVar15;
        puVar7 = puVar14;
        iVar5 = iVar20;
        if (0 < param_3) {
          do {
            iVar5 = iVar5 + -1;
            *puVar7 = 1;
            puVar7 = puVar7 + 1;
          } while (iVar5 != 0);
          puVar14 = (uint *)((int)puVar14 + iVar18 + 4);
        }
        if (0 < iVar11) {
          iVar5 = memset(puVar14,0);
          puVar14 = (uint *)(iVar5 + iVar11 * 4);
        }
      }
      else {
        param_2[1] = uVar15 + 1;
        *puVar12 = 0;
LAB_ram_4300b1be:
        puVar14 = puVar14 + param_3;
      }
      puVar4 = puVar4 + 1;
      puVar12 = puVar12 + 1;
    } while (puVar4 != puVar19);
  }
  return;
}
