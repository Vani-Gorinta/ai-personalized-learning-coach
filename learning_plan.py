
from ai_service import generate_study_plan


def create_learning_plan(
    subject,
    goal,
    level,
    duration,
    study_time
):
    """
    Generate a personalized learning plan using AI.
    """

    # Validate user inputs
    if not subject or not subject.strip():
        raise ValueError("Please enter a subject.")

    if not goal or not goal.strip():
        raise ValueError("Please enter your learning goal.")

    if duration <= 0:
        raise ValueError("Duration must be greater than zero.")

    if study_time <= 0:
        raise ValueError("Daily study time must be greater than zero.")

    # Generate the study plan using Gemini AI
    ai_plan = generate_study_plan(
        subject=subject,
        goal=goal,
        level=level,
        duration=duration,
        study_time=study_time
    )

    # Store the generated plan
    learning_plan = {
        "subject": subject,
        "goal": goal,
        "level": level,
        "duration": duration,
        "daily_study_time": study_time,
        "plan": ai_plan
    }

    return learning_plan


def display_learning_plan(plan):
    """
    Display the generated learning plan in Streamlit.
    """

    import streamlit as st

    # Study Plan Overview
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #201A43, #30205C);
            padding: 22px;
            border-radius: 15px;
            border: 1px solid #6846A5;
            margin-bottom: 20px;
        ">
            <h3 style="
                color: #FFFFFF;
                margin-top: 0;
                margin-bottom: 20px;
            ">
                📚 Study Plan Overview
            </h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Subject and Goal
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📘 Subject**")
        st.write(plan["subject"])

    with col2:
        st.markdown("**🎯 Learning Goal**")
        st.write(plan["goal"])

    st.divider()

    # Level and Duration
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("**📊 Knowledge Level**")
        st.write(plan["level"])

    with col4:
        st.markdown("**📅 Target Duration**")
        st.write(f'{plan["duration"]} days')

    st.divider()

    # Daily Study Time
    st.markdown("**⏱️ Daily Study Time**")
    st.write(f'{plan["daily_study_time"]} minutes per day')

    # Study Schedule
    st.divider()

    st.markdown(
        """
        <h3 style="color: #B99AFF;">
            🗓️ Your Personalized Study Schedule
        </h3>
        """,
        unsafe_allow_html=True
    )

    # Display the complete AI-generated plan
    if plan.get("plan"):
        st.markdown(plan["plan"])
    else:
        st.warning("No study schedule is available.")
