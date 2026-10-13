/* GHIDRA REFERENCE PSEUDOCODE, NOT COMPILED.
 * Retains addresses, unresolved SDK calls and decompiler type/overlap artifacts.
 * Executable reconstruction: app/web/photo_api.c + app/media/photo_upload.c.
 */

// Audit label: http_photo_at_4200d54c; entry: ram:4200d54c; name: http_photo_at_4200d54c

undefined4 http_photo_at_4200d54c(undefined4 http_request)

{
  undefined4 uVar1;

  uVar1 = (*(code *)&SUB_ram_400004a8)(&DAT_ram_3c0e2e6e);
  send_http_json_number_at_4200d394(&DAT_ram_3c0e2e6e,uVar1,0);
  FUN_ram_4203b114(http_request,"Connection","close");
  uVar1 = (*(code *)&SUB_ram_400004a8)(&DAT_ram_3c0e2e6e);
  FUN_ram_4203b192(http_request,&DAT_ram_3c0e2e6e,uVar1);
  return 0;
}

// Audit label: http_finish_upload_at_4200d978; entry: ram:4200d978; name: http_finish_upload_at_4200d978

undefined4 http_finish_upload_at_4200d978(undefined4 http_request)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 auStack_90 [136];

  iVar2 = httpd_req_recv(http_request,auStack_90,0x7f);
  iVar1 = DAT_ram_3fcbd2d4;
  if (iVar2 < 1) {
    FUN_ram_4203b382(http_request,0,"Failed to receive data");
    uVar3 = 0xffffffff;
  }
  else {
    auStack_90[iVar2] = 0;
    *(undefined4 *)(&DAT_ram_3fcb7ba4 + (DAT_ram_3fcbd2d4 + 0x67) * 4) = DAT_ram_3fcbd2d8;
    if (iVar1 == 1) {
      enabled_photo_mask_at_3fcb7b9c = enabled_photo_mask_at_3fcb7b9c | 1;
    }
    else if (iVar1 == 2) {
      enabled_photo_mask_at_3fcb7b9c = enabled_photo_mask_at_3fcb7b9c | 2;
    }
    else if (iVar1 == 3) {
      enabled_photo_mask_at_3fcb7b9c = enabled_photo_mask_at_3fcb7b9c | 4;
    }
    else if (iVar1 == 4) {
      enabled_photo_mask_at_3fcb7b9c = enabled_photo_mask_at_3fcb7b9c | 8;
    }
    else if (iVar1 == 5) {
      enabled_photo_mask_at_3fcb7b9c = enabled_photo_mask_at_3fcb7b9c | 0x10;
    }
    save_settings_sector_at_42008a00();
    DAT_ram_3fcbd2d4 = 0;
    DAT_ram_3fcbd2d8 = 0;
    DAT_ram_3fcbd2dc = 0;
    DAT_ram_3fcbd2e0 = 0;
    DAT_ram_3fcbd2e4 = 0;
    DAT_ram_3fcbd2e8 = 0;
    FUN_ram_4203b15e(http_request,&DAT_ram_3c0c3288);
    FUN_ram_4203b114(http_request,"Connection","close");
    FUN_ram_4203b192(http_request,&DAT_ram_3c0c328c,2);
    DAT_ram_3fcc39d8 = 0;
    uVar3 = 0;
  }
  return uVar3;
}

// Audit label: http_upload_chunk_at_4200dc58; entry: ram:4200dc58; name: http_upload_chunk_at_4200dc58

