#define ESP_LWIP_COMPONENT_BUILD
/**
 * @file
 * SNTP client options list
 */

/*
 * Copyright (c) 2007-2009 Frédéric Bernon, Simon Goldschmidt
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 * 3. The name of the author may not be used to endorse or promote products
 *    derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
 * SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
 * OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
 * IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
 * OF SUCH DAMAGE.
 *
 * This file is part of the lwIP TCP/IP stack.
 *
 * Author: Frédéric Bernon, Simon Goldschmidt
 *
 */
#ifndef LWIP_HDR_APPS_SNTP_OPTS_H
#define LWIP_HDR_APPS_SNTP_OPTS_H

/**
 * @defgroup sntp_opts Options
 * @ingroup sntp
 * @{
 */

/** SNTP macro to change system time in seconds
 * Define SNTP_SET_SYSTEM_TIME_US(sec, us) to set the time in microseconds
 * instead of this one if you need the additional precision. Alternatively,
 * define SNTP_SET_SYSTEM_TIME_NTP(sec, frac) in order to work with native
 * NTP timestamps instead.
 */
#if !defined SNTP_SET_SYSTEM_TIME || defined __DOXYGEN__
#define SNTP_SET_SYSTEM_TIME(sec)   LWIP_UNUSED_ARG(sec)
#endif

/** The maximum number of SNTP servers that can be set */
#if !defined SNTP_MAX_SERVERS || defined __DOXYGEN__
#define SNTP_MAX_SERVERS           LWIP_DHCP_MAX_NTP_SERVERS
#endif

/** Set this to 1 to implement the callback function called by dhcp when
 * NTP servers are received. */
#if !defined SNTP_GET_SERVERS_FROM_DHCP || defined __DOXYGEN__
#define SNTP_GET_SERVERS_FROM_DHCP LWIP_DHCP_GET_NTP_SRV
#endif

/** Set this to 1 to implement the callback function called by dhcpv6 when
 * NTP servers are received. */
#if !defined SNTP_GET_SERVERS_FROM_DHCPV6 || defined __DOXYGEN__
#define SNTP_GET_SERVERS_FROM_DHCPV6 LWIP_DHCP6_GET_NTP_SRV
#endif

/** Set this to 1 to support DNS names (or IP address strings) to set sntp servers
 * One server address/name can be defined as default if SNTP_SERVER_DNS == 1:
 * \#define SNTP_SERVER_ADDRESS "pool.ntp.org"
 */
#if !defined SNTP_SERVER_DNS || defined __DOXYGEN__
#define SNTP_SERVER_DNS            0
#endif

/**
 * SNTP_DEBUG: Enable debugging for SNTP.
 */
#if !defined SNTP_DEBUG || defined __DOXYGEN__
#define SNTP_DEBUG                  LWIP_DBG_OFF
#endif

/** SNTP server port */
#if !defined SNTP_PORT || defined __DOXYGEN__
#define SNTP_PORT                   LWIP_IANA_PORT_SNTP
#endif

/** Sanity check:
 * Define this to
 * - 0 to turn off sanity checks (default; smaller code)
 * - >= 1 to check address and port of the response packet to ensure the
 *        response comes from the server we sent the request to.
 * - >= 2 to check returned Originate Timestamp against Transmit Timestamp
 *        sent to the server (to ensure response to older request).
 * - >= 3 @todo: discard reply if any of the VN, Stratum, or Transmit Timestamp
 *        fields is 0 or the Mode field is not 4 (unicast) or 5 (broadcast).
 * - >= 4 @todo: to check that the Root Delay and Root Dispersion fields are each
 *        greater than or equal to 0 and less than infinity, where infinity is
 *        currently a cozy number like one second. This check avoids using a
 *        server whose synchronization source has expired for a very long time.
 */
#if !defined SNTP_CHECK_RESPONSE || defined __DOXYGEN__
#define SNTP_CHECK_RESPONSE         0
#endif

/** Enable round-trip delay compensation.
 * Compensate for the round-trip delay by calculating the clock offset from
 * the originate, receive, transmit and destination timestamps, as per RFC.
 *
 * The calculation requires compiler support for 64-bit integers. Also, either
 * SNTP_SET_SYSTEM_TIME_US or SNTP_SET_SYSTEM_TIME_NTP has to be implemented
 * for setting the system clock with sub-second precision. Likewise, either
 * SNTP_GET_SYSTEM_TIME or SNTP_GET_SYSTEM_TIME_NTP needs to be implemented
 * with sub-second precision.
 *
 * Although not strictly required, it makes sense to combine this option with
 * SNTP_CHECK_RESPONSE >= 2 for sanity-checking of the received timestamps.
 * Also, in order for the round-trip calculation to work, the difference
 * between the local clock and the NTP server clock must not be larger than
 * about 34 years. If that limit is exceeded, the implementation will fall back
 * to setting the clock without compensation. In order to ensure that the local
 * clock is always within the permitted range for compensation, even at first
 * try, it may be necessary to store at least the current year in non-volatile
 * memory.
 */
#if !defined SNTP_COMP_ROUNDTRIP || defined __DOXYGEN__
#define SNTP_COMP_ROUNDTRIP         0
#endif

/** According to the RFC, this shall be a random delay
 * between 1 and 5 minutes (in milliseconds) to prevent load peaks.
 * This can be defined to a random generation function,
 * which must return the delay in milliseconds as u32_t.
 * Turned off by default.
 */
#if !defined SNTP_STARTUP_DELAY || defined __DOXYGEN__
#ifdef LWIP_RAND
#define SNTP_STARTUP_DELAY          1
#else
#define SNTP_STARTUP_DELAY          0
#endif
#endif

/** If you want the startup delay to be a function, define this
 * to a function (including the brackets) and define SNTP_STARTUP_DELAY to 1.
 */
#if !defined SNTP_STARTUP_DELAY_FUNC || defined __DOXYGEN__
#define SNTP_STARTUP_DELAY_FUNC     (LWIP_RAND() % 5000)
#endif

/** SNTP receive timeout - in milliseconds
 * Also used as retry timeout - this shouldn't be too low.
 * Default is 15 seconds. Must not be beolw 15 seconds by specification (i.e. 15000)
 */
#if !defined SNTP_RECV_TIMEOUT || defined __DOXYGEN__
#define SNTP_RECV_TIMEOUT           15000
#endif

/** SNTP update delay - in milliseconds
 * Default is 1 hour. Must not be beolw 60 seconds by specification (i.e. 60000)
 */
#if !defined SNTP_UPDATE_DELAY || defined __DOXYGEN__
#define SNTP_UPDATE_DELAY           3600000
#endif

/** SNTP macro to get system time, used with SNTP_CHECK_RESPONSE >= 2
 * to send in request and compare in response. Also used for round-trip
 * delay compensation if SNTP_COMP_ROUNDTRIP != 0.
 * Alternatively, define SNTP_GET_SYSTEM_TIME_NTP(sec, frac) in order to
 * work with native NTP timestamps instead.
 */
#if !defined SNTP_GET_SYSTEM_TIME || defined __DOXYGEN__
#define SNTP_GET_SYSTEM_TIME(sec, us)     do { (sec) = 0; (us) = 0; } while(0)
#endif

/** Default retry timeout (in milliseconds) if the response
 * received is invalid.
 * This is doubled with each retry until SNTP_RETRY_TIMEOUT_MAX is reached.
 */
#if !defined SNTP_RETRY_TIMEOUT || defined __DOXYGEN__
#define SNTP_RETRY_TIMEOUT          SNTP_RECV_TIMEOUT
#endif

/** Maximum retry timeout (in milliseconds). */
#if !defined SNTP_RETRY_TIMEOUT_MAX || defined __DOXYGEN__
#define SNTP_RETRY_TIMEOUT_MAX      (SNTP_RETRY_TIMEOUT * 10)
#endif

/** Increase retry timeout with every retry sent
 * Default is on to conform to RFC.
 */
#if !defined SNTP_RETRY_TIMEOUT_EXP || defined __DOXYGEN__
#define SNTP_RETRY_TIMEOUT_EXP      1
#endif

/** Keep a reachability shift register per server
 * Default is on to conform to RFC.
 */
#if !defined SNTP_MONITOR_SERVER_REACHABILITY || defined __DOXYGEN__
#define SNTP_MONITOR_SERVER_REACHABILITY 1
#endif

/**
 * @}
 */

#endif /* LWIP_HDR_APPS_SNTP_OPTS_H */
/*
 * SPDX-FileCopyrightText: 2015-2024 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#ifndef __ESP_SNTP_H__
#define __ESP_SNTP_H__


#ifdef __cplusplus
extern "C" {
#endif

/*
 * The time update takes place in the sntp_sync_time() function.
 * The user has the ability to redefine this function in order
 * to re-define its functionality. This function has two time update modes,
 * which can be set via the sntp_set_sync_mode() function.
 * Two available modes are as follows:
 * - the first is an immediate update when receiving time from the sntp server,
 * - the second is a smooth time update (if the time error is no more than 35 minutes,
 *   and an immediate update if the error is more than 35 minutes).
 *
 * To receive notification of time synchronization,
 * you can use the callback function or get the synchronization status
 * via the sntp_get_sync_status() function.
 *
 * To determine the time synchronization time on the device, you can use:
 * 1) sntp_set_time_sync_notification_cb() function to set the callback function,
 *    which is convenient to use to receive notification of the update time.
 * 2) sntp_get_sync_status() function for getting time synchronization status.
 *    After the time synchronization is completed, the status will be
 *    SNTP_SYNC_STATUS_COMPLETED, after, it will be reseted to SNTP_SYNC_STATUS_RESET
 *    to wait for the next sync cycle.
 */

/// Aliases for esp_sntp prefixed API (inherently thread safe)
#define esp_sntp_sync_time sntp_sync_time
#define esp_sntp_set_sync_mode sntp_set_sync_mode
#define esp_sntp_get_sync_mode sntp_get_sync_mode
#define esp_sntp_get_sync_status sntp_get_sync_status
#define esp_sntp_set_sync_status sntp_set_sync_status
#define esp_sntp_set_time_sync_notification_cb sntp_set_time_sync_notification_cb
#define esp_sntp_set_sync_interval sntp_set_sync_interval
#define esp_sntp_get_sync_interval sntp_get_sync_interval
#define esp_sntp_restart sntp_restart

#ifndef SNTP_OPMODE_POLL
#define SNTP_OPMODE_POLL ESP_SNTP_OPMODE_POLL
#else
#warning "Defined!"
#endif /* SNTP_OPMODE_POLL */

/// SNTP time update mode
typedef enum {
    SNTP_SYNC_MODE_IMMED,   /*!< Update system time immediately when receiving a response from the SNTP server. */
    SNTP_SYNC_MODE_SMOOTH,  /*!< Smooth time updating. Time error is gradually reduced using adjtime function. If the difference between SNTP response time and system time is large (more than 35 minutes) then update immediately. */
} sntp_sync_mode_t;

