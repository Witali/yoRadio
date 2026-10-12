/* GHIDRA REFERENCE PSEUDOCODE, NOT COMPILED.
 * Retains addresses, unresolved SDK calls and decompiler type/overlap artifacts.
 * Executable reconstruction: ESP-IDF / libc (not ported).
 */

// Audit label: lwip_socket; entry: ram:4201ab6e; name: lwip_socket

int lwip_socket(int arg0,int arg1,int arg2)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;

  if (arg1 == 2) {
    if (arg0 == 2) {
      if (arg2 == 0x88) {
        uVar3 = 0x21;
      }
      else {
        uVar3 = 0x20;
      }
    }
    else if (arg2 == 0x88) {
      uVar3 = 0x29;
    }
    else {
      uVar3 = 0x28;
    }
    iVar4 = FUN_ram_420322ca(uVar3,0,FUN_ram_42019300);
  }
  else if (arg1 == 3) {
    if (arg0 == 2) {
      uVar3 = 0x40;
    }
    else {
      uVar3 = 0x48;
    }
    iVar4 = FUN_ram_420322ca(uVar3,arg2 & 0xff,FUN_ram_42019300);
  }
  else {
    if (arg1 != 1) {
      puVar1 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
      *puVar1 = 0x16;
      return -1;
    }
    if (arg0 == 2) {
      uVar3 = 0x10;
    }
    else {
      uVar3 = 0x18;
    }
    iVar4 = FUN_ram_420322ca(uVar3,0,FUN_ram_42019300);
  }
  if (iVar4 == 0) {
    puVar1 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
    *puVar1 = 0x69;
    iVar2 = -1;
  }
  else {
    iVar2 = FUN_ram_420181ce(iVar4,0);
    if (iVar2 == -1) {
      FUN_ram_420323b0(iVar4);
      puVar1 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
      *puVar1 = 0x17;
    }
    else {
      *(int *)(iVar4 + 0x1c) = iVar2;
      FUN_ram_42018718(&DAT_ram_3fcc0168 + (iVar2 + -0x36) * 5);
    }
  }
  return iVar2;
}

// Audit label: lwip_bind; entry: ram:4201a468; name: lwip_bind

int lwip_bind(int arg0,void *arg1,uint arg2)

{
  char cVar1;
  undefined4 *puVar2;
  int iVar3;
  int iVar4;
  undefined4 *puVar5;
  undefined4 uVar6;
  undefined2 uStack_2a;
  int iStack_28;
  int iStack_24;
  int iStack_20;
  char cStack_14;

  puVar2 = (undefined4 *)FUN_ram_420187f4();
  if (puVar2 == (undefined4 *)0x0) {
    iVar3 = -1;
  }
  else {
    cVar1 = *(char *)((int)arg1 + 1);
    if (((cVar1 == '\x02') && ((*(uint *)*puVar2 & 8) == 0)) ||
       ((cVar1 == '\n' && ((*(uint *)*puVar2 & 8) != 0)))) {
      if ((((arg2 == 0x10) || (arg2 == 0x1c)) && ((cVar1 == '\x02' || (cVar1 == '\n')))) &&
         (((uint)arg1 & 3) == 0)) {
        FUN_ram_4201848e(arg1,&iStack_28,&uStack_2a);
        if ((((cStack_14 == '\x06') && (iStack_28 == 0)) && (iStack_24 == 0)) &&
           (iStack_20 == -0x10000)) {
          cStack_14 = '\0';
        }
        iVar3 = FUN_ram_4203241a(*puVar2,&iStack_28,uStack_2a);
        if (iVar3 == 0) {
          FUN_ram_42018718(puVar2);
          iVar3 = 0;
        }
        else {
          iVar4 = FUN_ram_420349e0();
          if (iVar4 != 0) {
            puVar5 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
            uVar6 = FUN_ram_420349e0(iVar3);
            *puVar5 = uVar6;
          }
          FUN_ram_42018718(puVar2);
          iVar3 = -1;
        }
      }
      else {
        iVar3 = FUN_ram_420349e0(0xfffffff0);
        if (iVar3 != 0) {
          puVar5 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
          uVar6 = FUN_ram_420349e0(0xfffffff0);
          *puVar5 = uVar6;
        }
        FUN_ram_42018718(puVar2);
        iVar3 = -1;
      }
    }
    else {
      iVar3 = FUN_ram_420349e0(0xfffffffa);
      if (iVar3 != 0) {
        puVar5 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
        uVar6 = FUN_ram_420349e0(0xfffffffa);
        *puVar5 = uVar6;
      }
      FUN_ram_42018718(puVar2);
      iVar3 = -1;
    }
  }
  return iVar3;
}

// Audit label: lwip_recvfrom; entry: ram:4201a7f0; name: lwip_recvfrom

int lwip_recvfrom(int arg0,void *arg1,uint arg2,int arg3,void *arg4,void *arg5)

{
  uint uVar1;
  undefined4 *puVar2;
  int iVar3;
  int iVar4;
  undefined4 *puVar5;
  undefined4 uVar6;
  ushort uStack_46;
  void *pvStack_44;
  uint uStack_40;
  void *pvStack_3c;
  undefined4 uStack_38;
  void **ppvStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;

  puVar2 = (undefined4 *)FUN_ram_420187f4();
  if (puVar2 == (undefined4 *)0x0) {
    uVar1 = 0xffffffff;
  }
  else if ((*(uint *)*puVar2 & 0xf0) == 0x10) {
    uVar1 = FUN_ram_42018eaa(puVar2,arg1,arg2,arg3);
    FUN_ram_42018658(puVar2,arg4,arg5,"lwip_recvfrom",arg0,uVar1);
    FUN_ram_42018718(puVar2);
  }
  else {
    uStack_46 = 0;
    uStack_2c = 0;
    uStack_28 = 0;
    uStack_24 = 0;
    ppvStack_34 = &pvStack_44;
    uStack_30 = 1;
    if (arg5 == (void *)0x0) {
      uStack_38 = 0;
    }
    else {
      uStack_38 = *(undefined4 *)arg5;
    }
    pvStack_44 = arg1;
    uStack_40 = arg2;
    pvStack_3c = arg4;
    iVar3 = FUN_ram_4201909e(puVar2,arg3,&pvStack_3c,&uStack_46,arg0);
    if (iVar3 == 0) {
      uVar1 = (uint)uStack_46;
      if (arg2 < uStack_46) {
        uVar1 = arg2;
      }
      if (0x7ffffffe < uVar1) {
        uVar1 = 0x7fffffff;
      }
      if (arg5 != (void *)0x0) {
        *(undefined4 *)arg5 = uStack_38;
      }
      FUN_ram_42018718(puVar2);
    }
    else {
      iVar4 = FUN_ram_420349e0();
      if (iVar4 != 0) {
        puVar5 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
        uVar6 = FUN_ram_420349e0(iVar3);
        *puVar5 = uVar6;
      }
      FUN_ram_42018718(puVar2);
      uVar1 = 0xffffffff;
    }
  }
  return uVar1;
}

// Audit label: lwip_sendto; entry: ram:4201a91c; name: lwip_sendto

int lwip_sendto(int arg0,void *arg1,uint arg2,int arg3,void *arg4,uint arg5)

{
  undefined4 *puVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  undefined4 *puVar5;
  undefined4 uVar6;
  int aiStack_48 [6];
  undefined1 uStack_30;
  char cStack_2c;
  undefined2 uStack_28;
  undefined2 uStack_22;

  puVar1 = (undefined4 *)FUN_ram_420187f4();
  if (puVar1 == (undefined4 *)0x0) {
    uVar4 = 0xffffffff;
  }
  else if ((*(uint *)*puVar1 & 0xf0) == 0x10) {
    FUN_ram_42018718();
    uVar4 = sdk_lwip_sendto_reference_at_4201aacc(arg0,arg1,arg2,arg3);
  }
  else if (arg2 < 0x10000) {
    if (((arg4 == (void *)0x0) && (arg5 == 0)) ||
       ((((arg5 == 0x10 || (arg5 == 0x1c)) && (arg4 != (void *)0x0)) &&
        (((*(char *)((int)arg4 + 1) == '\x02' || (*(char *)((int)arg4 + 1) == '\n')) &&
         (((uint)arg4 & 3) == 0)))))) {
      aiStack_48[1] = 0;
      aiStack_48[0] = 0;
      if (arg4 == (void *)0x0) {
        uStack_22 = 0;
        if ((*(uint *)*puVar1 & 8) == 0) {
          aiStack_48[2] = 0;
          cStack_2c = '\0';
          aiStack_48[5] = 0;
          aiStack_48[4] = 0;
          aiStack_48[3] = 0;
          uStack_30 = 0;
        }
        else {
          aiStack_48[2] = 0;
          aiStack_48[3] = 0;
          aiStack_48[4] = 0;
          aiStack_48[5] = 0;
          uStack_30 = 0;
          cStack_2c = '\x06';
        }
      }
      else {
        FUN_ram_4201848e(arg4,aiStack_48 + 2,&uStack_22);
      }
      uStack_28 = uStack_22;
      iVar2 = FUN_ram_42034a30(aiStack_48,arg2 & 0xffff);
      if (iVar2 == 0) {
        iVar2 = -1;
      }
      else {
        (*(code *)&SUB_ram_4000048c)(*(undefined4 *)(aiStack_48[0] + 4),arg1,arg2 & 0xffff);
        if (((cStack_2c == '\x06') && (aiStack_48[2] == 0)) &&
           ((aiStack_48[3] == 0 && (aiStack_48[4] == -0x10000)))) {
          aiStack_48[2] = aiStack_48[5];
          cStack_2c = '\0';
        }
        iVar2 = FUN_ram_42032580(*puVar1,aiStack_48);
      }
      FUN_ram_42034a92(aiStack_48);
      iVar3 = FUN_ram_420349e0(iVar2);
      if (iVar3 != 0) {
        puVar5 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
        uVar6 = FUN_ram_420349e0(iVar2);
        *puVar5 = uVar6;
      }
      FUN_ram_42018718(puVar1);
      if (iVar2 == 0) {
        uVar4 = arg2 & 0xffff;
      }
      else {
        uVar4 = 0xffffffff;
      }
    }
    else {
      iVar2 = FUN_ram_420349e0(0xfffffff0);
      if (iVar2 != 0) {
        puVar5 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
        uVar6 = FUN_ram_420349e0(0xfffffff0);
        *puVar5 = uVar6;
      }
      FUN_ram_42018718(puVar1);
      uVar4 = 0xffffffff;
    }
  }
  else {
    puVar5 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
    *puVar5 = 0x7a;
    FUN_ram_42018718(puVar1);
    uVar4 = 0xffffffff;
  }
  return uVar4;
}

// Audit label: httpd_req_recv; entry: ram:4203b694; name: httpd_req_recv

int httpd_req_recv(int param_1,int param_2,uint param_3)

{
  undefined4 *puVar1;
  int iVar2;
  uint uVar3;
  undefined4 uStack_18;
  int iStack_14;

  if (param_1 == 0) {
    iVar2 = -2;
  }
  else if (param_2 == 0) {
    iVar2 = -2;
  }
  else {
    puVar1 = *(undefined4 **)(param_1 + 0x210);
    uVar3 = puVar1[6];
    if (param_3 <= (uint)puVar1[6]) {
      uVar3 = param_3;
    }
    if (uVar3 == 0) {
      iVar2 = 0;
    }
    else {
      iVar2 = FUN_ram_4203b0c2();
      if (-1 < iVar2) {
        puVar1[6] = puVar1[6] - iVar2;
        uStack_18 = *(undefined4 *)*puVar1;
        iStack_14 = iVar2;
        FUN_ram_420390f2(5,&uStack_18);
      }
    }
  }
  return iVar2;
}

// Audit label: httpd_req_get_hdr_value_str; entry: ram:4203a51e; name: httpd_req_get_hdr_value_str

undefined4 httpd_req_get_hdr_value_str(int param_1,int param_2,undefined4 param_3,uint param_4)

{
  char *pcVar1;
  char *pcVar2;
  int iVar3;
  uint uVar4;
  undefined4 uVar5;
  int iVar6;

  if (param_1 == 0) {
    uVar5 = 0x102;
  }
  else if (param_2 == 0) {
    uVar5 = 0x102;
  }
  else {
    pcVar1 = *(char **)(*(int *)(param_1 + 0x210) + 4);
    iVar3 = *(int *)(*(int *)(param_1 + 0x210) + 0x28);
    while (iVar6 = iVar3 + -1, iVar3 != 0) {
      pcVar2 = (char *)(*(code *)&SUB_ram_40000514)(pcVar1,0x3a);
      if (pcVar2 == (char *)0x0) {
        return 0x105;
      }
      iVar3 = (*(code *)&SUB_ram_400004a8)(param_2);
      if (((int)pcVar2 - (int)pcVar1 == iVar3) &&
         (iVar3 = (*(code *)&SUB_ram_4000052c)(pcVar1,param_2,iVar3), iVar3 == 0)) {
        do {
          pcVar2 = pcVar2 + 1;
        } while (*pcVar2 == ' ');
        uVar4 = (*(code *)&SUB_ram_40000524)(param_3,pcVar2,param_4);
        if (uVar4 <= param_4) {
          return 0;
        }
        return 0xb004;
      }
      iVar3 = iVar6;
      if (iVar6 != 0) {
        iVar6 = (*(code *)&SUB_ram_400004a8)(pcVar1);
        for (pcVar1 = pcVar1 + iVar6 + 1; *pcVar1 == '\0'; pcVar1 = pcVar1 + 1) {
        }
      }
    }
    uVar5 = 0x105;
  }
  return uVar5;
}

// Audit label: httpd_start; entry: ram:420396ac; name: httpd_start

undefined4 httpd_start(int *param_1,int param_2)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;

  if (param_1 == (int *)0x0) {
    uVar3 = 0x102;
  }
  else if (param_2 == 0) {
    uVar3 = 0x102;
  }
  else if (*(ushort *)(param_2 + 0x1c) < 8) {
    puVar1 = (undefined4 *)FUN_ram_42038c48();
    if (puVar1 == (undefined4 *)0x0) {
      uVar3 = 0xb007;
    }
    else {
      iVar2 = sdk_lwip_socket_reference_at_42038e52();
      if (iVar2 == 0) {
        FUN_ram_4203ad5e(puVar1);
        iVar2 = FUN_ram_420b203a(FUN_ram_42039606,"httpd",*(undefined2 *)(puVar1 + 1),puVar1,*puVar1
                                 ,puVar1 + 0x1b,puVar1[2],puVar1[3]);
        if (iVar2 == 1) {
          *param_1 = (int)puVar1;
          FUN_ram_420390f2(1,0,0);
          uVar3 = 0;
        }
        else {
          FUN_ram_420390a6(puVar1);
          uVar3 = 0xb008;
        }
      }
      else {
        FUN_ram_420390a6(puVar1);
        uVar3 = 0xffffffff;
      }
    }
  }
  else {
    uVar3 = FUN_ram_4038d3b4(param_2);
    FUN_ram_4038d2a2(1,"httpd",
                     "E (%lu) %s: Config option max_open_sockets is too large (max allowed %d, 3 sockets used by HTTP server internally)\n\tEither decrease this or configure LWIP_MAX_SOCKETS to a larger value\n"
                     ,uVar3,"httpd",7);
    uVar3 = 0x102;
  }
  return uVar3;
}

