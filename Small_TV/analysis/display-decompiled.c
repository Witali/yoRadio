// Ghidra 12.0.4 C-like output from the verified Small_TV factory dump.
// ESP-IDF 5.5.4 API types supplied during analysis; whitespace normalized.
// Not recovered original source and not a buildable firmware target.

// Entry: 0x42008bd2; end: ram:42008c4b

void Set_Backlight_Duty(uint arg0)

{
  int iVar1;

  iVar1 = ledc_set_duty(0,0,(arg0 * 0x1fff) / 1000);
  if (iVar1 != 0) {
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(iVar1,"./main/hello_world_main.c",0x2a0,"Set_Backlight_Duty",
                     "ledc_set_duty(LEDC_MODE, LEDC_CHANNEL, Light_Duty)");
  }
  iVar1 = ledc_update_duty(0,0);
  if (iVar1 == 0) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  FUN_ram_4038726a(iVar1,"./main/hello_world_main.c",0x2a2,"Set_Backlight_Duty",
                   "ledc_update_duty(LEDC_MODE, LEDC_CHANNEL)");
}



// Entry: 0x42008d62; end: ram:42008e07

void Backlight_pwm_init(void)

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
    FUN_ram_4038726a(iVar1,"./main/hello_world_main.c",0x2ec,"Backlight_pwm_init",
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
    Set_Backlight_Duty(backlight_level_per_mille);
    return;
  }
                    /* WARNING: Subroutine does not return */
  FUN_ram_4038726a(iVar1,"./main/hello_world_main.c",0x2f8,"Backlight_pwm_init",
                   "ledc_channel_config(&ledc_channel)");
}



// Entry: 0x4200917c; end: ram:42009191

void st7789_spi_pre_transfer_callback(spi_transaction_t *arg0)

{
  gpio_set_level(5,(uint)arg0->user);
  return;
}



// Entry: 0x42009192; end: ram:420091b1

void st7789_delay_ms(uint arg0)

{
  vTaskDelay(arg0 / 10);
  return;
}



// Entry: 0x420091b2; end: ram:420091e3

void st7789_reset(void)

{
  gpio_set_level(1,0);
  st7789_delay_ms(100);
  gpio_set_level(1,1);
  st7789_delay_ms(100);
  return;
}



// Entry: 0x420091e4; end: ram:42009259

void st7789_write_cmd(uchar arg0)

{
  int iVar1;
  uchar auStack_41 [9];
  spi_transaction_t sStack_38;

  sStack_38.flags = 0;
  sStack_38.cmd = 0;
  sStack_38.padding[0] = '\0';
  sStack_38.padding[1] = '\0';
  sStack_38.addr._0_4_ = 0;
  sStack_38.addr._4_4_ = 0;
  sStack_38.rxlength = 0;
  sStack_38.override_freq_hz = 0;
  sStack_38.user = (void *)0x0;
  sStack_38.rx_buffer = (void *)0x0;
  sStack_38.length = 8;
  sStack_38.tx_buffer = auStack_41;
  auStack_41[0] = arg0;
  iVar1 = spi_device_polling_transmit(display_spi,&sStack_38);
  if (iVar1 == 0) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  FUN_ram_4038e2f0("spi_oled.c",0x70,"st7789_write_cmd","ret == ESP_OK");
}



// Entry: 0x4200925a; end: ram:420092cf

void st7789_write_data(void *arg0,int arg1)

{
  int iVar1;
  spi_transaction_t sStack_38;

  if (arg1 != 0) {
    sStack_38.flags = 0;
    sStack_38.cmd = 0;
    sStack_38.padding[0] = '\0';
    sStack_38.padding[1] = '\0';
    sStack_38.addr._0_4_ = 0;
    sStack_38.addr._4_4_ = 0;
    sStack_38.rxlength = 0;
    sStack_38.override_freq_hz = 0;
    sStack_38.rx_buffer = (void *)0x0;
    sStack_38.length = arg1 << 3;
    sStack_38.user = (void *)0x1;
    sStack_38.tx_buffer = arg0;
    iVar1 = spi_device_polling_transmit(display_spi,&sStack_38);
    if (iVar1 != 0) {
                    /* WARNING: Subroutine does not return */
      FUN_ram_4038e2f0("spi_oled.c",0x7f,"st7789_write_data","ret == ESP_OK");
    }
  }
  return;
}



// Entry: 0x420092d0; end: ram:42009349

void st7789_set_window(uint arg0,uint arg1,uint arg2,uint arg3)

{
  undefined1 uStack_28;
  undefined1 uStack_27;
  undefined1 uStack_26;
  undefined1 uStack_25;
  undefined1 uStack_24;
  undefined1 uStack_23;
  undefined1 uStack_22;
  undefined1 uStack_21;

  st7789_write_cmd('*');
  uStack_24 = (undefined1)(arg0 >> 8);
  uStack_23 = (undefined1)arg0;
  uStack_22 = (undefined1)(arg2 >> 8);
  uStack_21 = (undefined1)arg2;
  st7789_write_data(&uStack_24,4);
  st7789_write_cmd('+');
  uStack_28 = (undefined1)(arg1 >> 8);
  uStack_27 = (undefined1)arg1;
  uStack_26 = (undefined1)(arg3 >> 8);
  uStack_25 = (undefined1)arg3;
  st7789_write_data(&uStack_28,4);
  st7789_write_cmd(',');
  return;
}



