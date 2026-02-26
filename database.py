import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://localhost/kaizen_cali')


def get_db():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS exercises (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            difficulty INTEGER NOT NULL CHECK(difficulty BETWEEN 1 AND 10),
            muscle_groups TEXT,
            description TEXT,
            cues TEXT,
            equipment TEXT DEFAULT 'none',
            video_url TEXT
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS progressions (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            description TEXT
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS progression_steps (
            id SERIAL PRIMARY KEY,
            progression_id INTEGER NOT NULL REFERENCES progressions(id),
            step_order INTEGER NOT NULL,
            exercise_id INTEGER NOT NULL REFERENCES exercises(id),
            criteria TEXT
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL DEFAULT 'Athlete',
            skill_level TEXT NOT NULL DEFAULT 'beginner',
            goals TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS user_progression_status (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            progression_id INTEGER NOT NULL REFERENCES progressions(id),
            current_step INTEGER NOT NULL DEFAULT 1,
            achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, progression_id)
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name TEXT,
            workout_type TEXT,
            duration INTEGER,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS workout_sets (
            id SERIAL PRIMARY KEY,
            workout_id INTEGER NOT NULL REFERENCES workouts(id) ON DELETE CASCADE,
            exercise_id INTEGER NOT NULL REFERENCES exercises(id),
            set_number INTEGER NOT NULL DEFAULT 1,
            reps INTEGER,
            hold_time INTEGER,
            weight REAL DEFAULT 0,
            rpe INTEGER
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS routine_templates (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            description TEXT,
            level TEXT,
            focus TEXT,
            duration INTEGER,
            is_preset INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS routine_exercises (
            id SERIAL PRIMARY KEY,
            template_id INTEGER NOT NULL REFERENCES routine_templates(id) ON DELETE CASCADE,
            exercise_id INTEGER NOT NULL REFERENCES exercises(id),
            exercise_order INTEGER NOT NULL,
            sets INTEGER DEFAULT 3,
            reps TEXT,
            rest_seconds INTEGER DEFAULT 60,
            notes TEXT
        )
    ''')

    conn.commit()
    cur.close()
    conn.close()