/// SNTP sync status
typedef enum {
    SNTP_SYNC_STATUS_RESET,         // Reset status.
    SNTP_SYNC_STATUS_COMPLETED,     // Time is synchronized.
    SNTP_SYNC_STATUS_IN_PROGRESS,   // Smooth time sync in progress.
} sntp_sync_status_t;

/// SNTP operating modes per lwip SNTP module
typedef enum {
    ESP_SNTP_OPMODE_POLL,
    ESP_SNTP_OPMODE_LISTENONLY,
} esp_sntp_operatingmode_t;

/**
 * @brief SNTP callback function for notifying about time sync event
 *
 * @param tv Time received from SNTP server.
 */
typedef void (*sntp_sync_time_cb_t) (struct timeval *tv);

/**
 * @brief This function updates the system time.
 *
 * This is a weak-linked function. It is possible to replace all SNTP update functionality
 * by placing a sntp_sync_time() function in the app firmware source.
 * If the default implementation is used, calling sntp_set_sync_mode() allows
 * the time synchronization mode to be changed to instant or smooth.
 * If a callback function is registered via sntp_set_time_sync_notification_cb(),
 * it will be called following time synchronization.
 *
 * @param tv Time received from SNTP server.
 */
void sntp_sync_time(struct timeval *tv);

/**
 * @brief Set the sync mode
 *
 * Modes allowed: SNTP_SYNC_MODE_IMMED and SNTP_SYNC_MODE_SMOOTH.
 * @param sync_mode Sync mode.
 */
void sntp_set_sync_mode(sntp_sync_mode_t sync_mode);

/**
 * @brief Get set sync mode
 *
 * @return  SNTP_SYNC_MODE_IMMED: Update time immediately.
 *          SNTP_SYNC_MODE_SMOOTH: Smooth time updating.
 */
sntp_sync_mode_t sntp_get_sync_mode(void);

/**
 * @brief Get status of time sync
 *
 * After the update is completed, the status will be returned as SNTP_SYNC_STATUS_COMPLETED.
 * After that, the status will be reset to SNTP_SYNC_STATUS_RESET.
 * If the update operation is not completed yet, the status will be SNTP_SYNC_STATUS_RESET.
 * If a smooth mode was chosen and the synchronization is still continuing (adjtime works), then it will be SNTP_SYNC_STATUS_IN_PROGRESS.
 *
 * @return  SNTP_SYNC_STATUS_RESET: Reset status.
 *          SNTP_SYNC_STATUS_COMPLETED: Time is synchronized.
 *          SNTP_SYNC_STATUS_IN_PROGRESS: Smooth time sync in progress.
 */
sntp_sync_status_t sntp_get_sync_status(void);

/**
 * @brief Set status of time sync
 *
 * @param sync_status status of time sync (see sntp_sync_status_t)
 */
void sntp_set_sync_status(sntp_sync_status_t sync_status);

/**
 * @brief Set a callback function for time synchronization notification
 *
 * @param callback a callback function
 */
void sntp_set_time_sync_notification_cb(sntp_sync_time_cb_t callback);

/**
 * @brief Set the sync interval of SNTP operation
 *
 * Note: SNTPv4 RFC 4330 enforces a minimum sync interval of 15 seconds.
 * This sync interval will be used in the next attempt update time throught SNTP.
 * To apply the new sync interval call the sntp_restart() function,
 * otherwise, it will be applied after the last interval expired.
 *
 * @param interval_ms   The sync interval in ms. It cannot be lower than 15 seconds, otherwise 15 seconds will be set.
 */
void sntp_set_sync_interval(uint32_t interval_ms);

/**
 * @brief Get the sync interval of SNTP operation
 *
 * @return  the sync interval
 */
uint32_t sntp_get_sync_interval(void);

/**
 * @brief Restart SNTP
 *
 * @return True  - Restart
 *         False - SNTP was not initialized yet
 */
bool sntp_restart(void);

/**
 * @brief Sets SNTP operating mode. The mode has to be set before init.
 *
 * @param operating_mode Desired operating mode
 */
void esp_sntp_setoperatingmode(esp_sntp_operatingmode_t operating_mode);

/**
 * @brief Init and start SNTP service
 */
void esp_sntp_init(void);

/**
 * @brief Stops SNTP service
 */
void esp_sntp_stop(void);

/**
 * @brief Sets SNTP server address
 *
 * @param idx Index of the server
 * @param addr IP address of the server
 */
void esp_sntp_setserver(u8_t idx, const ip_addr_t *addr);

/**
 * @brief Sets SNTP hostname
 * @param idx Index of the server
 * @param server Name of the server
 */
void esp_sntp_setservername(u8_t idx, const char *server);

/**
 * @brief Gets SNTP server name
 * @param idx Index of the server
 * @return Name of the server
 */
const char *esp_sntp_getservername(u8_t idx);

/**
 * @brief Get SNTP server IP
 * @param idx Index of the server
 * @return IP address of the server
 */
const ip_addr_t* esp_sntp_getserver(u8_t idx);

/**
 * @brief Checks if sntp is enabled
 * @return true if sntp module is enabled
 */
bool esp_sntp_enabled(void);

/**
 * @brief Gets the server reachability shift register as described in RFC 5905.
 * @param idx Index of the SNTP server
 * @return reachability shift register
 */
uint8_t esp_sntp_getreachability(uint8_t idx);

/**
 * @brief Get the configured operating mode
 *
 * @return operating mode enum
 */
esp_sntp_operatingmode_t esp_sntp_getoperatingmode(void);

#if LWIP_DHCP_GET_NTP_SRV
/**
 * @brief Enable acquiring SNTP server from DHCP
 * @param enable True for enabling SNTP from DHCP
 */
void esp_sntp_servermode_dhcp(bool enable);
#endif /* LWIP_DHCP_GET_NTP_SRV */

#if !defined(ESP_LWIP_COMPONENT_BUILD) && !defined(ESP_NETIF_COMPONENT_BUILD)
/**
 * @brief if not build within lwip, provide translating inlines,
 * that will warn about thread safety
 */
static inline __attribute__((deprecated("use esp_sntp_setoperatingmode() instead")))
void sntp_setoperatingmode(u8_t operating_mode)
{
    esp_sntp_setoperatingmode((esp_sntp_operatingmode_t)operating_mode);
}

static inline __attribute__((deprecated("use esp_sntp_servermode_dhcp() instead")))
void sntp_servermode_dhcp(int set_servers_from_dhcp)
{
#if LWIP_DHCP_GET_NTP_SRV
    esp_sntp_servermode_dhcp(set_servers_from_dhcp);
#endif
}

static inline __attribute__((deprecated("use esp_sntp_setservername() instead")))
void sntp_setservername(u8_t idx, const char *server)
{
    esp_sntp_setservername(idx, server);
}

static inline __attribute__((deprecated("use esp_sntp_init() instead")))
void sntp_init(void)
{
    esp_sntp_init();
}

static inline __attribute__((deprecated("use esp_sntp_getservername() instead")))
const char *sntp_getservername(u8_t idx)
{
    return esp_sntp_getservername(idx);
}

static inline __attribute__((deprecated("use esp_sntp_getserver() instead")))
const ip_addr_t* sntp_getserver(u8_t idx)
{
    return esp_sntp_getserver(idx);
}

static inline __attribute__((deprecated("use esp_sntp_getreachability() instead")))
uint8_t sntp_getreachability(uint8_t idx)
{
    return esp_sntp_getreachability(idx);
}

static inline __attribute__((deprecated("use esp_sntp_getoperatingmode() instead")))
esp_sntp_operatingmode_t sntp_getoperatingmode(void)
{
    return esp_sntp_getoperatingmode();
}

#endif /* ESP_LWIP_COMPONENT_BUILD */


#ifdef __cplusplus
}
#endif

#endif // __ESP_SNTP_H__

#undef SNTP_OPMODE_POLL
#define SNTP_OPMODE_POLL 0
/**
 * @file
 * SNTP client API
 */

/*
 * Copyright (c) 2007-2009 Frédéric Bernon, Simon Goldschmidt
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 * 3. The name of the author may not be used to endorse or promote products
 *    derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
 * SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
 * OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
 * IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
 * OF SUCH DAMAGE.
 *
 * This file is part of the lwIP TCP/IP stack.
 *
 * Author: Frédéric Bernon, Simon Goldschmidt
 *
 */
#ifndef LWIP_HDR_APPS_SNTP_H
#define LWIP_HDR_APPS_SNTP_H

#ifdef __cplusplus
extern "C" {
#endif

/* SNTP operating modes: default is to poll using unicast.
   The mode has to be set before calling sntp_init(). */
#define SNTP_OPMODE_POLL            0
#define SNTP_OPMODE_LISTENONLY      1
void sntp_setoperatingmode(u8_t operating_mode);
u8_t sntp_getoperatingmode(void);

void sntp_init(void);
void sntp_stop(void);
u8_t sntp_enabled(void);

void sntp_setserver(u8_t idx, const ip_addr_t *addr);
const ip_addr_t* sntp_getserver(u8_t idx);
u8_t sntp_getkodreceived(u8_t idx);

#if SNTP_MONITOR_SERVER_REACHABILITY
u8_t sntp_getreachability(u8_t idx);
#endif /* SNTP_MONITOR_SERVER_REACHABILITY */

#if SNTP_SERVER_DNS
void sntp_setservername(u8_t idx, const char *server);
const char *sntp_getservername(u8_t idx);
#endif /* SNTP_SERVER_DNS */

#if SNTP_GET_SERVERS_FROM_DHCP || SNTP_GET_SERVERS_FROM_DHCPV6
void sntp_servermode_dhcp(int set_servers_from_dhcp);
#else /* SNTP_GET_SERVERS_FROM_DHCP || SNTP_GET_SERVERS_FROM_DHCPV6 */
#define sntp_servermode_dhcp(x)
#endif /* SNTP_GET_SERVERS_FROM_DHCP || SNTP_GET_SERVERS_FROM_DHCPV6 */

#ifdef __cplusplus
}
#endif

#endif /* LWIP_HDR_APPS_SNTP_H */
/*
 * SPDX-FileCopyrightText: 2022-2025 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#pragma once

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief SNTP event base for esp-netif
 */
ESP_EVENT_DECLARE_BASE(NETIF_SNTP_EVENT);

/**
 * @brief Event IDs for NETIF_SNTP_EVENT
 */
typedef enum {
    NETIF_SNTP_TIME_SYNC = 0,  /**< System time synchronized via SNTP */
} esp_netif_sntp_event_t;

/**
 * @brief Event payload for NETIF_SNTP_TIME_SYNC
 *
 * The event data passed to handlers registered for
 * `NETIF_SNTP_EVENT`/`NETIF_SNTP_TIME_SYNC` is a pointer to this struct.
 */
typedef struct esp_netif_sntp_time_sync {
    struct timeval tv;  ///< Time of synchronization as reported by SNTP
} esp_netif_sntp_time_sync_t;


/**
 * @brief Time sync notification function
 */
