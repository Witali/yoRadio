// Export every recognized factory function and account for unresolved code.
// Run only on a private copy of the analyzed factory application project.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.SourceType;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;

public class ExportAllFunctions extends GhidraScript {
    private final Gson gson = new GsonBuilder().disableHtmlEscaping().create();

    private Map<String,Object> row(Object... pairs) {
        Map<String,Object> result = new LinkedHashMap<>();
        for (int i=0; i<pairs.length; i+=2) result.put((String)pairs[i], pairs[i+1]);
        return result;
    }

    private String digest(byte[] data) throws Exception {
        StringBuilder result = new StringBuilder();
        for (byte b:MessageDigest.getInstance("SHA-256").digest(data)) result.append(String.format("%02x", b&255));
        return result.toString();
    }

    private PrintWriter writer(File dir, String name) throws Exception {
        return new PrintWriter(new File(dir,name), StandardCharsets.UTF_8);
    }

    private AddressSet executable() {
        AddressSet result = new AddressSet();
        for (MemoryBlock block:currentProgram.getMemory().getBlocks())
            if (block.isInitialized() && block.isExecute()) result.add(block.getStart(),block.getEnd());
        return result;
    }

    private List<Map<String,Object>> recoverEntries(AddressSet exec, File known) throws Exception {
        FunctionManager manager = currentProgram.getFunctionManager();
        List<Map<String,Object>> result = new ArrayList<>();
        if (known != null) {
            for (String line:Files.readAllLines(known.toPath(),StandardCharsets.UTF_8)) {
                if (line.isBlank()) continue;
                String[] fields=line.split("\t",2);
                Address address=toAddr(fields[0]);
                if (!exec.contains(address)) continue;
                Function function=manager.getFunctionAt(address);
                if (function == null && manager.getFunctionContaining(address) == null) {
                    disassemble(address);
                    function=createFunction(address,null);
                }
                if (function != null && (function.getName().startsWith("FUN_") || function.getName().equals(fields[1])))
                    function.setName(fields[1],SourceType.ANALYSIS);
                result.add(row("source","reviewed-symbol-map","address",address.toString(),
                    "function_at_entry",function != null,"requested_name",fields[1]));
            }
        }
        for (int pass=0; pass<3; pass++) {
            Set<Address> candidates=new TreeSet<>();
            InstructionIterator instructions=currentProgram.getListing().getInstructions(exec,true);
            while (instructions.hasNext()) {
                Instruction instruction=instructions.next();
                if (!instruction.getFlowType().isCall() || instruction.getFlowType().isComputed()) continue;
                for (Address target:instruction.getFlows())
                    if (exec.contains(target) && manager.getFunctionAt(target)==null && manager.getFunctionContaining(target)==null)
                        candidates.add(target);
            }
            int created=0;
            for (Address target:candidates) {
                monitor.checkCancelled();
                disassemble(target);
                Function function=createFunction(target,null);
                if (function != null) created++;
                result.add(row("source","direct-call","pass",pass,"address",target.toString(),"created",function!=null));
            }
            if (created==0) break;
            analyzeChanges(currentProgram);
        }
        return result;
    }

