import streamlit as st
import pandas as pd
import requests
import json
import time
import random
from PIL import Image
from datetime import date

# --- CONFIGURATION ---
BRIDGE_URL = "https://script.google.com/macros/s/AKfycbzjOu8JiFHsoTiHclvScouiMIrZbrxmUpjEOLAemFNClb-2S3YQ_HTzCbB3yTNDSxwb/exec"
TOTAL_TEST_TIME = 25 * 60 
QUESTION_TIME_LIMIT = 60
ADMIN_MASTER_KEY = "Medanta@2026"

# --- FULL BEHAVIORAL BANK (ALL 50 QUESTIONS) ---
BEHAVIORAL_BANK = [
    {"question": "How do you handle a patient who refuses necessary medical treatment?", "Option A": "Respect their wish and document", "Option B": "Explain risks and notify doctor", "Option C": "Force the treatment", "Option D": "Ignore the refusal", "Correct Answer": "Explain risks and notify doctor"},
    {"question": "If you notice a colleague skipping hand hygiene, what do you do?", "Option A": "Ignore it to avoid conflict", "Option B": "Politely remind them immediately", "Option C": "Report to HR immediately", "Option D": "Do the same", "Correct Answer": "Politely remind them immediately"},
    {"question": "A family member asks for a patient's diagnosis but isn't the primary contact. You:", "Option A": "Tell them anyway", "Option B": "Direct them to the primary contact", "Option C": "Ask the patient's roommate", "Option D": "Tell them to check the file", "Correct Answer": "Direct them to the primary contact"},
    {"question": "What is the primary goal of the SBAR communication technique?", "Option A": "To waste time", "Option B": "Standardized, clear reporting", "Option C": "Personal chatting", "Option D": "To confuse colleagues", "Correct Answer": "Standardized, clear reporting"},
    {"question": "You find a spill in a hospital corridor. What is your first action?", "Option A": "Walk around it", "Option B": "Stay by it and call for cleaning", "Option C": "Wait for your shift to end", "Option D": "Hope someone else sees it", "Correct Answer": "Stay by it and call for cleaning"},
    {"question": "How should you respond to an aggressive visitor?", "Option A": "Shout back", "Option B": "Remain calm and call security", "Option C": "Leave the floor", "Option D": "Argue about the rules", "Correct Answer": "Remain calm and call security"},
    {"question": "What does 'Patient-Centered Care' mean to you?", "Option A": "Treating only the disease", "Option B": "Involving patient in decisions", "Option C": "Doing what the doctor says only", "Option D": "Following a fixed script", "Correct Answer": "Involving patient in decisions"},
    {"question": "If you realize you made a medication error, what is the first step?", "Option A": "Hide the evidence", "Option B": "Immediately report to supervisor", "Option C": "Wait to see if patient reacts", "Option D": "Blame the pharmacy", "Correct Answer": "Immediately report to supervisor"},
    {"question": "How do you handle multiple urgent tasks assigned at once?", "Option A": "Do the easiest first", "Option B": "Prioritize by patient safety risk", "Option C": "Do nothing", "Option D": "Complain to the HOD", "Correct Answer": "Prioritize by patient safety risk"},
    {"question": "During a code blue, if your role is unclear, you should:", "Option A": "Leave the room", "Option B": "Ask the team lead for a task", "Option C": "Start chest compressions anyway", "Option D": "Stand and watch", "Correct Answer": "Ask the team lead for a task"},
    {"question": "A patient is anxious about surgery. You should:", "Option A": "Tell them to be brave", "Option B": "Listen and validate their feelings", "Option C": "Tell them about a failed surgery", "Option D": "Ignore the anxiety", "Correct Answer": "Listen and validate their feelings"},
    {"question": "Teamwork in a hospital is successful when:", "Option A": "Everyone works in silos", "Option B": "Communication is open and shared", "Option C": "The senior makes all decisions", "Option D": "Mistakes are kept secret", "Correct Answer": "Communication is open and shared"},
    {"question": "When using a computer in a public area, you should:", "Option A": "Leave it logged in", "Option B": "Lock screen when leaving", "Option C": "Share your password with staff", "Option D": "Write password on a post-it", "Correct Answer": "Lock screen when leaving"},
    {"question": "Cultural sensitivity in healthcare means:", "Option A": "Treating everyone identically", "Option B": "Respecting diverse beliefs and needs", "Option C": "Ignoring cultural differences", "Option D": "Making assumptions based on origin", "Correct Answer": "Respecting diverse beliefs and needs"},
    {"question": "To prevent patient falls, you must ensure:", "Option A": "Floor is always wet", "Option B": "Call bell is within reach", "Option C": "Side rails are always down", "Option D": "Patient walks alone", "Correct Answer": "Call bell is within reach"},
    {"question": "The 'Time Out' before surgery is for:", "Option A": "A coffee break", "Option B": "Verifying patient, site, and procedure", "Option C": "Checking staff attendance", "Option D": "Discussing the news", "Correct Answer": "Verifying patient, site, and procedure"},
    {"question": "If a doctor gives a verbal order that seems incorrect, you:", "Option A": "Follow it anyway", "Option B": "Politely ask for clarification", "Option C": "Tell other nurses they are wrong", "Option D": "Do the opposite", "Correct Answer": "Politely ask for clarification"},
    {"question": "Effective listening involves:", "Option A": "Interrupting often", "Option B": "Maintaining eye contact and nodding", "Option C": "Looking at your phone", "Option D": "Thinking of your next response", "Correct Answer": "Maintaining eye contact and nodding"},
    {"question": "In a fire emergency (RACE), 'R' stands for:", "Option A": "Run away", "Option B": "Rescue those in danger", "Option C": "Report to HR", "Option D": "Ring the bell", "Correct Answer": "Rescue those in danger"},
    {"question": "Proper use of PPE is necessary to:", "Option A": "Look professional", "Option B": "Prevent cross-contamination", "Option C": "Follow fashion trends", "Option D": "Save on laundry costs", "Correct Answer": "Prevent cross-contamination"},
    {"question": "If you feel overwhelmed by your workload, you should:", "Option A": "Cry in the breakroom", "Option B": "Discuss with your supervisor", "Option C": "Quit without notice", "Option D": "Work slower", "Correct Answer": "Discuss with your supervisor"},
    {"question": "Conflict with a colleague should be resolved by:", "Option A": "Gossiping", "Option B": "Direct, professional conversation", "Option C": "Ignoring them forever", "Option D": "Screaming in the hallway", "Correct Answer": "Direct, professional conversation"},
    {"question": "Patient confidentiality applies to:", "Option A": "Only medical records", "Option B": "All personal and medical info", "Option C": "Only famous patients", "Option D": "Nothing after discharge", "Correct Answer": "All personal and medical info"},
    {"question": "A 'Near Miss' event should be:", "Option A": "Forgotten if no one was hurt", "Option B": "Reported to prevent future harm", "Option C": "Kept secret to avoid paperwork", "Option D": "Blamed on the patient", "Correct Answer": "Reported to prevent future harm"},
    {"question": "The most important factor in wound care is:", "Option A": "Speed", "Option B": "Aseptic technique", "Option C": "The brand of bandage", "Option D": "Patient preference only", "Correct Answer": "Aseptic technique"},
    {"question": "When a patient is in pain, you should:", "Option A": "Tell them it's normal", "Option B": "Assess and address promptly", "Option C": "Wait for the next shift", "Option D": "Give water only", "Correct Answer": "Assess and address promptly"},
    {"question": "Empathy differs from sympathy because it involves:", "Option A": "Feeling sorry for someone", "Option B": "Understanding their perspective", "Option C": "Giving them money", "Option D": "Crying with them", "Correct Answer": "Understanding their perspective"},
    {"question": "Staff resilience is best built by:", "Option A": "Working double shifts", "Option B": "Peer support and self-care", "Option C": "Never taking breaks", "Option D": "Hiding all emotions", "Correct Answer": "Peer support and self-care"},
    {"question": "Bio-medical waste should be segregated:", "Option A": "At the end of the day", "Option B": "At the point of generation", "Option C": "By the housekeeping only", "Option D": "In any available bin", "Correct Answer": "At the point of generation"},
    {"question": "The 'Rights of Medication' include:", "Option A": "Right time, Right patient", "Option B": "Right color, Right smell", "Option C": "Right price, Right brand", "Option D": "Right hospital, Right room", "Correct Answer": "Right time, Right patient"},
    {"question": "To improve patient satisfaction, we must:", "Option A": "Give free food", "Option B": "Communicate clearly and kindly", "Option C": "Ignore their complaints", "Option D": "Reduce staff count", "Correct Answer": "Communicate clearly and kindly"},
    {"question": "In the hospital, 'Silent Mode' refers to:", "Option A": "No talking at all", "Option B": "Reducing noise for patient healing", "Option C": "Turning off all monitors", "Option D": "Working in the dark", "Correct Answer": "Reducing noise for patient healing"},
    {"question": "If a patient falls under your watch, first:", "Option A": "Call the family", "Option B": "Assess for injury and call for help", "Option C": "Try to pull them up quickly", "Option D": "Run for the incident form", "Correct Answer": "Assess for injury and call for help"},
    {"question": "When answering the hospital phone, you should:", "Option A": "Just say 'Hello'", "Option B": "State department and your name", "Option C": "Wait for them to speak first", "Option D": "Keep them on hold", "Correct Answer": "State department and your name"},
    {"question": "Hand rubbing with alcohol should take:", "Option A": "2 seconds", "Option B": "20-30 seconds", "Option C": "5 minutes", "Option D": "Only after surgery", "Correct Answer": "20-30 seconds"},
    {"question": "A patient's call bell should be answered within:", "Option A": "1 hour", "Option B": "A few minutes", "Option C": "Next shift", "Option D": "When you are free", "Correct Answer": "A few minutes"},
    {"question": "Integrity in nursing means:", "Option A": "Doing right when no one looks", "Option B": "Following orders blindly", "Option C": "Being the fastest at tasks", "Option D": "Never taking a leave", "Correct Answer": "Doing right when no one looks"},
    {"question": "If you see a stranger in a restricted area:", "Option A": "Smile and wave", "Option B": "Politely ask for their ID/purpose", "Option C": "Ignore them", "Option D": "Call the CEO", "Correct Answer": "Politely ask for their ID/purpose"},
    {"question": "Standard precautions apply to:", "Option A": "Only HIV patients", "Option B": "All patients regardless of diagnosis", "Option C": "Only elderly patients", "Option D": "Only in the ICU", "Correct Answer": "All patients regardless of diagnosis"},
    {"question": "Effective debriefing after a critical incident helps:", "Option A": "Assign blame", "Option B": "Learn and provide emotional support", "Option C": "Finish the shift early", "Option D": "Hide mistakes", "Correct Answer": "Learn and provide emotional support"},
    {"question": "A nurse's signature in a chart means:", "Option A": "The patient is happy", "Option B": "The documented care was provided", "Option C": "It is the end of the day", "Option D": "They want a promotion", "Correct Answer": "The documented care was provided"},
    {"question": "To promote a culture of safety, we must:", "Option A": "Punish every error", "Option B": "Encourage open reporting of errors", "Option C": "Reduce clinical training", "Option D": "Keep secrets from the HOD", "Correct Answer": "Encourage open reporting of errors"},
    {"question": "Professionalism includes:", "Option A": "Arriving late", "Option B": "Appropriate attire and punctuality", "Option C": "Using slang with patients", "Option D": "Ignoring hospital policies", "Correct Answer": "Appropriate attire and punctuality"},
    {"question": "When a patient has passed away, the family needs:", "Option A": "Clinical data only", "Option B": "Compassion and privacy", "Option C": "The hospital bill immediately", "Option D": "To leave the room instantly", "Correct Answer": "Compassion and privacy"},
    {"question": "Shared decision making involves:", "Option A": "Only the doctor", "Option B": "Doctor, Patient, and Family", "Option C": "The insurance company only", "Option D": "The government", "Correct Answer": "Doctor, Patient, and Family"},
    {"question": "Body mechanics are important to:", "Option A": "Look strong", "Option B": "Prevent back injuries to staff", "Option C": "Work faster", "Option D": "Entertain patients", "Correct Answer": "Prevent back injuries to staff"},
    {"question": "Sharp containers should be replaced when:", "Option A": "Overflowing", "Option B": "3/4th full", "Option C": "Once a year", "Option D": "Never", "Correct Answer": "3/4th full"},
    {"question": "Documentation should be done:", "Option A": "Before the care", "Option B": "As soon as possible after care", "Option C": "Only if there is a problem", "Option D": "Once a week", "Correct Answer": "As soon as possible after care"},
    {"question": "Informed consent is the responsibility of:", "Option A": "The nurse", "Option B": "The performing physician", "Option C": "The patient's friend", "Option D": "The security guard", "Correct Answer": "The performing physician"},
    {"question": "The primary focus of JCI is:", "Option A": "Hospital profits", "Option B": "Patient safety and quality of care", "Option C": "Staff uniform colors", "Option D": "Cafeteria food", "Correct Answer": "Patient safety and quality of care"}
]

