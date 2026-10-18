#pragma once
#define ESP_RETURN_ON_FALSE(condition,error,...) do {if (!(condition)) return (error);} while (0)
#define ESP_RETURN_ON_ERROR(expression,...) do {int error=(expression);if (error) return error;} while (0)
