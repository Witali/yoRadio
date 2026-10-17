async function uploadImageInChunks(file, fileNumber) {
    /* Upload ordered blocks, retry lost replies and publish only after all ACKs.
     * REQUESTED_CHANGE: remove software waits after successful synchronous flash
     * writes and after the final failed attempt. Keep backoff between retries. */
    const chunkSize = 4096;
    const maxAttempts = 5;
    const totalChunks = Math.ceil(file.size / chunkSize);
    const startResponse = await fetch('/start_upload', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({file_number: fileNumber, file_size: file.size,
            total_chunks: totalChunks})
    });
    if (!startResponse.ok) throw new Error('Failed to start upload session');

    for (let chunkIndex = 0; chunkIndex < totalChunks; chunkIndex++) {
        const start = chunkIndex * chunkSize;
        const formData = new FormData();
        formData.append('chunk', file.slice(start, Math.min(start + chunkSize, file.size)));
        formData.append('file_number', fileNumber.toString());
        formData.append('chunk_index', chunkIndex.toString());
        formData.append('total_chunks', totalChunks.toString());
        let lastError;
        let success = false;
        for (let attempt = 0; attempt < maxAttempts; attempt++) {
            try {
                const progress = Math.round((chunkIndex / totalChunks) * 100);
                updateLoadingText(`Uploading... ${progress}% (File ${fileNumber})`);
                const response = await fetch('/upload_chunk', {method: 'POST', body: formData});
                if (response.ok) {
                    success = true;
                    break;
                }
                lastError = `HTTP ${response.status}`;
            } catch (error) {
                lastError = error.message;
            }
            // A lost reply may follow a completed write. Reuse the same block,
            // and wait only when another attempt will actually be made.
            if (attempt + 1 < maxAttempts) {
                await new Promise(resolve => setTimeout(resolve, 500 * (attempt + 1)));
            }
        }
        if (!success) throw new Error(`Chunk ${chunkIndex} failed after retries: ${lastError}`);
        // The native server ACK follows esp_partition_write. Awaiting that ACK
        // paces writes without the factory page's additional 50 ms per block.
    }

    const finishResponse = await fetch('/finish_upload', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({file_number: fileNumber, file_name: `file${fileNumber}.jpg`})
    });
    if (!finishResponse.ok) throw new Error('Finish upload command failed');
}
