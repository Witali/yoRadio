/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: get_sbr_bitstream @ ram:430082ea
 * Types and parameter counts are inferred; verify against disassembly. */

void get_sbr_bitstream(int *param_1,int *param_2)

{
  ushort uVar1;
  uint uVar2;
  uint uVar3;
  undefined1 *puVar4;
  int iVar5;
  uint uVar6;
  undefined1 uVar7;
  byte bVar8;
  uint uVar9;
  ushort *puVar10;
  int iVar11;
  uint uVar12;
  int iVar13;

  gp = &__global_pointer_;
  uVar3 = param_2[1];
  iVar11 = param_2[3];
  iVar5 = *param_2;
  uVar12 = iVar11 - (uVar3 >> 3);
  puVar10 = (ushort *)((uVar3 >> 3) + iVar5);
  uVar6 = uVar3 + 4;
  if (uVar12 < 2) {
    if (uVar12 == 1) {
      uVar12 = (uint)(byte)*puVar10 << 8;
      goto LAB_ram_43008318;
    }
    param_2[1] = uVar6;
    uVar12 = 0;
  }
  else {
    uVar1 = *puVar10;
    uVar12 = (uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 & 0xffff;
LAB_ram_43008318:
    param_2[1] = uVar6;
    uVar12 = (uVar12 << (uVar3 & 7)) >> 0xc & 0xf;
    if (uVar12 == 0xf) {
      uVar9 = iVar11 - (uVar6 >> 3);
      puVar10 = (ushort *)(iVar5 + (uVar6 >> 3));
      if (uVar9 < 2) {
        uVar12 = 0xe;
        if (uVar9 == 1) {
          uVar12 = ((((uint)(byte)*puVar10 << 8) << (uVar6 & 7)) >> 8 & 0xff) + 0xe;
        }
      }
      else {
        uVar1 = *puVar10;
        uVar12 = ((((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 << (uVar6 & 7)) << 0x10) >> 0x18) + 0xe
        ;
      }
      uVar6 = uVar3 + 0xc;
      param_2[1] = uVar6;
    }
  }
  uVar3 = iVar11 - (uVar6 >> 3);
  puVar10 = (ushort *)((uVar6 >> 3) + iVar5);
  if (uVar3 < 2) {
    if (uVar3 != 1) goto LAB_ram_43008376;
    uVar3 = (uint)(byte)*puVar10 << 8;
  }
  else {
    uVar1 = *puVar10;
    uVar3 = (uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 & 0xffff;
  }
  uVar9 = (uVar3 << (uVar6 & 7)) >> 0xc & 0xf;
  uVar3 = uVar6 + 4;
  param_2[1] = uVar3;
  if (((uVar9 - 0xd < 2) && (uVar12 != 0)) && (iVar13 = *param_1, iVar13 < 1)) {
    uVar2 = iVar11 - (uVar3 >> 3);
    puVar10 = (ushort *)((uVar3 >> 3) + iVar5);
    param_1[iVar13 * 0x103 + 3] = uVar9;
    param_1[iVar13 * 0x103 + 4] = uVar12;
    if (uVar2 < 2) {
      bVar8 = 0;
      if (uVar2 == 1) {
        bVar8 = (byte)((((uint)(byte)*puVar10 << 8) << (uVar3 & 7)) >> 0xc) & 0xf;
      }
    }
    else {
      uVar1 = *puVar10;
      bVar8 = (byte)(((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 << (uVar3 & 7)) >> 8) >> 4;
    }
    uVar3 = uVar6 + 8;
    param_2[1] = uVar3;
    *(byte *)(param_1 + iVar13 * 0x103 + 5) = bVar8;
    if (uVar12 != 1) {
      puVar4 = (undefined1 *)((int)param_1 + iVar13 * 0x40c + 0x15);
      do {
        uVar9 = iVar11 - (uVar3 >> 3);
        puVar10 = (ushort *)(iVar5 + (uVar3 >> 3));
        if (uVar9 < 2) {
          uVar7 = 0;
          if (uVar9 == 1) {
            uVar7 = (undefined1)((((uint)(byte)*puVar10 << 8) << (uVar3 & 7)) >> 8);
          }
        }
        else {
          uVar1 = *puVar10;
          uVar7 = (undefined1)(((uint)(uVar1 >> 8) + (uint)uVar1 * 0x100 << (uVar3 & 7)) >> 8);
        }
        uVar3 = uVar3 + 8;
        param_2[1] = uVar3;
        *puVar4 = uVar7;
        puVar4 = puVar4 + 1;
      } while (uVar3 != uVar12 * 8 + uVar6);
    }
    *param_1 = iVar13 + 1;
    return;
  }
LAB_ram_43008376:
  param_2[1] = uVar12 * 8 + uVar6;
  return;
}
