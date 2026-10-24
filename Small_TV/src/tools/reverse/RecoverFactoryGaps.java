// Reconstruct three byte-verified SDK functions in a disposable analysis session.
// @category SmallTV.Analysis
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.SourceType;
import com.google.gson.GsonBuilder;
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

public class RecoverFactoryGaps extends GhidraScript {
    // Hash initialized bytes only; analysis metadata may change, code/data may not.
    private Map<String,String> memoryHashes() throws Exception {
        Map<String,String> result=new LinkedHashMap<>();
        for(var block:currentProgram.getMemory().getBlocks()) {
            if(!block.isInitialized())continue;
            byte[] bytes=new byte[Math.toIntExact(block.getSize())];
            if(currentProgram.getMemory().getBytes(block.getStart(),bytes)!=bytes.length)
                throw new IllegalStateException("Incomplete memory read");
            result.put(block.getName(),HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes)));
        }
        return result;
    }

    // Record caller ownership/ranges without assuming the preceding prologue owns it.
    private Map<String,Object> owner(Address address) {
        Map<String,Object> row=new LinkedHashMap<>();Function function=getFunctionContaining(address);
        if(function!=null) {
            row.put("entry",String.format("0x%08x",function.getEntryPoint().getOffset()));
            row.put("name",function.getName());List<List<String>> ranges=new ArrayList<>();
            var iterator=function.getBody().getAddressRanges();
            while(iterator.hasNext()) {
                var range=iterator.next();ranges.add(List.of(String.format("0x%08x",range.getMinAddress().getOffset()),
                    String.format("0x%08x",range.getMaxAddress().getOffset())));
            }
            row.put("ranges",ranges);
        }
        return row;
    }

    @Override
    public void run() throws Exception {
        // Use only a copied project and headless -readOnly: metadata changes are discarded.
        String[] args=getScriptArgs();if(args.length!=2)throw new IllegalArgumentException("Expected match JSON and new output path");
        Path output=Path.of(args[1]);if(Files.exists(output))throw new IllegalArgumentException("Preserve evidence");
        var input=JsonParser.parseString(Files.readString(Path.of(args[0]),StandardCharsets.UTF_8)).getAsJsonObject();
        if(!input.get("factory_elf_sha256").getAsString().equals(currentProgram.getExecutableSHA256()) ||
            !input.get("passed").getAsBoolean() || input.getAsJsonArray("functions").size()!=3)
            throw new IllegalArgumentException("Unverified function match input");
        Map<String,Object> result=new LinkedHashMap<>();Map<String,String> before=memoryHashes();
        result.put("program_sha256",currentProgram.getExecutableSHA256());result.put("memory_before",before);
        result.put("instruction_count_before",currentProgram.getListing().getNumInstructions());
        result.put("functions_before",currentProgram.getFunctionManager().getFunctionCount());
        List<Map<String,Object>> observations=new ArrayList<>();
        for(var item:input.getAsJsonArray("functions")) {
            var spec=item.getAsJsonObject();long start=Long.decode(spec.get("start").getAsString());
            long end=Long.decode(spec.get("end").getAsString());String name=spec.get("name").getAsString();
            if(start<0x42000020L || end>0x420b29d4L || end<=start || end-start>4096 || !name.matches("[A-Za-z_][A-Za-z_0-9]*"))
                throw new IllegalArgumentException("Function bounds/name outside this recovery");
            Address entry=toAddr(start),last=toAddr(end-1),site=toAddr(Long.decode(spec.get("site").getAsString()));
            if(getFunctionContaining(entry)!=null || getFunctionContaining(site)!=null)
                throw new IllegalStateException("Expected the original missing-function state");
            byte[] bytes=new byte[Math.toIntExact(end-start)];currentProgram.getMemory().getBytes(entry,bytes);
            if(!HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes)).equals(spec.get("factory_function_sha256").getAsString()))
                throw new IllegalArgumentException("Function bytes differ from the verified match");
            Map<String,Object> row=new LinkedHashMap<>();row.put("name",name);row.put("start",spec.get("start").getAsString());
            row.put("end",spec.get("end").getAsString());row.put("site",spec.get("site").getAsString());
            row.put("caller_site",spec.get("caller_site").getAsString());
            row.put("caller_owner",owner(toAddr(Long.decode(spec.get("caller_site").getAsString()))));
            int count=0;
            for(Address pc=entry;pc.compareTo(last)<=0;) {
                if(getInstructionAt(pc)==null && !disassemble(pc))throw new IllegalStateException("Disassembly failed");
                var instruction=getInstructionAt(pc);if(instruction==null || instruction.getMaxAddress().compareTo(last)>0)
                    throw new IllegalStateException("Instruction exceeds matched SDK function");
                pc=pc.add(instruction.getLength());count++;
            }
            Function function=currentProgram.getFunctionManager().createFunction(name,entry,new AddressSet(entry,last),SourceType.ANALYSIS);
            if(function==null || !function.equals(getFunctionContaining(site)))throw new IllegalStateException("Recovered ownership failed");
            row.put("decoded_instructions",count);row.put("recovered_owner",owner(site));observations.add(row);
        }
        Map<String,String> after=memoryHashes();if(!before.equals(after))throw new IllegalStateException("Analysis changed program bytes");
        result.put("memory_after",after);result.put("functions",observations);
        result.put("functions_after",currentProgram.getFunctionManager().getFunctionCount());
        result.put("instruction_count_after",currentProgram.getListing().getNumInstructions());
        result.put("program_bytes_unchanged",true);result.put("whole_image_completeness_proved",false);
        Files.createDirectories(output.toAbsolutePath().getParent());
        Files.writeString(output,new GsonBuilder().setPrettyPrinting().create().toJson(result)+"\n",StandardCharsets.UTF_8);
        println("Recovered three matched SDK bodies in transient analysis; all program bytes unchanged");
    }
}
