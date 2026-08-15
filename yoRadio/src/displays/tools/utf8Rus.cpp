#include "Arduino.h"
#include "../../core/options.h"
#include "../dspcore.h"
#include "utf8Rus.h"

namespace {

constexpr uint32_t REPLACEMENT_CHARACTER = 0xFFFD;

bool isContinuation(uint8_t value) {
  return (value & 0xC0) == 0x80;
}

uint32_t nextCodePoint(const char* text, size_t& offset) {
  const uint8_t first = (uint8_t)text[offset++];
  if (first < 0x80) return first;

  const uint8_t second = (uint8_t)text[offset];
  if (first >= 0xC2 && first <= 0xDF && second && isContinuation(second)) {
    offset++;
    return ((uint32_t)(first & 0x1F) << 6) | (second & 0x3F);
  }

  const uint8_t third = second ? (uint8_t)text[offset + 1] : 0;
  if (first >= 0xE0 && first <= 0xEF && second && third &&
      isContinuation(second) && isContinuation(third) &&
      !(first == 0xE0 && second < 0xA0) &&
      !(first == 0xED && second >= 0xA0)) {
    offset += 2;
    return ((uint32_t)(first & 0x0F) << 12) |
           ((uint32_t)(second & 0x3F) << 6) | (third & 0x3F);
  }

  const uint8_t fourth = third ? (uint8_t)text[offset + 2] : 0;
  if (first >= 0xF0 && first <= 0xF4 && second && third && fourth &&
      isContinuation(second) && isContinuation(third) && isContinuation(fourth) &&
      !(first == 0xF0 && second < 0x90) &&
      !(first == 0xF4 && second >= 0x90)) {
    offset += 3;
    return ((uint32_t)(first & 0x07) << 18) |
           ((uint32_t)(second & 0x3F) << 12) |
           ((uint32_t)(third & 0x3F) << 6) | (fourth & 0x3F);
  }

  return REPLACEMENT_CHARACTER;
}

const char* normalizedText(uint32_t codePoint) {
  switch (codePoint) {
    // Spaces, zero-width characters and a soft hyphen.
    case 0x00A0:
    case 0x1680:
    case 0x2000: case 0x2001: case 0x2002: case 0x2003: case 0x2004:
    case 0x2005: case 0x2006: case 0x2007: case 0x2008: case 0x2009:
    case 0x200A: case 0x202F: case 0x205F: case 0x3000:
      return " ";
    case 0x00AD:
    case 0x200B: case 0x200C: case 0x200D:
    case 0x2060:
    case 0xFEFF:
      return "";

    // Quotation marks, apostrophes and primes.
    case 0x00AB: case 0x00BB:
    case 0x201C: case 0x201D: case 0x201E: case 0x201F:
    case 0x2033: case 0x2036:
      return "\"";
    case 0x2018: case 0x2019: case 0x201A: case 0x201B:
    case 0x2032: case 0x2035:
      return "'";

    // Dashes, punctuation and common typographic marks.
    case 0x2010: case 0x2011: case 0x2012:
    case 0x2013: case 0x2014: case 0x2015:
    case 0x2212:
      return "-";
    case 0x2022: case 0x2023: case 0x2043: case 0x2219:
      return "*";
    case 0x2026:
      return "...";
    case 0x2044: case 0x2215:
      return "/";
    case 0x00B1:
      return "+/-";
    case 0x00D7:
      return "x";
    case 0x00F7:
      return "/";
    case 0x2116:
      return "No";
    case 0x2122:
      return "TM";
    case 0x2260:
      return "!=";
    case 0x2264:
      return "<=";
    case 0x2265:
      return ">=";
    case 0x2190: return "<";
    case 0x2191: return "^";
    case 0x2192: return ">";
    case 0x2193: return "v";
    case 0x266A: case 0x266B:
      return "\x0E"; // Existing note glyph in the yoRadio 5x7 font.

    // Copyright, registration and currencies.
    case 0x00A9: return "(C)";
    case 0x00AE: return "(R)";
    case 0x00A3: return "GBP";
    case 0x00A5: return "Y";
    case 0x20AC: return "EUR";
    case 0x20BD: return "RUB";

    // Latin-1 and Latin Extended-A letters folded to the 5x7 ASCII set.
    case 0x00C0: case 0x00C1: case 0x00C2: case 0x00C3: case 0x00C4:
    case 0x00C5: case 0x0100: case 0x0102: case 0x0104: return "A";
    case 0x00E0: case 0x00E1: case 0x00E2: case 0x00E3: case 0x00E4:
    case 0x00E5: case 0x0101: case 0x0103: case 0x0105: return "a";
    case 0x00C6: return "AE";
    case 0x00E6: return "ae";
    case 0x00C7: case 0x0106: case 0x0108: case 0x010A: case 0x010C: return "C";
    case 0x00E7: case 0x0107: case 0x0109: case 0x010B: case 0x010D: return "c";
    case 0x00D0: case 0x010E: case 0x0110: return "D";
    case 0x00F0: case 0x010F: case 0x0111: return "d";
    case 0x00C8: case 0x00C9: case 0x00CA: case 0x00CB: case 0x0112:
    case 0x0114: case 0x0116: case 0x0118: case 0x011A: return "E";
    case 0x00E8: case 0x00E9: case 0x00EA: case 0x00EB: case 0x0113:
    case 0x0115: case 0x0117: case 0x0119: case 0x011B: return "e";
    case 0x011C: case 0x011E: case 0x0120: case 0x0122: return "G";
    case 0x011D: case 0x011F: case 0x0121: case 0x0123: return "g";
    case 0x0124: case 0x0126: return "H";
    case 0x0125: case 0x0127: return "h";
    case 0x00CC: case 0x00CD: case 0x00CE: case 0x00CF: case 0x0128:
    case 0x012A: case 0x012C: case 0x012E: case 0x0130: return "I";
    case 0x00EC: case 0x00ED: case 0x00EE: case 0x00EF: case 0x0129:
    case 0x012B: case 0x012D: case 0x012F: case 0x0131: return "i";
    case 0x0134: return "J";
    case 0x0135: return "j";
    case 0x0136: return "K";
    case 0x0137: case 0x0138: return "k";
    case 0x0139: case 0x013B: case 0x013D: case 0x013F: case 0x0141: return "L";
    case 0x013A: case 0x013C: case 0x013E: case 0x0140: case 0x0142: return "l";
    case 0x00D1: case 0x0143: case 0x0145: case 0x0147: return "N";
    case 0x00F1: case 0x0144: case 0x0146: case 0x0148: case 0x0149: return "n";
    case 0x00D2: case 0x00D3: case 0x00D4: case 0x00D5: case 0x00D6:
    case 0x00D8: case 0x014C: case 0x014E: case 0x0150: return "O";
    case 0x00F2: case 0x00F3: case 0x00F4: case 0x00F5: case 0x00F6:
    case 0x00F8: case 0x014D: case 0x014F: case 0x0151: return "o";
    case 0x0152: return "OE";
    case 0x0153: return "oe";
    case 0x0154: case 0x0156: case 0x0158: return "R";
    case 0x0155: case 0x0157: case 0x0159: return "r";
    case 0x015A: case 0x015C: case 0x015E: case 0x0160: return "S";
    case 0x015B: case 0x015D: case 0x015F: case 0x0161: return "s";
    case 0x00DF: return "ss";
    case 0x0162: case 0x0164: case 0x0166: return "T";
    case 0x0163: case 0x0165: case 0x0167: return "t";
    case 0x00D9: case 0x00DA: case 0x00DB: case 0x00DC: case 0x0168:
    case 0x016A: case 0x016C: case 0x016E: case 0x0170: case 0x0172: return "U";
    case 0x00F9: case 0x00FA: case 0x00FB: case 0x00FC: case 0x0169:
    case 0x016B: case 0x016D: case 0x016F: case 0x0171: case 0x0173: return "u";
    case 0x0174: return "W";
    case 0x0175: return "w";
    case 0x00DD: case 0x0176: case 0x0178: return "Y";
    case 0x00FD: case 0x00FF: case 0x0177: return "y";
    case 0x0179: case 0x017B: case 0x017D: return "Z";
    case 0x017A: case 0x017C: case 0x017E: return "z";
    case 0x00DE: return "TH";
    case 0x00FE: return "th";

    // Common Ukrainian and Belarusian Cyrillic letters outside Russian.
    case 0x0404: return "E";  case 0x0454: return "e";
    case 0x0406: return "I";  case 0x0456: return "i";
    case 0x0407: return "I";  case 0x0457: return "i";
    case 0x040E: return "U";  case 0x045E: return "u";
    case 0x0490: return "G";  case 0x0491: return "g";
  }

  // Combining diacritical marks are omitted, preserving their base letter.
  if (codePoint >= 0x0300 && codePoint <= 0x036F) return "";
  return nullptr;
}

} // namespace