// Audit label: esp_http_client_perform; entry: ram:4203e7b8; name: esp_http_client_perform

int esp_http_client_perform(void *arg0)

{
  void *pvVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  int *piVar5;
  int iVar6;
  uint uVar7;
  longlong lVar8;
  void *apvStack_14 [2];

  iVar2 = -1;
  apvStack_14[0] = arg0;
  do {
    if (*(int *)((int)apvStack_14[0] + 0xc) != 0) {
      FUN_ram_4203d5e2();
    }
    uVar7 = *(uint *)((int)apvStack_14[0] + 0x80);
    if (uVar7 == 3) {
LAB_ram_4203e7e6:
      iVar2 = FUN_ram_4203d766(apvStack_14[0]);
      if (iVar2 != 0) {
        if ((*(char *)((int)apvStack_14[0] + 0xc4) != '\0') &&
           (piVar5 = (int *)(*(code *)&SUB_ram_40000670)(), *piVar5 == 0xb)) {
          return 0x7007;
        }
        pvVar1 = apvStack_14[0];
        uVar4 = FUN_ram_420839a6(*(undefined4 *)((int)apvStack_14[0] + 0x1c));
        FUN_ram_4203ca1a(pvVar1,0,uVar4,0);
        FUN_ram_4203cad0(0,apvStack_14,4);
        return iVar2;
      }
LAB_ram_4203e7f2:
      *(byte *)((int)apvStack_14[0] + 0xdc) = *(byte *)((int)apvStack_14[0] + 0xdc) & 0xfe;
      lVar8 = FUN_ram_4203d64c();
      if (lVar8 < 0) {
        if (((*(char *)((int)apvStack_14[0] + 0xc4) == '\0') ||
            (piVar5 = (int *)(*(code *)&SUB_ram_40000670)(), *piVar5 != 0xb)) && (lVar8 != -0x7007))
        {
          *(byte *)((int)apvStack_14[0] + 0xdc) = *(byte *)((int)apvStack_14[0] + 0xdc) | 1;
          iVar2 = FUN_ram_420839b0(*(undefined4 *)((int)apvStack_14[0] + 0x1c));
          pvVar1 = apvStack_14[0];
          if (iVar2 == 0x80) {
            uVar4 = FUN_ram_4038d3b4();
            FUN_ram_4038d2a2(2,"HTTP_CLIENT","W (%lu) %s: Close connection due to FIN received\n",
                             uVar4,"HTTP_CLIENT");
            FUN_ram_4203d7ee(apvStack_14[0]);
            pvVar1 = apvStack_14[0];
            uVar4 = FUN_ram_420839a6(*(undefined4 *)((int)apvStack_14[0] + 0x1c));
            FUN_ram_4203ca1a(pvVar1,0,uVar4,0);
            FUN_ram_4203cad0(0,apvStack_14,4);
            iVar2 = 0x7008;
          }
          else {
            uVar4 = FUN_ram_420839a6(*(undefined4 *)((int)apvStack_14[0] + 0x1c));
            FUN_ram_4203ca1a(pvVar1,0,uVar4,0);
            FUN_ram_4203cad0(0,apvStack_14,4);
            iVar2 = 0x7004;
          }
        }
        else {
          iVar2 = 0x7007;
        }
        return iVar2;
      }
LAB_ram_4203e80a:
      *(byte *)((int)apvStack_14[0] + 0xdc) = *(byte *)((int)apvStack_14[0] + 0xdc) | 1;
      iVar2 = FUN_ram_4203e6f4();
      if (iVar2 != 0) {
        uVar4 = FUN_ram_4038d3b4();
        FUN_ram_4038d2a2(1,"HTTP_CLIENT","E (%lu) %s: Error response\n",uVar4,"HTTP_CLIENT");
        pvVar1 = apvStack_14[0];
        uVar4 = FUN_ram_420839a6(*(undefined4 *)((int)apvStack_14[0] + 0x1c));
        FUN_ram_4203ca1a(pvVar1,0,uVar4,0);
        FUN_ram_4203cad0(0,apvStack_14,4);
        return iVar2;
      }
      do {
        iVar2 = 0;
        if ((*(char *)(*(int *)((int)apvStack_14[0] + 0x24) + 0x2c) == '\0') ||
           (*(char *)((int)apvStack_14[0] + 0x7c) != '\0')) goto LAB_ram_4203e858;
        iVar3 = FUN_ram_4203d334();
      } while (0 < iVar3);
      if ((*(char *)((int)apvStack_14[0] + 0xc4) != '\0') &&
         (piVar5 = (int *)(*(code *)&SUB_ram_40000670)(), *piVar5 == 0xb)) {
        return 0x7007;
      }
      if ((*(int *)((int)apvStack_14[0] + 0x6c) != 5) &&
         (*(char *)((int)apvStack_14[0] + 0x7c) == '\0')) {
        uVar4 = FUN_ram_4038d3b4();
        FUN_ram_4038d2a2(1,"HTTP_CLIENT","E (%lu) %s: Incomplete chunked data received %d\n",uVar4,
                         "HTTP_CLIENT",iVar3);
        if (iVar3 == 0xe001) {
          iVar2 = 0x700b;
        }
        else if (iVar3 == 0xe002) {
          iVar2 = 0x7008;
        }
        else {
          iVar2 = 0x700c;
        }
      }
LAB_ram_4203e858:
      do {
        iVar3 = *(int *)((int)apvStack_14[0] + 0x24);
        if ((*(int *)(iVar3 + 0x14) <= *(int *)(iVar3 + 0x24)) &&
           ((*(int *)(iVar3 + 0x14) != *(int *)(iVar3 + 0x24) ||
            (*(uint *)(iVar3 + 0x10) <= *(uint *)(iVar3 + 0x20))))) goto LAB_ram_4203e898;
        iVar3 = FUN_ram_4203d334();
      } while (0 < iVar3);
      if ((*(char *)((int)apvStack_14[0] + 0xc4) != '\0') &&
         (piVar5 = (int *)(*(code *)&SUB_ram_40000670)(), *piVar5 == 0xb)) {
        return 0x7007;
      }
      if (*(int *)((int)apvStack_14[0] + 0x6c) == 5) {
LAB_ram_4203e898:
        if (iVar2 != 0) goto LAB_ram_4203e89c;
        FUN_ram_4203ca1a(apvStack_14[0],5,0,0);
        FUN_ram_4203cad0(5,apvStack_14,4);
      }
      else {
        iVar6 = *(int *)((int)apvStack_14[0] + 0x24);
        if ((*(int *)(iVar6 + 0x14) <= *(int *)(iVar6 + 0x24)) &&
           ((*(int *)(iVar6 + 0x14) != *(int *)(iVar6 + 0x24) ||
            (*(uint *)(iVar6 + 0x10) <= *(uint *)(iVar6 + 0x20))))) goto LAB_ram_4203e898;
        uVar4 = FUN_ram_4038d3b4();
        iVar2 = *(int *)((int)apvStack_14[0] + 0x24);
        FUN_ram_4038d2a2(1,"HTTP_CLIENT",
                         "E (%lu) %s: Incomlete data received, ret=%d, %lld/%lld bytes\n",uVar4,
                         "HTTP_CLIENT",iVar3,*(undefined4 *)(iVar2 + 0x20),
                         *(undefined4 *)(iVar2 + 0x24),*(undefined4 *)(iVar2 + 0x10),
                         *(undefined4 *)(iVar2 + 0x14));
        if (iVar3 == 0xe001) {
          iVar2 = 0x700b;
        }
        else if (iVar3 == 0xe002) {
          iVar2 = 0x7008;
        }
        else {
          iVar2 = 0x700c;
        }
LAB_ram_4203e89c:
        pvVar1 = apvStack_14[0];
        uVar4 = FUN_ram_420839a6(*(undefined4 *)((int)apvStack_14[0] + 0x1c));
        FUN_ram_4203ca1a(pvVar1,0,uVar4,0);
        FUN_ram_4203cad0(0,apvStack_14,4);
      }
      *(undefined4 *)(*(int *)(*(int *)((int)apvStack_14[0] + 0x24) + 4) + 0x10) = 0;
      iVar3 = FUN_ram_4207e4e0(*(undefined4 *)((int)apvStack_14[0] + 0x10));
      if (iVar3 == 0) {
        FUN_ram_4203d7ee(apvStack_14[0]);
      }
      else if (2 < *(uint *)((int)apvStack_14[0] + 0x80)) {
        *(undefined4 *)((int)apvStack_14[0] + 0x80) = 2;
        *(undefined1 *)((int)apvStack_14[0] + 0xbc) = 0;
      }
    }
    else {
      if (uVar7 < 4) {
        if (uVar7 == 1) {
          iVar2 = FUN_ram_4203d838();
          pvVar1 = apvStack_14[0];
          if (iVar2 != 0) {
            if ((*(char *)((int)apvStack_14[0] + 0xc4) != '\0') && (iVar2 == 0x7006)) {
              return 0x7007;
            }
            uVar4 = FUN_ram_420839a6(*(undefined4 *)((int)apvStack_14[0] + 0x1c));
            FUN_ram_4203ca1a(pvVar1,0,uVar4,0);
            FUN_ram_4203cad0(0,apvStack_14,4);
            return iVar2;
          }
        }
        else if (uVar7 != 2) goto LAB_ram_4203e8e2;
        iVar2 = FUN_ram_4203e470(apvStack_14[0],*(undefined4 *)((int)apvStack_14[0] + 0x44));
        if (iVar2 != 0) {
          if ((*(char *)((int)apvStack_14[0] + 0xc4) != '\0') &&
             (piVar5 = (int *)(*(code *)&SUB_ram_40000670)(), *piVar5 == 0xb)) {
            return 0x7007;
          }
          pvVar1 = apvStack_14[0];
          uVar4 = FUN_ram_420839a6(*(undefined4 *)((int)apvStack_14[0] + 0x1c));
          FUN_ram_4203ca1a(pvVar1,0,uVar4,0);
          FUN_ram_4203cad0(0,apvStack_14,4);
          return iVar2;
        }
        goto LAB_ram_4203e7e6;
      }
      if (uVar7 == 4) goto LAB_ram_4203e7f2;
      if (uVar7 == 6) goto LAB_ram_4203e80a;
    }
LAB_ram_4203e8e2:
    if (*(int *)((int)apvStack_14[0] + 0xc) == 0) {
      return iVar2;
    }
    if (iVar2 != 0) {
      return iVar2;
    }
  } while( true );
}

// Audit label: esp_http_client_cleanup; entry: ram:4203d9f2; name: esp_http_client_cleanup

int esp_http_client_cleanup(void *arg0)

{
  int iVar1;
  undefined4 *puVar2;

  if (arg0 == (void *)0x0) {
    iVar1 = -1;
  }
  else {
    FUN_ram_4203d7ee();
    if (*(int *)((int)arg0 + 0x18) != 0) {
      FUN_ram_4208388e();
    }
    if (*(undefined4 **)((int)arg0 + 0x20) != (undefined4 *)0x0) {
      FUN_ram_4203f124(**(undefined4 **)((int)arg0 + 0x20));
      puVar2 = *(undefined4 **)(*(int *)((int)arg0 + 0x20) + 4);
      if (puVar2 != (undefined4 *)0x0) {
        FUN_ram_4038e4da(*puVar2);
      }
      FUN_ram_4038e4da(*(undefined4 *)(*(int *)((int)arg0 + 0x20) + 4));
      FUN_ram_4038e4da(*(undefined4 *)((int)arg0 + 0x20));
    }
    if (*(undefined4 **)((int)arg0 + 0x24) != (undefined4 *)0x0) {
      FUN_ram_4203f124(**(undefined4 **)((int)arg0 + 0x24));
      puVar2 = *(undefined4 **)(*(int *)((int)arg0 + 0x24) + 4);
      if (puVar2 != (undefined4 *)0x0) {
        FUN_ram_4038e4da(*puVar2);
        FUN_ram_4203caa6(*(undefined4 *)(*(int *)((int)arg0 + 0x24) + 4));
      }
      FUN_ram_4038e4da(*(undefined4 *)(*(int *)((int)arg0 + 0x24) + 4));
      FUN_ram_4038e4da(*(undefined4 *)((int)arg0 + 0x24));
    }
    if (*(int *)((int)arg0 + 0xd8) != 0) {
      FUN_ram_4038e4da();
    }
    FUN_ram_4038e4da(*(undefined4 *)((int)arg0 + 0x10));
    FUN_ram_4038e4da(*(undefined4 *)((int)arg0 + 0x14));
    FUN_ram_4203cbdc(arg0);
    FUN_ram_4203cc66(arg0);
    FUN_ram_4038e4da(*(undefined4 *)((int)arg0 + 0x2c));
    FUN_ram_4038e4da(*(undefined4 *)((int)arg0 + 0x3c));
    FUN_ram_4038e4da(*(undefined4 *)((int)arg0 + 0x40));
    FUN_ram_4038e4da(*(undefined4 *)((int)arg0 + 0x34));
    FUN_ram_4038e4da(*(undefined4 *)((int)arg0 + 0x38));
    FUN_ram_4038e4da(arg0);
    iVar1 = 0;
  }
  return iVar1;
}

// Audit label: esp_flash_read; entry: ram:40392326; name: esp_flash_read

int esp_flash_read(undefined4 *param_1,int param_2,uint param_3,uint param_4)

{
  char cVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  undefined4 *apuStack_34 [4];
  uint uStack_24;

  apuStack_34[0] = param_1;
  iVar2 = (**(code **)(PTR_PTR_ram_3fcb5974 + 8))(apuStack_34);
  if (iVar2 == 0) {
    if (*(int *)(apuStack_34[0][1] + 0x40) == 0) {
      iVar2 = 0x6005;
    }
    else if (param_2 == 0) {
      iVar2 = 0x102;
    }
    else if ((uint)apuStack_34[0][5] < param_3) {
      iVar2 = 0x102;
    }
    else if ((uint)apuStack_34[0][5] < param_3 + param_4) {
      iVar2 = 0x102;
    }
    else if (param_4 != 0) {
      cVar1 = (**(code **)(*(int *)*apuStack_34[0] + 0x30))((int *)*apuStack_34[0],param_2);
      uVar4 = param_4;
      if (0x4000 < param_4) {
        uVar4 = 0x4000;
      }
      if (param_2 + 0xc0360000U < 0x40000 || cVar1 != '\0') {
        iVar3 = 0;
      }
      else {
        uStack_24 = 0;
        if ((*(code **)(apuStack_34[0][2] + 0x10) == (code *)0x0) ||
           (iVar3 = (**(code **)(apuStack_34[0][2] + 0x10))(apuStack_34[0][3],uVar4,&uStack_24),
           uVar4 = uStack_24, iVar3 == 0)) {
          return 0x101;
        }
      }
      while (iVar2 = (**(code **)PTR_PTR_ram_3fcb5974)(apuStack_34[0]), iVar2 == 0) {
        iVar2 = param_2;
        if (iVar3 != 0) {
          iVar2 = iVar3;
        }
        uVar5 = param_4;
        if (uVar4 < param_4) {
          uVar5 = uVar4;
        }
        iVar2 = (**(code **)(apuStack_34[0][1] + 0x40))(apuStack_34[0],iVar2,param_3,uVar5);
        if (iVar2 != 0) {
          (**(code **)(PTR_PTR_ram_3fcb5974 + 4))(apuStack_34[0],iVar2);
          break;
        }
        iVar2 = (**(code **)(PTR_PTR_ram_3fcb5974 + 4))(apuStack_34[0],0);
        if (iVar3 != 0) {
          (*(code *)&SUB_ram_4000048c)(param_2,iVar3,uVar5);
        }
        param_3 = param_3 + uVar5;
        param_4 = param_4 - uVar5;
        param_2 = param_2 + uVar5;
        if ((iVar2 != 0) || (param_4 == 0)) break;
      }
      if (*(code **)(apuStack_34[0][2] + 0x14) != (code *)0x0) {
        (**(code **)(apuStack_34[0][2] + 0x14))(apuStack_34[0][3],iVar3);
      }
    }
  }
  return iVar2;
}

