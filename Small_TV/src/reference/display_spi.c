/* GHIDRA REFERENCE PSEUDOCODE, NOT COMPILED.
 * Retains addresses, unresolved SDK calls and decompiler type/overlap artifacts.
 * Per-function reconstruction targets: symbol-map.json native_targets.
 */

// Audit label: application_review; entry: ram:4200917c; name: st7789_spi_dc_callback_at_4200917c

void st7789_spi_dc_callback_at_4200917c(spi_transaction_t *transaction)

{
  gpio_set_level(5,(uint)transaction->user);
  return;
}

// Audit label: application_review; entry: ram:42009192; name: st7789_delay_ms_at_42009192

void st7789_delay_ms_at_42009192(uint milliseconds)

{
  vTaskDelay(milliseconds / 10);
  return;
}

// Audit label: application_review; entry: ram:420091b2; name: st7789_reset_at_420091b2

void st7789_reset_at_420091b2(void)

{
  gpio_set_level(1,0);
  st7789_delay_ms_at_42009192(100);
  gpio_set_level(1,1);
  st7789_delay_ms_at_42009192(100);
  return;
}

// Audit label: application_review; entry: ram:420091e4; name: st7789_write_command_at_420091e4

void st7789_write_command_at_420091e4(uchar command)

{
  int spi_result;
  uchar command_storage [9];
  spi_transaction_t transaction;

  transaction.flags = 0;
  transaction.cmd = 0;
  transaction.padding[0] = '\0';
  transaction.padding[1] = '\0';
  transaction.addr._0_4_ = 0;
  transaction.addr._4_4_ = 0;
  transaction.rxlength = 0;
  transaction.override_freq_hz = 0;
  transaction.user = (void *)0x0;
  transaction.rx_buffer = (void *)0x0;
  transaction.length = 8;
  transaction.tx_buffer = command_storage;
  command_storage[0] = command;
  spi_result = spi_device_polling_transmit(display_spi,&transaction);
  if (spi_result == 0) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  FUN_ram_4038e2f0("spi_oled.c",0x70,"st7789_write_command_at_420091e4","ret == ESP_OK");
}

// Audit label: application_review; entry: ram:4200925a; name: st7789_write_data_at_4200925a

void st7789_write_data_at_4200925a(void *data,int byte_count)

{
  int spi_result;
  spi_transaction_t transaction;

  if (byte_count != 0) {
    transaction.flags = 0;
    transaction.cmd = 0;
    transaction.padding[0] = '\0';
    transaction.padding[1] = '\0';
    transaction.addr._0_4_ = 0;
    transaction.addr._4_4_ = 0;
    transaction.rxlength = 0;
    transaction.override_freq_hz = 0;
    transaction.rx_buffer = (void *)0x0;
    transaction.length = byte_count << 3;
    transaction.user = (void *)0x1;
    transaction.tx_buffer = data;
    spi_result = spi_device_polling_transmit(display_spi,&transaction);
    if (spi_result != 0) {
                    /* WARNING: Subroutine does not return */
      FUN_ram_4038e2f0("spi_oled.c",0x7f,"st7789_write_data_at_4200925a","ret == ESP_OK");
    }
  }
  return;
}

// Audit label: application_review; entry: ram:420092d0; name: st7789_set_window_at_420092d0

void st7789_set_window_at_420092d0(uint x_start,uint y_start,uint x_end,uint y_end)

{
  undefined1 y_start_high;
  undefined1 y_start_low;
  undefined1 y_end_high;
  undefined1 y_end_low;
  undefined1 x_start_high;
  undefined1 x_start_low;
  undefined1 x_end_high;
  undefined1 x_end_low;

  st7789_write_command_at_420091e4('*');
  x_start_high = (undefined1)(x_start >> 8);
  x_start_low = (undefined1)x_start;
  x_end_high = (undefined1)(x_end >> 8);
  x_end_low = (undefined1)x_end;
  st7789_write_data_at_4200925a(&x_start_high,4);
  st7789_write_command_at_420091e4('+');
  y_start_high = (undefined1)(y_start >> 8);
  y_start_low = (undefined1)y_start;
  y_end_high = (undefined1)(y_end >> 8);
  y_end_low = (undefined1)y_end;
  st7789_write_data_at_4200925a(&y_start_high,4);
  st7789_write_command_at_420091e4(',');
  return;
}

// Audit label: application_review; entry: ram:4200934a; name: st7789_initialize_at_4200934a

void st7789_initialize_at_4200934a(void)

