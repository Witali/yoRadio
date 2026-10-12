/* GHIDRA REFERENCE PSEUDOCODE, NOT COMPILED.
 * Retains addresses, unresolved SDK calls and decompiler type/overlap artifacts.
 * Executable reconstruction: app/network/wifi.c + app/network/dns.c.
 */

// Audit label: application_review; entry: ram:4200c578; name: stop_wifi_http_server_at_4200c578

void stop_wifi_http_server_at_4200c578(void)

{
  int iVar1;
  undefined4 uVar2;

  if (wifi_http_server_handle_at_3fcc3a70 != 0) {
    iVar1 = stop_http_server_at_4200fcbe();
    if (iVar1 == 0) {
      wifi_http_server_handle_at_3fcc3a70 = 0;
      uVar2 = FUN_ram_4038d3b4();
      FUN_ram_4038d2a2(1,"wifi station","E (%lu) %s: stop http server success.\n\n",uVar2,
                       "wifi station");
    }
    else {
      uVar2 = FUN_ram_4038d3b4();
      FUN_ram_4038d2a2(1,"wifi station","E (%lu) %s: Failed to stop http server\n\n",uVar2,
                       "wifi station");
    }
  }
  return;
}

// Audit label: application_review; entry: ram:4200c5ec; name: start_wifi_http_server_at_4200c5ec

void start_wifi_http_server_at_4200c5ec(void)

{
  wifi_http_server_handle_at_3fcc3a70 = start_http_server_at_4200fa88();
  return;
}

// Audit label: application_review; entry: ram:4200c602; name: wifi_station_event_handler_at_4200c602

void wifi_station_event_handler_at_4200c602(undefined4 event_context,undefined *event_base,int event_id,int event_data)

{
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;

  if ((PTR_s_WIFI_EVENT_ram_3c0cf320_ram_3c0f1eb8 == event_base) && (event_id == 2)) {
    FUN_ram_4204551e();
  }
  else if ((PTR_s_WIFI_EVENT_ram_3c0cf320_ram_3c0f1eb8 == event_base) && (event_id == 5)) {
    if (DAT_ram_3fcc3a78 < 4) {
      FUN_ram_4204551e();
      DAT_ram_3fcc3a78 = DAT_ram_3fcc3a78 + 1;
      wifi_connection_state_at_3fcc3a74 = 1;
    }
    else {
      FUN_ram_40388e2e(DAT_ram_3fcc3a7c,2);
      stop_wifi_http_server_at_4200c578(event_context);
    }
  }
  else if ((PTR_s_IP_EVENT_ram_3c0cb788_ram_3c0f1848 == event_base) && (event_id == 0)) {
    uStack_28 = 0;
    uStack_24 = 0;
    uStack_20 = 0;
    uStack_1c = 0;
    uStack_18 = 0;
    uStack_14 = 0;
    FUN_ram_420365f2(event_data + 4,&uStack_28,0x18);
    (*(code *)&SUB_ram_40000498)(&DAT_ram_3fcb7b84,&uStack_28);
    DAT_ram_3fcc3a78 = 0;
    DAT_ram_3fcc39ea = 0;
    start_wifi_http_server_at_4200c5ec(event_context);
    FUN_ram_40388e2e(DAT_ram_3fcc3a7c,1);
  }
  return;
}

// Audit label: application_review; entry: ram:4200c6e2; name: wifi_ap_event_handler_at_4200c6e2

void wifi_ap_event_handler_at_4200c6e2(undefined4 event_context,undefined *event_base,int event_id)

{
  if ((PTR_s_WIFI_EVENT_ram_3c0cf320_ram_3c0f1eb8 == event_base) && (event_id == 0xe)) {
    start_wifi_http_server_at_4200c5ec();
  }
  else if ((PTR_s_WIFI_EVENT_ram_3c0cf320_ram_3c0f1eb8 == event_base) && (event_id == 0xf)) {
    stop_wifi_http_server_at_4200c578();
  }
  else if ((PTR_s_WIFI_EVENT_ram_3c0cf320_ram_3c0f1eb8 == event_base) && (event_id == 2)) {
    FUN_ram_4204551e();
  }
  else if ((PTR_s_IP_EVENT_ram_3c0cb788_ram_3c0f1848 == event_base) && (event_id == 0)) {
    DAT_ram_3fcc3a78 = 0;
    FUN_ram_40388e2e(DAT_ram_3fcc3a7c,1);
  }
  return;
}

