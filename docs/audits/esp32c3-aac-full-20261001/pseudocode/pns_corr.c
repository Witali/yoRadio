/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: pns_corr @ ram:4300ba86
 * Types and parameter counts are inferred; verify against disassembly. */

void pns_corr(uint param_1,int param_2,int param_3,int param_4,int param_5,int param_6,int *param_7,
             int param_8,int *param_9)

{
  short *psVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int *piVar5;
  int iVar6;

  gp = &__global_pointer_;
  if (0 < param_4) {
    iVar6 = (param_6 - ((int)param_1 >> 2)) + -1;
    *param_7 = iVar6;
    iVar2 = *(int *)(hcb2_scale_mod_4 + (param_1 & 3) * 4);
    if (param_5 < 1) {
      while( true ) {
        piVar5 = param_7 + param_3;
        param_7 = piVar5 + param_3;
        if (param_4 == 1) break;
        *piVar5 = iVar6;
        if (param_4 + -2 == 0) {
          return;
        }
        *param_7 = iVar6;
        param_4 = param_4 + -2;
      }
    }
    else {
      iVar3 = param_5;
      piVar5 = param_9;
      iVar4 = param_8;
      while( true ) {
        do {
          psVar1 = (short *)(param_8 + 2);
          iVar3 = iVar3 + -1;
          param_8 = param_8 + 4;
          *param_9 = *psVar1 * iVar2;
          param_9 = param_9 + 1;
        } while (iVar3 != 0);
        param_4 = param_4 + -1;
        if (param_4 == 0) break;
        param_7 = param_7 + param_3;
        param_9 = piVar5 + param_5 + (param_2 - param_5);
        param_8 = iVar4 + param_5 * 4 + (param_2 - param_5) * 4;
        *param_7 = iVar6;
        iVar3 = param_5;
        piVar5 = param_9;
        iVar4 = param_8;
      }
    }
  }
  return;
}
