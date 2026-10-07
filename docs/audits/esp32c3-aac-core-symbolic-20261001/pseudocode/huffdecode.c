/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: huffdecode @ ram:43009192
 * Types and parameter counts are inferred; verify against disassembly. */

int huffdecode(uint param_1,aac_analysis_bits_t *bits,aac_analysis_core_t *core,
              aac_analysis_core_channel_t **channels)

{
  byte bVar1;
  aac_analysis_channel_shared_t *tns;
  int iVar2;
  int32_t *piVar3;
  int iVar4;
  aac_analysis_core_channel_t *paVar5;
  uint uVar6;
  int32_t iVar7;
  int32_t iVar8;
  uint uVar9;
  int32_t iVar10;
  int32_t iVar11;
  uint32_t uVar12;
  int32_t iVar13;
  int32_t iVar14;
  aac_analysis_channel_shared_t *paVar15;

  gp = &__global_pointer_;
  uVar12 = bits->used_bits;
  uVar9 = uVar12 + 4;
  bits->used_bits = uVar9;
  uVar6 = (core->mc).channel[0].is_pair;
  if (param_1 == 1) {
    if (uVar9 >> 3 < bits->input_length) {
      bVar1 = bits->buffer[uVar9 >> 3];
      bits->used_bits = uVar12 + 5;
      if (uVar6 != 1) {
        if ((core->mc).implicit_channels == 0) {
          return 1;
        }
        (core->mc).channel[0].is_pair = 1;
        (core->mc).channels = 2;
      }
      paVar5 = *channels;
      uVar6 = ((uint)bVar1 << (uVar9 & 7)) >> 7 & 1;
      tns = (paVar5->spectrum).shared;
      if (uVar6 != 0) {
        paVar15 = (channels[1]->spectrum).shared;
        piVar3 = tns->groups;
        iVar2 = get_ics_info(bits,1,(uint *)&(paVar5->spectrum).window,
                             (uint *)&(paVar5->spectrum).current_shape,piVar3,(uint *)&tns->max_band
                             ,core->window_map,&tns->ltp,&paVar15->ltp);
        if (iVar2 != 0) {
          return iVar2;
        }
        paVar5 = channels[1];
        iVar7 = ((*channels)->spectrum).current_shape;
        iVar10 = tns->max_band;
        (paVar5->spectrum).window = ((*channels)->spectrum).window;
        (paVar5->spectrum).current_shape = iVar7;
        paVar15->max_band = iVar10;
        iVar7 = tns->groups[3];
        iVar10 = tns->groups[4];
        iVar8 = tns->groups[5];
        iVar11 = tns->groups[6];
        iVar14 = *piVar3;
        iVar13 = tns->groups[1];
        paVar15->groups[2] = tns->groups[2];
        paVar15->groups[3] = iVar7;
        paVar15->groups[4] = iVar10;
        paVar15->groups[0] = iVar14;
        paVar15->groups[1] = iVar13;
        paVar15->groups[5] = iVar8;
        paVar15->groups[6] = iVar11;
        paVar15->groups[7] = tns->groups[7];
        iVar2 = getmask(core->window_map[((*channels)->spectrum).window],bits,piVar3,tns->max_band,
                        (uint *)core->mask);
        core->has_mask = iVar2;
        if (iVar2 == 3) {
          return 1;
        }
        uVar9 = 2;
        tns = ((*channels)->spectrum).shared;
        goto LAB_ram_430091fc;
      }
    }
    else {
      bits->used_bits = uVar12 + 5;
      if (uVar6 == 1) {
        tns = ((*channels)->spectrum).shared;
      }
      else {
        if ((core->mc).implicit_channels == 0) {
          return 1;
        }
        tns = ((*channels)->spectrum).shared;
        (core->mc).channel[0].is_pair = 1;
        (core->mc).channels = 2;
      }
    }
    core->has_mask = 0;
    uVar6 = 0;
    uVar9 = 2;
  }
  else {
    if (uVar6 != param_1) {
      if ((core->mc).implicit_channels == 0) {
        return 1;
      }
      (core->mc).channel[0].is_pair = param_1 & 1;
      (core->mc).channels = (param_1 & 1) + 1;
      uVar6 = param_1;
    }
    if (uVar6 != 0) {
      return 0;
    }
    tns = ((*channels)->spectrum).shared;
    core->has_mask = 0;
    uVar6 = 0;
    uVar9 = 1;
  }
LAB_ram_430091fc:
  iVar2 = 0;
  while( true ) {
    iVar4 = getics(bits,uVar6,core,*channels,tns->groups,&tns->max_band,(uint *)tns->codebook,
                   &tns->tns,core->window_map,&(core->shared->spectral).pulse,
                   (core->shared->spectral).sections);
    channels = channels + 1;
    if ((uVar9 <= iVar2 + 1U) || (iVar4 != 0)) break;
    iVar2 = 1;
    tns = ((*channels)->spectrum).shared;
  }
  return iVar4;
}