// Audit label: application_review; entry: ram:4200c74e; name: captive_dns_task_at_4200c74e

void captive_dns_task_at_4200c74e(void)

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

// Audit label: application_review; entry: ram:4200c956; name: inspect_netif_dhcp_state_at_4200c956

void inspect_netif_dhcp_state_at_4200c956(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined1 auStack_20 [12];
  undefined1 auStack_14 [4];

  if (param_1 == 0) {
    uVar2 = FUN_ram_4038d3b4();
    FUN_ram_4038d2a2(1,"wifi station","E (%lu) %s: Netif is NULL\n",uVar2,"wifi station");
  }
  else {
    iVar1 = FUN_ram_42036974(param_1,auStack_14);
    if (iVar1 != 0) {
      uVar2 = FUN_ram_4038d3b4();
      uVar3 = FUN_ram_4201724e(iVar1);
      FUN_ram_4038d2a2(1,"wifi station","E (%lu) %s: Failed to get DHCP status: %s\n",uVar2,
                       "wifi station",uVar3);
    }
    FUN_ram_42036bde(param_1,auStack_20);
  }
  return;
}

// Audit label: application_review; entry: ram:4200c9e0; name: scan_wifi_access_points_at_4200c9e0

void scan_wifi_access_points_at_4200c9e0(void)

{
  short sVar1;
  int iVar2;
  undefined2 auStack_12 [9];

  auStack_12[0] = 0x14;
  sVar1 = FUN_ram_42069046(0,1);
  if (sVar1 == 0) {
    FUN_ram_420691f8(&DAT_ram_3fcc3a6e);
    FUN_ram_42069256(auStack_12,&DAT_ram_3fcbcba4);
    for (iVar2 = 0; iVar2 < (int)(uint)DAT_ram_3fcc3a6e; iVar2 = iVar2 + 1) {
    }
  }
  return;
}

// Audit label: application_review; entry: ram:4200ca30; name: initialize_wifi_station_at_4200ca30

