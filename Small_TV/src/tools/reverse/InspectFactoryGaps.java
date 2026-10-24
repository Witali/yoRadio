// Observe missing instruction sites without changing their analysis or bytes.
// @category SmallTV.Analysis
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import com.google.gson.GsonBuilder;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class InspectFactoryGaps extends GhidraScript {
    // Keep guest addresses separate from any non-memory namespace.
    private String address(Address value) {
        return value.getAddressSpace().isMemorySpace() ? String.format("0x%08x",value.getOffset()) : value.toString();
    }

    // Preserve incoming edges, including data pointers, without dumping data literals.
    private List<Map<String,Object>> references(Address target) throws Exception {
        List<Map<String,Object>> result=new ArrayList<>();
        var iterator=currentProgram.getReferenceManager().getReferencesTo(target);
        while (iterator.hasNext()) {
            var ref=iterator.next(); Map<String,Object> row=new LinkedHashMap<>();
            row.put("from",address(ref.getFromAddress())); row.put("type",ref.getReferenceType().toString());
            row.put("from_space",ref.getFromAddress().getAddressSpace().getName());
            var instruction=getInstructionAt(ref.getFromAddress());
            if (instruction!=null) row.put("bytes",HexFormat.of().formatHex(instruction.getBytes()));
            result.add(row);
        }
        return result;
    }

    // Export actual function ranges; a nearby prologue alone is not a boundary proof.
    private Map<String,Object> function(Function function) throws Exception {
        Map<String,Object> row=new LinkedHashMap<>();
        if (function==null) return row;
        row.put("entry",address(function.getEntryPoint())); row.put("name",function.getName());
        row.put("body_bytes",function.getBody().getNumAddresses());
        List<List<String>> ranges=new ArrayList<>();
        var iterator=function.getBody().getAddressRanges();
        while (iterator.hasNext()) {
            var range=iterator.next();ranges.add(List.of(address(range.getMinAddress()),address(range.getMaxAddress())));
        }
        row.put("ranges",ranges);row.put("references",references(function.getEntryPoint()));
        return row;
    }

    @Override
    public void run() throws Exception {
        // No disassembly, functions, symbols or memory are changed in this observer.
        String[] args=getScriptArgs();if(args.length!=1) throw new IllegalArgumentException("Expected new JSON path");
        Path output=Path.of(args[0]);if(Files.exists(output)) throw new IllegalArgumentException("Preserve evidence");
        Map<String,Object> result=new LinkedHashMap<>();
        result.put("schema_version",1);result.put("program_sha256",currentProgram.getExecutableSHA256());
        List<Map<String,Object>> sites=new ArrayList<>();
        for (long value:new long[]{0x42058280L,0x420662daL,0x420757d2L}) {
            Address target=toAddr(value);Map<String,Object> row=new LinkedHashMap<>();
            row.put("site",address(target));row.put("references",references(target));
            row.put("containing_function",function(getFunctionContaining(target)));
            var before=currentProgram.getFunctionManager().getFunctions(target,false);
            var after=currentProgram.getFunctionManager().getFunctions(target,true);
            row.put("previous_function",function(before.hasNext()?before.next():null));
            row.put("next_function",function(after.hasNext()?after.next():null));
            var unit=currentProgram.getListing().getCodeUnitContaining(target);
            if(unit!=null) {
                row.put("unit_start",address(unit.getMinAddress()));row.put("unit_bytes",unit.getLength());
                row.put("unit_class",unit.getClass().getSimpleName());
            }
            var data=currentProgram.getListing().getDefinedDataContaining(target);
            if(data!=null) row.put("data_type",data.getDataType().getName());
            List<Map<String,Object>> nearby=new ArrayList<>();
            var iterator=currentProgram.getListing().getInstructions(target.subtract(32),true);
            while(iterator.hasNext()) {
                Instruction instruction=iterator.next();if(instruction.getAddress().compareTo(target.add(48))>=0)break;
                Map<String,Object> item=new LinkedHashMap<>();item.put("pc",address(instruction.getAddress()));
                item.put("bytes",HexFormat.of().formatHex(instruction.getBytes()));
                item.put("mnemonic",instruction.getMnemonicString());nearby.add(item);
            }
            row.put("nearby_instructions",nearby);sites.add(row);
        }
        result.put("sites",sites);Files.createDirectories(output.toAbsolutePath().getParent());
        Files.writeString(output,new GsonBuilder().setPrettyPrinting().create().toJson(result)+"\n",StandardCharsets.UTF_8);
        println("Observed three missing GP sites without changing the program");
    }
}
