// REQUESTED_CHANGE: persist a cumulative per-photo limit, without changing crop/privacy.
(() => {
    'use strict';
    const maximumKiB = 4294967295;
    const validLimit = value => Number.isInteger(value) && value >= 0 && value <= maximumKiB;

    document.addEventListener('DOMContentLoaded', () => {
        const form = document.getElementById('jpeg-write-form');
        const input = document.getElementById('jpeg-write-limit');
        const button = document.getElementById('jpeg-write-save');
        const status = document.getElementById('jpeg-write-status');
        if (!form || !input || !button || !status) return;

        // Never show a guessed default as the saved preference after a read error.
        button.disabled = true;
        fetch('/get_jpeg_write_limit').then(response => {
            if (!response.ok) throw new Error('Could not read the saved write limit');
            return response.json();
        }).then(data => {
            if (!validLimit(data.limit_kib)) throw new Error('Invalid saved write limit');
            input.value = String(data.limit_kib);
            button.disabled = false;
        }).catch(error => { status.textContent = error.message; });

        // Validate before POST; textContent keeps server errors out of HTML markup.
        form.addEventListener('submit', async event => {
            event.preventDefault();
            const text = input.value.trim();
            const value = Number(text);
            if (!/^[0-9]+$/.test(text) || !validLimit(value)) {
                status.textContent = 'Enter a whole number from 0 to 4294967295 KiB';
                return;
            }
            button.disabled = true;
            try {
                const response = await fetch('/set_jpeg_write_limit', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({limit_kib: value})
                });
                if (!response.ok) throw new Error(await response.text());
                status.textContent = value === 0 ? 'Saved: processing writes and erases are disabled' :
                    `Saved: ${value} KiB per processed photo`;
            } catch (error) {
                status.textContent = `Could not save: ${error.message}`;
            } finally {
                button.disabled = false;
            }
        });
    });
})();
