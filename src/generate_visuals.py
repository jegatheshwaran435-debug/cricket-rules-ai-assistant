import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DATA_IMAGES_DIR = Path(__file__).resolve().parent.parent / "data" / "images"
DATA_IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def get_default_font(size: int = 24):
    """Attempt to load a standard truetype font or fallback to default."""
    try:
        # Standard Windows fonts
        for font_name in ["segoeui.ttf", "arial.ttf", "calibri.ttf", "tahoma.ttf"]:
            try:
                return ImageFont.truetype(font_name, size)
            except IOError:
                continue
        return ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()


def create_base_canvas(width=1280, height=720, bg_color="#0d1b1e", title="", subtitle="", law_tag=""):
    """Creates a sleek 16:9 infographic canvas with headers, borders, and footer."""
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Top Header Banner
    draw.rectangle([(0, 0), (width, 85)], fill="#071214")
    draw.line([(0, 85), (width, 85)], fill="#22c55e", width=3)

    # Fonts
    font_title = get_default_font(32)
    font_sub = get_default_font(18)
    font_tag = get_default_font(16)

    # Law Tag Badge
    if law_tag:
        draw.rounded_rectangle([(30, 24), (200, 60)], radius=8, fill="#166534", outline="#22c55e", width=2)
        draw.text((45, 32), law_tag, fill="#f0fdf4", font=font_tag)

    # Title & Subtitle
    title_x = 220 if law_tag else 40
    draw.text((title_x, 18), title, fill="#ffffff", font=font_title)
    draw.text((title_x, 54), subtitle, fill="#94a3b8", font=font_sub)

    # Outer Frame Border
    draw.rectangle([(0, 0), (width - 1, height - 1)], outline="#334155", width=2)

    # Bottom Footer Banner
    draw.rectangle([(0, height - 45), (width, height)], fill="#071214")
    draw.line([(0, height - 45), (width, height - 45)], fill="#1e293b", width=1)
    font_footer = get_default_font(15)
    draw.text((30, height - 32), "🏏 Cricket Rules AI Assistant • Official MCC Laws & ICC Standard Playing Conditions Visual Explainer", fill="#64748b", font=font_footer)

    return img, draw


# ==============================================================================
# VISUAL SCENARIO GENERATORS
# ==============================================================================

def generate_lbw_hawkeye():
    """1. LBW Hawkeye Projection with Impact & Pitching Zones."""
    img, draw = create_base_canvas(
        title="Hawkeye LBW Ball Tracking & Impact Zone Explainer",
        subtitle="Pitching In-Line • Impact In-Line • Hitting Stumps Criteria",
        law_tag="MCC LAW 36"
    )
    font_lg = get_default_font(22)
    font_md = get_default_font(17)
    font_sm = get_default_font(14)

    # Ground Pitch Zone (Perspective Green / Clay pitch)
    draw.rectangle([(160, 140), (1120, 580)], fill="#152b1b", outline="#22c55e", width=2)
    draw.line([(320, 140), (320, 580)], fill="#335c3d", width=2)  # Off side line
    draw.line([(960, 140), (960, 580)], fill="#335c3d", width=2)  # Leg side line

    # Wickets Area (Right Side)
    draw.rectangle([(980, 260), (1040, 460)], fill="#1e293b", outline="#cbd5e1", width=2)
    # 3 Stumps
    for y in [310, 360, 410]:
        draw.line([(1000, y), (1030, y)], fill="#f59e0b", width=8)
    draw.text((1010, 230), "STUMPS", fill="#f59e0b", font=font_md)

    # 3 Key Checkpoints Boxes
    # 1. Pitching Zone
    draw.rounded_rectangle([(220, 290), (360, 430)], radius=12, fill="#065f46", outline="#34d399", width=3)
    draw.ellipse([(270, 340), (310, 380)], fill="#fbbf24", outline="#ffffff", width=2)
    draw.text((235, 305), "1. PITCHING", fill="#a7f3d0", font=font_lg)
    draw.text((240, 395), "In-Line / Off Side", fill="#ffffff", font=font_sm)
    draw.text((245, 410), "(NOT Outside Leg)", fill="#f87171", font=font_sm)

    # Ball Trajectory Line
    draw.line([(310, 360), (600, 360)], fill="#38bdf8", width=6)

    # 2. Impact Zone
    draw.rounded_rectangle([(560, 280), (740, 440)], radius=12, fill="#1e3a8a", outline="#60a5fa", width=3)
    draw.ellipse([(630, 340), (670, 380)], fill="#38bdf8", outline="#ffffff", width=2)
    draw.text((575, 295), "2. PAD IMPACT", fill="#bfdbfe", font=font_lg)
    draw.text((585, 395), "Struck In-Line", fill="#ffffff", font=font_sm)
    draw.text((575, 415), "Or No Shot Offered", fill="#cbd5e1", font=font_sm)

    # Hawkeye Virtual Projection Path (Dotted / Glowing Gold)
    for x in range(670, 1000, 25):
        draw.line([(x, 360), (x + 15, 360)], fill="#f59e0b", width=5)

    # 3. Wicket Zone (HITTING)
    draw.rounded_rectangle([(820, 200), (950, 280)], radius=8, fill="#991b1b", outline="#ef4444", width=2)
    draw.text((835, 215), "3. WICKETS", fill="#fecaca", font=font_lg)
    draw.text((840, 245), "HITTING (>50%)", fill="#ffffff", font=font_md)

    # Decision Banner
    draw.rounded_rectangle([(400, 500), (880, 560)], radius=10, fill="#14532d", outline="#4ade80", width=2)
    draw.text((430, 515), "DECISION: OUT (LBW) - ALL 5 LAWS SATISFIED", fill="#4ade80", font=font_lg)

    img.save(DATA_IMAGES_DIR / "lbw_hawkeye_projection.png")
    print("✓ Generated lbw_hawkeye_projection.png")


