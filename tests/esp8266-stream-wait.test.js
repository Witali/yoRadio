const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const {spawnSync} = require("node:child_process");

const root = path.resolve(__dirname, "..");
const sourceDir = path.join(root, "esp8266", "rtos-sdk-native", "main");
const protocol = path.join(sourceDir, "http_stream_protocol.c");
const harness = path.join(__dirname, "native", "esp8266_stream_wait_test.c");

function findVcVars() {
  const base = "C:\\Program Files\\Microsoft Visual Studio";
  if(!fs.existsSync(base)) return null;
  for(const version of fs.readdirSync(base).sort().reverse()) {
    const versionDir = path.join(base, version);
    for(const edition of fs.readdirSync(versionDir).sort().reverse()) {
      const candidate = path.join(versionDir, edition, "VC", "Auxiliary", "Build", "vcvars64.bat");
      if(fs.existsSync(candidate)) return candidate;
    }
  }
  return null;
}

test("ESP8266 bounded readiness wait preserves cancellation and inactivity deadlines", t => {
  const outputDir = fs.mkdtempSync(path.join(os.tmpdir(), "yoradio-http-test-"));
  const executable = path.join(outputDir, process.platform === "win32" ? "http-test.exe" : "http-test");
  t.after(() => fs.rmSync(outputDir, {recursive: true, force: true}));
  let build;
  if(process.platform === "win32") {
    const vcvars = findVcVars();
    if(!vcvars) return t.skip("Visual C++ build tools are not installed");
const command = `@call "${vcvars}" >nul`+"\r\n"+`@if errorlevel 1 exit /b %errorlevel%`+"\r\n"+`@cl /nologo /std:c11 /W4 /WX /I"${sourceDir}" "${protocol}" "${harness}" /Fe:"${executable}"`+"\r\n";
    const batch = path.join(outputDir, "build.cmd");
    fs.writeFileSync(batch, command);
    build = spawnSync("cmd.exe", ["/d", "/c", batch], {
      cwd: outputDir,
      encoding: "utf8",
    });
  } else {
    build = spawnSync("cc", ["-std=c11", "-Wall", "-Wextra", "-Werror", `-I${sourceDir}`, protocol, harness, "-o", executable], {
      cwd: outputDir,
      encoding: "utf8",
    });
    if(build.error?.code === "ENOENT") return t.skip("A host C compiler is not installed");
  }
  assert.equal(build.status, 0, `${build.stdout}\n${build.stderr}`);
  const run = spawnSync(executable, [], {encoding: "utf8"});
  assert.equal(run.status, 0, `${run.stdout}\n${run.stderr}`);
  assert.match(run.stdout, /Stream wait tests passed/);
});


test("ready-wait SDK uses persistent per-thread semaphores", t => {
 const sdk=process.env.IDF_PATH||path.join(root,".worktree/esp8266-native-port/.build/esp8266-rtos-sdk");
 const file=path.join(sdk,"components/lwip/port/esp8266/include/lwipopts.h");
 if(!fs.existsSync(file))return t.skip("ESP8266 SDK not installed");
 const config=fs.readFileSync(file,"utf8");
 assert.match(config,/#define LWIP_NETCONN_SEM_PER_THREAD\s+1/);
});
