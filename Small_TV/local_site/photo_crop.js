/* Compute a square entirely inside the decoded image, using slider positions.
 * Percentages cover the available travel after zoom, including both edges. */
function squareCropBounds(width, height, zoom, horizontal, vertical) {
    if (![width, height, zoom, horizontal, vertical].every(Number.isFinite) ||
        width <= 0 || height <= 0 || zoom < 1 || zoom > 4 ||
        horizontal < 0 || horizontal > 100 || vertical < 0 || vertical > 100) {
        throw new Error('Invalid image crop');
    }
    const size = Math.min(width, height) / zoom;
    return {x: (width - size) * horizontal / 100,
        y: (height - size) * vertical / 100, size};
}

/* Resize about the opposite corner, keeping the LCD's square proportions.
 * Project pointer movement onto the corner diagonal and clamp to the image
 * edges and 1..4× zoom limits; crossing the anchor never flips the frame. */
function resizeSquareCrop(crop, width, height, corner, dx, dy) {
    if (!['nw','ne','sw','se'].includes(corner) ||
        ![width,height,crop.x,crop.y,crop.size,dx,dy].every(Number.isFinite) ||
        width <= 0 || height <= 0 || crop.size <= 0 || crop.x < 0 || crop.y < 0 ||
        crop.x + crop.size > width || crop.y + crop.size > height) {
        throw new Error('Invalid crop resize');
    }
    const sx = corner.endsWith('e') ? 1 : -1;
    const sy = corner.startsWith('s') ? 1 : -1;
    const anchorX = sx > 0 ? crop.x : crop.x + crop.size;
    const anchorY = sy > 0 ? crop.y : crop.y + crop.size;
    const maximum = Math.min(sx > 0 ? width - anchorX : anchorX,
        sy > 0 ? height - anchorY : anchorY, Math.min(width,height));
    const minimum = Math.min(width,height) / 4;
    const size = Math.max(minimum, Math.min(maximum, crop.size + (sx*dx + sy*dy)/2));
    return {x: sx > 0 ? anchorX : anchorX - size,
        y: sy > 0 ? anchorY : anchorY - size, size};
}

/* Let the user move/zoom a square before any upload request is sent.
 * The full image is drawn with letterboxing; the selected source coordinates
 * are independent of CSS size, so dragging also works on a phone. */
