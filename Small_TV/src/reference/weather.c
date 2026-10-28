/* GHIDRA REFERENCE PSEUDOCODE, NOT COMPILED.
 * Retains addresses, unresolved SDK calls and decompiler type/overlap artifacts.
 * Per-function reconstruction targets: symbol-map.json native_targets.
 */

// Audit label: application_review; entry: ram:4200fcbe; name: stop_http_server_at_4200fcbe

void stop_http_server_at_4200fcbe(void)

{
  sdk_caller_of_lwip_sendto_reference_at_4203977e();
  return;
}

// Audit label: application_review; entry: ram:4200fccc; name: weather_http_event_handler_at_4200fccc

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 weather_http_event_handler_at_4200fccc(uint *param_1)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  undefined4 uVar9;
  undefined8 uVar10;
  undefined8 uStack_28;

  uVar8 = *param_1;
  if (uVar8 == 6) {
    if (DAT_ram_3fcc3aa0 != 0) {
      FUN_ram_4038e4da();
      DAT_ram_3fcc3aa0 = 0;
      DAT_ram_3fcc3a9c = 0;
    }
  }
  else if (uVar8 < 7) {
    if (uVar8 == 4) {
      if (DAT_ram_3fcc3aa0 == 0) {
        FUN_ram_4203e61a(param_1[1]);
        DAT_ram_3fcc3aa0 = FUN_ram_4038e4be();
        DAT_ram_3fcc3a9c = 0;
        if (DAT_ram_3fcc3aa0 == 0) {
          uVar2 = FUN_ram_4038d3b4();
          FUN_ram_4038d2a2(1,"WEATHER","E (%lu) %s: Failed to allocate memory for output buffer\n",
                           uVar2,"WEATHER");
          return 0xffffffff;
        }
      }
      iVar1 = DAT_ram_3fcc3a9c;
      (*(code *)&SUB_ram_4000048c)(DAT_ram_3fcc3aa0 + DAT_ram_3fcc3a9c,param_1[2],param_1[3]);
      DAT_ram_3fcc3a9c = iVar1 + param_1[3];
    }
    else if ((uVar8 == 5) && (DAT_ram_3fcc3aa0 != 0)) {
      iVar1 = FUN_ram_420137a4();
      if (iVar1 != 0) {
        uVar2 = FUN_ram_420137e0(iVar1,"weather");
        iVar3 = FUN_ram_42013996();
        if (iVar3 != 0) {
          uVar2 = FUN_ram_420137ca(uVar2,0);
          iVar3 = FUN_ram_420137e0(uVar2,&DAT_ram_3c0c16bc);
          iVar4 = FUN_ram_420137e0(uVar2,"description");
          iVar5 = FUN_ram_420137e0(uVar2,&DAT_ram_3c0c39cc);
          DAT_ram_3fcbff6c = 0;
          DAT_ram_3fcbff70 = 0;
          DAT_ram_3fcbff74 = 0;
          DAT_ram_3fcbff78 = 0;
          DAT_ram_3fcbff7c = 0;
          uVar2 = *(undefined4 *)(iVar3 + 0x10);
          uVar8 = (*(code *)&SUB_ram_400004a8)(uVar2);
          if (uVar8 < 0x10) {
            (*(code *)&SUB_ram_40000498)(&DAT_ram_3fcbff6c,uVar2);
          }
          else {
            (*(code *)&SUB_ram_4000049c)(&DAT_ram_3fcbff6c,uVar2,0xf);
          }
          DAT_ram_3fcbff80 = 0;
          DAT_ram_3fcbff84 = 0;
          DAT_ram_3fcbff88 = 0;
          DAT_ram_3fcbff8c = 0;
          DAT_ram_3fcbff90 = 0;
          uVar2 = *(undefined4 *)(iVar4 + 0x10);
          uVar8 = (*(code *)&SUB_ram_400004a8)(uVar2);
          if (uVar8 < 0x10) {
            (*(code *)&SUB_ram_40000498)(&DAT_ram_3fcbff80,uVar2);
          }
          else {
            (*(code *)&SUB_ram_4000049c)(&DAT_ram_3fcbff80,uVar2,0xf);
          }
          DAT_ram_3fcc3aac = 0;
          DAT_ram_3fcc3ab0 = 0;
          uVar2 = *(undefined4 *)(iVar5 + 0x10);
          uVar8 = (*(code *)&SUB_ram_400004a8)(uVar2);
          if (uVar8 < 6) {
            (*(code *)&SUB_ram_40000498)(&DAT_ram_3fcc3aac,uVar2);
          }
          else {
            (*(code *)&SUB_ram_4000049c)(&DAT_ram_3fcc3aac,uVar2,5);
          }
          iVar3 = (*(code *)&SUB_ram_400004ac)(&DAT_ram_3fcc3aac,&DAT_ram_3c0c39d4);
          if (iVar3 == 0) {
            iVar3 = (*(code *)&SUB_ram_400004ac)(&DAT_ram_3fcc3aac,&DAT_ram_3c0c39d8);
            if (iVar3 == 0) {
              iVar3 = (*(code *)&SUB_ram_400004ac)(&DAT_ram_3fcc3aac,&DAT_ram_3c0c39dc);
              if (iVar3 == 0) {
                iVar3 = (*(code *)&SUB_ram_400004ac)(&DAT_ram_3fcc3aac,&DAT_ram_3c0c39e0);
                if (iVar3 == 0) {
                  iVar3 = (*(code *)&SUB_ram_400004ac)(&DAT_ram_3fcc3aac,&DAT_ram_3c0c39e4);
                  if (iVar3 == 0) {
                    iVar3 = (*(code *)&SUB_ram_400004ac)(&DAT_ram_3fcc3aac,&DAT_ram_3c0c39e8);
                    if (iVar3 == 0) {
                      iVar3 = (*(code *)&SUB_ram_400004ac)(&DAT_ram_3fcc3aac,&DAT_ram_3c0c39ec);
                      if (iVar3 == 0) {
                        iVar3 = (*(code *)&SUB_ram_400004ac)(&DAT_ram_3fcc3aac,&DAT_ram_3c0c39f0);
                        if (iVar3 == 0) {
                          iVar3 = (*(code *)&SUB_ram_400004ac)(&DAT_ram_3fcc3aac,&DAT_ram_3c0c39f4);
                          if (iVar3 == 0) {
                            iVar3 = (*(code *)&SUB_ram_400004ac)
                                              (&DAT_ram_3fcc3aac,&DAT_ram_3c0c39f8);
                            if (iVar3 == 0) {
                              iVar3 = (*(code *)&SUB_ram_400004ac)
                                                (&DAT_ram_3fcc3aac,&DAT_ram_3c0c39fc);
                              if (iVar3 == 0) {
                                iVar3 = (*(code *)&SUB_ram_400004ac)
                                                  (&DAT_ram_3fcc3aac,&DAT_ram_3c0c3a00);
                                if (iVar3 == 0) {
                                  iVar3 = (*(code *)&SUB_ram_400004ac)
                                                    (&DAT_ram_3fcc3aac,&DAT_ram_3c0c3a04);
                                  if (iVar3 == 0) {
                                    iVar3 = (*(code *)&SUB_ram_400004ac)
                                                      (&DAT_ram_3fcc3aac,&DAT_ram_3c0c3a08);
                                    if (iVar3 == 0) {
                                      iVar3 = (*(code *)&SUB_ram_400004ac)
                                                        (&DAT_ram_3fcc3aac,&DAT_ram_3c0c3a0c);
                                      if (iVar3 == 0) {
                                        iVar3 = (*(code *)&SUB_ram_400004ac)
                                                          (&DAT_ram_3fcc3aac,&DAT_ram_3c0c3a10);
                                        if (iVar3 == 0) {
                                          iVar3 = (*(code *)&SUB_ram_400004ac)
                                                            (&DAT_ram_3fcc3aac,&DAT_ram_3c0c3a14);
                                          if (iVar3 == 0) {
                                            iVar3 = (*(code *)&SUB_ram_400004ac)
                                                              (&DAT_ram_3fcc3aac,&DAT_ram_3c0c3a18);
                                            if (iVar3 == 0) {
                                              DAT_ram_3fcc3aa8 = 0;
                                            }
                                            else {
                                              DAT_ram_3fcc3aa8 = 0x3b6c00;
                                            }
                                          }
                                          else {
                                            DAT_ram_3fcc3aa8 = 0x3b3000;
                                          }
                                        }
                                        else {
                                          DAT_ram_3fcc3aa8 = 0x3af400;
                                        }
                                      }
                                      else {
                                        DAT_ram_3fcc3aa8 = 0x3ab800;
                                      }
                                    }
                                    else {
                                      DAT_ram_3fcc3aa8 = 0x3a7c00;
                                    }
                                  }
                                  else {
                                    DAT_ram_3fcc3aa8 = 0x3a4000;
                                  }
                                }
                                else {
                                  DAT_ram_3fcc3aa8 = 0x3a0400;
                                }
                              }
                              else {
                                DAT_ram_3fcc3aa8 = 0x39c800;
                              }
                            }
                            else {
                              DAT_ram_3fcc3aa8 = 0x398c00;
                            }
                          }
                          else {
                            DAT_ram_3fcc3aa8 = 0x395000;
                          }
                        }
                        else {
                          DAT_ram_3fcc3aa8 = 0x391400;
                        }
                      }
                      else {
                        DAT_ram_3fcc3aa8 = 0x38d800;
                      }
                    }
                    else {
                      DAT_ram_3fcc3aa8 = 0x389c00;
                    }
                  }
                  else {
                    DAT_ram_3fcc3aa8 = 0x386000;
                  }
                }
                else {
                  DAT_ram_3fcc3aa8 = 0x382400;
                }
              }
              else {
                DAT_ram_3fcc3aa8 = 0x37e800;
              }
            }
            else {
              DAT_ram_3fcc3aa8 = 0x37ac00;
            }
          }
          else {
            DAT_ram_3fcc3aa8 = 0x377000;
          }
        }
        iVar3 = FUN_ram_420137e0(iVar1,&DAT_ram_3c0c16bc);
        uVar10 = CONCAT44(DAT_ram_3fcc3a34,DAT_ram_3fcc3a30);
        if (iVar3 != 0) {
          iVar4 = FUN_ram_420137e0(iVar3,&DAT_ram_3c0c3a1c);
          iVar5 = FUN_ram_420137e0(iVar3,"humidity");
          iVar6 = FUN_ram_420137e0(iVar3,"temp_min");
          iVar7 = FUN_ram_420137e0(iVar3,"temp_max");
          FUN_ram_420137e0(iVar3,"pressure");
          (*(code *)&SUB_ram_40000a9c)
                    (*(undefined4 *)(iVar4 + 0x18),*(undefined4 *)(iVar4 + 0x1c),DAT_ram_3c0d6348,
                     DAT_ram_3c0d634c);
          weather_temperature_c_at_3fcc3a4c = (*(code *)&SUB_ram_40000a34)();
          weather_humidity_at_3fcc3a48 =
               (*(code *)&SUB_ram_40000a34)
                         (*(undefined4 *)(iVar5 + 0x18),*(undefined4 *)(iVar5 + 0x1c));
          uVar10 = (*(code *)&SUB_ram_40000a9c)
                             (*(undefined4 *)(iVar7 + 0x18),*(undefined4 *)(iVar7 + 0x1c),
                              DAT_ram_3c0d6348,DAT_ram_3c0d634c);
          DAT_ram_3fcc3a3c = (undefined4)((ulonglong)uVar10 >> 0x20);
          DAT_ram_3fcc3a38 = (undefined4)uVar10;
          uVar10 = (*(code *)&SUB_ram_40000a9c)
                             (*(undefined4 *)(iVar6 + 0x18),*(undefined4 *)(iVar6 + 0x1c),
                              DAT_ram_3c0d6348,DAT_ram_3c0d634c);
        }
        DAT_ram_3fcc3a34 = (undefined4)((ulonglong)uVar10 >> 0x20);
        DAT_ram_3fcc3a30 = (undefined4)uVar10;
        iVar3 = FUN_ram_420137e0(iVar1,&DAT_ram_3c0c3a54);
        if (iVar3 != 0) {
          iVar4 = FUN_ram_420137e0(iVar3,"speed");
          iVar3 = FUN_ram_420137e0(iVar3,&DAT_ram_3c0c3a64);
          DAT_ram_3fcc3a40 = *(undefined4 *)(iVar4 + 0x18);
          DAT_ram_3fcc3a44 = *(undefined4 *)(iVar4 + 0x1c);
          DAT_ram_3fcbff94 = 0;
          _DAT_ram_3fcbff98 = 0;
          DAT_ram_3fcbff9c._0_1_ = '\0';
          DAT_ram_3fcbff9c._1_1_ = '\0';
          DAT_ram_3fcbff9c._2_1_ = '\0';
          DAT_ram_3fcbff9c._3_1_ = '\0';
          DAT_ram_3fcbffa0._0_1_ = '\0';
          DAT_ram_3fcbffa0._1_1_ = '\0';
          DAT_ram_3fcbffa0._2_1_ = '\0';
          DAT_ram_3fcbffa0._3_1_ = '\0';
          DAT_ram_3fcbffa4 = 0;
          uVar2 = *(undefined4 *)(iVar3 + 0x18);
          uVar9 = *(undefined4 *)(iVar3 + 0x1c);
          iVar3 = (*(code *)&SUB_ram_40000a6c)(uVar2,uVar9,DAT_ram_3c0d6350,DAT_ram_3c0d6354);
          if ((iVar3 < 0) &&
             (iVar3 = (*(code *)&SUB_ram_40000a84)(uVar2,uVar9,DAT_ram_3c0d6358,DAT_ram_3c0d635c),
             -1 < iVar3)) {
            iVar3 = (*(code *)&SUB_ram_40000a84)(uVar2,uVar9,DAT_ram_3c0d6360,DAT_ram_3c0d6364);
            if (iVar3 < 0) {
              DAT_ram_3fcbff94._0_1_ = s_North_Northeast_ram_3c0c3a68[0];
              DAT_ram_3fcbff94._1_1_ = s_North_Northeast_ram_3c0c3a68[1];
              DAT_ram_3fcbff94._2_1_ = s_North_Northeast_ram_3c0c3a68[2];
              DAT_ram_3fcbff94._3_1_ = s_North_Northeast_ram_3c0c3a68[3];
              DAT_ram_3fcbff98._0_1_ = s_North_Northeast_ram_3c0c3a68[4];
              DAT_ram_3fcbff98._1_1_ = s_North_Northeast_ram_3c0c3a68[5];
              DAT_ram_3fcbff98_1._1_1_ = s_North_Northeast_ram_3c0c3a68[6];
              DAT_ram_3fcbff98_1._2_1_ = s_North_Northeast_ram_3c0c3a68[7];
              DAT_ram_3fcbff9c._0_1_ = s_North_Northeast_ram_3c0c3a68[8];
              DAT_ram_3fcbff9c._1_1_ = s_North_Northeast_ram_3c0c3a68[9];
              DAT_ram_3fcbff9c._2_1_ = s_North_Northeast_ram_3c0c3a68[10];
              DAT_ram_3fcbff9c._3_1_ = s_North_Northeast_ram_3c0c3a68[0xb];
              DAT_ram_3fcbffa0._0_1_ = s_North_Northeast_ram_3c0c3a68[0xc];
              DAT_ram_3fcbffa0._1_1_ = s_North_Northeast_ram_3c0c3a68[0xd];
              DAT_ram_3fcbffa0._2_1_ = s_North_Northeast_ram_3c0c3a68[0xe];
              DAT_ram_3fcbffa0._3_1_ = s_North_Northeast_ram_3c0c3a68[0xf];
            }
            else {
              iVar3 = (*(code *)&SUB_ram_40000a84)(uVar2,uVar9,DAT_ram_3c0d6368,DAT_ram_3c0d636c);
              if (iVar3 < 0) {
                DAT_ram_3fcbff94._0_1_ = 'N';
                DAT_ram_3fcbff94._1_1_ = 'o';
                DAT_ram_3fcbff94._2_1_ = 'r';
                DAT_ram_3fcbff94._3_1_ = 't';
                _DAT_ram_3fcbff98 = 0x73616568;
                DAT_ram_3fcbff9c = CONCAT22(DAT_ram_3fcbff9c._2_2_,0x74);
              }
              else {
                iVar3 = (*(code *)&SUB_ram_40000a84)(uVar2,uVar9,DAT_ram_3c0d6370,DAT_ram_3c0d6374);
                if (iVar3 < 0) {
                  DAT_ram_3fcbff94._0_1_ = s_East_Northeast_ram_3c0c3a78[0];
                  DAT_ram_3fcbff94._1_1_ = s_East_Northeast_ram_3c0c3a78[1];
                  DAT_ram_3fcbff94._2_1_ = s_East_Northeast_ram_3c0c3a78[2];
                  DAT_ram_3fcbff94._3_1_ = s_East_Northeast_ram_3c0c3a78[3];
                  DAT_ram_3fcbff98._0_1_ = s_East_Northeast_ram_3c0c3a78[4];
                  DAT_ram_3fcbff98._1_1_ = s_East_Northeast_ram_3c0c3a78[5];
                  DAT_ram_3fcbff98_1._1_1_ = s_East_Northeast_ram_3c0c3a78[6];
                  DAT_ram_3fcbff98_1._2_1_ = s_East_Northeast_ram_3c0c3a78[7];
                  DAT_ram_3fcbff9c._0_1_ = s_East_Northeast_ram_3c0c3a78[8];
                  DAT_ram_3fcbff9c._1_1_ = s_East_Northeast_ram_3c0c3a78[9];
                  DAT_ram_3fcbff9c._2_1_ = s_East_Northeast_ram_3c0c3a78[10];
                  DAT_ram_3fcbff9c._3_1_ = s_East_Northeast_ram_3c0c3a78[0xb];
                  DAT_ram_3fcbffa0._0_3_ =
                       CONCAT12(s_East_Northeast_ram_3c0c3a78[0xe],
                                s_East_Northeast_ram_3c0c3a78._12_2_);
                }
                else {
                  iVar3 = (*(code *)&SUB_ram_40000a84)
                                    (uVar2,uVar9,DAT_ram_3c0d6378,DAT_ram_3c0d637c);
                  if (iVar3 < 0) {
                    DAT_ram_3fcbff94._0_1_ = 'E';
                    DAT_ram_3fcbff94._1_1_ = 'a';
                    DAT_ram_3fcbff94._2_1_ = 's';
                    DAT_ram_3fcbff94._3_1_ = 't';
                    _DAT_ram_3fcbff98 = _DAT_ram_3fcbff98 & 0xffffff00;
                  }
                  else {
                    iVar3 = (*(code *)&SUB_ram_40000a84)
                                      (uVar2,uVar9,DAT_ram_3c0d6380,DAT_ram_3c0d6384);
                    if (iVar3 < 0) {
                      DAT_ram_3fcbff94._0_1_ = s_East_Southeast_ram_3c0c3a88[0];
                      DAT_ram_3fcbff94._1_1_ = s_East_Southeast_ram_3c0c3a88[1];
                      DAT_ram_3fcbff94._2_1_ = s_East_Southeast_ram_3c0c3a88[2];
                      DAT_ram_3fcbff94._3_1_ = s_East_Southeast_ram_3c0c3a88[3];
                      DAT_ram_3fcbff98._0_1_ = s_East_Southeast_ram_3c0c3a88[4];
                      DAT_ram_3fcbff98._1_1_ = s_East_Southeast_ram_3c0c3a88[5];
                      DAT_ram_3fcbff98_1._1_1_ = s_East_Southeast_ram_3c0c3a88[6];
                      DAT_ram_3fcbff98_1._2_1_ = s_East_Southeast_ram_3c0c3a88[7];
                      DAT_ram_3fcbff9c._0_1_ = s_East_Southeast_ram_3c0c3a88[8];
                      DAT_ram_3fcbff9c._1_1_ = s_East_Southeast_ram_3c0c3a88[9];
                      DAT_ram_3fcbff9c._2_1_ = s_East_Southeast_ram_3c0c3a88[10];
                      DAT_ram_3fcbff9c._3_1_ = s_East_Southeast_ram_3c0c3a88[0xb];
                      DAT_ram_3fcbffa0._0_3_ =
                           CONCAT12(s_East_Southeast_ram_3c0c3a88[0xe],
                                    s_East_Southeast_ram_3c0c3a88._12_2_);
                    }
                    else {
                      iVar3 = (*(code *)&SUB_ram_40000a84)
                                        (uVar2,uVar9,DAT_ram_3c0d6388,DAT_ram_3c0d638c);
                      if (iVar3 < 0) {
                        DAT_ram_3fcbff94._0_1_ = s_Southeast_ram_3c0c3a98[0];
                        DAT_ram_3fcbff94._1_1_ = s_Southeast_ram_3c0c3a98[1];
                        DAT_ram_3fcbff94._2_1_ = s_Southeast_ram_3c0c3a98[2];
                        DAT_ram_3fcbff94._3_1_ = s_Southeast_ram_3c0c3a98[3];
                        DAT_ram_3fcbff98._0_1_ = s_Southeast_ram_3c0c3a98[4];
                        DAT_ram_3fcbff98._1_1_ = s_Southeast_ram_3c0c3a98[5];
                        DAT_ram_3fcbff98_1._1_1_ = s_Southeast_ram_3c0c3a98[6];
                        DAT_ram_3fcbff98_1._2_1_ = s_Southeast_ram_3c0c3a98[7];
                        DAT_ram_3fcbff9c =
                             CONCAT22(DAT_ram_3fcbff9c._2_2_,s_Southeast_ram_3c0c3a98._8_2_);
                      }
                      else {
                        iVar3 = (*(code *)&SUB_ram_40000a84)
                                          (uVar2,uVar9,DAT_ram_3c0d6390,DAT_ram_3c0d6394);
                        if (iVar3 < 0) {
                          DAT_ram_3fcbff94._0_1_ = s_South_Southeast_ram_3c0c3aa4[0];
                          DAT_ram_3fcbff94._1_1_ = s_South_Southeast_ram_3c0c3aa4[1];
                          DAT_ram_3fcbff94._2_1_ = s_South_Southeast_ram_3c0c3aa4[2];
                          DAT_ram_3fcbff94._3_1_ = s_South_Southeast_ram_3c0c3aa4[3];
                          DAT_ram_3fcbff98._0_1_ = s_South_Southeast_ram_3c0c3aa4[4];
                          DAT_ram_3fcbff98._1_1_ = s_South_Southeast_ram_3c0c3aa4[5];
                          DAT_ram_3fcbff98_1._1_1_ = s_South_Southeast_ram_3c0c3aa4[6];
                          DAT_ram_3fcbff98_1._2_1_ = s_South_Southeast_ram_3c0c3aa4[7];
                          DAT_ram_3fcbff9c._0_1_ = s_South_Southeast_ram_3c0c3aa4[8];
                          DAT_ram_3fcbff9c._1_1_ = s_South_Southeast_ram_3c0c3aa4[9];
                          DAT_ram_3fcbff9c._2_1_ = s_South_Southeast_ram_3c0c3aa4[10];
                          DAT_ram_3fcbff9c._3_1_ = s_South_Southeast_ram_3c0c3aa4[0xb];
                          DAT_ram_3fcbffa0._0_1_ = s_South_Southeast_ram_3c0c3aa4[0xc];
                          DAT_ram_3fcbffa0._1_1_ = s_South_Southeast_ram_3c0c3aa4[0xd];
                          DAT_ram_3fcbffa0._2_1_ = s_South_Southeast_ram_3c0c3aa4[0xe];
                          DAT_ram_3fcbffa0._3_1_ = s_South_Southeast_ram_3c0c3aa4[0xf];
                        }
                        else {
                          iVar3 = (*(code *)&SUB_ram_40000a84)
                                            (uVar2,uVar9,DAT_ram_3c0d6398,DAT_ram_3c0d639c);
                          if (iVar3 < 0) {
                            DAT_ram_3fcbff94._0_1_ = 'S';
                            DAT_ram_3fcbff94._1_1_ = 'o';
                            DAT_ram_3fcbff94._2_1_ = 'u';
                            DAT_ram_3fcbff94._3_1_ = 't';
                            _DAT_ram_3fcbff98 = CONCAT22(DAT_ram_3fcbff98_1._1_2_,0x68);
                          }
                          else {
                            iVar3 = (*(code *)&SUB_ram_40000a84)
                                              (uVar2,uVar9,DAT_ram_3c0d63a0,DAT_ram_3c0d63a4);
                            if (iVar3 < 0) {
                              DAT_ram_3fcbff94._0_1_ = s_South_Southwest_ram_3c0c3ab4[0];
                              DAT_ram_3fcbff94._1_1_ = s_South_Southwest_ram_3c0c3ab4[1];
                              DAT_ram_3fcbff94._2_1_ = s_South_Southwest_ram_3c0c3ab4[2];
                              DAT_ram_3fcbff94._3_1_ = s_South_Southwest_ram_3c0c3ab4[3];
                              DAT_ram_3fcbff98._0_1_ = s_South_Southwest_ram_3c0c3ab4[4];
                              DAT_ram_3fcbff98._1_1_ = s_South_Southwest_ram_3c0c3ab4[5];
                              DAT_ram_3fcbff98_1._1_1_ = s_South_Southwest_ram_3c0c3ab4[6];
                              DAT_ram_3fcbff98_1._2_1_ = s_South_Southwest_ram_3c0c3ab4[7];
                              DAT_ram_3fcbff9c._0_1_ = s_South_Southwest_ram_3c0c3ab4[8];
                              DAT_ram_3fcbff9c._1_1_ = s_South_Southwest_ram_3c0c3ab4[9];
                              DAT_ram_3fcbff9c._2_1_ = s_South_Southwest_ram_3c0c3ab4[10];
                              DAT_ram_3fcbff9c._3_1_ = s_South_Southwest_ram_3c0c3ab4[0xb];
                              DAT_ram_3fcbffa0._0_1_ = s_South_Southwest_ram_3c0c3ab4[0xc];
                              DAT_ram_3fcbffa0._1_1_ = s_South_Southwest_ram_3c0c3ab4[0xd];
                              DAT_ram_3fcbffa0._2_1_ = s_South_Southwest_ram_3c0c3ab4[0xe];
                              DAT_ram_3fcbffa0._3_1_ = s_South_Southwest_ram_3c0c3ab4[0xf];
                            }
                            else {
                              iVar3 = (*(code *)&SUB_ram_40000a84)
                                                (uVar2,uVar9,DAT_ram_3c0d63a8,DAT_ram_3c0d63ac);
                              if (iVar3 < 0) {
                                DAT_ram_3fcbff94._0_1_ = s_Southwest_ram_3c0c3ac4[0];
                                DAT_ram_3fcbff94._1_1_ = s_Southwest_ram_3c0c3ac4[1];
                                DAT_ram_3fcbff94._2_1_ = s_Southwest_ram_3c0c3ac4[2];
                                DAT_ram_3fcbff94._3_1_ = s_Southwest_ram_3c0c3ac4[3];
                                DAT_ram_3fcbff98._0_1_ = s_Southwest_ram_3c0c3ac4[4];
                                DAT_ram_3fcbff98._1_1_ = s_Southwest_ram_3c0c3ac4[5];
                                DAT_ram_3fcbff98_1._1_1_ = s_Southwest_ram_3c0c3ac4[6];
                                DAT_ram_3fcbff98_1._2_1_ = s_Southwest_ram_3c0c3ac4[7];
                                DAT_ram_3fcbff9c =
                                     CONCAT22(DAT_ram_3fcbff9c._2_2_,s_Southwest_ram_3c0c3ac4._8_2_)
                                ;
                              }
                              else {
                                iVar3 = (*(code *)&SUB_ram_40000a84)
                                                  (uVar2,uVar9,DAT_ram_3c0d63b0,DAT_ram_3c0d63b4);
                                if (iVar3 < 0) {
                                  DAT_ram_3fcbff94._0_1_ = s_West_Southwest_ram_3c0c3ad0[0];
                                  DAT_ram_3fcbff94._1_1_ = s_West_Southwest_ram_3c0c3ad0[1];
                                  DAT_ram_3fcbff94._2_1_ = s_West_Southwest_ram_3c0c3ad0[2];
                                  DAT_ram_3fcbff94._3_1_ = s_West_Southwest_ram_3c0c3ad0[3];
                                  DAT_ram_3fcbff98._0_1_ = s_West_Southwest_ram_3c0c3ad0[4];
                                  DAT_ram_3fcbff98._1_1_ = s_West_Southwest_ram_3c0c3ad0[5];
                                  DAT_ram_3fcbff98_1._1_1_ = s_West_Southwest_ram_3c0c3ad0[6];
                                  DAT_ram_3fcbff98_1._2_1_ = s_West_Southwest_ram_3c0c3ad0[7];
                                  DAT_ram_3fcbff9c._0_1_ = s_West_Southwest_ram_3c0c3ad0[8];
                                  DAT_ram_3fcbff9c._1_1_ = s_West_Southwest_ram_3c0c3ad0[9];
                                  DAT_ram_3fcbff9c._2_1_ = s_West_Southwest_ram_3c0c3ad0[10];
                                  DAT_ram_3fcbff9c._3_1_ = s_West_Southwest_ram_3c0c3ad0[0xb];
                                  DAT_ram_3fcbffa0._0_3_ =
                                       CONCAT12(s_West_Southwest_ram_3c0c3ad0[0xe],
                                                s_West_Southwest_ram_3c0c3ad0._12_2_);
                                }
                                else {
                                  iVar3 = (*(code *)&SUB_ram_40000a84)
                                                    (uVar2,uVar9,DAT_ram_3c0d63b8,DAT_ram_3c0d63bc);
                                  if (iVar3 < 0) {
                                    DAT_ram_3fcbff94._0_1_ = 'W';
                                    DAT_ram_3fcbff94._1_1_ = 'e';
                                    DAT_ram_3fcbff94._2_1_ = 's';
                                    DAT_ram_3fcbff94._3_1_ = 't';
                                    _DAT_ram_3fcbff98 = _DAT_ram_3fcbff98 & 0xffffff00;
                                  }
                                  else {
                                    iVar3 = (*(code *)&SUB_ram_40000a84)
                                                      (uVar2,uVar9,DAT_ram_3c0d63c0,DAT_ram_3c0d63c4
                                                      );
                                    if (iVar3 < 0) {
                                      DAT_ram_3fcbff94._0_1_ = s_West_Northwest_ram_3c0c3ae0[0];
                                      DAT_ram_3fcbff94._1_1_ = s_West_Northwest_ram_3c0c3ae0[1];
                                      DAT_ram_3fcbff94._2_1_ = s_West_Northwest_ram_3c0c3ae0[2];
                                      DAT_ram_3fcbff94._3_1_ = s_West_Northwest_ram_3c0c3ae0[3];
                                      DAT_ram_3fcbff98._0_1_ = s_West_Northwest_ram_3c0c3ae0[4];
                                      DAT_ram_3fcbff98._1_1_ = s_West_Northwest_ram_3c0c3ae0[5];
                                      DAT_ram_3fcbff98_1._1_1_ = s_West_Northwest_ram_3c0c3ae0[6];
                                      DAT_ram_3fcbff98_1._2_1_ = s_West_Northwest_ram_3c0c3ae0[7];
                                      DAT_ram_3fcbff9c._0_1_ = s_West_Northwest_ram_3c0c3ae0[8];
                                      DAT_ram_3fcbff9c._1_1_ = s_West_Northwest_ram_3c0c3ae0[9];
                                      DAT_ram_3fcbff9c._2_1_ = s_West_Northwest_ram_3c0c3ae0[10];
                                      DAT_ram_3fcbff9c._3_1_ = s_West_Northwest_ram_3c0c3ae0[0xb];
                                      DAT_ram_3fcbffa0._0_3_ =
                                           CONCAT12(s_West_Northwest_ram_3c0c3ae0[0xe],
                                                    s_West_Northwest_ram_3c0c3ae0._12_2_);
                                    }
                                    else {
                                      iVar3 = (*(code *)&SUB_ram_40000a84)
                                                        (uVar2,uVar9,DAT_ram_3c0d63c8,
                                                         DAT_ram_3c0d63cc);
                                      if (iVar3 < 0) {
                                        DAT_ram_3fcbff94._0_1_ = s_Northwest_ram_3c0c3af0[0];
                                        DAT_ram_3fcbff94._1_1_ = s_Northwest_ram_3c0c3af0[1];
                                        DAT_ram_3fcbff94._2_1_ = s_Northwest_ram_3c0c3af0[2];
                                        DAT_ram_3fcbff94._3_1_ = s_Northwest_ram_3c0c3af0[3];
                                        DAT_ram_3fcbff98._0_1_ = s_Northwest_ram_3c0c3af0[4];
                                        DAT_ram_3fcbff98._1_1_ = s_Northwest_ram_3c0c3af0[5];
                                        DAT_ram_3fcbff98_1._1_1_ = s_Northwest_ram_3c0c3af0[6];
                                        DAT_ram_3fcbff98_1._2_1_ = s_Northwest_ram_3c0c3af0[7];
                                        DAT_ram_3fcbff9c =
                                             CONCAT22(DAT_ram_3fcbff9c._2_2_,
                                                      s_Northwest_ram_3c0c3af0._8_2_);
                                      }
                                      else {
                                        DAT_ram_3fcbff9c._0_1_ = s_North_Northwest_ram_3c0c3afc[8];
                                        DAT_ram_3fcbff9c._1_1_ = s_North_Northwest_ram_3c0c3afc[9];
                                        DAT_ram_3fcbff9c._2_1_ = s_North_Northwest_ram_3c0c3afc[10];
                                        DAT_ram_3fcbff9c._3_1_ = s_North_Northwest_ram_3c0c3afc[0xb]
                                        ;
                                        DAT_ram_3fcbffa0._0_1_ = s_North_Northwest_ram_3c0c3afc[0xc]
                                        ;
                                        DAT_ram_3fcbffa0._1_1_ = s_North_Northwest_ram_3c0c3afc[0xd]
                                        ;
                                        DAT_ram_3fcbffa0._2_1_ = s_North_Northwest_ram_3c0c3afc[0xe]
                                        ;
                                        DAT_ram_3fcbffa0._3_1_ = s_North_Northwest_ram_3c0c3afc[0xf]
                                        ;
                                        DAT_ram_3fcbff94._0_1_ = s_North_Northwest_ram_3c0c3afc[0];
                                        DAT_ram_3fcbff94._1_1_ = s_North_Northwest_ram_3c0c3afc[1];
                                        DAT_ram_3fcbff94._2_1_ = s_North_Northwest_ram_3c0c3afc[2];
                                        DAT_ram_3fcbff94._3_1_ = s_North_Northwest_ram_3c0c3afc[3];
                                        DAT_ram_3fcbff98._0_1_ = s_North_Northwest_ram_3c0c3afc[4];
                                        DAT_ram_3fcbff98._1_1_ = s_North_Northwest_ram_3c0c3afc[5];
                                        DAT_ram_3fcbff98_1._1_1_ = s_North_Northwest_ram_3c0c3afc[6]
                                        ;
                                        DAT_ram_3fcbff98_1._2_1_ = s_North_Northwest_ram_3c0c3afc[7]
                                        ;
                                      }
                                    }
                                  }
                                }
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
          else {
            DAT_ram_3fcbff94._0_1_ = 'N';
            DAT_ram_3fcbff94._1_1_ = 'o';
            DAT_ram_3fcbff94._2_1_ = 'r';
            DAT_ram_3fcbff94._3_1_ = 't';
            _DAT_ram_3fcbff98 = CONCAT22(DAT_ram_3fcbff98_1._1_2_,0x68);
          }
        }
        FUN_ram_420137e0(iVar1,"visibility");
        iVar3 = FUN_ram_420137e0(iVar1,&DAT_ram_3c0c3b18);
        if (iVar3 != 0) {
          uStack_28 = (*(code *)&SUB_ram_40000a30)
                                (*(undefined4 *)(iVar3 + 0x18),*(undefined4 *)(iVar3 + 0x1c));
          iVar3 = FUN_ram_420137e0(iVar1,"timezone");
          if (iVar3 != 0) {
            uVar8 = (*(code *)&SUB_ram_40000a40)
                              (*(undefined4 *)(iVar3 + 0x18),*(undefined4 *)(iVar3 + 0x1c));
            uStack_28 = uStack_28 + (ulonglong)uVar8;
          }
          DAT_ram_3fcc3aa4 = FUN_ram_420aa57a(&uStack_28);
          *(int *)(DAT_ram_3fcc3aa4 + 0x14) = *(int *)(DAT_ram_3fcc3aa4 + 0x14) + 0x76c;
        }
        DAT_ram_3fcc39d7 = 1;
        FUN_ram_4201322a(iVar1);
      }
      FUN_ram_4038e4da(DAT_ram_3fcc3aa0);
      DAT_ram_3fcc3aa0 = 0;
      DAT_ram_3fcc3a9c = 0;
    }
  }
  else if (uVar8 == 7) {
    FUN_ram_4203d3a6(param_1[1],&DAT_ram_3c0c3b3c,"user@example.com");
    FUN_ram_4203d3a6(param_1[1],"Accept","text/html");
    FUN_ram_4203e43e(param_1[1]);
  }
  return 0;
}

// Audit label: application_review; entry: ram:42010864; name: fetch_current_weather_at_42010864

void fetch_current_weather_at_42010864(void)

{
  char cVar1;
  void *arg0;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  char *pcVar5;
  char *pcVar6;
  char *apcStack_1d4 [19];
  undefined4 uStack_188;
  code *pcStack_178;
  char local_13c [12];
  char local_130 [288];

  (*(code *)&SUB_ram_40000488)(local_130 + 0x20,0,0x100);
  local_130[0] = '\0';
  local_130[1] = '\0';
  local_130[2] = '\0';
  local_130[3] = '\0';
  local_130[4] = '\0';
  local_130[5] = '\0';
  local_130[6] = '\0';
  local_130[7] = '\0';
  local_130[8] = '\0';
  local_130[9] = '\0';
  local_130[10] = '\0';
  local_130[0xb] = '\0';
  local_130[0xc] = '\0';
  local_130[0xd] = '\0';
  local_130[0xe] = '\0';
  local_130[0xf] = '\0';
  local_130[0x10] = '\0';
  local_130[0x11] = '\0';
  local_130[0x12] = '\0';
  local_130[0x13] = '\0';
  local_130[0x14] = '\0';
  local_130[0x15] = '\0';
  local_130[0x16] = '\0';
  local_130[0x17] = '\0';
  local_130[0x18] = '\0';
  local_130[0x19] = '\0';
  local_130[0x1a] = '\0';
  local_130[0x1b] = '\0';
  local_130[0x1c] = '\0';
  local_130[0x1d] = '\0';
  local_130[0x1e] = '\0';
  local_130[0x1f] = '\0';
  pcVar5 = &city_name_at_3fcb7c77;
  pcVar6 = local_130;
  while( true ) {
    cVar1 = *pcVar5;
    if ((cVar1 == '\0') || (0x1e < (uint)((int)pcVar6 - (int)local_130))) break;
    if (cVar1 == ' ') {
      *pcVar6 = '%';
      pcVar6[1] = '2';
      pcVar6[2] = '0';
      pcVar6 = pcVar6 + 3;
    }
    else {
      *pcVar6 = cVar1;
      pcVar6 = pcVar6 + 1;
    }
    pcVar5 = pcVar5 + 1;
  }
  *pcVar6 = '\0';
  local_13c[0] = '\0';
  local_13c[1] = '\0';
  local_13c[2] = '\0';
  local_13c[3] = '\0';
  local_13c[4] = '\0';
  local_13c[5] = '\0';
  local_13c[6] = '\0';
  local_13c[7] = '\0';
  local_13c[8] = '\0';
  local_13c[9] = '\0';
  pcVar5 = &country_code_at_3fcb7c63;
  pcVar6 = local_13c;
  while( true ) {
    cVar1 = *pcVar5;
    if ((cVar1 == '\0') || (8 < (uint)((int)pcVar6 - (int)local_13c))) break;
    if (cVar1 == ' ') {
      *pcVar6 = '%';
      pcVar6[1] = '2';
      pcVar6[2] = '0';
      pcVar6 = pcVar6 + 3;
    }
    else {
      *pcVar6 = cVar1;
      pcVar6 = pcVar6 + 1;
    }
    pcVar5 = pcVar5 + 1;
  }
  *pcVar6 = '\0';
  (*(code *)&SUB_ram_400006a8)
            (local_130 + 0x20,"http://api.openweathermap.org/data/2.5/weather?q=%s,%s&appid=%s",
             local_130,local_13c,&weather_api_key_at_3fcb7cb8);
  (*(code *)&SUB_ram_40000488)(apcStack_1d4,0,0x98);
  uStack_188 = 10000;
  pcStack_178 = weather_http_event_handler_at_4200fccc;
  apcStack_1d4[0] = local_130 + 0x20;
  arg0 = (void *)esp_http_client_init(apcStack_1d4);
  iVar2 = esp_http_client_perform(arg0);
  if (iVar2 != 0) {
    uVar3 = FUN_ram_4038d3b4();
    uVar4 = FUN_ram_4201724e(iVar2);
    FUN_ram_4038d2a2(1,"WEATHER","E (%lu) %s: HTTP GET request failed: %s\n",uVar3,"WEATHER",uVar4);
  }
  esp_http_client_cleanup(arg0);
  return;
}
