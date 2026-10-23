idf_component_register(SRCS "curve_unit.c" "public/floor0.c" "public/floor_lookup.c"
    INCLUDE_DIRS "." "public" REQUIRES freertos)
# Preserve public C diagnostics. SDK function/data section GC must remove
# unreachable decoder glue; no stub, codec archive or source edits are allowed.
target_compile_options(${COMPONENT_LIB} PRIVATE -fno-inline -ffunction-sections -fdata-sections)
