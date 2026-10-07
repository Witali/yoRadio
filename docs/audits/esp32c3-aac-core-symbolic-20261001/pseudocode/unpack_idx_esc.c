/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: unpack_idx_esc @ ram:43015eba
 * Types and parameter counts are inferred; verify against disassembly. */

void unpack_idx_esc(undefined2 *param_1,int param_2,aac_analysis_codebook_t *book,
                   aac_analysis_bits_t *bits,int *param_5)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  uint uVar9;
  uint8_t *puVar10;
  byte *pbVar11;
  uint uVar12;
  uint32_t uVar13;
  uint uVar14;
  uint32_t uVar15;

  gp = &__global_pointer_;
  iVar2 = book->offset;
  iVar8 = param_2 * *(int *)(div_mod + book->modulus * 4) >> 0xd;
  uVar12 = iVar8 - iVar2;
  iVar5 = param_2 - book->modulus * iVar8;
  uVar7 = iVar5 - iVar2;
  if (iVar8 == iVar2) {
    if (iVar2 == iVar5) {
      iVar2 = *param_5;
      *param_1 = 0;
      uVar12 = uVar7;
      if (iVar2 < 0) {
        *param_5 = 0;
        iVar2 = 0;
      }
      goto LAB_ram_43015f04;
    }
    uVar9 = bits->used_bits;
    uVar4 = bits->input_length;
    uVar6 = uVar9 >> 3;
    if (uVar6 < uVar4) {
      puVar10 = bits->buffer;
      uVar14 = 0;
LAB_ram_43015f2e:
      uVar3 = ((uint)puVar10[uVar6] << (uVar9 & 7)) >> 7 & 1;
      goto LAB_ram_43015f44;
    }
    bits->used_bits = uVar9 + 1;
    uVar9 = uVar7 & 0x1f;
    uVar14 = 0;
    uVar3 = 0;
  }
  else {
    uVar9 = bits->used_bits;
    uVar4 = bits->input_length;
    puVar10 = bits->buffer;
    uVar14 = 0;
    if (uVar9 >> 3 < uVar4) {
      bVar1 = puVar10[uVar9 >> 3];
      bits->used_bits = uVar9 + 1;
      uVar14 = ((uint)bVar1 << (uVar9 & 7)) >> 7 & 1;
    }
    else {
      bits->used_bits = uVar9 + 1;
    }
    if (uVar7 == 0) {
      uVar9 = 0;
      uVar3 = 0;
    }
    else {
      uVar9 = uVar9 + 1;
      uVar3 = 0;
      uVar6 = uVar9 >> 3;
      if (uVar6 < uVar4) goto LAB_ram_43015f2e;
LAB_ram_43015f44:
      bits->used_bits = uVar9 + 1;
      uVar9 = uVar7 & 0x1f;
    }
    if ((uVar12 & 0x1f) == 0x10) {
      uVar15 = bits->used_bits;
      uVar13 = uVar15;
      do {
        uVar6 = uVar13;
        uVar13 = uVar6 + 1;
        if (uVar4 <= uVar6 >> 3) {
          bits->used_bits = uVar13;
          break;
        }
        bVar1 = puVar10[uVar6 >> 3];
        bits->used_bits = uVar13;
      } while (((uint)bVar1 << (uVar6 & 7) & 0x80) != 0);
      uVar4 = uVar4 - (uVar13 >> 3);
      uVar6 = (uVar6 - uVar15) + 4;
      pbVar11 = puVar10 + (uVar13 >> 3);
      if (uVar4 < 4) {
        if (uVar4 == 2) {
          uVar4 = 0;
LAB_ram_4301617a:
          uVar4 = (uint)pbVar11[1] << 0x10 | uVar4;
        }
        else {
          if (uVar4 == 3) {
            uVar4 = (uint)pbVar11[2] << 8;
            goto LAB_ram_4301617a;
          }
          if (uVar4 != 1) {
            uVar4 = 0;
            goto LAB_ram_4301611a;
          }
          uVar4 = 0;
        }
        uVar4 = (((uint)*pbVar11 << 0x18 | uVar4) << (uVar13 & 7)) >> (0x20 - uVar6 & 0x1f);
      }
      else {
        uVar4 = (((uint)*pbVar11 << 0x18 | (uint)pbVar11[1] << 0x10 | (uint)pbVar11[3] |
                 (uint)pbVar11[2] << 8) << (uVar13 & 7)) >> (0x20 - uVar6 & 0x1f);
      }
LAB_ram_4301611a:
      bits->used_bits = uVar6 + uVar13;
      uVar12 = (int)(((1 << (uVar6 & 0x1f)) + uVar4) * uVar12) >> 4;
    }
  }
  iVar2 = ((int)uVar12 >> 0x1f ^ uVar12) - ((int)uVar12 >> 0x1f);
  if (uVar14 != 0) {
    uVar12 = -uVar12;
  }
  iVar5 = *param_5;
  *param_1 = (short)uVar12;
  if (iVar5 < iVar2) {
    *param_5 = iVar2;
  }
  if (uVar9 == 0x10) {
    uVar15 = bits->used_bits;
    uVar13 = uVar15;
    do {
      uVar12 = uVar13;
      uVar13 = uVar12 + 1;
      if (bits->input_length <= uVar12 >> 3) {
        bits->used_bits = uVar13;
        break;
      }
      bVar1 = bits->buffer[uVar12 >> 3];
      bits->used_bits = uVar13;
    } while (((uint)bVar1 << (uVar12 & 7) & 0x80) != 0);
    uVar12 = (uVar12 - uVar15) + 4;
    uVar14 = bits->input_length - (uVar13 >> 3);
    pbVar11 = bits->buffer + (uVar13 >> 3);
    if (uVar14 < 4) {
      if (uVar14 == 2) {
        uVar14 = 0;
LAB_ram_43016190:
        uVar14 = (uint)pbVar11[1] << 0x10 | uVar14;
      }
      else {
        if (uVar14 == 3) {
          uVar14 = (uint)pbVar11[2] << 8;
          goto LAB_ram_43016190;
        }
        if (uVar14 != 1) {
          uVar14 = 0;
          goto LAB_ram_430160d8;
        }
        uVar14 = 0;
      }
      uVar14 = (((uint)*pbVar11 << 0x18 | uVar14) << (uVar13 & 7)) >> (0x20 - uVar12 & 0x1f);
    }
    else {
      uVar14 = (((uint)*pbVar11 << 0x18 | (uint)pbVar11[1] << 0x10 | (uint)pbVar11[3] |
                (uint)pbVar11[2] << 8) << (uVar13 & 7)) >> (0x20 - uVar12 & 0x1f);
    }
LAB_ram_430160d8:
    bits->used_bits = uVar12 + uVar13;
    uVar7 = (int)(((1 << (uVar12 & 0x1f)) + uVar14) * uVar7) >> 4;
  }
  if (uVar3 == 0) {
    iVar2 = *param_5;
    uVar12 = uVar7;
  }
  else {
    iVar2 = *param_5;
    uVar12 = -uVar7;
  }
LAB_ram_43015f04:
  param_1[1] = (short)uVar12;
  iVar5 = (uVar7 ^ (int)uVar7 >> 0x1f) - ((int)uVar7 >> 0x1f);
  if (iVar2 < iVar5) {
    *param_5 = iVar5;
  }
  return;
}
