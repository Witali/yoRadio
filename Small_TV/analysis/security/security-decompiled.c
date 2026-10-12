// Audit label: lwip_socket_reference; entry: ram:4200c74e; name: FUN_ram_4200c74e

void FUN_ram_4200c74e(void)

{
  int arg0;
  int iVar1;
  undefined4 uVar2;
  undefined4 *puVar3;
  uint uStack_134;
  undefined1 auStack_130 [16];
  undefined1 uStack_120;
  undefined1 uStack_11f;
  undefined2 uStack_11e;
  undefined4 uStack_11c;
  undefined1 auStack_110 [128];
  undefined1 auStack_90 [2];
  char cStack_8e;

  uStack_134 = 0x10;
  uStack_11c = 0;
  uStack_11f = 2;
  uStack_11e = 0x3500;
  arg0 = lwip_socket(2,2,0x11);
  if (arg0 < 0) {
    uVar2 = FUN_ram_4038d3b4();
    puVar3 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
    FUN_ram_4038d2a2(1,"wifi station","E (%lu) %s: Unable to create socket: errno %d\n",uVar2,
                     "wifi station",*puVar3);
    FUN_ram_403894c6(0);
  }
  else {
    iVar1 = lwip_bind(arg0,&uStack_120,0x10);
    if (-1 < iVar1) {
      do {
        iVar1 = lwip_recvfrom(arg0,auStack_90,0x7f,0,auStack_130,&uStack_134);
        if ((0 < iVar1) && (-1 < cStack_8e)) {
          (*(code *)&SUB_ram_4000048c)(auStack_110,auStack_90,iVar1);
          auStack_110[2] = 0x84;
          auStack_110[3] = 0;
          auStack_110[6] = 0;
          auStack_110[7] = 1;
          auStack_110[8] = 0;
          auStack_110[9] = 0;
          auStack_110[10] = 0;
          auStack_110[0xb] = 0;
          auStack_110[iVar1] = 0xc0;
          auStack_110[iVar1 + 1] = 0xc;
          auStack_110[iVar1 + 2] = 0;
          auStack_110[iVar1 + 3] = 1;
          auStack_110[iVar1 + 4] = 0;
          auStack_110[iVar1 + 5] = 1;
          auStack_110[iVar1 + 6] = 0;
          auStack_110[iVar1 + 7] = 0;
          auStack_110[iVar1 + 8] = 0;
          auStack_110[iVar1 + 9] = 0x3c;
          auStack_110[iVar1 + 10] = 0;
          auStack_110[iVar1 + 0xb] = 4;
          auStack_110[iVar1 + 0xc] = 0xc0;
          auStack_110[iVar1 + 0xd] = 0xa8;
          auStack_110[iVar1 + 0xe] = 0x2b;
          auStack_110[iVar1 + 0xf] = 1;
          lwip_sendto(arg0,auStack_110,iVar1 + 0x10,0,auStack_130,uStack_134);
        }
        vTaskDelay(1);
      } while( true );
    }
    uVar2 = FUN_ram_4038d3b4();
    puVar3 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
    FUN_ram_4038d2a2(1,"wifi station","E (%lu) %s: Socket unable to bind: errno %d\n",uVar2,
                     "wifi station",*puVar3);
    FUN_ram_420ab05c(arg0);
    FUN_ram_403894c6(0);
  }
  return;
}



// Audit label: uri_set_led_brightness; entry: ram:4200d66a; name: uri_set_led_brightness

undefined4 uri_set_led_brightness(undefined4 param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_50 [72];

  iVar1 = httpd_req_recv(param_1,auStack_50,0x3f);
  if (iVar1 < 1) {
    FUN_ram_4203b382(param_1,8,0);
    uVar2 = 0xffffffff;
  }
  else {
    auStack_50[iVar1] = 0;
    iVar1 = (*(code *)&SUB_ram_400004ac)(auStack_50,"ledBrightness=");
    if (iVar1 != 0) {
      iVar1 = (*(code *)&SUB_ram_40000580)(iVar1 + 0xe);
      DAT_ram_3fcb7d1c = iVar1 * -10 + 1000;
      DAT_ram_3fcc39f2 = 1;
      DAT_ram_3fcc39e0 = 1;
      DAT_ram_3fcc39dc = 0x32;
    }
    FUN_ram_4203b114(param_1,"Connection","close");
    FUN_ram_4203b192(param_1,&DAT_ram_3c0c328c,2);
    uVar2 = 0;
  }
  return uVar2;
}



// Audit label: uri_SetTimeModeValue; entry: ram:4200d720; name: uri_SetTimeModeValue

undefined4 uri_SetTimeModeValue(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_24 [28];

  if (*(uint *)(param_1 + 0x20c) < 0x41) {
    iVar1 = httpd_req_recv(param_1,auStack_24,0x14);
    if (iVar1 < 1) {
      FUN_ram_4203b382(param_1,8,0);
      uVar2 = 0xffffffff;
    }
    else {
      auStack_24[iVar1] = 0;
      iVar1 = (*(code *)&SUB_ram_400004ac)(auStack_24,"timemode");
      if ((*(byte *)(iVar1 + 0xb) - 0x30 & 0xff) < 3) {
        DAT_ram_3fcb7d18 = *(byte *)(iVar1 + 0xb) - 0x30;
        DAT_ram_3fcc39f5 = 1;
        DAT_ram_3fcc39e0 = 1;
        DAT_ram_3fcc39dc = 0x32;
        DAT_ram_3fcc3a26 = 1;
      }
      FUN_ram_4203b114(param_1,"Connection","close");
      FUN_ram_4203b192(param_1,&DAT_ram_3c0c328c,2);
      uVar2 = 0;
    }
  }
  else {
    FUN_ram_4203b382(param_1,9,0);
    uVar2 = 0xffffffff;
  }
  return uVar2;
}



// Audit label: uri_setclocktype; entry: ram:4200d7f0; name: uri_setclocktype

undefined4 uri_setclocktype(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_24 [28];

  if (*(uint *)(param_1 + 0x20c) < 0x41) {
    iVar1 = httpd_req_recv(param_1,auStack_24,0x14);
    if (iVar1 < 1) {
      FUN_ram_4203b382(param_1,8,0);
      uVar2 = 0xffffffff;
    }
    else {
      auStack_24[iVar1] = 0;
      iVar1 = (*(code *)&SUB_ram_400004ac)(auStack_24,"clocktype");
      if ((*(byte *)(iVar1 + 0xc) - 0x30 & 0xff) < 4) {
        DAT_ram_3fcb7d04 = *(byte *)(iVar1 + 0xc) - 0x30;
        DAT_ram_3fcc39e9 = 0;
        DAT_ram_3fcc39e0 = 1;
        DAT_ram_3fcc39dc = 0x32;
      }
      FUN_ram_4203b114(param_1,"Connection","close");
      FUN_ram_4203b192(param_1,&DAT_ram_3c0c328c,2);
      uVar2 = 0;
    }
  }
  else {
    FUN_ram_4203b382(param_1,9,0);
    uVar2 = 0xffffffff;
  }
  return uVar2;
}



// Audit label: uri_setgifvalue; entry: ram:4200d8b8; name: uri_setgifvalue

undefined4 uri_setgifvalue(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_20 [24];

  if (*(uint *)(param_1 + 0x20c) < 0x41) {
    iVar1 = httpd_req_recv(param_1,auStack_20,0x10);
    if (iVar1 < 1) {
      FUN_ram_4203b382(param_1,8,0);
      uVar2 = 0xffffffff;
    }
    else {
      auStack_20[iVar1] = 0;
      iVar1 = (*(code *)&SUB_ram_400004ac)(auStack_20,&DAT_ram_3c0c326c);
      if ((*(byte *)(iVar1 + 6) - 0x30 & 0xff) < 5) {
        DAT_ram_3fcb7d00 = *(byte *)(iVar1 + 6) - 0x30;
        DAT_ram_3fcc39e0 = 1;
        DAT_ram_3fcc39dc = 0x32;
      }
      FUN_ram_4203b114(param_1,"Connection","close");
      FUN_ram_4203b192(param_1,&DAT_ram_3c0c328c,2);
      uVar2 = 0;
    }
  }
  else {
    FUN_ram_4203b382(param_1,9,0);
    uVar2 = 0xffffffff;
  }
  return uVar2;
}



// Audit label: uri_finish_upload; entry: ram:4200d978; name: uri_finish_upload

undefined4 uri_finish_upload(undefined4 param_1)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 auStack_90 [136];

  iVar2 = httpd_req_recv(param_1,auStack_90,0x7f);
  iVar1 = DAT_ram_3fcbd2d4;
  if (iVar2 < 1) {
    FUN_ram_4203b382(param_1,0,"Failed to receive data");
    uVar3 = 0xffffffff;
  }
  else {
    auStack_90[iVar2] = 0;
    *(undefined4 *)(&DAT_ram_3fcb7ba4 + (DAT_ram_3fcbd2d4 + 0x67) * 4) = DAT_ram_3fcbd2d8;
    if (iVar1 == 1) {
      DAT_ram_3fcb7b9c = DAT_ram_3fcb7b9c | 1;
    }
    else if (iVar1 == 2) {
      DAT_ram_3fcb7b9c = DAT_ram_3fcb7b9c | 2;
    }
    else if (iVar1 == 3) {
      DAT_ram_3fcb7b9c = DAT_ram_3fcb7b9c | 4;
    }
    else if (iVar1 == 4) {
      DAT_ram_3fcb7b9c = DAT_ram_3fcb7b9c | 8;
    }
    else if (iVar1 == 5) {
      DAT_ram_3fcb7b9c = DAT_ram_3fcb7b9c | 0x10;
    }
    FUN_ram_42008a00();
    DAT_ram_3fcbd2d4 = 0;
    DAT_ram_3fcbd2d8 = 0;
    DAT_ram_3fcbd2dc = 0;
    DAT_ram_3fcbd2e0 = 0;
    DAT_ram_3fcbd2e4 = 0;
    DAT_ram_3fcbd2e8 = 0;
    FUN_ram_4203b15e(param_1,&DAT_ram_3c0c3288);
    FUN_ram_4203b114(param_1,"Connection","close");
    FUN_ram_4203b192(param_1,&DAT_ram_3c0c328c,2);
    DAT_ram_3fcc39d8 = 0;
    uVar3 = 0;
  }
  return uVar3;
}



// Audit label: uri_upload_chunk; entry: ram:4200dc58; name: uri_upload_chunk

undefined4 uri_upload_chunk(int param_1)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uStack_114;
  undefined1 auStack_110 [128];
  undefined1 auStack_90 [128];

  (*(code *)&SUB_ram_40000488)(auStack_90,0,0x80);
  (*(code *)&SUB_ram_40000488)(auStack_110,0,0x80);
  iVar1 = httpd_req_get_hdr_value_str(param_1,"Content-Type",auStack_110,0x80);
  if (iVar1 == 0) {
    iVar1 = *(int *)(param_1 + 0x20c);
    if (iVar1 == 0) {
      FUN_ram_4203b382(param_1,3,"Empty chunk");
      uVar3 = 0xffffffff;
    }
    else if (DAT_ram_3fcbd2d4 - 1U < 5) {
      if ((uint)(DAT_ram_3fcbd2dc + iVar1) < 0x19001) {
        iVar2 = httpd_req_recv(param_1,&DAT_ram_3fcbd2ec,iVar1);
        if (iVar2 == iVar1) {
          uStack_114 = 0;
          FUN_ram_4200db12(&DAT_ram_3fcbd2ec,iVar1,auStack_90,&uStack_114);
          FUN_ram_4203b15e(param_1,&DAT_ram_3c0c3288);
          FUN_ram_4203b114(param_1,"Connection","close");
          FUN_ram_4203b192(param_1,&DAT_ram_3c0c328c,2);
          uVar3 = 0;
        }
        else {
          FUN_ram_4203b382(param_1,3,"Incomplete chunk");
          uVar3 = 0xffffffff;
        }
      }
      else {
        FUN_ram_4203b382(param_1,3,"Out of memory");
        uVar3 = 0xffffffff;
      }
    }
    else {
      FUN_ram_4203b382(param_1,3,"No active upload");
      uVar3 = 0xffffffff;
    }
  }
  else {
    FUN_ram_4203b382(param_1,3,"Missing Content-Type");
    uVar3 = 0xffffffff;
  }
  return uVar3;
}



// Audit label: uri_start_upload; entry: ram:4200dda4; name: uri_start_upload

undefined4 uri_start_upload(undefined4 param_1)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  undefined1 auStack_120 [268];

  iVar2 = httpd_req_recv(param_1,auStack_120,0xff);
  if (iVar2 < 1) {
    FUN_ram_4203b382(param_1,0,"Failed to receive data");
    uVar6 = 0xffffffff;
  }
  else {
    auStack_120[iVar2] = 0;
    iVar2 = FUN_ram_420137a4(auStack_120);
    if (iVar2 == 0) {
      FUN_ram_4203b382(param_1,3,"Invalid JSON");
      uVar6 = 0xffffffff;
    }
    else {
      iVar3 = FUN_ram_420137e0(iVar2,"file_number");
      iVar4 = FUN_ram_420137e0(iVar2,"file_size");
      iVar5 = FUN_ram_420137e0(iVar2,"total_chunks");
      if (((iVar3 == 0) || (iVar4 == 0)) || (iVar5 == 0)) {
        FUN_ram_4201322a(iVar2);
        FUN_ram_4203b382(param_1,3,"Missing required fields");
        uVar6 = 0xffffffff;
      }
      else {
        iVar3 = *(int *)(iVar3 + 0x14);
        if (iVar3 - 1U < 5) {
          DAT_ram_3fcbd2d8 = *(uint *)(iVar4 + 0x14);
          DAT_ram_3fcbd2dc = 0;
          DAT_ram_3fcbd2e0 = *(undefined4 *)(iVar5 + 0x14);
          DAT_ram_3fcbd2e4 = 0;
          DAT_ram_3fcbd2e8 = 0;
          DAT_ram_3fcbd2d4 = iVar3;
          if (DAT_ram_3fcbd2d8 < 0x19001) {
            DAT_ram_3fcbd2e8 = (iVar3 + -1) * 0x19000 + 0x200000;
            for (uVar1 = 0; uVar1 < 0x19000; uVar1 = uVar1 + 0x1000) {
              esp_flash_erase_region(0,DAT_ram_3fcbd2e8 + uVar1,0x1000);
            }
            FUN_ram_4201322a(iVar2);
            FUN_ram_4203b15e(param_1,&DAT_ram_3c0c3288);
            FUN_ram_4203b114(param_1,"Connection","close");
            FUN_ram_4203b192(param_1,&DAT_ram_3c0c328c,2);
            DAT_ram_3fcc39d8 = 1;
            uVar6 = 0;
          }
          else {
            FUN_ram_4201322a(iVar2);
            FUN_ram_4203b382(param_1,3,"File too large");
            uVar6 = 0xffffffff;
          }
        }
        else {
          FUN_ram_4201322a(iVar2);
          FUN_ram_4203b382(param_1,3,"Invalid file number");
          uVar6 = 0xffffffff;
        }
      }
    }
  }
  return uVar6;
}



// Audit label: uri_set_checkbox_state; entry: ram:4200e2ec; name: uri_set_checkbox_state

