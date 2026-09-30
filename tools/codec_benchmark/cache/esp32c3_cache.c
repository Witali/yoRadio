// SPDX-License-Identifier: GPL-2.0-or-later
// QEMU 9.2 plugin: a unified read-only flash-cache traffic model, not a timer.
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "qemu-plugin.h"
#include "cache_model.h"

_Static_assert(sizeof(uintptr_t) >= 8, "This plugin requires a 64-bit host");

QEMU_PLUGIN_EXPORT int qemu_plugin_version = QEMU_PLUGIN_VERSION;
static cache_model_t caches[3]; // continuous LRU, continuous FIFO, cold-call LRU
static cache_stats_t stats[3];
static uint32_t mmu[128];
static bool active;
static int selected = -1;
static unsigned passes[3], calls, rows, errors;
static uint64_t unknown, mmu_writes;
static FILE *report;
static const char *names[] = {"lc48000_stereo", "he48000_stereo", "hev2_44100_stereo"};
static const char *models[] = {"continuous_lru", "continuous_fifo", "cold_call_lru"};

static bool is_flash(uint64_t address) {
    return (address >= 0x42000000 && address < 0x42800000) ||
           (address >= 0x3c000000 && address < 0x3c800000);
}

static void access_flash(uint64_t address, unsigned size, bool data) {
    // Split at MMU page boundaries; mapping may be non-contiguous.
    while (size) {
        unsigned part = 0x10000 - (address & 0xffff);
        if (part > size) part = size;
        uint32_t physical;
        if (flash_offset(address, mmu, &physical)) {
            for (unsigned i = 0; i < 3; ++i) {
                if (i < 2 || active)
                    cache_access(&caches[i], active ? &stats[i] : NULL, physical, part, data);
            }
        } else if (active) ++unknown;
        size -= part;
        address += part;
    }
}

static void finish_case(void) {
    if (selected < 0 || active) { ++errors; return; }
    fprintf(report, "%s{\"case\":\"%s\",\"pass\":%u,\"calls\":%u,\"models\":{",
            rows++ ? ",\n" : "", names[selected], passes[selected], calls);
    for (unsigned i = 0; i < 3; ++i) {
        fprintf(report, "%s\"%s\":{\"instruction_line_accesses\":%" PRIu64
                ",\"data_line_accesses\":%" PRIu64 ",\"instruction_misses\":%" PRIu64
                ",\"data_misses\":%" PRIu64 ",\"evictions\":%" PRIu64
                ",\"refill_bytes\":%" PRIu64 "}", i ? "," : "", models[i],
                stats[i].accesses[0], stats[i].accesses[1], stats[i].misses[0],
                stats[i].misses[1], stats[i].evictions,
                (stats[i].misses[0] + stats[i].misses[1]) * CACHE_LINE);
    }
    fputs("}}", report);
    fflush(report);
    selected = -1;
}

static void marker(unsigned int cpu, void *userdata) {
    (void)cpu;
    unsigned code = (uintptr_t)userdata;
    if (code >= 0x6a0 && code <= 0x6a2) {
        if (active || selected >= 0) ++errors;
        selected = code - 0x6a0;
        ++passes[selected];
        memset(stats, 0, sizeof(stats));
        calls = 0;
    } else if (code == 0x6b0) {
        if (active || selected < 0) ++errors;
        cache_clear(&caches[2]);
        active = true;
        ++calls;
    } else if (code == 0x6b1) {
        if (!active) ++errors;
        active = false;
    } else if (code == 0x6bf) finish_case();
}

static void instruction(unsigned int cpu, void *userdata) {
    (void)cpu;
    uintptr_t packed = (uintptr_t)userdata;
    access_flash(packed >> 3, packed & 7, false);
}

