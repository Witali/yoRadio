/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: apply_tns @ ram:43000996
 * Types and parameter counts are inferred; verify against disassembly. */

void apply_tns(int param_1,int param_2,aac_analysis_window_t *window,aac_analysis_tns_t *tns,
              int param_5,undefined4 param_6)

{
  short sVar1;
  int iVar2;
  aac_analysis_tns_filter_t *paVar3;
  int32_t *piVar4;
  aac_analysis_tns_filter_t *paVar5;
  int *piVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  int iVar10;
  int *piVar11;
  int *piVar12;
  uint32_t uVar13;
  int iVar14;
  int *piVar15;
  int iVar16;
  int iVar17;
  int iVar18;
  int16_t **ppiVar19;
  int iVar20;
  int iVar21;
  int iVar22;
  int iVar23;
  short *psVar24;
  short *psVar25;
  int *piVar27;
  int *piVar28;
  short *psVar26;

  gp = &__global_pointer_;
  iVar16 = window->coefficients_per_window[0];
  iVar8 = window->bands_per_window[0];
  piVar4 = tns->lpc;
  ppiVar19 = window->band_top;
  iVar20 = 0;
  paVar5 = tns->filter;
  do {
    tns = (aac_analysis_tns_t *)tns->filter_count;
    iVar22 = *(int *)tns;
    paVar3 = paVar5;
    iVar18 = iVar22;
    if (0 < iVar22) {
      do {
        uVar13 = paVar3->order;
        if (0 < (int)uVar13) {
          iVar7 = paVar3->stop_coefficient - paVar3->start_coefficient;
          if (0 < iVar7) {
            piVar6 = (int *)(paVar3->start_coefficient * 4 + param_1);
            if (param_5 == 0) {
              iVar2 = paVar3->stop_band - paVar3->start_band;
              if (iVar2 < 1) {
                tns_ar_filter(piVar6,iVar7,paVar3->direction,piVar4,paVar3->lpc_q);
                uVar13 = paVar3->order;
              }
              else {
                iVar14 = param_2 + paVar3->stop_band * 4;
                iVar17 = paVar3->start_band + -1;
                iVar21 = 0x7fff;
                iVar10 = iVar14;
                iVar23 = iVar2;
                do {
                  piVar15 = (int *)(iVar10 + -4);
                  iVar10 = iVar10 + -4;
                  iVar23 = iVar23 + -1;
                  if (*piVar15 < iVar21) {
                    iVar21 = *piVar15;
                  }
                } while (iVar23 != 0);
                iVar23 = iVar2 + -1;
                piVar15 = (int *)(iVar14 + iVar23 * -4 + -4);
                psVar24 = *ppiVar19;
                iVar10 = 0;
                if (-1 < iVar17) {
                  iVar10 = (int)psVar24[iVar17];
                  psVar24 = psVar24 + iVar17 + 1;
                }
                psVar25 = psVar24;
                piVar27 = piVar6;
                piVar28 = piVar15;
                do {
                  psVar26 = psVar25 + 1;
                  sVar1 = *psVar25;
                  iVar10 = sVar1 - iVar10 >> 2;
                  if (0 < iVar10) {
                    uVar9 = *piVar28 - iVar21;
                    if (0x1f < (int)uVar9) {
                      uVar9 = 0x1f;
                    }
                    piVar11 = piVar27;
                    do {
                      piVar12 = piVar11 + 4;
                      piVar11[1] = piVar11[1] >> (uVar9 & 0x1f);
                      *piVar11 = *piVar11 >> (uVar9 & 0x1f);
                      piVar11[2] = piVar11[2] >> (uVar9 & 0x1f);
                      piVar11[3] = piVar11[3] >> (uVar9 & 0x1f);
                      piVar11 = piVar12;
                    } while (piVar27 + iVar10 * 4 != piVar12);
                    piVar27 = piVar27 + iVar10 * 4;
                  }
                  iVar10 = (int)sVar1;
                  psVar25 = psVar26;
                  piVar28 = piVar28 + 1;
                } while (psVar26 != psVar24 + iVar2);
                piVar15 = piVar15 + iVar2;
                iVar7 = tns_ar_filter(piVar6,iVar7,paVar3->direction,piVar4,paVar3->lpc_q);
                while( true ) {
                  piVar15[-1] = iVar21 - iVar7;
                  piVar15 = piVar15 + -1;
                  if (iVar23 == 0) break;
                  iVar23 = iVar23 + -1;
                }
                uVar13 = paVar3->order;
              }
            }
            else {
              tns_inv_filter(piVar6,iVar7,paVar3->direction,piVar4,paVar3->lpc_q,uVar13,param_6);
              uVar13 = paVar3->order;
            }
          }
          piVar4 = piVar4 + uVar13;
        }
        iVar18 = iVar18 + -1;
        paVar3 = paVar3 + 1;
      } while (iVar18 != 0);
      paVar5 = paVar5 + iVar22;
    }
    iVar20 = iVar20 + 1;
    param_1 = param_1 + iVar16 * 4;
    ppiVar19 = ppiVar19 + 1;
    param_2 = param_2 + iVar8 * 4;
  } while (iVar20 < window->windows);
  return;
}
