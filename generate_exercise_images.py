"""
Generate exercise demo images using DALL-E 3.

Creates 2 images per exercise (start + end position) in a consistent
minimalist illustration style. Saves to static/images/exercises/.

Usage:
    export OPENAI_API_KEY="sk-..."
    python generate_exercise_images.py

Requires: pip install openai requests
"""

import os
import json
import time
import requests
from pathlib import Path
from openai import OpenAI

OUTPUT_DIR = Path(__file__).parent / "static" / "images" / "exercises"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

STYLE_PREFIX = (
    "Minimalist flat vector fitness illustration on a solid dark background (#1a1d27). "
    "A fit athletic figure shown in side view demonstrating the exercise. "
    "Clean lines, no text, no labels, muted colors with indigo (#6366f1) accent highlights "
    "on active muscles. Simple, modern, app-ready style. "
)

# (exercise_name, slug, start_prompt, end_prompt)
EXERCISES = [
    # PUSH
    ("Wall Push-Up", "wall-push-up",
     "Person standing facing a wall with arms extended, hands flat on wall at chest height, body straight at slight angle",
     "Person leaning into wall with bent arms, chest close to wall, body in a straight line at an angle"),
    ("Incline Push-Up", "incline-push-up",
     "Person in push-up position with hands on a bench/elevated surface, arms straight, body in straight line",
     "Person in lowered push-up position with hands on bench, chest near bench, elbows bent"),
    ("Knee Push-Up", "knee-push-up",
     "Person in push-up position from knees, arms straight, body straight from knees to head",
     "Person lowered to floor in knee push-up, chest near ground, elbows bent at 45 degrees"),
    ("Push-Up", "push-up",
     "Person in high plank push-up position, arms fully extended, body straight from head to toes",
     "Person in bottom of push-up, chest near floor, elbows bent at 45 degrees, body straight"),
    ("Diamond Push-Up", "diamond-push-up",
     "Person in push-up position with hands close together forming a diamond shape under chest, arms straight",
     "Person lowered in diamond push-up, chest touching hands, elbows close to body"),
    ("Wide Push-Up", "wide-push-up",
     "Person in push-up position with hands placed wide apart, wider than shoulders, arms straight",
     "Person lowered in wide push-up, chest near floor, elbows flared out"),
    ("Decline Push-Up", "decline-push-up",
     "Person in push-up position with feet elevated on a bench, arms straight, body angled downward",
     "Person lowered in decline push-up, head near floor, feet still elevated on bench"),
    ("Archer Push-Up", "archer-push-up",
     "Person in wide push-up position, one arm straight to the side, weight shifted to the other arm",
     "Person lowered on one arm in archer push-up, other arm extended straight, body close to floor"),
    ("Pseudo Planche Push-Up", "pseudo-planche-push-up",
     "Person in push-up position with hands rotated backward near waist, fingers pointing toward feet, leaning forward",
     "Person lowered in pseudo planche push-up, body leaned forward, chest near floor, hands by waist"),
    ("One-Arm Push-Up", "one-arm-push-up",
     "Person in push-up position balancing on one arm, other arm behind back, wide foot stance",
     "Person lowered on one arm, chest near floor, other arm behind back, wide stance"),
    ("Pike Push-Up", "pike-push-up",
     "Person in pike position, hips high in inverted V shape, arms straight, head between arms",
     "Person in pike position lowered, head near floor between hands, elbows bent"),
    ("Elevated Pike Push-Up", "elevated-pike-push-up",
     "Person in pike position with feet on a box, hips at 90 degrees, arms straight, head between arms",
     "Person in elevated pike lowered, head near floor, feet on box, elbows bent"),
    ("Handstand Push-Up (Wall)", "handstand-push-up-wall",
     "Person in handstand against a wall, arms fully extended, body vertical and straight",
     "Person in handstand against wall, lowered with head near floor, elbows bent"),
    ("Freestanding HSPU", "freestanding-hspu",
     "Person in freestanding handstand, no wall, arms fully extended, body perfectly vertical",
     "Person in freestanding handstand lowered, head near floor, balancing without wall"),
    ("Planche Lean", "planche-lean",
     "Person in push-up position leaning far forward, shoulders past hands, arms straight, on toes",
     "Person in maximum planche lean, shoulders well past wrists, body angled forward, arms straight"),
    ("Tuck Planche", "tuck-planche",
     "Person holding tuck planche, arms straight on floor, knees tucked to chest, body lifted off ground horizontally",
     "Person holding tuck planche from different angle, floating with tucked knees, arms locked straight"),
    ("Straddle Planche", "straddle-planche",
     "Person holding straddle planche, arms straight, body horizontal, legs wide apart in straddle",
     "Person holding straddle planche from different angle, floating horizontal with straddled legs"),
    ("Full Planche", "full-planche",
     "Person holding full planche, arms straight on floor, body completely horizontal, legs together and extended",
     "Person holding full planche from different angle, body parallel to ground, arms locked"),

    # PULL
    ("Dead Hang", "dead-hang",
     "Person hanging from a pull-up bar with arms fully extended, shoulders relaxed, body straight",
     "Person hanging from pull-up bar with active shoulders, shoulder blades pulled down, arms straight"),
    ("Scapular Pulls", "scapular-pulls",
     "Person hanging from bar with arms straight, shoulders in relaxed position near ears",
     "Person hanging from bar, shoulders actively pulled down and back, arms still straight, chest slightly lifted"),
    ("Australian Row", "australian-row",
     "Person hanging under a low bar, body straight and angled, arms fully extended, heels on ground",
     "Person pulled up to low bar, chest touching bar, body straight, heels on ground"),
    ("Negative Pull-Up", "negative-pull-up",
     "Person at top of pull-up with chin above bar, arms bent, gripping bar",
     "Person midway through lowering from pull-up, arms partially extended, controlled descent"),
    ("Chin-Up", "chin-up",
     "Person hanging from bar with underhand/supinated grip, arms fully extended",
     "Person at top of chin-up, chin above bar, underhand grip, arms fully bent"),
    ("Pull-Up", "pull-up",
     "Person hanging from bar with overhand grip, arms fully extended, body straight",
     "Person at top of pull-up, chin above bar, overhand grip, arms fully bent"),
    ("Wide Pull-Up", "wide-pull-up",
     "Person hanging from bar with wide overhand grip, arms extended, hands much wider than shoulders",
     "Person at top of wide pull-up, chest near bar, wide grip, elbows flared"),
    ("Close-Grip Pull-Up", "close-grip-pull-up",
     "Person hanging from bar with hands very close together, arms extended",
     "Person at top of close-grip pull-up, chin above bar, hands touching"),
    ("L-Sit Pull-Up", "l-sit-pull-up",
     "Person hanging from bar with legs extended horizontally in L-sit position, arms straight",
     "Person at top of pull-up while holding L-sit, chin above bar, legs horizontal"),
    ("Archer Pull-Up", "archer-pull-up",
     "Person hanging from bar with wide grip, arms extended",
     "Person pulled up to one side of bar, one arm bent at top, other arm extended along bar"),
    ("Typewriter Pull-Up", "typewriter-pull-up",
     "Person at top of pull-up, chin above bar, about to traverse sideways",
     "Person traversing along bar at top of pull-up, moving sideways with chin above bar"),
    ("Muscle-Up", "muscle-up",
     "Person hanging from bar, about to perform explosive pull for muscle-up",
     "Person on top of bar in dip position after completing muscle-up, arms straight, above bar"),
    ("One-Arm Chin-Up", "one-arm-chin-up",
     "Person hanging from bar with one arm, underhand grip, other arm at side",
     "Person at top of one-arm chin-up, chin above bar, single arm bent"),

    # LEGS
    ("Bodyweight Squat", "bodyweight-squat",
     "Person standing upright, feet shoulder width apart, arms in front for balance",
     "Person in deep squat position, thighs below parallel, arms extended forward for balance"),
    ("Split Squat", "split-squat",
     "Person standing in staggered stance, one foot forward one back, upright posture",
     "Person in bottom of split squat/lunge, front knee at 90 degrees, back knee near floor"),
    ("Bulgarian Split Squat", "bulgarian-split-squat",
     "Person standing with rear foot elevated on a bench behind them, front foot forward",
     "Person in bottom of Bulgarian split squat, rear foot on bench, front thigh parallel to floor"),
    ("Step-Up", "step-up",
     "Person standing in front of a box/bench, one foot on top of box",
     "Person standing on top of box on one leg, fully extended, other leg hanging"),
    ("Jump Squat", "jump-squat",
     "Person in deep squat position, about to explode upward",
     "Person in mid-air after jumping from squat, arms up, feet off ground"),
    ("Cossack Squat", "cossack-squat",
     "Person standing with wide stance, feet wider than shoulders",
     "Person in deep cossack squat, weight on one leg bent deep, other leg straight to the side"),
    ("Pistol Squat (Assisted)", "pistol-squat-assisted",
     "Person standing on one leg, holding a pole/support with one hand, other leg slightly forward",
     "Person in deep single-leg squat holding support, one leg extended forward, sitting deep"),
    ("Pistol Squat", "pistol-squat",
     "Person standing on one leg, arms forward, other leg slightly lifted",
     "Person in full pistol squat, sitting deep on one leg, other leg extended straight forward"),
    ("Shrimp Squat", "shrimp-squat",
     "Person standing on one leg, holding opposite foot behind with hand",
     "Person in bottom of shrimp squat, one leg bent deep, other foot held behind touching glute, knee near floor"),
    ("Nordic Curl (Assisted)", "nordic-curl-assisted",
     "Person kneeling upright, feet anchored, hands ready to catch at bottom",
     "Person leaning forward from knees in nordic curl, body at an angle, hands pushing off floor"),
    ("Nordic Curl", "nordic-curl",
     "Person kneeling upright, feet anchored under something, body vertical",
     "Person fully extended forward in nordic curl, body nearly horizontal from knees, controlled"),
    ("Glute Bridge", "glute-bridge",
     "Person lying on back, knees bent, feet flat on floor, hips on ground",
     "Person in glute bridge, hips lifted high, shoulders on ground, straight line from knees to shoulders"),
    ("Single-Leg Glute Bridge", "single-leg-glute-bridge",
     "Person lying on back, one knee bent foot on floor, other leg extended straight up",
     "Person in single-leg glute bridge, hips high, one leg extended, driving through one foot"),
    ("Calf Raise", "calf-raise",
     "Person standing flat on feet, feet hip width apart",
     "Person risen up on toes in calf raise, heels high off ground"),
    ("Single-Leg Calf Raise", "single-leg-calf-raise",
     "Person standing on one foot, other foot lifted off ground",
     "Person risen up on toes on one foot, heel high, other foot lifted"),

    # CORE
    ("Dead Bug", "dead-bug",
     "Person lying on back, arms extended toward ceiling, knees bent at 90 degrees above hips",
     "Person lying on back with opposite arm and leg extended, other arm and knee still up"),
    ("Plank", "plank",
     "Person in forearm plank position, body straight from head to heels, on forearms and toes",
     "Person in forearm plank from slightly different angle, body rigid and straight, core engaged"),
    ("Side Plank", "side-plank",
     "Person in side plank on one forearm, body straight, hips lifted, feet stacked",
     "Person in side plank from front view, body in straight line, balancing on one forearm"),
    ("Hollow Body Hold", "hollow-body-hold",
     "Person lying on back, arms and legs extended, everything on the ground",
     "Person in hollow body hold, lower back pressed to floor, arms and legs lifted off ground in banana shape"),
    ("Hanging Knee Raise", "hanging-knee-raise",
     "Person hanging from pull-up bar, arms extended, body straight",
     "Person hanging from bar with knees raised to chest, arms straight, knees tucked up"),
    ("Hanging Leg Raise", "hanging-leg-raise",
     "Person hanging from pull-up bar, arms extended, legs straight down",
     "Person hanging from bar with straight legs raised to horizontal, L-shape position"),
    ("Toes to Bar", "toes-to-bar",
     "Person hanging from bar, arms extended, body straight",
     "Person hanging from bar with feet touching the bar, legs straight, body in V-shape"),
    ("Dragon Flag (Tuck)", "dragon-flag-tuck",
     "Person lying on bench gripping behind head, body flat on bench",
     "Person in tuck dragon flag, shoulders on bench, body lifted with knees tucked, gripping bench behind head"),
    ("Dragon Flag", "dragon-flag",
     "Person lying on bench gripping behind head, body flat",
     "Person in full dragon flag, shoulders on bench, body straight and lifted at an angle, gripping behind head"),
    ("Ab Wheel Rollout", "ab-wheel-rollout",
     "Person kneeling behind ab wheel, hands on wheel handles, body upright",
     "Person fully extended in ab wheel rollout, body stretched out nearly flat, hands on wheel far in front"),
    ("Front Lever Tuck", "front-lever-tuck",
     "Person hanging from bar, arms straight, about to lift into tuck lever",
     "Person in tuck front lever, hanging from bar with arms straight, body horizontal, knees tucked to chest"),
    ("Front Lever", "front-lever",
     "Person hanging from bar, arms straight, body vertical",
     "Person in full front lever, hanging from bar with arms straight, body completely horizontal, legs extended"),
    ("Back Lever", "back-lever",
     "Person hanging from bar, arms straight",
     "Person in back lever position, hanging from bar with arms straight, body horizontal facing downward behind the bar"),

    # SKILL
    ("Crow Pose", "crow-pose",
     "Person crouching with hands on floor, knees resting on backs of upper arms, feet still on ground",
     "Person balanced in crow pose, hands on floor, knees on triceps, feet lifted off ground, leaning forward"),
    ("Frog Stand", "frog-stand",
     "Person in deep squat with hands on floor in front, preparing to lean forward",
     "Person balanced in frog stand, hands on floor, knees on elbows, body tilted forward, feet off ground"),
    ("Wall Handstand", "wall-handstand",
     "Person standing facing away from wall, hands on ground, about to kick up",
     "Person in handstand against wall, arms straight, body vertical, feet touching wall"),
    ("Freestanding Handstand", "freestanding-handstand",
     "Person in freestanding handstand, arms straight, body perfectly vertical, no wall",
     "Person in freestanding handstand from different angle, balanced on hands, body straight"),
    ("Elbow Lever", "elbow-lever",
     "Person crouching with hands on floor, elbows bent, preparing to lean forward",
     "Person in elbow lever, balanced horizontally on bent arms, elbow in hip crease, body and legs extended horizontally"),
    ("Human Flag (Tuck)", "human-flag-tuck",
     "Person gripping a vertical pole with both hands, standing to the side",
     "Person in tuck human flag on pole, body sideways, knees tucked, holding horizontal position on vertical pole"),
    ("Human Flag", "human-flag",
     "Person gripping vertical pole, preparing for flag",
     "Person in full human flag, body horizontal and straight, gripping vertical pole, arms pushing and pulling"),

    # MOBILITY
    ("Shoulder Dislocates", "shoulder-dislocates",
     "Person standing holding a stick/band with wide grip in front of body at hip level",
     "Person with stick/band passed overhead and behind back, arms wide, completing the shoulder dislocate circle"),
    ("Cat-Cow Stretch", "cat-cow-stretch",
     "Person on hands and knees with back arched downward (cow position), head looking up",
     "Person on hands and knees with back rounded upward (cat position), head tucked down"),
    ("Deep Squat Hold", "deep-squat-hold",
     "Person standing with feet shoulder width apart",
     "Person sitting in deep squat, heels flat, chest up, elbows pushing knees outward"),
    ("Wrist Circles", "wrist-circles",
     "Person standing with arms extended, hands in fists, wrists in neutral position",
     "Person standing with arms extended, wrists rotated in circular motion, hands open"),
    ("Hip Circles", "hip-circles",
     "Person standing with hands on hips, feet shoulder width apart",
     "Person standing with hands on hips, hips pushed to one side in a large circle"),
    ("Arm Circles", "arm-circles",
     "Person standing with arms extended out to sides at shoulder height",
     "Person standing with arms making large circles, arms at various positions in the rotation"),
    ("World's Greatest Stretch", "worlds-greatest-stretch",
     "Person in a deep lunge position, hands on the ground on either side of front foot",
     "Person in deep lunge with one arm rotated up toward ceiling, torso twisted open"),
    ("Pancake Stretch", "pancake-stretch",
     "Person seated on floor with legs spread wide in straddle, sitting upright",
     "Person in pancake stretch, legs wide, torso folded forward toward floor, chest down"),
    ("Pike Stretch", "pike-stretch",
     "Person seated on floor with legs together extended forward, sitting upright",
     "Person in pike stretch, legs together, torso folded forward, hands reaching past toes"),
    ("Bridge", "bridge",
     "Person lying on back, knees bent, feet and hands flat on floor by ears",
     "Person in full gymnastic bridge, hips pushed high, arms straight, arched backward"),
    ("German Hang", "german-hang",
     "Person hanging from bar with arms extended, facing the bar",
     "Person in german hang, rotated behind and below bar, shoulders fully extended, hanging with arms behind"),
    ("Skin the Cat", "skin-the-cat",
     "Person hanging from bar, legs lifted and beginning to rotate backward",
     "Person rotated fully through on bar, in german hang position, completing the skin the cat movement"),
]