void initialize_wifi_station_at_4200ca30(void)

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
  wifi_connection_state_at_3fcc3a74 = 0;
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
  iVar3 = FUN_ram_420aeab6(PTR_s_WIFI_EVENT_ram_3c0cf320_ram_3c0f1eb8,0xffffffff,wifi_station_event_handler_at_4200c602,0,
                           auStack_ac);
  puVar1 = PTR_s_IP_EVENT_ram_3c0cb788_ram_3c0f1848;
  if (iVar3 != 0) {
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(iVar3,"./main/wifi_connect.c",0xaf,"wifi_init_sta",
                     "esp_event_handler_instance_register(WIFI_EVENT, ESP_EVENT_ANY_ID, &event_handler, NULL, &instance_any_id)"
                    );
  }
  iVar3 = FUN_ram_420aeab6(PTR_s_IP_EVENT_ram_3c0cb788_ram_3c0f1848,0,wifi_station_event_handler_at_4200c602,0,auStack_b0)
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
  (*(code *)&SUB_ram_40000498)(&uStack_168,&wifi_ssid_at_3fcb7ba0);
  (*(code *)&SUB_ram_40000498)(acStack_148,&wifi_password_at_3fcb7be1);
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
    scan_wifi_access_points_at_4200c9e0();
    FUN_ram_420b10ce();
    wifi_connection_state_at_3fcc3a74 = 1;
    uVar4 = FUN_ram_40388c4e(DAT_ram_3fcc3a7c,3,0,0,0xffffffff);
    if ((uVar4 & 1) == 0) {
      if ((uVar4 & 2) != 0) {
        wifi_connection_state_at_3fcc3a74 = 4;
        DAT_ram_3fcb7cfc = 2;
        save_settings_sector_at_42008a00();
                    /* WARNING: Subroutine does not return */
        esp_restart();
      }
      uVar5 = FUN_ram_4038d3b4();
      FUN_ram_4038d2a2(1,"wifi station","E (%lu) %s: UNEXPECTED EVENT\n",uVar5,"wifi station");
    }
    else {
      wifi_connection_state_at_3fcc3a74 = 2;
      DAT_ram_3fcc39ea = 0;
      iVar3 = FUN_ram_420aeae0(puVar1,0,wifi_station_event_handler_at_4200c602);
      if (iVar3 != 0) {
                    /* WARNING: Subroutine does not return */
        FUN_ram_4038726a(iVar3,"./main/wifi_connect.c",0xeb,"wifi_init_sta",
                         "esp_event_handler_unregister(IP_EVENT, IP_EVENT_STA_GOT_IP, &event_handler)"
                        );
      }
      iVar3 = FUN_ram_420aeae0(puVar2,0xffffffff,wifi_station_event_handler_at_4200c602);
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

// Audit label: application_review; entry: ram:4200ce40; name: update_wifi_connection_mode_at_4200ce40

void update_wifi_connection_mode_at_4200ce40(void)

{
  if (DAT_ram_3fcb7cfc == 1) {
    if ((wifi_connection_state_at_3fcc3a74 == '\0') || (wifi_connection_state_at_3fcc3a74 == '\x03')) {
      initialize_wifi_station_at_4200ca30();
    }
    else if (wifi_connection_state_at_3fcc3a74 == '\x04') {
      DAT_ram_3fcb7cfc = 0;
      save_settings_sector_at_42008a00();
      DAT_ram_3fcc39ea = 1;
    }
  }
  else {
    DAT_ram_3fcc39ea = 1;
  }
  return;
}

// Audit label: application_review; entry: ram:4200ce9e; name: configure_softap_network_at_4200ce9e

undefined4 configure_softap_network_at_4200ce9e(void)

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

// Audit label: application_review; entry: ram:4200d06e; name: initialize_wifi_softap_at_4200d06e

void initialize_wifi_softap_at_4200d06e(void)

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
  iVar1 = FUN_ram_420aeab6(PTR_s_WIFI_EVENT_ram_3c0cf320_ram_3c0f1eb8,0xffffffff,wifi_ap_event_handler_at_4200c6e2,0,
                           0);
  if (iVar1 != 0) {
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(iVar1,"./main/wifi_connect.c",0x1e3,"wifi_init_softap",
                     "esp_event_handler_instance_register(WIFI_EVENT, ESP_EVENT_ANY_ID, &wifi_event_handler, NULL, NULL)"
                    );
  }
  iVar1 = FUN_ram_420aeab6(PTR_s_IP_EVENT_ram_3c0cb788_ram_3c0f1848,0,wifi_ap_event_handler_at_4200c6e2,0,0);
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
    uVar2 = configure_softap_network_at_4200ce9e();
    iVar1 = FUN_ram_42068d06();
    if (iVar1 == 0) {
      vTaskDelay(100);
      inspect_netif_dhcp_state_at_4200c956(uVar2);
      scan_wifi_access_points_at_4200c9e0();
      wifi_connection_state_at_3fcc3a74 = 5;
      FUN_ram_420b10ce();
      FUN_ram_4038a7a4(captive_dns_task_at_4200c74e,"dns_server",0x1000,0,5,0,0x7fffffff);
      return;
    }
                    /* WARNING: Subroutine does not return */
    FUN_ram_4038726a(iVar1,"./main/wifi_connect.c",0x1ff,"wifi_init_softap","esp_wifi_start()");
  }
                    /* WARNING: Subroutine does not return */
  FUN_ram_4038726a(iVar1,"./main/wifi_connect.c",0x1f2,"wifi_init_softap",
                   "esp_wifi_set_mode(WIFI_MODE_APSTA)");
}
