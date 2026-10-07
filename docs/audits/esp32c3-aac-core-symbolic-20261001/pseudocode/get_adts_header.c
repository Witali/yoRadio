/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: get_adts_header @ ram:4300756a
 * Types and parameter counts are inferred; verify against disassembly. */

void get_adts_header(aac_analysis_core_t *core,uint *param_2,int *param_3,int param_4)

{
  byte bVar1;
  uint uVar2;
  uint uVar3;
  aac_analysis_program_t *paVar4;
  byte *pbVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  uint uVar9;
  uint8_t *puVar10;
  uint32_t uVar11;
  uint uVar12;

  gp = &__global_pointer_;
  iVar8 = *param_3;
  while (param_4 < iVar8) {
    iVar8 = find_adts_syncword(param_2,&core->input,0x1c,0xfffffff);
    if (iVar8 == 0) {
      paVar4 = core->program;
      puVar10 = (core->input).buffer;
      uVar7 = paVar4->crc_absent;
      goto LAB_ram_430075cc;
    }
    (core->input).used_bits = 0;
    core->frame_number = 0;
    core->invoke = 0;
    iVar8 = *param_3;
  }
  *param_2 = 0x7ff8;
  iVar8 = find_adts_syncword(param_2,&core->input,0xf,0x7ffb);
  uVar7 = (core->input).used_bits;
  puVar10 = (core->input).buffer;
  uVar3 = (core->input).input_length - (uVar7 >> 3);
  pbVar5 = puVar10 + (uVar7 >> 3);
  if (uVar3 < 4) {
    if (uVar3 == 2) {
      uVar3 = 0;
LAB_ram_43007838:
      uVar3 = (uint)pbVar5[1] << 0x10 | uVar3;
LAB_ram_43007840:
      uVar3 = (uint)*pbVar5 << 0x18 | uVar3;
      goto LAB_ram_43007690;
    }
    if (uVar3 == 3) {
      uVar3 = (uint)pbVar5[2] << 8;
      goto LAB_ram_43007838;
    }
    if (uVar3 == 1) {
      uVar3 = 0;
      goto LAB_ram_43007840;
    }
    uVar3 = *param_2;
    (core->input).used_bits = uVar7 + 0xd;
    paVar4 = core->program;
    *param_2 = uVar3 << 0xd;
    paVar4->crc_absent = 0;
    paVar4->profile = 0;
    paVar4->sample_rate_index = 0;
    uVar9 = 0;
    uVar12 = 0;
    uVar7 = 0;
LAB_ram_430077aa:
    iVar6 = uVar9 - (uVar9 != 0);
    (paVar4->front).tag[0] = 0;
    (paVar4->mono).present = 0;
    (paVar4->stereo).present = 0;
    (paVar4->matrix).present = 0;
    (paVar4->front).is_pair[0] = iVar6;
    (paVar4->front).count = 1;
    if (iVar8 != 0) goto LAB_ram_430076ea;
    iVar8 = set_mc_info(&core->mc,uVar12,0,iVar6,core->window_map,core->short_band_width);
    paVar4 = core->program;
    puVar10 = (core->input).buffer;
    uVar7 = paVar4->crc_absent;
    if (iVar8 != 0) goto LAB_ram_430076ea;
    *param_3 = *param_3 + 1;
LAB_ram_430075cc:
    uVar3 = (core->input).used_bits;
    uVar11 = (core->input).input_length;
    uVar9 = uVar11 - (uVar3 >> 3);
    uVar12 = uVar3 & 7;
    pbVar5 = puVar10 + (uVar3 >> 3);
    if (3 < uVar9) goto LAB_ram_430075e6;
LAB_ram_43007708:
    if (uVar9 == 2) {
      uVar9 = 0;
LAB_ram_43007850:
      uVar9 = (uint)pbVar5[1] << 0x10 | uVar9;
    }
    else {
      if (uVar9 == 3) {
        uVar9 = (uint)pbVar5[2] << 8;
        goto LAB_ram_43007850;
      }
      if (uVar9 != 1) {
        uVar9 = 0;
        uVar12 = 0;
        goto LAB_ram_43007618;
      }
      uVar9 = 0;
    }
    bVar1 = *pbVar5;
    uVar2 = uVar3 + 0x1c;
    (core->input).used_bits = uVar2;
    paVar4->frame_length = ((((uint)bVar1 << 0x18 | uVar9) << uVar12) << 2) >> 0x13;
    paVar4->headerless_frames = 0;
  }
  else {
    uVar3 = (uint)*pbVar5 << 0x18 | (uint)pbVar5[1] << 0x10 | (uint)pbVar5[3] | (uint)pbVar5[2] << 8
    ;
LAB_ram_43007690:
    uVar12 = *param_2;
    uVar3 = uVar3 << (uVar7 & 7);
    paVar4 = core->program;
    (core->input).used_bits = uVar7 + 0xd;
    *param_2 = uVar12 << 0xd | uVar3 >> 0x13;
    uVar12 = uVar3 >> 0x19 & 0xf;
    uVar7 = uVar3 >> 0x1f;
    uVar9 = uVar3 >> 0x15 & 7;
    paVar4->crc_absent = uVar7;
    paVar4->profile = uVar3 >> 0x1d & 3;
    paVar4->sample_rate_index = uVar12;
    if (uVar9 < 3) goto LAB_ram_430077aa;
    (paVar4->front).is_pair[0] = uVar9 - 1;
    (paVar4->front).tag[0] = 0;
    (paVar4->mono).present = 0;
    (paVar4->stereo).present = 0;
    (paVar4->matrix).present = 0;
    (paVar4->front).count = 1;
LAB_ram_430076ea:
    *param_3 = 0;
    uVar3 = (core->input).used_bits;
    uVar11 = (core->input).input_length;
    uVar9 = uVar11 - (uVar3 >> 3);
    uVar12 = uVar3 & 7;
    pbVar5 = puVar10 + (uVar3 >> 3);
    if (uVar9 < 4) goto LAB_ram_43007708;
LAB_ram_430075e6:
    uVar12 = ((uint)*pbVar5 << 0x18 | (uint)pbVar5[1] << 0x10 | (uint)pbVar5[3] |
             (uint)pbVar5[2] << 8) << uVar12;
    uVar9 = uVar12 >> 4 & 3;
    uVar12 = (uVar12 << 2) >> 0x13;
LAB_ram_43007618:
    uVar2 = uVar3 + 0x1c;
    (core->input).used_bits = uVar2;
    paVar4->frame_length = uVar12;
    paVar4->headerless_frames = uVar9;
  }
  if (uVar7 != 0) {
    return;
  }
  uVar7 = uVar11 - (uVar2 >> 3);
  pbVar5 = puVar10 + (uVar2 >> 3);
  if (3 < uVar7) {
    uVar11 = (((uint)*pbVar5 << 0x18 | (uint)pbVar5[1] << 0x10 | (uint)pbVar5[3] |
              (uint)pbVar5[2] << 8) << (uVar2 & 7)) >> 0x10;
    goto LAB_ram_4300781a;
  }
  if (uVar7 == 2) {
    uVar7 = 0;
LAB_ram_43007876:
    uVar7 = (uint)pbVar5[1] << 0x10 | uVar7;
  }
  else {
    if (uVar7 == 3) {
      uVar7 = (uint)pbVar5[2] << 8;
      goto LAB_ram_43007876;
    }
    if (uVar7 != 1) {
      uVar11 = 0;
      goto LAB_ram_4300781a;
    }
    uVar7 = 0;
  }
  uVar11 = (((uint)*pbVar5 << 0x18 | uVar7) << (uVar2 & 7)) >> 0x10;
LAB_ram_4300781a:
  (core->input).used_bits = uVar3 + 0x2c;
  paVar4->crc = uVar11;
  return;
}
