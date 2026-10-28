// FIXED_FACTORY: validate BLOB summaries and erase mismatches only after successful scans.
esp_err_t Storage::eraseMismatchedBlobIndexes(TBlobIndexList& blobIdxList)
{
    for (auto it = mPageManager.begin(); it != mPageManager.end(); ++it) {
        Page& p = *it;
        size_t itemIndex = 0;
        Item item;
        esp_err_t err;
        while ((err = p.findItem(Page::NS_ANY, ItemType::BLOB_DATA, nullptr, itemIndex, item)) == ESP_OK) {
            auto iter = std::find_if(blobIdxList.begin(), blobIdxList.end(), [=](const BlobIndexNode& e) -> bool {
                return strncmp(item.key, e.key, sizeof(e.key)-1) == 0 && item.nsIndex == e.nsIndex &&
                    item.chunkIndex >= static_cast<uint8_t>(e.chunkStart) &&
                    item.chunkIndex < static_cast<uint8_t>(e.chunkStart == nvs::VerOffset::VER_0_OFFSET ?
                                                         nvs::VerOffset::VER_1_OFFSET : nvs::VerOffset::VER_ANY);
            });
            if (iter != blobIdxList.end()) {
                iter->observedDataSize += item.varLength.dataSize;
                iter->observedChunkCount++;
            }
            itemIndex += item.span;
        }
        if (err != ESP_ERR_NVS_NOT_FOUND) return err;
    }
    auto iter = blobIdxList.begin();
    while (iter != blobIdxList.end()) {
        if (iter->observedDataSize != iter->dataSize || iter->observedChunkCount != iter->chunkCount) {
            for (auto it = mPageManager.begin(); it != mPageManager.end(); ++it) {
                if (it->state() == Page::PageState::CORRUPT || it->state() == Page::PageState::INVALID ||
                    it->state() == Page::PageState::UNINITIALIZED) continue;
                auto err = it->eraseItem(iter->nsIndex, ItemType::BLOB_IDX, iter->key,
                                         Page::DEFAULT_PURGE_AFTER_ERASE, 255, iter->chunkStart);
                if (err == ESP_OK) break;
                if (err != ESP_ERR_NVS_NOT_FOUND && err != ESP_ERR_NVS_TYPE_MISMATCH) return err;
            }
            auto tmp = iter;
            ++iter;
            blobIdxList.erase(tmp);
            delete static_cast<BlobIndexNode*>(tmp);
        } else {
            ++iter;
        }
    }
    return ESP_OK;
}
