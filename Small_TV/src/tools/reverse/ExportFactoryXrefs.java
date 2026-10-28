// Export address-only references from the complete existing analysis database.
// @category SmallTV.Analysis
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Reference;
import com.google.gson.GsonBuilder;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class ExportFactoryXrefs extends GhidraScript {
    // Preserve numeric identity; do not export string data or decompiler literals.
    private String address(Address value) {
        // FIXED_TEST: Address.toString may include "ram:"; emit a numeric ELF address.
        return value.getAddressSpace().isMemorySpace() ? String.format("0x%08x", value.getOffset()) : value.toString();
    }

    // Describe the real containing function without guessing an unanalysed boundary.
    private Map<String,Object> owner(Address from) {
        Map<String,Object> row = new LinkedHashMap<>();
        Function function = currentProgram.getFunctionManager().getFunctionContaining(from);
        if (function != null) {
            row.put("entry", address(function.getEntryPoint()));
            row.put("name", function.getName());
        }
        return row;
    }

    // Save only reference type, code location and instruction bytes for ELF replay.
    private Map<String,Object> reference(Reference ref) throws Exception {
        Map<String,Object> row = new LinkedHashMap<>();
        Address from = ref.getFromAddress();
        row.put("from", address(from)); row.put("to", address(ref.getToAddress()));
        row.put("from_space", from.getAddressSpace().getName());
        row.put("to_space", ref.getToAddress().getAddressSpace().getName());
        row.put("type", ref.getReferenceType().toString());
        row.put("source", ref.getSource().toString());
        row.put("operand", ref.getOperandIndex()); row.put("owner", owner(from));
        Instruction instruction = getInstructionAt(from);
        if (instruction != null) {
            row.put("mnemonic", instruction.getMnemonicString());
            row.put("bytes", HexFormat.of().formatHex(instruction.getBytes()));
        }
        return row;
    }

    // Query every reference to an exact address, including data/callback pointers.
    private List<Map<String,Object>> references(Address target) throws Exception {
        List<Map<String,Object>> rows = new ArrayList<>();
        var refs = currentProgram.getReferenceManager().getReferencesTo(target);
        while (refs.hasNext()) { monitor.checkCancelled(); rows.add(reference(refs.next())); }
        return rows;
    }

    @Override
    public void run() throws Exception {
        // Read-only export: no createFunction, symbol mutation, analysis or program saves.
        String[] args = getScriptArgs();
        if (args.length != 1) throw new IllegalArgumentException("Expected a new output JSON path");
        Path path = Path.of(args[0]);
        if (Files.exists(path)) throw new IllegalArgumentException("Preserve existing evidence");
        Map<String,Object> result = new LinkedHashMap<>();
        result.put("schema_version", 1); result.put("semantic_equivalence_proved", false);
        result.put("whole_image_completeness_proved", false);
        result.put("program_sha256", currentProgram.getExecutableSHA256());
        result.put("language", currentProgram.getLanguageID().toString());
        result.put("compiler", currentProgram.getCompilerSpec().getCompilerSpecID().toString());
        Map<String,Long> targets = new LinkedHashMap<>();
        targets.put("timer_network", 0x3fcc39f0L); targets.put("timer_slow", 0x3fcc39f4L);
        targets.put("browser_time_stored", 0x3fcb7d14L);
        targets.put("browser_time_active_gp_minus_2000", 0x3fcb41f0L);
        targets.put("click_count", 0x3fcc3a90L); targets.put("jpeg_flash_output", 0x3fcc3a6cL);
        targets.put("settings_base", 0x3fcb7b9cL);
        targets.put("timer_callback", 0x4200826aL); targets.put("app_main", 0x42008e56L);
        targets.put("jpeg_output_callback", 0x4200c374L); targets.put("draw_jpeg", 0x4200c518L);
        Map<String,Object> queried = new LinkedHashMap<>();
        for (var entry : targets.entrySet()) {
            Map<String,Object> row = new LinkedHashMap<>();
            row.put("address", String.format("0x%08x", entry.getValue()));
            row.put("references", references(toAddr(entry.getValue()))); queried.put(entry.getKey(), row);
        }
        result.put("targets", queried);
        List<Map<String,Object>> blocks = new ArrayList<>();
        for (MemoryBlock block : currentProgram.getMemory().getBlocks()) {
            Map<String,Object> row = new LinkedHashMap<>();
            row.put("name", block.getName()); row.put("start", address(block.getStart()));
            row.put("size", block.getSize()); row.put("execute", block.isExecute());
            row.put("initialized", block.isInitialized());
            if (block.isInitialized()) {
                byte[] data = new byte[Math.toIntExact(block.getSize())];
                int count = currentProgram.getMemory().getBytes(block.getStart(), data);
                if (count != data.length) throw new IllegalStateException("Incomplete block read");
                row.put("sha256", HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(data)));
            }
            blocks.add(row);
        }
        result.put("memory_blocks", blocks);
        result.put("instruction_count", currentProgram.getListing().getNumInstructions());
        // Ghidra's existing database does not resolve every gp-relative data reference.
        // Export those instructions separately for independent RV32/GNU decoding.
        List<Map<String,Object>> gp = new ArrayList<>();
        var instructions = currentProgram.getListing().getInstructions(true);
        while (instructions.hasNext()) {
            Instruction instruction = instructions.next();
            if (instruction.getLength() != 4) continue;
            byte[] data = instruction.getBytes();
            int word = (data[0]&255) | ((data[1]&255)<<8) | ((data[2]&255)<<16) | ((data[3]&255)<<24);
            int opcode = word & 127;
            if ((opcode != 3 && opcode != 35) || ((word >>> 15)&31) != 3) continue;
            Map<String,Object> row = new LinkedHashMap<>();
            row.put("from", address(instruction.getAddress()));
            row.put("bytes", HexFormat.of().formatHex(data)); row.put("owner", owner(instruction.getAddress()));
            row.put("mnemonic", instruction.getMnemonicString()); gp.add(row);
        }
        result.put("gp_accesses", gp);
        List<Map<String,Object>> functions = new ArrayList<>();
        var iterator = currentProgram.getFunctionManager().getFunctions(true);
        while (iterator.hasNext()) {
            monitor.checkCancelled(); Function function = iterator.next();
            Map<String,Object> row = new LinkedHashMap<>();
            row.put("entry", address(function.getEntryPoint())); row.put("name", function.getName());
            row.put("space", function.getEntryPoint().getAddressSpace().getName());
            row.put("body_bytes", function.getBody().getNumAddresses());
            row.put("references", references(function.getEntryPoint()));
            functions.add(row);
        }
        result.put("functions", functions);
        Files.createDirectories(path.toAbsolutePath().getParent());
        try (PrintWriter out = new PrintWriter(Files.newBufferedWriter(path, StandardCharsets.UTF_8))) {
            new GsonBuilder().setPrettyPrinting().create().toJson(result, out);
        }
        println("Exported " + functions.size() + " analysed functions and " + targets.size() + " target reference sets");
    }
}
