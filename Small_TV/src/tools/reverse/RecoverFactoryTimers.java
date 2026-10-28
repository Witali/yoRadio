// Restore byte-qualified timer metadata only in a disposable read-only session.
// @category SmallTV.Analysis
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.SourceType;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class RecoverFactoryTimers extends GhidraScript {
    // Hash initialized program bytes independently of temporary analysis metadata.
    private Map<String,String> memoryHashes() throws Exception {
        Map<String,String> result = new LinkedHashMap<>();
        for (var block : currentProgram.getMemory().getBlocks()) {
            if (!block.isInitialized()) continue;
            byte[] data = new byte[Math.toIntExact(block.getSize())];
            if (currentProgram.getMemory().getBytes(block.getStart(), data) != data.length)
                throw new IllegalStateException("Incomplete block read");
            result.put(block.getName(), digest(data));
        }
        return result;
    }

    // Use the same byte identity as the independent SDK matcher.
    private String digest(byte[] data) throws Exception {
        return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(data));
    }

    // Preserve the actual existing name/body before any transient metadata change.
    private Map<String,Object> describe(Function function) {
        Map<String,Object> result = new LinkedHashMap<>();
        if (function == null) return result;
        result.put("entry", String.format("0x%08x", function.getEntryPoint().getOffset()));
        result.put("name", function.getName());
        result.put("body_bytes", function.getBody().getNumAddresses());
        List<List<String>> ranges = new ArrayList<>();
        var iterator = function.getBody().getAddressRanges();
        while (iterator.hasNext()) {
            var range = iterator.next();
            ranges.add(List.of(String.format("0x%08x", range.getMinAddress().getOffset()),
                               String.format("0x%08x", range.getMaxAddress().getOffset())));
        }
        result.put("ranges", ranges);
        return result;
    }

    // FunctionManager's count and its enumerable functions are separate observations.
    private int enumeratedFunctions() {
        int count = 0;
        var iterator = currentProgram.getFunctionManager().getFunctions(true);
        while (iterator.hasNext()) { iterator.next(); count++; }
        return count;
    }

    // Require agreeing duplicate rows where the two verified selections overlap.
    private void addSpecs(Map<Long,JsonObject> specs, Iterable<com.google.gson.JsonElement> rows) {
        for (var item : rows) {
            var row = item.getAsJsonObject();
            long start = Long.decode(row.get("start").getAsString());
            if (specs.containsKey(start)) {
                var old = specs.get(start);
                for (String key : new String[]{"name", "end", "factory_function_sha256", "linked_instruction_starts"})
                    if (!old.get(key).equals(row.get(key))) throw new IllegalArgumentException("Conflicting matched bounds");
            } else specs.put(start, row);
        }
    }

    @Override
    public void run() throws Exception {
        // Headless -readOnly discards these metadata edits; no program byte is patched.
        String[] args = getScriptArgs();
        if (args.length != 3) throw new IllegalArgumentException("Expected timer match, dispatch audit and new output");
        Path output = Path.of(args[2]);
        if (Files.exists(output)) throw new IllegalArgumentException("Preserve existing evidence");
        var timers = JsonParser.parseString(Files.readString(Path.of(args[0]))).getAsJsonObject();
        var audit = JsonParser.parseString(Files.readString(Path.of(args[1]))).getAsJsonObject();
        var factory = audit.getAsJsonObject("factory");
        String identity = currentProgram.getExecutableSHA256();
        if (!timers.get("passed").getAsBoolean() || !audit.get("passed").getAsBoolean() ||
            !identity.equals(timers.get("factory_elf_sha256").getAsString()) ||
            !identity.equals(factory.get("factory_elf_sha256").getAsString()))
            throw new IllegalArgumentException("Unqualified timer input");
        Map<Long,JsonObject> specs = new LinkedHashMap<>();
        addSpecs(specs, timers.getAsJsonArray("functions"));
        addSpecs(specs, factory.getAsJsonArray("functions"));
        if (specs.size() != 21) throw new IllegalArgumentException("Expected 21 distinct qualified bodies");
        var before = memoryHashes();
        Map<String,Object> result = new LinkedHashMap<>();
        result.put("program_sha256", identity); result.put("memory_before", before);
        result.put("instruction_count_before", currentProgram.getListing().getNumInstructions());
        result.put("functions_before", currentProgram.getFunctionManager().getFunctionCount());
        result.put("enumerated_before", enumeratedFunctions());
        List<Map<String,Object>> observations = new ArrayList<>();
        for (var item : specs.entrySet()) {
            long start = item.getKey(), end = Long.decode(item.getValue().get("end").getAsString());
            var spec = item.getValue(); String name = spec.get("name").getAsString();
            if (start < 0x42000020L || end > 0x420b29d4L || end <= start || end-start > 4096 ||
                !name.matches("[A-Za-z_][A-Za-z_0-9]*")) throw new IllegalArgumentException("Invalid timer extent");
            Address entry = toAddr(start), last = toAddr(end-1);
            byte[] data = new byte[Math.toIntExact(end-start)];
            if (currentProgram.getMemory().getBytes(entry, data) != data.length ||
                !digest(data).equals(spec.get("factory_function_sha256").getAsString()))
                throw new IllegalArgumentException("Timer bytes differ");
            Function function = getFunctionAt(entry);
            Map<String,Object> row = new LinkedHashMap<>();
            row.put("name", name); row.put("start", spec.get("start").getAsString());
            row.put("end", spec.get("end").getAsString()); row.put("before", describe(function));
            int beforeCount = 0;
            var existingInstructions = currentProgram.getListing().getInstructions(new AddressSet(entry,last), true);
            while (existingInstructions.hasNext()) { existingInstructions.next(); beforeCount++; }
            row.put("instructions_in_range_before", beforeCount);
            int count = 0, createdInstructions = 0;
            for (Address pc = entry; pc.compareTo(last) <= 0;) {
                monitor.checkCancelled();
                Function owner = getFunctionContaining(pc);
                if (owner != null && !owner.getEntryPoint().equals(entry))
                    throw new IllegalStateException("Timer intersects another function");
                if (getInstructionAt(pc) == null) {
                    if (!disassemble(pc)) throw new IllegalStateException("Timer disassembly failed");
                    createdInstructions++;
                }
                var instruction = getInstructionAt(pc);
                if (instruction == null || instruction.getMaxAddress().compareTo(last) > 0)
                    throw new IllegalStateException("Timer instruction exceeds qualified body");
                pc = pc.add(instruction.getLength()); count++;
            }
            if (count != spec.get("linked_instruction_starts").getAsInt())
                throw new IllegalStateException("Independent instruction count differs");
            boolean created = function == null;
            if (created) function = currentProgram.getFunctionManager().createFunction(name, entry, new AddressSet(entry,last), SourceType.ANALYSIS);
            else {
                function.setBody(new AddressSet(entry,last));
                function.setName(name, SourceType.ANALYSIS);
            }
            row.put("created_function", created); row.put("decoded_instructions", count);
            row.put("disassemble_requests", createdInstructions); row.put("after", describe(function));
            observations.add(row);
        }
        var table = factory.getAsJsonObject("table");
        byte[] expected = HexFormat.of().parseHex(table.get("bytes_hex").getAsString());
        byte[] actual = new byte[expected.length];
        currentProgram.getMemory().getBytes(toAddr(Long.decode(table.get("address").getAsString())), actual);
        if (!java.util.Arrays.equals(actual,expected)) throw new IllegalStateException("Timer table bytes differ");
        List<Map<String,Object>> edges = new ArrayList<>();
        for (var item : table.getAsJsonArray("entries")) {
            var entry = item.getAsJsonObject(); long target = Long.decode(entry.get("target").getAsString());
            Function function = getFunctionAt(toAddr(target));
            if (function == null || !function.getName().equals(entry.get("name").getAsString()))
                throw new IllegalStateException("Callback table has no qualified owner");
            Map<String,Object> edge = new LinkedHashMap<>();
            edge.put("id", entry.get("id").getAsInt()); edge.put("cell", entry.get("cell").getAsString());
            edge.put("target", entry.get("target").getAsString()); edge.put("owner", describe(function));
            edges.add(edge);
        }
        var after = memoryHashes();
        if (!before.equals(after)) throw new IllegalStateException("Program bytes changed during recovery");
        result.put("memory_after", after); result.put("functions", observations); result.put("table_edges", edges);
        result.put("instruction_count_after", currentProgram.getListing().getNumInstructions());
        result.put("functions_after", currentProgram.getFunctionManager().getFunctionCount());
        result.put("enumerated_after", enumeratedFunctions());
        result.put("program_bytes_unchanged", true); result.put("whole_image_completeness_proved", false);
        Files.createDirectories(output.toAbsolutePath().getParent());
        Files.writeString(output, new GsonBuilder().setPrettyPrinting().create().toJson(result)+"\n", StandardCharsets.UTF_8);
        println("Recovered/renamed 21 qualified bodies and verified 14 callback owners; program bytes unchanged");
    }
}
