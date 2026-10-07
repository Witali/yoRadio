/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: tns_inv_filter @ ram:43014452
 * Types and parameter counts are inferred; verify against disassembly. */

void tns_inv_filter(int *param_1,int param_2,int param_3,int *param_4,int param_5,int param_6,
                   int *param_7)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  int *piVar5;
  int iVar6;
  int iVar7;
  int iVar8;

  gp = &__global_pointer_;
  if (param_3 == -1) {
    param_1 = param_1 + param_2 + -1;
  }
  if (param_6 != 0) {
    param_7 = (int *)memset(param_7,0,param_6 << 2);
  }
  if (param_2 < 1) {
    return;
  }
  iVar3 = 0;
  iVar1 = param_6;
  piVar5 = param_4;
  piVar2 = param_7;
  iVar7 = 0;
  iVar8 = param_6;
  if (param_6 < 1) goto LAB_ram_4301451a;
LAB_ram_430144ae:
  do {
    do {
      iVar1 = iVar1 + -1;
      iVar3 = iVar3 + (int)((longlong)*piVar5 * (longlong)*piVar2 >> 0x25);
      piVar5 = piVar5 + 1;
      piVar2 = piVar2 + 1;
    } while (iVar1 != 0);
    iVar1 = (iVar8 + -1) * 4;
    piVar5 = param_7 + iVar8;
    while( true ) {
      piVar2 = (int *)((int)param_7 + iVar1);
      iVar1 = *param_1;
      iVar8 = iVar7 + 1;
      piVar5[-1] = iVar1;
      *param_1 = (iVar3 >> (param_5 - 5U & 0x1f)) + iVar1;
      param_2 = param_2 + -1;
      param_1 = param_1 + param_3;
      if (param_6 == iVar8) break;
      if (param_2 == 0) {
        return;
      }
      iVar3 = 0;
      iVar1 = iVar8;
      piVar5 = param_4;
      do {
        iVar4 = *piVar5;
        iVar6 = *piVar2;
        iVar1 = iVar1 + -1;
        piVar5 = piVar5 + 1;
        piVar2 = piVar2 + 1;
        iVar3 = iVar3 + (int)((longlong)iVar4 * (longlong)iVar6 >> 0x25);
      } while (iVar1 != 0);
      iVar1 = param_6 - iVar8;
      piVar5 = param_4 + iVar7 + 1;
      piVar2 = param_7;
      iVar7 = iVar8;
      iVar8 = iVar1;
      if (0 < iVar1) goto LAB_ram_430144ae;
LAB_ram_4301451a:
      iVar1 = -4;
      piVar5 = param_7;
    }
    iVar3 = 0;
    if (param_2 == 0) {
      return;
    }
    iVar7 = 0;
    iVar1 = param_6;
    piVar5 = param_4;
    piVar2 = param_7;
    iVar8 = param_6;
  } while( true );
}
