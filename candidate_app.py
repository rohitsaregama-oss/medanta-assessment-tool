import streamlit as st
import pandas as pd
import requests
import time
import random
from datetime import date
import os

# ================= SAFE SECRET LOAD =================
try:
    ADMIN_MASTER_KEY = st.secrets["ADMIN_MASTER_KEY"]
except:
    ADMIN_MASTER_KEY = None

# ================= CONFIG =================
BRIDGE_URL = "https://script.google.com/macros/s/AKfycbw2Phahbp2SqwL_3UsQBiMIZDpWe-gXY1gS3jjvaDBCpOMhxSLWzjhhB-V57AIFsX3g/exec"

TOTAL_QUESTIONS = 25
TECH_Q_COUNT = 18
BEHAV_Q_COUNT = 7
PASS_PERCENT = 60

GLOBAL_TEST_TIME = 25 * 60
DEFAULT_Q_TIME = 45
REDUCED_Q_TIME = 25
REVIEW_TIME_LIMIT = 120  # seconds

st.set_page_config(page_title="Medanta Staff Assessment", layout="centered")

# ================= SESSION INIT =================
if "started" not in st.session_state:
    st.session_state.update({
        "started": False,
        "q_index": 0,
        "answers": {},
        "candidate_data": {},
        "questions": [],
        "level": "beginner",
        "start_time": None,
        "question_start_time": None,
        "fishy_counter": 0,
        "per_q_time": DEFAULT_Q_TIME,
        "review_mode": False,
        "review_start": None,
        "admin_unlocked": False
    })

