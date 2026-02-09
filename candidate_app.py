import streamlit as st
import pandas as pd
import requests
import time
import random
from datetime import date, datetime
import os

# ---------------- CONFIG ----------------
BRIDGE_URL = "https://script.google.com/macros/s/AKfycbzCICknuaFGUOqwPX_kMnTy_1FtA4ppm44ZAft56-Y21_4xCidrjvTkM6gwcuZW_4so/exec"
ADMIN_MASTER_KEY = "Medanta@2026"

TOTAL_QUESTIONS = 25
TECH_Q_COUNT = 18
BEHAV_Q_COUNT = 7
PASS_PERCENT = 60
TOTAL_TEST_TIME = 25 * 60  # seconds

st.set_page_config(page_title="Medanta Staff Assessment", layout="centered")

# ---------------- SESSION INIT ----------------
if "started" not in st.session_state:
    st.session_state.started = False
    st.session_state.review_mode = False
    st.session_state.q_index = 0
    st.session_state.answers = {}
    st.session_state.candidate_data = {}
    st.session_state.level = "beginner"
    st.session_state.start_time = None
    st.session_state.questions_df = None
    st.session_state.admin_unlocked = False

# ---------------- STYLE ----------------
st.markdown("""
<style>
.stApp {
    background-image: linear-gradient(rgba(255,255,255,0.94), rgba(255,255,255,0.94)),
                      url("https://www.transparenttextures.com/patterns/medical-icons.png");
    background-attachment: fixed;
    background-size: cover;
}
</style>
""", unsafe_allow_html=True)

# ---------------- IMPROVEMENT TIPS ----------------
IMPROVEMENT_TIPS = [
    "Focus on medication safety and the 5 Rights.",
    "Revise hand hygiene – the 5 Moments are critical.",
    "Review emergency codes and response protocols.",
    "Strengthen documentation accuracy and timeliness.",
    "Improve patient communication using ISBAR.",
    "Revisit infection control and PPE usage.",
    "Ensure patient privacy in public areas.",
    "Practice fall prevention and patient mobility safety.",
    "Relearn biomedical waste segregation.",
    "Focus on teamwork and escalation pathways.",
    "Revise JCI International Patient Safety Goals."
]

