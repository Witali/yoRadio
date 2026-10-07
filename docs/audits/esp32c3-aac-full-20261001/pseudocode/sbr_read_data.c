/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_read_data @ ram:4301356c
 * Types and parameter counts are inferred; verify against disassembly. */

int sbr_read_data(int param_1,undefined4 param_2,int param_3)

{
  undefined4 *puVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  undefined4 *puVar6;
  undefined4 uVar7;
  int aiStack_34 [8];

  gp = &__global_pointer_;
  aiStack_34[4] = *(int *)(param_3 + 0x10) << 3;
  aiStack_34[0] = param_3 + 0x14;
  aiStack_34[2] = 0;
  aiStack_34[1] = 0;
  aiStack_34[3] = 0;
  buf_getbits(aiStack_34,4);
  if ((*(int *)(param_3 + 0xc) == 0xe) &&
     (iVar3 = sbr_crc_check(aiStack_34,*(int *)(param_3 + 0x10) * 8 + -0xe), iVar3 == 0)) {
    iVar3 = 0;
    goto LAB_ram_430135bc;
  }
  iVar3 = buf_getbits(aiStack_34,1);
  if (iVar3 == 0) {
    if (*(int *)(param_3 + 8) == 0) {
LAB_ram_43013680:
      if (*(int *)(param_1 + 4) != 2) {
        iVar3 = 0;
        goto LAB_ram_430135bc;
      }
LAB_ram_430136c8:
      iVar3 = sbr_get_sce(param_1 + 8,aiStack_34,*(undefined4 *)(param_1 + 0xc984));
      goto LAB_ram_430135bc;
    }
    if (*(int *)(param_3 + 8) == 1) {
LAB_ram_4301365e:
      iVar3 = 0;
LAB_ram_43013660:
      if (*(int *)(param_1 + 4) == 2) {
        iVar3 = sbr_get_cpe(param_1 + 8,param_1 + 0x64c8,aiStack_34);
      }
      goto LAB_ram_430135bc;
    }
  }
  else {
    iVar3 = sbr_get_header_data(param_1 + 200,aiStack_34,*(undefined4 *)(param_1 + 4));
    if (*(int *)(param_3 + 8) == 0) {
      if (iVar3 != 1) goto LAB_ram_43013680;
      iVar3 = sbr_reset_dec(param_1 + 8,param_2,*(undefined4 *)(param_1 + 0xd4));
      if (iVar3 != 0) goto LAB_ram_430135bc;
      *(undefined4 *)(param_1 + 4) = 2;
      goto LAB_ram_430136c8;
    }
    if (*(int *)(param_3 + 8) == 1) {
      puVar6 = (undefined4 *)(param_1 + 200);
      puVar5 = (undefined4 *)(param_1 + 0x6588);
      do {
        uVar7 = *puVar6;
        uVar4 = puVar6[1];
        puVar5[2] = puVar6[2];
        *puVar5 = uVar7;
        puVar5[1] = uVar4;
        puVar1 = puVar6 + 3;
        puVar6 = puVar6 + 4;
        puVar5[3] = *puVar1;
        puVar5 = puVar5 + 4;
      } while (puVar6 != (undefined4 *)(param_1 + 0x108));
      if (iVar3 == 1) {
        iVar2 = param_1 + 8;
        do {
          iVar3 = sbr_reset_dec(iVar2,param_2,*(undefined4 *)(param_1 + 0xd4));
          if (iVar3 != 0) goto LAB_ram_43013660;
          *(undefined4 *)(iVar2 + -4) = 2;
          iVar2 = iVar2 + 0x64c0;
        } while (param_1 + 0xc988 != iVar2);
      }
      goto LAB_ram_4301365e;
    }
  }
  iVar3 = 10;
LAB_ram_430135bc:
  if ((uint)aiStack_34[4] < (-aiStack_34[3] & 7U) + aiStack_34[3]) {
    iVar3 = 0xe;
  }
  return iVar3;
}
