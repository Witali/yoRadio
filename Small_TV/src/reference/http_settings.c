/* GHIDRA REFERENCE PSEUDOCODE, NOT COMPILED.
 * Retains addresses, unresolved SDK calls and decompiler type/overlap artifacts.
 * Per-function reconstruction targets: symbol-map.json native_targets.
 */

// Audit label: http_restart_at_4200d34a; entry: ram:4200d34a; name: http_restart_at_4200d34a

undefined4 http_restart_at_4200d34a(undefined4 http_request)

{
  FUN_ram_4203b114(http_request,"Connection","close");
  FUN_ram_4203b192(http_request,&DAT_ram_3c0c328c,2);
  DAT_ram_3fcc39e4 = 5;
  DAT_ram_3fcc39e8 = 1;
  return 0;
}

// Audit label: http_root_at_4200d404; entry: ram:4200d404; name: http_root_at_4200d404

undefined4 http_root_at_4200d404(undefined4 http_request)

{
  undefined4 uVar1;

  if (wifi_connection_state_at_3fcc3a74 == '\x02') {
    uVar1 = (*(code *)&SUB_ram_400004a8)(&DAT_ram_3c0d963b);
    send_http_json_number_at_4200d394(&DAT_ram_3c0d963b,uVar1,0);
    FUN_ram_4203b114(http_request,"Connection","close");
    uVar1 = (*(code *)&SUB_ram_400004a8)(&DAT_ram_3c0d963b);
    FUN_ram_4203b192(http_request,&DAT_ram_3c0d963b,uVar1);
  }
  else {
    uVar1 = (*(code *)&SUB_ram_400004a8)(&DAT_ram_3c0d6edc);
    send_http_json_number_at_4200d394(&DAT_ram_3c0d6edc,uVar1,0);
    FUN_ram_4203b114(http_request,"Connection","close");
    uVar1 = (*(code *)&SUB_ram_400004a8)(&DAT_ram_3c0d6edc);
    FUN_ram_4203b192(http_request,&DAT_ram_3c0d6edc,uVar1);
  }
  return 0;
}

// Audit label: http_set_night_brightness_at_4200d5ac; entry: ram:4200d5ac; name: http_set_night_brightness_at_4200d5ac

undefined4 http_set_night_brightness_at_4200d5ac(undefined4 http_request)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_50 [72];

  iVar1 = httpd_req_recv(http_request,auStack_50,0x3f);
  if (iVar1 < 1) {
    FUN_ram_4203b382(http_request,8,0);
    uVar2 = 0xffffffff;
  }
  else {
    auStack_50[iVar1] = 0;
    iVar1 = (*(code *)&SUB_ram_400004ac)(auStack_50,"NightBrightness=");
    if (iVar1 != 0) {
      DAT_ram_3fcc3a98 = (*(code *)&SUB_ram_40000580)(iVar1 + 0x10);
      night_backlight_per_mille_at_3fcb7d38 = DAT_ram_3fcc3a98 * -10 + 1000;
      DAT_ram_3fcc39f2 = 1;
      DAT_ram_3fcc39e0 = 1;
      DAT_ram_3fcc39dc = 0x32;
    }
    FUN_ram_4203b114(http_request,"Connection","close");
    FUN_ram_4203b192(http_request,&DAT_ram_3c0c328c,2);
    uVar2 = 0;
  }
  return uVar2;
}

// Audit label: http_set_led_brightness_at_4200d66a; entry: ram:4200d66a; name: http_set_led_brightness_at_4200d66a

undefined4 http_set_led_brightness_at_4200d66a(undefined4 http_request)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_50 [72];

  iVar1 = httpd_req_recv(http_request,auStack_50,0x3f);
  if (iVar1 < 1) {
    FUN_ram_4203b382(http_request,8,0);
    uVar2 = 0xffffffff;
  }
  else {
    auStack_50[iVar1] = 0;
    iVar1 = (*(code *)&SUB_ram_400004ac)(auStack_50,"ledBrightness=");
    if (iVar1 != 0) {
      iVar1 = (*(code *)&SUB_ram_40000580)(iVar1 + 0xe);
      day_backlight_per_mille_at_3fcb7d1c = iVar1 * -10 + 1000;
      DAT_ram_3fcc39f2 = 1;
      DAT_ram_3fcc39e0 = 1;
      DAT_ram_3fcc39dc = 0x32;
    }
    FUN_ram_4203b114(http_request,"Connection","close");
    FUN_ram_4203b192(http_request,&DAT_ram_3c0c328c,2);
    uVar2 = 0;
  }
  return uVar2;
}

