// Export sanitized security evidence for the verified Small_TV application.
// Run ExportDisplay.java first to apply the shared hardware/API annotations.
// The input must be the analysis ELF produced by prepare_analysis.py.
// @category Analysis
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.data.*;
import java.io.*;
import java.util.*;

public class ExportSecurity extends GhidraScript {
    private final Map<Function,String> selected = new LinkedHashMap<>();
    private void signature(long address, DataType result, DataType... types) throws Exception {
        Function f=getFunctionAt(toAddr(address));
        Parameter[] args=new Parameter[types.length];
        for(int i=0;i<types.length;i++) args[i]=new ParameterImpl("arg"+i,types[i],currentProgram);
        f.updateFunction(currentProgram.getCompilerSpec().getDefaultCallingConvention().getName(),
            new ReturnParameterImpl(result,currentProgram),Arrays.asList(args),
            Function.FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,true,SourceType.USER_DEFINED);
    }
    private Function labelFunction(long address, String name) throws Exception {
        Function f=getFunctionAt(toAddr(address));
        if(f==null) f=createFunction(toAddr(address),name);
        if(f!=null) {f.setName(name,SourceType.USER_DEFINED);selected.put(f,name);}
        return f;
    }
    private void collectReferences(long address,String name,PrintWriter refs) throws Exception {
        for(Reference ref:getReferencesTo(toAddr(address))) {
            Function f=getFunctionContaining(ref.getFromAddress());
            refs.printf("%s\t%08x\t%s\t%s\t%s%n",name,address,ref.getFromAddress(),
                f==null?"-":f.getEntryPoint(),f==null?"-":f.getName());
            if(f!=null) selected.putIfAbsent(f,name+"_reference");
        }
    }
    @Override public void run() throws Exception {
        File dir=new File(getScriptArgs()[0]);dir.mkdirs();
        Map<Long,String> extra=new LinkedHashMap<>();
        extra.put(0x4201ab6eL,"lwip_socket");
        extra.put(0x4201a468L,"lwip_bind");
        extra.put(0x4201a7f0L,"lwip_recvfrom");
        extra.put(0x4201a91cL,"lwip_sendto");
        extra.put(0x4203b694L,"httpd_req_recv");
        extra.put(0x4203a51eL,"httpd_req_get_hdr_value_str");
        extra.put(0x420396acL,"httpd_start");
        extra.put(0x4203e7b8L,"esp_http_client_perform");
        extra.put(0x4203d9f2L,"esp_http_client_cleanup");
        extra.put(0x40392326L,"esp_flash_read");
        for(Map.Entry<Long,String> item:extra.entrySet()) labelFunction(item.getKey(),item.getValue());
        DataType i32=IntegerDataType.dataType, u32=UnsignedIntegerDataType.dataType;
        DataType ptr=new PointerDataType(VoidDataType.dataType,4);
        signature(0x4201ab6eL,i32,i32,i32,i32);
        signature(0x4201a468L,i32,i32,ptr,u32);
        signature(0x4201a7f0L,i32,i32,ptr,u32,i32,ptr,ptr);
        signature(0x4201a91cL,i32,i32,ptr,u32,i32,ptr,u32);
        signature(0x4203e7b8L,i32,ptr);
        signature(0x4203d9f2L,i32,ptr);
        try(PrintWriter refs=new PrintWriter(new File(dir,"security-references.tsv"),"UTF-8")) {
            refs.println("identifier\taddress\treference\tfunction_entry\tfunction_name");
            for(Map.Entry<Long,String> item:extra.entrySet()) collectReferences(item.getKey(),item.getValue(),refs);
            collectReferences(0x3fcbd2ecL,"upload_receive_buffer",refs);
            collectReferences(0x3fcb7ba0L,"configured_ssid",refs);
            collectReferences(0x3fcb7be1L,"configured_wifi_password",refs);
            collectReferences(0x3fcc3a5cL,"jpeg_write_cursor",refs);
            Map<Long,String> strings=new LinkedHashMap<>();
            strings.put(0x3c0c29ecL,"pool_ntp_org");
            strings.put(0x3c0c3c08L,"aliyun_ntp");
            strings.put(0x3c0c3c18L,"cn_pool_ntp_org");
            strings.put(0x3c0c3b58L,"openweather_url");
            strings.put(0x3c0c2c3cL,"udp_socket_error");
            strings.put(0x3c0c2c6cL,"udp_bind_error");
            strings.put(0x3c0ef86cL,"esp_flash_write");
            strings.put(0x3c0ef87cL,"esp_flash_erase_region");
            strings.put(0x3c0f1b64L,"httpd_register_uri_handler");
            strings.put(0x3c0f1c64L,"esp_http_client_init");
            strings.put(0x3c0f7cd0L,"esp_ota_get_running_partition");
            for(Map.Entry<Long,String> item:strings.entrySet()) collectReferences(item.getKey(),item.getValue(),refs);
            List<Function> libraries=new ArrayList<>(selected.keySet());
            for(Function f:libraries) {
                for(Reference ref:getReferencesTo(f.getEntryPoint())) {
                    if(!ref.getReferenceType().isCall()) continue;
                    Function caller=getFunctionContaining(ref.getFromAddress());
                    refs.printf("caller_of_%s\t%s\t%s\t%s\t%s%n",selected.get(f),f.getEntryPoint(),
                        ref.getFromAddress(),caller==null?"-":caller.getEntryPoint(),caller==null?"-":caller.getName());
                    if(caller!=null) selected.putIfAbsent(caller,"caller_of_"+selected.get(f));
                }
            }
            // URI descriptors parsed from the initialized image: addr/method/function/context.
            long[] tables={0x3c0d665cL,0x3fcb44a0L};
            int[] counts={31,3};
            try(PrintWriter routes=new PrintWriter(new File(dir,"registered-routes.tsv"),"UTF-8")) {
                routes.println("descriptor\tmethod\turi\thandler");
                for(int t=0;t<tables.length;t++) for(int i=0;i<counts[t];i++) {
                    Address base=toAddr(tables[t]+24L*i);
                    long uri=Integer.toUnsignedLong(currentProgram.getMemory().getInt(base));
                    int method=currentProgram.getMemory().getInt(base.add(4));
                    long handler=Integer.toUnsignedLong(currentProgram.getMemory().getInt(base.add(8)));
                    StringBuilder text=new StringBuilder();
                    for(int j=0;j<128;j++){byte c=currentProgram.getMemory().getByte(toAddr(uri+j));if(c==0)break;text.append((char)c);}
                    String route=text.toString();
                    routes.printf("%s\t%d\t%s\t%08x%n",base,method,route,handler);
                    labelFunction(handler,"uri_"+(route.equals("/")?"root":route.substring(1)).replaceAll("[^A-Za-z0-9_]","_"));
                }
            }
            // Give library APIs names where their own __func__ strings identify them.
            Map<Long,String> APIs=new LinkedHashMap<>();
            APIs.put(0x3c0f1b64L,"httpd_register_uri_handler");
            APIs.put(0x3c0f1c64L,"esp_http_client_init");
            APIs.put(0x3c0ef86cL,"esp_flash_write");
            APIs.put(0x3c0ef87cL,"esp_flash_erase_region");
            APIs.put(0x3c0f7cd0L,"esp_ota_get_running_partition");
            for(Map.Entry<Long,String> item:APIs.entrySet()) for(Reference ref:getReferencesTo(toAddr(item.getKey()))) {
                Function f=getFunctionContaining(ref.getFromAddress());
                if(f!=null && f.getName().startsWith("FUN_")) f.setName(item.getValue(),SourceType.ANALYSIS);
            }
        }
        labelFunction(0x4200ce9eL,"wifi_setup_ap_config");
        labelFunction(0x4200d06eL,"wifi_setup_ap_start");
        labelFunction(0x4200d4beL,"http_404_captive_redirect");
        labelFunction(0x4200b5ccL,"read_animation_frame_table");
        labelFunction(0x4200c33eL,"jpeg_flash_read_callback");
        DecompInterface decompiler=new DecompInterface();decompiler.openProgram(currentProgram);
        try(PrintWriter out=new PrintWriter(new File(dir,"security-decompiled.c"),"UTF-8")) {
            for(Map.Entry<Function,String> item:selected.entrySet()) {
                Function f=item.getKey();
                long a=f.getEntryPoint().getOffset();
                // Keep application handlers plus the SDK running-partition guard.
                if((a<0x42008000L || a>=0x42011000L) && a!=0x4207bc60L) continue;
                out.printf("// Audit label: %s; entry: %s; name: %s%n",item.getValue(),f.getEntryPoint(),f.getName());
                DecompileResults r=decompiler.decompileFunction(f,60,monitor);
                if(r.decompileCompleted()) out.println(r.getDecompiledFunction().getC());
                else out.println("// Failed: "+r.getErrorMessage());
                out.println();
            }
        }
        File codeFile=new File(dir,"security-decompiled.c");
        String codeText=java.nio.file.Files.readString(codeFile.toPath(),java.nio.charset.StandardCharsets.UTF_8);
        codeText=codeText.replaceAll("(?m)[ \\t]+$","").stripTrailing()+"\n";
        java.nio.file.Files.writeString(codeFile.toPath(),codeText,java.nio.charset.StandardCharsets.UTF_8);
        decompiler.dispose();println("Security evidence export complete");
    }
}
