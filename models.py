from database import get_db
from werkzeug.security import generate_password_hash, check_password_hash


# ── AUTH ─────────────────────────────────────────────────────

def create_user(email, password, name='Athlete'):
    conn = get_db()
    cur = conn.cursor()
    password_hash = generate_password_hash(password)
    cur.execute('''
        INSERT INTO users (email, password_hash, name)
        VALUES (%s, %s, %s)
        RETURNING id
    ''', (email, password_hash, name))
    user_id = cur.fetchone()['id']

    # Initialize progression status for this user
    cur.execute("SELECT id FROM progressions")
    for row in cur.fetchall():
        cur.execute('''
            INSERT INTO user_progression_status (user_id, progression_id, current_step)
            VALUES (%s, %s, 1)
            ON CONFLICT (user_id, progression_id) DO NOTHING
        ''', (user_id, row['id']))

    conn.commit()
    cur.close()
    conn.close()
    return user_id


def get_user_by_email(email):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return dict(user) if user else None


def get_user_by_id(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return dict(user) if user else None


def verify_password(stored_hash, password):
    return check_password_hash(stored_hash, password)


# ── EXERCISES ─────────────────────────────────────────────────

def get_all_exercises(category=None, difficulty_min=None, difficulty_max=None, search=None):
    conn = get_db()
    cur = conn.cursor()
    query = "SELECT * FROM exercises WHERE 1=1"
    params = []
    if category:
        query += " AND category = %s"
        params.append(category)
    if difficulty_min:
        query += " AND difficulty >= %s"
        params.append(difficulty_min)
    if difficulty_max:
        query += " AND difficulty <= %s"
        params.append(difficulty_max)
    if search:
        query += " AND (name ILIKE %s OR description ILIKE %s OR muscle_groups ILIKE %s)"
        params.extend([f"%{search}%"] * 3)
    query += " ORDER BY category, difficulty, name"
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in rows]


def get_exercise(exercise_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM exercises WHERE id = %s", (exercise_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return dict(row) if row else None


# ── PROGRESSIONS ──────────────────────────────────────────────

def get_all_progressions(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM progressions ORDER BY id")
    progs = cur.fetchall()
    result = []
    for p in progs:
        prog = dict(p)
        cur.execute('''
            SELECT ps.*, e.name as exercise_name, e.difficulty, e.description as exercise_description
            FROM progression_steps ps
            JOIN exercises e ON ps.exercise_id = e.id
            WHERE ps.progression_id = %s
            ORDER BY ps.step_order
        ''', (p['id'],))
        prog['steps'] = [dict(s) for s in cur.fetchall()]

        cur.execute('''
            SELECT current_step, achieved_at FROM user_progression_status
            WHERE user_id = %s AND progression_id = %s
        ''', (user_id, p['id']))
        status = cur.fetchone()
        prog['current_step'] = status['current_step'] if status else 1
        result.append(prog)
    cur.close()
    conn.close()
    return result


def advance_progression(user_id, progression_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT current_step FROM user_progression_status WHERE user_id = %s AND progression_id = %s",
        (user_id, progression_id)
    )
    status = cur.fetchone()
    cur.execute(
        "SELECT COUNT(*) as cnt FROM progression_steps WHERE progression_id = %s",
        (progression_id,)
    )
    total = cur.fetchone()['cnt']

    current = status['current_step'] if status else 1
    if current < total:
        new_step = current + 1
        cur.execute('''
            INSERT INTO user_progression_status (user_id, progression_id, current_step, achieved_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (user_id, progression_id) DO UPDATE SET current_step = %s, achieved_at = CURRENT_TIMESTAMP
        ''', (user_id, progression_id, new_step, new_step))
        conn.commit()
        cur.close()
        conn.close()
        return new_step
    cur.close()
    conn.close()
    return current


def regress_progression(user_id, progression_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT current_step FROM user_progression_status WHERE user_id = %s AND progression_id = %s",
        (user_id, progression_id)
    )
    status = cur.fetchone()
    current = status['current_step'] if status else 1
    if current > 1:
        new_step = current - 1
        cur.execute('''
            UPDATE user_progression_status SET current_step = %s, achieved_at = CURRENT_TIMESTAMP
            WHERE user_id = %s AND progression_id = %s
        ''', (new_step, user_id, progression_id))
        conn.commit()
        cur.close()
        conn.close()
        return new_step
    cur.close()
    conn.close()
    return current


# ── WORKOUTS ──────────────────────────────────────────────────

def create_workout(user_id, name, workout_type='custom', duration=None, notes=None):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO workouts (user_id, name, workout_type, duration, notes)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    ''', (user_id, name, workout_type, duration, notes))
    workout_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    return workout_id


def add_workout_set(workout_id, exercise_id, set_number, reps=None, hold_time=None, weight=0, rpe=None):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO workout_sets (workout_id, exercise_id, set_number, reps, hold_time, weight, rpe)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (workout_id, exercise_id, set_number, reps, hold_time, weight, rpe))
    conn.commit()
    cur.close()
    conn.close()


def get_workout(user_id, workout_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM workouts WHERE id = %s AND user_id = %s", (workout_id, user_id))
    workout = cur.fetchone()
    if not workout:
        cur.close()
        conn.close()
        return None
    w = dict(workout)
    cur.execute('''
        SELECT ws.*, e.name as exercise_name, e.category
        FROM workout_sets ws
        JOIN exercises e ON ws.exercise_id = e.id
        WHERE ws.workout_id = %s
        ORDER BY ws.id
    ''', (workout_id,))
    w['sets'] = [dict(s) for s in cur.fetchall()]
    cur.close()
    conn.close()
    return w


def get_workouts(user_id, limit=50):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT w.*, COUNT(ws.id) as set_count
        FROM workouts w
        LEFT JOIN workout_sets ws ON w.id = ws.workout_id
        WHERE w.user_id = %s
        GROUP BY w.id
        ORDER BY w.created_at DESC
        LIMIT %s
    ''', (user_id, limit))
    workouts = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(w) for w in workouts]


