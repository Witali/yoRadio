// Windows-owned socket telemetry: no packet-capture driver or adapter changes.
// SIO_TCP_INFO/TCP_INFO_v0 layout is verified against Windows SDK mstcpip.h.
using System;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Diagnostics;
using System.Text;
using System.Threading;
using System.Globalization;

public static class NetworkTcpSource {
    static readonly object LogLock = new object();
    static int nextId, active;
    static string Quote(string text) {
        var b=new StringBuilder("\"");
        foreach(char c in text) {
            if(c=='"'||c=='\\') b.Append('\\').Append(c);
            else if(c<32) b.Append("\\u").Append(((int)c).ToString("x4"));
            else b.Append(c);
        }
        return b.Append('"').ToString();
    }
    static void Log(string fields) {
        lock(LogLock) Console.WriteLine("{\"utc\":"+Quote(DateTime.UtcNow.ToString("o"))+","+fields+"}");
    }
    static int QueryInt(Uri uri,string key,int fallback) {
        foreach(string item in uri.Query.TrimStart('?').Split('&')) {
            string[] pair=item.Split('='); int value;
            if(pair.Length==2&&pair[0]==key&&Int32.TryParse(pair[1],out value))return value;
        }
        return fallback;
    }
    sealed class Connection {
        public Socket socket; public int id, sampleMs;
        public long accepted; public volatile bool done;
        public readonly Stopwatch clock=Stopwatch.StartNew();
        public void Sample() {
            var version=new byte[4]; var info=new byte[88];
            while(!done) {
                try {
                    int n=socket.IOControl(unchecked((int)0xd8000027),version,info);
                    if(n!=88) { Log("\"event\":\"tcp_info_size\",\"id\":"+id+",\"bytes\":"+n);return; }
                    Log("\"event\":\"tcp\",\"id\":"+id+",\"ms\":"+clock.ElapsedMilliseconds+
                        ",\"accepted_body\":"+Interlocked.Read(ref accepted)+
                        ",\"mss\":"+BitConverter.ToUInt32(info,4)+
                        ",\"rtt_us\":"+BitConverter.ToUInt32(info,20)+
                        ",\"min_rtt_us\":"+BitConverter.ToUInt32(info,24)+
                        ",\"in_flight\":"+BitConverter.ToUInt32(info,28)+
                        ",\"cwnd\":"+BitConverter.ToUInt32(info,32)+
                        ",\"snd_wnd\":"+BitConverter.ToUInt32(info,36)+
                        ",\"bytes_out\":"+BitConverter.ToUInt64(info,48)+
                        ",\"bytes_retrans\":"+BitConverter.ToUInt32(info,68)+
                        ",\"fast_retrans\":"+BitConverter.ToUInt32(info,72)+
                        ",\"dup_acks\":"+BitConverter.ToUInt32(info,76)+
                        ",\"rto_episodes\":"+BitConverter.ToUInt32(info,80));
                } catch(SocketException ex) {
                    Log("\"event\":\"tcp_info_error\",\"id\":"+id+",\"error\":"+ex.ErrorCode);return;
                } catch(ObjectDisposedException) { return; }
                Thread.Sleep(sampleMs);
            }
        }
    }
    static void SendAll(Socket socket,byte[] bytes) {
        int offset=0;
        while(offset<bytes.Length) {
            int n=socket.Send(bytes,offset,bytes.Length-offset,SocketFlags.None);
            if(n<=0)throw new IOException("Socket closed while sending headers");
            offset+=n;
        }
    }
    static void Serve(Socket socket,string root,int sampleMs) {
        var c=new Connection {socket=socket,id=Interlocked.Increment(ref nextId),sampleMs=sampleMs};
        Thread sampler=null; long maxSendUs=0; int code=0;
        try {
            socket.NoDelay=true;socket.ReceiveTimeout=5000;socket.SendTimeout=5000;
            var header=new byte[4096];int used=0;
            while(used<header.Length) {
                int n=socket.Receive(header,used,header.Length-used,SocketFlags.None);
                if(n<=0)return;
                used+=n;
                if(Encoding.ASCII.GetString(header,0,used).Contains("\r\n\r\n"))break;
            }
            string request=Encoding.ASCII.GetString(header,0,used);
            string[] first=request.Split('\n')[0].TrimEnd('\r').Split(' ');
            if(first.Length!=3||first[0]!="GET"||!request.Contains("\r\n\r\n")) {
                SendAll(socket,Encoding.ASCII.GetBytes("HTTP/1.1 400 Bad Request\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"));return;
            }
            var uri=new Uri("http://fixture"+first[1]);
            string file=null,mime=null;
            if(uri.AbsolutePath=="/mp3-128") {file="tests/fixtures/mp3_composite/mix-128.mp3";mime="audio/mpeg";}
            if(uri.AbsolutePath=="/mp3-320") {file="tests/fixtures/mp3_composite/mix-320.mp3";mime="audio/mpeg";}
            if(uri.AbsolutePath=="/aac-64") {file="tests/fixtures/aac_composite/mix-064.aac";mime="audio/aac";}
            int rate=QueryInt(uri,"rate",0);
            if(file==null||(rate!=0&&rate!=64&&rate!=128&&rate!=320)) {
                SendAll(socket,Encoding.ASCII.GetBytes("HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"));return;
            }
            byte[] audio=File.ReadAllBytes(Path.Combine(root,file));
            long target=rate>0?rate*1000L/8*35:128L*1024*1024;
            long length=((target+audio.Length-1)/audio.Length)*audio.Length;
            Log("\"event\":\"begin\",\"id\":"+c.id+",\"path\":"+Quote(uri.AbsolutePath)+
                ",\"case\":"+QueryInt(uri,"case",-1)+",\"variant\":"+QueryInt(uri,"variant",-1)+
                ",\"rate_kbps\":"+rate+",\"send_buffer\":"+socket.SendBufferSize+
                ",\"sample_ms\":"+sampleMs+",\"content_length\":"+length);
            sampler=new Thread(c.Sample);sampler.IsBackground=true;sampler.Start();
            SendAll(socket,Encoding.ASCII.GetBytes("HTTP/1.1 200 OK\r\nContent-Type: "+mime+
                "\r\nContent-Length: "+length+"\r\nConnection: close\r\n\r\n"));
            var pacing=Stopwatch.StartNew();
            while(c.accepted<length) {
                int offset=(int)(c.accepted%audio.Length);
                int count=(int)Math.Min(1024L,Math.Min(audio.Length-offset,length-c.accepted));
                long start=Stopwatch.GetTimestamp();
                int sent=socket.Send(audio,offset,count,SocketFlags.None);
                long elapsed=(Stopwatch.GetTimestamp()-start)*1000000/Stopwatch.Frequency;
                if(elapsed>maxSendUs)maxSendUs=elapsed;
                if(sent<=0)break;
                Interlocked.Add(ref c.accepted,sent);
                if(rate>0) {
                    double deadline=c.accepted*8.0/rate;
                    while(deadline>pacing.Elapsed.TotalMilliseconds)
                        Thread.Sleep((int)Math.Max(1,Math.Min(100,Math.Ceiling(deadline-pacing.Elapsed.TotalMilliseconds))));
                }
            }
        } catch(SocketException ex) { code=ex.ErrorCode; }
          catch(Exception ex) { code=-1;Log("\"event\":\"error\",\"id\":"+c.id+",\"type\":"+Quote(ex.GetType().Name)); }
        finally {
            c.done=true;if(sampler!=null)sampler.Join(1500);
            Log("\"event\":\"end\",\"id\":"+c.id+",\"accepted_body\":"+c.accepted+
                ",\"elapsed_ms\":"+c.clock.ElapsedMilliseconds+",\"max_send_us\":"+maxSendUs+",\"error\":"+code);
            socket.Dispose();Interlocked.Decrement(ref active);
        }
    }
    public static void Run(string root,string address,int port,int sampleMs) {
        var listener=new TcpListener(IPAddress.Parse(address),port);listener.Start(8);
        Log("\"event\":\"listen\",\"address\":"+Quote(address)+",\"port\":"+port);
        try {
            while(true) {
                Socket socket=listener.AcceptSocket();
                if(Interlocked.Increment(ref active)>4) {socket.Dispose();Interlocked.Decrement(ref active);continue;}
                var worker=new Thread(()=>Serve(socket,root,sampleMs));worker.IsBackground=true;worker.Start();
            }
        } finally {listener.Stop();}
    }
}
