import threading
import time

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Live Quiz", page_icon="🏆")

TEACHER_PASSWORD = "teacher123"   

questions = [
    {
        "question": "What is the capital of France?",
        "options": ["Berlin", "Madrid", "Paris", "Rome"],
        "answer": "Paris",
    },
    {
        "question": "What is 7 x 8?",
        "options": ["54", "56", "58", "64"],
        "answer": "56",
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Venus", "Mars", "Jupiter", "Saturn"],
        "answer": "Mars",
    },
    {
        "question": "What is the capital of Nigeria?",
        "options": ["Lagos", "Abuja", "Kano", "Port Harcourt"],
        "answer": "Abuja",
    },
    {
        "question": "In what year did Nigeria gain independence?",
        "options": ["1957", "1960", "1963", "1966"],
        "answer": "1960",
    },
    {
        "question": "What is the square root of 144?",
        "options": ["10", "11", "12", "14"],
        "answer": "12",
    },
    {
        "question": "What is 15% of 200?",
        "options": ["20", "25", "30", "35"],
        "answer": "30",
    },
    {
        "question": "What is the smallest prime number?",
        "options": ["0", "1", "2", "3"],
        "answer": "2",
    },
    {
        "question": "Which is the largest planet in our solar system?",
        "options": ["Earth", "Saturn", "Neptune", "Jupiter"],
        "answer": "Jupiter",
    },
    {
        "question": "Which gas do plants absorb from the air for photosynthesis?",
        "options": ["Oxygen", "Carbon dioxide", "Nitrogen", "Hydrogen"],
        "answer": "Carbon dioxide",
    },
    {
        "question": "What is the chemical formula for water?",
        "options": ["CO2", "NaCl", "H2O", "O2"],
        "answer": "H2O",
    },
    {
        "question": "Who wrote the play Romeo and Juliet?",
        "options": ["Charles Dickens", "William Shakespeare", "Chinua Achebe", "Jane Austen"],
        "answer": "William Shakespeare",
    },
    {
        "question": "How many continents are there?",
        "options": ["5", "6", "7", "8"],
        "answer": "7",
    },
    {
        "question": "Which is the largest ocean on Earth?",
        "options": ["Atlantic", "Indian", "Arctic", "Pacific"],
        "answer": "Pacific",
    },
    {
        "question": "What is the fastest land animal?",
        "options": ["Lion", "Cheetah", "Horse", "Leopard"],
        "answer": "Cheetah",
    },
]


# ---------- Shared scoreboard (one copy for ALL visitors) ----------
@st.cache_resource
def get_board():
    return {"lock": threading.Lock(), "scores": {}}


board = get_board()


# ---------- Private state (one copy per visitor) ----------
if "submitted" not in st.session_state:
    st.session_state.submitted = False
    st.session_state.player = ""
    st.session_state.score = 0


# ---------- Live scoreboard ----------
@st.fragment(run_every=3)
def show_scoreboard():
    st.subheader("🏆 Live Scoreboard")

    with board["lock"]:
        scores = dict(board["scores"])

    if not scores:
        st.info("No one has submitted yet.")
        return

    rows = [
        {"Name": name, "Score": info["score"], "At": info["time"]}
        for name, info in scores.items()
    ]
    df = pd.DataFrame(rows).sort_values(
        by=["Score", "At"], ascending=[False, True]
    )
    df["Submitted"] = df["At"].apply(
        lambda t: time.strftime("%H:%M:%S", time.localtime(t))
    )
    df.insert(0, "Rank", range(1, len(df) + 1))
    st.dataframe(df[["Rank", "Name", "Score", "Submitted"]], hide_index=True)


# ---------- Sidebar: scoreboard + teacher controls ----------
with st.sidebar:
    show_scoreboard()

    st.divider()
    with st.expander("Teacher controls"):
        pw = st.text_input("Password", type="password")
        if st.button("Reset scoreboard"):
            if pw == TEACHER_PASSWORD:
                with board["lock"]:
                    board["scores"].clear()
                st.success("Scoreboard cleared.")
            else:
                st.error("Wrong password.")


# ---------- Main page ----------
st.title("📝 Live Quiz")

if st.session_state.submitted:
    st.success(f"Thanks, {st.session_state.player}! Your answers are in.")
    st.metric("Your score", f"{st.session_state.score} / {len(questions)}")
    if st.session_state.score == len(questions):
        st.balloons()
    st.write("Watch the scoreboard on the left to see how you rank.")
else:
    st.write("Enter your name, answer all questions, then click Submit.")

    with st.form("quiz_form"):
        name = st.text_input("Your name")

        answers = []
        for i, q in enumerate(questions):
            choice = st.radio(
                f"Q{i + 1}. {q['question']}",
                q["options"],
                index=None,
                key=f"question_{i}",
            )
            answers.append(choice)

        submit = st.form_submit_button("Submit")

    if submit:
        clean_name = name.strip()

        if not clean_name:
            st.warning("Please enter your name.")
        elif None in answers:
            st.warning("Please answer all questions.")
        else:
            score = sum(
                1 for a, q in zip(answers, questions) if a == q["answer"]
            )

            with board["lock"]:
                taken = clean_name.lower() in {
                    n.lower() for n in board["scores"]
                }
                if not taken:
                    board["scores"][clean_name] = {
                        "score": score,
                        "time": time.time(),
                    }

            if taken:
                st.error("That name is already on the scoreboard. Use another.")
            else:
                st.session_state.submitted = True
                st.session_state.player = clean_name
                st.session_state.score = score
                st.rerun()