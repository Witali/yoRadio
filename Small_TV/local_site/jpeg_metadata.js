/* Remove encoder metadata from the known sRGB Canvas JPEG, keeping pixel data.
 * The device still validates baseline 240x240 dimensions, complete scans and EOI. */
async function stripCanvasJpegMetadata(blob) {
    const bytes = new Uint8Array(await blob.arrayBuffer());
    if (bytes.length < 4 || bytes[0] !== 255 || bytes[1] !== 0xd8 ||
        bytes[bytes.length - 2] !== 255 || bytes[bytes.length - 1] !== 0xd9) {
        throw new Error('Canvas did not produce a complete JPEG');
    }
    const parts = [bytes.subarray(0, 2)];
    let position = 2;
    while (position + 4 <= bytes.length) {
        if (bytes[position] !== 255 || bytes[position + 1] === 255) {
            throw new Error('Invalid Canvas JPEG marker');
        }
        const marker = bytes[position + 1];
        const length = (bytes[position + 2] << 8) | bytes[position + 3];
        const end = position + 2 + length;
        if (length < 2 || end > bytes.length) {
            throw new Error('Truncated Canvas JPEG header');
        }
        if (marker === 0xda) {
            // Entropy bytes include FF00 escapes: never search/edit them as
            // header segments. Copy the complete encoded scan and EOI intact.
            parts.push(bytes.subarray(position));
            return new Blob(parts, {type: 'image/jpeg'});
        }
        // Canvas pixels already use sRGB. APP/COM can reveal EXIF, profiles,
        // software or thumbnails; no such segment is needed by the LCD decoder.
        if (!(marker >= 0xe0 && marker <= 0xef) && marker !== 0xfe) {
            parts.push(bytes.subarray(position, end));
        }
        position = end;
    }
    throw new Error('Canvas JPEG has no image scan');
}
