/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_create_limiter_bands @ ram:430104e4
 * Types and parameter counts are inferred; verify against disassembly. */

void sbr_create_limiter_bands(int *param_1,int *param_2,int *param_3,int *param_4,int param_5)

{
  bool bVar1;
  int *piVar2;
  int iVar3;
  int *piVar4;
  int iVar5;
  int iVar6;
  int *piVar7;
  int iVar8;
  int *piVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int *piStack_134;
  int *piStack_12c;
  int iStack_108;
  int aiStack_104 [4];
  undefined1 auStack_f4 [24];
  int local_dc [42];

  gp = &__global_pointer_;
  aiStack_104[0] = 0x26666680;
  iVar8 = param_3[param_5];
  iVar12 = *param_4;
  aiStack_104[1] = 0x40000000;
  aiStack_104[2] = 0x60000000;
  iVar11 = *param_3;
  if (iVar12 < 1) {
    iVar6 = 0;
  }
  else {
    piVar2 = aiStack_104 + 3;
    do {
      piVar4 = param_4 + 1;
      piVar7 = piVar2 + 1;
      param_4 = param_4 + 1;
      *piVar2 = *piVar4 - iVar11;
      iVar6 = iVar12;
      piVar2 = piVar7;
    } while (piVar7 != aiStack_104 + 3 + iVar12);
  }
  piStack_134 = aiStack_104 + 3;
  piStack_134[iVar6] = iVar8 - iVar11;
  param_1[1] = iVar8 - iVar11;
  *param_1 = 0;
  *param_2 = 1;
  piVar2 = &iStack_108;
  while( true ) {
    piStack_12c = param_1 + 0xd;
    param_2 = param_2 + 1;
    piVar4 = param_3;
    piVar7 = local_dc;
    if (-1 < param_5) {
      do {
        iVar6 = *piVar4;
        piVar9 = piVar7 + 1;
        piVar4 = piVar4 + 1;
        *piVar7 = iVar6 - iVar11;
        piVar7 = piVar9;
      } while (piVar9 != local_dc + param_5 + 1);
    }
    if (1 < iVar12) {
      memcpy(local_dc + param_5 + 1,auStack_f4,(iVar12 + -1) * 4);
    }
    *param_2 = param_5 + iVar12 + -1;
    shellsort(local_dc,param_5 + iVar12);
    iVar6 = *param_2;
    iVar10 = 1;
    if (0 < iVar6) break;
LAB_ram_43010658:
    iVar10 = 0;
    piVar4 = piStack_12c;
    piVar7 = local_dc;
    if (-1 < iVar6) {
      do {
        iVar6 = *piVar7;
        iVar10 = iVar10 + 1;
        piVar7 = piVar7 + 1;
        *piVar4 = iVar6;
        piVar4 = piVar4 + 1;
      } while (iVar10 <= *param_2);
    }
    piVar2 = piVar2 + 1;
    param_1 = piStack_12c;
    if (piVar2 == aiStack_104 + 2) {
      return;
    }
  }
LAB_ram_4301060c:
  do {
    piVar7 = local_dc + iVar10;
    piVar4 = local_dc + iVar10 + -1;
    iVar6 = pv_log2(((*piVar7 + iVar11) * 0x100000) / (*piVar4 + iVar11));
    if (0xfae147a <
        (int)(((uint)(iVar6 * piVar2[1]) >> 0x14) +
             (int)((ulonglong)((longlong)iVar6 * (longlong)piVar2[1]) >> 0x20) * 0x1000)) {
      iVar6 = *param_2;
      iVar10 = iVar10 + 1;
      if (iVar6 < iVar10) goto LAB_ram_43010658;
      goto LAB_ram_4301060c;
    }
    iVar6 = *piVar4;
    if (*piVar7 == iVar6) {
      iVar6 = *param_2;
      *piVar7 = iVar8;
      shellsort(local_dc,iVar6 + 1);
      iVar6 = *param_2 + -1;
      *param_2 = iVar6;
    }
    else {
      iVar5 = 0;
      piVar4 = piStack_134;
      if (-1 < iVar12) {
        do {
          iVar3 = *piVar4;
          iVar5 = iVar5 + 1;
          piVar4 = piVar4 + 1;
          if (iVar6 == iVar3) {
            bVar1 = true;
            goto LAB_ram_430106e6;
          }
        } while (iVar5 <= iVar12);
        bVar1 = false;
LAB_ram_430106e6:
        iVar6 = 0;
        piVar4 = piStack_134;
        do {
          iVar5 = *piVar4;
          iVar6 = iVar6 + 1;
          piVar4 = piVar4 + 1;
          if (*piVar7 == iVar5) {
            iVar6 = *param_2;
            if (!bVar1) {
              local_dc[iVar10 + -1] = iVar8;
              goto LAB_ram_43010742;
            }
            iVar10 = iVar10 + 1;
            if (iVar10 <= iVar6) goto LAB_ram_4301060c;
            goto LAB_ram_43010658;
          }
        } while (iVar6 <= iVar12);
      }
      iVar6 = *param_2;
      local_dc[iVar10] = iVar8;
LAB_ram_43010742:
      shellsort(local_dc,iVar6 + 1);
      iVar6 = *param_2 + -1;
      *param_2 = iVar6;
    }
    if (iVar6 < iVar10) goto LAB_ram_43010658;
  } while( true );
}
