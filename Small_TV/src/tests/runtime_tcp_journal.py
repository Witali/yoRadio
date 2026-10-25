"""Replay same-stop TCP observations and keep a small attribution time series."""
from collections import Counter


class TcpCoverage:
    """Keep busy observations explicit and verify additive heap accounting."""
    def __init__(self, topology, tcp):
        """Reuse qualified decoders for the complete journal, not a bounded tail."""
        self.topology, self.tcp = topology, tcp
        self.series, self.busy = [], Counter()
        self.observed = self.maximum_pcbs = self.maximum_segments = self.maximum_pbufs = 0

    def __call__(self, snapshot):
        """Verify literal heap instructions before deriving any TCP memory metric."""
        self.topology.validate(snapshot)
        self.tcp.validate(snapshot, self.topology)
        data = snapshot['tcp_topology']
        row = {'label': snapshot['label'], 'guest_seconds': snapshot['guest_seconds'],
               'heap_free_bytes': snapshot['heap']['free_bytes'], 'observed': data['observed']}
        if not data['observed']:
            row['reason'] = data['gate']['reason']
            self.busy[row['reason']] += 1
        else:
            attribution = data['attribution']
            total_capacity = sum(part['inventory']['allocated_capacity_bytes'] for part in snapshot['heap_topology']['heaps'])
            total_headers = sum(part['inventory']['allocated_header_bytes'] for part in snapshot['heap_topology']['heaps'])
            if (attribution['allocated_capacity_bytes'] != total_capacity or
                    attribution['allocated_header_bytes'] != total_headers):
                raise ValueError('TCP attribution does not cover the observed heap inventory')
            self.observed += 1
            self.maximum_pcbs = max(self.maximum_pcbs, len(data['pcbs']))
            self.maximum_segments = max(self.maximum_segments, len(data['segments']))
            self.maximum_pbufs = max(self.maximum_pbufs, len(data['pbufs']))
            row.update(tcp_consumed_bytes=attribution['attributed_capacity_bytes'] + attribution['attributed_header_bytes'],
                       unclassified_consumed_bytes=attribution['unclassified_capacity_bytes'] + attribution['unclassified_header_bytes'],
                       tcp_blocks=attribution['attributed_blocks'], unclassified_blocks=attribution['unclassified_blocks'],
                       pcbs=len(data['pcbs']), segments=len(data['segments']), pbufs=len(data['pbufs']),
                       time_wait_pcbs=data['list_counts']['time_wait'], unregistered_pcbs=data['unregistered_pcbs'])
        self.series.append(row)

    def summary(self):
        """Report coverage separately from firmware correctness or leak conclusions."""
        return {'snapshots': len(self.series), 'observed': self.observed, 'busy_reasons': dict(sorted(self.busy.items())),
                'maximum_pcbs': self.maximum_pcbs, 'maximum_segments': self.maximum_segments,
                'maximum_pbufs': self.maximum_pbufs}
