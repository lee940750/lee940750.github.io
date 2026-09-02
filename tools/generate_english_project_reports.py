from pathlib import Path

import fitz
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "assets" / "documents"


def source_pages(filename: str) -> int:
    with fitz.open(str(DOCS / filename)) as doc:
        return doc.page_count


def make_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=21,
            leading=25,
            textColor=colors.HexColor("#073b4c"),
            alignment=TA_LEFT,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Deck",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#4a5f68"),
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Section",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#073b4c"),
            spaceBefore=12,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SmallCaps",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=10,
            textColor=colors.HexColor("#0f766e"),
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableHeader",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=10,
            textColor=colors.white,
            spaceAfter=0,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#1f2933"),
            spaceAfter=7,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportBullet",
            parent=styles["Body"],
            leftIndent=14,
            firstLineIndent=-8,
            bulletIndent=0,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Footer",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=9,
            textColor=colors.HexColor("#607078"),
            alignment=TA_RIGHT,
        )
    )
    return styles


STYLES = make_styles()


def clean(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def p(text: str, style="Body"):
    return Paragraph(clean(text), STYLES[style])


def bullets(items):
    flow = []
    for item in items:
        flow.append(Paragraph(clean(item), STYLES["ReportBullet"], bulletText="-"))
    return flow


def meta_table(rows):
    table = Table(
        [[p(k, "SmallCaps"), p(v, "Deck")] for k, v in rows],
        colWidths=[1.65 * inch, 4.85 * inch],
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f6faf9")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cfe0dd")),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d9e7e4")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def decision_table(headers, rows):
    data = [[p(h, "TableHeader") for h in headers]]
    for row in rows:
        data.append([p(cell, "Deck") for cell in row])
    table = Table(data, colWidths=[1.45 * inch, 1.65 * inch, 1.9 * inch, 1.5 * inch], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#fbfdfc")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cfe0dd")),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d9e7e4")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def page_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#d9e7e4"))
    canvas.line(doc.leftMargin, 0.55 * inch, LETTER[0] - doc.rightMargin, 0.55 * inch)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#607078"))
    canvas.drawRightString(
        LETTER[0] - doc.rightMargin,
        0.35 * inch,
        f"CHENG-HSUAN LEE - English project report version - Page {doc.page}",
    )
    canvas.restoreState()


COMMON_REVIEW_NOTE = (
    "This English version is formatted for graduate application review. It preserves the engineering "
    "purpose, design decisions, validation evidence, and individual contribution signals of the original "
    "course document while presenting the material in concise English."
)


REPORTS = [
    {
        "source": "drone-final-engineering-report.pdf",
        "output": "drone-final-engineering-report-english.pdf",
        "title": "Quadcopter Ball-Transfer Drone - Final Engineering Report",
        "project": "Quadcopter Ball-Transfer Drone",
        "course": "Practice of Mechanical Engineering",
        "type": "Final engineering report",
        "role": "Team lead, system designer, and integration coordinator",
        "overview": [
            "This project developed a quadcopter capable of carrying and transferring a ball while maintaining sufficient flight stability for final evaluation. The mission required mechanical design, airframe layout, payload architecture, electronics integration, propulsion testing, and final-run risk control to work as one system.",
            "My strongest contribution was keeping the team focused on system behavior instead of isolated subsystem success. Payload placement changed mass distribution, frame stiffness influenced vibration, and motor/propeller choices affected the available control margin.",
            "The completed build earned full marks and a course grade of A+. The system also became a reference point for many peer teams, who looked to our architecture, testing approach, and integration decisions while developing their own builds.",
        ],
        "signals": [
            "Led mission-level design decisions across airframe, payload, electronics, propulsion, and test strategy.",
            "Used thrust-to-throttle experiments to convert propulsion uncertainty into actionable design information.",
            "Separated signal-chain, flight-controller, structural, vibration, and motor issues during integration debugging.",
            "Prepared spare parts, rule checks, and fallback responses for a final evaluation with limited room for failure.",
        ],
        "sections": [
            ("System Architecture", [
                "The drone was treated as a full robot system: airframe geometry, ball-transfer mechanism, power distribution, sensor/controller setup, and test procedure were evaluated together.",
                "Design decisions were prioritized by their effect on stable flight and successful ball transfer, not by whether they looked elegant as individual components.",
            ]),
            ("Testing and Validation", [
                "Propulsion behavior was studied through motor, propeller, ESC, battery, and throttle-response testing.",
                "Flight tests were used to diagnose drift, vibration, crash risk, resonance, control setup, and mechanical fragility.",
                "Final preparation focused on repeatability, spare assemblies, and controlled responses to likely failure modes.",
            ]),
            ("Graduate Application Signal", [
                "This report shows the ability to lead a physical robotics project where mechanical design, embedded systems, flight behavior, and team decisions must be integrated under evaluation pressure.",
            ]),
        ],
        "table": [
            ["Payload integration", "Designed airframe and transfer mechanism as one system", "Reduced late-stage instability after payload assembly", "System architecture"],
            ["Unknown propulsion margin", "Ran thrust-to-throttle experiments", "Turned motor behavior into design evidence", "Experimental validation"],
            ["Unstable flight symptoms", "Separated signal, controller, vibration, and structure causes", "Avoided treating every issue as tuning", "Integration debugging"],
            ["Final evaluation risk", "Prepared spare parts and fallback plans", "Made the final run less dependent on one perfect attempt", "Engineering leadership"],
        ],
    },
    {
        "source": "drone-thrust-to-throttle-experiment.pdf",
        "output": "drone-thrust-to-throttle-experiment-english.pdf",
        "title": "Drone Propulsion Validation - Thrust-to-Throttle Experiment",
        "project": "Quadcopter Ball-Transfer Drone",
        "course": "Practice of Mechanical Engineering",
        "type": "Experiment record",
        "role": "System test planner and integration debugger",
        "overview": [
            "This experiment documented the relationship between throttle command and produced thrust for the drone propulsion system. The goal was to make motor, propeller, ESC, and battery behavior visible before relying on the drone in final flight tests.",
            "The experiment supported safer engineering judgment: instead of choosing parts only from nominal specifications, the team used measured behavior to reason about lift margin, payload feasibility, and control risk.",
        ],
        "signals": [
            "Connected propulsion testing to flight stability and payload decisions.",
            "Used quantitative test behavior to guide final hardware choices.",
            "Treated the propulsion chain as a system: command input, ESC response, motor output, propeller loading, and battery condition.",
        ],
        "sections": [
            ("Experiment Purpose", [
                "Measure how thrust changed with throttle command and identify whether the system had enough margin for controlled flight with the mission payload.",
                "Use the data to support airframe and payload decisions before final integration.",
            ]),
            ("Engineering Interpretation", [
                "A useful drone test is not only a number; it is a decision tool. The thrust curve helped identify safe operating regions and exposed where control authority could become fragile.",
                "The result made final testing more deliberate by connecting hardware selection to flight behavior.",
            ]),
        ],
        "table": [
            ["Propulsion uncertainty", "Measured thrust response", "Estimated flight margin before final tests", "Test design"],
            ["Payload requirement", "Compared expected lift to mission load", "Reduced guesswork in payload integration", "Mechanical-electrical integration"],
            ["Final run safety", "Used data to guide throttle and risk planning", "Supported more controlled final evaluation", "Evidence-based judgment"],
        ],
    },
    {
        "source": "drone-dynamic-testing-after-midterm.pdf",
        "output": "drone-dynamic-testing-after-midterm-english.pdf",
        "title": "Drone Dynamic Testing After Midterm - Reliability Notes",
        "project": "Quadcopter Ball-Transfer Drone",
        "course": "Practice of Mechanical Engineering",
        "type": "System test record",
        "role": "Team lead and flight-test debugger",
        "overview": [
            "This record summarizes dynamic testing after the midterm stage, when the project moved from basic assembly toward repeated flight behavior and mission execution.",
            "The major value of the work was diagnostic: drift, unstable response, crash risk, frame damage, and ball-transfer issues had to be separated into controllable causes rather than discussed as vague flight failure.",
        ],
        "signals": [
            "Converted test failures into subsystem-level hypotheses.",
            "Connected flight response to RC setup, deadband, control parameters, structure, and payload behavior.",
            "Used repeated testing to improve final reliability rather than waiting for a perfect build.",
        ],
        "sections": [
            ("Observed Problems", [
                "Dynamic flight introduced problems that were not visible during static build checks, including drift, unstable attitude response, transfer instability, and crash-related damage.",
                "These symptoms were treated as engineering information, not simply as failed attempts.",
            ]),
            ("Debugging Method", [
                "The team separated control input behavior, flight-controller settings, frame stiffness, payload placement, and operator procedure.",
                "Each test created a clearer next action: recalibrate, reinforce, revise geometry, change procedure, or reduce risk during final attempts.",
            ]),
        ],
        "table": [
            ["Drift and instability", "Checked control setup and neutral behavior", "Reduced hidden bias in flight commands", "Controls debugging"],
            ["Crash damage", "Reviewed structure and repair plan", "Kept the system testable after failures", "Hardware iteration"],
            ["Transfer reliability", "Adjusted procedure and payload interaction", "Protected mission success, not just flight", "System-level testing"],
        ],
    },
    {
        "source": "drone-flight-controller-motor-sbus-debugging.pdf",
        "output": "drone-flight-controller-motor-sbus-debugging-english.pdf",
        "title": "Drone Flight Controller, Motor Fault, and SBUS Debugging",
        "project": "Quadcopter Ball-Transfer Drone",
        "course": "Practice of Mechanical Engineering",
        "type": "Debugging note",
        "role": "Signal-chain and integration debugger",
        "overview": [
            "This note documents troubleshooting work around flight-controller setup, motor behavior, and SBUS signal communication. It captures the kind of integration work that decides whether a physical robot can be tested at all.",
            "The engineering challenge was to avoid guessing. A flight failure could come from wiring, channel mapping, controller configuration, motor output, calibration, signal protocol, or vibration. The work focused on isolating these causes systematically.",
        ],
        "signals": [
            "Worked through command path, receiver/SBUS behavior, flight-controller configuration, and motor response.",
            "Used step-by-step checks to identify whether faults belonged to hardware, communication, or configuration.",
            "Strengthened the final drone by making the electronics stack more understandable to the whole team.",
        ],
        "sections": [
            ("Debugging Strategy", [
                "Trace the signal path from controller input to receiver output, flight-controller interpretation, ESC command, and motor response.",
                "Verify one interface at a time so that later flight tests do not hide basic communication failures.",
            ]),
            ("System Impact", [
                "Signal-chain confidence allowed the team to focus final testing on flight behavior and mission strategy instead of repeatedly reopening basic electronics uncertainty.",
            ]),
        ],
        "table": [
            ["Motor response fault", "Checked power, controller output, and ESC/motor path", "Prevented blind tuning around a hardware issue", "Electrical debugging"],
            ["SBUS uncertainty", "Traced receiver and channel behavior", "Improved confidence in command input", "Communication protocols"],
            ["Flight-controller setup", "Verified configuration before flight tests", "Reduced final-test surprises", "Embedded integration"],
        ],
    },
    {
        "source": "drone-personal-journal-and-feedback.pdf",
        "output": "drone-personal-journal-and-feedback-english.pdf",
        "title": "Drone Project - Personal Journal and Team Feedback",
        "project": "Quadcopter Ball-Transfer Drone",
        "course": "Practice of Mechanical Engineering",
        "type": "Personal record",
        "role": "Team lead and system integrator",
        "overview": [
            "This personal record reflects the leadership and execution process behind the drone project. It emphasizes weekly progress, team coordination, design tradeoffs, and the pressure of turning a complex build into a working final system.",
            "For graduate review, the value of this document is not only the technical result. It shows that I can keep a team moving when requirements are ambiguous, failure modes overlap, and final evaluation pressure is real.",
        ],
        "signals": [
            "Coordinated mechanical, electrical, control, and testing tasks across the team.",
            "Helped translate weekly setbacks into concrete next actions.",
            "Balanced ambition with practical risk control near final evaluation.",
        ],
        "sections": [
            ("Leadership Evidence", [
                "The project required repeated communication between subteams because airframe changes affected payload behavior, electronics layout, and flight-test safety.",
                "Leadership meant making the system testable: deciding what to try next, what to repair first, and when to simplify.",
            ]),
            ("Reflection", [
                "This project strengthened my interest in robotics because it made clear that physical systems reward engineers who can connect design, control, testing, and people.",
            ]),
        ],
        "table": [
            ["Ambiguous failures", "Organized next tests and subsystem checks", "Kept progress from stalling", "Project leadership"],
            ["Limited time", "Prioritized final-run reliability", "Protected the strongest route to success", "Decision making"],
            ["Team coordination", "Connected mechanical and control discussions", "Improved shared understanding", "Technical communication"],
        ],
    },
    {
        "source": "drone-first-progress-report.pdf",
        "output": "drone-first-progress-report-english.pdf",
        "title": "Drone Project - First Progress Report",
        "project": "Quadcopter Ball-Transfer Drone",
        "course": "Practice of Mechanical Engineering",
        "type": "Progress report",
        "role": "Team lead and concept evaluator",
        "overview": [
            "The first progress stage focused on concept selection and early comparison across possible mission approaches. The team needed to identify a feasible path before committing to detailed fabrication.",
            "The core decision was to choose a design direction that could satisfy the ball-transfer mission while remaining stable, buildable, and adjustable enough for later testing.",
        ],
        "signals": [
            "Compared candidate architectures by stability, fabrication difficulty, control risk, and mission feasibility.",
            "Established the system-level framing that later made the drone a reference point for peers.",
            "Started from constraints instead of jumping directly into parts.",
        ],
        "sections": [
            ("Concept Evaluation", [
                "Early design work considered how the drone would hold, move, and release the ball while preserving flight stability.",
                "The concept phase helped the team identify which risks were mechanical, which were control-related, and which required testing.",
            ]),
            ("Next Steps", [
                "Move from concept comparison to prototype geometry, electronics planning, and testable propulsion assumptions.",
            ]),
        ],
        "table": [
            ["Mission ambiguity", "Compared several possible approaches", "Avoided premature commitment", "Concept design"],
            ["Flight stability", "Considered payload and frame together", "Protected future testability", "System thinking"],
            ["Team planning", "Defined next build questions", "Made progress measurable", "Technical leadership"],
        ],
    },
    {
        "source": "drone-second-progress-report.pdf",
        "output": "drone-second-progress-report-english.pdf",
        "title": "Drone Project - Second Progress Report",
        "project": "Quadcopter Ball-Transfer Drone",
        "course": "Practice of Mechanical Engineering",
        "type": "Progress report",
        "role": "Team lead and integration planner",
        "overview": [
            "The second progress stage moved the project from concept to early flight and ball-handling tests. The team began seeing how design assumptions changed once hardware was assembled.",
            "The report documents revision of the ball-handling concept and the shift from ideal design to integration reality.",
        ],
        "signals": [
            "Responded to early flight-test evidence rather than defending the first concept.",
            "Adjusted mechanical direction based on stability, payload behavior, and fabrication limits.",
            "Kept the team aligned as design choices became more constrained.",
        ],
        "sections": [
            ("Build-Test Revision", [
                "Early tests exposed the interaction between payload design and drone stability.",
                "The team revised the ball-handling approach to reduce integration risk and improve final feasibility.",
            ]),
            ("Engineering Learning", [
                "Physical testing made clear that lightweight design, control margin, and assembly quality had to be developed together.",
            ]),
        ],
        "table": [
            ["Early test mismatch", "Revised ball-handling approach", "Adapted to real build behavior", "Iterative design"],
            ["Payload stability", "Changed integration assumptions", "Reduced flight risk", "System debugging"],
            ["Schedule pressure", "Focused on feasible next prototypes", "Protected final progress", "Leadership"],
        ],
    },
    {
        "source": "drone-third-progress-report.pdf",
        "output": "drone-third-progress-report-english.pdf",
        "title": "Drone Project - Third Progress Report",
        "project": "Quadcopter Ball-Transfer Drone",
        "course": "Practice of Mechanical Engineering",
        "type": "Progress report",
        "role": "Team lead, test planner, and debugging coordinator",
        "overview": [
            "The third progress stage emphasized hardware iteration, thrust experiment interpretation, remote-control packet debugging, and final strategy development.",
            "At this point, the project shifted from making a drone that could be assembled to making a system that could be trusted in the final evaluation.",
        ],
        "signals": [
            "Linked propulsion data to mechanical and control decisions.",
            "Worked through remote-control packet and signal-chain uncertainty.",
            "Converted late-stage issues into a final strategy instead of scattered repairs.",
        ],
        "sections": [
            ("Late-Stage Integration", [
                "The team used testing to determine which parts of the system needed redesign, reinforcement, recalibration, or procedure changes.",
                "This stage strengthened the connection between experimental data and final mission planning.",
            ]),
            ("Final Strategy", [
                "The strongest path was to simplify risk, verify core behaviors, prepare spares, and make the final attempt predictable.",
            ]),
        ],
        "table": [
            ["Propulsion margin", "Used thrust experiment results", "Guided final design confidence", "Experimental reasoning"],
            ["Remote control uncertainty", "Debugged command and packet behavior", "Improved control reliability", "Embedded communication"],
            ["Final attempt pressure", "Developed practical final strategy", "Reduced unnecessary risk", "Execution leadership"],
        ],
    },
    {
        "source": "drone-fourth-progress-report.pdf",
        "output": "drone-fourth-progress-report-english.pdf",
        "title": "Drone Project - Fourth Progress Report",
        "project": "Quadcopter Ball-Transfer Drone",
        "course": "Practice of Mechanical Engineering",
        "type": "Progress report",
        "role": "Team lead and final-integration coordinator",
        "overview": [
            "The fourth progress stage focused on late design comparison, three-ball carrier updates, final strategy, and future improvement planning.",
            "The report captures the point where the team had to decide which improvements truly increased final reliability and which changes would create new risk.",
        ],
        "signals": [
            "Balanced additional mechanism capability with flight and schedule risk.",
            "Compared late-stage design options using final-test reliability as the main criterion.",
            "Prepared improvement directions without compromising near-term execution.",
        ],
        "sections": [
            ("Final Design Decisions", [
                "Late-stage drone work required restraint. Not every improvement was worth integrating if it reduced test time or increased uncertainty.",
                "The team prioritized a final configuration that could be tested, repaired, and executed under evaluation conditions.",
            ]),
            ("Future Improvement Plan", [
                "Potential improvements included cleaner payload packaging, stronger structural damping, more robust electronics layout, and more systematic test data collection.",
            ]),
        ],
        "table": [
            ["Three-ball carrier ambition", "Evaluated capability against reliability", "Kept mission success central", "Design judgment"],
            ["Limited test time", "Prioritized validated configuration", "Avoided late risky changes", "Risk control"],
            ["Future improvements", "Separated next-version ideas from final build", "Protected final evaluation", "Engineering planning"],
        ],
    },
    {
        "source": "drone-first-project-worksheet.pdf",
        "output": "drone-first-project-worksheet-english.pdf",
        "title": "Drone Project - First Engineering Worksheet",
        "project": "Quadcopter Ball-Transfer Drone",
        "course": "Practice of Mechanical Engineering",
        "type": "Worksheet",
        "role": "Team lead and concept contributor",
        "overview": [
            "This worksheet supported early requirement definition, concept comparison, and team planning for the ball-transfer drone project.",
            "It is included as process evidence showing that the final system was developed through structured engineering checkpoints rather than a single late build attempt.",
        ],
        "signals": [
            "Defined early mission requirements and design questions.",
            "Compared feasible build directions before detailed fabrication.",
            "Established a shared language for later subsystem work.",
        ],
        "sections": [
            ("Worksheet Function", [
                "Record early assumptions, candidate approaches, expected risks, and next tasks.",
                "Translate a broad course challenge into specific engineering decisions for the team.",
            ]),
        ],
        "table": [
            ["Open-ended mission", "Outlined requirements and constraints", "Made design work concrete", "Requirements analysis"],
            ["Multiple concepts", "Compared early paths", "Prepared better prototype choices", "Concept selection"],
            ["Team coordination", "Recorded next actions", "Kept work aligned", "Project management"],
        ],
    },
    {
        "source": "drone-second-project-worksheet.pdf",
        "output": "drone-second-project-worksheet-english.pdf",
        "title": "Drone Project - Second Engineering Worksheet",
        "project": "Quadcopter Ball-Transfer Drone",
        "course": "Practice of Mechanical Engineering",
        "type": "Worksheet",
        "role": "Team lead and integration contributor",
        "overview": [
            "This worksheet documented intermediate planning as the drone moved toward physical integration. It supported decisions about test priorities, subsystem risk, and next prototype changes.",
            "The key value was converting early build experience into a practical path for later validation.",
        ],
        "signals": [
            "Tracked integration risks across airframe, payload, electronics, and testing.",
            "Used worksheet checkpoints to keep the team from losing system-level priorities.",
            "Prepared the transition from concept work to evidence-driven iteration.",
        ],
        "sections": [
            ("Worksheet Function", [
                "Clarify what had been tested, what remained uncertain, and what the next build cycle needed to answer.",
            ]),
        ],
        "table": [
            ["Prototype uncertainty", "Recorded test priorities", "Made the next build cycle measurable", "Engineering planning"],
            ["Subsystem interaction", "Tracked airframe and payload risks", "Reduced late integration conflict", "System integration"],
            ["Team execution", "Clarified responsibility and next tasks", "Supported steady progress", "Leadership"],
        ],
    },
    {
        "source": "drone-third-project-worksheet.pdf",
        "output": "drone-third-project-worksheet-english.pdf",
        "title": "Drone Project - Third Engineering Worksheet",
        "project": "Quadcopter Ball-Transfer Drone",
        "course": "Practice of Mechanical Engineering",
        "type": "Worksheet",
        "role": "Team lead and test contributor",
        "overview": [
            "This worksheet supported late-stage test planning, propulsion interpretation, and electronics/debugging follow-up.",
            "It provides process evidence for how the team moved from observed failures toward specific integration decisions.",
        ],
        "signals": [
            "Connected propulsion testing with final design choices.",
            "Recorded troubleshooting priorities as the electronics and control stack became more important.",
            "Helped turn test results into final strategy.",
        ],
        "sections": [
            ("Worksheet Function", [
                "Organize late-stage uncertainties into solvable tasks: propulsion margin, control communication, payload reliability, and final-test procedure.",
            ]),
        ],
        "table": [
            ["Late test data", "Organized interpretation and action items", "Reduced vague debugging", "Test analysis"],
            ["Control stack risk", "Tracked signal/debugging tasks", "Improved final reliability", "Embedded systems"],
            ["Final strategy", "Connected data to execution planning", "Prepared evaluation performance", "System leadership"],
        ],
    },
    {
        "source": "drone-fourth-project-worksheet.pdf",
        "output": "drone-fourth-project-worksheet-english.pdf",
        "title": "Drone Project - Fourth Engineering Worksheet",
        "project": "Quadcopter Ball-Transfer Drone",
        "course": "Practice of Mechanical Engineering",
        "type": "Worksheet",
        "role": "Team lead and final execution planner",
        "overview": [
            "This worksheet organized final-stage priorities for the drone project, including final configuration decisions, testing readiness, and improvement planning.",
            "It is useful as evidence of disciplined project closure: what to finish, what to test, what to simplify, and what to leave for a future version.",
        ],
        "signals": [
            "Separated final-evaluation needs from future-version ideas.",
            "Focused the team on validated, executable design choices.",
            "Documented final readiness and remaining risks.",
        ],
        "sections": [
            ("Worksheet Function", [
                "Turn late-stage project uncertainty into a clear final preparation checklist and future improvement record.",
            ]),
        ],
        "table": [
            ["Final readiness", "Prioritized validated design choices", "Protected evaluation performance", "Risk management"],
            ["Future improvements", "Recorded next-version ideas", "Avoided destabilizing final build", "Engineering judgment"],
            ["Team closure", "Clarified final tasks", "Improved execution under pressure", "Leadership"],
        ],
    },
    {
        "source": "robot-dog-final-report.pdf",
        "output": "robot-dog-final-report-english.pdf",
        "title": "Self-Built Simple Quadruped Robot Dog - Final Report",
        "project": "Self-Built Simple Quadruped Robot Dog",
        "course": "Microprocessor Controlled Systems",
        "type": "Final report",
        "role": "Team lead, mechanical designer, and controls developer",
        "overview": [
            "This project built an eight-servo quadruped robot dog using a 3D-printed structure, ESP32 controller, PCA9685 servo driver, MATLAB gait reasoning, and Arduino implementation.",
            "The main engineering value was system integration. The robot had to be mechanically serviceable, electrically reliable, and controllable enough to demonstrate multiple behaviors.",
            "The final robot completed forward walking, standing, sitting, waving, hip lift, and rocking behaviors, earning a course grade of A+.",
        ],
        "signals": [
            "Designed a repairable 3D-printed body around servo replacement, wire routing, battery placement, and center-of-gravity constraints.",
            "Connected MATLAB gait simulation and inverse-kinematics reasoning to embedded servo output.",
            "Calibrated servo direction, neutral angle, mechanical offsets, and gait timing through repeated testing.",
            "Led the team through failures that crossed mechanics, electronics, software, and assembly.",
        ],
        "sections": [
            ("Mechanical Architecture", [
                "The body was designed as a working robot platform rather than a display model. Repair access, repeated testing, battery placement, and wire routing were part of the structure.",
                "The design supported continuous iteration because servos and electronics could be accessed during debugging.",
            ]),
            ("Control Implementation", [
                "MATLAB was used to reason about gait trajectories and reachable workspace before translating the logic into Arduino code.",
                "The ESP32 and PCA9685 controlled eight MG90S servos. Real behavior required calibration of direction, neutral angle, offsets, and update timing.",
            ]),
            ("Validation", [
                "The final demonstration showed multiple behaviors on one platform, proving that the mechanical geometry and embedded control software worked together.",
            ]),
        ],
        "table": [
            ["Compact eight-servo body", "Designed a serviceable 3D-printed structure", "Made repair and calibration possible", "Mechanical packaging"],
            ["Simulation-hardware mismatch", "Calibrated servo direction and offsets", "Reduced model-to-robot mismatch", "System debugging"],
            ["Multiple behaviors", "Separated gait update, IK, and servo output", "Made behavior tuning easier", "Embedded control"],
            ["Team integration", "Coordinated hardware and software fixes", "Kept testing moving through failures", "Leadership"],
        ],
    },
    {
        "source": "robot-dog-final-presentation.pdf",
        "output": "robot-dog-final-presentation-english.pdf",
        "title": "Self-Built Simple Quadruped Robot Dog - Final Presentation",
        "project": "Self-Built Simple Quadruped Robot Dog",
        "course": "Microprocessor Controlled Systems",
        "type": "Final presentation deck",
        "role": "Team lead, presenter, and integration contributor",
        "overview": [
            "This English presentation version summarizes the final robot dog build, including structure, electronics, gait logic, mechanical updates, and behavior demonstrations.",
            "The presentation evidence shows a complete small-scale legged robot workflow: design, fabricate, wire, simulate, program, calibrate, repair, and demonstrate.",
        ],
        "signals": [
            "Explained the project as an integrated robot system, not separate slides of CAD and code.",
            "Connected behavior demonstrations to the mechanical and embedded decisions behind them.",
            "Presented technical progress in a form that reviewers can scan quickly.",
        ],
        "sections": [
            ("Presentation Narrative", [
                "The project begins with the requirement to create an interactive quadruped robot and moves through body design, servo selection, control logic, and testing.",
                "Final behaviors demonstrate that the platform could execute more than one scripted motion after calibration.",
            ]),
            ("Reviewer Focus", [
                "Look for cross-domain execution: 3D-printed structure, electronics layout, MATLAB reasoning, ESP32/PCA9685 control, and repeated hardware debugging.",
            ]),
        ],
        "table": [
            ["Audience needs", "Condensed technical workflow into presentation form", "Made engineering decisions easy to review", "Technical communication"],
            ["Demonstration focus", "Linked behaviors to underlying control", "Showed system-level execution", "Robotics integration"],
            ["Final result", "Presented multiple working behaviors", "Supported A+ course outcome", "Execution quality"],
        ],
    },
    {
        "source": "robot-dog-midterm-report.pdf",
        "output": "robot-dog-midterm-report-english.pdf",
        "title": "Self-Built Simple Quadruped Robot Dog - Midterm Progress Report",
        "project": "Self-Built Simple Quadruped Robot Dog",
        "course": "Microprocessor Controlled Systems",
        "type": "Midterm progress report",
        "role": "Team lead, mechanical designer, and controls developer",
        "overview": [
            "The midterm stage documented early kinematics work, hardware planning, circuit layout, and next-step development for the robot dog.",
            "The value of this report is process evidence: the team moved from concept and simulation toward a physical platform that could later support real demonstrations.",
        ],
        "signals": [
            "Used early MATLAB kinematics to guide real servo and linkage decisions.",
            "Planned electronics around ESP32, PCA9685, servos, and power delivery.",
            "Identified integration issues before the final demonstration stage.",
        ],
        "sections": [
            ("Midterm Engineering State", [
                "The project was still transitioning from planned geometry to reliable physical motion.",
                "Key work included gait reasoning, structure iteration, circuit planning, and preparing for calibration.",
            ]),
            ("Next Development Goals", [
                "Complete body assembly, validate servo directions and offsets, improve power layout, and convert gait logic into embedded behavior.",
            ]),
        ],
        "table": [
            ["Early gait concept", "Used MATLAB reasoning", "Prepared IK and reachable workspace checks", "Kinematics"],
            ["Electronics planning", "Mapped controller, driver, and servo layout", "Reduced final wiring confusion", "Embedded design"],
            ["Final demo preparation", "Identified calibration and assembly tasks", "Made remaining work actionable", "Project leadership"],
        ],
    },
    {
        "source": "foldable-mechanism-final-report.pdf",
        "output": "foldable-mechanism-final-report-english.pdf",
        "title": "Foldable Long-Distance Ball Transfer Mechanism - Final Report",
        "project": "Foldable Long-Distance Ball Transfer Mechanism",
        "course": "Machine Design Theory",
        "type": "Final machine design report",
        "role": "Team lead, concept designer, and fabrication planner",
        "overview": [
            "This project designed a deployable ball-transfer mechanism under strict packaging and reliability constraints. The mechanism had to move from compact storage to working configuration and transfer a ball across distance.",
            "The final design used fabrication-aware choices such as 3D-printed parts, MDF structure, hinges, and latch hardware to improve deployment repeatability, locked-state stiffness, and repair speed.",
            "The final mechanism performed reliably during evaluation and strengthened my ability to connect mechanism architecture with fabrication, assembly order, and test behavior.",
        ],
        "signals": [
            "Treated packaging as the central engineering problem rather than a late detail.",
            "Balanced ideal motion paths with buildable mechanics and available fabrication methods.",
            "Used accessible hardware to improve reliability and iteration speed.",
            "Led concept selection, folding architecture, fabrication planning, and final refinement.",
        ],
        "sections": [
            ("Mechanism Architecture", [
                "The mechanism needed to satisfy storage constraints, deployment motion, stiffness, ball-transfer path, and repair access simultaneously.",
                "This shifted the project from simply making a transfer path to designing a compact machine that could repeatedly move between storage and operation.",
            ]),
            ("Fabrication Strategy", [
                "Early folding concepts were simplified and adapted to the tools and hardware available.",
                "Hinges, latch hardware, MDF, and 3D-printed parts were chosen to create a more predictable motion path and locked state.",
            ]),
            ("Validation", [
                "Final testing emphasized repeatable deployment and practical reliability rather than unnecessary complexity.",
            ]),
        ],
        "table": [
            ["Strict storage envelope", "Made folding architecture central", "Prevented a working path from becoming impossible to package", "Design for constraints"],
            ["Repeatable deployment", "Used hinge and latch hardware", "Improved motion predictability and locked stiffness", "Mechanism design"],
            ["Fabrication limits", "Used accessible materials and repair-friendly assembly", "Made iteration faster", "Fabrication-aware design"],
            ["Final reliability", "Prioritized stable execution over complexity", "Improved final-test performance", "Engineering judgment"],
        ],
    },
    {
        "source": "foldable-mechanism-midterm-report.pdf",
        "output": "foldable-mechanism-midterm-report-english.pdf",
        "title": "Foldable Long-Distance Ball Transfer Mechanism - Midterm Design Presentation",
        "project": "Foldable Long-Distance Ball Transfer Mechanism",
        "course": "Machine Design Theory",
        "type": "Midterm design presentation",
        "role": "Team lead and concept designer",
        "overview": [
            "The midterm presentation documented concept-stage work for the foldable mechanism, including container design, polar-positioning arm logic, packaging constraints, and early architecture decisions.",
            "The key contribution was identifying that packaging and deployment reliability would dominate the final design. This helped the team avoid building a mechanism that worked in theory but could not fit, lock, or survive testing.",
        ],
        "signals": [
            "Defined packaging constraints as primary design inputs.",
            "Compared early architecture options around motion, size, stiffness, and fabrication.",
            "Prepared the project for later simplification and reliable hardware choices.",
        ],
        "sections": [
            ("Concept Direction", [
                "The project explored how a ball-transfer mechanism could be stored compactly while still deploying into a useful working geometry.",
                "Early work considered container layout, polar-positioning arm behavior, and the mechanical consequences of strict size limits.",
            ]),
            ("Path to Final Design", [
                "The midterm stage made clear that the final mechanism would need simpler hardware, predictable deployment, and careful assembly planning.",
            ]),
        ],
        "table": [
            ["Packaging constraint", "Centered design around storage envelope", "Made the main risk visible early", "Requirement analysis"],
            ["Motion concept", "Evaluated polar-positioning arm logic", "Connected geometry to mechanism function", "Mechanism synthesis"],
            ["Buildability", "Prepared for accessible materials and hardware", "Improved later final reliability", "Fabrication planning"],
        ],
    },
]


def build_report(report):
    output = DOCS / report["output"]
    source = report["source"]
    pages = source_pages(source)

    doc = BaseDocTemplate(
        str(output),
        pagesize=LETTER,
        leftMargin=0.72 * inch,
        rightMargin=0.72 * inch,
        topMargin=0.72 * inch,
        bottomMargin=0.75 * inch,
        title=report["title"],
        author="CHENG-HSUAN LEE",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    template = PageTemplate(id="main", frames=[frame], onPage=page_footer)
    doc.addPageTemplates([template])

    story = []
    story.append(p("ENGLISH PROJECT REPORT VERSION", "SmallCaps"))
    story.append(Paragraph(clean(report["title"]), STYLES["ReportTitle"]))
    story.append(p(COMMON_REVIEW_NOTE, "Deck"))
    story.append(
        meta_table(
            [
                ("Applicant", "CHENG-HSUAN LEE"),
                ("Project", report["project"]),
                ("Course", report["course"]),
                ("Document Type", report["type"]),
                ("Primary Role", report["role"]),
                ("Original Source", f"{source} ({pages} pages)"),
            ]
        )
    )
    story.append(Spacer(1, 10))

    story.append(p("Executive Summary", "Section"))
    for para in report["overview"]:
        story.append(p(para))

    story.append(p("Applicant Contribution Signals", "Section"))
    story.extend(bullets(report["signals"]))

    for title, items in report["sections"]:
        story.append(p(title, "Section"))
        for item in items:
            story.append(p(item))

    story.append(p("Technical Decision Table", "Section"))
    story.append(
        decision_table(
            ["Constraint", "Decision", "Why It Mattered", "Skill Demonstrated"],
            report["table"],
        )
    )

    story.append(Spacer(1, 10))
    story.append(p("How to Read This Evidence", "Section"))
    story.append(
        p(
            "This document is intended to help a reviewer quickly understand the engineering content of the original report in English. The original PDF remains available in the project archive as the source artifact with its original figures, tables, screenshots, and course formatting."
        )
    )

    doc.build(story)
    return output


def main():
    outputs = []
    for report in REPORTS:
        outputs.append(build_report(report))
    for path in outputs:
        print(path.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