// Audit label: http_SetTimeModeValue_at_4200d720; entry: ram:4200d720; name: http_SetTimeModeValue_at_4200d720

undefined4 http_SetTimeModeValue_at_4200d720(int http_request)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_24 [28];

  if (*(uint *)(http_request + 0x20c) < 0x41) {
    iVar1 = httpd_req_recv(http_request,auStack_24,0x14);
    if (iVar1 < 1) {
      FUN_ram_4203b382(http_request,8,0);
      uVar2 = 0xffffffff;
    }
    else {
      auStack_24[iVar1] = 0;
      iVar1 = (*(code *)&SUB_ram_400004ac)(auStack_24,"timemode");
      if ((*(byte *)(iVar1 + 0xb) - 0x30 & 0xff) < 3) {
        date_format_at_3fcb7d18 = *(byte *)(iVar1 + 0xb) - 0x30;
        DAT_ram_3fcc39f5 = 1;
        DAT_ram_3fcc39e0 = 1;
        DAT_ram_3fcc39dc = 0x32;
        DAT_ram_3fcc3a26 = 1;
      }
      FUN_ram_4203b114(http_request,"Connection","close");
      FUN_ram_4203b192(http_request,&DAT_ram_3c0c328c,2);
      uVar2 = 0;
    }
  }
  else {
    FUN_ram_4203b382(http_request,9,0);
    uVar2 = 0xffffffff;
  }
  return uVar2;
}

// Audit label: http_setclocktype_at_4200d7f0; entry: ram:4200d7f0; name: http_setclocktype_at_4200d7f0

undefined4 http_setclocktype_at_4200d7f0(int http_request)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_24 [28];

  if (*(uint *)(http_request + 0x20c) < 0x41) {
    iVar1 = httpd_req_recv(http_request,auStack_24,0x14);
    if (iVar1 < 1) {
      FUN_ram_4203b382(http_request,8,0);
      uVar2 = 0xffffffff;
    }
    else {
      auStack_24[iVar1] = 0;
      iVar1 = (*(code *)&SUB_ram_400004ac)(auStack_24,"clocktype");
      if ((*(byte *)(iVar1 + 0xc) - 0x30 & 0xff) < 4) {
        selected_clock_theme_at_3fcb7d04 = *(byte *)(iVar1 + 0xc) - 0x30;
        DAT_ram_3fcc39e9 = 0;
        DAT_ram_3fcc39e0 = 1;
        DAT_ram_3fcc39dc = 0x32;
      }
      FUN_ram_4203b114(http_request,"Connection","close");
      FUN_ram_4203b192(http_request,&DAT_ram_3c0c328c,2);
      uVar2 = 0;
    }
  }
  else {
    FUN_ram_4203b382(http_request,9,0);
    uVar2 = 0xffffffff;
  }
  return uVar2;
}

// Audit label: http_setgifvalue_at_4200d8b8; entry: ram:4200d8b8; name: http_setgifvalue_at_4200d8b8

undefined4 http_setgifvalue_at_4200d8b8(int http_request)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_20 [24];

  if (*(uint *)(http_request + 0x20c) < 0x41) {
    iVar1 = httpd_req_recv(http_request,auStack_20,0x10);
    if (iVar1 < 1) {
      FUN_ram_4203b382(http_request,8,0);
      uVar2 = 0xffffffff;
    }
    else {
      auStack_20[iVar1] = 0;
      iVar1 = (*(code *)&SUB_ram_400004ac)(auStack_20,&DAT_ram_3c0c326c);
      if ((*(byte *)(iVar1 + 6) - 0x30 & 0xff) < 5) {
        selected_animation_at_3fcb7d00 = *(byte *)(iVar1 + 6) - 0x30;
        DAT_ram_3fcc39e0 = 1;
        DAT_ram_3fcc39dc = 0x32;
      }
      FUN_ram_4203b114(http_request,"Connection","close");
      FUN_ram_4203b192(http_request,&DAT_ram_3c0c328c,2);
      uVar2 = 0;
    }
  }
  else {
    FUN_ram_4203b382(http_request,9,0);
    uVar2 = 0xffffffff;
  }
  return uVar2;
}

