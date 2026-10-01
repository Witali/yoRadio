/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: PVMP4AudioDecoderResetBuffer @ ram:4300f77e
 * Types and parameter counts are inferred; verify against disassembly. */

void PVMP4AudioDecoderResetBuffer(undefined4 *param_1)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  int iVar5;

  gp = &__global_pointer_;
  memset(param_1 + 0x55c,0,0x1000);
  memset(param_1 + 0xe89,0,0x1000);
  iVar1 = param_1[0x2296];
  if (((iVar1 != 0) && (*(int *)(iVar1 + 0xc980) == 0)) && (*(char *)(param_1 + 2) != '\0')) {
    param_1[0x54f7] = iVar1 + 0xc988;
    memset(param_1 + 0x3c,0,0x240);
    memset(param_1 + 0x2cc,0,0x240);
    memset(iVar1 + 0x42c0,0,0x900);
    *(undefined4 *)(iVar1 + 0x1160) = 0;
    *(undefined4 *)(iVar1 + 0x1164) = 0;
    *(undefined4 *)(iVar1 + 0x1168) = 0;
    *(undefined4 *)(iVar1 + 0x116c) = 0;
    *(undefined4 *)(iVar1 + 0x1170) = 0;
    *(undefined4 *)(iVar1 + 0x1174) = 0;
    *(undefined4 *)(iVar1 + 0x1178) = 0;
    *(undefined4 *)(iVar1 + 0x117c) = 0;
    *(undefined4 *)(iVar1 + 0x1180) = 0;
    *(undefined4 *)(iVar1 + 0x1184) = 0;
    memset(param_1 + 0x969,0,0x240);
    memset(param_1 + 0xbf9,0,0x240);
    memset(iVar1 + 0xa780,0,0x900);
    *(undefined4 *)(iVar1 + 0x7620) = 0;
    *(undefined4 *)(iVar1 + 0x7624) = 0;
    *(undefined4 *)(iVar1 + 0x7628) = 0;
    *(undefined4 *)(iVar1 + 0x762c) = 0;
    *(undefined4 *)(iVar1 + 0x7630) = 0;
    *(undefined4 *)(iVar1 + 0x7634) = 0;
    *(undefined4 *)(iVar1 + 0x7638) = 0;
    *(undefined4 *)(iVar1 + 0x763c) = 0;
    *(undefined4 *)(iVar1 + 0x7640) = 0;
    *(undefined4 *)(iVar1 + 0x7644) = 0;
    iVar5 = iVar1 + 0x11b8;
    do {
      iVar5 = memset(iVar5,0,0x80);
      iVar5 = iVar5 + 0x80;
    } while (iVar5 != iVar1 + 0x15b8);
    *(undefined4 *)(iVar1 + 0x11a0) = 0;
    *(undefined4 *)(iVar1 + 0x11a4) = 0;
    *(undefined4 *)(iVar1 + 0x11a8) = 0;
    *(undefined4 *)(iVar1 + 0x11ac) = 0;
    *(undefined4 *)(iVar1 + 0x11b0) = 0;
    *(undefined4 *)(iVar1 + 0x11b4) = 0;
    iVar5 = iVar1 + 0x4cc0;
    do {
      memset(iVar5,0,0x100);
      iVar2 = iVar5 + 0x500;
      iVar5 = iVar5 + 0x100;
      memset(iVar2,0,0x100);
    } while (iVar1 + 0x51c0 != iVar5);
    memset(iVar1 + 0x3e40,0,0x480);
    memset(iVar1 + 0x39bc,0,0x480);
    puVar3 = (undefined4 *)param_1[0x2297];
    if (puVar3[1] == 1) {
      iVar5 = iVar1 + 0x7678;
      do {
        iVar5 = memset(iVar5,0,0x80);
        iVar5 = iVar5 + 0x80;
      } while (iVar1 + 0x7a78 != iVar5);
      memset(iVar1 + 0xa300,0,0x480);
      iVar5 = iVar1 + 0xb180;
      *(undefined4 *)(iVar1 + 0x7660) = 0;
      *(undefined4 *)(iVar1 + 0x7664) = 0;
      *(undefined4 *)(iVar1 + 0x7668) = 0;
      *(undefined4 *)(iVar1 + 0x766c) = 0;
      *(undefined4 *)(iVar1 + 0x7670) = 0;
      *(undefined4 *)(iVar1 + 0x7674) = 0;
      do {
        memset(iVar5,0,0x100);
        iVar2 = iVar5 + 0x500;
        iVar5 = iVar5 + 0x100;
        memset(iVar2,0,0x100);
      } while (iVar1 + 0xb680 != iVar5);
      puVar3 = (undefined4 *)param_1[0x2297];
    }
    else if (param_1[0x30] == 1) {
      iVar1 = 0;
      do {
        puVar3 = *(undefined4 **)(*(int *)(*(int *)(param_1[0x54f7] + 0x1fc) + 0xc) + iVar1);
        *puVar3 = 0;
        puVar3[4] = 0;
        puVar3[1] = 0;
        puVar3[2] = 0;
        puVar3[3] = 0;
        puVar3[5] = 0;
        puVar3[6] = 0;
        puVar3[7] = 0;
        puVar3[8] = 0;
        puVar3[9] = 0;
        puVar3[10] = 0;
        puVar3[0xb] = 0;
        puVar3 = *(undefined4 **)(*(int *)(*(int *)(param_1[0x54f7] + 0x1fc) + 0x10) + iVar1);
        iVar1 = iVar1 + 4;
        *puVar3 = 0;
        puVar3[1] = 0;
        puVar3[2] = 0;
        puVar3[3] = 0;
        puVar3[4] = 0;
        puVar3[5] = 0;
        puVar3[6] = 0;
        puVar3[7] = 0;
        puVar3[8] = 0;
        puVar3[9] = 0;
        puVar3[10] = 0;
        puVar3[0xb] = 0;
      } while (iVar1 != 0xc);
      puVar3 = (undefined4 *)param_1[0x2297];
    }
    iVar1 = param_1[0x2296];
    *(undefined4 *)(iVar1 + 4) = 1;
    *(undefined4 *)(iVar1 + 0x64c4) = 1;
    puVar4 = *(undefined4 **)(iVar1 + 0xc984);
    *puVar3 = 0;
    *(undefined4 *)(iVar1 + 0xc980) = 1;
    *puVar4 = 0;
  }
  *param_1 = 0;
  *(undefined1 *)(param_1 + 2) = *(undefined1 *)(param_1 + 0x22a0);
  return;
}
