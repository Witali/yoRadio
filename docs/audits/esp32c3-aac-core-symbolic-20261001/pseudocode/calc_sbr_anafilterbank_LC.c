/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: calc_sbr_anafilterbank_LC @ ram:430017f2
 * Types and parameter counts are inferred; verify against disassembly. */

void calc_sbr_anafilterbank_LC(int *param_1,undefined4 param_2,int *param_3,int param_4)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  int *piVar5;
  int iVar6;
  int iVar7;

  gp = &__global_pointer_;
  calc_sbr_anafilterbank_LC_core(param_2,param_3);
  piVar1 = param_3 + 0x40;
  piVar4 = piVar1;
  piVar5 = param_3;
  do {
    iVar6 = piVar5[0x20];
    iVar7 = *piVar5;
    iVar3 = piVar5[0x21];
    iVar2 = piVar5[1];
    *piVar4 = iVar6 - iVar7 >> 1;
    piVar4[1] = iVar3 - iVar2 >> 1;
    piVar4[0x20] = iVar6 + iVar7;
    piVar4[0x21] = iVar3 + iVar2;
    iVar3 = piVar5[0x22];
    iVar7 = piVar5[2];
    iVar2 = piVar5[0x23];
    iVar6 = piVar5[3];
    piVar4[2] = iVar3 - iVar7 >> 1;
    piVar5 = piVar5 + 4;
    piVar4[0x22] = iVar3 + iVar7;
    piVar4[3] = iVar2 - iVar6 >> 1;
    piVar4[0x23] = iVar2 + iVar6;
    piVar4 = piVar4 + 4;
  } while (param_3 + 0x20 != piVar5);
  idct_32(piVar1);
  dst_32(param_3 + 0x60,param_3 + 0x80);
  iVar2 = 0;
  piVar4 = param_1;
  if (0 < param_4) {
    do {
      *piVar4 = *piVar1 + piVar1[0x20];
      iVar2 = iVar2 + 4;
      piVar4[1] = piVar1[0x21] - piVar1[1];
      piVar4[2] = -piVar1[0x22] - piVar1[2];
      piVar4[3] = piVar1[3] - piVar1[0x23];
      piVar1 = piVar1 + 4;
      piVar4 = piVar4 + 4;
    } while (iVar2 < param_4);
    if (param_4 == 0x20) {
      return;
    }
  }
  memset(param_1 + param_4,0,(0x20 - param_4) * 4);
  return;
}
