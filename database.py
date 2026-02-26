import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'calisthenics.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            difficulty INTEGER NOT NULL CHECK(difficulty BETWEEN 1 AND 10),
            muscle_groups TEXT,
            description TEXT,
            cues TEXT,
            equipment TEXT DEFAULT 'none',
            video_url TEXT
        );

        CREATE TABLE IF NOT EXISTS progressions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS progression_steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            progression_id INTEGER NOT NULL,
            step_order INTEGER NOT NULL,
            exercise_id INTEGER NOT NULL,
            criteria TEXT,
            FOREIGN KEY (progression_id) REFERENCES progressions(id),
            FOREIGN KEY (exercise_id) REFERENCES exercises(id)
        );

        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY CHECK(id = 1),
            name TEXT DEFAULT 'Athlete',
            skill_level TEXT DEFAULT 'beginner',
            goals TEXT DEFAULT 'general fitness',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS user_progression_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            progression_id INTEGER NOT NULL UNIQUE,
            current_step INTEGER NOT NULL DEFAULT 1,
            achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (progression_id) REFERENCES progressions(id)
        );

        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            workout_type TEXT,
            duration INTEGER,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS workout_sets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_id INTEGER NOT NULL,
            exercise_id INTEGER NOT NULL,
            set_number INTEGER NOT NULL DEFAULT 1,
            reps INTEGER,
            hold_time INTEGER,
            weight REAL DEFAULT 0,
            rpe INTEGER,
            FOREIGN KEY (workout_id) REFERENCES workouts(id) ON DELETE CASCADE,
            FOREIGN KEY (exercise_id) REFERENCES exercises(id)
        );

        CREATE TABLE IF NOT EXISTS routine_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            level TEXT,
            focus TEXT,
            duration INTEGER,
            is_preset INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS routine_exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_id INTEGER NOT NULL,
            exercise_id INTEGER NOT NULL,
            exercise_order INTEGER NOT NULL,
            sets INTEGER DEFAULT 3,
            reps TEXT,
            rest_seconds INTEGER DEFAULT 60,
            notes TEXT,
            FOREIGN KEY (template_id) REFERENCES routine_templates(id) ON DELETE CASCADE,
            FOREIGN KEY (exercise_id) REFERENCES exercises(id)
        );
    ''')

    # Ensure user profile exists
    cursor.execute("INSERT OR IGNORE INTO user_profile (id) VALUES (1)")
    conn.commit()
    conn.close()
