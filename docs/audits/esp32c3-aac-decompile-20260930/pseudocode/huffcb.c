/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: huffcb @ ram:42058d5e
 * Types and parameter counts are inferred; verify against disassembly. */

uint huffcb(uint *param_1,int *param_2,uint *param_3,uint param_4,int param_5,int param_6)

{
  ushort uVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  ushort *puVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  int iVar9;
  uint uVar10;
  uint uVar11;
  int iVar12;
  uint uVar13;
  uint uVar14;

  gp = &__global_pointer_;
  if ((int)param_4 < 1) {
    if (param_4 == 0) {
      return 0;
    }
    return 0;
  }
  uVar13 = *param_3;
  iVar12 = *param_2;
  iVar3 = param_2[3];
  uVar10 = (1 << (uVar13 & 0x1f)) - 1;
  uVar14 = 0x10 - uVar13;
  uVar2 = 0;
  uVar6 = 0;
  uVar7 = 0;
  do {
    uVar4 = param_2[1];
    uVar11 = iVar3 - (uVar4 >> 3);
    puVar5 = (ushort *)(iVar12 + (uVar4 >> 3));
    if (uVar11 < 2) {
      uVar8 = 0;
      if (uVar11 == 1) {
        uVar8 = (((uint)(byte)*puVar5 << 8) << (uVar4 & 7)) >> 0xc & 0xf;
      }
    }
    else {
      uVar1 = *puVar5;
      uVar8 = (((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 << (uVar4 & 7)) << 0x10) >> 0x1c;
    }
    uVar4 = uVar4 + 4;
    param_2[1] = uVar4;
    *param_1 = uVar8;
    uVar11 = iVar3 - (uVar4 >> 3);
    puVar5 = (ushort *)(iVar12 + (uVar4 >> 3));
    if (uVar11 < 2) {
      uVar8 = 0;
      if (uVar11 == 1) {
        uVar8 = (((uint)(byte)*puVar5 << 8) << (uVar4 & 7) & 0xffff) >> (uVar14 & 0x1f);
      }
    }
    else {
      uVar1 = *puVar5;
      uVar8 = ((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 << (uVar4 & 7) & 0xffff) >> (uVar14 & 0x1f);
    }
    uVar4 = uVar4 + uVar13;
    param_2[1] = uVar4;
    if (((int)uVar7 < (int)param_4) && (uVar10 == uVar8)) {
      do {
        uVar11 = iVar3 - (uVar4 >> 3);
        uVar7 = uVar7 + uVar10;
        puVar5 = (ushort *)(iVar12 + (uVar4 >> 3));
        if (uVar11 < 2) {
          uVar8 = 0;
          if (uVar11 != 1) goto LAB_ram_42058e1a;
          uVar1 = *puVar5;
          param_2[1] = uVar4 + uVar13;
          uVar8 = (((uint)(byte)uVar1 << 8) << (uVar4 & 7) & 0xffff) >> (uVar14 & 0x1f);
        }
        else {
          uVar1 = *puVar5;
          uVar8 = ((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 << (uVar4 & 7) & 0xffff) >>
                  (uVar14 & 0x1f);
LAB_ram_42058e1a:
          param_2[1] = uVar4 + uVar13;
        }
      } while ((uVar10 == uVar8) && (uVar4 = uVar4 + uVar13, (int)uVar7 < (int)param_4));
    }
    uVar7 = uVar7 + uVar8;
    param_1[1] = uVar7;
    iVar9 = uVar7 - uVar2;
    if ((iVar9 == param_6) && (iVar9 < (int)param_4)) {
      uVar2 = uVar7 + (param_5 - param_6);
      param_1[3] = uVar2;
      param_1[2] = 0;
      uVar6 = uVar6 + 2;
      param_1 = param_1 + 4;
      uVar7 = uVar2;
    }
    else {
      uVar6 = uVar6 + 1;
      if (param_6 < iVar9) break;
      param_1 = param_1 + 2;
    }
    uVar4 = uVar7;
    if ((int)uVar7 < (int)uVar6) {
      uVar4 = uVar6;
    }
  } while ((int)uVar4 < (int)param_4);
  if ((uVar7 == param_4) && ((int)uVar6 <= (int)param_4)) {
    return uVar6;
  }
  return 0;
}
