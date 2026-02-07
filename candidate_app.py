import streamlit as st
import pandas as pd
import requests
import json
import time
import random
from PIL import Image
from datetime import date

# --- CONFIGURATION ---
BRIDGE_URL = "https://script.google.com/macros/s/AKfycbykNToCtX66Enoiu9YwK4_h12JSlm-uwqvTrVBng4ujMrjJUKtub7GkHuaPGHzs8yHt/exec"
ADMIN_MASTER_KEY = "Medanta@2026"
TOTAL_TEST_TIME = 25 * 60  # 25 Minutes
SEC_PER_QUESTION = 60      # 60 Seconds per question

st.set_page_config(page_title="Medanta Assessment Tool", layout="centered")

# --- CUSTOM CSS ---
st.markdown("<style>.stApp {background-image: linear-gradient(rgba(255,255,255,0.92), rgba(255,255,255,0.92)), url('https://www.transparenttextures.com/patterns/medical-icons.png'); background-attachment: fixed; background-size: cover;}</style>", unsafe_allow_html=True)

# --- FULL BEHAVIORAL BANK (50 QUESTIONS) ---
BEHAVIORAL_BANK = [
    {"question": "How do you handle a patient who refuses treatment?", "Option A": "Respect and document", "Option B": "Explain risks and notify doctor", "Option C": "Force it", "Option D": "Ignore", "Correct Answer": "Explain risks and notify doctor"},
    {"question": "Notice a colleague skipping hand hygiene?", "Option A": "Ignore it", "Option B": "Politely remind them", "Option C": "Report to HR", "Option D": "Do the same", "Correct Answer": "Politely remind them"},
    {"question": "A family member asks for another patient's status?", "Option A": "Tell them", "Option B": "Protect privacy and decline", "Option C": "Tell them to ask the patient", "Option D": "Share limited info", "Correct Answer": "Protect privacy and decline"},
    {"question": "You make a minor medication error with no harm caused?", "Option A": "Hide it", "Option B": "Report it immediately", "Option C": "Wait and see", "Option D": "Tell only the patient", "Correct Answer": "Report it immediately"},
    {"question": "Patient is angry about the wait time?", "Option A": "Argue back", "Option B": "Listen and empathize", "Option C": "Ignore them", "Option D": "Tell them to leave", "Correct Answer": "Listen and empathize"},
    {"question": "Emergency alarm goes off in another zone?", "Option A": "Stay at your post", "Option B": "Follow hospital protocol", "Option C": "Run to help immediately", "Option D": "Ignore it", "Correct Answer": "Follow hospital protocol"},
    {"question": "A doctor gives a verbal order you find unclear?", "Option A": "Follow it anyway", "Option B": "Ask for clarification", "Option C": "Ask a nurse", "Option D": "Wait for written order", "Correct Answer": "Ask for clarification"},
    {"question": "You find a spill in the hallway?", "Option A": "Walk around it", "Option B": "Clean/Mark it immediately", "Option C": "Call housekeeping later", "Option D": "Tell a colleague", "Correct Answer": "Clean/Mark it immediately"},
    {"question": "A patient falls while you are assisting them?", "Option A": "Pull them up quickly", "Option B": "Ease to floor and call help", "Option C": "Run for a doctor", "Option D": "Leave to get a chair", "Correct Answer": "Ease to floor and call help"},
    {"question": "Conflicting instructions from two supervisors?", "Option A": "Pick one", "Option B": "Seek clarification from both", "Option C": "Do neither", "Option D": "Complain to HR", "Correct Answer": "Seek clarification from both"},
    {"question": "What is the primary goal of JCI accreditation?", "Option A": "Hospital profit", "Option B": "Patient safety and quality", "Option C": "International fame", "Option D": "Staff reduction", "Correct Answer": "Patient safety and quality"},
    {"question": "Correct way to identify a patient?", "Option A": "Room number", "Option B": "Name and DOB/ID number", "Option C": "Diagnosis", "Option D": "Asking 'Are you Mr. X?'", "Correct Answer": "Name and DOB/ID number"},
    {"question": "When should you perform hand hygiene?", "Option A": "Only after patient contact", "Option B": "Before and after patient contact", "Option C": "Only when hands are soiled", "Option D": "Once every hour", "Correct Answer": "Before and after patient contact"},
    {"question": "A colleague is being bullied in the unit?", "Option A": "Stay out of it", "Option B": "Support them and report", "Option C": "Join in", "Option D": "Tell them to be tougher", "Correct Answer": "Support them and report"},
    {"question": "A patient’s vitals are slightly abnormal?", "Option A": "Re-check and report", "Option B": "Assume equipment is broken", "Option C": "Document and ignore", "Option D": "Wait for next shift", "Correct Answer": "Re-check and report"},
    {"question": "Fire 'RACE' acronym: What does 'R' stand for?", "Option A": "Run", "Option B": "Rescue", "Option C": "Report", "Option D": "Ring alarm", "Correct Answer": "Rescue"},
    {"question": "How to handle a sharps container that is full?", "Option A": "Push needles down", "Option B": "Close and replace it", "Option C": "Leave it for others", "Option D": "Shake it to make room", "Correct Answer": "Close and replace it"},
    {"question": "Professionalism involves which of the following?", "Option A": "Arriving late", "Option B": "Punctuality and respect", "Option C": "Gossiping", "Option D": "Ignoring uniform codes", "Correct Answer": "Punctuality and respect"},
    {"question": "A visitor is smoking in a non-smoking zone?", "Option A": "Ignore them", "Option B": "Politely inform of policy", "Option C": "Call security immediately", "Option D": "Ask for a cigarette", "Correct Answer": "Politely inform of policy"},
    {"question": "Standard precautions apply to?", "Option A": "Only HIV patients", "Option B": "All patients", "Option C": "Only surgical patients", "Option D": "Only ICU patients", "Correct Answer": "All patients"},
    {"question": "Correct use of PPE?", "Option A": "Re-use gloves", "Option B": "Discard after each use", "Option C": "Wear same mask all day", "Option D": "Wash gloves", "Correct Answer": "Discard after each use"},
    {"question": "A patient is at high risk for pressure ulcers?", "Option A": "Turn every 8 hours", "Option B": "Turn every 2 hours", "Option C": "Keep them still", "Option D": "Use only one pillow", "Correct Answer": "Turn every 2 hours"},
    {"question": "The 'Time Out' before surgery is for?", "Option A": "Staff coffee break", "Option B": "Verifying patient/site/procedure", "Option C": "Cleaning the room", "Option D": "Counting money", "Correct Answer": "Verifying patient/site/procedure"},
    {"question": "Patient wants to read their own medical record?", "Option A": "Refuse", "Option B": "Follow hospital policy for access", "Option C": "Hand it over immediately", "Option D": "Tell them it's illegal", "Correct Answer": "Follow hospital policy for access"},
    {"question": "You see a visitor looking lost?", "Option A": "Walk past", "Option B": "Offer assistance", "Option C": "Tell them to find a map", "Option D": "Point and walk away", "Correct Answer": "Offer assistance"},
    {"question": "Washing hands with soap should take at least?", "Option A": "5 seconds", "Option B": "20 seconds", "Option C": "2 minutes", "Option D": "10 seconds", "Correct Answer": "20 seconds"},
    {"question": "A patient is NPO but asks for water?", "Option A": "Give a small sip", "Option B": "Explain NPO status", "Option C": "Give a full glass", "Option D": "Ignore the request", "Correct Answer": "Explain NPO status"},
    {"question": "Code Blue refers to?", "Option A": "Fire", "Option B": "Cardiac/Resp Arrest", "Option C": "Infant Abduction", "Option D": "Bomb threat", "Correct Answer": "Cardiac/Resp Arrest"},
    {"question": "Documentation should be?", "Option A": "Done at end of week", "Option B": "Accurate and timely", "Option C": "Vague", "Option D": "Done in pencil", "Correct Answer": "Accurate and timely"},
    {"question": "A patient's call bell has been ringing for 5 mins?", "Option A": "Wait for their nurse", "Option B": "Answer it immediately", "Option C": "Unplug it", "Option D": "Tell them to wait", "Correct Answer": "Answer it immediately"},
    {"question": "Proper way to lift a heavy object?", "Option A": "Bend at waist", "Option B": "Bend at knees/Use legs", "Option C": "Twist your back", "Option D": "Hold far from body", "Correct Answer": "Bend at knees/Use legs"},
    {"question": "A patient is hard of hearing?", "Option A": "Shout loudly", "Option B": "Face them and speak clearly", "Option C": "Talk to their family only", "Option D": "Avoid talking to them", "Correct Answer": "Face them and speak clearly"},
    {"question": "Infection control: 'Donning' means?", "Option A": "Taking off PPE", "Option B": "Putting on PPE", "Option C": "Cleaning equipment", "Option D": "Washing hands", "Correct Answer": "Putting on PPE"},
    {"question": "Medical waste in Yellow bags is?", "Option A": "General waste", "Option B": "Infectious waste", "Option C": "Glassware", "Option D": "Recyclables", "Correct Answer": "Infectious waste"},
    {"question": "A patient is being discharged. Your role?", "Option A": "Say goodbye", "Option B": "Verify discharge instructions", "Option C": "Just wheel them out", "Option D": "Keep their records", "Correct Answer": "Verify discharge instructions"},
    {"question": "Telephone orders should be?", "Option A": "Ignored", "Option B": "Read back and verified", "Option C": "Written later", "Option D": "Only for non-meds", "Correct Answer": "Read back and verified"},
    {"question": "Patient feels dizzy while walking?", "Option A": "Keep walking", "Option B": "Assist to sit/lie down", "Option C": "Tell them to breathe", "Option D": "Leave to get help", "Correct Answer": "Assist to sit/lie down"},
    {"question": "HIPAA/Privacy: Discussing patients in the lift?", "Option A": "Okay if quiet", "Option B": "Strictly prohibited", "Option C": "Okay if no names used", "Option D": "Okay with staff", "Correct Answer": "Strictly prohibited"},
    {"question": "The '5 Rights' of medication include?", "Option A": "Right Patient/Right Med", "Option B": "Right Price", "Option C": "Right Doctor", "Option D": "Right Hospital", "Correct Answer": "Right Patient/Right Med"},
    {"question": "You are late for your shift?", "Option A": "Sneak in", "Option B": "Notify supervisor early", "Option C": "Blame traffic later", "Option D": "Don't mention it", "Correct Answer": "Notify supervisor early"},
    {"question": "Patient is at risk for suicide?", "Option A": "Leave them alone", "Option B": "Ensure constant observation", "Option C": "Give them privacy", "Option D": "Tell them to cheer up", "Correct Answer": "Ensure constant observation"},
    {"question": "Correct order for 'Doffing' PPE?", "Option A": "Gown then Gloves", "Option B": "Gloves then Gown", "Option C": "Mask then Gloves", "Option D": "Doesn't matter", "Correct Answer": "Gloves then Gown"},
    {"question": "A patient has a localized infection?", "Option A": "Use airborne precautions", "Option B": "Use contact precautions", "Option C": "No precautions needed", "Option D": "Wear two masks", "Correct Answer": "Use contact precautions"},
    {"question": "Effective teamwork requires?", "Option A": "Working alone", "Option B": "Clear communication", "Option C": "Competition", "Option D": "Keeping secrets", "Correct Answer": "Clear communication"},
    {"question": "Patient’s IV site is red and swollen?", "Option A": "Apply ice", "Option B": "Stop infusion/Notify nurse", "Option C": "Increase rate", "Option D": "Ignore it", "Correct Answer": "Stop infusion/Notify nurse"},
    {"question": "The most common source of hospital infections?", "Option A": "Air vents", "Option B": "Hands of staff", "Option C": "Food", "Option D": "Visitors", "Correct Answer": "Hands of staff"},
    {"question": "Patient is unconscious and needs care?", "Option A": "Wait for family", "Option B": "Implied consent/Emergency care", "Option C": "Do nothing", "Option D": "Ask a neighbor", "Correct Answer": "Implied consent/Emergency care"},
    {"question": "Your ID badge should be?", "Option A": "In your pocket", "Option B": "Visible at all times", "Option C": "In your car", "Option D": "Left at home", "Correct Answer": "Visible at all times"},
    {"question": "A patient complains about a doctor's behavior?", "Option A": "Agree with them", "Option B": "Escalate to Patient Relations", "Option C": "Tell them to be quiet", "Option D": "Defend the doctor", "Correct Answer": "Escalate to Patient Relations"},
    {"question": "Cultural competence means?", "Option A": "Treating everyone differently", "Option B": "Respecting all backgrounds", "Option C": "Ignoring culture", "Option D": "Stereotyping", "Correct Answer": "Respecting all backgrounds"}
]

