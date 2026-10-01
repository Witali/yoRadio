/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: hufffac @ ram:4300940a
 * Types and parameter counts are inferred; verify against disassembly. */

int hufffac(aac_analysis_window_t *window,aac_analysis_bits_t *bits,int *param_3,int param_4,
           aac_analysis_section_t *sections,uint param_6,uint *param_7,int *param_8)

{
  ushort uVar1;
  bool bVar2;
  uint *puVar3;
  uint *puVar4;
  uint *puVar5;
  int iVar6;
  int32_t iVar7;
  uint *puVar8;
  int iVar9;
  int *piVar10;
  int32_t *piVar11;
  uint uVar13;
  uint uVar14;
  uint uVar15;
  uint uVar16;
  int iVar17;
  int iVar18;
  int iStack_58;
  uint *puStack_54;
  int *piStack_50;
  int *piStack_48;
  int iStack_44;
  int32_t *piVar12;

  gp = &__global_pointer_;
  memset(param_7,0,0x200);
  if (param_4 == 0) {
    memset(param_8,0,0x200);
  }
  else if (param_4 == 1) {
    uVar15 = sections->end;
    iVar7 = sections->codebook;
    iVar17 = (int)uVar15 >> 2;
    iVar6 = iVar17;
    piVar10 = param_8;
    piVar11 = param_8;
    if (iVar17 != 0) {
      do {
        *piVar11 = iVar7;
        piVar11[1] = iVar7;
        piVar11[2] = iVar7;
        iVar6 = iVar6 + -1;
        piVar11[3] = iVar7;
        piVar11 = piVar11 + 4;
      } while (iVar6 != 0);
      piVar10 = param_8 + iVar17 * 4;
      uVar15 = sections->end;
    }
    if ((uVar15 & 3) != 0) {
      piVar11 = piVar10;
      do {
        piVar12 = piVar11 + 1;
        *piVar11 = iVar7;
        piVar11 = piVar12;
      } while (piVar12 != piVar10 + (uVar15 & 3));
    }
  }
  else {
    iVar6 = 0;
    if (0 < param_4) {
      do {
        if (iVar6 < sections->end) {
          iVar7 = sections->codebook;
          piVar11 = param_8 + iVar6;
          do {
            *piVar11 = iVar7;
            iVar6 = iVar6 + 1;
            piVar11 = piVar11 + 1;
          } while (iVar6 < sections->end);
        }
        param_4 = param_4 + -1;
        sections = sections + 1;
      } while (param_4 != 0);
    }
  }
  if (window->windows < 1) {
    iStack_58 = 0;
  }
  else {
    bVar2 = true;
    uVar16 = param_6 - 0x5a;
    uVar15 = 0;
    iStack_44 = 0;
    iVar6 = 0;
    puStack_54 = param_7;
    piStack_50 = param_8;
    piStack_48 = param_3;
    do {
      iVar17 = window->bands_per_window[iVar6];
      iVar6 = *piStack_48;
      if (0 < iVar17) {
        iStack_58 = 0;
        iVar9 = *piStack_50;
        iVar18 = 0;
        puVar4 = puStack_54;
        piVar10 = piStack_50;
        if (iVar9 == 0xd) goto LAB_ram_43009520;
        do {
          if (iVar9 < 0xe) {
            if (iVar9 != 0) {
              if (iVar9 != 0xc) goto LAB_ram_43009578;
              iStack_58 = 1;
              goto LAB_ram_430094a2;
            }
          }
          else if (iVar9 - 0xeU < 2) {
            iVar9 = decode_huff_scl(bits);
            uVar15 = uVar15 + iVar9 + -0x3c;
            *puVar4 = uVar15;
          }
          else {
LAB_ram_43009578:
            iVar9 = decode_huff_scl(bits);
            param_6 = param_6 + iVar9 + -0x3c;
            if (param_6 < 0x100) {
              *puVar4 = param_6;
            }
            else {
              iStack_58 = 1;
            }
          }
          while( true ) {
            iVar18 = iVar18 + 1;
            piVar10 = piVar10 + 1;
            puVar4 = puVar4 + 1;
            if (iVar17 == iVar18) goto LAB_ram_430094a2;
            iVar9 = *piVar10;
            if (iVar9 != 0xd) break;
LAB_ram_43009520:
            if (bVar2) {
              uVar13 = bits->used_bits;
              uVar14 = bits->input_length - (uVar13 >> 3);
              if (uVar14 < 2) {
                iVar9 = -0x100;
                if (uVar14 == 1) {
                  iVar9 = ((((uint)(byte)*(ushort *)(bits->buffer + (uVar13 >> 3)) << 8) <<
                           (uVar13 & 7)) >> 7 & 0x1ff) - 0x100;
                }
              }
              else {
                uVar1 = *(ushort *)(bits->buffer + (uVar13 >> 3));
                iVar9 = ((((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 << (uVar13 & 7)) << 0x10) >>
                        0x17) - 0x100;
              }
              bits->used_bits = uVar13 + 9;
            }
            else {
              iVar9 = decode_huff_scl(bits);
              iVar9 = iVar9 + -0x3c;
            }
            uVar16 = uVar16 + iVar9;
            *puVar4 = uVar16;
            bVar2 = false;
          }
        } while( true );
      }
      iStack_58 = 0;
LAB_ram_430094a2:
      iVar9 = iStack_44;
      if ((window->is_long == 0) && (iVar9 = iStack_44 + 1, iVar9 < iVar6)) {
        puVar3 = puStack_54 + iVar17;
        puVar4 = puVar3;
        iVar18 = iVar9;
        puVar5 = puStack_54;
        if (0 < iVar17) {
          do {
            do {
              uVar13 = *puStack_54;
              puVar8 = puStack_54 + iVar17;
              puStack_54 = puStack_54 + 1;
              *puVar8 = uVar13;
            } while (puVar4 != puStack_54);
            iVar18 = iVar18 + 1;
            puStack_54 = puVar5 + iVar17;
            puVar4 = puVar4 + iVar17;
            puVar5 = puStack_54;
          } while (iVar18 != iVar6);
        }
        iVar18 = iVar6 - iStack_44;
        iStack_44 = (iVar9 + iVar6 + -1) - iStack_44;
        puStack_54 = (uint *)((iVar18 + -2) * iVar17 * 4 + (int)puVar3);
        iVar9 = window->windows;
      }
      else {
        iStack_44 = iVar9;
        iVar9 = window->windows;
      }
      if (iVar9 <= iVar6) {
        return iStack_58;
      }
      piStack_48 = piStack_48 + 1;
      piStack_50 = piStack_50 + iVar17;
      puStack_54 = puStack_54 + iVar17;
    } while (iStack_58 == 0);
  }
  return iStack_58;
}