undefined4 uri_set_checkbox_state(undefined4 param_1)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined1 auStack_a0 [136];

  iVar2 = httpd_req_recv(param_1,auStack_a0,0x7f);
  if (iVar2 < 1) {
    FUN_ram_4203b382(param_1,0,"Failed to receive data");
    uVar7 = 0xffffffff;
  }
  else {
    auStack_a0[iVar2] = 0;
    iVar2 = FUN_ram_420137a4(auStack_a0);
    if (iVar2 == 0) {
      FUN_ram_4203b382(param_1,3,"Invalid JSON");
      uVar7 = 0xffffffff;
    }
    else {
      iVar3 = FUN_ram_420137e0(iVar2,"checkbox_id");
      iVar4 = FUN_ram_420137e0(iVar2,"checked");
      if ((((iVar3 == 0) || (iVar5 = FUN_ram_42013984(iVar3), iVar5 == 0)) || (iVar4 == 0)) ||
         (iVar5 = FUN_ram_42013974(iVar4), iVar5 == 0)) {
        FUN_ram_4203b382(param_1,3,"Missing checkbox_id or checked field");
        FUN_ram_4201322a(iVar2);
        uVar7 = 0xffffffff;
      }
      else {
        uVar7 = *(undefined4 *)(iVar3 + 0x10);
        iVar3 = FUN_ram_42013962(iVar4);
        bVar1 = iVar3 != 0;
        iVar4 = (*(code *)&SUB_ram_400004a0)(uVar7,"file1-switch");
        if (iVar4 == 0) {
          if (iVar3 == 0) {
            DAT_ram_3fcb7d40 = DAT_ram_3fcb7d40 & 0xfffffffe;
          }
          else {
            DAT_ram_3fcb7d40 = DAT_ram_3fcb7d40 | 1;
          }
          DAT_ram_3fcc39e0 = 1;
          DAT_ram_3fcc39dc = 0x32;
          DAT_ram_3fcc3a88 = bVar1;
        }
        else {
          iVar4 = (*(code *)&SUB_ram_400004a0)(uVar7,"file2-switch");
          if (iVar4 == 0) {
            if (iVar3 == 0) {
              DAT_ram_3fcb7d40 = DAT_ram_3fcb7d40 & 0xfffffffd;
            }
            else {
              DAT_ram_3fcb7d40 = DAT_ram_3fcb7d40 | 2;
            }
            DAT_ram_3fcc39e0 = 1;
            DAT_ram_3fcc39dc = 0x32;
            DAT_ram_3fcc3a89 = bVar1;
          }
          else {
            iVar4 = (*(code *)&SUB_ram_400004a0)(uVar7,"file3-switch");
            if (iVar4 == 0) {
              if (iVar3 == 0) {
                DAT_ram_3fcb7d40 = DAT_ram_3fcb7d40 & 0xfffffffb;
              }
              else {
                DAT_ram_3fcb7d40 = DAT_ram_3fcb7d40 | 4;
              }
              DAT_ram_3fcc39e0 = 1;
              DAT_ram_3fcc39dc = 0x32;
              DAT_ram_3fcc3a8a = bVar1;
            }
            else {
              iVar4 = (*(code *)&SUB_ram_400004a0)(uVar7,"file4-switch");
              if (iVar4 == 0) {
                if (iVar3 == 0) {
                  DAT_ram_3fcb7d40 = DAT_ram_3fcb7d40 & 0xfffffff7;
                }
                else {
                  DAT_ram_3fcb7d40 = DAT_ram_3fcb7d40 | 8;
                }
                DAT_ram_3fcc39e0 = 1;
                DAT_ram_3fcc39dc = 0x32;
                DAT_ram_3fcc3a8b = bVar1;
              }
              else {
                iVar4 = (*(code *)&SUB_ram_400004a0)(uVar7,"file5-switch");
                if (iVar4 == 0) {
                  if (iVar3 == 0) {
                    DAT_ram_3fcb7d40 = DAT_ram_3fcb7d40 & 0xffffffef;
                  }
                  else {
                    DAT_ram_3fcb7d40 = DAT_ram_3fcb7d40 | 0x10;
                  }
                  DAT_ram_3fcc39e0 = 1;
                  DAT_ram_3fcc39dc = 0x32;
                  DAT_ram_3fcc3a8c = bVar1;
                }
                else {
                  uVar6 = FUN_ram_4038d3b4();
                  FUN_ram_4038d2a2(2,&DAT_ram_3c0c3290,"W (%lu) %s: Unknown checkbox ID: %s\n",uVar6
                                   ,&DAT_ram_3c0c3290,uVar7);
                }
              }
            }
          }
        }
        uVar7 = FUN_ram_4038d3b4();
        FUN_ram_4038d2a2(2,&DAT_ram_3c0c3290,"W (%lu) %s: PhotoDisplay_Set: %08X\n",uVar7,
                         &DAT_ram_3c0c3290,DAT_ram_3fcb7d40);
        FUN_ram_4201322a(iVar2);
        FUN_ram_4203b114(param_1,"Connection","close");
        FUN_ram_4203b192(param_1,&DAT_ram_3c0c328c,2);
        uVar7 = 0;
      }
    }
  }
  return uVar7;
}



// Audit label: uri_advancedset; entry: ram:4200e9ea; name: uri_advancedset

undefined4 uri_advancedset(undefined4 param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  char acStack_138 [4];
  char acStack_134 [4];
  char acStack_130 [4];
  char acStack_12c [2];
  char cStack_12a;
  undefined1 uStack_129;
  undefined4 uStack_128;
  undefined1 uStack_124;
  undefined1 auStack_120 [264];

  iVar1 = httpd_req_recv(param_1,auStack_120,0xff);
  if (iVar1 < 1) {
    FUN_ram_4203b382(param_1,8,0);
    uVar4 = 0xffffffff;
  }
  else {
    auStack_120[iVar1] = 0;
    iVar2 = (*(code *)&SUB_ram_400004ac)(auStack_120,"\"ntp\":\"");
    iVar1 = (*(code *)&SUB_ram_400004ac)(auStack_120,"\"openweathermapKey\":\"");
    if (iVar2 != 0) {
      iVar2 = iVar2 + 7;
      iVar3 = (*(code *)&SUB_ram_40000514)(iVar2,0x22);
      if ((iVar3 != 0) && (uVar5 = iVar3 - iVar2, uVar5 < 0x40)) {
        (*(code *)&SUB_ram_40000488)(&DAT_ram_3fcb7c22,0,0x41);
        (*(code *)&SUB_ram_4000049c)(&DAT_ram_3fcb7c22,iVar2,uVar5);
        (&DAT_ram_3fcb7c22)[uVar5] = 0;
        DAT_ram_3fcc39e0 = 1;
        DAT_ram_3fcc39dc = 0x32;
      }
    }
    if (iVar1 != 0) {
      iVar1 = iVar1 + 0x15;
      iVar2 = (*(code *)&SUB_ram_40000514)(iVar1,0x22);
      if ((iVar2 != 0) && (uVar5 = iVar2 - iVar1, uVar5 < 0x40)) {
        (*(code *)&SUB_ram_40000488)(&DAT_ram_3fcb7cb8,0,0x41);
        (*(code *)&SUB_ram_4000049c)(&DAT_ram_3fcb7cb8,iVar1,uVar5);
        (&DAT_ram_3fcb7cb8)[uVar5] = 0;
        DAT_ram_3fcc39e0 = 1;
        DAT_ram_3fcc39dc = 0x32;
      }
    }
    uStack_128 = 0;
    uStack_124 = 0;
    iVar1 = (*(code *)&SUB_ram_400004ac)(auStack_120,"\"clickCount\":");
    if (iVar1 != 0) {
      iVar1 = iVar1 + 0xd;
      iVar2 = (*(code *)&SUB_ram_40000514)(iVar1,0x7d);
      if ((iVar2 != 0) && ((uint)(iVar2 - iVar1) < 4)) {
        (*(code *)&SUB_ram_4000049c)(&uStack_128,iVar1);
        uVar5 = (*(code *)&SUB_ram_40000580)(&uStack_128);
        if (uVar5 < 0xb) {
          DAT_ram_3fcc3a90 = uVar5 & 0xff;
        }
      }
    }
    acStack_138[0] = s_Settings_saved_ram_3c0d6944[0];
    acStack_138[1] = s_Settings_saved_ram_3c0d6944[1];
    acStack_138[2] = s_Settings_saved_ram_3c0d6944[2];
    acStack_138[3] = s_Settings_saved_ram_3c0d6944[3];
    acStack_134[0] = s_Settings_saved_ram_3c0d6944[4];
    acStack_134[1] = s_Settings_saved_ram_3c0d6944[5];
    acStack_134[2] = s_Settings_saved_ram_3c0d6944[6];
    acStack_134[3] = s_Settings_saved_ram_3c0d6944[7];
    acStack_130[0] = s_Settings_saved_ram_3c0d6944[8];
    acStack_130[1] = s_Settings_saved_ram_3c0d6944[9];
    acStack_130[2] = s_Settings_saved_ram_3c0d6944[10];
    acStack_130[3] = s_Settings_saved_ram_3c0d6944[0xb];
    acStack_12c[0] = s_Settings_saved_ram_3c0d6944[0xc];
    acStack_12c[1] = s_Settings_saved_ram_3c0d6944[0xd];
    cStack_12a = s_Settings_saved_ram_3c0d6944[0xe];
    uStack_129 = 0;
    FUN_ram_4203b178(param_1,"text/plain");
    FUN_ram_4203b114(param_1,"Connection","close");
    uVar4 = (*(code *)&SUB_ram_400004a8)(acStack_138);
    FUN_ram_4203b192(param_1,acStack_138,uVar4);
    uVar4 = 0;
  }
  return uVar4;
}



// Audit label: uri_settings; entry: ram:4200ef62; name: uri_settings

undefined4 uri_settings(undefined4 param_1)

{
  undefined1 uVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 auStack_90 [128];

  iVar2 = httpd_req_recv(param_1,auStack_90,0x7f);
  if (iVar2 < 1) {
    uVar3 = 0xffffffff;
  }
  else {
    auStack_90[iVar2] = 0;
    uVar1 = FUN_ram_4200eefe(auStack_90,"tempUnit");
    *(undefined1 *)(gp + -1999) = uVar1;
    DAT_ram_3fcc3a96 = FUN_ram_4200eefe(auStack_90,"hourFormat");
    DAT_ram_3fcc3a95 = FUN_ram_4200eefe(auStack_90,"mileDisplay");
    iVar2 = FUN_ram_4200eefe(auStack_90,"timeSync");
    *(char *)(gp + -2000) = (char)iVar2;
    DAT_ram_3fcc39f5 = 1;
    DAT_ram_3fcb7d08 = (uint)(*(char *)(gp + -1999) != '\0');
    DAT_ram_3fcb7d0c = (uint)(DAT_ram_3fcc3a96 != '\0');
    DAT_ram_3fcb7d10 = (uint)(DAT_ram_3fcc3a95 != '\0');
    DAT_ram_3fcb7d14 = (uint)(iVar2 != 0);
    DAT_ram_3fcc39f2 = 1;
    DAT_ram_3fcc39e0 = 1;
    DAT_ram_3fcc39dc = 0x32;
    FUN_ram_4203b114(param_1,"Connection","close");
    FUN_ram_4203b192(param_1,&DAT_ram_3c0c328c,2);
    uVar3 = 0;
  }
  return uVar3;
}



// Audit label: uri_set_clock_color; entry: ram:4200f0c0; name: uri_set_clock_color

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 uri_set_clock_color(undefined4 param_1)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  uint auStack_5c [2];
  undefined2 uStack_54;
  undefined1 auStack_50 [64];

  iVar2 = httpd_req_recv(param_1,auStack_50,0x3f);
  if (iVar2 < 1) {
    FUN_ram_4203b382(param_1,8,0);
    uVar6 = 0xffffffff;
  }
  else {
    auStack_50[iVar2] = 0;
    auStack_5c[0] = 0;
    auStack_5c[1] = 0;
    uStack_54 = 0;
    iVar2 = (*(code *)&SUB_ram_400004ac)(auStack_50,"\"index\":");
    if (iVar2 == 0) {
      uVar3 = 0xffffffff;
    }
    else {
      uVar3 = (*(code *)&SUB_ram_40000580)(iVar2 + 8);
    }
    auStack_5c[0] = 0;
    auStack_5c[1] = 0;
    uStack_54 = 0;
    iVar2 = (*(code *)&SUB_ram_400004ac)(auStack_50,"\"color\":\"");
    if (iVar2 != 0) {
      iVar2 = iVar2 + 9;
      iVar4 = (*(code *)&SUB_ram_40000514)(iVar2,0x22);
      if ((iVar4 != 0) && ((uint)(iVar4 - iVar2) < 9)) {
        (*(code *)&SUB_ram_4000049c)(auStack_5c,iVar2);
      }
    }
    if (((uVar3 < 3) && (iVar2 = (*(code *)&SUB_ram_400004a8)(auStack_5c), iVar2 == 7)) &&
       ((auStack_5c[0] & 0xff) == 0x23)) {
      FUN_ram_42008b58(auStack_5c);
      uVar5 = FUN_ram_42008aae();
      uVar6 = uVar5;
      uVar1 = _DAT_ram_3fcb7d24;
      if (((uVar3 != 0) && (uVar6 = _DAT_ram_3fcb7d20, uVar1 = uVar5, uVar3 != 1)) &&
         (uVar1 = _DAT_ram_3fcb7d24, uVar3 == 2)) {
        _DAT_ram_3fcb7d28 = uVar5;
      }
      _DAT_ram_3fcb7d24 = uVar1;
      _DAT_ram_3fcb7d20 = uVar6;
      DAT_ram_3fcc39e0 = 1;
      DAT_ram_3fcc39dc = 0x32;
      DAT_ram_3fcc3a26 = 1;
      FUN_ram_4203b114(param_1,"Connection","close");
      FUN_ram_4203b192(param_1,&DAT_ram_3c0c328c,2);
      uVar6 = 0;
    }
    else {
      FUN_ram_4203b382(param_1,3,0);
      uVar6 = 0xffffffff;
    }
  }
  return uVar6;
}



// Audit label: uri_set_night_brightness; entry: ram:4200d5ac; name: uri_set_night_brightness

undefined4 uri_set_night_brightness(undefined4 param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_50 [72];

  iVar1 = httpd_req_recv(param_1,auStack_50,0x3f);
  if (iVar1 < 1) {
    FUN_ram_4203b382(param_1,8,0);
    uVar2 = 0xffffffff;
  }
  else {
    auStack_50[iVar1] = 0;
    iVar1 = (*(code *)&SUB_ram_400004ac)(auStack_50,"NightBrightness=");
    if (iVar1 != 0) {
      DAT_ram_3fcc3a98 = (*(code *)&SUB_ram_40000580)(iVar1 + 0x10);
      DAT_ram_3fcb7d38 = DAT_ram_3fcc3a98 * -10 + 1000;
      DAT_ram_3fcc39f2 = 1;
      DAT_ram_3fcc39e0 = 1;
      DAT_ram_3fcc39dc = 0x32;
    }
    FUN_ram_4203b114(param_1,"Connection","close");
    FUN_ram_4203b192(param_1,&DAT_ram_3c0c328c,2);
    uVar2 = 0;
  }
  return uVar2;
}



// Audit label: uri_wifireset; entry: ram:4200e84c; name: uri_wifireset

undefined4 uri_wifireset(undefined4 param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  undefined1 auStack_120 [268];

  iVar1 = httpd_req_recv(param_1,auStack_120,0xff);
  if (iVar1 < 1) {
    FUN_ram_4203b382(param_1,8,0);
    uVar4 = 0xffffffff;
  }
  else {
    auStack_120[iVar1] = 0;
    iVar2 = (*(code *)&SUB_ram_400004ac)(auStack_120,"\"ssid\":\"");
    iVar1 = (*(code *)&SUB_ram_400004ac)(auStack_120,"\"password\":\"");
    if (iVar2 != 0) {
      iVar2 = iVar2 + 8;
      iVar3 = (*(code *)&SUB_ram_40000514)(iVar2,0x22);
      if ((iVar3 != 0) && (uVar5 = iVar3 - iVar2, uVar5 < 0x40)) {
        (*(code *)&SUB_ram_4000049c)(&DAT_ram_3fcb7ba0,iVar2,uVar5);
        (&DAT_ram_3fcb7ba0)[uVar5] = 0;
      }
    }
    if (iVar1 != 0) {
      iVar1 = iVar1 + 0xc;
      iVar2 = (*(code *)&SUB_ram_40000514)(iVar1,0x22);
      if ((iVar2 != 0) && (uVar5 = iVar2 - iVar1, uVar5 < 0x40)) {
        (*(code *)&SUB_ram_4000049c)(&DAT_ram_3fcb7be1,iVar1,uVar5);
        (&DAT_ram_3fcb7be1)[uVar5] = 0;
      }
    }
    uVar4 = (*(code *)&SUB_ram_400004a8)(&DAT_ram_3fcbff2c);
    (*(code *)&SUB_ram_4000049c)(&DAT_ram_3fcb7ba0,&DAT_ram_3fcbff2c,uVar4);
    uVar4 = (*(code *)&SUB_ram_400004a8)(&DAT_ram_3fcbfeec);
    (*(code *)&SUB_ram_4000049c)(&DAT_ram_3fcb7be1,&DAT_ram_3fcbfeec,uVar4);
    DAT_ram_3fcb7cfc = 1;
    FUN_ram_42008a00();
    FUN_ram_4203b114(param_1,"Connection","close");
    FUN_ram_4203b192(param_1,&DAT_ram_3c0c328c,2);
    DAT_ram_3fcc39e4 = 10;
    DAT_ram_3fcc39e8 = 1;
    uVar4 = 0;
  }
  return uVar4;
}



