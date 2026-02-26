from flask import Flask, render_template, request, jsonify
import database
import models
import generator as gen
import seed_data

app = Flask(__name__)

database.init_db()
seed_data.seed()


# ── Page Routes ───────────────────────────────────────────────

@app.route('/')
def dashboard():
    return render_template('dashboard.html', active='dashboard')


@app.route('/track')
def tracker():
    return render_template('tracker.html', active='tracker')


@app.route('/generate')
def generate():
    return render_template('generator.html', active='generator')


@app.route('/progressions')
def progressions():
    return render_template('progressions.html', active='progressions')


@app.route('/exercises')
def exercises():
    return render_template('exercises.html', active='exercises')


@app.route('/settings')
def settings():
    profile = models.get_profile()
    return render_template('settings.html', active='settings', profile=profile)


# ── API: Exercises ────────────────────────────────────────────

@app.route('/api/exercises')
def api_exercises():
    category = request.args.get('category')
    search = request.args.get('search')
    diff_min = request.args.get('difficulty_min', type=int)
    diff_max = request.args.get('difficulty_max', type=int)
    return jsonify(models.get_all_exercises(category, diff_min, diff_max, search))


@app.route('/api/exercises/<int:exercise_id>')
def api_exercise(exercise_id):
    ex = models.get_exercise(exercise_id)
    if not ex:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(ex)


# ── API: Progressions ────────────────────────────────────────

@app.route('/api/progressions')
def api_progressions():
    return jsonify(models.get_all_progressions())


@app.route('/api/progressions/<int:prog_id>/advance', methods=['POST'])
def api_advance(prog_id):
    new_step = models.advance_progression(prog_id)
    return jsonify({'current_step': new_step})


@app.route('/api/progressions/<int:prog_id>/regress', methods=['POST'])
def api_regress(prog_id):
    new_step = models.regress_progression(prog_id)
    return jsonify({'current_step': new_step})


@app.route('/api/progressions/reset', methods=['POST'])
def api_reset_progressions():
    conn = database.get_db()
    conn.execute("UPDATE user_progression_status SET current_step = 1")
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})


# ── API: Workouts ─────────────────────────────────────────────

@app.route('/api/workouts', methods=['GET'])
def api_get_workouts():
    return jsonify(models.get_workouts())


@app.route('/api/workouts/<int:workout_id>', methods=['GET'])
def api_get_workout(workout_id):
    w = models.get_workout(workout_id)
    if not w:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(w)


@app.route('/api/workouts', methods=['POST'])
def api_create_workout():
    data = request.get_json()
    workout_id = models.create_workout(
        name=data.get('name', 'Workout'),
        workout_type=data.get('type', 'custom'),
        duration=data.get('duration'),
        notes=data.get('notes')
    )
    for s in data.get('sets', []):
        models.add_workout_set(
            workout_id=workout_id,
            exercise_id=s['exercise_id'],
            set_number=s.get('set_number', 1),
            reps=s.get('reps'),
            hold_time=s.get('hold_time'),
            weight=s.get('weight', 0),
            rpe=s.get('rpe')
        )
    return jsonify({'id': workout_id}), 201


@app.route('/api/workouts/<int:workout_id>', methods=['DELETE'])
def api_delete_workout(workout_id):
    models.delete_workout(workout_id)
    return jsonify({'status': 'ok'})


# ── API: Generator ────────────────────────────────────────────

@app.route('/api/generate', methods=['POST'])
def api_generate():
    data = request.get_json()
    workout = gen.generate_workout(
        level=data.get('level', 'beginner'),
        focus=data.get('focus', 'full body'),
        duration=data.get('duration', 45),
        goal=data.get('goal', 'strength'),
        equipment=data.get('equipment', 'bar')
    )
    return jsonify(workout)


# ── API: Templates ────────────────────────────────────────────

@app.route('/api/templates', methods=['GET'])
def api_get_templates():
    return jsonify(models.get_templates())


@app.route('/api/templates', methods=['POST'])
def api_save_template():
    data = request.get_json()
    tmpl_id = models.save_template(
        name=data['name'],
        description=data.get('description', ''),
        level=data.get('level', ''),
        focus=data.get('focus', ''),
        duration=data.get('duration'),
        exercises=data.get('exercises', [])
    )
    return jsonify({'id': tmpl_id}), 201


@app.route('/api/templates/<int:template_id>', methods=['DELETE'])
def api_delete_template(template_id):
    models.delete_template(template_id)
    return jsonify({'status': 'ok'})


# ── API: Dashboard ────────────────────────────────────────────

@app.route('/api/dashboard')
def api_dashboard():
    return jsonify(models.get_dashboard_stats())


# ── API: Profile ──────────────────────────────────────────────

@app.route('/api/profile', methods=['PUT'])
def api_update_profile():
    data = request.get_json()
    models.update_profile(
        name=data.get('name', 'Athlete'),
        skill_level=data.get('skill_level', 'beginner'),
        goals=data.get('goals', '')
    )
    return jsonify({'status': 'ok'})


# ── API: Export / Import ──────────────────────────────────────

@app.route('/api/export')
def api_export():
    conn = database.get_db()
    data = {
        'workouts': [],
        'progression_status': [],
        'profile': dict(conn.execute("SELECT * FROM user_profile WHERE id = 1").fetchone()),
    }

    workouts = conn.execute("SELECT * FROM workouts ORDER BY created_at").fetchall()
    for w in workouts:
        workout = dict(w)
        sets = conn.execute(
            "SELECT * FROM workout_sets WHERE workout_id = ?", (w['id'],)
        ).fetchall()
        workout['sets'] = [dict(s) for s in sets]
        data['workouts'].append(workout)

    statuses = conn.execute("SELECT * FROM user_progression_status").fetchall()
    data['progression_status'] = [dict(s) for s in statuses]

    conn.close()
    return jsonify(data)


@app.route('/api/import', methods=['POST'])
def api_import():
    data = request.get_json()

    if 'profile' in data:
        p = data['profile']
        models.update_profile(p.get('name', 'Athlete'), p.get('skill_level', 'beginner'), p.get('goals', ''))

    if 'progression_status' in data:
        conn = database.get_db()
        for ps in data['progression_status']:
            conn.execute('''
                INSERT INTO user_progression_status (progression_id, current_step)
                VALUES (?, ?)
                ON CONFLICT(progression_id) DO UPDATE SET current_step = ?
            ''', (ps['progression_id'], ps['current_step'], ps['current_step']))
        conn.commit()
        conn.close()

    if 'workouts' in data:
        for w in data['workouts']:
            wid = models.create_workout(w.get('name'), w.get('workout_type'), w.get('duration'), w.get('notes'))
            for s in w.get('sets', []):
                models.add_workout_set(wid, s['exercise_id'], s.get('set_number', 1),
                                       s.get('reps'), s.get('hold_time'), s.get('weight', 0), s.get('rpe'))

    return jsonify({'status': 'ok'})


# ── App Init ──────────────────────────────────────────────────

if __name__ == '__main__':
    print("\n  Kaizen Cali")
    print("  Running at http://localhost:5001\n")
    app.run(debug=True, port=5001)
