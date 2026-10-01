# Development image — rejected standalone experiment

Early scratch plus lossless PS-control relocation; no PC16 compression. All six HE/v2 starts in three switching cycles failed a 51596-byte allocation, largest block 43008 bytes. Rejected as a full-radio fix.

No deep sleep. Application-only OTA image; never overwrite user NVS or SPIFFS. See `manifest.json` for exact binary/configuration fingerprints and source-provenance limitations.