# ---------------- 50 BEHAVIORAL QUESTIONS ----------------
BEHAVIORAL_BANK = [
    {"question": "How do you handle a patient who refuses treatment?", "Option A": "Respect and document", "Option B": "Explain risks and notify doctor", "Option C": "Force it", "Option D": "Ignore", "Correct Answer": "Explain risks and notify doctor"},
    {"question": "Notice a colleague skipping hand hygiene?", "Option A": "Ignore it", "Option B": "Politely remind them", "Option C": "Report to HR", "Option D": "Do the same", "Correct Answer": "Politely remind them"},
    {"question": "Family asks about another patient?", "Option A": "Tell them", "Option B": "Protect privacy", "Option C": "Share limited info", "Option D": "Ignore", "Correct Answer": "Protect privacy"},
    {"question": "Minor medication error with no harm?", "Option A": "Hide it", "Option B": "Report immediately", "Option C": "Wait", "Option D": "Tell patient only", "Correct Answer": "Report immediately"},
    {"question": "Angry patient due to waiting?", "Option A": "Argue", "Option B": "Listen and empathize", "Option C": "Ignore", "Option D": "Ask to leave", "Correct Answer": "Listen and empathize"},
    {"question": "Emergency alarm in another area?", "Option A": "Ignore", "Option B": "Follow protocol", "Option C": "Run immediately", "Option D": "Panic", "Correct Answer": "Follow protocol"},
    {"question": "Unclear verbal order?", "Option A": "Follow anyway", "Option B": "Seek clarification", "Option C": "Ask nurse", "Option D": "Ignore", "Correct Answer": "Seek clarification"},
    {"question": "Spill in corridor?", "Option A": "Walk away", "Option B": "Mark/Clean immediately", "Option C": "Tell later", "Option D": "Ignore", "Correct Answer": "Mark/Clean immediately"},
    {"question": "Patient fall during ambulation?", "Option A": "Lift fast", "Option B": "Ease down & call help", "Option C": "Leave", "Option D": "Ignore", "Correct Answer": "Ease down & call help"},
    {"question": "Conflicting instructions?", "Option A": "Pick one", "Option B": "Clarify", "Option C": "Ignore", "Option D": "Complain", "Correct Answer": "Clarify"},
    {"question": "Primary goal of JCI?", "Option A": "Profit", "Option B": "Patient safety", "Option C": "Fame", "Option D": "Staff reduction", "Correct Answer": "Patient safety"},
    {"question": "Correct patient identification?", "Option A": "Room number", "Option B": "Name + DOB", "Option C": "Diagnosis", "Option D": "Guess", "Correct Answer": "Name + DOB"},
    {"question": "Hand hygiene timing?", "Option A": "After only", "Option B": "Before & after", "Option C": "Hourly", "Option D": "When dirty", "Correct Answer": "Before & after"},
    {"question": "Colleague bullied?", "Option A": "Ignore", "Option B": "Support & report", "Option C": "Join", "Option D": "Blame", "Correct Answer": "Support & report"},
    {"question": "Vitals slightly abnormal?", "Option A": "Ignore", "Option B": "Recheck & report", "Option C": "Wait", "Option D": "Hide", "Correct Answer": "Recheck & report"},
    {"question": "Sharps container full?", "Option A": "Push down", "Option B": "Replace", "Option C": "Leave", "Option D": "Shake", "Correct Answer": "Replace"},
    {"question": "Professionalism means?", "Option A": "Late", "Option B": "Punctual & respectful", "Option C": "Gossip", "Option D": "Ignore rules", "Correct Answer": "Punctual & respectful"},
    {"question": "Patient privacy in lifts?", "Option A": "Allowed", "Option B": "Prohibited", "Option C": "Sometimes", "Option D": "Only staff", "Correct Answer": "Prohibited"},
    {"question": "Standard precautions apply to?", "Option A": "HIV only", "Option B": "All patients", "Option C": "ICU", "Option D": "Surgery", "Correct Answer": "All patients"},
    {"question": "Correct PPE usage?", "Option A": "Reuse gloves", "Option B": "Discard after use", "Option C": "Wash gloves", "Option D": "Reuse mask", "Correct Answer": "Discard after use"},
    {"question": "Pressure ulcer prevention?", "Option A": "Turn 8 hrs", "Option B": "Turn 2 hrs", "Option C": "No movement", "Option D": "One pillow", "Correct Answer": "Turn 2 hrs"},
    {"question": "Time out before surgery?", "Option A": "Break", "Option B": "Verify patient/site", "Option C": "Clean", "Option D": "Count tools", "Correct Answer": "Verify patient/site"},
    {"question": "Patient wants record access?", "Option A": "Refuse", "Option B": "Follow policy", "Option C": "Hand over", "Option D": "Lie", "Correct Answer": "Follow policy"},
    {"question": "Lost visitor?", "Option A": "Ignore", "Option B": "Help", "Option C": "Point", "Option D": "Walk away", "Correct Answer": "Help"},
    {"question": "Handwash duration?", "Option A": "5 sec", "Option B": "20 sec", "Option C": "1 min", "Option D": "10 sec", "Correct Answer": "20 sec"},
    {"question": "NPO patient asks water?", "Option A": "Give sip", "Option B": "Explain NPO", "Option C": "Give glass", "Option D": "Ignore", "Correct Answer": "Explain NPO"},
    {"question": "Code Blue?", "Option A": "Fire", "Option B": "Cardiac arrest", "Option C": "Bomb", "Option D": "Infant abduction", "Correct Answer": "Cardiac arrest"},
    {"question": "Documentation should be?", "Option A": "Late", "Option B": "Accurate & timely", "Option C": "Vague", "Option D": "Pencil", "Correct Answer": "Accurate & timely"},
    {"question": "Call bell ringing?", "Option A": "Wait", "Option B": "Respond immediately", "Option C": "Unplug", "Option D": "Ignore", "Correct Answer": "Respond immediately"},
    {"question": "Proper lifting?", "Option A": "Bend waist", "Option B": "Use legs", "Option C": "Twist", "Option D": "Stretch arms", "Correct Answer": "Use legs"},
    {"question": "Hard of hearing patient?", "Option A": "Shout", "Option B": "Face & speak clearly", "Option C": "Avoid", "Option D": "Family only", "Correct Answer": "Face & speak clearly"},
    {"question": "Donning PPE means?", "Option A": "Remove", "Option B": "Put on", "Option C": "Clean", "Option D": "Wash hands", "Correct Answer": "Put on"},
    {"question": "Yellow BMW bag?", "Option A": "General", "Option B": "Infectious", "Option C": "Glass", "Option D": "Paper", "Correct Answer": "Infectious"},
    {"question": "Discharge role?", "Option A": "Wheel out", "Option B": "Verify instructions", "Option C": "Say bye", "Option D": "Ignore", "Correct Answer": "Verify instructions"},
    {"question": "Telephone orders?", "Option A": "Ignore", "Option B": "Read back", "Option C": "Later", "Option D": "Avoid", "Correct Answer": "Read back"},
    {"question": "Patient dizzy?", "Option A": "Walk", "Option B": "Assist to sit", "Option C": "Leave", "Option D": "Ignore", "Correct Answer": "Assist to sit"},
    {"question": "5 Rights include?", "Option A": "Right patient", "Option B": "Right price", "Option C": "Right hospital", "Option D": "Right building", "Correct Answer": "Right patient"},
    {"question": "Late for duty?", "Option A": "Sneak", "Option B": "Inform supervisor", "Option C": "Lie", "Option D": "Ignore", "Correct Answer": "Inform supervisor"},
    {"question": "Suicidal patient?", "Option A": "Leave", "Option B": "Constant observation", "Option C": "Privacy", "Option D": "Ignore", "Correct Answer": "Constant observation"},
    {"question": "Teamwork requires?", "Option A": "Silence", "Option B": "Clear communication", "Option C": "Competition", "Option D": "Secrets", "Correct Answer": "Clear communication"},
    {"question": "IV site red?", "Option A": "Ignore", "Option B": "Stop & report", "Option C": "Increase rate", "Option D": "Cover", "Correct Answer": "Stop & report"},
    {"question": "Main infection source?", "Option A": "Air", "Option B": "Hands", "Option C": "Food", "Option D": "Visitors", "Correct Answer": "Hands"},
    {"question": "Unconscious patient consent?", "Option A": "Wait family", "Option B": "Implied consent", "Option C": "Do nothing", "Option D": "Ask staff", "Correct Answer": "Implied consent"},
    {"question": "ID badge?", "Option A": "Pocket", "Option B": "Visible", "Option C": "Car", "Option D": "Home", "Correct Answer": "Visible"},
    {"question": "Complaint about doctor?", "Option A": "Agree", "Option B": "Escalate properly", "Option C": "Defend", "Option D": "Ignore", "Correct Answer": "Escalate properly"},
    {"question": "Cultural competence?", "Option A": "Ignore culture", "Option B": "Respect all", "Option C": "Stereotype", "Option D": "Avoid", "Correct Answer": "Respect all"}
]

