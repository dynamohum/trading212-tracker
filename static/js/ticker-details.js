async function initDetails(ticker) {
    loadDetails(ticker);
    loadDividends(ticker);
    loadHistory(ticker, '1y');
}

async function loadDetails(ticker) {
    try {
        const data = await ApiClient.getTickerDetails(ticker);
        if (data.name) {
            document.getElementById('itemName').innerHTML = `${data.name} <span class="ticker-badge">${ticker}</span>`;
        }
        if (data.type) {
            document.getElementById('itemDesc').innerText = `${data.type} • ${data.currencyCode || ''} • ${data.shortName || ''}`;
        }
    } catch (e) { console.error(e); }
}

async function loadDividends(ticker) {
    try {
        const data = await ApiClient.getTickerDividends(ticker);
        const items = data.items || [];

        const divContent = document.getElementById('dividendsContent');

        if (items.length === 0) {
            divContent.innerHTML = '<div style="color: var(--text-secondary);">No dividends found.</div>';
            return;
        }

        let html = `
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Amount</th>
                        <th>Type</th>
                    </tr>
                </thead>
                <tbody>
        `;

        items.sort((a, b) => new Date(b.paidOn || b.paymentDate) - new Date(a.paidOn || a.paymentDate));

        items.forEach(d => {
            const date = new Date(d.paidOn || d.paymentDate).toLocaleDateString();
            const amount = parseFloat(d.amount || d.grossAmount || 0).toFixed(2);
            const currency = d.currency || '';
            const type = d.type || 'Dividend';

            html += `
                <tr>
                    <td>${date}</td>
                    <td>${amount} ${currency}</td>
                    <td>${type}</td>
                </tr>
            `;
        });

        html += '</tbody></table>';
        divContent.innerHTML = html;

    } catch (e) {
        document.getElementById('dividendsContent').innerHTML = '<div class="error-msg">Failed to load dividends</div>';
    }
}

let chartInstance = null;

async function loadHistory(ticker, period) {
    const chartDiv = document.getElementById('chart');
    chartDiv.innerHTML = '<div class="loading">Loading Chart...</div>';

    // Highlight active button
    document.querySelectorAll('.period-btn').forEach(b => {
        b.style.background = b.innerText.toLowerCase() === period.toLowerCase() || (period === 'max' && b.innerText === 'Max') ? 'rgba(255,255,255,0.1)' : 'transparent';
    });

    try {
        const interval = period === '1mo' ? '1d' : (period === 'max' ? '1wk' : '1d');
        const data = await ApiClient.getTickerHistory(ticker, period, interval);

        if (!data.items || data.items.length === 0) {
            chartDiv.innerHTML = '<div class="loading">No history data available.</div>';
            return;
        }

        const seriesData = data.items.map(item => ({
            x: new Date(item.time),
            y: [item.open, item.high, item.low, item.close].map(v => v !== null ? parseFloat(v.toFixed(3)) : v)
        }));

        renderChart(seriesData);

        const last = data.items[data.items.length - 1];
        if (last) {
            const priceEl = document.getElementById('currentPrice');
            if (priceEl) priceEl.innerText = last.close.toFixed(3);
        }

    } catch (e) {
        chartDiv.innerHTML = '<div class="error-msg">Failed to load chart</div>';
    }
}

function renderChart(seriesData) {
    document.getElementById('chart').innerHTML = '';

    const options = {
        series: [{ data: seriesData }],
        chart: {
            type: 'candlestick',
            height: 350,
            background: 'transparent',
            toolbar: { show: false }
        },
        theme: { mode: 'dark' },
        xaxis: {
            type: 'datetime',
            labels: { style: { colors: '#94a3b8' } },
            axisBorder: { show: false },
            axisTicks: { show: false }
        },
        yaxis: {
            tooltip: { enabled: true },
            labels: { style: { colors: '#94a3b8' } }
        },
        grid: {
            borderColor: '#334155',
            strokeDashArray: 4
        },
        plotOptions: {
            candlestick: {
                colors: { upward: '#4ade80', downward: '#f87171' }
            }
        }
    };

    if (chartInstance) chartInstance.destroy();
    chartInstance = new ApexCharts(document.querySelector("#chart"), options);
    chartInstance.render();
}

// Global export
window.initDetails = initDetails;
window.loadHistory = loadHistory;