// Audit label: uri_updateCity; entry: ram:4200f2c0; name: uri_updateCity

undefined4 uri_updateCity(undefined4 param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 uStack_124;
  undefined1 auStack_120 [260];

  uStack_124 = 0x8cbcef;
  iVar1 = httpd_req_recv(param_1,auStack_120,0xff);
  if (iVar1 < 1) {
    FUN_ram_4203b382(param_1,8,0);
    uVar5 = 0xffffffff;
  }
  else {
    auStack_120[iVar1] = 0;
    iVar2 = (*(code *)&SUB_ram_400004ac)(auStack_120,"\"city\":\"");
    iVar2 = iVar2 + 8;
    iVar3 = (*(code *)&SUB_ram_40000514)(iVar2,0x2c);
    iVar4 = (*(code *)&SUB_ram_400004ac)(iVar2,&uStack_124);
    iVar1 = iVar3;
    if (iVar4 != 0) {
      iVar1 = iVar4;
    }
    (*(code *)&SUB_ram_40000488)(&DAT_ram_3fcb7c77,0,0x41);
    (*(code *)&SUB_ram_4000049c)(&DAT_ram_3fcb7c77,iVar2,iVar1 - iVar2);
    if (iVar4 == 0) {
      iVar4 = iVar3 + 1;
    }
    else {
      iVar4 = iVar4 + 3;
    }
    iVar1 = (*(code *)&SUB_ram_400004ac)(iVar4,&DAT_ram_3c0c36f4);
    (*(code *)&SUB_ram_40000488)(&DAT_ram_3fcb7c63,0,0x14);
    (*(code *)&SUB_ram_4000049c)(&DAT_ram_3fcb7c63,iVar4,iVar1 - iVar4);
    DAT_ram_3fcc39e0 = 1;
    DAT_ram_3fcc39dc = 0x32;
    DAT_ram_3fcc39f3 = 1;
    DAT_ram_3fcc39d7 = 0;
    DAT_ram_3fcc39e9 = 0;
    DAT_ram_3fcc3ab9 = 0;
    DAT_ram_3fcc3ab8 = 0;
    FUN_ram_4203b114(param_1,"Connection","close");
    FUN_ram_4203b192(param_1,&DAT_ram_3c0c328c,2);
    uVar5 = 0;
  }
  return uVar5;
}



// Audit label: uri_configure; entry: ram:4200f57e; name: uri_configure

undefined4 uri_configure(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  undefined1 auStack_120 [268];

  if (*(uint *)(param_1 + 0x20c) < 0x41) {
    iVar1 = httpd_req_recv(param_1,auStack_120,0xff);
    if (iVar1 < 1) {
      FUN_ram_4203b382(param_1,8,0);
      uVar4 = 0xffffffff;
    }
    else {
      auStack_120[iVar1] = 0;
      iVar2 = (*(code *)&SUB_ram_400004ac)(auStack_120,"\"ssid\":\"");
      iVar1 = (*(code *)&SUB_ram_400004ac)(auStack_120,"\"password\":\"");
      (*(code *)&SUB_ram_40000488)(&DAT_ram_3fcbff2c,0,0x40);
      if (iVar2 != 0) {
        iVar2 = iVar2 + 8;
        iVar3 = (*(code *)&SUB_ram_40000514)(iVar2,0x22);
        if ((iVar3 != 0) && (uVar5 = iVar3 - iVar2, uVar5 < 0x3f)) {
          (*(code *)&SUB_ram_4000049c)(&DAT_ram_3fcbff2c,iVar2,uVar5);
          (&DAT_ram_3fcbff2c)[uVar5] = 0;
        }
      }
      (*(code *)&SUB_ram_40000488)(&DAT_ram_3fcbfeec,0,0x40);
      if (iVar1 != 0) {
        iVar1 = iVar1 + 0xc;
        iVar2 = (*(code *)&SUB_ram_40000514)(iVar1,0x22);
        if ((iVar2 != 0) && (uVar5 = iVar2 - iVar1, uVar5 < 0x3f)) {
          (*(code *)&SUB_ram_4000049c)(&DAT_ram_3fcbfeec,iVar1,uVar5);
          (&DAT_ram_3fcbfeec)[uVar5] = 0;
        }
      }
      (*(code *)&SUB_ram_40000488)(&DAT_ram_3fcb7ba0,0,0x41);
      (*(code *)&SUB_ram_40000498)(&DAT_ram_3fcb7ba0,&DAT_ram_3fcbff2c);
      (*(code *)&SUB_ram_40000488)(&DAT_ram_3fcb7be1,0,0x41);
      (*(code *)&SUB_ram_40000498)(&DAT_ram_3fcb7be1,&DAT_ram_3fcbfeec);
      DAT_ram_3fcb7cfc = 1;
      FUN_ram_42008a00();
      FUN_ram_4203b114(param_1,"Connection","close");
      FUN_ram_4203b192(param_1,&DAT_ram_3c0c328c,2);
      DAT_ram_3fcc39e4 = 10;
      DAT_ram_3fcc39e8 = 1;
      uVar4 = 0;
    }
  }
  else {
    FUN_ram_4203b382(param_1,9,0);
    uVar4 = 0xffffffff;
  }
  return uVar4;
}



// Audit label: uri_set_display_time; entry: ram:4200f7aa; name: uri_set_display_time

undefined4 uri_set_display_time(undefined4 param_1)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uStack_64;
  undefined4 uStack_60;
  undefined4 uStack_5c;
  undefined4 uStack_58;
  undefined4 uStack_54;
  undefined1 auStack_50 [68];

  iVar1 = httpd_req_recv(param_1,auStack_50,0x3f);
  if (iVar1 < 1) {
    FUN_ram_4203b382(param_1,8,0);
    uVar3 = 0xffffffff;
  }
  else {
    auStack_50[iVar1] = 0;
    uStack_64 = 0;
    uStack_60 = 0;
    uStack_5c = 0;
    uStack_58 = 0;
    uStack_54 = 0;
    iVar1 = (*(code *)&SUB_ram_400004ac)(auStack_50,"\"display_time\":");
    if (iVar1 != 0) {
      iVar1 = iVar1 + 0xf;
      iVar2 = (*(code *)&SUB_ram_40000514)(iVar1,0x7d);
      if ((iVar2 != 0) && ((uint)(iVar2 - iVar1) < 0x13)) {
        (*(code *)&SUB_ram_4000049c)(&uStack_64,iVar1);
      }
    }
    FUN_ram_4200f764(&uStack_64);
    FUN_ram_4203b114(param_1,"Connection","close");
    FUN_ram_4203b192(param_1,&DAT_ram_3c0c328c,2);
    uVar3 = 0;
  }
  return uVar3;
}



// Audit label: uri_SetNightStartTime; entry: ram:4200f8a8; name: uri_SetNightStartTime

undefined4 uri_SetNightStartTime(int param_1)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined1 auStack_24 [24];

  if (*(uint *)(param_1 + 0x20c) < 0x41) {
    iVar1 = httpd_req_recv(param_1,auStack_24,0x14);
    if (iVar1 < 1) {
      FUN_ram_4203b382(param_1,8,0);
      uVar3 = 0xffffffff;
    }
    else {
      auStack_24[iVar1] = 0;
      uStack_38 = 0;
      uStack_34 = 0;
      uStack_30 = 0;
      uStack_2c = 0;
      uStack_28 = 0;
      iVar1 = (*(code *)&SUB_ram_400004ac)(auStack_24,"\"StartTime\":\"");
      if (iVar1 != 0) {
        iVar1 = iVar1 + 0xd;
        iVar2 = (*(code *)&SUB_ram_40000514)(iVar1,0x22);
        if ((iVar2 != 0) && ((uint)(iVar2 - iVar1) < 0x13)) {
          (*(code *)&SUB_ram_4000049c)(&uStack_38,iVar1);
        }
      }
      FUN_ram_4200f85c(&uStack_38);
      FUN_ram_4203b114(param_1,"Connection","close");
      FUN_ram_4203b192(param_1,&DAT_ram_3c0c328c,2);
      uVar3 = 0;
    }
  }
  else {
    FUN_ram_4203b382(param_1,9,0);
    uVar3 = 0xffffffff;
  }
  return uVar3;
}



// Audit label: uri_SetNightStopTime; entry: ram:4200f9be; name: uri_SetNightStopTime

undefined4 uri_SetNightStopTime(int param_1)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined1 auStack_24 [24];

  if (*(uint *)(param_1 + 0x20c) < 0x41) {
    iVar1 = httpd_req_recv(param_1,auStack_24,0x14);
    if (iVar1 < 1) {
      FUN_ram_4203b382(param_1,8,0);
      uVar3 = 0xffffffff;
    }
    else {
      auStack_24[iVar1] = 0;
      uStack_38 = 0;
      uStack_34 = 0;
      uStack_30 = 0;
      uStack_2c = 0;
      uStack_28 = 0;
      iVar1 = (*(code *)&SUB_ram_400004ac)(auStack_24,"\"StopTime\":\"");
      if (iVar1 != 0) {
        iVar1 = iVar1 + 0xc;
        iVar2 = (*(code *)&SUB_ram_40000514)(iVar1,0x22);
        if ((iVar2 != 0) && ((uint)(iVar2 - iVar1) < 0x13)) {
          (*(code *)&SUB_ram_4000049c)(&uStack_38,iVar1);
        }
      }
      FUN_ram_4200f972(&uStack_38);
      FUN_ram_4203b114(param_1,"Connection","close");
      FUN_ram_4203b192(param_1,&DAT_ram_3c0c328c,2);
      uVar3 = 0;
    }
  }
  else {
    FUN_ram_4203b382(param_1,9,0);
    uVar3 = 0xffffffff;
  }
  return uVar3;
}



// Audit label: http_404_captive_redirect; entry: ram:4200d4be; name: http_404_captive_redirect

undefined4 http_404_captive_redirect(undefined4 param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_50;
  undefined4 uStack_4c;
  undefined4 uStack_48;
  undefined1 uStack_44;

  iVar1 = httpd_req_get_hdr_value_str(param_1,&DAT_ram_3c0c3204,&local_50,0x40);
  if (iVar1 != 0) {
    local_50 = DAT_ram_3c0c2ae8;
    uStack_4c = DAT_ram_3c0c2aec;
    uStack_48 = DAT_ram_3c0c2af0;
    uStack_44 = DAT_ram_3c0c2af4;
  }
  iVar1 = (*(code *)&SUB_ram_400004ac)(&local_50,&DAT_ram_3c0c2ae8);
  if (iVar1 == 0) {
    FUN_ram_4203b15e(param_1,"302 Found");
    FUN_ram_4203b114(param_1,"Location","http://192.168.43.1/");
    FUN_ram_4203b192(param_1,0,0);
    uVar2 = 0;
  }
  else {
    uVar2 = uri_root(param_1);
  }
  return uVar2;
}



// Audit label: httpd_start_reference; entry: ram:4200fa88; name: FUN_ram_4200fa88

undefined4 FUN_ram_4200fa88(void)

{
  undefined *puVar1;
  int iVar2;
  undefined *puVar3;
  undefined *puVar4;
  undefined4 *puVar5;
  undefined **ppuVar6;
  undefined4 uStack_74;
  undefined4 local_70 [7];
  undefined2 uStack_52;

  ppuVar6 = (undefined **)&DAT_ram_3c0d6954;
  puVar5 = local_70;
  do {
    puVar1 = ppuVar6[1];
    puVar3 = ppuVar6[2];
    puVar4 = ppuVar6[3];
    *puVar5 = *ppuVar6;
    puVar5[1] = puVar1;
    puVar5[2] = puVar3;
    puVar5[3] = puVar4;
    ppuVar6 = ppuVar6 + 4;
    puVar5 = puVar5 + 4;
  } while (ppuVar6 != &PTR_s_China_ram_3c0c3c60_ram_3c0d69b4);
  uStack_52 = 0x40;
  uStack_74 = 0;
  FUN_ram_420b10ce();
  iVar2 = httpd_start(&uStack_74,local_70);
  if (iVar2 == 0) {
    httpd_register_uri_handler(uStack_74,&PTR_DAT_ram_3c0c28b8_ram_3c0d692c);
    httpd_register_uri_handler(uStack_74,&PTR_s__configure_ram_3c0c3968_ram_3c0d6914);
    httpd_register_uri_handler(uStack_74,&PTR_s__scan_ram_3c0c3960_ram_3c0d68fc);
    httpd_register_uri_handler(uStack_74,&PTR_s__setgifvalue_ram_3c0c3950_ram_3c0d68e4);
    httpd_register_uri_handler(uStack_74,&PTR_s__getgifvalue_ram_3c0c3940_ram_3c0d68cc);
    httpd_register_uri_handler(uStack_74,&PTR_s__setclocktype_ram_3c0c3930_ram_3c0d68b4);
    httpd_register_uri_handler(uStack_74,&PTR_s__getclocktype_ram_3c0c3920_ram_3c0d689c);
    httpd_register_uri_handler(uStack_74,&PTR_s__settings_ram_3c0c3914_ram_3c0d6884);
    httpd_register_uri_handler(uStack_74,&PTR_s__getsettings_ram_3c0c3904_ram_3c0d686c);
    httpd_register_uri_handler(uStack_74,&PTR_s__SetTimeModeValue_ram_3c0c38f0_ram_3c0d6854);
    httpd_register_uri_handler(uStack_74,&PTR_s__GetTimeModeValue_ram_3c0c38dc_ram_3c0d683c);
    httpd_register_uri_handler(uStack_74,&PTR_s__updateCity_ram_3c0c38d0_ram_3c0d6824);
    httpd_register_uri_handler(uStack_74,&PTR_s__get_led_brightness_ram_3c0c38bc_ram_3c0d680c);
    httpd_register_uri_handler(uStack_74,&PTR_s__set_led_brightness_ram_3c0c38a8_ram_3c0d67f4);
    httpd_register_uri_handler(uStack_74,&PTR_s__get_clock_colors_ram_3c0c3894_ram_3c0d67dc);
    httpd_register_uri_handler(uStack_74,&PTR_s__set_clock_color_ram_3c0c3880_ram_3c0d67c4);
    httpd_register_uri_handler(uStack_74,&PTR_s__get_night_brightness_ram_3c0c3868_ram_3c0d67ac);
    httpd_register_uri_handler(uStack_74,&PTR_s__set_night_brightness_ram_3c0c3850_ram_3c0d6794);
    httpd_register_uri_handler(uStack_74,&PTR_s__GetNightStartTime_ram_3c0c3828_ram_3c0d6764);
    httpd_register_uri_handler(uStack_74,&PTR_s__SetNightStartTime_ram_3c0c383c_ram_3c0d677c);
    httpd_register_uri_handler(uStack_74,&PTR_s__GetNightStopTime_ram_3c0c3800_ram_3c0d6734);
    httpd_register_uri_handler(uStack_74,&PTR_s__SetNightStopTime_ram_3c0c3814_ram_3c0d674c);
    httpd_register_uri_handler(uStack_74,&PTR_s__restart_ram_3c0c37f4_ram_3c0d671c);
    httpd_register_uri_handler(uStack_74,&PTR_s__advancedset_ram_3c0c37e4_ram_3c0d6704);
    httpd_register_uri_handler(uStack_74,&PTR_s__wifireset_ram_3c0c37d8_ram_3c0d66ec);
    httpd_register_uri_handler(uStack_74,&PTR_s__photo_ram_3c0c37d0_ram_3c0d66d4);
    httpd_register_uri_handler(uStack_74,&PTR_s__get_display_time_ram_3c0c37bc_ram_3c0d66bc);
    httpd_register_uri_handler(uStack_74,&PTR_s__set_display_time_ram_3c0c37a8_ram_3c0d66a4);
    httpd_register_uri_handler(uStack_74,&PTR_s__get_checkbox_state_ram_3c0c3794_ram_3c0d668c);
    httpd_register_uri_handler(uStack_74,&PTR_s__set_checkbox_state_ram_3c0c3780_ram_3c0d6674);
    httpd_register_uri_handler(uStack_74,&PTR_s__get_Photo_File_ram_3c0c3770_ram_3c0d665c);
    httpd_register_uri_handler(uStack_74,gp + -0x4f0);
    httpd_register_uri_handler(uStack_74,gp + -0x508);
    httpd_register_uri_handler(uStack_74,gp + -0x520);
    FUN_ram_4203b640(uStack_74,6,http_404_captive_redirect);
  }
  else {
    uStack_74 = 0;
  }
  return uStack_74;
}



