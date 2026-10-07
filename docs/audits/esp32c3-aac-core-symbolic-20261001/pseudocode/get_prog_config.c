/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: get_prog_config @ ram:43007c52
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4 get_prog_config(aac_analysis_core_t *core,aac_analysis_program_t *program)

{
  byte bVar1;
  ushort uVar2;
  aac_analysis_elements_t *paVar3;
  aac_analysis_bits_t *bits;
  undefined4 uVar4;
  int32_t iVar5;
  aac_analysis_program_t *paVar6;
  uint uVar7;
  int32_t iVar8;
  uint8_t *puVar9;
  int32_t iVar10;
  int iVar11;
  uint uVar12;
  uint uVar13;
  aac_analysis_program_t **ppaVar14;
  uint uVar15;
  uint uVar16;
  uint uVar17;
  ushort *puVar18;
  int iVar19;
  uint uVar20;

  gp = &__global_pointer_;
  uVar13 = (core->input).used_bits;
  uVar12 = (core->input).input_length;
  puVar9 = (core->input).buffer;
  uVar17 = uVar12 - (uVar13 >> 3);
  uVar15 = uVar13 & 7;
  if (uVar17 < 2) {
    uVar16 = 0;
    if (uVar17 != 1) goto LAB_ram_43007c84;
    uVar2 = *(ushort *)(puVar9 + (uVar13 >> 3));
    uVar7 = uVar13 + 4;
    uVar20 = uVar12 - (uVar7 >> 3);
    (core->input).used_bits = uVar7;
    uVar16 = (((uint)(byte)uVar2 << 8) << uVar15) >> 0xc & 0xf;
    uVar17 = uVar7 & 7;
    puVar18 = (ushort *)(puVar9 + (uVar7 >> 3));
    if (1 < uVar20) goto LAB_ram_43007c9e;
LAB_ram_43007fc6:
    uVar7 = 0;
    if (uVar20 == 1) {
      uVar7 = (((uint)(byte)*puVar18 << 8) << uVar17) >> 0xe & 3;
    }
  }
  else {
    uVar2 = *(ushort *)(puVar9 + (uVar13 >> 3));
    uVar16 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << uVar15) << 0x10) >> 0x1c;
LAB_ram_43007c84:
    uVar7 = uVar13 + 4;
    uVar20 = uVar12 - (uVar7 >> 3);
    (core->input).used_bits = uVar7;
    uVar17 = uVar7 & 7;
    puVar18 = (ushort *)(puVar9 + (uVar7 >> 3));
    if (uVar20 < 2) goto LAB_ram_43007fc6;