# ---------------- SIDEBAR ADMIN ----------------
with st.sidebar:
    st.subheader("⚙️ Admin")

    unlock = st.checkbox("Unlock Level Settings")

    if unlock and not st.session_state.admin_unlocked:
        key = st.text_input("Master Key", type="password")
        if key == ADMIN_MASTER_KEY:
            st.session_state.admin_unlocked = True
            st.success("Admin unlocked")

    if st.session_state.admin_unlocked and not st.session_state.started:
        st.session_state.level = st.selectbox(
            "Assign Test Level",
            ["beginner", "intermediate", "advanced"],
            index=["beginner", "intermediate", "advanced"].index(st.session_state.level)
        )

    st.divider()
    st.info(f"Difficulty: **{st.session_state.level.upper()}**")

# ---------------- SCREEN 1 ----------------
if not st.session_state.started:
    st.title("🏥 Medanta Staff Assessment")
    st.subheader("Staff Information")

    name = st.text_input("Full Name")
    dob = st.date_input("Date of Birth", min_value=date(1960, 1, 1))
    qual = st.text_input("Qualification")
    cat = st.selectbox("Staff Category", ["Nursing", "Non-Nursing"])
    reg = st.text_input("Registration Number") if cat == "Nursing" else "N/A"
    college = st.text_input("College Name")
    contact = st.text_input("Contact Number (10 digits)")

    if st.button("Start Assessment", type="primary"):
        if name and contact.isdigit() and len(contact) == 10:
            if not os.path.exists("questions.xlsx"):
                st.error("questions.xlsx file not found.")
                st.stop()

            df_xl = pd.read_excel("questions.xlsx")
            required = {"question", "Option A", "Option B", "Option C", "Option D", "Correct Answer", "level"}
            if not required.issubset(df_xl.columns):
                st.error("Invalid question file format.")
                st.stop()

            tech = df_xl[df_xl["level"].str.lower() == st.session_state.level].sample(TECH_Q_COUNT)
            behav = pd.DataFrame(random.sample(BEHAVIORAL_BANK, BEHAV_Q_COUNT))
            st.session_state.questions_df = pd.concat([tech, behav]).sample(frac=1).reset_index(drop=True)

            st.session_state.candidate_data = {
                "name": name,
                "dob": str(dob),
                "qualification": qual,
                "category": cat,
                "reg_no": reg,
                "college": college,
                "contact": contact
            }

            if st.session_state.start_time is None:
                st.session_state.start_time = time.time()

            st.session_state.started = True
            st.rerun()
        else:
            st.warning("Please enter valid details.")

