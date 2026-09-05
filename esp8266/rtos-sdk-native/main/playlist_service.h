#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "esp_err.h"

#define PLAYLIST_PATH "/spiffs/data/playlist.csv"
#define PLAYLIST_INDEX_PATH "/spiffs/data/playlist.idx"

typedef struct {
    char name[144];
    char url[512];
    int8_t output_gain_db;
} playlist_station_t;

typedef esp_err_t (*playlist_station_visitor_t)(uint16_t one_based_index,
                                                const char *name,
                                                const char *url,
                                                int8_t output_gain_db,
                                                void *context);

esp_err_t playlist_service_init(void);
esp_err_t playlist_service_rebuild(void);
bool playlist_service_validate(const char *path);
esp_err_t playlist_service_install(const char *temporary);
bool playlist_service_entry_supported(char *line);
uint16_t playlist_service_count(void);
bool playlist_service_get(uint16_t one_based_index, playlist_station_t *station);
esp_err_t playlist_service_visit(uint16_t one_based_index,
                                 playlist_station_visitor_t visitor,
                                 void *context);
bool playlist_service_find_http_index(uint16_t start, int direction,
                                      uint16_t *found_index);
bool playlist_service_find_http(uint16_t start, int direction,
                                uint16_t *found_index,
                                playlist_station_t *station);
