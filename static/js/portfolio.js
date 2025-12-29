// State
let allPositions = [];
let hiddenTickers = [];
let sortState = { field: 'pl', direction: 'desc' };
let refreshIntervalId = null;

// Field Mapping for Sorting
const fieldMap = {
    'name': (pos) => (pos.instrument ? pos.instrument.name : (pos.name || '')).toLowerCase(),
    'quantity': (pos) => parseFloat(pos.quantity || 0),
    'avgPrice': (pos) => parseFloat(pos.averagePricePaid || pos.averagePrice || 0),
    'currentPrice': (pos) => parseFloat(pos.currentPrice || 0),
    'subtotal': (pos) => {
        if (pos.walletImpact) return parseFloat(pos.walletImpact.currentValue || 0);
        return (parseFloat(pos.quantity || 0) * parseFloat(pos.currentPrice || 0));
    },
    'pl': (pos) => {
        if (pos.walletImpact) return parseFloat(pos.walletImpact.unrealizedProfitLoss || 0);
        return parseFloat(pos.ppl || 0);
    }
};

async function initPortfolio() {
    initEventListeners();
    await loadSettings();
    await fetchPositions();

    // Auto Refresh default 10s (managed by input)
    setupRefresh(10);
}

function initEventListeners() {
    const refreshInput = document.getElementById('refreshRate');
    if (refreshInput) {
        refreshInput.addEventListener('change', () => setupRefresh(parseInt(refreshInput.value)));
    }

    document.getElementById('trackingToggle').addEventListener('change', (e) => {
        updateTracking(e.target.checked);
    });

    const accountSelect = document.getElementById('accountSelect');
    if (accountSelect) {
        accountSelect.addEventListener('change', (e) => switchAccount(e.target.value));
    }
}

function setupRefresh(seconds) {
    if (seconds < 5) seconds = 5;
    if (seconds > 300) seconds = 300;

    if (refreshIntervalId) clearInterval(refreshIntervalId);
    refreshIntervalId = setInterval(fetchPositions, seconds * 1000);
}

async function loadSettings() {
    try {
        const data = await ApiClient.getSettings();
        document.getElementById('trackingToggle').checked = data.tracking;
        hiddenTickers = data.hidden_tickers || [];

        if (data.tracking) {
            document.getElementById('returnsBar').style.display = 'flex';
            fetchReturns();
        }

        // Load account status
        const acc = await ApiClient.getAccountStatus();
        updateAccountSwitcher(acc);
    } catch (e) {
        console.error(e);
    }
}

function updateAccountSwitcher(status) {
    const switcher = document.getElementById('accountSwitcher');
    const select = document.getElementById('accountSelect');

    if (status.available.length > 1) {
        switcher.style.display = 'block';
        select.innerHTML = status.available.map(a =>
            `<option value="${a}" ${a === status.current ? 'selected' : ''}>${a}</option>`
        ).join('');
    }
}

async function switchAccount(account) {
    try {
        await ApiClient.switchAccount(account);
        fetchPositions();
    } catch (e) {
        alert("Failed to switch account");
    }
}

async function updateTracking(enabled) {
    try {
        await ApiClient.updateSettings({ tracking: enabled });
        const bar = document.getElementById('returnsBar');
        bar.style.display = enabled ? 'flex' : 'none';
        if (enabled) fetchReturns();
    } catch (e) { console.error(e); }
}

async function fetchPositions() {
    try {
        const data = await ApiClient.getPositions();
        allPositions = Array.isArray(data) ? data : (data.items || []);
        renderTable();

        if (document.getElementById('trackingToggle').checked) {
            fetchReturns();
        }
    } catch (e) {
        document.getElementById('content').innerHTML = `<div class="error-msg">${e.message}</div>`;
    }
}

async function fetchReturns() {
    try {
        const data = await ApiClient.getReturns();
        const periods = ['1h', '24h', '7d', '30d', '1y'];

        let html = '';
        periods.forEach(p => {
            const val = data[p];
            if (val !== undefined) {
                html += `
                    <div class="return-item">
                        <span class="return-label">${p}</span>
                        <span class="return-val ${Formatters.colorClass(val)}">${Formatters.percent(val)}</span>
                    </div>
                `;
            }
        });
        document.getElementById('returnsBar').innerHTML = html || '<span style="color:var(--text-secondary)">No history yet</span>';
    } catch (e) { console.error(e); }
}

function handleSort(field) {
    if (sortState.field === field) {
        sortState.direction = sortState.direction === 'desc' ? 'asc' : 'desc';
    } else {
        sortState.field = field;
        sortState.direction = field === 'name' ? 'asc' : 'desc';
    }
    renderTable();
}