st.set_page_config(page_title="Medanta Assessment", layout="centered")

# --- HEADER ---
col1, col2, col3 = st.columns([2, 4, 2])
try:
    col1.image("MHPL logo 2.png", use_container_width=True)
    except:
    st.write("🏥 **Medanta Hospital Lucknow**")

st.title("Staff Assessment Tool")

@st.cache_data
def get_hybrid_questions(level_choice):
    try:
        df = pd.read_excel("questions.xlsx")
        df = df.fillna("") # Fixes the "NaN" display error
        
        # SMART SEARCH: Finds 'Level' or 'Levels' automatically
        level_col = next((c for c in df.columns if 'level' in c.lower()), None)
        if not level_col:
            st.error("Error: Could not find 'Level' column in Excel.")
            return pd.DataFrame()

        df[level_col] = df[level_col].astype(str).str.strip().str.lower()
        target = str(level_choice).strip().lower()
        
        tech_filtered = df[df[level_col] == target]
        if tech_filtered.empty:
            st.error(f"No questions found for '{level_choice}'. Check Excel spelling.")
            return pd.DataFrame()
            
        num_behav = random.randint(5, 8)
        num_tech = 25 - num_behav
        tech_sel = tech_filtered.sample(n=min(len(tech_filtered), num_tech))
        behav_sel = pd.DataFrame(random.sample(BEHAVIORAL_BANK, num_behav))
        return pd.concat([tech_sel, behav_sel], ignore_index=True).sample(frac=1).reset_index(drop=True)
    except Exception as e:
        st.error(f"Excel Error: {e}")
        return pd.DataFrame()

