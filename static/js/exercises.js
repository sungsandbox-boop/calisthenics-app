let allExercises = [];

async function loadExercises() {
    allExercises = await api('/api/exercises');
    renderExercises(allExercises);
}

function renderExercises(exercises) {
    const grid = document.getElementById('exercises-grid');
    document.getElementById('exercise-count').textContent = `${exercises.length} exercises`;

    if (exercises.length === 0) {
        grid.innerHTML = '<div class="empty-state"><div class="empty-state-icon">&#128270;</div><p>No exercises match your filters</p></div>';
        return;
    }

    grid.innerHTML = exercises.map(ex => `
        <div class="exercise-card" onclick="this.classList.toggle('expanded')">
            <div class="exercise-card-header">
                <span class="exercise-card-name">${ex.name}</span>
                ${categoryBadge(ex.category)}
            </div>
            <div class="exercise-card-meta">
                ${difficultyDots(ex.difficulty)}
                <span class="text-muted text-sm">${ex.equipment !== 'none' ? ex.equipment : ''}</span>
            </div>
            <div class="exercise-card-body">
                <p class="mt-8">${ex.description || ''}</p>
                ${ex.cues ? `<p class="mt-8"><strong>Cues:</strong> ${ex.cues}</p>` : ''}
                ${ex.muscle_groups ? `<p class="mt-8 text-muted text-sm">Muscles: ${ex.muscle_groups}</p>` : ''}
                <button class="btn-demo mt-8" onclick="event.stopPropagation();showVideoModal('${ex.name.replace(/'/g, "\\'")}')">&#9654; Watch Demo</button>
            </div>
        </div>
    `).join('');
}

function filterExercises() {
    const search = document.getElementById('search-input').value.toLowerCase();
    const category = document.getElementById('filter-category').value;
    const difficulty = document.getElementById('filter-difficulty').value;

    let filtered = allExercises;

    if (search) {
        filtered = filtered.filter(ex =>
            ex.name.toLowerCase().includes(search) ||
            (ex.description || '').toLowerCase().includes(search) ||
            (ex.muscle_groups || '').toLowerCase().includes(search)
        );
    }

    if (category) {
        filtered = filtered.filter(ex => ex.category === category);
    }

    if (difficulty) {
        const [min, max] = difficulty.split('-').map(Number);
        filtered = filtered.filter(ex => ex.difficulty >= min && ex.difficulty <= max);
    }

    renderExercises(filtered);
}

document.getElementById('search-input').addEventListener('input', filterExercises);
document.getElementById('filter-category').addEventListener('change', filterExercises);
document.getElementById('filter-difficulty').addEventListener('change', filterExercises);

loadExercises();
