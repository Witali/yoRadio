/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: energy_estimation_LC @ ram:43002040
 * Types and parameter counts are inferred; verify against disassembly. */

void energy_estimation_LC
               (int param_1,int param_2,int param_3,int param_4,int param_5,int param_6,int param_7,
               int param_8)

{
  int iVar1;
  uint *puVar2;
  int *piVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  uint uVar9;

  gp = &__global_pointer_;
  iVar8 = *(int *)(param_4 + param_5 * 4 + 8) * 2;
  if (iVar8 <= param_8) {
    *(undefined4 *)(param_2 + param_7 * 4) = 0;
    *(undefined4 *)(param_3 + param_7 * 4) = 0xffffff9c;
    return;
  }
  uVar9 = (iVar8 - param_8) - 1;
  param_6 = param_6 + param_8 * 0x30;
  piVar3 = (int *)(param_1 + param_6 * 4);
  uVar5 = 0;
  iVar8 = 0;
  do {
    iVar6 = *piVar3;
    iVar1 = piVar3[0x30];
    piVar3 = piVar3 + 0x60;
    uVar7 = iVar6 * iVar6 + uVar5;
    uVar5 = uVar7 + iVar1 * iVar1;
    iVar8 = (uint)(uVar5 < uVar7) +
            (uint)(uVar7 < (uint)(iVar6 * iVar6)) +
            (int)((ulonglong)((longlong)iVar6 * (longlong)iVar6) >> 0x20) + iVar8 +
            (int)((ulonglong)((longlong)iVar1 * (longlong)iVar1) >> 0x20);
  } while ((int *)((((uVar9 & 0xfffffffe) + (uVar9 >> 1)) * 0x20 + param_6) * 4 + param_1 + 0x180)
           != piVar3);
  if (iVar8 < 0) {
    uVar7 = 0x1fffffff;
  }
  else {
    if (uVar5 == 0 && iVar8 == 0) {
      *(undefined4 *)(param_2 + param_7 * 4) = 0;
      *(undefined4 *)(param_3 + param_7 * 4) = 0xffffff9c;
      return;
    }
    uVar7 = uVar5 >> 2;
    if (iVar8 != 0) {
      iVar1 = pv_normalize(iVar8);
      uVar4 = iVar1 - 1;
      if ((int)(iVar1 - 0x21U) < 0) {
        iVar8 = (iVar8 << (uVar4 & 0x1f)) + ((uVar5 >> 1) >> (0x1f - uVar4 & 0x1f));
      }
      else {
        iVar8 = uVar5 << (iVar1 - 0x21U & 0x1f);
      }
      uVar7 = iVar8 >> 1;
      iVar8 = 0x21 - uVar4;
      goto LAB_ram_43002112;
    }
  }
  iVar8 = pv_normalize(uVar7);
  uVar7 = uVar7 << (iVar8 - 1U & 0x1f);
  iVar8 = 2 - (iVar8 - 1U);
LAB_ram_43002112:
  iVar1 = param_8 + 2 + (uVar9 & 0xfffffffe);
  uVar5 = iVar1 - param_8;
  *(int *)(param_3 + param_7 * 4) = iVar8;
  puVar2 = (uint *)(param_2 + param_7 * 4);
  if ((param_8 - iVar1 & uVar5) != uVar5) {
    *puVar2 = (uint)((ulonglong)
                     ((longlong)((int)*(short *)(pow2 + uVar5 * 2) << 0x10) * (longlong)(int)uVar7)
                    >> 0x20);
    return;
  }
  *puVar2 = uVar7 >> ((int)*(short *)(pow2 + uVar5 * 2) & 0x1fU);
  return;
}
