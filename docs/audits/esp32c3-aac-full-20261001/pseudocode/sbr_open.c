/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_open @ ram:430134a8
 * Types and parameter counts are inferred; verify against disassembly. */

void sbr_open(int param_1,undefined4 param_2,undefined4 *param_3,int param_4)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  undefined4 *puVar6;

  gp = &__global_pointer_;
  puVar1 = param_3;
  do {
    memset(puVar1,0,0x64c0);
    puVar6 = &defaultHeader;
    puVar5 = puVar1 + 0x32;
    do {
      uVar2 = puVar6[1];
      uVar3 = puVar6[2];
      uVar4 = puVar6[3];
      *puVar5 = *puVar6;
      puVar5[1] = uVar2;
      puVar5[2] = uVar3;
      puVar5[3] = uVar4;
      puVar6 = puVar6 + 4;
      puVar5 = puVar5 + 4;
    } while (puVar6 != (undefined4 *)samp_rate_info);
    if (param_4 != 0 || 24000 < param_1) {
      puVar1[0x35] = 1;
    }
    uVar2 = init_sbr_dec(param_1,param_3[0x35],param_2,puVar1 + 2);
    *puVar1 = uVar2;
    puVar1[1] = 1;
    puVar1[0x1c5] = 1;
    puVar1 = puVar1 + 0x1930;
  } while (puVar1 != param_3 + 0x3260);
  return;
}
