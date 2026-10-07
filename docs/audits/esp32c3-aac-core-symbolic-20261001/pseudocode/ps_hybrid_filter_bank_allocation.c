/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: ps_hybrid_filter_bank_allocation @ ram:4300d5d4
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4
ps_hybrid_filter_bank_allocation
          (aac_hybrid_abi_t **hybrid,int param_2,int *param_3,undefined4 *param_4)

{
  int32_t **ppiVar1;
  int32_t **ppiVar2;
  int iVar3;
  int32_t **ppiVar4;
  aac_hybrid_abi_t *paVar5;
  int iVar6;
  int32_t **ppiVar7;
  int iVar8;
  aac_hybrid_abi_t *paVar9;
  int32_t **ppiVar10;

  gp = &__global_pointer_;
  paVar9 = (aac_hybrid_abi_t *)*param_4;
  *hybrid = (aac_hybrid_abi_t *)0x0;
  paVar5 = paVar9 + 1;
  paVar9->resolution = &paVar5->bands;
  ppiVar4 = (int32_t **)(&paVar5->bands + param_2);
  if (param_2 < 1) {
    ppiVar2 = ppiVar4 + param_2 + param_2;
    paVar9->imag_history = ppiVar4 + param_2;
    paVar9->bands = param_2;
    paVar9->real_history = ppiVar4;
    paVar9->history_length = 0xc;
    ppiVar4 = ppiVar2;
    ppiVar1 = ppiVar2;
  }
  else {
    iVar8 = 0;
    iVar6 = 0;
    do {
      iVar3 = *param_3;
      iVar6 = iVar6 + 1;
      param_3 = param_3 + 1;
      paVar5->bands = iVar3;
      if (((iVar3 - 2U & 0xfffffffd) != 0) && (iVar3 != 8)) {
        return 1;
      }
      if (iVar8 < iVar3) {
        iVar8 = iVar3;
      }
      paVar5 = (aac_hybrid_abi_t *)&paVar5->resolution;
    } while (param_2 != iVar6);
    ppiVar7 = ppiVar4 + param_2;
    ppiVar10 = ppiVar7 + param_2;
    paVar9->bands = param_2;
    paVar9->real_history = ppiVar4;
    paVar9->imag_history = ppiVar7;
    paVar9->history_length = 0xc;
    ppiVar1 = ppiVar7;
    ppiVar2 = ppiVar10;
    do {
      *ppiVar4 = (int32_t *)ppiVar2;
      *ppiVar1 = (int32_t *)(ppiVar2 + 0xc);
      ppiVar4 = ppiVar4 + 1;
      ppiVar2 = ppiVar2 + 0x18;
      ppiVar1 = ppiVar1 + 1;
    } while (ppiVar7 != ppiVar4);
    ppiVar2 = ppiVar10 + param_2 * 0x18 + iVar8;
    ppiVar4 = ppiVar2 + iVar8;
    ppiVar1 = ppiVar10 + param_2 * 0x18;
  }
  paVar9->real_scratch = (int32_t *)ppiVar1;
  paVar9->imag_scratch = (int32_t *)ppiVar2;
  *hybrid = paVar9;
  *param_4 = ppiVar4;
  return 0;
}