typedef void (*esp_sntp_time_cb_t)(struct timeval *tv);

/**
 * @brief Utility macro for providing multiple servers in parentheses
 */
#define ESP_SNTP_SERVER_LIST(...)   { __VA_ARGS__ }

/**
 * @brief Default configuration to init SNTP with multiple servers
 * @param servers_in_list Number of servers in the list
 * @param list_of_servers List of servers (use ESP_SNTP_SERVER_LIST(...))
 *
 */
#define ESP_NETIF_SNTP_DEFAULT_CONFIG_MULTIPLE(servers_in_list, list_of_servers)   {   \
            .smooth_sync = false,                       \
            .server_from_dhcp = false,                  \
            .wait_for_sync = true,                      \
            .start = true,                              \
            .sync_cb = NULL,                            \
            .renew_servers_after_new_IP = false,        \
            .ip_event_to_renew = IP_EVENT_STA_GOT_IP,   \
            .index_of_first_server = 0,                 \
            .num_of_servers = (servers_in_list),        \
            .servers = list_of_servers,                 \
}

/**
 * @brief Default configuration with a single server
 */
#define ESP_NETIF_SNTP_DEFAULT_CONFIG(server) \
            ESP_NETIF_SNTP_DEFAULT_CONFIG_MULTIPLE(1, {server})

/**
 * @brief SNTP configuration struct
 */
typedef struct esp_sntp_config {
    bool smooth_sync;              ///< set to true if smooth sync required
    bool server_from_dhcp;         ///< set to true to request NTP server config from DHCP
    bool wait_for_sync;            ///< if true, we create a semaphore to signal time sync event
    bool start;                    ///< set to true to automatically start the SNTP service
    esp_sntp_time_cb_t sync_cb;    ///< optionally sets callback function on time sync event
    bool renew_servers_after_new_IP; ///< this is used to refresh server list if NTP provided by DHCP (which cleans other pre-configured servers)
    ip_event_t ip_event_to_renew;  ///< set the IP event id on which we refresh server list (if renew_servers_after_new_IP=true)
    size_t index_of_first_server;  ///< refresh server list after this server (if renew_servers_after_new_IP=true)
    size_t num_of_servers;         ///< number of preconfigured NTP servers
    const char* servers[CONFIG_LWIP_SNTP_MAX_SERVERS]; ///< list of servers
} esp_sntp_config_t;

/**
 * @brief Initialize SNTP with supplied config struct
 * @param config Config struct
 * @return ESP_OK on success
 */
esp_err_t esp_netif_sntp_init(const esp_sntp_config_t * config);

/**
 * @brief Start SNTP service
 *          if it wasn't started during init (config.start = false)
 *          or restart it if already started
 * @return ESP_OK on success
 */
esp_err_t esp_netif_sntp_start(void);

/**
 * @brief Deinitialize esp_netif SNTP module
 */
void esp_netif_sntp_deinit(void);

/**
 * @brief Wait for time sync event
 * @param tout Specified timeout in RTOS ticks
 * @return ESP_TIMEOUT if sync event didn't came within the timeout
 *         ESP_ERR_NOT_FINISHED if the sync event came, but we're in smooth update mode and still in progress (SNTP_SYNC_STATUS_IN_PROGRESS)
 *         ESP_OK if time sync'ed
 */
esp_err_t esp_netif_sntp_sync_wait(TickType_t tout);

/**
 * @brief Returns SNTP server's reachability shift register as described in RFC 5905.
 *
 * @param index Index of the SERVER
 * @param reachability reachability shift register
 * @return ESP_OK on success,
 *         ESP_ERR_INVALID_STATE if SNTP not initialized
 *         ESP_ERR_INVALID_ARG if invalid arguments
 */
esp_err_t esp_netif_sntp_reachability(unsigned int index, unsigned int *reachability);

#ifdef __cplusplus
}
#endif
#pragma once

#ifdef __cplusplus
extern "C" {
#endif

#define NATIVE_TIME_SNTP_SERVER_COUNT 2U
#define NATIVE_TIME_SNTP_NAME_CAPACITY 35U

typedef struct {
    uint16_t sync_interval_minutes;
    uint8_t server_count;
    char servers[NATIVE_TIME_SNTP_SERVER_COUNT][NATIVE_TIME_SNTP_NAME_CAPACITY];
} native_time_sntp_config_t;

typedef void (*native_time_sntp_sync_cb_t)(
    void *context, const struct timeval *synced_time);

// Allocates the controller mutex only; TCP/IP need not exist yet. The callback
// and context remain valid until reboot. Repeated init must use the same pair.
esp_err_t native_time_sntp_init(native_time_sntp_sync_cb_t callback, void *context);

// A station GOT_IP proves TCP/IP is initialized. This atomic latch is safe
// before init and does not mean the station is still connected.
void native_time_sntp_notify_network_ready(void);

// No TCP/IP call occurs before the ready latch. Calls are serialized. Names
// are copied into permanent storage. Equal running configurations are a no-op.
// The caller must separately serialize obtaining and applying its settings.
esp_err_t native_time_sntp_apply(const native_time_sntp_config_t *config);
esp_err_t native_time_sntp_restart(void);

// There is deliberately no runtime deinit: pending lwIP DNS is not cancelled
// by stopping SNTP. Reconfiguration guarantees name-buffer lifetime, not DNS
// generation cancellation. Pinned assertion-enabled lwIP can abort on UDP PCB
// allocation failure; the public SDK does not expose recoverable start OOM.

#ifdef __cplusplus
}
#endif

/* DNS table entry states */
typedef enum {
  DNS_STATE_UNUSED           = 0,
  DNS_STATE_NEW              = 1,
  DNS_STATE_ASKING           = 2,
  DNS_STATE_DONE             = 3
} dns_state_enum_t;

/** DNS table entry */
struct dns_table_entry {
  u32_t ttl[DNS_MAX_HOST_IP];
  ip_addr_t ipaddr[DNS_MAX_HOST_IP];
  u8_t  ipaddr_cnt;
  u16_t txid;
  u8_t  state;
  u8_t  server_idx;
  u8_t  tmr;
  u8_t  retries;
  u8_t  seqno;
#if ((LWIP_DNS_SECURE & LWIP_DNS_SECURE_RAND_SRC_PORT) != 0)
  u8_t pcb_idx;
#endif
  char name[DNS_MAX_NAME_LENGTH];
#if LWIP_IPV4 && LWIP_IPV6
  u8_t reqaddrtype;
#endif /* LWIP_IPV4 && LWIP_IPV6 */
#if LWIP_DNS_SUPPORT_MDNS_QUERIES
  u8_t is_mdns;
#endif
};

/** DNS request table entry: used when dns_gehostbyname cannot answer the
 * request from the DNS table */
struct dns_req_entry {
  /* pointer to callback on DNS query done */
  dns_found_callback found;
  /* argument passed to the callback function */
  void *arg;
#if ((LWIP_DNS_SECURE & LWIP_DNS_SECURE_NO_MULTIPLE_OUTSTANDING) != 0)
  u8_t dns_table_idx;
#endif
#if LWIP_IPV4 && LWIP_IPV6
  u8_t reqaddrtype;
#endif /* LWIP_IPV4 && LWIP_IPV6 */
};


static struct dns_table_entry dns_table[DNS_TABLE_SIZE];
static struct dns_req_entry dns_requests[DNS_MAX_REQUESTS];
static u8_t dns_seqno;
static err_t
dns_enqueue(const char *name, size_t hostnamelen, dns_found_callback found,
            void *callback_arg LWIP_DNS_ADDRTYPE_ARG(u8_t dns_addrtype) LWIP_DNS_ISMDNS_ARG(u8_t is_mdns))
{
  u8_t i;
  u8_t lseq, lseqi;
  struct dns_table_entry *entry = NULL;
  size_t namelen;
  struct dns_req_entry *req;
#if ((LWIP_DNS_SECURE & LWIP_DNS_SECURE_NO_MULTIPLE_OUTSTANDING) != 0)
  u8_t r;
#endif

  namelen = LWIP_MIN(hostnamelen, DNS_MAX_NAME_LENGTH - 1);

#if ((LWIP_DNS_SECURE & LWIP_DNS_SECURE_NO_MULTIPLE_OUTSTANDING) != 0)
  /* check for duplicate entries */
  for (i = 0; i < DNS_TABLE_SIZE; i++) {
    if ((dns_table[i].state == DNS_STATE_ASKING) &&
        (lwip_strnicmp(name, dns_table[i].name, namelen) == 0) &&
        !dns_table[i].name[namelen]) {
#if LWIP_IPV4 && LWIP_IPV6
      if (dns_table[i].reqaddrtype != dns_addrtype) {
        /* requested address types don't match
           this can lead to 2 concurrent requests, but mixing the address types
           for the same host should not be that common */
        continue;
      }
#endif /* LWIP_IPV4 && LWIP_IPV6 */
      /* this is a duplicate entry, find a free request entry */
      for (r = 0; r < DNS_MAX_REQUESTS; r++) {
        if (dns_requests[r].found == NULL) {
          dns_requests[r].found = found;
          dns_requests[r].arg = callback_arg;
          dns_requests[r].dns_table_idx = i;
          LWIP_DNS_SET_ADDRTYPE(dns_requests[r].reqaddrtype, dns_addrtype);
          LWIP_DEBUGF(DNS_DEBUG, ("dns_enqueue: \"%s\": duplicate request\n", name));
          return ERR_INPROGRESS;
        }
      }
    }
  }
  /* no duplicate entries found */
#endif

  /* search an unused entry, or the oldest one */
  lseq = 0;
  lseqi = DNS_TABLE_SIZE;
  for (i = 0; i < DNS_TABLE_SIZE; ++i) {
    entry = &dns_table[i];
    /* is it an unused entry ? */
    if (entry->state == DNS_STATE_UNUSED) {
      break;
    }
    /* check if this is the oldest completed entry */
    if (entry->state == DNS_STATE_DONE) {
      u8_t age = (u8_t)(dns_seqno - entry->seqno);
      if (age > lseq) {
        lseq = age;
        lseqi = i;
      }
    }
  }

  /* if we don't have found an unused entry, use the oldest completed one */
  if (i == DNS_TABLE_SIZE) {
    if ((lseqi >= DNS_TABLE_SIZE) || (dns_table[lseqi].state != DNS_STATE_DONE)) {
      /* no entry can be used now, table is full */
      LWIP_DEBUGF(DNS_DEBUG, ("dns_enqueue: \"%s\": DNS entries table is full\n", name));
      return ERR_MEM;
    } else {
      /* use the oldest completed one */
      i = lseqi;
      entry = &dns_table[i];
    }
  }

#if ((LWIP_DNS_SECURE & LWIP_DNS_SECURE_NO_MULTIPLE_OUTSTANDING) != 0)
  /* find a free request entry */
  req = NULL;
  for (r = 0; r < DNS_MAX_REQUESTS; r++) {
    if (dns_requests[r].found == NULL) {
      req = &dns_requests[r];
      break;
    }
  }
  if (req == NULL) {
    /* no request entry can be used now, table is full */
    LWIP_DEBUGF(DNS_DEBUG, ("dns_enqueue: \"%s\": DNS request entries table is full\n", name));
    return ERR_MEM;
  }
  req->dns_table_idx = i;
#else
  /* in this configuration, the entry index is the same as the request index */
  req = &dns_requests[i];
#endif

  /* use this entry */
  LWIP_DEBUGF(DNS_DEBUG, ("dns_enqueue: \"%s\": use DNS entry %"U16_F"\n", name, (u16_t)(i)));

  /* fill the entry */
  entry->state = DNS_STATE_NEW;
  entry->seqno = dns_seqno;
  entry->ipaddr_cnt = 0;
  {
    u8_t j;
    for (j = 0; j < DNS_MAX_HOST_IP; j++) {
      ip_addr_set_zero(&entry->ipaddr[j]);
    }
  }
  LWIP_DNS_SET_ADDRTYPE(entry->reqaddrtype, dns_addrtype);
  LWIP_DNS_SET_ADDRTYPE(req->reqaddrtype, dns_addrtype);
  req->found = found;
  req->arg   = callback_arg;
  MEMCPY(entry->name, name, namelen);
  entry->name[namelen] = 0;

#if ((LWIP_DNS_SECURE & LWIP_DNS_SECURE_RAND_SRC_PORT) != 0)
  entry->pcb_idx = dns_alloc_pcb();
  if (entry->pcb_idx >= DNS_MAX_SOURCE_PORTS) {
    /* failed to get a UDP pcb */
    LWIP_DEBUGF(DNS_DEBUG, ("dns_enqueue: \"%s\": failed to allocate a pcb\n", name));
    entry->state = DNS_STATE_UNUSED;
    entry->ipaddr_cnt = 0;
    req->found = NULL;
    return ERR_MEM;
  }
  LWIP_DEBUGF(DNS_DEBUG, ("dns_enqueue: \"%s\": use DNS pcb %"U16_F"\n", name, (u16_t)(entry->pcb_idx)));
#endif

#if LWIP_DNS_SUPPORT_MDNS_QUERIES
  entry->is_mdns = is_mdns;
#endif

  dns_seqno++;

  /* force to send query without waiting timer */
  dns_check_entry(i);
#if ESP_LWIP_DNS_TIMERS_ONDEMAND
  if (!s_is_tmr_start) {
    sys_timeout(DNS_TMR_INTERVAL, dns_timeout_cb, NULL);
    s_is_tmr_start = true;
  }
#endif /* ESP_LWIP_DNS_TIMERS_ONDEMAND */

  /* dns query is enqueued */
  return ERR_INPROGRESS;
}

