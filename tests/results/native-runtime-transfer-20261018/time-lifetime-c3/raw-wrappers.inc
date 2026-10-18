static void do_setoperatingmode(void *ctx)
{
    sntp_setoperatingmode((intptr_t)ctx);
}

void esp_sntp_setoperatingmode(esp_sntp_operatingmode_t operating_mode)
{
    SNTP_ERROR(tcpip_callback(do_setoperatingmode, (void*)operating_mode),
               "esp_sntp_setoperatingmode: tcpip_callback() failed");
}

static void do_init(void *ctx)
{
    sntp_init();
}

void esp_sntp_init(void)
{
    SNTP_ERROR(tcpip_callback(do_init, NULL), "esp_sntp_init: tcpip_callback() failed");
}

static void do_stop(void *ctx)
{
    sntp_stop();
}

void esp_sntp_stop(void)
{
    SNTP_ERROR(tcpip_callback(do_stop, NULL), "esp_sntp_stop: tcpip_callback() failed");
}

struct tcpip_setserver {
    struct tcpip_api_call_data call;
    u8_t idx;
    const ip_addr_t *addr;
};

static err_t do_setserver(struct tcpip_api_call_data *msg)
{
    struct tcpip_setserver *params = __containerof(msg, struct tcpip_setserver, call);
    sntp_setserver(params->idx, params->addr);
    return ERR_OK;
}

void esp_sntp_setserver(u8_t idx, const ip_addr_t *addr)
{
    struct tcpip_setserver params = {
            .idx = idx,
            .addr = addr
    };
    SNTP_ERROR(tcpip_api_call(do_setserver, &params.call), "esp_sntp_setserver :tcpip_api_call() failed");
}

struct tcpip_setservername {
    struct tcpip_api_call_data call;
    u8_t idx;
    const char *server;
};

static err_t do_setservername(struct tcpip_api_call_data *msg)
{
    struct tcpip_setservername *params = __containerof(msg, struct tcpip_setservername, call);
    sntp_setservername(params->idx, params->server);
    return ERR_OK;
}

void esp_sntp_setservername(u8_t idx, const char *server)
{
    struct tcpip_setservername params = {
            .idx = idx,
            .server = server
    };
    SNTP_ERROR(tcpip_api_call(do_setservername, &params.call), "esp_sntp_setservername :tcpip_api_call() failed");
}

const char *esp_sntp_getservername(u8_t idx)
{
    return sntp_getservername(idx);
}

const ip_addr_t* esp_sntp_getserver(u8_t idx)
{
    return sntp_getserver(idx);
}

uint8_t esp_sntp_getreachability(uint8_t idx)
{
#if SNTP_MONITOR_SERVER_REACHABILITY
    return sntp_getreachability(idx);
#endif
    LWIP_ERROR("sntp_getreachability() in not enabled in lwipopts", false, );
    return 0;
}

esp_sntp_operatingmode_t esp_sntp_getoperatingmode(void)
{
    return (esp_sntp_operatingmode_t)sntp_getoperatingmode();
}

#if LWIP_DHCP_GET_NTP_SRV
static void do_servermode_dhcp(void* ctx)
{
    sntp_servermode_dhcp((intptr_t)ctx);
}

void esp_sntp_servermode_dhcp(bool enable)
{
    SNTP_ERROR(tcpip_callback(do_servermode_dhcp, (void*)enable), "esp_sntp_servermode_dhcp: tcpip_callback() failed");
}

#endif /* LWIP_DHCP_GET_NTP_SRV */

bool esp_sntp_enabled(void)
{
    return sntp_enabled();
}
