import streamlit as st
import pandas as pd
import requests
import json
import time
import random
from datetime import date, datetime
import io

# --- CONFIGURATION ---
# Updated Bridge URL as requested
BRIDGE_URL = "https://script.google.com/macros/s/AKfycbzCICknuaFGUOqwPX_kMnTy_1FtA4ppm44ZAft56-Y21_4xCidrjvTkM6gwcuZW_4so/exec"
ADMIN_MASTER_KEY = "Medanta@2026"
TOTAL_TEST_TIME = 25 * 60  # Total 25 minutes

st.set_page_config(page_title="Medanta Staff Assessment", layout="centered")

# --- CUSTOM THEME & BLUE REVIEW BUTTON ---
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(255,255,255,0.94), rgba(255,255,255,0.94)), 
                          url("https://www.transparenttextures.com/patterns/medical-icons.png");
        background-attachment: fixed;
        background-size: cover;
    }
    /* Blue Review Button Design */
    div.stButton > button:first-child:contains("Review") {
        background-color: #0000FF !important;
        color: white !important;
        border-radius: 5px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 50 BEHAVIORAL QUESTIONS WITH TOPICS ---
BEHAVIORAL_BANK = [
    {"question": "How do you handle a patient who refuses treatment?", "Option A": "Respect and document", "Option B": "Explain risks and notify doctor", "Option C": "Force it", "Option D": "Ignore", "Correct Answer": "Explain risks and notify doctor", "Topic": "Patient Rights"},
    {"question": "Notice a colleague skipping hand hygiene?", "Option A": "Ignore it", "Option B": "Politely remind them", "Option C": "Report to HR", "Option D": "Do the same", "Correct Answer": "Politely remind them", "Topic": "Infection Control"},
    {"question": "A family member asks for another patient's status?", "Option A": "Tell them", "Option B": "Protect privacy and decline", "Option C": "Tell them to ask the patient", "Option D": "Share limited info", "Correct Answer": "Protect privacy and decline", "Topic": "Privacy & HIPAA"},
    {"question": "You make a minor medication error with no harm caused?", "Option A": "Hide it", "Option B": "Report it immediately", "Option C": "Wait and see", "Option D": "Tell only the patient", "Correct Answer": "Report it immediately", "Topic": "Patient Safety"},
    {"question": "Patient is angry about the wait time?", "Option A": "Argue back", "Option B": "Listen and empathize", "Option C": "Ignore them", "Option D": "Tell them to leave", "Correct Answer": "Listen and empathize", "Topic": "Communication"},
    {"question": "Emergency alarm goes off in another zone?", "Option A": "Stay at your post", "Option B": "Follow hospital protocol", "Option C": "Run to help immediately", "Option D": "Ignore it", "Correct Answer": "Follow hospital protocol", "Topic": "Emergency Protocols"},
    {"question": "A doctor gives a verbal order you find unclear?", "Option A": "Follow it anyway", "Option B": "Ask for clarification", "Option C": "Ask a nurse", "Option D": "Wait for written order", "Correct Answer": "Ask for clarification", "Topic": "Clinical Communication"},
    {"question": "You find a spill in the hallway?", "Option A": "Walk around it", "Option B": "Clean/Mark it immediately", "Option C": "Call housekeeping later", "Option D": "Tell a colleague", "Correct Answer": "Clean/Mark it immediately", "Topic": "Environment Safety"},
    {"question": "A patient falls while you are assisting them?", "Option A": "Pull them up quickly", "Option B": "Ease to floor and call help", "Option C": "Run for a doctor", "Option D": "Leave to get a chair", "Correct Answer": "Ease to floor and call help", "Topic": "Patient Safety"},
    {"question": "Conflicting instructions from two supervisors?", "Option A": "Pick one", "Option B": "Seek clarification from both", "Option C": "Do neither", "Option D": "Complain to HR", "Correct Answer": "Seek clarification from both", "Topic": "Teamwork"},
    {"question": "What is the primary goal of JCI accreditation?", "Option A": "Hospital profit", "Option B": "Patient safety and quality", "Option C": "International fame", "Option D": "Staff reduction", "Correct Answer": "Patient safety and quality", "Topic": "JCI Standards"},
    {"question": "Correct way to identify a patient?", "Option A": "Room number", "Option B": "Name and DOB/ID number", "Option C": "Diagnosis", "Option D": "Asking 'Are you Mr. X?'", "Correct Answer": "Name and DOB/ID number", "Topic": "Patient Identification"},
    {"question": "When should you perform hand hygiene?", "Option A": "Only after patient contact", "Option B": "Before and after patient contact", "Option C": "Only when hands are soiled", "Option D": "Once every hour", "Correct Answer": "Before and after patient contact", "Topic": "Infection Control"},
    {"question": "A colleague is being bullied in the unit?", "Option A": "Stay out of it", "Option B": "Support them and report", "Option C": "Join in", "Option D": "Tell them to be tougher", "Correct Answer": "Support them and report", "Topic": "Professionalism"},
    {"question": "A patient’s vitals are slightly abnormal?", "Option A": "Re-check and report", "Option B": "Assume equipment is broken", "Option C": "Document and ignore", "Option D": "Wait for next shift", "Correct Answer": "Re-check and report", "Topic": "Vitals Monitoring"},
    {"question": "Fire 'RACE' acronym: What does 'R' stand for?", "Option A": "Run", "Option B": "Rescue", "Option C": "Report", "Option D": "Ring alarm", "Correct Answer": "Rescue", "Topic": "Fire Safety"},
    {"question": "How to handle a sharps container that is full?", "Option A": "Push needles down", "Option B": "Close and replace it", "Option C": "Leave it for others", "Option D": "Shake it to make room", "Correct Answer": "Close and replace it", "Topic": "Waste Management"},
    {"question": "Professionalism involves which of the following?", "Option A": "Arriving late", "Option B": "Punctuality and respect", "Option C": "Gossiping", "Option D": "Ignoring uniform codes", "Correct Answer": "Punctuality and respect", "Topic": "Professionalism"},
    {"question": "A visitor is smoking in a non-smoking zone?", "Option A": "Ignore them", "Option B": "Politely inform of policy", "Option C": "Call security immediately", "Option D": "Ask for a cigarette", "Correct Answer": "Politely inform of policy", "Topic": "Policy Compliance"},
    {"question": "Standard precautions apply to?", "Option A": "Only HIV patients", "Option B": "All patients", "Option C": "Only surgical patients", "Option D": "Only ICU patients", "Correct Answer": "All patients", "Topic": "Infection Control"},
    {"question": "Correct use of PPE?", "Option A": "Re-use gloves", "Option B": "Discard after each use", "Option C": "Wear same mask all day", "Option D": "Wash gloves", "Correct Answer": "Discard after each use", "Topic": "Infection Control"},
    {"question": "A patient is at high risk for pressure ulcers?", "Option A": "Turn every 8 hours", "Option B": "Turn every 2 hours", "Option C": "Keep them still", "Option D": "Use only one pillow", "Correct Answer": "Turn every 2 hours", "Topic": "Patient Care"},
    {"question": "The 'Time Out' before surgery is for?", "Option A": "Staff coffee break", "Option B": "Verifying patient/site/procedure", "Option C": "Cleaning the room", "Option D": "Counting money", "Correct Answer": "Verifying patient/site/procedure", "Topic": "Surgical Safety"},
    {"question": "Patient wants to read their own medical record?", "Option A": "Refuse", "Option B": "Follow hospital policy for access", "Option C": "Hand it over immediately", "Option D": "Tell them it's illegal", "Correct Answer": "Follow hospital policy for access", "Topic": "Patient Rights"},
    {"question": "You see a visitor looking lost?", "Option A": "Walk past", "Option B": "Offer assistance", "Option C": "Tell them to find a map", "Option D": "Point and walk away", "Correct Answer": "Offer assistance", "Topic": "Patient Experience"},
    {"question": "Washing hands with soap should take at least?", "Option A": "5 seconds", "Option B": "20 seconds", "Option C": "2 minutes", "Option D": "10 seconds", "Correct Answer": "20 seconds", "Topic": "Infection Control"},
    {"question": "A patient is NPO but asks for water?", "Option A": "Give a small sip", "Option B": "Explain NPO status", "Option C": "Give a full glass", "Option D": "Ignore the request", "Correct Answer": "Explain NPO status", "Topic": "Clinical Care"},
    {"question": "Code Blue refers to?", "Option A": "Fire", "Option B": "Cardiac/Resp Arrest", "Option C": "Infant Abduction", "Option D": "Bomb threat", "Correct Answer": "Cardiac/Resp Arrest", "Topic": "Emergency Codes"},
    {"question": "Documentation should be?", "Option A": "Done at end of week", "Option B": "Accurate and timely", "Option C": "Vague", "Option D": "Done in pencil", "Correct Answer": "Accurate and timely", "Topic": "Medical Records"},
    {"question": "A patient's call bell has been ringing for 5 mins?", "Option A": "Wait for their nurse", "Option B": "Answer it immediately", "Option C": "Unplug it", "Option D": "Tell them to wait", "Correct Answer": "Answer it immediately", "Topic": "Patient Responsiveness"},
    {"question": "Proper way to lift a heavy object?", "Option A": "Bend at waist", "Option B": "Bend at knees/Use legs", "Option C": "Twist your back", "Option D": "Hold far from body", "Correct Answer": "Bend at knees/Use legs", "Topic": "Occupational Safety"},
    {"question": "A patient is hard of hearing?", "Option A": "Shout loudly", "Option B": "Face them and speak clearly", "Option C": "Talk to their family only", "Option D": "Avoid talking to them", "Correct Answer": "Face them and speak clearly", "Topic": "Communication"},
    {"question": "Infection control: 'Donning' means?", "Option A": "Taking off PPE", "Option B": "Putting on PPE", "Option C": "Cleaning equipment", "Option D": "Washing hands", "Correct Answer": "Putting on PPE", "Topic": "Infection Control"},
    {"question": "Medical waste in Yellow bags is?", "Option A": "General waste", "Option B": "Infectious waste", "Option C": "Glassware", "Option D": "Recyclables", "Correct Answer": "Infectious waste", "Topic": "Waste Management"},
    {"question": "A patient is being discharged. Your role?", "Option A": "Say goodbye", "Option B": "Verify discharge instructions", "Option C": "Just wheel them out", "Option D": "Keep their records", "Correct Answer": "Verify discharge instructions", "Topic": "Discharge Planning"},
    {"question": "Telephone orders should be?", "Option A": "Ignored", "Option B": "Read back and verified", "Option C": "Written later", "Option D": "Only for non-meds", "Correct Answer": "Read back and verified", "Topic": "Clinical Communication"},
    {"question": "Patient feels dizzy while walking?", "Option A": "Keep walking", "Option B": "Assist to sit/lie down", "Option C": "Tell them to breathe", "Option D": "Leave to get help", "Correct Answer": "Assist to sit/lie down", "Topic": "Patient Safety"},
    {"question": "HIPAA/Privacy: Discussing patients in the lift?", "Option A": "Okay if quiet", "Option B": "Strictly prohibited", "Option C": "Okay if no names used", "Option D": "Okay with staff", "Correct Answer": "Strictly prohibited", "Topic": "Privacy & HIPAA"},
    {"question": "The '5 Rights' of medication include?", "Option A": "Right Patient/Right Med", "Option B": "Right Price", "Option C": "Right Doctor", "Option D": "Right Hospital", "Correct Answer": "Right Patient/Right Med", "Topic": "Medication Safety"},
    {"question": "You are late for your shift?", "Option A": "Sneak in", "Option B": "Notify supervisor early", "Option C": "Blame traffic later", "Option D": "Don't mention it", "Correct Answer": "Notify supervisor early", "Topic": "Professionalism"},
    {"question": "Patient is at risk for suicide?", "Option A": "Leave them alone", "Option B": "Ensure constant observation", "Option C": "Give them privacy", "Option D": "Tell them to cheer up", "Correct Answer": "Ensure constant observation", "Topic": "Patient Safety"},
    {"question": "Correct order for 'Doffing' PPE?", "Option A": "Gown then Gloves", "Option B": "Gloves then Gown", "Option C": "Mask then Gloves", "Option D": "Doesn't matter", "Correct Answer": "Gloves then Gown", "Topic": "Infection Control"},
    {"question": "A patient has a localized infection?", "Option A": "Use airborne precautions", "Option B": "Use contact precautions", "Option C": "No precautions needed", "Option D": "Wear two masks", "Correct Answer": "Use contact precautions", "Topic": "Infection Control"},
    {"question": "Effective teamwork requires?", "Option A": "Working alone", "Option B": "Clear communication", "Option C": "Competition", "Option D": "Keeping secrets", "Correct Answer": "Clear communication", "Topic": "Teamwork"},
    {"question": "Patient’s IV site is red and swollen?", "Option A": "Apply ice", "Option B": "Stop infusion/Notify nurse", "Option C": "Increase rate", "Option D": "Ignore it", "Correct Answer": "Stop infusion/Notify nurse", "Topic": "Clinical Care"},
    {"question": "The most common source of hospital infections?", "Option A": "Air vents", "Option B": "Hands of staff", "Option C": "Food", "Option D": "Visitors", "Correct Answer": "Hands of staff", "Topic": "Infection Control"},
    {"question": "Patient is unconscious and needs care?", "Option A": "Wait for family", "Option B": "Implied consent/Emergency care", "Option C": "Do nothing", "Option D": "Ask a neighbor", "Correct Answer": "Implied consent/Emergency care", "Topic": "Patient Rights"},
    {"question": "Your ID badge should be?", "Option A": "In your pocket", "Option B": "Visible at all times", "Option C": "In your car", "Option D": "Left at home", "Correct Answer": "Visible at all times", "Topic": "Security"},
    {"question": "A patient complains about a doctor's behavior?", "Option A": "Agree with them", "Option B": "Escalate to Patient Relations", "Option C": "Tell them to be quiet", "Option D": "Defend the doctor", "Correct Answer": "Escalate to Patient Relations", "Topic": "Patient Experience"},
    {"question": "Cultural competence means?", "Option A": "Treating everyone differently", "Option B": "Respecting all backgrounds", "Option C": "Ignoring culture", "Option D": "Stereotyping", "Correct Answer": "Respecting all backgrounds", "Topic": "Professionalism"}
]

# --- SESSION STATE INITIALIZATION ---
if "started" not in st.session_state:
    st.session_state.update({
        "started": False, "review_mode": False, "q_index": 0, 
        "answers": {}, "candidate_data": {}, "level": "beginner",
        "start_time": None, "questions_df": None
    })

# Sidebar Admin
with st.sidebar:
    st.subheader("⚙️ Admin")
    if st.checkbox("Unlock Level Settings"):
        if st.text_input("Master Key", type="password") == ADMIN_MASTER_KEY:
            st.session_state.level = st.selectbox("Assign Test Level", ["beginner", "intermediate", "advanced"])
    st.divider()
    st.info(f"Difficulty: **{st.session_state.level.upper()}**")

# --- SCREEN 1: STAFF INFO ---
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
        if name and len(contact) == 10:
            st.session_state.candidate_data = {
                "name": name, "dob": str(dob), "qualification": qual, 
                "category": cat, "reg_no": reg, "college": college, "contact": contact
            }
            try:
                # Load Excel questions and mix with Behavioral Bank
                df_xl = pd.read_excel("questions.xlsx")
                tech_q = df_xl[df_xl['level'].str.lower() == st.session_state.level.lower()].sample(n=18)
                behav_q = pd.DataFrame(random.sample(BEHAVIORAL_BANK, 7))
                st.session_state.questions_df = pd.concat([tech_q, behav_q], ignore_index=True).sample(frac=1).reset_index(drop=True)
                st.session_state.start_time = time.time()
                st.session_state.started = True
                st.rerun()
            except Exception as e:
                st.error(f"Error loading questions: {e}")
        else:
            st.warning("Please fill all required information correctly.")

# --- SCREEN 2: ASSESSMENT ---
elif st.session_state.started:
    q_df = st.session_state.questions_df
    elapsed = time.time() - st.session_state.start_time
    rem_time = max(0, TOTAL_TEST_TIME - elapsed)
    
    st.sidebar.metric("⏳ Time Remaining", f"{int(rem_time // 60)}m {int(rem_time % 60)}s")
    
    if rem_time <= 0:
        st.warning("Time is up! Redirecting to review...")
        st.session_state.review_mode = True

    # --- REVIEW MODE ---
    if st.session_state.review_mode:
        st.title("📝 Review & Submit")
        st.write("Click any question button to go back and modify your answer.")
        
        # Grid layout for question review
        grid = st.columns(5)
        for i in range(25):
            status = "✅" if f"Q{i+1}" in st.session_state.answers else "⚪"
            if grid[i % 5].button(f"{status} Q{i+1}", key=f"rev_{i}"):
                st.session_state.q_index = i
                st.session_state.review_mode = False
                st.rerun()
        
        st.divider()
        if st.button("Final Submit Assessment", type="primary", use_container_width=True):
            # Scoring and Feedback Logic
            correct = 0
            weak_topics = []
            for idx, row in q_df.iterrows():
                user_ans = st.session_state.answers.get(f"Q{idx+1}")
                if user_ans == row["Correct Answer"]:
                    correct += 1
                else:
                    weak_topics.append(row.get("Topic", "General Clinical Protocols"))
            
            score_num = (correct / 25) * 100
            score_pct = f"{score_num}%"
            
            # Post to Google Bridge
            payload = {**st.session_state.candidate_data, "score": score_pct, "duration": f"{round(elapsed/60, 2)} mins"}
            requests.post(BRIDGE_URL, json=payload)
            
            # Result Display
            st.divider()
            eval_msg = ""
            if score_num >= 60:
                st.balloons()
                st.success(f"🎊 PASS! Final Score: {score_pct}")
                eval_msg = "Sufficient knowledge demonstrated."
            else:
                st.error(f"❌ RESULT: NOT CLEARED. Final Score: {score_pct}")
                recommends = list(set(weak_topics))[:3]
                st.warning(f"Required Improvement in: {', '.join(recommends)}")
                eval_msg = f"Needs improvement in: {', '.join(recommends)}"

            # Progress Report Download
            report = f"""
            MEDANTA STAFF ASSESSMENT PROGRESS REPORT
            Candidate: {st.session_state.candidate_data['name']}
            Date: {datetime.now().strftime('%Y-%m-%d')}
            Final Score: {score_pct}
            Evaluation: {eval_msg}
            """
            st.download_button("📥 Download Progress Report", report, file_name=f"Report_{st.session_state.candidate_data['name']}.txt")
            st.session_state.started = False

    # --- QUESTION VIEW ---
    else:
        idx = st.session_state.q_index
        row = q_df.iloc[idx]
        st.subheader(f"Question {idx+1} of 25")
        st.write(f"### {row['question']}")
        
        opts = [row["Option A"], row["Option B"], row["Option C"], row["Option D"]]
        prev_ans = st.session_state.answers.get(f"Q{idx+1}")
        
        # Radio button with pre-selected previous answer for review purposes
        choice = st.radio("Select Choice:", opts, index=opts.index(prev_ans) if prev_ans in opts else 0, key=f"q_radio_{idx}")
        st.session_state.answers[f"Q{idx+1}"] = choice
        
        # Navigation Buttons
        c1, c2, c3 = st.columns([1,1,2])
        if idx > 0 and c1.button("⬅️ Previous"):
            st.session_state.q_index -= 1
            st.rerun()
        if idx < 24 and c2.button("Next ➡️"):
            st.session_state.q_index += 1
            st.rerun()
            
        # The Blue Review Button
        if c3.button("Review All Answers 📝", use_container_width=True):
            st.session_state.review_mode = True
            st.rerun()
