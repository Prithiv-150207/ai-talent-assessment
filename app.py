import streamlit as st
import pickle
import PyPDF2
from mcq_questions import mcq_questions

# ---------------- PDF DOWNLOAD IMPORTS ----------------
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ---------------- LOAD MODEL ----------------
model = pickle.load(open("talent_model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

# ---------------- PDF REPORT FUNCTION ----------------
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

# ---------------- TITLE ----------------
st.title("AI Talent Assessment System")
st.write("Answer the questions to discover your strongest talent.")
st.markdown("---")

# ---------------- PDF UPLOAD ----------------
st.header("📄 Upload Physiology PDF")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
pdf_text = ""

if uploaded_file is not None:
    pdf_reader = PyPDF2.PdfReader(uploaded_file)

    for page in pdf_reader.pages:
        text = page.extract_text()
        if text:
            pdf_text += text

    st.success("PDF Uploaded Successfully!")
    st.subheader("Extracted Text Preview")
    st.write(pdf_text[:1000])

# ---------------- MCQ SECTION ----------------
st.header("MCQ Assessment")

mcq_scores = {
    "analytical": 0,
    "creative": 0,
    "leadership": 0,
    "entrepreneurship": 0
}

for i, q in enumerate(mcq_questions):
    answer = st.slider(q["question"], 1, 5, 3, key=f"mcq_{i}")
    mcq_scores[q["skill"]] += answer

# ---------------- TEXT QUESTIONS ----------------
st.header("Descriptive Assessment")

questions = [
    "Describe a challenge you solved.",
    "How would you turn an idea into a product?",
    "How do you identify opportunities in the market?",
    "How would you solve a complex problem step by step?",
    "How do you handle disagreements in a group?"
]

answers = []

for i, q in enumerate(questions):
    ans = st.text_input(q, key=f"text_{i}")
    answers.append(ans)

# ---------------- SUBMIT ----------------
if st.button("Submit Assessment"):

    predicted_scores = {
        "analytical": 0,
        "creative": 0,
        "leadership": 0,
        "entrepreneurship": 0
    }

    # ---------------- PDF ANALYSIS ----------------
    if pdf_text.strip() != "":
        st.subheader("📄 PDF Analysis")

        chunks = pdf_text.split(".")[:10]

        pdf_results = []

        for chunk in chunks:
            if chunk.strip() != "":
                vec = vectorizer.transform([chunk])
                pred = model.predict(vec)[0]
                pdf_results.append(pred)

        st.write("PDF Insights:", pdf_results)

    # ---------------- AI PREDICTIONS ----------------
    st.subheader("AI Predictions")

    for ans in answers:
        if ans.strip() != "":
            vec = vectorizer.transform([ans])
            pred = model.predict(vec)[0]
            predicted_scores[pred] += 1

            st.write(f"Answer: {ans}")
            st.write(f"Predicted Skill: {pred}")
            st.write("---")

    # ---------------- COMBINE SCORES ----------------
    final_scores = {
        "analytical": mcq_scores["analytical"] + predicted_scores["analytical"],
        "creative": mcq_scores["creative"] + predicted_scores["creative"],
        "leadership": mcq_scores["leadership"] + predicted_scores["leadership"],
        "entrepreneurship": mcq_scores["entrepreneurship"] + predicted_scores["entrepreneurship"]
    }

    # ---------------- OUTPUT ----------------
    st.success("Assessment submitted!")
    st.markdown("## 📊 Final Analysis")

    total = sum(final_scores.values())

    for skill, score in final_scores.items():
        percent = (score / total) * 100 if total > 0 else 0
        st.write(f"{skill.capitalize()}: {round(percent, 2)}%")

    # ---------------- GRAPH ----------------
    st.subheader("Skill Distribution")
    st.bar_chart(final_scores)

    # ---------------- STRONGEST ----------------
    strongest = max(final_scores, key=final_scores.get)
    st.success(f"Your strongest talent is: {strongest.upper()}")

    # ---------------- AI EXPLANATION ----------------
    st.subheader("AI Explanation")

    explanation = []

    for ans in answers:
        ans = ans.lower()

        if "analyze" in ans or "step" in ans or "problem" in ans:
            explanation.append("problem-solving and analytical thinking")

        elif "idea" in ans or "create" in ans:
            explanation.append("creativity and idea generation")

        elif "team" in ans or "lead" in ans:
            explanation.append("leadership and teamwork")

        elif "business" in ans or "market" in ans or "startup" in ans:
            explanation.append("entrepreneurial thinking")

    if explanation:
        st.write(f"You are strong in {strongest} because your answers show {', '.join(set(explanation))}.")
    else:
        st.write("Your responses indicate general strengths across multiple areas.")

    # ---------------- CAREER ----------------
    st.subheader("Career Recommendation")

    if strongest == "analytical":
        st.info("Suggested Career: Data Scientist / Analyst")

    elif strongest == "creative":
        st.info("Suggested Career: Designer / Innovator")

    elif strongest == "leadership":
        st.info("Suggested Career: Manager / Team Leader")

    elif strongest == "entrepreneurship":
        st.info("Suggested Career: Startup Founder / Business Owner")

    # ---------------- REAL LIFE ----------------
    st.subheader("Real-Life Example")

    if strongest == "analytical":
        st.write("Example: A data analyst studying crop patterns to improve yield.")

    elif strongest == "creative":
        st.write("Example: Designing innovative apps or products.")

    elif strongest == "leadership":
        st.write("Example: Leading a team project successfully.")

    elif strongest == "entrepreneurship":
        st.write("Example: Building AGRIZEN-like startup solutions.")

    # ---------------- PDF DOWNLOAD ----------------
    create_pdf(final_scores, strongest)

    with open("report.pdf", "rb") as file:
        st.download_button(
            label="📄 Download Report (PDF)",
            data=file,
            file_name="Talent_Report.pdf",
            mime="application/pdf"
        )