@st.cache_data
def get_hybrid_questions(level_choice):
    try:
        df = pd.read_excel("questions.xlsx")
        df = df.fillna("")
        level_col = next((c for c in df.columns if 'level' in c.lower()), None)
        df[level_col] = df[level_col].astype(str).str.strip().str.lower()
        tech_filtered = df[df[level_col] == str(level_choice).lower()]
        num_behav = random.randint(5, 8)
        num_tech = 25 - num_behav
        tech_sel = tech_filtered.sample(n=min(len(tech_filtered), num_tech))
        behav_sel = pd.DataFrame(random.sample(BEHAVIORAL_BANK, num_behav))
        return pd.concat([tech_sel, behav_sel], ignore_index=True).sample(frac=1).reset_index(drop=True)
    except:
        return pd.DataFrame()

# --- INITIALIZE STATE ---
if "started" not in st.session_state:
    st.session_state.update({
        "started": False, "review_mode": False, "q_index": 0, "answers": {}, 
        "candidate_data": {}, "level": "beginner", "q_start_time": 0
    })

# --- SIDEBAR ADMIN ---
with st.sidebar:
    st.subheader("⚙️ Admin")
    if st.checkbox("Unlock"):
        if st.text_input("Key", type="password") == ADMIN_MASTER_KEY:
            st.session_state.level = st.selectbox("Level", ["beginner", "intermediate", "advanced"])
    st.divider()
    st.info(f"Level: {st.session_state.level.upper()}")

