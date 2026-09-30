/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: sbr_get_header_data @ ram:42049468
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4 sbr_get_header_data(int *param_1,undefined4 param_2,int param_3)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int *piVar5;
  int *piVar6;
  int local_60 [7];
  int iStack_44;
  int iStack_40;
  int iStack_3c;
  int iStack_38;

  gp = &__global_pointer_;
  if (param_3 == 2) {
    piVar5 = local_60;
    piVar6 = param_1;
    do {
      iVar1 = piVar6[1];
      iVar2 = piVar6[2];
      iVar4 = piVar6[3];
      *piVar5 = *piVar6;
      piVar5[1] = iVar1;
      piVar5[2] = iVar2;
      piVar5[3] = iVar4;
      piVar6 = piVar6 + 4;
      piVar5 = piVar5 + 4;
    } while (piVar6 != param_1 + 0x10);
  }
  else {
    memset(local_60,0,0x40);
  }
  iVar1 = buf_getbits(param_2,1);
  param_1[4] = iVar1;
  iVar1 = buf_getbits(param_2,4);
  param_1[5] = iVar1;
  iVar1 = buf_getbits(param_2,4);
  param_1[6] = iVar1;
  iVar1 = buf_getbits(param_2,3);
  param_1[7] = iVar1;
  buf_getbits(param_2,2);
  iVar1 = buf_getbits(param_2,1);
  iVar2 = buf_getbits(param_2,1);
  if (iVar1 == 0) {
    iVar1 = 2;
    param_1[8] = 2;
    param_1[9] = 1;
  }
  else {
    iVar1 = buf_getbits(param_2,2);
    param_1[8] = iVar1;
    iVar1 = buf_getbits(param_2,1);
    param_1[9] = iVar1;
    iVar1 = buf_getbits(param_2,2);
  }
  param_1[10] = iVar1;
  if (iVar2 == 0) {
    iVar1 = 1;
    param_1[0xc] = 2;
    param_1[0xd] = 2;
    param_1[0xe] = 1;
  }
  else {
    iVar1 = buf_getbits(param_2,2);
    param_1[0xc] = iVar1;
    iVar1 = buf_getbits(param_2,2);
    param_1[0xd] = iVar1;
    iVar1 = buf_getbits(param_2,1);
    param_1[0xe] = iVar1;
    iVar1 = buf_getbits(param_2,1);
  }
  param_1[0xf] = iVar1;
  if ((((param_3 != 2) || (*param_1 = 0, local_60[5] != param_1[5])) || (local_60[6] != param_1[6]))
     || (((iStack_44 != param_1[7] || (iStack_40 != param_1[8])) ||
         ((iStack_3c != param_1[9] || (uVar3 = 0, iStack_38 != param_1[10])))))) {
    uVar3 = 1;
    *param_1 = 1;
  }
  return uVar3;
}
