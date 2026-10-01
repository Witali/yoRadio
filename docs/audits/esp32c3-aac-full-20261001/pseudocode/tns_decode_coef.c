/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: tns_decode_coef @ ram:4301428c
 * Types and parameter counts are inferred; verify against disassembly. */

int tns_decode_coef(int param_1,int param_2,int *param_3,uint *param_4)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint *puVar6;
  uint *puVar7;
  uint uVar8;
  uint *puVar9;
  int *piVar10;
  int iVar11;
  uint *puVar12;
  uint uVar13;
  int iVar14;
  int iVar15;
  int iVar16;

  gp = &__global_pointer_;
  iVar11 = *(int *)((int)&neg_offset + param_2 * 4);
  iVar14 = -4;
  iVar16 = -1;
  iVar3 = 0x13;
  iVar15 = 0;
  puVar6 = (uint *)0x0;
  puVar7 = param_4 + 0x14;
  do {
    iVar2 = -4 - iVar14;
    iVar5 = *(int *)(tns_table + (*(int *)((int)param_3 + iVar14 + 4) + iVar11) * 4 + param_2 * 0x40
                    );
    uVar13 = iVar5 >> 0xc;
    uVar1 = iVar5 >> 0x1f ^ uVar13;
    iVar4 = iVar15;
    puVar12 = puVar7;
    puVar9 = param_4;
    if (iVar15 == 0) {
      *puVar7 = uVar13;
      puVar12 = (uint *)((int)param_4 + iVar2);
      param_4 = puVar7;
    }
    else {
      do {
        uVar8 = *puVar6;
        iVar4 = iVar4 + -1;
        puVar6 = puVar6 + -1;
        uVar8 = (int)((ulonglong)((longlong)iVar5 * (longlong)(int)uVar8) >> 0x20) * 2 + *puVar9;
        *puVar12 = uVar8;
        puVar12 = puVar12 + 1;
        puVar9 = puVar9 + 1;
      } while (iVar4 != 0);
      *(uint *)((int)puVar7 + iVar14 + 4) = uVar13;
      puVar7 = (uint *)((int)puVar7 + iVar14 + 4);
      uVar1 = uVar1 | uVar8 ^ (int)uVar8 >> 0x1f;
      puVar6 = puVar7;
      for (iVar4 = iVar16; iVar4 != 0; iVar4 = iVar4 + -1) {
        puVar12 = puVar6 + -2;
        puVar6 = puVar6 + -1;
        uVar1 = uVar1 | (int)*puVar12 >> 0x1f ^ *puVar12;
      }
      puVar12 = (uint *)((int)param_4 + iVar2 + iVar14 + 4);
      param_4 = (uint *)((int)puVar7 + (-4 - iVar14));
      if (0x3fffffff < (int)uVar1) {
        uVar1 = (int)uVar1 >> 1;
        iVar4 = iVar15;
        puVar6 = puVar12;
        do {
          piVar10 = (int *)((int)puVar6 + ((int)param_4 - (int)puVar12));
          iVar4 = iVar4 + -1;
          *piVar10 = *piVar10 >> 1;
          *puVar6 = (int)*puVar6 >> 1;
          puVar6 = puVar6 + 1;
        } while (iVar4 != 0);
        piVar10 = (int *)((int)param_4 + iVar14 + 4);
        puVar12 = (uint *)((int)puVar12 + iVar2 + iVar14 + 4);
        iVar3 = iVar3 + -1;
        *piVar10 = *piVar10 >> 1;
        param_4 = (uint *)((int)piVar10 + iVar2);
      }
    }
    iVar14 = iVar14 + 4;
    iVar15 = iVar15 + 1;
    iVar16 = iVar16 + 1;
    puVar6 = puVar7;
    puVar7 = puVar12;
  } while (iVar15 < param_1);
  iVar11 = 0;
  if ((int)uVar1 < 0x8000) {
    if ((uVar1 != 0) && ((int)uVar1 < 0x4000)) {
      do {
        uVar1 = uVar1 << 1;
        iVar11 = iVar11 + -1;
      } while ((int)uVar1 < 0x4000);
      iVar3 = iVar3 - iVar11;
      if (iVar3 < 0x10) {
        return iVar3;
      }
      if (param_1 < 1) {
        return 0xf;
      }
      goto LAB_ram_430143a6;
    }
  }
  else {
    do {
      uVar1 = (int)uVar1 >> 1;
      iVar11 = iVar11 + 1;
    } while (0x7fff < (int)uVar1);
  }
  if (param_1 < 1) {
    if (0xf < iVar3 - iVar11) {
      return 0xf;
    }
    return iVar3 - iVar11;
  }
  piVar10 = param_3;
  iVar14 = param_1;
  do {
    iVar14 = iVar14 + -1;
    *piVar10 = *param_4 << (0x10U - iVar11 & 0x1f);
    param_4 = param_4 + 1;
    piVar10 = piVar10 + 1;
  } while (iVar14 != 0);
  iVar3 = iVar3 - iVar11;
  if (iVar3 < 0x10) {
    return iVar3;
  }
LAB_ram_430143a6:
  do {
    param_1 = param_1 + -1;
    *param_3 = *param_3 >> (iVar3 - 0xfU & 0x1f);
    param_3 = param_3 + 1;
  } while (param_1 != 0);
  return 0xf;
}
