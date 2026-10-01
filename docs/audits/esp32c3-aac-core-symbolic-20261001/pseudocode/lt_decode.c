/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: lt_decode @ ram:4300af4e
 * Types and parameter counts are inferred; verify against disassembly. */

void lt_decode(int param_1,aac_analysis_bits_t *bits,int param_3,aac_analysis_ltp_t *ltp)

{
  byte bVar1;
  ushort uVar2;
  uint8_t *puVar3;
  int32_t *piVar4;
  int32_t *piVar5;
  int iVar6;
  int32_t *piVar7;
  uint uVar8;
  uint uVar9;
  int iVar10;
  uint uVar11;
  uint32_t uVar12;
  int iVar13;
  byte *pbVar14;
  int32_t *piVar15;
  int iVar16;
  uint uVar17;
  int iVar18;
  int32_t *piVar19;
  int iVar20;

  gp = &__global_pointer_;
  uVar8 = bits->used_bits;
  puVar3 = bits->buffer;
  uVar17 = bits->input_length - (uVar8 >> 3);
  pbVar14 = puVar3 + (uVar8 >> 3);
  piVar15 = ltp->band_prediction;
  if (uVar17 < 3) {
    if (uVar17 == 1) {
      uVar17 = 0;
    }
    else {
      uVar11 = 0;
      if (uVar17 != 2) goto LAB_ram_4300af96;
      uVar17 = (uint)pbVar14[1] << 8;
    }
    uVar11 = (((uint)*pbVar14 << 0x10 | uVar17) << (uVar8 & 7)) >> 0xd & 0x7ff;
  }
  else {
    uVar11 = (((uint)*pbVar14 << 0x10 | (uint)pbVar14[1] << 8 | (uint)pbVar14[2]) << (uVar8 & 7)) >>
             0xd & 0x7ff;
  }
LAB_ram_4300af96:
  bits->used_bits = uVar8 + 0xb;
  ltp->delay[0] = uVar11;
  uVar8 = bits->used_bits;
  uVar17 = bits->input_length;
  uVar11 = uVar17 - (uVar8 >> 3);
  if (uVar11 < 2) {
    uVar9 = 0;
    if (uVar11 == 1) {
      uVar2 = *(ushort *)(puVar3 + (uVar8 >> 3));
      bits->used_bits = uVar8 + 3;
      ltp->weight = (((uint)(byte)uVar2 << 8) << (uVar8 & 7)) >> 0xd & 7;
      goto joined_r0x4300b08a;
    }
  }
  else {
    uVar2 = *(ushort *)(puVar3 + (uVar8 >> 3));
    uVar9 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar8 & 7)) << 0x10) >> 0x1d;
  }
  bits->used_bits = uVar8 + 3;
  ltp->weight = uVar9;