def generate_dead_ball_helmet():
    """2. Dead Ball: Ball Striking Resting Helmet on Ground."""
    img, draw = create_base_canvas(
        title="Ball Striking Fielder's Helmet Resting on Ground",
        subtitle="Immediate Dead Ball • 5 Penalty Runs Awarded to Batting Side",
        law_tag="MCC LAW 28.3"
    )
    font_lg = get_default_font(24)
    font_md = get_default_font(18)
    font_sm = get_default_font(14)

    # Pitch Grass
    draw.rectangle([(100, 140), (1180, 580)], fill="#0f291e", outline="#1e4e38", width=2)

    # Wicket Keeper Stumps & Crease
    draw.line([(350, 180), (350, 540)], fill="#ffffff", width=4)
    draw.text((360, 200), "POPPING CREASE", fill="#94a3b8", font=font_sm)

    # Stumps
    draw.rectangle([(280, 320), (310, 420)], fill="#f59e0b", outline="#ffffff", width=2)
    draw.text((270, 290), "STUMPS", fill="#f59e0b", font=font_md)

    # Resting Helmet behind Keeper
    draw.arc([(560, 320), (700, 440)], start=180, end=360, fill="#0284c7", width=12)
    draw.rectangle([(570, 380), (690, 410)], fill="#0369a1")
    draw.text((580, 420), "RESTING HELMET", fill="#38bdf8", font=font_md)

    # Ball trajectory hitting helmet
    draw.line([(320, 360), (600, 360)], fill="#ef4444", width=5)
    draw.ellipse([(590, 345), (620, 375)], fill="#ef4444", outline="#ffffff", width=2)
    draw.text((630, 330), "IMPACT!", fill="#f87171", font=font_lg)

    # Big Rules Alert Cards
    draw.rounded_rectangle([(150, 460), (600, 540)], radius=12, fill="#7f1d1d", outline="#ef4444", width=3)
    draw.text((170, 475), "⛔ BALL BECOMES DEAD IMMEDIATELY", fill="#ffffff", font=font_lg)
    draw.text((170, 510), "No batter can be dismissed after the strike", fill="#fca5a5", font=font_sm)

    draw.rounded_rectangle([(650, 460), (1130, 540)], radius=12, fill="#14532d", outline="#22c55e", width=3)
    draw.text((670, 475), "➕ 5 PENALTY RUNS TO BATTING SIDE", fill="#ffffff", font=font_lg)
    draw.text((670, 510), "Awarded to extras; completed runs also count", fill="#86efac", font=font_sm)

    img.save(DATA_IMAGES_DIR / "dead_ball_helmet_ground.png")
    print("✓ Generated dead_ball_helmet_ground.png")


def generate_no_ball_foot_fault():
    """3. No Ball: Front Foot & Back Foot Crease Faults."""
    img, draw = create_base_canvas(
        title="Fair Delivery Crease Regulations (Foot Fault No-Ball)",
        subtitle="Front Foot Popping Crease Limit & Back Foot Return Crease Limit",
        law_tag="MCC LAW 21.5"
    )
    font_lg = get_default_font(22)
    font_md = get_default_font(17)
    font_sm = get_default_font(14)

    # Turf
    draw.rectangle([(120, 140), (1160, 580)], fill="#132a1c")

    # Crease Lines
    # Popping Crease (Horizontal)
    draw.line([(300, 360), (1050, 360)], fill="#ffffff", width=6)
    draw.text((880, 330), "POPPING CREASE", fill="#ffffff", font=font_md)

    # Return Crease (Vertical Right)
    draw.line([(1050, 180), (1050, 540)], fill="#ffffff", width=4)
    draw.text((1060, 240), "RETURN CREASE", fill="#ffffff", font=font_sm)

    # Bowling Crease
    draw.line([(300, 480), (1050, 480)], fill="#94a3b8", width=3)
    draw.text((880, 490), "BOWLING CREASE", fill="#94a3b8", font=font_sm)

    # Front Foot Overstepping Graphic (Left)
    draw.rounded_rectangle([(320, 200), (620, 350)], radius=12, fill="#7f1d1d", outline="#ef4444", width=3)
    # Shoe illustration beyond line
    draw.rounded_rectangle([(420, 340), (520, 400)], radius=15, fill="#e2e8f0", outline="#ef4444", width=3)
    draw.text((340, 215), "❌ NO-BALL: OVERSTEPPING", fill="#fecaca", font=font_lg)
    draw.text((340, 255), "No part of front foot grounded", fill="#ffffff", font=font_sm)
    draw.text((340, 275), "or airborne behind popping crease line", fill="#ffffff", font=font_sm)
    draw.text((340, 305), "Penalty: 1 Run + Free Hit (White Ball)", fill="#fca5a5", font=font_sm)

    # Legal Front Foot Graphic (Center)
    draw.rounded_rectangle([(660, 200), (960, 350)], radius=12, fill="#14532d", outline="#22c55e", width=3)
    # Shoe illustration crossing line but heel grounded behind
    draw.rounded_rectangle([(760, 330), (860, 390)], radius=15, fill="#e2e8f0", outline="#22c55e", width=3)
    draw.text((680, 215), "✓ FAIR DELIVERY (LEGAL)", fill="#bbf7d0", font=font_lg)
    draw.text((680, 255), "Some part of the front foot", fill="#ffffff", font=font_sm)
    draw.text((680, 275), "is grounded or raised behind the line", fill="#ffffff", font=font_sm)
    draw.text((680, 305), "Heel safely behind popping crease", fill="#86efac", font=font_sm)

    img.save(DATA_IMAGES_DIR / "no_ball_foot_fault.png")
    print("✓ Generated no_ball_foot_fault.png")