{
  int initialization_result;
  spi_device_interface_config_t spi_device_config;
  spi_bus_config_t spi_bus_config;
  gpio_config_t gpio_config;

  gpio_config.intr_type = 0;
  gpio_config.mode = 2;
  gpio_config.pin_bit_mask._0_4_ = 0x22;
  gpio_config.pin_bit_mask._4_4_ = 0;
  gpio_config.pull_down_en = 0;
  gpio_config.pull_up_en = 1;
  gpio_config(&gpio_config);
  spi_bus_config.data4_io_num = 0;
  spi_bus_config.data5_io_num = 0;
  spi_bus_config.data6_io_num = 0;
  spi_bus_config.data7_io_num = 0;
  spi_bus_config.data_io_default_level = '\0';
  spi_bus_config.padding[0] = '\0';
  spi_bus_config.padding[1] = '\0';
  spi_bus_config.padding[2] = '\0';
  spi_bus_config.flags = 0;
  spi_bus_config.isr_cpu_id = 0;
  spi_bus_config.intr_flags = 0;
  spi_bus_config.mosi_io_num = 6;
  spi_bus_config.miso_io_num = -1;
  spi_bus_config.sclk_io_num = 4;
  spi_bus_config.quadwp_io_num = -1;
  spi_bus_config.quadhd_io_num = -1;
  spi_bus_config.max_transfer_sz = 0x9600;
  initialization_result = spi_bus_initialize(1,&spi_bus_config,3);
  if (initialization_result != 0) {
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(initialization_result,"./main/spi_oled.c",0xae,"st7789_initialize_at_4200934a",&DAT_ram_3c0c2b1c);
  }
  spi_device_config.clock_source = 0;
  spi_device_config.duty_cycle_pos = 0;
  spi_device_config.cs_ena_pretrans = 0;
  spi_device_config.cs_ena_posttrans = '\0';
  spi_device_config.padding[0] = '\0';
  spi_device_config.padding[1] = '\0';
  spi_device_config.padding[2] = '\0';
  spi_device_config.input_delay_ns = 0;
  spi_device_config.sample_point = 0;
  spi_device_config.flags = 0;
  spi_device_config.post_cb = (void *)0x0;
  spi_device_config.command_bits = '\0';
  spi_device_config.address_bits = '\0';
  spi_device_config.dummy_bits = '\0';
  spi_device_config.mode = '\x03';
  spi_device_config.clock_speed_hz = 40000000;
  spi_device_config.spics_io_num = -1;
  spi_device_config.queue_size = 7;
  spi_device_config.pre_cb = st7789_spi_dc_callback_at_4200917c;
  initialization_result = spi_bus_add_device(1,&spi_device_config,(void **)&display_spi);
  if (initialization_result == 0) {
    st7789_reset_at_420091b2();
    st7789_delay_ms_at_42009192(0x96);
    st7789_write_command_at_420091e4('\x11');
    st7789_delay_ms_at_42009192(0x96);
    st7789_write_command_at_420091e4(':');
    display_init_data[0] = 'U';
    st7789_write_data_at_4200925a(display_init_data,1);
    st7789_write_command_at_420091e4('6');
    display_init_data[0] = '\0';
    st7789_write_data_at_4200925a(display_init_data,1);
    st7789_write_command_at_420091e4('*');
    display_init_data[0] = '\0';
    display_init_data[1] = '\0';
    display_init_data[2] = '\0';
    display_init_data[3] = 0xf0;
    st7789_write_data_at_4200925a(display_init_data,4);
    st7789_write_command_at_420091e4('+');
    display_init_data[0] = '\0';
    display_init_data[1] = '\0';
    display_init_data[2] = '\0';
    display_init_data[3] = 0xf0;
    st7789_write_data_at_4200925a(display_init_data,4);
    st7789_write_command_at_420091e4('!');
    st7789_delay_ms_at_42009192(0x14);
    st7789_write_command_at_420091e4('\x13');
    st7789_delay_ms_at_42009192(0x14);
    st7789_write_command_at_420091e4(')');
    return;
  }
                    /* WARNING: Subroutine does not return */
  FUN_ram_4038726a(initialization_result,"./main/spi_oled.c",0xb9,"st7789_initialize_at_4200934a",&DAT_ram_3c0c2b1c);
}

// Audit label: application_review; entry: ram:4200950e; name: st7789_blit_rectangle_at_4200950e

void st7789_blit_rectangle_at_4200950e(uint x_start,uint y_start,uint x_end,uint y_end,void *pixel_data)

{
  uint uVar1;
  uint uVar2;

  if ((((x_start < 0xf0) && (y_start < 0xf0)) && (x_end < 0xf0)) && (y_end < 0xf0)) {
    st7789_set_window_at_420092d0(x_start,y_start,x_end,y_end);
    uVar1 = ((x_end - x_start) + 1) * ((y_end - y_start) + 1);
    for (uVar2 = 0; uVar2 < uVar1 >> 5; uVar2 = uVar2 + 1) {
      st7789_write_data_at_4200925a(pixel_data,0x40);
      pixel_data = (void *)((int)pixel_data + 0x40);
    }
    uVar1 = uVar1 & 0x1f;
    if (uVar1 != 0) {
      st7789_write_data_at_4200925a(pixel_data,uVar1 << 1);
    }
  }
  return;
}

// Audit label: application_review; entry: ram:4200958a; name: st7789_draw_pixel_at_4200958a

void st7789_draw_pixel_at_4200958a(uint x,uint y,ushort color_rgb565)

{
  undefined1 uStack_14;
  undefined1 uStack_13;

  if ((x < 0xf0) && (y < 0xf0)) {
    st7789_set_window_at_420092d0(x,y,x,y);
    uStack_14 = (undefined1)(color_rgb565 >> 8);
    uStack_13 = (undefined1)color_rgb565;
    st7789_write_data_at_4200925a(&uStack_14,2);
  }
  return;
}