// Audit label: http_GetTimeModeValue_at_4200df5a; entry: ram:4200df5a; name: http_GetTimeModeValue_at_4200df5a

undefined4 http_GetTimeModeValue_at_4200df5a(undefined4 http_request)

{
  undefined4 uVar1;
  undefined1 uStack_14;
  undefined1 uStack_13;

  uStack_14 = 0x32;
  if (date_format_at_3fcb7d18 == 0) {
    uStack_14 = 0x30;
  }
  else if (date_format_at_3fcb7d18 == 1) {
    uStack_14 = 0x31;
  }
  uStack_13 = 0;
  FUN_ram_4203b178(http_request,"text/plain");
  FUN_ram_4203b114(http_request,"Connection","close");
  uVar1 = (*(code *)&SUB_ram_400004a8)(&uStack_14);
  FUN_ram_4203b192(http_request,&uStack_14,uVar1);
  return 0;
}

// Audit label: http_getclocktype_at_4200dfdc; entry: ram:4200dfdc; name: http_getclocktype_at_4200dfdc

undefined4 http_getclocktype_at_4200dfdc(undefined4 http_request)

{
  undefined4 uVar1;
  undefined1 uStack_14;
  undefined1 uStack_13;

  uStack_14 = 0x30;
  if (selected_clock_theme_at_3fcb7d04 != 0) {
    if (selected_clock_theme_at_3fcb7d04 == 1) {
      uStack_14 = 0x31;
    }
    else if (selected_clock_theme_at_3fcb7d04 == 2) {
      uStack_14 = 0x32;
    }
    else if (selected_clock_theme_at_3fcb7d04 == 3) {
      uStack_14 = 0x33;
    }
  }
  uStack_13 = 0;
  FUN_ram_4203b178(http_request,"text/plain");
  FUN_ram_4203b114(http_request,"Connection","close");
  uVar1 = (*(code *)&SUB_ram_400004a8)(&uStack_14);
  FUN_ram_4203b192(http_request,&uStack_14,uVar1);
  return 0;
}

// Audit label: http_getgifvalue_at_4200e074; entry: ram:4200e074; name: http_getgifvalue_at_4200e074

undefined4 http_getgifvalue_at_4200e074(undefined4 http_request)

{
  undefined4 uVar1;
  undefined1 uStack_14;
  undefined1 uStack_13;

  uStack_14 = 0x30;
  if (selected_animation_at_3fcb7d00 != 0) {
    if (selected_animation_at_3fcb7d00 == 1) {
      uStack_14 = 0x31;
    }
    else if (selected_animation_at_3fcb7d00 == 2) {
      uStack_14 = 0x32;
    }
    else if (selected_animation_at_3fcb7d00 == 3) {
      uStack_14 = 0x33;
    }
    else if (selected_animation_at_3fcb7d00 == 4) {
      uStack_14 = 0x34;
    }
  }
  uStack_13 = 0;
  FUN_ram_4203b178(http_request,"text/plain");
  FUN_ram_4203b114(http_request,"Connection","close");
  uVar1 = (*(code *)&SUB_ram_400004a8)(&uStack_14);
  FUN_ram_4203b192(http_request,&uStack_14,uVar1);
  return 0;
}

// Audit label: http_wifireset_at_4200e84c; entry: ram:4200e84c; name: http_wifireset_at_4200e84c

undefined4 http_wifireset_at_4200e84c(undefined4 http_request)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  undefined1 auStack_120 [268];

  iVar1 = httpd_req_recv(http_request,auStack_120,0xff);
  if (iVar1 < 1) {
    FUN_ram_4203b382(http_request,8,0);
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
        (*(code *)&SUB_ram_4000049c)(&wifi_ssid_at_3fcb7ba0,iVar2,uVar5);
        (&wifi_ssid_at_3fcb7ba0)[uVar5] = 0;
      }
    }
    if (iVar1 != 0) {
      iVar1 = iVar1 + 0xc;
      iVar2 = (*(code *)&SUB_ram_40000514)(iVar1,0x22);
      if ((iVar2 != 0) && (uVar5 = iVar2 - iVar1, uVar5 < 0x40)) {
        (*(code *)&SUB_ram_4000049c)(&wifi_password_at_3fcb7be1,iVar1,uVar5);
        (&wifi_password_at_3fcb7be1)[uVar5] = 0;
      }
    }
    uVar4 = (*(code *)&SUB_ram_400004a8)(&DAT_ram_3fcbff2c);
    (*(code *)&SUB_ram_4000049c)(&wifi_ssid_at_3fcb7ba0,&DAT_ram_3fcbff2c,uVar4);
    uVar4 = (*(code *)&SUB_ram_400004a8)(&DAT_ram_3fcbfeec);
    (*(code *)&SUB_ram_4000049c)(&wifi_password_at_3fcb7be1,&DAT_ram_3fcbfeec,uVar4);
    DAT_ram_3fcb7cfc = 1;
    save_settings_sector_at_42008a00();
    FUN_ram_4203b114(http_request,"Connection","close");
    FUN_ram_4203b192(http_request,&DAT_ram_3c0c328c,2);
    DAT_ram_3fcc39e4 = 10;
    DAT_ram_3fcc39e8 = 1;
    uVar4 = 0;
  }
  return uVar4;
}

