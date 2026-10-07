/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: differential_Decoding @ ram:420471ec
 * Types and parameter counts are inferred; verify against disassembly. */

void differential_Decoding
               (int param_1,int *param_2,int *param_3,int param_4,int param_5,int param_6,
               int param_7,int param_8)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  undefined4 *puVar4;
  int iVar5;

  gp = &__global_pointer_;
  if (param_1 != 1) {
    iVar3 = memset(param_2,0,param_5 << 2);
    if ((param_6 == 2) && (iVar1 = param_5 * 2 + -1, 0 < iVar1)) {
      puVar4 = (undefined4 *)(param_5 * 8 + iVar3);
      do {
        iVar5 = iVar1 >> 1;
        iVar1 = iVar1 + -1;
        puVar4 = puVar4 + -1;
        *puVar4 = *(undefined4 *)(iVar5 * 4 + iVar3);
      } while (iVar1 != 0);
      return;
    }
    return;
  }
  if (param_4 == 0) {
    iVar1 = *param_2;
    iVar3 = param_8;
    if ((iVar1 < param_8) && (iVar3 = iVar1, iVar1 < param_7)) {
      iVar3 = param_7;
    }
    *param_2 = iVar3;
    piVar2 = param_2 + 1;
    if (1 < param_5) {
      do {
        iVar1 = *piVar2 + iVar3;
        iVar3 = param_8;
        if ((iVar1 < param_8) && (iVar3 = param_7, param_7 < iVar1)) {
          iVar3 = iVar1;
        }
        *piVar2 = iVar3;
        piVar2 = piVar2 + 1;
      } while (piVar2 != param_2 + param_5);
    }
  }
  else {
    if (param_6 == 1) {
      if (param_5 < 1) {
        return;
      }
      piVar2 = param_2 + param_5;
      do {
        iVar1 = *param_3;
        param_3 = param_3 + 1;
        iVar1 = *param_2 + iVar1;
        iVar3 = param_8;
        if ((iVar1 < param_8) && (iVar3 = iVar1, iVar1 < param_7)) {
          iVar3 = param_7;
        }
        *param_2 = iVar3;
        param_2 = param_2 + 1;
      } while (piVar2 != param_2);
      return;
    }
    piVar2 = param_2;
    if (0 < param_5) {
      do {
        iVar1 = *param_3;
        param_3 = param_3 + 2;
        iVar1 = iVar1 + *piVar2;
        iVar3 = param_8;
        if ((iVar1 < param_8) && (iVar3 = param_7, param_7 < iVar1)) {
          iVar3 = iVar1;
        }
        *piVar2 = iVar3;
        piVar2 = piVar2 + 1;
      } while (param_2 + param_5 != piVar2);
    }
  }
  if ((param_6 == 2) && (iVar3 = param_5 * 2 + -1, 0 < iVar3)) {
    piVar2 = param_2 + param_5 * 2;
    do {
      iVar1 = iVar3 >> 1;
      iVar3 = iVar3 + -1;
      piVar2 = piVar2 + -1;
      *piVar2 = param_2[iVar1];
    } while (iVar3 != 0);
    return;
  }
  return;
}
