// FIXED_FACTORY: rebuild page order/recover interrupted copying, propagating every I/O failure.
esp_err_t PageManager::load(Partition *partition, uint32_t baseSector, uint32_t sectorCount)
{
    if (partition == nullptr) {
        return ESP_ERR_INVALID_ARG;
    }
    mBaseSector = baseSector;
    mPageCount = sectorCount;
    mPageList.clear();
    mFreePageList.clear();
    mPages.reset(new (nothrow) Page[sectorCount]);
    if (!mPages) return ESP_ERR_NO_MEM;

    for (uint32_t i = 0; i < sectorCount; ++i) {
        auto err = mPages[i].load(partition, baseSector + i);
        if (err != ESP_OK) return err;
        uint32_t seqNumber;
        if (mPages[i].getSeqNumber(seqNumber) != ESP_OK) {
            mFreePageList.push_back(&mPages[i]);
        } else {
            auto pos = std::find_if(std::begin(mPageList), std::end(mPageList), [=](const Page& page) -> bool {
                uint32_t otherSeqNumber;
                return page.getSeqNumber(otherSeqNumber) == ESP_OK && otherSeqNumber > seqNumber;
            });
            if (pos == mPageList.end()) mPageList.push_back(&mPages[i]);
            else mPageList.insert(pos, &mPages[i]);
        }
    }
    if (mPageList.empty()) {
        mSeqNumber = 0;
        return activatePage();
    }
    uint32_t lastSeqNo;
    auto err = mPageList.back().getSeqNumber(lastSeqNo);
    if (err != ESP_OK) return err;
    mSeqNumber = lastSeqNo + 1;

    if (!partition->get_readonly()) {
        Page& lastPage = back();
        size_t lastItemIndex = SIZE_MAX;
        Item item;
        size_t itemIndex = 0;
        while ((err = lastPage.findItem(Page::NS_ANY, ItemType::ANY, nullptr, itemIndex, item)) == ESP_OK) {
            itemIndex += item.span;
            lastItemIndex = itemIndex;
        }
        if (err != ESP_ERR_NVS_NOT_FOUND) return err;

        if (lastItemIndex != SIZE_MAX) {
            auto last = PageManager::TPageListIterator(&lastPage);
            // Remove only the first matching predecessor. A different type is
            // an ordinary search miss here, including legacy BLOB replacement.
            auto erasePrevious = [&](ItemType datatype) -> esp_err_t {
                for (auto it = begin(); it != last; ++it) {
                    if (it->state() == Page::PageState::FREEING) continue;
                    auto result = it->eraseItem(item.nsIndex, datatype, item.key,
                                               Page::DEFAULT_PURGE_AFTER_ERASE, item.chunkIndex);
                    if (result == ESP_OK) return ESP_OK;
                    if (result != ESP_ERR_NVS_NOT_FOUND && result != ESP_ERR_NVS_TYPE_MISMATCH) return result;
                }
                return ESP_ERR_NVS_NOT_FOUND;
            };
            err = erasePrevious(item.datatype);
            if (err == ESP_ERR_NVS_NOT_FOUND && item.datatype == ItemType::BLOB_IDX) {
                err = erasePrevious(ItemType::BLOB);
            }
            if (err != ESP_OK && err != ESP_ERR_NVS_NOT_FOUND) return err;
        }

        for (auto it = begin(); it != end(); ++it) {
            if (it->state() != Page::PageState::FREEING) continue;
            Page* newPage = &mPageList.back();
            if (newPage->state() == Page::PageState::ACTIVE) {
                err = newPage->erase();
                if (err != ESP_OK) return err;
                mPageList.erase(newPage);
                mFreePageList.push_back(newPage);
            }
            err = activatePage();
            if (err != ESP_OK) return err;
            newPage = &mPageList.back();
            err = it->copyItems(*newPage);
            if (err != ESP_OK && err != ESP_ERR_NVS_NOT_FOUND) return err;
            err = it->erase();
            if (err != ESP_OK) return err;
            Page* p = static_cast<Page*>(it);
            mPageList.erase(it);
            mFreePageList.push_back(p);
            break;
        }
        if (mFreePageList.empty()) return ESP_ERR_NVS_NO_FREE_PAGES;
    }
    return ESP_OK;
}
