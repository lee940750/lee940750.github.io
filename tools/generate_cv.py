from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "documents" / "cheng-hsuan-lee-cv.pdf"

TEAL = colors.HexColor("#0f766e")
TEXT = colors.HexColor("#161616")
MUTED = colors.HexColor("#4d5960")
LINE = colors.HexColor("#d8e2df")
SOFT = colors.HexColor("#f4f8f6")


styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "Title",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=22,
    leading=25,
    alignment=TA_CENTER,
    textColor=TEXT,
    spaceAfter=3,
)

portfolio_style = ParagraphStyle(
    "Portfolio",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=11,
    leading=13,
    alignment=TA_CENTER,
    textColor=TEAL,
    spaceAfter=2,
)

contact_style = ParagraphStyle(
    "Contact",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=9,
    leading=11,
    alignment=TA_CENTER,
    textColor=MUTED,
    spaceAfter=4,
)

signal_style = ParagraphStyle(
    "Signal",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=9,
    leading=11,
    alignment=TA_CENTER,
    textColor=TEAL,
    spaceAfter=11,
)

section_style = ParagraphStyle(
    "Section",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=12.5,
    leading=14,
    textColor=TEXT,
    spaceBefore=8,
    spaceAfter=5,
)

body_style = ParagraphStyle(
    "Body",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=8.8,
    leading=10.4,
    textColor=TEXT,
    alignment=TA_LEFT,
    spaceAfter=4,
)

body_small_style = ParagraphStyle(
    "BodySmall",
    parent=body_style,
    fontSize=8.45,
    leading=9.8,
    spaceAfter=3,
)

role_style = ParagraphStyle(
    "Role",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=9.4,
    leading=11,
    textColor=TEXT,
    spaceAfter=0,
)

italic_style = ParagraphStyle(
    "Italic",
    parent=styles["Normal"],
    fontName="Helvetica-Oblique",
    fontSize=8.7,
    leading=10.2,
    textColor=MUTED,
    spaceAfter=2,
)

bullet_style = ParagraphStyle(
    "Bullet",
    parent=body_small_style,
    leftIndent=10,
    firstLineIndent=-7,
    spaceAfter=2,
)

table_label_style = ParagraphStyle(
    "TableLabel",
    parent=body_small_style,
    fontName="Helvetica-Bold",
    fontSize=8.7,
    leading=10.2,
    textColor=TEAL,
)


def p(text, style=body_style):
    return Paragraph(text, style)


def section(title):
    return [
        Paragraph(title, section_style),
        Table([[""]], colWidths=[7.6 * inch], rowHeights=[1.1], style=[
            ("BACKGROUND", (0, 0), (-1, -1), TEAL),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]),
        Spacer(1, 5),
    ]


def bullets(items):
    return [Paragraph("- " + item, bullet_style) for item in items]


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(0.55 * inch, 0.42 * inch, 7.95 * inch, 0.42 * inch)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(0.55 * inch, 0.28 * inch, "CHENG-HSUAN LEE | Academic CV")
    canvas.drawRightString(7.95 * inch, 0.28 * inch, f"Page {doc.page}")
    canvas.restoreState()


