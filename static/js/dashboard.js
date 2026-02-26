async function loadDashboard() {
    const stats = await api('/api/dashboard');

    document.getElementById('stat-streak').textContent = stats.streak;
    document.getElementById('stat-week').textContent = stats.week_workouts;
    document.getElementById('stat-total').textContent = stats.total_workouts;
    document.getElementById('stat-volume').textContent = stats.total_volume.toLocaleString();

    renderVolumeChart(stats.category_volume);
}

function renderVolumeChart(data) {
    const ctx = document.getElementById('volume-chart').getContext('2d');

    if (data.length === 0) {
        ctx.font = '14px sans-serif';
        ctx.fillStyle = '#9ca3af';
        ctx.textAlign = 'center';
        ctx.fillText('Log workouts to see your volume chart', ctx.canvas.width / 2, ctx.canvas.height / 2);
        return;
    }

    // Group by week and category
    const weeks = [...new Set(data.map(d => d.week))].sort();
    const categories = [...new Set(data.map(d => d.category))];

    const colorMap = {
        push: '#f97316',
        pull: '#3b82f6',
        legs: '#22c55e',
        core: '#eab308',
        skill: '#a855f7',
        mobility: '#14b8a6',
    };

    const datasets = categories.map(cat => ({
        label: cat.charAt(0).toUpperCase() + cat.slice(1),
        data: weeks.map(w => {
            const match = data.find(d => d.week === w && d.category === cat);
            return match ? match.vol : 0;
        }),
        backgroundColor: colorMap[cat] || '#6366f1',
        borderRadius: 4,
    }));

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: weeks.map(w => `Week ${w}`),
            datasets: datasets,
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#e4e4e7', boxWidth: 12 }
                }
            },
            scales: {
                x: {
                    stacked: true,
                    ticks: { color: '#9ca3af' },
                    grid: { color: '#2e3140' },
                },
                y: {
                    stacked: true,
                    ticks: { color: '#9ca3af' },
                    grid: { color: '#2e3140' },
                    title: { display: true, text: 'Total Reps', color: '#9ca3af' }
                }
            }
        }
    });
}

loadDashboard();
