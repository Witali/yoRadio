/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: get_sbr_stopfreq @ ram:43008562
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