# ================= 50 BEHAVIORAL QUESTIONS =================
BEHAVIORAL_BANK = [
    {"question":"How do you handle a patient who refuses treatment?","Option A":"Respect and document","Option B":"Explain risks and notify doctor","Option C":"Force treatment","Option D":"Ignore","Correct Answer":"Explain risks and notify doctor"},
    {"question":"You notice a colleague skipping hand hygiene.","Option A":"Ignore","Option B":"Politely remind","Option C":"Report to HR","Option D":"Do the same","Correct Answer":"Politely remind"},
    {"question":"A family member asks about another patient.","Option A":"Tell them","Option B":"Protect privacy","Option C":"Share limited info","Option D":"Ignore","Correct Answer":"Protect privacy"},
    {"question":"You commit a minor medication error with no harm.","Option A":"Hide it","Option B":"Report immediately","Option C":"Wait","Option D":"Tell patient only","Correct Answer":"Report immediately"},
    {"question":"Patient angry due to waiting time.","Option A":"Argue","Option B":"Listen and empathize","Option C":"Ignore","Option D":"Ask to leave","Correct Answer":"Listen and empathize"},
    {"question":"Emergency alarm in another unit.","Option A":"Ignore","Option B":"Follow protocol","Option C":"Run immediately","Option D":"Panic","Correct Answer":"Follow protocol"},
    {"question":"Doctor gives unclear verbal order.","Option A":"Follow anyway","Option B":"Seek clarification","Option C":"Ask nurse","Option D":"Ignore","Correct Answer":"Seek clarification"},
    {"question":"Spill found in corridor.","Option A":"Walk away","Option B":"Mark/Clean immediately","Option C":"Inform later","Option D":"Ignore","Correct Answer":"Mark/Clean immediately"},
    {"question":"Patient falls during ambulation.","Option A":"Lift quickly","Option B":"Ease down & call help","Option C":"Leave","Option D":"Ignore","Correct Answer":"Ease down & call help"},
    {"question":"Conflicting instructions from seniors.","Option A":"Pick one","Option B":"Clarify","Option C":"Ignore","Option D":"Complain","Correct Answer":"Clarify"},
    {"question":"Primary goal of JCI.","Option A":"Profit","Option B":"Patient safety","Option C":"Branding","Option D":"Staff control","Correct Answer":"Patient safety"},
    {"question":"Correct patient identification.","Option A":"Room number","Option B":"Name + DOB","Option C":"Diagnosis","Option D":"Guess","Correct Answer":"Name + DOB"},
    {"question":"When to perform hand hygiene.","Option A":"After care only","Option B":"Before & after care","Option C":"Hourly","Option D":"When dirty","Correct Answer":"Before & after care"},
    {"question":"Colleague being bullied.","Option A":"Ignore","Option B":"Support & report","Option C":"Join","Option D":"Blame","Correct Answer":"Support & report"},
    {"question":"Vitals slightly abnormal.","Option A":"Ignore","Option B":"Recheck & report","Option C":"Wait","Option D":"Hide","Correct Answer":"Recheck & report"},
    {"question":"Sharps container full.","Option A":"Push needles","Option B":"Replace","Option C":"Leave","Option D":"Shake","Correct Answer":"Replace"},
    {"question":"Professionalism means.","Option A":"Late arrival","Option B":"Punctual & respectful","Option C":"Gossip","Option D":"Ignore rules","Correct Answer":"Punctual & respectful"},
    {"question":"Discussing patients in lift.","Option A":"Allowed","Option B":"Prohibited","Option C":"Sometimes","Option D":"Only staff","Correct Answer":"Prohibited"},
    {"question":"Standard precautions apply to.","Option A":"HIV only","Option B":"All patients","Option C":"ICU","Option D":"Surgery","Correct Answer":"All patients"},
    {"question":"Correct PPE usage.","Option A":"Reuse gloves","Option B":"Discard after use","Option C":"Wash gloves","Option D":"Reuse mask","Correct Answer":"Discard after use"},
    {"question":"Pressure ulcer prevention.","Option A":"Turn 8 hrs","Option B":"Turn 2 hrs","Option C":"No movement","Option D":"One pillow","Correct Answer":"Turn 2 hrs"},
    {"question":"Time-out before surgery.","Option A":"Break","Option B":"Verify patient/site","Option C":"Clean","Option D":"Count tools","Correct Answer":"Verify patient/site"},
    {"question":"Patient requests medical record.","Option A":"Refuse","Option B":"Follow policy","Option C":"Hand over","Option D":"Lie","Correct Answer":"Follow policy"},
    {"question":"Lost visitor.","Option A":"Ignore","Option B":"Assist","Option C":"Point","Option D":"Walk away","Correct Answer":"Assist"},
    {"question":"Hand wash duration.","Option A":"5 sec","Option B":"20 sec","Option C":"1 min","Option D":"10 sec","Correct Answer":"20 sec"},
    {"question":"NPO patient asks for water.","Option A":"Give sip","Option B":"Explain NPO","Option C":"Give glass","Option D":"Ignore","Correct Answer":"Explain NPO"},
    {"question":"Code Blue refers to.","Option A":"Fire","Option B":"Cardiac arrest","Option C":"Bomb threat","Option D":"Infant abduction","Correct Answer":"Cardiac arrest"},
    {"question":"Documentation should be.","Option A":"Late","Option B":"Accurate & timely","Option C":"Vague","Option D":"Pencil","Correct Answer":"Accurate & timely"},
    {"question":"Call bell ringing.","Option A":"Wait","Option B":"Respond immediately","Option C":"Unplug","Option D":"Ignore","Correct Answer":"Respond immediately"},
    {"question":"Proper lifting technique.","Option A":"Bend waist","Option B":"Use legs","Option C":"Twist","Option D":"Stretch arms","Correct Answer":"Use legs"},
    {"question":"Hard of hearing patient.","Option A":"Shout","Option B":"Face & speak clearly","Option C":"Avoid","Option D":"Family only","Correct Answer":"Face & speak clearly"},
    {"question":"Donning PPE means.","Option A":"Remove","Option B":"Put on","Option C":"Clean","Option D":"Wash hands","Correct Answer":"Put on"},
    {"question":"Yellow BMW bag.","Option A":"General waste","Option B":"Infectious waste","Option C":"Glass","Option D":"Paper","Correct Answer":"Infectious waste"},
    {"question":"Discharge responsibility.","Option A":"Wheel out","Option B":"Verify instructions","Option C":"Say bye","Option D":"Ignore","Correct Answer":"Verify instructions"},
    {"question":"Telephone orders.","Option A":"Ignore","Option B":"Read back","Option C":"Later","Option D":"Avoid","Correct Answer":"Read back"},
    {"question":"Patient dizzy while walking.","Option A":"Continue","Option B":"Assist to sit","Option C":"Leave","Option D":"Ignore","Correct Answer":"Assist to sit"},
    {"question":"5 Rights include.","Option A":"Right patient","Option B":"Right price","Option C":"Right hospital","Option D":"Right building","Correct Answer":"Right patient"},
    {"question":"Late for duty.","Option A":"Sneak in","Option B":"Inform supervisor","Option C":"Lie","Option D":"Ignore","Correct Answer":"Inform supervisor"},
    {"question":"Suicidal patient.","Option A":"Leave alone","Option B":"Constant observation","Option C":"Privacy","Option D":"Ignore","Correct Answer":"Constant observation"},
    {"question":"Teamwork requires.","Option A":"Silence","Option B":"Clear communication","Option C":"Competition","Option D":"Secrets","Correct Answer":"Clear communication"},
    {"question":"IV site red and swollen.","Option A":"Ignore","Option B":"Stop & report","Option C":"Increase rate","Option D":"Cover","Correct Answer":"Stop & report"},
    {"question":"Most common infection source.","Option A":"Air","Option B":"Hands","Option C":"Food","Option D":"Visitors","Correct Answer":"Hands"},
    {"question":"Unconscious patient consent.","Option A":"Wait family","Option B":"Implied consent","Option C":"Do nothing","Option D":"Ask staff","Correct Answer":"Implied consent"},
    {"question":"ID badge should be.","Option A":"Pocket","Option B":"Visible","Option C":"Car","Option D":"Home","Correct Answer":"Visible"},
    {"question":"Complaint about doctor.","Option A":"Agree","Option B":"Escalate properly","Option C":"Defend","Option D":"Ignore","Correct Answer":"Escalate properly"},
    {"question":"Cultural competence.","Option A":"Ignore culture","Option B":"Respect all","Option C":"Stereotype","Option D":"Avoid","Correct Answer":"Respect all"}
]