undefined4 http_upload_chunk_at_4200dc58(int http_request)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uStack_114;
  undefined1 auStack_110 [128];
  undefined1 auStack_90 [128];

  (*(code *)&SUB_ram_40000488)(auStack_90,0,0x80);
  (*(code *)&SUB_ram_40000488)(auStack_110,0,0x80);
  iVar1 = httpd_req_get_hdr_value_str(http_request,"Content-Type",auStack_110,0x80);
  if (iVar1 == 0) {
    iVar1 = *(int *)(http_request + 0x20c);
    if (iVar1 == 0) {
      FUN_ram_4203b382(http_request,3,"Empty chunk");
      uVar3 = 0xffffffff;
    }
    else if (DAT_ram_3fcbd2d4 - 1U < 5) {
      if ((uint)(DAT_ram_3fcbd2dc + iVar1) < 0x19001) {
        iVar2 = httpd_req_recv(http_request,&DAT_ram_3fcbd2ec,iVar1);
        if (iVar2 == iVar1) {
          uStack_114 = 0;
          parse_multipart_upload_body_at_4200db12(&DAT_ram_3fcbd2ec,iVar1,auStack_90,&uStack_114);
          FUN_ram_4203b15e(http_request,&DAT_ram_3c0c3288);
          FUN_ram_4203b114(http_request,"Connection","close");
          FUN_ram_4203b192(http_request,&DAT_ram_3c0c328c,2);
          uVar3 = 0;
        }
        else {
          FUN_ram_4203b382(http_request,3,"Incomplete chunk");
          uVar3 = 0xffffffff;
        }
      }
      else {
        FUN_ram_4203b382(http_request,3,"Out of memory");
        uVar3 = 0xffffffff;
      }
    }
    else {
      FUN_ram_4203b382(http_request,3,"No active upload");
      uVar3 = 0xffffffff;
    }
  }
  else {
    FUN_ram_4203b382(http_request,3,"Missing Content-Type");
    uVar3 = 0xffffffff;
  }
  return uVar3;
}

// Audit label: http_start_upload_at_4200dda4; entry: ram:4200dda4; name: http_start_upload_at_4200dda4

undefined4 http_start_upload_at_4200dda4(undefined4 http_request)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  undefined1 auStack_120 [268];

  iVar2 = httpd_req_recv(http_request,auStack_120,0xff);
  if (iVar2 < 1) {
    FUN_ram_4203b382(http_request,0,"Failed to receive data");
    uVar6 = 0xffffffff;
  }
  else {
    auStack_120[iVar2] = 0;
    iVar2 = FUN_ram_420137a4(auStack_120);
    if (iVar2 == 0) {
      FUN_ram_4203b382(http_request,3,"Invalid JSON");
      uVar6 = 0xffffffff;
    }
    else {
      iVar3 = FUN_ram_420137e0(iVar2,"file_number");
      iVar4 = FUN_ram_420137e0(iVar2,"file_size");
      iVar5 = FUN_ram_420137e0(iVar2,"total_chunks");
      if (((iVar3 == 0) || (iVar4 == 0)) || (iVar5 == 0)) {
        FUN_ram_4201322a(iVar2);
        FUN_ram_4203b382(http_request,3,"Missing required fields");
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
            FUN_ram_4203b15e(http_request,&DAT_ram_3c0c3288);
            FUN_ram_4203b114(http_request,"Connection","close");
            FUN_ram_4203b192(http_request,&DAT_ram_3c0c328c,2);
            DAT_ram_3fcc39d8 = 1;
            uVar6 = 0;
          }
          else {
            FUN_ram_4201322a(iVar2);
            FUN_ram_4203b382(http_request,3,"File too large");
            uVar6 = 0xffffffff;
          }
        }
        else {
          FUN_ram_4201322a(iVar2);
          FUN_ram_4203b382(http_request,3,"Invalid file number");
          uVar6 = 0xffffffff;
        }
      }
    }
  }
  return uVar6;
}

// Audit label: http_get_Photo_File_at_4200e11c; entry: ram:4200e11c; name: http_get_Photo_File_at_4200e11c

undefined4 http_get_Photo_File_at_4200e11c(undefined4 http_request)

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

  iVar2 = FUN_ram_4203a4a8(http_request,auStack_50,0x40);
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
      FUN_ram_4203b382(http_request,6,"Image not found");
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
    FUN_ram_4203b178(http_request,"application/json");
    FUN_ram_4203b114(http_request,"Connection","close");
    uVar6 = (*(code *)&SUB_ram_400004a8)(uVar5);
    FUN_ram_4203b192(http_request,uVar5,uVar6);
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
      FUN_ram_4203b178(http_request,"application/octet-stream");
      FUN_ram_4203b114(http_request,"Connection","close");
      FUN_ram_4203b192(http_request,&DAT_ram_3fcbd2ec,uVar7 - uVar8);
      uVar4 = 0;
    }
    else {
      FUN_ram_4203b382(http_request,3,"Invalid chunk index");
      uVar4 = 0xffffffff;
    }
  }
  return uVar4;
}

