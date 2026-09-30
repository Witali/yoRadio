/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: ps_hybrid_analysis @ ram:4204789c
 * Types and parameter counts are inferred; verify against disassembly. */

void ps_hybrid_analysis(int param_1,int param_2,int param_3,int param_4,int *param_5,int param_6,
                       int param_7)

{
  int iVar1;
  void *dst_void;
  void *src_void;
  int iVar2;
  void *dst_void_00;
  int iVar3;
  int iVar4;
  undefined4 *puVar5;
  undefined4 *puVar6;

  gp = &__global_pointer_;
  if (*param_5 < 1) {
    return;
  }
  iVar1 = (param_7 + 0x20) * 4 + param_6;
  puVar6 = (undefined4 *)(param_1 + 0x600);
  puVar5 = (undefined4 *)(param_2 + 0x600);
  iVar3 = 0;
  iVar4 = 0;
  do {
    while( true ) {
      iVar2 = param_5[1];
      *(undefined4 *)(iVar1 + 0x30) = *puVar6;
      *(undefined4 *)(iVar1 + 0xe0) = *puVar5;
      iVar2 = *(int *)(iVar2 + iVar4 * 4);
      dst_void_00 = (void *)(param_3 + iVar3 * 4);
      dst_void = (void *)(iVar3 * 4 + param_4);
      if (iVar2 != 2) break;
      two_ch_filtering(iVar1,iVar1 + 0xb0,dst_void_00,dst_void);
      iVar4 = iVar4 + 1;
      iVar3 = iVar3 + 2;
      iVar1 = iVar1 + 0x160;
      puVar6 = puVar6 + 1;
      puVar5 = puVar5 + 1;
      if (*param_5 <= iVar4) {
        gp = &__global_pointer_;
        return;
      }
    }
    if (iVar2 == 8) {
      iVar3 = iVar3 + 6;
      eight_ch_filtering(iVar1,iVar1 + 0xb0,param_5[5],param_5[6],param_6);
      memmove(dst_void_00,(void *)param_5[5],0x10);
      iVar2 = param_5[5];
      src_void = (void *)param_5[6];
      *(int *)((int)dst_void_00 + 8) = *(int *)((int)dst_void_00 + 8) + *(int *)(iVar2 + 0x14);
      *(int *)((int)dst_void_00 + 0xc) = *(int *)((int)dst_void_00 + 0xc) + *(int *)(iVar2 + 0x10);
      *(undefined4 *)((int)dst_void_00 + 0x10) = *(undefined4 *)(iVar2 + 0x18);
      *(undefined4 *)((int)dst_void_00 + 0x14) = *(undefined4 *)(iVar2 + 0x1c);
      memmove(dst_void,src_void,0x10);
      iVar2 = param_5[6];
      *(int *)((int)dst_void + 8) = *(int *)((int)dst_void + 8) + *(int *)(iVar2 + 0x14);
      *(int *)((int)dst_void + 0xc) = *(int *)((int)dst_void + 0xc) + *(int *)(iVar2 + 0x10);
      *(undefined4 *)((int)dst_void + 0x10) = *(undefined4 *)(iVar2 + 0x18);
      *(undefined4 *)((int)dst_void + 0x14) = *(undefined4 *)(iVar2 + 0x1c);
    }
    iVar4 = iVar4 + 1;
    iVar1 = iVar1 + 0x160;
    puVar6 = puVar6 + 1;
    puVar5 = puVar5 + 1;
  } while (iVar4 < *param_5);
  return;
}