# ================= SIDEBAR ADMIN =================
with st.sidebar:
    st.subheader("⚙️ Admin")
    if st.checkbox("Unlock Level Settings"):
        key = st.text_input("Master Key", type="password")
        if ADMIN_MASTER_KEY and key == ADMIN_MASTER_KEY:
            st.session_state.admin_unlocked = True
            st.success("Admin unlocked")

    if st.session_state.admin_unlocked and not st.session_state.started:
        st.session_state.level = st.selectbox(
            "Difficulty",
            ["beginner", "intermediate", "advanced"],
            index=["beginner", "intermediate", "advanced"].index(st.session_state.level)
        )

    st.divider()
    st.info(f"Difficulty: **{st.session_state.level.upper()}**")

# ================= QUESTION PREP =================
def prepare_questions(df):
    qlist = []
    for _, r in df.iterrows():
        opts = [r["Option A"], r["Option B"], r["Option C"], r["Option D"]]
        random.shuffle(opts)
        qlist.append({
            "question": r["question"],
            "options": opts,
            "correct": r["Correct Answer"]
        })
    random.shuffle(qlist)
    return qlist

# ================= SCREEN 1 =================
if not st.session_state.started:
    st.title("🏥 Medanta Staff Assessment")

    name = st.text_input("Full Name")
    dob = st.date_input("Date of Birth", min_value=date(1960, 1, 1))
    qual = st.text_input("Qualification")
    cat = st.selectbox("Staff Category", ["Nursing", "Non-Nursing"])
    reg = st.text_input("Registration Number") if cat == "Nursing" else "N/A"
    college = st.text_input("College Name")
    contact = st.text_input("Contact Number")

    if st.button("Start Assessment"):
        if not (name and contact.isdigit() and len(contact) == 10):
            st.warning("Please enter valid details")
            st.stop()

        if not os.path.exists("questions.xlsx"):
            st.error("questions.xlsx not found")
            st.stop()

        df = pd.read_excel("questions.xlsx")
        tech = df[df["level"].str.lower() == st.session_state.level].sample(TECH_Q_COUNT)
        behav = pd.DataFrame(random.sample(BEHAVIORAL_BANK, BEHAV_Q_COUNT))
        full = pd.concat([tech, behav])

        st.session_state.questions = prepare_questions(full)
        st.session_state.candidate_data = {
            "name": name, "dob": str(dob), "qualification": qual,
            "category": cat, "reg_no": reg, "college": college, "contact": contact
        }

        st.session_state.start_time = time.time()
        st.session_state.question_start_time = time.time()
        st.session_state.started = True
        st.rerun()