// Audit label: application_review; entry: ram:4200807e; name: dev_null_close_at_4200807e

undefined4 dev_null_close_at_4200807e(uint param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 *puVar1;

  if ((0xf < param_1) || ((DAT_ram_3fcc39bc >> ((param_1 & 0xf) << 1) & 2) == 0)) {
    puVar1 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
    *puVar1 = 9;
    param_3 = 0xffffffff;
  }
  return param_3;
}

// Audit label: application_review; entry: ram:420080b4; name: dev_null_read_at_420080b4

undefined4 dev_null_read_at_420080b4(uint param_1)

{
  undefined4 *puVar1;

  if ((param_1 < 0x10) && ((DAT_ram_3fcc39bc >> ((param_1 & 0xf) << 1) & 1) != 0)) {
    return 0;
  }
  puVar1 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
  *puVar1 = 9;
  return 0xffffffff;
}

// Audit label: application_review; entry: ram:420080e8; name: dev_null_write_at_420080e8

undefined4 dev_null_write_at_420080e8(uint param_1)

{
  undefined4 *puVar1;

  if ((param_1 < 0x10) && ((DAT_ram_3fcc39bc >> ((param_1 & 0xf) << 1) & 1) != 0)) {
    return 0;
  }
  puVar1 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
  *puVar1 = 9;
  return 0xffffffff;
}

// Audit label: application_review; entry: ram:4200811c; name: dev_null_seek_at_4200811c

undefined4 dev_null_seek_at_4200811c(uint param_1,undefined4 param_2,uint param_3)

{
  undefined4 *puVar1;

  if ((param_1 < 0x10) && ((DAT_ram_3fcc39bc >> ((param_1 & 0xf) << 1) & 3) != 0)) {
    if (param_3 < 3) {
      return 0;
    }
    puVar1 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
    *puVar1 = 0x16;
    return 0xffffffff;
  }
  puVar1 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
  *puVar1 = 9;
  return 0xffffffff;
}

// Audit label: application_review; entry: ram:42008166; name: dev_null_open_at_42008166

undefined4 dev_null_open_at_42008166(uint param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 *puVar1;

  if ((0xf < param_1) || ((DAT_ram_3fcc39bc >> ((param_1 & 0xf) << 1) & 2) == 0)) {
    puVar1 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
    *puVar1 = 9;
    param_3 = 0xffffffff;
  }
  return param_3;
}

// Audit label: application_review; entry: ram:4200819c; name: dev_null_stat_at_4200819c

undefined4 dev_null_stat_at_4200819c(undefined4 param_1,int param_2)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 *puVar3;

  iVar2 = (*(code *)&SUB_ram_400004a0)(param_1,&DAT_ram_3c0c28b8);
  if (iVar2 == 0) {
    (*(code *)&SUB_ram_40000488)(param_2,0,0x58);
    *(undefined4 *)(param_2 + 4) = 0x21b6;
    *(undefined2 *)(param_2 + 8) = 1;
    uVar1 = 0;
  }
  else {
    puVar3 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
    *puVar3 = 2;
    uVar1 = 0xffffffff;
  }
  return uVar1;
}

// Audit label: application_review; entry: ram:420081f4; name: dev_null_fstat_at_420081f4

undefined4 dev_null_fstat_at_420081f4(uint param_1,int param_2)

{
  undefined4 uVar1;
  undefined4 *puVar2;

  if (param_1 < 0x10) {
    (*(code *)&SUB_ram_40000488)(param_2,0,0x58);
    *(undefined4 *)(param_2 + 4) = 0x21b6;
    *(undefined2 *)(param_2 + 8) = 1;
    uVar1 = 0;
  }
  else {
    puVar2 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
    *puVar2 = 9;
    uVar1 = 0xffffffff;
  }
  return uVar1;
}

// Audit label: application_review; entry: ram:4200823a; name: register_dev_null_at_4200823a

void register_dev_null_at_4200823a(void)

{
  FUN_ram_42006c56("/dev/null",&PTR_FUN_ram_42008166_ram_3c0d61cc,8,0);
  return;
}

// Audit label: application_review; entry: ram:4200825c; name: initialize_dev_null_at_4200825c

void initialize_dev_null_at_4200825c(void)

{
  register_dev_null_at_4200823a();
  return;
}

// Audit label: lwip_socket_reference; entry: ram:42038e52; name: sdk_lwip_socket_reference_at_42038e52

undefined4 sdk_lwip_socket_reference_at_42038e52(int param_1)

{
  int arg0;
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 *puVar4;
  undefined4 local_40;
  undefined *puStack_3c;
  ushort uStack_3a;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;

  arg0 = lwip_socket(10,1,0);
  if (arg0 < 0) {
    uVar3 = FUN_ram_4038d3b4();
    puVar4 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
    FUN_ram_4038d2a2(1,"httpd","E (%lu) %s: %s: error in socket (%d)\n",uVar3,"httpd",
                     "httpd_server_init",*puVar4);
    uVar3 = 0xffffffff;
  }
  else {
    uStack_20 = 0;
    uStack_1c = 0;
    uStack_18 = 0;
    uStack_14 = 0;
    uStack_38 = 0;
    uStack_34 = 0;
    uStack_30 = 0;
    uStack_2c = 0;
    uStack_28 = 0;
    uStack_24 = 0;
    _puStack_3c = CONCAT22(*(ushort *)(param_1 + 0x18) >> 8 | *(ushort *)(param_1 + 0x18) << 8,
                           &mcycle);
    local_40 = 1;
    iVar1 = FUN_ram_4201b1dc(arg0,0xfff,4,&local_40);
    if (iVar1 < 0) {
      uVar3 = FUN_ram_4038d3b4();
      puVar4 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
      FUN_ram_4038d2a2(2,"httpd","W (%lu) %s: %s: error in setsockopt SO_REUSEADDR (%d)\n",uVar3,
                       "httpd","httpd_server_init",*puVar4);
    }
    iVar1 = lwip_bind(arg0,&puStack_3c,0x1c);
    if (iVar1 < 0) {
      uVar3 = FUN_ram_4038d3b4();
      puVar4 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
      FUN_ram_4038d2a2(1,"httpd","E (%lu) %s: %s: error in bind (%d)\n",uVar3,"httpd",
                       "httpd_server_init",*puVar4);
      FUN_ram_420ab05c(arg0);
      uVar3 = 0xffffffff;
    }
    else {
      iVar1 = FUN_ram_4201a760(arg0,*(undefined2 *)(param_1 + 0x22));
      if (iVar1 < 0) {
        uVar3 = FUN_ram_4038d3b4();
        puVar4 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
        FUN_ram_4038d2a2(1,"httpd","E (%lu) %s: %s: error in listen (%d)\n",uVar3,"httpd",
                         "httpd_server_init",*puVar4);
        FUN_ram_420ab05c(arg0);
        uVar3 = 0xffffffff;
      }
      else {
        iVar1 = sdk_lwip_socket_reference_at_4203c930(*(undefined2 *)(param_1 + 0x1a));
        if (iVar1 < 0) {
          uVar3 = FUN_ram_4038d3b4();
          puVar4 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
          FUN_ram_4038d2a2(1,"httpd","E (%lu) %s: %s: error in creating ctrl socket (%d)\n",uVar3,
                           "httpd","httpd_server_init",*puVar4);
          FUN_ram_420ab05c(arg0);
          uVar3 = 0xffffffff;
        }
        else {
          iVar2 = lwip_socket(2,2,0x11);
          if (iVar2 < 0) {
            uVar3 = FUN_ram_4038d3b4();
            puVar4 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
            FUN_ram_4038d2a2(1,"httpd","E (%lu) %s: %s: error in creating msg socket (%d)\n",uVar3,
                             "httpd","httpd_server_init",*puVar4);
            FUN_ram_420ab05c(arg0);
            FUN_ram_420ab05c(iVar1);
            uVar3 = 0xffffffff;
          }
          else {
            *(int *)(param_1 + 0x60) = arg0;
            *(int *)(param_1 + 100) = iVar1;
            *(int *)(param_1 + 0x68) = iVar2;
            uVar3 = 0;
          }
        }
      }
    }
  }
  return uVar3;
}

// Audit label: lwip_socket_reference; entry: ram:4203c930; name: sdk_lwip_socket_reference_at_4203c930

int sdk_lwip_socket_reference_at_4203c930(ushort param_1)

{
  int arg0;
  int iVar1;
  undefined2 uStack_2c;
  ushort uStack_2a;
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;

  arg0 = lwip_socket(2,2,0x11);
  if (arg0 < 0) {
    arg0 = -1;
  }
  else {
    uStack_28 = 0;
    uStack_24 = 0;
    uStack_20 = 0;
    uStack_1c = 0;
    uStack_18 = 0;
    uStack_14 = 0;
    _uStack_2c = CONCAT22(param_1 << 8 | param_1 >> 8,0x200);
    FUN_ram_4202b924("127.0.0.1",&uStack_28);
    iVar1 = lwip_bind(arg0,&uStack_2c,0x10);
    if (iVar1 < 0) {
      FUN_ram_420ab05c(arg0);
      arg0 = -1;
    }
  }
  return arg0;
}

// Audit label: lwip_socket_reference; entry: ram:42081cca; name: sdk_lwip_socket_reference_at_42081cca

undefined4
sdk_lwip_socket_reference_at_42081cca(undefined4 param_1,undefined4 param_2,int param_3,int param_4,undefined4 param_5,
                int *param_6)

{
  ushort uVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  int aiStack_24 [3];

  uStack_44 = 0;
  uStack_40 = 0;
  uStack_38 = 0;
  uStack_34 = 0;
  uStack_30 = 0;
  uStack_2c = 0;
  uStack_28 = 0;
  if (param_4 == 1) {
    uStack_40 = 2;
  }
  else if (param_4 == 2) {
    uStack_40 = 10;
  }
  uStack_3c = 1;
  iVar2 = (*(code *)&SUB_ram_40000534)();
  if (iVar2 == 0) {
    uVar4 = 0x101;
  }
  else {
    iVar3 = FUN_ram_420a35a2(iVar2,0,&uStack_44,aiStack_24);
    if ((iVar3 == 0) && (aiStack_24[0] != 0)) {
      FUN_ram_4038e4da(iVar2);
      iVar2 = lwip_socket(*(int *)(aiStack_24[0] + 4),*(int *)(aiStack_24[0] + 8),
                          *(int *)(aiStack_24[0] + 0xc));
      *param_6 = iVar2;
      if (iVar2 < 0) {
        uVar4 = FUN_ram_4038d3b4();
        FUN_ram_4038d2a2(1,&DAT_ram_3c0d2798,
                         "E (%lu) %s: Failed to create socket (family %d socktype %d protocol %d)\n"
                         ,uVar4,&DAT_ram_3c0d2798,*(undefined4 *)(aiStack_24[0] + 4),
                         *(undefined4 *)(aiStack_24[0] + 8),*(undefined4 *)(aiStack_24[0] + 0xc));
        FUN_ram_420a3584(aiStack_24[0]);
        uVar4 = 0x8002;
      }
      else {
        uVar1 = (ushort)((uint)param_3 >> 8);
        if (*(int *)(aiStack_24[0] + 4) == 2) {
          iVar2 = *(int *)(aiStack_24[0] + 0x14);
          *(ushort *)(iVar2 + 2) = (ushort)(param_3 << 8) | uVar1 & 0xff;
          (*(code *)&SUB_ram_4000048c)(param_5,iVar2,0x10);
        }
        else {
          if (*(int *)(aiStack_24[0] + 4) != 10) {
            uVar4 = FUN_ram_4038d3b4();
            FUN_ram_4038d2a2(1,&DAT_ram_3c0d2798,"E (%lu) %s: Unsupported protocol family %d\n",
                             uVar4,&DAT_ram_3c0d2798,*(undefined4 *)(aiStack_24[0] + 4));
            FUN_ram_420ab05c(*param_6);
            FUN_ram_420a3584(aiStack_24[0]);
            return 0x8003;
          }
          iVar2 = *(int *)(aiStack_24[0] + 0x14);
          *(ushort *)(iVar2 + 2) = (ushort)(param_3 << 8) | uVar1 & 0xff;
          *(undefined1 *)(iVar2 + 1) = 10;
          (*(code *)&SUB_ram_4000048c)(param_5,iVar2,0x1c);
        }
        FUN_ram_420a3584(aiStack_24[0]);
        uVar4 = 0;
      }
    }
    else {
      uVar4 = FUN_ram_4038d3b4();
      FUN_ram_4038d2a2(1,&DAT_ram_3c0d2798,
                       "E (%lu) %s: couldn\'t get hostname for :%s: getaddrinfo() returns %d, addrinfo=%p\n"
                       ,uVar4,&DAT_ram_3c0d2798,iVar2,iVar3,aiStack_24[0]);
      FUN_ram_4038e4da(iVar2);
      uVar4 = 0x8001;
    }
  }
  return uVar4;
}

// Audit label: lwip_recvfrom_reference; entry: ram:4201a8f6; name: sdk_lwip_recvfrom_reference_at_4201a8f6

void sdk_lwip_recvfrom_reference_at_4201a8f6(int param_1,void *param_2,uint param_3)

{
  lwip_recvfrom(param_1,param_2,param_3,0,(void *)0x0,(void *)0x0);
  return;
}

// Audit label: lwip_recvfrom_reference; entry: ram:4201a90a; name: sdk_lwip_recvfrom_reference_at_4201a90a

void sdk_lwip_recvfrom_reference_at_4201a90a(int param_1,void *param_2,uint param_3,int param_4)

{
  lwip_recvfrom(param_1,param_2,param_3,param_4,(void *)0x0,(void *)0x0);
  return;
}

// Audit label: lwip_sendto_reference; entry: ram:4203c9b2; name: sdk_lwip_sendto_reference_at_4203c9b2