# ---------------- SCREEN 2 ----------------
else:
    elapsed = time.time() - st.session_state.start_time
    remaining = max(0, TOTAL_TEST_TIME - elapsed)

    st.sidebar.metric("⏳ Time Left", f"{int(remaining//60)}m {int(remaining%60)}s")

    if remaining <= 0:
        st.session_state.review_mode = True

    df = st.session_state.questions_df

    # REVIEW MODE
    if st.session_state.review_mode:
        st.title("📝 Review & Submit")
        cols = st.columns(5)
        for i in range(TOTAL_QUESTIONS):
            mark = "✅" if f"Q{i+1}" in st.session_state.answers else "⚪"
            if cols[i % 5].button(f"{mark} Q{i+1}"):
                st.session_state.q_index = i
                st.session_state.review_mode = False
                st.rerun()

        if st.button("Final Submit", type="primary", use_container_width=True):
            correct = 0
            for i, row in df.iterrows():
                if st.session_state.answers.get(f"Q{i+1}") == row["Correct Answer"]:
                    correct += 1

            score = round((correct / TOTAL_QUESTIONS) * 100, 2)
            duration = round(elapsed / 60, 2)

            payload = {**st.session_state.candidate_data,
                       "score_percent": score,
                       "duration_minutes": duration}

            requests.post(BRIDGE_URL, json=payload)

            if score >= PASS_PERCENT:
                st.balloons()
                st.success(f"PASS – Score: {score}%")
            else:
                tip = random.choice(IMPROVEMENT_TIPS)
                st.error(f"NOT CLEARED – Score: {score}%")
                st.warning(f"Improvement Guidance: {tip}")

            st.session_state.started = False

    # QUESTION VIEW
    else:
        idx = st.session_state.q_index
        row = df.iloc[idx]

        st.subheader(f"Question {idx+1} of {TOTAL_QUESTIONS}")
        st.write(row["question"])

        options = [row["Option A"], row["Option B"], row["Option C"], row["Option D"]]
        prev = st.session_state.answers.get(f"Q{idx+1}")

        choice = st.radio(
            "Select an option:",
            options,
            index=options.index(prev) if prev in options else None,
            key=f"q_{idx}"
        )

        if choice:
            st.session_state.answers[f"Q{idx+1}"] = choice

        c1, c2, c3 = st.columns([1, 1, 2])
        if idx > 0 and c1.button("⬅ Previous"):
            st.session_state.q_index -= 1
            st.rerun()
        if idx < TOTAL_QUESTIONS - 1 and c2.button("Next ➡"):
            st.session_state.q_index += 1
            st.rerun()
        if c3.button("Review All"):
            st.session_state.review_mode = True
            st.rerun()
