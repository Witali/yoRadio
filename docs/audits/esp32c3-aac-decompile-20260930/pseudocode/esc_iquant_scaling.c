/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: esc_iquant_scaling @ ram:4205c01a
 * Types and parameter counts are inferred; verify against disassembly. */

void esc_iquant_scaling(int param_1,undefined4 param_2,int param_3,int param_4,int param_5,
                       int param_6)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;

  gp = &__global_pointer_;
  iVar3 = param_3 * 4;
  iVar1 = memset(param_2,0);
  if (0 < param_6) {
    uVar7 = 0x1b - param_4;
    uVar2 = param_3 - 1;
    if (param_5 == 0) {
      if (param_6 < 0x400) {
        if (-1 < (int)uVar2) {
          iVar1 = iVar1 + iVar3;
          iVar3 = param_3 * 2 + param_1;
          do {
            uVar4 = (uint)*(short *)(iVar3 + -2);
            uVar8 = (uint)*(short *)(iVar3 + -4);
            if (uVar4 != 0) {
              *(int *)(iVar1 + -4) =
                   (int)((*(uint *)(inverseQuantTable +
                                   ((uVar4 ^ (int)uVar4 >> 0xf) - ((int)uVar4 >> 0xf) & 0xffff) * 4)
                         >> (uVar7 & 0x1f)) * uVar4) >> 1;
            }
            if (uVar8 != 0) {
              *(int *)(iVar1 + -8) =
                   (int)((*(uint *)(inverseQuantTable +
                                   ((uVar8 ^ (int)uVar8 >> 0xf) - ((int)uVar8 >> 0xf) & 0xffff) * 4)
                         >> (uVar7 & 0x1f)) * uVar8) >> 1;
            }
            uVar4 = (uint)*(short *)(iVar3 + -6);
            uVar8 = (uint)*(short *)(iVar3 + -8);
            iVar3 = iVar3 + -8;
            if (uVar4 != 0) {
              *(int *)(iVar1 + -0xc) =
                   (int)((*(uint *)(inverseQuantTable +
                                   ((uVar4 ^ (int)uVar4 >> 0xf) - ((int)uVar4 >> 0xf) & 0xffff) * 4)
                         >> (uVar7 & 0x1f)) * uVar4) >> 1;
            }
            if (uVar8 != 0) {
              *(int *)(iVar1 + -0x10) =
                   (int)((*(uint *)(inverseQuantTable +
                                   ((uVar8 ^ (int)uVar8 >> 0xf) - ((int)uVar8 >> 0xf) & 0xffff) * 4)
                         >> (uVar7 & 0x1f)) * uVar8) >> 1;
            }
            iVar1 = iVar1 + -0x10;
          } while (param_1 + -8 + param_3 * 2 + (uVar2 >> 2) * -8 != iVar3);
          return;
        }
      }
      else if (0 < param_3) {
        iVar1 = iVar1 + iVar3;
        iVar3 = param_1 + param_3 * 2;
        uVar4 = 0x1d - param_4;
        do {
          uVar8 = (uint)*(short *)(iVar3 + -2);
          if (uVar8 != 0) {
            uVar5 = (uVar8 ^ (int)uVar8 >> 0xf) - ((int)uVar8 >> 0xf);
            uVar6 = uVar5 & 0xffff;
            if (uVar6 < 0x400) {
              *(int *)(iVar1 + -4) =
                   (int)((*(uint *)(inverseQuantTable + uVar6 * 4) >> (uVar7 & 0x1f)) * uVar8) >> 1;
            }
            else {
              *(int *)(iVar1 + -4) =
                   (int)((((uint)(*(int *)(inverseQuantTable + (uVar6 >> 3) * 4) << 1) >>
                          (uVar7 & 0x1f)) +
                         ((*(int *)(inverseQuantTable + (uVar6 >> 3) * 4 + 4) -
                          *(int *)(inverseQuantTable + (uVar6 >> 3) * 4)) * (uVar5 & 7) >>
                         (uVar4 & 0x1f))) * uVar8) >> 1;
            }
          }
          uVar8 = (uint)*(short *)(iVar3 + -4);
          if (uVar8 != 0) {
            uVar5 = (uVar8 ^ (int)uVar8 >> 0xf) - ((int)uVar8 >> 0xf);
            uVar6 = uVar5 & 0xffff;
            if (uVar6 < 0x400) {
              *(int *)(iVar1 + -8) =
                   (int)((*(uint *)(inverseQuantTable + uVar6 * 4) >> (uVar7 & 0x1f)) * uVar8) >> 1;
            }
            else {
              *(int *)(iVar1 + -8) =
                   (int)((((uint)(*(int *)(inverseQuantTable + (uVar6 >> 3) * 4) << 1) >>
                          (uVar7 & 0x1f)) +
                         ((*(int *)(inverseQuantTable + (uVar6 >> 3) * 4 + 4) -
                          *(int *)(inverseQuantTable + (uVar6 >> 3) * 4)) * (uVar5 & 7) >>
                         (uVar4 & 0x1f))) * uVar8) >> 1;
            }
          }
          uVar8 = (uint)*(short *)(iVar3 + -6);
          if (uVar8 != 0) {
            uVar5 = (uVar8 ^ (int)uVar8 >> 0xf) - ((int)uVar8 >> 0xf);
            uVar6 = uVar5 & 0xffff;
            if (uVar6 < 0x400) {
              *(int *)(iVar1 + -0xc) =
                   (int)((*(uint *)(inverseQuantTable + uVar6 * 4) >> (uVar7 & 0x1f)) * uVar8) >> 1;
            }
            else {
              *(int *)(iVar1 + -0xc) =
                   (int)((((uint)(*(int *)(inverseQuantTable + (uVar6 >> 3) * 4) << 1) >>
                          (uVar7 & 0x1f)) +
                         ((*(int *)(inverseQuantTable + (uVar6 >> 3) * 4 + 4) -
                          *(int *)(inverseQuantTable + (uVar6 >> 3) * 4)) * (uVar5 & 7) >>
                         (uVar4 & 0x1f))) * uVar8) >> 1;
            }
          }
          uVar8 = (uint)*(short *)(iVar3 + -8);
          if (uVar8 != 0) {
            uVar5 = (uVar8 ^ (int)uVar8 >> 0xf) - ((int)uVar8 >> 0xf);
            uVar6 = uVar5 & 0xffff;
            if (uVar6 < 0x400) {
              *(int *)(iVar1 + -0x10) =
                   (int)((*(uint *)(inverseQuantTable + uVar6 * 4) >> (uVar7 & 0x1f)) * uVar8) >> 1;
            }
            else {
              *(int *)(iVar1 + -0x10) =
                   (int)((((uint)(*(int *)(inverseQuantTable + (uVar6 >> 3) * 4) << 1) >>
                          (uVar7 & 0x1f)) +
                         ((*(int *)(inverseQuantTable + (uVar6 >> 3) * 4 + 4) -
                          *(int *)(inverseQuantTable + (uVar6 >> 3) * 4)) * (uVar5 & 7) >>
                         (uVar4 & 0x1f))) * uVar8) >> 1;
            }
          }
          iVar3 = iVar3 + -8;
          iVar1 = iVar1 + -0x10;
        } while (param_1 + -8 + param_3 * 2 + (uVar2 >> 2) * -8 != iVar3);
      }
    }
    else if (param_6 < 0x400) {
      if (-1 < (int)uVar2) {
        iVar1 = iVar1 + iVar3;
        param_5 = param_5 << 0x10;
        iVar3 = param_3 * 2 + param_1;
        do {
          uVar8 = (uint)*(short *)(iVar3 + -2);
          uVar4 = (uint)*(short *)(iVar3 + -4);
          if (uVar8 != 0) {
            *(int *)(iVar1 + -4) =
                 (int)((ulonglong)
                       ((longlong)
                        (int)((*(uint *)(inverseQuantTable +
                                        ((uVar8 ^ (int)uVar8 >> 0xf) - ((int)uVar8 >> 0xf) & 0xffff)
                                        * 4) >> (uVar7 & 0x1f)) * uVar8) * (longlong)param_5) >>
                      0x20) << 1;
          }
          if (uVar4 != 0) {
            *(int *)(iVar1 + -8) =
                 (int)((ulonglong)
                       ((longlong)
                        (int)((*(uint *)(inverseQuantTable +
                                        ((uVar4 ^ (int)uVar4 >> 0xf) - ((int)uVar4 >> 0xf) & 0xffff)
                                        * 4) >> (uVar7 & 0x1f)) * uVar4) * (longlong)param_5) >>
                      0x20) << 1;
          }
          uVar8 = (uint)*(short *)(iVar3 + -6);
          uVar4 = (uint)*(short *)(iVar3 + -8);
          iVar3 = iVar3 + -8;
          if (uVar8 != 0) {
            *(int *)(iVar1 + -0xc) =
                 (int)((ulonglong)
                       ((longlong)
                        (int)((*(uint *)(inverseQuantTable +
                                        ((uVar8 ^ (int)uVar8 >> 0xf) - ((int)uVar8 >> 0xf) & 0xffff)
                                        * 4) >> (uVar7 & 0x1f)) * uVar8) * (longlong)param_5) >>
                      0x20) << 1;
          }
          if (uVar4 != 0) {
            *(int *)(iVar1 + -0x10) =
                 (int)((ulonglong)
                       ((longlong)
                        (int)((*(uint *)(inverseQuantTable +
                                        ((uVar4 ^ (int)uVar4 >> 0xf) - ((int)uVar4 >> 0xf) & 0xffff)
                                        * 4) >> (uVar7 & 0x1f)) * uVar4) * (longlong)param_5) >>
                      0x20) << 1;
          }
          iVar1 = iVar1 + -0x10;
        } while (iVar3 != param_1 + -8 + param_3 * 2 + (uVar2 >> 2) * -8);
      }
    }
    else if (-1 < (int)uVar2) {
      iVar1 = iVar1 + iVar3;
      param_5 = param_5 << 0x10;
      iVar3 = param_1 + param_3 * 2;
      uVar4 = 0x1d - param_4;
      do {
        uVar8 = (uint)*(short *)(iVar3 + -2);
        if (uVar8 != 0) {
          uVar5 = (uVar8 ^ (int)uVar8 >> 0xf) - ((int)uVar8 >> 0xf);
          uVar6 = uVar5 & 0xffff;
          if (uVar6 < 0x400) {
            *(int *)(iVar1 + -4) =
                 (int)((ulonglong)
                       ((longlong)
                        (int)((*(uint *)(inverseQuantTable + uVar6 * 4) >> (uVar7 & 0x1f)) * uVar8)
                       * (longlong)param_5) >> 0x20) << 1;
          }
          else {
            *(int *)(iVar1 + -4) =
                 (int)((ulonglong)
                       ((longlong)
                        (int)((((uint)(*(int *)(inverseQuantTable + (uVar6 >> 3) * 4) << 1) >>
                               (uVar7 & 0x1f)) +
                              ((*(int *)(inverseQuantTable + (uVar6 >> 3) * 4 + 4) -
                               *(int *)(inverseQuantTable + (uVar6 >> 3) * 4)) * (uVar5 & 7) >>
                              (uVar4 & 0x1f))) * uVar8) * (longlong)param_5) >> 0x20) << 1;
          }
        }
        uVar8 = (uint)*(short *)(iVar3 + -4);
        if (uVar8 != 0) {
          uVar5 = (uVar8 ^ (int)uVar8 >> 0xf) - ((int)uVar8 >> 0xf);
          uVar6 = uVar5 & 0xffff;
          if (uVar6 < 0x400) {
            *(int *)(iVar1 + -8) =
                 (int)((ulonglong)
                       ((longlong)
                        (int)((*(uint *)(inverseQuantTable + uVar6 * 4) >> (uVar7 & 0x1f)) * uVar8)
                       * (longlong)param_5) >> 0x20) << 1;
          }
          else {
            *(int *)(iVar1 + -8) =
                 (int)((ulonglong)
                       ((longlong)
                        (int)((((uint)(*(int *)(inverseQuantTable + (uVar6 >> 3) * 4) << 1) >>
                               (uVar7 & 0x1f)) +
                              ((*(int *)(inverseQuantTable + (uVar6 >> 3) * 4 + 4) -
                               *(int *)(inverseQuantTable + (uVar6 >> 3) * 4)) * (uVar5 & 7) >>
                              (uVar4 & 0x1f))) * uVar8) * (longlong)param_5) >> 0x20) << 1;
          }
        }
        uVar8 = (uint)*(short *)(iVar3 + -6);
        if (uVar8 != 0) {
          uVar5 = (uVar8 ^ (int)uVar8 >> 0xf) - ((int)uVar8 >> 0xf);
          uVar6 = uVar5 & 0xffff;
          if (uVar6 < 0x400) {
            *(int *)(iVar1 + -0xc) =
                 (int)((ulonglong)
                       ((longlong)
                        (int)((*(uint *)(inverseQuantTable + uVar6 * 4) >> (uVar7 & 0x1f)) * uVar8)
                       * (longlong)param_5) >> 0x20) << 1;
          }
          else {
            *(int *)(iVar1 + -0xc) =
                 (int)((ulonglong)
                       ((longlong)
                        (int)((((uint)(*(int *)(inverseQuantTable + (uVar6 >> 3) * 4) << 1) >>
                               (uVar7 & 0x1f)) +
                              ((*(int *)(inverseQuantTable + (uVar6 >> 3) * 4 + 4) -
                               *(int *)(inverseQuantTable + (uVar6 >> 3) * 4)) * (uVar5 & 7) >>
                              (uVar4 & 0x1f))) * uVar8) * (longlong)param_5) >> 0x20) << 1;
          }
        }
        uVar8 = (uint)*(short *)(iVar3 + -8);
        if (uVar8 != 0) {
          uVar5 = (uVar8 ^ (int)uVar8 >> 0xf) - ((int)uVar8 >> 0xf);
          uVar6 = uVar5 & 0xffff;
          if (uVar6 < 0x400) {
            *(int *)(iVar1 + -0x10) =
                 (int)((ulonglong)
                       ((longlong)
                        (int)((*(uint *)(inverseQuantTable + uVar6 * 4) >> (uVar7 & 0x1f)) * uVar8)
                       * (longlong)param_5) >> 0x20) << 1;
          }
          else {
            *(int *)(iVar1 + -0x10) =
                 (int)((ulonglong)
                       ((longlong)
                        (int)((((uint)(*(int *)(inverseQuantTable + (uVar6 >> 3) * 4) << 1) >>
                               (uVar7 & 0x1f)) +
                              ((*(int *)(inverseQuantTable + (uVar6 >> 3) * 4 + 4) -
                               *(int *)(inverseQuantTable + (uVar6 >> 3) * 4)) * (uVar5 & 7) >>
                              (uVar4 & 0x1f))) * uVar8) * (longlong)param_5) >> 0x20) << 1;
          }
        }
        iVar3 = iVar3 + -8;
        iVar1 = iVar1 + -0x10;
      } while (iVar3 != param_1 + -8 + param_3 * 2 + (uVar2 >> 2) * -8);
    }
  }
  return;
}
