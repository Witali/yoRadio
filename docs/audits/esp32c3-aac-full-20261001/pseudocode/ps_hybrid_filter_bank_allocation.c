/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: ps_hybrid_filter_bank_allocation @ ram:4300d5d4
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4
ps_hybrid_filter_bank_allocation(undefined4 *param_1,int param_2,int *param_3,undefined4 *param_4)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  int *piVar4;
  int iVar5;
  int *piVar6;
  int iVar7;
  int *piVar8;
  int *piVar9;

  gp = &__global_pointer_;
  piVar8 = (int *)*param_4;
  *param_1 = 0;
  piVar1 = piVar8 + 7;
  piVar8[1] = (int)piVar1;
  piVar4 = piVar1 + param_2;
  if (param_2 < 1) {
    piVar2 = piVar4 + param_2 + param_2;
    piVar8[4] = (int)(piVar4 + param_2);
    *piVar8 = param_2;
    piVar8[3] = (int)piVar4;
    piVar8[2] = 0xc;
    piVar4 = piVar2;
    piVar1 = piVar2;
  }
  else {
    iVar7 = 0;
    iVar5 = 0;
    do {
      iVar3 = *param_3;
      iVar5 = iVar5 + 1;
      param_3 = param_3 + 1;
      *piVar1 = iVar3;
      if (((iVar3 - 2U & 0xfffffffd) != 0) && (iVar3 != 8)) {
        return 1;
      }
      if (iVar7 < iVar3) {
        iVar7 = iVar3;
      }
      piVar1 = piVar1 + 1;
    } while (param_2 != iVar5);
    piVar6 = piVar4 + param_2;
    piVar9 = piVar6 + param_2;
    *piVar8 = param_2;
    piVar8[3] = (int)piVar4;
    piVar8[4] = (int)piVar6;
    piVar8[2] = 0xc;
    piVar1 = piVar6;
    piVar2 = piVar9;
    do {
      *piVar4 = (int)piVar2;
      *piVar1 = (int)(piVar2 + 0xc);
      piVar4 = piVar4 + 1;
      piVar2 = piVar2 + 0x18;
      piVar1 = piVar1 + 1;
    } while (piVar6 != piVar4);
    piVar2 = piVar9 + param_2 * 0x18 + iVar7;
    piVar4 = piVar2 + iVar7;
    piVar1 = piVar9 + param_2 * 0x18;
  }
  piVar8[5] = (int)piVar1;
  piVar8[6] = (int)piVar2;
  *param_1 = piVar8;
  *param_4 = piVar4;
  return 0;
}
