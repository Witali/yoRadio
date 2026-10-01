/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_envelope_unmapping @ ram:430117e8
 * Types and parameter counts are inferred; verify against disassembly. */

void sbr_envelope_unmapping(int *param_1,int param_2)

{
  uint *puVar1;
  int iVar2;
  int *piVar3;
  uint uVar4;
  uint *puVar5;
  int *piVar6;
  uint *puVar7;
  int iVar8;
  uint uVar9;

  gp = &__global_pointer_;
  if (*(int *)(param_2 + 0xac) == 0) {
    if (0 < *param_1) {
      puVar5 = (uint *)(param_2 + 0xb98);
      puVar7 = (uint *)(param_1 + 0x2e6);
      iVar2 = 0;
      do {
        uVar4 = puVar5[-0x122];
        uVar9 = 0x40000000;
        *puVar7 = ((int)puVar7[-0x122] >> 1) + 7;
        if ((puVar7[-0x122] & 1) != 0) {
          uVar9 = 0x5a827980;
        }
        iVar8 = (int)uVar4 >> 1;
        puVar7[-0x122] = uVar9;
        uVar9 = iVar8 - 0xc;
        *puVar5 = uVar9;
        if ((uVar4 & 1) == 0) {
          puVar5[-0x122] = 0x40000000;
          if ((int)uVar9 < 0) {
            if (-0xb < (int)uVar9) {
              uVar4 = 0x40000000 - *(int *)(InvFiltFactors + iVar8 * -4 + 4);
              goto LAB_ram_43011874;
            }
            *puVar5 = *puVar7;
            *puVar7 = 0;
          }
          else {
            if ((int)uVar9 < 0xb) {
              uVar4 = *(uint *)(one_over_one_plus_two_to_n + uVar9 * 4);
            }
            else {
              uVar4 = 0x40000000 - (0x40000000 >> (uVar9 & 0x1f));
            }
LAB_ram_43011874:
            puVar5[-0x122] = uVar4;
            *puVar5 = *puVar7 - uVar9;
          }
          uVar9 = puVar7[-0x122];
          uVar4 = puVar5[-0x122];
          if (uVar9 != 0x40000000) {
            uVar4 = (uVar9 * uVar4 >> 0x1e) +
                    (int)((ulonglong)((longlong)(int)uVar9 * (longlong)(int)uVar4) >> 0x20) * 4;
            puVar5[-0x122] = uVar4;
          }
          puVar7[-0x122] = uVar4;
        }
        else if ((int)uVar9 < 0) {
          if ((int)uVar9 < -0xb) {
            puVar5[-0x122] = 0x40000000;
            *puVar5 = 0;
            uVar9 = 0;
            goto LAB_ram_430119e6;
          }
          puVar5[-0x122] = 0x40000000 - *(int *)(one_over_one_plus_two_to_n + iVar8 * -4);
          uVar4 = puVar5[-0x122];
          *puVar5 = *puVar7 - uVar9;
          uVar9 = puVar7[-0x122];
          if (uVar9 == 0x40000000) goto LAB_ram_43011a4a;
LAB_ram_430119fc:
          puVar5[-0x122] =
               (uVar9 * uVar4 >> 0x1e) +
               (int)((ulonglong)((longlong)(int)uVar9 * (longlong)(int)uVar4) >> 0x20) * 4;
          puVar7[-0x122] = uVar4;
          *puVar7 = *puVar7 + 1;
        }
        else {
          if ((int)uVar9 < 0xc) {
            puVar5[-0x122] = *(uint *)(one_over_one_plus_sq_2_by_two_to_n + uVar9 * 4);
          }
          else {
            puVar5[-0x122] = 0x40000000 - (0x40000000 >> (uVar9 & 0x1f));
          }
LAB_ram_430119e6:
          uVar4 = puVar5[-0x122];
          *puVar5 = *puVar7 - uVar9;
          uVar9 = puVar7[-0x122];
          if (uVar9 != 0x40000000) goto LAB_ram_430119fc;
LAB_ram_43011a4a:
          puVar7[-0x122] =
               (uVar4 * 0x5a827980 >> 0x1e) +
               (int)((ulonglong)((longlong)(int)uVar4 * 0x5a827980) >> 0x20) * 4;
        }
        iVar2 = iVar2 + 1;
        puVar5 = puVar5 + 1;
        puVar7 = puVar7 + 1;
      } while (iVar2 < *param_1);
    }
  }
  else if (0 < *param_1) {
    puVar7 = (uint *)(param_2 + 0xb98);
    puVar5 = (uint *)(param_1 + 0x2e6);
    iVar2 = 0;
    do {
      uVar4 = puVar7[-0x122];
      *puVar5 = puVar5[-0x122] + 7;
      uVar9 = uVar4 - 0xc;
      puVar7[-0x122] = 0x40000000;
      *puVar7 = uVar9;
      if ((int)uVar9 < 0) {
        if (-0xb < (int)uVar9) {
          iVar8 = *(int *)(one_over_one_plus_two_to_n + (0xc - uVar4) * 4);
LAB_ram_430119cc:
          uVar4 = 0x40000000 - iVar8;
          goto LAB_ram_43011984;
        }
        *puVar7 = *puVar5;
        *puVar5 = 0;
      }
      else {
        iVar8 = 0x40000000 >> (uVar9 & 0x1f);
        if (10 < (int)uVar9) goto LAB_ram_430119cc;
        uVar4 = *(uint *)(one_over_one_plus_two_to_n + uVar9 * 4);
LAB_ram_43011984:
        puVar7[-0x122] = uVar4;
        *puVar7 = *puVar5 - uVar9;
      }
      puVar1 = puVar7 + -0x122;
      iVar2 = iVar2 + 1;
      puVar7 = puVar7 + 1;
      puVar5[-0x122] = *puVar1;
      puVar5 = puVar5 + 1;
    } while (iVar2 < *param_1);
  }
  if (param_1[1] < 1) {
    return;
  }
  piVar3 = (int *)(param_2 + 0x1108);
  piVar6 = param_1 + 0x442;
  iVar2 = 0;
  do {
    piVar6[10] = 7 - *piVar6;
    uVar4 = *piVar3 - 0xc;
    piVar3[10] = uVar4;
    if ((int)uVar4 < 0) {
      if ((int)uVar4 < -10) {
        *piVar3 = 0x40000000;
        piVar3[10] = 0;
        uVar4 = 0;
      }
      else {
        iVar8 = *(int *)(one_over_one_plus_two_to_n + (0xc - *piVar3) * 4);
LAB_ram_43011934:
        *piVar3 = 0x40000000 - iVar8;
      }
    }
    else {
      iVar8 = 0x40000000 >> (uVar4 & 0x1f);
      if (10 < (int)uVar4) goto LAB_ram_43011934;
      *piVar3 = *(int *)(one_over_one_plus_two_to_n + uVar4 * 4);
    }
    iVar2 = iVar2 + 1;
    piVar3[10] = piVar6[10] - uVar4;
    *piVar6 = *piVar3;
    piVar6 = piVar6 + 1;
    piVar3 = piVar3 + 1;
    if (param_1[1] <= iVar2) {
      return;
    }
  } while( true );
}
