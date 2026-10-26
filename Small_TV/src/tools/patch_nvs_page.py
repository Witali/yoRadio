"""Apply bounded Small TV NVS recovery corrections to a build-local SDK source copy."""
import argparse
import hashlib
import json
from pathlib import Path

SOURCE_SHA = 'b6c1dd565c41479e9ad7d7b5caf296c4621b1b93e6b6eb048e0cd562c5a559c7'
FIXES = ('erased-slot-counts', 'hash-candidate-identity', 'blob-chunk-identity',
         'recovery-io-error-propagation')


def sha(raw):
    """Identify exact source bytes rather than accepting a nearby SDK revision."""
    return hashlib.sha256(raw).hexdigest()


def patch(raw):
    """Preserve the vendor source and license, changing only qualified recovery decisions."""
    if sha(raw) != SOURCE_SHA:
        raise ValueError('NVS SDK source differs; requalify before applying recovery fixes')
    text = raw.decode('utf8').replace('\r\n', '\n')
    edits = (
        ('esp_err_t Page::eraseEntryAndSpan(size_t index, const bool purgeAfterErase)\n{',
         '''// FIXED_FACTORY: erase a record/span while counting each physical slot once.
esp_err_t Page::eraseEntryAndSpan(size_t index, const bool purgeAfterErase)
{'''),
        ('''                ++mErasedEntryCount;
            }
            if (span == 1)''',
         '''                // A partially erased span already contributed these slots.
                if (state != EntryState::ERASED) {
                    ++mErasedEntryCount;
                }
            }
            if (span == 1)'''),
        ('''    } else {
        auto rc = alterEntryState(index, EntryState::ERASED);
        if (rc != ESP_OK) {
            return rc;
        }
        if(purgeAfterErase)''',
         '''    } else {
        auto rc = alterEntryState(index, EntryState::ERASED);
        if (rc != ESP_OK) {
            return rc;
        }
        // ILLEGAL/EMPTY slots were not counted as erased by the initial scan.
        if (state != EntryState::ERASED) {
            ++mErasedEntryCount;
        }
        if(purgeAfterErase)'''),
        ('esp_err_t Page::mLoadEntryTable()\n{',
         '''// FIXED_FACTORY: preserve key/chunk identity and surface recovery I/O failures.
esp_err_t Page::mLoadEntryTable()
{'''),
        ('''                ++mErasedEntryCount;
            } else {
                break;
            }
        }

        // check that all variable-length items''',
         '''                // A damaged tail may reach a slot already counted as erased.
                if (oldState != EntryState::ERASED) {
                    ++mErasedEntryCount;
                }
            } else {
                break;
            }
        }

        // check that all variable-length items'''),
        ('''            size_t duplicateIndex = mHashList.find(0, item);
''',
         '''            size_t duplicateIndex = mHashList.find(0, item);
            // HashList stores only a 24-bit hash. Confirm full identity before
            // discarding an older record, and continue past unrelated collisions.
            // Datatype is deliberately excluded: replacing a key's type is valid.
            while (duplicateIndex < i) {
                Item candidate;
                err = readEntry(duplicateIndex, candidate);
                if (err != ESP_OK) {
                    mState = PageState::INVALID;
                    return err;
                }
                if (candidate.nsIndex == item.nsIndex &&
                        candidate.chunkIndex == item.chunkIndex &&
                        strncmp(candidate.key, item.key, Item::MAX_KEY_LENGTH) == 0) {
                    break;
                }
                duplicateIndex = mHashList.find(duplicateIndex + 1, item);
            }
'''),
        ('findItem(item.nsIndex, item.datatype, item.key, findItemIndex, dupItem) == ESP_OK',
         '''findItem(item.nsIndex, item.datatype, item.key, findItemIndex, dupItem,
                         item.chunkIndex) == ESP_OK'''),
        ('''                if (needErase) {
                    eraseEntryAndSpan(i, DEFAULT_PURGE_AFTER_ERASE);
                    continue;
                }''',
         '''                if (needErase) {
                    err = eraseEntryAndSpan(i, DEFAULT_PURGE_AFTER_ERASE);
                    if (err != ESP_OK) {
                        mState = PageState::INVALID;
                        return err;
                    }
                    continue;
                }'''),
        ('''            if (duplicateIndex < i) {
                eraseEntryAndSpan(duplicateIndex, DEFAULT_PURGE_AFTER_ERASE);
            }''',
         '''            if (duplicateIndex < i) {
                err = eraseEntryAndSpan(duplicateIndex, DEFAULT_PURGE_AFTER_ERASE);
                if (err != ESP_OK) {
                    mState = PageState::INVALID;
                    return err;
                }
            }'''),
        ('''            if (findItem(item.nsIndex, item.datatype, item.key, findItemIndex, dupItem,
                         item.chunkIndex) == ESP_OK) {''',
         '''            err = findItem(item.nsIndex, item.datatype, item.key, findItemIndex, dupItem,
                           item.chunkIndex);
            if (err != ESP_OK && err != ESP_ERR_NVS_NOT_FOUND) {
                mState = PageState::INVALID;
                return err;
            }
            if (err == ESP_OK) {'''),
        ('''                    if (state != EntryState::WRITTEN) {
                        eraseEntryAndSpan(i, DEFAULT_PURGE_AFTER_ERASE);
                        break;
                    }''',
         '''                    if (state != EntryState::WRITTEN) {
                        err = eraseEntryAndSpan(i, DEFAULT_PURGE_AFTER_ERASE);
                        if (err != ESP_OK) {
                            mState = PageState::INVALID;
                            return err;
                        }
                        break;
                    }'''),
    )
    for before, after in edits:
        if text.count(before) != 1:
            raise ValueError('NVS patch context is absent or ambiguous')
        text = text.replace(before, after, 1)
    return text.encode('utf8')


def write_changed(path, raw):
    """Avoid needless recompilation when configure sees the same generated source."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_bytes() != raw:
        path.write_bytes(raw)


def main():
    """Require separate source/output paths; never modify the shared SDK in place."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'output', 'report'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    paths = [getattr(args, name).resolve() for name in ('source', 'output', 'report')]
    if len(set(paths)) != 3:
        raise ValueError('SDK source, generated copy and report must be separate files')
    original = args.source.read_bytes(); fixed = patch(original)
    report = dict(schema='small-tv-nvs-recovery-v1', source_sha256=sha(original),
                  generated_sha256=sha(fixed), generator_sha256=sha(Path(__file__).read_bytes()),
                  fixes=list(FIXES), shared_sdk_modified=False)
    write_changed(args.output, fixed)
    write_changed(args.report, (json.dumps(report, indent=2)+'\n').encode())
    print(json.dumps(report))


if __name__ == '__main__':
    main()
