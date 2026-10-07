/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: unpack_idx_sgn @ ram:43015cd6
 * Types and parameter counts are inferred; verify against disassembly. */

void unpack_idx_sgn(undefined2 *param_1,int param_2,aac_analysis_codebook_t *book,
                   aac_analysis_bits_t *bits,int *param_5)

{
  byte bVar1;
  uint uVar2;
  undefined2 *puVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  int iVar10;

  gp = &__global_pointer_;
  iVar8 = book->modulus;
  iVar5 = book->offset;
  puVar3 = param_1;
  if (book->dimensions == 4) {
    iVar7 = param_2 * 0x13 >> 9;
    uVar9 = iVar7 - iVar5;
    iVar10 = iVar7 * -0x1b + param_2;
    if (iVar7 == iVar5) {
      *param_1 = 0;
    }
    else {
      uVar6 = bits->used_bits;
      uVar2 = uVar9;
      if (uVar6 >> 3 < bits->input_length) {
        bVar1 = bits->buffer[uVar6 >> 3];
        bits->used_bits = uVar6 + 1;
        if (((uint)bVar1 << (uVar6 & 7) & 0x80) != 0) {
          uVar2 = -uVar9;
        }
      }
      else {
        bits->used_bits = uVar6 + 1;
      }
      iVar4 = *param_5;
      *param_1 = (short)uVar2;
      iVar7 = ((int)uVar9 >> 0x1f ^ uVar9) - ((int)uVar9 >> 0x1f);
      if (iVar4 < iVar7) {
        *param_5 = iVar7;
      }
    }
    iVar7 = iVar10 * 0x39 >> 9;
    param_2 = iVar10 + iVar7 * -9;
    puVar3 = param_1 + 2;
    uVar9 = iVar7 - iVar5;
    if (iVar7 == iVar5) {
      param_1[1] = 0;
    }
    else {
      uVar6 = bits->used_bits;
      uVar2 = uVar9;
      if (uVar6 >> 3 < bits->input_length) {
        bVar1 = bits->buffer[uVar6 >> 3];
        bits->used_bits = uVar6 + 1;
        if (((uint)bVar1 << (uVar6 & 7) & 0x80) != 0) {
          uVar2 = -uVar9;
        }
      }
      else {
        bits->used_bits = uVar6 + 1;
      }
      iVar10 = *param_5;
      param_1[1] = (short)uVar2;
      iVar7 = ((int)uVar9 >> 0x1f ^ uVar9) - ((int)uVar9 >> 0x1f);
      if (iVar10 < iVar7) {
        *param_5 = iVar7;
      }
    }
  }
  iVar7 = param_2 * *(int *)(div_mod + iVar8 * 4) >> 0xd;
  uVar9 = iVar7 - iVar5;
  iVar8 = param_2 - iVar8 * iVar7;
  if (iVar7 == iVar5) {
    *puVar3 = 0;
  }
  else {
    uVar6 = bits->used_bits;
    uVar2 = uVar9;
    if (uVar6 >> 3 < bits->input_length) {
      bVar1 = bits->buffer[uVar6 >> 3];
      bits->used_bits = uVar6 + 1;
      if (((uint)bVar1 << (uVar6 & 7) & 0x80) != 0) {
        uVar2 = -uVar9;
      }
    }
    else {
      bits->used_bits = uVar6 + 1;
    }
    iVar7 = *param_5;
    *puVar3 = (short)uVar2;
    iVar10 = ((int)uVar9 >> 0x1f ^ uVar9) - ((int)uVar9 >> 0x1f);
    if (iVar7 < iVar10) {
      *param_5 = iVar10;
    }
  }
  uVar9 = iVar8 - iVar5;
  if (iVar8 == iVar5) {
    puVar3[1] = 0;
  }
  else {
    uVar6 = bits->used_bits;
    uVar2 = uVar9;
    if (uVar6 >> 3 < bits->input_length) {
      bVar1 = bits->buffer[uVar6 >> 3];
      bits->used_bits = uVar6 + 1;
      if (((uint)bVar1 << (uVar6 & 7) & 0x80) != 0) {
        uVar2 = -uVar9;
      }
    }
    else {
      bits->used_bits = uVar6 + 1;
    }
    iVar5 = *param_5;
    puVar3[1] = (short)uVar2;
    iVar8 = (uVar9 ^ (int)uVar9 >> 0x1f) - ((int)uVar9 >> 0x1f);
    if (iVar5 < iVar8) {
      *param_5 = iVar8;
      return;
    }
  }
  return;
}