def delete_workout(user_id, workout_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM workouts WHERE id = %s AND user_id = %s", (workout_id, user_id))
    conn.commit()
    cur.close()
    conn.close()


# ── DASHBOARD STATS ───────────────────────────────────────────

def get_dashboard_stats(user_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) as cnt FROM workouts WHERE user_id = %s", (user_id,))
    total_workouts = cur.fetchone()['cnt']

    cur.execute('''
        SELECT COUNT(*) as cnt FROM workout_sets ws
        JOIN workouts w ON ws.workout_id = w.id
        WHERE w.user_id = %s
    ''', (user_id,))
    total_sets = cur.fetchone()['cnt']

    cur.execute('''
        SELECT COALESCE(SUM(COALESCE(ws.reps,0)), 0) as vol FROM workout_sets ws
        JOIN workouts w ON ws.workout_id = w.id
        WHERE w.user_id = %s
    ''', (user_id,))
    total_volume = cur.fetchone()['vol']

    # This week's workouts
    cur.execute('''
        SELECT COUNT(*) as cnt FROM workouts
        WHERE user_id = %s AND created_at >= CURRENT_DATE - INTERVAL '7 days'
    ''', (user_id,))
    week_workouts = cur.fetchone()['cnt']

    # Streak: consecutive days with workouts
    streak = 0
    cur.execute('''
        SELECT DISTINCT created_at::date as d FROM workouts
        WHERE user_id = %s
        ORDER BY d DESC
    ''', (user_id,))
    days = cur.fetchall()
    if days:
        from datetime import date, timedelta
        today = date.today()
        for i, row in enumerate(days):
            day = row['d']
            expected = today - timedelta(days=i)
            if day == expected:
                streak += 1
            elif i == 0 and day == today - timedelta(days=1):
                streak += 1
                today = today - timedelta(days=1)
            else:
                break

    # Volume per category over last 4 weeks
    cur.execute('''
        SELECT e.category, EXTRACT(WEEK FROM w.created_at)::TEXT as week,
               SUM(COALESCE(ws.reps, 0)) as vol
        FROM workout_sets ws
        JOIN exercises e ON ws.exercise_id = e.id
        JOIN workouts w ON ws.workout_id = w.id
        WHERE w.user_id = %s AND w.created_at >= CURRENT_DATE - INTERVAL '28 days'
        GROUP BY e.category, week
        ORDER BY week
    ''', (user_id,))
    category_volume = cur.fetchall()

    cur.close()
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

def get_templates(user_id, preset_only=False):
    conn = get_db()
    cur = conn.cursor()
    if preset_only:
        cur.execute("SELECT * FROM routine_templates WHERE is_preset = 1 ORDER BY id")
    else:
        cur.execute('''
            SELECT * FROM routine_templates
            WHERE is_preset = 1 OR user_id = %s
            ORDER BY id
        ''', (user_id,))
    templates = cur.fetchall()
    result = []
    for t in templates:
        tmpl = dict(t)
        cur.execute('''
            SELECT re.*, e.name as exercise_name, e.category, e.difficulty
            FROM routine_exercises re
            JOIN exercises e ON re.exercise_id = e.id
            WHERE re.template_id = %s
            ORDER BY re.exercise_order
        ''', (t['id'],))
        tmpl['exercises'] = [dict(e) for e in cur.fetchall()]
        result.append(tmpl)
    cur.close()
    conn.close()
    return result


def save_template(user_id, name, description, level, focus, duration, exercises):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO routine_templates (user_id, name, description, level, focus, duration)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    ''', (user_id, name, description, level, focus, duration))
    tmpl_id = cur.fetchone()['id']
    for i, ex in enumerate(exercises):
        cur.execute('''
            INSERT INTO routine_exercises (template_id, exercise_id, exercise_order, sets, reps, rest_seconds, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (tmpl_id, ex['exercise_id'], i + 1, ex.get('sets', 3), ex.get('reps', ''), ex.get('rest', 60), ex.get('notes', '')))
    conn.commit()
    cur.close()
    conn.close()
    return tmpl_id


def delete_template(user_id, template_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM routine_templates WHERE id = %s AND is_preset = 0 AND user_id = %s", (template_id, user_id))
    conn.commit()
    cur.close()
    conn.close()


# ── USER PROFILE ──────────────────────────────────────────────

def get_profile(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, skill_level, goals, email, created_at FROM users WHERE id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return dict(row) if row else {}


def update_profile(user_id, name, skill_level, goals):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        UPDATE users SET name = %s, skill_level = %s, goals = %s WHERE id = %s
    ''', (name, skill_level, goals, user_id))
    conn.commit()
    cur.close()
    conn.close()
