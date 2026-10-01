/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: limitMinMax @ ram:4300ce28
 * Types and parameter counts are inferred; verify against disassembly. */

int limitMinMax(int param_1,int param_2,int param_3)

{
  gp = &__global_pointer_;
  if (param_3 <= param_1) {
    return param_3;
  }
  if (param_2 <= param_1) {
    return param_1;
  }
  return param_2;
}