joined_r0x4300b08a:
  if (param_1 != 2) {
    uVar8 = uVar8 + 3;
    iVar20 = param_3;
    if (0x28 < param_3) {
      iVar20 = 0x28;
    }
    piVar5 = piVar15;
    iVar18 = iVar20;
    if (0 < param_3) {
      while( true ) {
        uVar11 = 0;
        if (uVar8 >> 3 < uVar17) {
          uVar11 = ((uint)puVar3[uVar8 >> 3] << (uVar8 & 7)) >> 7 & 1;
        }
        bits->used_bits = uVar8 + 1;
        *piVar5 = uVar11;
        if (iVar18 + -1 == 0) break;
        uVar8 = bits->used_bits;
        uVar17 = bits->input_length;
        piVar5 = piVar5 + 1;
        iVar18 = iVar18 + -1;
      }
      piVar15 = piVar15 + iVar20;
    }
    if (param_3 - iVar20 < 1) {
      return;
    }
    memset(piVar15,0,(param_3 - iVar20) * 4);
    return;
  }
  uVar9 = uVar8 + 3;
  uVar11 = uVar9 >> 3;
  iVar20 = ltp->delay[0];
  piVar5 = ltp->delay;
  iVar18 = 7;
  uVar12 = uVar8 + 4;
  if (uVar17 <= uVar11) goto LAB_ram_4300b0ec;
  while( true ) {
    bVar1 = puVar3[uVar11];
    bits->used_bits = uVar12;
    uVar8 = ((uint)bVar1 << (uVar9 & 7)) >> 7 & 1;
    piVar5[-0x89] = uVar8;
    if (uVar8 != 0) break;
    while( true ) {
      if (iVar18 == 0) {
        return;
      }
      uVar9 = bits->used_bits;
      piVar5 = piVar5 + 1;
      uVar11 = uVar9 >> 3;
      piVar15 = piVar15 + param_3;
      iVar18 = iVar18 + -1;
      uVar12 = uVar9 + 1;
      if (uVar11 < bits->input_length) break;
LAB_ram_4300b0ec:
      bits->used_bits = uVar12;
      piVar5[-0x89] = 0;
    }
  }
  iVar16 = param_3;
  if (0xd < param_3) {
    iVar16 = 0xd;
  }
  *piVar5 = iVar20;
  piVar4 = piVar15;
  iVar13 = iVar16;
  if (0 < param_3) {
    do {
      iVar13 = iVar13 + -1;
      *piVar4 = 1;
      piVar4 = piVar4 + 1;
    } while (iVar13 != 0);
    piVar15 = piVar15 + iVar16;
  }
  iVar13 = param_3 - iVar16;
  if (0 < iVar13) {
    iVar6 = memset(piVar15,0,iVar13 * 4);
    piVar15 = (int32_t *)(iVar6 + iVar13 * 4);
  }
  if (iVar18 != 0) {
    piVar4 = piVar5 + 2;
    piVar19 = piVar4 + iVar18;
    iVar6 = iVar20 + 0x10;
    iVar18 = 0;
    if (0 < param_3) {
      iVar18 = (iVar16 + -1) * 4;
    }
    piVar5 = piVar5 + -0x88;
    do {
      uVar8 = bits->used_bits;
      if (uVar8 >> 3 < bits->input_length) {
        bVar1 = puVar3[uVar8 >> 3];
        bits->used_bits = uVar8 + 1;
        uVar8 = ((uint)bVar1 << (uVar8 & 7)) >> 7 & 1;
        *piVar5 = uVar8;
        if (uVar8 == 0) goto LAB_ram_4300b1be;
        uVar17 = bits->used_bits;
        uVar8 = uVar17 + 1;
        iVar10 = iVar20;
        if (uVar17 >> 3 < bits->input_length) {
          bVar1 = puVar3[uVar17 >> 3];
          bits->used_bits = uVar8;
          if (((uint)bVar1 << (uVar17 & 7) & 0x80) != 0) {
            uVar11 = bits->input_length - (uVar8 >> 3);
            if (uVar11 < 2) {
              iVar10 = iVar6;
              if (uVar11 == 1) {
                iVar10 = iVar6 - ((((uint)(byte)*(ushort *)(puVar3 + (uVar8 >> 3)) << 8) <<
                                  (uVar8 & 7)) >> 0xb & 0x1f);
              }
            }
            else {
              uVar2 = *(ushort *)(puVar3 + (uVar8 >> 3));
              iVar10 = iVar6 - ((((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar8 & 7)) << 0x10)
                               >> 0x1b);
            }
            bits->used_bits = uVar17 + 6;
          }
        }
        else {
          bits->used_bits = uVar8;
        }
        piVar4[-1] = iVar10;
        piVar7 = piVar15;
        iVar10 = iVar16;
        if (0 < param_3) {
          do {
            iVar10 = iVar10 + -1;
            *piVar7 = 1;
            piVar7 = piVar7 + 1;
          } while (iVar10 != 0);
          piVar15 = (int32_t *)((int)piVar15 + iVar18 + 4);
        }
        if (0 < iVar13) {
          iVar10 = memset(piVar15,0);
          piVar15 = (int32_t *)(iVar10 + iVar13 * 4);
        }
      }
      else {
        bits->used_bits = uVar8 + 1;
        *piVar5 = 0;
LAB_ram_4300b1be:
        piVar15 = piVar15 + param_3;
      }
      piVar4 = piVar4 + 1;
      piVar5 = piVar5 + 1;
    } while (piVar4 != piVar19);
  }
  return;
}