# ================= SCREEN 2 =================
else:
    elapsed = time.time() - st.session_state.start_time
    remaining = max(0, GLOBAL_TEST_TIME - elapsed)
    st.sidebar.metric("⏳ Test Time Left", f"{int(remaining//60)}m {int(remaining%60)}s")

    if remaining <= 0:
        st.session_state.review_mode = True
        st.session_state.review_start = time.time()

    # -------- REVIEW MODE --------
    if st.session_state.review_mode:
        review_left = REVIEW_TIME_LIMIT - (time.time() - st.session_state.review_start)
        if review_left <= 0:
            st.warning("Review time expired. Submitting...")
        else:
            st.info(f"Review time left: {int(review_left)} sec")

        cols = st.columns(5)
        for i in range(TOTAL_QUESTIONS):
            mark = "✅" if i in st.session_state.answers else "⚪"
            if cols[i % 5].button(f"{mark} Q{i+1}"):
                st.session_state.q_index = i
                st.session_state.review_mode = False
                st.session_state.question_start_time = time.time()
                st.rerun()

        if st.button("Final Submit") or review_left <= 0:
            correct = sum(
                1 for i, q in enumerate(st.session_state.questions)
                if st.session_state.answers.get(i) == q["correct"]
            )
            score = round((correct / TOTAL_QUESTIONS) * 100, 2)

            requests.post(BRIDGE_URL, json={
                **st.session_state.candidate_data,
                "score": score
            })

            st.success(f"Assessment submitted. Score: {score}%")
            st.session_state.started = False
            st.stop()

    # -------- QUESTION MODE --------
    else:
        q = st.session_state.questions[st.session_state.q_index]

        # Safe per-question timer
        q_elapsed = time.time() - st.session_state.question_start_time
        if (
            q_elapsed > st.session_state.per_q_time
            and st.session_state.q_index not in st.session_state.answers
        ):
            st.session_state.q_index += 1
            st.session_state.question_start_time = time.time()

            if st.session_state.q_index >= TOTAL_QUESTIONS:
                st.session_state.review_mode = True
                st.session_state.review_start = time.time()
            st.rerun()

        st.subheader(f"Question {st.session_state.q_index + 1}")
        st.write(q["question"])
        st.caption(f"Time left for this question: {int(st.session_state.per_q_time - q_elapsed)} sec")

        choice = st.radio(
            "Select answer",
            q["options"],
            index=None,
            key=f"q_{st.session_state.q_index}"
        )

        if choice:
            time_taken = q_elapsed
            if time_taken > 40:
                st.session_state.fishy_counter += 1
            else:
                st.session_state.fishy_counter = 0

            if st.session_state.fishy_counter >= 3:
                st.session_state.per_q_time = REDUCED_Q_TIME

            st.session_state.answers[st.session_state.q_index] = choice
            st.session_state.q_index += 1
            st.session_state.question_start_time = time.time()

            if st.session_state.q_index >= TOTAL_QUESTIONS:
                st.session_state.review_mode = True
                st.session_state.review_start = time.time()

            st.rerun()

