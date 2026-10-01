/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: high_freq_coeff_LC @ ram:43011c3a
 * Types and parameter counts are inferred; verify against disassembly. */

void high_freq_coeff_LC(int param_1,int *param_2,int param_3,int *param_4,int *param_5)

{
  bool bVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  int *piVar6;
  int iVar7;
  int *piVar8;
  int iVar9;
  int iVar10;
  aac_analysis_fraction_t aStack_5c;
  aac_analysis_autocorrelation_t aStack_54;

  gp = &__global_pointer_;
  iVar2 = 1;
  if (1 < *param_4) {
    piVar6 = param_5 + 1;
    do {
      while( true ) {
        calc_auto_corr_LC(&aStack_54,param_1,iVar2,0x26);
        iVar10 = iVar2 * 4;
        if ((aStack_54.r11_real != 0) && (aStack_54.determinant != 0)) break;
        iVar7 = param_2[1];
        *(undefined4 *)(*param_2 + iVar10) = 0;
        *(undefined4 *)(iVar7 + iVar10) = 0;
        *piVar6 = 0;
LAB_ram_43011c7e:
        iVar2 = iVar2 + 1;
        piVar6 = piVar6 + 1;
        if (*param_4 <= iVar2) goto LAB_ram_43011d46;
      }
      pv_div(aStack_54.r01_real,aStack_54.r11_real,&aStack_5c);
      iVar7 = -(aStack_5c.mantissa >> 2);
      if (aStack_5c.exponent < 1) {
        if (aStack_5c.exponent == 0) {
          iVar5 = 0x40000000;
          if (aStack_5c.mantissa < 0x40000000) {
            bVar1 = false;
            if (-0x40000000 < aStack_5c.mantissa) {
              iVar5 = -aStack_5c.mantissa;
              bVar1 = false;
            }
          }
          else {
            iVar5 = -0x40000000;
            bVar1 = false;
          }
        }
        else {
          if (aStack_5c.exponent < -3) {
            bVar1 = true;
            iVar7 = -0x80000000;
          }
          else {
            iVar7 = iVar7 << (-aStack_5c.exponent & 0x1fU);
            bVar1 = iVar7 == -0x80000000;
          }
          iVar5 = -0x40000000;
          if (aStack_5c.mantissa < 1) {
            iVar5 = 0x40000000;
          }
        }
      }
      else {
        iVar5 = -aStack_5c.mantissa >> (aStack_5c.exponent & 0x1fU);
        iVar7 = iVar7 >> (aStack_5c.exponent & 0x1fU);
        bVar1 = false;
      }
      *piVar6 = iVar5;
      uVar3 = (((uint)(aStack_54.r01_real * aStack_54.r12_real) >> 0x1e) +
              (int)((ulonglong)((longlong)aStack_54.r01_real * (longlong)aStack_54.r12_real) >> 0x20
                   ) * 4) -
              (((uint)(aStack_54.r02_real * aStack_54.r11_real) >> 0x1e) +
              (int)((ulonglong)((longlong)aStack_54.r02_real * (longlong)aStack_54.r11_real) >> 0x20
                   ) * 4);
      if (((int)(((int)uVar3 >> 0x1f ^ uVar3) - ((int)uVar3 >> 0x1f)) >> 2 <
           (aStack_54.determinant >> 0x1f ^ aStack_54.determinant) - (aStack_54.determinant >> 0x1f)
          ) && (!bVar1)) {
        pv_div(uVar3,aStack_54.determinant,&aStack_5c);
        piVar8 = (int *)(param_2[1] + iVar10);
        *piVar8 = aStack_5c.mantissa;
        uVar3 = aStack_5c.exponent + 2;
        if ((int)uVar3 < 1) {
          if (uVar3 != 0) {
            *piVar8 = *piVar8 << (-aStack_5c.exponent - 2U & 0x1f);
          }
        }
        else {
          *piVar8 = *piVar8 >> (uVar3 & 0x1f);
        }
        aStack_5c.exponent = uVar3;
        pv_div(aStack_54.r12_real,aStack_54.r11_real,&aStack_5c);
        iVar5 = aStack_5c.mantissa >> 2;
        if (aStack_5c.exponent < 1) {
          if (aStack_5c.exponent != 0) {
            iVar5 = iVar5 << (-aStack_5c.exponent & 0x1fU);
          }
        }
        else {
          iVar5 = iVar5 >> (aStack_5c.exponent & 0x1fU);
        }
        iVar4 = param_2[1];
        iVar9 = *(int *)(iVar4 + iVar10);
        iVar7 = iVar7 - (((uint)(iVar5 * iVar9) >> 0x1c) +
                        (int)((ulonglong)((longlong)iVar5 * (longlong)iVar9) >> 0x20) * 0x10);
        if (iVar7 + 0x3fffffffU < 0x7fffffff) {
          *(int *)(*param_2 + iVar10) = iVar7;
        }
        else {
          *(int *)(*param_2 + iVar10) = 0;
          *(int *)(iVar4 + iVar10) = 0;
        }
        goto LAB_ram_43011c7e;
      }
      iVar7 = param_2[1];
      iVar2 = iVar2 + 1;
      *(undefined4 *)(*param_2 + iVar10) = 0;
      *(undefined4 *)(iVar7 + iVar10) = 0;
      piVar6 = piVar6 + 1;
    } while (iVar2 < *param_4);
  }
LAB_ram_43011d46:
  *param_5 = 0;
  *(undefined4 *)(param_3 + 4) = 0;
  uVar3 = 2;
  piVar6 = (int *)(param_3 + 4);
  if (*param_4 < 3) {
    return;
  }
  do {
    while (piVar6[1] = 0, (uVar3 & 1) != 0) {
      if (0 < param_5[2]) {
        iVar2 = param_5[1];
        if (iVar2 < 1) {
          if (*param_5 < 0) goto LAB_ram_43011db8;
        }
        else {
          piVar6[1] = 0x40000000;
          if (*param_5 < 0) {
            iVar2 = param_5[1];
            *piVar6 = 0x40000000 -
                      (((uint)(iVar2 * iVar2) >> 0x1e) +
                      (int)((ulonglong)((longlong)iVar2 * (longlong)iVar2) >> 0x20) * 4);
          }
        }
      }
LAB_ram_43011d8e:
      uVar3 = uVar3 + 1;
      piVar6 = piVar6 + 1;
      param_5 = param_5 + 1;
      if (*param_4 <= (int)uVar3) {
        return;
      }
    }
    if (-1 < param_5[2]) goto LAB_ram_43011d8e;
    iVar2 = param_5[1];
    if (iVar2 < 0) {
      piVar6[1] = 0x40000000;
      if (0 < *param_5) {
        iVar2 = param_5[1];
        *piVar6 = 0x40000000 -
                  (((uint)(iVar2 * iVar2) >> 0x1e) +
                  (int)((ulonglong)((longlong)iVar2 * (longlong)iVar2) >> 0x20) * 4);
      }
      goto LAB_ram_43011d8e;
    }
    if (*param_5 < 1) goto LAB_ram_43011d8e;
LAB_ram_43011db8:
    uVar3 = uVar3 + 1;
    piVar6 = piVar6 + 1;
    param_5 = param_5 + 1;
    *piVar6 = 0x40000000 -
              (((uint)(iVar2 * iVar2) >> 0x1e) +
              (int)((ulonglong)((longlong)iVar2 * (longlong)iVar2) >> 0x20) * 4);
    if (*param_4 <= (int)uVar3) {
      return;
    }
  } while( true );
}
