/** Format a network option while preserving the API's signed RSSI in dBm. */
function formatWifiNetworkLabel(network) {
    // FIXED_FACTORY: Math.abs erased the sign of received signal power.
    const suffix = Number.isFinite(network.rssi) ? ` (${network.rssi}dBm)` : '';
    return network.ssid + suffix;
}

/** Distinguish the manual-entry option from a real access point's SSID. */
function isManualWifiSelection(select) {
    // FIXED_FACTORY: the literal SSID "manual" is a valid discovered network.
    return select.selectedOptions[0]?.dataset.manualEntry === 'true';
}
