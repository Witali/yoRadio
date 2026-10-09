#pragma once
// Maximum absolute difference in signed 16-bit PCM, per sample and channel.
// A limit of 3 means +/-3 integer units, not three discarded bits (+/-7).
// Numerical qualification does not waive format, RAM, lifecycle or speed gates.
#define AAC_PCM_PRODUCTION_ERROR_LSB 3
#define AAC_PCM_DEVELOPMENT_ERROR_LSB 5
