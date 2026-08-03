const CATALOG = [
    { group: 'Weekly Plans', desc: '5GB (5 days)', price: 1000 },
    { group: 'Weekly Plans', desc: '10GB (7 days, 2 devices)', price: 2000 },
    { group: 'Weekly Plans', desc: '15GB Premium (7 days, 2 devices)', price: 3000 },
    { group: 'Weekly Plans', desc: '25GB VIP (14 days, 2 devices)', price: 5000 },
    { group: 'Monthly Plans', desc: '40GB (30 days, 3 devices)', price: 8000 },
    { group: 'Monthly Plans', desc: '50GB Premium (30 days, 3 devices)', price: 10000 },
    { group: 'Monthly Plans', desc: '75GB Big Boys & Big Girls (30 days, 4 devices)', price: 15000 },
    { group: 'Unlimited Plans', desc: 'Unlimited (1 week, 1 device)', price: 8000 },
    { group: 'Unlimited Plans', desc: 'Unlimited (1 week, 2 devices)', price: 15000 },
    { group: 'Unlimited Plans', desc: 'Unlimited (1 month, 2 devices)', price: 32000 },
];

const itemCatalog = document.getElementById('itemCatalog');
if (itemCatalog) {
    const groups = {};
    CATALOG.forEach((item, i) => {
        if (!groups[item.group]) groups[item.group] = document.createElement('optgroup');
        groups[item.group].label = item.group;
        const opt = document.createElement('option');
        opt.value = i;
        opt.textContent = `${item.desc} — ₦${item.price.toLocaleString()}`;
        groups[item.group].appendChild(opt);
    });
    Object.values(groups).forEach((g) => itemCatalog.appendChild(g));

    let items = [];
    const naira = (n) => `₦${n.toLocaleString()}`;

    const quoteNumber = `ANQ-${new Date().toISOString().slice(0, 10).replace(/-/g, '')}-${Math.floor(100 + Math.random() * 900)}`;
    document.getElementById('quoteNumber').textContent = `Quote #${quoteNumber}`;
    document.getElementById('quoteDate').textContent = new Date().toLocaleDateString('en-NG', { year: 'numeric', month: 'long', day: 'numeric' });

    function render() {
        const body = document.getElementById('quoteItemsBody');
        body.innerHTML = '';
        if (items.length === 0) {
            body.innerHTML = '<tr class="quote-empty-row"><td colspan="5">No items added yet — add a plan or custom item to build your quote.</td></tr>';
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
                body.appendChild(tr);
            });
        }
        const total = items.reduce((sum, item) => sum + item.qty * item.price, 0);
        document.getElementById('quoteSubtotal').textContent = naira(total);
        document.getElementById('quoteTotal').textContent = naira(total);

        body.querySelectorAll('.quote-item-qty').forEach((input) => {
            input.addEventListener('change', (e) => {
                const i = Number(e.target.dataset.i);
                const qty = Math.max(1, Number(e.target.value) || 1);
                items[i].qty = qty;
                render();
            });
        });
        body.querySelectorAll('.quote-remove-btn').forEach((btn) => {
            btn.addEventListener('click', (e) => {
                const i = Number(e.target.dataset.i);
                items.splice(i, 1);
                render();
            });
        });
        updateEmailLink();
    }

    document.getElementById('addCatalogItem').addEventListener('click', () => {
        const catalogItem = CATALOG[Number(itemCatalog.value)];
        if (!catalogItem) return;
        const existing = items.find((it) => it.desc === catalogItem.desc && it.price === catalogItem.price);
        if (existing) {
            existing.qty += 1;
        } else {
            items.push({ desc: catalogItem.desc, price: catalogItem.price, qty: 1 });
        }
        render();
    });

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

    document.getElementById('addCustomItem').addEventListener('click', () => {
        addFreeformItem('customDesc', 'customPrice', 'customQty');
    });

    const materialPreset = document.getElementById('materialPreset');
    materialPreset.addEventListener('change', () => {
        if (materialPreset.value) {
            document.getElementById('materialDesc').value = materialPreset.value;
            document.getElementById('materialPrice').focus();
        }
    });
    document.getElementById('addMaterialItem').addEventListener('click', () => {
        addFreeformItem('materialDesc', 'materialPrice', 'materialQty');
        materialPreset.value = '';
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