// Entry: 0x4200934a; end: ram:4200950d

void st7789_init(void)

{
  int iVar1;
  spi_device_interface_config_t local_90;
  spi_bus_config_t sStack_60;
  gpio_config_t gStack_28;

  gStack_28.intr_type = 0;
  gStack_28.mode = 2;
  gStack_28.pin_bit_mask._0_4_ = 0x22;
  gStack_28.pin_bit_mask._4_4_ = 0;
  gStack_28.pull_down_en = 0;
  gStack_28.pull_up_en = 1;
  gpio_config(&gStack_28);
  sStack_60.data4_io_num = 0;
  sStack_60.data5_io_num = 0;
  sStack_60.data6_io_num = 0;
  sStack_60.data7_io_num = 0;
  sStack_60.data_io_default_level = '\0';
  sStack_60.padding[0] = '\0';
  sStack_60.padding[1] = '\0';
  sStack_60.padding[2] = '\0';
  sStack_60.flags = 0;
  sStack_60.isr_cpu_id = 0;
  sStack_60.intr_flags = 0;
  sStack_60.mosi_io_num = 6;
  sStack_60.miso_io_num = -1;
  sStack_60.sclk_io_num = 4;
  sStack_60.quadwp_io_num = -1;
  sStack_60.quadhd_io_num = -1;
  sStack_60.max_transfer_sz = 0x9600;
  iVar1 = spi_bus_initialize(1,&sStack_60,3);
  if (iVar1 != 0) {
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(iVar1,"./main/spi_oled.c",0xae,"st7789_init",&DAT_ram_3c0c2b1c);
  }
  local_90.clock_source = 0;
  local_90.duty_cycle_pos = 0;
  local_90.cs_ena_pretrans = 0;
  local_90.cs_ena_posttrans = '\0';
  local_90.padding[0] = '\0';
  local_90.padding[1] = '\0';
  local_90.padding[2] = '\0';
  local_90.input_delay_ns = 0;
  local_90.sample_point = 0;
  local_90.flags = 0;
  local_90.post_cb = (void *)0x0;
  local_90.command_bits = '\0';
  local_90.address_bits = '\0';
  local_90.dummy_bits = '\0';
  local_90.mode = '\x03';
  local_90.clock_speed_hz = 40000000;
  local_90.spics_io_num = -1;
  local_90.queue_size = 7;
  local_90.pre_cb = st7789_spi_pre_transfer_callback;
  iVar1 = spi_bus_add_device(1,&local_90,(void **)&display_spi);
  if (iVar1 == 0) {
    st7789_reset();
    st7789_delay_ms(0x96);
    st7789_write_cmd('\x11');
    st7789_delay_ms(0x96);
    st7789_write_cmd(':');
    display_init_data[0] = 'U';
    st7789_write_data(display_init_data,1);
    st7789_write_cmd('6');
    display_init_data[0] = '\0';
    st7789_write_data(display_init_data,1);
    st7789_write_cmd('*');
    display_init_data[0] = '\0';
    display_init_data[1] = '\0';
    display_init_data[2] = '\0';
    display_init_data[3] = 0xf0;
    st7789_write_data(display_init_data,4);
    st7789_write_cmd('+');
    display_init_data[0] = '\0';
    display_init_data[1] = '\0';
    display_init_data[2] = '\0';
    display_init_data[3] = 0xf0;
    st7789_write_data(display_init_data,4);
    st7789_write_cmd('!');
    st7789_delay_ms(0x14);
    st7789_write_cmd('\x13');
    st7789_delay_ms(0x14);
    st7789_write_cmd(')');
    return;
  }
                    /* WARNING: Subroutine does not return */
  FUN_ram_4038726a(iVar1,"./main/spi_oled.c",0xb9,"st7789_init",&DAT_ram_3c0c2b1c);
}



// Entry: 0x4200950e; end: ram:42009589

void st7789_blit_rect(uint arg0,uint arg1,uint arg2,uint arg3,void *arg4)

{
  uint uVar1;
  uint uVar2;

  if ((((arg0 < 0xf0) && (arg1 < 0xf0)) && (arg2 < 0xf0)) && (arg3 < 0xf0)) {
    st7789_set_window(arg0,arg1,arg2,arg3);
    uVar1 = ((arg2 - arg0) + 1) * ((arg3 - arg1) + 1);
    for (uVar2 = 0; uVar2 < uVar1 >> 5; uVar2 = uVar2 + 1) {
      st7789_write_data(arg4,0x40);
      arg4 = (void *)((int)arg4 + 0x40);
    }
    uVar1 = uVar1 & 0x1f;
    if (uVar1 != 0) {
      st7789_write_data(arg4,uVar1 << 1);
    }
  }
  return;
}



// Entry: 0x4200958a; end: ram:420095c3

void st7789_draw_pixel(uint arg0,uint arg1,ushort arg2)

{
  undefined1 uStack_14;
  undefined1 uStack_13;

  if ((arg0 < 0xf0) && (arg1 < 0xf0)) {
    st7789_set_window(arg0,arg1,arg0,arg1);
    uStack_14 = (undefined1)(arg2 >> 8);
    uStack_13 = (undefined1)arg2;
    st7789_write_data(&uStack_14,2);
  }
  return;
}



// Entry: 0x42008e56; end: ram:4200917b

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
        FUN_ram_4200d06e();
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
