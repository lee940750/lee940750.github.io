from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, PageBreak, Paragraph, SimpleDocTemplate


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'assets' / 'documents' / 'cheng-hsuan-lee-cv.pdf'
INK = colors.HexColor('#161616')
MUTED = colors.HexColor('#4d5960')
ACCENT = colors.HexColor('#0b4f4a')
WIDTH = 7.4 * inch

body = ParagraphStyle('Body', fontName='Helvetica', fontSize=9.4, leading=12, textColor=INK, spaceAfter=4)
title = ParagraphStyle('Name', parent=body, fontName='Helvetica-Bold', fontSize=22, leading=25, alignment=TA_CENTER, spaceAfter=4)
contact = ParagraphStyle('Contact', parent=body, fontSize=9.2, leading=12, alignment=TA_CENTER, textColor=MUTED, spaceAfter=3)
portfolio = ParagraphStyle('Portfolio', parent=contact, fontName='Helvetica-Bold', fontSize=10.5, leading=13, textColor=ACCENT, spaceAfter=4)
heading = ParagraphStyle('Section', parent=body, fontName='Helvetica-Bold', fontSize=11.5, leading=14, spaceBefore=10, spaceAfter=4, keepWithNext=True)
role = ParagraphStyle('Role', parent=body, fontName='Helvetica-Bold', fontSize=10, leading=12.5, spaceBefore=4, spaceAfter=2, keepWithNext=True)
meta = ParagraphStyle('Meta', parent=body, fontName='Helvetica-Oblique', fontSize=9, leading=11.2, textColor=MUTED, spaceAfter=4, keepWithNext=True)
bullet = ParagraphStyle('Bullet', parent=body, leftIndent=10, firstLineIndent=-7, spaceAfter=4)


def p(text, style=body):
    return Paragraph(text, style)


def section(label):
    return [p(label, heading), HRFlowable(width=WIDTH, thickness=0.55, color=ACCENT, spaceAfter=5)]