def generate_no_ball_waist_high():
    """4. No Ball: Waist High Full Toss (Beamer)."""
    img, draw = create_base_canvas(
        title="Waist-High Full Toss (Dangerous Beamer Delivery)",
        subtitle="Any delivery passing striker above waist height on the full is a No Ball",
        law_tag="MCC LAW 21.9"
    )
    font_lg = get_default_font(24)
    font_md = get_default_font(18)
    font_sm = get_default_font(15)

    # Pitch & Crease
    draw.rectangle([(120, 140), (1160, 580)], fill="#0f261b")
    draw.line([(850, 160), (850, 560)], fill="#ffffff", width=4)
    draw.text((860, 180), "POPPING CREASE", fill="#94a3b8", font=font_sm)

    # Batter Standing Silhouette
    draw.rectangle([(810, 260), (850, 480)], fill="#475569")  # Body
    draw.ellipse([(815, 210), (845, 250)], fill="#64748b")   # Head
    draw.line([(830, 340), (830, 490)], fill="#f8fafc", width=4) # Bat

    # Waist Line
    draw.line([(400, 360), (950, 360)], fill="#f59e0b", width=3)
    draw.text((420, 335), "WAIST HEIGHT LEVEL (UPRIGHT STANCE)", fill="#fbbf24", font=font_md)

    # Ball Trajectory above waist
    draw.line([(200, 280), (800, 310)], fill="#ef4444", width=6)
    draw.ellipse([(785, 295), (815, 325)], fill="#ef4444", outline="#ffffff", width=3)

    # Warning Box
    draw.rounded_rectangle([(180, 420), (750, 540)], radius=12, fill="#7f1d1d", outline="#ef4444", width=3)
    draw.text((200, 435), "🚨 NO-BALL: WAIST-HIGH FULL TOSS", fill="#fecaca", font=font_lg)
    draw.text((200, 475), "• Judged standing upright at the popping crease", fill="#ffffff", font=font_sm)
    draw.text((200, 500), "• Regardless of bowling pace (fast or spin)", fill="#ffffff", font=font_sm)

    img.save(DATA_IMAGES_DIR / "no_ball_waist_high_full_toss.png")
    print("✓ Generated no_ball_waist_high_full_toss.png")


def generate_powerplay_fielding():
    """5. Powerplay & Fielding Restrictions (30-Yard Circle)."""
    img, draw = create_base_canvas(
        title="ODI & T20I Powerplay & 30-Yard Circle Restrictions",
        subtitle="Mandatory Powerplay Limits & Boundary Protection Guidelines",
        law_tag="ICC PLAYING CONDITIONS"
    )
    font_lg = get_default_font(22)
    font_md = get_default_font(17)
    font_sm = get_default_font(14)

    # Stadium Oval Field
    draw.ellipse([(140, 120), (780, 600)], fill="#14532d", outline="#22c55e", width=4)
    # 30-Yard Inner Circle
    draw.ellipse([(280, 220), (640, 500)], fill="#15803d", outline="#ffffff", width=3)
    # Pitch
    draw.rectangle([(430, 310), (490, 410)], fill="#d97706")
    draw.text((370, 240), "30-YARD CIRCLE", fill="#ffffff", font=font_sm)

    # Fielders Dots Inside / Outside
    draw.ellipse([(340, 300), (360, 320)], fill="#38bdf8") # In-ring fielder
    draw.ellipse([(580, 340), (600, 360)], fill="#38bdf8")
    draw.ellipse([(460, 270), (480, 290)], fill="#38bdf8")
    draw.ellipse([(460, 430), (480, 450)], fill="#38bdf8")

    # Only 2 Outside in Powerplay
    draw.ellipse([(200, 240), (220, 260)], fill="#ef4444")
    draw.ellipse([(720, 480), (740, 500)], fill="#ef4444")
    draw.text((700, 510), "Max 2 Outside", fill="#f87171", font=font_sm)

    # Info Cards on Right
    draw.rounded_rectangle([(820, 140), (1220, 270)], radius=10, fill="#1e293b", outline="#38bdf8", width=2)
    draw.text((840, 155), "POWERPLAY 1 (Overs 1-10)", fill="#38bdf8", font=font_lg)
    draw.text((840, 195), "• Max 2 fielders outside 30-yard ring", fill="#ffffff", font=font_sm)
    draw.text((840, 225), "• T20I: Overs 1-6 (Max 2 outside)", fill="#94a3b8", font=font_sm)

    draw.rounded_rectangle([(820, 290), (1220, 420)], radius=10, fill="#1e293b", outline="#f59e0b", width=2)
    draw.text((840, 305), "POWERPLAY 2 (Overs 11-40)", fill="#f59e0b", font=font_lg)
    draw.text((840, 345), "• Max 4 fielders outside 30-yard ring", fill="#ffffff", font=font_sm)
    draw.text((840, 375), "• Building the middle overs", fill="#94a3b8", font=font_sm)

    draw.rounded_rectangle([(820, 440), (1220, 570)], radius=10, fill="#1e293b", outline="#22c55e", width=2)
    draw.text((840, 455), "POWERPLAY 3 (Overs 41-50)", fill="#22c55e", font=font_lg)
    draw.text((840, 495), "• Max 5 fielders outside 30-yard ring", fill="#ffffff", font=font_sm)
    draw.text((840, 525), "• Death overs fielding layout", fill="#94a3b8", font=font_sm)

    img.save(DATA_IMAGES_DIR / "powerplay_fielding_restrictions.png")
    print("✓ Generated powerplay_fielding_restrictions.png")


def generate_mankad_run_out():
    """6. Mankad: Non-Striker Leaving Ground Early."""
    img, draw = create_base_canvas(
        title="Running Out the Non-Striker Leaving Ground Early ('Mankad')",
        subtitle="Legitimate Mode of Dismissal Categorized Officially Under Run Out",
        law_tag="MCC LAW 38.3"
    )
    font_lg = get_default_font(24)
    font_md = get_default_font(18)
    font_sm = get_default_font(15)

    # Turf
    draw.rectangle([(100, 140), (1180, 580)], fill="#0f291e")

    # Non-Striker Popping Crease
    draw.line([(450, 160), (450, 560)], fill="#ffffff", width=5)
    draw.text((460, 180), "NON-STRIKER POPPING CREASE", fill="#94a3b8", font=font_sm)

    # Stumps at non-striker's end
    draw.rectangle([(380, 300), (410, 420)], fill="#f59e0b", outline="#ffffff", width=2)
    draw.text((360, 270), "STUMPS BROKEN", fill="#f59e0b", font=font_md)

    # Non-Striker Batter (Out of crease)
    draw.rounded_rectangle([(520, 310), (620, 430)], radius=10, fill="#334155")
    draw.text((530, 350), "BATTER", fill="#ffffff", font=font_md)
    draw.text((500, 440), "OUT OF GROUND BEFORE RELEASE", fill="#ef4444", font=font_sm)

    # Bowler stopping delivery action
    draw.rounded_rectangle([(240, 310), (340, 430)], radius=10, fill="#166534")
    draw.text((255, 350), "BOWLER", fill="#ffffff", font=font_md)

    # Big Explanation Banner
    draw.rounded_rectangle([(150, 480), (1130, 560)], radius=10, fill="#1e293b", outline="#22c55e", width=2)
    draw.text((180, 495), "✓ OFFICIAL MCC RULE: 100% FAIR DISMISSAL (RUN OUT)", fill="#4ade80", font=font_lg)
    draw.text((180, 530), "Permitted until the moment the bowler would normally be expected to release the ball.", fill="#cbd5e1", font=font_sm)

    img.save(DATA_IMAGES_DIR / "mankad_non_striker_run_out.png")
    print("✓ Generated mankad_non_striker_run_out.png")


