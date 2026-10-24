/* GHIDRA REFERENCE PSEUDOCODE, NOT COMPILED.
 * Retains addresses, unresolved SDK calls and decompiler type/overlap artifacts.
 * Per-function reconstruction targets: symbol-map.json native_targets.
 */

// Audit label: application_review; entry: ram:4200d394; name: send_http_json_number_at_4200d394

void send_http_json_number_at_4200d394(undefined4 param_1,undefined4 param_2,int param_3)

{
  undefined *puVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;

  iVar2 = (*(code *)&SUB_ram_400004ac)(param_1,"{{STATE}}");
  if (iVar2 != 0) {
    if (param_3 == 0) {
      puVar1 = &DAT_ram_3c0c31f4;
    }
    else {
      puVar1 = &DAT_ram_3c0c31f0;
    }
    uVar3 = (*(code *)&SUB_ram_400004a8)(puVar1);
    (*(code *)&SUB_ram_4000048c)(iVar2,puVar1,uVar3);
    iVar4 = (*(code *)&SUB_ram_400004a8)(puVar1);
    (*(code *)&SUB_ram_40000488)(iVar4 + iVar2,0x20,9 - iVar4);
  }
  return;
}

// Audit label: application_review; entry: ram:4200d4be; name: http_captive_redirect_at_4200d4be

undefined4 http_captive_redirect_at_4200d4be(undefined4 param_1)

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
    uVar2 = http_root_at_4200d404(param_1);
  }
  return uVar2;
}

// Audit label: application_review; entry: ram:4200daaa; name: find_multipart_bytes_at_4200daaa

int find_multipart_bytes_at_4200daaa(int param_1,uint param_2,undefined4 param_3)

{
  uint uVar1;
  uint uVar2;
  int iVar3;

  uVar2 = (*(code *)&SUB_ram_400004a8)(param_3);
  if ((uVar2 != 0) && (uVar2 <= param_2)) {
    for (uVar1 = 0; uVar1 <= param_2 - uVar2; uVar1 = uVar1 + 1) {
      iVar3 = (*(code *)&SUB_ram_40000494)(param_1 + uVar1,param_3,uVar2);
      if (iVar3 == 0) {
        return param_1 + uVar1;
      }
    }
  }
  return 0;
}

// Audit label: application_review; entry: ram:4200db12; name: parse_multipart_upload_body_at_4200db12

void parse_multipart_upload_body_at_4200db12(int param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  uint uVar4;

  if ((((param_1 != 0) && (param_2 != 0)) && (param_3 != 0)) && (param_4 != 0)) {
    iVar1 = find_multipart_bytes_at_4200daaa(param_1,param_2,&DAT_ram_3c0c0838);
    if (iVar1 == 0) {
      uVar3 = FUN_ram_4038d3b4();
      FUN_ram_4038d2a2(1,&DAT_ram_3c0c3290,"E (%lu) %s: not find 0D 0A 0D 0A\n\n",uVar3,
                       &DAT_ram_3c0c3290);
    }
    else {
      uVar4 = iVar1 + 4;
      uVar2 = find_multipart_bytes_at_4200daaa(uVar4,param_2 - (uVar4 - param_1),"---");
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

// Audit label: application_review; entry: ram:4200eefe; name: parse_json_switch_value_at_4200eefe

bool parse_json_switch_value_at_4200eefe(undefined4 json_text,undefined4 field_name)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  char *pcVar4;
  undefined1 auStack_30 [36];

  (*(code *)&SUB_ram_400006ac)(auStack_30,0x20,"\"%s\":",field_name);
  iVar2 = (*(code *)&SUB_ram_400004ac)(json_text,auStack_30);
  if (iVar2 == 0) {
    bVar1 = true;
  }
  else {
    iVar3 = (*(code *)&SUB_ram_400004a8)(auStack_30);
    for (pcVar4 = (char *)(iVar3 + iVar2); *pcVar4 == ' '; pcVar4 = pcVar4 + 1) {
    }
    bVar1 = *pcVar4 == '1';
  }
  return bVar1;
}

// Audit label: application_review; entry: ram:4200f764; name: parse_photo_interval_at_4200f764

void parse_photo_interval_at_4200f764(int interval_text)

{
  uint uVar1;

  if ((interval_text != 0) && (uVar1 = (*(code *)&SUB_ram_40000580)(), uVar1 - 3 < 0x3a)) {
    photo_interval_seconds_at_3fcb7d3c = uVar1 & 0xff;
    DAT_ram_3fcc39e0 = 1;
    DAT_ram_3fcc39dc = 0x32;
  }
  return;
}

// Audit label: application_review; entry: ram:4200f85c; name: parse_night_start_hour_at_4200f85c

void parse_night_start_hour_at_4200f85c(int start_hour_text)

{
  uint uVar1;

  if ((start_hour_text != 0) && (uVar1 = (*(code *)&SUB_ram_40000580)(), uVar1 - 0x12 < 6)) {
    night_start_hour_at_3fcb7d30 = uVar1 & 0xff;
    DAT_ram_3fcc39f2 = 1;
    DAT_ram_3fcc39e0 = 1;
    DAT_ram_3fcc39dc = 0x32;
  }
  return;
}

// Audit label: application_review; entry: ram:4200f972; name: parse_night_stop_hour_at_4200f972

void parse_night_stop_hour_at_4200f972(int stop_hour_text)

{
  uint uVar1;

  if ((stop_hour_text != 0) && (uVar1 = (*(code *)&SUB_ram_40000580)(), uVar1 - 5 < 8)) {
    night_stop_hour_at_3fcb7d34 = uVar1 & 0xff;
    DAT_ram_3fcc39f2 = 1;
    DAT_ram_3fcc39e0 = 1;
    DAT_ram_3fcc39dc = 0x32;
  }
  return;
}

// Audit label: application_review; entry: ram:4200fa88; name: start_http_server_at_4200fa88

undefined4 start_http_server_at_4200fa88(void)

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
    FUN_ram_4203b640(uStack_74,6,http_captive_redirect_at_4200d4be);
  }
  else {
    uStack_74 = 0;
  }
  return uStack_74;
}