// Audit label: http_advancedset_at_4200e9ea; entry: ram:4200e9ea; name: http_advancedset_at_4200e9ea

undefined4 http_advancedset_at_4200e9ea(undefined4 http_request)

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

  iVar1 = httpd_req_recv(http_request,auStack_120,0xff);
  if (iVar1 < 1) {
    FUN_ram_4203b382(http_request,8,0);
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
        (*(code *)&SUB_ram_40000488)(&ntp_server_at_3fcb7c22,0,0x41);
        (*(code *)&SUB_ram_4000049c)(&ntp_server_at_3fcb7c22,iVar2,uVar5);
        (&ntp_server_at_3fcb7c22)[uVar5] = 0;
        DAT_ram_3fcc39e0 = 1;
        DAT_ram_3fcc39dc = 0x32;
      }
    }
    if (iVar1 != 0) {
      iVar1 = iVar1 + 0x15;
      iVar2 = (*(code *)&SUB_ram_40000514)(iVar1,0x22);
      if ((iVar2 != 0) && (uVar5 = iVar2 - iVar1, uVar5 < 0x40)) {
        (*(code *)&SUB_ram_40000488)(&weather_api_key_at_3fcb7cb8,0,0x41);
        (*(code *)&SUB_ram_4000049c)(&weather_api_key_at_3fcb7cb8,iVar1,uVar5);
        (&weather_api_key_at_3fcb7cb8)[uVar5] = 0;
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
    FUN_ram_4203b178(http_request,"text/plain");
    FUN_ram_4203b114(http_request,"Connection","close");
    uVar4 = (*(code *)&SUB_ram_400004a8)(acStack_138);
    FUN_ram_4203b192(http_request,acStack_138,uVar4);
    uVar4 = 0;
  }
  return uVar4;
}

// Audit label: http_GetNightStopTime_at_4200ec12; entry: ram:4200ec12; name: http_GetNightStopTime_at_4200ec12

undefined4 http_GetNightStopTime_at_4200ec12(undefined4 http_request)

{
  undefined4 uVar1;
  undefined1 auStack_18 [12];

  (*(code *)&SUB_ram_400006a8)(auStack_18,&DAT_ram_3c0c35f8,night_stop_hour_at_3fcb7d34);
  FUN_ram_4203b178(http_request,"text/plain");
  FUN_ram_4203b114(http_request,"Connection","close");
  uVar1 = (*(code *)&SUB_ram_400004a8)(auStack_18);
  FUN_ram_4203b192(http_request,auStack_18,uVar1);
  return 0;
}

// Audit label: http_GetNightStartTime_at_4200ec80; entry: ram:4200ec80; name: http_GetNightStartTime_at_4200ec80

undefined4 http_GetNightStartTime_at_4200ec80(undefined4 http_request)

{
  undefined4 uVar1;
  undefined1 auStack_18 [12];

  (*(code *)&SUB_ram_400006a8)(auStack_18,&DAT_ram_3c0c35f8,night_start_hour_at_3fcb7d30);
  FUN_ram_4203b178(http_request,"text/plain");
  FUN_ram_4203b114(http_request,"Connection","close");
  uVar1 = (*(code *)&SUB_ram_400004a8)(auStack_18);
  FUN_ram_4203b192(http_request,auStack_18,uVar1);
  return 0;
}

// Audit label: http_get_night_brightness_at_4200ecee; entry: ram:4200ecee; name: http_get_night_brightness_at_4200ecee