    @Override public void run() throws Exception {
        String[] args=getScriptArgs();
        if (args.length<1 || args.length>3) throw new IllegalArgumentException("output-directory [reviewed-address-name.tsv [expected-elf-sha256]]");
        File dir=new File(args[0]);
        if (dir.exists()) throw new IOException("Preserve existing export directory");
        if (!dir.mkdirs()) throw new IOException("Cannot create export directory");
        String expected=args.length==3?args[2]:"8c9fd166a6536bc1bc236fc98018eb0daba9aad01ce8356511ad68eba03de882";
        if (!expected.matches("[0-9a-f]{64}") || !expected.equals(currentProgram.getExecutableSHA256()))
            throw new IOException("Unexpected factory application ELF");
        AddressSet exec=executable();
        List<Map<String,Object>> recovered=recoverEntries(exec,args.length>=2?new File(args[1]):null);
        AddressSet instructionBytes=new AddressSet(),functionBytes=new AddressSet();
        long instructionCount=0,computedFlows=0;
        try (PrintWriter assembly=writer(dir,"instructions.asm"); PrintWriter indirect=writer(dir,"computed-flows.jsonl")) {
            InstructionIterator instructions=currentProgram.getListing().getInstructions(exec,true);
            while (instructions.hasNext()) {
                monitor.checkCancelled();
                Instruction instruction=instructions.next();
                instructionBytes.add(instruction.getMinAddress(),instruction.getMaxAddress());
                byte[] bytes=instruction.getBytes();
                StringBuilder hex=new StringBuilder();
                for (byte b:bytes) hex.append(String.format("%02x",b&255));
                assembly.printf("%s: %s %s%n",instruction.getAddress(),hex,instruction);
                instructionCount++;
                if (instruction.getFlowType().isComputed()) {
                    Function owner=currentProgram.getFunctionManager().getFunctionContaining(instruction.getAddress());
                    List<String> flows=new ArrayList<>();
                    for (Address a:instruction.getFlows()) flows.add(a.toString());
                    indirect.println(gson.toJson(row("address",instruction.getAddress().toString(),
                        "owner",owner==null?null:owner.getEntryPoint().toString(),"instruction",instruction.toString(),
                        "kind",instruction.getFlowType().toString(),"resolved_flows",flows)));
                    computedFlows++;
                }
            }
        }
        int total=0,completed=0,failed=0,external=0,withWarnings=0;
        List<Map<String,Object>> failures=new ArrayList<>();
        DecompInterface decompiler=new DecompInterface();
        if (!decompiler.openProgram(currentProgram)) throw new IOException("Decompiler initialization failed");
        try (PrintWriter code=writer(dir,"all-functions.c"); PrintWriter index=writer(dir,"functions.jsonl")) {
            code.println("/* Ghidra pseudocode from the factory application. Not original source, not buildable C. */");
            FunctionIterator functions=currentProgram.getFunctionManager().getFunctions(true);
            while (functions.hasNext()) {
                monitor.checkCancelled();
                Function function=functions.next();
                if (function.isExternal()) {external++;continue;}
                if (!exec.contains(function.getEntryPoint())) continue;
                total++;
                functionBytes.add(function.getBody().intersect(exec));
                DecompileResults result=decompiler.decompileFunction(function,30,monitor);
                boolean retried=false;
                if (!result.decompileCompleted()) {
                    retried=true;
                    decompiler.flushCache();
                    result=decompiler.decompileFunction(function,120,monitor);
                }
                boolean success=result.decompileCompleted() && result.getDecompiledFunction()!=null;
                String text=success?result.getDecompiledFunction().getC():"";
                String error=result.getErrorMessage();
                if (error==null) error="";
                boolean warnings=!error.isBlank() || text.contains("WARNING:");
                if (success) completed++; else failed++;
                if (warnings) withWarnings++;
                Map<String,Object> metadata=row("address",function.getEntryPoint().toString(),
                    "name",function.getName(),"body_bytes",function.getBody().getNumAddresses(),
                    "completed",success,"retried",retried,"warnings",warnings,
                    "error",error,"pseudocode_sha256",digest(text.getBytes(StandardCharsets.UTF_8)));
                index.println(gson.toJson(metadata));
                if (!success) failures.add(metadata);
                code.printf("%n/* ENTRY %s %s BODY_BYTES %d COMPLETED %s */%n",function.getEntryPoint(),
                    function.getName(),function.getBody().getNumAddresses(),success);
                if (success) code.println(text); else code.println("/* Decompilation failed; see functions.jsonl. */");
                if (total%100==0) {
                    code.flush(); index.flush();
                    println("Factory export: "+total+" functions, "+completed+" completed, "+failed+" failed");
                }
            }
        } finally { decompiler.dispose(); }
        AddressSet undecoded=new AddressSet(exec);undecoded.delete(instructionBytes);
        AddressSet unowned=instructionBytes.subtract(functionBytes);
        try (PrintWriter gaps=writer(dir,"code-gaps.jsonl")) {
            for (String kind:new String[]{"undecoded-executable","instructions-without-function"}) {
                AddressRangeIterator ranges=(kind.equals("undecoded-executable")?undecoded:unowned).getAddressRanges();
                while (ranges.hasNext()) {
                    AddressRange range=ranges.next();
                    gaps.println(gson.toJson(row("kind",kind,"start",range.getMinAddress().toString(),
                        "end",range.getMaxAddress().toString(),"bytes",range.getLength())));
                }
            }
        }
        List<Map<String,Object>> blocks=new ArrayList<>();
        for (MemoryBlock block:currentProgram.getMemory().getBlocks())
            blocks.add(row("name",block.getName(),"start",block.getStart().toString(),"bytes",block.getSize(),
                "initialized",block.isInitialized(),"execute",block.isExecute()));
        Map<String,Object> report=row("schema","small-tv-full-decompilation-v1","program_sha256",currentProgram.getExecutableSHA256(),
            "language",currentProgram.getLanguageID().toString(),"functions_attempted",total,"completed",completed,"failed",failed,
            "external_functions_skipped",external,"functions_with_warnings",withWarnings,"instruction_count",instructionCount,
            "executable_bytes",exec.getNumAddresses(),"decoded_instruction_bytes",instructionBytes.getNumAddresses(),
            "function_body_bytes",functionBytes.getNumAddresses(),"undecoded_executable_bytes",undecoded.getNumAddresses(),
            "instruction_bytes_without_function",unowned.getNumAddresses(),"computed_flow_sites",computedFlows,
            "memory_blocks",blocks,"entry_recovery",recovered,"failures",failures,
            "whole_image_completeness_proved",false,"semantic_equivalence_proved",false,"physical_hardware_tested",false);
        Files.writeString(new File(dir,"report.json").toPath(),new GsonBuilder().setPrettyPrinting().create().toJson(report)+"\n",StandardCharsets.UTF_8);
        println("Factory export complete: "+completed+"/"+total+" functions; undecoded executable bytes "+undecoded.getNumAddresses());
    }
}
