import random
from database import get_db


def generate_workout(level='beginner', focus='full body', duration=45, goal='strength', equipment='none'):
    conn = get_db()

    # Map level to difficulty range
    level_ranges = {
        'beginner': (1, 3),
        'intermediate': (3, 6),
        'advanced': (6, 10),
    }
    diff_min, diff_max = level_ranges.get(level, (1, 10))

    # Map focus to categories
    focus_categories = {
        'full body': ['push', 'pull', 'legs', 'core'],
        'push': ['push'],
        'pull': ['pull'],
        'legs': ['legs'],
        'core': ['core'],
        'upper body': ['push', 'pull'],
        'skills': ['skill', 'push', 'pull', 'core'],
        'push/pull': ['push', 'pull'],
    }
    categories = focus_categories.get(focus, ['push', 'pull', 'legs', 'core'])

    # Goal-based volume
    goal_params = {
        'strength': {'sets': 4, 'reps': '3-5', 'rest': 120},
        'endurance': {'sets': 3, 'reps': '12-20', 'rest': 45},
        'skill': {'sets': 3, 'reps': '5-8', 'rest': 90},
        'hypertrophy': {'sets': 4, 'reps': '8-12', 'rest': 75},
    }
    vol = goal_params.get(goal, goal_params['strength'])

    # Get user's current progression exercises for preference
    progression_exercises = set()
    prog_data = conn.execute('''
        SELECT ps.exercise_id
        FROM user_progression_status ups
        JOIN progression_steps ps ON ups.progression_id = ps.progression_id
            AND ps.step_order = ups.current_step
    ''').fetchall()
    for row in prog_data:
        progression_exercises.add(row['exercise_id'])

    # Fetch candidate exercises
    equipment_filter = ""
    eq_params = []
    if equipment == 'none':
        equipment_filter = " AND equipment = 'none'"
    elif equipment == 'bar':
        equipment_filter = " AND equipment IN ('none', 'bar')"

    placeholders = ','.join('?' * len(categories))
    query = f'''
        SELECT * FROM exercises
        WHERE category IN ({placeholders})
        AND difficulty BETWEEN ? AND ?
        {equipment_filter}
        ORDER BY difficulty
    '''
    params = categories + [diff_min, diff_max] + eq_params
    candidates = conn.execute(query, params).fetchall()
    candidates = [dict(r) for r in candidates]

    # Also get warmup/mobility exercises
    warmup = conn.execute('''
        SELECT * FROM exercises WHERE category = 'mobility' AND difficulty <= 2
        ORDER BY RANDOM() LIMIT 3
    ''').fetchall()
    warmup = [dict(r) for r in warmup]

    conn.close()

    # Estimate exercise count based on duration
    # Rough estimate: 5 min warmup + ~5 min per exercise (including rest)
    available_time = duration - 5  # subtract warmup time
    time_per_exercise = vol['sets'] * 1.5 + vol['rest'] * vol['sets'] / 60  # rough minutes
    exercise_count = max(3, min(len(candidates), int(available_time / max(time_per_exercise, 3))))

    # Select exercises: prefer progression exercises, ensure category diversity
    selected = []
    used_ids = set()

    # First: try to include progression exercises that are in candidates
    for ex in candidates:
        if ex['id'] in progression_exercises and ex['id'] not in used_ids:
            selected.append(ex)
            used_ids.add(ex['id'])
            if len(selected) >= exercise_count:
                break

    # Fill remaining slots with diverse category picks
    if len(selected) < exercise_count:
        by_category = {}
        for ex in candidates:
            if ex['id'] not in used_ids:
                by_category.setdefault(ex['category'], []).append(ex)

        # Round-robin from categories
        cat_lists = list(by_category.values())
        for cat_exercises in cat_lists:
            random.shuffle(cat_exercises)

        idx = 0
        while len(selected) < exercise_count and cat_lists:
            cat = cat_lists[idx % len(cat_lists)]
            if cat:
                ex = cat.pop(0)
                selected.append(ex)
                used_ids.add(ex['id'])
            else:
                cat_lists.pop(idx % len(cat_lists))
                if not cat_lists:
                    break
                continue
            idx += 1

    # Build the workout
    workout_exercises = []

    # Add warmup exercises
    for i, ex in enumerate(warmup):
        workout_exercises.append({
            'exercise_id': ex['id'],
            'exercise_name': ex['name'],
            'category': ex['category'],
            'difficulty': ex['difficulty'],
            'sets': 2,
            'reps': '30 seconds' if ex['difficulty'] <= 1 else '10',
            'rest': 30,
            'notes': 'Warmup',
            'order': i + 1,
        })

    # Add main exercises
    for i, ex in enumerate(selected):
        is_skill = ex['category'] == 'skill'
        workout_exercises.append({
            'exercise_id': ex['id'],
            'exercise_name': ex['name'],
            'category': ex['category'],
            'difficulty': ex['difficulty'],
            'sets': vol['sets'] if not is_skill else 5,
            'reps': vol['reps'] if not is_skill else '5-10 seconds',
            'rest': vol['rest'] if not is_skill else 120,
            'notes': 'Skill work' if is_skill else None,
            'order': len(warmup) + i + 1,
        })

    return {
        'name': f"{level.title()} {focus.title()} Workout",
        'level': level,
        'focus': focus,
        'duration': duration,
        'goal': goal,
        'exercises': workout_exercises,
    }
