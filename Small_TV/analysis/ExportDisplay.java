// Export the display routines from the reconstructed ESP32-C2 analysis ELF.
// @category Analysis
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.listing.ReturnParameterImpl;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.DataIterator;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.symbol.Reference;
import java.io.File;
import java.io.PrintWriter;
import java.util.LinkedHashMap;
import java.util.Map;

public class ExportDisplay extends GhidraScript {
    private StructureDataType structure(String name, Object... fields) {
        StructureDataType result = new StructureDataType(name, 0);
        for (int i = 0; i < fields.length; i += 2) {
            result.add((DataType)fields[i], (String)fields[i+1], null);
        }
        return result;
    }
    private void signature(long address, DataType returnType, DataType... types) throws Exception {
        Function function = getFunctionAt(toAddr(address));
        Parameter[] parameters = new Parameter[types.length];
        for (int i = 0; i < types.length; i++) {
            parameters[i] = new ParameterImpl("arg" + i, types[i], currentProgram);
        }
        function.updateFunction(currentProgram.getCompilerSpec().getDefaultCallingConvention().getName(),
            new ReturnParameterImpl(returnType, currentProgram),
            java.util.Arrays.asList(parameters), FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true, SourceType.USER_DEFINED);
    }
    @Override
    public void run() throws Exception {
        String outputDir = getScriptArgs()[0];
        new File(outputDir).mkdirs();
        Map<Long, String> named = new LinkedHashMap<>();
        named.put(0x42008bd2L, "Set_Backlight_Duty");
        named.put(0x42008d62L, "Backlight_pwm_init");
        named.put(0x4200917cL, "st7789_spi_pre_transfer_callback");
        named.put(0x42009192L, "st7789_delay_ms");
        named.put(0x420091b2L, "st7789_reset");
        named.put(0x420091e4L, "st7789_write_cmd");
        named.put(0x4200925aL, "st7789_write_data");
        named.put(0x420092d0L, "st7789_set_window");
        named.put(0x4200934aL, "st7789_init");
        named.put(0x4200950eL, "st7789_blit_rect");
        named.put(0x4200958aL, "st7789_draw_pixel");
        named.put(0x42008e56L, "app_main");
        named.put(0x42037fbeL, "spi_bus_initialize");
        named.put(0x420385dcL, "spi_bus_add_device");
        named.put(0x40383c7cL, "spi_device_polling_transmit");
        named.put(0x42014c2eL, "ledc_timer_config");
        named.put(0x42015104L, "ledc_channel_config");
        named.put(0x4201550cL, "ledc_set_duty");
        named.put(0x42014e68L, "ledc_update_duty");
        named.put(0x420ada16L, "gpio_config");
        named.put(0x40384ea8L, "gpio_set_level");
        named.put(0x40389aeeL, "vTaskDelay");
        named.put(0x4200065cL, "esp_restart");
        for (Map.Entry<Long, String> item : named.entrySet()) {
            Address address = toAddr(item.getKey());
            Function function = getFunctionAt(address);
            if (function == null) function = createFunction(address, item.getValue());
            if (function != null) function.setName(item.getValue(), SourceType.USER_DEFINED);
        }
        DataType u32 = UnsignedIntegerDataType.dataType;
        DataType i32 = IntegerDataType.dataType;
        DataType u8 = UnsignedCharDataType.dataType;
        DataType u16 = UnsignedShortDataType.dataType;
        DataType u64 = UnsignedLongLongDataType.dataType;
        DataType v = VoidDataType.dataType;
        DataType ptr = new PointerDataType(v, 4);
        DataType pad3 = new ArrayDataType(u8, 3, 1);
        DataType pad2 = new ArrayDataType(u8, 2, 1);
        StructureDataType gpio = structure("gpio_config_t", u64,"pin_bit_mask", i32,"mode",
            i32,"pull_up_en",i32,"pull_down_en",i32,"intr_type");
        StructureDataType bus = structure("spi_bus_config_t",i32,"mosi_io_num",i32,"miso_io_num",
            i32,"sclk_io_num",i32,"quadwp_io_num",i32,"quadhd_io_num",i32,"data4_io_num",
            i32,"data5_io_num",i32,"data6_io_num",i32,"data7_io_num",u8,"data_io_default_level",
            pad3,"padding",i32,"max_transfer_sz",u32,"flags",i32,"isr_cpu_id",i32,"intr_flags");
        StructureDataType device = structure("spi_device_interface_config_t",u8,"command_bits",
            u8,"address_bits",u8,"dummy_bits",u8,"mode",i32,"clock_source",u16,"duty_cycle_pos",
            u16,"cs_ena_pretrans",u8,"cs_ena_posttrans",pad3,"padding",i32,"clock_speed_hz",
            i32,"input_delay_ns",i32,"sample_point",i32,"spics_io_num",u32,"flags",
            i32,"queue_size",ptr,"pre_cb",ptr,"post_cb");
        StructureDataType transaction = structure("spi_transaction_t",u32,"flags",u16,"cmd",
            pad2,"padding",u64,"addr",u32,"length",u32,"rxlength",u32,"override_freq_hz",
            ptr,"user",ptr,"tx_buffer",ptr,"rx_buffer");
        StructureDataType timer = structure("ledc_timer_config_t",i32,"speed_mode",i32,"duty_resolution",
            i32,"timer_num",u32,"freq_hz",i32,"clk_cfg",u8,"deconfigure",pad3,"padding");
        StructureDataType channel = structure("ledc_channel_config_t",i32,"gpio_num",i32,"speed_mode",
            i32,"channel",i32,"intr_type",i32,"timer_sel",u32,"duty",i32,"hpoint",
            i32,"sleep_mode",u32,"flags");
        signature(0x420ada16L,i32,new PointerDataType(gpio,4));
        signature(0x42037fbeL,i32,i32,new PointerDataType(bus,4),i32);
        signature(0x420385dcL,i32,i32,new PointerDataType(device,4),new PointerDataType(ptr,4));
        signature(0x40383c7cL,i32,ptr,new PointerDataType(transaction,4));
        signature(0x42014c2eL,i32,new PointerDataType(timer,4));
        signature(0x42015104L,i32,new PointerDataType(channel,4));
        signature(0x4201550cL,i32,i32,i32,u32);
        signature(0x42014e68L,i32,i32,i32);
        signature(0x40384ea8L,i32,i32,u32);
        signature(0x40389aeeL,v,u32);
        signature(0x4200065cL,v);
        getFunctionAt(toAddr(0x4200065cL)).setNoReturn(true);
        signature(0x42008bd2L,v,u32);
        signature(0x42008d62L,v);
        signature(0x4200917cL,v,new PointerDataType(transaction,4));
        signature(0x42009192L,v,u32);
        signature(0x420091b2L,v);
        signature(0x420091e4L,v,u8);
        signature(0x4200925aL,v,ptr,i32);
        signature(0x420092d0L,v,u32,u32,u32,u32);
        signature(0x4200934aL,v);
        signature(0x4200950eL,v,u32,u32,u32,u32,ptr);
        signature(0x4200958aL,v,u32,u32,u16);
        signature(0x42008e56L,v);
        clearListing(toAddr(0x3fcb7d58L),toAddr(0x3fcb7d5bL));
        createData(toAddr(0x3fcb7d58L),new ArrayDataType(u8,4,1));
        createLabel(toAddr(0x3fcb7d58L),"display_init_data",true);
        createLabel(toAddr(0x3fcc39fcL),"display_spi",true);
        createLabel(toAddr(0x3fcc39ecL),"backlight_level_per_mille",true);
        Map<Function,String> peripheralFunctions = new LinkedHashMap<>();
        DataIterator dataIterator = currentProgram.getListing().getDefinedData(true);
        while (dataIterator.hasNext()) {
            Data data = dataIterator.next();
            Object value = data.getValue();
            if (!(value instanceof String)) continue;
            String text = (String)value;
            if (!text.matches("(gpio_|uart_|i2c_|adc_|rmt_|sdmmc_|sdspi_|temperature_sensor_)[A-Za-z0-9_]+")) continue;
            for (Reference ref : getReferencesTo(data.getAddress())) {
                Function function = getFunctionContaining(ref.getFromAddress());
                if (function != null) peripheralFunctions.put(function,text);
            }
        }
        try (PrintWriter writer = new PrintWriter(new File(outputDir,"peripheral-api-references.tsv"),"UTF-8")) {
            writer.println("string_identifier\tfunction_entry\tcall_address\tcaller_entry\tcaller");
            for (Map.Entry<Function,String> item : peripheralFunctions.entrySet()) {
                Function function = item.getKey();
                if (function.getName().startsWith("FUN_")) function.setName(item.getValue(),SourceType.ANALYSIS);
                boolean found = false;
                for (Reference ref : getReferencesTo(function.getEntryPoint())) {
                    if (!ref.getReferenceType().isCall()) continue;
                    Function caller = getFunctionContaining(ref.getFromAddress());
                    writer.printf("%s\t%s\t%s\t%s\t%s%n",item.getValue(),function.getEntryPoint(),
                        ref.getFromAddress(),caller == null ? "-" : caller.getEntryPoint(),
                        caller == null ? "-" : caller.getName());
                    found = true;
                }
                if (!found) writer.printf("%s\t%s\t-\t-\t-%n",item.getValue(),function.getEntryPoint());
            }
        }
        try (PrintWriter writer = new PrintWriter(new File(outputDir,"weather-endpoint-references.tsv"),"UTF-8")) {
            writer.println("endpoint_string\treference\tfunction_entry");
            for (Reference ref : getReferencesTo(toAddr(0x3c0c3b58L))) {
                Function function = getFunctionContaining(ref.getFromAddress());
                writer.printf("3c0c3b58\t%s\t%s%n",ref.getFromAddress(),
                    function == null ? "-" : function.getEntryPoint());
            }
        }
        try (PrintWriter writer = new PrintWriter(new File(outputDir,"peripheral-callers.tsv"),"UTF-8")) {
            writer.println("target\tentry\tcall_address\tcaller_entry\tcaller");
            for (Map.Entry<Long,String> item : named.entrySet()) {
                if (item.getKey() < 0x42037fbeL && item.getKey() >= 0x42000000L &&
                    !item.getValue().startsWith("ledc")) continue;
                for (Reference ref : getReferencesTo(toAddr(item.getKey()))) {
                    if (!ref.getReferenceType().isCall()) continue;
                    Function caller = getFunctionContaining(ref.getFromAddress());
                    writer.printf("%s\t%08x\t%s\t%s\t%s%n",item.getValue(),item.getKey(),
                        ref.getFromAddress(),caller == null ? "-" : caller.getEntryPoint(),
                        caller == null ? "-" : caller.getName());
                }
            }
        }
        DecompInterface decompiler = new DecompInterface();
        decompiler.openProgram(currentProgram);
        try (PrintWriter writer = new PrintWriter(new File(outputDir, "display-decompiled.c"), "UTF-8")) {
            for (Map.Entry<Long, String> item : named.entrySet()) {
                if (item.getKey() == 0x42037fbeL) break;
                Function function = getFunctionAt(toAddr(item.getKey()));
                if (function == null) { writer.println("// Missing " + item.getValue()); continue; }
                writer.printf("// Entry: 0x%08x; end: %s%n", item.getKey(), function.getBody().getMaxAddress());
                DecompileResults result = decompiler.decompileFunction(function, 60, monitor);
                if (result.decompileCompleted()) writer.println(result.getDecompiledFunction().getC());
                else writer.println("// Decompilation failed: " + result.getErrorMessage());
                writer.println();
                println("Exported " + item.getValue() + " at " + function.getEntryPoint());
            }
        }
        decompiler.dispose();
        println("Program functions: " + currentProgram.getFunctionManager().getFunctionCount());
    }
}