undefined4 http_get_night_brightness_at_4200ecee(undefined4 http_request)

{
  undefined4 uVar1;
  undefined1 auStack_44 [56];

  (*(code *)&SUB_ram_400006ac)
            (auStack_44,0x32,"{\"brightness\":%d}",100 - night_backlight_per_mille_at_3fcb7d38 / 10 & 0xffff);
  FUN_ram_4203b178(http_request,"application/json");
  FUN_ram_4203b114(http_request,"Connection","close");
  uVar1 = (*(code *)&SUB_ram_400004a8)(auStack_44);
  FUN_ram_4203b192(http_request,auStack_44,uVar1);
  return 0;
}

// Audit label: http_get_led_brightness_at_4200ed78; entry: ram:4200ed78; name: http_get_led_brightness_at_4200ed78

undefined4 http_get_led_brightness_at_4200ed78(undefined4 http_request)

{
  undefined4 uVar1;
  undefined1 auStack_44 [56];

  (*(code *)&SUB_ram_400006ac)
            (auStack_44,0x32,"{\"brightness\":%d}",100 - day_backlight_per_mille_at_3fcb7d1c / 10 & 0xffff);
  FUN_ram_4203b178(http_request,"application/json");
  FUN_ram_4203b114(http_request,"Connection","close");
  uVar1 = (*(code *)&SUB_ram_400004a8)(auStack_44);
  FUN_ram_4203b192(http_request,auStack_44,uVar1);
  return 0;
}

// Audit label: http_getsettings_at_4200ee02; entry: ram:4200ee02; name: http_getsettings_at_4200ee02

undefined4 http_getsettings_at_4200ee02(undefined4 http_request)

{
  undefined4 uVar1;
  undefined1 auStack_90 [132];

  if (fahrenheit_flag_at_3fcb7d08 == 0) {
    *(undefined1 *)(gp + -1999) = 0;
  }
  else {
    *(undefined1 *)(gp + -1999) = 1;
  }
  DAT_ram_3fcc3a96 = hour12_flag_at_3fcb7d0c != 0;
  DAT_ram_3fcc3a95 = miles_flag_at_3fcb7d10 != 0;
  if (browser_time_flag_at_3fcb7d14 == 0) {
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
  FUN_ram_4203b178(http_request,"application/json");
  FUN_ram_4203b114(http_request,"Connection","close");
  uVar1 = (*(code *)&SUB_ram_400004a8)(auStack_90);
  FUN_ram_4203b192(http_request,auStack_90,uVar1);
  return 0;
}

// Audit label: http_settings_at_4200ef62; entry: ram:4200ef62; name: http_settings_at_4200ef62

undefined4 http_settings_at_4200ef62(undefined4 http_request)

{
  undefined1 uVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 auStack_90 [128];

  iVar2 = httpd_req_recv(http_request,auStack_90,0x7f);
  if (iVar2 < 1) {
    uVar3 = 0xffffffff;
  }
  else {
    auStack_90[iVar2] = 0;
    uVar1 = parse_json_switch_value_at_4200eefe(auStack_90,"tempUnit");
    *(undefined1 *)(gp + -1999) = uVar1;
    DAT_ram_3fcc3a96 = parse_json_switch_value_at_4200eefe(auStack_90,"hourFormat");
    DAT_ram_3fcc3a95 = parse_json_switch_value_at_4200eefe(auStack_90,"mileDisplay");
    iVar2 = parse_json_switch_value_at_4200eefe(auStack_90,"timeSync");
    *(char *)(gp + -2000) = (char)iVar2;
    DAT_ram_3fcc39f5 = 1;
    fahrenheit_flag_at_3fcb7d08 = (uint)(*(char *)(gp + -1999) != '\0');
    hour12_flag_at_3fcb7d0c = (uint)(DAT_ram_3fcc3a96 != '\0');
    miles_flag_at_3fcb7d10 = (uint)(DAT_ram_3fcc3a95 != '\0');
    browser_time_flag_at_3fcb7d14 = (uint)(iVar2 != 0);
    DAT_ram_3fcc39f2 = 1;
    DAT_ram_3fcc39e0 = 1;
    DAT_ram_3fcc39dc = 0x32;
    FUN_ram_4203b114(http_request,"Connection","close");
    FUN_ram_4203b192(http_request,&DAT_ram_3c0c328c,2);
    uVar3 = 0;
  }
  return uVar3;
}

// Audit label: http_set_clock_color_at_4200f0c0; entry: ram:4200f0c0; name: http_set_clock_color_at_4200f0c0

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 http_set_clock_color_at_4200f0c0(undefined4 http_request)

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

  iVar2 = httpd_req_recv(http_request,auStack_50,0x3f);
  if (iVar2 < 1) {
    FUN_ram_4203b382(http_request,8,0);
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
      parse_hex_color_at_42008b58(auStack_5c);
      uVar5 = hex_color_to_rgb565_at_42008aae();
      uVar6 = uVar5;
      uVar1 = overlapping_clock_minute_color_rgb565_at_3fcb7d24;
      if (((uVar3 != 0) && (uVar6 = overlapping_clock_hour_color_rgb565_at_3fcb7d20, uVar1 = uVar5, uVar3 != 1)) &&
         (uVar1 = overlapping_clock_minute_color_rgb565_at_3fcb7d24, uVar3 == 2)) {
        overlapping_clock_detail_color_rgb565_at_3fcb7d28 = uVar5;
      }
      overlapping_clock_minute_color_rgb565_at_3fcb7d24 = uVar1;
      overlapping_clock_hour_color_rgb565_at_3fcb7d20 = uVar6;
      DAT_ram_3fcc39e0 = 1;
      DAT_ram_3fcc39dc = 0x32;
      DAT_ram_3fcc3a26 = 1;
      FUN_ram_4203b114(http_request,"Connection","close");
      FUN_ram_4203b192(http_request,&DAT_ram_3c0c328c,2);
      uVar6 = 0;
    }
    else {
      FUN_ram_4203b382(http_request,3,0);
      uVar6 = 0xffffffff;
    }
  }
  return uVar6;
}

