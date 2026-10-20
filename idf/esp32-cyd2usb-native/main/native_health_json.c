#include "native_health.h"

#include <inttypes.h>
#include <stdarg.h>
#include <stdio.h>
#include "json_buffer.h"

// Only bounded numeric groups and fixed keys use this formatter. User strings
// continue through json_buffer_string in the ordinary status endpoint.
static void append_numbers(json_buffer_t *out, const char *format, ...)
    __attribute__((format(printf, 2, 3)));
static void append_numbers(json_buffer_t *out, const char *format, ...) {
    char chunk[256];
    va_list arguments;
    va_start(arguments, format);
    int count = vsnprintf(chunk, sizeof(chunk), format, arguments);
    va_end(arguments);
    if (count < 0 || (size_t)count >= sizeof(chunk)) {out->failed=true;return;}
    json_buffer_bytes(out, chunk, (size_t)count);
}

static void append_percent(json_buffer_t *out, bool available, uint16_t tenths) {
    if (available) append_numbers(out, "%u.%u", (unsigned)(tenths/10), (unsigned)(tenths%10));
    else json_buffer_raw(out, "null");
}

bool native_health_format_json(char *body, size_t capacity,
        const native_health_snapshot_t *snapshot, const native_health_runtime_t *runtime) {
    if (!body || !snapshot || !runtime || !runtime->cores || runtime->cores>2) return false;
    json_buffer_t out;json_buffer_init(&out,body,capacity);
    const native_health_faults_t *f=&snapshot->faults;
    const native_health_cpu_t *cpu=&snapshot->cpu;
    const native_input_health_t *input=&runtime->input;
    const native_output_metrics_t *driver=&runtime->output_driver;
    append_numbers(&out,"{\"schema\":1,\"boot_id\":\"%016" PRIx64 "\",\"uptime_ms\":%" PRIu64
        ",\"reset_reason\":%" PRIu32 ",\"cores\":%" PRIu32,
        runtime->boot_id,runtime->uptime_ms,runtime->reset_reason,runtime->cores);
    append_numbers(&out,",\"heap\":%" PRIu32 ",\"largest\":%" PRIu32 ",\"minimum_heap\":%" PRIu32
        ",\"tasks\":%" PRIu32 ",\"allocation_failures\":%" PRIu32,
        runtime->heap_free,runtime->heap_largest,runtime->heap_minimum,runtime->tasks,f->allocation_failures);
    append_numbers(&out,",\"memory\":{\"internal_free\":%" PRIu32 ",\"internal_largest\":%" PRIu32
        ",\"dma_free\":%" PRIu32 ",\"dma_largest\":%" PRIu32 "}",
        runtime->internal_free,runtime->internal_largest,runtime->dma_free,runtime->dma_largest);
    append_numbers(&out,",\"last_allocation_failure\":{\"size\":%" PRIu32 ",\"caps\":%" PRIu32 "}",
        f->allocation_size,f->allocation_caps);
    append_numbers(&out,",\"decoder_failure\":{\"sequence\":%" PRIu32 ",\"generation\":%" PRIu32
        ",\"codec\":%" PRIu32 ",\"stage\":%" PRIu32 ",\"result\":%" PRId32,
        f->decoder_failures,f->decoder_generation,f->decoder_codec,f->decoder_stage,f->decoder_result);
    append_numbers(&out,",\"completion\":%" PRIu32 ",\"input_bytes\":%" PRIu32
        ",\"allocation_sequence\":%" PRIu32 "}",
        f->decoder_completion,f->decoder_input_bytes,f->decoder_allocation_sequence);
    append_numbers(&out,",\"stream_failure\":{\"sequence\":%" PRIu32 ",\"generation\":%" PRIu32
        ",\"completion\":%" PRIu32 ",\"result\":%" PRId32 "}",
        f->stream_failures,f->stream_generation,f->stream_completion,f->stream_result);
    append_numbers(&out,",\"output\":{\"failures\":%" PRIu32 ",\"write_errors\":%" PRIu32
        ",\"configure_errors\":%" PRIu32 ",\"flush_errors\":%" PRIu32,
        f->output_failures,f->output_write_errors,f->output_configure_errors,f->output_flush_errors);
    append_numbers(&out,",\"generation\":%" PRIu32 ",\"stage\":%" PRIu32 ",\"result\":%" PRId32 "}",
        f->output_generation,f->output_stage,f->output_result);
    append_numbers(&out,",\"output_driver\":{\"writes\":%" PRIu32 ",\"requested_bytes\":%" PRIu64
        ",\"written_bytes\":%" PRIu64 ",\"errors\":%" PRIu32,
        driver->writes,driver->requested_bytes,driver->written_bytes,driver->errors);
    append_numbers(&out,",\"timeouts\":%" PRIu32 ",\"short_writes\":%" PRIu32
        ",\"saturated\":%s,\"completion_queue_drops\":",
        driver->timeouts,driver->short_writes,driver->saturated?"true":"false");
    if (driver->queue_drops_available) append_numbers(&out,"%" PRIu32,driver->completion_queue_drops);
    else json_buffer_raw(&out,"null");
    append_numbers(&out,",\"timing_enabled\":%s,\"timing_samples\":%" PRIu32
        ",\"invalid_time_samples\":%" PRIu32 ",\"write_us\":",
        driver->timing_enabled?"true":"false",driver->timing_samples,driver->invalid_time_samples);
    bool timed=driver->timing_enabled && driver->timing_samples;
    if (timed) append_numbers(&out,"%" PRIu64,driver->write_us);
    else json_buffer_raw(&out,"null");
    json_buffer_raw(&out,",\"max_write_us\":");
    if (timed) append_numbers(&out,"%" PRIu64,driver->max_write_us);
    else json_buffer_raw(&out,"null");
    json_buffer_raw(&out,"}");
    append_numbers(&out,",\"input\":{\"available\":%s,\"leased\":%s,\"resident\":%" PRIu32
        ",\"minimum\":%" PRIu32 ",\"target\":%" PRIu32 ",\"limit\":%" PRIu32,
        input->available?"true":"false",input->leased?"true":"false",
        input->resident,input->minimum,input->target,input->limit);
    append_numbers(&out,",\"ready\":%" PRIu32 ",\"reading\":%" PRIu32 ",\"writing\":%" PRIu32
        ",\"released\":%" PRIu32 ",\"ready_payload_bytes\":%" PRIu32
        ",\"reading_payload_bytes\":%" PRIu32 "}",
        input->ready,input->reading,input->writing,input->released,
        input->ready_payload_bytes,input->reading_payload_bytes);
    append_numbers(&out,",\"cpu\":{\"enabled\":%s,\"available\":%s,\"sample_uptime_ms\":%" PRIu64
        ",\"snapshot_failures\":%" PRIu32 ",\"overall_percent\":",
        cpu->enabled?"true":"false",cpu->available?"true":"false",
        cpu->sampled_us/1000,cpu->snapshot_failures);
    append_percent(&out,cpu->available,cpu->overall_tenths);
    json_buffer_raw(&out,",\"core_percent\":[");
    for (unsigned core=0;core<runtime->cores;++core) {
        if (core)json_buffer_raw(&out,",");
        append_percent(&out,cpu->available,cpu->core_tenths[core]);
    }
    json_buffer_raw(&out,"],\"tasks\":{");
    static const char *const names[NATIVE_HEALTH_TASKS]={"stream","decode","output","http"};
    for (unsigned role=0;role<NATIVE_HEALTH_TASKS;++role) {
        if (role)json_buffer_raw(&out,",");
        json_buffer_string(&out,names[role]);
        json_buffer_raw(&out,":{\"percent_of_one_core\":");
        append_percent(&out,cpu->task[role].available,cpu->task[role].percent_tenths);
        json_buffer_raw(&out,",\"stack_free_min\":");
        if (cpu->task[role].present) append_numbers(&out,"%" PRIu32,cpu->task[role].stack_free_min);
        else json_buffer_raw(&out,"null");
        json_buffer_raw(&out,"}");
    }
    json_buffer_raw(&out,"}}}");
    return !out.failed;
}
