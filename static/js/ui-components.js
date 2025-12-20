const UI = {
    generateSparkline: (data) => {
        const width = 100;
        const height = 30;

        if (!data || data.length === 0) return '';
        if (data.length === 1) {
            return `<svg width="${width}" height="${height}"><circle cx="${width / 2}" cy="${height / 2}" r="3" fill="#38bdf8"/></svg>`;
        }

        const min = Math.min(...data);
        const max = Math.max(...data);
        const range = max - min || 1;

        const points = data.map((val, i) => {
            const x = (i / (data.length - 1)) * width;
            const y = height - ((val - min) / range) * height;
            return `${x},${y}`;
        });

        const strokeColor = data[data.length - 1] >= data[0] ? '#4ade80' : '#f87171';

        return `
            <svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" style="overflow: visible;">
                <polyline fill="none" stroke="${strokeColor}" stroke-width="2" points="${points.join(' ')}" />
                <circle cx="${points[points.length - 1].split(',')[0]}" cy="${points[points.length - 1].split(',')[1]}" r="2" fill="${strokeColor}" />
            </svg>
        `;
    },

    showModal: (modalId) => {
        const el = document.getElementById(modalId);
        if (el) {
            el.style.display = 'flex';
        }
    },

    closeModal: (modalId) => {
        const el = document.getElementById(modalId);
        if (el) {
            el.style.display = 'none';
        }
    }
};
