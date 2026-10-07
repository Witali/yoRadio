// Apply checked ABI types to a COPY of the AAC analysis program, then export it.
// Arguments: directory containing types.json, function inventory file
// @category YoRadio.Analysis
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.SourceType;
import com.google.gson.*;
import java.nio.file.*;
import java.util.*;

public class ApplyAacTypes extends GhidraScript {
    private final Map<String,DataType> imported = new HashMap<>();
    private final CategoryPath category = new CategoryPath("/AAC_RV32_DWARF");
    private JsonObject nodes, roots;
    private DataType build(String id) {
        if (imported.containsKey(id)) return imported.get(id);
        JsonObject n = nodes.getAsJsonObject(id);
        String kind = n.get("kind").getAsString(), name = n.get("name").getAsString();
        int bytes = n.get("bytes").getAsInt();
        if (name.isEmpty()) name = "anonymous_" + id;
        DataTypeManager manager = currentProgram.getDataTypeManager();
        DataType result;
        switch (kind) {
        case "structure_type":
            StructureDataType struct = new StructureDataType(category, name, bytes, manager);
            imported.put(id, struct);
            for (JsonElement element : n.getAsJsonArray("members")) {
                JsonObject m = element.getAsJsonObject();
                DataType t = build(m.get("type").getAsString());
                String label = m.get("name").getAsString();
                struct.replaceAtOffset(m.get("offset").getAsInt(), t, t.getLength(),
                    label.isEmpty() ? "layout" : label, null);
            }
            result = struct; break;
        case "union_type":
            UnionDataType union = new UnionDataType(category, name, manager);
            imported.put(id, union);
            for (JsonElement element : n.getAsJsonArray("members")) {
                JsonObject m = element.getAsJsonObject();
                DataType t = build(m.get("type").getAsString());
                String label = m.get("name").getAsString();
                union.add(t, t.getLength(), label.isEmpty() ? "layout" : label, null);
            }
            result = union; break;
        case "typedef":
            result = new TypedefDataType(category, name, build(n.get("type").getAsString()), manager); break;
        case "const_type": case "volatile_type":
            result = build(n.get("type").getAsString()); break;
        case "pointer_type":
            result = new PointerDataType(n.has("type") ? build(n.get("type").getAsString()) : VoidDataType.dataType, 4, manager); break;
        case "array_type":
            result = build(n.get("type").getAsString());
            JsonArray dims = n.getAsJsonArray("dimensions");
            for (int i = dims.size() - 1; i >= 0; --i)
                result = new ArrayDataType(result, dims.get(i).getAsInt(), result.getLength(), manager);
            break;
        case "base_type":
            int encoding = n.get("encoding").getAsInt();
            if (encoding != 5 && encoding != 6 && encoding != 7 && encoding != 8)
                throw new IllegalArgumentException("Unsupported base type: " + n);
            result = encoding == 5 || encoding == 6 ? AbstractIntegerDataType.getSignedDataType(bytes, manager) :
                AbstractIntegerDataType.getUnsignedDataType(bytes, manager); break;
        default: throw new IllegalArgumentException("Unsupported DWARF type: " + n);
        }
        if (result.getLength() != bytes) throw new IllegalStateException("DWARF size mismatch: " + n);
        imported.put(id, result);
        return result;
    }
    private DataType type(String name) { return build(roots.get(name).getAsString()); }
    private DataType pointed(String declaration) {
        String base = declaration.replace("*", "").trim();
        DataType t = type(base);
        for (char ch : declaration.toCharArray()) if (ch == '*')
            t = new PointerDataType(t, currentProgram.getDataTypeManager());
        return t;
    }
    @Override public void run() throws Exception {
        Path folder = Path.of(getScriptArgs()[0]);
        JsonObject meta = JsonParser.parseString(Files.readString(folder.resolve("types.json"))).getAsJsonObject();
        if (!currentProgram.getExecutableSHA256().equals(meta.get("elf_sha256").getAsString()) ||
            !currentProgram.getLanguageID().toString().equals("RISCV:LE:32:default"))
            throw new IllegalArgumentException("Wrong analysis ELF/architecture");
        nodes = meta.getAsJsonObject("nodes"); roots = meta.getAsJsonObject("roots");
        for (var entry : meta.getAsJsonObject("types").entrySet()) {
            DataType t = type(entry.getKey());
            JsonObject expected = entry.getValue().getAsJsonObject();
            if (t.getLength() != expected.get("bytes").getAsInt())
                throw new IllegalStateException("Size mismatch: " + entry.getKey() + " actual=" + t.getLength() +
                    " expected=" + expected.get("bytes") + " " + t);
            while (t instanceof TypeDef) t = ((TypeDef)t).getBaseDataType();
            Composite c = (Composite)t;
            for (JsonElement element : expected.getAsJsonArray("fields")) {
                JsonObject field = element.getAsJsonObject();
                String name = field.get("name").getAsString();
                boolean found = false;
                for (DataTypeComponent member : c.getComponents()) {
                    // The anonymous union/structure member is named "layout".
                    if (name.isEmpty() ? member.getOffset() == field.get("offset").getAsInt() &&
                                        member.getLength() == field.get("bytes").getAsInt()
                                       : name.equals(member.getFieldName())) {
                        if (member.getOffset() != field.get("offset").getAsInt() ||
                            member.getLength() != field.get("bytes").getAsInt())
                            throw new IllegalStateException("Field mismatch: " + entry.getKey() + "." + name);
                        found = true; break;
                    }
                }
                if (!found) throw new IllegalStateException("Missing field: " + entry.getKey() + "." + name);
            }
        }
        // Use native ELF symbols, never a hardcoded absolute data address.
        if (meta.has("data_symbols")) {
            for (var entry : meta.getAsJsonObject("data_symbols").entrySet()) {
                var symbols = currentProgram.getSymbolTable().getGlobalSymbols(entry.getKey());
                if (symbols.size() != 1) throw new IllegalStateException("Missing/ambiguous data symbol: " + entry.getKey());
                var address = symbols.get(0).getAddress();
                DataType dataType = type(entry.getValue().getAsString());
                byte[] before = new byte[dataType.getLength()], after = new byte[dataType.getLength()];
                if (currentProgram.getMemory().getBytes(address, before) != before.length)
                    throw new IllegalStateException("Incomplete table: " + entry.getKey());
                clearListing(address, address.add(before.length - 1));
                createData(address, dataType);
                currentProgram.getMemory().getBytes(address, after);
                if (!Arrays.equals(before, after)) throw new IllegalStateException("Table bytes changed");
            }
        }
        DecompInterface decompiler = new DecompInterface();
        if (!decompiler.openProgram(currentProgram)) throw new IllegalStateException(decompiler.getLastMessage());
        Map<Function,List<ParameterImpl>> changes = new LinkedHashMap<>();
        JsonObject assignments = meta.getAsJsonObject("parameters");
        Set<String> missing = new HashSet<>(assignments.keySet());
        try {
            FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);
            while (functions.hasNext()) {
                Function f = functions.next();
                if (!missing.remove(f.getName())) continue;
                var result = decompiler.decompileFunction(f, 90, monitor);
                if (!result.decompileCompleted()) throw new IllegalStateException("Cannot inspect: " + f.getName());
                var prototype = result.getHighFunction().getFunctionPrototype();
                JsonObject map = assignments.getAsJsonObject(f.getName());
                List<ParameterImpl> parameters = new ArrayList<>();
                for (int i = 0; i < prototype.getNumParams(); ++i) {
                    var parameter = prototype.getParam(i);
                    JsonObject override = map.getAsJsonObject(Integer.toString(i));
                    parameters.add(new ParameterImpl(override == null ? parameter.getName() : override.get("name").getAsString(),
                        override == null ? parameter.getDataType() : pointed(override.get("type").getAsString()), currentProgram));
                }
                for (String key : map.keySet()) if (Integer.parseInt(key) >= parameters.size())
                    throw new IllegalStateException("Uninferred argument: " + f.getName() + ":" + key);
                changes.put(f, parameters);
            }
        } finally { decompiler.dispose(); }
        if (!missing.isEmpty()) throw new IllegalStateException("Missing functions: " + missing);
        for (var entry : changes.entrySet()) {
            entry.getKey().setCallingConvention(currentProgram.getCompilerSpec().getDefaultCallingConvention().getName());
            entry.getKey().replaceParameters(entry.getValue(),
                Function.FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED);
        }
        Files.writeString(folder.resolve("applied-types.json"), new GsonBuilder().setPrettyPrinting().create().toJson(meta) + "\n");
        println("AAC types: checked " + meta.getAsJsonObject("types").size() + " layouts; annotated " + changes.size() + " functions");
        runScript("DecompileAacMemory.java", new String[] { folder.resolve("pseudocode").toString(),
            "inventory:" + getScriptArgs()[1] });
    }
}