def generate_images():
    client = OpenAI()

    total = len(EXERCISES)
    for i, (name, slug, start_desc, end_desc) in enumerate(EXERCISES):
        start_path = OUTPUT_DIR / f"{slug}-start.png"
        end_path = OUTPUT_DIR / f"{slug}-end.png"

        # Skip if both already exist
        if start_path.exists() and end_path.exists():
            print(f"[{i+1}/{total}] {name} -- already exists, skipping")
            continue

        for position, desc, path in [("start", start_desc, start_path), ("end", end_desc, end_path)]:
            if path.exists():
                print(f"  {position} already exists, skipping")
                continue

            prompt = STYLE_PREFIX + desc + "."
            print(f"[{i+1}/{total}] {name} ({position})...", end=" ", flush=True)

            try:
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                image_url = response.data[0].url
                img_data = requests.get(image_url).content
                with open(path, "wb") as f:
                    f.write(img_data)
                print("OK")
            except Exception as e:
                print(f"FAILED: {e}")

            # Rate limit: DALL-E 3 allows ~5 requests/min on free tier
            time.sleep(13)

    print("\nDone! Images saved to:", OUTPUT_DIR)


def generate_manifest():
    """Generate a JSON manifest of all exercises and their image paths."""
    manifest = {}
    for name, slug, _, _ in EXERCISES:
        manifest[name] = {
            "slug": slug,
            "start": f"/static/images/exercises/{slug}-start.png",
            "end": f"/static/images/exercises/{slug}-end.png",
        }
    manifest_path = OUTPUT_DIR / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"Manifest written to {manifest_path}")


if __name__ == "__main__":
    generate_manifest()
    print(f"\n{len(EXERCISES)} exercises, {len(EXERCISES) * 2} images to generate.\n")
    generate_images()
