/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: raw_stream_parameter_setup @ ram:4300f4e4
 * Types and parameter counts are inferred; verify against disassembly. */

void raw_stream_parameter_setup(undefined4 param_1,int param_2,int param_3)

{
  undefined4 *puVar1;
  int iVar2;

  gp = &__global_pointer_;
  puVar1 = *(undefined4 **)(param_3 + 0x2c);
  param_2 = param_2 - (uint)(param_2 != 0);
  puVar1[1] = param_1;
  *puVar1 = 1;
  puVar1[3] = 1;
  puVar1[4] = param_2;
  puVar1[0xd5] = 0;
  puVar1[0x14] = 0;
  puVar1[0xc9] = 0;
  puVar1[0xcc] = 0;
  puVar1[0xcf] = 0;
  set_mc_info(param_3 + 0x8c,param_1,0,param_2,param_3 + 0x78,param_3 + 0x30);
  iVar2 = *(int *)(param_3 + 0x2c);
  *(undefined4 *)(iVar2 + 0x350) = 0;
  *(undefined4 *)(iVar2 + 0x34c) = 0;
  return;
}