// Audit label: http_get_clock_colors_at_4200f22a; entry: ram:4200f22a; name: http_get_clock_colors_at_4200f22a

undefined4 http_get_clock_colors_at_4200f22a(undefined4 http_request)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined1 auStack_a0 [140];

  uVar1 = rgb565_to_rgb888_at_42008a6a(clock_hour_color_rgb565_at_3fcb7d20);
  uVar2 = rgb565_to_rgb888_at_42008a6a(clock_minute_color_rgb565_at_3fcb7d24);
  uVar3 = rgb565_to_rgb888_at_42008a6a(clock_detail_color_rgb565_at_3fcb7d28);
  (*(code *)&SUB_ram_400006ac)
            (auStack_a0,0x80,"{\"color0\":\"#%06lx\",\"color1\":\"#%06lx\",\"color2\":\"#%06lx\"}",
             uVar1,uVar2,uVar3);
  FUN_ram_4203b178(http_request,"application/json");
  FUN_ram_4203b114(http_request,"Connection","close");
  uVar1 = (*(code *)&SUB_ram_400004a8)(auStack_a0);
  FUN_ram_4203b192(http_request,auStack_a0,uVar1);
  return 0;
}

// Audit label: http_updateCity_at_4200f2c0; entry: ram:4200f2c0; name: http_updateCity_at_4200f2c0

undefined4 http_updateCity_at_4200f2c0(undefined4 http_request)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 uStack_124;
  undefined1 auStack_120 [260];

  uStack_124 = 0x8cbcef;
  iVar1 = httpd_req_recv(http_request,auStack_120,0xff);
  if (iVar1 < 1) {
    FUN_ram_4203b382(http_request,8,0);
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
    (*(code *)&SUB_ram_40000488)(&city_name_at_3fcb7c77,0,0x41);
    (*(code *)&SUB_ram_4000049c)(&city_name_at_3fcb7c77,iVar2,iVar1 - iVar2);
    if (iVar4 == 0) {
      iVar4 = iVar3 + 1;
    }
    else {
      iVar4 = iVar4 + 3;
    }
    iVar1 = (*(code *)&SUB_ram_400004ac)(iVar4,&DAT_ram_3c0c36f4);
    (*(code *)&SUB_ram_40000488)(&country_code_at_3fcb7c63,0,0x14);
    (*(code *)&SUB_ram_4000049c)(&country_code_at_3fcb7c63,iVar4,iVar1 - iVar4);
    DAT_ram_3fcc39e0 = 1;
    DAT_ram_3fcc39dc = 0x32;
    DAT_ram_3fcc39f3 = 1;
    DAT_ram_3fcc39d7 = 0;
    DAT_ram_3fcc39e9 = 0;
    DAT_ram_3fcc3ab9 = 0;
    DAT_ram_3fcc3ab8 = 0;
    FUN_ram_4203b114(http_request,"Connection","close");
    FUN_ram_4203b192(http_request,&DAT_ram_3c0c328c,2);
    uVar5 = 0;
  }
  return uVar5;
}

