// FIXED_FACTORY: collect published BLOB indices, distinguishing end-of-search from read/OOM failure.
esp_err_t Storage::populateBlobIndices(TBlobIndexList& blobIdxList)
{
    for (auto it = mPageManager.begin(); it != mPageManager.end(); ++it) {
        Page& p = *it;
        size_t itemIndex = 0;
        Item item;
        esp_err_t err;
        while ((err = p.findItem(Page::NS_ANY, ItemType::BLOB_IDX, nullptr, itemIndex, item)) == ESP_OK) {
            BlobIndexNode* entry = new (std::nothrow) BlobIndexNode;
            if (!entry) return ESP_ERR_NO_MEM;
            item.getKey(entry->key, sizeof(entry->key));
            entry->nsIndex = item.nsIndex;
            entry->chunkStart = item.blobIndex.chunkStart;
            entry->chunkCount = item.blobIndex.chunkCount;
            entry->dataSize = item.blobIndex.dataSize;
            entry->observedDataSize = 0;
            entry->observedChunkCount = 0;
            blobIdxList.push_back(entry);
            itemIndex += item.span;
        }
        if (err != ESP_ERR_NVS_NOT_FOUND) return err;
    }
    return ESP_OK;
}
