// Recover only object-qualified runtime bodies in a disposable read-only project.
// @category SmallTV.Analysis
import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.disassemble.DisassembleCommand;
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

public class RecoverFactoryRuntime extends GhidraScript {
    // The prepared ELF's executable hash binds all addresses to one factory image.
    private static final String FACTORY = "8c9fd166a6536bc1bc236fc98018eb0daba9aad01ce8356511ad68eba03de882";

    // Use numeric guest addresses independent of Ghidra's namespace display settings.
    private String hex(long value) { return String.format("0x%08x", value); }

    // Hash complete initialized blocks before and after metadata-only changes.
    private Map<String,String> memoryHashes() throws Exception {
        Map<String,String> result = new LinkedHashMap<>();
        for (var block : currentProgram.getMemory().getBlocks()) {
            if (!block.isInitialized()) continue;
            byte[] bytes = new byte[Math.toIntExact(block.getSize())];
            if (currentProgram.getMemory().getBytes(block.getStart(), bytes) != bytes.length)
                throw new IllegalStateException("Incomplete initialized block");
            result.put(block.getName(), digest(bytes));
        }
        return result;
    }

    // Match raw code identity independently of Ghidra's function or instruction metadata.
    private String digest(byte[] bytes) throws Exception {
        return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
    }

    // Preserve every old range so that trimming cannot hide unqualified instructions.
    private Map<String,Object> describe(Function function) {
        Map<String,Object> row = new LinkedHashMap<>();
        if (function == null) return row;
        row.put("entry", hex(function.getEntryPoint().getOffset()));
        row.put("name", function.getName()); row.put("body_bytes", function.getBody().getNumAddresses());
        List<List<String>> ranges = new ArrayList<>();
        var iterator = function.getBody().getAddressRanges();
        while (iterator.hasNext()) {
            var range = iterator.next();
            ranges.add(List.of(hex(range.getMinAddress().getOffset()), hex(range.getMaxAddress().getOffset())));
        }
        row.put("ranges", ranges); return row;
    }

    // Enumerate both byte boundaries and instruction references without creating new ones.
    private List<Map<String,Object>> instructions(long start, long end) throws Exception {
        List<Map<String,Object>> rows = new ArrayList<>();
        for (long pc = start; pc < end;) {
            var instruction = getInstructionAt(toAddr(pc));
            if (instruction == null || instruction.getMaxAddress().getOffset() >= end)
                throw new IllegalStateException("Incomplete qualified disassembly");
            Map<String,Object> row = new LinkedHashMap<>();
            row.put("pc", hex(pc)); row.put("bytes", HexFormat.of().formatHex(instruction.getBytes()));
            row.put("mnemonic", instruction.getMnemonicString());
            List<Map<String,Object>> refs = new ArrayList<>();
            for (var ref : instruction.getReferencesFrom()) {
                Map<String,Object> edge = new LinkedHashMap<>();
                edge.put("target", ref.getToAddress().toString());
                edge.put("offset", ref.getToAddress().getOffset());
                edge.put("space", ref.getToAddress().getAddressSpace().getName());
                edge.put("type", ref.getReferenceType().toString());
                edge.put("source", ref.getSource().toString()); edge.put("operand",ref.getOperandIndex()); refs.add(edge);
            }
            row.put("references", refs); rows.add(row); pc += instruction.getLength();
        }
        return rows;
    }

