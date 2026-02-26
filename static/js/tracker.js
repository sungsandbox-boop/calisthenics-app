let exercises = [];
let workoutExercises = []; // [{exercise_id, exercise_name, sets: [{reps, hold_time, weight, rpe}]}]

async function init() {
    exercises = await api('/api/exercises');
    const select = document.getElementById('add-exercise-select');
    select.innerHTML = '<option value="">Select exercise to add...</option>' +
        exercises.map(e => `<option value="${e.id}">${e.name} (${e.category})</option>`).join('');
    loadHistory();

    // Check if there's prefill data from generator
    const prefill = sessionStorage.getItem('prefill_workout');
    if (prefill) {
        sessionStorage.removeItem('prefill_workout');
        const data = JSON.parse(prefill);
        showNewWorkout();
        document.getElementById('workout-name').value = data.name || '';
        document.getElementById('workout-duration').value = data.duration || '';
        for (const ex of data.exercises) {
            const exercise = exercises.find(e => e.id === ex.exercise_id);
            if (exercise) {
                const sets = [];
                const numSets = ex.sets || 3;
                for (let i = 0; i < numSets; i++) {
                    sets.push({ reps: '', hold_time: '', weight: '', rpe: '' });
                }
                workoutExercises.push({
                    exercise_id: exercise.id,
                    exercise_name: exercise.name,
                    sets: sets
                });
            }
        }
        renderWorkoutExercises();
    }
}

function showNewWorkout() {
    document.getElementById('new-workout').classList.remove('hidden');
    workoutExercises = [];
    renderWorkoutExercises();
}

function cancelWorkout() {
    document.getElementById('new-workout').classList.add('hidden');
    document.getElementById('workout-name').value = '';
    document.getElementById('workout-duration').value = '';
    document.getElementById('workout-notes').value = '';
    workoutExercises = [];
}

function addExerciseToWorkout() {
    const select = document.getElementById('add-exercise-select');
    const id = parseInt(select.value);
    if (!id) return;

    const exercise = exercises.find(e => e.id === id);
    workoutExercises.push({
        exercise_id: id,
        exercise_name: exercise.name,
        sets: [{ reps: '', hold_time: '', weight: '', rpe: '' }]
    });
    select.value = '';
    renderWorkoutExercises();
}

function renderWorkoutExercises() {
    const container = document.getElementById('workout-exercises');
    if (workoutExercises.length === 0) {
        container.innerHTML = '<p class="text-muted text-sm mt-8">No exercises added yet</p>';
        return;
    }

    container.innerHTML = workoutExercises.map((ex, ei) => `
        <div class="card" style="padding:12px; margin-bottom:8px;">
            <div class="flex-between mb-8">
                <strong>${ex.exercise_name}</strong>
                <button class="btn btn-sm btn-danger" onclick="removeExercise(${ei})">Remove</button>
            </div>
            <div>
                <div class="set-row" style="font-size:0.75rem; color:var(--text-muted)">
                    <span class="set-num">#</span>
                    <span style="width:70px">Reps</span>
                    <span style="width:70px">Hold (s)</span>
                    <span style="width:70px">Weight</span>
                    <span style="width:70px">RPE</span>
                    <span style="width:30px"></span>
                </div>
                ${ex.sets.map((set, si) => `
                    <div class="set-row">
                        <span class="set-num">${si + 1}</span>
                        <input type="number" placeholder="reps" value="${set.reps}" onchange="updateSet(${ei},${si},'reps',this.value)">
                        <input type="number" placeholder="sec" value="${set.hold_time}" onchange="updateSet(${ei},${si},'hold_time',this.value)">
                        <input type="number" placeholder="kg" value="${set.weight}" step="0.5" onchange="updateSet(${ei},${si},'weight',this.value)">
                        <input type="number" placeholder="1-10" min="1" max="10" value="${set.rpe}" onchange="updateSet(${ei},${si},'rpe',this.value)">
                        <button class="btn btn-sm btn-danger" onclick="removeSet(${ei},${si})" style="padding:2px 6px">x</button>
                    </div>
                `).join('')}
            </div>
            <button class="btn btn-sm mt-8" onclick="addSet(${ei})">+ Set</button>
        </div>
    `).join('');
}