def generate_drs_umpires_call():
    """7. DRS & Umpire's Call Zones."""
    img, draw = create_base_canvas(
        title="DRS Ball Tracking & Umpire's Call Zones Explainer",
        subtitle="Pitching • Impact • Stumps Hitting Margin of Error Standards",
        law_tag="ICC DRS PROTOCOL"
    )
    font_lg = get_default_font(22)
    font_md = get_default_font(17)
    font_sm = get_default_font(14)

    # 3 Zone Comparison Cards
    # Card 1: Pitching
    draw.rounded_rectangle([(80, 160), (420, 480)], radius=12, fill="#1e293b", outline="#38bdf8", width=2)
    draw.text((100, 180), "1. PITCHING ZONE", fill="#38bdf8", font=font_lg)
    draw.line([(100, 220), (400, 220)], fill="#334155", width=1)
    draw.text((100, 240), "• Center of ball must pitch", fill="#ffffff", font=font_sm)
    draw.text((100, 265), "  between wicket-to-wicket line", fill="#ffffff", font=font_sm)
    draw.text((100, 300), "• Pitching Outside Leg = NOT OUT", fill="#f87171", font=font_md)
    draw.text((100, 330), "  (Never overturned)", fill="#94a3b8", font=font_sm)
    draw.text((100, 380), "Overturn Threshold:", fill="#94a3b8", font=font_sm)
    draw.text((100, 405), "> 50% of ball in-line", fill="#34d399", font=font_md)

    # Card 2: Impact
    draw.rounded_rectangle([(470, 160), (810, 480)], radius=12, fill="#1e293b", outline="#f59e0b", width=2)
    draw.text((490, 180), "2. IMPACT ZONE", fill="#f59e0b", font=font_lg)
    draw.line([(490, 220), (790, 220)], fill="#334155", width=1)
    draw.text((490, 240), "• First point of contact with pad", fill="#ffffff", font=font_sm)
    draw.text((490, 275), "• Center within stump line: IN-LINE", fill="#34d399", font=font_sm)
    draw.text((490, 310), "• Center on edge of stump:", fill="#fbbf24", font=font_sm)
    draw.text((510, 335), "UMPIRE'S CALL", fill="#fbbf24", font=font_md)
    draw.text((490, 380), "No shot offered:", fill="#94a3b8", font=font_sm)
    draw.text((490, 405), "Can be outside off stump", fill="#ffffff", font=font_sm)

    # Card 3: Wicket Hitting
    draw.rounded_rectangle([(860, 160), (1200, 480)], radius=12, fill="#1e293b", outline="#ef4444", width=2)
    draw.text((880, 180), "3. WICKETS (HITTING)", fill="#ef4444", font=font_lg)
    draw.line([(880, 220), (1180, 220)], fill="#334155", width=1)
    draw.text((880, 240), "• Trajectory projected to stumps", fill="#ffffff", font=font_sm)
    draw.text((880, 275), "> 50% ball hitting zone = HITTING", fill="#34d399", font=font_sm)
    draw.text((880, 310), "< 50% edge clipping:", fill="#fbbf24", font=font_sm)
    draw.text((900, 335), "UMPIRE'S CALL", fill="#fbbf24", font=font_md)
    draw.text((880, 380), "Review Retention:", fill="#94a3b8", font=font_sm)
    draw.text((880, 405), "Team KEEPS review on Umpire's Call", fill="#60a5fa", font=font_sm)

    # Bottom Banner
    draw.rounded_rectangle([(180, 510), (1100, 560)], radius=8, fill="#0f172a", outline="#64748b", width=1)
    draw.text((210, 525), "💡 ON-FIELD DECISION STANDS ON UMPIRE'S CALL • REVIEW IS NOT LOST", fill="#f8fafc", font=font_md)

    img.save(DATA_IMAGES_DIR / "drs_umpires_call_zones.png")
    print("✓ Generated drs_umpires_call_zones.png")


