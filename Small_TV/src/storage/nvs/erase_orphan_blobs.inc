// FIXED_FACTORY: remove unpublished BLOB data, returning actual scan/erase failures.
esp_err_t Storage::eraseOrphanDataBlobs(TBlobIndexList& blobIdxList)
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
                    item.chunkIndex < static_cast<uint8_t>(e.chunkStart)+e.chunkCount;
            });
            if (iter == blobIdxList.end()) {
                err = p.eraseItem(item.nsIndex, item.datatype, item.key, Page::DEFAULT_PURGE_AFTER_ERASE, item.chunkIndex);
                if (err != ESP_OK) return err;
            }
            itemIndex += item.span;
        }
        if (err != ESP_ERR_NVS_NOT_FOUND) return err;
    }
    return ESP_OK;
}