// Audit label: esp_http_client_perform_reference; entry: ram:42010864; name: FUN_ram_42010864

void FUN_ram_42010864(void)

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
  pcVar5 = &DAT_ram_3fcb7c77;
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
  pcVar5 = &DAT_ram_3fcb7c63;
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
             local_130,local_13c,&DAT_ram_3fcb7cb8);
  (*(code *)&SUB_ram_40000488)(apcStack_1d4,0,0x98);
  uStack_188 = 10000;
  pcStack_178 = FUN_ram_4200fccc;
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



// Audit label: read_animation_frame_table; entry: ram:4200b5cc; name: read_animation_frame_table

void read_animation_frame_table(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;

  (*(code *)&SUB_ram_40000488)(&DAT_ram_3fcba5a8,0,0x400);
  if (DAT_ram_3fcb7d00 == 3) {
    iVar2 = 0x313000;
  }
  else if (DAT_ram_3fcb7d00 < 4) {
    if (DAT_ram_3fcb7d00 == 1) {
      iVar2 = 0x2af000;
    }
    else if (DAT_ram_3fcb7d00 == 2) {
      iVar2 = 0x2e1000;
    }
    else {
      iVar2 = 0x27d000;
    }
  }
  else if (DAT_ram_3fcb7d00 == 4) {
    iVar2 = 0x345000;
  }
  else {
    iVar2 = 0x27d000;
  }
  esp_flash_read(0,&DAT_ram_3fcba5a8,iVar2,0x400);
  if (((DAT_ram_3fcba5a8 == 'G') && (DAT_ram_3fcba5a9 == 'I')) && (DAT_ram_3fcba5aa == 'F')) {
    do {
      uVar3 = (uint)DAT_ram_3fcc3a24;
      iVar1 = *(int *)(&DAT_ram_3fcba5b7 + uVar3 * 8);
      DAT_ram_3fcc3a24 = DAT_ram_3fcc3a24 + 1;
      if (*(int *)(&DAT_ram_3fcba5b3 + uVar3 * 8) == 0 && iVar1 == 0) {
        DAT_ram_3fcc3a24 = 0;
      }
      if (0x7e < DAT_ram_3fcc3a24) {
        DAT_ram_3fcc3a24 = 0;
      }
    } while (*(int *)(&DAT_ram_3fcba5b3 + uVar3 * 8) == 0 && iVar1 == 0);
    FUN_ram_4200c518(0xa0,0xa0,iVar1 + iVar2);
  }
  return;
}



// Audit label: esp_flash_read_reference; entry: ram:42010eca; name: FUN_ram_42010eca

void FUN_ram_42010eca(uint param_1,int param_2,int param_3)

{
  int iVar1;
  int iVar2;
  void *arg4;
  uint uVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  undefined1 auStack_68 [4];
  uint uStack_64;
  uint uStack_60;
  short sStack_5a;
  short asStack_40 [5];
  int iStack_36;

  esp_flash_read(0,asStack_40,param_3,0xe);
  esp_flash_read(0,auStack_68,param_3 + 0xe,0x28);
  if ((asStack_40[0] == 0x4d42) && (sStack_5a == 0x18)) {
    uVar7 = (uStack_60 ^ (int)uStack_60 >> 0x1f) - ((int)uStack_60 >> 0x1f);
    uVar6 = (uStack_64 + 1) * 3 & 0xfffffffc;
    iVar2 = FUN_ram_4038e4be(uVar6);
    arg4 = (void *)FUN_ram_4038e4be(uStack_64 << 1);
    for (uVar5 = 0; uVar5 < uVar7; uVar5 = uVar5 + 1) {
      uVar3 = uVar5;
      if (0 < (int)uStack_60) {
        uVar3 = (uVar7 - uVar5) - 1;
      }
      esp_flash_read(0,iVar2,uVar3 * uVar6 + iStack_36 + param_3,uVar6);
      for (uVar3 = 0; uVar3 < uStack_64; uVar3 = uVar3 + 1) {
        iVar1 = uVar3 * 3;
        iVar4 = (*(byte *)(iVar1 + 1 + iVar2) & 0xfc) << 3;
        *(ushort *)(uVar3 * 2 + (int)arg4) =
             (ushort)(*(byte *)(iVar1 + 2 + iVar2) & 0xf8) | (ushort)((uint)iVar4 >> 8) |
             ((ushort)iVar4 | (ushort)(*(byte *)(iVar2 + iVar1) >> 3)) << 8;
      }
      uVar3 = param_2 + uVar5 & 0xffff;
      st7789_blit_rect(param_1,uVar3,(param_1 + uStack_64 & 0xffff) - 1 & 0xffff,uVar3,arg4);
    }
    FUN_ram_4038e4da(iVar2);
    FUN_ram_4038e4da(arg4);
  }
  return;
}



// Audit label: jpeg_flash_read_callback; entry: ram:4200c33e; name: jpeg_flash_read_callback

int jpeg_flash_read_callback(int param_1,int param_2,int param_3)

{
  int *piVar1;

  piVar1 = *(int **)(param_1 + 0x74);
  if (param_2 == 0) {
    *piVar1 = *piVar1 + param_3;
  }
  else {
    esp_flash_read(0,param_2,*piVar1,param_3);
    *piVar1 = *piVar1 + param_3;
  }
  return param_3;
}



// Audit label: esp_flash_read_reference; entry: ram:42008552; name: FUN_ram_42008552

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_ram_42008552(void)

{
  esp_flash_read(0,&DAT_ram_3fcb7b9c,0x3e7000,0x1bc);
  if (0x1e < DAT_ram_3fcb7b9c) {
    DAT_ram_3fcb7b9c = 0x1f;
  }
  if ((DAT_ram_3fcb7c22 == '\0') || (DAT_ram_3fcb7c22 == -1)) {
    (*(code *)&SUB_ram_40000488)(&DAT_ram_3fcb7c22,0,0x41);
    DAT_ram_3fcb7c22 = s_pool_ntp_org_ram_3c0c29ec[0];
    DAT_ram_3fcb7c22_1 = s_pool_ntp_org_ram_3c0c29ec[1];
    DAT_ram_3fcb7c24._0_1_ = s_pool_ntp_org_ram_3c0c29ec[2];
    DAT_ram_3fcb7c24._1_1_ = s_pool_ntp_org_ram_3c0c29ec[3];
    DAT_ram_3fcb7c26._0_1_ = s_pool_ntp_org_ram_3c0c29ec[4];
    DAT_ram_3fcb7c26._1_1_ = s_pool_ntp_org_ram_3c0c29ec[5];
    DAT_ram_3fcb7c28._0_1_ = s_pool_ntp_org_ram_3c0c29ec[6];
    DAT_ram_3fcb7c28._1_1_ = s_pool_ntp_org_ram_3c0c29ec[7];
    DAT_ram_3fcb7c2a._0_1_ = s_pool_ntp_org_ram_3c0c29ec[8];
    DAT_ram_3fcb7c2a._1_1_ = s_pool_ntp_org_ram_3c0c29ec[9];
    DAT_ram_3fcb7c2c._0_1_ = s_pool_ntp_org_ram_3c0c29ec[10];
    DAT_ram_3fcb7c2c._1_1_ = s_pool_ntp_org_ram_3c0c29ec[0xb];
    DAT_ram_3fcb7c2e = s_pool_ntp_org_ram_3c0c29ec[0xc];
  }
  if ((DAT_ram_3fcb7c77 == '\0') || (DAT_ram_3fcb7c77 == -1)) {
    (*(code *)&SUB_ram_40000488)(&DAT_ram_3fcb7c77,0,0x41);
    DAT_ram_3fcb7c77 = s_Shenzhen_ram_3c0c29fc[0];
    DAT_ram_3fcb7c78 = s_Shenzhen_ram_3c0c29fc[1];
    DAT_ram_3fcb7c79 = s_Shenzhen_ram_3c0c29fc[2];
    DAT_ram_3fcb7c7a = s_Shenzhen_ram_3c0c29fc[3];
    DAT_ram_3fcb7c7b = s_Shenzhen_ram_3c0c29fc[4];
    DAT_ram_3fcb7c7c = s_Shenzhen_ram_3c0c29fc[5];
    DAT_ram_3fcb7c7d = s_Shenzhen_ram_3c0c29fc[6];
    DAT_ram_3fcb7c7e = s_Shenzhen_ram_3c0c29fc[7];
    DAT_ram_3fcb7c7f = s_Shenzhen_ram_3c0c29fc[8];
  }
  if ((DAT_ram_3fcb7c63 == '\0') || (DAT_ram_3fcb7c63 == -1)) {
    (*(code *)&SUB_ram_40000488)(&DAT_ram_3fcb7c63,0,0x14);
    DAT_ram_3fcb7c63 = 'C';
    DAT_ram_3fcb7c64 = 0x4e;
    DAT_ram_3fcb7c65 = 0;
  }
  if (((_DAT_ram_3fcb7cb8 & 0xff) == 0) || ((_DAT_ram_3fcb7cb8 & 0xff) == 0xff)) {
    (*(code *)&SUB_ram_40000488)(&DAT_ram_3fcb7cb8,0,0x41);
    _DAT_ram_3fcb7cb8 = DAT_ram_3c0c2a08;
    DAT_ram_3fcb7cbc = DAT_ram_3c0c2a0c;
    DAT_ram_3fcb7cc0 = DAT_ram_3c0c2a10;
    DAT_ram_3fcb7cc4 = DAT_ram_3c0c2a14;
    DAT_ram_3fcb7cc8 = DAT_ram_3c0c2a18;
    DAT_ram_3fcb7ccc = DAT_ram_3c0c2a1c;
    DAT_ram_3fcb7cd0 = DAT_ram_3c0c2a20;
    DAT_ram_3fcb7cd4 = DAT_ram_3c0c2a24;
    DAT_ram_3fcb7cd8 = DAT_ram_3c0c2a28;
  }
  if (4 < DAT_ram_3fcb7d00) {
    DAT_ram_3fcb7d00 = 0;
  }
  if (3 < DAT_ram_3fcb7d04) {
    DAT_ram_3fcb7d04 = 0;
  }
  if (1 < DAT_ram_3fcb7d08) {
    DAT_ram_3fcb7d08 = 0;
  }
  if (1 < DAT_ram_3fcb7d0c) {
    DAT_ram_3fcb7d0c = 0;
  }
  if (1 < DAT_ram_3fcb7d10) {
    DAT_ram_3fcb7d10 = 0;
  }
  if (1 < DAT_ram_3fcb7d14) {
    DAT_ram_3fcb7d14 = 0;
  }
  if (1 < DAT_ram_3fcb7d18) {
    DAT_ram_3fcb7d18 = 2;
  }
  if (1000 < DAT_ram_3fcb7d1c) {
    DAT_ram_3fcb7d1c = 0;
  }
  if (0xffff < _DAT_ram_3fcb7d20) {
    _DAT_ram_3fcb7d20 = 0xf800;
  }
  if (0xffff < _DAT_ram_3fcb7d24) {
    _DAT_ram_3fcb7d24 = 0xffe0;
  }
  if (0xffff < _DAT_ram_3fcb7d28) {
    _DAT_ram_3fcb7d28 = 0xffff;
  }
  if (1 < DAT_ram_3fcb7d2c) {
    DAT_ram_3fcb7d2c = 0;
  }
  if (5 < DAT_ram_3fcb7d30 - 0x12U) {
    DAT_ram_3fcb7d30 = 0x16;
  }
  if (7 < DAT_ram_3fcb7d34 - 5U) {
    DAT_ram_3fcb7d34 = 9;
  }
  if (1000 < DAT_ram_3fcb7d38) {
    DAT_ram_3fcb7d38 = 500;
  }
  if (0x3c < DAT_ram_3fcb7d3c) {
    DAT_ram_3fcb7d3c = 5;
  }
  if (0x1f < DAT_ram_3fcb7d40) {
    DAT_ram_3fcb7d40 = 0x1f;
  }
  if (0x19000 < DAT_ram_3fcb7d44) {
    DAT_ram_3fcb7d44 = 0x10fcf;
  }
  if (0x19000 < DAT_ram_3fcb7d48) {
    DAT_ram_3fcb7d48 = 0x188af;
  }
  if (0x19000 < DAT_ram_3fcb7d4c) {
    DAT_ram_3fcb7d4c = 0x156ce;
  }
  if (0x19000 < DAT_ram_3fcb7d50) {
    DAT_ram_3fcb7d50 = 0x10399;
  }
  if (0x19000 < DAT_ram_3fcb7d54) {
    DAT_ram_3fcb7d54 = 0x14ecd;
  }
  return;
}



// Audit label: uri_get_Photo_File; entry: ram:4200e11c; name: uri_get_Photo_File

undefined4 uri_get_Photo_File(undefined4 param_1)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  uint uVar7;
  uint uVar8;
  undefined8 uVar9;
  undefined1 auStack_80 [16];
  undefined1 auStack_70 [16];
  undefined1 auStack_60 [16];
  undefined1 auStack_50 [64];

  iVar2 = FUN_ram_4203a4a8(param_1,auStack_50,0x40);
  if (iVar2 == 0) {
    iVar2 = FUN_ram_4203a3b6(auStack_50,&DAT_ram_3c0c3414,auStack_80,0x10);
    if (iVar2 == 0) {
      uVar1 = (*(code *)&SUB_ram_40000580)(auStack_80);
    }
    else {
      uVar1 = 0;
    }
    iVar2 = FUN_ram_4203a3b6(auStack_50,"chunk",auStack_70);
    if (iVar2 == 0) {
      iVar2 = (*(code *)&SUB_ram_40000580)(auStack_70);
    }
    else {
      iVar2 = 0;
    }
    iVar3 = FUN_ram_4203a3b6(auStack_50,"size",auStack_60,0x10);
    if (iVar3 == 0) {
      iVar3 = (*(code *)&SUB_ram_40000580)(auStack_60);
    }
    else {
      iVar3 = 0;
    }
    if (5 < uVar1) {
      FUN_ram_4203b382(param_1,6,"Image not found");
      return 0xffffffff;
    }
  }
  else {
    uVar1 = 0;
    iVar2 = 0;
    iVar3 = 0;
  }
  if (iVar3 == 0 && iVar2 == 0) {
    uVar4 = FUN_ram_42013948();
    FUN_ram_42013814(uVar4,"exists",1);
    uVar9 = (*(code *)&SUB_ram_40000a64)(*(undefined4 *)(&DAT_ram_3fcb7ba4 + (uVar1 + 0x67) * 4));
    FUN_ram_42013906(uVar4,"size",(int)uVar9,(int)((ulonglong)uVar9 >> 0x20));
    uVar5 = FUN_ram_420137b6(uVar4);
    FUN_ram_4203b178(param_1,"application/json");
    FUN_ram_4203b114(param_1,"Connection","close");
    uVar6 = (*(code *)&SUB_ram_400004a8)(uVar5);
    FUN_ram_4203b192(param_1,uVar5,uVar6);
    FUN_ram_4201322a(uVar4);
    uVar4 = 0;
  }
  else {
    uVar8 = iVar3 * iVar2;
    uVar7 = *(uint *)(&DAT_ram_3fcb7ba4 + (uVar1 + 0x67) * 4);
    if (uVar8 < uVar7) {
      if (iVar3 + uVar8 <= uVar7) {
        uVar7 = iVar3 + uVar8;
      }
      esp_flash_read(0,&DAT_ram_3fcbd2ec,uVar1 * 0x19000 + 0x1e7000 + uVar8,uVar7 - uVar8);
      FUN_ram_4203b178(param_1,"application/octet-stream");
      FUN_ram_4203b114(param_1,"Connection","close");
      FUN_ram_4203b192(param_1,&DAT_ram_3fcbd2ec,uVar7 - uVar8);
      uVar4 = 0;
    }
    else {
      FUN_ram_4203b382(param_1,3,"Invalid chunk index");
      uVar4 = 0xffffffff;
    }
  }
  return uVar4;
}



