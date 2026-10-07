/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: get_sbr_stopfreq @ ram:42058738
 * Types and parameter counts are inferred; verify against disassembly. */

undefined1 get_sbr_stopfreq(int param_1,int param_2)

{
  uint uVar1;

  gp = &__global_pointer_;
  if (param_1 == 24000) {
    uVar1 = 2;
  }
  else if (param_1 < 0x5dc1) {
    uVar1 = 4;
    if ((param_1 != 16000) && (uVar1 = 3, param_1 != 0x5622)) {
      uVar1 = 1;
    }
  }
  else {
    uVar1 = 2;
    if (param_1 != 32000) {
      uVar1 = (uint)(param_1 != 48000);
    }
  }
  return sbr_stopfreq_tbl[param_2 + uVar1 * 0xd];
}