size_t strlen_utf8(const char* text) {
  size_t count = 0;
  size_t offset = 0;
  while (text[offset]) {
    nextCodePoint(text, offset);
    count++;
  }
  return count;
}

char* utf8Rus(const char* text, bool uppercase) {
  static char out[BUFLEN];
  int outPos = 0;

#if defined(DSP_LCD) && !defined(LCD_RUS)
  static const char* russianTransliteration[] = {
    "A","B","V","G","D","E","ZH","Z","I","Y",
    "K","L","M","N","O","P","R","S","T","U",
    "F","H","TS","CH","SH","SHCH","'","YU","'","E","YU","YA"
  };
#endif
#if defined(DSP_LCD) && defined(LCD_RUS)
  static const unsigned char russianLcd[] PROGMEM = {
    0x41,0xa0,0x42,0xa1,0xe0,0x45,0xa3,0xa4,0xa5,0xa6,0x4b,0xa7,0x4d,0x48,0x4f,
    0xa8,0x50,0x43,0x54,0xa9,0xaa,0x58,0xe1,0xab,0xac,0xe2,0xad,0xae,0x62,0xaf,0xb0,0xb1
  };
#endif

  auto appendAscii = [&](char value) {
    if (outPos >= BUFLEN - 1) return;
#if defined(DSP_LCD) && !defined(LCD_RUS)
    char displayValue = (char)toupper((unsigned char)value);
    if (displayValue == 7) displayValue = (char)165;
    if (displayValue == 9) displayValue = (char)223;
    out[outPos++] = displayValue;
#else
    out[outPos++] = uppercase ? (char)toupper((unsigned char)value) : value;
#endif
  };

  auto appendText = [&](const char* value) {
    while (*value && outPos < BUFLEN - 1) appendAscii(*value++);
  };

  size_t offset = 0;
  while (text[offset] && outPos < BUFLEN - 1) {
    const uint32_t codePoint = nextCodePoint(text, offset);
    if (codePoint < 0x80) {
      appendAscii((char)codePoint);
      continue;
    }

    if (codePoint == 0x0401 || codePoint == 0x0451) {
#if defined(DSP_LCD) && !defined(LCD_RUS)
      appendText("YO");
#else
      out[outPos++] = uppercase || codePoint == 0x0401 ? (char)0xA8 : (char)0xB8;
#endif
      continue;
    }

    if (codePoint >= 0x0410 && codePoint <= 0x044F) {
      const uint8_t russianIndex = (uint8_t)((codePoint - 0x0410) & 0x1F);
#if defined(DSP_LCD) && !defined(LCD_RUS)
      appendText(russianTransliteration[russianIndex]);
#elif defined(DSP_LCD) && defined(LCD_RUS)
      out[outPos++] = russianLcd[russianIndex];
#else
      uint8_t displayValue = (uint8_t)(0xC0 + (codePoint - 0x0410));
      if (uppercase && displayValue >= 0xE0) displayValue -= 0x20;
      out[outPos++] = (char)displayValue;
#endif
      continue;
    }

    if (codePoint == 0x00B0) {
#if defined(DSP_LCD)
      out[outPos++] = (char)223;
#else
      out[outPos++] = (char)9;
#endif
      continue;
    }

    const char* replacement = normalizedText(codePoint);
    if (replacement) appendText(replacement);
    else appendAscii('?');
  }

  out[outPos] = 0;
  return out;
}