static void dns_check_entry(u8_t index){dns_table[index].state=DNS_STATE_ASKING;}
static err_t dns_gethostbyname(const char *name,ip_addr_t *address,dns_found_callback callback,void *context){(void)address;assert(in_tcpip);return dns_enqueue(name,strlen(name),callback,context);}

#define TAG SDK_EXTENSION_TAG
#define settimeofday host_settimeofday
#define gettimeofday host_gettimeofday
#define adjtime host_adjtime
/*
 * SPDX-FileCopyrightText: 2015-2024 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */

// Remove compat macro and include lwip API
#undef SNTP_OPMODE_POLL
#define SNTP_OPMODE_POLL 0
#define SNTP_OPMODE_POLL 0

static const char *TAG = "sntp";

ESP_STATIC_ASSERT(SNTP_OPMODE_POLL == ESP_SNTP_OPMODE_POLL, "SNTP mode in lwip doesn't match the IDF enum. Please make sure lwIP version is correct");
ESP_STATIC_ASSERT(SNTP_OPMODE_LISTENONLY == ESP_SNTP_OPMODE_LISTENONLY, "SNTP mode in lwip doesn't match the IDF enum. Please make sure lwIP version is correct");

#define SNTP_ERROR(func, message) do { \
        err_t err = func;   \
        LWIP_ERROR(message, err == ERR_OK, );   \
    } while (0)

static volatile sntp_sync_mode_t sntp_sync_mode = SNTP_SYNC_MODE_IMMED;
static volatile sntp_sync_status_t sntp_sync_status = SNTP_SYNC_STATUS_RESET;
static sntp_sync_time_cb_t time_sync_notification_cb = NULL;
static uint32_t s_sync_interval = CONFIG_LWIP_SNTP_UPDATE_DELAY;

inline void sntp_set_sync_status(sntp_sync_status_t sync_status)
{
    sntp_sync_status = sync_status;
}

void __attribute__((weak)) sntp_sync_time(struct timeval *tv)
{
    if (sntp_sync_mode == SNTP_SYNC_MODE_IMMED) {
        settimeofday(tv, NULL);
        sntp_set_sync_status(SNTP_SYNC_STATUS_COMPLETED);
    } else if (sntp_sync_mode == SNTP_SYNC_MODE_SMOOTH) {
        struct timeval tv_now;
        gettimeofday(&tv_now, NULL);
        int64_t cpu_time = (int64_t)tv_now.tv_sec * 1000000L + (int64_t)tv_now.tv_usec;
        int64_t sntp_time = (int64_t)tv->tv_sec * 1000000L + (int64_t)tv->tv_usec;
        int64_t delta = sntp_time - cpu_time;
        struct timeval tv_delta = { .tv_sec = delta / 1000000L, .tv_usec = delta % 1000000L };
        if (adjtime(&tv_delta, NULL) == -1) {
            ESP_LOGD(TAG, "Function adjtime don't update time because the error is very big");
            settimeofday(tv, NULL);
            ESP_LOGD(TAG, "Time was synchronized through settimeofday");
            sntp_set_sync_status(SNTP_SYNC_STATUS_COMPLETED);
        } else {
            sntp_set_sync_status(SNTP_SYNC_STATUS_IN_PROGRESS);
        }
    }
    if (time_sync_notification_cb) {
        time_sync_notification_cb(tv);
    }
}

void sntp_set_sync_mode(sntp_sync_mode_t sync_mode)
{
    sntp_sync_mode = sync_mode;
}

sntp_sync_mode_t sntp_get_sync_mode(void)
{
    return sntp_sync_mode;
}

// set a callback function for time synchronization notification
void sntp_set_time_sync_notification_cb(sntp_sync_time_cb_t callback)
{
    time_sync_notification_cb = callback;
}

sntp_sync_status_t sntp_get_sync_status(void)
{
    sntp_sync_status_t ret_sync_status = SNTP_SYNC_STATUS_RESET;
    sntp_sync_status_t sync_status = sntp_sync_status;
    if (sync_status == SNTP_SYNC_STATUS_COMPLETED) {
        sntp_set_sync_status(SNTP_SYNC_STATUS_RESET);
        ret_sync_status = SNTP_SYNC_STATUS_COMPLETED;
    } else if (sync_status == SNTP_SYNC_STATUS_IN_PROGRESS) {
        struct timeval outdelta;
        adjtime(NULL, &outdelta);
        if (outdelta.tv_sec == 0 && outdelta.tv_usec == 0) {
            sntp_set_sync_status(SNTP_SYNC_STATUS_RESET);
            ret_sync_status = SNTP_SYNC_STATUS_COMPLETED;
        } else {
            ret_sync_status = SNTP_SYNC_STATUS_IN_PROGRESS;
        }
    }
    return ret_sync_status;
}

void sntp_set_sync_interval(uint32_t interval_ms)
{
    if (interval_ms < 15000) {
        // SNTPv4 RFC 4330 enforces a minimum update time of 15 seconds
        interval_ms = 15000;
    }
    s_sync_interval = interval_ms;
}

uint32_t sntp_get_sync_interval(void)
{
    return s_sync_interval;
}

static void sntp_do_restart(void *ctx)
{
    (void)ctx;
    sntp_stop();
    sntp_init();
}

bool sntp_restart(void)
{
    if (sntp_enabled()) {
        SNTP_ERROR(tcpip_callback(sntp_do_restart, NULL), "sntp_restart: tcpip_callback() failed");
        return true;
    }
    return false;
}

void sntp_set_system_time(uint32_t sec, uint32_t us)
{
    // Note: SNTP/NTP timestamp is defined as 64-bit fixed point int
    // in seconds from 1900 (integer part is the first 32 bits)
    // which overflows in 2036.
    // The lifetime of the NTP timestamps has been extended by convention
    // of the MSB bit 0 to span between 1968 and 2104. This is implemented
    // in lwip sntp module, so this API returns number of seconds/milliseconds
    // representing dates range from 1968 to 2104.
    // (see: RFC-4330#section-3 and https://github.com/lwip-tcpip/lwip/blob/239918cc/src/apps/sntp/sntp.c#L129-L134)
    // Warning: Here, we convert the 32 bit NTP timestamp to 64 bit representation
    // of system time (time_t). This won't work for timestamps in future
    // after some time in 2104
    struct timeval tv = { .tv_sec = sec, .tv_usec = us };
    sntp_sync_time(&tv);
}

void sntp_get_system_time(uint32_t *sec, uint32_t *us)
{
    struct timeval tv = { .tv_sec = 0, .tv_usec = 0 };
    gettimeofday(&tv, NULL);
    // Warning: Here, we convert 64 bit representation of system time (time_t) to
    // 32 bit NTP timestamp. This won't work for future timestamps after some time in 2104
    // (see: RFC-4330#section-3)
    *(sec) = tv.tv_sec;
    *(us) = tv.tv_usec;
    sntp_set_sync_status(SNTP_SYNC_STATUS_RESET);
}


#undef TAG
#undef settimeofday
#undef gettimeofday
#undef adjtime
/**
 * @file
 * SNTP client module
 */

/*
 * Copyright (c) 2007-2009 Frédéric Bernon, Simon Goldschmidt
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 * 3. The name of the author may not be used to endorse or promote products
 *    derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
 * SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
 * OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
 * IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
 * OF SUCH DAMAGE.
 *
 * This file is part of the lwIP TCP/IP stack.
 *
 * Author: Frédéric Bernon, Simon Goldschmidt
 */


/**
 * @defgroup sntp SNTP
 * @ingroup apps
 *
 * This is simple "SNTP" client for the lwIP raw API.
 * It is a minimal implementation of SNTPv4 as specified in RFC 4330.
 *
 * You need to increase MEMP_NUM_SYS_TIMEOUT by one if you use SNTP!
 *
 * For a list of some public NTP servers, see this link:
 * http://support.ntp.org/bin/view/Servers/NTPPoolServers
 *
 * @todo:
 * - complete SNTP_CHECK_RESPONSE checks 3 and 4
 */

#if LWIP_UDP

/* Handle support for more than one server via SNTP_MAX_SERVERS */
#if SNTP_MAX_SERVERS > 1
#define SNTP_SUPPORT_MULTIPLE_SERVERS 1
#else /* NTP_MAX_SERVERS > 1 */
#define SNTP_SUPPORT_MULTIPLE_SERVERS 0
#endif /* NTP_MAX_SERVERS > 1 */

