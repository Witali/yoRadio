/* GHIDRA REFERENCE PSEUDOCODE, NOT COMPILED.
 * Retains addresses, unresolved SDK calls and decompiler type/overlap artifacts.
 * Executable reconstruction: app/app_main.c.
 */

// Audit label: application_review; entry: ram:4200826a; name: system_timer_alarm_callback_at_4200826a

undefined4 system_timer_alarm_callback_at_4200826a(void)

{
  byte bVar1;

  if (DAT_ram_3fcc39eb != '\0') {
    if (0xb4 < (byte)(DAT_ram_3fcc3a56 + 1U)) {
      DAT_ram_3fcc39eb = '\0';
    }
    DAT_ram_3fcc3a56 = DAT_ram_3fcc3a56 + '\x01';
    draw_startup_connection_status_at_4200c1c8();
  }
  bVar1 = DAT_ram_3fcc39cc + 1;
  DAT_ram_3fcc39cc = DAT_ram_3fcc39cc + '\x01';
  if (10 < bVar1) {
    DAT_ram_3fcc39cc = '\0';
    DAT_ram_3fcc39f6 = 1;
    bVar1 = DAT_ram_3fcc39cb + 1;
    DAT_ram_3fcc39cb = DAT_ram_3fcc39cb + '\x01';
    if (2 < bVar1) {
      DAT_ram_3fcc39cb = '\0';
      DAT_ram_3fcc39f7 = 1;
    }
    DAT_ram_3fcc39ca = DAT_ram_3fcc39ca + 1;
    if (photo_interval_seconds_at_3fcb7d3c <= DAT_ram_3fcc39ca) {
      DAT_ram_3fcc39ca = 0;
      DAT_ram_3fcc39f8 = 1;
    }
    bVar1 = DAT_ram_3fcc39c9 + 1;
    DAT_ram_3fcc39c9 = DAT_ram_3fcc39c9 + '\x01';
    if (0x3b < bVar1) {
      DAT_ram_3fcc39c9 = '\0';
      DAT_ram_3fcc39f5 = 1;
      DAT_ram_3fcc39f0 = 1;
    }
    bVar1 = DAT_ram_3fcc39c8 + 1;
    DAT_ram_3fcc39c8 = DAT_ram_3fcc39c8 + '\x01';
    if (0xb4 < bVar1) {
      DAT_ram_3fcc39c8 = '\0';
      DAT_ram_3fcc39f4 = 1;
    }
    DAT_ram_3fcc39c4 = DAT_ram_3fcc39c4 + 1;
    if (0x708 < DAT_ram_3fcc39c4) {
      DAT_ram_3fcc39c4 = 0;
      DAT_ram_3fcc39f3 = 1;
    }
  }
  return 0;
}

// Audit label: application_review; entry: ram:420083b6; name: initialize_system_timer_at_420083b6

void initialize_system_timer_at_420083b6(void)

{
  int iVar1;
  code *pcStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_24;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;

  local_year_at_3fcbffc8 = 0x7e9;
  local_month_at_3fcbffcc = 9;
  local_day_at_3fcbffcd = 0x13;
  local_hour_at_3fcbffce = 0x11;
  local_minute_at_3fcbffcf = 4;
  local_second_at_3fcbffd0 = 0x28;
  local_weekday_at_3fcbffd1 = 5;
  DAT_ram_3fcc39eb = 1;
  DAT_ram_3fcc3a56 = 0;
  DAT_ram_3fcc39ea = 1;
  uStack_18 = 0;
  uStack_14 = 0;
  uStack_24 = 5;
  uStack_20 = 1;
  uStack_1c = 1000000;
  iVar1 = FUN_ram_420ae234(&uStack_24,&DAT_ram_3fcc39d0);
  if (iVar1 != 0) {
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(iVar1,"./main/hello_world_main.c",0xe1,"System_timer_init",
                     "gptimer_new_timer(&timer_config, &gptimer)");
  }
  uStack_40 = DAT_ram_3c0d6290;
  uStack_3c = DAT_ram_3c0d6294;
  uStack_38 = DAT_ram_3c0d6298;
  uStack_34 = DAT_ram_3c0d629c;
  uStack_30 = DAT_ram_3c0d62a0;
  uStack_2c = DAT_ram_3c0d62a4;
  iVar1 = FUN_ram_420ae6b0(DAT_ram_3fcc39d0,&uStack_40);
  if (iVar1 != 0) {
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(iVar1,"./main/hello_world_main.c",0xe8,"System_timer_init",
                     "gptimer_set_alarm_action(gptimer, &alarm_config)");
  }
  pcStack_44 = system_timer_alarm_callback_at_4200826a;
  iVar1 = FUN_ram_420ae534(DAT_ram_3fcc39d0,&pcStack_44,0);
  if (iVar1 != 0) {
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(iVar1,"./main/hello_world_main.c",0xee,"System_timer_init",
                     "gptimer_register_event_callbacks(gptimer, &cbs, NULL)");
  }
  iVar1 = FUN_ram_420ae88a(DAT_ram_3fcc39d0);
  if (iVar1 == 0) {
    iVar1 = FUN_ram_420ae9bc(DAT_ram_3fcc39d0);
    if (iVar1 == 0) {
      return;
    }
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(iVar1,"./main/hello_world_main.c",0xf2,"System_timer_init",
                     "gptimer_start(gptimer)");
  }
                    /* WARNING: Subroutine does not return */
  FUN_ram_4038726a(iVar1,"./main/hello_world_main.c",0xf0,"System_timer_init",
                   "gptimer_enable(gptimer)");
}

// Audit label: application_review; entry: ram:42008e08; name: initialize_selected_clock_theme_at_42008e08