# --- MAIN LOGIC ---
if not st.session_state.started:
    st.title("🏥 Medanta Staff Assessment")
    st.subheader("Staff Information")
    name = st.text_input("Full Name")
    dob = st.date_input("Date of Birth", min_value=date(1960, 1, 1))
    qual = st.text_input("Qualification")
    cat = st.selectbox("Staff Category", ["Nursing", "Non-Nursing"])
    reg = st.text_input("Registration Number") if cat == "Nursing" else "N/A"
    college = st.text_input("College Name")
    contact = st.text_input("Contact Number")

    if st.button("Start Assessment", type="primary"):
        if name and len(contact) == 10:
            st.session_state.candidate_data = {
                "name": name, "dob": str(dob), "qualification": qual, 
                "category": cat, "reg_no": reg, "college": college, "contact": contact
            }
            st.session_state.questions_df = get_hybrid_questions(st.session_state.level)
            st.session_state.started = True
            st.session_state.start_time = time.time()
            st.session_state.q_start_time = time.time() # Reset question timer
            st.rerun()

elif st.session_state.started:
    q_df = st.session_state.questions_df
    now = time.time()
    
    # Overall Test Timer
    elapsed_total = now - st.session_state.start_time
    rem_total = max(0, TOTAL_TEST_TIME - elapsed_total)
    
    # Per-Question Timer
    elapsed_q = now - st.session_state.q_start_time
    rem_q = max(0, SEC_PER_QUESTION - elapsed_q)
    
    st.sidebar.metric("⏳ Total Time Left", f"{int(rem_total // 60)}m {int(rem_total % 60)}s")
    
    if not st.session_state.review_mode:
        st.sidebar.metric("⏱️ Question Time", f"{int(rem_q)}s")

    # Force auto-next if question timer hits zero
    if rem_q <= 0 and not st.session_state.review_mode:
        idx = st.session_state.q_index
        if f"Q{idx+1}" not in st.session_state.answers:
            st.session_state.answers[f"Q{idx+1}"] = "Time Expired"
        if idx < 24:
            st.session_state.q_index += 1
            st.session_state.q_start_time = time.time()
        else:
            st.session_state.review_mode = True
        st.rerun()

    if st.session_state.review_mode:
        st.header("📝 Review Your Answers")
        review_data = []
        for i in range(25):
            user_ans = st.session_state.answers.get(f"Q{i+1}", "Not Answered")
            review_data.append({"No.": i+1, "Question": q_df.iloc[i]['question'][:60]+"...", "Answer": user_ans})
        st.table(pd.DataFrame(review_data))

        if st.button("🚀 Final Submit", type="primary") or rem_total <= 0:
            correct = sum(1 for i, row in q_df.iterrows() if st.session_state.answers.get(f"Q{i+1}") == row["Correct Answer"])
            score_pct = f"{round((correct/25)*100, 2)}%"
            duration = f"{round((time.time() - st.session_state.start_time)/60, 2)} mins"
            payload = {**st.session_state.candidate_data, "score": score_pct, "duration": duration, "answers": json.dumps(st.session_state.answers)}
            try:
                res = requests.post(BRIDGE_URL, json=payload, timeout=15)
                if res.status_code == 200:
                    st.balloons(); st.success(f"Submitted! Score: {score_pct}"); st.session_state.started = False
                else: st.error("Submission failed.")
            except: st.error("Connection lost.")
    else:
        idx = st.session_state.q_index
        q_row = q_df.iloc[idx]
        st.subheader(f"Question {idx+1} of 25")
        st.write(f"### {q_row['question']}")
        options = [q_row["Option A"], q_row["Option B"], q_row["Option C"], q_row["Option D"]]
        current_ans = st.session_state.answers.get(f"Q{idx+1}", options[0])
        user_choice = st.radio("Choose one:", options, index=options.index(current_ans) if current_ans in options else 0, key=f"r_{idx}")
        
        if st.button("Save & Next ➡️"):
            st.session_state.answers[f"Q{idx+1}"] = user_choice
            if idx < 24:
                st.session_state.q_index += 1
                st.session_state.q_start_time = time.time() # Reset timer for next question
            else:
                st.session_state.review_mode = True
            st.rerun()