# --- LOGIN & ADMIN ---
if "started" not in st.session_state:
    st.session_state.update({"started": False, "review_mode": False, "q_index": 0, "answers": {}, "candidate_data": {}, "level": "beginner"})

if not st.session_state.started:
    with st.expander("Admin: Set Level"):
        key = st.text_input("Master Key", type="password")
        if key == ADMIN_MASTER_KEY:
            st.session_state.level = st.selectbox("Assign Level", ["beginner", "intermediate", "advanced"])

    st.subheader("Staff Information")
    name = st.text_input("Full Name")
    dob = st.date_input("Date of Birth", min_value=date(1960, 1, 1))
    qual = st.text_input("Qualification")
    cat = st.selectbox("Staff Category", ["Nursing", "Non-Nursing"])
    reg = st.text_input("Registration Number") if cat == "Nursing" else "N/A"
    college = st.text_input("College Name")
    contact = st.text_input("Contact Number (10 digits)")

    if st.button("Start Assessment"):
        if name and len(contact) == 10:
            st.session_state.candidate_data = {
                "name": name, "dob": str(dob), "qualification": qual, 
                "category": cat, "reg_no": reg, "college": college, "contact": contact
            }
            st.session_state.questions_df = get_hybrid_questions(st.session_state.level)
            if not st.session_state.questions_df.empty:
                st.session_state.started = True
                st.session_state.start_time = time.time()
                st.rerun()
        else:
            st.error("Please fill all fields and enter 10-digit mobile.")

