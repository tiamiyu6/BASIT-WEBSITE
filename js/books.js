const booksTableBody = document.getElementById('booksTableBody');
if (booksTableBody) {
    const STORAGE_KEY = 'accessnetng_sales_records';
    const naira = (n) => `₦${Math.round(Math.abs(n)).toLocaleString()}`;

    const PLAN_PRESETS = [
        { group: 'Weekly Plans', desc: '5GB (5 days)', gb: 5, price: 1000 },
        { group: 'Weekly Plans', desc: '10GB (7 days, 2 devices)', gb: 10, price: 2000 },
        { group: 'Weekly Plans', desc: '15GB Premium (7 days, 2 devices)', gb: 15, price: 3000 },
        { group: 'Weekly Plans', desc: '25GB VIP (14 days, 2 devices)', gb: 25, price: 5000 },
        { group: 'Monthly Plans', desc: '40GB (30 days, 3 devices)', gb: 40, price: 8000 },
        { group: 'Monthly Plans', desc: '50GB Premium (30 days, 3 devices)', gb: 50, price: 10000 },
        { group: 'Monthly Plans', desc: '75GB Big Boys & Big Girls (30 days, 4 devices)', gb: 75, price: 15000 },
        { group: 'Unlimited Plans', desc: 'Unlimited (1 week, 1 device)', gb: 0, price: 8000 },
        { group: 'Unlimited Plans', desc: 'Unlimited (1 week, 2 devices)', gb: 0, price: 15000 },
        { group: 'Unlimited Plans', desc: 'Unlimited (1 month, 2 devices)', gb: 0, price: 32000 },
    ];

    function migrate(list) {
        return list.map((r) => ({
            id: r.id || Date.now() + Math.random(),
            date: r.date,
            type: r.type === 'expense' ? 'expense' : 'income',
            customer: r.customer || '',
            plan: r.plan || '',
            gb: Number(r.gb) || 0,
            amount: Math.abs(Number(r.amount) || 0),
            method: r.method || 'Other',
        }));
    }

    function loadRecords() {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            const parsed = raw ? JSON.parse(raw) : [];
            return Array.isArray(parsed) ? migrate(parsed) : [];
        } catch (e) {
            return [];
        }
    }
    function saveRecords(list) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
    }

    let records = loadRecords();

    function pad(n) { return String(n).padStart(2, '0'); }
    function toDateKey(d) { return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`; }
    function parseLocalDate(dateStr) { return new Date(`${dateStr}T00:00:00`); }
    function getWeekStart(d) {
        const day = d.getDay();
        const diff = (day === 0 ? -6 : 1) - day;
        const monday = new Date(d);
        monday.setDate(d.getDate() + diff);
        monday.setHours(0, 0, 0, 0);
        return monday;
    }

    const today = new Date();
    const todayKey = toDateKey(today);
    const weekStart = getWeekStart(today);
    const weekEnd = new Date(weekStart);
    weekEnd.setDate(weekStart.getDate() + 6);
    const monthKey = todayKey.slice(0, 7);

    function chronoSort(list) {
        return [...list].sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : a.id - b.id));
    }

    function withRunningBalance() {
        let running = 0;
        const map = new Map();
        chronoSort(records).forEach((r) => {
            running += r.type === 'expense' ? -r.amount : r.amount;
            map.set(r.id, running);
        });
        return { map, finalBalance: running };
    }

    function summarize(filterFn) {
        const matched = records.filter(filterFn);
        const income = matched.filter((r) => r.type !== 'expense').reduce((s, r) => s + r.amount, 0);
        const expense = matched.filter((r) => r.type === 'expense').reduce((s, r) => s + r.amount, 0);
        const gb = matched.filter((r) => r.type !== 'expense').reduce((s, r) => s + (r.gb || 0), 0);
        return { count: matched.length, income, expense, net: income - expense, gb };
    }

    function renderBalance(finalBalance) {
        const el = document.getElementById('currentBalance');
        el.textContent = (finalBalance < 0 ? '-' : '') + naira(finalBalance);
        el.classList.toggle('negative', finalBalance < 0);
        const all = summarize(() => true);
        document.getElementById('balanceMeta').textContent =
            `${naira(all.income)} in · ${naira(all.expense)} out · all time`;
    }

    function renderSummary() {
        const buckets = [
            { label: 'Today', data: summarize((r) => r.date === todayKey) },
            { label: 'This Week', data: summarize((r) => { const d = parseLocalDate(r.date); return d >= weekStart && d <= weekEnd; }) },
            { label: 'This Month', data: summarize((r) => r.date.slice(0, 7) === monthKey) },
            { label: 'All Time', data: summarize(() => true) },
        ];
        document.getElementById('booksSummary').innerHTML = buckets.map((b) => `
            <div class="books-stat">
                <span class="books-stat-label">${b.label}</span>
                <span class="books-stat-amount">${b.data.net < 0 ? '-' : ''}${naira(b.data.net)}</span>
                <span class="books-stat-meta">${naira(b.data.income)} in · ${naira(b.data.expense)} out · ${b.data.gb.toLocaleString()} GB · ${b.data.count} txn${b.data.count === 1 ? '' : 's'}</span>
            </div>
        `).join('');
    }

    function renderTrend() {
        const svg = document.getElementById('trendChart');
        const days = [];
        for (let i = 6; i >= 0; i--) {
            const d = new Date(today);
            d.setDate(today.getDate() - i);
            const key = toDateKey(d);
            const net = records
                .filter((r) => r.date === key)
                .reduce((s, r) => s + (r.type === 'expense' ? -r.amount : r.amount), 0);
            days.push({ key, label: d.toLocaleDateString('en-NG', { weekday: 'short' }), net });
        }
        const W = 700, H = 200, padding = 30;
        const maxAbs = Math.max(1, ...days.map((d) => Math.abs(d.net)));
        const barWidth = (W - padding * 2) / days.length - 14;
        const zeroY = H / 2;
        svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
        svg.innerHTML = days.map((d, i) => {
            const x = padding + i * ((W - padding * 2) / days.length) + 7;
            const barH = Math.abs(d.net) / maxAbs * (H / 2 - 30);
            const y = d.net >= 0 ? zeroY - barH : zeroY;
            const cls = d.net >= 0 ? 'books-trend-bar-income' : 'books-trend-bar-expense';
            const valueLabel = d.net !== 0 ? naira(d.net) : '';
            return `
                <rect x="${x}" y="${y}" width="${barWidth}" height="${Math.max(barH, 1)}" rx="3" class="${cls}"></rect>
                <text x="${x + barWidth / 2}" y="${H - 8}" text-anchor="middle" class="books-trend-axis-label">${d.label}</text>
                ${valueLabel ? `<text x="${x + barWidth / 2}" y="${d.net >= 0 ? y - 6 : y + barH + 14}" text-anchor="middle" class="books-trend-value-label">${valueLabel}</text>` : ''}
            `;
        }).join('') + `<line x1="${padding}" y1="${zeroY}" x2="${W - padding}" y2="${zeroY}" stroke="var(--line)" stroke-width="1"></line>`;
    }

    function renderTable(balanceMap) {
        const sorted = chronoSort(records).reverse();
        if (sorted.length === 0) {
            booksTableBody.innerHTML = '<tr class="books-empty-row"><td colspan="9">No transactions recorded yet — add your first entry above.</td></tr>';
            return;
        }
        booksTableBody.innerHTML = sorted.map((r) => {
            const bal = balanceMap.get(r.id) || 0;
            return `
            <tr>
                <td>${r.date}</td>
                <td><span class="books-type-badge books-type-badge-${r.type}">${r.type === 'expense' ? 'Expense' : 'Income'}</span></td>
                <td>${r.customer || '—'}</td>
                <td>${r.plan || '—'}</td>
                <td>${r.gb ? r.gb : '—'}</td>
                <td class="${r.type === 'expense' ? 'books-amount-expense' : ''}">${r.type === 'expense' ? '-' : ''}${naira(r.amount)}</td>
                <td>${r.method}</td>
                <td>${bal < 0 ? '-' : ''}${naira(bal)}</td>
                <td><button type="button" class="books-remove-btn" data-id="${r.id}" aria-label="Delete entry">&times;</button></td>
            </tr>`;
        }).join('');
        booksTableBody.querySelectorAll('.books-remove-btn').forEach((btn) => {
            btn.addEventListener('click', () => {
                const id = Number(btn.dataset.id);
                records = records.filter((r) => r.id !== id);
                saveRecords(records);
                renderAll();
            });
        });
    }

    function renderAll() {
        const { map, finalBalance } = withRunningBalance();
        renderBalance(finalBalance);
        renderSummary();
        renderTrend();
        renderTable(map);
    }

    // Transaction type toggle
    let currentType = 'income';
    const typeButtons = document.querySelectorAll('.books-type-btn');
    const planRow = document.getElementById('bPlanRow');
    const planLabel = document.getElementById('bPlanLabel');
    const amountLabel = document.getElementById('bAmountLabel');
    const gbWrap = document.getElementById('bGbWrap');

    function applyTypeUI() {
        typeButtons.forEach((b) => b.classList.toggle('active', b.dataset.type === currentType));
        const isExpense = currentType === 'expense';
        planRow.style.display = isExpense ? 'none' : '';
        gbWrap.style.display = isExpense ? 'none' : '';
        planLabel.textContent = isExpense ? 'Description' : 'Plan / package';
        document.getElementById('bPlan').placeholder = isExpense ? 'e.g. MikroTik router purchase' : 'e.g. 10GB Weekly';
        amountLabel.textContent = isExpense ? 'Amount spent (₦)' : 'Amount paid (₦)';
    }
    typeButtons.forEach((btn) => {
        btn.addEventListener('click', () => {
            currentType = btn.dataset.type;
            applyTypeUI();
        });
    });
    applyTypeUI();

    // Quick plan picker
    const planPreset = document.getElementById('bPlanPreset');
    const groups = {};
    PLAN_PRESETS.forEach((item, i) => {
        if (!groups[item.group]) groups[item.group] = document.createElement('optgroup');
        groups[item.group].label = item.group;
        const opt = document.createElement('option');
        opt.value = i;
        opt.textContent = `${item.desc} — ₦${item.price.toLocaleString()}`;
        groups[item.group].appendChild(opt);
    });
    Object.values(groups).forEach((g) => planPreset.appendChild(g));

    const amountInput = document.getElementById('bAmount');
    function setAmountValue(n) {
        amountInput.value = n ? Number(n).toLocaleString('en-US') : '';
    }
    planPreset.addEventListener('change', () => {
        const item = PLAN_PRESETS[Number(planPreset.value)];
        if (!item) return;
        document.getElementById('bPlan').value = item.desc;
        document.getElementById('bGb').value = item.gb || '';
        setAmountValue(item.price);
    });

    amountInput.addEventListener('input', () => {
        const digitsOnly = amountInput.value.replace(/[^\d]/g, '');
        amountInput.value = digitsOnly ? Number(digitsOnly).toLocaleString('en-US') : '';
    });

    const dateInput = document.getElementById('bDate');
    dateInput.value = todayKey;

    document.getElementById('addEntry').addEventListener('click', () => {
        const date = dateInput.value || todayKey;
        const customer = document.getElementById('bCustomer').value.trim();
        const plan = document.getElementById('bPlan').value.trim();
        const gb = currentType === 'expense' ? 0 : (Number(document.getElementById('bGb').value) || 0);
        const amount = Number(amountInput.value.replace(/,/g, '')) || 0;
        const method = document.getElementById('bMethod').value;

        if (amount <= 0) {
            amountInput.focus();
            return;
        }

        const isDuplicate = records.some((r) =>
            r.date === date && r.amount === amount && r.type === currentType &&
            r.customer.toLowerCase() === customer.toLowerCase());
        if (isDuplicate) {
            const proceed = confirm('This looks like a duplicate of an existing entry (same date, amount, customer, and type). Add it anyway?');
            if (!proceed) return;
        }

        records.push({ id: Date.now(), date, type: currentType, customer, plan, gb, amount, method });
        saveRecords(records);

        document.getElementById('bCustomer').value = '';
        document.getElementById('bPlan').value = '';
        document.getElementById('bGb').value = '';
        amountInput.value = '';
        planPreset.value = '';
        dateInput.value = todayKey;

        renderAll();
    });

    function download(filename, content, mime) {
        const blob = new Blob([content], { type: mime });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    document.getElementById('exportCsv').addEventListener('click', () => {
        const header = 'Date,Type,Customer,Plan,GB,Amount,Method\n';
        const rows = chronoSort(records)
            .map((r) => [r.date, r.type, r.customer, r.plan, r.gb, r.amount, r.method]
                .map((v) => `"${String(v ?? '').replace(/"/g, '""')}"`)
                .join(','))
            .join('\n');
        download(`accessnetng-sales-${todayKey}.csv`, header + rows, 'text/csv');
    });

    document.getElementById('backupJson').addEventListener('click', () => {
        download(`accessnetng-sales-backup-${todayKey}.json`, JSON.stringify(records, null, 2), 'application/json');
    });

    document.getElementById('restoreJson').addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = () => {
            try {
                const imported = JSON.parse(reader.result);
                if (!Array.isArray(imported)) throw new Error('Invalid file');
                const replace = confirm(`Import ${imported.length} record(s)? This will replace all current records — export a backup first if unsure.`);
                if (replace) {
                    records = migrate(imported);
                    saveRecords(records);
                    renderAll();
                }
            } catch (err) {
                alert('Could not read that file — make sure it\'s a backup exported from this page.');
            }
            e.target.value = '';
        };
        reader.readAsText(file);
    });

    document.getElementById('clearAll').addEventListener('click', () => {
        if (records.length === 0) return;
        const sure = confirm('Delete ALL records from this browser? Export a backup first if you want to keep them. This cannot be undone.');
        if (sure) {
            records = [];
            saveRecords(records);
            renderAll();
        }
    });

    renderAll();
}
