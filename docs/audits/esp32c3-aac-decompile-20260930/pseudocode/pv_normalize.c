/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: pv_normalize @ ram:420484c2
 * Types and parameter counts are inferred; verify against disassembly. */

int pv_normalize(uint param_1)

{
  int iVar1;

  gp = &__global_pointer_;
  if ((int)param_1 < 0x10000000) {
    if ((int)param_1 < 0x1000000) {
      if ((int)param_1 < 0x10000) {
        if ((int)param_1 < 0x100) {
          if ((int)param_1 < 0x10) {
            param_1 = param_1 << 0x1b;
            iVar1 = 0x1b;
          }
          else {
            param_1 = param_1 << 0x17;
            iVar1 = 0x17;
          }
        }
        else if ((int)param_1 < 0x1000) {
          param_1 = param_1 << 0x13;
          iVar1 = 0x13;
        }
        else {
          param_1 = param_1 << 0xf;
          iVar1 = 0xf;
        }
      }
      else if ((int)param_1 < 0x100000) {
        param_1 = param_1 << 0xb;
        iVar1 = 0xb;
      }
      else {
        param_1 = param_1 << 7;
        iVar1 = 7;
      }
    }
    else {
      param_1 = param_1 << 3;
      iVar1 = 3;
    }
    param_1 = param_1 & 0x78000000;
    if (param_1 != 0x18000000) {
      if (0x18000000 < param_1) goto LAB_ram_42048524;
      if (param_1 == 0x8000000) {
        return iVar1 + 3;
      }
      if (param_1 != 0x10000000) {
        return iVar1;
      }
    }
  }
  else {
    param_1 = param_1 & 0x78000000;
    iVar1 = 0;
    if ((param_1 != 0x18000000) && (0x18000000 < param_1)) {
LAB_ram_42048524:
      if (param_1 != 0x30000000) {
        if (param_1 < 0x30000001) {
          if ((int)param_1 >> 0x1c != 2) {
            return iVar1;
          }
        }
        else if (param_1 != 0x38000000) {
          return iVar1;
        }
      }
      return iVar1 + 1;
    }
  }
  return iVar1 + 2;
}