#ifndef SNTP_SUPPRESS_DELAY_CHECK
#if SNTP_UPDATE_DELAY < 15000
#error "SNTPv4 RFC 4330 enforces a minimum update time of 15 seconds (define SNTP_SUPPRESS_DELAY_CHECK to disable this error)!"
#endif
#endif

/* the various debug levels for this file */
#define SNTP_DEBUG_TRACE        (SNTP_DEBUG | LWIP_DBG_TRACE)
#define SNTP_DEBUG_STATE        (SNTP_DEBUG | LWIP_DBG_STATE)
#define SNTP_DEBUG_WARN         (SNTP_DEBUG | LWIP_DBG_LEVEL_WARNING)
#define SNTP_DEBUG_WARN_STATE   (SNTP_DEBUG | LWIP_DBG_LEVEL_WARNING | LWIP_DBG_STATE)
#define SNTP_DEBUG_SERIOUS      (SNTP_DEBUG | LWIP_DBG_LEVEL_SERIOUS)

#define SNTP_ERR_KOD                1

/* SNTP protocol defines */
#define SNTP_MSG_LEN                48

#define SNTP_OFFSET_LI_VN_MODE      0
#define SNTP_LI_MASK                0xC0
#define SNTP_LI_NO_WARNING          (0x00 << 6)
#define SNTP_LI_LAST_MINUTE_61_SEC  (0x01 << 6)
#define SNTP_LI_LAST_MINUTE_59_SEC  (0x02 << 6)
#define SNTP_LI_ALARM_CONDITION     (0x03 << 6) /* (clock not synchronized) */

#define SNTP_VERSION_MASK           0x38
#define SNTP_VERSION                (4/* NTP Version 4*/<<3)

#define SNTP_MODE_MASK              0x07
#define SNTP_MODE_CLIENT            0x03
#define SNTP_MODE_SERVER            0x04
#define SNTP_MODE_BROADCAST         0x05

#define SNTP_OFFSET_STRATUM         1
#define SNTP_STRATUM_KOD            0x00

#define SNTP_OFFSET_ORIGINATE_TIME  24
#define SNTP_OFFSET_RECEIVE_TIME    32
#define SNTP_OFFSET_TRANSMIT_TIME   40

/* Number of seconds between 1970 and Feb 7, 2036 06:28:16 UTC (epoch 1) */
#define DIFF_SEC_1970_2036          ((u32_t)2085978496L)

/** Convert NTP timestamp fraction to microseconds.
 */
#ifndef SNTP_FRAC_TO_US
# if LWIP_HAVE_INT64
#  define SNTP_FRAC_TO_US(f)        ((u32_t)(((u64_t)(f) * 1000000UL) >> 32))
# else
#  define SNTP_FRAC_TO_US(f)        ((u32_t)(f) / 4295)
# endif
#endif /* !SNTP_FRAC_TO_US */

/* Configure behaviour depending on native, microsecond or second precision.
 * Treat NTP timestamps as signed two's-complement integers. This way,
 * timestamps that have the MSB set simply become negative offsets from
 * the epoch (Feb 7, 2036 06:28:16 UTC). Representable dates range from
 * 1968 to 2104.
 */
#ifndef SNTP_SET_SYSTEM_TIME_NTP
# ifdef SNTP_SET_SYSTEM_TIME_US
#  define SNTP_SET_SYSTEM_TIME_NTP(s, f) \
    SNTP_SET_SYSTEM_TIME_US((u32_t)((s) + DIFF_SEC_1970_2036), SNTP_FRAC_TO_US(f))
# else
#  define SNTP_SET_SYSTEM_TIME_NTP(s, f) \
    SNTP_SET_SYSTEM_TIME((u32_t)((s) + DIFF_SEC_1970_2036))
# endif
#endif /* !SNTP_SET_SYSTEM_TIME_NTP */

/* Get the system time either natively as NTP timestamp or convert from
 * Unix time in seconds and microseconds. Take care to avoid overflow if the
 * microsecond value is at the maximum of 999999. Also add 0.5 us fudge to
 * avoid special values like 0, and to mask round-off errors that would
 * otherwise break round-trip conversion identity.
 */
#ifndef SNTP_GET_SYSTEM_TIME_NTP
# define SNTP_GET_SYSTEM_TIME_NTP(s, f) do { \
    u32_t sec_, usec_; \
    SNTP_GET_SYSTEM_TIME(sec_, usec_); \
    (s) = (s32_t)(sec_ - DIFF_SEC_1970_2036); \
    (f) = usec_ * 4295 - ((usec_ * 2143) >> 16) + 2147; \
  } while (0)
#endif /* !SNTP_GET_SYSTEM_TIME_NTP */

/* Start offset of the timestamps to extract from the SNTP packet */
#define SNTP_OFFSET_TIMESTAMPS \
    (SNTP_OFFSET_TRANSMIT_TIME + 8 - sizeof(struct sntp_timestamps))

/* Round-trip delay arithmetic helpers */
#if SNTP_COMP_ROUNDTRIP
# if !LWIP_HAVE_INT64
#  error "SNTP round-trip delay compensation requires 64-bit arithmetic"
# endif
# define SNTP_SEC_FRAC_TO_S64(s, f) \
    ((s64_t)(((u64_t)(s) << 32) | (u32_t)(f)))
# define SNTP_TIMESTAMP_TO_S64(t) \
    SNTP_SEC_FRAC_TO_S64(lwip_ntohl((t).sec), lwip_ntohl((t).frac))
#endif /* SNTP_COMP_ROUNDTRIP */

/**
 * 64-bit NTP timestamp, in network byte order.
 */
struct sntp_time {
  u32_t sec;
  u32_t frac;
};

/**
 * Timestamps to be extracted from the NTP header.
 */
struct sntp_timestamps {
#if SNTP_COMP_ROUNDTRIP || SNTP_CHECK_RESPONSE >= 2
  struct sntp_time orig;
  struct sntp_time recv;
#endif
  struct sntp_time xmit;
};

/**
 * SNTP packet format (without optional fields)
 * Timestamps are coded as 64 bits:
 * - signed 32 bits seconds since Feb 07, 2036, 06:28:16 UTC (epoch 1)
 * - unsigned 32 bits seconds fraction (2^32 = 1 second)
 */
#ifdef PACK_STRUCT_USE_INCLUDES
#endif
PACK_STRUCT_BEGIN
struct sntp_msg {
  PACK_STRUCT_FLD_8(u8_t  li_vn_mode);
  PACK_STRUCT_FLD_8(u8_t  stratum);
  PACK_STRUCT_FLD_8(u8_t  poll);
  PACK_STRUCT_FLD_8(u8_t  precision);
  PACK_STRUCT_FIELD(u32_t root_delay);
  PACK_STRUCT_FIELD(u32_t root_dispersion);
  PACK_STRUCT_FIELD(u32_t reference_identifier);
  PACK_STRUCT_FIELD(u32_t reference_timestamp[2]);
  PACK_STRUCT_FIELD(u32_t originate_timestamp[2]);
  PACK_STRUCT_FIELD(u32_t receive_timestamp[2]);
  PACK_STRUCT_FIELD(u32_t transmit_timestamp[2]);
} PACK_STRUCT_STRUCT;
PACK_STRUCT_END
#ifdef PACK_STRUCT_USE_INCLUDES
#endif

/* function prototypes */
static void sntp_request(void *arg);

/** The operating mode */
static u8_t sntp_opmode;

/** The UDP pcb used by the SNTP client */
static struct udp_pcb *sntp_pcb;
/** Names/Addresses of servers */
struct sntp_server {
#if SNTP_SERVER_DNS
  const char *name;
#endif /* SNTP_SERVER_DNS */
  ip_addr_t addr;
#if SNTP_MONITOR_SERVER_REACHABILITY
  /** Reachability shift register as described in RFC 5905 */
  u8_t reachability;
#endif /* SNTP_MONITOR_SERVER_REACHABILITY */
#if SNTP_SUPPORT_MULTIPLE_SERVERS
  u8_t kod_received;
#endif
};
static struct sntp_server sntp_servers[SNTP_MAX_SERVERS];

#if SNTP_GET_SERVERS_FROM_DHCP || SNTP_GET_SERVERS_FROM_DHCPV6
static u8_t sntp_set_servers_from_dhcp;
#endif /* SNTP_GET_SERVERS_FROM_DHCP || SNTP_GET_SERVERS_FROM_DHCPV6 */
#if SNTP_SUPPORT_MULTIPLE_SERVERS
/** The currently used server (initialized to 0) */
static u8_t sntp_current_server;
#else /* SNTP_SUPPORT_MULTIPLE_SERVERS */
#define sntp_current_server 0
#endif /* SNTP_SUPPORT_MULTIPLE_SERVERS */

#if SNTP_RETRY_TIMEOUT_EXP
#define SNTP_RESET_RETRY_TIMEOUT() sntp_retry_timeout = SNTP_RETRY_TIMEOUT
/** Retry time, initialized with SNTP_RETRY_TIMEOUT and doubled with each retry. */
static u32_t sntp_retry_timeout;
#else /* SNTP_RETRY_TIMEOUT_EXP */
#define SNTP_RESET_RETRY_TIMEOUT()
#define sntp_retry_timeout SNTP_RETRY_TIMEOUT
#endif /* SNTP_RETRY_TIMEOUT_EXP */

#if SNTP_CHECK_RESPONSE >= 1
/** Saves the last server address to compare with response */
static ip_addr_t sntp_last_server_address;
#endif /* SNTP_CHECK_RESPONSE >= 1 */

#if SNTP_CHECK_RESPONSE >= 2
/** Saves the last timestamp sent (which is sent back by the server)
 * to compare against in response. Stored in network byte order. */
static struct sntp_time sntp_last_timestamp_sent;
#endif /* SNTP_CHECK_RESPONSE >= 2 */

#if defined(LWIP_DEBUG) && !defined(sntp_format_time)
/* Debug print helper. */
static const char *
sntp_format_time(s32_t sec)
{
  time_t ut;
  ut = (u32_t)((u32_t)sec + DIFF_SEC_1970_2036);
  return ctime(&ut);
}
#endif /* LWIP_DEBUG && !sntp_format_time */

/**
 * SNTP processing of received timestamp
 */