int sdk_lwip_sendto_reference_at_4203c9b2(int param_1,ushort param_2,void *param_3,uint param_4)

{
  int iVar1;
  undefined2 uStack_2c;
  ushort uStack_2a;
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;

  uStack_28 = 0;
  uStack_24 = 0;
  uStack_20 = 0;
  uStack_1c = 0;
  uStack_18 = 0;
  uStack_14 = 0;
  _uStack_2c = CONCAT22(param_2 >> 8 | param_2 << 8,0x200);
  FUN_ram_4202b924("127.0.0.1",&uStack_28);
  iVar1 = lwip_sendto(param_1,param_3,param_4,0,&uStack_2c,0x10);
  if (iVar1 < 0) {
    iVar1 = -1;
  }
  return iVar1;
}

// Audit label: lwip_sendto_reference; entry: ram:4201aacc; name: sdk_lwip_sendto_reference_at_4201aacc

int sdk_lwip_sendto_reference_at_4201aacc(int param_1,void *param_2,uint param_3,uint param_4)

{
  undefined4 *puVar1;
  int iVar2;
  int iVar3;
  undefined4 *puVar4;
  undefined4 uVar5;
  uint uVar6;
  int aiStack_24 [3];

  puVar1 = (undefined4 *)FUN_ram_420187f4();
  if (puVar1 == (undefined4 *)0x0) {
    aiStack_24[0] = -1;
  }
  else if ((*(uint *)*puVar1 & 0xf0) == 0x10) {
    if ((param_4 & 0x10) == 0) {
      uVar6 = 1;
    }
    else {
      uVar6 = 3;
    }
    aiStack_24[0] = 0;
    iVar2 = FUN_ram_42032696(*puVar1,param_2,param_3,uVar6 | (int)param_4 >> 1 & 4U,aiStack_24);
    iVar3 = FUN_ram_420349e0();
    if (iVar3 != 0) {
      puVar4 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
      uVar5 = FUN_ram_420349e0(iVar2);
      *puVar4 = uVar5;
    }
    FUN_ram_42018718(puVar1);
    if (iVar2 != 0) {
      aiStack_24[0] = -1;
    }
  }
  else {
    FUN_ram_42018718();
    aiStack_24[0] = lwip_sendto(param_1,param_2,param_3,param_4,(void *)0x0,0);
  }
  return aiStack_24[0];
}

// Audit label: httpd_req_recv_reference; entry: ram:4203a36c; name: sdk_httpd_req_recv_reference_at_4203a36c

undefined4 sdk_httpd_req_recv_reference_at_4203a36c(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  undefined1 auStack_30 [36];

  iVar1 = param_1 + 0x80;
  iVar2 = *(int *)(param_1 + 0x290);
  do {
    uVar4 = *(uint *)(iVar2 + 0x18);
    if (uVar4 == 0) {
      FUN_ram_4203a206(iVar1);
      return 0;
    }
    if (0x20 < uVar4) {
      uVar4 = 0x20;
    }
    iVar3 = httpd_req_recv(iVar1,auStack_30,uVar4);
  } while (0 < iVar3);
  FUN_ram_4203a206(iVar1);
  return 0xffffffff;
}

// Audit label: httpd_req_get_hdr_value_str_reference; entry: ram:4203bd4a; name: sdk_httpd_req_get_hdr_value_str_reference_at_4203bd4a

undefined4 sdk_httpd_req_get_hdr_value_str_reference_at_4203bd4a(int param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  undefined1 auStack_21c [192];
  undefined4 uStack_15c;
  undefined4 uStack_158;
  undefined4 uStack_154;
  undefined4 uStack_150;
  undefined4 uStack_14c;
  undefined4 uStack_148;
  undefined4 uStack_144;
  undefined4 uStack_140;
  undefined4 uStack_13c;
  undefined4 uStack_138;
  undefined4 uStack_134;
  undefined4 uStack_130;
  undefined2 uStack_12c;
  undefined4 uStack_128;
  undefined1 auStack_124 [104];
  undefined1 auStack_bc [68];
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
  undefined1 uStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined2 uStack_24;
  undefined1 uStack_22;

  if ((param_1 == 0) || (*(int **)(param_1 + 0x210) == (int *)0x0)) {
    uVar2 = FUN_ram_4038d3b4();
    FUN_ram_4038d2a2(2,"httpd_ws","W (%lu) %s: %s: Argument is invalid\n",uVar2,"httpd_ws",
                     "httpd_ws_respond_server_handshake");
    uVar2 = 0x102;
  }
  else if (*(char *)(**(int **)(param_1 + 0x210) + 0xb9) == '\0') {
    uStack_24 = 0;
    uStack_22 = 0;
    iVar1 = httpd_req_get_hdr_value_str(param_1,"Sec-WebSocket-Version",&uStack_24,3);
    if (iVar1 == 0) {
      iVar1 = (*(code *)&SUB_ram_40000504)(&uStack_24,&DAT_ram_3c0ce030);
      if (iVar1 == 0) {
        uStack_40 = 0;
        uStack_3c = 0;
        uStack_38 = 0;
        uStack_34 = 0;
        uStack_30 = 0;
        uStack_2c = 0;
        uStack_28 = 0;
        iVar1 = httpd_req_get_hdr_value_str(param_1,"Sec-WebSocket-Key",&uStack_40,0x1c);
        if (iVar1 == 0) {
          uStack_64 = 0;
          uStack_60 = 0;
          uStack_5c = 0;
          uStack_58 = 0;
          uStack_54 = 0;
          uStack_50 = 0;
          uStack_4c = 0;
          uStack_48 = 0;
          uStack_44 = 0;
          uStack_78 = 0;
          uStack_74 = 0;
          uStack_70 = 0;
          uStack_6c = 0;
          uStack_68 = 0;
          (*(code *)&SUB_ram_40000488)(auStack_bc,0,0x42);
          (*(code *)&SUB_ram_40000498)(auStack_bc,&uStack_40);
          iVar1 = (*(code *)&SUB_ram_400004a8)(auStack_bc);
          (*(code *)&SUB_ram_4000048c)
                    (auStack_bc + iVar1,"258EAFA5-E914-47DA-95CA-C5AB0DC85B11",0x25);
          uVar2 = (*(code *)&SUB_ram_400004a8)(auStack_bc);
          FUN_ram_4204e254(auStack_124);
          iVar1 = FUN_ram_4204e296(auStack_124);
          if ((iVar1 == 0) && (iVar1 = FUN_ram_4204e2b8(auStack_124,auStack_bc,uVar2), iVar1 == 0))
          {
            iVar1 = FUN_ram_4204e39a(auStack_124,&uStack_78);
          }
          FUN_ram_4204e26c(auStack_124);
          if (iVar1 == 0) {
            uStack_128 = 0;
            FUN_ram_4204746a(&uStack_64,0x21,&uStack_128,&uStack_78,0x14);
            uStack_15c = 0;
            uStack_158 = 0;
            uStack_154 = 0;
            uStack_150 = 0;
            uStack_14c = 0;
            uStack_148 = 0;
            uStack_144 = 0;
            uStack_140 = 0;
            uStack_13c = 0;
            uStack_138 = 0;
            uStack_134 = 0;
            uStack_130 = 0;
            uStack_12c = 0;
            iVar1 = httpd_req_get_hdr_value_str(param_1,"Sec-WebSocket-Protocol",&uStack_15c,0x31);
            if (iVar1 == 0xb004) {
              uVar2 = FUN_ram_4038d3b4();
              FUN_ram_4038d2a2(2,"httpd_ws",
                               "W (%lu) %s: Sec-WebSocket-Protocol length exceeded buffer size of %lu, was truncated\n"
                               ,uVar2,"httpd_ws",0x32);
            }
            (*(code *)&SUB_ram_40000488)(auStack_21c,0,0xc0);
            uVar3 = (*(code *)&SUB_ram_400006ac)
                              (auStack_21c,0xc0,
                               "HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: %s\r\n"
                               ,&uStack_64);
            if (uVar3 < 0xc1) {
              iVar1 = FUN_ram_4203bc86(param_2,&uStack_15c,0x32);
              if (iVar1 != 0) {
                iVar1 = (*(code *)&SUB_ram_400006ac)
                                  (auStack_21c + uVar3,0xc0 - uVar3,"Sec-WebSocket-Protocol: %s\r\n"
                                   ,param_2);
                if (iVar1 < 1) {
                  uVar2 = FUN_ram_4038d3b4();
                  FUN_ram_4038d2a2(1,"httpd_ws",
                                   "E (%lu) %s: Error in response generation(snprintf of subprotocol returned %d, buffer size: %lu\n"
                                   ,uVar2,"httpd_ws",iVar1,0xc0);
                  return 0xffffffff;
                }
                uVar3 = uVar3 + iVar1;
                if (0xbf < uVar3) {
                  uVar2 = FUN_ram_4038d3b4();
                  FUN_ram_4038d2a2(1,"httpd_ws",
                                   "E (%lu) %s: Error in response generation(snprintf of subprotocol returned %d, desired response len: %d, buffer size: %lu\n"
                                   ,uVar2,"httpd_ws",iVar1,uVar3,0xc0);
                  return 0xffffffff;
                }
              }
              (*(code *)&SUB_ram_400006ac)(auStack_21c + uVar3,0xc0 - uVar3,"\r\n");
              uVar3 = uVar3 + 2;
              if (uVar3 < 0xc0) {
                iVar1 = FUN_ram_4203b010(param_1,auStack_21c,uVar3);
                uVar2 = 0;
                if (iVar1 < 0) {
                  uVar2 = FUN_ram_4038d3b4();
                  FUN_ram_4038d2a2(2,"httpd_ws","W (%lu) %s: %s: Failed to send the response\n",
                                   uVar2,"httpd_ws","httpd_ws_respond_server_handshake");
                  uVar2 = 0xffffffff;
                }
              }
              else {
                uVar2 = FUN_ram_4038d3b4();
                FUN_ram_4038d2a2(1,"httpd_ws",
                                 "E (%lu) %s: Error in response generation(snprintf of header terminal returned %d, desired response len: %d, buffer size: %lu\n"
                                 ,uVar2,"httpd_ws",2,uVar3,0xc0);
                uVar2 = 0xffffffff;
              }
            }
            else {
              uVar2 = FUN_ram_4038d3b4();
              FUN_ram_4038d2a2(2,"httpd_ws","W (%lu) %s: %s: Failed to prepare Tx buffer\n",uVar2,
                               "httpd_ws","httpd_ws_respond_server_handshake");
              uVar2 = 0xffffffff;
            }
          }
          else {
            uVar2 = FUN_ram_4038d3b4();
            FUN_ram_4038d2a2(1,"httpd_ws",
                             "E (%lu) %s: Error in calculating SHA1 sum , returned 0x%02X\n",uVar2,
                             "httpd_ws",iVar1);
            uVar2 = 0xffffffff;
          }
        }
        else {
          uVar2 = FUN_ram_4038d3b4();
          FUN_ram_4038d2a2(2,"httpd_ws","W (%lu) %s: %s: Cannot find client key\n",uVar2,"httpd_ws",
                           "httpd_ws_respond_server_handshake");
          uVar2 = 0x105;
        }
      }
      else {
        uVar2 = FUN_ram_4038d3b4();
        FUN_ram_4038d2a2(2,"httpd_ws",
                         "W (%lu) %s: %s: \"Sec-WebSocket-Version\" is not \"13\", it is: %s\n",
                         uVar2,"httpd_ws","httpd_ws_respond_server_handshake",&uStack_24);
        uVar2 = 0x10a;
      }
    }
    else {
      uVar2 = FUN_ram_4038d3b4();
      FUN_ram_4038d2a2(2,"httpd_ws","W (%lu) %s: %s: \"Sec-WebSocket-Version\" is not found\n",uVar2
                       ,"httpd_ws","httpd_ws_respond_server_handshake");
      uVar2 = 0x105;
    }
  }
  else {
    uVar2 = FUN_ram_4038d3b4();
    FUN_ram_4038d2a2(2,"httpd_ws",
                     "W (%lu) %s: %s: State is invalid - Handshake has been performed\n",uVar2,
                     "httpd_ws","httpd_ws_respond_server_handshake");
    uVar2 = 0x103;
  }
  return uVar2;
}

// Audit label: httpd_req_get_hdr_value_str_reference; entry: ram:4203a5f8; name: sdk_httpd_req_get_hdr_value_str_reference_at_4203a5f8

undefined4 sdk_httpd_req_get_hdr_value_str_reference_at_4203a5f8(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  short sVar3;
  int iVar4;
  char *pcVar5;
  undefined4 *puVar6;
  int iVar7;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined2 uStack_24;

  iVar1 = *(int *)(param_1 + 0x18);
  iVar7 = *(int *)(iVar1 + 0x28);
  puVar6 = *(undefined4 **)(iVar7 + 0x210);
  if (*(int *)(iVar1 + 0x2c) == 1) {
    iVar4 = FUN_ram_42039a9a();
    if (iVar4 != 0) {
      *(undefined4 *)(iVar1 + 0x2c) = 6;
      return 0xffffffff;
    }
  }
  else {
    if (*(int *)(iVar1 + 0x2c) != 3) {
      uVar2 = FUN_ram_4038d3b4();
      FUN_ram_4038d2a2(1,"httpd_parse","E (%lu) %s: %s: unexpected state transition\n",uVar2,
                       "httpd_parse","cb_headers_complete");
      *(undefined4 *)(iVar1 + 0x30) = 0;
      *(undefined4 *)(iVar1 + 0x2c) = 6;
      return 0xffffffff;
    }
    pcVar5 = (char *)(*(int *)(iVar1 + 0x34) + *(int *)(iVar1 + 0x38));
    iVar4 = *(int *)(iVar1 + 0x44) - ((int)pcVar5 - puVar6[1]);
    if (iVar4 < 2) {
      uVar2 = FUN_ram_4038d3b4();
      FUN_ram_4038d2a2(1,"httpd_parse",
                       "E (%lu) %s: %s: invalid length of data remaining to be parsed\n",uVar2,
                       "httpd_parse","cb_headers_complete");
      *(undefined4 *)(iVar1 + 0x30) = 0;
      *(undefined4 *)(iVar1 + 0x2c) = 6;
      return 0xffffffff;
    }
    sVar3 = 2;
    while ((iVar4 != 0 && (sVar3 != 0))) {
      if (*pcVar5 == '\n') {
        sVar3 = sVar3 + -1;
      }
      *pcVar5 = '\0';
      pcVar5 = pcVar5 + 1;
      iVar4 = iVar4 + -1;
    }
    if (sVar3 != 0) {
      uVar2 = FUN_ram_4038d3b4();
      FUN_ram_4038d2a2(1,"httpd_parse","E (%lu) %s: %s: incomplete termination of headers\n",uVar2,
                       "httpd_parse","cb_headers_complete");
      *(undefined4 *)(iVar1 + 0x30) = 3;
      *(undefined4 *)(iVar1 + 0x2c) = 6;
      return 0xffffffff;
    }
    *(char **)(iVar1 + 0x34) = pcVar5;
    puVar6[10] = puVar6[10] + 1;
  }
  iVar4 = *(int *)(param_1 + 8);
  if (iVar4 == -1) {
    iVar4 = 0;
  }
  *(int *)(iVar7 + 0x20c) = iVar4;
  if (*(int *)(param_1 + 0x14) < 0) {
    uStack_2c = 0x73626577;
    uStack_28 = 0x656b636f;
    uStack_24 = 0x74;
    iVar4 = httpd_req_get_hdr_value_str(iVar7,"Upgrade",&uStack_2c,10);
    if (iVar4 == 0) {
      iVar4 = (*(code *)&SUB_ram_40000504)("websocket",&uStack_2c);
      if (iVar4 == 0) {
        *(undefined1 *)(puVar6 + 0x15) = 1;
        goto LAB_ram_4203a6c6;
      }
      uVar2 = FUN_ram_4038d3b4();
      FUN_ram_4038d2a2(2,"httpd_parse","W (%lu) %s: %s: Upgrade header found but it\'s %s\n",uVar2,
                       "httpd_parse","cb_headers_complete",&uStack_2c);
      *(undefined4 *)(iVar1 + 0x30) = 3;
      *(undefined4 *)(iVar1 + 0x2c) = 6;
    }
    else {
      uVar2 = FUN_ram_4038d3b4();
      FUN_ram_4038d2a2(2,"httpd_parse",
                       "W (%lu) %s: %s: Upgrade header does not match the length of \"websocket\"\n"
                       ,uVar2,"httpd_parse","cb_headers_complete");
      *(undefined4 *)(iVar1 + 0x30) = 3;
      *(undefined4 *)(iVar1 + 0x2c) = 6;
    }
    uVar2 = 0xffffffff;
  }
  else {
LAB_ram_4203a6c6:
    *(undefined4 *)(iVar1 + 0x2c) = 4;
    puVar6[6] = *(undefined4 *)(iVar7 + 0x20c);
    FUN_ram_420390f2(3,*puVar6);
    uVar2 = 0;
  }
  return uVar2;
}

