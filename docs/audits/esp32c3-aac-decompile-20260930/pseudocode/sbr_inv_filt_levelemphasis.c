/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: sbr_inv_filt_levelemphasis @ ram:4202a4a0
 * Types and parameter counts are inferred; verify against disassembly. */

void sbr_inv_filt_levelemphasis(int *param_1,int *param_2,int param_3,int *param_4,int *param_5)

{
  int *piVar1;
  int iVar2;
  int iVar3;

  gp = &__global_pointer_;
  if (param_3 < 1) {
    return;
  }
  piVar1 = param_1 + param_3;
LAB_ram_4202a54c:
  do {
    iVar2 = *param_1;
    if (iVar2 == 2) {
      iVar2 = *param_5;
      if (iVar2 < 0x1cccccc1) {
        iVar2 = ((uint)(iVar2 * 0x3000000) >> 0x1d) +
                (((uint)((uint)(iVar2 * 3) < (uint)(iVar2 * 2)) + (iVar2 >> 0x1f) * 2) * 0x1000000 +
                ((uint)(iVar2 * 3) >> 8)) * 8 + 0x1a19998e;
      }
      else {
        iVar2 = (iVar2 >> 2) + 0x15999990;
      }
    }
    else if (iVar2 == 3) {
      iVar2 = *param_5;
      if (iVar2 < 0x1f5c2901) {
        iVar2 = ((uint)(iVar2 * 0x3000000) >> 0x1d) +
                (((uint)((uint)(iVar2 * 3) < (uint)(iVar2 * 2)) + (iVar2 >> 0x1f) * 2) * 0x1000000 +
                ((uint)(iVar2 * 3) >> 8)) * 8 + 0x1c6b8528;
      }
      else {
        iVar2 = (iVar2 >> 2) + 0x17851ec0;
      }
    }
    else if (iVar2 == 1) {
      if (*param_2 == 0) {
        iVar2 = *param_5;
        if (iVar2 < 0x13333341) {
          iVar2 = ((uint)(iVar2 * 0x3000000) >> 0x1d) +
                  (((uint)((uint)(iVar2 * 3) < (uint)(iVar2 * 2)) + (iVar2 >> 0x1f) * 2) * 0x1000000
                  + ((uint)(iVar2 * 3) >> 8)) * 8 + 0x11666672;
        }
        else {
          iVar2 = (iVar2 >> 2) + 0xe666670;
        }
      }
      else {
        iVar2 = *param_5;
        if (iVar2 < 0x18000001) {
          iVar2 = ((uint)(iVar2 * 0x3000000) >> 0x1d) +
                  (((uint)((uint)(iVar2 * 3) < (uint)(iVar2 * 2)) + (iVar2 >> 0x1f) * 2) * 0x1000000
                  + ((uint)(iVar2 * 3) >> 8)) * 8 + 0x15c00000;
        }
        else {
          iVar2 = (iVar2 >> 2) + 0x12000000;
        }
      }
    }
    else {
      iVar2 = *param_5;
      iVar3 = *(int *)(InvFiltFactors + (uint)(*param_2 == 1) * 4);
      if (iVar3 < iVar2) {
        iVar2 = iVar3 * 3 + iVar2 >> 2;
      }
      else {
        iVar2 = ((uint)(iVar2 * 0x3000000) >> 0x1d) +
                (((uint)((uint)(iVar2 * 3) < (uint)(iVar2 * 2)) + (iVar2 >> 0x1f) * 2) * 0x1000000 +
                ((uint)(iVar2 * 3) >> 8)) * 8 +
                ((uint)(iVar3 * 0x1d000000) >> 0x1d) +
                (int)((ulonglong)((longlong)iVar3 * 0x1d000000) >> 0x20) * 8;
      }
      if (iVar2 < 0x800000) {
        *param_4 = 0;
        param_1 = param_1 + 1;
        param_4 = param_4 + 1;
        param_5 = param_5 + 1;
        param_2 = param_2 + 1;
        if (param_1 == piVar1) {
          return;
        }
        goto LAB_ram_4202a54c;
      }
    }
    if (0x1fe00000 < iVar2) {
      iVar2 = 0x1fe00000;
    }
    *param_4 = iVar2;
    param_1 = param_1 + 1;
    param_4 = param_4 + 1;
    param_5 = param_5 + 1;
    param_2 = param_2 + 1;
    if (param_1 == piVar1) {
      gp = &__global_pointer_;
      return;
    }
  } while( true );
}