LAB_ram_43007c9e:
    uVar7 = (((uint)(*puVar18 >> 8) + (uint)*puVar18 * 0x100 << uVar17) << 0x10) >> 0x1e;
  }
  uVar17 = uVar13 + 6;
  (core->input).used_bits = uVar17;
  program->profile = uVar7;
  uVar7 = uVar12 - (uVar17 >> 3);
  if (uVar7 < 2) {
    uVar20 = 0;
    if (uVar7 == 1) {
      uVar20 = (((uint)(byte)*(ushort *)(puVar9 + (uVar17 >> 3)) << 8) << (uVar17 & 7)) >> 0xc & 0xf
      ;
    }
  }
  else {
    uVar2 = *(ushort *)(puVar9 + (uVar17 >> 3));
    uVar20 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar17 & 7)) << 0x10) >> 0x1c;
  }
  iVar19 = core->adif_test;
  uVar17 = uVar13 + 10;
  (core->input).used_bits = uVar17;
  program->sample_rate_index = uVar20;
  if ((iVar19 == 0) && (core->program->sample_rate_index != uVar20)) {
    (core->input).used_bits = uVar13;
    return 1;
  }
  uVar7 = uVar12 - (uVar17 >> 3);
  bits = &core->input;
  if (uVar7 < 2) {
    uVar20 = 0;
    if (uVar7 == 1) {
      uVar20 = (((uint)(byte)*(ushort *)(puVar9 + (uVar17 >> 3)) << 8) << (uVar17 & 7)) >> 0xc & 0xf
      ;
    }
  }
  else {
    uVar2 = *(ushort *)(puVar9 + (uVar17 >> 3));
    uVar20 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar17 & 7)) << 0x10) >> 0x1c;
  }
  uVar17 = uVar13 + 0xe;
  (core->input).used_bits = uVar17;
  (program->front).count = uVar20;
  uVar7 = uVar12 - (uVar17 >> 3);
  if (uVar7 < 2) {
    uVar20 = 0;
    if (uVar7 == 1) {
      uVar20 = (((uint)(byte)*(ushort *)(puVar9 + (uVar17 >> 3)) << 8) << (uVar17 & 7)) >> 0xc & 0xf
      ;
    }
  }
  else {
    uVar2 = *(ushort *)(puVar9 + (uVar17 >> 3));
    uVar20 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar17 & 7)) << 0x10) >> 0x1c;
  }
  uVar17 = uVar13 + 0x12;
  (core->input).used_bits = uVar17;
  (program->side).count = uVar20;
  uVar7 = uVar12 - (uVar17 >> 3);
  if (uVar7 < 2) {
    uVar20 = 0;
    if (uVar7 == 1) {
      uVar20 = (((uint)(byte)*(ushort *)(puVar9 + (uVar17 >> 3)) << 8) << (uVar17 & 7)) >> 0xc & 0xf
      ;
    }
  }
  else {
    uVar2 = *(ushort *)(puVar9 + (uVar17 >> 3));
    uVar20 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar17 & 7)) << 0x10) >> 0x1c;
  }
  uVar17 = uVar13 + 0x16;
  (core->input).used_bits = uVar17;
  (program->back).count = uVar20;
  uVar7 = uVar12 - (uVar17 >> 3);
  if (uVar7 < 2) {
    uVar20 = 0;
    if (uVar7 == 1) {
      uVar20 = (((uint)(byte)*(ushort *)(puVar9 + (uVar17 >> 3)) << 8) << (uVar17 & 7)) >> 0xe & 3;
    }
  }
  else {
    uVar2 = *(ushort *)(puVar9 + (uVar17 >> 3));
    uVar20 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar17 & 7)) << 0x10) >> 0x1e;
  }
  (core->input).used_bits = uVar13 + 0x18;
  uVar17 = uVar13 + 0x18 >> 3;
  (program->lfe).count = uVar20;
  uVar7 = uVar12 - uVar17;
  if (uVar7 < 2) {
    uVar20 = 0;
    if (uVar7 == 1) {
      uVar20 = (uint)(byte)*(ushort *)(puVar9 + uVar17) << 8;
    }
  }
  else {
    uVar2 = *(ushort *)(puVar9 + uVar17);
    uVar20 = (uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 & 0xffff;
  }
  uVar17 = uVar13 + 0x1b;
  (core->input).used_bits = uVar17;
  (program->data).count = (uVar20 << uVar15) >> 0xd & 7;
  uVar7 = uVar12 - (uVar17 >> 3);
  if (uVar7 < 2) {
    uVar20 = 0;
    if (uVar7 == 1) {
      uVar20 = (((uint)(byte)*(ushort *)(puVar9 + (uVar17 >> 3)) << 8) << (uVar17 & 7)) >> 0xc & 0xf
      ;
    }
  }
  else {
    uVar2 = *(ushort *)(puVar9 + (uVar17 >> 3));
    uVar20 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar17 & 7)) << 0x10) >> 0x1c;
  }
  uVar7 = uVar13 + 0x1f;
  (core->input).used_bits = uVar7;
  (program->coupling).count = uVar20;
  uVar17 = uVar13 + 0x20;
  if (uVar7 >> 3 < uVar12) {
    bVar1 = puVar9[uVar7 >> 3];
    (core->input).used_bits = uVar17;
    uVar7 = ((uint)bVar1 << (uVar7 & 7)) >> 7 & 1;
    (program->mono).present = uVar7;
    if (uVar7 != 0) {
      uVar7 = uVar12 - (uVar17 >> 3);
      if (uVar7 < 2) {
        uVar20 = 0;
        if (uVar7 == 1) {
          uVar20 = (uint)(byte)*(ushort *)(puVar9 + (uVar17 >> 3)) << 8;
        }
      }
      else {
        uVar2 = *(ushort *)(puVar9 + (uVar17 >> 3));
        uVar20 = (uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 & 0xffff;
      }
      uVar17 = uVar13 + 0x24;
      (core->input).used_bits = uVar17;
      (program->mono).tag = (uVar20 << uVar15) >> 0xc & 0xf;
    }
  }
  else {
    (core->input).used_bits = uVar17;
    (program->mono).present = 0;
  }
  uVar13 = uVar17 + 1;
  if (uVar17 >> 3 < uVar12) {
    bVar1 = puVar9[uVar17 >> 3];
    (core->input).used_bits = uVar13;
    uVar15 = ((uint)bVar1 << (uVar17 & 7)) >> 7 & 1;
    (program->stereo).present = uVar15;
    if (uVar15 != 0) {
      uVar15 = uVar12 - (uVar13 >> 3);
      if (uVar15 < 2) {
        uVar7 = 0;
        if (uVar15 == 1) {
          uVar7 = (((uint)(byte)*(ushort *)(puVar9 + (uVar13 >> 3)) << 8) << (uVar13 & 7)) >> 0xc &
                  0xf;
        }
      }
      else {
        uVar2 = *(ushort *)(puVar9 + (uVar13 >> 3));
        uVar7 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar13 & 7)) << 0x10) >> 0x1c;
      }
      uVar13 = uVar17 + 5;
      (core->input).used_bits = uVar13;
      (program->stereo).tag = uVar7;
    }
  }
  else {
    (core->input).used_bits = uVar13;
    (program->stereo).present = 0;
  }
  uVar15 = uVar13 + 1;
  if (uVar13 >> 3 < uVar12) {
    bVar1 = puVar9[uVar13 >> 3];
    (core->input).used_bits = uVar15;
    uVar17 = ((uint)bVar1 << (uVar13 & 7)) >> 7 & 1;
    (program->matrix).present = uVar17;
    if (uVar17 != 0) {
      uVar17 = uVar12 - (uVar15 >> 3);
      if (uVar17 < 2) {
        uVar7 = 0;
        if (uVar17 == 1) {
          uVar7 = (((uint)(byte)*(ushort *)(puVar9 + (uVar15 >> 3)) << 8) << (uVar15 & 7)) >> 0xe &
                  3;
        }
      }
      else {
        uVar2 = *(ushort *)(puVar9 + (uVar15 >> 3));
        uVar7 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar15 & 7)) << 0x10) >> 0x1e;
      }
      uVar17 = uVar13 + 3;
      (core->input).used_bits = uVar17;
      (program->matrix).tag = uVar7;
      uVar15 = 0;
      if (uVar17 >> 3 < uVar12) {
        uVar15 = ((uint)puVar9[uVar17 >> 3] << (uVar17 & 7)) >> 7 & 1;
      }
      (core->input).used_bits = uVar13 + 4;
      (program->matrix).pseudo_surround = uVar15;
    }
  }
  else {
    (core->input).used_bits = uVar15;
    (program->matrix).present = 0;
  }
  get_ele_list(&program->front,bits,1);
  get_ele_list(&program->side,bits,1);
  get_ele_list(&program->back,bits,1);
  get_ele_list(&program->lfe,bits,0);
  get_ele_list(&program->data,bits,0);
  get_ele_list(&program->coupling,bits,1);
  byte_align(bits);
  uVar12 = (core->input).used_bits;
  uVar13 = (core->input).input_length - (uVar12 >> 3);
  puVar18 = (ushort *)((core->input).buffer + (uVar12 >> 3));
  if (uVar13 < 2) {
    if (uVar13 == 1) {
      uVar13 = (uint)(byte)*puVar18 << 8;
      goto LAB_ram_43007f48;
    }
  }
  else {
    uVar2 = *puVar18;
    uVar13 = (uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 & 0xffff;
LAB_ram_43007f48:
    uVar13 = (uVar13 << (uVar12 & 7)) >> 8 & 0xff;
    if (uVar13 != 0) {
      (core->input).used_bits = (uVar13 - 1) * 8 + uVar12 + 0x10;
      goto LAB_ram_43007f66;
    }
  }
  (core->input).used_bits = uVar12 + 8;
LAB_ram_43007f66:
  if (core->current_program < 0) {
    core->current_program = uVar16;
  }
  else if (uVar16 != core->current_program) {
    return 0;
  }
  paVar6 = program + 1;
  ppaVar14 = &core->program;
  do {
    iVar10 = (program->front).count;
    iVar5 = program->sample_rate_index;
    iVar8 = program->unidentified_word;
    *ppaVar14 = (aac_analysis_program_t *)program->profile;
    ppaVar14[1] = (aac_analysis_program_t *)iVar5;
    ppaVar14[2] = (aac_analysis_program_t *)iVar8;
    ppaVar14[3] = (aac_analysis_program_t *)iVar10;
    paVar3 = &program->front;
    program = (aac_analysis_program_t *)((program->front).is_pair + 1);
    ppaVar14[4] = (aac_analysis_program_t *)paVar3->is_pair[0];
    ppaVar14 = ppaVar14 + 5;
  } while (program != paVar6);
  paVar6 = core->program;
  iVar11 = (paVar6->front).is_pair[0];
  iVar5 = (paVar6->front).tag[0];
  iVar19 = paVar6->sample_rate_index;
  if ((core->mc).sample_rate_index != iVar19) {
    (core->mc).sample_rate_index = iVar19;
    iVar19 = infoinit(iVar19,core->window_map,core->short_band_width);
    uVar4 = 1;
    if (iVar19 == 0) {
      (core->mc).channel[0].tag = iVar5;
      (core->mc).channel[0].is_pair = iVar11;
      (core->mc).channels = iVar11 + 1;
      if (iVar11 != 0) {
        (core->mc).channel[1].is_pair = 1;
      }
      uVar4 = 0;
    }
    return uVar4;
  }
  (core->mc).channel[0].tag = iVar5;
  (core->mc).channel[0].is_pair = iVar11;
  (core->mc).channels = iVar11 + 1;
  if (iVar11 != 0) {
    (core->mc).channel[1].is_pair = 1;
  }
  return 0;
}
