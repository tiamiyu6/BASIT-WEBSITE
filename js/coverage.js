const coverageMapEl = document.getElementById('coverageMap');
if (coverageMapEl) {
    const HUB = { name: 'Downtown Apartment', sub: 'Main server · Malate, KWASU' };

    const NODES = [
        { name: 'Downtown Apartment 2', area: 'Malate, KWASU', status: 'live' },
        { name: 'Folab', area: 'Malate, KWASU', status: 'live', since: 'Live since 2025' },
        { name: 'Bob Sam', area: 'Malate, KWASU', status: 'live' },
        { name: 'Kik Apartment', area: 'Malate, KWASU', status: 'live' },
        { name: 'Ife Hostel', area: 'Malate, KWASU', status: 'live' },
        { name: 'Jagun Hostel', area: 'Malate, KWASU', status: 'live' },
        { name: 'Joseph Hostel', area: 'Malate, KWASU', status: 'live' },
        { name: 'Alajitaiwo Hostel', area: 'Malate, KWASU', status: 'live' },
        { name: 'White Bridge', area: 'Malate, KWASU', status: 'live' },
        { name: 'Sandra', area: 'Malate, KWASU', status: 'live' },
        { name: 'House 22', area: 'Malate, KWASU', status: 'live' },
        { name: 'Jay Jay Hostel', area: 'Malate, KWASU', status: 'live' },
        { name: 'Downtown Apartment 3', area: 'Malate, KWASU', status: 'soon' },
        { name: 'Downtown Apartment 4', area: 'Malate, KWASU', status: 'soon' },
        { name: 'Downtown Apartment 5', area: 'Malate, KWASU', status: 'soon' },
        { name: 'Fadaka Hostel', area: 'Malate, KWASU', status: 'soon' },
        { name: 'Atinuke', area: 'Malate, KWASU', status: 'soon' },
    ];

    const SVG_NS = 'http://www.w3.org/2000/svg';
    const W = 800;
    const H = 460;
    const CX = W / 2;
    const CY = H / 2;
    const R = 195;

    function svgEl(tag, attrs) {
        const e = document.createElementNS(SVG_NS, tag);
        Object.keys(attrs).forEach((k) => e.setAttribute(k, attrs[k]));
        return e;
    }

    NODES.forEach((node, i) => {
        const angle = (i / NODES.length) * Math.PI * 2 - Math.PI / 2;
        node.x = CX + R * Math.cos(angle);
        node.y = CY + R * Math.sin(angle) * 0.82;
    });

    const tooltip = document.getElementById('coverageTooltip');

    function showTooltip(node) {
        const svgRect = coverageMapEl.getBoundingClientRect();
        const scaleX = svgRect.width / W;
        const scaleY = svgRect.height / H;
        tooltip.querySelector('.coverage-tooltip-name').textContent = node.name;
        tooltip.querySelector('.coverage-tooltip-meta').textContent =
            `${node.area} · ${node.status === 'soon' ? 'Coming soon' : (node.since || 'Live')}`;
        tooltip.style.left = `${node.x * scaleX}px`;
        tooltip.style.top = `${node.y * scaleY}px`;
        tooltip.classList.add('visible');
        tooltip.classList.toggle('flip', node.x > CX * 1.15);
    }
    function hideTooltip() {
        tooltip.classList.remove('visible');
    }

    function renderMap() {
        coverageMapEl.setAttribute('viewBox', `0 0 ${W} ${H}`);
        coverageMapEl.innerHTML = '';

        NODES.forEach((node) => {
            coverageMapEl.appendChild(svgEl('line', {
                x1: CX, y1: CY, x2: node.x, y2: node.y,
                class: `coverage-line coverage-line-${node.status}`,
                'data-status': node.status,
            }));
        });

        const hubGroup = svgEl('g', { class: 'coverage-hub' });
        hubGroup.appendChild(svgEl('circle', { cx: CX, cy: CY, r: 16, class: 'coverage-hub-pulse' }));
        hubGroup.appendChild(svgEl('circle', { cx: CX, cy: CY, r: 7, class: 'coverage-hub-dot' }));
        const hubLabel = svgEl('text', { x: CX, y: CY - 22, class: 'coverage-hub-label', 'text-anchor': 'middle' });
        hubLabel.textContent = HUB.name;
        const hubSub = svgEl('text', { x: CX, y: CY + 30, class: 'coverage-hub-sub', 'text-anchor': 'middle' });
        hubSub.textContent = HUB.sub;
        hubGroup.appendChild(hubLabel);
        hubGroup.appendChild(hubSub);
        coverageMapEl.appendChild(hubGroup);

        NODES.forEach((node) => {
            const g = svgEl('g', {
                class: `coverage-node coverage-node-${node.status}`,
                tabindex: '0',
                role: 'button',
                'aria-label': `${node.name}, ${node.area} — ${node.status === 'soon' ? 'coming soon' : 'live'}`,
                'data-status': node.status,
            });
            g.appendChild(svgEl('circle', { cx: node.x, cy: node.y, r: 12, class: 'coverage-node-hit' }));
            g.appendChild(svgEl('circle', { cx: node.x, cy: node.y, r: 6, class: 'coverage-node-dot' }));
            g.addEventListener('mouseenter', () => showTooltip(node));
            g.addEventListener('focus', () => showTooltip(node));
            g.addEventListener('mouseleave', hideTooltip);
            g.addEventListener('blur', hideTooltip);
            g.addEventListener('click', () => showTooltip(node));
            coverageMapEl.appendChild(g);
        });
    }

    function renderList() {
        const listEl = document.getElementById('coverageList');
        const live = NODES.filter((n) => n.status === 'live');
        const soon = NODES.filter((n) => n.status === 'soon');

        function itemHtml(node) {
            return `<div class="coverage-list-item" data-status="${node.status}">
                <span class="coverage-list-dot coverage-list-dot-${node.status}"></span>
                <div>
                    <strong>${node.name}</strong>
                    <span>${node.area}${node.since ? ' · ' + node.since : ''}</span>
                </div>
            </div>`;
        }

        listEl.innerHTML = `
            <div class="coverage-list-col" data-status="live">
                <h4 class="coverage-list-heading"><span class="coverage-list-dot coverage-list-dot-live"></span>Live Now</h4>
                <div class="coverage-list-item" data-status="live">
                    <span class="coverage-list-dot coverage-list-dot-hub"></span>
                    <div><strong>${HUB.name}</strong><span>${HUB.sub}</span></div>
                </div>
                ${live.map(itemHtml).join('')}
            </div>
            <div class="coverage-list-col" data-status="soon">
                <h4 class="coverage-list-heading"><span class="coverage-list-dot coverage-list-dot-soon"></span>Coming Soon</h4>
                ${soon.map(itemHtml).join('')}
            </div>
        `;
    }

    function applyFilter(filter) {
        coverageMapEl.querySelectorAll('.coverage-node').forEach((g) => {
            g.classList.toggle('dimmed', filter !== 'all' && g.dataset.status !== filter);
        });
        coverageMapEl.querySelectorAll('.coverage-line').forEach((line) => {
            line.classList.toggle('dimmed', filter !== 'all' && line.dataset.status !== filter);
        });
        document.querySelectorAll('.coverage-list-col').forEach((col) => {
            col.hidden = filter !== 'all' && col.dataset.status !== filter;
        });
        hideTooltip();
    }

    document.querySelectorAll('.coverage-tab').forEach((tab) => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.coverage-tab').forEach((t) => t.classList.remove('active'));
            tab.classList.add('active');
            applyFilter(tab.dataset.filter);
        });
    });

    renderMap();
    renderList();
}