function renderTable() {
    const content = document.getElementById('content');

    // Filter
    const positions = allPositions.filter(pos => {
        const ticker = pos.instrument?.ticker || pos.ticker;
        return !hiddenTickers.includes(ticker);
    });

    if (positions.length === 0) {
        content.innerHTML = '<div class="loading">No positions found (or all hidden).</div>';
        document.getElementById('totalValue').textContent = Formatters.currency(0);
        return;
    }

    // Sort
    positions.sort((a, b) => {
        const valA = fieldMap[sortState.field](a);
        const valB = fieldMap[sortState.field](b);
        return sortState.direction === 'asc' ? (valA > valB ? 1 : -1) : (valA < valB ? 1 : -1);
    });

    // Totals
    let totalVal = 0;
    let totalPl = 0;

    let html = `
        <table>
            <thead>
                <tr>
                    <th onclick="handleSort('name')" class="header-sortable" style="text-align: left; cursor:pointer;">Name</th>
                    <th onclick="handleSort('quantity')" class="text-right cursor-pointer">Quantity</th>
                    <th onclick="handleSort('avgPrice')" class="text-right cursor-pointer">Avg Price</th>
                    <th onclick="handleSort('currentPrice')" class="text-right cursor-pointer">Current</th>
                    <th onclick="handleSort('subtotal')" class="text-right cursor-pointer">Holdings</th>
                    <th onclick="handleSort('pl')" class="text-right col-pl cursor-pointer">P/L</th>
                </tr>
            </thead>
            <tbody>
    `;

    positions.forEach(pos => {
        const ticker = pos.instrument?.ticker || pos.ticker;
        const name = pos.instrument?.name || pos.name || ticker;
        const qty = parseFloat(pos.quantity || 0);
        const avg = parseFloat(pos.averagePricePaid || pos.averagePrice || 0);
        const curr = parseFloat(pos.currentPrice || 0);

        let subtotal = 0;
        let pl = 0;
        let currency = 'GBP';

        if (pos.walletImpact) {
            subtotal = parseFloat(pos.walletImpact.currentValue || 0);
            pl = parseFloat(pos.walletImpact.unrealizedProfitLoss || 0);
            currency = pos.walletImpact.currency || 'GBP';
        } else {
            subtotal = qty * curr;
            pl = parseFloat(pos.ppl || 0);
        }

        totalVal += subtotal;
        totalPl += pl;

        html += `
            <tr onclick="window.location.href='/ticker/${ticker}'" style="cursor: pointer;">
                <td>
                    <div style="font-weight: 500;">${name}</div>
                    <div class="ticker" style="font-size: 0.8em;">${ticker}</div>
                </td>
                <td class="text-right">${Formatters.number(qty, 4)}</td>
                <td class="text-right">${Formatters.number(avg)}</td>
                <td class="text-right">${Formatters.number(curr)}</td>
                <td class="text-right" style="font-weight: 600;">${Formatters.number(subtotal)} <small>${currency}</small></td>
                <td class="text-right ${Formatters.colorClass(pl)}">
                    <div style="font-weight: 600;">${Formatters.number(pl)}</div>
                    <div style="font-size: 0.8em;">${Formatters.percent((pl / (subtotal - pl)) * 100)}</div>
                </td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    content.innerHTML = html;

    document.getElementById('totalValue').textContent = Formatters.currency(totalVal);
    document.getElementById('totalReturn').textContent = Formatters.number(totalPl);
    document.getElementById('totalReturn').className = Formatters.colorClass(totalPl);
}


// Visibility Modal Logic
function openVisibilityModal() {
    UI.showModal('visibilityModal');
    renderVisibilityList();
}

function closeVisibilityModal() {
    UI.closeModal('visibilityModal');
}

function renderVisibilityList() {
    const list = document.getElementById('visibilityList');
    if (!allPositions.length) {
        list.innerHTML = 'No items';
        return;
    }

    const sorted = [...allPositions].sort((a, b) => (a.ticker || '').localeCompare(b.ticker || ''));

    let html = '';
    sorted.forEach(pos => {
        const ticker = pos.instrument?.ticker || pos.ticker;
        const isHidden = hiddenTickers.includes(ticker);

        html += `
            <div class="visibility-item" style="display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.05);">
                <span>${ticker}</span>
                <label class="switch">
                    <input type="checkbox" ${!isHidden ? 'checked' : ''} data-ticker="${ticker}">
                    <span class="slider"></span>
                </label>
            </div>
        `;
    });
    list.innerHTML = html;
}

async function saveVisibility() {
    const inputs = document.querySelectorAll('#visibilityList input');
    const newHidden = [];
    inputs.forEach(inp => {
        if (!inp.checked) newHidden.push(inp.getAttribute('data-ticker'));
    });

    hiddenTickers = newHidden;
    try {
        await ApiClient.updateSettings({ hidden_tickers: newHidden });
        renderTable();
        closeVisibilityModal();
    } catch (e) { alert("Failed to save"); }
}

// Global exposure for HTML inline access (helpers)
window.initPortfolio = initPortfolio;
window.handleSort = handleSort;
window.openVisibilityModal = openVisibilityModal;
window.closeVisibilityModal = closeVisibilityModal;
window.saveVisibility = saveVisibility;
window.switchAccount = switchAccount;
window.fetchPositions = fetchPositions;

document.addEventListener('DOMContentLoaded', initPortfolio);