static void
sntp_process(const struct sntp_timestamps *timestamps)
{
  s32_t sec;
  u32_t frac;

  sec  = (s32_t)lwip_ntohl(timestamps->xmit.sec);
  frac = lwip_ntohl(timestamps->xmit.frac);

#if SNTP_COMP_ROUNDTRIP
# if SNTP_CHECK_RESPONSE >= 2
  if (timestamps->recv.sec != 0 || timestamps->recv.frac != 0)
# endif
  {
    s32_t dest_sec;
    u32_t dest_frac;
    u32_t step_sec;

    /* Get the destination time stamp, i.e. the current system time */
    SNTP_GET_SYSTEM_TIME_NTP(dest_sec, dest_frac);

    step_sec = (dest_sec < sec) ? ((u32_t)sec - (u32_t)dest_sec)
               : ((u32_t)dest_sec - (u32_t)sec);
    /* In order to avoid overflows, skip the compensation if the clock step
     * is larger than about 34 years. */
    if ((step_sec >> 30) == 0) {
      s64_t t1, t2, t3, t4;

      t4 = SNTP_SEC_FRAC_TO_S64(dest_sec, dest_frac);
      t3 = SNTP_SEC_FRAC_TO_S64(sec, frac);
      t1 = SNTP_TIMESTAMP_TO_S64(timestamps->orig);
      t2 = SNTP_TIMESTAMP_TO_S64(timestamps->recv);
      /* Clock offset calculation according to RFC 4330 */
      t4 += ((t2 - t1) + (t3 - t4)) / 2;

      sec  = (s32_t)((u64_t)t4 >> 32);
      frac = (u32_t)((u64_t)t4);
    }
  }
#endif /* SNTP_COMP_ROUNDTRIP */

  SNTP_SET_SYSTEM_TIME_NTP(sec, frac);
  LWIP_UNUSED_ARG(frac); /* might be unused if only seconds are set */
  LWIP_DEBUGF(SNTP_DEBUG_TRACE, ("sntp_process: %s, %" U32_F " us\n",
                                 sntp_format_time(sec), SNTP_FRAC_TO_US(frac)));
}

/**
 * Initialize request struct to be sent to server.
 */
static void
sntp_initialize_request(struct sntp_msg *req)
{
  memset(req, 0, SNTP_MSG_LEN);
  req->li_vn_mode = SNTP_LI_NO_WARNING | SNTP_VERSION | SNTP_MODE_CLIENT;

#if SNTP_CHECK_RESPONSE >= 2 || SNTP_COMP_ROUNDTRIP
  {
    s32_t secs;
    u32_t sec, frac;
    /* Get the transmit timestamp */
    SNTP_GET_SYSTEM_TIME_NTP(secs, frac);
    sec  = lwip_htonl((u32_t)secs);
    frac = lwip_htonl(frac);

# if SNTP_CHECK_RESPONSE >= 2
    sntp_last_timestamp_sent.sec  = sec;
    sntp_last_timestamp_sent.frac = frac;
# endif
    req->transmit_timestamp[0] = sec;
    req->transmit_timestamp[1] = frac;
  }
#endif /* SNTP_CHECK_RESPONSE >= 2 || SNTP_COMP_ROUNDTRIP */
}

/**
 * Retry: send a new request (and increase retry timeout).
 *
 * @param arg is unused (only necessary to conform to sys_timeout)
 */
static void
sntp_retry(void *arg)
{
  LWIP_UNUSED_ARG(arg);

  LWIP_DEBUGF(SNTP_DEBUG_STATE, ("sntp_retry: Next request will be sent in %"U32_F" ms\n",
                                 sntp_retry_timeout));

  /* set up a timer to send a retry and increase the retry delay */
  sys_untimeout(sntp_request, NULL);
  sys_timeout(sntp_retry_timeout, sntp_request, NULL);

#if SNTP_RETRY_TIMEOUT_EXP
  {
    u32_t new_retry_timeout;
    /* increase the timeout for next retry */
    new_retry_timeout = sntp_retry_timeout << 1;
    /* limit to maximum timeout and prevent overflow */
    if ((new_retry_timeout <= SNTP_RETRY_TIMEOUT_MAX) &&
        (new_retry_timeout > sntp_retry_timeout)) {
      sntp_retry_timeout = new_retry_timeout;
    } else {
      sntp_retry_timeout = SNTP_RETRY_TIMEOUT_MAX;
    }
  }
#endif /* SNTP_RETRY_TIMEOUT_EXP */
}

#if SNTP_SUPPORT_MULTIPLE_SERVERS
/**
 * If Kiss-of-Death is received (or another packet parsing error),
 * try the next server or retry the current server and increase the retry
 * timeout if only one server is available.
 * (implicitly, SNTP_MAX_SERVERS > 1)
 *
 * @param arg is unused (only necessary to conform to sys_timeout)
 */
static void
sntp_try_next_server(void *arg)
{
  u8_t old_server, i;
  LWIP_UNUSED_ARG(arg);

  old_server = sntp_current_server;
  for (i = 0; i < SNTP_MAX_SERVERS - 1; i++) {
    sntp_current_server++;
    if (sntp_current_server >= SNTP_MAX_SERVERS) {
      sntp_current_server = 0;
    }
    if (sntp_servers[sntp_current_server].kod_received) {
      /* KOD received, don't use this server */
      continue;
    }
    if (!ip_addr_isany(&sntp_servers[sntp_current_server].addr)
#if SNTP_SERVER_DNS
        || (sntp_servers[sntp_current_server].name != NULL)
#endif
       ) {
      LWIP_DEBUGF(SNTP_DEBUG_STATE, ("sntp_try_next_server: Sending request to server %"U16_F"\n",
                                     (u16_t)sntp_current_server));
      /* new server: reset retry timeout */
      SNTP_RESET_RETRY_TIMEOUT();
      /* instantly send a request to the next server */
      sntp_request(NULL);
      return;
    }
  }
  /* no other valid server found */
  sntp_current_server = old_server;
  sntp_retry(NULL);
}

static void
sntp_kod_try_next_server(void *arg)
{
  sntp_servers[sntp_current_server].kod_received = 1;
  sntp_try_next_server(arg);
}

#else /* SNTP_SUPPORT_MULTIPLE_SERVERS */
/* Always retry on error if only one server is supported */
#define sntp_try_next_server     sntp_retry
#define sntp_kod_try_next_server sntp_retry
#endif /* SNTP_SUPPORT_MULTIPLE_SERVERS */

/** UDP recv callback for the sntp pcb */
static void
sntp_recv(void *arg, struct udp_pcb *pcb, struct pbuf *p, const ip_addr_t *addr, u16_t port)
{
  struct sntp_timestamps timestamps;
  u8_t mode;
  u8_t stratum;
  err_t err;

  LWIP_UNUSED_ARG(arg);
  LWIP_UNUSED_ARG(pcb);

  err = ERR_ARG;
#if SNTP_CHECK_RESPONSE >= 1
  /* check server address and port */
  if (((sntp_opmode != SNTP_OPMODE_POLL) || ip_addr_eq(addr, &sntp_last_server_address)) &&
      (port == SNTP_PORT))
#else /* SNTP_CHECK_RESPONSE >= 1 */
  LWIP_UNUSED_ARG(addr);
  LWIP_UNUSED_ARG(port);
#endif /* SNTP_CHECK_RESPONSE >= 1 */
  {
    /* process the response */
    if (p->tot_len == SNTP_MSG_LEN) {
      mode = pbuf_get_at(p, SNTP_OFFSET_LI_VN_MODE) & SNTP_MODE_MASK;
      /* if this is a SNTP response... */
      if (((sntp_opmode == SNTP_OPMODE_POLL)       && (mode == SNTP_MODE_SERVER)) ||
          ((sntp_opmode == SNTP_OPMODE_LISTENONLY) && (mode == SNTP_MODE_BROADCAST))) {
        stratum = pbuf_get_at(p, SNTP_OFFSET_STRATUM);

        if (stratum == SNTP_STRATUM_KOD) {
          /* Kiss-of-death packet. Use another server or increase UPDATE_DELAY. */
          err = SNTP_ERR_KOD;
          LWIP_DEBUGF(SNTP_DEBUG_STATE, ("sntp_recv: Received Kiss-of-Death\n"));
        } else {
          pbuf_copy_partial(p, &timestamps, sizeof(timestamps), SNTP_OFFSET_TIMESTAMPS);
#if SNTP_CHECK_RESPONSE >= 2
          /* check originate_timetamp against sntp_last_timestamp_sent */
          if (timestamps.orig.sec != sntp_last_timestamp_sent.sec ||
              timestamps.orig.frac != sntp_last_timestamp_sent.frac) {
            LWIP_DEBUGF(SNTP_DEBUG_WARN,
                        ("sntp_recv: Invalid originate timestamp in response\n"));
          } else
#endif /* SNTP_CHECK_RESPONSE >= 2 */
            /* @todo: add code for SNTP_CHECK_RESPONSE >= 3 and >= 4 here */
          {
            /* correct answer */
            err = ERR_OK;
          }
        }
      } else {
        LWIP_DEBUGF(SNTP_DEBUG_WARN, ("sntp_recv: Invalid mode in response: %"U16_F"\n", (u16_t)mode));
        /* wait for correct response */
        err = ERR_TIMEOUT;
      }
    } else {
      LWIP_DEBUGF(SNTP_DEBUG_WARN, ("sntp_recv: Invalid packet length: %"U16_F"\n", p->tot_len));
    }
  }
#if SNTP_CHECK_RESPONSE >= 1
  else {
    /* packet from wrong remote address or port, wait for correct response */
    err = ERR_TIMEOUT;
  }
#endif /* SNTP_CHECK_RESPONSE >= 1 */

  pbuf_free(p);

  if (err == ERR_OK) {
    /* correct packet received: process it it */
    sntp_process(&timestamps);

#if SNTP_MONITOR_SERVER_REACHABILITY
    /* indicate that server responded */
    sntp_servers[sntp_current_server].reachability |= 1;
#endif /* SNTP_MONITOR_SERVER_REACHABILITY */
    /* Set up timeout for next request (only if poll response was received)*/
    if (sntp_opmode == SNTP_OPMODE_POLL) {
      u32_t sntp_update_delay;
      sys_untimeout(sntp_try_next_server, NULL);
      sys_untimeout(sntp_request, NULL);

      /* Correct response, reset retry timeout */
      SNTP_RESET_RETRY_TIMEOUT();

      sntp_update_delay = (u32_t)SNTP_UPDATE_DELAY;
      sys_timeout(sntp_update_delay, sntp_request, NULL);
      LWIP_DEBUGF(SNTP_DEBUG_STATE, ("sntp_recv: Scheduled next time request: %"U32_F" ms\n",
                                     sntp_update_delay));
    }
  } else if (err == SNTP_ERR_KOD) {
    /* KOD errors are only processed in case of an explicit poll response */
    if (sntp_opmode == SNTP_OPMODE_POLL) {
      /* Kiss-of-death packet. Use another server or increase UPDATE_DELAY. */
      sys_untimeout(sntp_request, NULL);
      sntp_kod_try_next_server(NULL);
    }
  } else {
    /* ignore any broken packet, poll mode: retry after timeout to avoid flooding */
  }
}

/** Actually send an sntp request to a server.
 *
 * @param server_addr resolved IP address of the SNTP server
 */
