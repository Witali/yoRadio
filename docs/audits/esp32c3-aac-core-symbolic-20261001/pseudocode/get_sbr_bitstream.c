/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: get_sbr_bitstream @ ram:430082ea
 * Types and parameter counts are inferred; verify against disassembly. */

void get_sbr_bitstream(aac_analysis_sbr_stream_t *stream,aac_analysis_bits_t *bits)

{
  ushort uVar1;
  uint uVar2;
  uint uVar3;
  uint8_t *puVar4;
  uint8_t *puVar5;
  uint uVar6;
  uint8_t uVar7;
  uint uVar8;
  uint32_t uVar9;
  uint uVar10;
  int iVar11;

  gp = &__global_pointer_;
  uVar3 = bits->used_bits;
  uVar9 = bits->input_length;
  puVar5 = bits->buffer;
  uVar10 = uVar9 - (uVar3 >> 3);
  uVar6 = uVar3 + 4;
  if (uVar10 < 2) {
    if (uVar10 == 1) {
      uVar10 = (uint)(byte)*(ushort *)(puVar5 + (uVar3 >> 3)) << 8;
      goto LAB_ram_43008318;
    }
    bits->used_bits = uVar6;
    uVar10 = 0;
  }
  else {
    uVar1 = *(ushort *)(puVar5 + (uVar3 >> 3));
    uVar10 = (uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 & 0xffff;
LAB_ram_43008318:
    bits->used_bits = uVar6;
    uVar10 = (uVar10 << (uVar3 & 7)) >> 0xc & 0xf;
    if (uVar10 == 0xf) {
      uVar8 = uVar9 - (uVar6 >> 3);
      if (uVar8 < 2) {
        uVar10 = 0xe;
        if (uVar8 == 1) {
          uVar10 = ((((uint)(byte)*(ushort *)(puVar5 + (uVar6 >> 3)) << 8) << (uVar6 & 7)) >> 8 &
                   0xff) + 0xe;
        }
      }
      else {
        uVar1 = *(ushort *)(puVar5 + (uVar6 >> 3));
        uVar10 = ((((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 << (uVar6 & 7)) << 0x10) >> 0x18) + 0xe
        ;
      }
      uVar6 = uVar3 + 0xc;
      bits->used_bits = uVar6;
    }
  }
  uVar3 = uVar9 - (uVar6 >> 3);
  if (uVar3 < 2) {
    if (uVar3 != 1) goto LAB_ram_43008376;
    uVar3 = (uint)(byte)*(ushort *)(puVar5 + (uVar6 >> 3)) << 8;
  }
  else {
    uVar1 = *(ushort *)(puVar5 + (uVar6 >> 3));
    uVar3 = (uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 & 0xffff;
  }
  uVar8 = (uVar3 << (uVar6 & 7)) >> 0xc & 0xf;
  uVar3 = uVar6 + 4;
  bits->used_bits = uVar3;
  if (((uVar8 - 0xd < 2) && (uVar10 != 0)) && (iVar11 = stream->elements, iVar11 < 1)) {
    uVar2 = uVar9 - (uVar3 >> 3);
    stream->element[iVar11].extension_type = uVar8;
    stream->element[iVar11].payload_bytes = uVar10;
    if (uVar2 < 2) {
      uVar7 = 0;
      if (uVar2 == 1) {
        uVar7 = (byte)((((uint)(byte)*(ushort *)(puVar5 + (uVar3 >> 3)) << 8) << (uVar3 & 7)) >> 0xc
                      ) & 0xf;
      }
    }
    else {
      uVar1 = *(ushort *)(puVar5 + (uVar3 >> 3));
      uVar7 = (byte)(((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 << (uVar3 & 7)) >> 8) >> 4;
    }
    uVar3 = uVar6 + 8;
    bits->used_bits = uVar3;
    stream->element[iVar11].payload[0] = uVar7;
    if (uVar10 != 1) {
      puVar4 = stream->element[iVar11].payload;
      do {
        puVar4 = puVar4 + 1;
        uVar8 = uVar9 - (uVar3 >> 3);
        if (uVar8 < 2) {
          uVar7 = 0;
          if (uVar8 == 1) {
            uVar7 = (uint8_t)((((uint)(byte)*(ushort *)(puVar5 + (uVar3 >> 3)) << 8) << (uVar3 & 7))
                             >> 8);
          }
        }
        else {
          uVar1 = *(ushort *)(puVar5 + (uVar3 >> 3));
          uVar7 = (uint8_t)(((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 << (uVar3 & 7)) >> 8);
        }
        uVar3 = uVar3 + 8;
        bits->used_bits = uVar3;
        *puVar4 = uVar7;
      } while (uVar3 != uVar10 * 8 + uVar6);
    }
    stream->elements = iVar11 + 1;
    return;
  }
LAB_ram_43008376:
  bits->used_bits = uVar10 * 8 + uVar6;
  return;
}
