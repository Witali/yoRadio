/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: get_adif_header @ ram:430072f2
 * Types and parameter counts are inferred; verify against disassembly. */

int get_adif_header(aac_analysis_core_t *core,aac_analysis_adif_t *adif)

{
  ushort uVar1;
  uint uVar2;
  uint8_t *puVar3;
  uint uVar4;
  byte *pbVar5;
  uint uVar6;
  int iVar7;
  uint32_t uVar8;
  uint uVar9;
  aac_analysis_scratch_t *paVar10;
  uint uVar11;
  uint uVar12;

  gp = &__global_pointer_;
  uVar9 = (core->input).used_bits;
  uVar4 = (core->input).input_length;
  puVar3 = (core->input).buffer;
  uVar2 = uVar4 - (uVar9 >> 3);
  paVar10 = core->scratch;
  pbVar5 = puVar3 + (uVar9 >> 3);
  uVar11 = uVar9 & 7;
  if (uVar2 < 3) {
    if (uVar2 == 1) {
      uVar2 = 0;
    }
    else {
      uVar6 = 0;
      if (uVar2 != 2) goto LAB_ram_43007338;
      uVar2 = (uint)pbVar5[1] << 8;
    }
    uVar6 = (((uint)*pbVar5 << 0x10 | uVar2) << uVar11) << 8;
  }
  else {
    uVar6 = ((((uint)*pbVar5 << 0x10 | (uint)pbVar5[1] << 8 | (uint)pbVar5[2]) << uVar11) >> 8) <<
            0x10;
  }
LAB_ram_43007338:
  uVar2 = uVar9 + 0x10 >> 3;
  (core->input).used_bits = uVar9 + 0x10;
  uVar12 = uVar4 - uVar2;
  pbVar5 = puVar3 + uVar2;
  if (uVar12 < 3) {
    if (uVar12 == 1) {
      uVar2 = 0;
    }
    else {
      if (uVar12 != 2) goto LAB_ram_43007536;
      uVar2 = (uint)pbVar5[1] << 8;
    }
    uVar2 = (uint)*pbVar5 << 0x10 | uVar2;
  }
  else {
    uVar2 = (uint)*pbVar5 << 0x10 | (uint)pbVar5[1] << 8 | (uint)pbVar5[2];
  }
  (core->input).used_bits = uVar9 + 0x20;
  if ((uVar6 | ((uVar2 << uVar11) << 8) >> 0x10) != 0x41444946) {
LAB_ram_43007536:
    (core->input).used_bits = uVar9;
    return -1;
  }
  uVar2 = uVar9 + 0x20 >> 3;
  iVar7 = uVar9 + 0x21;
  if ((uVar2 < uVar4) && (((uint)puVar3[uVar2] << uVar11 & 0x80) != 0)) {
    iVar7 = uVar9 + 0x69;
  }
  uVar2 = iVar7 + 2;
  (core->input).used_bits = uVar2;
  uVar9 = 0;
  if (uVar2 >> 3 < uVar4) {
    uVar9 = (uint)puVar3[uVar2 >> 3] << (uVar2 & 7) & 0x80;
  }
  uVar2 = iVar7 + 3;
  uVar11 = uVar4 - (uVar2 >> 3);
  (core->input).used_bits = uVar2;
  pbVar5 = puVar3 + (uVar2 >> 3);
  if (3 < uVar11) {
    uVar2 = (((uint)*pbVar5 << 0x18 | (uint)pbVar5[1] << 0x10 | (uint)pbVar5[3] |
             (uint)pbVar5[2] << 8) << (uVar2 & 7)) >> 9;
    goto LAB_ram_4300741a;
  }
  if (uVar11 == 2) {
    uVar11 = 0;
LAB_ram_43007548:
    uVar11 = (uint)pbVar5[1] << 0x10 | uVar11;
  }
  else {
    if (uVar11 == 3) {
      uVar11 = (uint)pbVar5[2] << 8;
      goto LAB_ram_43007548;
    }
    if (uVar11 != 1) {
      uVar2 = 0;
      goto LAB_ram_4300741a;
    }
    uVar11 = 0;
  }
  uVar2 = (((uint)*pbVar5 << 0x18 | uVar11) << (uVar2 & 7)) >> 9;
LAB_ram_4300741a:
  uVar11 = iVar7 + 0x1a;
  (core->input).used_bits = uVar11;
  paVar10->words[9] = uVar2;
  uVar4 = uVar4 - (uVar11 >> 3);
  if (uVar4 < 2) {
    uVar2 = 0;
    if (uVar4 == 1) {
      uVar2 = (((uint)(byte)*(ushort *)(puVar3 + (uVar11 >> 3)) << 8) << (uVar11 & 7)) >> 0xc & 0xf;
    }
  }
  else {
    uVar1 = *(ushort *)(puVar3 + (uVar11 >> 3));
    uVar2 = (((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 << (uVar11 & 7)) << 0x10) >> 0x1c;
  }
  (core->input).used_bits = iVar7 + 0x1e;
  do {
    if (uVar9 == 0) {
      uVar8 = (core->input).used_bits;
      core->adif_test = 1;
      (core->input).used_bits = uVar8 + 0x14;
      iVar7 = get_prog_config(core,(aac_analysis_program_t *)adif);
    }
    else {
      core->adif_test = 1;
      iVar7 = get_prog_config(core,(aac_analysis_program_t *)adif);
    }
  } while ((uVar2 != 0) && (uVar2 = uVar2 - 1, iVar7 == 0));
  return iVar7;
}