def bullets(items):
    return [p('- ' + text, bullet) for text in items]


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#d9e1df'))
    canvas.setLineWidth(0.5)
    canvas.line(0.55 * inch, 0.42 * inch, 7.95 * inch, 0.42 * inch)
    canvas.setFont('Helvetica', 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(0.55 * inch, 0.28 * inch, 'CHENG-HSUAN LEE | Academic CV')
    canvas.drawRightString(7.95 * inch, 0.28 * inch, f'{doc.page}')
    canvas.restoreState()


def build_story():
    story = [
        p('CHENG-HSUAN LEE', title),
        p('<link href="https://lee940750.github.io" color="#0b4f4a">lee940750.github.io</link>', portfolio),
        p('Taipei, Taiwan | +886 905 499 682 | <link href="mailto:lee940750@gmail.com">lee940750@gmail.com</link>', contact),
        p('Legged robotics | Actuator design | Learning-based control | Sim-to-real experiments', contact),
    ]
    story += section('EDUCATION')
    story.append(p('National Taiwan University | B.S. in Mechanical Engineering', role))
    story.append(p('Taipei, Taiwan | 2023-2027 (expected)', meta))
    story.append(p(
        '<b>Selected coursework:</b> Microprocessor Controlled Systems; Automatic Control; Applied Electronics; '
        'Mechanism; Machine Design Theory; Engineering Graphics; Practice of Mechanical Engineering; '
        'Manufacturing Processes; Workshop Practice; Mechanical Engineering Laboratory I/II; Dynamics; Numerical Analysis.'
    ))
    story.append(p('<b>Taipei Municipal Chien Kuo High School</b> | 2020-2023 | CKHS Robotics Team'))

    story += section('PUBLICATION AND CONFERENCE PRESENTATION')
    story.append(p(
        '<b>Cheng-Hsuan Lee</b>, Yi-Cheng Wang, Yu-Hsuan Chi, Yu-Mei Huang, Yu-Cheng Kuo, and Chung-Hsien Kuo. '
        '<b>"Sim-to-Real Performance Analysis of a Custom Quadruped Robot Using Gait-Generator-Guided Reinforcement Learning."</b> '
        '<i>2026 International Automatic Control Conference (CACS 2026)</i>, IEEE conference proceedings, '
        'Taichung, Taiwan, October 21-24, 2026. '
        '<link href="https://lee940750.github.io/assets/documents/cacs-2026-quadruped-paper.pdf" color="#0b4f4a">[Paper]</link>'
    ))
    story += bullets([
        '<b>First author; in-person English oral presenter.</b> Personally presented the research at CACS 2026.',
        '<b>Best Student Paper Award - Honorable Mention;</b> selected among <b>11 finalists</b> before the final award evaluation.',
    ])

    story += section('RESEARCH AND LABORATORY EXPERIENCE')
    story.append(p('NTUME ASR Lab | Learning-Based Quadruped Robot Integration', role))
    story.append(p('Undergraduate researcher | Control Systems Laboratory | Rifle custom 12-DoF quadruped', meta))
    story.append(p(
        'Research across <b>actuator hardware, embedded motor control, locomotion learning, and physical validation</b>. '
        'Connected mechanical behavior and controller feedback to the sim-to-real investigation reported in our first-author CACS paper.'
    ))
    story += bullets([
        '<b>Actuator and reducer development:</b> designed and fabricated cycloidal and planetary reduction-gearbox concepts; '
        'examined packaging, backlash, bearing support, shaft strength, assembly tolerance, and serviceability for repeated robot tests.',
        '<b>Motor-control interfaces:</b> worked on communication packets, Arduino/Teensy-side programming, command/readback routines, '
        'calibration, and position/velocity/current feedback with ODrive-controlled actuation.',
        '<b>Learning experiments:</b> ran and documented Isaac Lab / Isaac Sim locomotion workflows using PPO and imitation learning; '
        'compared clearance, posture, contact, torque, and action-smoothness terms using checkpoints, TensorBoard records, and simulation videos.',
        '<b>Hardware-feasible gait guidance:</b> the study first checked a robot-specific gait reference by direct hardware execution, '
        'then used joint- and foot-tracking references to guide PPO toward physically executable locomotion.',
        '<b>Deployment and failure diagnosis:</b> used ROS 2 launches, rosbag data, joint feedback, IMU records, current traces, and physical '
        'inspection to separate policy errors from sensing, communication, calibration, and drivetrain faults.',
        '<b>Quantitative transfer evidence:</b> the study evaluated two guided controllers over <b>six hardware recordings</b>; all sustained '
        'walking at a <b>0.4 m/s straight, level-ground command</b>, retaining <b>84.9-90.0%</b> of simulated swing amplitude '
        'with <b>0.980-0.990</b> phase correlation.',
        '<b>Failure analysis and next experiments:</b> traced the recorded pure-RL deployment failure to inadequate foot motion and actuator '
        'loading; documented residual joint-tracking, body-motion, and current gaps to motivate hardware identification and better feedback estimation.',
    ])

    story.append(PageBreak())
    story += section('SELECTED ENGINEERING PROJECTS')
    story.append(p('Self-Built Simple Robot Dog | Team Lead, Mechanical Designer, Controls Developer', role))
    story.append(p('Microprocessor Controlled Systems | Course-built eight-servo platform, distinct from the ASR Lab research robot', meta))
    story += bullets([
        '<b>Led mechanical and embedded integration:</b> designed a serviceable 3D-printed body, servo layout, wiring, and battery placement; '
        'translated MATLAB gait and inverse-kinematics reasoning into ESP32/PCA9685 control with calibrated servo output.',
        '<b>A+ result:</b> demonstrated walking, standing, sitting, waving, and rocking through repeated hardware testing and repair.',
    ])
    story.append(p('Quadcopter Ball-Transfer Drone | Team Lead and Systems Integrator', role))
    story.append(p('Practice of Mechanical Engineering | Full marks and A+ course grade', meta))
    story += bullets([
        '<b>Led a complete flying-robot mission:</b> coordinated airframe, payload mechanism, propulsion, electronics, SBUS signal debugging, '
        'spare parts, and final-run preparation; used thrust-to-throttle tests and vibration checks to guide integration.',
        '<b>Peer influence:</b> many peer teams referenced our system architecture, testing approach, and integration decisions during their builds.',
    ])
    story.append(p('Foldable Ball Transfer Mechanism | Team Lead', role))
    story.append(p('Machine Design Theory | Packaging-constrained deployable mechanism', meta))
    story += bullets([
        '<b>Led concept selection and fabrication planning:</b> developed folding architecture and evaluated hinges, latches, stiffness, '
        'assembly sequence, and repair access to achieve reliable deployment and ball transfer within storage constraints.',
    ])

    story += section('LEADERSHIP AND TEAM EXECUTION')
    story += bullets([
        '<b>Engineering project leadership:</b> led the robot dog, drone, and foldable-mechanism teams, translating open-ended goals '
        'into design decisions, task ownership, integration tests, and final deliverables.',
        '<b>CKHS Robotics Team / FIRST Robotics Competition:</b> served as programming, strategy, and scouting leader; connected '
        'autonomous logic, driver needs, mechanism limits, match data, and repair constraints during regional and championship competition.',
        '<b>Evidence-based coordination:</b> supported mobile scouting tools and Excel analysis workflows for robot comparison, '
        'alliance selection, and match decisions; coordinated mechanical, electrical, and software troubleshooting under deadlines.',
    ])

    story += section('AWARDS AND RECOGNITION')
    story += bullets([
        '<b>2026 CACS:</b> Best Student Paper Award - Honorable Mention; one of 11 finalists; first author.',
        '<b>2022 FRC Sacramento Regional:</b> Finalist and Industrial Design Award.',
        '<b>2022 FRC New Taipei City x Hon Hai Regional:</b> Engineering Inspiration Award; qualified for Houston Championship.',
        '<b>2023 FRC Los Angeles and San Diego Regionals:</b> Excellence in Engineering Award at each regional.',
        '<b>2nd ISS Kibo Robot Programming Challenge, Taiwan Preliminary:</b> Merit Award.',
        '<b>58th Hsinchu County Science Fair, Biology:</b> Second Place.',
    ])

    story += section('TECHNICAL SKILLS')
    for text in [
        '<b>Mechanical:</b> CAD, engineering drawings, 3D printing, machining, mechanism design, cycloidal/planetary reducers, actuator packaging, and tolerance/assembly planning.',
        '<b>Learning and control:</b> Isaac Lab / Isaac Sim, PPO/DWAQ workflows, imitation learning, reward design, ROS 2, rosbag, TensorBoard, URDF, Pinocchio, MATLAB/Simulink.',
        '<b>Embedded and software:</b> Python, C++, Arduino, ESP32, Teensy, ODrive, PCA9685, RS485, UART, I2C, PWM, Linux, and Git/GitHub.',
        '<b>Experiments:</b> motor feedback analysis, servo calibration, thrust testing, signal-chain debugging, failure isolation, and technical reporting.',
    ]:
        story.append(p(text))
    return story


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=letter,
        rightMargin=0.55 * inch, leftMargin=0.55 * inch,
        topMargin=0.42 * inch, bottomMargin=0.55 * inch,
        title='CHENG-HSUAN LEE Academic CV', author='CHENG-HSUAN LEE',
    )
    doc.build(build_story(), onFirstPage=footer, onLaterPages=footer)


if __name__ == '__main__':
    main()
