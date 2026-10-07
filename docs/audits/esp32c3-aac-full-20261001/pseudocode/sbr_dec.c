/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_dec @ ram:43010770
 * Types and parameter counts are inferred; verify against disassembly. */

void sbr_dec(int param_1,int *param_2,int param_3,int param_4,undefined4 *param_5,int *param_6,
            int param_7,int param_8)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  uint *puVar3;
  uint *puVar4;
  int iVar5;
  int iVar6;
  uint *puVar7;
  uint *puVar8;
  uint *puVar9;
  int *piVar10;
  undefined4 uVar11;
  uint uVar12;
  int iVar13;
  uint uVar14;
  uint uVar15;
  int *piVar16;
  uint uVar17;
  int iVar18;
  int iVar19;
  undefined4 *puVar20;
  undefined4 *puVar21;
  uint uVar22;
  int iVar23;
  uint *puVar24;
  int iVar25;
  int iVar26;
  undefined4 uStack_60;
  undefined4 uStack_5c;
  undefined4 uStack_58;
  undefined4 uStack_54;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined4 uStack_48;

  gp = &__global_pointer_;
  puVar4 = *(uint **)(param_8 + 0x8a74);
  uVar2 = 0x20;
  if (param_4 != 0) {
    uVar2 = param_5[9];
  }
  iVar18 = param_3 + 0x3e38;
  memmove(*(undefined4 *)(param_3 + 0x3e34),iVar18,0x480);
  iVar19 = param_5[1];
  if (iVar19 == 0) {
    memmove(*(undefined4 *)(param_3 + 0x39b0),param_3 + 0x39b4,0x480);
    iVar19 = param_5[1];
  }
  iVar23 = param_1 + 0x27e;
  iVar25 = 0;
  while( true ) {
    iVar5 = (param_5[6] + iVar25) * 0x80;
    iVar6 = iVar5 + 0x11b0 + param_3;
    if (iVar19 == 1) {
      calc_sbr_anafilterbank_LC(iVar6,iVar23,puVar4,uVar2);
    }
    else {
      calc_sbr_anafilterbank(iVar6,iVar5 + 0x25b0 + param_3,iVar23,puVar4,uVar2);
    }
    if (iVar25 == 0x1f) break;
    iVar25 = iVar25 + 1;
    iVar19 = param_5[1];
    iVar23 = iVar23 + 0x40;
  }
  uVar12 = 0x20;
  if (*(int *)(param_8 + 0xec) == 0) {
    puVar20 = (undefined4 *)(param_1 + 0x800);
    puVar21 = (undefined4 *)(param_1 + 0xa40);
    do {
      uVar2 = *puVar20;
      uVar11 = puVar20[1];
      puVar21[2] = puVar20[2];
      *puVar21 = uVar2;
      puVar21[1] = uVar11;
      puVar1 = puVar20 + 3;
      puVar20 = puVar20 + 4;
      puVar21[3] = *puVar1;
      puVar21 = puVar21 + 4;
    } while (puVar20 != (undefined4 *)(param_1 + 0xa40));
    if (param_4 != 0) goto LAB_ram_43010876;
LAB_ram_43010dd4:
    iVar19 = 0;
    do {
      memset(*(int *)(param_3 + 0x3e34) + iVar19,0,0xc0);
      iVar23 = *(int *)(param_3 + 0x39b0) + iVar19;
      iVar19 = iVar19 + 0xc0;
      memset(iVar23,0,0xc0);
    } while (iVar19 != 0x1c80);
  }
  else {
    puVar20 = (undefined4 *)(param_1 + 0x800);
    puVar21 = (undefined4 *)(param_1 + -0xa40);
    do {
      uVar2 = *puVar20;
      uVar11 = puVar20[1];
      puVar21[2] = puVar20[2];
      *puVar21 = uVar2;
      puVar21[1] = uVar11;
      puVar1 = puVar20 + 3;
      puVar20 = puVar20 + 4;
      puVar21[3] = *puVar1;
      puVar21 = puVar21 + 4;
    } while (puVar20 != (undefined4 *)(param_1 + 0xa40));
    if (param_4 == 0) goto LAB_ram_43010dd4;
LAB_ram_43010876:
    iVar19 = param_5[7] * 0x80;
    if (param_5[1] == 1) {
      sbr_generate_high_freq
                (param_3 + 0x11b0 + iVar19,0,*(undefined4 *)(param_3 + 0x3e34),0,param_3 + 0x128,
                 param_3 + 0x150,param_5 + 0x84,param_5[0xc6],param_5[9],param_5 + 0x89,param_5[199]
                 ,*param_5,param_3 + 0x10,param_3 + 0x4bb8,puVar4,param_3 + 0x1180,param_3 + 0x1198,
                 param_5 + 200,1,param_5 + 0xb);
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
                        param_3 + 0x70c,param_5 + 0xd3,param_5 + 0xcf,0,0,0,0,puVar4,&uStack_60,
                        param_5 + 0x107,param_5[1]);
    }
    else {
      sbr_generate_high_freq
                (param_3 + 0x11b0 + iVar19,param_3 + 0x25b0 + iVar19,
                 *(undefined4 *)(param_3 + 0x3e34),*(undefined4 *)(param_3 + 0x39b0),param_3 + 0x128
                 ,param_3 + 0x150,param_5 + 0x84,param_5[0xc6],param_5[9],param_5 + 0x89,
                 param_5[199],*param_5,param_3 + 0x10,0,puVar4,param_3 + 0x1180,param_3 + 0x1198,
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
                        param_3 + 0x60b8,param_3 + 0x61b8,param_3 + 0x62b8,param_3 + 0x63b8,puVar4,
                        &uStack_60,param_5 + 0x107,param_5[1]);
    }
    if ((*(int *)(param_8 + 0xc0) != 0) && (param_7 != 0)) {
      iVar25 = param_8 + 0x25a4;
      iVar19 = param_8 + 0x4ba4;
      *(int *)(param_7 + 0x620) = iVar25;
      *(int *)(param_7 + 0x624) = iVar19;
      iVar23 = 0;
      do {
        if (iVar23 < *(int *)(param_3 + 0x14) << 1) {
          uVar22 = param_5[10];
        }
        else {
          uVar22 = param_5[9];
        }
        iVar5 = param_5[0xb];
        puVar24 = (uint *)(iVar25 + iVar23 * 0x100);
        puVar3 = (uint *)(iVar19 + iVar23 * 0x100);
        if (iVar5 < (int)uVar22) {
          iVar19 = 0x80;
          uVar22 = uVar12;
LAB_ram_43010a24:
          iVar25 = (param_5[7] + iVar23) * 0x80;
          piVar10 = (int *)(param_3 + 0x11b0 + iVar25);
          piVar16 = (int *)(iVar25 + param_3 + 0x25b0);
          iVar25 = 0;
          puVar7 = puVar24;
          puVar8 = puVar3;
          do {
            iVar5 = *piVar10;
            iVar25 = iVar25 + 1;
            piVar10 = piVar10 + 1;
            uVar14 = iVar5 << 1;
            if ((int)uVar14 >> 1 != iVar5) {
              uVar14 = iVar5 >> 0x1f ^ 0x7fffffff;
            }
            *puVar7 = uVar14;
            iVar5 = *piVar16;
            puVar7 = puVar7 + 1;
            piVar16 = piVar16 + 1;
            uVar14 = iVar5 << 1;
            if ((int)uVar14 >> 1 != iVar5) {
              uVar14 = iVar5 >> 0x1f ^ 0x7fffffff;
            }
            *puVar8 = uVar14;
            puVar8 = puVar8 + 1;
          } while (iVar25 < (int)uVar22);
          iVar5 = param_5[0xb];
        }
        else {
          iVar19 = uVar22 << 2;
          if (0 < (int)uVar22) goto LAB_ram_43010a24;
        }
        memcpy((int)puVar24 + iVar19,*(int *)(param_3 + 0x3e34) + iVar23 * 0xc0,(iVar5 - uVar22) * 4
              );
        memcpy((int)puVar3 + iVar19,*(int *)(param_3 + 0x39b0) + iVar23 * 0xc0,
               (param_5[0xb] - uVar22) * 4);
        memset(puVar24 + param_5[0xb],0,(0x40 - param_5[0xb]) * 4);
        iVar23 = iVar23 + 1;
        memset(puVar3 + param_5[0xb],0,(0x40 - param_5[0xb]) * 4);
        iVar25 = *(int *)(param_7 + 0x620);
        iVar19 = *(int *)(param_7 + 0x624);
      } while (iVar23 != 0x20);
      puVar3 = (uint *)(iVar19 + 0x2014);
      puVar24 = (uint *)(iVar25 + 0x2000);
      iVar19 = 0x20;
      do {
        piVar10 = (int *)((param_5[7] + iVar19) * 0x80 + param_3 + 0x25b0);
        puVar7 = puVar24;
        puVar8 = puVar3 + -5;
        do {
          puVar9 = puVar8;
          iVar23 = piVar10[-0x500];
          uVar12 = iVar23 << 1;
          if ((int)uVar12 >> 1 != iVar23) {
            uVar12 = iVar23 >> 0x1f ^ 0x7fffffff;
          }
          *puVar7 = uVar12;
          iVar23 = *piVar10;
          puVar7 = puVar7 + 1;
          piVar10 = piVar10 + 1;
          uVar12 = iVar23 << 1;
          if ((int)uVar12 >> 1 != iVar23) {
            uVar12 = iVar23 >> 0x1f ^ 0x7fffffff;
          }
          *puVar9 = uVar12;
          puVar8 = puVar9 + 1;
        } while (puVar9 + 1 != puVar3);
        iVar19 = iVar19 + 1;
        puVar3 = puVar9 + 0x41;
        puVar24 = puVar24 + 0x40;
      } while (iVar19 != 0x26);
      iVar19 = param_3 + 0x11b0;
      iVar23 = 0;
      if (0 < (int)param_5[6]) {
        do {
          iVar25 = (param_5[4] + iVar23) * 0x80;
          memmove(iVar19,iVar25 + 0x11b0 + param_3,0x80);
          memmove(iVar19 + 0x1400,iVar25 + 0x25b0 + param_3,0x80);
          iVar23 = iVar23 + 1;
          iVar19 = iVar19 + 0x80;
        } while (iVar23 < (int)param_5[6]);
      }
      memmove(iVar18,*(int *)(param_3 + 0x3e34) + 0x1800,0x480);
      memmove(param_3 + 0x39b4,*(int *)(param_3 + 0x39b0) + 0x1800,0x480);
      puVar3 = puVar4 + 0x40;
      if (*(char *)(param_8 + 0xb4) == '\0') {
        memmove(puVar4 + 0x9c0,param_3 + 0x42b8,0x900);
      }
      else {
        memmove(puVar4 + 0x5c0,param_3 + 0x42b8,0x500);
      }
      iVar18 = 0;
      puVar24 = puVar4 + 0xcc;
      do {
        memmove(puVar24 + -0x2c,*(undefined4 *)(*(int *)(*(int *)(param_7 + 0x1fc) + 0xc) + iVar18),
                0x30);
        puVar21 = (undefined4 *)(*(int *)(*(int *)(param_7 + 0x1fc) + 0x10) + iVar18);
        iVar18 = iVar18 + 4;
        memmove(puVar24,*puVar21,0x30);
        puVar24 = puVar24 + 0x58;
      } while (iVar18 != 0xc);
      memset(puVar4 + *(int *)(param_7 + 0x14),0,(0x40 - *(int *)(param_7 + 0x14)) * 4);
      memset(puVar3 + *(int *)(param_7 + 0x14),0,(0x40 - *(int *)(param_7 + 0x14)) * 4);
      puVar24 = puVar4 + 0x5a0;
      iVar23 = 0;
      iVar19 = 0;
      iVar18 = 0;
      do {
        iVar25 = iVar18;
        if (*(int *)(iVar18 * 4 + param_7 + 0x150) == iVar19) {
          iVar25 = iVar18 + 1;
          ps_init_stereo_mixing(param_7,iVar18,param_5[0xb]);
        }
        ps_applied(param_7,*(int *)(param_7 + 0x620) + iVar23,*(int *)(param_7 + 0x624) + iVar23,
                   puVar4,puVar3,puVar4 + 0x80,iVar19);
        iVar18 = *(int *)(param_7 + 0x620) + iVar23;
        iVar5 = *(int *)(param_7 + 0x624) + iVar23;
        if (*(char *)(param_8 + 0xb4) == '\0') {
          if (iVar19 < 0x10) {
            iVar13 = *param_2;
            iVar6 = iVar23;
          }
          else {
            iVar13 = param_2[1];
            iVar6 = iVar23 + -0x1000;
          }
          calc_sbr_synfilterbank(iVar18,iVar5,iVar13 + iVar6,(int)puVar4 + (0x2600 - iVar23),0);
        }
        else {
          calc_sbr_synfilterbank(iVar18,iVar5,iVar19 * 0x80 + *param_2,puVar24,1);
        }
        memmove(*(int *)(param_7 + 0x620) + iVar23,puVar4,0x100);
        iVar19 = iVar19 + 1;
        memmove(*(int *)(param_7 + 0x624) + iVar23,puVar3,0x100);
        iVar23 = iVar23 + 0x100;
        puVar24 = puVar24 + -0x20;
        iVar18 = iVar25;
      } while (iVar19 != 0x20);
      iVar18 = 0;
      puVar3 = puVar4 + 0xec;
      do {
        memmove(*(undefined4 *)(*(int *)(*(int *)(param_7 + 0x1fc) + 0xc) + iVar18),puVar3 + -0x2c,
                0x30);
        puVar21 = (undefined4 *)(*(int *)(*(int *)(param_7 + 0x1fc) + 0x10) + iVar18);
        iVar18 = iVar18 + 4;
        memmove(*puVar21,puVar3,0x30);
        puVar3 = puVar3 + 0x58;
      } while (iVar18 != 0xc);
      memmove(param_3 + 0x42b8,puVar4 + 0x1c0,0x900);
      if (*(char *)(param_8 + 0xb4) == '\0') {
        memmove(puVar4 + 0x940,*(undefined4 *)(param_7 + 4),0x900);
      }
      else {
        memmove(puVar4 + 0x540,*(undefined4 *)(param_7 + 4),0x500);
      }
      puVar3 = puVar4 + 0x520;
      iVar18 = 0;
      iVar19 = 0;
      do {
        iVar23 = *(int *)(param_7 + 0x620) + iVar18;
        iVar25 = *(int *)(param_7 + 0x624) + iVar18;
        if (*(char *)(param_8 + 0xb4) == '\0') {
          if (iVar19 < 0x10) {
            iVar6 = *param_6;
            iVar5 = iVar18;
          }
          else {
            iVar6 = param_6[1];
            iVar5 = iVar18 + -0x1000;
          }
          calc_sbr_synfilterbank(iVar23,iVar25,iVar6 + iVar5,(int)puVar4 + (0x2400 - iVar18),0);
        }
        else {
          calc_sbr_synfilterbank(iVar23,iVar25,iVar19 * 0x80 + *param_6,puVar3,1);
        }
        iVar19 = iVar19 + 1;
        iVar18 = iVar18 + 0x100;
        puVar3 = puVar3 + -0x20;
      } while (iVar19 != 0x20);
      if (*(char *)(param_8 + 0xb4) == '\0') {
        memmove(*(undefined4 *)(param_7 + 4),puVar4 + 0x140,0x900);
        uVar2 = param_5[9];
        *(undefined4 *)(param_3 + 0xbc) = 0;
        param_5[10] = uVar2;
        return;
      }
      memmove(*(undefined4 *)(param_7 + 4),puVar4 + 0x140,0x500);
      *(undefined4 *)(param_3 + 0xbc) = 0;
      goto LAB_ram_4301128c;
    }
  }
  puVar3 = puVar4 + 0x40;
  if (*(char *)(param_8 + 0xb4) == '\0') {
    memmove(puVar4 + 0x880,param_3 + 0x42b8,0x900);
  }
  else {
    memmove(puVar4 + 0x480,param_3 + 0x42b8,0x500);
  }
  puVar24 = puVar4 + 0x840;
  puVar7 = puVar4 + 0x460;
  iVar19 = 0;
  iVar23 = 0;
  iVar25 = 0;
  do {
    iVar5 = param_5[1];
    iVar6 = (param_5[7] + iVar25) * 0x80;
    piVar16 = (int *)(iVar6 + 0x11b0 + param_3);
    puVar8 = puVar4;
    piVar10 = piVar16;
    if (param_4 == 0) {
      param_5[0xb] = 0x20;
      if (iVar5 != 1) goto LAB_ram_43010ea6;
LAB_ram_4301113e:
      uVar14 = 0;
      iVar26 = 0x10;
      iVar5 = iVar26;
      uVar22 = uVar12;
LAB_ram_4301114a:
      do {
        *puVar8 = *piVar10 >> 9;
        iVar26 = iVar26 + -1;
        puVar8[1] = piVar10[1] >> 9;
        puVar8 = puVar8 + 2;
        piVar10 = piVar10 + 2;
      } while (iVar26 != 0);
      piVar16 = piVar16 + (iVar5 + -1) * 2 + 2;
      puVar8 = puVar4 + (iVar5 + -1) * 2 + 2;
LAB_ram_43011172:
      puVar9 = puVar8;
      if (uVar14 != 0) {
        puVar9 = puVar8 + 1;
        *puVar8 = *piVar16 >> 9;
      }
      iVar5 = param_5[0xb];
      if ((int)uVar22 < iVar5) {
        piVar10 = (int *)(*(int *)(param_3 + 0x3e34) + iVar19);
        puVar8 = puVar9;
        do {
          puVar9 = puVar8 + 1;
          uVar22 = uVar22 + 1;
          *puVar8 = *piVar10 << 1;
          iVar5 = param_5[0xb];
          piVar10 = piVar10 + 1;
          puVar8 = puVar9;
        } while ((int)uVar22 < iVar5);
      }
      memset(puVar9,0,(0x40 - iVar5) * 4);
      if (*(char *)(param_8 + 0xb4) == '\0') {
        if (iVar25 < 0x10) {
          iVar6 = *param_2;
          iVar5 = iVar23;
        }
        else {
          iVar6 = param_2[1];
          iVar5 = iVar23 + -0x1000;
        }
        calc_sbr_synfilterbank_LC(puVar4,iVar6 + iVar5,puVar24,0);
      }
      else {
        calc_sbr_synfilterbank_LC(puVar4,iVar25 * 0x80 + *param_2,puVar7,1);
      }
    }
    else {
      if (iVar25 < *(int *)(param_3 + 0x14) << 1) {
        uVar22 = param_5[10];
      }
      else {
        uVar22 = param_5[9];
      }
      iVar13 = param_5[0xb];
      if (iVar13 < (int)uVar22) {
        if (iVar5 == 1) goto LAB_ram_4301113e;
LAB_ram_43010ea6:
        uVar14 = 0;
        iVar26 = 0x10;
        iVar5 = 0x80;
        uVar22 = uVar12;
        uVar15 = uVar12;
LAB_ram_43010eb4:
        do {
          iVar13 = *piVar16;
          piVar16 = piVar16 + 1;
          uVar22 = uVar22 - 1;
          uVar17 = iVar13 << 1;
          if ((int)uVar17 >> 1 != iVar13) {
            uVar17 = iVar13 >> 0x1f ^ 0x7fffffff;
          }
          *puVar8 = uVar17;
          puVar8 = puVar8 + 1;
        } while (uVar22 != 0);
        iVar13 = param_5[0xb];
        uVar22 = uVar15;
      }
      else {
        iVar26 = (int)uVar22 >> 1;
        uVar14 = uVar22 & 1;
        if (iVar5 == 1) {
          iVar5 = iVar26;
          if (iVar26 != 0) goto LAB_ram_4301114a;
          goto LAB_ram_43011172;
        }
        iVar5 = uVar22 << 2;
        uVar15 = uVar22;
        if (uVar22 != 0) goto LAB_ram_43010eb4;
        iVar26 = 0;
        uVar14 = 0;
        iVar5 = 0;
      }
      puVar21 = (undefined4 *)((int)puVar4 + iVar5);
      if ((int)uVar22 < iVar13) {
        puVar20 = (undefined4 *)(*(int *)(param_3 + 0x3e34) + iVar19);
        uVar15 = uVar22;
        do {
          uVar2 = *puVar20;
          uVar15 = uVar15 + 1;
          puVar20 = puVar20 + 1;
          *puVar21 = uVar2;
          iVar13 = param_5[0xb];
          puVar21 = puVar21 + 1;
        } while ((int)uVar15 < iVar13);
      }
      memset(puVar21,0,(0x40 - iVar13) * 4);
      piVar16 = (int *)(iVar6 + 0x25b0 + param_3);
      iVar6 = iVar26;
      piVar10 = piVar16;
      puVar8 = puVar3;
      if (iVar26 != 0) {
        do {
          iVar13 = *piVar10;
          iVar6 = iVar6 + -1;
          uVar15 = iVar13 << 1;
          if ((int)uVar15 >> 1 != iVar13) {
            uVar15 = iVar13 >> 0x1f ^ 0x7fffffff;
          }
          *puVar8 = uVar15;
          iVar13 = piVar10[1];
          uVar15 = iVar13 << 1;
          if ((int)uVar15 >> 1 != iVar13) {
            uVar15 = iVar13 >> 0x1f ^ 0x7fffffff;
          }
          puVar8[1] = uVar15;
          piVar10 = piVar10 + 2;
          puVar8 = puVar8 + 2;
        } while (iVar6 != 0);
        piVar16 = piVar16 + (iVar26 + -1) * 2 + 2;
        puVar8 = puVar4 + (iVar26 + -1) * 2 + 0x42;
      }
      if (uVar14 != 0) {
        iVar6 = *piVar16;
        uVar14 = iVar6 << 1;
        if (iVar6 != (int)uVar14 >> 1) {
          uVar14 = iVar6 >> 0x1f ^ 0x7fffffff;
        }
        *puVar8 = uVar14;
      }
      iVar6 = param_5[0xb];
      puVar21 = (undefined4 *)((int)puVar3 + iVar5);
      if ((int)uVar22 < iVar6) {
        puVar20 = (undefined4 *)(*(int *)(param_3 + 0x39b0) + iVar19);
        do {
          uVar2 = *puVar20;
          uVar22 = uVar22 + 1;
          puVar20 = puVar20 + 1;
          *puVar21 = uVar2;
          iVar6 = param_5[0xb];
          puVar21 = puVar21 + 1;
        } while ((int)uVar22 < iVar6);
      }
      memset(puVar21,0,(0x40 - iVar6) * 4);
      if (*(char *)(param_8 + 0xb4) == '\0') {
        if (iVar25 < 0x10) {
          iVar6 = *param_2;
          iVar5 = iVar23;
        }
        else {
          iVar6 = param_2[1];
          iVar5 = iVar23 + -0x1000;
        }
        calc_sbr_synfilterbank(puVar4,puVar3,iVar6 + iVar5,puVar24,0);
      }
      else {
        calc_sbr_synfilterbank(puVar4,puVar3,iVar25 * 0x80 + *param_2,puVar7,1);
      }
    }
    iVar25 = iVar25 + 1;
    iVar23 = iVar23 + 0x100;
    puVar24 = puVar24 + -0x40;
    puVar7 = puVar7 + -0x20;
    iVar19 = iVar19 + 0xc0;
  } while (iVar25 != 0x20);
  if (*(char *)(param_8 + 0xb4) == '\0') {
    memmove(param_3 + 0x42b8,puVar4 + 0x80,0x900);
  }
  else {
    memmove(param_3 + 0x42b8,puVar4 + 0x80,0x500);
  }
  iVar23 = param_3 + 0x11b0;
  iVar19 = 0;
  if (0 < (int)param_5[6]) {
    do {
      iVar23 = memmove(iVar23,(param_5[4] + iVar19) * 0x80 + 0x11b0 + param_3,0x80);
      iVar19 = iVar19 + 1;
      iVar23 = iVar23 + 0x80;
    } while (iVar19 < (int)param_5[6]);
  }
  memmove(iVar18,*(int *)(param_3 + 0x3e34) + 0x1800,0x480);
  if (param_5[1] == 0) {
    iVar19 = param_3 + 0x25b0;
    iVar18 = 0;
    if (0 < (int)param_5[6]) {
      do {
        iVar19 = memmove(iVar19,(param_5[4] + iVar18) * 0x80 + 0x25b0 + param_3,0x80);
        iVar18 = iVar18 + 1;
        iVar19 = iVar19 + 0x80;
      } while (iVar18 < (int)param_5[6]);
    }
    memmove(param_3 + 0x39b4,*(int *)(param_3 + 0x39b0) + 0x1800,0x480);
  }
  *(undefined4 *)(param_3 + 0xbc) = 0;
  if (param_4 == 0) {
    return;
  }
LAB_ram_4301128c:
  param_5[10] = param_5[9];
  return;
}
