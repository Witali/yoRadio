"""Exercise heap metadata selection/bounds under ASan/UBSan (host cc required)."""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='heap-layout-') as directory:
    tmp = Path(directory)
    (tmp/'test.c').write_text(r'''
#include <assert.h>
#include <stdio.h>
#include "heap_layout_capture.h"
int main(void) {
    heap_layout_capture_t s = {0};
    // Adjacent tiny allocations are useful evidence even below the threshold.
    heap_layout_record(&s, 0x1000, 0x1100, 32, true);
    heap_layout_record(&s, 0x1000, 0x1124, 512, false);
    heap_layout_record(&s, 0x1000, 0x1328, 16, true);
    assert(s.count == 3 && s.rows[0].address == 0x1100 && s.rows[2].address == 0x1328);
    heap_layout_record(&s, 0x1000, 0x133c, 1024, false);
    assert(s.count == 4); // The previous neighbor must not be duplicated.
    heap_layout_record(&s, 0x1000, 0x1740, 32, true);
    heap_layout_record(&s, 0x1000, 0x1764, 64, true);
    assert(s.count == 5); // Unselected small blocks still enter byte totals.
    heap_layout_record(&s, 0x2000, 0x2100, 256, false);
    assert(s.count == 6 && s.rows[5].address == 0x2100); // No cross-heap neighbor.
    heap_layout_record(&s, 0x2000, 0x2204, 512, true);
    heap_layout_record(&s, 0x2000, 0x2408, 12288, true);
    assert(s.count == 8 && s.blocks == 9 && s.dropped == 0);
    assert(s.free_bytes == 512+1024+256 && s.used_bytes == 32+16+32+64+512+12288);
    assert(s.rows[7].size_used == (UINT32_C(0x80000000) | 12288));
    // Saturation is explicit; collection continues without overwriting rows.
    heap_layout_capture_t full = {0};
    for (size_t i = 0; i < HEAP_LAYOUT_ROWS+11; ++i)
        heap_layout_record(&full, 0x1000, 0x1100+i*2048, 1024, true);
    assert(full.count == HEAP_LAYOUT_ROWS && full.dropped == 11);
    assert(full.blocks == HEAP_LAYOUT_ROWS+11 && full.used_bytes == (HEAP_LAYOUT_ROWS+11)*1024);
    assert(full.rows[HEAP_LAYOUT_ROWS-1].address == 0x1100+(HEAP_LAYOUT_ROWS-1)*2048);
    puts("HEAP_LAYOUT_PASS neighbors, heap boundaries, de-duplication, totals and truncation");
}
''')
    exe = tmp/'heap-layout'
    subprocess.run(['cc', '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                    '-I'+str(ROOT/'idf/esp32c3-oled-native/main'),
                    str(tmp/'test.c'), '-o', str(exe)], check=True)
    subprocess.run([str(exe)], check=True)