// Audit label: http_scan_at_4200f440; entry: ram:4200f440; name: http_scan_at_4200f440

undefined4 http_scan_at_4200f440(undefined4 http_request)

{
  int iVar1;
  undefined1 *puVar2;
  int iVar3;
  undefined4 uVar4;
  undefined1 auStack_60 [72];

  scan_wifi_access_points_at_4200c9e0();
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
  FUN_ram_4203b178(http_request,"application/json");
  FUN_ram_4203b114(http_request,"Connection","close");
  uVar4 = (*(code *)&SUB_ram_400004a8)(puVar2);
  FUN_ram_4203b192(http_request,puVar2,uVar4);
  FUN_ram_4038e4da(puVar2);
  return 0;
}

// Audit label: http_configure_at_4200f57e; entry: ram:4200f57e; name: http_configure_at_4200f57e

undefined4 http_configure_at_4200f57e(int http_request)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  undefined1 auStack_120 [268];

  if (*(uint *)(http_request + 0x20c) < 0x41) {
    iVar1 = httpd_req_recv(http_request,auStack_120,0xff);
    if (iVar1 < 1) {
      FUN_ram_4203b382(http_request,8,0);
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
      (*(code *)&SUB_ram_40000488)(&wifi_ssid_at_3fcb7ba0,0,0x41);
      (*(code *)&SUB_ram_40000498)(&wifi_ssid_at_3fcb7ba0,&DAT_ram_3fcbff2c);
      (*(code *)&SUB_ram_40000488)(&wifi_password_at_3fcb7be1,0,0x41);
      (*(code *)&SUB_ram_40000498)(&wifi_password_at_3fcb7be1,&DAT_ram_3fcbfeec);
      DAT_ram_3fcb7cfc = 1;
      save_settings_sector_at_42008a00();
      FUN_ram_4203b114(http_request,"Connection","close");
      FUN_ram_4203b192(http_request,&DAT_ram_3c0c328c,2);
      DAT_ram_3fcc39e4 = 10;
      DAT_ram_3fcc39e8 = 1;
      uVar4 = 0;
    }
  }
  else {
    FUN_ram_4203b382(http_request,9,0);
    uVar4 = 0xffffffff;
  }
  return uVar4;
}

// Audit label: http_SetNightStartTime_at_4200f8a8; entry: ram:4200f8a8; name: http_SetNightStartTime_at_4200f8a8

undefined4 http_SetNightStartTime_at_4200f8a8(int http_request)

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

  if (*(uint *)(http_request + 0x20c) < 0x41) {
    iVar1 = httpd_req_recv(http_request,auStack_24,0x14);
    if (iVar1 < 1) {
      FUN_ram_4203b382(http_request,8,0);
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
      parse_night_start_hour_at_4200f85c(&uStack_38);
      FUN_ram_4203b114(http_request,"Connection","close");
      FUN_ram_4203b192(http_request,&DAT_ram_3c0c328c,2);
      uVar3 = 0;
    }
  }
  else {
    FUN_ram_4203b382(http_request,9,0);
    uVar3 = 0xffffffff;
  }
  return uVar3;
}

// Audit label: http_SetNightStopTime_at_4200f9be; entry: ram:4200f9be; name: http_SetNightStopTime_at_4200f9be

undefined4 http_SetNightStopTime_at_4200f9be(int http_request)

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

  if (*(uint *)(http_request + 0x20c) < 0x41) {
    iVar1 = httpd_req_recv(http_request,auStack_24,0x14);
    if (iVar1 < 1) {
      FUN_ram_4203b382(http_request,8,0);
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
      parse_night_stop_hour_at_4200f972(&uStack_38);
      FUN_ram_4203b114(http_request,"Connection","close");
      FUN_ram_4203b192(http_request,&DAT_ram_3c0c328c,2);
      uVar3 = 0;
    }
  }
  else {
    FUN_ram_4203b382(http_request,9,0);
    uVar3 = 0xffffffff;
  }
  return uVar3;
}
