// Recover complete SDK byte matches without stealing another function's body.
import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.SourceType;
import com.google.gson.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

public class RecoverMatchedFunctions extends GhidraScript {
    private String digest(byte[] bytes) throws Exception {
        return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
    }

    private Map<String,String> memoryHashes() throws Exception {
        Map<String,String> hashes=new LinkedHashMap<>();
        for (var block:currentProgram.getMemory().getBlocks()) {
            if (!block.isInitialized()) continue;
            byte[] bytes=new byte[Math.toIntExact(block.getSize())];
            if (currentProgram.getMemory().getBytes(block.getStart(),bytes)!=bytes.length)
                throw new IllegalStateException("Incomplete initialized memory");
            hashes.put(block.getName(),digest(bytes));
        }
        return hashes;
    }

    @Override public void run() throws Exception {
        String[] args=getScriptArgs();
        if (args.length!=2) throw new IllegalArgumentException("match-manifest new-report.json");
        Path output=Path.of(args[1]);
        if (Files.exists(output)) throw new IllegalArgumentException("Preserve recovery evidence");
        JsonObject manifest=JsonParser.parseString(Files.readString(Path.of(args[0]))).getAsJsonObject();
        if (!"small-tv-wifi-gap-matches-v1".equals(manifest.get("schema").getAsString()) ||
            !"8c9fd166a6536bc1bc236fc98018eb0daba9aad01ce8356511ad68eba03de882".equals(currentProgram.getExecutableSHA256()) ||
            !currentProgram.getExecutableSHA256().equals(manifest.get("factory_elf_sha256").getAsString()))
            throw new IllegalArgumentException("Unexpected factory match manifest");
        Map<String,String> before=memoryHashes();
        List<Map<String,Object>> rows=new ArrayList<>();
        int created=0;
        for (JsonElement element:manifest.getAsJsonArray("functions")) {
            monitor.checkCancelled();
            JsonObject spec=element.getAsJsonObject();
            long start=Long.decode(spec.get("start").getAsString()),end=Long.decode(spec.get("end").getAsString());
            if (end<=start || end-start>4096) throw new IllegalArgumentException("Unbounded matched function");
            Address entry=toAddr(start),last=toAddr(end-1);
            var block=currentProgram.getMemory().getBlock(entry);
            if (block==null || !block.isInitialized() || !block.isExecute() || !block.contains(last))
                throw new IllegalArgumentException("Matched function outside executable block");
            byte[] bytes=new byte[(int)(end-start)];
            currentProgram.getMemory().getBytes(entry,bytes);
            if (!digest(bytes).equals(spec.get("code_sha256").getAsString()))
                throw new IllegalArgumentException("Matched function bytes changed");
            Map<String,Object> row=new LinkedHashMap<>();
            row.put("start",spec.get("start").getAsString());row.put("end",spec.get("end").getAsString());
            row.put("sdk_name_candidate",spec.get("name").getAsString());
            AddressSet range=new AddressSet(entry,last);
            boolean overlap=false;
            AddressIterator addresses=range.getAddresses(true);
            while (addresses.hasNext())
                if (getFunctionContaining(addresses.next())!=null) {overlap=true;break;}
            if (overlap) {
                row.put("status","preserved-existing-function-overlap");
            } else {
                // The full source-to-linked matcher already established every
                // byte boundary. Ghidra may have treated this region as data.
                currentProgram.getListing().clearCodeUnits(entry,last,false,monitor);
                if (!new DisassembleCommand(entry,range,true).applyTo(currentProgram,monitor))
                    throw new IllegalStateException("Matched body could not be disassembled");
                String name="sdk_candidate_"+spec.get("name").getAsString().replaceAll("[^A-Za-z0-9_]","_")+"_"+Long.toHexString(start);
                Function function=currentProgram.getFunctionManager().createFunction(name,entry,range,SourceType.ANALYSIS);
                row.put("status","created");row.put("name",function.getName());created++;
            }
            rows.add(row);
        }
        // Independently decode all 32 hardware-vector jumps. They are vector
        // table slots, not 32 invented C functions. Retain the shared ISR entry.
        List<Map<String,Object>> vectors=new ArrayList<>();
        for (int slot=0;slot<32;slot++) {
            Address entry=toAddr(0x40380000L+4*slot);
            byte[] bytes=new byte[4];currentProgram.getMemory().getBytes(entry,bytes);
            int word=(bytes[0]&255)|((bytes[1]&255)<<8)|((bytes[2]&255)<<16)|((bytes[3]&255)<<24);
            if ((word&0xfff)!=0x6f) throw new IllegalStateException("Unexpected vector-table opcode");
            int immediate=((word>>>31)<<20)|(((word>>>12)&255)<<12)|(((word>>>20)&1)<<11)|(((word>>>21)&1023)<<1);
            int displacement=(immediate<<11)>>11;
            long target=entry.getOffset()+displacement;
            if (target!=0x40380102L && target!=0x403801d8L) throw new IllegalStateException("Unexpected vector target");
            AddressSet range=new AddressSet(entry,entry.add(3));
            if (getInstructionAt(entry)==null && !new DisassembleCommand(entry,range,false).applyTo(currentProgram,monitor))
                throw new IllegalStateException("Vector disassembly failed");
            Map<String,Object> row=new LinkedHashMap<>();row.put("slot",slot);row.put("target",String.format("0x%08x",target));vectors.add(row);
        }
        Address isr=toAddr(0x403801d8L);
        if (getFunctionAt(isr)==null && getFunctionContaining(isr)==null) {
            disassemble(isr);
            if (createFunction(isr,"hardware_interrupt_entry_at_403801d8")==null)
                throw new IllegalStateException("Hardware ISR entry recovery failed");
        }
        Map<String,String> after=memoryHashes();
        if (!before.equals(after)) throw new IllegalStateException("Metadata recovery changed firmware bytes");
        Map<String,Object> result=new LinkedHashMap<>();
        result.put("schema","small-tv-matched-function-recovery-v1");result.put("created_sdk_functions",created);
        result.put("functions",rows);result.put("vector_slots",vectors);result.put("memory_before",before);
        result.put("memory_after",after);result.put("program_bytes_unchanged",true);
        result.put("all_sdk_names_independently_proved",false);result.put("whole_image_completeness_proved",false);
        Files.writeString(output,new GsonBuilder().setPrettyPrinting().create().toJson(result)+"\n",StandardCharsets.UTF_8);
        println("Recovered "+created+" complete SDK function candidates and the hardware vector entries");
    }
}
