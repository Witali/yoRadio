// FIXED_FACTORY: initialize Storage only after every recovery step succeeds; own all temporary nodes.
esp_err_t Storage::init(uint32_t baseSector, uint32_t sectorCount)
{
    mState = StorageState::INVALID;
    auto err = mPageManager.load(mPartition, baseSector, sectorCount);
    if (err != ESP_OK) return err;

    clearNamespaces();
    std::fill_n(mNamespaceUsage.data(), mNamespaceUsage.byteSize()/4, 0);
    for (auto it = mPageManager.begin(); it != mPageManager.end(); ++it) {
        Page& p = *it;
        size_t itemIndex = 0;
        Item item;
        while ((err = p.findItem(Page::NS_INDEX, ItemType::U8, nullptr, itemIndex, item)) == ESP_OK) {
            NamespaceEntry* entry = new (std::nothrow) NamespaceEntry;
            if (!entry) return ESP_ERR_NO_MEM;
            item.getKey(entry->mName, sizeof(entry->mName));
            err = item.getValue(entry->mIndex);
            if (err != ESP_OK) {
                delete entry;
                return err;
            }
            if (mNamespaceUsage.set(entry->mIndex, true) != ESP_OK) {
                delete entry;
                return ESP_FAIL;
            }
            mNamespaces.push_back(entry);
            itemIndex += item.span;
        }
        if (err != ESP_ERR_NVS_NOT_FOUND) return err;
    }
    if (mNamespaceUsage.set(0, true) != ESP_OK || mNamespaceUsage.set(255, true) != ESP_OK) return ESP_FAIL;

    {
        TBlobIndexList blobIdxList;
        // The list is local to this recovery attempt. Scope exit must release
        // nodes already allocated even when a later allocation or I/O fails.
        struct Cleanup {
            TBlobIndexList& list;
            ~Cleanup() { list.clearAndFreeNodes(); }
        } cleanup{blobIdxList};
        err = populateBlobIndices(blobIdxList);
        if (err != ESP_OK) return err;
        err = eraseMismatchedBlobIndexes(blobIdxList);
        if (err != ESP_OK) return err;
        err = eraseOrphanDataBlobs(blobIdxList);
        if (err != ESP_OK) return err;
    }
    mState = StorageState::ACTIVE;
#ifdef DEBUG_STORAGE
    debugCheck();
#endif
    return ESP_OK;
}
