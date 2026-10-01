/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: get_adts_header @ ram:4300756a
 * Types and parameter counts are inferred; verify against disassembly. */

void get_adts_header(undefined4 *param_1,uint *param_2,int *param_3,int param_4)

{
  byte bVar1;
  uint uVar2;
  uint uVar3;
  uint *puVar4;
  byte *pbVar5;
  uint uVar6;
  int iVar7;
  uint uVar8;
  int iVar9;
  uint uVar10;

  gp = &__global_pointer_;
  iVar7 = *param_3;
  while (param_4 < iVar7) {
    iVar7 = find_adts_syncword(param_2,param_1 + 6,0x1c,0xfffffff);
    if (iVar7 == 0) {
      puVar4 = (uint *)param_1[0xb];
      iVar7 = param_1[6];
      uVar6 = puVar4[0xd5];
      goto LAB_ram_430075cc;
    }
    param_1[7] = 0;
    *param_1 = 0;
    param_1[0x229a] = 0;
    iVar7 = *param_3;
  }
  *param_2 = 0x7ff8;
  iVar9 = find_adts_syncword(param_2,param_1 + 6,0xf,0x7ffb);
  uVar6 = param_1[7];
  iVar7 = param_1[6];
  uVar3 = param_1[9] - (uVar6 >> 3);
  pbVar5 = (byte *)((uVar6 >> 3) + iVar7);
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
    param_1[7] = uVar6 + 0xd;
    puVar4 = (uint *)param_1[0xb];
    *param_2 = uVar3 << 0xd;
    puVar4[0xd5] = 0;
    *puVar4 = 0;
    puVar4[1] = 0;
    uVar8 = 0;
    uVar10 = 0;
    uVar6 = 0;
LAB_ram_430077aa:
    uVar8 = uVar8 - (uVar8 != 0);
    puVar4[0x14] = 0;
    puVar4[0xc9] = 0;
    puVar4[0xcc] = 0;
    puVar4[0xcf] = 0;
    puVar4[4] = uVar8;
    puVar4[3] = 1;
    if (iVar9 != 0) goto LAB_ram_430076ea;
    iVar9 = set_mc_info(param_1 + 0x23,uVar10,0,uVar8,param_1 + 0x1e,param_1 + 0xc);
    puVar4 = (uint *)param_1[0xb];
    iVar7 = param_1[6];
    uVar6 = puVar4[0xd5];
    if (iVar9 != 0) goto LAB_ram_430076ea;
    *param_3 = *param_3 + 1;
LAB_ram_430075cc:
    uVar3 = param_1[7];
    iVar9 = param_1[9];
    uVar8 = iVar9 - (uVar3 >> 3);
    uVar10 = uVar3 & 7;
    pbVar5 = (byte *)((uVar3 >> 3) + iVar7);
    if (3 < uVar8) goto LAB_ram_430075e6;
LAB_ram_43007708:
    if (uVar8 == 2) {
      uVar8 = 0;
LAB_ram_43007850:
      uVar8 = (uint)pbVar5[1] << 0x10 | uVar8;
    }
    else {
      if (uVar8 == 3) {
        uVar8 = (uint)pbVar5[2] << 8;
        goto LAB_ram_43007850;
      }
      if (uVar8 != 1) {
        uVar8 = 0;
        uVar10 = 0;
        goto LAB_ram_43007618;
      }
      uVar8 = 0;
    }
    bVar1 = *pbVar5;
    uVar2 = uVar3 + 0x1c;
    param_1[7] = uVar2;
    puVar4[0xd4] = ((((uint)bVar1 << 0x18 | uVar8) << uVar10) << 2) >> 0x13;
    puVar4[0xd3] = 0;
  }
  else {
    uVar3 = (uint)*pbVar5 << 0x18 | (uint)pbVar5[1] << 0x10 | (uint)pbVar5[3] | (uint)pbVar5[2] << 8
    ;
LAB_ram_43007690:
    uVar10 = *param_2;
    uVar3 = uVar3 << (uVar6 & 7);
    puVar4 = (uint *)param_1[0xb];
    param_1[7] = uVar6 + 0xd;
    *param_2 = uVar10 << 0xd | uVar3 >> 0x13;
    uVar10 = uVar3 >> 0x19 & 0xf;
    uVar6 = uVar3 >> 0x1f;
    uVar8 = uVar3 >> 0x15 & 7;
    puVar4[0xd5] = uVar6;
    *puVar4 = uVar3 >> 0x1d & 3;
    puVar4[1] = uVar10;
    if (uVar8 < 3) goto LAB_ram_430077aa;
    puVar4[4] = uVar8 - 1;
    puVar4[0x14] = 0;
    puVar4[0xc9] = 0;
    puVar4[0xcc] = 0;
    puVar4[0xcf] = 0;
    puVar4[3] = 1;
LAB_ram_430076ea:
    *param_3 = 0;
    uVar3 = param_1[7];
    iVar9 = param_1[9];
    uVar8 = iVar9 - (uVar3 >> 3);
    uVar10 = uVar3 & 7;
    pbVar5 = (byte *)((uVar3 >> 3) + iVar7);
    if (uVar8 < 4) goto LAB_ram_43007708;
LAB_ram_430075e6:
    uVar10 = ((uint)*pbVar5 << 0x18 | (uint)pbVar5[1] << 0x10 | (uint)pbVar5[3] |
             (uint)pbVar5[2] << 8) << uVar10;
    uVar8 = uVar10 >> 4 & 3;
    uVar10 = (uVar10 << 2) >> 0x13;
LAB_ram_43007618:
    uVar2 = uVar3 + 0x1c;
    param_1[7] = uVar2;
    puVar4[0xd4] = uVar10;
    puVar4[0xd3] = uVar8;
  }
  if (uVar6 != 0) {
    return;
  }
  uVar6 = iVar9 - (uVar2 >> 3);
  pbVar5 = (byte *)((uVar2 >> 3) + iVar7);
  if (3 < uVar6) {
    uVar6 = (((uint)*pbVar5 << 0x18 | (uint)pbVar5[1] << 0x10 | (uint)pbVar5[3] |
             (uint)pbVar5[2] << 8) << (uVar2 & 7)) >> 0x10;
    goto LAB_ram_4300781a;
  }
  if (uVar6 == 2) {
    uVar6 = 0;
LAB_ram_43007876:
    uVar6 = (uint)pbVar5[1] << 0x10 | uVar6;
  }
  else {
    if (uVar6 == 3) {
      uVar6 = (uint)pbVar5[2] << 8;
      goto LAB_ram_43007876;
    }
    if (uVar6 != 1) {
      uVar6 = 0;
      goto LAB_ram_4300781a;
    }
    uVar6 = 0;
  }
  uVar6 = (((uint)*pbVar5 << 0x18 | uVar6) << (uVar2 & 7)) >> 0x10;
LAB_ram_4300781a:
  param_1[7] = uVar3 + 0x2c;
  puVar4[0xd6] = uVar6;
  return;
}
