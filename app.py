import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import database
import models
import generator as gen
import seed_data

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')

# ── Flask-Login Setup ────────────────────────────────────────

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.email = user_data['email']
        self.name = user_data['name']
        self.skill_level = user_data.get('skill_level', 'beginner')


@login_manager.user_loader
def load_user(user_id):
    user_data = models.get_user_by_id(int(user_id))
    if user_data:
        return User(user_data)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Unauthorized'}), 401
    return redirect(url_for('login'))


# ── Init DB & Seed ───────────────────────────────────────────

database.init_db()
seed_data.seed()


# ── Auth Routes ──────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user_data = models.get_user_by_email(email)
        if user_data and models.verify_password(user_data['password_hash'], password):
            login_user(User(user_data))
            return redirect(url_for('dashboard'))
        flash('Invalid email or password.', 'error')
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not name or not email or not password:
            flash('All fields are required.', 'error')
        elif password != confirm:
            flash('Passwords do not match.', 'error')
        elif len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
        else:
            existing = models.get_user_by_email(email)
            if existing:
                flash('An account with that email already exists.', 'error')
            else:
                user_id = models.create_user(email, password, name)
                user_data = models.get_user_by_id(user_id)
                login_user(User(user_data))
                return redirect(url_for('dashboard'))
    return render_template('signup.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ── Page Routes ───────────────────────────────────────────────

@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html', active='dashboard')


@app.route('/track')
@login_required
def tracker():
    return render_template('tracker.html', active='tracker')


@app.route('/generate')
@login_required
def generate():
    return render_template('generator.html', active='generator')


@app.route('/progressions')
@login_required
def progressions():
    return render_template('progressions.html', active='progressions')


@app.route('/exercises')
@login_required
def exercises():
    return render_template('exercises.html', active='exercises')


@app.route('/settings')
@login_required
def settings():
    profile = models.get_profile(current_user.id)
    return render_template('settings.html', active='settings', profile=profile)


# ── API: Exercises ────────────────────────────────────────────

@app.route('/api/exercises')
@login_required
def api_exercises():
    category = request.args.get('category')
    search = request.args.get('search')
    diff_min = request.args.get('difficulty_min', type=int)
    diff_max = request.args.get('difficulty_max', type=int)
    return jsonify(models.get_all_exercises(category, diff_min, diff_max, search))


@app.route('/api/exercises/<int:exercise_id>')
@login_required
def api_exercise(exercise_id):
    ex = models.get_exercise(exercise_id)
    if not ex:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(ex)


# ── API: Progressions ────────────────────────────────────────

@app.route('/api/progressions')
@login_required
def api_progressions():
    return jsonify(models.get_all_progressions(current_user.id))


@app.route('/api/progressions/<int:prog_id>/advance', methods=['POST'])
@login_required
def api_advance(prog_id):
    new_step = models.advance_progression(current_user.id, prog_id)
    return jsonify({'current_step': new_step})


@app.route('/api/progressions/<int:prog_id>/regress', methods=['POST'])
@login_required
def api_regress(prog_id):
    new_step = models.regress_progression(current_user.id, prog_id)
    return jsonify({'current_step': new_step})


@app.route('/api/progressions/reset', methods=['POST'])
@login_required
def api_reset_progressions():
    conn = database.get_db()
    cur = conn.cursor()
    cur.execute("UPDATE user_progression_status SET current_step = 1 WHERE user_id = %s", (current_user.id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'status': 'ok'})


# ── API: Workouts ─────────────────────────────────────────────

@app.route('/api/workouts', methods=['GET'])
@login_required
def api_get_workouts():
    return jsonify(models.get_workouts(current_user.id))


@app.route('/api/workouts/<int:workout_id>', methods=['GET'])
@login_required
def api_get_workout(workout_id):
    w = models.get_workout(current_user.id, workout_id)
    if not w:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(w)


@app.route('/api/workouts', methods=['POST'])
@login_required
def api_create_workout():
    data = request.get_json()
    workout_id = models.create_workout(
        user_id=current_user.id,
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
@login_required
def api_delete_workout(workout_id):
    models.delete_workout(current_user.id, workout_id)
    return jsonify({'status': 'ok'})


# ── API: Generator ────────────────────────────────────────────

@app.route('/api/generate', methods=['POST'])
@login_required
def api_generate():
    data = request.get_json()
    workout = gen.generate_workout(
        user_id=current_user.id,
        level=data.get('level', 'beginner'),
        focus=data.get('focus', 'full body'),
        duration=data.get('duration', 45),
        goal=data.get('goal', 'strength'),
        equipment=data.get('equipment', 'bar')
    )
    return jsonify(workout)


# ── API: Templates ────────────────────────────────────────────

@app.route('/api/templates', methods=['GET'])
@login_required
def api_get_templates():
    return jsonify(models.get_templates(current_user.id))


@app.route('/api/templates', methods=['POST'])
@login_required
def api_save_template():
    data = request.get_json()
    tmpl_id = models.save_template(
        user_id=current_user.id,
        name=data['name'],
        description=data.get('description', ''),
        level=data.get('level', ''),
        focus=data.get('focus', ''),
        duration=data.get('duration'),
        exercises=data.get('exercises', [])
    )
    return jsonify({'id': tmpl_id}), 201


@app.route('/api/templates/<int:template_id>', methods=['DELETE'])
@login_required
def api_delete_template(template_id):
    models.delete_template(current_user.id, template_id)
    return jsonify({'status': 'ok'})


# ── API: Dashboard ────────────────────────────────────────────

@app.route('/api/dashboard')
@login_required
def api_dashboard():
    return jsonify(models.get_dashboard_stats(current_user.id))


# ── API: Profile ──────────────────────────────────────────────

@app.route('/api/profile', methods=['PUT'])
@login_required
def api_update_profile():
    data = request.get_json()
    models.update_profile(
        user_id=current_user.id,
        name=data.get('name', 'Athlete'),
        skill_level=data.get('skill_level', 'beginner'),
        goals=data.get('goals', '')
    )
    return jsonify({'status': 'ok'})


# ── API: Export / Import ──────────────────────────────────────

@app.route('/api/export')
@login_required
def api_export():
    conn = database.get_db()
    cur = conn.cursor()

    profile = models.get_profile(current_user.id)
    data = {
        'workouts': [],
        'progression_status': [],
        'profile': profile,
    }

    cur.execute("SELECT * FROM workouts WHERE user_id = %s ORDER BY created_at", (current_user.id,))
    workouts = cur.fetchall()
    for w in workouts:
        workout = dict(w)
        cur.execute(
            "SELECT * FROM workout_sets WHERE workout_id = %s", (w['id'],)
        )
        workout['sets'] = [dict(s) for s in cur.fetchall()]
        data['workouts'].append(workout)

    cur.execute("SELECT * FROM user_progression_status WHERE user_id = %s", (current_user.id,))
    data['progression_status'] = [dict(s) for s in cur.fetchall()]

    cur.close()
    conn.close()
    return jsonify(data)


@app.route('/api/import', methods=['POST'])
@login_required
def api_import():
    data = request.get_json()

    if 'profile' in data:
        p = data['profile']
        models.update_profile(current_user.id, p.get('name', 'Athlete'), p.get('skill_level', 'beginner'), p.get('goals', ''))

    if 'progression_status' in data:
        conn = database.get_db()
        cur = conn.cursor()
        for ps in data['progression_status']:
            cur.execute('''
                INSERT INTO user_progression_status (user_id, progression_id, current_step)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, progression_id) DO UPDATE SET current_step = %s
            ''', (current_user.id, ps['progression_id'], ps['current_step'], ps['current_step']))
        conn.commit()
        cur.close()
        conn.close()

    if 'workouts' in data:
        for w in data['workouts']:
            wid = models.create_workout(current_user.id, w.get('name'), w.get('workout_type'), w.get('duration'), w.get('notes'))
            for s in w.get('sets', []):
                models.add_workout_set(wid, s['exercise_id'], s.get('set_number', 1),
                                       s.get('reps'), s.get('hold_time'), s.get('weight', 0), s.get('rpe'))

    return jsonify({'status': 'ok'})


# ── App Init ──────────────────────────────────────────────────

if __name__ == '__main__':
    print("\n  Kaizen Cali")
    print("  Running at http://localhost:5001\n")
    app.run(debug=True, port=5001)