// Audit label: configured_ssid_reference; entry: ram:4200ca30; name: FUN_ram_4200ca30

void FUN_ram_4200ca30(void)

{
  undefined *puVar1;
  undefined *puVar2;
  int iVar3;
  uint uVar4;
  undefined4 uVar5;
  undefined4 uStack_168;
  undefined4 uStack_164;
  undefined4 uStack_160;
  undefined4 uStack_15c;
  undefined4 uStack_158;
  undefined4 uStack_154;
  undefined4 uStack_150;
  undefined4 uStack_14c;
  char acStack_148 [88];
  undefined4 uStack_f0;
  undefined1 auStack_b0 [4];
  undefined1 auStack_ac [4];
  int iStack_a8;
  undefined4 uStack_a4;
  undefined4 uStack_a0;
  undefined *puStack_9c;
  undefined *puStack_98;
  undefined *puStack_94;
  undefined *puStack_90;
  undefined *puStack_8c;
  undefined *puStack_88;
  undefined *puStack_84;
  undefined *puStack_80;
  undefined *puStack_7c;
  undefined4 uStack_78;
  undefined4 uStack_74;
  undefined4 uStack_70;
  undefined4 uStack_6c;
  undefined4 uStack_68;
  undefined4 uStack_64;
  undefined4 uStack_60;
  undefined4 uStack_5c;
  undefined4 uStack_58;
  undefined4 uStack_54;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined4 uStack_48;
  undefined4 uStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined1 uStack_28;
  undefined4 uStack_24;
  undefined4 uStack_20;
  undefined1 uStack_1c;
  undefined4 uStack_18;

  DAT_ram_3fcc3a7c = FUN_ram_40388bfe();
  DAT_ram_3fcc3a74 = 0;
  iVar3 = FUN_ram_42036604();
  if (iVar3 != 0) {
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(iVar3,"./main/wifi_connect.c",0xa5,"wifi_init_sta","esp_netif_init()");
  }
  iVar3 = FUN_ram_420aeb30();
  if (iVar3 != 0) {
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(iVar3,"./main/wifi_connect.c",0xa7,"wifi_init_sta",
                     "esp_event_loop_create_default()");
  }
  FUN_ram_42045a7a();
  iStack_a8 = gp + -0x424;
  uStack_a4 = DAT_ram_3c0f1e8c;
  uStack_a0 = DAT_ram_3c0f1e90;
  puStack_9c = PTR_FUN_ram_420437c2_ram_3c0f1e94;
  puStack_98 = PTR_FUN_ram_42043a72_ram_3c0f1e98;
  puStack_94 = PTR_FUN_ram_420438d0_ram_3c0f1e9c;
  puStack_90 = PTR_FUN_ram_42043960_ram_3c0f1ea0;
  puStack_8c = PTR_FUN_ram_42043ba4_ram_3c0f1ea4;
  puStack_88 = PTR_FUN_ram_420440de_ram_3c0f1ea8;
  puStack_84 = PTR_FUN_ram_420441a2_ram_3c0f1eac;
  puStack_80 = PTR_FUN_ram_420435da_ram_3c0f1eb0;
  puStack_7c = PTR_FUN_ram_420437aa_ram_3c0f1eb4;
  uStack_78 = 10;
  uStack_74 = 0x20;
  uStack_70 = 1;
  uStack_6c = 0;
  uStack_68 = 0x20;
  uStack_64 = 0;
  uStack_60 = 5;
  uStack_5c = 0;
  uStack_58 = 0;
  uStack_54 = 1;
  uStack_50 = 1;
  uStack_4c = 0;
  uStack_48 = 1;
  uStack_44 = 1;
  uStack_40 = 6;
  uStack_3c = 0;
  uStack_38 = 0x2f0;
  uStack_34 = 0x20;
  uStack_30 = 0xa1;
  uStack_2c = 0;
  uStack_28 = 1;
  uStack_24 = 2;
  uStack_20 = 1;
  uStack_1c = 0;
  uStack_18 = 0x1f2f3f4f;
  iVar3 = FUN_ram_4204544e(&iStack_a8);
  puVar2 = PTR_s_WIFI_EVENT_ram_3c0cf320_ram_3c0f1eb8;
  if (iVar3 != 0) {
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(iVar3,"./main/wifi_connect.c",0xab,"wifi_init_sta","esp_wifi_init(&cfg)");
  }
  iVar3 = FUN_ram_420aeab6(PTR_s_WIFI_EVENT_ram_3c0cf320_ram_3c0f1eb8,0xffffffff,FUN_ram_4200c602,0,
                           auStack_ac);
  puVar1 = PTR_s_IP_EVENT_ram_3c0cb788_ram_3c0f1848;
  if (iVar3 != 0) {
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(iVar3,"./main/wifi_connect.c",0xaf,"wifi_init_sta",
                     "esp_event_handler_instance_register(WIFI_EVENT, ESP_EVENT_ANY_ID, &event_handler, NULL, &instance_any_id)"
                    );
  }
  iVar3 = FUN_ram_420aeab6(PTR_s_IP_EVENT_ram_3c0cb788_ram_3c0f1848,0,FUN_ram_4200c602,0,auStack_b0)
  ;
  if (iVar3 != 0) {
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(iVar3,"./main/wifi_connect.c",0xb4,"wifi_init_sta",
                     "esp_event_handler_instance_register(IP_EVENT, IP_EVENT_STA_GOT_IP, &event_handler, NULL, &instance_got_ip)"
                    );
  }
  (*(code *)&SUB_ram_40000488)(&uStack_168,0,0xb8);
  uStack_168 = 0x6c616d53;
  uStack_164 = 0x56545f6c;
  uStack_160 = 0;
  uStack_15c = 0;
  uStack_158 = 0;
  uStack_154 = 0;
  uStack_150 = 0;
  uStack_14c = 0;
  (*(code *)&SUB_ram_40000498)(&uStack_168,&DAT_ram_3fcb7ba0);
  (*(code *)&SUB_ram_40000498)(acStack_148,&DAT_ram_3fcb7be1);
  if (acStack_148[0] != '\0') {
    uStack_f0 = 3;
  }
  iVar3 = FUN_ram_42068cb6(1);
  if (iVar3 != 0) {
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(iVar3,"./main/wifi_connect.c",0xd1,"wifi_init_sta",
                     "esp_wifi_set_mode(WIFI_MODE_STA)");
  }
  iVar3 = FUN_ram_420692da(0,&uStack_168);
  if (iVar3 != 0) {
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(iVar3,"./main/wifi_connect.c",0xd2,"wifi_init_sta",
                     "esp_wifi_set_config(ESP_IF_WIFI_STA, &wifi_config)");
  }
  iVar3 = FUN_ram_42068d06();
  if (iVar3 == 0) {
    FUN_ram_4200c9e0();
    FUN_ram_420b10ce();
    DAT_ram_3fcc3a74 = 1;
    uVar4 = FUN_ram_40388c4e(DAT_ram_3fcc3a7c,3,0,0,0xffffffff);
    if ((uVar4 & 1) == 0) {
      if ((uVar4 & 2) != 0) {
        DAT_ram_3fcc3a74 = 4;
        DAT_ram_3fcb7cfc = 2;
        FUN_ram_42008a00();
                    /* WARNING: Subroutine does not return */
        esp_restart();
      }
      uVar5 = FUN_ram_4038d3b4();
      FUN_ram_4038d2a2(1,"wifi station","E (%lu) %s: UNEXPECTED EVENT\n",uVar5,"wifi station");
    }
    else {
      DAT_ram_3fcc3a74 = 2;
      DAT_ram_3fcc39ea = 0;
      iVar3 = FUN_ram_420aeae0(puVar1,0,FUN_ram_4200c602);
      if (iVar3 != 0) {
                    /* WARNING: Subroutine does not return */
        FUN_ram_4038726a(iVar3,"./main/wifi_connect.c",0xeb,"wifi_init_sta",
                         "esp_event_handler_unregister(IP_EVENT, IP_EVENT_STA_GOT_IP, &event_handler)"
                        );
      }
      iVar3 = FUN_ram_420aeae0(puVar2,0xffffffff,FUN_ram_4200c602);
      if (iVar3 != 0) {
                    /* WARNING: Subroutine does not return */
        FUN_ram_4038726a(iVar3,"./main/wifi_connect.c",0xec,"wifi_init_sta",
                         "esp_event_handler_unregister(WIFI_EVENT, ESP_EVENT_ANY_ID, &event_handler)"
                        );
      }
      FUN_ram_40388f00(DAT_ram_3fcc3a7c);
    }
    return;
  }
                    /* WARNING: Subroutine does not return */
  FUN_ram_4038726a(iVar3,"./main/wifi_connect.c",0xd3,"wifi_init_sta","esp_wifi_start()");
}



// Audit label: jpeg_write_cursor_reference; entry: ram:4200c374; name: FUN_ram_4200c374

undefined4 FUN_ram_4200c374(int param_1,int param_2,ushort *param_3)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  void *arg4;
  uint uVar4;
  int iVar5;
  int iVar6;

  iVar6 = *(int *)(param_1 + 0x74);
  uVar1 = (uint)param_3[2];
  iVar5 = *(int *)(iVar6 + 8);
  iVar2 = *(int *)(iVar6 + 4) + ((uVar1 - DAT_ram_3fcc3a65) * iVar5 + (uint)*param_3) * 2;
  uVar4 = (((uint)param_3[1] - (uint)*param_3) + 1) * 0x20000 >> 0x10;
  for (; uVar3 = (uint)param_3[3], uVar1 <= uVar3; uVar1 = uVar1 + 1 & 0xffff) {
    (*(code *)&SUB_ram_4000048c)(iVar2,param_2,uVar4);
    param_2 = param_2 + uVar4;
    iVar2 = iVar2 + iVar5 * 2;
  }
  if (*(int *)(iVar6 + 8) - 1U <= (uint)param_3[1]) {
    arg4 = *(void **)(iVar6 + 4);
    uVar1 = (iVar2 + uVar4 + iVar5 * -2) - (int)arg4 & 0xffff;
    if ((0x13ff < ((uint)(*(int *)(iVar6 + 8) << 0x14) >> 0x10) + uVar1) ||
       ((uint)DAT_ram_3fcc3a66 <= uVar3 + 1)) {
      if (DAT_ram_3fcc3a6c == '\0') {
        st7789_blit_rect((uint)DAT_ram_3fcc3a5a,
                         (uint)DAT_ram_3fcc3a58 + (uint)DAT_ram_3fcc3a65 & 0xffff,
                         (uint)param_3[1] + (uint)DAT_ram_3fcc3a5a & 0xffff,
                         uVar3 + DAT_ram_3fcc3a58 & 0xffff,arg4);
      }
      else {
        esp_flash_write(0,arg4,DAT_ram_3fcc3a5c,uVar1);
        DAT_ram_3fcc3a5c = DAT_ram_3fcc3a5c + uVar1;
      }
      DAT_ram_3fcc3a65 = (char)param_3[3] + 1;
    }
  }
  return 1;
}



// Audit label: pool_ntp_org_reference; entry: ram:42010a06; name: FUN_ram_42010a06

void FUN_ram_42010a06(void)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;

  iVar1 = FUN_ram_42017f44();
  if (iVar1 != 0) {
    FUN_ram_42017f0a();
  }
  DAT_ram_3fcbffa8 = 0;
  DAT_ram_3fcbffac = 0;
  DAT_ram_3fcbffb0 = 0;
  DAT_ram_3fcbffb4 = 0;
  DAT_ram_3fcbffb8 = 0;
  DAT_ram_3fcbffbc = 0;
  DAT_ram_3fcbffc0 = 0;
  DAT_ram_3fcbffc4 = 0;
  iVar1 = 0;
  do {
    if ((&PTR_DAT_ram_3c0c3c68_ram_3c0d69b8)[iVar1 * 3] == (undefined *)0x0) {
LAB_ram_42010a9a:
      DAT_ram_3fcbffa8 = 0x30544d47;
      DAT_ram_3fcbffac = 0x545342;
      uVar3 = FUN_ram_4038d3b4();
      FUN_ram_4038d2a2(2,&DAT_ram_3c0c3bc4,
                       "W (%lu) %s: Country not found, using default timezone: GMT0BST\n",uVar3,
                       &DAT_ram_3c0c3bc4);
LAB_ram_42010ade:
      FUN_ram_42017eda(0);
      FUN_ram_42017f22(0,"ntp1.aliyun.com");
      if (DAT_ram_3fcb7c22 == '\0') {
        FUN_ram_42017f22(1,"cn.pool.ntp.org");
      }
      else {
        FUN_ram_42017f22(1,&DAT_ram_3fcb7c22);
      }
      FUN_ram_42017f22(2,"pool.ntp.org");
      FUN_ram_42017e90(FUN_ram_420109de);
      FUN_ram_42017ef2();
      FUN_ram_420a9340(&DAT_ram_3c0c3c28,&DAT_ram_3fcbffa8,1);
      FUN_ram_420aa9c8();
      DAT_ram_3fcc3ab9 = 1;
      DAT_ram_3fcc3ab8 = 0;
      return;
    }
    iVar2 = (*(code *)&SUB_ram_400004a0)
                      ((&PTR_DAT_ram_3c0c3c68_ram_3c0d69b8)[iVar1 * 3],&DAT_ram_3fcb7c63);
    if (iVar2 == 0) {
      (*(code *)&SUB_ram_4000049c)
                (&DAT_ram_3fcbffa8,(&PTR_s_CST_8_ram_3c0c3c6c_ram_3c0d69bc)[iVar1 * 3],0x1f);
      if ((DAT_ram_3fcbffa8 & 0xff) != 0) goto LAB_ram_42010ade;
      goto LAB_ram_42010a9a;
    }
    iVar1 = iVar1 + 1;
  } while( true );
}



// Audit label: caller_of_httpd_start_reference; entry: ram:4200c5ec; name: FUN_ram_4200c5ec

void FUN_ram_4200c5ec(void)

{
  DAT_ram_3fcc3a70 = FUN_ram_4200fa88();
  return;
}



// Audit label: caller_of_esp_http_client_perform_reference; entry: ram:42008e56; name: app_main

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void app_main(void)