def generate_super_over_procedure():
    """8. Super Over Procedure Flowchart."""
    img, draw = create_base_canvas(
        title="ICC Super Over Tie-Breaker Procedure",
        subtitle="Standard Knockout & Tournament Playoff Resolution",
        law_tag="ICC APPENDIX"
    )
    font_lg = get_default_font(22)
    font_md = get_default_font(17)
    font_sm = get_default_font(14)

    # Step 1
    draw.rounded_rectangle([(80, 220), (320, 420)], radius=12, fill="#1e293b", outline="#38bdf8", width=2)
    draw.text((100, 240), "STEP 1: SETUP", fill="#38bdf8", font=font_lg)
    draw.text((100, 280), "• Match ends in a TIE", fill="#ffffff", font=font_sm)
    draw.text((100, 310), "• Team batting 2nd in", fill="#ffffff", font=font_sm)
    draw.text((100, 335), "  main match bats 1st", fill="#ffffff", font=font_sm)

    # Arrow 1
    draw.line([(320, 320), (370, 320)], fill="#ffffff", width=4)

    # Step 2
    draw.rounded_rectangle([(370, 220), (610, 420)], radius=12, fill="#1e293b", outline="#f59e0b", width=2)
    draw.text((390, 240), "STEP 2: INNINGS", fill="#f59e0b", font=font_lg)
    draw.text((390, 280), "• 1 Over (6 balls)", fill="#ffffff", font=font_sm)
    draw.text((390, 310), "• Max 2 Wickets allowed", fill="#ffffff", font=font_sm)
    draw.text((390, 340), "• Loss of 2nd wicket", fill="#fca5a5", font=font_sm)
    draw.text((390, 365), "  ends innings immediately", fill="#fca5a5", font=font_sm)

    # Arrow 2
    draw.line([(610, 320), (660, 320)], fill="#ffffff", width=4)

    # Step 3
    draw.rounded_rectangle([(660, 220), (900, 420)], radius=12, fill="#1e293b", outline="#22c55e", width=2)
    draw.text((680, 240), "STEP 3: RESULT", fill="#22c55e", font=font_lg)
    draw.text((680, 280), "• Higher runs scored wins", fill="#ffffff", font=font_sm)
    draw.text((680, 315), "• If runs are TIED:", fill="#fde047", font=font_sm)
    draw.text((680, 345), "  Play SUBSEQUENT", fill="#fde047", font=font_md)
    draw.text((680, 375), "  Super Overs until won", fill="#fde047", font=font_sm)

    # Arrow 3
    draw.line([(900, 320), (950, 320)], fill="#ffffff", width=4)

    # Step 4: Rule Change Note
    draw.rounded_rectangle([(950, 220), (1200, 420)], radius=12, fill="#7f1d1d", outline="#ef4444", width=2)
    draw.text((970, 240), "ABOLISHED RULE", fill="#f87171", font=font_lg)
    draw.text((970, 280), "• Boundary Countback rule", fill="#ffffff", font=font_sm)
    draw.text((970, 310), "  was officially removed", fill="#ffffff", font=font_sm)
    draw.text((970, 335), "  by ICC in Oct 2019.", fill="#ffffff", font=font_sm)
    draw.text((970, 370), "• Matches can no longer", fill="#cbd5e1", font=font_sm)
    draw.text((970, 395), "  be decided on boundaries", fill="#cbd5e1", font=font_sm)

    img.save(DATA_IMAGES_DIR / "super_over_procedure.png")
    print("✓ Generated super_over_procedure.png")


def generate_stumped_vs_run_out():
    """9. Stumped vs Run Out Comparison."""
    img, draw = create_base_canvas(
        title="Stumped (Law 39) vs Run Out (Law 38) Distinction",
        subtitle="Action of Wicketkeeper, Attempting a Run & Ball in Play Criteria",
        law_tag="MCC LAWS 38 & 39"
    )
    font_lg = get_default_font(24)
    font_md = get_default_font(18)
    font_sm = get_default_font(15)

    # Left: Stumped Box
    draw.rounded_rectangle([(80, 160), (620, 540)], radius=12, fill="#0f172a", outline="#38bdf8", width=3)
    draw.text((110, 185), "OUT STUMPED (LAW 39)", fill="#38bdf8", font=font_lg)
    draw.line([(110, 225), (590, 225)], fill="#334155", width=2)
    draw.text((110, 250), "1. Bowled delivery is NOT a No ball (can be Wide).", fill="#ffffff", font=font_sm)
    draw.text((110, 290), "2. Batter is out of their ground.", fill="#ffffff", font=font_sm)
    draw.text((110, 330), "3. Batter is NOT attempting a run.", fill="#fbbf24", font=font_md)
    draw.text((110, 370), "4. Wicket put down fairly by the wicket-keeper alone", fill="#ffffff", font=font_sm)
    draw.text((110, 395), "   without assistance of another fielder.", fill="#ffffff", font=font_sm)
    draw.text((110, 450), "Credited to Bowler & Wicketkeeper", fill="#86efac", font=font_sm)

    # Right: Run Out Box
    draw.rounded_rectangle([(660, 160), (1200, 540)], radius=12, fill="#0f172a", outline="#f59e0b", width=3)
    draw.text((690, 185), "OUT RUN OUT (LAW 38)", fill="#f59e0b", font=font_lg)
    draw.line([(690, 225), (1170, 225)], fill="#334155", width=2)
    draw.text((690, 250), "1. Ball is in play (even off a No ball).", fill="#ffffff", font=font_sm)
    draw.text((690, 290), "2. Either batter is out of their ground.", fill="#ffffff", font=font_sm)
    draw.text((690, 330), "3. Batter IS attempting a run (or trying to get back).", fill="#fbbf24", font=font_md)
    draw.text((690, 370), "4. Wicket put down by ANY fielder or keeper throwing.", fill="#ffffff", font=font_sm)
    draw.text((690, 420), "Sliding Bat Exception (Law 38.2.2):", fill="#94a3b8", font=font_sm)
    draw.text((690, 445), "Not out if bat grounded once and bounces in running.", fill="#86efac", font=font_sm)

    img.save(DATA_IMAGES_DIR / "stumped_vs_run_out.png")
    print("✓ Generated stumped_vs_run_out.png")


def generate_boundary_catch():
    """10. Fair Catch vs Boundary Touch."""
    img, draw = create_base_canvas(
        title="Boundary Rope Contact & Airborne Relay Catch",
        subtitle="First Contact Within Boundary • Complete Firm Control Required",
        law_tag="MCC LAW 33.2"
    )
    font_lg = get_default_font(22)
    font_md = get_default_font(17)
    font_sm = get_default_font(14)

    draw.rectangle([(100, 140), (1180, 560)], fill="#0f261b")
    # Boundary Rope
    draw.line([(600, 140), (600, 560)], fill="#ef4444", width=8)
    draw.text((530, 160), "IN PLAY", fill="#4ade80", font=font_lg)
    draw.text((630, 160), "OVER BOUNDARY (6)", fill="#f87171", font=font_lg)

    draw.rounded_rectangle([(140, 240), (550, 480)], radius=12, fill="#14532d", outline="#22c55e", width=2)
    draw.text((160, 260), "✓ LEGAL BOUNDARY CATCH", fill="#86efac", font=font_lg)
    draw.text((160, 305), "• Fielder's first contact MUST be inside rope", fill="#ffffff", font=font_sm)
    draw.text((160, 340), "• Can jump from inside, toss ball up, land outside,", fill="#ffffff", font=font_sm)
    draw.text((160, 365), "  jump back into field of play to complete catch.", fill="#ffffff", font=font_sm)
    draw.text((160, 405), "• Must NOT be touching boundary line while", fill="#fde047", font=font_sm)
    draw.text((160, 430), "  in physical contact with the ball.", fill="#fde047", font=font_sm)

    draw.rounded_rectangle([(650, 240), (1060, 480)], radius=12, fill="#7f1d1d", outline="#ef4444", width=2)
    draw.text((670, 260), "❌ NOT OUT CAUGHT (BOUNDARY 6)", fill="#fca5a5", font=font_lg)
    draw.text((670, 305), "• Any touch of boundary cushion while holding ball", fill="#ffffff", font=font_sm)
    draw.text((670, 340), "• Fielder grounding foot beyond boundary rope", fill="#ffffff", font=font_sm)
    draw.text((670, 365), "  at instant of touching the ball", fill="#ffffff", font=font_sm)
    draw.text((670, 415), "Scored as 6 runs to the batter.", fill="#fecaca", font=font_md)

    img.save(DATA_IMAGES_DIR / "fair_catch_boundary_relay.png")
    print("✓ Generated fair_catch_boundary_relay.png")


