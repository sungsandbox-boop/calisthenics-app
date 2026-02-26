import os
import re
import sqlite3

DATABASE_URL = os.environ.get('DATABASE_URL', '')
USE_POSTGRES = bool(DATABASE_URL)

if USE_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor


# ── SQLite Compatibility Layer ───────────────────────────────
# Wraps SQLite to accept PostgreSQL syntax so models.py,
# seed_data.py, and generator.py work unchanged on both.

class SQLiteCursor:
    def __init__(self, cursor):
        self._cursor = cursor
        self._returning = False

    def execute(self, query, params=None):
        query = self._adapt(query)
        if params:
            self._cursor.execute(query, tuple(params))
        else:
            self._cursor.execute(query)
        return self

    def _adapt(self, q):
        self._returning = False

        # SERIAL PRIMARY KEY -> INTEGER PRIMARY KEY
        q = re.sub(r'SERIAL\s+PRIMARY\s+KEY', 'INTEGER PRIMARY KEY', q, flags=re.I)

        # RETURNING <col> — strip and flag for lastrowid
        if re.search(r'\bRETURNING\s+\w+', q, flags=re.I):
            q = re.sub(r'\s*RETURNING\s+\w+', '', q, flags=re.I)
            self._returning = True

        # ILIKE -> LIKE (SQLite LIKE is case-insensitive for ASCII)
        q = re.sub(r'\bILIKE\b', 'LIKE', q, flags=re.I)

        # CURRENT_DATE - INTERVAL 'N days' -> date('now', '-N days')
        q = re.sub(
            r"CURRENT_DATE\s*-\s*INTERVAL\s*'(\d+)\s*days?'",
            r"date('now', '-\1 days')", q, flags=re.I
        )

        # EXTRACT(WEEK FROM col)::TEXT -> strftime('%W', col)
        q = re.sub(
            r"EXTRACT\s*\(\s*WEEK\s+FROM\s+([\w.]+)\s*\)::TEXT",
            r"strftime('%W', \1)", q, flags=re.I
        )

        # col::date -> date(col)
        q = re.sub(r'(\w+(?:\.\w+)?)::date', r'date(\1)', q, flags=re.I)

        # %s -> ?
        q = q.replace('%s', '?')

        return q

    def fetchone(self):
        if self._returning:
            return {'id': self._cursor.lastrowid}
        row = self._cursor.fetchone()
        return dict(row) if row else None

    def fetchall(self):
        return [dict(row) for row in self._cursor.fetchall()]

    def close(self):
        self._cursor.close()


class SQLiteConnection:
    def __init__(self, path):
        self._conn = sqlite3.connect(path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")

    def cursor(self):
        return SQLiteCursor(self._conn.cursor())

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()


# ── Public API ───────────────────────────────────────────────

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kaizen_cali.db')


def get_db():
    if USE_POSTGRES:
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return SQLiteConnection(DB_PATH)


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