{
  int iVar1;
  undefined1 auStack_20 [4];
  undefined1 auStack_1c [28];

  vTaskDelay(100);
  FUN_ram_42017ccc(auStack_1c);
  iVar1 = FUN_ram_40392148(0,auStack_20);
  if (iVar1 != 0) {
    return;
  }
  iVar1 = FUN_ram_4038ab1e();
  (*(code *)&SUB_ram_40000590)(*(undefined4 *)(iVar1 + 8));
  iVar1 = FUN_ram_4203f586();
  if ((iVar1 == 0x110d) || (iVar1 == 0x1110)) {
    iVar1 = FUN_ram_4203f738();
    if (iVar1 != 0) {
                    /* WARNING: Subroutine does not return */
      FUN_ram_4038726a(iVar1,"./main/hello_world_main.c",0x33e,"app_main","nvs_flash_erase()");
    }
    iVar1 = FUN_ram_4203f586();
  }
  if (iVar1 != 0) {
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(iVar1,"./main/hello_world_main.c",0x341,"app_main",&DAT_ram_3c0c2ae4);
  }
  _DAT_ram_3fcb7b84 = DAT_ram_3c0c2ae8;
  DAT_ram_3fcb7b88 = DAT_ram_3c0c2aec;
  DAT_ram_3fcb7b8c = DAT_ram_3c0c2af0;
  DAT_ram_3fcb7b90 = DAT_ram_3c0c2af4;
  FUN_ram_42009a24();
  FUN_ram_42008552();
  FUN_ram_420083b6();
  FUN_ram_42009a0a(0);
  Backlight_pwm_init();
  DAT_ram_3fcc39e9 = '\0';
  DAT_ram_3fcc39d7 = '\0';
  DAT_ram_3fcc39d6 = '\0';
  if (DAT_ram_3fcb7cfc == 2) {
    DAT_ram_3fcc39eb = '\0';
    DAT_ram_3fcc3a54 = 0;
    DAT_ram_3fcc3a74 = '\0';
    DAT_ram_3fcc39ea = '\x01';
  }
  else {
    FUN_ram_4200c100();
  }
  do {
    if (DAT_ram_3fcc39eb == '\0') {
      if (DAT_ram_3fcc39ea == '\0') {
        if ((DAT_ram_3fcc3a74 == '\x02') && (DAT_ram_3fcc39d7 == '\0')) {
          if (DAT_ram_3fcc39d6 == '\0') {
            DAT_ram_3fcc39d6 = '\x1e';
            FUN_ram_42010864();
          }
          else {
            DAT_ram_3fcc39d6 = DAT_ram_3fcc39d6 + -1;
          }
        }
        if (DAT_ram_3fcc39e9 == '\0') {
          DAT_ram_3fcc39e9 = '\x01';
          FUN_ram_42008e08();
        }
        else if (DAT_ram_3fcb7d04 == 0) {
          FUN_ram_4200b738();
        }
        else if (DAT_ram_3fcb7d04 == 1) {
          FUN_ram_4200bd8c();
        }
        else if (DAT_ram_3fcb7d04 == 2) {
          FUN_ram_4200bc36();
        }
        else if (DAT_ram_3fcb7d04 == 3) {
          FUN_ram_4200a5b0();
        }
        if (DAT_ram_3fcc39f3 != '\0') {
          DAT_ram_3fcc39f3 = '\0';
          FUN_ram_42010864();
        }
        FUN_ram_42010b70();
        if (DAT_ram_3fcc39e0 != '\0') {
          if (DAT_ram_3fcc39dc == 0) {
            DAT_ram_3fcc39e0 = '\0';
            FUN_ram_42008a00();
          }
          else {
            DAT_ram_3fcc39dc = DAT_ram_3fcc39dc + -1;
          }
        }
        if (DAT_ram_3fcbffd0 != DAT_ram_3fcc39f1) {
          DAT_ram_3fcc39f1 = DAT_ram_3fcbffd0;
          if (DAT_ram_3fcbffd0 == '\0') {
            DAT_ram_3fcc39f2 = '\x01';
          }
        }
        if (DAT_ram_3fcc39f2 != '\0') {
          DAT_ram_3fcc39f2 = '\0';
          FUN_ram_42008c4c();
        }
      }
      else if (DAT_ram_3fcc3a74 != '\x05') {
        wifi_setup_ap_start();
        FUN_ram_42010c4e();
      }
    }
    else if (DAT_ram_3fcc3a74 == '\x02') {
      if (DAT_ram_3fcc39d7 == '\0') {
        if (DAT_ram_3fcc39d6 == '\0') {
          DAT_ram_3fcc39d6 = '\x1e';
          FUN_ram_42010864();
        }
        else {
          DAT_ram_3fcc39d6 = DAT_ram_3fcc39d6 + -1;
        }
      }
      if (DAT_ram_3fcc39d5 == '\0') {
        if (DAT_ram_3fcc39d4 == '\0') {
          DAT_ram_3fcc39d4 = '\x1e';
          FUN_ram_42010b70();
        }
        else {
          DAT_ram_3fcc39d4 = DAT_ram_3fcc39d4 + -1;
        }
      }
    }
    else {
      FUN_ram_4200ce40();
    }
    if (DAT_ram_3fcc39e8 != '\0') {
      if (DAT_ram_3fcc39e4 == 0) {
        DAT_ram_3fcc39e8 = '\0';
                    /* WARNING: Subroutine does not return */
        esp_restart();
      }
      DAT_ram_3fcc39e4 = DAT_ram_3fcc39e4 + -1;
    }
    vTaskDelay(10);
  } while( true );
}



// Audit label: caller_of_esp_flash_read_reference; entry: ram:4200b738; name: FUN_ram_4200b738

void FUN_ram_4200b738(void)

{
  byte bVar1;
  undefined8 uVar2;

  if (DAT_ram_3fcc39f7 != '\0') {
    DAT_ram_3fcc39f7 = '\0';
    if (DAT_ram_3fcc39d7 == '\0') {
      DAT_ram_3fcba9b8 = s_Getting_Weather_ram_3c0c2b50._0_4_;
      DAT_ram_3fcba9bc = s_Getting_Weather_ram_3c0c2b50._4_4_;
      DAT_ram_3fcba9c0 = s_Getting_Weather_ram_3c0c2b50._8_4_;
      DAT_ram_3fcba9c4 = s_Getting_Weather_ram_3c0c2b50._12_4_;
    }
    else {
      if (DAT_ram_3fcc3a25 == '\0') {
        (*(code *)&SUB_ram_40000498)(&DAT_ram_3fcba9b8,&DAT_ram_3fcb7b84);
      }
      else if (DAT_ram_3fcc3a25 == '\x01') {
        (*(code *)&SUB_ram_40000498)(&DAT_ram_3fcba9b8,&DAT_ram_3fcbff94);
      }
      else if (DAT_ram_3fcc3a25 == '\x02') {
        (*(code *)&SUB_ram_40000498)(&DAT_ram_3fcba9b8,&DAT_ram_3fcb7b84);
      }
      else if (DAT_ram_3fcc3a25 == '\x03') {
        DAT_ram_3fcba9b8 = s_Wind_Speed_ram_3c0c2b60._0_4_;
        DAT_ram_3fcba9bc = s_Wind_Speed_ram_3c0c2b60._4_4_;
        DAT_ram_3fcba9c0._0_3_ =
             CONCAT12(s_Wind_Speed_ram_3c0c2b60[10],s_Wind_Speed_ram_3c0c2b60._8_2_);
      }
      else if (DAT_ram_3fcc3a25 == '\x04') {
        DAT_ram_3fcba9b8._0_1_ = '\0';
        DAT_ram_3fcba9b8._1_1_ = '\0';
        DAT_ram_3fcba9b8._2_1_ = '\0';
        DAT_ram_3fcba9b8._3_1_ = '\0';
        DAT_ram_3fcba9bc._0_1_ = '\0';
        DAT_ram_3fcba9bc._1_1_ = '\0';
        DAT_ram_3fcba9bc._2_1_ = '\0';
        DAT_ram_3fcba9bc._3_1_ = '\0';
        DAT_ram_3fcba9c0._0_1_ = '\0';
        DAT_ram_3fcba9c0._1_1_ = '\0';
        DAT_ram_3fcba9c0._2_1_ = '\0';
        DAT_ram_3fcba9c0._3_1_ = '\0';
        DAT_ram_3fcba9c4._0_1_ = '\0';
        DAT_ram_3fcba9c4._1_1_ = '\0';
        DAT_ram_3fcba9c4._2_1_ = '\0';
        DAT_ram_3fcba9c4._3_1_ = '\0';
        DAT_ram_3fcba9c8 = 0;
        if (DAT_ram_3fcb7d10 == 1) {
          uVar2 = (*(code *)&SUB_ram_40000a8c)
                            (DAT_ram_3fcc3a40,DAT_ram_3fcc3a44,DAT_ram_3c0d6338,DAT_ram_3c0d633c);
          (*(code *)&SUB_ram_400006a8)
                    (&DAT_ram_3fcba9b8,"%.1fkm/h",(int)uVar2,(int)((ulonglong)uVar2 >> 0x20));
        }
        else {
          uVar2 = (*(code *)&SUB_ram_40000a8c)
                            (DAT_ram_3fcc3a40,DAT_ram_3fcc3a44,DAT_ram_3c0d6340,DAT_ram_3c0d6344);
          (*(code *)&SUB_ram_400006a8)
                    (&DAT_ram_3fcba9b8,"%.1fmile/h",(int)uVar2,(int)((ulonglong)uVar2 >> 0x20));
        }
      }
      else if (DAT_ram_3fcc3a25 == '\x05') {
        (*(code *)&SUB_ram_40000498)(&DAT_ram_3fcba9b8,&DAT_ram_3fcb7b84);
      }
      else if (DAT_ram_3fcc3a25 == '\x06') {
        (*(code *)&SUB_ram_40000498)(&DAT_ram_3fcba9b8,&DAT_ram_3fcbff80);
      }
      else if (DAT_ram_3fcc3a25 == '\a') {
        DAT_ram_3fcba9b8._0_1_ = '\0';
        DAT_ram_3fcba9b8._1_1_ = '\0';
        DAT_ram_3fcba9b8._2_1_ = '\0';
        DAT_ram_3fcba9b8._3_1_ = '\0';
        DAT_ram_3fcba9bc._0_1_ = '\0';
        DAT_ram_3fcba9bc._1_1_ = '\0';
        DAT_ram_3fcba9bc._2_1_ = '\0';
        DAT_ram_3fcba9bc._3_1_ = '\0';
        DAT_ram_3fcba9c0._0_1_ = '\0';
        DAT_ram_3fcba9c0._1_1_ = '\0';
        DAT_ram_3fcba9c0._2_1_ = '\0';
        DAT_ram_3fcba9c0._3_1_ = '\0';
        DAT_ram_3fcba9c4._0_1_ = '\0';
        DAT_ram_3fcba9c4._1_1_ = '\0';
        DAT_ram_3fcba9c4._2_1_ = '\0';
        DAT_ram_3fcba9c4._3_1_ = '\0';
        DAT_ram_3fcba9c8 = 0;
        if (DAT_ram_3fcb7d08 == 1) {
          uVar2 = (*(code *)&SUB_ram_40000a8c)
                            (DAT_ram_3fcc3a30,DAT_ram_3fcc3a34,DAT_ram_3c0d6328,DAT_ram_3c0d632c);
          uVar2 = (*(code *)&SUB_ram_40000a18)
                            ((int)uVar2,(int)((ulonglong)uVar2 >> 0x20),DAT_ram_3c0d6330,
                             DAT_ram_3c0d6334);
          (*(code *)&SUB_ram_400006a8)
                    (&DAT_ram_3fcba9b8,&DAT_ram_3c0c2b84,(int)uVar2,(int)((ulonglong)uVar2 >> 0x20))
          ;
        }
        else {
          (*(code *)&SUB_ram_400006a8)
                    (&DAT_ram_3fcba9b8,&DAT_ram_3c0c2b94,DAT_ram_3fcc3a30,DAT_ram_3fcc3a34);
        }
      }
      else if (DAT_ram_3fcc3a25 == '\b') {
        (*(code *)&SUB_ram_40000498)(&DAT_ram_3fcba9b8,&DAT_ram_3fcb7b84);
      }
      else if (DAT_ram_3fcc3a25 == '\t') {
        DAT_ram_3fcba9b8._0_1_ = '\0';
        DAT_ram_3fcba9b8._1_1_ = '\0';
        DAT_ram_3fcba9b8._2_1_ = '\0';
        DAT_ram_3fcba9b8._3_1_ = '\0';
        DAT_ram_3fcba9bc._0_1_ = '\0';
        DAT_ram_3fcba9bc._1_1_ = '\0';
        DAT_ram_3fcba9bc._2_1_ = '\0';
        DAT_ram_3fcba9bc._3_1_ = '\0';
        DAT_ram_3fcba9c0._0_1_ = '\0';
        DAT_ram_3fcba9c0._1_1_ = '\0';
        DAT_ram_3fcba9c0._2_1_ = '\0';
        DAT_ram_3fcba9c0._3_1_ = '\0';
        DAT_ram_3fcba9c4._0_1_ = '\0';
        DAT_ram_3fcba9c4._1_1_ = '\0';
        DAT_ram_3fcba9c4._2_1_ = '\0';
        DAT_ram_3fcba9c4._3_1_ = '\0';
        DAT_ram_3fcba9c8 = 0;
        if (DAT_ram_3fcb7d08 == 1) {
          uVar2 = (*(code *)&SUB_ram_40000a8c)
                            (DAT_ram_3fcc3a38,DAT_ram_3fcc3a3c,DAT_ram_3c0d6328,DAT_ram_3c0d632c);
          uVar2 = (*(code *)&SUB_ram_40000a18)
                            ((int)uVar2,(int)((ulonglong)uVar2 >> 0x20),DAT_ram_3c0d6330,
                             DAT_ram_3c0d6334);
          (*(code *)&SUB_ram_400006a8)
                    (&DAT_ram_3fcba9b8,&DAT_ram_3c0c2ba4,(int)uVar2,(int)((ulonglong)uVar2 >> 0x20))
          ;
        }
        else {
          (*(code *)&SUB_ram_400006a8)
                    (&DAT_ram_3fcba9b8,&DAT_ram_3c0c2bb4,DAT_ram_3fcc3a38,DAT_ram_3fcc3a3c);
        }
      }
      bVar1 = DAT_ram_3fcc3a25 + 1;
      DAT_ram_3fcc3a25 = DAT_ram_3fcc3a25 + '\x01';
      if (9 < bVar1) {
        DAT_ram_3fcc3a25 = '\0';
      }
    }
    FUN_ram_4200af5e();
  }
  if (((DAT_ram_3fcbffce != DAT_ram_3fcc3a29) || (DAT_ram_3fcbffcf != DAT_ram_3fcc3a28)) ||
     (DAT_ram_3fcbffd0 != DAT_ram_3fcc3a27)) {
    FUN_ram_4200afcc();
    DAT_ram_3fcc3a29 = DAT_ram_3fcbffce;
    DAT_ram_3fcc3a28 = DAT_ram_3fcbffcf;
    DAT_ram_3fcc3a27 = DAT_ram_3fcbffd0;
  }
  if (DAT_ram_3fcc39f5 != '\0') {
    DAT_ram_3fcc39f5 = '\0';
    FUN_ram_4200b340();
    FUN_ram_4200aefc();
  }
  read_animation_frame_table();
  return;
}



// Audit label: caller_of_esp_flash_read_reference; entry: ram:4200b340; name: FUN_ram_4200b340

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_ram_4200b340(void)

{
  byte bVar1;
  undefined4 uVar2;
  undefined8 uVar3;

  if (DAT_ram_3fcc39d7 != '\0') {
    bVar1 = (*(code *)&SUB_ram_400004a8)(&DAT_ram_3fcbff6c);
    if (bVar1 < 7) {
      if (bVar1 == 0) goto LAB_ram_4200b3ac;
    }
    else {
      bVar1 = 6;
    }
    FUN_ram_4200abee(((int)(0x50 - (uint)(byte)(bVar1 * '\f')) >> 1 & 0xffffU) + 0xa0 & 0xffff,0x53,
                     &DAT_ram_3fcbff6c,0x18,0xffe0,0);
  }
LAB_ram_4200b3ac:
  if (DAT_ram_3fcc3aa8 != 0) {
    FUN_ram_42010eca(0xb4,10);
  }
  FUN_ram_4200c518(10,0xb4,0x3ba800);
  FUN_ram_4200c518(0x28,0xba,0x3c2000);
  _DAT_ram_3fcba9a8 = 0;
  DAT_ram_3fcba9ac = 0;
  DAT_ram_3fcba9b0 = 0;
  DAT_ram_3fcba9b4 = 0;
  DAT_ram_3fcba9b6 = 0;
  FUN_ram_42009936(0x50,0xb4,0x48,0x18,0);
  if (DAT_ram_3fcc39d7 == '\0') {
    if (DAT_ram_3fcb7d08 == 1) {
      _DAT_ram_3fcba9a8 = 0xa82d2d20;
      DAT_ram_3fcba9ac = CONCAT22(DAT_ram_3fcba9ac._2_2_,0x48);
    }
    else {
      _DAT_ram_3fcba9a8 = 0xa12d2d20;
      DAT_ram_3fcba9ac = CONCAT22(DAT_ram_3fcba9ac._2_2_,0xe6);
    }
  }
  else {
    uVar3 = (*(code *)&SUB_ram_40000a54)(DAT_ram_3fcc3a4c);
    uVar2 = (undefined4)((ulonglong)uVar3 >> 0x20);
    if (DAT_ram_3fcb7d08 == 1) {
      uVar3 = (*(code *)&SUB_ram_40000a8c)((int)uVar3,uVar2,DAT_ram_3c0d6328,DAT_ram_3c0d632c);
      uVar3 = (*(code *)&SUB_ram_40000a18)
                        ((int)uVar3,(int)((ulonglong)uVar3 >> 0x20),DAT_ram_3c0d6330,
                         DAT_ram_3c0d6334);
      (*(code *)&SUB_ram_400006a8)
                (&DAT_ram_3fcba9a8,&DAT_ram_3c0c2b8c,(int)uVar3,(int)((ulonglong)uVar3 >> 0x20));
    }
    else {
      (*(code *)&SUB_ram_400006a8)(&DAT_ram_3fcba9a8,&DAT_ram_3c0c2b9c,(int)uVar3,uVar2);
    }
  }
  FUN_ram_4200abee(0x50,0xb4,&DAT_ram_3fcba9a8,0x18,0xffff,0);
  FUN_ram_4200c518(0xc,0xd2,0x3be400);
  FUN_ram_4200c518(0x28,0xd8,0x3c5c00);
  _DAT_ram_3fcba9a8 = 0;
  DAT_ram_3fcba9ac = 0;
  DAT_ram_3fcba9b0 = 0;
  DAT_ram_3fcba9b4 = 0;
  DAT_ram_3fcba9b6 = 0;
  FUN_ram_42009936(0x50,0xd2,0x48,0x18,0);
  if (DAT_ram_3fcc39d7 == '\0') {
    (*(code *)&SUB_ram_400006a8)(&DAT_ram_3fcba9a8," --%%");
  }
  else {
    (*(code *)&SUB_ram_400006a8)(&DAT_ram_3fcba9a8," %d%%",DAT_ram_3fcc3a48);
  }
  FUN_ram_4200abee(0x50,0xd2,&DAT_ram_3fcba9a8,0x18,0xffff,0);
  return;
}



