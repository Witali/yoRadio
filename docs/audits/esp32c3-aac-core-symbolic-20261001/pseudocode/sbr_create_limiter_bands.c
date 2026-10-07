/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_create_limiter_bands @ ram:430104e4
 * Types and parameter counts are inferred; verify against disassembly. */

void sbr_create_limiter_bands
               (int *param_1,int *param_2,int *param_3,aac_analysis_patch_t *patch,int param_5)

{
  int32_t *piVar1;
  bool bVar2;
  int *piVar3;
  int iVar4;
  int *piVar5;
  int iVar6;
  int iVar7;
  int *piVar8;
  int iVar9;
  int *piVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int *piStack_134;
  int *piStack_12c;
  int iStack_108;
  int aiStack_104 [4];
  undefined1 auStack_f4 [24];
  int local_dc [42];

  gp = &__global_pointer_;
  aiStack_104[0] = 0x26666680;
  iVar9 = param_3[param_5];
  iVar13 = patch->count;
  aiStack_104[1] = 0x40000000;
  aiStack_104[2] = 0x60000000;
  iVar12 = *param_3;
  if (iVar13 < 1) {
    iVar7 = 0;
  }
  else {
    piVar3 = aiStack_104 + 3;
    do {
      piVar1 = patch->start_band;
      piVar5 = piVar3 + 1;
      patch = (aac_analysis_patch_t *)patch->start_band;
      *piVar3 = *piVar1 - iVar12;
      iVar7 = iVar13;
      piVar3 = piVar5;
    } while (piVar5 != aiStack_104 + 3 + iVar13);
  }
  piStack_134 = aiStack_104 + 3;
  piStack_134[iVar7] = iVar9 - iVar12;
  param_1[1] = iVar9 - iVar12;
  *param_1 = 0;
  *param_2 = 1;
  piVar3 = &iStack_108;
  while( true ) {
    piStack_12c = param_1 + 0xd;
    param_2 = param_2 + 1;
    piVar5 = param_3;
    piVar8 = local_dc;
    if (-1 < param_5) {
      do {
        iVar7 = *piVar5;
        piVar10 = piVar8 + 1;
        piVar5 = piVar5 + 1;
        *piVar8 = iVar7 - iVar12;
        piVar8 = piVar10;
      } while (piVar10 != local_dc + param_5 + 1);
    }
    if (1 < iVar13) {
      memcpy(local_dc + param_5 + 1,auStack_f4,(iVar13 + -1) * 4);
    }
    *param_2 = param_5 + iVar13 + -1;
    shellsort(local_dc,param_5 + iVar13);
    iVar7 = *param_2;
    iVar11 = 1;
    if (0 < iVar7) break;
LAB_ram_43010658:
    iVar11 = 0;
    piVar5 = piStack_12c;
    piVar8 = local_dc;
    if (-1 < iVar7) {
      do {
        iVar7 = *piVar8;
        iVar11 = iVar11 + 1;
        piVar8 = piVar8 + 1;
        *piVar5 = iVar7;
        piVar5 = piVar5 + 1;
      } while (iVar11 <= *param_2);
    }
    piVar3 = piVar3 + 1;
    param_1 = piStack_12c;
    if (piVar3 == aiStack_104 + 2) {
      return;
    }
  }
LAB_ram_4301060c:
  do {
    piVar8 = local_dc + iVar11;
    piVar5 = local_dc + iVar11 + -1;
    iVar7 = pv_log2(((*piVar8 + iVar12) * 0x100000) / (*piVar5 + iVar12));
    if (0xfae147a <
        (int)(((uint)(iVar7 * piVar3[1]) >> 0x14) +
             (int)((ulonglong)((longlong)iVar7 * (longlong)piVar3[1]) >> 0x20) * 0x1000)) {
      iVar7 = *param_2;
      iVar11 = iVar11 + 1;
      if (iVar7 < iVar11) goto LAB_ram_43010658;
      goto LAB_ram_4301060c;
    }
    iVar7 = *piVar5;
    if (*piVar8 == iVar7) {
      iVar7 = *param_2;
      *piVar8 = iVar9;
      shellsort(local_dc,iVar7 + 1);
      iVar7 = *param_2 + -1;
      *param_2 = iVar7;
    }
    else {
      iVar6 = 0;
      piVar5 = piStack_134;
      if (-1 < iVar13) {
        do {
          iVar4 = *piVar5;
          iVar6 = iVar6 + 1;
          piVar5 = piVar5 + 1;
          if (iVar7 == iVar4) {
            bVar2 = true;
            goto LAB_ram_430106e6;
          }
        } while (iVar6 <= iVar13);
        bVar2 = false;
LAB_ram_430106e6:
        iVar7 = 0;
        piVar5 = piStack_134;
        do {
          iVar6 = *piVar5;
          iVar7 = iVar7 + 1;
          piVar5 = piVar5 + 1;
          if (*piVar8 == iVar6) {
            iVar7 = *param_2;
            if (!bVar2) {
              local_dc[iVar11 + -1] = iVar9;
              goto LAB_ram_43010742;
            }
            iVar11 = iVar11 + 1;
            if (iVar11 <= iVar7) goto LAB_ram_4301060c;
            goto LAB_ram_43010658;
          }
        } while (iVar7 <= iVar13);
      }
      iVar7 = *param_2;
      local_dc[iVar11] = iVar9;
LAB_ram_43010742:
      shellsort(local_dc,iVar7 + 1);
      iVar7 = *param_2 + -1;
      *param_2 = iVar7;
    }
    if (iVar7 < iVar11) goto LAB_ram_43010658;
  } while( true );
}
