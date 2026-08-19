#ifndef displaySSD1306_72x40conf_h
#define displaySSD1306_72x40conf_h

#define DSP_WIDTH       72
#define TFT_FRAMEWDT    0
#define MAX_WIDTH       DSP_WIDTH

#define HIDE_RSSI
#define HIDE_WEATHER
#define HIDE_HEAPBAR
#define HIDE_VOL
#define HIDE_VU
#define HIDE_TITLE2
#define HIDE_CLOCK
#define HIDE_BITRATE

// Profile-specific font selectors interpreted by the text widgets.
#define C3_TITLE_FONT_SIZE 3
#define C3_IP_FONT_SIZE    4

#define bootLogoTop     0

const ScrollConfig metaConf       PROGMEM = {{ 0, 0, C3_TITLE_FONT_SIZE, WA_LEFT }, 96, false, 72, 3500, 1, 35 };
const ScrollConfig title1Conf     PROGMEM = {{ 0, 14, C3_TITLE_FONT_SIZE, WA_LEFT }, 140, false, 72, 3500, 1, 35 };
const ScrollConfig playlistConf   PROGMEM = {{ 0, 16, 1, WA_LEFT }, 96, true, 72, 500, 1, 35 };
const ScrollConfig apTitleConf    PROGMEM = {{ 0, 0, 1, WA_CENTER }, 64, false, 72, 0, 1, 35 };
const ScrollConfig apSettConf     PROGMEM = {{ 0, 32, 1, WA_LEFT }, 96, false, 72, 0, 1, 35 };
const ScrollConfig weatherConf    PROGMEM = {{ 0, 24, 1, WA_LEFT }, 96, true, 72, 0, 1, 35 };

const FillConfig metaBGConf       PROGMEM = {{ 0, 0, 0, WA_LEFT }, 72, 12, false };
const FillConfig metaBGConfInv    PROGMEM = {{ 0, 8, 0, WA_LEFT }, 72, 1, false };
const FillConfig volbarConf       PROGMEM = {{ 0, 37, 0, WA_LEFT }, 72, 3, true };
const FillConfig playlBGConf      PROGMEM = {{ 0, 15, 0, WA_LEFT }, 72, 10, false };

const WidgetConfig bootstrConf    PROGMEM = { 0, 31, 1, WA_CENTER };
const WidgetConfig bitrateConf    PROGMEM = { 0, 10, 1, WA_RIGHT };
const WidgetConfig voltxtConf     PROGMEM = { 0, 24, 1, WA_RIGHT };
const WidgetConfig iptxtConf      PROGMEM = { 0, 32, C3_IP_FONT_SIZE, WA_CENTER };
const WidgetConfig rssiConf       PROGMEM = { 0, 32, 1, WA_RIGHT };
const WidgetConfig numConf        PROGMEM = { 0, 19, 1, WA_CENTER };
const WidgetConfig apNameConf     PROGMEM = { 0, 8, 1, WA_LEFT };
const WidgetConfig apName2Conf    PROGMEM = { 0, 16, 1, WA_LEFT };
const WidgetConfig apPassConf     PROGMEM = { 0, 24, 1, WA_LEFT };
const WidgetConfig apPass2Conf    PROGMEM = { 0, 32, 1, WA_LEFT };
const WidgetConfig clockConf      PROGMEM = { 0, 27, 1, WA_CENTER };
const WidgetConfig vuConf         PROGMEM = { 0, 24, 1, WA_LEFT };

const WidgetConfig bootWdtConf    PROGMEM = { 0, 20, 1, WA_CENTER };
const ProgressConfig bootPrgConf  PROGMEM = { 90, 10, 2 };

const VUBandsConfig bandsConf     PROGMEM = { 6, 24, 1, 1, 4, 2 };

const char numtxtFmt[]            PROGMEM = "%d";
const char rssiFmt[]              PROGMEM = "%d";
const char iptxtFmt[]             PROGMEM = "%s";
const char voltxtFmt[]            PROGMEM = "%d";
const char bitrateFmt[]           PROGMEM = "%d";

const MoveConfig clockMove        PROGMEM = { 0, 0, -1 };
const MoveConfig weatherMove      PROGMEM = { 0, 0, -1 };
const MoveConfig weatherMoveVU    PROGMEM = { 0, 0, -1 };

#endif
