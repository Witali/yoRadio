/* GHIDRA REFERENCE PSEUDOCODE, NOT COMPILED.
 * Retains addresses, unresolved SDK calls and decompiler type/overlap artifacts.
 * Per-function reconstruction targets: symbol-map.json native_targets.
 */

// Audit label: application_review; entry: ram:42008bd2; name: set_backlight_duty_at_42008bd2

void set_backlight_duty_at_42008bd2(uint duty_per_mille)

{
  int ledc_result;

  ledc_result = ledc_set_duty(0,0,(duty_per_mille * 0x1fff) / 1000);
  if (ledc_result != 0) {
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(ledc_result,"./main/hello_world_main.c",0x2a0,"set_backlight_duty_at_42008bd2",
                     "ledc_set_duty(LEDC_MODE, LEDC_CHANNEL, Light_Duty)");
  }
  ledc_result = ledc_update_duty(0,0);
  if (ledc_result == 0) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  FUN_ram_4038726a(ledc_result,"./main/hello_world_main.c",0x2a2,"set_backlight_duty_at_42008bd2",
                   "ledc_update_duty(LEDC_MODE, LEDC_CHANNEL)");
}

// Audit label: application_review; entry: ram:42008c4c; name: update_day_night_backlight_at_42008c4c

void update_day_night_backlight_at_42008c4c(void)

{
  uint uVar1;

  if (night_mode_flag_at_3fcb7d2c == 1) {
    uVar1 = ((uint)local_hour_at_3fcbffce * 0x3c0000 >> 0x10) + (uint)local_minute_at_3fcbffcf;
    if ((uVar1 < (uint)(night_start_hour_at_3fcb7d30 * 0x3c0000) >> 0x10) &&
       ((0x2d0 < uVar1 || ((uint)(night_stop_hour_at_3fcb7d34 * 0x3c0000) >> 0x10 < uVar1)))) {
      if (day_backlight_per_mille_at_3fcb7d1c != backlight_level_per_mille) {
        set_backlight_duty_at_42008bd2(day_backlight_per_mille_at_3fcb7d1c);
        backlight_level_per_mille = day_backlight_per_mille_at_3fcb7d1c;
      }
    }
    else if (night_backlight_per_mille_at_3fcb7d38 != backlight_level_per_mille) {
      set_backlight_duty_at_42008bd2(night_backlight_per_mille_at_3fcb7d38);
      backlight_level_per_mille = night_backlight_per_mille_at_3fcb7d38;
    }
  }
  else if (day_backlight_per_mille_at_3fcb7d1c != backlight_level_per_mille) {
    set_backlight_duty_at_42008bd2(day_backlight_per_mille_at_3fcb7d1c);
    backlight_level_per_mille = day_backlight_per_mille_at_3fcb7d1c;
  }
  return;
}

// Audit label: application_review; entry: ram:42008d62; name: initialize_backlight_pwm_at_42008d62

void initialize_backlight_pwm_at_42008d62(void)

{
  int iVar1;
  ledc_channel_config_t lStack_4c;
  ledc_timer_config_t lStack_28;

  backlight_level_per_mille = 100;
  lStack_28.speed_mode = 0;
  lStack_28.timer_num = 0;
  lStack_28.clk_cfg = 0;
  lStack_28.deconfigure = '\0';
  lStack_28.padding[0] = '\0';
  lStack_28.padding[1] = '\0';
  lStack_28.padding[2] = '\0';
  lStack_28.duty_resolution = 0xd;
  lStack_28.freq_hz = 1000;
  iVar1 = ledc_timer_config(&lStack_28);
  if (iVar1 != 0) {
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(iVar1,"./main/hello_world_main.c",0x2ec,"initialize_backlight_pwm_at_42008d62",
                     "ledc_timer_config(&ledc_timer)");
  }
  lStack_4c.speed_mode = 0;
  lStack_4c.channel = 0;
  lStack_4c.intr_type = 0;
  lStack_4c.timer_sel = 0;
  lStack_4c.duty = 0;
  lStack_4c.hpoint = 0;
  lStack_4c.sleep_mode = 0;
  lStack_4c.flags = 0;
  lStack_4c.gpio_num = 0x12;
  iVar1 = ledc_channel_config(&lStack_4c);
  if (iVar1 == 0) {
    set_backlight_duty_at_42008bd2(backlight_level_per_mille);
    return;
  }
                    /* WARNING: Subroutine does not return */
  FUN_ram_4038726a(iVar1,"./main/hello_world_main.c",0x2f8,"initialize_backlight_pwm_at_42008d62",
                   "ledc_channel_config(&ledc_channel)");
}
