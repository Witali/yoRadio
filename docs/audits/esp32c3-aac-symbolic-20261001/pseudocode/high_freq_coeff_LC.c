/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: high_freq_coeff_LC @ ram:43011c3a
 * Types and parameter counts are inferred; verify against disassembly. */

void high_freq_coeff_LC(undefined4 param_1,int *param_2,int param_3,int *param_4,int *param_5)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int *piVar5;
  int iVar6;
  int *piVar7;
  bool bVar8;
  int iVar9;
  int iVar10;
  int iStack_5c;
  uint uStack_58;
  int iStack_54;
  int iStack_50;
  int iStack_4c;
  int iStack_48;
  uint uStack_34;

  gp = &__global_pointer_;
  iVar1 = 1;
  if (1 < *param_4) {
    piVar5 = param_5 + 1;
    do {
      while( true ) {
        calc_auto_corr_LC(&iStack_54,param_1,iVar1,0x26);
        iVar10 = iVar1 * 4;
        if ((iStack_54 != 0) && (uStack_34 != 0)) break;
        iVar6 = param_2[1];
        *(undefined4 *)(*param_2 + iVar10) = 0;
        *(undefined4 *)(iVar6 + iVar10) = 0;
        *piVar5 = 0;
LAB_ram_43011c7e:
        iVar1 = iVar1 + 1;
        piVar5 = piVar5 + 1;
        if (*param_4 <= iVar1) goto LAB_ram_43011d46;
      }
      pv_div(iStack_50,iStack_54,&iStack_5c);
      iVar6 = -(iStack_5c >> 2);
      if ((int)uStack_58 < 1) {
        if (uStack_58 == 0) {
          iVar4 = 0x40000000;
          if (iStack_5c < 0x40000000) {
            bVar8 = false;
            if (-0x40000000 < iStack_5c) {
              iVar4 = -iStack_5c;
              bVar8 = false;
            }
          }
          else {
            iVar4 = -0x40000000;
            bVar8 = false;
          }
        }
        else {
          if ((int)uStack_58 < -3) {
            bVar8 = true;
            iVar6 = -0x80000000;
          }
          else {
            iVar6 = iVar6 << (-uStack_58 & 0x1f);
            bVar8 = iVar6 == -0x80000000;
          }
          iVar4 = -0x40000000;
          if (iStack_5c < 1) {
            iVar4 = 0x40000000;
          }
        }
      }
      else {
        iVar4 = -iStack_5c >> (uStack_58 & 0x1f);
        iVar6 = iVar6 >> (uStack_58 & 0x1f);
        bVar8 = false;
      }
      *piVar5 = iVar4;
      uVar2 = (((uint)(iStack_50 * iStack_48) >> 0x1e) +
              (int)((ulonglong)((longlong)iStack_50 * (longlong)iStack_48) >> 0x20) * 4) -
              (((uint)(iStack_4c * iStack_54) >> 0x1e) +
              (int)((ulonglong)((longlong)iStack_4c * (longlong)iStack_54) >> 0x20) * 4);
      if (((int)(((int)uVar2 >> 0x1f ^ uVar2) - ((int)uVar2 >> 0x1f)) >> 2 <
           (int)(((int)uStack_34 >> 0x1f ^ uStack_34) - ((int)uStack_34 >> 0x1f))) && (!bVar8)) {
        pv_div(uVar2,uStack_34,&iStack_5c);
        piVar7 = (int *)(param_2[1] + iVar10);
        *piVar7 = iStack_5c;
        uVar2 = uStack_58 + 2;
        if ((int)uVar2 < 1) {
          if (uVar2 != 0) {
            *piVar7 = *piVar7 << (-uStack_58 - 2 & 0x1f);
          }
        }
        else {
          *piVar7 = *piVar7 >> (uVar2 & 0x1f);
        }
        uStack_58 = uVar2;
        pv_div(iStack_48,iStack_54,&iStack_5c);
        iVar4 = iStack_5c >> 2;
        if ((int)uStack_58 < 1) {
          if (uStack_58 != 0) {
            iVar4 = iVar4 << (-uStack_58 & 0x1f);
          }
        }
        else {
          iVar4 = iVar4 >> (uStack_58 & 0x1f);
        }
        iVar3 = param_2[1];
        iVar9 = *(int *)(iVar3 + iVar10);
        iVar6 = iVar6 - (((uint)(iVar4 * iVar9) >> 0x1c) +
                        (int)((ulonglong)((longlong)iVar4 * (longlong)iVar9) >> 0x20) * 0x10);
        if (iVar6 + 0x3fffffffU < 0x7fffffff) {
          *(int *)(*param_2 + iVar10) = iVar6;
        }
        else {
          *(int *)(*param_2 + iVar10) = 0;
          *(int *)(iVar3 + iVar10) = 0;
        }
        goto LAB_ram_43011c7e;
      }
      iVar6 = param_2[1];
      iVar1 = iVar1 + 1;
      *(undefined4 *)(*param_2 + iVar10) = 0;
      *(undefined4 *)(iVar6 + iVar10) = 0;
      piVar5 = piVar5 + 1;
    } while (iVar1 < *param_4);
  }
LAB_ram_43011d46:
  *param_5 = 0;
  *(undefined4 *)(param_3 + 4) = 0;
  uVar2 = 2;
  piVar5 = (int *)(param_3 + 4);
  if (*param_4 < 3) {
    return;
  }
  do {
    while (piVar5[1] = 0, (uVar2 & 1) != 0) {
      if (0 < param_5[2]) {
        iVar1 = param_5[1];
        if (iVar1 < 1) {
          if (*param_5 < 0) goto LAB_ram_43011db8;
        }
        else {
          piVar5[1] = 0x40000000;
          if (*param_5 < 0) {
            iVar1 = param_5[1];
            *piVar5 = 0x40000000 -
                      (((uint)(iVar1 * iVar1) >> 0x1e) +
                      (int)((ulonglong)((longlong)iVar1 * (longlong)iVar1) >> 0x20) * 4);
          }
        }
      }
LAB_ram_43011d8e:
      uVar2 = uVar2 + 1;
      piVar5 = piVar5 + 1;
      param_5 = param_5 + 1;
      if (*param_4 <= (int)uVar2) {
        return;
      }
    }
    if (-1 < param_5[2]) goto LAB_ram_43011d8e;
    iVar1 = param_5[1];
    if (iVar1 < 0) {
      piVar5[1] = 0x40000000;
      if (0 < *param_5) {
        iVar1 = param_5[1];
        *piVar5 = 0x40000000 -
                  (((uint)(iVar1 * iVar1) >> 0x1e) +
                  (int)((ulonglong)((longlong)iVar1 * (longlong)iVar1) >> 0x20) * 4);
      }
      goto LAB_ram_43011d8e;
    }
    if (*param_5 < 1) goto LAB_ram_43011d8e;
LAB_ram_43011db8:
    uVar2 = uVar2 + 1;
    piVar5 = piVar5 + 1;
    param_5 = param_5 + 1;
    *piVar5 = 0x40000000 -
              (((uint)(iVar1 * iVar1) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar1 * (longlong)iVar1) >> 0x20) * 4);
    if (*param_4 <= (int)uVar2) {
      return;
    }
  } while( true );
}
