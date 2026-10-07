/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: synthesis_sub_band_LC @ ram:42049790
 * Types and parameter counts are inferred; verify against disassembly. */

void synthesis_sub_band_LC(int param_1,undefined4 *param_2)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int *piVar4;
  int iVar5;
  undefined4 *puVar6;
  undefined4 *puVar7;
  undefined4 *puVar8;

  gp = &__global_pointer_;
  synthesis_sub_band_LC_core2(param_2,param_1,CosTable_48);
  pv_split_LC(param_2,param_1 + 0x80);
  dct_16(param_2,1);
  dct_16(param_1 + 0x80,1);
  iVar5 = *(int *)(param_1 + 0xbc);
  param_2[0x1f] = iVar5;
  piVar4 = (int *)(param_1 + 0xb8);
  puVar6 = param_2 + 0xf;
  puVar8 = param_2 + 0x1e;
  do {
    iVar1 = *piVar4;
    uVar2 = *puVar6;
    puVar8[-1] = iVar5 + iVar1;
    *puVar8 = uVar2;
    iVar3 = piVar4[-1];
    uVar2 = puVar6[-1];
    puVar7 = puVar6 + -3;
    puVar8[-3] = iVar1 + iVar3;
    puVar8[-2] = uVar2;
    iVar5 = piVar4[-2];
    puVar8[-4] = puVar6[-2];
    puVar8[-5] = iVar3 + iVar5;
    piVar4 = piVar4 + -3;
    puVar6 = puVar7;
    puVar8 = puVar8 + -6;
  } while (param_2 != puVar7);
  pv_split_LC(param_1,param_1 + 0x80);
  dct_16(param_1,1);
  dct_16(param_1 + 0x80,1);
  synthesis_sub_band_LC_core1(param_2,param_1,param_2);
  return;
}
