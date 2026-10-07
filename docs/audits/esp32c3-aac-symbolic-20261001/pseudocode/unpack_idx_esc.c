/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: unpack_idx_esc @ ram:43015eba
 * Types and parameter counts are inferred; verify against disassembly. */

void unpack_idx_esc(undefined2 *param_1,int param_2,int param_3,int *param_4,int *param_5)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  byte *pbVar11;
  uint uVar12;
  uint uVar13;

  gp = &__global_pointer_;
  iVar2 = *(int *)(param_3 + 0xc);
  iVar7 = param_2 * *(int *)(div_mod + *(int *)(param_3 + 8) * 4) >> 0xd;
  uVar12 = iVar7 - iVar2;
  param_2 = param_2 - *(int *)(param_3 + 8) * iVar7;
  uVar6 = param_2 - iVar2;
  if (iVar7 == iVar2) {
    if (iVar2 == param_2) {
      iVar2 = *param_5;
      *param_1 = 0;
      uVar12 = uVar6;
      if (iVar2 < 0) {
        *param_5 = 0;
        iVar2 = 0;
      }
      goto LAB_ram_43015f04;
    }
    uVar8 = param_4[1];
    uVar4 = param_4[3];
    uVar5 = uVar8 >> 3;
    if (uVar5 < uVar4) {
      iVar2 = *param_4;
      uVar13 = 0;
LAB_ram_43015f2e:
      uVar3 = ((uint)*(byte *)(uVar5 + iVar2) << (uVar8 & 7)) >> 7 & 1;
      goto LAB_ram_43015f44;
    }
    param_4[1] = uVar8 + 1;
    uVar8 = uVar6 & 0x1f;
    uVar13 = 0;
    uVar3 = 0;
  }
  else {
    uVar8 = param_4[1];
    uVar4 = param_4[3];
    iVar2 = *param_4;
    uVar13 = 0;
    if (uVar8 >> 3 < uVar4) {
      bVar1 = *(byte *)((uVar8 >> 3) + iVar2);
      param_4[1] = uVar8 + 1;
      uVar13 = ((uint)bVar1 << (uVar8 & 7)) >> 7 & 1;
    }
    else {
      param_4[1] = uVar8 + 1;
    }
    if (uVar6 == 0) {
      uVar8 = 0;
      uVar3 = 0;
    }
    else {
      uVar8 = uVar8 + 1;
      uVar3 = 0;
      uVar5 = uVar8 >> 3;
      if (uVar5 < uVar4) goto LAB_ram_43015f2e;
LAB_ram_43015f44:
      param_4[1] = uVar8 + 1;
      uVar8 = uVar6 & 0x1f;
    }
    if ((uVar12 & 0x1f) == 0x10) {
      uVar9 = param_4[1];
      uVar5 = uVar9;
      do {
        uVar10 = uVar5;
        uVar5 = uVar10 + 1;
        if (uVar4 <= uVar10 >> 3) {
          param_4[1] = uVar5;
          break;
        }
        bVar1 = *(byte *)(iVar2 + (uVar10 >> 3));
        param_4[1] = uVar5;
      } while (((uint)bVar1 << (uVar10 & 7) & 0x80) != 0);
      uVar4 = uVar4 - (uVar5 >> 3);
      uVar9 = (uVar10 - uVar9) + 4;
      pbVar11 = (byte *)(iVar2 + (uVar5 >> 3));
      if (uVar4 < 4) {
        if (uVar4 == 2) {
          uVar4 = 0;
LAB_ram_4301617a:
          uVar4 = (uint)pbVar11[1] << 0x10 | uVar4;
        }
        else {
          if (uVar4 == 3) {
            uVar4 = (uint)pbVar11[2] << 8;
            goto LAB_ram_4301617a;
          }
          if (uVar4 != 1) {
            uVar4 = 0;
            goto LAB_ram_4301611a;
          }
          uVar4 = 0;
        }
        uVar4 = (((uint)*pbVar11 << 0x18 | uVar4) << (uVar5 & 7)) >> (0x20 - uVar9 & 0x1f);
      }
      else {
        uVar4 = (((uint)*pbVar11 << 0x18 | (uint)pbVar11[1] << 0x10 | (uint)pbVar11[3] |
                 (uint)pbVar11[2] << 8) << (uVar5 & 7)) >> (0x20 - uVar9 & 0x1f);
      }
LAB_ram_4301611a:
      param_4[1] = uVar9 + uVar5;
      uVar12 = (int)(((1 << (uVar9 & 0x1f)) + uVar4) * uVar12) >> 4;
    }
  }
  iVar2 = ((int)uVar12 >> 0x1f ^ uVar12) - ((int)uVar12 >> 0x1f);
  if (uVar13 != 0) {
    uVar12 = -uVar12;
  }
  iVar7 = *param_5;
  *param_1 = (short)uVar12;
  if (iVar7 < iVar2) {
    *param_5 = iVar2;
  }
  if (uVar8 == 0x10) {
    uVar13 = param_4[1];
    uVar12 = uVar13;
    do {
      uVar4 = uVar12;
      uVar12 = uVar4 + 1;
      if ((uint)param_4[3] <= uVar4 >> 3) {
        param_4[1] = uVar12;
        break;
      }
      bVar1 = *(byte *)(*param_4 + (uVar4 >> 3));
      param_4[1] = uVar12;
    } while (((uint)bVar1 << (uVar4 & 7) & 0x80) != 0);
    uVar13 = (uVar4 - uVar13) + 4;
    uVar4 = param_4[3] - (uVar12 >> 3);
    pbVar11 = (byte *)(*param_4 + (uVar12 >> 3));
    if (uVar4 < 4) {
      if (uVar4 == 2) {
        uVar4 = 0;
LAB_ram_43016190:
        uVar4 = (uint)pbVar11[1] << 0x10 | uVar4;
      }
      else {
        if (uVar4 == 3) {
          uVar4 = (uint)pbVar11[2] << 8;
          goto LAB_ram_43016190;
        }
        if (uVar4 != 1) {
          uVar4 = 0;
          goto LAB_ram_430160d8;
        }
        uVar4 = 0;
      }
      uVar4 = (((uint)*pbVar11 << 0x18 | uVar4) << (uVar12 & 7)) >> (0x20 - uVar13 & 0x1f);
    }
    else {
      uVar4 = (((uint)*pbVar11 << 0x18 | (uint)pbVar11[1] << 0x10 | (uint)pbVar11[3] |
               (uint)pbVar11[2] << 8) << (uVar12 & 7)) >> (0x20 - uVar13 & 0x1f);
    }
LAB_ram_430160d8:
    param_4[1] = uVar13 + uVar12;
    uVar6 = (int)(((1 << (uVar13 & 0x1f)) + uVar4) * uVar6) >> 4;
  }
  if (uVar3 == 0) {
    iVar2 = *param_5;
    uVar12 = uVar6;
  }
  else {
    iVar2 = *param_5;
    uVar12 = -uVar6;
  }
LAB_ram_43015f04:
  param_1[1] = (short)uVar12;
  iVar7 = (uVar6 ^ (int)uVar6 >> 0x1f) - ((int)uVar6 >> 0x1f);
  if (iVar2 < iVar7) {
    *param_5 = iVar7;
  }
  return;
}