def generate_obstructing_field():
    """11. Obstructing the Field (Law 37)."""
    img, draw = create_base_canvas(
        title="Obstructing the Field: Wilful Diversion vs Accidental Contact",
        subtitle="Deliberate Distraction or Interception While Ball is in Play",
        law_tag="MCC LAW 37"
    )
    font_lg = get_default_font(22)
    font_md = get_default_font(17)
    font_sm = get_default_font(14)

    draw.rounded_rectangle([(80, 180), (600, 520)], radius=12, fill="#7f1d1d", outline="#ef4444", width=2)
    draw.text((100, 205), "❌ OUT: OBSTRUCTING THE FIELD", fill="#fecaca", font=font_lg)
    draw.line([(100, 245), (580, 245)], fill="#ef4444", width=1)
    draw.text((100, 270), "• Batter wilfully attempts to obstruct or distract", fill="#ffffff", font=font_sm)
    draw.text((100, 295), "  the fielding side by word or action.", fill="#ffffff", font=font_sm)
    draw.text((100, 335), "• Deliberately changing running trajectory to block", fill="#ffffff", font=font_sm)
    draw.text((100, 360), "  a fielder's throw aimed at the stumps.", fill="#ffffff", font=font_sm)
    draw.text((100, 400), "• Returning the ball to fielder with bat/hand", fill="#ffffff", font=font_sm)
    draw.text((100, 425), "  without consent of fielding side.", fill="#ffffff", font=font_sm)

    draw.rounded_rectangle([(680, 180), (1200, 520)], radius=12, fill="#14532d", outline="#22c55e", width=2)
    draw.text((700, 205), "✓ NOT OUT (PERMITTED ACTIONS)", fill="#bbf7d0", font=font_lg)
    draw.line([(700, 245), (1180, 245)], fill="#22c55e", width=1)
    draw.text((700, 270), "• Accidental obstruction while running normally.", fill="#ffffff", font=font_sm)
    draw.text((700, 310), "• Action taken solely to avoid serious injury.", fill="#ffffff", font=font_sm)
    draw.text((700, 350), "• Batter running straight in their established line.", fill="#ffffff", font=font_sm)
    draw.text((700, 390), "• Ball deflecting inadvertently off bat/body.", fill="#ffffff", font=font_sm)

    img.save(DATA_IMAGES_DIR / "obstructing_the_field.png")
    print("✓ Generated obstructing_the_field.png")


def generate_dead_ball_boundary_touch():
    """12. Dead Ball / Boundary Touch."""
    img, draw = create_base_canvas(
        title="Dead Ball & Boundary Interception Regulations",
        subtitle="When Does the Ball Become Dead on the Boundary",
        law_tag="MCC LAW 20"
    )
    font_lg = get_default_font(22)
    font_md = get_default_font(17)
    font_sm = get_default_font(14)

    draw.rounded_rectangle([(100, 180), (600, 500)], radius=12, fill="#1e293b", outline="#38bdf8", width=2)
    draw.text((120, 205), "CONDITIONS: BALL IS DEAD", fill="#38bdf8", font=font_lg)
    draw.text((120, 250), "• Settled in hands of keeper or bowler", fill="#ffffff", font=font_sm)
    draw.text((120, 285), "• A boundary 4 or 6 is scored", fill="#ffffff", font=font_sm)
    draw.text((120, 320), "• A batter is dismissed", fill="#ffffff", font=font_sm)
    draw.text((120, 355), "• Ball lodges in batter/umpire clothing", fill="#ffffff", font=font_sm)
    draw.text((120, 390), "• Umpire calls 'Over' or 'Time'", fill="#ffffff", font=font_sm)

    draw.rounded_rectangle([(680, 180), (1180, 500)], radius=12, fill="#1e293b", outline="#f59e0b", width=2)
    draw.text((700, 205), "CEASING TO BE DEAD", fill="#f59e0b", font=font_lg)
    draw.text((700, 250), "• The ball ceases to be dead (comes into play)", fill="#ffffff", font=font_sm)
    draw.text((700, 275), "  when the bowler begins run-up or action.", fill="#ffffff", font=font_sm)
    draw.text((700, 320), "• Either umpire calls 'Dead Ball' when:", fill="#ffffff", font=font_sm)
    draw.text((700, 345), "  - Unfair play occurs", fill="#cbd5e1", font=font_sm)
    draw.text((700, 370), "  - Serious player injury happens", fill="#cbd5e1", font=font_sm)
    draw.text((700, 395), "  - Striker is not ready for delivery", fill="#cbd5e1", font=font_sm)

    img.save(DATA_IMAGES_DIR / "dead_ball_boundary_touch.png")
    print("✓ Generated dead_ball_boundary_touch.png")


