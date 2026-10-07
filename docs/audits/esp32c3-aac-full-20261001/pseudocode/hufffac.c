/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: hufffac @ ram:4300940a
 * Types and parameter counts are inferred; verify against disassembly. */

int hufffac(int *param_1,int *param_2,int *param_3,int param_4,int *param_5,uint param_6,
           uint *param_7,int *param_8)

{
  ushort uVar1;
  bool bVar2;
  ushort *puVar3;
  uint *puVar4;
  uint *puVar5;
  uint *puVar6;
  int iVar7;
  int iVar8;
  uint *puVar9;
  int iVar10;
  int *piVar11;
  int *piVar12;
  uint uVar14;
  uint uVar15;
  uint uVar16;
  uint uVar17;
  int iVar18;
  int iStack_58;
  uint *puStack_54;
  int *piStack_50;
  int *piStack_48;
  int iStack_44;
  int *piVar13;

  gp = &__global_pointer_;
  memset(param_7,0,0x200);
  if (param_4 == 0) {
    memset(param_8,0,0x200);
  }
  else if (param_4 == 1) {
    uVar16 = param_5[1];
    iVar10 = *param_5;
    iVar8 = (int)uVar16 >> 2;
    iVar7 = iVar8;
    piVar11 = param_8;
    if (iVar8 != 0) {
      do {
        *piVar11 = iVar10;
        piVar11[1] = iVar10;
        piVar11[2] = iVar10;
        iVar7 = iVar7 + -1;
        piVar11[3] = iVar10;
        piVar11 = piVar11 + 4;
      } while (iVar7 != 0);
      piVar11 = param_8 + iVar8 * 4;
      uVar16 = param_5[1];
    }
    if ((uVar16 & 3) != 0) {
      piVar12 = piVar11;
      do {
        piVar13 = piVar12 + 1;
        *piVar12 = iVar10;
        piVar12 = piVar13;
      } while (piVar13 != piVar11 + (uVar16 & 3));
    }
  }
  else {
    iVar7 = 0;
    if (0 < param_4) {
      do {
        if (iVar7 < param_5[1]) {
          iVar8 = *param_5;
          piVar11 = param_8 + iVar7;
          do {
            *piVar11 = iVar8;
            iVar7 = iVar7 + 1;
            piVar11 = piVar11 + 1;
          } while (iVar7 < param_5[1]);
        }
        param_4 = param_4 + -1;
        param_5 = param_5 + 2;
      } while (param_4 != 0);
    }
  }
  if (param_1[1] < 1) {
    iStack_58 = 0;
  }
  else {
    bVar2 = true;
    uVar17 = param_6 - 0x5a;
    uVar16 = 0;
    iStack_44 = 0;
    iVar7 = 0;
    puStack_54 = param_7;
    piStack_50 = param_8;
    piStack_48 = param_3;
    do {
      iVar8 = param_1[iVar7 + 0xc];
      iVar7 = *piStack_48;
      if (0 < iVar8) {
        iStack_58 = 0;
        iVar10 = *piStack_50;
        iVar18 = 0;
        puVar5 = puStack_54;
        piVar11 = piStack_50;
        if (iVar10 == 0xd) goto LAB_ram_43009520;
        do {
          if (iVar10 < 0xe) {
            if (iVar10 != 0) {
              if (iVar10 != 0xc) goto LAB_ram_43009578;
              iStack_58 = 1;
              goto LAB_ram_430094a2;
            }
          }
          else if (iVar10 - 0xeU < 2) {
            iVar10 = decode_huff_scl(param_2);
            uVar16 = uVar16 + iVar10 + -0x3c;
            *puVar5 = uVar16;
          }
          else {
LAB_ram_43009578:
            iVar10 = decode_huff_scl(param_2);
            param_6 = param_6 + iVar10 + -0x3c;
            if (param_6 < 0x100) {
              *puVar5 = param_6;
            }
            else {
              iStack_58 = 1;
            }
          }
          while( true ) {
            iVar18 = iVar18 + 1;
            piVar11 = piVar11 + 1;
            puVar5 = puVar5 + 1;
            if (iVar8 == iVar18) goto LAB_ram_430094a2;
            iVar10 = *piVar11;
            if (iVar10 != 0xd) break;
LAB_ram_43009520:
            if (bVar2) {
              uVar14 = param_2[1];
              uVar15 = param_2[3] - (uVar14 >> 3);
              puVar3 = (ushort *)((uVar14 >> 3) + *param_2);
              if (uVar15 < 2) {
                iVar10 = -0x100;
                if (uVar15 == 1) {
                  iVar10 = ((((uint)(byte)*puVar3 << 8) << (uVar14 & 7)) >> 7 & 0x1ff) - 0x100;
                }
              }
              else {
                uVar1 = *puVar3;
                iVar10 = ((((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 << (uVar14 & 7)) << 0x10) >>
                         0x17) - 0x100;
              }
              param_2[1] = uVar14 + 9;
            }
            else {
              iVar10 = decode_huff_scl(param_2);
              iVar10 = iVar10 + -0x3c;
            }
            uVar17 = uVar17 + iVar10;
            *puVar5 = uVar17;
            bVar2 = false;
          }
        } while( true );
      }
      iStack_58 = 0;
LAB_ram_430094a2:
      iVar10 = iStack_44;
      if ((*param_1 == 0) && (iVar10 = iStack_44 + 1, iVar10 < iVar7)) {
        puVar4 = puStack_54 + iVar8;
        puVar5 = puVar4;
        iVar18 = iVar10;
        puVar6 = puStack_54;
        if (0 < iVar8) {
          do {
            do {
              uVar14 = *puStack_54;
              puVar9 = puStack_54 + iVar8;
              puStack_54 = puStack_54 + 1;
              *puVar9 = uVar14;
            } while (puVar5 != puStack_54);
            iVar18 = iVar18 + 1;
            puStack_54 = puVar6 + iVar8;
            puVar5 = puVar5 + iVar8;
            puVar6 = puStack_54;
          } while (iVar18 != iVar7);
        }
        iVar18 = iVar7 - iStack_44;
        iStack_44 = (iVar10 + iVar7 + -1) - iStack_44;
        puStack_54 = (uint *)((iVar18 + -2) * iVar8 * 4 + (int)puVar4);
        iVar10 = param_1[1];
      }
      else {
        iStack_44 = iVar10;
        iVar10 = param_1[1];
      }
      if (iVar10 <= iVar7) {
        return iStack_58;
      }
      piStack_48 = piStack_48 + 1;
      piStack_50 = piStack_50 + iVar8;
      puStack_54 = puStack_54 + iVar8;
    } while (iStack_58 == 0);
  }
  return iStack_58;
}
