/* Exercise the public city route, including an update arriving during body I/O. */
static tv_settings_t concurrent_city_settings;
static uint32_t concurrent_city_configuration,concurrent_city_selection;

static void change_settings_during_city_request(void)
{
    /* Model another producer changing the theme/brightness after HTTP's snapshot. */
    tv_settings_t s;
    settings_snapshot(&s);
    CHECK(settings_select_theme((s.theme+1)%4)==ESP_OK);
    settings_snapshot(&s);
    s.day_level=s.day_level==500?400:500;
    CHECK(settings_replace(&s)==ESP_OK);
    settings_snapshot_with_revisions(&concurrent_city_settings,&concurrent_city_configuration,
                                      &concurrent_city_selection);
}

static void test_city_theme_requests(void)
{
    /* FIXED_RECONSTRUCTION: factory 0x4200f3cc clears the latch for every city command.
     * Repeated commands must repaint all themes without wearing flash unnecessarily. */
    tv_settings_t original,s,actual,expected;
    uint32_t configuration,selection,next_configuration,next_selection;
    settings_snapshot(&original);
    for(unsigned theme=0;theme<4;++theme) {
        s=original;s.theme=theme;strcpy(s.city,"London");strcpy(s.country,"GB");
        CHECK(settings_replace(&s)==ESP_OK && settings_flush()==ESP_OK);
        settings_snapshot_with_revisions(&s,&configuration,&selection);
        unsigned committed=nvs_commits,weather_before=weather_requests;
        for(unsigned repeat=0;repeat<3;++repeat) {
            post("/updateCity","{\"city\":\"London,gb\"}",200);
            settings_snapshot_with_revisions(&actual,&next_configuration,&next_selection);
            CHECK(!memcmp(&actual,&s,sizeof(s)));
            CHECK(next_configuration==configuration && next_selection==selection+repeat+1);
            CHECK(weather_requests==weather_before+repeat+1);
            CHECK(settings_flush()==ESP_OK && nvs_commits==committed);
        }
        selection=next_selection;weather_before=weather_requests;
        expected=s;strcpy(expected.city,"Budapest");strcpy(expected.country,"HU");
        post("/updateCity","{\"city\":\"Budapest,HU\"}",200);
        settings_snapshot_with_revisions(&actual,&next_configuration,&next_selection);
        CHECK(!memcmp(&actual,&expected,sizeof(actual)));
        CHECK(next_configuration==configuration+1 && next_selection==selection+1);
        CHECK(weather_requests==weather_before+1);
        CHECK(settings_flush()==ESP_OK && nvs_commits==committed+1);

        settings_snapshot_with_revisions(&s,&configuration,&selection);
        weather_before=weather_requests;committed=nvs_commits;
        const char *invalid[]={"{\"city\":\"London\"}","{\"city\":\",GB\"}",
                               "{\"city\":\"London,G/B\"}","{\"city\":null}"};
        for(unsigned i=0;i<sizeof(invalid)/sizeof(invalid[0]);++i) {
            post("/updateCity",invalid[i],400);
            settings_snapshot_with_revisions(&actual,&next_configuration,&next_selection);
            CHECK(!memcmp(&actual,&s,sizeof(s)));
            CHECK(next_configuration==configuration && next_selection==selection);
            CHECK(weather_requests==weather_before);
            CHECK(settings_flush()==ESP_OK && nvs_commits==committed);
        }

        /* The city route owns only city/country; it must not roll back a newer theme. */
        before_body_read=change_settings_during_city_request;
        post("/updateCity","{\"city\":\"Szeged,HU\"}",200);
        CHECK(before_body_read==NULL);
        expected=concurrent_city_settings;strcpy(expected.city,"Szeged");
        strcpy(expected.country,"HU");
        settings_snapshot_with_revisions(&actual,&next_configuration,&next_selection);
        CHECK(!memcmp(&actual,&expected,sizeof(actual)));
        CHECK(next_configuration==concurrent_city_configuration+1 &&
              next_selection==concurrent_city_selection+1);
    }
    /* Public API validation must not publish a reset for rejected locations. */
    settings_snapshot_with_revisions(&s,&configuration,&selection);
    CHECK(settings_flush()==ESP_OK);
    unsigned committed=nvs_commits;
    char overlong[66];memset(overlong,'x',sizeof(overlong)-1);overlong[65]=0;
    CHECK(settings_update_city(NULL,"GB")==ESP_ERR_INVALID_ARG);
    CHECK(settings_update_city("","GB")==ESP_ERR_INVALID_ARG);
    CHECK(settings_update_city(overlong,"GB")==ESP_ERR_INVALID_ARG);
    CHECK(settings_update_city("London",NULL)==ESP_ERR_INVALID_ARG);
    CHECK(settings_update_city("London","G/B")==ESP_ERR_INVALID_ARG);
    settings_snapshot_with_revisions(&actual,&next_configuration,&next_selection);
    CHECK(!memcmp(&actual,&s,sizeof(s)));
    CHECK(next_configuration==configuration && next_selection==selection);
    CHECK(settings_flush()==ESP_OK && nvs_commits==committed);
    CHECK(settings_replace(&original)==ESP_OK && settings_flush()==ESP_OK);
}
