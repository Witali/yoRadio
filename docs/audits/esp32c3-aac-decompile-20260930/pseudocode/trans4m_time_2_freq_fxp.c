/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: trans4m_time_2_freq_fxp @ ram:4202c35e
 * Types and parameter counts are inferred; verify against disassembly. */

void trans4m_time_2_freq_fxp
               (int *param_1,int param_2,int param_3,int param_4,int *param_5,undefined4 param_6)

{
  short sVar1;
  short sVar2;
  short *psVar3;
  int *piVar4;
  int *piVar5;
  int *piVar6;
  int *piVar7;
  int iVar8;
  uint uVar9;
  short *psVar10;
  undefined1 *apuStack_20 [6];

  gp = &__global_pointer_;
  apuStack_20[2] = Short_Window_sine_fxp;
  apuStack_20[3] = Short_Window_KBD_fxp;
  apuStack_20[0] = Long_Window_sine_fxp;
  apuStack_20[1] = Long_Window_KBD_fxp;
  iVar8 = *param_5;
  if (param_2 != 2) {
    *param_5 = 0xf - iVar8;
    uVar9 = iVar8 - 1;
    piVar5 = param_1 + 0x400;
    if (param_2 == 1) {
      psVar3 = (short *)apuStack_20[param_3];
      piVar4 = param_1;
      do {
        sVar1 = *psVar3;
        sVar2 = psVar3[0x200];
        piVar6 = piVar4 + 1;
        psVar3 = psVar3 + 1;
        *piVar4 = (int)((ulonglong)((longlong)((int)sVar1 << 0x10) * (longlong)*piVar4) >> 0x20) >>
                  (uVar9 & 0x1f);
        piVar4[0x200] =
             (int)((ulonglong)((longlong)((int)sVar2 << 0x10) * (longlong)piVar4[0x200]) >> 0x20) >>
             (uVar9 & 0x1f);
        piVar4 = piVar6;
      } while (param_1 + 0x200 != piVar6);
      if (uVar9 != 0) {
        do {
          piVar4 = piVar5 + 2;
          *piVar5 = *piVar5 >> (uVar9 & 0x1f);
          piVar5[1] = piVar5[1] >> (uVar9 & 0x1f);
          piVar5 = piVar4;
        } while (piVar4 != param_1 + 0x5c0);
      }
      psVar3 = (short *)(apuStack_20[param_4 + 2] + 0xfe);
      piVar5 = param_1 + 0x5c0;
      do {
        sVar1 = *psVar3;
        sVar2 = psVar3[-0x40];
        piVar4 = piVar5 + 1;
        psVar3 = psVar3 + -1;
        *piVar5 = (int)((ulonglong)((longlong)((int)sVar1 << 0x10) * (longlong)*piVar5) >> 0x20) >>
                  (uVar9 & 0x1f);
        piVar5[0x40] = (int)((ulonglong)((longlong)((int)sVar2 << 0x10) * (longlong)piVar5[0x40]) >>
                            0x20) >> (uVar9 & 0x1f);
        piVar5 = piVar4;
      } while (param_1 + 0x600 != piVar4);
      memset(param_1 + 0x640,0,0x700);
    }
    else if (param_2 == 3) {
      memset(param_1,0,0x700);
      psVar3 = (short *)apuStack_20[param_3 + 2];
      piVar4 = param_1 + 0x1c0;
      do {
        sVar1 = *psVar3;
        sVar2 = psVar3[0x40];
        piVar6 = piVar4 + 1;
        psVar3 = psVar3 + 1;
        *piVar4 = (int)((ulonglong)((longlong)((int)sVar1 << 0x10) * (longlong)*piVar4) >> 0x20) >>
                  (uVar9 & 0x1f);
        piVar4[0x40] = (int)((ulonglong)((longlong)((int)sVar2 << 0x10) * (longlong)piVar4[0x40]) >>
                            0x20) >> (uVar9 & 0x1f);
        piVar4 = piVar6;
      } while (param_1 + 0x200 != piVar6);
      if (uVar9 != 0) {
        piVar4 = param_1 + 0x240;
        do {
          piVar6 = piVar4 + 2;
          *piVar4 = *piVar4 >> (uVar9 & 0x1f);
          piVar4[1] = piVar4[1] >> (uVar9 & 0x1f);
          piVar4 = piVar6;
        } while (piVar6 != piVar5);
      }
      psVar3 = (short *)(apuStack_20[param_4] + 0x7fe);
      do {
        sVar1 = *psVar3;
        sVar2 = psVar3[-0x200];
        piVar4 = piVar5 + 1;
        psVar3 = psVar3 + -1;
        *piVar5 = (int)((ulonglong)((longlong)((int)sVar1 << 0x10) * (longlong)*piVar5) >> 0x20) >>
                  (uVar9 & 0x1f);
        piVar5[0x200] =
             (int)((ulonglong)((longlong)((int)sVar2 << 0x10) * (longlong)piVar5[0x200]) >> 0x20) >>
             (uVar9 & 0x1f);
        piVar5 = piVar4;
      } while (param_1 + 0x600 != piVar4);
    }
    else {
      psVar10 = (short *)apuStack_20[param_3];
      psVar3 = (short *)(apuStack_20[param_4] + 0x7fe);
      piVar4 = piVar5;
      piVar6 = param_1;
      do {
        sVar1 = *psVar10;
        sVar2 = *psVar3;
        piVar7 = piVar6 + 1;
        psVar10 = psVar10 + 1;
        *piVar6 = (int)((ulonglong)((longlong)((int)sVar1 << 0x10) * (longlong)*piVar6) >> 0x20) >>
                  (uVar9 & 0x1f);
        *piVar4 = (int)((ulonglong)((longlong)((int)sVar2 << 0x10) * (longlong)*piVar4) >> 0x20) >>
                  (uVar9 & 0x1f);
        psVar3 = psVar3 + -1;
        piVar4 = piVar4 + 1;
        piVar6 = piVar7;
      } while (piVar7 != piVar5);
    }
    iVar8 = mdct_fxp(param_1,param_6,0x800);
    *param_5 = *param_5 + iVar8;
  }
  return;
}
