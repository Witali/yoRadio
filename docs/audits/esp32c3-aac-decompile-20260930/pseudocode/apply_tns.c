/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: apply_tns @ ram:42040ce4
 * Types and parameter counts are inferred; verify against disassembly. */

void apply_tns(int param_1,int param_2,int param_3,int *param_4,int param_5,undefined4 param_6)

{
  short sVar1;
  int *piVar2;
  int *piVar3;
  int *piVar4;
  int *piVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  int iVar9;
  int *piVar10;
  int *piVar11;
  int iVar12;
  int iVar13;
  int *piVar14;
  int iVar15;
  int iVar16;
  int iVar17;
  undefined4 *puVar18;
  int iVar19;
  int iVar20;
  int iVar21;
  int iVar22;
  short *psVar23;
  short *psVar24;
  int *piVar26;
  int *piVar27;
  short *psVar25;

  gp = &__global_pointer_;
  iVar15 = *(int *)(param_3 + 0x10);
  iVar7 = *(int *)(param_3 + 0x30);
  piVar3 = param_4 + 0x41;
  puVar18 = (undefined4 *)(param_3 + 0x70);
  iVar19 = 0;
  piVar4 = param_4 + 9;
  do {
    param_4 = param_4 + 1;
    iVar21 = *param_4;
    piVar2 = piVar4;
    iVar17 = iVar21;
    if (0 < iVar21) {
      do {
        iVar12 = piVar2[4];
        if (0 < iVar12) {
          iVar6 = piVar2[3] - piVar2[2];
          if (0 < iVar6) {
            piVar5 = (int *)(piVar2[2] * 4 + param_1);
            if (param_5 == 0) {
              iVar12 = piVar2[1] - *piVar2;
              if (iVar12 < 1) {
                tns_ar_filter(piVar5,iVar6,piVar2[5],piVar3,piVar2[6]);
                iVar12 = piVar2[4];
              }
              else {
                iVar13 = param_2 + piVar2[1] * 4;
                iVar16 = *piVar2 + -1;
                iVar20 = 0x7fff;
                iVar9 = iVar13;
                iVar22 = iVar12;
                do {
                  piVar14 = (int *)(iVar9 + -4);
                  iVar9 = iVar9 + -4;
                  iVar22 = iVar22 + -1;
                  if (*piVar14 < iVar20) {
                    iVar20 = *piVar14;
                  }
                } while (iVar22 != 0);
                iVar22 = iVar12 + -1;
                piVar14 = (int *)(iVar13 + iVar22 * -4 + -4);
                psVar23 = (short *)*puVar18;
                iVar9 = 0;
                if (-1 < iVar16) {
                  iVar9 = (int)psVar23[iVar16];
                  psVar23 = psVar23 + iVar16 + 1;
                }
                psVar24 = psVar23;
                piVar26 = piVar5;
                piVar27 = piVar14;
                do {
                  psVar25 = psVar24 + 1;
                  sVar1 = *psVar24;
                  iVar9 = sVar1 - iVar9 >> 2;
                  if (0 < iVar9) {
                    uVar8 = *piVar27 - iVar20;
                    if (0x1f < (int)uVar8) {
                      uVar8 = 0x1f;
                    }
                    piVar10 = piVar26;
                    do {
                      piVar11 = piVar10 + 4;
                      piVar10[1] = piVar10[1] >> (uVar8 & 0x1f);
                      *piVar10 = *piVar10 >> (uVar8 & 0x1f);
                      piVar10[2] = piVar10[2] >> (uVar8 & 0x1f);
                      piVar10[3] = piVar10[3] >> (uVar8 & 0x1f);
                      piVar10 = piVar11;
                    } while (piVar26 + iVar9 * 4 != piVar11);
                    piVar26 = piVar26 + iVar9 * 4;
                  }
                  iVar9 = (int)sVar1;
                  psVar24 = psVar25;
                  piVar27 = piVar27 + 1;
                } while (psVar25 != psVar23 + iVar12);
                piVar14 = piVar14 + iVar12;
                iVar12 = tns_ar_filter(piVar5,iVar6,piVar2[5],piVar3,piVar2[6]);
                while( true ) {
                  piVar14[-1] = iVar20 - iVar12;
                  piVar14 = piVar14 + -1;
                  if (iVar22 == 0) break;
                  iVar22 = iVar22 + -1;
                }
                iVar12 = piVar2[4];
              }
            }
            else {
              tns_inv_filter(piVar5,iVar6,piVar2[5],piVar3,piVar2[6],iVar12,param_6);
              iVar12 = piVar2[4];
            }
          }
          piVar3 = piVar3 + iVar12;
        }
        iVar17 = iVar17 + -1;
        piVar2 = piVar2 + 7;
      } while (iVar17 != 0);
      piVar4 = piVar4 + (iVar21 + -1) * 7 + 7;
    }
    iVar19 = iVar19 + 1;
    param_1 = param_1 + iVar15 * 4;
    puVar18 = puVar18 + 1;
    param_2 = param_2 + iVar7 * 4;
  } while (iVar19 < *(int *)(param_3 + 4));
  return;
}