static void
sntp_send_request(const ip_addr_t *server_addr)
{
  struct pbuf *p;

  LWIP_ASSERT("server_addr != NULL", server_addr != NULL);

  p = pbuf_alloc(PBUF_TRANSPORT, SNTP_MSG_LEN, PBUF_RAM);
  if (p != NULL) {
    struct sntp_msg *sntpmsg = (struct sntp_msg *)p->payload;
    LWIP_DEBUGF(SNTP_DEBUG_STATE, ("sntp_send_request: Sending request to server\n"));
    /* initialize request message */
    sntp_initialize_request(sntpmsg);
    /* send request */
    udp_sendto(sntp_pcb, p, server_addr, SNTP_PORT);
    /* free the pbuf after sending it */
    pbuf_free(p);
#if SNTP_MONITOR_SERVER_REACHABILITY
    /* indicate new packet has been sent */
    sntp_servers[sntp_current_server].reachability <<= 1;
#endif /* SNTP_MONITOR_SERVER_REACHABILITY */
    /* set up receive timeout: try next server or retry on timeout */
    sys_untimeout(sntp_try_next_server, NULL);
    sys_timeout((u32_t)SNTP_RECV_TIMEOUT, sntp_try_next_server, NULL);
#if SNTP_CHECK_RESPONSE >= 1
    /* save server address to verify it in sntp_recv */
    ip_addr_copy(sntp_last_server_address, *server_addr);
#endif /* SNTP_CHECK_RESPONSE >= 1 */
  } else {
    LWIP_DEBUGF(SNTP_DEBUG_SERIOUS, ("sntp_send_request: Out of memory, trying again in %"U32_F" ms\n",
                                     (u32_t)SNTP_RETRY_TIMEOUT));
    /* out of memory: set up a timer to send a retry */
    sys_untimeout(sntp_request, NULL);
    sys_timeout((u32_t)SNTP_RETRY_TIMEOUT, sntp_request, NULL);
  }
}

#if SNTP_SERVER_DNS
/**
 * DNS found callback when using DNS names as server address.
 */
static void
sntp_dns_found(const char *hostname, const ip_addr_t *ipaddr, void *arg)
{
  LWIP_UNUSED_ARG(hostname);
  LWIP_UNUSED_ARG(arg);

  if (ipaddr != NULL) {
    /* Address resolved, send request */
    LWIP_DEBUGF(SNTP_DEBUG_STATE, ("sntp_dns_found: Server address resolved, sending request\n"));
    sntp_servers[sntp_current_server].addr = *ipaddr;
    sntp_send_request(ipaddr);
  } else {
    /* DNS resolving failed -> try another server */
    LWIP_DEBUGF(SNTP_DEBUG_WARN_STATE, ("sntp_dns_found: Failed to resolve server address resolved, trying next server\n"));
    sntp_try_next_server(NULL);
  }
}
#endif /* SNTP_SERVER_DNS */

/**
 * Send out an sntp request.
 *
 * @param arg is unused (only necessary to conform to sys_timeout)
 */
static void
sntp_request(void *arg)
{
  ip_addr_t sntp_server_address;
  err_t err;

  LWIP_UNUSED_ARG(arg);

  /* initialize SNTP server address */
#if SNTP_SERVER_DNS
  if (sntp_servers[sntp_current_server].name) {
    /* always resolve the name and rely on dns-internal caching & timeout */
    ip_addr_set_zero(&sntp_servers[sntp_current_server].addr);
    err = dns_gethostbyname(sntp_servers[sntp_current_server].name, &sntp_server_address,
                            sntp_dns_found, NULL);
    if (err == ERR_INPROGRESS) {
      /* DNS request sent, wait for sntp_dns_found being called */
      LWIP_DEBUGF(SNTP_DEBUG_STATE, ("sntp_request: Waiting for server address to be resolved.\n"));
      return;
    } else if (err == ERR_OK) {
      sntp_servers[sntp_current_server].addr = sntp_server_address;
    }
  } else
#endif /* SNTP_SERVER_DNS */
  {
    sntp_server_address = sntp_servers[sntp_current_server].addr;
    err = (ip_addr_isany_val(sntp_server_address)) ? ERR_ARG : ERR_OK;
  }

  if (err == ERR_OK) {
    LWIP_DEBUGF(SNTP_DEBUG_TRACE, ("sntp_request: current server address is %s\n",
                                   ipaddr_ntoa(&sntp_server_address)));
    sntp_send_request(&sntp_server_address);
  } else {
    /* address conversion failed, try another server */
    LWIP_DEBUGF(SNTP_DEBUG_WARN_STATE, ("sntp_request: Invalid server address, trying next server.\n"));
    sys_untimeout(sntp_try_next_server, NULL);
    sys_timeout((u32_t)SNTP_RETRY_TIMEOUT, sntp_try_next_server, NULL);
  }
}

/**
 * @ingroup sntp
 * Initialize this module.
 * Send out request instantly or after SNTP_STARTUP_DELAY(_FUNC).
 */
void
sntp_init(void)
{
  /* LWIP_ASSERT_CORE_LOCKED(); is checked by udp_new() */
  LWIP_DEBUGF(SNTP_DEBUG_TRACE, ("sntp_init: SNTP initialised\n"));

#ifdef SNTP_SERVER_ADDRESS
#if SNTP_SERVER_DNS
  sntp_setservername(0, SNTP_SERVER_ADDRESS);
#else
#error SNTP_SERVER_ADDRESS string not supported SNTP_SERVER_DNS==0
#endif
#endif /* SNTP_SERVER_ADDRESS */

  if (sntp_pcb == NULL) {
    sntp_pcb = udp_new_ip_type(IPADDR_TYPE_ANY);
    LWIP_ASSERT("Failed to allocate udp pcb for sntp client", sntp_pcb != NULL);
    if (sntp_pcb != NULL) {
      udp_recv(sntp_pcb, sntp_recv, NULL);

      if (sntp_opmode == SNTP_OPMODE_POLL) {
        SNTP_RESET_RETRY_TIMEOUT();
#if SNTP_STARTUP_DELAY
        sys_timeout((u32_t)SNTP_STARTUP_DELAY_FUNC, sntp_request, NULL);
#else
        sntp_request(NULL);
#endif
      } else if (sntp_opmode == SNTP_OPMODE_LISTENONLY) {
        ip_set_option(sntp_pcb, SOF_BROADCAST);
        udp_bind(sntp_pcb, IP_ANY_TYPE, SNTP_PORT);
      }
    }
  }
}

/**
 * @ingroup sntp
 * Stop this module.
 */
void
sntp_stop(void)
{
  LWIP_ASSERT_CORE_LOCKED();
  if (sntp_pcb != NULL) {
#if SNTP_MONITOR_SERVER_REACHABILITY
    u8_t i;
    for (i = 0; i < SNTP_MAX_SERVERS; i++) {
      sntp_servers[i].reachability = 0;
    }
#endif /* SNTP_MONITOR_SERVER_REACHABILITY */
    sys_untimeout(sntp_request, NULL);
    sys_untimeout(sntp_try_next_server, NULL);
    udp_remove(sntp_pcb);
    sntp_pcb = NULL;
  }
}

/**
 * @ingroup sntp
 * Get enabled state.
 */
u8_t sntp_enabled(void)
{
  return (sntp_pcb != NULL) ? 1 : 0;
}

/**
 * @ingroup sntp
 * Sets the operating mode.
 * @param operating_mode one of the available operating modes
 */
void
sntp_setoperatingmode(u8_t operating_mode)
{
  LWIP_ASSERT_CORE_LOCKED();
  LWIP_ASSERT("Invalid operating mode", operating_mode <= SNTP_OPMODE_LISTENONLY);
  LWIP_ASSERT("Operating mode must not be set while SNTP client is running", sntp_pcb == NULL);
  sntp_opmode = operating_mode;
}

/**
 * @ingroup sntp
 * Gets the operating mode.
 */
u8_t
sntp_getoperatingmode(void)
{
  return sntp_opmode;
}

#if SNTP_MONITOR_SERVER_REACHABILITY
/**
 * @ingroup sntp
 * Gets the server reachability shift register as described in RFC 5905.
 *
 * @param idx the index of the NTP server
 */
u8_t
sntp_getreachability(u8_t idx)
{
  if (idx < SNTP_MAX_SERVERS) {
    return sntp_servers[idx].reachability;
  }
  return 0;
}
#endif /* SNTP_MONITOR_SERVER_REACHABILITY */

#if SNTP_GET_SERVERS_FROM_DHCP || SNTP_GET_SERVERS_FROM_DHCPV6
/**
 * Config SNTP server handling by IP address, name, or DHCP; clear table
 * @param set_servers_from_dhcp enable or disable getting server addresses from dhcp
 */
void
sntp_servermode_dhcp(int set_servers_from_dhcp)
{
  u8_t new_mode = set_servers_from_dhcp ? 1 : 0;
  LWIP_ASSERT_CORE_LOCKED();
  if (sntp_set_servers_from_dhcp != new_mode) {
    sntp_set_servers_from_dhcp = new_mode;
  }
}
#endif /* SNTP_GET_SERVERS_FROM_DHCP || SNTP_GET_SERVERS_FROM_DHCPV6 */

/**
 * @ingroup sntp
 * Initialize one of the NTP servers by IP address
 *
 * @param idx the index of the NTP server to set must be < SNTP_MAX_SERVERS
 * @param server IP address of the NTP server to set
 */
void
sntp_setserver(u8_t idx, const ip_addr_t *server)
{
  LWIP_ASSERT_CORE_LOCKED();
  if (idx < SNTP_MAX_SERVERS) {
    if (server != NULL) {
      sntp_servers[idx].addr = (*server);
#if SNTP_SUPPORT_MULTIPLE_SERVERS
      sntp_servers[idx].kod_received = 0;
#endif
    } else {
      ip_addr_set_zero(&sntp_servers[idx].addr);
    }
#if SNTP_SERVER_DNS
    sntp_servers[idx].name = NULL;
#endif
  }
}

#if LWIP_DHCP && SNTP_GET_SERVERS_FROM_DHCP
/**
 * Initialize one of the NTP servers by IP address, required by DHCP
 *
 * @param num the index of the NTP server to set must be < SNTP_MAX_SERVERS
 * @param server IP address of the NTP server to set
 */
void
dhcp_set_ntp_servers(u8_t num, const ip4_addr_t *server)
{
  LWIP_DEBUGF(SNTP_DEBUG_TRACE, ("sntp: %s %u.%u.%u.%u as NTP server #%u via DHCP\n",
                                 (sntp_set_servers_from_dhcp ? "Got" : "Rejected"),
                                 ip4_addr1(server), ip4_addr2(server), ip4_addr3(server), ip4_addr4(server), num));
  if (sntp_set_servers_from_dhcp && num) {
    u8_t i;
    for (i = 0; (i < num) && (i < SNTP_MAX_SERVERS); i++) {
      ip_addr_t addr;
      ip_addr_copy_from_ip4(addr, server[i]);
      sntp_setserver(i, &addr);
    }
    for (i = num; i < SNTP_MAX_SERVERS; i++) {
      sntp_setserver(i, NULL);
    }
  }
}
#endif /* LWIP_DHCP && SNTP_GET_SERVERS_FROM_DHCP */

