let currentWorkout = null;

async function generateWorkout() {
    const params = {
        level: document.getElementById('gen-level').value,
        focus: document.getElementById('gen-focus').value,
        duration: parseInt(document.getElementById('gen-duration').value),
        goal: document.getElementById('gen-goal').value,
        equipment: document.getElementById('gen-equipment').value,
    };

    currentWorkout = await api('/api/generate', {
        method: 'POST',
        body: JSON.stringify(params)
    });

    const container = document.getElementById('generated-workout');
    container.classList.remove('hidden');

    document.getElementById('gen-workout-name').textContent = currentWorkout.name;
    document.getElementById('gen-workout-meta').textContent =
        `${currentWorkout.duration} min | ${currentWorkout.goal} | ${currentWorkout.exercises.length} exercises`;

    const exContainer = document.getElementById('gen-workout-exercises');
    exContainer.innerHTML = currentWorkout.exercises.map(ex => `
        <div class="workout-exercise-row">
            <div class="exercise-order">${ex.order}</div>
            <div class="exercise-info">
                <div class="exercise-info-name">${ex.exercise_name}</div>
                <div class="exercise-info-detail">
                    ${categoryBadge(ex.category)}
                    ${ex.sets} sets x ${ex.reps} | Rest: ${ex.rest}s
                    ${ex.notes ? ` | ${ex.notes}` : ''}
                </div>
            </div>
            <button class="btn-demo" onclick="showVideoModal('${ex.exercise_name.replace(/'/g, "\\'")}')">Demo</button>
        </div>
    `).join('');
}

function startWorkout() {
    if (!currentWorkout) return;
    sessionStorage.setItem('prefill_workout', JSON.stringify(currentWorkout));
    window.location.href = '/track';
}

async function saveAsTemplate() {
    if (!currentWorkout) return;
    const name = prompt('Template name:', currentWorkout.name);
    if (!name) return;

    await api('/api/templates', {
        method: 'POST',
        body: JSON.stringify({
            name: name,
            description: `${currentWorkout.level} ${currentWorkout.focus} - ${currentWorkout.goal}`,
            level: currentWorkout.level,
            focus: currentWorkout.focus,
            duration: currentWorkout.duration,
            exercises: currentWorkout.exercises.map(ex => ({
                exercise_id: ex.exercise_id,
                sets: ex.sets,
                reps: String(ex.reps),
                rest: ex.rest,
                notes: ex.notes || ''
            }))
        })
    });
    showToast('Template saved!');
    loadTemplates();
}

async function loadTemplates() {
    const templates = await api('/api/templates');
    const container = document.getElementById('templates-list');

    if (templates.length === 0) {
        container.innerHTML = '<p class="text-muted">No templates yet. Generate a workout and save it!</p>';
        return;
    }

    container.innerHTML = templates.map(t => `
        <div class="card" style="padding:14px; margin-bottom:8px;">
            <div class="flex-between">
                <div>
                    <strong>${t.name}</strong>
                    ${t.is_preset ? '<span class="badge badge-skill" style="margin-left:6px">Preset</span>' : ''}
                    <div class="text-muted text-sm">${t.description || ''} | ${t.exercises.length} exercises | ${t.duration || '?'} min</div>
                </div>
                <div class="btn-group">
                    <button class="btn btn-sm btn-primary" onclick="loadTemplate(${t.id})">Use</button>
                    ${!t.is_preset ? `<button class="btn btn-sm btn-danger" onclick="deleteTemplate(${t.id})">Delete</button>` : ''}
                </div>
            </div>
        </div>
    `).join('');
}

async function loadTemplate(id) {
    const templates = await api('/api/templates');
    const t = templates.find(x => x.id === id);
    if (!t) return;

    currentWorkout = {
        name: t.name,
        duration: t.duration,
        goal: t.level,
        exercises: t.exercises.map((ex, i) => ({
            exercise_id: ex.exercise_id,
            exercise_name: ex.exercise_name,
            category: ex.category,
            sets: ex.sets,
            reps: ex.reps,
            rest: ex.rest_seconds,
            notes: ex.notes,
            order: i + 1
        }))
    };

    // Display it
    const container = document.getElementById('generated-workout');
    container.classList.remove('hidden');
    document.getElementById('gen-workout-name').textContent = currentWorkout.name;
    document.getElementById('gen-workout-meta').textContent =
        `${currentWorkout.duration} min | ${currentWorkout.exercises.length} exercises`;

    const exContainer = document.getElementById('gen-workout-exercises');
    exContainer.innerHTML = currentWorkout.exercises.map(ex => `
        <div class="workout-exercise-row">
            <div class="exercise-order">${ex.order}</div>
            <div class="exercise-info">
                <div class="exercise-info-name">${ex.exercise_name}</div>
                <div class="exercise-info-detail">
                    ${categoryBadge(ex.category)}
                    ${ex.sets} sets x ${ex.reps} | Rest: ${ex.rest}s
                    ${ex.notes ? ` | ${ex.notes}` : ''}
                </div>
            </div>
            <button class="btn-demo" onclick="showVideoModal('${ex.exercise_name.replace(/'/g, "\\'")}')">Demo</button>
        </div>
    `).join('');

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function deleteTemplate(id) {
    if (!confirm('Delete this template?')) return;
    await api(`/api/templates/${id}`, { method: 'DELETE' });
    showToast('Template deleted');
    loadTemplates();
}

loadTemplates();
