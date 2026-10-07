/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: getics @ ram:42058804
 * Types and parameter counts are inferred; verify against disassembly. */

int getics(int *param_1,int param_2,int param_3,int param_4,int *param_5,int *param_6,
          undefined4 *param_7,uint *param_8,int param_9,uint *param_10,undefined4 *param_11)

{
  byte bVar1;
  ushort uVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  undefined4 *puVar7;
  int iVar8;
  int iVar9;
  undefined4 uVar10;
  uint uVar11;
  int *piVar12;
  int iVar13;
  undefined4 *puVar14;
  int *piVar15;
  ushort *puVar16;

  gp = &__global_pointer_;
  uVar4 = param_1[1];
  uVar3 = param_1[3] - (uVar4 >> 3);
  puVar16 = (ushort *)(*param_1 + (uVar4 >> 3));
  if (uVar3 < 2) {
    uVar11 = 0;
    if (uVar3 != 1) goto LAB_ram_4205886a;
    uVar2 = *puVar16;
    param_1[1] = uVar4 + 8;
    uVar11 = (((uint)(byte)uVar2 << 8) << (uVar4 & 7)) >> 8 & 0xff;
    if (param_2 != 0) goto LAB_ram_42058876;
LAB_ram_42058974:
    iVar6 = get_ics_info(param_1,param_2,param_4 + 0x24a8,param_4 + 0x24b0,param_5,param_6,param_9,
                         *(int *)(param_4 + 0x2484) + 0xad0,0);
    piVar15 = *(int **)(*(int *)(param_4 + 0x24a8) * 4 + param_9);
    if (*param_6 < 1) goto LAB_ram_420589bc;
LAB_ram_4205888c:
    iVar9 = 0;
    piVar12 = param_5;
    do {
      iVar8 = *piVar12;
      piVar12 = piVar12 + 1;
      iVar9 = iVar9 + 1;
    } while (iVar8 < piVar15[1]);
    iVar9 = huffcb(param_11,param_1,piVar15 + 0x14,piVar15[0xc] * iVar9);
    if (iVar9 == 0) {
      if (*piVar15 != 0) {
        return 1;
      }
      calc_gsfb_table(piVar15,param_5);
      return 1;
    }
    if (0 < iVar9) {
      iVar8 = 0;
      puVar7 = param_11;
      do {
        iVar5 = puVar7[1];
        iVar8 = iVar5 - iVar8;
        if (0 < iVar8) {
          uVar10 = *puVar7;
          iVar13 = iVar8;
          puVar14 = param_7;
          do {
            iVar13 = iVar13 + -1;
            *puVar14 = uVar10;
            puVar14 = puVar14 + 1;
          } while (iVar13 != 0);
          param_7 = param_7 + iVar8;
        }
        puVar7 = puVar7 + 2;
        iVar8 = iVar5;
      } while (param_11 + iVar9 * 2 != puVar7);
    }
    iVar8 = *piVar15;
  }
  else {
    uVar2 = *puVar16;
    uVar11 = (((uint)(uVar2 >> 8) + (uint)uVar2 * 0x100 << (uVar4 & 7)) << 0x10) >> 0x18;
LAB_ram_4205886a:
    param_1[1] = uVar4 + 8;
    if (param_2 == 0) goto LAB_ram_42058974;
LAB_ram_42058876:
    iVar6 = 0;
    piVar15 = *(int **)(*(int *)(param_4 + 0x24a8) * 4 + param_9);
    if (0 < *param_6) goto LAB_ram_4205888c;
LAB_ram_420589bc:
    memset(param_7,0,0x200);
    iVar8 = *piVar15;
    iVar9 = 0;
  }
  if (iVar8 == 0) {
    calc_gsfb_table(piVar15,param_5);
  }
  if (iVar6 != 0) {
    return iVar6;
  }
  iVar6 = hufffac(piVar15,param_1,param_5,iVar9,param_11,uVar11,*(int *)(param_4 + 0x2484) + 0x4ac,
                  *(undefined4 *)(param_3 + 0x8a74));
  if (iVar6 != 0) {
    return iVar6;
  }
  uVar3 = param_1[1];
  uVar11 = param_1[3];
  iVar6 = *param_1;
  uVar4 = uVar3 + 1;
  if (uVar3 >> 3 < uVar11) {
    bVar1 = *(byte *)((uVar3 >> 3) + iVar6);
    param_1[1] = uVar4;
    uVar3 = ((uint)bVar1 << (uVar3 & 7)) >> 7 & 1;
    *param_10 = uVar3;
    if (uVar3 != 0) {
      if (*piVar15 != 1) {
        return 1;
      }
      iVar6 = get_pulse_data(param_10,param_1);
      if (iVar6 != 0) {
        return iVar6;
      }
      uVar4 = param_1[1];
      iVar6 = *param_1;
      uVar11 = param_1[3];
    }
  }
  else {
    param_1[1] = uVar4;
    *param_10 = 0;
  }
  if (uVar4 >> 3 < uVar11) {
    bVar1 = *(byte *)((uVar4 >> 3) + iVar6);
    param_1[1] = uVar4 + 1;
    uVar3 = ((uint)bVar1 << (uVar4 & 7)) >> 7 & 1;
    *param_8 = uVar3;
    if (uVar3 != 0) {
      get_tns(*(undefined4 *)(*(int *)(param_4 + 0x2484) + 0xacc),param_1,
              *(undefined4 *)(param_4 + 0x24a8),piVar15,param_3 + 0x8c,param_8,
              *(undefined4 *)(param_3 + 0x8a74));
      iVar6 = *param_1;
      uVar11 = param_1[3];
      goto LAB_ram_42058a32;
    }
  }
  else {
    param_1[1] = uVar4 + 1;
    *param_8 = 0;
  }
  if (0 < piVar15[1]) {
    memset(param_8 + 1,0,piVar15[1] << 2);
  }
LAB_ram_42058a32:
  uVar3 = param_1[1];
  if (uVar3 >> 3 < uVar11) {
    bVar1 = *(byte *)(iVar6 + (uVar3 >> 3));
    param_1[1] = uVar3 + 1;
    if (((uint)bVar1 << (uVar3 & 7) & 0x80) != 0) {
      return 1;
    }
  }
  else {
    param_1[1] = uVar3 + 1;
  }
  iVar6 = huffspec_fxp(piVar15,param_1,iVar9,param_11,*(int *)(param_4 + 0x2484) + 0x4ac,
                       *(undefined4 *)(param_4 + 0x2480),*(undefined4 *)(param_3 + 0x8a78),
                       *(undefined4 *)(param_3 + 0x8a74));
  return iVar6;
}