def technical_table(rows, col_widths=None):
    if col_widths is None:
        col_widths = [1.55 * inch, 6.05 * inch]
    table_rows = []
    for label, desc in rows:
        table_rows.append([p(label, table_label_style), p(desc, body_small_style)])
    table = Table(table_rows, colWidths=col_widths, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("BACKGROUND", (0, 0), (0, -1), SOFT),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def build_story():
    story = []

    story += [
        Paragraph("CHENG-HSUAN LEE", title_style),
        Paragraph("PORTFOLIO: lee940750.github.io", portfolio_style),
        Paragraph("Taipei, Taiwan | +886 905 499 682 | lee940750@gmail.com", contact_style),
        Paragraph(
            "Robotics-focused Mechanical Engineering undergraduate | Legged robotics, robot learning, actuator design, sim-to-real testing",
            signal_style,
        ),
    ]

    story += section("PROFILE")
    story.append(p(
        "Mechanical Engineering undergraduate at National Taiwan University focused on complete physical robot systems. "
        "My current work in NTUME ASR Lab connects 12-DoF quadruped locomotion, actuator/reducer design, motor communication, "
        "Isaac Lab reinforcement-learning workflows, ROS2 deployment, and sim-to-real debugging. I am especially interested "
        "in legged robots whose hardware, control policies, and experimental behavior must be designed together."
    ))

    story += section("EDUCATION")
    story.append(p("<b>National Taiwan University - B.S. in Mechanical Engineering</b>", body_style))
    story.append(p("<i>Taipei, Taiwan | Expected 2027</i>", italic_style))
    story.append(p(
        "<b>Relevant coursework:</b> Automatic Control; Microprocessor Controlled Systems; Applied Electronics; Mechanism; "
        "Machine Design Theory; Engineering Graphics; Practice of Mechanical Engineering; Manufacturing Processes; Workshop Practice; "
        "Mechanical Engineering Laboratory I/II; Engineering Materials; Strength of Materials; Dynamics; Numerical Analysis; "
        "Fluid Mechanics; Thermodynamics; Heat Transfer.",
        body_small_style,
    ))
    story.append(p("<b>Taipei Municipal Chien Kuo High School</b>", body_style))
    story.append(p("<i>Taipei, Taiwan | 2020-2023</i>", italic_style))
    story.append(p(
        "Built early robotics foundation through CKHS Robotics Team, FRC programming, strategy, scouting, and international competition work.",
        body_small_style,
    ))

    story += section("RESEARCH AND LABORATORY EXPERIENCE")
    story.append(p("<b>NTUME ASR Lab - Learning-Based Quadruped Robot Integration</b>", role_style))
    story.append(p(
        "<i>Control Systems Laboratory Experience | Rifle 12-DoF quadruped platform | Current laboratory work</i>",
        italic_style,
    ))
    story.append(p(
        "Working at the boundary between legged robot hardware and learning-based control. My lab work focuses on making learned "
        "locomotion usable on imperfect physical hardware by connecting actuator design, embedded motor communication, policy training, "
        "deployment logs, and failure analysis into one experimental loop.",
        body_small_style,
    ))
    story += bullets([
        "Built a full quadruped development workflow that links mechanical architecture, leg-module packaging, actuator layout, compact reducer concepts, wiring, motor communication, Isaac Lab simulation, and physical robot validation.",
        "Designed and fabricated motor reduction gearbox concepts for leg actuation, including cycloidal and planetary reducers, while evaluating torque transmission, backlash, bearing support, manufacturability, assembly tolerance, and repair access.",
        "Developed motor-control and communication experience through packet design, Arduino-based control-board programming, command scaling, calibration, and speed/position/current feedback checks.",
        "Ran and documented Isaac Lab / Isaac Sim locomotion experiments using DWAQ/PPO and imitation-learning workflows, tuning foot clearance, posture, contact behavior, gait regularity, torque penalties, action smoothness, and standing behavior.",
        "Prepared the simulation-to-hardware path through URDF/model checks, observation/action mapping, actuator limits, policy export, ROS2 motor/sensor launches, rosbag recording, topic review, and safety checks.",
        "Diagnosed deployment failures by comparing policy outputs, motor logs, foot-height traces, IMU interpretation, TensorBoard records, and observed robot motion, separating policy issues from actuator, sensor, communication, and assembly problems.",
        "Converted physical failures into engineering revisions, including encoder/magnet-seat tolerance checks, shaft material and coaxiality concerns, loose linkage correction, calibration changes, and serviceability improvements for repeated tests.",
    ])
    story.append(Spacer(1, 3))
    story.append(technical_table([
        (
            "Research signal",
            "Hardware-aware robot learning: actuator packaging, reducer behavior, motor feedback, state estimation, and learned policy behavior are treated as one coupled system.",
        ),
        (
            "Methods in use",
            "Isaac Lab / Isaac Sim, DWAQ/PPO, imitation learning, reward shaping, TensorBoard run comparison, URDF checks, ROS2 launch workflows, rosbag records, and topic-level debugging.",
        ),
        (
            "Hardware interface",
            "Actuator/reducer packaging, ODrive/Teensy context, motor speed/position/current feedback, communication packet design, calibration, wiring checks, and fault isolation.",
        ),
        (
            "Graduate fit",
            "Prepared for robotics research where mechanical design, embedded control, robot learning, and real-world testing must be evaluated together rather than in isolation.",
        ),
    ]))

    story.append(PageBreak())

    story += section("SELECTED ENGINEERING PROJECTS")
    story.append(p("<b>Self-Built Simple Robot Dog - Team Lead, Mechanical Designer, Controls Developer</b>", role_style))
    story.append(p("<i>Microprocessor Controlled Systems | A+ outcome | ESP32, PCA9685, MATLAB, Arduino, 3D-printed structure</i>", italic_style))
    story += bullets([
        "Designed and integrated a compact eight-servo quadruped platform around serviceability, wiring, battery placement, center-of-gravity position, and repeated repair during gait testing.",
        "Translated inverse-kinematics and gait reasoning from MATLAB into embedded ESP32/PCA9685 servo control, separating behavior logic, gait timing, calibration, and servo output for easier debugging.",
        "Implemented and tuned behavior modes including walking, standing, sitting, waving, hip-lift, and rocking, using observed robot motion to revise timing and calibration choices.",
        "Used the project as a practical bridge into legged-robot research by confronting the mismatch between simulated motion, servo limits, wiring, and physical body behavior.",
    ])

    story.append(p("<b>Quadcopter Ball-Transfer Drone - Team Lead and Systems Integrator</b>", role_style))
    story.append(p("<i>Practice of Mechanical Engineering | Full marks and A+ outcome | Peer reference point for many teams</i>", italic_style))
    story += bullets([
        "Led full-system mission design for a drone that had to fly, carry, transfer, and release balls reliably under final evaluation pressure.",
        "Coordinated airframe, payload mechanism, flight controller, SBUS receiver, ESC/motor setup, spare-system planning, and final-risk control; our architecture and testing process became a reference point for many peer teams.",
        "Used thrust-to-throttle tests, drift diagnosis, vibration checks, crash recovery, payload trials, and signal-chain debugging to convert failure symptoms into specific design decisions.",
        "Maintained engineering records across final report, dynamic testing, thrust characterization, flight-controller/motor/SBUS debugging, and personal design feedback.",
    ])

    story.append(p("<b>Foldable Ball Transfer Mechanism - Team Lead</b>", role_style))
    story.append(p("<i>Machine Design Theory | Mechanism design, packaging constraint, fabrication-aware decision making</i>", italic_style))
    story += bullets([
        "Designed a foldable long-distance ball-transfer mechanism under packaging and deployment constraints, balancing ideal motion with buildable structure.",
        "Evaluated folding architecture, linkage geometry, component accessibility, fabrication feasibility, latch behavior, locked-state stiffness, and tolerance sensitivity before committing to the final design.",
        "Favored reliable deployment, assembly order, repair access, and accessible fabrication over unnecessary complexity, strengthening practical hardware judgment.",
    ])

    story += section("COMPETITION ROBOTICS AND LEADERSHIP")
    story.append(p("<b>CKHS Robotics Team - Programming and Strategy Lead</b>", role_style))
    story.append(p("<i>FIRST Robotics Competition and scouting/strategy systems</i>", italic_style))
    story += bullets([
        "Led programming and strategy work in competition robotics, connecting autonomous logic, driver needs, mechanism limits, match strategy, and repair speed under real event pressure.",
        "Built scouting and analysis workflows, including mobile data collection and Excel/VBA-based comparison tools, to turn large match datasets into alliance-selection and strategy decisions.",
        "Gained repeated practice communicating across mechanical, electrical, programming, drive-team, and strategy responsibilities during high-pressure regional and championship events.",
    ])

    story += section("AWARDS AND RECOGNITION")
    story += bullets([
        "2022 FRC Sacramento Regional - Finalist and Industrial Design Award.",
        "2022 FRC New Taipei City x Hon Hai Regional - Engineering Inspiration Award; qualified for Houston Championship.",
        "2022 FRC Carver Championship Division, Houston - international championship participation.",
        "2023 FRC Los Angeles Regional - Excellence in Engineering Award.",
        "2023 FRC San Diego Regional - Excellence in Engineering Award.",
        "2nd ISS Kibo Robot Programming Challenge Taiwan Preliminary - Merit Award.",
        "58th Hsinchu County Science Fair, Biology Division - Second Place.",
    ])

    story += section("TECHNICAL SKILLS")
    story.append(technical_table([
        (
            "Mechanical Systems",
            "Mechanism design; actuator packaging; cycloidal/planetary reducer concepts; CAD; 3D printing; machining; engineering drawings; tolerance and assembly planning.",
        ),
        (
            "Robot Learning and Control",
            "NVIDIA Isaac Lab / Isaac Sim; DWAQ/PPO workflows; imitation learning; reward shaping; observation/action-space tuning; URDF; ROS2; Pinocchio; MATLAB/Simulink; motor calibration.",
        ),
        (
            "Embedded and Software",
            "Python; C++; Arduino; ESP32; Teensy 4.0; ODrive; PCA9685; RS485; UART; I2C; PWM; Git/GitHub; Linux; serial diagnostics.",
        ),
        (
            "Testing and Documentation",
            "Thrust testing; vibration/drift diagnosis; motor speed/position/current feedback; TensorBoard comparison; rosbag/topic checks; failure isolation; engineering reports; portfolio documentation.",
        ),
    ]))

    return story


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        rightMargin=0.45 * inch,
        leftMargin=0.45 * inch,
        topMargin=0.42 * inch,
        bottomMargin=0.55 * inch,
        title="CHENG-HSUAN LEE Academic CV",
        author="CHENG-HSUAN LEE",
    )
    doc.build(build_story(), onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    main()
