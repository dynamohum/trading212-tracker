const ApiClient = {
    async get(endpoint) {
        try {
            const res = await fetch(endpoint);
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.error || `Request failed with status ${res.status}`);
            }
            return await res.json();
        } catch (e) {
            console.error(`API Get Error (${endpoint}):`, e);
            throw e;
        }
    },

    async post(endpoint, data) {
        try {
            const res = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.error || `Request failed with status ${res.status}`);
            }
            return await res.json();
        } catch (e) {
            console.error(`API Post Error (${endpoint}):`, e);
            throw e;
        }
    },

    // Specific endpoints
    getPositions: () => ApiClient.get('/api/positions'),
    getReturns: () => ApiClient.get('/api/returns'),
    getSettings: () => ApiClient.get('/api/settings'),
    updateSettings: (data) => ApiClient.post('/api/settings', data),
    getTickerDetails: (ticker) => ApiClient.get(`/api/ticker/${ticker}/details`),
    getTickerDividends: (ticker) => ApiClient.get(`/api/ticker/${ticker}/dividends`),
    getTickerHistory: (ticker, period, interval) => ApiClient.get(`/api/ticker/${ticker}/history?period=${period}&interval=${interval}`),
    switchAccount: (account) => ApiClient.post('/api/account/switch', { account }),
    getAccountStatus: () => ApiClient.get('/api/account/status')
};