def generate_timed_out():
    """13. Timed Out (Law 40 - e.g., Angelo Mathews scenario)."""
    img, draw = create_base_canvas(
        title="Timed Out Regulations & Mandatory Timelines",
        subtitle="2-Minute (ICC) vs 3-Minute (MCC) Limit • Broken Equipment Precedent • Appeal Rule",
        law_tag="MCC LAW 40"
    )
    font_lg = get_default_font(22)
    font_md = get_default_font(17)
    font_sm = get_default_font(14)

    # Left Box: Countdown Clock & Limits
    draw.rounded_rectangle([(80, 150), (460, 520)], radius=12, fill="#1e293b", outline="#ef4444", width=3)
    draw.text((100, 175), "⏱️ COUNTDOWN LIMITS", fill="#f87171", font=font_lg)
    
    # Timer graphic circle
    draw.ellipse([(190, 220), (330, 360)], fill="#0f172a", outline="#ef4444", width=4)
    font_timer = get_default_font(32)
    draw.text((225, 275), "2:00", fill="#ef4444", font=font_timer)

    draw.text((100, 385), "• ICC ODI/T20I Playing Conditions:", fill="#ffffff", font=font_sm)
    draw.text((120, 405), "Strict 2 Minutes from dismissal", fill="#38bdf8", font=font_md)
    draw.text((100, 435), "• MCC Official Laws Default:", fill="#ffffff", font=font_sm)
    draw.text((120, 455), "3 Minutes from dismissal", fill="#a7f3d0", font=font_md)
    draw.text((100, 485), "Incoming batter must be ready to face ball.", fill="#94a3b8", font=font_sm)

    # Middle Box: The Angelo Mathews Precedent & Equipment Delays
    draw.rounded_rectangle([(490, 150), (860, 520)], radius=12, fill="#1e293b", outline="#f59e0b", width=2)
    draw.text((510, 175), "🛡️ BROKEN EQUIPMENT CHECK", fill="#fbbf24", font=font_lg)
    draw.text((510, 220), "• Angelo Mathews Precedent (2023 CWC):", fill="#ffffff", font=font_sm)
    draw.text((530, 245), "Helmet strap snapped before taking guard.", fill="#cbd5e1", font=font_sm)
    draw.text((510, 280), "• Umpire Consultation Requirement:", fill="#ffffff", font=font_sm)
    draw.text((530, 305), "Batter MUST seek umpire permission BEFORE", fill="#fca5a5", font=font_sm)
    draw.text((530, 325), "the 2-minute timer elapses to swap gear.", fill="#fca5a5", font=font_sm)
    draw.text((510, 360), "• Calling for New Equipment:", fill="#ffffff", font=font_sm)
    draw.text((530, 385), "Does NOT automatically freeze the clock.", fill="#cbd5e1", font=font_sm)
    draw.text((510, 420), "• Historical Precedent:", fill="#ffffff", font=font_sm)
    draw.text((530, 445), "First timed-out dismissal in international", fill="#cbd5e1", font=font_sm)
    draw.text((530, 465), "cricket history (SL vs BAN, Delhi 2023).", fill="#cbd5e1", font=font_sm)

    # Right Box: Mandatory Appeal by Fielding Captain
    draw.rounded_rectangle([(890, 150), (1200, 520)], radius=12, fill="#1e293b", outline="#34d399", width=2)
    draw.text((910, 175), "🗣️ MANDATORY APPEAL", fill="#34d399", font=font_lg)
    draw.text((910, 220), "• Law 31.1 Adjudication:", fill="#ffffff", font=font_sm)
    draw.text((930, 245), "Umpires CANNOT give a batter", fill="#ffffff", font=font_sm)
    draw.text((930, 265), "out Timed Out unilaterally.", fill="#ffffff", font=font_sm)
    draw.text((910, 305), "• Fielding Captain Must Appeal:", fill="#38bdf8", font=font_md)
    draw.text((930, 335), "An appeal ('How's that?') is", fill="#ffffff", font=font_sm)
    draw.text((930, 355), "strictly mandatory.", fill="#ffffff", font=font_sm)
    draw.text((910, 395), "• Captain May Withdraw Appeal:", fill="#ffffff", font=font_sm)
    draw.text((930, 420), "With umpire consent, the fielding", fill="#cbd5e1", font=font_sm)
    draw.text((930, 440), "captain may withdraw the appeal", fill="#cbd5e1", font=font_sm)
    draw.text((930, 460), "before the next ball is bowled.", fill="#cbd5e1", font=font_sm)

    img.save(DATA_IMAGES_DIR / "timed_out_law40.png")
    print("✓ Generated timed_out_law40.png")


def generate_hit_ball_twice():
    """14. Hit the Ball Twice (Law 34)."""
    img, draw = create_base_canvas(
        title="Hit the Ball Twice Adjudication Diagram",
        subtitle="Lawful Defence of Wicket vs Unlawful Second Strike • Dead Ball Call & Run Penalties",
        law_tag="MCC LAW 34"
    )
    font_lg = get_default_font(22)
    font_md = get_default_font(17)
    font_sm = get_default_font(14)

    # Left: Lawful Second Strike (Guarding Wicket)
    draw.rounded_rectangle([(100, 150), (620, 520)], radius=12, fill="#064e3b", outline="#22c55e", width=3)
    draw.text((120, 175), "✅ LAWFUL: DEFENDING THE WICKET", fill="#4ade80", font=font_lg)
    draw.text((120, 220), "• Law 34.2 Sole Purpose of Defence:", fill="#ffffff", font=font_sm)
    draw.text((140, 245), "Striker may strike ball a 2nd time solely to", fill="#f0fdf4", font=font_sm)
    draw.text((140, 265), "prevent the ball from hitting their stumps.", fill="#f0fdf4", font=font_sm)
    draw.text((120, 305), "• Permitted Equipment:", fill="#ffffff", font=font_sm)
    draw.text((140, 330), "Can be struck with the bat or any part of body", fill="#f0fdf4", font=font_sm)
    draw.text((140, 350), "(excluding a hand NOT holding the bat).", fill="#f0fdf4", font=font_sm)
    draw.text((120, 390), "• Crucial Limitation on Runs:", fill="#fde047", font=font_md)
    draw.text((140, 420), "NO RUNS may be scored off a defensive 2nd hit.", fill="#ffffff", font=font_sm)
    draw.text((140, 440), "If batters attempt a run, ball becomes dead,", fill="#ffffff", font=font_sm)
    draw.text((140, 460), "and 0 runs are credited to batting side.", fill="#ffffff", font=font_sm)

    # Right: Unlawful Second Strike (Out Hit the Ball Twice)
    draw.rounded_rectangle([(660, 150), (1180, 520)], radius=12, fill="#450a0a", outline="#ef4444", width=3)
    draw.text((680, 175), "❌ UNLAWFUL: OUT HIT BALL TWICE", fill="#f87171", font=font_lg)
    draw.text((680, 220), "• Law 34.1.1 Grounds for Dismissal:", fill="#ffffff", font=font_sm)
    draw.text((700, 245), "Striker wilfully strikes the ball a 2nd time:", fill="#fef2f2", font=font_sm)
    draw.text((720, 270), "1. To attempt a run or score a boundary", fill="#fca5a5", font=font_sm)
    draw.text((720, 295), "2. To prevent a fielder from completing a catch", fill="#fca5a5", font=font_sm)
    draw.text((720, 320), "3. When stumps were NOT in any danger", fill="#fca5a5", font=font_sm)
    draw.text((680, 360), "• Returning Ball to Fielder (Law 37.4):", fill="#ffffff", font=font_sm)
    draw.text((700, 385), "Hitting or kicking ball back to fielder without", fill="#fef2f2", font=font_sm)
    draw.text((700, 405), "consent is ruled OUT Obstructing the Field.", fill="#fef2f2", font=font_sm)
    draw.text((680, 445), "• Bowler Credit:", fill="#38bdf8", font=font_md)
    draw.text((700, 470), "The dismissal does NOT credit bowler's figures.", fill="#ffffff", font=font_sm)

    img.save(DATA_IMAGES_DIR / "hit_ball_twice_law34.png")
    print("✓ Generated hit_ball_twice_law34.png")


