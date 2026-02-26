from database import get_db


def seed():
    conn = get_db()
    c = conn.cursor()

    # Check if already seeded
    c.execute("SELECT COUNT(*) FROM exercises")
    if c.fetchone()[0] > 0:
        conn.close()
        return

    # ── EXERCISES ──────────────────────────────────────────────
    exercises = [
        # PUSH (category='push')
        ("Wall Push-Up", "push", 1, "chest,shoulders,triceps", "Push-up against a wall for beginners.", "Keep body straight, lower chest to wall", "none", None),
        ("Incline Push-Up", "push", 2, "chest,shoulders,triceps", "Push-up on an elevated surface.", "Hands on bench or step, full range of motion", "none", None),
        ("Knee Push-Up", "push", 2, "chest,shoulders,triceps", "Push-up from the knees.", "Keep hips extended, lower chest to floor", "none", None),
        ("Push-Up", "push", 3, "chest,shoulders,triceps", "Standard push-up from toes.", "Body straight, chest to floor, elbows 45 degrees", "none", None),
        ("Diamond Push-Up", "push", 4, "triceps,chest", "Push-up with hands together forming a diamond.", "Hands under chest, elbows close to body", "none", None),
        ("Wide Push-Up", "push", 3, "chest,shoulders", "Push-up with hands wider than shoulders.", "Hands 1.5x shoulder width, control the descent", "none", None),
        ("Decline Push-Up", "push", 4, "upper chest,shoulders", "Push-up with feet elevated.", "Feet on a step or bench, maintain straight body", "none", None),
        ("Archer Push-Up", "push", 5, "chest,shoulders,triceps", "Push-up shifting weight to one arm.", "One arm extends to side, other arm does the work", "none", None),
        ("Pseudo Planche Push-Up", "push", 6, "shoulders,chest", "Push-up with hands turned back by hips.", "Lean forward, hands by waist, fingers point back", "none", None),
        ("One-Arm Push-Up", "push", 8, "chest,shoulders,triceps,core", "Push-up on a single arm.", "Wider stance, keep hips square, full range of motion", "none", None),
        ("Pike Push-Up", "push", 4, "shoulders,triceps", "Push-up in pike position targeting shoulders.", "Hips high, head between arms, lower head to floor", "none", None),
        ("Elevated Pike Push-Up", "push", 5, "shoulders,triceps", "Pike push-up with feet elevated.", "Feet on box, hips at 90 degrees", "none", None),
        ("Handstand Push-Up (Wall)", "push", 7, "shoulders,triceps", "Push-up in handstand against wall.", "Kick up to wall, lower head to floor, press up", "none", None),
        ("Freestanding HSPU", "push", 9, "shoulders,triceps,core", "Handstand push-up without wall support.", "Balance in handstand, controlled descent and press", "none", None),
        ("Planche Lean", "push", 5, "shoulders,core", "Lean forward in push-up position.", "Arms straight, lean forward shifting weight to hands", "none", None),
        ("Tuck Planche", "push", 7, "shoulders,core", "Hold planche with knees tucked.", "Arms straight, knees to chest, hips at hand height", "none", None),
        ("Straddle Planche", "push", 9, "shoulders,core", "Hold planche with legs straddled.", "Straight arms, legs wide, body horizontal", "none", None),
        ("Full Planche", "push", 10, "shoulders,core,chest", "Hold full planche position.", "Body horizontal, arms straight, legs together", "none", None),

        # PULL (category='pull')
        ("Dead Hang", "pull", 1, "forearms,shoulders", "Hang from bar with straight arms.", "Shoulders active, grip firm, breathe steadily", "bar", None),
        ("Scapular Pulls", "pull", 2, "back,shoulders", "Hang and pull shoulder blades down.", "Arms straight, depress scapulae, hold briefly", "bar", None),
        ("Australian Row", "pull", 2, "back,biceps", "Inverted row under a low bar.", "Body straight, pull chest to bar, squeeze back", "bar", None),
        ("Negative Pull-Up", "pull", 3, "back,biceps", "Slowly lower from top of pull-up.", "Jump to top, lower for 5 seconds, full extension", "bar", None),
        ("Chin-Up", "pull", 4, "biceps,back", "Pull-up with underhand grip.", "Palms facing you, pull chin over bar", "bar", None),
        ("Pull-Up", "pull", 4, "back,biceps", "Standard overhand pull-up.", "Dead hang to chin over bar, control the descent", "bar", None),
        ("Wide Pull-Up", "pull", 5, "back,shoulders", "Pull-up with wide overhand grip.", "Hands wider than shoulders, pull to upper chest", "bar", None),
        ("Close-Grip Pull-Up", "pull", 5, "biceps,back", "Pull-up with hands close together.", "Hands touching or close, chin over bar", "bar", None),
        ("L-Sit Pull-Up", "pull", 6, "back,biceps,core", "Pull-up while holding L-sit.", "Legs horizontal, pull chin over bar", "bar", None),
        ("Archer Pull-Up", "pull", 7, "back,biceps", "Pull-up shifting to one arm.", "Pull to one side, other arm extends along bar", "bar", None),
        ("Typewriter Pull-Up", "pull", 7, "back,biceps", "Pull up and move side to side at top.", "Pull up, traverse bar left to right", "bar", None),
        ("Muscle-Up", "pull", 8, "back,chest,triceps", "Pull-up transitioning to dip above bar.", "Explosive pull, lean forward over bar, press up", "bar", None),
        ("One-Arm Chin-Up", "pull", 10, "back,biceps", "Chin-up with a single arm.", "Full range of motion, control the movement", "bar", None),

        # LEGS (category='legs')
        ("Bodyweight Squat", "legs", 1, "quads,glutes", "Basic air squat.", "Feet shoulder width, sit back, knees track toes", "none", None),
        ("Split Squat", "legs", 2, "quads,glutes", "Stationary lunge position squat.", "Back foot elevated or on ground, front knee 90 degrees", "none", None),
        ("Bulgarian Split Squat", "legs", 3, "quads,glutes,balance", "Split squat with rear foot elevated.", "Rear foot on bench, lower until front thigh parallel", "none", None),
        ("Step-Up", "legs", 2, "quads,glutes", "Step up onto elevated surface.", "Drive through front heel, full extension at top", "none", None),
        ("Jump Squat", "legs", 3, "quads,glutes,power", "Squat followed by a jump.", "Full squat, explode upward, soft landing", "none", None),
        ("Cossack Squat", "legs", 4, "quads,adductors,mobility", "Deep side lunge with one leg straight.", "Shift weight to one side, other leg straight", "none", None),
        ("Pistol Squat (Assisted)", "legs", 5, "quads,glutes,balance", "Single-leg squat holding support.", "Hold pole or doorframe, squat on one leg", "none", None),
        ("Pistol Squat", "legs", 7, "quads,glutes,balance", "Full single-leg squat.", "One leg extended forward, full depth, stand up", "none", None),
        ("Shrimp Squat", "legs", 7, "quads,glutes", "Single-leg squat grabbing rear foot.", "Grab foot behind, squat until knee touches floor", "none", None),
        ("Nordic Curl (Assisted)", "legs", 5, "hamstrings", "Eccentric hamstring curl with support.", "Kneel, lower slowly, push off floor to return", "none", None),
        ("Nordic Curl", "legs", 8, "hamstrings", "Full nordic hamstring curl.", "Kneel, lower body controlled, hamstrings only", "none", None),
        ("Glute Bridge", "legs", 1, "glutes,hamstrings", "Lie on back, lift hips.", "Feet flat, squeeze glutes, lift hips high", "none", None),
        ("Single-Leg Glute Bridge", "legs", 3, "glutes,hamstrings", "Glute bridge on one leg.", "One leg extended, drive hips up with other leg", "none", None),
        ("Calf Raise", "legs", 1, "calves", "Rise up on toes.", "Slow up, pause at top, slow down", "none", None),
        ("Single-Leg Calf Raise", "legs", 3, "calves", "Calf raise on one leg.", "Full range of motion, hold at top", "none", None),

        # CORE (category='core')
        ("Dead Bug", "core", 1, "core,hip flexors", "Lie on back, extend opposite arm and leg.", "Lower back pressed to floor, move slowly", "none", None),
        ("Plank", "core", 2, "core", "Hold push-up position on forearms.", "Body straight, squeeze glutes, breathe steadily", "none", None),
        ("Side Plank", "core", 3, "obliques,core", "Hold side position on one forearm.", "Stack feet, hips up, body in straight line", "none", None),
        ("Hollow Body Hold", "core", 3, "core", "Lie on back, arms and legs extended off floor.", "Lower back pressed to floor, body in banana shape", "none", None),
        ("Hanging Knee Raise", "core", 3, "core,hip flexors", "Hang from bar, raise knees to chest.", "Controlled movement, no swinging", "bar", None),
        ("Hanging Leg Raise", "core", 5, "core,hip flexors", "Hang from bar, raise straight legs.", "Legs straight, raise to horizontal or higher", "bar", None),
        ("Toes to Bar", "core", 6, "core,hip flexors", "Hang from bar, touch toes to bar.", "Control the descent, minimize swing", "bar", None),
        ("Dragon Flag (Tuck)", "core", 5, "core", "Lie on bench, lift body with knees tucked.", "Shoulders stay down, lift from core", "none", None),
        ("Dragon Flag", "core", 7, "core", "Full dragon flag with straight body.", "Body rigid, lower slowly, shoulders anchored", "none", None),
        ("Ab Wheel Rollout", "core", 5, "core", "Roll ab wheel out and back.", "Tight core, full extension, control return", "none", None),
        ("Front Lever Tuck", "pull", 5, "back,lats,core", "Hang with body horizontal, knees tucked.", "Arms straight, body horizontal, knees to chest", "bar", None),
        ("Front Lever", "pull", 9, "back,lats,core", "Full front lever with straight body.", "Body horizontal, arms straight, everything tight", "bar", None),
        ("Back Lever", "core", 7, "shoulders,core", "Hang inverted with body horizontal behind bar.", "Arms straight, body horizontal below bar", "bar", None),

        # SKILLS (category='skill')
        ("Crow Pose", "skill", 3, "shoulders,core,balance", "Balance on hands with knees on triceps.", "Lean forward, knees on backs of arms, lift feet", "none", None),
        ("Frog Stand", "skill", 2, "shoulders,core,balance", "Balance on hands in tucked position.", "Hands on ground, knees on elbows, lean forward", "none", None),
        ("Wall Handstand", "skill", 3, "shoulders,core,balance", "Handstand with wall support.", "Kick up, belly to wall or back to wall, hold", "none", None),
        ("Freestanding Handstand", "skill", 7, "shoulders,core,balance", "Balance in handstand without support.", "Kick up, find balance, use fingers and wrists", "none", None),
        ("Elbow Lever", "skill", 4, "core,balance,shoulders", "Balance horizontally on bent arms.", "Elbow in hip crease, lean forward, lift legs", "none", None),
        ("Human Flag (Tuck)", "skill", 7, "obliques,shoulders,core", "Side flag on pole with knees tucked.", "Bottom arm pushes, top arm pulls, tuck knees", "bar", None),
        ("Human Flag", "skill", 10, "obliques,shoulders,core", "Full human flag with straight body.", "Body horizontal sideways, arms push/pull on pole", "bar", None),

        # MOBILITY (category='mobility')
        ("Shoulder Dislocates", "mobility", 1, "shoulders", "Pass a stick over head and behind back.", "Wide grip, straight arms, smooth circles", "none", None),
        ("Cat-Cow Stretch", "mobility", 1, "spine", "Alternate arching and rounding spine on hands and knees.", "Inhale arch, exhale round, move with breath", "none", None),
        ("Deep Squat Hold", "mobility", 1, "hips,ankles", "Sit in a deep squat position.", "Heels down, chest up, elbows push knees out", "none", None),
        ("Wrist Circles", "mobility", 1, "wrists", "Circle wrists in both directions.", "10 circles each direction, full range of motion", "none", None),
        ("Hip Circles", "mobility", 1, "hips", "Circle hips in both directions.", "Large circles, both directions, controlled", "none", None),
        ("Arm Circles", "mobility", 1, "shoulders", "Circle arms forward and backward.", "Start small, increase size, both directions", "none", None),
        ("World's Greatest Stretch", "mobility", 2, "hips,thoracic", "Lunge with twist and reach.", "Lunge, elbow to instep, rotate and reach up", "none", None),
        ("Pancake Stretch", "mobility", 2, "hamstrings,adductors", "Seated wide-leg forward fold.", "Legs wide, fold forward, chest toward floor", "none", None),
        ("Pike Stretch", "mobility", 2, "hamstrings", "Seated forward fold with legs together.", "Legs straight, fold forward, reach for toes", "none", None),
        ("Bridge", "mobility", 3, "spine,shoulders,wrists", "Full gymnastic bridge.", "Hands and feet on floor, push hips up high", "none", None),
        ("German Hang", "mobility", 3, "shoulders", "Hang behind the bar with shoulders extended.", "Slowly rotate behind bar, hold stretch", "bar", None),
        ("Skin the Cat", "mobility", 4, "shoulders,core", "Rotate through a full circle on bar.", "Pull legs over, rotate back, return to hang", "bar", None),
    ]

    c.executemany('''
        INSERT INTO exercises (name, category, difficulty, muscle_groups, description, cues, equipment, video_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', exercises)

    # ── PROGRESSIONS ──────────────────────────────────────────
    progressions = [
        ("Push-Up Progression", "push", "From wall push-ups to one-arm push-ups"),
        ("Pull-Up Progression", "pull", "From dead hangs to one-arm chin-ups"),
        ("Squat Progression", "legs", "From air squats to pistol squats"),
        ("Core Progression", "core", "From planks to dragon flags"),
        ("Dip Progression", "push", "From bench dips to weighted dips"),
        ("Handstand Progression", "skill", "From wall holds to freestanding HSPU"),
        ("Front Lever Progression", "pull", "From tuck to full front lever"),
        ("Back Lever Progression", "core", "From german hang to full back lever"),
        ("Planche Progression", "push", "From planche lean to full planche"),
        ("Muscle-Up Progression", "pull", "From pull-ups to clean muscle-ups"),
        ("L-Sit Progression", "core", "From tuck holds to full L-sit"),
        ("Human Flag Progression", "skill", "From tuck flag to full human flag"),
    ]

    c.executemany('''
        INSERT INTO progressions (name, category, description)
        VALUES (?, ?, ?)
    ''', progressions)

    # Helper: get exercise id by name
    def eid(name):
        c.execute("SELECT id FROM exercises WHERE name = ?", (name,))
        row = c.fetchone()
        if row:
            return row[0]
        return None

    # ── PROGRESSION STEPS ─────────────────────────────────────
    progression_steps = {
        "Push-Up Progression": [
            ("Wall Push-Up", "3x15 with good form"),
            ("Incline Push-Up", "3x12 with good form"),
            ("Knee Push-Up", "3x15 with good form"),
            ("Push-Up", "3x15 with good form"),
            ("Diamond Push-Up", "3x12 with good form"),
            ("Archer Push-Up", "3x8 each side"),
            ("One-Arm Push-Up", "3x5 each side"),
        ],
        "Pull-Up Progression": [
            ("Dead Hang", "30 second hold"),
            ("Scapular Pulls", "3x10 with control"),
            ("Australian Row", "3x12 with good form"),
            ("Negative Pull-Up", "3x5 with 5-second descent"),
            ("Chin-Up", "3x8 with good form"),
            ("Pull-Up", "3x10 with good form"),
            ("Wide Pull-Up", "3x8 with good form"),
            ("Archer Pull-Up", "3x5 each side"),
            ("One-Arm Chin-Up", "1x1 each side"),
        ],
        "Squat Progression": [
            ("Bodyweight Squat", "3x20 with good form"),
            ("Split Squat", "3x12 each leg"),
            ("Bulgarian Split Squat", "3x10 each leg"),
            ("Cossack Squat", "3x8 each side"),
            ("Pistol Squat (Assisted)", "3x5 each leg"),
            ("Pistol Squat", "3x5 each leg"),
            ("Shrimp Squat", "3x5 each leg"),
        ],
        "Core Progression": [
            ("Dead Bug", "3x10 each side"),
            ("Plank", "60 second hold"),
            ("Hollow Body Hold", "30 second hold"),
            ("Hanging Knee Raise", "3x12"),
            ("Hanging Leg Raise", "3x10"),
            ("Toes to Bar", "3x8"),
            ("Dragon Flag (Tuck)", "3x5"),
            ("Dragon Flag", "3x5"),
        ],
        "Dip Progression": [
            ("Knee Push-Up", "3x15 with good form"),
            ("Push-Up", "3x15 with good form"),
            ("Diamond Push-Up", "3x12 with good form"),
            ("Decline Push-Up", "3x12 with good form"),
            ("Pike Push-Up", "3x10 with good form"),
        ],
        "Handstand Progression": [
            ("Pike Push-Up", "3x10 with good form"),
            ("Elevated Pike Push-Up", "3x8 with good form"),
            ("Wall Handstand", "3x30 second hold"),
            ("Freestanding Handstand", "30 second hold"),
            ("Handstand Push-Up (Wall)", "3x5"),
            ("Freestanding HSPU", "3x3"),
        ],
        "Front Lever Progression": [
            ("Dead Hang", "30 second hold"),
            ("Scapular Pulls", "3x10"),
            ("Front Lever Tuck", "3x10 second hold"),
            ("Front Lever", "10 second hold"),
        ],
        "Back Lever Progression": [
            ("German Hang", "3x15 second hold"),
            ("Skin the Cat", "3x5 controlled"),
            ("Back Lever", "10 second hold"),
        ],
        "Planche Progression": [
            ("Planche Lean", "3x15 seconds"),
            ("Pseudo Planche Push-Up", "3x8"),
            ("Tuck Planche", "3x10 second hold"),
            ("Straddle Planche", "10 second hold"),
            ("Full Planche", "5 second hold"),
        ],
        "Muscle-Up Progression": [
            ("Pull-Up", "3x10 with good form"),
            ("Wide Pull-Up", "3x8"),
            ("L-Sit Pull-Up", "3x5"),
            ("Typewriter Pull-Up", "3x3 each side"),
            ("Muscle-Up", "3x3 clean reps"),
        ],
        "L-Sit Progression": [
            ("Plank", "60 second hold"),
            ("Hollow Body Hold", "30 second hold"),
            ("Dead Bug", "3x10 each side"),
            ("Hanging Knee Raise", "3x15"),
            ("Hanging Leg Raise", "3x10"),
        ],
        "Human Flag Progression": [
            ("Side Plank", "3x30 seconds each side"),
            ("Hanging Leg Raise", "3x10"),
            ("Human Flag (Tuck)", "3x5 second hold each side"),
            ("Human Flag", "5 second hold each side"),
        ],
    }

    for prog_name, steps in progression_steps.items():
        c.execute("SELECT id FROM progressions WHERE name = ?", (prog_name,))
        prog_id = c.fetchone()[0]
        for order, (ex_name, criteria) in enumerate(steps, 1):
            ex_id = eid(ex_name)
            if ex_id:
                c.execute('''
                    INSERT INTO progression_steps (progression_id, step_order, exercise_id, criteria)
                    VALUES (?, ?, ?, ?)
                ''', (prog_id, order, ex_id, criteria))

    # ── INITIAL PROGRESSION STATUS (all start at step 1) ──────
    c.execute("SELECT id FROM progressions")
    for row in c.fetchall():
        c.execute('''
            INSERT OR IGNORE INTO user_progression_status (progression_id, current_step)
            VALUES (?, 1)
        ''', (row[0],))

    # ── PRESET ROUTINE TEMPLATES ──────────────────────────────
    templates = [
        ("Beginner Full Body", "A balanced full-body routine for beginners", "beginner", "full body", 45, 1),
        ("Intermediate Push-Pull-Legs", "PPL split for intermediate athletes", "intermediate", "push/pull", 60, 1),
        ("Advanced Skill-Focused", "Skill work with strength base", "advanced", "skills", 75, 1),
    ]

    c.executemany('''
        INSERT INTO routine_templates (name, description, level, focus, duration, is_preset)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', templates)

    # Beginner Full Body routine
    beginner_exercises = [
        ("Arm Circles", 1, 2, "30 seconds", 30, "Warmup"),
        ("Deep Squat Hold", 2, 2, "30 seconds", 30, "Warmup"),
        ("Wrist Circles", 3, 2, "20 each direction", 30, "Warmup"),
        ("Push-Up", 4, 3, "8-12", 60, None),
        ("Australian Row", 5, 3, "8-12", 60, None),
        ("Bodyweight Squat", 6, 3, "12-15", 60, None),
        ("Plank", 7, 3, "30-60 seconds", 60, None),
        ("Glute Bridge", 8, 3, "12-15", 60, None),
        ("Dead Bug", 9, 3, "10 each side", 60, None),
    ]

    c.execute("SELECT id FROM routine_templates WHERE name = 'Beginner Full Body'")
    tmpl_id = c.fetchone()[0]
    for ex_name, order, sets, reps, rest, notes in beginner_exercises:
        ex_id = eid(ex_name)
        if ex_id:
            c.execute('''
                INSERT INTO routine_exercises (template_id, exercise_id, exercise_order, sets, reps, rest_seconds, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (tmpl_id, ex_id, order, sets, reps, rest, notes))

    # Intermediate PPL routine
    intermediate_exercises = [
        ("Shoulder Dislocates", 1, 2, "10", 30, "Warmup"),
        ("Cat-Cow Stretch", 2, 2, "10 each", 30, "Warmup"),
        ("Diamond Push-Up", 3, 4, "8-10", 90, None),
        ("Decline Push-Up", 4, 3, "10-12", 60, None),
        ("Pike Push-Up", 5, 3, "8-10", 90, None),
        ("Pull-Up", 6, 4, "6-8", 90, None),
        ("Australian Row", 7, 3, "10-12", 60, None),
        ("Bulgarian Split Squat", 8, 3, "8-10 each", 90, None),
        ("Nordic Curl (Assisted)", 9, 3, "5-8", 90, None),
        ("Hanging Leg Raise", 10, 3, "8-10", 60, None),
    ]

    c.execute("SELECT id FROM routine_templates WHERE name = 'Intermediate Push-Pull-Legs'")
    tmpl_id = c.fetchone()[0]
    for ex_name, order, sets, reps, rest, notes in intermediate_exercises:
        ex_id = eid(ex_name)
        if ex_id:
            c.execute('''
                INSERT INTO routine_exercises (template_id, exercise_id, exercise_order, sets, reps, rest_seconds, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (tmpl_id, ex_id, order, sets, reps, rest, notes))

    # Advanced Skill-Focused routine
    advanced_exercises = [
        ("Shoulder Dislocates", 1, 2, "10", 30, "Warmup"),
        ("Wrist Circles", 2, 2, "20 each", 30, "Warmup"),
        ("Skin the Cat", 3, 3, "5", 60, "Warmup/Skill"),
        ("Wall Handstand", 4, 3, "30 seconds", 90, "Skill"),
        ("Tuck Planche", 5, 5, "10 seconds", 120, "Skill"),
        ("Front Lever Tuck", 6, 5, "10 seconds", 120, "Skill"),
        ("Muscle-Up", 7, 3, "3-5", 120, None),
        ("Pistol Squat", 8, 3, "5 each", 90, None),
        ("Dragon Flag", 9, 3, "5", 90, None),
    ]

    c.execute("SELECT id FROM routine_templates WHERE name = 'Advanced Skill-Focused'")
    tmpl_id = c.fetchone()[0]
    for ex_name, order, sets, reps, rest, notes in advanced_exercises:
        ex_id = eid(ex_name)
        if ex_id:
            c.execute('''
                INSERT INTO routine_exercises (template_id, exercise_id, exercise_order, sets, reps, rest_seconds, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (tmpl_id, ex_id, order, sets, reps, rest, notes))

    conn.commit()
    conn.close()


if __name__ == '__main__':
    from database import init_db
    init_db()
    seed()
    print("Database seeded successfully!")
