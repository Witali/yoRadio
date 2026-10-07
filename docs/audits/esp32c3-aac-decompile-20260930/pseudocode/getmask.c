/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: getmask @ ram:42058b4e
 * Types and parameter counts are inferred; verify against disassembly. */

uint getmask(int param_1,int *param_2,int *param_3,uint param_4,uint *param_5)

{
  ushort uVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  uint *puVar6;
  uint uVar7;
  uint uVar8;
  int iVar9;
  byte *pbVar10;
  uint uVar11;
  int iVar12;
  ushort *puVar13;

  gp = &__global_pointer_;
  uVar8 = param_2[1];
  uVar11 = param_2[3] - (uVar8 >> 3);
  puVar13 = (ushort *)(*param_2 + (uVar8 >> 3));
  if (uVar11 < 2) {
    if (uVar11 != 1) {
      param_2[1] = uVar8 + 2;
      return 0;
    }
    uVar11 = (uint)(byte)*puVar13 << 8;
  }
  else {
    uVar1 = *puVar13;
    uVar11 = (uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 & 0xffff;
  }
  uVar11 = (uVar11 << (uVar8 & 7)) >> 0xe & 3;
  param_2[1] = uVar8 + 2;
  if (uVar11 != 1) {
    if (uVar11 == 2) {
      iVar12 = *(int *)(param_1 + 4);
      iVar9 = 0;
      if (0 < iVar12) {
        do {
          iVar4 = *(int *)(iVar9 * 4 + param_1 + 0x30);
          puVar6 = param_5;
          iVar9 = iVar4;
          if (0 < iVar4) {
            do {
              iVar9 = iVar9 + -1;
              *puVar6 = 1;
              puVar6 = puVar6 + 1;
            } while (iVar9 != 0);
            param_5 = param_5 + iVar4;
          }
          iVar9 = *param_3;
          param_3 = param_3 + 1;
        } while (iVar9 < iVar12);
      }
      uVar11 = 2;
    }
    return uVar11;
  }
  iVar9 = *(int *)(param_1 + 4);
  iVar12 = 0;
  if (0 < iVar9) {
    do {
      if (0 < (int)param_4) {
        iVar4 = *param_2;
        uVar8 = param_4;
        do {
          uVar11 = uVar8;
          if (0x19 < (int)uVar8) {
            uVar11 = 0x19;
          }
          uVar7 = param_2[1];
          uVar5 = param_2[3] - (uVar7 >> 3);
          pbVar10 = (byte *)((uVar7 >> 3) + iVar4);
          uVar2 = 1 << (uVar11 - 1 & 0x1f);
          if (uVar5 < 4) {
            if (uVar5 == 2) {
              uVar5 = 0;
LAB_ram_42058cf8:
              uVar5 = (uint)pbVar10[1] << 0x10 | uVar5;
            }
            else {
              if (uVar5 == 3) {
                uVar5 = (uint)pbVar10[2] << 8;
                goto LAB_ram_42058cf8;
              }
              if (uVar5 != 1) {
                uVar5 = 0;
                goto LAB_ram_42058c6c;
              }
              uVar5 = 0;
            }
            uVar5 = (((uint)*pbVar10 << 0x18 | uVar5) << (uVar7 & 7)) >> (0x20 - uVar11 & 0x1f);
          }
          else {
            uVar5 = (((uint)*pbVar10 << 0x18 | (uint)pbVar10[1] << 0x10 | (uint)pbVar10[3] |
                     (uint)pbVar10[2] << 8) << (uVar7 & 7)) >> (0x20 - uVar11 & 0x1f);
          }
LAB_ram_42058c6c:
          param_2[1] = uVar7 + uVar11;
          puVar6 = param_5;
          uVar7 = uVar11;
          do {
            uVar7 = uVar7 - 1;
            *puVar6 = (uVar2 & uVar5) >> (uVar7 & 0x1f);
            uVar2 = uVar2 >> 1;
            puVar6 = puVar6 + 1;
          } while (uVar7 != 0);
          uVar8 = uVar8 - uVar11;
          param_5 = param_5 + uVar11;
        } while (0 < (int)uVar8);
      }
      iVar4 = *(int *)(iVar12 * 4 + param_1 + 0x30) - param_4;
      if (iVar4 < 0) {
        return 3;
      }
      iVar4 = iVar4 * 4;
      iVar3 = memset(param_5,0,iVar4);
      iVar12 = *param_3;
      param_3 = param_3 + 1;
      param_5 = (uint *)(iVar3 + iVar4);
    } while (iVar12 < iVar9);
  }
  return 1;
}
