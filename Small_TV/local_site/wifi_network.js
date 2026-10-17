/** Format a network option while preserving the API's signed RSSI in dBm. */
function formatWifiNetworkLabel(network) {
    // FIXED_FACTORY: Math.abs erased the sign of received signal power.
    const suffix = Number.isFinite(network.rssi) ? ` (${network.rssi}dBm)` : '';
    return network.ssid + suffix;
}
