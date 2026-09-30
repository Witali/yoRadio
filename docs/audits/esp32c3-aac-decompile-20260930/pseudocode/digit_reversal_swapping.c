/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: digit_reversal_swapping @ ram:4205704a
 * Types and parameter counts are inferred; verify against disassembly. */

void digit_reversal_swapping(int param_1,int param_2)

{
  undefined4 *puVar1;
  short *psVar2;
  short *psVar3;
  int iVar4;
  int iVar5;
  undefined4 *puVar6;
  undefined4 uVar7;
  undefined4 uVar8;

  gp = &__global_pointer_;
  psVar2 = &digit_reverse_swap_256;
  do {
    psVar3 = psVar2 + 2;
    iVar4 = *psVar2 * 4;
    puVar6 = (undefined4 *)(param_1 + iVar4);
    iVar5 = psVar2[1] * 4;
    uVar8 = *puVar6;
    puVar1 = (undefined4 *)(param_1 + iVar5 + 4);
    *puVar6 = *(undefined4 *)(param_1 + iVar5);
    uVar7 = puVar6[1];
    *(undefined4 *)(param_1 + iVar4 + 4) = *puVar1;
    *(undefined4 *)(param_1 + iVar5) = uVar8;
    *puVar1 = uVar7;
    puVar6 = (undefined4 *)(iVar5 + param_2);
    uVar8 = *puVar6;
    puVar1 = (undefined4 *)(iVar4 + 4 + param_2);
    *puVar6 = *(undefined4 *)(iVar4 + param_2);
    uVar7 = puVar6[1];
    *(undefined4 *)(iVar5 + 4 + param_2) = *puVar1;
    *(undefined4 *)(iVar4 + param_2) = uVar8;
    *puVar1 = uVar7;
    psVar2 = psVar3;
  } while (psVar3 != (short *)&UNK_ram_3c12e2dc);
  return;
}
