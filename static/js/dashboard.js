const categoryColors = {
    push: '#f97316',
    pull: '#3b82f6',
    legs: '#22c55e',
    core: '#eab308',
    skill: '#a855f7',
    mobility: '#14b8a6',
};

async function loadDashboard() {
    const stats = await api('/api/dashboard');

    // Stat cards
    document.getElementById('stat-streak').textContent = stats.streak;
    document.getElementById('stat-week').textContent = stats.week_workouts;
    document.getElementById('stat-total').textContent = stats.total_workouts;
    document.getElementById('stat-volume').textContent = stats.total_volume.toLocaleString();
    document.getElementById('stat-sets').textContent = stats.total_sets.toLocaleString();
    document.getElementById('stat-avg').textContent = stats.avg_reps.toLocaleString();

    // Greeting subtitle based on streak
    const sub = document.getElementById('greeting-subtitle');
    if (stats.streak >= 7) sub.textContent = stats.streak + ' day streak — unstoppable!';
    else if (stats.streak >= 3) sub.textContent = stats.streak + ' day streak — keep it going!';
    else if (stats.total_workouts > 0) sub.textContent = 'Ready for today\'s session?';

    renderRecentWorkouts(stats.recent_workouts);
    renderVolumeChart(stats.category_volume);
    renderBreakdownChart(stats.category_breakdown);
    renderProgressionSnapshot(stats.progression_snapshot);
}

function renderRecentWorkouts(workouts) {
    const el = document.getElementById('recent-workouts');
    if (!workouts || workouts.length === 0) return;

    el.innerHTML = workouts.map(w => {
        const d = new Date(w.created_at);
        const date = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        const type = w.workout_type || 'custom';
        return `<div class="recent-workout-item">
            <div class="recent-workout-info">
                <span class="recent-workout-name">${w.name || 'Workout'}</span>
                <span class="recent-workout-meta">${date} &middot; ${type} &middot; ${w.set_count} sets</span>
            </div>
            <a href="/track" class="btn btn-sm">View</a>
        </div>`;
    }).join('');
}

function renderVolumeChart(data) {
    const ctx = document.getElementById('volume-chart').getContext('2d');

    if (!data || data.length === 0) {
        ctx.font = '14px -apple-system, sans-serif';
        ctx.fillStyle = 'rgba(235,235,245,0.3)';
        ctx.textAlign = 'center';
        ctx.fillText('Log workouts to see your volume chart', ctx.canvas.width / 2, ctx.canvas.height / 2);
        return;
    }

    const weeks = [...new Set(data.map(d => d.week))].sort();
    const categories = [...new Set(data.map(d => d.category))];

    const datasets = categories.map(cat => ({
        label: cat.charAt(0).toUpperCase() + cat.slice(1),
        data: weeks.map(w => {
            const match = data.find(d => d.week === w && d.category === cat);
            return match ? match.vol : 0;
        }),
        backgroundColor: categoryColors[cat] || '#6366f1',
        borderRadius: 4,
    }));

    new Chart(ctx, {
        type: 'bar',
        data: { labels: weeks.map(w => 'Week ' + w), datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: '#e4e4e7', boxWidth: 12 } } },
            scales: {
                x: { stacked: true, ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                y: { stacked: true, ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' }, title: { display: true, text: 'Total Reps', color: '#9ca3af' } }
            }
        }
    });
}

function renderBreakdownChart(data) {
    const ctx = document.getElementById('breakdown-chart').getContext('2d');

    if (!data || data.length === 0) {
        ctx.font = '14px -apple-system, sans-serif';
        ctx.fillStyle = 'rgba(235,235,245,0.3)';
        ctx.textAlign = 'center';
        ctx.fillText('No data yet', ctx.canvas.width / 2, ctx.canvas.height / 2);
        return;
    }

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => d.category.charAt(0).toUpperCase() + d.category.slice(1)),
            datasets: [{
                data: data.map(d => d.total),
                backgroundColor: data.map(d => categoryColors[d.category] || '#6366f1'),
                borderWidth: 0,
                spacing: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#e4e4e7', boxWidth: 12, padding: 16 }
                }
            }
        }
    });
}

function renderProgressionSnapshot(progressions) {
    const el = document.getElementById('progression-snapshot');
    if (!progressions || progressions.length === 0) return;

    el.innerHTML = progressions.map(p => {
        const pct = Math.round((p.current_step / p.total_steps) * 100);
        const cat = p.category || 'skill';
        return `<div class="progress-snapshot-item">
            <div class="progress-snapshot-header">
                <span class="progress-snapshot-name">${p.name}</span>
                <span class="badge badge-${cat}">${cat}</span>
            </div>
            <div class="progress-snapshot-detail">
                <span class="text-muted text-sm">Step ${p.current_step}/${p.total_steps}${p.current_exercise ? ' — ' + p.current_exercise : ''}</span>
            </div>
            <div class="progress-bar-track">
                <div class="progress-bar-fill" style="width:${pct}%;background:${categoryColors[cat] || '#6366f1'}"></div>
            </div>
        </div>`;
    }).join('');
}

loadDashboard();