function choosePhotoCrop(image) {
    return new Promise((resolve, reject) => {
        const dialog = document.getElementById('crop-dialog');
        const preview = document.getElementById('crop-preview');
        const context = preview.getContext('2d');
        const zoom = document.getElementById('crop-zoom');
        const horizontal = document.getElementById('crop-horizontal');
        const vertical = document.getElementById('crop-vertical');
        const confirm = document.getElementById('crop-confirm');
        const cancel = document.getElementById('crop-cancel');
        const width = image.naturalWidth, height = image.naturalHeight;
        const scale = Math.min(preview.width / width, preview.height / height);
        const offsetX = (preview.width - width * scale) / 2;
        const offsetY = (preview.height - height * scale) / 2;
        const listeners = [];
        let drag = null;
        zoom.value = '1'; horizontal.value = '50'; vertical.value = '50';
        let selected = squareCropBounds(width, height, 1, 50, 50);

        function bounds() {
            return selected;
        }
        function selectFromControls() {
            selected = squareCropBounds(width, height, Number(zoom.value),
                Number(horizontal.value), Number(vertical.value));
            redraw();
        }
        // Darken only the unselected pixels, leaving the source image visible.
        function redraw() {
            const crop = bounds();
            const x = offsetX + crop.x * scale, y = offsetY + crop.y * scale;
            const size = crop.size * scale;
            context.clearRect(0, 0, preview.width, preview.height);
            context.fillStyle = '#fff';
            context.fillRect(offsetX, offsetY, width * scale, height * scale);
            context.drawImage(image, offsetX, offsetY, width * scale, height * scale);
            context.fillStyle = 'rgba(0,0,0,.6)';
            context.fillRect(0, 0, preview.width, y);
            context.fillRect(0, y + size, preview.width, preview.height - y - size);
            context.fillRect(0, y, x, size);
            context.fillRect(x + size, y, preview.width - x - size, size);
            context.lineWidth = 2; context.strokeStyle = '#fff';
            context.strokeRect(x, y, size, size);
            // Visible corner handles keep a usable size at narrow CSS widths.
            const handle = 12 * preview.width / preview.getBoundingClientRect().width;
            context.fillStyle = '#fff';
            for (const hx of [x,x+size]) for (const hy of [y,y+size]) {
                context.fillRect(hx-handle/2,hy-handle/2,handle,handle);
            }
            horizontal.disabled = width === crop.size;
            vertical.disabled = height === crop.size;
        }
        function listen(target, event, handler) {
            target.addEventListener(event, handler);
            listeners.push(() => target.removeEventListener(event, handler));
        }
        // Remove every handler on confirm/cancel so repeated uploads do not
        // retain earlier images or invoke multiple upload promises.
        function finish(accepted) {
            const crop = accepted ? bounds() : null;
            listeners.forEach(remove => remove());
            if (drag && preview.hasPointerCapture(drag.id)) preview.releasePointerCapture(drag.id);
            drag = null;
            dialog.close();
            if (accepted) resolve(crop);
            else reject(new DOMException('Upload cancelled', 'AbortError'));
        }
        listen(zoom, 'input', selectFromControls);
        listen(horizontal, 'input', selectFromControls);
        listen(vertical, 'input', selectFromControls);
        listen(confirm, 'click', () => finish(true));
        listen(cancel, 'click', () => finish(false));
        listen(dialog, 'cancel', event => { event.preventDefault(); finish(false); });
        listen(preview, 'pointerdown', event => {
            if (drag) return;
            const crop = bounds();
            const rectangle = preview.getBoundingClientRect();
            const px = (event.clientX-rectangle.left)*preview.width/rectangle.width;
            const py = (event.clientY-rectangle.top)*preview.height/rectangle.height;
            const radius = 14 * preview.width / rectangle.width;
            let corner = null;
            for (const [name,cx,cy] of [['nw',crop.x,crop.y],['ne',crop.x+crop.size,crop.y],
                ['sw',crop.x,crop.y+crop.size],['se',crop.x+crop.size,crop.y+crop.size]]) {
                if (Math.hypot(px-offsetX-cx*scale,py-offsetY-cy*scale) <= radius) {
                    corner = name; break;
                }
            }
            drag = {id:event.pointerId, x:event.clientX, y:event.clientY, crop, corner};
            preview.style.cursor = corner ? (corner==='nw' || corner==='se' ?
                'nwse-resize' : 'nesw-resize') : 'move';
            preview.setPointerCapture(event.pointerId);
        });
        listen(preview, 'pointermove', event => {
            if (!drag || drag.id !== event.pointerId) return;
            const rectangle = preview.getBoundingClientRect();
            const dx = (event.clientX - drag.x) * preview.width / rectangle.width / scale;
            const dy = (event.clientY - drag.y) * preview.height / rectangle.height / scale;
            if (drag.corner) selected = resizeSquareCrop(drag.crop,width,height,drag.corner,dx,dy);
            else selected = {x:Math.max(0,Math.min(width-drag.crop.size,drag.crop.x+dx)),
                y:Math.max(0,Math.min(height-drag.crop.size,drag.crop.y+dy)),size:drag.crop.size};
            // Keep exact source coordinates for export; range values are only
            // a rounded display until the user actually moves a slider.
            zoom.value = String(Math.min(width,height) / selected.size);
            horizontal.value = String(width===selected.size ? 50 : selected.x*100/(width-selected.size));
            vertical.value = String(height===selected.size ? 50 : selected.y*100/(height-selected.size));
            redraw();
        });
        function endDrag(event) {
            if (drag && drag.id === event.pointerId) {
                if (preview.hasPointerCapture(drag.id)) preview.releasePointerCapture(drag.id);
                drag = null;
                preview.style.cursor = 'move';
            }
        }
        listen(preview, 'pointerup', endDrag);
        listen(preview, 'pointercancel', endDrag);
        hideLoading();
        dialog.showModal();
        redraw();
    });
}

/* Decode locally, ask which square to keep, and resample it to LCD dimensions.
 * Canvas produces fresh JPEG pixels; stripCanvasJpegMetadata removes the
 * encoder's APP/COM segments before the existing chunk upload begins. */
async function resizeAndCropImage(file) {
    if (!file.type.startsWith('image/')) throw new Error('File is not an image');
    const image = new Image();
    const url = URL.createObjectURL(file);
    try {
        await new Promise((resolve, reject) => {
            image.onload = resolve;
            image.onerror = () => reject(new Error('Failed to load image'));
            image.src = url;
        });
        const crop = await choosePhotoCrop(image);
        showLoading('Processing selected area…');
        const canvas = document.createElement('canvas');
        canvas.width = canvas.height = 240;
        const context = canvas.getContext('2d');
        // JPEG has no alpha channel; transparent input gets a white background.
        context.fillStyle = '#fff'; context.fillRect(0, 0, 240, 240);
        context.drawImage(image, crop.x, crop.y, crop.size, crop.size, 0, 0, 240, 240);
        const encode = quality => new Promise((resolve, reject) => {
            canvas.toBlob(blob => blob ? resolve(blob) :
                reject(new Error('Canvas JPEG encoding failed')), 'image/jpeg', quality);
        });
        let blob = await encode(0.9);
        if (blob.size > 100 * 1024) blob = await encode(0.6);
        if (blob.size > 100 * 1024) throw new Error('Image exceeds the 100KB slot');
        return blob;
    } finally {
        URL.revokeObjectURL(url);
    }
}
