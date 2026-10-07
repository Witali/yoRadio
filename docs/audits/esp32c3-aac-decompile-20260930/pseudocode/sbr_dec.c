/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: sbr_dec @ ram:42028524
 * Types and parameter counts are inferred; verify against disassembly. */

void sbr_dec(int param_1,int *param_2,int param_3,int param_4,undefined4 *param_5,int *param_6,
            int param_7,int param_8)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  uint *puVar3;
  void *pvVar4;
  uint *src_void;
  int iVar5;
  int iVar6;
  uint *puVar7;
  uint *puVar8;
  uint *puVar9;
  int *piVar10;
  undefined4 uVar11;
  uint uVar12;
  int iVar13;
  int iVar14;
  uint uVar15;
  uint uVar16;
  int *piVar17;
  uint uVar18;
  void *pvVar19;
  int iVar20;
  undefined4 *puVar21;
  undefined4 *puVar22;
  uint uVar23;
  int iVar24;
  uint *puVar25;
  int iVar26;
  undefined4 uStack_60;
  undefined4 uStack_5c;
  undefined4 uStack_58;
  undefined4 uStack_54;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined4 uStack_48;

  gp = &__global_pointer_;
  src_void = *(uint **)(param_8 + 0x8a74);
  uVar2 = 0x20;
  if (param_4 != 0) {
    uVar2 = param_5[9];
  }
  pvVar19 = (void *)(param_3 + 0x3e38);
  memmove(*(void **)(param_3 + 0x3e34),pvVar19,0x480);
  iVar20 = param_5[1];
  if (iVar20 == 0) {
    memmove(*(void **)(param_3 + 0x39b0),(void *)(param_3 + 0x39b4),0x480);
    iVar20 = param_5[1];
  }
  iVar24 = param_1 + 0x27e;
  iVar26 = 0;
  while( true ) {
    iVar5 = (param_5[6] + iVar26) * 0x80;
    iVar6 = iVar5 + 0x11b0 + param_3;
    if (iVar20 == 1) {
      calc_sbr_anafilterbank_LC(iVar6,iVar24,src_void,uVar2);
    }
    else {
      calc_sbr_anafilterbank(iVar6,iVar5 + 0x25b0 + param_3,iVar24,src_void,uVar2);
    }
    if (iVar26 == 0x1f) break;
    iVar26 = iVar26 + 1;
    iVar20 = param_5[1];
    iVar24 = iVar24 + 0x40;
  }
  uVar12 = 0x20;
  if (*(int *)(param_8 + 0xec) == 0) {
    puVar21 = (undefined4 *)(param_1 + 0x800);
    puVar22 = (undefined4 *)(param_1 + 0xa40);
    do {
      uVar2 = *puVar21;
      uVar11 = puVar21[1];
      puVar22[2] = puVar21[2];
      *puVar22 = uVar2;
      puVar22[1] = uVar11;
      puVar1 = puVar21 + 3;
      puVar21 = puVar21 + 4;
      puVar22[3] = *puVar1;
      puVar22 = puVar22 + 4;
    } while (puVar21 != (undefined4 *)(param_1 + 0xa40));
    if (param_4 != 0) goto LAB_ram_42028622;
LAB_ram_42028b70:
    iVar20 = 0;
    do {
      memset(*(int *)(param_3 + 0x3e34) + iVar20,0,0xc0);
      iVar24 = *(int *)(param_3 + 0x39b0) + iVar20;
      iVar20 = iVar20 + 0xc0;
      memset(iVar24,0,0xc0);
    } while (iVar20 != 0x1c80);
  }
  else {
    puVar21 = (undefined4 *)(param_1 + 0x800);
    puVar22 = (undefined4 *)(param_1 + -0xa40);
    do {
      uVar2 = *puVar21;
      uVar11 = puVar21[1];
      puVar22[2] = puVar21[2];
      *puVar22 = uVar2;
      puVar22[1] = uVar11;
      puVar1 = puVar21 + 3;
      puVar21 = puVar21 + 4;
      puVar22[3] = *puVar1;
      puVar22 = puVar22 + 4;
    } while (puVar21 != (undefined4 *)(param_1 + 0xa40));
    if (param_4 == 0) goto LAB_ram_42028b70;
LAB_ram_42028622:
    iVar20 = param_5[7] * 0x80;
    if (param_5[1] == 1) {
      sbr_generate_high_freq
                (param_3 + 0x11b0 + iVar20,0,*(undefined4 *)(param_3 + 0x3e34),0,param_3 + 0x128,
                 param_3 + 0x150,param_5 + 0x84,param_5[0xc6],param_5[9],param_5 + 0x89,param_5[199]
                 ,*param_5,param_3 + 0x10,param_3 + 0x4bb8,src_void,param_3 + 0x1180,
                 param_3 + 0x1198,param_5 + 200,1,param_5 + 0xb);
      uStack_60 = param_5[200];
      uStack_5c = param_5[0xc9];
      uStack_58 = param_5[0xca];
      uStack_54 = param_5[0xcb];
      uStack_50 = param_5[0xcc];
      uStack_4c = param_5[0xcd];
      uStack_48 = param_5[0xce];
      calc_sbr_envelope(param_3,*(undefined4 *)(param_3 + 0x3e34),0,param_5 + 0xd,param_5 + 0xc4,
                        param_5 + 0x83,param_5[0xc6],*(undefined4 *)(param_3 + 0xbc),
                        param_3 + 0x4bb8,param_3 + 0x704,param_3 + 0x708,param_3 + 0x604,
                        param_3 + 0x70c,param_5 + 0xd3,param_5 + 0xcf,0,0,0,0,src_void,&uStack_60,
                        param_5 + 0x107,param_5[1]);
    }
    else {
      sbr_generate_high_freq
                (param_3 + 0x11b0 + iVar20,param_3 + 0x25b0 + iVar20,
                 *(undefined4 *)(param_3 + 0x3e34),*(undefined4 *)(param_3 + 0x39b0),param_3 + 0x128
                 ,param_3 + 0x150,param_5 + 0x84,param_5[0xc6],param_5[9],param_5 + 0x89,
                 param_5[199],*param_5,param_3 + 0x10,0,src_void,param_3 + 0x1180,param_3 + 0x1198,
                 param_5 + 200,param_5[1],param_5 + 0xb);
      uStack_60 = param_5[200];
      uStack_5c = param_5[0xc9];
      uStack_58 = param_5[0xca];
      uStack_54 = param_5[0xcb];
      uStack_50 = param_5[0xcc];
      uStack_4c = param_5[0xcd];
      uStack_48 = param_5[0xce];
      calc_sbr_envelope(param_3,*(undefined4 *)(param_3 + 0x3e34),*(undefined4 *)(param_3 + 0x39b0),
                        param_5 + 0xd,param_5 + 0xc4,param_5 + 0x83,param_5[0xc6],
                        *(undefined4 *)(param_3 + 0xbc),0,param_3 + 0x704,param_3 + 0x708,
                        param_3 + 0x604,param_3 + 0x70c,param_5 + 0xd3,param_5 + 0xcf,
                        param_3 + 0x60b8,param_3 + 0x61b8,param_3 + 0x62b8,param_3 + 0x63b8,src_void
                        ,&uStack_60,param_5 + 0x107,param_5[1]);
    }
    if ((*(int *)(param_8 + 0xc0) != 0) && (param_7 != 0)) {
      iVar26 = param_8 + 0x25a4;
      iVar20 = param_8 + 0x4ba4;
      *(int *)(param_7 + 0x620) = iVar26;
      *(int *)(param_7 + 0x624) = iVar20;
      iVar24 = 0;
      do {
        if (iVar24 < *(int *)(param_3 + 0x14) << 1) {
          uVar23 = param_5[10];
        }
        else {
          uVar23 = param_5[9];
        }
        iVar5 = param_5[0xb];
        puVar25 = (uint *)(iVar26 + iVar24 * 0x100);
        puVar3 = (uint *)(iVar20 + iVar24 * 0x100);
        if (iVar5 < (int)uVar23) {
          iVar20 = 0x80;
          uVar23 = uVar12;
LAB_ram_420287c8:
          iVar26 = (param_5[7] + iVar24) * 0x80;
          piVar10 = (int *)(param_3 + 0x11b0 + iVar26);
          piVar17 = (int *)(iVar26 + param_3 + 0x25b0);
          iVar26 = 0;
          puVar7 = puVar25;
          puVar8 = puVar3;
          do {
            iVar5 = *piVar10;
            iVar26 = iVar26 + 1;
            piVar10 = piVar10 + 1;
            uVar15 = iVar5 << 1;
            if ((int)uVar15 >> 1 != iVar5) {
              uVar15 = iVar5 >> 0x1f ^ 0x7fffffff;
            }
            *puVar7 = uVar15;
            iVar5 = *piVar17;
            puVar7 = puVar7 + 1;
            piVar17 = piVar17 + 1;
            uVar15 = iVar5 << 1;
            if ((int)uVar15 >> 1 != iVar5) {
              uVar15 = iVar5 >> 0x1f ^ 0x7fffffff;
            }
            *puVar8 = uVar15;
            puVar8 = puVar8 + 1;
          } while (iVar26 < (int)uVar23);
          iVar5 = param_5[0xb];
        }
        else {
          iVar20 = uVar23 << 2;
          if (0 < (int)uVar23) goto LAB_ram_420287c8;
        }
        memcpy((void *)((int)puVar25 + iVar20),(void *)(*(int *)(param_3 + 0x3e34) + iVar24 * 0xc0),
               (iVar5 - uVar23) * 4);
        memcpy((void *)((int)puVar3 + iVar20),(void *)(*(int *)(param_3 + 0x39b0) + iVar24 * 0xc0),
               (param_5[0xb] - uVar23) * 4);
        memset(puVar25 + param_5[0xb],0,(0x40 - param_5[0xb]) * 4);
        iVar24 = iVar24 + 1;
        memset(puVar3 + param_5[0xb],0,(0x40 - param_5[0xb]) * 4);
        iVar26 = *(int *)(param_7 + 0x620);
        iVar20 = *(int *)(param_7 + 0x624);
      } while (iVar24 != 0x20);
      puVar3 = (uint *)(iVar20 + 0x2014);
      puVar25 = (uint *)(iVar26 + 0x2000);
      iVar20 = 0x20;
      do {
        piVar10 = (int *)((param_5[7] + iVar20) * 0x80 + param_3 + 0x25b0);
        puVar7 = puVar25;
        puVar8 = puVar3 + -5;
        do {
          puVar9 = puVar8;
          iVar24 = piVar10[-0x500];
          uVar12 = iVar24 << 1;
          if ((int)uVar12 >> 1 != iVar24) {
            uVar12 = iVar24 >> 0x1f ^ 0x7fffffff;
          }
          *puVar7 = uVar12;
          iVar24 = *piVar10;
          puVar7 = puVar7 + 1;
          piVar10 = piVar10 + 1;
          uVar12 = iVar24 << 1;
          if ((int)uVar12 >> 1 != iVar24) {
            uVar12 = iVar24 >> 0x1f ^ 0x7fffffff;
          }
          *puVar9 = uVar12;
          puVar8 = puVar9 + 1;
        } while (puVar9 + 1 != puVar3);
        iVar20 = iVar20 + 1;
        puVar3 = puVar9 + 0x41;
        puVar25 = puVar25 + 0x40;
      } while (iVar20 != 0x26);
      pvVar4 = (void *)(param_3 + 0x11b0);
      iVar20 = 0;
      if (0 < (int)param_5[6]) {
        do {
          iVar24 = (param_5[4] + iVar20) * 0x80;
          memmove(pvVar4,(void *)(iVar24 + 0x11b0 + param_3),0x80);
          memmove((void *)((int)pvVar4 + 0x1400),(void *)(iVar24 + 0x25b0 + param_3),0x80);
          iVar20 = iVar20 + 1;
          pvVar4 = (void *)((int)pvVar4 + 0x80);
        } while (iVar20 < (int)param_5[6]);
      }
      memmove(pvVar19,(void *)(*(int *)(param_3 + 0x3e34) + 0x1800),0x480);
      memmove((void *)(param_3 + 0x39b4),(void *)(*(int *)(param_3 + 0x39b0) + 0x1800),0x480);
      puVar3 = src_void + 0x40;
      if (*(char *)(param_8 + 0xb4) == '\0') {
        memmove(src_void + 0x9c0,(void *)(param_3 + 0x42b8),0x900);
      }
      else {
        memmove(src_void + 0x5c0,(void *)(param_3 + 0x42b8),0x500);
      }
      iVar20 = 0;
      puVar25 = src_void + 0xcc;
      do {
        memmove(puVar25 + -0x2c,*(void **)(*(int *)(*(int *)(param_7 + 0x1fc) + 0xc) + iVar20),0x30)
        ;
        puVar22 = (undefined4 *)(*(int *)(*(int *)(param_7 + 0x1fc) + 0x10) + iVar20);
        iVar20 = iVar20 + 4;
        memmove(puVar25,(void *)*puVar22,0x30);
        puVar25 = puVar25 + 0x58;
      } while (iVar20 != 0xc);
      memset(src_void + *(int *)(param_7 + 0x14),0,(0x40 - *(int *)(param_7 + 0x14)) * 4);
      memset(puVar3 + *(int *)(param_7 + 0x14),0,(0x40 - *(int *)(param_7 + 0x14)) * 4);
      puVar25 = src_void + 0x5a0;
      iVar26 = 0;
      iVar24 = 0;
      iVar20 = 0;
      do {
        iVar5 = iVar20;
        if (*(int *)(iVar20 * 4 + param_7 + 0x150) == iVar24) {
          iVar5 = iVar20 + 1;
          ps_init_stereo_mixing(param_7,iVar20,param_5[0xb]);
        }
        ps_applied(param_7,*(int *)(param_7 + 0x620) + iVar26,*(int *)(param_7 + 0x624) + iVar26,
                   src_void,puVar3,src_void + 0x80,iVar24);
        iVar20 = *(int *)(param_7 + 0x620) + iVar26;
        iVar6 = *(int *)(param_7 + 0x624) + iVar26;
        if (*(char *)(param_8 + 0xb4) == '\0') {
          if (iVar24 < 0x10) {
            iVar13 = *param_2;
            iVar14 = iVar26;
          }
          else {
            iVar13 = param_2[1];
            iVar14 = iVar26 + -0x1000;
          }
          calc_sbr_synfilterbank(iVar20,iVar6,iVar13 + iVar14,(int)src_void + (0x2600 - iVar26),0);
        }
        else {
          calc_sbr_synfilterbank(iVar20,iVar6,iVar24 * 0x80 + *param_2,puVar25,1);
        }
        memmove((void *)(*(int *)(param_7 + 0x620) + iVar26),src_void,0x100);
        iVar24 = iVar24 + 1;
        memmove((void *)(*(int *)(param_7 + 0x624) + iVar26),puVar3,0x100);
        iVar26 = iVar26 + 0x100;
        puVar25 = puVar25 + -0x20;
        iVar20 = iVar5;
      } while (iVar24 != 0x20);
      iVar20 = 0;
      puVar3 = src_void + 0xec;
      do {
        memmove(*(void **)(*(int *)(*(int *)(param_7 + 0x1fc) + 0xc) + iVar20),puVar3 + -0x2c,0x30);
        puVar22 = (undefined4 *)(*(int *)(*(int *)(param_7 + 0x1fc) + 0x10) + iVar20);
        iVar20 = iVar20 + 4;
        memmove((void *)*puVar22,puVar3,0x30);
        puVar3 = puVar3 + 0x58;
      } while (iVar20 != 0xc);
      memmove((void *)(param_3 + 0x42b8),src_void + 0x1c0,0x900);
      if (*(char *)(param_8 + 0xb4) == '\0') {
        memmove(src_void + 0x940,*(void **)(param_7 + 4),0x900);
      }
      else {
        memmove(src_void + 0x540,*(void **)(param_7 + 4),0x500);
      }
      puVar3 = src_void + 0x520;
      iVar20 = 0;
      iVar24 = 0;
      do {
        iVar26 = *(int *)(param_7 + 0x620) + iVar20;
        iVar5 = *(int *)(param_7 + 0x624) + iVar20;
        if (*(char *)(param_8 + 0xb4) == '\0') {
          if (iVar24 < 0x10) {
            iVar14 = *param_6;
            iVar6 = iVar20;
          }
          else {
            iVar14 = param_6[1];
            iVar6 = iVar20 + -0x1000;
          }
          calc_sbr_synfilterbank(iVar26,iVar5,iVar14 + iVar6,(int)src_void + (0x2400 - iVar20),0);
        }
        else {
          calc_sbr_synfilterbank(iVar26,iVar5,iVar24 * 0x80 + *param_6,puVar3,1);
        }
        iVar24 = iVar24 + 1;
        iVar20 = iVar20 + 0x100;
        puVar3 = puVar3 + -0x20;
      } while (iVar24 != 0x20);
      if (*(char *)(param_8 + 0xb4) == '\0') {
        memmove(*(void **)(param_7 + 4),src_void + 0x140,0x900);
        uVar2 = param_5[9];
        *(undefined4 *)(param_3 + 0xbc) = 0;
        param_5[10] = uVar2;
        return;
      }
      memmove(*(void **)(param_7 + 4),src_void + 0x140,0x500);
      *(undefined4 *)(param_3 + 0xbc) = 0;
      goto LAB_ram_42029018;
    }
  }
  puVar3 = src_void + 0x40;
  if (*(char *)(param_8 + 0xb4) == '\0') {
    memmove(src_void + 0x880,(void *)(param_3 + 0x42b8),0x900);
  }
  else {
    memmove(src_void + 0x480,(void *)(param_3 + 0x42b8),0x500);
  }
  puVar25 = src_void + 0x840;
  puVar7 = src_void + 0x460;
  iVar20 = 0;
  iVar24 = 0;
  iVar26 = 0;
  do {
    iVar5 = param_5[1];
    iVar6 = (param_5[7] + iVar26) * 0x80;
    piVar17 = (int *)(iVar6 + 0x11b0 + param_3);
    puVar8 = src_void;
    piVar10 = piVar17;
    if (param_4 == 0) {
      param_5[0xb] = 0x20;
      if (iVar5 != 1) goto LAB_ram_42028c42;
LAB_ram_42028ed6:
      uVar15 = 0;
      iVar13 = 0x10;
      iVar5 = iVar13;
      uVar23 = uVar12;
LAB_ram_42028ee2:
      do {
        *puVar8 = *piVar10 >> 9;
        iVar13 = iVar13 + -1;
        puVar8[1] = piVar10[1] >> 9;
        puVar8 = puVar8 + 2;
        piVar10 = piVar10 + 2;
      } while (iVar13 != 0);
      piVar17 = piVar17 + (iVar5 + -1) * 2 + 2;
      puVar8 = src_void + (iVar5 + -1) * 2 + 2;
LAB_ram_42028f0a:
      puVar9 = puVar8;
      if (uVar15 != 0) {
        puVar9 = puVar8 + 1;
        *puVar8 = *piVar17 >> 9;
      }
      iVar5 = param_5[0xb];
      if ((int)uVar23 < iVar5) {
        piVar10 = (int *)(*(int *)(param_3 + 0x3e34) + iVar20);
        puVar8 = puVar9;
        do {
          puVar9 = puVar8 + 1;
          uVar23 = uVar23 + 1;
          *puVar8 = *piVar10 << 1;
          iVar5 = param_5[0xb];
          piVar10 = piVar10 + 1;
          puVar8 = puVar9;
        } while ((int)uVar23 < iVar5);
      }
      memset(puVar9,0,(0x40 - iVar5) * 4);
      if (*(char *)(param_8 + 0xb4) == '\0') {
        if (iVar26 < 0x10) {
          iVar6 = *param_2;
          iVar5 = iVar24;
        }
        else {
          iVar6 = param_2[1];
          iVar5 = iVar24 + -0x1000;
        }
        calc_sbr_synfilterbank_LC(src_void,iVar6 + iVar5,puVar25,0);
      }
      else {
        calc_sbr_synfilterbank_LC(src_void,iVar26 * 0x80 + *param_2,puVar7,1);
      }
    }
    else {
      if (iVar26 < *(int *)(param_3 + 0x14) << 1) {
        uVar23 = param_5[10];
      }
      else {
        uVar23 = param_5[9];
      }
      iVar14 = param_5[0xb];
      if (iVar14 < (int)uVar23) {
        if (iVar5 == 1) goto LAB_ram_42028ed6;
LAB_ram_42028c42:
        uVar15 = 0;
        iVar13 = 0x10;
        iVar5 = 0x80;
        uVar23 = uVar12;
        uVar16 = uVar12;
LAB_ram_42028c50:
        do {
          iVar14 = *piVar17;
          piVar17 = piVar17 + 1;
          uVar23 = uVar23 - 1;
          uVar18 = iVar14 << 1;
          if ((int)uVar18 >> 1 != iVar14) {
            uVar18 = iVar14 >> 0x1f ^ 0x7fffffff;
          }
          *puVar8 = uVar18;
          puVar8 = puVar8 + 1;
        } while (uVar23 != 0);
        iVar14 = param_5[0xb];
        uVar23 = uVar16;
      }
      else {
        iVar13 = (int)uVar23 >> 1;
        uVar15 = uVar23 & 1;
        if (iVar5 == 1) {
          iVar5 = iVar13;
          if (iVar13 != 0) goto LAB_ram_42028ee2;
          goto LAB_ram_42028f0a;
        }
        iVar5 = uVar23 << 2;
        uVar16 = uVar23;
        if (uVar23 != 0) goto LAB_ram_42028c50;
        iVar13 = 0;
        uVar15 = 0;
        iVar5 = 0;
      }
      puVar22 = (undefined4 *)((int)src_void + iVar5);
      if ((int)uVar23 < iVar14) {
        puVar21 = (undefined4 *)(*(int *)(param_3 + 0x3e34) + iVar20);
        uVar16 = uVar23;
        do {
          uVar2 = *puVar21;
          uVar16 = uVar16 + 1;
          puVar21 = puVar21 + 1;
          *puVar22 = uVar2;
          iVar14 = param_5[0xb];
          puVar22 = puVar22 + 1;
        } while ((int)uVar16 < iVar14);
      }
      memset(puVar22,0,(0x40 - iVar14) * 4);
      piVar17 = (int *)(iVar6 + 0x25b0 + param_3);
      iVar6 = iVar13;
      piVar10 = piVar17;
      puVar8 = puVar3;
      if (iVar13 != 0) {
        do {
          iVar14 = *piVar10;
          iVar6 = iVar6 + -1;
          uVar16 = iVar14 << 1;
          if ((int)uVar16 >> 1 != iVar14) {
            uVar16 = iVar14 >> 0x1f ^ 0x7fffffff;
          }
          *puVar8 = uVar16;
          iVar14 = piVar10[1];
          uVar16 = iVar14 << 1;
          if ((int)uVar16 >> 1 != iVar14) {
            uVar16 = iVar14 >> 0x1f ^ 0x7fffffff;
          }
          puVar8[1] = uVar16;
          piVar10 = piVar10 + 2;
          puVar8 = puVar8 + 2;
        } while (iVar6 != 0);
        piVar17 = piVar17 + (iVar13 + -1) * 2 + 2;
        puVar8 = src_void + (iVar13 + -1) * 2 + 0x42;
      }
      if (uVar15 != 0) {
        iVar6 = *piVar17;
        uVar15 = iVar6 << 1;
        if (iVar6 != (int)uVar15 >> 1) {
          uVar15 = iVar6 >> 0x1f ^ 0x7fffffff;
        }
        *puVar8 = uVar15;
      }
      iVar6 = param_5[0xb];
      puVar22 = (undefined4 *)((int)puVar3 + iVar5);
      if ((int)uVar23 < iVar6) {
        puVar21 = (undefined4 *)(*(int *)(param_3 + 0x39b0) + iVar20);
        do {
          uVar2 = *puVar21;
          uVar23 = uVar23 + 1;
          puVar21 = puVar21 + 1;
          *puVar22 = uVar2;
          iVar6 = param_5[0xb];
          puVar22 = puVar22 + 1;
        } while ((int)uVar23 < iVar6);
      }
      memset(puVar22,0,(0x40 - iVar6) * 4);
      if (*(char *)(param_8 + 0xb4) == '\0') {
        if (iVar26 < 0x10) {
          iVar6 = *param_2;
          iVar5 = iVar24;
        }
        else {
          iVar6 = param_2[1];
          iVar5 = iVar24 + -0x1000;
        }
        calc_sbr_synfilterbank(src_void,puVar3,iVar6 + iVar5,puVar25,0);
      }
      else {
        calc_sbr_synfilterbank(src_void,puVar3,iVar26 * 0x80 + *param_2,puVar7,1);
      }
    }
    iVar26 = iVar26 + 1;
    iVar24 = iVar24 + 0x100;
    puVar25 = puVar25 + -0x40;
    puVar7 = puVar7 + -0x20;
    iVar20 = iVar20 + 0xc0;
  } while (iVar26 != 0x20);
  if (*(char *)(param_8 + 0xb4) == '\0') {
    memmove((void *)(param_3 + 0x42b8),src_void + 0x80,0x900);
  }
  else {
    memmove((void *)(param_3 + 0x42b8),src_void + 0x80,0x500);
  }
  pvVar4 = (void *)(param_3 + 0x11b0);
  iVar20 = 0;
  if (0 < (int)param_5[6]) {
    do {
      pvVar4 = memmove(pvVar4,(void *)((param_5[4] + iVar20) * 0x80 + 0x11b0 + param_3),0x80);
      iVar20 = iVar20 + 1;
      pvVar4 = (void *)((int)pvVar4 + 0x80);
    } while (iVar20 < (int)param_5[6]);
  }
  memmove(pvVar19,(void *)(*(int *)(param_3 + 0x3e34) + 0x1800),0x480);
  if (param_5[1] == 0) {
    pvVar19 = (void *)(param_3 + 0x25b0);
    iVar20 = 0;
    if (0 < (int)param_5[6]) {
      do {
        pvVar19 = memmove(pvVar19,(void *)((param_5[4] + iVar20) * 0x80 + 0x25b0 + param_3),0x80);
        iVar20 = iVar20 + 1;
        pvVar19 = (void *)((int)pvVar19 + 0x80);
      } while (iVar20 < (int)param_5[6]);
    }
    memmove((void *)(param_3 + 0x39b4),(void *)(*(int *)(param_3 + 0x39b0) + 0x1800),0x480);
  }
  *(undefined4 *)(param_3 + 0xbc) = 0;
  if (param_4 == 0) {
    return;
  }
LAB_ram_42029018:
  param_5[10] = param_5[9];
  return;
}