// Audit label: http_set_checkbox_state_at_4200e2ec; entry: ram:4200e2ec; name: http_set_checkbox_state_at_4200e2ec

undefined4 http_set_checkbox_state_at_4200e2ec(undefined4 http_request)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined1 auStack_a0 [136];

  iVar2 = httpd_req_recv(http_request,auStack_a0,0x7f);
  if (iVar2 < 1) {
    FUN_ram_4203b382(http_request,0,"Failed to receive data");
    uVar7 = 0xffffffff;
  }
  else {
    auStack_a0[iVar2] = 0;
    iVar2 = FUN_ram_420137a4(auStack_a0);
    if (iVar2 == 0) {
      FUN_ram_4203b382(http_request,3,"Invalid JSON");
      uVar7 = 0xffffffff;
    }
    else {
      iVar3 = FUN_ram_420137e0(iVar2,"checkbox_id");
      iVar4 = FUN_ram_420137e0(iVar2,"checked");
      if ((((iVar3 == 0) || (iVar5 = FUN_ram_42013984(iVar3), iVar5 == 0)) || (iVar4 == 0)) ||
         (iVar5 = FUN_ram_42013974(iVar4), iVar5 == 0)) {
        FUN_ram_4203b382(http_request,3,"Missing checkbox_id or checked field");
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
            slideshow_photo_mask_at_3fcb7d40 = slideshow_photo_mask_at_3fcb7d40 & 0xfffffffe;
          }
          else {
            slideshow_photo_mask_at_3fcb7d40 = slideshow_photo_mask_at_3fcb7d40 | 1;
          }
          DAT_ram_3fcc39e0 = 1;
          DAT_ram_3fcc39dc = 0x32;
          DAT_ram_3fcc3a88 = bVar1;
        }
        else {
          iVar4 = (*(code *)&SUB_ram_400004a0)(uVar7,"file2-switch");
          if (iVar4 == 0) {
            if (iVar3 == 0) {
              slideshow_photo_mask_at_3fcb7d40 = slideshow_photo_mask_at_3fcb7d40 & 0xfffffffd;
            }
            else {
              slideshow_photo_mask_at_3fcb7d40 = slideshow_photo_mask_at_3fcb7d40 | 2;
            }
            DAT_ram_3fcc39e0 = 1;
            DAT_ram_3fcc39dc = 0x32;
            DAT_ram_3fcc3a89 = bVar1;
          }
          else {
            iVar4 = (*(code *)&SUB_ram_400004a0)(uVar7,"file3-switch");
            if (iVar4 == 0) {
              if (iVar3 == 0) {
                slideshow_photo_mask_at_3fcb7d40 = slideshow_photo_mask_at_3fcb7d40 & 0xfffffffb;
              }
              else {
                slideshow_photo_mask_at_3fcb7d40 = slideshow_photo_mask_at_3fcb7d40 | 4;
              }
              DAT_ram_3fcc39e0 = 1;
              DAT_ram_3fcc39dc = 0x32;
              DAT_ram_3fcc3a8a = bVar1;
            }
            else {
              iVar4 = (*(code *)&SUB_ram_400004a0)(uVar7,"file4-switch");
              if (iVar4 == 0) {
                if (iVar3 == 0) {
                  slideshow_photo_mask_at_3fcb7d40 = slideshow_photo_mask_at_3fcb7d40 & 0xfffffff7;
                }
                else {
                  slideshow_photo_mask_at_3fcb7d40 = slideshow_photo_mask_at_3fcb7d40 | 8;
                }
                DAT_ram_3fcc39e0 = 1;
                DAT_ram_3fcc39dc = 0x32;
                DAT_ram_3fcc3a8b = bVar1;
              }
              else {
                iVar4 = (*(code *)&SUB_ram_400004a0)(uVar7,"file5-switch");
                if (iVar4 == 0) {
                  if (iVar3 == 0) {
                    slideshow_photo_mask_at_3fcb7d40 = slideshow_photo_mask_at_3fcb7d40 & 0xffffffef;
                  }
                  else {
                    slideshow_photo_mask_at_3fcb7d40 = slideshow_photo_mask_at_3fcb7d40 | 0x10;
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
                         &DAT_ram_3c0c3290,slideshow_photo_mask_at_3fcb7d40);
        FUN_ram_4201322a(iVar2);
        FUN_ram_4203b114(http_request,"Connection","close");
        FUN_ram_4203b192(http_request,&DAT_ram_3c0c328c,2);
        uVar7 = 0;
      }
    }
  }
  return uVar7;
}

// Audit label: http_get_checkbox_state_at_4200e630; entry: ram:4200e630; name: http_get_checkbox_state_at_4200e630

undefined4 http_get_checkbox_state_at_4200e630(undefined4 http_request)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;

  DAT_ram_3fcc3a80 = (slideshow_photo_mask_at_3fcb7d40 & 1) != 0;
  DAT_ram_3fcc3a81 = (slideshow_photo_mask_at_3fcb7d40 & 2) != 0;
  DAT_ram_3fcc3a82 = (slideshow_photo_mask_at_3fcb7d40 & 4) != 0;
  DAT_ram_3fcc3a83 = (slideshow_photo_mask_at_3fcb7d40 & 8) != 0;
  DAT_ram_3fcc3a84 = (slideshow_photo_mask_at_3fcb7d40 & 0x10) != 0;
  uVar1 = FUN_ram_42013948();
  FUN_ram_42013814(uVar1,"file1_switch",DAT_ram_3fcc3a80);
  FUN_ram_42013814(uVar1,"file2_switch",DAT_ram_3fcc3a81);
  FUN_ram_42013814(uVar1,"file3_switch",DAT_ram_3fcc3a82);
  FUN_ram_42013814(uVar1,"file4_switch",DAT_ram_3fcc3a83);
  FUN_ram_42013814(uVar1,"file5_switch",DAT_ram_3fcc3a84);
  uVar2 = FUN_ram_420137b6(uVar1);
  FUN_ram_4203b178(http_request,"application/json");
  FUN_ram_4203b114(http_request,"Connection","close");
  uVar3 = (*(code *)&SUB_ram_400004a8)(uVar2);
  FUN_ram_4203b192(http_request,uVar2,uVar3);
  FUN_ram_4201322a(uVar1);
  FUN_ram_4038e4da(uVar2);
  return 0;
}

// Audit label: http_get_display_time_at_4200e7b6; entry: ram:4200e7b6; name: http_get_display_time_at_4200e7b6

undefined4 http_get_display_time_at_4200e7b6(undefined4 http_request)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined8 uVar4;

  uVar1 = FUN_ram_42013948();
  uVar4 = (*(code *)&SUB_ram_40000a64)(photo_interval_seconds_at_3fcb7d3c);
  FUN_ram_42013906(uVar1,"displaytime",(int)uVar4,(int)((ulonglong)uVar4 >> 0x20));
  uVar2 = FUN_ram_420137b6(uVar1);
  FUN_ram_4203b178(http_request,"application/json");
  FUN_ram_4203b114(http_request,"Connection","close");
  uVar3 = (*(code *)&SUB_ram_400004a8)(uVar2);
  FUN_ram_4203b192(http_request,uVar2,uVar3);
  FUN_ram_4201322a(uVar1);
  FUN_ram_4038e4da(uVar2);
  return 0;
}

// Audit label: http_set_display_time_at_4200f7aa; entry: ram:4200f7aa; name: http_set_display_time_at_4200f7aa

undefined4 http_set_display_time_at_4200f7aa(undefined4 http_request)

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

  iVar1 = httpd_req_recv(http_request,auStack_50,0x3f);
  if (iVar1 < 1) {
    FUN_ram_4203b382(http_request,8,0);
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
    parse_photo_interval_at_4200f764(&uStack_64);
    FUN_ram_4203b114(http_request,"Connection","close");
    FUN_ram_4203b192(http_request,&DAT_ram_3c0c328c,2);
    uVar3 = 0;
  }
  return uVar3;
}