void initialize_selected_clock_theme_at_42008e08(void)

{
  clear_display_at_42009a0a(0);
  if (selected_clock_theme_at_3fcb7d04 == 0) {
    initialize_classic_clock_at_4200aebe();
  }
  else if (selected_clock_theme_at_3fcb7d04 == 1) {
    initialize_simple_clock_at_4200bd26();
  }
  else if (selected_clock_theme_at_3fcb7d04 == 2) {
    initialize_photo_slideshow_at_4200bb20();
  }
  else if (selected_clock_theme_at_3fcb7d04 == 3) {
    initialize_dial_clock_at_4200a156();
  }
  set_backlight_duty_at_42008bd2(0);
  return;
}

// Audit label: application_review; entry: ram:42008e56; name: application_main_at_42008e56

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void application_main_at_42008e56(void)

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
      FUN_ram_4038726a(iVar1,"./main/hello_world_main.c",0x33e,"application_main_at_42008e56","nvs_flash_erase()");
    }
    iVar1 = FUN_ram_4203f586();
  }
  if (iVar1 != 0) {
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(iVar1,"./main/hello_world_main.c",0x341,"application_main_at_42008e56",&DAT_ram_3c0c2ae4);
  }
  _DAT_ram_3fcb7b84 = DAT_ram_3c0c2ae8;
  DAT_ram_3fcb7b88 = DAT_ram_3c0c2aec;
  DAT_ram_3fcb7b8c = DAT_ram_3c0c2af0;
  DAT_ram_3fcb7b90 = DAT_ram_3c0c2af4;
  initialize_display_at_42009a24();
  load_settings_and_defaults_at_42008552();
  initialize_system_timer_at_420083b6();
  clear_display_at_42009a0a(0);
  initialize_backlight_pwm_at_42008d62();
  DAT_ram_3fcc39e9 = '\0';
  DAT_ram_3fcc39d7 = '\0';
  DAT_ram_3fcc39d6 = '\0';
  if (DAT_ram_3fcb7cfc == 2) {
    DAT_ram_3fcc39eb = '\0';
    DAT_ram_3fcc3a54 = 0;
    wifi_connection_state_at_3fcc3a74 = '\0';
    DAT_ram_3fcc39ea = '\x01';
  }
  else {
    draw_initial_clock_screen_at_4200c100();
  }
  do {
    if (DAT_ram_3fcc39eb == '\0') {
      if (DAT_ram_3fcc39ea == '\0') {
        if ((wifi_connection_state_at_3fcc3a74 == '\x02') && (DAT_ram_3fcc39d7 == '\0')) {
          if (DAT_ram_3fcc39d6 == '\0') {
            DAT_ram_3fcc39d6 = '\x1e';
            fetch_current_weather_at_42010864();
          }
          else {
            DAT_ram_3fcc39d6 = DAT_ram_3fcc39d6 + -1;
          }
        }
        if (DAT_ram_3fcc39e9 == '\0') {
          DAT_ram_3fcc39e9 = '\x01';
          initialize_selected_clock_theme_at_42008e08();
        }
        else if (selected_clock_theme_at_3fcb7d04 == 0) {
          render_classic_clock_at_4200b738();
        }
        else if (selected_clock_theme_at_3fcb7d04 == 1) {
          render_simple_clock_at_4200bd8c();
        }
        else if (selected_clock_theme_at_3fcb7d04 == 2) {
          advance_photo_slideshow_at_4200bc36();
        }
        else if (selected_clock_theme_at_3fcb7d04 == 3) {
          render_dial_clock_at_4200a5b0();
        }
        if (DAT_ram_3fcc39f3 != '\0') {
          DAT_ram_3fcc39f3 = '\0';
          fetch_current_weather_at_42010864();
        }
        update_local_time_at_42010b70();
        if (DAT_ram_3fcc39e0 != '\0') {
          if (DAT_ram_3fcc39dc == 0) {
            DAT_ram_3fcc39e0 = '\0';
            save_settings_sector_at_42008a00();
          }
          else {
            DAT_ram_3fcc39dc = DAT_ram_3fcc39dc + -1;
          }
        }
        if (local_second_at_3fcbffd0 != DAT_ram_3fcc39f1) {
          DAT_ram_3fcc39f1 = local_second_at_3fcbffd0;
          if (local_second_at_3fcbffd0 == '\0') {
            DAT_ram_3fcc39f2 = '\x01';
          }
        }
        if (DAT_ram_3fcc39f2 != '\0') {
          DAT_ram_3fcc39f2 = '\0';
          update_day_night_backlight_at_42008c4c();
        }
      }
      else if (wifi_connection_state_at_3fcc3a74 != '\x05') {
        initialize_wifi_softap_at_4200d06e();
        draw_wifi_setup_instructions_at_42010c4e();
      }
    }
    else if (wifi_connection_state_at_3fcc3a74 == '\x02') {
      if (DAT_ram_3fcc39d7 == '\0') {
        if (DAT_ram_3fcc39d6 == '\0') {
          DAT_ram_3fcc39d6 = '\x1e';
          fetch_current_weather_at_42010864();
        }
        else {
          DAT_ram_3fcc39d6 = DAT_ram_3fcc39d6 + -1;
        }
      }
      if (DAT_ram_3fcc39d5 == '\0') {
        if (DAT_ram_3fcc39d4 == '\0') {
          DAT_ram_3fcc39d4 = '\x1e';
          update_local_time_at_42010b70();
        }
        else {
          DAT_ram_3fcc39d4 = DAT_ram_3fcc39d4 + -1;
        }
      }
    }
    else {
      update_wifi_connection_mode_at_4200ce40();
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