function updateSet(ei, si, field, value) {
    workoutExercises[ei].sets[si][field] = value;
}

function addSet(ei) {
    workoutExercises[ei].sets.push({ reps: '', hold_time: '', weight: '', rpe: '' });
    renderWorkoutExercises();
}

function removeSet(ei, si) {
    workoutExercises[ei].sets.splice(si, 1);
    if (workoutExercises[ei].sets.length === 0) {
        workoutExercises.splice(ei, 1);
    }
    renderWorkoutExercises();
}

function removeExercise(ei) {
    workoutExercises.splice(ei, 1);
    renderWorkoutExercises();
}

async function saveWorkout() {
    const name = document.getElementById('workout-name').value || 'Workout';
    const duration = parseInt(document.getElementById('workout-duration').value) || null;
    const notes = document.getElementById('workout-notes').value;

    if (workoutExercises.length === 0) {
        showToast('Add at least one exercise');
        return;
    }

    // Build sets array
    const sets = [];
    for (const ex of workoutExercises) {
        for (let i = 0; i < ex.sets.length; i++) {
            const s = ex.sets[i];
            sets.push({
                exercise_id: ex.exercise_id,
                set_number: i + 1,
                reps: parseInt(s.reps) || null,
                hold_time: parseInt(s.hold_time) || null,
                weight: parseFloat(s.weight) || 0,
                rpe: parseInt(s.rpe) || null,
            });
        }
    }

    await api('/api/workouts', {
        method: 'POST',
        body: JSON.stringify({ name, duration, notes, sets })
    });

    showToast('Workout saved!');
    cancelWorkout();
    loadHistory();
}

async function loadHistory() {
    const workouts = await api('/api/workouts');
    const container = document.getElementById('workout-history');

    if (workouts.length === 0) {
        container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">&#128170;</div><p>No workouts yet. Start logging!</p></div>';
        return;
    }

    container.innerHTML = workouts.map(w => `
        <div class="workout-item" onclick="toggleWorkout(this, ${w.id})">
            <div class="workout-header">
                <div>
                    <strong>${w.name || 'Workout'}</strong>
                    <span class="text-muted text-sm" style="margin-left:8px">${w.set_count} sets</span>
                </div>
                <div>
                    <span class="workout-date">${formatDate(w.created_at)}</span>
                </div>
            </div>
            <div class="workout-details" id="details-${w.id}">Loading...</div>
        </div>
    `).join('');
}

async function toggleWorkout(el, id) {
    el.classList.toggle('expanded');
    if (el.classList.contains('expanded')) {
        const w = await api(`/api/workouts/${id}`);
        const details = document.getElementById(`details-${id}`);

        if (w.sets.length === 0) {
            details.innerHTML = '<p class="text-muted">No sets recorded</p>';
            return;
        }

        // Group sets by exercise
        const grouped = {};
        for (const s of w.sets) {
            if (!grouped[s.exercise_name]) grouped[s.exercise_name] = [];
            grouped[s.exercise_name].push(s);
        }

        let html = '<div class="table-wrap"><table><tr><th>Exercise</th><th>Set</th><th>Reps</th><th>Hold</th><th>Weight</th><th>RPE</th></tr>';
        for (const [name, sets] of Object.entries(grouped)) {
            for (const s of sets) {
                html += `<tr>
                    <td>${s.set_number === 1 ? name : ''}</td>
                    <td>${s.set_number}</td>
                    <td>${s.reps || '-'}</td>
                    <td>${s.hold_time ? s.hold_time + 's' : '-'}</td>
                    <td>${s.weight ? s.weight + 'kg' : '-'}</td>
                    <td>${s.rpe || '-'}</td>
                </tr>`;
            }
        }
        html += '</table></div>';

        if (w.notes) {
            html += `<p class="text-muted text-sm mt-8">${w.notes}</p>`;
        }

        html += `<button class="btn btn-sm btn-danger mt-8" onclick="event.stopPropagation(); deleteWorkout(${id})">Delete Workout</button>`;
        details.innerHTML = html;
    }
}

async function deleteWorkout(id) {
    if (!confirm('Delete this workout?')) return;
    await api(`/api/workouts/${id}`, { method: 'DELETE' });
    showToast('Workout deleted');
    loadHistory();
}

init();