// Audit label: caller_of_configured_ssid_reference; entry: ram:4200ce40; name: FUN_ram_4200ce40

void FUN_ram_4200ce40(void)

{
  if (DAT_ram_3fcb7cfc == 1) {
    if ((DAT_ram_3fcc3a74 == '\0') || (DAT_ram_3fcc3a74 == '\x03')) {
      FUN_ram_4200ca30();
    }
    else if (DAT_ram_3fcc3a74 == '\x04') {
      DAT_ram_3fcb7cfc = 0;
      FUN_ram_42008a00();
      DAT_ram_3fcc39ea = 1;
    }
  }
  else {
    DAT_ram_3fcc39ea = 1;
  }
  return;
}



// Audit label: caller_of_pool_ntp_org_reference; entry: ram:42010b70; name: FUN_ram_42010b70

void FUN_ram_42010b70(void)

{
  undefined4 uVar1;
  int iVar2;
  uint uStack_3c;
  undefined1 uStack_38;
  undefined1 uStack_34;
  undefined1 uStack_30;
  char cStack_2c;
  int iStack_28;
  undefined1 uStack_24;
  undefined1 auStack_18 [16];

  if (DAT_ram_3fcc3ab9 == '\0') {
    FUN_ram_42010a06();
  }
  else {
    FUN_ram_420aa7e2(auStack_18);
    FUN_ram_420aa5ce(auStack_18,&uStack_3c);
    if (iStack_28 < 0x7d) {
      DAT_ram_3fcc3ab4 = DAT_ram_3fcc3ab4 + 1;
      if (0x14 < DAT_ram_3fcc3ab4) {
        uVar1 = FUN_ram_4038d3b4();
        FUN_ram_4038d2a2(2,&DAT_ram_3c0c3bc4,"W (%lu) %s: Time not synced yet. Current year: %d\n",
                         uVar1,&DAT_ram_3c0c3bc4,iStack_28 + 0x76c);
        DAT_ram_3fcc3ab4 = 0;
        iVar2 = FUN_ram_42017ea0();
        if (iVar2 == 0) {
          DAT_ram_3fcc3ab9 = '\0';
        }
      }
    }
    else {
      DAT_ram_3fcc3ab4 = 0;
      if (DAT_ram_3fcbffd0 != uStack_3c) {
        DAT_ram_3fcbffc8 = iStack_28 + 0x76c;
        DAT_ram_3fcbffcc = cStack_2c + '\x01';
        DAT_ram_3fcbffcd = uStack_30;
        DAT_ram_3fcbffce = uStack_34;
        DAT_ram_3fcbffcf = uStack_38;
        DAT_ram_3fcbffd0 = (byte)uStack_3c;
        DAT_ram_3fcbffd1 = uStack_24;
      }
    }
  }
  return;
}



// Audit label: caller_of_esp_flash_write_reference; entry: ram:4200db12; name: FUN_ram_4200db12

void FUN_ram_4200db12(int param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  uint uVar4;

  if ((((param_1 != 0) && (param_2 != 0)) && (param_3 != 0)) && (param_4 != 0)) {
    iVar1 = FUN_ram_4200daaa(param_1,param_2,&DAT_ram_3c0c0838);
    if (iVar1 == 0) {
      uVar3 = FUN_ram_4038d3b4();
      FUN_ram_4038d2a2(1,&DAT_ram_3c0c3290,"E (%lu) %s: not find 0D 0A 0D 0A\n\n",uVar3,
                       &DAT_ram_3c0c3290);
    }
    else {
      uVar4 = iVar1 + 4;
      uVar2 = FUN_ram_4200daaa(uVar4,param_2 - (uVar4 - param_1),"---");
      if (uVar2 == 0) {
        uVar3 = FUN_ram_4038d3b4();
        FUN_ram_4038d2a2(1,&DAT_ram_3c0c3290,"E (%lu) %s: not find ---\n\n",uVar3,&DAT_ram_3c0c3290)
        ;
      }
      else {
        for (; (*(char *)(uVar2 - 1) == '\r' || (*(char *)(uVar2 - 1) == '\n')); uVar2 = uVar2 - 1)
        {
        }
        if (uVar4 < uVar2) {
          iVar1 = uVar2 - uVar4;
          uVar3 = FUN_ram_4038d3b4();
          FUN_ram_4038d2a2(1,&DAT_ram_3c0c3290,"E (%lu) %s: start:0x%x end:0x%x content_len:%d\n",
                           uVar3,&DAT_ram_3c0c3290,uVar4,uVar2,iVar1);
          esp_flash_write(0,uVar4,DAT_ram_3fcbd2e8,iVar1);
          DAT_ram_3fcbd2dc = DAT_ram_3fcbd2dc + iVar1;
          DAT_ram_3fcbd2e8 = iVar1 + DAT_ram_3fcbd2e8;
          DAT_ram_3fcbd2e4 = DAT_ram_3fcbd2e4 + 1;
        }
        else {
          uVar3 = FUN_ram_4038d3b4();
          FUN_ram_4038d2a2(1,&DAT_ram_3c0c3290,"E (%lu) %s: start:0x%x end:0x%x data len=0\n\n",
                           uVar3,&DAT_ram_3c0c3290,uVar4,uVar2);
        }
      }
    }
  }
  return;
}



// Audit label: caller_of_esp_flash_write_reference; entry: ram:42008a00; name: FUN_ram_42008a00

void FUN_ram_42008a00(void)

{
  esp_flash_erase_region(0,0x3e7000,0x1000);
  esp_flash_write(0,&DAT_ram_3fcb7b9c,0x3e7000,0x1bc);
  return;
}



// Audit label: caller_of_esp_ota_get_running_partition_reference; entry: ram:4207bc60; name: FUN_ram_4207bc60

undefined4 FUN_ram_4207bc60(uint param_1,int param_2)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;

  if (param_1 < 0x8c01) {
    uVar1 = 0;
  }
  else {
    iVar2 = esp_ota_get_running_partition();
    uVar3 = *(uint *)(iVar2 + 0xc);
    if ((param_1 < uVar3) || (*(int *)(iVar2 + 0x10) + uVar3 <= param_1)) {
      if (param_1 < uVar3) {
        if (uVar3 < param_1 + param_2) {
          uVar1 = 0;
        }
        else {
          uVar1 = 1;
        }
      }
      else {
        uVar1 = 1;
      }
    }
    else {
      uVar1 = 0;
    }
  }
  return uVar1;
}



// Audit label: uri_get_checkbox_state; entry: ram:4200e630; name: uri_get_checkbox_state

undefined4 uri_get_checkbox_state(undefined4 param_1)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;

  DAT_ram_3fcc3a80 = (DAT_ram_3fcb7d40 & 1) != 0;
  DAT_ram_3fcc3a81 = (DAT_ram_3fcb7d40 & 2) != 0;
  DAT_ram_3fcc3a82 = (DAT_ram_3fcb7d40 & 4) != 0;
  DAT_ram_3fcc3a83 = (DAT_ram_3fcb7d40 & 8) != 0;
  DAT_ram_3fcc3a84 = (DAT_ram_3fcb7d40 & 0x10) != 0;
  uVar1 = FUN_ram_42013948();
  FUN_ram_42013814(uVar1,"file1_switch",DAT_ram_3fcc3a80);
  FUN_ram_42013814(uVar1,"file2_switch",DAT_ram_3fcc3a81);
  FUN_ram_42013814(uVar1,"file3_switch",DAT_ram_3fcc3a82);
  FUN_ram_42013814(uVar1,"file4_switch",DAT_ram_3fcc3a83);
  FUN_ram_42013814(uVar1,"file5_switch",DAT_ram_3fcc3a84);
  uVar2 = FUN_ram_420137b6(uVar1);
  FUN_ram_4203b178(param_1,"application/json");
  FUN_ram_4203b114(param_1,"Connection","close");
  uVar3 = (*(code *)&SUB_ram_400004a8)(uVar2);
  FUN_ram_4203b192(param_1,uVar2,uVar3);
  FUN_ram_4201322a(uVar1);
  FUN_ram_4038e4da(uVar2);
  return 0;
}



// Audit label: uri_get_display_time; entry: ram:4200e7b6; name: uri_get_display_time

undefined4 uri_get_display_time(undefined4 param_1)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined8 uVar4;

  uVar1 = FUN_ram_42013948();
  uVar4 = (*(code *)&SUB_ram_40000a64)(DAT_ram_3fcb7d3c);
  FUN_ram_42013906(uVar1,"displaytime",(int)uVar4,(int)((ulonglong)uVar4 >> 0x20));
  uVar2 = FUN_ram_420137b6(uVar1);
  FUN_ram_4203b178(param_1,"application/json");
  FUN_ram_4203b114(param_1,"Connection","close");
  uVar3 = (*(code *)&SUB_ram_400004a8)(uVar2);
  FUN_ram_4203b192(param_1,uVar2,uVar3);
  FUN_ram_4201322a(uVar1);
  FUN_ram_4038e4da(uVar2);
  return 0;
}



// Audit label: uri_photo; entry: ram:4200d54c; name: uri_photo

undefined4 uri_photo(undefined4 param_1)

{
  undefined4 uVar1;

  uVar1 = (*(code *)&SUB_ram_400004a8)(&DAT_ram_3c0e2e6e);
  FUN_ram_4200d394(&DAT_ram_3c0e2e6e,uVar1,0);
  FUN_ram_4203b114(param_1,"Connection","close");
  uVar1 = (*(code *)&SUB_ram_400004a8)(&DAT_ram_3c0e2e6e);
  FUN_ram_4203b192(param_1,&DAT_ram_3c0e2e6e,uVar1);
  return 0;
}



// Audit label: uri_restart; entry: ram:4200d34a; name: uri_restart

undefined4 uri_restart(undefined4 param_1)

{
  FUN_ram_4203b114(param_1,"Connection","close");
  FUN_ram_4203b192(param_1,&DAT_ram_3c0c328c,2);
  DAT_ram_3fcc39e4 = 5;
  DAT_ram_3fcc39e8 = 1;
  return 0;
}



// Audit label: uri_GetNightStopTime; entry: ram:4200ec12; name: uri_GetNightStopTime

undefined4 uri_GetNightStopTime(undefined4 param_1)

{
  undefined4 uVar1;
  undefined1 auStack_18 [12];

  (*(code *)&SUB_ram_400006a8)(auStack_18,&DAT_ram_3c0c35f8,DAT_ram_3fcb7d34);
  FUN_ram_4203b178(param_1,"text/plain");
  FUN_ram_4203b114(param_1,"Connection","close");
  uVar1 = (*(code *)&SUB_ram_400004a8)(auStack_18);
  FUN_ram_4203b192(param_1,auStack_18,uVar1);
  return 0;
}



// Audit label: uri_GetNightStartTime; entry: ram:4200ec80; name: uri_GetNightStartTime

undefined4 uri_GetNightStartTime(undefined4 param_1)

{
  undefined4 uVar1;
  undefined1 auStack_18 [12];

  (*(code *)&SUB_ram_400006a8)(auStack_18,&DAT_ram_3c0c35f8,DAT_ram_3fcb7d30);
  FUN_ram_4203b178(param_1,"text/plain");
  FUN_ram_4203b114(param_1,"Connection","close");
  uVar1 = (*(code *)&SUB_ram_400004a8)(auStack_18);
  FUN_ram_4203b192(param_1,auStack_18,uVar1);
  return 0;
}



// Audit label: uri_get_night_brightness; entry: ram:4200ecee; name: uri_get_night_brightness

undefined4 uri_get_night_brightness(undefined4 param_1)

{
  undefined4 uVar1;
  undefined1 auStack_44 [56];

  (*(code *)&SUB_ram_400006ac)
            (auStack_44,0x32,"{\"brightness\":%d}",100 - DAT_ram_3fcb7d38 / 10 & 0xffff);
  FUN_ram_4203b178(param_1,"application/json");
  FUN_ram_4203b114(param_1,"Connection","close");
  uVar1 = (*(code *)&SUB_ram_400004a8)(auStack_44);
  FUN_ram_4203b192(param_1,auStack_44,uVar1);
  return 0;
}



// Audit label: uri_get_clock_colors; entry: ram:4200f22a; name: uri_get_clock_colors

undefined4 uri_get_clock_colors(undefined4 param_1)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined1 auStack_a0 [140];

  uVar1 = FUN_ram_42008a6a(DAT_ram_3fcb7d20);
  uVar2 = FUN_ram_42008a6a(DAT_ram_3fcb7d24);
  uVar3 = FUN_ram_42008a6a(DAT_ram_3fcb7d28);
  (*(code *)&SUB_ram_400006ac)
            (auStack_a0,0x80,"{\"color0\":\"#%06lx\",\"color1\":\"#%06lx\",\"color2\":\"#%06lx\"}",
             uVar1,uVar2,uVar3);
  FUN_ram_4203b178(param_1,"application/json");
  FUN_ram_4203b114(param_1,"Connection","close");
  uVar1 = (*(code *)&SUB_ram_400004a8)(auStack_a0);
  FUN_ram_4203b192(param_1,auStack_a0,uVar1);
  return 0;
}



// Audit label: uri_get_led_brightness; entry: ram:4200ed78; name: uri_get_led_brightness

undefined4 uri_get_led_brightness(undefined4 param_1)

{
  undefined4 uVar1;
  undefined1 auStack_44 [56];

  (*(code *)&SUB_ram_400006ac)
            (auStack_44,0x32,"{\"brightness\":%d}",100 - DAT_ram_3fcb7d1c / 10 & 0xffff);
  FUN_ram_4203b178(param_1,"application/json");
  FUN_ram_4203b114(param_1,"Connection","close");
  uVar1 = (*(code *)&SUB_ram_400004a8)(auStack_44);
  FUN_ram_4203b192(param_1,auStack_44,uVar1);
  return 0;
}



// Audit label: uri_GetTimeModeValue; entry: ram:4200df5a; name: uri_GetTimeModeValue

undefined4 uri_GetTimeModeValue(undefined4 param_1)

{
  undefined4 uVar1;
  undefined1 uStack_14;
  undefined1 uStack_13;

  uStack_14 = 0x32;
  if (DAT_ram_3fcb7d18 == 0) {
    uStack_14 = 0x30;
  }
  else if (DAT_ram_3fcb7d18 == 1) {
    uStack_14 = 0x31;
  }
  uStack_13 = 0;
  FUN_ram_4203b178(param_1,"text/plain");
  FUN_ram_4203b114(param_1,"Connection","close");
  uVar1 = (*(code *)&SUB_ram_400004a8)(&uStack_14);
  FUN_ram_4203b192(param_1,&uStack_14,uVar1);
  return 0;
}



// Audit label: uri_getsettings; entry: ram:4200ee02; name: uri_getsettings

undefined4 uri_getsettings(undefined4 param_1)