static void memory(unsigned int cpu, qemu_plugin_meminfo_t info,
                   uint64_t address, void *userdata) {
    (void)cpu; (void)userdata;
    if (qemu_plugin_mem_is_store(info)) {
        if (address >= 0x600c5000 && address < 0x600c5200) {
            if (active) ++errors;
            qemu_plugin_mem_value value = qemu_plugin_mem_get_value(info);
            if ((address & 3) || value.type != QEMU_PLUGIN_MEM_VALUE_U32) { ++errors; return; }
            unsigned index = (address - 0x600c5000) / 4;
            if (mmu[index] != value.data.u32) {
                for (unsigned i = 0; i < 3; ++i) cache_clear(&caches[i]);
            }
            mmu[index] = value.data.u32;
            ++mmu_writes;
        } else if (active && (is_flash(address) ||
                   (address >= 0x600c4000 && address < 0x600c5000))) ++errors;
    } else if (is_flash(address)) {
        access_flash(address, 1u << qemu_plugin_mem_size_shift(info), true);
    }
}

static void translate(qemu_plugin_id_t id, struct qemu_plugin_tb *tb) {
    (void)id;
    for (size_t i = 0; i < qemu_plugin_tb_n_insns(tb); ++i) {
        struct qemu_plugin_insn *insn = qemu_plugin_tb_get_insn(tb, i);
        uint64_t address = qemu_plugin_insn_vaddr(insn);
        size_t size = qemu_plugin_insn_size(insn);
        uint8_t bytes[4] = {0};
        qemu_plugin_insn_data(insn, bytes, sizeof(bytes));
        uint32_t opcode = bytes[0] | bytes[1] << 8 | bytes[2] << 16 | (uint32_t)bytes[3] << 24;
        unsigned code = opcode >> 20;
        bool control = size == 4 && (opcode & 0xfffff) == 0x13 &&
                       ((code >= 0x6a0 && code <= 0x6a2) || code == 0x6b0 ||
                        code == 0x6b1 || code == 0x6bf);
        // Begin-marker fetch warms the cache; end-marker fetch is the last
        // measured fetch. Both are ordinary instructions in the guest stream.
        if (is_flash(address))
            qemu_plugin_register_vcpu_insn_exec_cb(insn, instruction, QEMU_PLUGIN_CB_NO_REGS,
                                                   (void *)(uintptr_t)((address << 3) | size));
        if (control)
            qemu_plugin_register_vcpu_insn_exec_cb(insn, marker, QEMU_PLUGIN_CB_NO_REGS,
                                                   (void *)(uintptr_t)code);
        qemu_plugin_register_vcpu_mem_cb(insn, memory, QEMU_PLUGIN_CB_NO_REGS,
                                         QEMU_PLUGIN_MEM_RW, NULL);
    }
}

static void finish(qemu_plugin_id_t id, void *userdata) {
    (void)id; (void)userdata;
    if (active || selected >= 0 || rows != 6) ++errors;
    for (unsigned i = 0; i < 3; ++i) if (passes[i] != 2) ++errors;
    fprintf(report, "\n],\"errors\":%u,\"unmapped_measured_accesses\":%" PRIu64
            ",\"observed_mmu_writes\":%" PRIu64 "}\n", errors, unknown, mmu_writes);
    fclose(report);
}

QEMU_PLUGIN_EXPORT int qemu_plugin_install(qemu_plugin_id_t id,
                                            const qemu_info_t *info,
                                            int argc, char **argv) {
    if (!info->system_emulation || info->system.smp_vcpus != 1 ||
        strcmp(info->target_name, "riscv32") || argc != 1 || strncmp(argv[0], "out=", 4)) return -1;
    report = fopen(argv[0] + 4, "w");
    if (!report) return -1;
    for (unsigned i = 0; i < 128; ++i) mmu[i] = 0x100;
    caches[1].fifo = true;
    fputs("{\"schema\":1,\"kind\":\"modelled_flash_cache_traffic\",\"target\":\"esp32c3\","
          "\"cache_bytes\":16384,\"ways\":8,\"line_bytes\":32,"
          "\"physical_timing_measured\":false,\"writeback_bytes\":0,"
          "\"assumptions\":{\"tag\":\"physical_flash_line\",\"set_index\":\"physical_line_modulo_64\","
          "\"hardware_replacement_policy_validated\":false,\"prefetch_modelled\":false,"
          "\"cache_control_commands_modelled\":false,\"refill_penalty_cycles\":null},\"runs\":[\n", report);
    qemu_plugin_register_vcpu_tb_trans_cb(id, translate);
    qemu_plugin_register_atexit_cb(id, finish, NULL);
    return 0;
}
