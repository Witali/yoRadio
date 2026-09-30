// Export memory-relevant AAC functions from a linked ESP32-C3 ELF.
// Run with Ghidra analyzeHeadless; arguments: output-directory [function-regex|@archive-symbols.txt].
// The @file form follows direct calls from AAC entry points within archive symbols.
// Output is pseudocode (trailing whitespace removed), not recovered/compilable source.
// @category YoRadio.Analysis

import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import com.google.gson.GsonBuilder;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.ArrayDeque;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.regex.Pattern;

public class DecompileAacMemory extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 1 || args.length > 2) {
            throw new IllegalArgumentException("output-directory [function-regex|@archive-symbols.txt]");
        }
        Path output = Path.of(args[0]);
        Files.createDirectories(output);
        if (!currentProgram.getLanguageID().toString().equals("RISCV:LE:32:default")) {
            throw new IllegalArgumentException("Import with -processor RISCV:LE:32:default");
        }
        String selection = args.length == 2 ? args[1] :
            "(?i).*(sbr|pvmp4|aac_dec).*|ps_.*|imdct_fxp|trans4m_.*|" +
            "envelope_application.*|energy_estimation.*|long_term_.*|apply_tns|get_dse|" +
            "get_adif_header|get_prog_config";
        HashSet<Function> selected = new HashSet<>();
        FunctionIterator candidates = currentProgram.getFunctionManager().getFunctions(true);
        if (selection.startsWith("@")) {
            HashSet<String> allowed = new HashSet<>(Files.readAllLines(Path.of(selection.substring(1))));
            HashSet<String> roots = new HashSet<>(java.util.List.of("esp_aac_dec_open",
                "esp_aac_dec_decode", "esp_aac_dec_close", "esp_aac_dec_reset",
                "esp_aac_dec_register", "esp_aac_dec_parse_frame"));
            ArrayDeque<Function> pending = new ArrayDeque<>();
            while (candidates.hasNext()) {
                Function function = candidates.next();
                if (roots.remove(function.getName())) pending.add(function);
            }
            if (!roots.isEmpty()) throw new IllegalStateException("Missing AAC roots: " + roots);
            while (!pending.isEmpty()) {
                Function function = pending.removeFirst();
                if (!selected.add(function)) continue;
                for (Function target : function.getCalledFunctions(monitor)) {
                    if (allowed.contains(target.getName())) pending.add(target);
                }
            }
        } else {
            Pattern names = Pattern.compile(selection);
            while (candidates.hasNext()) {
                Function function = candidates.next();
                if (names.matcher(function.getName()).matches()) selected.add(function);
            }
        }
        DecompInterface decompiler = new DecompInterface();
        if (!decompiler.openProgram(currentProgram)) {
            throw new IllegalStateException(decompiler.getLastMessage());
        }
        ArrayList<Map<String, Object>> entries = new ArrayList<>();
        int failed = 0;
        try {
            FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);
            while (functions.hasNext()) {
                monitor.checkCancelled();
                Function function = functions.next();
                if (!selected.contains(function)) continue;
                DecompileResults result = decompiler.decompileFunction(function, 90, monitor);
                LinkedHashMap<String, Object> entry = new LinkedHashMap<>();
                entry.put("name", function.getName());
                entry.put("address", function.getEntryPoint().toString());
                entry.put("body_bytes", function.getBody().getNumAddresses());
                entry.put("completed", result.decompileCompleted());
                entry.put("warning", result.getErrorMessage());
                ArrayList<String> calls = new ArrayList<>();
                for (Function target : function.getCalledFunctions(monitor)) {
                    calls.add(target.getName());
                }
                calls.sort(String::compareTo);
                entry.put("calls", calls);
                if (result.decompileCompleted()) {
                    String pseudocode = result.getDecompiledFunction().getC()
                        .replaceAll("(?m)[ \\t]+$", "").stripTrailing() + "\n";
                    entry.put("pseudocode_contains_warning", pseudocode.contains("WARNING:"));
                    String filename = function.getName().replaceAll("[^A-Za-z0-9_.-]", "_") + ".c";
                    String header = "/* Ghidra pseudocode; NOT original source.\n" +
                        " * ELF SHA-256: " + currentProgram.getExecutableSHA256() + "\n" +
                        " * Function: " + function.getName() + " @ " + function.getEntryPoint() +
                        "\n * Types and parameter counts are inferred; verify against disassembly. */\n";
                    Files.writeString(output.resolve(filename),
                        header + pseudocode, StandardCharsets.UTF_8);
                    entry.put("file", filename);
                } else {
                    failed++;
                }
                entries.add(entry);
            }
            LinkedHashMap<String, Object> manifest = new LinkedHashMap<>();
            manifest.put("program", currentProgram.getName());
            manifest.put("sha256", currentProgram.getExecutableSHA256());
            manifest.put("language", currentProgram.getLanguageID().toString());
            manifest.put("compiler", currentProgram.getCompilerSpec().getCompilerSpecID().toString());
            manifest.put("selection", selection);
            manifest.put("scope", "Direct-call graph only; inferred prototypes are not an ABI specification");
            manifest.put("functions", entries);
            Files.writeString(output.resolve("manifest.json"),
                new GsonBuilder().setPrettyPrinting().create().toJson(manifest) + "\n",
                StandardCharsets.UTF_8);
        } finally {
            decompiler.dispose();
        }
        println("AAC export: " + entries.size() + " functions; " + failed + " failures");
        if (entries.isEmpty() || failed != 0) {
            throw new IllegalStateException("Incomplete decompilation; inspect manifest.json");
        }
    }
}
