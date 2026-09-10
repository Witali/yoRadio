#include "config.h"
#include "bands.h"
#include "entcode.h"
#include <assert.h>
#include <string.h>

int main(void)
{
    ec_ctx ctx, expected;
    memset(&ctx, 0x5a, sizeof(ctx));
    expected = ctx;
    expected.error = 1;
    /* No valid mode, bands, or scratch: rejection must precede every access. */
    quant_all_bands(1, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL,
                    0, 0, 0, 0, NULL, 0, 0, &ctx, 0, 0, NULL, 0, 0, 0,
                    NULL, 0);
    assert(memcmp(&ctx, &expected, sizeof(ctx)) == 0);
    return 0;
}
