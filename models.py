from database import get_db


# ── EXERCISES ─────────────────────────────────────────────────

def get_all_exercises(category=None, difficulty_min=None, difficulty_max=None, search=None):
    conn = get_db()
    query = "SELECT * FROM exercises WHERE 1=1"
    params = []
    if category:
        query += " AND category = ?"
        params.append(category)
    if difficulty_min:
        query += " AND difficulty >= ?"
        params.append(difficulty_min)
    if difficulty_max:
        query += " AND difficulty <= ?"
        params.append(difficulty_max)
    if search:
        query += " AND (name LIKE ? OR description LIKE ? OR muscle_groups LIKE ?)"
        params.extend([f"%{search}%"] * 3)
    query += " ORDER BY category, difficulty, name"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_exercise(exercise_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM exercises WHERE id = ?", (exercise_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ── PROGRESSIONS ──────────────────────────────────────────────

def get_all_progressions():
    conn = get_db()
    progs = conn.execute("SELECT * FROM progressions ORDER BY id").fetchall()
    result = []
    for p in progs:
        prog = dict(p)
        steps = conn.execute('''
            SELECT ps.*, e.name as exercise_name, e.difficulty, e.description as exercise_description
            FROM progression_steps ps
            JOIN exercises e ON ps.exercise_id = e.id
            WHERE ps.progression_id = ?
            ORDER BY ps.step_order
        ''', (p['id'],)).fetchall()
        prog['steps'] = [dict(s) for s in steps]

        status = conn.execute('''
            SELECT current_step, achieved_at FROM user_progression_status
            WHERE progression_id = ?
        ''', (p['id'],)).fetchone()
        prog['current_step'] = status['current_step'] if status else 1
        result.append(prog)
    conn.close()
    return result


def advance_progression(progression_id):
    conn = get_db()
    status = conn.execute(
        "SELECT current_step FROM user_progression_status WHERE progression_id = ?",
        (progression_id,)
    ).fetchone()
    total = conn.execute(
        "SELECT COUNT(*) as cnt FROM progression_steps WHERE progression_id = ?",
        (progression_id,)
    ).fetchone()['cnt']

    current = status['current_step'] if status else 1
    if current < total:
        new_step = current + 1
        conn.execute('''
            INSERT INTO user_progression_status (progression_id, current_step, achieved_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(progression_id) DO UPDATE SET current_step = ?, achieved_at = CURRENT_TIMESTAMP
        ''', (progression_id, new_step, new_step))
        conn.commit()
        conn.close()
        return new_step
    conn.close()
    return current


def regress_progression(progression_id):
    conn = get_db()
    status = conn.execute(
        "SELECT current_step FROM user_progression_status WHERE progression_id = ?",
        (progression_id,)
    ).fetchone()
    current = status['current_step'] if status else 1
    if current > 1:
        new_step = current - 1
        conn.execute('''
            UPDATE user_progression_status SET current_step = ?, achieved_at = CURRENT_TIMESTAMP
            WHERE progression_id = ?
        ''', (new_step, progression_id))
        conn.commit()
        conn.close()
        return new_step
    conn.close()
    return current


# ── WORKOUTS ──────────────────────────────────────────────────

def create_workout(name, workout_type='custom', duration=None, notes=None):
    conn = get_db()
    cursor = conn.execute('''
        INSERT INTO workouts (name, workout_type, duration, notes)
        VALUES (?, ?, ?, ?)
    ''', (name, workout_type, duration, notes))
    workout_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return workout_id


def add_workout_set(workout_id, exercise_id, set_number, reps=None, hold_time=None, weight=0, rpe=None):
    conn = get_db()
    conn.execute('''
        INSERT INTO workout_sets (workout_id, exercise_id, set_number, reps, hold_time, weight, rpe)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (workout_id, exercise_id, set_number, reps, hold_time, weight, rpe))
    conn.commit()
    conn.close()


def get_workout(workout_id):
    conn = get_db()
    workout = conn.execute("SELECT * FROM workouts WHERE id = ?", (workout_id,)).fetchone()
    if not workout:
        conn.close()
        return None
    w = dict(workout)
    sets = conn.execute('''
        SELECT ws.*, e.name as exercise_name, e.category
        FROM workout_sets ws
        JOIN exercises e ON ws.exercise_id = e.id
        WHERE ws.workout_id = ?
        ORDER BY ws.id
    ''', (workout_id,)).fetchall()
    w['sets'] = [dict(s) for s in sets]
    conn.close()
    return w


def get_workouts(limit=50):
    conn = get_db()
    workouts = conn.execute('''
        SELECT w.*, COUNT(ws.id) as set_count
        FROM workouts w
        LEFT JOIN workout_sets ws ON w.id = ws.workout_id
        GROUP BY w.id
        ORDER BY w.created_at DESC
        LIMIT ?
    ''', (limit,)).fetchall()
    conn.close()
    return [dict(w) for w in workouts]


def delete_workout(workout_id):
    conn = get_db()
    conn.execute("DELETE FROM workouts WHERE id = ?", (workout_id,))
    conn.commit()
    conn.close()


# ── DASHBOARD STATS ───────────────────────────────────────────

def get_dashboard_stats():
    conn = get_db()

    total_workouts = conn.execute("SELECT COUNT(*) as cnt FROM workouts").fetchone()['cnt']
    total_sets = conn.execute("SELECT COUNT(*) as cnt FROM workout_sets").fetchone()['cnt']
    total_volume = conn.execute(
        "SELECT COALESCE(SUM(COALESCE(reps,0)), 0) as vol FROM workout_sets"
    ).fetchone()['vol']

    # This week's workouts
    week_workouts = conn.execute('''
        SELECT COUNT(*) as cnt FROM workouts
        WHERE created_at >= date('now', '-7 days')
    ''').fetchone()['cnt']

    # Streak: consecutive days with workouts
    streak = 0
    days = conn.execute('''
        SELECT DISTINCT date(created_at) as d FROM workouts
        ORDER BY d DESC
    ''').fetchall()
    if days:
        from datetime import date, timedelta
        today = date.today()
        for i, row in enumerate(days):
            day = date.fromisoformat(row['d'])
            expected = today - timedelta(days=i)
            if day == expected:
                streak += 1
            elif i == 0 and day == today - timedelta(days=1):
                # Allow starting from yesterday
                streak += 1
                today = today - timedelta(days=1)
            else:
                break

    # Volume per category over last 4 weeks
    category_volume = conn.execute('''
        SELECT e.category, strftime('%W', w.created_at) as week,
               SUM(COALESCE(ws.reps, 0)) as vol
        FROM workout_sets ws
        JOIN exercises e ON ws.exercise_id = e.id
        JOIN workouts w ON ws.workout_id = w.id
        WHERE w.created_at >= date('now', '-28 days')
        GROUP BY e.category, week
        ORDER BY week
    ''').fetchall()

    conn.close()
    return {
        'total_workouts': total_workouts,
        'total_sets': total_sets,
        'total_volume': total_volume,
        'week_workouts': week_workouts,
        'streak': streak,
        'category_volume': [dict(r) for r in category_volume],
    }


# ── ROUTINE TEMPLATES ─────────────────────────────────────────

def get_templates(preset_only=False):
    conn = get_db()
    query = "SELECT * FROM routine_templates"
    if preset_only:
        query += " WHERE is_preset = 1"
    query += " ORDER BY id"
    templates = conn.execute(query).fetchall()
    result = []
    for t in templates:
        tmpl = dict(t)
        exercises = conn.execute('''
            SELECT re.*, e.name as exercise_name, e.category, e.difficulty
            FROM routine_exercises re
            JOIN exercises e ON re.exercise_id = e.id
            WHERE re.template_id = ?
            ORDER BY re.exercise_order
        ''', (t['id'],)).fetchall()
        tmpl['exercises'] = [dict(e) for e in exercises]
        result.append(tmpl)
    conn.close()
    return result


def save_template(name, description, level, focus, duration, exercises):
    conn = get_db()
    cursor = conn.execute('''
        INSERT INTO routine_templates (name, description, level, focus, duration)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, description, level, focus, duration))
    tmpl_id = cursor.lastrowid
    for i, ex in enumerate(exercises):
        conn.execute('''
            INSERT INTO routine_exercises (template_id, exercise_id, exercise_order, sets, reps, rest_seconds, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (tmpl_id, ex['exercise_id'], i + 1, ex.get('sets', 3), ex.get('reps', ''), ex.get('rest', 60), ex.get('notes', '')))
    conn.commit()
    conn.close()
    return tmpl_id


def delete_template(template_id):
    conn = get_db()
    conn.execute("DELETE FROM routine_templates WHERE id = ? AND is_preset = 0", (template_id,))
    conn.commit()
    conn.close()


# ── USER PROFILE ──────────────────────────────────────────────

def get_profile():
    conn = get_db()
    row = conn.execute("SELECT * FROM user_profile WHERE id = 1").fetchone()
    conn.close()
    return dict(row) if row else {}


def update_profile(name, skill_level, goals):
    conn = get_db()
    conn.execute('''
        UPDATE user_profile SET name = ?, skill_level = ?, goals = ? WHERE id = 1
    ''', (name, skill_level, goals))
    conn.commit()
    conn.close()
