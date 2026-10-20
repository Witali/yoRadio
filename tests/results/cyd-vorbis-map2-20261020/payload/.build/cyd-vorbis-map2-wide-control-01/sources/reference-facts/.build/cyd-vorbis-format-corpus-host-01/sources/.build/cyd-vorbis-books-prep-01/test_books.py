"""Pure byte/construction checks only; no decoder, PCM synthesis or subprocess."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import unittest

import generate_books as g

HERE = Path(__file__).resolve().parent
DATA = HERE / "generated01"


class ConstructionTests(unittest.TestCase):
    def test_entry_order_words_and_reversal(self):
        g.construction_controls()
        self.assertEqual([g.reverse(w) for w in g.words([3, 1, 3, 3, 3])], [0, 1, 4, 2, 6])
        self.assertEqual([g.reverse(w) if w else None for w in g.words([1, 0, 2, 3, 0, 3])],
                         [0, None, 1, 3, None, 7])

    def test_actual_header_books_and_ordered_gap(self):
        for book in g.configurations():
            packet = g.setup(book)
            packet.report()
            r = g.Reader(packet.data())
            r.take(64)
            self.assertEqual(g.read_book(r), g.scalar_book(book["ordered"]))
            self.assertEqual(g.read_book(r), {k: v for k, v in book.items() if k != "id"})
            if book["ordered"]:
                gap = [f for f in packet.fields if f["name"] == "book[1].length_2_count"]
                self.assertEqual([(f["width"], f["value"]) for f in gap], [(3, 0)])

    def test_sparse_original_index_lookup2_values(self):
        seq0, seq1 = g.configurations()[-2:]
        self.assertEqual(g.vectors(seq0), [[-1, -1, -1, -1], [-1, 1, 1, -1],
                         [1, -1, 1, -1], [-1, 1, -1, 1], [1, -1, -1, 1], [1, 1, 1, 1]])
        self.assertEqual(g.vectors(seq1), [[-1, -2, -3, -4], [-1, 0, 1, 0],
                         [1, 0, 1, 0], [-1, 0, -1, 0], [1, 0, -1, 0], [1, 2, 3, 4]])
        self.assertNotEqual(g.vectors(seq0)[2], g.vectors(seq0)[1])
        bad = dict(seq0, multiplicands=seq0["multiplicands"][:16])
        with self.assertRaisesRegex(ValueError, "includes sparse holes"):
            g.vectors(bad)

    def test_lookup1_extra_entry_and_sequence_reset(self):
        books = g.configurations()
        self.assertEqual(g.quantvals(5, 2), 2)
        self.assertEqual(g.quantvals(6, 2), 2)
        self.assertEqual(g.vectors(books[0]), [[-1, -1], [1, -1], [-1, 1], [1, 1], [-1, -1]])
        self.assertEqual(g.vectors(books[3]), [[-1, -2], [1, 0], [-1, 0], [1, 2], [-1, -2]])
        self.assertEqual(g.vectors(books[2])[5], [1, -1])

    def test_every_actual_packet_uses_public_entry_indices(self):
        for book in g.configurations():
            usage, classes = Counter(), set()
            for number in range(len(g.MODES)):
                packet = g.audio(book, number)
                packet.report()
                observed = g.inspect_audio(packet.data(), book, number)
                classes.update(observed["classwords"])
                for channel, entries in enumerate(observed["vector_entry_ids"]):
                    self.assertEqual(entries, g.selected_entries(book, number, channel))
                    usage.update(entries)
                    self.assertEqual(len(observed["residue_vectors"][channel]), 16)
            self.assertEqual(classes, {0, 1})
            self.assertEqual(set(usage), {i for i, n in enumerate(book["lengths"]) if n})
            self.assertTrue(all(n > 1 for n in usage.values()))

    def test_complete_packet_consumption_and_malformed_construction_controls(self):
        book = g.configurations()[0]
        packet = g.audio(book, 0).data()
        for bad in (packet + b"\0", packet[:-1], bytes([packet[0] ^ 1]) + packet[1:]):
            with self.assertRaises(ValueError):
                g.inspect_audio(bad, book, 0)
        for lengths in ([1, 1, 1], [2, 2]):
            with self.assertRaises(ValueError):
                g.words(lengths)

    def test_constructed_spectral_equivalence_and_sequence_difference(self):
        books = {b["id"]: b for b in g.configurations()}
        document = json.loads((DATA / "matrix.json").read_text())
        spectral = {name: [g.inspect_audio(g.audio(b, i).data(), b, i)["residue_vectors"]
                           for i in range(len(g.MODES))] for name, b in books.items()}
        for group in document["expected_same_decoder_pcm_equal_groups"]:
            self.assertTrue(all(spectral[name] == spectral[group[0]] for name in group))
        for first, second in document["expected_same_decoder_pcm_different_pairs"]:
            self.assertNotEqual(spectral[first], spectral[second])
        self.assertFalse(document["independent_pcm_checks_executed"])
        self.assertFalse(document["target_qualification_executed"])

    def test_stored_manifest_carriers_offsets_and_raw_accounting(self):
        manifest = json.loads((DATA / "manifest.json").read_text())
        for row in manifest["files"]:
            content = (DATA / row["path"]).read_bytes()
            self.assertEqual(len(content), row["bytes"])
            self.assertEqual(hashlib.sha256(content).hexdigest(), row["sha256"])
        document = json.loads((DATA / "matrix.json").read_text())
        self.assertEqual((document["case_count"], document["raw_packet_count"]), (8, 112))
        for case in document["cases"]:
            self.assertEqual((case["rate"], case["channels"], case["short"], case["long"]), (192000, 2, 256, 2048))
            self.assertEqual((case["expected_raw_samples"], case["expected_s16le_bytes"]), (7040, 28160))
            self.assertEqual(case["transitions"], {"SS": 4, "SL": 3, "LS": 3, "LL": 3})
            self.assertEqual(len((DATA / case["identification"]).read_bytes()), 30)
            audio = (DATA / case["audio"]).read_bytes()
            offsets = case["offsets"]
            self.assertEqual((offsets[0], offsets[-1], len(offsets)), (0, len(audio), 15))
            pages = g.base.read_pages((DATA / case["ogg"]).read_bytes())
            self.assertEqual(len(pages), 17)
            self.assertEqual([p["granule"] for p in pages], [0, 0, 0] + case["packet_granules"])
            self.assertEqual([p["packet"] for p in pages[3:]], [audio[a:b] for a, b in zip(offsets, offsets[1:])])
            damaged = bytearray((DATA / case["ogg"]).read_bytes())
            damaged[-1] ^= 1
            with self.assertRaisesRegex(ValueError, "CRC mismatch"):
                g.base.read_pages(damaged)


if __name__ == "__main__":
    unittest.main(verbosity=2)
