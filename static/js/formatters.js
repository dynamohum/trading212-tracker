const Formatters = {
    currency: (val, code = '') => {
        if (val === undefined || val === null) return '--';
        return parseFloat(val).toFixed(2) + (code ? ' ' + code : '');
    },

    number: (val, decimals = 2) => {
        if (val === undefined || val === null) return '--';
        return parseFloat(val).toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
    },

    percent: (val) => {
        if (val === undefined || val === null) return '--';
        const num = parseFloat(val);
        const sign = num >= 0 ? '+' : '';
        return `${sign}${num.toFixed(2)}%`;
    },

    colorClass: (val) => {
        const num = parseFloat(val);
        if (num > 0) return 'positive';
        if (num < 0) return 'negative';
        return '';
    }
};