# --- TESTING INTERFACE ---
elif st.session_state.started:
    q_df = st.session_state.questions_df
    elapsed = time.time() - st.session_state.start_time
    rem = max(0, TOTAL_TEST_TIME - elapsed)
    st.sidebar.metric("Time Remaining", f"{int(rem // 60)}m {int(rem % 60)}s")

    if st.session_state.review_mode:
        st.subheader("Review Answers")
        if st.button("Final Submit", type="primary") or rem <= 0:
            correct = sum(1 for i, row in q_df.iterrows() if st.session_state.answers.get(f"Q{i+1}") == row["Correct Answer"])
            score_pct = f"{round((correct/25)*100, 2)}%"
            duration = f"{round((time.time() - st.session_state.start_time)/60, 2)} mins"
            
            payload = {**st.session_state.candidate_data, "score": score_pct, "duration": duration, "answers": json.dumps(st.session_state.answers)}
            try:
                res = requests.post(BRIDGE_URL, json=payload, timeout=15)
                if res.status_code == 200:
                    st.balloons(); st.success(f"Submitted! Score: {score_pct}"); st.session_state.started = False
                else: st.error("Submission Error (Bridge Issue)")
            except: st.error("Connection Error (Check Bridge URL)")
    else:
        idx = st.session_state.q_index
        q_row = q_df.iloc[idx]
        st.write(f"### Question {idx+1}")
        st.write(q_row["question"])
        opts = [q_row["Option A"], q_row["Option B"], q_row["Option C"], q_row["Option D"]]
        ans = st.radio("Select choice:", opts, key=f"q{idx}")
        if st.button("Next Question"):
            st.session_state.answers[f"Q{idx+1}"] = ans
            if idx < 24: st.session_state.q_index += 1
            else: st.session_state.review_mode = True

            st.rerun()
