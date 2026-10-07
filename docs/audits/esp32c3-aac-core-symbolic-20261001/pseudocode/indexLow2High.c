/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: indexLow2High @ ram:43011732
 * Types and parameter counts are inferred; verify against disassembly. */

int indexLow2High(int param_1,int param_2,int param_3)

{
  gp = &__global_pointer_;
  if (param_3 != 0) {
    return param_2;
  }
  if (param_1 < 0) {
    if (param_2 < -param_1) {
      return param_2 * 3;
    }
  }
  else if (param_2 < param_1) {
    gp = &__global_pointer_;
    return param_2;
  }
  return param_2 * 2 - param_1;
}