def generate_wide_ball():
    """15. Wide Ball Variations (Law 22)."""
    img, draw = create_base_canvas(
        title="Wide Ball Tramlines & Judging Criteria Explainer",
        subtitle="Off-Side Tramline • Leg-Side Margin • Batter Movement & Switch-Hit Adjustments",
        law_tag="MCC LAW 22"
    )
    font_lg = get_default_font(22)
    font_md = get_default_font(17)
    font_sm = get_default_font(14)

    # Pitch Diagram in Center
    draw.rectangle([(160, 140), (1120, 380)], fill="#152b1b", outline="#22c55e", width=2)
    # Stumps
    draw.rectangle([(980, 220), (1020, 300)], fill="#f59e0b", outline="#cbd5e1", width=2)
    draw.text((985, 195), "STUMPS", fill="#f59e0b", font=font_sm)

    # Tramlines
    # Off-side tramline (17 inches inside return crease)
    draw.line([(200, 180), (1000, 180)], fill="#38bdf8", width=3)
    draw.text((220, 155), "OFF-SIDE TRAMLINE (17 inches from return crease)", fill="#38bdf8", font=font_sm)

    # Leg-side tramline
    draw.line([(200, 340), (1000, 340)], fill="#f43f5e", width=3)
    draw.text((220, 350), "LEG-SIDE MARGIN (Strict Wide in Limited Overs)", fill="#f43f5e", font=font_sm)

    # Ball passes wide line
    draw.line([(200, 160), (1080, 160)], fill="#fbbf24", width=4)
    draw.ellipse([(1060, 145), (1095, 180)], fill="#fbbf24", outline="#ffffff", width=2)
    draw.text((950, 130), "WIDE BALL", fill="#fbbf24", font=font_lg)

    # 3 Summary Cards Below
    draw.rounded_rectangle([(100, 400), (430, 530)], radius=10, fill="#1e293b", outline="#38bdf8", width=2)
    draw.text((120, 415), "1. OFF-SIDE RULE", fill="#38bdf8", font=font_md)
    draw.text((120, 445), "• Ball outside tramline is Wide.", fill="#ffffff", font=font_sm)
    draw.text((120, 470), "• If batter moves toward off-side,", fill="#cbd5e1", font=font_sm)
    draw.text((120, 490), "  wide line moves with batter.", fill="#cbd5e1", font=font_sm)

    draw.rounded_rectangle([(460, 400), (790, 530)], radius=10, fill="#1e293b", outline="#f43f5e", width=2)
    draw.text((480, 415), "2. LEG-SIDE ZERO MARGIN", fill="#f43f5e", font=font_md)
    draw.text((480, 445), "• Any ball passing down leg side", fill="#ffffff", font=font_sm)
    draw.text((480, 465), "  behind batter's pads = WIDE.", fill="#ffffff", font=font_sm)
    draw.text((480, 490), "• Unless batter moves / plays shot.", fill="#cbd5e1", font=font_sm)

    draw.rounded_rectangle([(820, 400), (1180, 530)], radius=10, fill="#1e293b", outline="#22c55e", width=2)
    draw.text((840, 415), "3. PENALTY & CONDITIONS", fill="#4ade80", font=font_md)
    draw.text((840, 445), "• 1 Penalty Run + Extra delivery.", fill="#ffffff", font=font_sm)
    draw.text((840, 470), "• Batter CAN be out Stumped / Run Out.", fill="#ffffff", font=font_sm)
    draw.text((840, 495), "• Batter CANNOT be bowled or LBW.", fill="#cbd5e1", font=font_sm)

    img.save(DATA_IMAGES_DIR / "wide_ball_variations_law22.png")
    print("✓ Generated wide_ball_variations_law22.png")


def generate_all_visuals():
    """Generates all 15 visual scenario infographics."""
    print(f"Generating visual infographics into: {DATA_IMAGES_DIR.resolve()}")
    generate_lbw_hawkeye()
    generate_dead_ball_helmet()
    generate_no_ball_foot_fault()
    generate_no_ball_waist_high()
    generate_powerplay_fielding()
    generate_mankad_run_out()
    generate_drs_umpires_call()
    generate_super_over_procedure()
    generate_stumped_vs_run_out()
    generate_boundary_catch()
    generate_obstructing_field()
    generate_dead_ball_boundary_touch()
    generate_timed_out()
    generate_hit_ball_twice()
    generate_wide_ball()
    print("🎉 All 15 visual explainer infographics generated successfully!")


if __name__ == "__main__":
    generate_all_visuals()
