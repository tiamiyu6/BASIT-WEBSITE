const booksTableBody = document.getElementById('booksTableBody');
if (booksTableBody) {
    const STORAGE_KEY = 'accessnetng_sales_records';
    const naira = (n) => `₦${Math.round(n).toLocaleString()}`;

    function loadRecords() {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            const parsed = raw ? JSON.parse(raw) : [];
            return Array.isArray(parsed) ? parsed : [];
        } catch (e) {
            return [];
        }
    }
    function saveRecords(records) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(records));
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

    function summarize(filterFn) {
        const matched = records.filter(filterFn);
        const amount = matched.reduce((sum, r) => sum + (Number(r.amount) || 0), 0);
        const gb = matched.reduce((sum, r) => sum + (Number(r.gb) || 0), 0);
        return { count: matched.length, amount, gb };
    }

    function renderSummary() {
        const todaySum = summarize((r) => r.date === todayKey);
        const weekSum = summarize((r) => {
            const d = parseLocalDate(r.date);
            return d >= weekStart && d <= weekEnd;
        });
        const monthSum = summarize((r) => r.date.slice(0, 7) === monthKey);
        const allSum = summarize(() => true);

        const cards = [
            { label: 'Today', data: todaySum },
            { label: 'This Week', data: weekSum },
            { label: 'This Month', data: monthSum },
            { label: 'All Time', data: allSum },
        ];

        document.getElementById('booksSummary').innerHTML = cards.map((c) => `
            <div class="books-stat">
                <span class="books-stat-label">${c.label}</span>
                <span class="books-stat-amount">${naira(c.data.amount)}</span>
                <span class="books-stat-meta">${c.data.gb.toLocaleString()} GB · ${c.data.count} sale${c.data.count === 1 ? '' : 's'}</span>
            </div>
        `).join('');
    }

    function renderTable() {
        const sorted = [...records].sort((a, b) => (a.date < b.date ? 1 : a.date > b.date ? -1 : b.id - a.id));
        if (sorted.length === 0) {
            booksTableBody.innerHTML = '<tr class="books-empty-row"><td colspan="7">No sales recorded yet — add your first entry above.</td></tr>';
            return;
        }
        booksTableBody.innerHTML = sorted.map((r) => `
            <tr>
                <td>${r.date}</td>
                <td>${r.customer || '—'}</td>
                <td>${r.plan || '—'}</td>
                <td>${r.gb ? r.gb : '—'}</td>
                <td>${naira(r.amount)}</td>
                <td>${r.method}</td>
                <td><button type="button" class="books-remove-btn" data-id="${r.id}" aria-label="Delete entry">&times;</button></td>
            </tr>
        `).join('');
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
        renderSummary();
        renderTable();
    }

    // Default date field to today, comma-format the amount field
    const dateInput = document.getElementById('bDate');
    dateInput.value = todayKey;

    const amountInput = document.getElementById('bAmount');
    amountInput.addEventListener('input', () => {
        const digitsOnly = amountInput.value.replace(/[^\d]/g, '');
        amountInput.value = digitsOnly ? Number(digitsOnly).toLocaleString('en-US') : '';
    });

    document.getElementById('addEntry').addEventListener('click', () => {
        const date = dateInput.value || todayKey;
        const customer = document.getElementById('bCustomer').value.trim();
        const plan = document.getElementById('bPlan').value.trim();
        const gb = Number(document.getElementById('bGb').value) || 0;
        const amount = Number(amountInput.value.replace(/,/g, '')) || 0;
        const method = document.getElementById('bMethod').value;

        if (amount <= 0) {
            amountInput.focus();
            return;
        }

        records.push({ id: Date.now(), date, customer, plan, gb, amount, method });
        saveRecords(records);

        document.getElementById('bCustomer').value = '';
        document.getElementById('bPlan').value = '';
        document.getElementById('bGb').value = '';
        amountInput.value = '';
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
        const header = 'Date,Customer,Plan,GB,Amount,Method\n';
        const rows = records
            .slice()
            .sort((a, b) => (a.date < b.date ? -1 : 1))
            .map((r) => [r.date, r.customer, r.plan, r.gb, r.amount, r.method]
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
                    records = imported;
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
        const sure = confirm('Delete ALL sales records from this browser? Export a backup first if you want to keep them. This cannot be undone.');
        if (sure) {
            records = [];
            saveRecords(records);
            renderAll();
        }
    });

    renderAll();
}
