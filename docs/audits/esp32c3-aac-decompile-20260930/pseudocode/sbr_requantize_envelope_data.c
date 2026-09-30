/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: sbr_requantize_envelope_data @ ram:4202a8f4
 * Types and parameter counts are inferred; verify against disassembly. */

void sbr_requantize_envelope_data(int *param_1)

{
  int *piVar1;
  int *piVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  uint *puVar7;
  uint *puVar8;

  gp = &__global_pointer_;
  iVar5 = *param_1;
  iVar4 = param_1[1];
  if (param_1[0x2b] == 0) {
    puVar7 = (uint *)(param_1 + 0x1c4);
    puVar8 = puVar7 + iVar5;
    if (0 < iVar5) {
      do {
        uVar3 = 0x40000000;
        puVar7[0x122] = ((int)*puVar7 >> 1) + 6;
        if ((*puVar7 & 1) != 0) {
          uVar3 = 0x5a827980;
        }
        *puVar7 = uVar3;
        puVar7 = puVar7 + 1;
      } while (puVar7 != puVar8);
    }
  }
  else if (0 < iVar5) {
    piVar1 = param_1 + 0x1c4;
    do {
      iVar6 = *piVar1;
      *piVar1 = 0x40000000;
      piVar2 = piVar1 + 1;
      piVar1[0x122] = iVar6 + 6;
      piVar1 = piVar2;
    } while (piVar2 != param_1 + 0x1c4 + iVar5);
  }
  if (0 < iVar4) {
    piVar1 = param_1 + 0x442;
    do {
      iVar5 = *piVar1;
      *piVar1 = 0x40000000;
      piVar2 = piVar1 + 1;
      piVar1[10] = 6 - iVar5;
      piVar1 = piVar2;
    } while (param_1 + 0x442 + iVar4 != piVar2);
  }
  return;
}