#if LWIP_IPV6_DHCP6 && SNTP_GET_SERVERS_FROM_DHCPV6
/**
 * Initialize one of the NTP servers by IP address, required by DHCPV6
 *
 * @param num the number of NTP server addresses to set must be < SNTP_MAX_SERVERS
 * @param server array of IP address of the NTP servers to set
 */
void
dhcp6_set_ntp_servers(u8_t num_ntp_servers, ip_addr_t* ntp_server_addrs)
{
  LWIP_DEBUGF(SNTP_DEBUG_TRACE, ("sntp: %s %u NTP server(s) via DHCPv6\n",
                                 (sntp_set_servers_from_dhcp ? "Got" : "Rejected"),
                                 num_ntp_servers));
  if (sntp_set_servers_from_dhcp && num_ntp_servers) {
    u8_t i;
    for (i = 0; (i < num_ntp_servers) && (i < SNTP_MAX_SERVERS); i++) {
      LWIP_DEBUGF(SNTP_DEBUG_TRACE, ("sntp: NTP server %u: %s\n",
                                     i, ipaddr_ntoa(&ntp_server_addrs[i])));
      sntp_setserver(i, &ntp_server_addrs[i]);
    }
    for (i = num_ntp_servers; i < SNTP_MAX_SERVERS; i++) {
      sntp_setserver(i, NULL);
    }
  }
}
#endif /* LWIP_DHCPv6 && SNTP_GET_SERVERS_FROM_DHCPV6 */

/**
 * @ingroup sntp
 * Obtain one of the currently configured by IP address (or DHCP) NTP servers
 *
 * @param idx the index of the NTP server
 * @return IP address of the indexed NTP server or "ip_addr_any" if the NTP
 *         server has not been configured by address (or at all).
 */
const ip_addr_t *
sntp_getserver(u8_t idx)
{
  if (idx < SNTP_MAX_SERVERS) {
    return &sntp_servers[idx].addr;
  }
  return IP_ADDR_ANY;
}

/**
 * @ingroup sntp
 * Check if a Kiss-of-Death has been received from this server (only valid for
 * SNTP_MAX_SERVERS > 1).
 *
 * @param idx the index of the NTP server
 * @return 1 if a KoD has been received, 0 if not.
 */
u8_t
sntp_getkodreceived(u8_t idx)
{
#if SNTP_SUPPORT_MULTIPLE_SERVERS
  if (idx < SNTP_MAX_SERVERS) {
    return sntp_servers[idx].kod_received;
  }
#else
  LWIP_UNUSED_ARG(idx);
#endif
  return 0;
}

#if SNTP_SERVER_DNS
/**
 * Initialize one of the NTP servers by name
 *
 * @param idx the index of the NTP server to set must be < SNTP_MAX_SERVERS
 * @param server DNS name of the NTP server to set, to be resolved at contact time
 */
void
sntp_setservername(u8_t idx, const char *server)
{
  LWIP_ASSERT_CORE_LOCKED();
  if (idx < SNTP_MAX_SERVERS) {
    sntp_servers[idx].name = server;
#if SNTP_SUPPORT_MULTIPLE_SERVERS
    sntp_servers[idx].kod_received = 0;
#endif
  }
}

/**
 * Obtain one of the currently configured by name NTP servers.
 *
 * @param idx the index of the NTP server
 * @return IP address of the indexed NTP server or NULL if the NTP
 *         server has not been configured by name (or at all)
 */
const char *
sntp_getservername(u8_t idx)
{
  if (idx < SNTP_MAX_SERVERS) {
    return sntp_servers[idx].name;
  }
  return NULL;
}
#endif /* SNTP_SERVER_DNS */

#endif /* LWIP_UDP */

#define TAG SDK_MANAGED_TAG
#define calloc host_calloc
/*
 * SPDX-FileCopyrightText: 2022-2025 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */

// Remove compat macro and include lwip API
#undef SNTP_OPMODE_POLL
#define SNTP_OPMODE_POLL 0

static const char *TAG = "esp_netif_sntp";

ESP_EVENT_DEFINE_BASE(NETIF_SNTP_EVENT);

typedef struct sntp_storage {
    esp_sntp_time_cb_t sync_cb;
    SemaphoreHandle_t sync_sem;
    ip_event_t ip_event_to_renew;
    size_t index_of_first_server;
    size_t num_of_servers;
    char* servers[];
} sntp_storage_t;

static sntp_storage_t *s_storage = NULL;

static void sync_time_cb(struct timeval *tv)
{
    if (s_storage && s_storage->sync_sem) {
        xSemaphoreGive(s_storage->sync_sem);
    }
    if (s_storage && s_storage->sync_cb) {
        s_storage->sync_cb(tv);
    }
    // Post event with the timeval payload
    esp_netif_sntp_time_sync_t evt = {0};
    if (tv) {
        evt.tv = *tv;
    }
    if (esp_event_post(NETIF_SNTP_EVENT, NETIF_SNTP_TIME_SYNC, &evt, sizeof(evt), 0) != ESP_OK) {
        ESP_LOGE(TAG, "Error posting SNTP time sync");
    }
}

static esp_err_t sntp_init_api(void *ctx)
{
    esp_err_t ret = ESP_OK;

    esp_sntp_config_t * config = ctx;
    ESP_GOTO_ON_FALSE(config->num_of_servers <= SNTP_MAX_SERVERS, ESP_ERR_INVALID_ARG, err, TAG, "Tried to configure more servers than enabled in lwip. Please update CONFIG_SNTP_MAX_SERVERS");

    sntp_set_time_sync_notification_cb(sync_time_cb);
    sntp_setoperatingmode(SNTP_OPMODE_POLL);

    for (int i = 0; i < config->num_of_servers; ++i) {
        sntp_setservername(i, config->servers[i]);
    }

    if (config->server_from_dhcp) {
#if LWIP_DHCP_GET_NTP_SRV
        sntp_servermode_dhcp(1);
#else
        ESP_GOTO_ON_FALSE(false, ESP_ERR_INVALID_ARG, err, TAG, "Tried to configure SNTP server from DHCP, while disabled. Please enable CONFIG_LWIP_DHCP_GET_NTP_SRV");
#endif
    }

    if (config->smooth_sync) {
        sntp_set_sync_mode(SNTP_SYNC_MODE_SMOOTH);
    }

    if (config->start) {
        sntp_init();
    }
err:
    return ret;
}

static esp_err_t renew_servers_api(void *ctx)
{
    if (s_storage && s_storage->num_of_servers) {
        for (int i = 0; i < s_storage->num_of_servers; ++i) {
            sntp_setservername(i + s_storage->index_of_first_server, s_storage->servers[i]);
        }
    }
    return ESP_OK;
}

void esp_netif_sntp_renew_servers(void *handler_args, esp_event_base_t base, int32_t event_id, void *event_data)
{
    esp_netif_tcpip_exec(renew_servers_api, NULL);
}

esp_err_t esp_netif_sntp_init(const esp_sntp_config_t * config)
{
    esp_err_t ret = ESP_OK;
    ESP_RETURN_ON_FALSE(s_storage == NULL, ESP_ERR_INVALID_STATE, TAG, "esp_netif_sntp already initialized");
    s_storage = calloc(1, sizeof(sntp_storage_t) + // allocate space for servers only if we are supposed to refresh the settings
                          (config->renew_servers_after_new_IP ? config->num_of_servers * sizeof(char*) : 0));
    ESP_GOTO_ON_FALSE(s_storage != NULL, ESP_ERR_NO_MEM, err, TAG, "Failed to allocate SNTP storage");
    if (config->wait_for_sync) {
        s_storage->sync_sem = xSemaphoreCreateBinary();
        ESP_GOTO_ON_FALSE(s_storage->sync_sem != NULL, ESP_ERR_NO_MEM, err, TAG, "Failed to SNTP sync semaphore");
    }
    if (config->renew_servers_after_new_IP && config->num_of_servers > 0) {
        s_storage->num_of_servers = config->num_of_servers;
        s_storage->index_of_first_server = config->index_of_first_server;
        // store the server names, as we'd have to refresh the config after IP event
        for (int i = 0; i < config->num_of_servers; ++i) {
            s_storage->servers[i] = strdup(config->servers[i]);
        }

        ESP_GOTO_ON_ERROR(esp_event_handler_register(IP_EVENT, config->ip_event_to_renew, esp_netif_sntp_renew_servers, NULL),
                          err, TAG, "Failed to register IP event");
        s_storage->ip_event_to_renew = config->ip_event_to_renew;

    }
    if (config->sync_cb) {
        s_storage->sync_cb = config->sync_cb;
    }

    ESP_GOTO_ON_ERROR(esp_netif_tcpip_exec(sntp_init_api, (void*)config), err, TAG, "Failed initialize SNTP service");

    return ret;

err:
    esp_netif_sntp_deinit();
    return ret;
}

static esp_err_t sntp_stop_api(void *ctx)
{
    sntp_stop();
    return ESP_OK;
}

void esp_netif_sntp_deinit(void)
{
    if (s_storage) {
        sntp_storage_t *storage = s_storage;
        s_storage = NULL;
        sntp_set_time_sync_notification_cb(NULL);
        esp_netif_tcpip_exec(sntp_stop_api, NULL);
        if (storage->num_of_servers) {
            for (int i = 0; i < storage->num_of_servers; ++i) {
                free(storage->servers[i]);
            }
            esp_event_handler_unregister(IP_EVENT, storage->ip_event_to_renew, esp_netif_sntp_renew_servers);
        }
        if (storage->sync_sem) {
            vSemaphoreDelete(storage->sync_sem);
        }
        free(storage);

    }
}

esp_err_t esp_netif_sntp_sync_wait(TickType_t tout)
{
    if (s_storage == NULL || s_storage->sync_sem == NULL) {
        return ESP_ERR_INVALID_STATE;
    }
    if (xQueueSemaphoreTake(s_storage->sync_sem, tout) != pdTRUE) {
        return ESP_ERR_TIMEOUT;
    }
    if (sntp_get_sync_mode() == SNTP_SYNC_MODE_SMOOTH &&
        sntp_get_sync_status() == SNTP_SYNC_STATUS_IN_PROGRESS) {
        return ESP_ERR_NOT_FINISHED;
    }
    return ESP_OK;
}

static esp_err_t sntp_start_api(void* ctx)
{
    sntp_stop();
    sntp_init();
    return ESP_OK;
}

esp_err_t esp_netif_sntp_start(void)
{
    return esp_netif_tcpip_exec(sntp_start_api, NULL);
}

esp_err_t esp_netif_sntp_reachability(unsigned int index, unsigned int *reachability)
{
    if (index >= SNTP_MAX_SERVERS || reachability == NULL) {
        return ESP_ERR_INVALID_ARG;
    }
    if (s_storage == NULL || sntp_enabled() == 0) {
        return ESP_ERR_INVALID_STATE;
    }
    *reachability = sntp_getreachability(index);
    return ESP_OK;
}

#undef calloc
#undef TAG
