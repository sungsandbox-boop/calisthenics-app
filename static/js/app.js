// Shared utilities

function showToast(message, duration = 2500) {
    let toast = document.querySelector('.toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.className = 'toast';
        document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), duration);
}

function difficultyDots(level, max = 10) {
    let html = '<span class="difficulty">';
    for (let i = 1; i <= max; i++) {
        html += `<span class="diff-dot ${i <= level ? 'filled' : ''}"></span>`;
    }
    html += '</span>';
    return html;
}

function categoryBadge(category) {
    return `<span class="badge badge-${category}">${category}</span>`;
}

async function api(url, options = {}) {
    const defaults = {
        headers: { 'Content-Type': 'application/json' },
    };
    const res = await fetch(url, { ...defaults, ...options });
    if (res.status === 401) {
        window.location.href = '/login';
        return;
    }
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', {
        month: 'short', day: 'numeric', year: 'numeric',
        hour: 'numeric', minute: '2-digit'
    });
}

// ── Exercise Demo Modal ───────────────────────────────────

let _exerciseManifest = null;

async function getExerciseManifest() {
    if (_exerciseManifest) return _exerciseManifest;
    try {
        const res = await fetch('/static/images/exercises/manifest.json');
        if (res.ok) _exerciseManifest = await res.json();
    } catch {}
    return _exerciseManifest || {};
}

function showVideoModal(exerciseName) {
    const modal = document.getElementById('video-modal');
    const body = document.getElementById('video-modal-body');
    const title = document.getElementById('video-modal-title');

    title.textContent = exerciseName;
    body.innerHTML = '<div class="video-modal-spinner">Loading demo...</div>';
    modal.classList.add('active');

    getExerciseManifest().then(manifest => {
        const entry = manifest[exerciseName];

        if (entry) {
            // Check if local images actually exist by loading them
            const startImg = new Image();
            const endImg = new Image();
            let startOk = false, endOk = false, checked = 0;

            const render = () => {
                checked++;
                if (checked < 2) return;

                if (!startOk && !endOk) {
                    showFallback(body, exerciseName);
                    return;
                }

                const images = [];
                if (startOk) images.push({ src: entry.start, label: 'Start Position' });
                if (endOk) images.push({ src: entry.end, label: 'End Position' });
                renderImages(body, exerciseName, images);
            };

            startImg.onload = () => { startOk = true; render(); };
            startImg.onerror = () => { startOk = false; render(); };
            endImg.onload = () => { endOk = true; render(); };
            endImg.onerror = () => { endOk = false; render(); };

            startImg.src = entry.start;
            endImg.src = entry.end;
        } else {
            showFallback(body, exerciseName);
        }
    });
}

function renderImages(body, exerciseName, images) {
    let html = '<div class="video-modal-images">';
    images.forEach((img, i) => {
        html += `<img src="${img.src}" alt="${exerciseName} - ${img.label}" class="${i > 0 ? 'hidden' : ''}" data-idx="${i}">`;
    });
    html += '</div>';

    if (images.length > 1) {
        html += '<div class="carousel-nav">';
        images.forEach((img, i) => {
            html += `<button class="carousel-dot ${i === 0 ? 'active' : ''}" onclick="carouselGo(${i})">${img.label}</button>`;
        });
        html += '</div>';
    }

    const ytQuery = encodeURIComponent(exerciseName + ' calisthenics tutorial');
    html += `<div style="margin-top:16px;text-align:center">
        <a href="https://www.youtube.com/results?search_query=${ytQuery}" target="_blank" rel="noopener" style="font-size:0.85rem">
            Watch video tutorials on YouTube &#8599;
        </a>
    </div>`;

    body.innerHTML = html;
}

function showFallback(body, exerciseName) {
    const ytQuery = encodeURIComponent(exerciseName + ' calisthenics tutorial');
    body.innerHTML = `
        <div class="video-modal-fallback">
            <p>Demo images not yet generated for this exercise.</p>
            <p class="text-sm" style="margin-top:8px">Run <code>python generate_exercise_images.py</code> to generate AI illustrations.</p>
            <a href="https://www.youtube.com/results?search_query=${ytQuery}" target="_blank" rel="noopener">
                Search on YouTube &#8599;
            </a>
        </div>`;
}

function carouselGo(idx) {
    const container = document.querySelector('.video-modal-images');
    if (!container) return;
    container.querySelectorAll('img').forEach(img => {
        img.classList.toggle('hidden', parseInt(img.dataset.idx) !== idx);
    });
    document.querySelectorAll('.carousel-dot').forEach((dot, i) => {
        dot.classList.toggle('active', i === idx);
    });
}

function closeVideoModal() {
    const modal = document.getElementById('video-modal');
    modal.classList.remove('active');
}