    @Override
    public void run() throws Exception {
        // Invoke only with -readOnly -noanalysis on a copy; no project saves or byte patches.
        String[] args = getScriptArgs();
        if (args.length != 2) throw new IllegalArgumentException("Expected manifest and new JSON output");
        Path output = Path.of(args[1]);
        if (Files.exists(output)) throw new IllegalArgumentException("Preserve existing evidence");
        var input = JsonParser.parseString(Files.readString(Path.of(args[0]))).getAsJsonObject();
        if (!FACTORY.equals(currentProgram.getExecutableSHA256()) ||
            !FACTORY.equals(input.get("factory_elf_sha256").getAsString()) ||
            !input.get("schema").getAsString().equals("factory-runtime-metadata-manifest-v1") ||
            input.getAsJsonArray("functions").size() != 10)
            throw new IllegalArgumentException("Unqualified factory runtime input");
        Map<Long,JsonObject> specs = new java.util.TreeMap<>();
        Map<Long,Map<String,Object>> old = new LinkedHashMap<>();
        for (var item : input.getAsJsonArray("functions")) {
            var spec = item.getAsJsonObject(); long start = Long.decode(spec.get("start").getAsString());
            long end = Long.decode(spec.get("end").getAsString());
            if (end <= start || end-start > 1024 || specs.put(start,spec) != null ||
                !(start == 0x40380102L || (start >= 0x420a3a0aL && end <= 0x420a4000L)))
                throw new IllegalArgumentException("Invalid or duplicate runtime extent");
            byte[] bytes = new byte[Math.toIntExact(end-start)];
            if (currentProgram.getMemory().getBytes(toAddr(start),bytes) != bytes.length ||
                !digest(bytes).equals(spec.get("code_sha256").getAsString()))
                throw new IllegalArgumentException("Qualified body bytes differ");
            old.put(start,describe(getFunctionAt(toAddr(start))));
        }
        var before = memoryHashes(); Map<String,Object> result = new LinkedHashMap<>();
        result.put("schema", "factory-runtime-metadata-recovery-v1");
        result.put("program_sha256", FACTORY); result.put("memory_before", before);
        result.put("function_count_before", currentProgram.getFunctionManager().getFunctionCount());
        result.put("instruction_count_before", currentProgram.getListing().getNumInstructions());
        List<String> instructionStartsBefore = new ArrayList<>();
        for (var spec : specs.values()) {
            long start = Long.decode(spec.get("start").getAsString());
            long end = Long.decode(spec.get("end").getAsString());
            var iterator = currentProgram.getListing().getInstructions(new AddressSet(toAddr(start),toAddr(end-1)),true);
            while (iterator.hasNext()) instructionStartsBefore.add(hex(iterator.next().getAddress().getOffset()));
        }
        result.put("instruction_starts_before",instructionStartsBefore);
        // Split only the two already observed overlong bodies. Preserve their detached bytes below.
        for (long start : new long[]{0x420a3da2L,0x420a3fc8L}) {
            Function function = getFunctionAt(toAddr(start));
            long originalEnd = start == 0x420a3da2L ? 0x420a3e0aL : 0x420a3fe8L;
            AddressSet expected = new AddressSet(toAddr(start),toAddr(originalEnd-1));
            if (function == null || !function.getBody().hasSameAddresses(expected))
                throw new IllegalStateException("Unexpected original merged runtime body");
            long end = Long.decode(specs.get(start).get("end").getAsString());
            function.setBody(new AddressSet(toAddr(start),toAddr(end-1)));
        }
        List<Map<String,Object>> rows = new ArrayList<>();
        for (var item : specs.entrySet()) {
            long start = item.getKey(), end = Long.decode(item.getValue().get("end").getAsString());
            var spec = item.getValue(); var range = new AddressSet(toAddr(start),toAddr(end-1));
            Function function = getFunctionAt(toAddr(start));
            if (function != null && !range.contains(function.getBody()))
                throw new IllegalStateException("Unqualified bytes would be detached");
            for (long pc = start; pc < end; pc++) {
                Function owner = getFunctionContaining(toAddr(pc));
                if (owner != null && !owner.equals(function)) throw new IllegalStateException("Different function overlaps runtime body");
            }
            // Restrict flow discovery to these qualified bytes; callees are not recursively decoded.
            var command = new DisassembleCommand(toAddr(start),range,true);
            if (!command.applyTo(currentProgram,monitor)) throw new IllegalStateException("Restricted disassembly failed");
            // A disconnected C++ landing pad is intentionally not reachable from the normal entry.
            for (var instruction : spec.getAsJsonArray("instructions")) {
                long pc = Long.decode(instruction.getAsJsonObject().get("pc").getAsString());
                if (pc < start || pc >= end) throw new IllegalArgumentException("Instruction outside body");
                if (getInstructionAt(toAddr(pc)) == null &&
                    !new DisassembleCommand(toAddr(pc),range,true).applyTo(currentProgram,monitor))
                    throw new IllegalStateException("Landing pad disassembly failed");
            }
            String name = spec.get("name").getAsString();
            if (!name.matches("[A-Za-z_][A-Za-z_0-9]*")) throw new IllegalArgumentException("Invalid runtime name");
            boolean created = function == null;
            if (created) function = currentProgram.getFunctionManager().createFunction(name,toAddr(start),range,SourceType.ANALYSIS);
            else { function.setBody(range); function.setName(name,SourceType.ANALYSIS); }
            Map<String,Object> row = new LinkedHashMap<>(); row.put("before",old.get(start));
            row.put("after",describe(function)); row.put("created_function",created);
            row.put("instructions",instructions(start,end)); rows.add(row);
        }
        List<Map<String,Object>> detached = new ArrayList<>();
        // These ten bytes stay decoded and explicitly unowned, not silently assigned a guessed SDK name.
        for (long[] range : new long[][]{{0x420a3e08L,0x420a3e0aL},{0x420a3fe0L,0x420a3fe8L}}) {
            for (long pc=range[0];pc<range[1];pc++)
                if (getFunctionContaining(toAddr(pc)) != null) throw new IllegalStateException("Detached bytes acquired an owner");
            Map<String,Object> row = new LinkedHashMap<>();
            row.put("start",hex(range[0])); row.put("end",hex(range[1]));
            row.put("instructions",instructions(range[0],range[1])); row.put("owner",Map.of()); detached.add(row);
        }
        var after = memoryHashes();
        if (!before.equals(after)) throw new IllegalStateException("Runtime recovery changed program bytes");
        result.put("functions",rows); result.put("detached",detached); result.put("memory_after",after);
        result.put("function_count_after",currentProgram.getFunctionManager().getFunctionCount());
        result.put("instruction_count_after",currentProgram.getListing().getNumInstructions());
        result.put("program_bytes_unchanged",true); result.put("whole_image_completeness_proved",false);
        Files.createDirectories(output.toAbsolutePath().getParent());
        Files.writeString(output,new GsonBuilder().setPrettyPrinting().create().toJson(result)+"\n",StandardCharsets.UTF_8);
        println("Recovered ten qualified runtime bodies; retained ten detached bytes explicitly unowned");
    }
}