// Audit label: esp_http_client_cleanup_reference; entry: ram:4203dd76; name: esp_http_client_init

void * esp_http_client_init(int *param_1)

{
  bool bVar1;
  void *arg0;
  int iVar2;
  int *piVar3;
  int iVar4;
  undefined4 uVar5;
  char *pcVar6;
  undefined4 auStack_24 [4];

  auStack_24[0] = 0;
  arg0 = (void *)FUN_ram_4038e4e8(1,0xe0);
  if (arg0 != (void *)0x0) {
    iVar2 = FUN_ram_4038e4e8(1,0x20);
    *(int *)((int)arg0 + 0x10) = iVar2;
    if (iVar2 != 0) {
      iVar2 = FUN_ram_4038e4e8(1,0x28);
      *(int *)((int)arg0 + 0x14) = iVar2;
      if (iVar2 != 0) {
        iVar2 = FUN_ram_4038e4e8(1,0x30);
        *(int *)((int)arg0 + 0x2c) = iVar2;
        if (iVar2 != 0) {
          piVar3 = (int *)FUN_ram_4038e4e8(1,0x30);
          *(int **)((int)arg0 + 0x20) = piVar3;
          if (piVar3 != (int *)0x0) {
            iVar2 = FUN_ram_4203ede0();
            *piVar3 = iVar2;
            if (iVar2 != 0) {
              iVar2 = *(int *)((int)arg0 + 0x20);
              iVar4 = FUN_ram_4038e4e8(1,0x18);
              *(int *)(iVar2 + 4) = iVar4;
              if (iVar4 != 0) {
                piVar3 = (int *)FUN_ram_4038e4e8(1,0x30);
                *(int **)((int)arg0 + 0x24) = piVar3;
                if (piVar3 != (int *)0x0) {
                  iVar2 = FUN_ram_4203ede0();
                  *piVar3 = iVar2;
                  if (iVar2 != 0) {
                    iVar2 = *(int *)((int)arg0 + 0x24);
                    iVar4 = FUN_ram_4038e4e8(1,0x18);
                    *(int *)(iVar2 + 4) = iVar4;
                    if (iVar4 != 0) {
                      iVar2 = FUN_ram_42083698();
                      *(int *)((int)arg0 + 0x18) = iVar2;
                      if ((((iVar2 == 0) || (iVar2 = FUN_ram_42084660(), iVar2 == 0)) ||
                          (iVar4 = FUN_ram_4208398e(iVar2,0x50), iVar4 != 0)) ||
                         (iVar4 = FUN_ram_420836fc(*(undefined4 *)((int)arg0 + 0x18),iVar2,
                                                   &DAT_ram_3c0ce7e0), iVar4 != 0)) {
                        uVar5 = FUN_ram_4038d3b4();
                        FUN_ram_4038d2a2(1,"HTTP_CLIENT","E (%lu) %s: Error initialize transport\n",
                                         uVar5,"HTTP_CLIENT");
                      }
                      else {
                        iVar4 = FUN_ram_4203ca7c(param_1[0x25],auStack_24);
                        if (iVar4 == 0) {
                          FUN_ram_4208453a(iVar2,auStack_24[0]);
                          iVar2 = FUN_ram_4203cf02(arg0,param_1,iVar2);
                          if (iVar2 == 0) {
                            uVar5 = FUN_ram_4038d3b4();
                            FUN_ram_4038d2a2(1,"HTTP_CLIENT",
                                             "E (%lu) %s: %s(%d): Failed to set TCP config\n",uVar5,
                                             "HTTP_CLIENT","esp_http_client_init",0x329);
                          }
                          else {
                            iVar2 = FUN_ram_420845b6();
                            if (((iVar2 == 0) || (iVar4 = FUN_ram_4208398e(iVar2,0x1bb), iVar4 != 0)
                                ) || (iVar4 = FUN_ram_420836fc(*(undefined4 *)((int)arg0 + 0x18),
                                                               iVar2,"https"), iVar4 != 0)) {
                              uVar5 = FUN_ram_4038d3b4();
                              FUN_ram_4038d2a2(1,"HTTP_CLIENT",
                                               "E (%lu) %s: Error initialize SSL Transport\n",uVar5,
                                               "HTTP_CLIENT");
                            }
                            else {
                              FUN_ram_4208453a(iVar2,auStack_24[0]);
                              iVar4 = FUN_ram_4203cf02(arg0,param_1,iVar2);
                              if (iVar4 == 0) {
                                uVar5 = FUN_ram_4038d3b4();
                                FUN_ram_4038d2a2(1,"HTTP_CLIENT",
                                                 "E (%lu) %s: %s(%d): Failed to set SSL config\n",
                                                 uVar5,"HTTP_CLIENT","esp_http_client_init",0x339);
                              }
                              else {
                                if (param_1[0x1e] == 0) {
                                  if (*(char *)((int)param_1 + 0x71) == '\0') {
                                    iVar4 = param_1[8];
                                    if (iVar4 != 0) {
                                      if (param_1[9] == 0) {
                                        uVar5 = (*(code *)&SUB_ram_400004a8)(iVar4);
                                        FUN_ram_42084512(iVar2,iVar4,uVar5);
                                      }
                                      else {
                                        FUN_ram_42084520(iVar2,iVar4);
                                      }
                                    }
                                  }
                                  else {
                                    FUN_ram_420844fa(iVar2);
                                  }
                                }
                                else {
                                  FUN_ram_42084598(iVar2);
                                }
                                iVar4 = param_1[10];
                                if (iVar4 != 0) {
                                  if (param_1[0xb] == 0) {
                                    uVar5 = (*(code *)&SUB_ram_400004a8)(iVar4);
                                    FUN_ram_4208452c(iVar2,iVar4,uVar5);
                                  }
                                  else {
                                    FUN_ram_42084544(iVar2,iVar4);
                                  }
                                }
                                FUN_ram_42084508(iVar2,param_1[0x10]);
                                iVar4 = param_1[0xc];
                                if (iVar4 != 0) {
                                  if (param_1[0xd] == 0) {
                                    uVar5 = (*(code *)&SUB_ram_400004a8)(iVar4);
                                    FUN_ram_42084550(iVar2,iVar4,uVar5);
                                  }
                                  else {
                                    FUN_ram_4208456a(iVar2,iVar4);
                                  }
                                }
                                if ((param_1[0xe] != 0) && (param_1[0xf] != 0)) {
                                  FUN_ram_4208455e(iVar2);
                                }
                                if (*(char *)((int)param_1 + 0x72) != '\0') {
                                  FUN_ram_42084580(iVar2);
                                }
                                if (param_1[0x1d] != 0) {
                                  FUN_ram_4208458e(iVar2);
                                }
                                iVar2 = FUN_ram_4203d002(arg0,param_1);
                                if (iVar2 == 0) {
                                  piVar3 = *(int **)(*(int *)((int)arg0 + 0x20) + 4);
                                  iVar2 = FUN_ram_4038e4be(*(undefined4 *)((int)arg0 + 0x90));
                                  *piVar3 = iVar2;
                                  if (iVar2 != 0) {
                                    piVar3 = *(int **)(*(int *)((int)arg0 + 0x24) + 4);
                                    iVar2 = FUN_ram_4038e4be(*(undefined4 *)((int)arg0 + 0x8c));
                                    *piVar3 = iVar2;
                                    if (iVar2 != 0) {
                                      pcVar6 = (char *)param_1[0x11];
                                      if (pcVar6 == (char *)0x0) {
                                        pcVar6 = "ESP32 HTTP Client/1.0";
                                      }
                                      if ((param_1[1] == 0) || (param_1[6] == 0)) {
                                        if (*param_1 == 0) {
                                          uVar5 = FUN_ram_4038d3b4();
                                          FUN_ram_4038d2a2(1,"HTTP_CLIENT",

                                                  "E (%lu) %s: config should have either URL or host & path\n"
                                                  ,uVar5,"HTTP_CLIENT");
                                        }
                                        else {
                                          iVar2 = FUN_ram_4203daea(arg0);
                                          if (iVar2 == 0) {
                                            if (*(int *)((int)arg0 + 0x50) == 0) {
                                              uVar5 = FUN_ram_4038d3b4();
                                              FUN_ram_4038d2a2(1,"HTTP_CLIENT",
                                                               "E (%lu) %s: invalid host\n",uVar5,
                                                               "HTTP_CLIENT");
                                            }
                                            else {
                                              iVar2 = FUN_ram_4203d274(*(int *)((int)arg0 + 0x50),
                                                                       *(undefined4 *)
                                                                        ((int)arg0 + 0x54));
                                              if (iVar2 == 0) {
                                                uVar5 = FUN_ram_4038d3b4();
                                                FUN_ram_4038d2a2(1,"HTTP_CLIENT",

                                                  "E (%lu) %s: Failed to allocate memory for host header\n"
                                                  ,uVar5,"HTTP_CLIENT");
                                              }
                                              else {
                                                iVar4 = FUN_ram_4203d3a6(arg0,"User-Agent",pcVar6);
                                                bVar1 = false;
                                                if (iVar4 == 0) {
                                                  iVar4 = FUN_ram_4203d3a6(arg0,&DAT_ram_3c0c3204,
                                                                           iVar2);
                                                  if (iVar4 == 0) {
                                                    bVar1 = true;
                                                  }
                                                  else {
                                                    bVar1 = false;
                                                  }
                                                }
                                                FUN_ram_4038e4da(iVar2);
                                                if (bVar1) goto LAB_ram_4203dfea;
                                                uVar5 = FUN_ram_4038d3b4();
                                                FUN_ram_4038d2a2(1,"HTTP_CLIENT",

                                                  "E (%lu) %s: Error while setting default configurations\n"
                                                  ,uVar5,"HTTP_CLIENT");
                                              }
                                            }
                                          }
                                          else {
                                            uVar5 = FUN_ram_4038d3b4();
                                            FUN_ram_4038d2a2(1,"HTTP_CLIENT",
                                                             "E (%lu) %s: Failed to set URL\n",uVar5
                                                             ,"HTTP_CLIENT");
                                          }
                                        }
                                      }
                                      else if (*(int *)((int)arg0 + 0x50) == 0) {
                                        uVar5 = FUN_ram_4038d3b4();
                                        FUN_ram_4038d2a2(1,"HTTP_CLIENT",
                                                         "E (%lu) %s: invalid host\n",uVar5,
                                                         "HTTP_CLIENT");
                                      }
                                      else {
                                        iVar2 = FUN_ram_4203d274(*(int *)((int)arg0 + 0x50),
                                                                 *(undefined4 *)((int)arg0 + 0x54));
                                        if (iVar2 == 0) {
                                          uVar5 = FUN_ram_4038d3b4();
                                          FUN_ram_4038d2a2(1,"HTTP_CLIENT",

                                                  "E (%lu) %s: Failed to allocate memory for host header\n"
                                                  ,uVar5,"HTTP_CLIENT");
                                        }
                                        else {
                                          iVar4 = FUN_ram_4203d3a6(arg0,"User-Agent",pcVar6);
                                          bVar1 = false;
                                          if (iVar4 == 0) {
                                            iVar4 = FUN_ram_4203d3a6(arg0,&DAT_ram_3c0c3204,iVar2);
                                            if (iVar4 == 0) {
                                              bVar1 = true;
                                            }
                                            else {
                                              bVar1 = false;
                                            }
                                          }
                                          FUN_ram_4038e4da(iVar2);
                                          if (bVar1) {
LAB_ram_4203dfea:
                                            *(byte *)((int)arg0 + 0xdc) =
                                                 *(byte *)((int)arg0 + 0xdc) | 1;
                                            **(undefined4 **)((int)arg0 + 0x14) = &LAB_ram_4203ca48;
                                            *(undefined1 **)(*(int *)((int)arg0 + 0x14) + 4) =
                                                 &LAB_ram_4203ca58;
                                            *(undefined1 **)(*(int *)((int)arg0 + 0x14) + 8) =
                                                 &LAB_ram_4203ca5c;
                                            *(code **)(*(int *)((int)arg0 + 0x14) + 0xc) =
                                                 FUN_ram_4203ce06;
                                            *(code **)(*(int *)((int)arg0 + 0x14) + 0x10) =
                                                 FUN_ram_4203ce3e;
                                            *(code **)(*(int *)((int)arg0 + 0x14) + 0x14) =
                                                 FUN_ram_4203cb8c;
                                            *(code **)(*(int *)((int)arg0 + 0x14) + 0x18) =
                                                 FUN_ram_4203cce2;
                                            *(undefined1 **)(*(int *)((int)arg0 + 0x14) + 0x1c) =
                                                 &LAB_ram_4203ca60;
                                            *(undefined1 **)(*(int *)((int)arg0 + 0x14) + 0x24) =
                                                 &LAB_ram_4203ca6c;
                                            *(undefined1 **)(*(int *)((int)arg0 + 0x14) + 0x20) =
                                                 &LAB_ram_4203ca70;
                                            *(void **)(*(int *)((int)arg0 + 0x10) + 0x18) = arg0;
                                            *(void **)((int)arg0 + 0x9c) = arg0;
                                            *(undefined4 *)((int)arg0 + 0x80) = 1;
                                            return arg0;
                                          }
                                          uVar5 = FUN_ram_4038d3b4();
                                          FUN_ram_4038d2a2(1,"HTTP_CLIENT",

                                                  "E (%lu) %s: Error while setting default configurations\n"
                                                  ,uVar5,"HTTP_CLIENT");
                                        }
                                      }
                                      goto LAB_ram_4203e0d0;
                                    }
                                  }
                                  uVar5 = FUN_ram_4038d3b4();
                                  FUN_ram_4038d2a2(1,"HTTP_CLIENT","E (%lu) %s: Allocation failed\n"
                                                   ,uVar5,"HTTP_CLIENT");
                                }
                                else {
                                  uVar5 = FUN_ram_4038d3b4();
                                  FUN_ram_4038d2a2(1,"HTTP_CLIENT",
                                                   "E (%lu) %s: Error set configurations\n",uVar5,
                                                   "HTTP_CLIENT");
                                }
                              }
                            }
                          }
                        }
                        else {
                          uVar5 = FUN_ram_4038d3b4();
                          FUN_ram_4038d2a2(1,"HTTP_CLIENT",
                                           "E (%lu) %s: %s(%d): Failed to convert addr type %d\n",
                                           uVar5,"HTTP_CLIENT","esp_http_client_init",0x326,
                                           param_1[0x25]);
                        }
                      }
                      goto LAB_ram_4203e0d0;
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
  uVar5 = FUN_ram_4038d3b4();
  FUN_ram_4038d2a2(1,"HTTP_CLIENT","E (%lu) %s: Error allocate memory\n",uVar5,"HTTP_CLIENT");
LAB_ram_4203e0d0:
  esp_http_client_cleanup(arg0);
  return (void *)0x0;
}

// Audit label: esp_flash_read_reference; entry: ram:4207bb52; name: sdk_esp_flash_read_reference_at_4207bb52

int sdk_esp_flash_read_reference_at_4207bb52(int *param_1,uint param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  undefined4 uStack_18;
  undefined4 uStack_14;

  if (param_1 != (int *)0x0) {
    if ((uint)param_1[4] < param_2) {
      iVar1 = 0x102;
    }
    else if (param_1[4] - param_2 < param_4) {
      iVar1 = 0x104;
    }
    else if (*(char *)((int)param_1 + 0x29) == '\0') {
      iVar1 = esp_flash_read(*param_1,param_3,param_1[3] + param_2);
    }
    else if (*param_1 == DAT_ram_3fcc3ae0) {
      iVar1 = FUN_ram_4207bab4(param_1,param_2,param_4,0,&uStack_14,&uStack_18);
      if (iVar1 == 0) {
        (*(code *)&SUB_ram_4000048c)(param_3,uStack_14,param_4);
        FUN_ram_4207bb44(uStack_18);
      }
    }
    else {
      iVar1 = 0x106;
    }
    return iVar1;
  }
                    /* WARNING: Subroutine does not return */
  FUN_ram_4038e2f0("partition_target.c",0x1d,"esp_partition_read","partition != NULL");
}

// Audit label: esp_flash_read_reference; entry: ram:4207b976; name: sdk_esp_flash_read_reference_at_4207b976

undefined4 sdk_esp_flash_read_reference_at_4207b976(undefined4 *param_1,uint param_2,undefined4 param_3,uint param_4)

{
  undefined4 uVar1;

  if (param_1 != (undefined4 *)0x0) {
    if ((uint)param_1[4] < param_2) {
      uVar1 = 0x102;
    }
    else if (param_1[4] - param_2 < param_4) {
      uVar1 = 0x104;
    }
    else {
      uVar1 = esp_flash_read(*param_1,param_3,param_1[3] + param_2);
    }
    return uVar1;
  }
                    /* WARNING: Subroutine does not return */
  FUN_ram_4038e2f0("partition_target.c",0x5e,"esp_partition_read_raw","partition != NULL");
}

// Audit label: esp_flash_write_reference; entry: ram:40392472; name: esp_flash_write

int esp_flash_write(undefined4 *param_1,undefined1 *param_2,uint param_3,uint param_4)

{
  char cVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  undefined1 *puVar7;
  uint uVar8;
  undefined1 *puVar9;
  undefined4 *puStack_54;
  undefined1 auStack_50 [40];

  puStack_54 = param_1;
  iVar2 = (**(code **)(PTR_PTR_ram_3fcb5974 + 8))(&puStack_54);
  if (iVar2 == 0) {
    if (*(int *)(puStack_54[1] + 0x44) == 0) {
      iVar2 = 0x6005;
    }
    else {
      if ((puStack_54 != (undefined4 *)0x0) && (*(code **)(puStack_54[2] + 8) != (code *)0x0)) {
        iVar3 = (**(code **)(puStack_54[2] + 8))(puStack_54[3],param_3,param_4);
        if (iVar3 == 0x10d) {
          return 0x10d;
        }
        if (iVar3 != 0) {
                    /* WARNING: Subroutine does not return */
          FUN_ram_4038e23e();
        }
      }
      if (param_2 == (undefined1 *)0x0) {
        iVar2 = 0x102;
      }
      else if ((uint)puStack_54[5] < param_3) {
        iVar2 = 0x102;
      }
      else if (puStack_54[5] - param_3 < param_4) {
        iVar2 = 0x102;
      }
      else if (param_4 != 0) {
        puVar9 = param_2 + -0x3fca0000;
        cVar1 = (**(code **)(*(int *)*puStack_54 + 0x24))((int *)*puStack_54,param_2);
        uVar5 = param_4;
        uVar8 = param_3;
        while( true ) {
          uVar6 = uVar5;
          if (puVar9 < (undefined1 *)0x40000 || cVar1 != '\0') {
            puVar7 = param_2;
            if (0x2000 < uVar5) {
              uVar6 = 0x2000;
            }
          }
          else {
            if (0x20 < uVar5) {
              uVar6 = 0x20;
            }
            (*(code *)&SUB_ram_4000048c)(auStack_50,param_2,uVar6);
            puVar7 = auStack_50;
          }
          if ((*(code **)(puStack_54[1] + 0x68) != (code *)0x0) &&
             (iVar2 = (**(code **)(puStack_54[1] + 0x68))(puStack_54,0), iVar2 != 0)) {
            return iVar2;
          }
          iVar2 = (**(code **)PTR_PTR_ram_3fcb5974)(puStack_54);
          if (iVar2 != 0) {
            uVar4 = 0;
            goto LAB_ram_403925b8;
          }
          iVar2 = (**(code **)(puStack_54[1] + 0x44))(puStack_54,puVar7,uVar8,uVar6);
          uVar5 = uVar5 - uVar6;
          if (param_4 <= uVar5) {
                    /* WARNING: Subroutine does not return */
            FUN_ram_4038e2f0("esp_flash_api.c",0x494,"esp_flash_write","len_remain < length");
          }
          if (iVar2 != 0) {
            uVar4 = 1;
            goto LAB_ram_403925b8;
          }
          if (uVar5 == 0) {
            iVar2 = (**(code **)(PTR_PTR_ram_3fcb5974 + 0xc))
                              (puStack_54,0,1,param_3,param_4,*(code **)(PTR_PTR_ram_3fcb5974 + 0xc)
                              );
            return iVar2;
          }
          iVar2 = (**(code **)(PTR_PTR_ram_3fcb5974 + 4))(puStack_54,0);
          if (iVar2 != 0) break;
          uVar8 = uVar8 + uVar6;
          param_2 = param_2 + uVar6;
        }
        uVar4 = 1;
LAB_ram_403925b8:
        iVar3 = (**(code **)(PTR_PTR_ram_3fcb5974 + 0xc))
                          (puStack_54,iVar2,uVar4,param_3,param_4,
                           *(code **)(PTR_PTR_ram_3fcb5974 + 0xc));
        if ((iVar3 != 0) && (*(int *)(gp + -0x7e8) != 0)) {
          (*(code *)&SUB_ram_40000034)
                    (s_E__s__restore_cache_fail_ram_3fcb5958,s_spi_flash_ram_3fcb5988);
        }
      }
    }
  }
  return iVar2;
}

// Audit label: esp_flash_erase_region_reference; entry: ram:40391e94; name: esp_flash_erase_region

int esp_flash_erase_region(int param_1,uint param_2,uint param_3)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  uint *puVar5;
  code *pcVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  int aiStack_34 [3];
  uint uStack_28;
  uint uStack_24;

  aiStack_34[0] = param_1;
  iVar2 = (**(code **)(PTR_PTR_ram_3fcb5974 + 8))(aiStack_34);
  if (iVar2 == 0) {
    if (*(int *)(*(int *)(aiStack_34[0] + 4) + 0x18) == 0) {
      iVar2 = 0x6005;
    }
    else if (*(int *)(*(int *)(aiStack_34[0] + 4) + 0x1c) == 0) {
      iVar2 = 0x6005;
    }
    else {
      if ((aiStack_34[0] != 0) &&
         (pcVar6 = *(code **)(*(int *)(aiStack_34[0] + 8) + 8), pcVar6 != (code *)0x0)) {
        iVar3 = (*pcVar6)(*(undefined4 *)(aiStack_34[0] + 0xc),param_2,param_3);
        if (iVar3 == 0x10d) {
          return 0x10d;
        }
        if (iVar3 != 0) {
                    /* WARNING: Subroutine does not return */
          FUN_ram_4038e23e();
        }
      }
      iVar3 = *(int *)(aiStack_34[0] + 4);
      if (*(int *)(iVar3 + 0x1c) == 0) {
        uVar9 = 0;
      }
      else {
        uVar9 = *(uint *)(iVar3 + 0x24);
      }
      uVar8 = *(uint *)(iVar3 + 0x20);
      if (uVar8 == 0) {
        iVar2 = 0x6003;
      }
      else if (uVar9 % uVar8 == 0) {
        if (*(uint *)(aiStack_34[0] + 0x14) < param_2) {
          iVar2 = 0x102;
        }
        else if (*(uint *)(aiStack_34[0] + 0x14) - param_2 < param_3) {
          iVar2 = 0x102;
        }
        else if (param_2 % uVar8 == 0) {
          if (param_3 % uVar8 == 0) {
            if (param_3 != 0) {
              if ((*(int *)(iVar3 + 0x38) != 0) && (*(char *)(iVar3 + 0x30) != '\0')) {
                iVar2 = (**(code **)PTR_PTR_ram_3fcb5974)();
                if (iVar2 != 0) {
                  return iVar2;
                }
                uStack_28 = 0;
                uStack_24 = 0;
                iVar2 = (**(code **)(*(int *)(aiStack_34[0] + 4) + 0x38))(aiStack_34[0],&uStack_28);
                if ((iVar2 == 0) && (uStack_28 != 0 || uStack_24 != 0)) {
                  iVar2 = 0;
                  uVar10 = 0;
                  while (((int)uVar10 < (int)(uint)*(byte *)(*(int *)(aiStack_34[0] + 4) + 0x30) &&
                         (iVar2 == 0))) {
                    puVar5 = (uint *)(*(int *)(*(int *)(aiStack_34[0] + 4) + 0x34) + uVar10 * 8);
                    if ((int)(uVar10 - 0x20) < 0) {
                      uVar7 = uStack_28 >> (uVar10 & 0x1f) |
                              (uStack_24 << 1) << (0x1f - uVar10 & 0x1f);
                    }
                    else {
                      uVar7 = uStack_24 >> (uVar10 - 0x20 & 0x1f);
                    }
                    if ((((uVar7 & 1) != 0) && (uVar7 = *puVar5, uVar7 < param_2 + param_3)) &&
                       (param_2 < puVar5[1] + uVar7)) {
                      iVar2 = 0x6006;
                    }
                    uVar10 = uVar10 + 1;
                  }
                }
                iVar2 = (**(code **)(PTR_PTR_ram_3fcb5974 + 4))(aiStack_34[0]);
              }
              uVar10 = param_3;
              uVar7 = param_2;
              if (iVar2 == 0) {
                do {
                  pcVar6 = *(code **)(*(int *)(aiStack_34[0] + 4) + 0x68);
                  if ((pcVar6 != (code *)0x0) && (iVar2 = (*pcVar6)(aiStack_34[0],0), iVar2 != 0)) {
                    return iVar2;
                  }
                  iVar2 = (**(code **)PTR_PTR_ram_3fcb5974)(aiStack_34[0]);
                  if (iVar2 != 0) {
                    uVar4 = 0;
                    goto LAB_ram_40392070;
                  }
                  if (((uVar9 == 0) || (uVar10 < uVar9)) || (uVar7 % uVar9 != 0)) {
                    iVar2 = (**(code **)(*(int *)(aiStack_34[0] + 4) + 0x18))(aiStack_34[0],uVar7);
                    uVar1 = uVar8;
                  }
                  else {
                    iVar2 = (**(code **)(*(int *)(aiStack_34[0] + 4) + 0x1c))(aiStack_34[0],uVar7);
                    uVar1 = uVar9;
                  }
                  uVar10 = uVar10 - uVar1;
                  if (param_3 <= uVar10) {
                    /* WARNING: Subroutine does not return */
                    FUN_ram_4038e2f0("esp_flash_api.c",0x2e9,"esp_flash_erase_region",
                                     "len_remain < len");
                  }
                  if (iVar2 != 0) {
                    uVar4 = 1;
                    goto LAB_ram_40392070;
                  }
                  if (uVar10 == 0) {
                    uVar4 = 1;
                    goto LAB_ram_40392070;
                  }
                  iVar2 = (**(code **)(PTR_PTR_ram_3fcb5974 + 4))(aiStack_34[0],0);
                  uVar7 = uVar7 + uVar1;
                } while (iVar2 == 0);
                uVar4 = 1;
LAB_ram_40392070:
                iVar2 = (**(code **)(PTR_PTR_ram_3fcb5974 + 0xc))
                                  (aiStack_34[0],iVar2,uVar4,param_2,param_3,
                                   *(code **)(PTR_PTR_ram_3fcb5974 + 0xc));
              }
            }
          }
          else {
            iVar2 = 0x102;
          }
        }
        else {
          iVar2 = 0x102;
        }
      }
      else {
        iVar2 = 0x6003;
      }
    }
  }
  return iVar2;
}

// Audit label: httpd_register_uri_handler_reference; entry: ram:4203b848; name: httpd_register_uri_handler

undefined4 httpd_register_uri_handler(int param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  int *piVar2;
  undefined4 *puVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;

  if (param_1 == 0) {
    uVar1 = 0x102;
  }
  else if (param_2 == (undefined4 *)0x0) {
    uVar1 = 0x102;
  }
  else {
    uVar1 = *param_2;
    uVar4 = (*(code *)&SUB_ram_400004a8)(uVar1);
    iVar5 = FUN_ram_4203b7aa(param_1,uVar1,uVar4,param_2[1],0);
    if (iVar5 == 0) {
      for (iVar5 = 0; iVar5 < (int)(uint)*(ushort *)(param_1 + 0x1e); iVar5 = iVar5 + 1) {
        iVar6 = iVar5 * 4;
        piVar2 = (int *)(*(int *)(param_1 + 0x7c) + iVar6);
        if (*piVar2 == 0) {
          iVar5 = FUN_ram_4038e4be(0x18);
          *piVar2 = iVar5;
          puVar3 = *(undefined4 **)(*(int *)(param_1 + 0x7c) + iVar6);
          if (puVar3 == (undefined4 *)0x0) {
            return 0xb007;
          }
          uVar1 = (*(code *)&SUB_ram_40000510)(*param_2);
          *puVar3 = uVar1;
          piVar2 = *(int **)(*(int *)(param_1 + 0x7c) + iVar6);
          if (*piVar2 != 0) {
            piVar2[1] = param_2[1];
            *(undefined4 *)(*(int *)(*(int *)(param_1 + 0x7c) + iVar6) + 8) = param_2[2];
            *(undefined4 *)(*(int *)(*(int *)(param_1 + 0x7c) + iVar6) + 0xc) = param_2[3];
            *(undefined1 *)(*(int *)(*(int *)(param_1 + 0x7c) + iVar6) + 0x10) =
                 *(undefined1 *)(param_2 + 4);
            *(undefined1 *)(*(int *)(*(int *)(param_1 + 0x7c) + iVar6) + 0x11) =
                 *(undefined1 *)((int)param_2 + 0x11);
            if (param_2[5] == 0) {
              *(undefined4 *)(*(int *)(*(int *)(param_1 + 0x7c) + iVar6) + 0x14) = 0;
            }
            else {
              iVar5 = *(int *)(*(int *)(param_1 + 0x7c) + iVar6);
              uVar1 = (*(code *)&SUB_ram_40000510)();
              *(undefined4 *)(iVar5 + 0x14) = uVar1;
              puVar3 = *(undefined4 **)(*(int *)(param_1 + 0x7c) + iVar6);
              if (puVar3[5] == 0) {
                FUN_ram_4038e4da(*puVar3);
                FUN_ram_4038e4da(*(undefined4 *)(*(int *)(param_1 + 0x7c) + iVar6));
                return 0xb007;
              }
            }
            return 0;
          }
          FUN_ram_4038e4da();
          return 0xb007;
        }
      }
      uVar1 = FUN_ram_4038d3b4();
      FUN_ram_4038d2a2(2,"httpd_uri","W (%lu) %s: %s: no slots left for registering handler\n",uVar1
                       ,"httpd_uri","httpd_register_uri_handler");
      uVar1 = 0xb001;
    }
    else {
      uVar1 = FUN_ram_4038d3b4();
      FUN_ram_4038d2a2(2,"httpd_uri",
                       "W (%lu) %s: %s: handler %s with method %d already registered\n",uVar1,
                       "httpd_uri","httpd_register_uri_handler",*param_2,param_2[1]);
      uVar1 = 0xb002;
    }
  }
  return uVar1;
}

// Audit label: esp_ota_get_running_partition_reference; entry: ram:420a331c; name: esp_ota_get_running_partition

int esp_ota_get_running_partition(void)

{
  uint uVar1;
  int iVar2;
  int iVar3;

  if (DAT_ram_3fcc3cd8 != 0) {
    return DAT_ram_3fcc3cd8;
  }
  uVar1 = FUN_ram_42016442(esp_ota_get_running_partition);
  if (uVar1 != 0xffffffff) {
    iVar2 = FUN_ram_4207b844(0,0xff,0);
    if (iVar2 == 0) {
                    /* WARNING: Subroutine does not return */
      FUN_ram_4038e2f0("esp_ota_ops.c",0x2d1,"esp_ota_get_running_partition","it != NULL");
    }
    while( true ) {
      if (iVar2 == 0) {
                    /* WARNING: Subroutine does not return */
        FUN_ram_4038e23e();
      }
      iVar3 = FUN_ram_4207b88a(iVar2);
      if ((*(uint *)(iVar3 + 0xc) <= uVar1) &&
         (uVar1 < *(uint *)(iVar3 + 0xc) + *(int *)(iVar3 + 0x10))) break;
      iVar2 = FUN_ram_4207b78e(iVar2);
    }
    FUN_ram_4207b77c(iVar2);
    DAT_ram_3fcc3cd8 = iVar3;
    return iVar3;
  }
                    /* WARNING: Subroutine does not return */
  FUN_ram_4038e2f0("esp_ota_ops.c",0x2cc,"esp_ota_get_running_partition",
                   "phys_offs != SPI_FLASH_CACHE2PHYS_FAIL");
}

// Audit label: caller_of_application_review; entry: ram:420b1e4e; name: sdk_caller_of_application_review_at_420b1e4e

void sdk_caller_of_application_review_at_420b1e4e(void)

{
  int iVar1;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;

  FUN_ram_42001ad4();
  uStack_14 = 0;
  uStack_1c = 5000;
  uStack_18 = 1;
  iVar1 = FUN_ram_42016d3a(&uStack_1c);
  if (iVar1 == 0) {
    application_main_at_42008e56();
    FUN_ram_403894c6(0);
    return;
  }
                    /* WARNING: Subroutine does not return */
  FUN_ram_4038726a(iVar1,"/IDF/components/freertos/app_startup.c",199,"main_task",
                   "esp_task_wdt_init(&twdt_config)");
}

// Audit label: caller_of_lwip_socket_reference; entry: ram:42082166; name: sdk_caller_of_lwip_socket_reference_at_42082166

/* WARNING: Type propagation algorithm not settling */

int sdk_caller_of_lwip_socket_reference_at_42082166(void)

{
  uint uVar1;
  int iVar2;
  int *piVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  undefined4 uVar6;
  int in_a3;
  undefined4 in_a4;
  uint *in_a5;
  uint local_60 [4];
  int aiStack_50 [4];
  uint uStack_40;
  undefined1 uStack_3c;
  char cStack_3b;

  iVar2 = sdk_lwip_socket_reference_at_42081cca();
  if (iVar2 != 0) {
    puVar5 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
    FUN_ram_42082972(in_a4,1,*puVar5);
    return iVar2;
  }
  iVar2 = FUN_ram_42081e80(uStack_40,in_a3);
  if ((iVar2 != 0) || (iVar2 = FUN_ram_420820a0(uStack_40,1), iVar2 != 0)) goto LAB_ram_42082194;
  if (cStack_3b == '\x02') {
    uVar6 = 0x10;
  }
  else {
    uVar6 = 0x1c;
  }
  iVar2 = FUN_ram_4201a62e(uStack_40,&uStack_3c,uVar6);
  if (iVar2 < 0) {
    piVar3 = (int *)(*(code *)&SUB_ram_40000670)();
    if (*piVar3 != 0x77) {
      uVar6 = FUN_ram_4038d3b4();
      uVar1 = uStack_40;
      puVar5 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
      uVar4 = FUN_ram_420aa3b8(*puVar5);
      FUN_ram_4038d2a2(1,&DAT_ram_3c0d2798,"E (%lu) %s: [sock=%d] connect() error: %s\n",uVar6,
                       &DAT_ram_3c0d2798,uVar1,uVar4);
      iVar2 = 0x8004;
      goto LAB_ram_42082194;
    }
    aiStack_50[0] = 10;
    aiStack_50[1] = 0;
    aiStack_50[2] = 0;
    if (in_a3 != 0) {
      if (*(char *)(in_a3 + 0x2c) != '\0') {
        *in_a5 = uStack_40;
        return 0;
      }
      if (0 < *(int *)(in_a3 + 0x30)) {
        FUN_ram_42081c9c(*(int *)(in_a3 + 0x30),local_60 + 4);
      }
    }
    uVar1 = uStack_40;
    for (iVar2 = 2; iVar2 != 0; iVar2 = iVar2 + -1) {
      local_60[iVar2 + 1] = 0;
    }
    if (uStack_40 < 0x40) {
      local_60[((int)(((int)uStack_40 >> 0x1f & 0x1fU) + uStack_40) >> 5) + 2] =
           local_60[((int)(((int)uStack_40 >> 0x1f & 0x1fU) + uStack_40) >> 5) + 2] |
           1 << (uStack_40 & 0x1f);
    }
    iVar2 = FUN_ram_420077a6(uVar1 + 1,0,local_60 + 2,0,local_60 + 4);
    if (iVar2 < 0) {
      uVar6 = FUN_ram_4038d3b4();
      uVar1 = uStack_40;
      puVar5 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
      uVar4 = FUN_ram_420aa3b8(*puVar5);
      FUN_ram_4038d2a2(1,&DAT_ram_3c0d2798,"E (%lu) %s: [sock=%d] select() error: %s\n",uVar6,
                       &DAT_ram_3c0d2798,uVar1,uVar4);
      puVar5 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
      FUN_ram_42082972(in_a4,1,*puVar5);
      iVar2 = 0x8004;
      goto LAB_ram_42082194;
    }
    if (iVar2 == 0) {
      uVar6 = FUN_ram_4038d3b4();
      FUN_ram_4038d2a2(1,&DAT_ram_3c0d2798,"E (%lu) %s: [sock=%d] select() timeout\n",uVar6,
                       &DAT_ram_3c0d2798,uStack_40);
      iVar2 = 0x8006;
      goto LAB_ram_42082194;
    }
    local_60[1] = 4;
    iVar2 = FUN_ram_4201b116(uStack_40,0xfff,0x1007,local_60,local_60 + 1);
    if (iVar2 < 0) {
      uVar6 = FUN_ram_4038d3b4();
      uVar1 = uStack_40;
      puVar5 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
      uVar4 = FUN_ram_420aa3b8(*puVar5);
      FUN_ram_4038d2a2(1,&DAT_ram_3c0d2798,"E (%lu) %s: [sock=%d] getsockopt() error: %s\n",uVar6,
                       &DAT_ram_3c0d2798,uVar1,uVar4);
      iVar2 = 0x8005;
      goto LAB_ram_42082194;
    }
    if (local_60[0] != 0) {
      FUN_ram_42082972(in_a4,1);
      uVar6 = FUN_ram_4038d3b4();
      uVar1 = uStack_40;
      uVar4 = FUN_ram_420aa3b8(local_60[0]);
      FUN_ram_4038d2a2(1,&DAT_ram_3c0d2798,"E (%lu) %s: [sock=%d] delayed connect error: %s\n",uVar6
                       ,&DAT_ram_3c0d2798,uVar1,uVar4);
      iVar2 = 0x8004;
      goto LAB_ram_42082194;
    }
  }
  if (((in_a3 == 0) || (*(char *)(in_a3 + 0x2c) != '\0')) ||
     (iVar2 = FUN_ram_420820a0(uStack_40,0), iVar2 == 0)) {
    *in_a5 = uStack_40;
    return 0;
  }
LAB_ram_42082194:
  FUN_ram_420ab05c(uStack_40);
  return iVar2;
}

// Audit label: caller_of_lwip_recvfrom_reference; entry: ram:42038b82; name: sdk_caller_of_lwip_recvfrom_reference_at_42038b82

void sdk_caller_of_lwip_recvfrom_reference_at_42038b82(int param_1)

{
  int iVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  int iStack_1c;
  code *pcStack_18;
  undefined4 uStack_14;

  iVar1 = sdk_lwip_recvfrom_reference_at_4201a90a(*(undefined4 *)(param_1 + 100),&iStack_1c,0xc,0);
  if (iVar1 < 1) {
    uVar3 = FUN_ram_4038d3b4();
    puVar2 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
    FUN_ram_4038d2a2(2,"httpd","W (%lu) %s: %s: error in recv (%d)\n",uVar3,"httpd",
                     "httpd_process_ctrl_msg",*puVar2);
  }
  else if (iVar1 == 0xc) {
    if (iStack_1c == 0) {
      *(undefined4 *)(param_1 + 0x70) = 2;
    }
    else if ((iStack_1c == 1) && (pcStack_18 != (code *)0x0)) {
      (*pcStack_18)(uStack_14);
    }
  }
  else {
    uVar3 = FUN_ram_4038d3b4();
    FUN_ram_4038d2a2(2,"httpd","W (%lu) %s: %s: incomplete msg\n",uVar3,"httpd",
                     "httpd_process_ctrl_msg");
  }
  return;
}

// Audit label: caller_of_lwip_recvfrom_reference; entry: ram:4203b732; name: sdk_caller_of_lwip_recvfrom_reference_at_4203b732

int sdk_caller_of_lwip_recvfrom_reference_at_4203b732(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4,
                    undefined4 param_5)

{
  int iVar1;

  if (param_3 == 0) {
    iVar1 = -2;
  }
  else {
    iVar1 = sdk_lwip_recvfrom_reference_at_4201a90a(param_2,param_3,param_4,param_5);
    if (iVar1 < 0) {
      iVar1 = FUN_ram_4203af6e(&DAT_ram_3c0cdd10,param_2);
    }
  }
  return iVar1;
}

// Audit label: caller_of_lwip_recvfrom_reference; entry: ram:42084396; name: sdk_caller_of_lwip_recvfrom_reference_at_42084396

int sdk_caller_of_lwip_recvfrom_reference_at_42084396(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 *puVar4;
  undefined4 uVar5;
  int *piVar6;
  int iVar7;

  if (param_1 == 0) {
    iVar7 = 0;
  }
  else {
    iVar7 = *(int *)(param_1 + 8);
  }
  iVar1 = FUN_ram_42083916(param_1,param_4);
  if (iVar1 == -1) {
    iVar2 = -2;
  }
  else {
    iVar2 = 0;
    if (iVar1 != 0) {
      iVar2 = sdk_lwip_recvfrom_reference_at_4201a90a(*(undefined4 *)(iVar7 + 0x6c),param_2,param_3,0);
      if (iVar2 < 0) {
        uVar3 = FUN_ram_4038d3b4();
        puVar4 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
        uVar5 = FUN_ram_420aa3b8(*puVar4);
        FUN_ram_4038d2a2(1,"transport_base","E (%lu) %s: tcp_read error, errno=%s\n",uVar3,
                         "transport_base",uVar5);
        puVar4 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
        FUN_ram_42083aa8(param_1,*puVar4);
        piVar6 = (int *)(*(code *)&SUB_ram_40000670)();
        if (*piVar6 == 0xb) {
          iVar2 = 0;
        }
        else {
          iVar2 = -2;
        }
      }
      else if (iVar2 == 0) {
        if (iVar1 < 1) {
          iVar2 = -1;
        }
        else {
          FUN_ram_420839ce(param_1,0xffffffff);
          iVar2 = -1;
        }
      }
    }
  }
  return iVar2;
}

// Audit label: caller_of_lwip_recvfrom_reference; entry: ram:42082418; name: sdk_caller_of_lwip_recvfrom_reference_at_42082418

void sdk_caller_of_lwip_recvfrom_reference_at_42082418(int param_1,undefined4 param_2,undefined4 param_3)

{
  sdk_lwip_recvfrom_reference_at_4201a90a(*(undefined4 *)(param_1 + 0x7ac),param_2,param_3,0);
  return;
}

// Audit label: caller_of_lwip_sendto_reference; entry: ram:4203977e; name: sdk_caller_of_lwip_sendto_reference_at_4203977e

undefined4 sdk_caller_of_lwip_sendto_reference_at_4203977e(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;

  if (param_1 == 0) {
    uVar2 = 0x102;
  }
  else {
    uStack_1c = 0;
    uStack_18 = 0;
    uStack_14 = 0;
    iVar1 = sdk_lwip_sendto_reference_at_4203c9b2(*(undefined4 *)(param_1 + 0x68),*(undefined2 *)(param_1 + 0x1a),
                             &uStack_1c,0xc);
    if (iVar1 < 0) {
      uVar2 = FUN_ram_4038d3b4();
      FUN_ram_4038d2a2(1,"httpd","E (%lu) %s: Failed to send shutdown signal err=%d\n",uVar2,"httpd"
                       ,iVar1);
      uVar2 = 0xffffffff;
    }
    else {
      while (*(int *)(param_1 + 0x70) != 3) {
        vTaskDelay(10);
      }
      if (*(int *)(param_1 + 0x2c) != 0) {
        if (*(code **)(param_1 + 0x30) == (code *)0x0) {
          FUN_ram_4038e4da();
        }
        else {
          (**(code **)(param_1 + 0x30))();
        }
        *(undefined4 *)(param_1 + 0x2c) = 0;
      }
      if (*(int *)(param_1 + 0x34) != 0) {
        if (*(code **)(param_1 + 0x38) == (code *)0x0) {
          FUN_ram_4038e4da();
        }
        else {
          (**(code **)(param_1 + 0x38))();
        }
        *(undefined4 *)(param_1 + 0x34) = 0;
      }
      FUN_ram_420390a6(param_1);
      FUN_ram_420390f2(8,0,0);
      uVar2 = 0;
    }
  }
  return uVar2;
}

// Audit label: caller_of_lwip_sendto_reference; entry: ram:42039642; name: sdk_caller_of_lwip_sendto_reference_at_42039642

undefined4 sdk_caller_of_lwip_sendto_reference_at_42039642(int param_1,int param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uStack_1c;
  int iStack_18;
  undefined4 uStack_14;

  if (param_1 == 0) {
    uVar2 = 0x102;
  }
  else if (param_2 == 0) {
    uVar2 = 0x102;
  }
  else {
    uStack_1c = 1;
    iStack_18 = param_2;
    uStack_14 = param_3;
    iVar1 = sdk_lwip_sendto_reference_at_4203c9b2(*(undefined4 *)(param_1 + 0x68),*(undefined2 *)(param_1 + 0x1a),
                             &uStack_1c,0xc);
    if (iVar1 < 0) {
      uVar2 = FUN_ram_4038d3b4();
      FUN_ram_4038d2a2(2,"httpd","W (%lu) %s: %s: failed to queue work\n",uVar2,"httpd",
                       "httpd_queue_work");
      uVar2 = 0xffffffff;
    }
    else {
      uVar2 = 0;
    }
  }
  return uVar2;
}

// Audit label: caller_of_lwip_sendto_reference; entry: ram:4201ac78; name: sdk_caller_of_lwip_sendto_reference_at_4201ac78

void sdk_caller_of_lwip_sendto_reference_at_4201ac78(void)

{
  sdk_lwip_sendto_reference_at_4201aacc();
  return;
}

// Audit label: caller_of_lwip_sendto_reference; entry: ram:42082404; name: sdk_caller_of_lwip_sendto_reference_at_42082404

void sdk_caller_of_lwip_sendto_reference_at_42082404(int param_1,undefined4 param_2,undefined4 param_3)

{
  sdk_lwip_sendto_reference_at_4201aacc(*(undefined4 *)(param_1 + 0x7ac),param_2,param_3,0);
  return;
}

// Audit label: caller_of_lwip_sendto_reference; entry: ram:420842b0; name: sdk_caller_of_lwip_sendto_reference_at_420842b0

int sdk_caller_of_lwip_sendto_reference_at_420842b0(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 *puVar3;
  undefined4 uVar4;
  int iVar5;

  if (param_1 == 0) {
    iVar5 = 0;
  }
  else {
    iVar5 = *(int *)(param_1 + 8);
  }
  iVar1 = FUN_ram_42083930(param_1,param_4);
  if (iVar1 < 1) {
    uVar2 = FUN_ram_4038d3b4();
    puVar3 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
    uVar4 = FUN_ram_420aa3b8(*puVar3);
    FUN_ram_4038d2a2(2,"transport_base",
                     "W (%lu) %s: Poll timeout or error, errno=%s, fd=%d, timeout_ms=%d\n",uVar2,
                     "transport_base",uVar4,*(undefined4 *)(iVar5 + 0x6c),param_4);
  }
  else {
    iVar1 = sdk_lwip_sendto_reference_at_4201aacc(*(undefined4 *)(iVar5 + 0x6c),param_2,param_3,0);
    if (iVar1 < 0) {
      uVar2 = FUN_ram_4038d3b4();
      puVar3 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
      uVar4 = FUN_ram_420aa3b8(*puVar3);
      FUN_ram_4038d2a2(1,"transport_base","E (%lu) %s: tcp_write error, errno=%s\n",uVar2,
                       "transport_base",uVar4);
      puVar3 = (undefined4 *)(*(code *)&SUB_ram_40000670)();
      FUN_ram_42083aa8(param_1,*puVar3);
    }
  }
  return iVar1;
}

// Audit label: caller_of_lwip_sendto_reference; entry: ram:4203b6fc; name: sdk_caller_of_lwip_sendto_reference_at_4203b6fc

int sdk_caller_of_lwip_sendto_reference_at_4203b6fc(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4,
                    undefined4 param_5)

{
  int iVar1;

  if (param_3 == 0) {
    iVar1 = -2;
  }
  else {
    iVar1 = sdk_lwip_sendto_reference_at_4201aacc(param_2,param_3,param_4,param_5);
    if (iVar1 < 0) {
      iVar1 = FUN_ram_4203af6e(&DAT_ram_3c0cdd08,param_2);
    }
  }
  return iVar1;
}

// Audit label: caller_of_httpd_req_recv_reference; entry: ram:4203adbc; name: sdk_caller_of_httpd_req_recv_reference_at_4203adbc

undefined4 sdk_caller_of_httpd_req_recv_reference_at_4203adbc(int param_1,int param_2)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;

  if (param_1 == 0) {
    uVar2 = 0xffffffff;
  }
  else if (param_2 == 0) {
    uVar2 = 0xffffffff;
  }
  else {
    iVar1 = FUN_ram_4203a288();
    if (iVar1 == 0) {
      iVar1 = sdk_httpd_req_recv_reference_at_4203a36c(param_1);
      if (iVar1 == 0) {
        uVar3 = *(uint *)(param_1 + 0x308) + 1;
        iVar1 = (uint)(uVar3 < *(uint *)(param_1 + 0x308)) + *(int *)(param_1 + 0x30c);
        *(uint *)(param_1 + 0x308) = uVar3;
        *(int *)(param_1 + 0x30c) = iVar1;
        *(uint *)(param_2 + 0x28) = uVar3;
        *(int *)(param_2 + 0x2c) = iVar1;
        uVar2 = 0;
      }
      else {
        uVar2 = 0xffffffff;
      }
    }
    else {
      uVar2 = 0xffffffff;
    }
  }
  return uVar2;
}

// Audit label: caller_of_httpd_req_get_hdr_value_str_reference; entry: ram:4203ba3e; name: sdk_caller_of_httpd_req_get_hdr_value_str_reference_at_4203ba3e

int sdk_caller_of_httpd_req_get_hdr_value_str_reference_at_4203ba3e(int param_1)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int iStack_14;

  iVar5 = param_1 + 0x80;
  iStack_14 = 0;
  if (((*(ushort *)(param_1 + 0x2d8) & 8) == 0) ||
     (iVar2 = FUN_ram_4203b7aa(param_1,param_1 + 0x88 + (uint)*(ushort *)(param_1 + 0x2e8),
                               *(undefined2 *)(param_1 + 0x2ea),*(undefined4 *)(param_1 + 0x84),
                               &iStack_14), iVar2 == 0)) {
    if (iStack_14 == 6) {
      uVar3 = FUN_ram_4038d3b4();
      FUN_ram_4038d2a2(2,"httpd_uri","W (%lu) %s: %s: URI \'%s\' not found\n",uVar3,"httpd_uri",
                       "httpd_uri",param_1 + 0x88);
      iVar5 = FUN_ram_4203b662(iVar5,6);
    }
    else if (iStack_14 == 7) {
      uVar3 = FUN_ram_4038d3b4();
      FUN_ram_4038d2a2(2,"httpd_uri","W (%lu) %s: %s: Method \'%d\' not allowed for URI \'%s\'\n",
                       uVar3,"httpd_uri","httpd_uri",*(undefined4 *)(param_1 + 0x84),param_1 + 0x88)
      ;
      iVar5 = FUN_ram_4203b662(iVar5,7);
    }
    else {
      iVar5 = -1;
    }
  }
  else {
    *(undefined4 *)(param_1 + 0x294) = *(undefined4 *)(iVar2 + 0xc);
    piVar1 = *(int **)(param_1 + 0x290);
    if (((*(char *)(iVar2 + 0x10) != '\0') && ((char)piVar1[0x15] != '\0')) &&
       (*(int *)(iVar2 + 4) == 1)) {
      iVar4 = sdk_httpd_req_get_hdr_value_str_reference_at_4203bd4a(iVar5,*(undefined4 *)(iVar2 + 0x14));
      if (iVar4 != 0) {
        return iVar4;
      }
      *(undefined1 *)(*piVar1 + 0xb9) = 1;
      *(undefined4 *)(*piVar1 + 0xbc) = *(undefined4 *)(iVar2 + 8);
      *(undefined1 *)(*piVar1 + 0xc0) = *(undefined1 *)(iVar2 + 0x11);
      *(undefined4 *)(*piVar1 + 0xc4) = *(undefined4 *)(iVar2 + 0xc);
    }
    iVar2 = (**(code **)(iVar2 + 8))(iVar5);
    iVar5 = 0;
    if (iVar2 != 0) {
      uVar3 = FUN_ram_4038d3b4();
      FUN_ram_4038d2a2(2,"httpd_uri","W (%lu) %s: %s: uri handler execution failed\n",uVar3,
                       "httpd_uri","httpd_uri");
      iVar5 = -1;
    }
  }
  return iVar5;
}

// Audit label: caller_of_esp_flash_read_reference; entry: ram:4204271a; name: sdk_caller_of_esp_flash_read_reference_at_4204271a

undefined4 sdk_caller_of_esp_flash_read_reference_at_4204271a(int param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  undefined4 uVar1;

  if ((param_4 & 0xf) == 0) {
    uVar1 = sdk_esp_flash_read_reference_at_4207bb52(*(undefined4 *)(param_1 + 0xc));
  }
  else {
    uVar1 = 0x102;
  }
  return uVar1;
}

// Audit label: caller_of_esp_flash_read_reference; entry: ram:4204270a; name: sdk_caller_of_esp_flash_read_reference_at_4204270a

void sdk_caller_of_esp_flash_read_reference_at_4204270a(int param_1)

{
  sdk_esp_flash_read_reference_at_4207b976(*(undefined4 *)(param_1 + 0xc));
  return;
}

// Audit label: caller_of_esp_flash_write_reference; entry: ram:4207b8e8; name: sdk_caller_of_esp_flash_write_reference_at_4207b8e8

undefined4 sdk_caller_of_esp_flash_write_reference_at_4207b8e8(int *param_1,uint param_2,undefined4 param_3,uint param_4)

{
  undefined4 uVar1;

  if (param_1 != (int *)0x0) {
    if (*(char *)((int)param_1 + 0x2a) == '\0') {
      if ((uint)param_1[4] < param_2) {
        uVar1 = 0x102;
      }
      else if (param_1[4] - param_2 < param_4) {
        uVar1 = 0x104;
      }
      else if (*(char *)((int)param_1 + 0x29) == '\0') {
        uVar1 = esp_flash_write(*param_1,param_3,param_2 + param_1[3]);
      }
      else if (*param_1 == DAT_ram_3fcc3ae0) {
        uVar1 = FUN_ram_40392644(*param_1,param_2 + param_1[3],param_3);
      }
      else {
        uVar1 = 0x106;
      }
    }
    else {
      uVar1 = 0x10d;
    }
    return uVar1;
  }
                    /* WARNING: Subroutine does not return */
  FUN_ram_4038e2f0("partition_target.c",0x42,"esp_partition_write","partition != NULL");
}

// Audit label: caller_of_esp_flash_write_reference; entry: ram:4207b9d0; name: sdk_caller_of_esp_flash_write_reference_at_4207b9d0

undefined4 sdk_caller_of_esp_flash_write_reference_at_4207b9d0(undefined4 *param_1,uint param_2,undefined4 param_3,uint param_4)

{
  undefined4 uVar1;

  if (param_1 != (undefined4 *)0x0) {
    if (*(char *)((int)param_1 + 0x2a) == '\0') {
      if ((uint)param_1[4] < param_2) {
        uVar1 = 0x102;
      }
      else if (param_1[4] - param_2 < param_4) {
        uVar1 = 0x104;
      }
      else {
        uVar1 = esp_flash_write(*param_1,param_3,param_1[3] + param_2);
      }
    }
    else {
      uVar1 = 0x10d;
    }
    return uVar1;
  }
                    /* WARNING: Subroutine does not return */
  FUN_ram_4038e2f0("partition_target.c",0x6c,"esp_partition_write_raw","partition != NULL");
}

// Audit label: caller_of_esp_flash_erase_region_reference; entry: ram:4207ba36; name: sdk_caller_of_esp_flash_erase_region_reference_at_4207ba36

undefined4 sdk_caller_of_esp_flash_erase_region_reference_at_4207ba36(undefined4 *param_1,uint param_2,uint param_3)

{
  undefined4 uVar1;

  if (param_1 != (undefined4 *)0x0) {
    if (*(char *)((int)param_1 + 0x2a) == '\0') {
      if ((uint)param_1[4] < param_2) {
        uVar1 = 0x102;
      }
      else if (param_1[4] - param_2 < param_3) {
        uVar1 = 0x104;
      }
      else if ((param_3 & 0xfff) == 0) {
        if ((param_2 & 0xfff) == 0) {
          uVar1 = esp_flash_erase_region(*param_1,param_2 + param_1[3]);
        }
        else {
          uVar1 = 0x102;
        }
      }
      else {
        uVar1 = 0x104;
      }
    }
    else {
      uVar1 = 0x10d;
    }
    return uVar1;
  }
                    /* WARNING: Subroutine does not return */
  FUN_ram_4038e2f0("partition_target.c",0x7e,"esp_partition_erase_range","partition != NULL");
}

// Audit label: caller_of_esp_ota_get_running_partition_reference; entry: ram:4207bc60; name: sdk_caller_of_esp_ota_get_running_partition_reference_at_4207bc60

undefined4 sdk_caller_of_esp_ota_get_running_partition_reference_at_4207bc60(uint param_1,int param_2)

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
