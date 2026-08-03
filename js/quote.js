const quoteItemsBody = document.getElementById('quoteItemsBody');
if (quoteItemsBody) {
    let items = [];
    const naira = (n) => `₦${n.toLocaleString()}`;

    const quoteNumber = `ANQ-${new Date().toISOString().slice(0, 10).replace(/-/g, '')}-${Math.floor(100 + Math.random() * 900)}`;
    document.getElementById('quoteNumber').textContent = `Quote #${quoteNumber}`;
    document.getElementById('quoteDate').textContent = new Date().toLocaleDateString('en-NG', { year: 'numeric', month: 'long', day: 'numeric' });

    function render() {
        quoteItemsBody.innerHTML = '';
        if (items.length === 0) {
            quoteItemsBody.innerHTML = '<tr class="quote-empty-row"><td colspan="5">No items added yet — add a service, material, or solar item to build your quote.</td></tr>';
        } else {
            items.forEach((item, i) => {
                const tr = document.createElement('tr');
                const lineTotal = item.qty * item.price;
                tr.innerHTML = `
                    <td>${item.desc}</td>
                    <td><input type="number" class="quote-item-qty" min="1" value="${item.qty}" data-i="${i}"></td>
                    <td>${naira(item.price)}</td>
                    <td>${naira(lineTotal)}</td>
                    <td class="quote-no-print"><button type="button" class="quote-remove-btn" data-i="${i}" aria-label="Remove item">&times;</button></td>
                `;
                quoteItemsBody.appendChild(tr);
            });
        }
        const total = items.reduce((sum, item) => sum + item.qty * item.price, 0);
        document.getElementById('quoteSubtotal').textContent = naira(total);
        document.getElementById('quoteTotal').textContent = naira(total);

        quoteItemsBody.querySelectorAll('.quote-item-qty').forEach((input) => {
            input.addEventListener('change', (e) => {
                const i = Number(e.target.dataset.i);
                const qty = Math.max(1, Number(e.target.value) || 1);
                items[i].qty = qty;
                render();
            });
        });
        quoteItemsBody.querySelectorAll('.quote-remove-btn').forEach((btn) => {
            btn.addEventListener('click', (e) => {
                const i = Number(e.target.dataset.i);
                items.splice(i, 1);
                render();
            });
        });
        updateEmailLink();
    }

    function addFreeformItem(descId, priceId, qtyId) {
        const descEl = document.getElementById(descId);
        const desc = descEl.value.trim();
        const price = Math.max(0, Number(document.getElementById(priceId).value) || 0);
        const qty = Math.max(1, Number(document.getElementById(qtyId).value) || 1);
        if (!desc) {
            descEl.focus();
            return;
        }
        items.push({ desc, price, qty });
        descEl.value = '';
        document.getElementById(priceId).value = '';
        document.getElementById(qtyId).value = '1';
        render();
    }

    function bindPreset(presetId, descId, priceId) {
        const preset = document.getElementById(presetId);
        preset.addEventListener('change', () => {
            if (preset.value) {
                document.getElementById(descId).value = preset.value;
                document.getElementById(priceId).focus();
            }
        });
        return preset;
    }

    const servicePreset = bindPreset('servicePreset', 'customDesc', 'customPrice');
    document.getElementById('addCustomItem').addEventListener('click', () => {
        addFreeformItem('customDesc', 'customPrice', 'customQty');
        servicePreset.value = '';
    });

    const materialPreset = bindPreset('materialPreset', 'materialDesc', 'materialPrice');
    document.getElementById('addMaterialItem').addEventListener('click', () => {
        addFreeformItem('materialDesc', 'materialPrice', 'materialQty');
        materialPreset.value = '';
    });

    const solarPreset = bindPreset('solarPreset', 'solarDesc', 'solarPrice');
    document.getElementById('addSolarItem').addEventListener('click', () => {
        addFreeformItem('solarDesc', 'solarPrice', 'solarQty');
        solarPreset.value = '';
    });

    function bindPreviewField(inputId, previewId, format) {
        const input = document.getElementById(inputId);
        const preview = document.getElementById(previewId);
        input.addEventListener('input', () => {
            preview.textContent = input.value.trim() ? format(input.value.trim()) : '';
        });
    }
    bindPreviewField('qClientName', 'previewClientName', (v) => v);
    document.getElementById('qClientName').addEventListener('input', (e) => {
        document.getElementById('previewClientName').textContent = e.target.value.trim() || '—';
    });
    bindPreviewField('qBuilding', 'previewBuilding', (v) => v);
    bindPreviewField('qEmail', 'previewEmail', (v) => v);
    bindPreviewField('qPhone', 'previewPhone', (v) => v);

    document.getElementById('qNotes').addEventListener('input', (e) => {
        const wrap = document.getElementById('previewNotesWrap');
        const text = e.target.value.trim();
        wrap.hidden = !text;
        document.getElementById('previewNotes').textContent = text;
    });

    function siteDetailsSummary() {
        const hostels = document.getElementById('qHostelsOnStreet').value.trim();
        const rooms = document.getElementById('qRoomCount').value.trim();
        const cluster = document.getElementById('qCluster').value;
        const parts = [];
        if (hostels) parts.push(`${hostels} hostel${hostels === '1' ? '' : 's'} on this street`);
        if (cluster === 'Yes') parts.push('part of a cluster of buildings');
        if (cluster === 'No') parts.push('standalone building');
        if (rooms) parts.push(`${rooms} room${rooms === '1' ? '' : 's'} needing coverage`);
        return parts.join(' · ');
    }

    function updateSiteDetails() {
        const summary = siteDetailsSummary();
        document.getElementById('previewSiteWrap').hidden = !summary;
        document.getElementById('previewSiteDetails').textContent = summary;
    }
    ['qHostelsOnStreet', 'qRoomCount'].forEach((id) => {
        document.getElementById(id).addEventListener('input', updateSiteDetails);
    });
    document.getElementById('qCluster').addEventListener('change', updateSiteDetails);

    document.getElementById('printQuote').addEventListener('click', () => window.print());

    function updateEmailLink() {
        const clientName = document.getElementById('qClientName').value.trim() || 'New Client';
        const building = document.getElementById('qBuilding').value.trim();
        const email = document.getElementById('qEmail').value.trim();
        const phone = document.getElementById('qPhone').value.trim();
        const notes = document.getElementById('qNotes').value.trim();
        const total = items.reduce((sum, item) => sum + item.qty * item.price, 0);

        let body = `Quote #${quoteNumber}\n\nClient: ${clientName}\n`;
        if (building) body += `Building: ${building}\n`;
        if (email) body += `Email: ${email}\n`;
        if (phone) body += `Phone: ${phone}\n`;
        const siteSummary = siteDetailsSummary();
        if (siteSummary) body += `Site details: ${siteSummary}\n`;
        body += `\nItems:\n`;
        if (items.length === 0) {
            body += `(no items added yet)\n`;
        } else {
            items.forEach((item) => {
                body += `- ${item.desc} x${item.qty} — ${naira(item.qty * item.price)}\n`;
            });
        }
        body += `\nTotal: ${naira(total)}\n`;
        if (notes) body += `\nNotes: ${notes}\n`;

        const subject = `Quote Request — ${clientName}`;
        document.getElementById('emailQuote').href =
            `mailto:tiamiyubasit47@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    }

    ['qClientName', 'qBuilding', 'qEmail', 'qPhone', 'qNotes', 'qHostelsOnStreet', 'qRoomCount'].forEach((id) => {
        document.getElementById(id).addEventListener('input', updateEmailLink);
    });
    document.getElementById('qCluster').addEventListener('change', updateEmailLink);

    render();
}