{
  undefined4 uVar1;
  undefined1 auStack_90 [132];

  if (DAT_ram_3fcb7d08 == 0) {
    *(undefined1 *)(gp + -1999) = 0;
  }
  else {
    *(undefined1 *)(gp + -1999) = 1;
  }
  DAT_ram_3fcc3a96 = DAT_ram_3fcb7d0c != 0;
  DAT_ram_3fcc3a95 = DAT_ram_3fcb7d10 != 0;
  if (DAT_ram_3fcb7d14 == 0) {
    *(undefined1 *)(gp + -2000) = 0;
  }
  else {
    *(undefined1 *)(gp + -2000) = 1;
  }
  (*(code *)&SUB_ram_400006ac)
            (auStack_90,0x80,
             "{\"tempUnit\":%d,\"hourFormat\":%d,\"mileDisplay\":%d,\"timeSync\":%d,\"nightmode\":%d}"
             ,*(undefined1 *)(gp + -1999),DAT_ram_3fcc3a96,DAT_ram_3fcc3a95,
             *(undefined1 *)(gp + -2000),DAT_ram_3fcc3a94);
  FUN_ram_4203b178(param_1,"application/json");
  FUN_ram_4203b114(param_1,"Connection","close");
  uVar1 = (*(code *)&SUB_ram_400004a8)(auStack_90);
  FUN_ram_4203b192(param_1,auStack_90,uVar1);
  return 0;
}



// Audit label: uri_getclocktype; entry: ram:4200dfdc; name: uri_getclocktype

undefined4 uri_getclocktype(undefined4 param_1)

{
  undefined4 uVar1;
  undefined1 uStack_14;
  undefined1 uStack_13;

  uStack_14 = 0x30;
  if (DAT_ram_3fcb7d04 != 0) {
    if (DAT_ram_3fcb7d04 == 1) {
      uStack_14 = 0x31;
    }
    else if (DAT_ram_3fcb7d04 == 2) {
      uStack_14 = 0x32;
    }
    else if (DAT_ram_3fcb7d04 == 3) {
      uStack_14 = 0x33;
    }
  }
  uStack_13 = 0;
  FUN_ram_4203b178(param_1,"text/plain");
  FUN_ram_4203b114(param_1,"Connection","close");
  uVar1 = (*(code *)&SUB_ram_400004a8)(&uStack_14);
  FUN_ram_4203b192(param_1,&uStack_14,uVar1);
  return 0;
}



// Audit label: uri_getgifvalue; entry: ram:4200e074; name: uri_getgifvalue

undefined4 uri_getgifvalue(undefined4 param_1)

{
  undefined4 uVar1;
  undefined1 uStack_14;
  undefined1 uStack_13;

  uStack_14 = 0x30;
  if (DAT_ram_3fcb7d00 != 0) {
    if (DAT_ram_3fcb7d00 == 1) {
      uStack_14 = 0x31;
    }
    else if (DAT_ram_3fcb7d00 == 2) {
      uStack_14 = 0x32;
    }
    else if (DAT_ram_3fcb7d00 == 3) {
      uStack_14 = 0x33;
    }
    else if (DAT_ram_3fcb7d00 == 4) {
      uStack_14 = 0x34;
    }
  }
  uStack_13 = 0;
  FUN_ram_4203b178(param_1,"text/plain");
  FUN_ram_4203b114(param_1,"Connection","close");
  uVar1 = (*(code *)&SUB_ram_400004a8)(&uStack_14);
  FUN_ram_4203b192(param_1,&uStack_14,uVar1);
  return 0;
}



// Audit label: uri_scan; entry: ram:4200f440; name: uri_scan

undefined4 uri_scan(undefined4 param_1)

{
  int iVar1;
  undefined1 *puVar2;
  int iVar3;
  undefined4 uVar4;
  undefined1 auStack_60 [72];

  FUN_ram_4200c9e0();
  if (0x14 < DAT_ram_3fcc3a6e) {
    DAT_ram_3fcc3a6e = 0x14;
  }
  puVar2 = (undefined1 *)FUN_ram_4038e4be((uint)DAT_ram_3fcc3a6e << 6);
  *puVar2 = 0x5b;
  puVar2[1] = 0;
  for (iVar1 = 0; iVar1 < (int)(uint)DAT_ram_3fcc3a6e; iVar1 = iVar1 + 1) {
    (*(code *)&SUB_ram_40000488)(auStack_60,0,0x40);
    (*(code *)&SUB_ram_400006ac)
              (auStack_60,0x40,"{\"ssid\":\"%s\",\"rssi\":%d}",&DAT_ram_3fcbcbaa + iVar1 * 0x5c,
               (int)(char)(&DAT_ram_3fcbcbd0)[iVar1 * 0x5c]);
    if (iVar1 < (int)(DAT_ram_3fcc3a6e - 1)) {
      iVar3 = (*(code *)&SUB_ram_400004a8)(auStack_60);
      auStack_60[iVar3] = 0x2c;
      auStack_60[iVar3 + 1] = 0;
    }
    (*(code *)&SUB_ram_4000050c)(puVar2,auStack_60);
  }
  iVar1 = (*(code *)&SUB_ram_400004a8)(puVar2);
  puVar2[iVar1] = 0x5d;
  (puVar2 + iVar1)[1] = 0;
  FUN_ram_4203b178(param_1,"application/json");
  FUN_ram_4203b114(param_1,"Connection","close");
  uVar4 = (*(code *)&SUB_ram_400004a8)(puVar2);
  FUN_ram_4203b192(param_1,puVar2,uVar4);
  FUN_ram_4038e4da(puVar2);
  return 0;
}



// Audit label: uri_root; entry: ram:4200d404; name: uri_root

undefined4 uri_root(undefined4 param_1)

{
  undefined4 uVar1;

  if (DAT_ram_3fcc3a74 == '\x02') {
    uVar1 = (*(code *)&SUB_ram_400004a8)(&DAT_ram_3c0d963b);
    FUN_ram_4200d394(&DAT_ram_3c0d963b,uVar1,0);
    FUN_ram_4203b114(param_1,"Connection","close");
    uVar1 = (*(code *)&SUB_ram_400004a8)(&DAT_ram_3c0d963b);
    FUN_ram_4203b192(param_1,&DAT_ram_3c0d963b,uVar1);
  }
  else {
    uVar1 = (*(code *)&SUB_ram_400004a8)(&DAT_ram_3c0d6edc);
    FUN_ram_4200d394(&DAT_ram_3c0d6edc,uVar1,0);
    FUN_ram_4203b114(param_1,"Connection","close");
    uVar1 = (*(code *)&SUB_ram_400004a8)(&DAT_ram_3c0d6edc);
    FUN_ram_4203b192(param_1,&DAT_ram_3c0d6edc,uVar1);
  }
  return 0;
}



// Audit label: wifi_setup_ap_config; entry: ram:4200ce9e; name: wifi_setup_ap_config

undefined4 wifi_setup_ap_config(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_f0;
  undefined4 uStack_ec;
  undefined4 uStack_e8;
  undefined4 uStack_e4;
  undefined4 uStack_e0;
  undefined4 uStack_dc;
  undefined4 uStack_d8;
  undefined4 uStack_d4;
  undefined1 uStack_90;
  undefined1 uStack_8f;
  undefined4 uStack_8c;
  undefined1 uStack_87;
  undefined1 uStack_35;
  undefined4 auStack_34 [5];
  undefined1 uStack_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;

  iVar1 = FUN_ram_42036770("WIFI_AP_DEF");
  if (iVar1 != 0) {
    FUN_ram_4203678e();
  }
  uVar2 = FUN_ram_420459d6();
  uStack_1c = 0;
  uStack_18 = 0;
  uStack_14 = 0;
  uStack_1c = FUN_ram_4202bb02(&DAT_ram_3c0c2ae8);
  uStack_18 = FUN_ram_4202bb02("255.255.255.0");
  uStack_14 = FUN_ram_4202bb02(&DAT_ram_3c0c2ae8);
  iVar1 = FUN_ram_420369c6(uVar2);
  if (iVar1 != 0) {
    FUN_ram_40387248(iVar1,"./main/wifi_connect.c",0x197,"wifi_init_softap2",
                     "esp_netif_dhcps_stop(esp_netif_ap)");
  }
  vTaskDelay(5);
  iVar1 = FUN_ram_42036f28(uVar2,&uStack_1c);
  if (iVar1 != 0) {
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(iVar1,"./main/wifi_connect.c",0x199,"wifi_init_softap2",
                     "esp_netif_set_ip_info(esp_netif_ap, &ip_info)");
  }
  auStack_34[0] = uStack_1c;
  uStack_20 = 0;
  iVar1 = FUN_ram_42036f42(uVar2,0,auStack_34);
  if (iVar1 != 0) {
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(iVar1,"./main/wifi_connect.c",0x1a5,"wifi_init_softap2",
                     "esp_netif_set_dns_info(esp_netif_ap, ESP_NETIF_DNS_MAIN, &dns_info)");
  }
  uStack_35 = 1;
  iVar1 = FUN_ram_420371f0(uVar2,1,6,&uStack_35,1);
  if (iVar1 == 0) {
    iVar1 = FUN_ram_420369ac(uVar2);
    if (iVar1 != 0) {
      FUN_ram_40387248(iVar1,"./main/wifi_connect.c",0x1b4,"wifi_init_softap2",
                       "esp_netif_dhcps_start(esp_netif_ap)");
    }
    (*(code *)&SUB_ram_40000488)(&local_f0,0,0xb8);
    local_f0 = 0x6c616d53;
    uStack_ec = 0x56545f6c;
    uStack_e8 = 0;
    uStack_e4 = 0;
    uStack_e0 = 0;
    uStack_dc = 0;
    uStack_d8 = 0;
    uStack_d4 = 0;
    uStack_90 = 8;
    uStack_8f = 1;
    uStack_87 = 3;
    uStack_8c = 0;
    iVar1 = FUN_ram_420692da(1,&local_f0);
    if (iVar1 == 0) {
      return uVar2;
    }
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(iVar1,"./main/wifi_connect.c",0x1c8,"wifi_init_softap2",
                     "esp_wifi_set_config(WIFI_IF_AP, &wifi_ap_config)");
  }
                    /* WARNING: Subroutine does not return */
  FUN_ram_4038726a(iVar1,"./main/wifi_connect.c",0x1aa,"wifi_init_softap2",
                   "esp_netif_dhcps_option( esp_netif_ap, ESP_NETIF_OP_SET, ESP_NETIF_DOMAIN_NAME_SERVER, &dhcps_dns_enabled, sizeof(dhcps_dns_enabled) )"
                  );
}



// Audit label: wifi_setup_ap_start; entry: ram:4200d06e; name: wifi_setup_ap_start

void wifi_setup_ap_start(void)

{
  int iVar1;
  undefined4 uVar2;
  int iStack_a8;
  undefined4 uStack_a4;
  undefined4 uStack_a0;
  undefined *puStack_9c;
  undefined *puStack_98;
  undefined *puStack_94;
  undefined *puStack_90;
  undefined *puStack_8c;
  undefined *puStack_88;
  undefined *puStack_84;
  undefined *puStack_80;
  undefined *puStack_7c;
  undefined4 uStack_78;
  undefined4 uStack_74;
  undefined4 uStack_70;
  undefined4 uStack_6c;
  undefined4 uStack_68;
  undefined4 uStack_64;
  undefined4 uStack_60;
  undefined4 uStack_5c;
  undefined4 uStack_58;
  undefined4 uStack_54;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined4 uStack_48;
  undefined4 uStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined1 uStack_28;
  undefined4 uStack_24;
  undefined4 uStack_20;
  undefined1 uStack_1c;
  undefined4 uStack_18;

  iVar1 = FUN_ram_42036604();
  if (iVar1 != 0) {
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(iVar1,"./main/wifi_connect.c",0x1d4,"wifi_init_softap","esp_netif_init()");
  }
  iVar1 = FUN_ram_420aeb30();
  if (iVar1 != 0) {
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(iVar1,"./main/wifi_connect.c",0x1d5,"wifi_init_softap",
                     "esp_event_loop_create_default()");
  }
  iVar1 = FUN_ram_4203f586();
  if ((iVar1 == 0x110d) || (iVar1 == 0x1110)) {
    iVar1 = FUN_ram_4203f738();
    if (iVar1 != 0) {
                    /* WARNING: Subroutine does not return */
      FUN_ram_4038726a(iVar1,"./main/wifi_connect.c",0x1da,"wifi_init_softap","nvs_flash_erase()");
    }
    iVar1 = FUN_ram_4203f586();
  }
  if (iVar1 != 0) {
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(iVar1,"./main/wifi_connect.c",0x1dd,"wifi_init_softap",&DAT_ram_3c0c2b1c);
  }
  DAT_ram_3fcc3a7c = FUN_ram_40388bfe();
  iVar1 = FUN_ram_420aeab6(PTR_s_WIFI_EVENT_ram_3c0cf320_ram_3c0f1eb8,0xffffffff,FUN_ram_4200c6e2,0,
                           0);
  if (iVar1 != 0) {
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(iVar1,"./main/wifi_connect.c",0x1e3,"wifi_init_softap",
                     "esp_event_handler_instance_register(WIFI_EVENT, ESP_EVENT_ANY_ID, &wifi_event_handler, NULL, NULL)"
                    );
  }
  iVar1 = FUN_ram_420aeab6(PTR_s_IP_EVENT_ram_3c0cb788_ram_3c0f1848,0,FUN_ram_4200c6e2,0,0);
  if (iVar1 != 0) {
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(iVar1,"./main/wifi_connect.c",0x1e8,"wifi_init_softap",
                     "esp_event_handler_instance_register(IP_EVENT, IP_EVENT_STA_GOT_IP, &wifi_event_handler, NULL, NULL)"
                    );
  }
  iStack_a8 = gp + -0x424;
  uStack_a4 = DAT_ram_3c0f1e8c;
  uStack_a0 = DAT_ram_3c0f1e90;
  puStack_9c = PTR_FUN_ram_420437c2_ram_3c0f1e94;
  puStack_98 = PTR_FUN_ram_42043a72_ram_3c0f1e98;
  puStack_94 = PTR_FUN_ram_420438d0_ram_3c0f1e9c;
  puStack_90 = PTR_FUN_ram_42043960_ram_3c0f1ea0;
  puStack_8c = PTR_FUN_ram_42043ba4_ram_3c0f1ea4;
  puStack_88 = PTR_FUN_ram_420440de_ram_3c0f1ea8;
  puStack_84 = PTR_FUN_ram_420441a2_ram_3c0f1eac;
  puStack_80 = PTR_FUN_ram_420435da_ram_3c0f1eb0;
  puStack_7c = PTR_FUN_ram_420437aa_ram_3c0f1eb4;
  uStack_78 = 10;
  uStack_74 = 0x20;
  uStack_70 = 1;
  uStack_6c = 0;
  uStack_68 = 0x20;
  uStack_64 = 0;
  uStack_60 = 5;
  uStack_5c = 0;
  uStack_58 = 0;
  uStack_54 = 1;
  uStack_50 = 1;
  uStack_4c = 0;
  uStack_48 = 1;
  uStack_44 = 1;
  uStack_40 = 6;
  uStack_3c = 0;
  uStack_38 = 0x2f0;
  uStack_34 = 0x20;
  uStack_30 = 0xa1;
  uStack_2c = 0;
  uStack_28 = 1;
  uStack_24 = 2;
  uStack_20 = 1;
  uStack_1c = 0;
  uStack_18 = 0x1f2f3f4f;
  iVar1 = FUN_ram_4204544e(&iStack_a8);
  if (iVar1 != 0) {
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(iVar1,"./main/wifi_connect.c",0x1f0,"wifi_init_softap","esp_wifi_init(&cfg)");
  }
  iVar1 = FUN_ram_42068cb6(3);
  if (iVar1 == 0) {
    uVar2 = wifi_setup_ap_config();
    iVar1 = FUN_ram_42068d06();
    if (iVar1 == 0) {
      vTaskDelay(100);
      FUN_ram_4200c956(uVar2);
      FUN_ram_4200c9e0();
      DAT_ram_3fcc3a74 = 5;
      FUN_ram_420b10ce();
      FUN_ram_4038a7a4(FUN_ram_4200c74e,"dns_server",0x1000,0,5,0,0x7fffffff);
      return;
    }
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(iVar1,"./main/wifi_connect.c",0x1ff,"wifi_init_softap","esp_wifi_start()");
  }
                    /* WARNING: Subroutine does not return */
  FUN_ram_4038726a(iVar1,"./main/wifi_connect.c",0x1f2,"wifi_init_softap",
                   "esp_wifi_set_mode(WIFI_MODE_APSTA)");
}
