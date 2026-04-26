import streamlit as st
import pickle
import pandas as pd
import random

# ---------------- LOAD DATASET ----------------
data = pd.read_csv("dataset.csv")

# ---------------- PDF IMPORTS ----------------
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ---------------- LOAD MODEL ----------------
model = pickle.load(open("talent_model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

# ---------------- SIDEBAR ----------------
st.sidebar.title("🚀 AI Talent System")

page = st.sidebar.radio("Navigate", [
    "🏠 Home",
    "👤 Profile",
    "📝 Assessment",
    "🤖 Interview Mode",
    "📊 Results"
])

# ---------------- QUESTION GENERATOR ----------------
templates = [
    "How do you usually handle {}?",
    "How confident are you in {}?",
    "Do you enjoy {}?",
    "What best describes your approach to {}?"
]

def generate_question():
    row = data.sample(1).iloc[0]
    text = row["question"]
    skill = row["skill"]

    question = random.choice(templates).format(text)
    return question, ["Yes", "Sometimes", "No"], skill

# ---------------- SESSION STATE ----------------
if "q_index" not in st.session_state:
    st.session_state.q_index = 0

if "scores" not in st.session_state:
    st.session_state.scores = {
        "analytical": 0,
        "creative": 0,
        "leadership": 0,
        "entrepreneurship": 0
    }

if "current_q" not in st.session_state:
    st.session_state.current_q = generate_question()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

MAX_Q = 5

# ---------------- PDF FUNCTION ----------------
def create_pdf(final_scores, strongest):
    doc = SimpleDocTemplate("report.pdf")
    styles = getSampleStyleSheet()

    content = []
    content.append(Paragraph("AI Talent Assessment Report", styles["Title"]))
    content.append(Spacer(1, 20))

    for skill, score in final_scores.items():
        content.append(Paragraph(f"{skill.capitalize()}: {round(score,2)}%", styles["Normal"]))
        content.append(Spacer(1, 10))

    content.append(Spacer(1, 20))
    content.append(Paragraph(f"Strongest Talent: {strongest.upper()}", styles["Heading2"]))

    doc.build(content)

# ---------------- HOME ----------------
if page == "🏠 Home":
    st.title("🚀 AI Talent Assessment System")

    st.markdown("""
    ### Discover your strengths using AI
    
    ✔ Smart Question Generation  
    ✔ Adaptive Assessment  
    ✔ Chatbot Interview Mode  
    ✔ Career Recommendation  
    """)

# ---------------- PROFILE ----------------
if page == "👤 Profile":
    st.title("👤 User Profile")

    name = st.text_input("Enter your name")
    age = st.number_input("Enter your age", 10, 60)
    grade = st.text_input("Enter your grade")

    if st.button("Save Profile"):
        st.session_state["name"] = name
        st.session_state["age"] = age
        st.session_state["grade"] = grade
        st.success("Profile saved successfully!")

# ---------------- ASSESSMENT ----------------
if page == "📝 Assessment":

    if "name" not in st.session_state:
        st.warning("⚠️ Please fill Profile first.")
        st.stop()

    st.title("📝 AI Adaptive Assessment")

    if st.session_state.q_index < MAX_Q:

        question, options, skill = st.session_state.current_q

        st.subheader(f"Question {st.session_state.q_index + 1}")
        st.write(question)

        answer = st.radio("Choose an option:", options)

        if st.button("Next"):

            if answer == "Yes":
                st.session_state.scores[skill] += 2
            elif answer == "Sometimes":
                st.session_state.scores[skill] += 1

            st.session_state.q_index += 1
            st.session_state.current_q = generate_question()

            st.rerun()

    else:
        st.success("Assessment Completed!")

        final_scores = st.session_state.scores
        strongest = max(final_scores, key=final_scores.get)

        st.session_state["final_scores"] = final_scores
        st.session_state["strongest"] = strongest

        st.write(f"### 🎯 {st.session_state['name']}, your talent is {strongest.upper()}")

        if st.button("Restart"):
            st.session_state.q_index = 0
            st.session_state.scores = {
                "analytical": 0,
                "creative": 0,
                "leadership": 0,
                "entrepreneurship": 0
            }
            st.session_state.current_q = generate_question()
            st.rerun()

# ---------------- INTERVIEW MODE ----------------
if page == "🤖 Interview Mode":

    st.title("🤖 AI Interview Mode")

    if "name" not in st.session_state:
        st.warning("⚠️ Please fill Profile first.")
        st.stop()

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("Type your answer...")

    if user_input:

        st.session_state.chat_history.append({"role": "user", "content": user_input})
        text = user_input.lower()

        if "problem" in text or "solve" in text:
            response = "🧠 You seem analytical! Explain your approach."
            st.session_state.scores["analytical"] += 1

        elif "idea" in text or "create" in text:
            response = "🎨 Creative! How do you generate ideas?"
            st.session_state.scores["creative"] += 1

        elif "team" in text or "lead" in text:
            response = "👑 Leadership detected! How do you manage people?"
            st.session_state.scores["leadership"] += 1

        elif "business" in text:
            response = "🚀 Entrepreneur mindset! What motivates you?"
            st.session_state.scores["entrepreneurship"] += 1

        else:
            response = "Interesting! Tell me more."

        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

    if st.button("Finish Interview"):
        final_scores = st.session_state.scores
        strongest = max(final_scores, key=final_scores.get)

        st.session_state["final_scores"] = final_scores
        st.session_state["strongest"] = strongest

        st.success("Interview completed! Go to Results 👉")

# ---------------- RESULTS ----------------
if page == "📊 Results":

    st.title("📊 Your Results")

    if "final_scores" not in st.session_state:
        st.warning("⚠️ Complete assessment first.")
    else:
        final_scores = st.session_state["final_scores"]
        strongest = st.session_state["strongest"]

        st.subheader("👤 User Details")
        st.write(f"Name: {st.session_state.get('name','')}")
        st.write(f"Age: {st.session_state.get('age','')}")
        st.write(f"Grade: {st.session_state.get('grade','')}")

        total = sum(final_scores.values())

        for skill, score in final_scores.items():
            percent = (score / total) * 100 if total > 0 else 0

            level = "High" if percent > 70 else "Moderate" if percent > 40 else "Low"

            st.write(f"{skill.capitalize()}: {round(percent, 2)}% ({level})")

        st.bar_chart(final_scores)

        st.markdown(f"## 🎯 Your Talent: **{strongest.upper()}**")

        df = pd.DataFrame([{
            "Name": st.session_state.get("name",""),
            "Strongest": strongest
        }])
        df.to_csv("results.csv", mode="a", header=False, index=False)

        create_pdf(final_scores, strongest)

        with open("report.pdf", "rb") as file:
            st.download_button(
                label="📄 Download Report",
                data=file,
                file_name="Talent_Report.pdf"
            )
