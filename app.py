import streamlit as st
from datetime import datetime
import pandas as pd
# =====================================================
# IMPORTS
# =====================================================

from learning_plan import (
    create_learning_plan,
    display_learning_plan
)

from database import (
    save_learner_profile,
    get_latest_profile,
    save_study_plan,
    get_latest_study_plan,
    get_dashboard_stats,
    get_quiz_history,
    update_learner_profile,
    update_topic_progress,
    get_topic_progress,
    record_study_time,
    get_study_sessions,
    get_learning_streak
)

from quiz_manager import (
    create_quiz,
    evaluate_quiz,
    generate_feedback,
    save_quiz_result,
    identify_weak_topic,
    get_latest_adaptive_recommendation
)

from ai_service import generate_tutor_response


# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="AI Learn | Personalized Learning Coach",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =====================================================
# 2. SESSION STATE
# =====================================================

if "menu" not in st.session_state:
    st.session_state["menu"] = "Dashboard"

if "database_loaded" not in st.session_state:

    saved_profile = get_latest_profile()

    if saved_profile:

        learner_id = saved_profile["id"]

        st.session_state["learner_id"] = learner_id

        st.session_state["learner_profile"] = {
            "subject": saved_profile["subject"],
            "goal": saved_profile["goal"],
            "level": saved_profile["level"],
            "duration": saved_profile["duration"],
            "study_time": saved_profile["daily_study_time"]
        }

        saved_plan = get_latest_study_plan(learner_id)

        if saved_plan:

            plan_content = saved_plan["plan_content"]

            if isinstance(plan_content, dict):
                st.session_state["current_plan"] = plan_content
            else:
                st.session_state["current_plan"] = {
                    "subject": saved_profile["subject"],
                    "plan": str(plan_content)
                }

        else:
            st.session_state["current_plan"] = None

    else:

        st.session_state["learner_id"] = None
        st.session_state["learner_profile"] = {}
        st.session_state["current_plan"] = None

    st.session_state["database_loaded"] = True


# Quiz state

if "quiz_data" not in st.session_state:
    st.session_state["quiz_data"] = None

if "quiz_result" not in st.session_state:
    st.session_state["quiz_result"] = None

if "quiz_submitted" not in st.session_state:
    st.session_state["quiz_submitted"] = False


# AI Tutor chat state

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []


def go_to_page(page):
    st.session_state["menu"] = page


# =====================================================
# 3. CUSTOM CSS
# =====================================================


st.markdown("""
<style>

/* ================================
   COSMIC VIOLET AI THEME
================================ */

/* Main application */
.stApp {
    background: linear-gradient(135deg, #080D1B 0%, #10172A 55%, #11102B 100%);
    color: #F8FAFC;
}

/* Main content */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #11132B 0%, #171433 100%);
    border-right: 1px solid #29264D;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.5rem;
}

/* Sidebar text */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {
    color: #D8D9F0;
}

/* Branding */
.brand {
    font-size: 27px;
    font-weight: 800;
    color: #B69CFF;
}

.brand-subtitle {
    font-size: 13px;
    color: #A5A4C5;
}

/* Welcome section */
.welcome-title {
    font-size: 32px;
    font-weight: 750;
    color: #FFFFFF;
}

.welcome-subtitle {
    color: #A5B4CF;
    font-size: 16px;
}

.date-text {
    text-align: right;
    color: #A5B4CF;
    font-size: 13px;
}

/* Headings */
h1, h2, h3, h4 {
    color: #F8FAFC !important;
}

/* Paragraphs and labels */
.stMarkdown p,
.stMarkdown li,
.stMarkdown label {
    color: #D5DCEF;
}

/* Cards and containers */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #151E33;
    border: 1px solid #303B59;
    border-radius: 14px;
}

/* Buttons */
/* Premium Purple Buttons */
.stButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #7C3AED, #9333EA) !important;
    color: #FFFFFF !important;
    border: 1px solid #A78BFA !important;
    border-radius: 10px !important;
    min-height: 44px !important;
    font-weight: 700 !important;
    width: 100% !important;
    opacity: 1 !important;
    transition: all 0.2s ease;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: linear-gradient(135deg, #9333EA, #6D28D9) !important;
    color: #FFFFFF !important;
    border: 1px solid #C4B5FD !important;
    box-shadow: 0 0 18px rgba(139, 92, 246, 0.35);
}

/* Input fields */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background-color: #111A2D !important;
    color: #F8FAFC !important;
    border: 1px solid #384665 !important;
    border-radius: 9px !important;
}

.stSelectbox div[data-baseweb="select"] > div {
    background-color: #111A2D;
    color: #F8FAFC;
    border-color: #384665;
}

/* Radio buttons and checkboxes */
.stRadio label,
.stCheckbox label {
    color: #D5DCEF !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: #151E33;
    border: 1px solid #303B59;
    border-radius: 13px;
    padding: 18px;
}

[data-testid="stMetricLabel"] {
    color: #A5B4CF !important;
}

[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
}

/* Alerts */
.stAlert {
    border-radius: 12px;
}

/* Dataframes and tables */
[data-testid="stDataFrame"],
[data-testid="stTable"] {
    background-color: #151E33;
    border-radius: 10px;
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    color: #B9C4DA;
}

.stTabs [aria-selected="true"] {
    color: #C4B5FD !important;
    border-bottom-color: #8B5CF6 !important;
}

/* Dividers */
hr {
    border-color: #303B59;
}

/* Links */
a {
    color: #A78BFA !important;
}

/* Progress bars */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #7C3AED, #38BDF8);
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #0B1120;
}

::-webkit-scrollbar-thumb {
    background: #51417E;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: #8B5CF6;
}

/* Smooth transitions */
[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stMetric"] {
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

[data-testid="stMetric"]:hover {
    border-color: #8060CF;
    box-shadow: 0 0 15px rgba(139, 92, 246, 0.12);
}

/* Remove white Streamlit header */
[data-testid="stHeader"] {
    background: #0B1120 !important;
}

/* Make toolbar transparent */
[data-testid="stToolbar"] {
    background: transparent !important;
}

/* Hide the white decoration above the app */
[data-testid="stDecoration"] {
    background: transparent !important;
}

/* Dark top area */
header {
    background: #0B1120 !important;
}

/* Deploy and menu controls */
[data-testid="stHeader"] button {
    color: #F8FAFC !important;
}

.brand-container {
    display: flex;
    align-items: center;
    gap: 13px;
    padding: 12px 5px 26px 5px;
    margin-bottom: 24px;
    border-bottom: 1px solid #30294F;
}

.brand-logo {
    width: 52px;
    height: 52px;
    min-width: 52px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #9333EA, #5B4BDB, #2563EB);
    border: 1px solid rgba(196, 181, 253, 0.4);
    border-radius: 16px;
    box-shadow: 0 5px 22px rgba(124, 58, 237, 0.35);
}

.brand-text {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.brand-name {
    color: #FFFFFF !important;
    font-size: 23px;
    font-weight: 800;
    letter-spacing: -0.7px;
    line-height: 1.2;
}

.brand-name span {
    color: #A78BFA;
}

.brand-subtitle {
    color: #A5A4C5 !important;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 1.4px;
    line-height: 1.4;
}

/* =================================
   PREMIUM SIDEBAR NAVIGATION
================================= */

/* Navigation container */
[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 8px;
}

/* Each navigation item */
[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 10px !important;
    padding: 10px 12px !important;
    margin: 2px 0 !important;
    transition: all 0.2s ease;
}

/* Hide radio circles */
[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
    display: none !important;
}

/* Navigation text */
[data-testid="stSidebar"] div[role="radiogroup"] label p {
    color: #C7C9E5 !important;
    font-size: 14px !important;
    font-weight: 550 !important;
}

/* Hover effect */
[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: #252044 !important;
    border-color: #493779 !important;
}

/* Selected navigation item */
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(
        100deg,
        #512A91,
        #33245F
    ) !important;
    border: 1px solid #8855DC !important;
    box-shadow: 0 3px 14px rgba(124, 58, 237, 0.2);
}

/* Selected navigation text */
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}
/* Compact sidebar navigation */
[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child {
    display: none !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    padding: 5px 10px !important;
    margin: 2px 0 !important;
    min-height: 38px !important;
    border-radius: 9px !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label p {
    color: #C7C9E5 !important;
    font-size: 14px !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
    background: #422477 !important;
    border: 1px solid #8855DC !important;
}

/* Button-based sidebar navigation */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: 1px solid transparent !important;
    color: #D8D9F0 !important;
    text-align: left !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    min-height: 42px !important;
    font-size: 14px !important;
    font-weight: 550 !important;
    box-shadow: none !important;
}

/* Hover */
[data-testid="stSidebar"] .stButton > button:hover {
    background: #292044 !important;
    border-color: #574184 !important;
    color: #FFFFFF !important;
}

/* Active button */
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(100deg, #512A91, #33245F) !important;
    border: 1px solid #8855DC !important;
    color: #FFFFFF !important;
    box-shadow: 0 3px 14px rgba(124, 58, 237, 0.2) !important;
}
/* FINAL SIDEBAR POLISH */

[data-testid="stSidebar"] .stButton > button {
    border: 1px solid transparent !important;
    background: transparent !important;
    color: #D8D9F0 !important;
    border-radius: 9px !important;
    text-align: left !important;
    padding: 8px 12px !important;
    min-height: 40px !important;
    box-shadow: none !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: #252044 !important;
    border-color: #493779 !important;
}

[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(100deg, #512A91, #33245F) !important;
    border: 1px solid #8855DC !important;
    color: white !important;
}

/* Recommendation alert */
[data-testid="stAlert"] {
    background: #252044 !important;
    border: 1px solid #60449A !important;
    border-radius: 10px !important;
}

[data-testid="stAlert"] p,
[data-testid="stAlert"] div {
    color: #F1ECFF !important;
}

/* =================================
   DARK THEME FORM IMPROVEMENTS
================================= */

/* Form labels */
[data-testid="stWidgetLabel"] p {
    color: #E5DDFB !important;
    font-weight: 600 !important;
}

/* Text inputs and text areas */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: #182139 !important;
    color: #FFFFFF !important;
    border: 1px solid #6550A5 !important;
    border-radius: 9px !important;
}

/* Select boxes */
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background: #182139 !important;
    color: #FFFFFF !important;
    border-color: #6550A5 !important;
}

/* Number inputs */
[data-testid="stNumberInput"] input {
    background: #182139 !important;
    color: #FFFFFF !important;
    border-color: #6550A5 !important;
}

/* Placeholder text */
input::placeholder,
textarea::placeholder {
    color: #9BA5BD !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(100deg, #7040D9, #923CE8) !important;
    color: #FFFFFF !important;
    border: 1px solid #A879FF !important;
    border-radius: 9px !important;
    font-weight: 600 !important;
}

/* FIX DROPDOWN SELECTED TEXT VISIBILITY */

[data-testid="stSelectbox"] [data-baseweb="select"] {
    background-color: #182139 !important;
    border: 1px solid #8060D8 !important;
    border-radius: 9px !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"] div[class*="singleValue"],
[data-testid="stSelectbox"] [data-baseweb="select"] div[class*="SingleValue"] {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    opacity: 1 !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"] input {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    caret-color: #FFFFFF !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"] svg {
    fill: #FFFFFF !important;
}
/* Fix all button text visibility */
.stButton > button,
.stButton > button p {
    color: #FFFFFF !important;
    opacity: 1 !important;
}

/* Button appearance */
.stButton > button {
    background: linear-gradient(90deg, #7040D9, #923CE8) !important;
    border: 1px solid #A879FF !important;
}

/* Force dark styling on Streamlit dropdown */
div[data-testid="stSelectbox"] div[data-baseweb="select"],
div[data-testid="stSelectbox"] div[role="combobox"] {
    background-color: #182139 !important;
    color: #FFFFFF !important;
}

div[data-testid="stSelectbox"] div[data-baseweb="select"] * {
    color: #FFFFFF !important;
}

div[data-testid="stSelectbox"] svg {
    fill: #FFFFFF !important;
}

/* Knowledge Level dropdown - readable styling */
div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background-color: #FFFFFF !important;
    border: 1px solid #8060D8 !important;
    border-radius: 8px !important;
}

div[data-testid="stSelectbox"] div[data-baseweb="select"] * {
    color: #172033 !important;
}

div[data-testid="stSelectbox"] input {
    color: #172033 !important;
    -webkit-text-fill-color: #172033 !important;
}

/* Dropdown options */
ul[role="listbox"] li {
    background-color: #FFFFFF !important;
    color: #172033 !important;
}
/* Learning Path - Professional Controls */

.stButton > button {
    background: linear-gradient(135deg, #7C3AED, #9333EA) !important;
    color: #FFFFFF !important;
    border: 1px solid #A78BFA !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    min-height: 44px;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #6D28D9, #7E22CE) !important;
    border: 1px solid #C4B5FD !important;
}

/* Dropdown styling */
div[data-baseweb="select"] > div {
    background-color: #19243B !important;
    border: 1px solid #6551A8 !important;
    color: #FFFFFF !important;
}

div[data-baseweb="select"] * {
    color: #FFFFFF !important;
}
/* ===== PREMIUM 10/10 LEARNING COACH THEME ===== */

/* Main background */
.stApp {
    background: linear-gradient(
        135deg,
        #0B1020,
        #10172A,
        #11182B
    ) !important;
    color: #F8FAFC !important;
}

/* Main headings */
h1, h2, h3 {
    color: #F8FAFC !important;
    font-weight: 750 !important;
    letter-spacing: -0.5px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #111329,
        #191532
    ) !important;
    border-right: 1px solid #292345;
}

/* Cards */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #151D32;
    border: 1px solid #303B59;
    border-radius: 16px;
}

/* Text inputs */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background: #19243B !important;
    color: #FFFFFF !important;
    border: 1px solid #6551A8 !important;
    border-radius: 10px !important;
}

/* Labels */
.stTextInput label,
.stTextArea label,
.stNumberInput label,
.stSelectbox label {
    color: #DCE3F5 !important;
    font-weight: 600 !important;
}

/* Buttons */
.stButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(
        135deg,
        #7C3AED,
        #9333EA
    ) !important;
    color: white !important;
    border: 1px solid #A78BFA !important;
    border-radius: 11px !important;
    font-weight: 700 !important;
    min-height: 44px !important;
    transition: all 0.2s ease;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: linear-gradient(
        135deg,
        #9333EA,
        #6D28D9
    ) !important;
    box-shadow: 0 0 18px rgba(139,92,246,0.35);
    transform: translateY(-1px);
}

/* Dropdown */
div[data-baseweb="select"] > div {
    background: #19243B !important;
    border: 1px solid #6551A8 !important;
    border-radius: 10px !important;
}

div[data-baseweb="select"] * {
    color: #FFFFFF !important;
}

/* Progress bars */
.stProgress > div > div > div {
    background: linear-gradient(
        90deg,
        #7C3AED,
        #A78BFA
    ) !important;
}

/* Dividers */
hr {
    border-color: #29334D !important;
}

/* =====================================
   PREMIUM INLINE CODE HIGHLIGHTS
   ===================================== */

.stMarkdown p code,
.stMarkdown li code,
.stMarkdown h1 code,
.stMarkdown h2 code,
.stMarkdown h3 code {
    background: linear-gradient(
        135deg,
        #251B46,
        #34205D
    ) !important;

    color: #D8B4FE !important;

    border: 1px solid #8055D9 !important;
    border-radius: 7px !important;

    padding: 4px 9px !important;

    font-family: "Consolas", monospace !important;
    font-size: 0.92em !important;
    font-weight: 650 !important;

    box-shadow:
        0 0 8px rgba(139, 92, 246, 0.16);

    transition: all 0.2s ease;
}

/* Subtle hover effect */

.stMarkdown p code:hover,
.stMarkdown li code:hover {
    background: #493078 !important;
    border-color: #C4B5FD !important;

    box-shadow:
        0 0 12px rgba(167, 139, 250, 0.35);
}

/* =====================================
   DAY-WISE LEARNING SCHEDULE
   ===================================== */

.stMarkdown h2 {
    color: #C4B5FD !important;
    font-size: 27px !important;
    font-weight: 800 !important;
    padding: 14px 0 10px 0 !important;
    border-bottom: 1px solid rgba(167, 139, 250, 0.25);
    margin-top: 28px !important;
}

.stMarkdown h3 {
    color: #E9D5FF !important;
    font-size: 21px !important;
    font-weight: 700 !important;
    margin-top: 20px !important;
}

.stMarkdown ul {
    padding-left: 25px !important;
}

.stMarkdown li {
    color: #E2E8F0 !important;
    line-height: 1.85 !important;
    margin-bottom: 5px !important;
}

.stMarkdown hr {
    border-color: rgba(167, 139, 250, 0.25) !important;
}

/* =====================================
   PREMIUM LEARNING CONTENT
   ===================================== */

/* Learning schedule section headings */
.stMarkdown h3 {
    background: linear-gradient(
        135deg,
        rgba(124, 58, 237, 0.16),
        rgba(147, 51, 234, 0.06)
    );

    border-left: 4px solid #A78BFA;
    border-radius: 8px;

    padding: 12px 16px !important;
    margin-top: 24px !important;

    color: #DDD6FE !important;
}

/* Learning content */
.stMarkdown li {
    color: #E2E8F0 !important;
    line-height: 1.9 !important;
    padding-left: 4px;
}

/* Strong text labels */
.stMarkdown strong {
    color: #C4B5FD !important;
    font-weight: 750 !important;
}

/* Horizontal separators */
.stMarkdown hr {
    border: none !important;
    border-top: 1px solid rgba(167, 139, 250, 0.25) !important;
    margin: 28px 0 !important;
}

/* =====================================
   PREMIUM DASHBOARD STATISTIC CARDS
   ===================================== */

[data-testid="stMetric"] {
    background: linear-gradient(
        145deg,
        #19213A,
        #211A42
    ) !important;

    border: 1px solid #493477 !important;
    border-radius: 16px !important;

    padding: 22px 20px !important;

    box-shadow:
        0 5px 18px rgba(0, 0, 0, 0.20);

    transition: all 0.25s ease;
}

/* Hover effect */
[data-testid="stMetric"]:hover {
    transform: translateY(-4px);

    border-color: #A78BFA !important;

    box-shadow:
        0 8px 25px rgba(124, 58, 237, 0.22);
}

/* Metric labels */
[data-testid="stMetricLabel"] {
    color: #C4B5FD !important;
    font-weight: 650 !important;
}

/* Metric values */
[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-size: 2.2rem !important;
    font-weight: 800 !important;
}

/* Metric icons and delta text */
[data-testid="stMetricDelta"] {
    color: #A78BFA !important;
}

/* CONTENT LIBRARY RESOURCE BUTTONS */

[data-testid="stLinkButton"] a {
    background: linear-gradient(135deg, #7C3AED, #5B35B5) !important;
    color: #FFFFFF !important;
    border: 1px solid #A78BFA !important;
    border-radius: 10px !important;
    font-weight: 650 !important;
    box-shadow: 0 4px 14px rgba(124, 58, 237, 0.22) !important;
    transition: all 0.2s ease !important;
}

[data-testid="stLinkButton"] a:hover {
    background: linear-gradient(135deg, #8B5CF6, #6D28D9) !important;
    color: #FFFFFF !important;
    border-color: #C4B5FD !important;
    transform: translateY(-2px);
}
/* Lesson Progress dropdown selected text */
div[data-testid="stSelectbox"]:has(label) div[data-baseweb="select"] span {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}


</style>
""", unsafe_allow_html=True)



# =========================================================
# 4. SIDEBAR NAVIGATION
# =========================================================

with st.sidebar:

    # ---------------------------------
    # AI LEARN BRANDING
    # ---------------------------------

    st.markdown("""
        <div class="brand-container">
            <div class="brand-logo">
                <!-- Keep your existing logo SVG here if you have one -->
                🧠
            </div>
            <div class="brand-text">
                <div class="brand-name">AI Learn</div>
                <div class="brand-subtitle">YOUR PERSONAL AI COACH</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ---------------------------------
    # NAVIGATION MENU
    # ---------------------------------

    menu_items = {
        "Dashboard": "🏠",
        "Learning Path": "📚",
        "Lesson Progress": "🎯",
        "Study Time": "⏱️",
        "Practice Quiz": "✍️",
        "Content Library": "📖",
        "AI Tutor": "🤖",
        "Analytics": "📊",
        "Settings": "⚙️"
    }

    if "menu" not in st.session_state:
        st.session_state.menu = "Dashboard"

    for page, page_icon in menu_items.items():

        is_active = st.session_state.menu == page

        if st.button(
            f"{page_icon}  {page}",
            key=f"nav_{page.replace(' ', '_')}",
            use_container_width=True,
            type="primary" if is_active else "secondary"
        ):
            st.session_state.menu = page
            st.rerun()

    menu = st.session_state.menu

    st.divider()

    # ---------------------------------
    # SMART MODE
    # ---------------------------------

    st.markdown("⚡ **Smart Mode**")
    st.caption("AI-powered learning")

    st.write("")

    st.divider()

    # ---------------------------------
    # LEARNING STREAK
    # ---------------------------------

    st.markdown("📈 **Learning Streak**")

    sidebar_learner_id = st.session_state.get("learner_id")

    sidebar_streak = (
        get_learning_streak(sidebar_learner_id)
        if sidebar_learner_id else 0
    )

    st.markdown(
        f"""
        <h2 style="color:#A78BFA; margin-bottom:0;">
            {sidebar_streak} {"day" if sidebar_streak == 1 else "days"}
        </h2>
        """,
        unsafe_allow_html=True
    )

    st.caption("Keep learning every day!")

    st.divider()

    # ---------------------------------
    # WELCOME MESSAGE
    # ---------------------------------

    st.markdown("👋 **Welcome back!**")
    st.caption("Ready to learn?")





# =====================================================
# 5. DASHBOARD PAGE
# =====================================================

if menu == "Dashboard":

    col1, col2 = st.columns([3, 1])

    with col1:

        st.markdown(
            '<div class="welcome-title">Welcome back!</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="welcome-subtitle">'
            'Ready to continue your learning journey?'
            '</div>',
            unsafe_allow_html=True
        )

    with col2:

        today = datetime.now().strftime("%A, %B %d, %Y")

        st.markdown(
            f"""
            <div class="date-text">
                Today<br>
                <b style="color:#222;">{today}</b>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")
    st.write("")

    # Dashboard statistics

    learner_id = st.session_state.get("learner_id")

    if learner_id:

        stats = get_dashboard_stats(learner_id)

    else:

        stats = {
            "completed_lessons": 0,
            "in_progress": 0,
            "total_study_hours": 0,
            "average_progress": 0
        }

    metrics = [
        ("📚 Completed Lessons",
         str(stats["completed_lessons"])),

        ("🕒 In Progress",
         str(stats["in_progress"])),

        ("📈 Total Study Time",
         f'{stats["total_study_hours"]}h'),

        ("🎯 Average Progress",
         f'{stats["average_progress"]}%')
    ]

    columns = st.columns(4)

    for col, metric in zip(columns, metrics):

        with col:

            st.metric(metric[0], metric[1])

    st.write("")
    st.subheader("✨ AI Recommendations for You")
    learner_id = st.session_state.get("learner_id")

    if learner_id:
        recommendation = get_latest_adaptive_recommendation(
            learner_id
        )

        if recommendation:
            with st.container(border=True):
                st.markdown("### 🧠 Adaptive Learning Recommendation")

                st.write("**Topic:**", recommendation["topic"])
                st.write(
                    "**Latest Performance:**",
                    f'{recommendation["score_percentage"]}%'
                )
                st.write(
                    "**Performance Level:**",
                    recommendation["performance"]
                )

                st.info(recommendation["recommendation"])

                st.write(
                    "**Next Action:**",
                    recommendation["next_action"]
                )

    profile = st.session_state["learner_profile"]

    if profile:

        with st.container(border=True):

            st.markdown("### 🎯 Your Current Learning Goal")

            st.write("Subject:", profile["subject"])
            st.write("Goal:", profile["goal"])
            st.write("Level:", profile["level"])

            st.button(
                "View My Study Plan",
                on_click=go_to_page,
                args=("Learning Path",)
            )

    else:

        with st.container(border=True):

            st.markdown("### 🎯 Your learning journey starts here!")

            st.write(
                "Create a personalized study plan to receive "
                "AI-powered learning recommendations."
            )

            st.button(
                "Create Study Plan",
                on_click=go_to_page,
                args=("Learning Path",)
            )

    st.write("")
    st.subheader("🚀 Start Your Learning Journey")

    col1, col2, col3 = st.columns(3)

    with col1:

        with st.container(border=True):

            st.markdown("### 📖 Create Study Plan")
            st.write("Generate a personalized learning schedule.")

            st.button(
                "Create Study Plan",
                key="home_study",
                on_click=go_to_page,
                args=("Learning Path",)
            )

    with col2:

        with st.container(border=True):

            st.markdown("### 📝 Practice Quiz")
            st.write("Test your knowledge with AI-generated questions.")

            st.button(
                "Start Quiz",
                key="home_quiz",
                on_click=go_to_page,
                args=("Practice Quiz",)
            )

    with col3:

        with st.container(border=True):

            st.markdown("### 🤖 AI Tutor")
            st.write("Get explanations for your questions.")

            st.button(
                "Open AI Tutor",
                key="home_tutor",
                on_click=go_to_page,
                args=("AI Tutor",)
            )


# =====================================================
# 6. LEARNING PATH PAGE
# =====================================================

elif menu == "Learning Path":

    st.title("📖 Learning Path")
    st.write("Create your personalized learning schedule.")
    st.divider()

    with st.form("learning_setup_form"):

        subject = st.text_input(
            "Subject",
            placeholder="Example: Python Programming"
        )

        goal = st.text_area(
            "Learning Goal",
            placeholder="What do you want to achieve?"
        )

        level = st.radio(
            "Knowledge Level",
            ["Beginner", "Intermediate", "Advanced"],
            horizontal=True
        )

        duration = st.number_input(
            "Target Duration (Days)",
            min_value=1,
            max_value=365,
            value=7
        )

        study_time = st.number_input(
            "Daily Study Time (Minutes)",
            min_value=10,
            max_value=600,
            value=45
        )

        submitted = st.form_submit_button(
            "✨ Generate Study Plan"
        )

    if submitted:

        if not subject.strip() or not goal.strip():
            st.warning("Please enter subject and goal.")

        else:

            try:

                with st.spinner("Generating your study plan..."):

                    plan = create_learning_plan(
                        subject=subject,
                        goal=goal,
                        level=level,
                        duration=int(duration),
                        study_time=int(study_time)
                    )

                    learner_profile = {
                        "name": "Student",
                        "subject": subject,
                        "goal": goal,
                        "level": level,
                        "duration": int(duration),
                        "study_time": int(study_time)
                    }

                    learner_id = st.session_state.get("learner_id")

                    if learner_id is None:

                        learner_id = save_learner_profile(
                            learner_profile
                        )

                        st.session_state["learner_id"] = learner_id

                    else:

                        update_learner_profile(
                            learner_id,
                            learner_profile
                        )

                    st.session_state["learner_profile"] = learner_profile
                    st.session_state["current_plan"] = plan

                    save_study_plan(learner_id, plan)

                    st.success(
                        "Your study plan has been generated and saved!"
                    )

            except Exception as error:
                st.error(f"Unable to generate study plan: {error}")

    current_plan = st.session_state.get("current_plan")

    if current_plan:

        st.divider()
        st.subheader("Your Personalized Study Plan")
        display_learning_plan(current_plan)

        learner_id = st.session_state.get("learner_id")

    if learner_id:
        recommendation = get_latest_adaptive_recommendation(
            learner_id
        )

        if recommendation:
            st.divider()
            st.subheader("🧠 Adaptive Learning Guidance")

            st.write(
                "**Topic to focus on:**",
                recommendation["topic"]
            )

            st.write(
                "**Latest Quiz Score:**",
                f'{recommendation["score_percentage"]}%'
            )

            st.info(recommendation["recommendation"])

            st.success(
                f'Next Action: {recommendation["next_action"]}'
            )




# =====================================================
# 7. LESSON PROGRESS PAGE
# =====================================================

elif menu == "Lesson Progress":

    st.title("📚 Lesson Progress")
    st.write("Track your learning topics and update their completion status.")
    st.divider()

    learner_id = st.session_state.get("learner_id")

    if not learner_id:

        st.info("Create a learning profile first to track lesson progress.")

        if st.button("Create Study Plan", key="progress_create_plan"):
            st.session_state["menu"] = "Learning Path"
            st.rerun()

    else:

        st.subheader("Update a Learning Topic")

        with st.form("lesson_progress_form"):

            topic_name = st.text_input(
                "Topic or Lesson Name",
                placeholder="Example: Python Variables and Data Types"
            )

            topic_status = st.radio(
                "Learning Status",
                ["Not Started", "In Progress", "Completed"],
                horizontal=True
            )

            topic_percentage = st.slider(
                "Progress Percentage",
                min_value=0,
                max_value=100,
                value=0,
                step=5
            )

            save_topic = st.form_submit_button(
                "💾 Save Lesson Progress",
                use_container_width=True
            )

        if save_topic:

            if not topic_name.strip():

                st.warning("Please enter a topic or lesson name.")

            else:

                try:

                    effective_progress = (
                        100 if topic_status == "Completed"
                        else topic_percentage
                    )

                    update_topic_progress(
                        learner_id=learner_id,
                        topic=topic_name.strip(),
                        status=topic_status,
                        progress=effective_progress
                    )

                    st.success("Lesson progress saved successfully!")
                    st.rerun()

                except Exception as error:

                    st.error(f"Could not save lesson progress: {error}")

        st.divider()
        st.subheader("Your Learning Progress")

        try:

            progress_items = get_topic_progress(learner_id)

        except Exception as error:

            progress_items = []
            st.error(f"Could not load lesson progress: {error}")

        if progress_items:

            completed_count = sum(
                1 for item in progress_items
                if item["status"] == "Completed"
            )

            in_progress_count = sum(
                1 for item in progress_items
                if item["status"] == "In Progress"
            )

            average_progress = round(
                sum(item["progress"] for item in progress_items)
                / len(progress_items),
                1
            )

            metric1, metric2, metric3 = st.columns(3)

            metric1.metric("Topics Tracked", len(progress_items))
            metric2.metric("Completed Topics", completed_count)
            metric3.metric("Average Progress", f"{average_progress}%")

            for item in progress_items:

                with st.container(border=True):

                    heading_col, status_col = st.columns([3, 1])

                    with heading_col:
                        st.markdown(f"**{item['topic']}**")

                    with status_col:
                        st.caption(item["status"])

                    st.progress(
                        max(0, min(100, int(item["progress"]))) / 100
                    )

                    st.caption(f"{item['progress']}% complete")

            st.caption(
                f"{in_progress_count} topic(s) currently in progress."
            )

        else:

            st.info(
                "No topics tracked yet. Add your first topic using the form above."
            )


# =====================================================
# 8. STUDY TIME TRACKING PAGE
# =====================================================

elif menu == "Study Time":

    st.title("⏱️ Study Time Tracking")
    st.write("Record your study sessions and build a consistent learning habit.")
    st.divider()

    learner_id = st.session_state.get("learner_id")

    if not learner_id:

        st.info("Create a learner profile first to record study time.")

        if st.button("Create Study Plan", key="study_time_create_plan"):
            st.session_state["menu"] = "Learning Path"
            st.rerun()

    else:

        st.subheader("Record a Study Session")

        with st.form("study_time_form"):

            study_minutes = st.number_input(
                "How many minutes did you study?",
                min_value=1,
                max_value=1440,
                value=30,
                step=5
            )

            session_note = st.text_input(
                "What did you study? (Optional)",
                placeholder="Example: Python loops and functions"
            )

            save_session = st.form_submit_button(
                "💾 Save Study Session",
                use_container_width=True
            )

        if save_session:

            try:

                record_study_time(
                    learner_id=learner_id,
                    duration_minutes=int(study_minutes)
                )

                st.success(
                    f"Saved {int(study_minutes)} minutes of study time!"
                )

                st.rerun()

            except Exception as error:

                st.error(f"Could not save study session: {error}")

        sessions = get_study_sessions(learner_id)

        total_minutes = sum(
            int(session["duration_minutes"])
            for session in sessions
        )

        total_hours = total_minutes // 60
        remaining_minutes = total_minutes % 60

        current_streak = get_learning_streak(learner_id)

        st.divider()
        st.subheader("Your Study Summary")

        metric1, metric2, metric3 = st.columns(3)

        metric1.metric("Total Study Sessions", len(sessions))

        metric2.metric(
            "Total Study Time",
            f"{total_hours}h {remaining_minutes}m"
        )

        metric3.metric(
            "Current Learning Streak",
            f"{current_streak} {'day' if current_streak == 1 else 'days'}"
        )

        st.subheader("Recent Study Sessions")

        if sessions:

            history_rows = []

            for session in sessions[:15]:

                try:

                    display_date = datetime.fromisoformat(
                        session["session_date"]
                    ).strftime("%d %b %Y, %I:%M:%S %p")

                except (TypeError, ValueError):

                    display_date = str(
                        session.get("session_date", "")
                    )

                history_rows.append({
                    "Date": display_date,
                    "Duration (minutes)": session["duration_minutes"]
                })

            
            styled_history = pd.DataFrame(history_rows).style.set_table_styles([
                {
                    "selector": "th",
                    "props": [
                        ("background-color", "#29204A"),
                        ("color", "#C4B5FD"),
                        ("font-weight", "bold"),
                        ("border", "1px solid #493779"),
                        ("padding", "12px")
                    ]
                },
                {
                    "selector": "td",
                    "props": [
                        ("background-color", "#151D32"),
                        ("color", "#F8FAFC"),
                        ("border", "1px solid #303B55"),
                        ("padding", "12px")
                    ]
                },
                {
                    "selector": "tr:hover td",
                    "props": [
                        ("background-color", "#252044")
                    ]
                }
            ])
    
            st.dataframe(
                styled_history,
                width="stretch",
                hide_index=True,
                height=250
            )


        else:

            st.info(
                "No study sessions recorded yet. Save your first session above."
            )

        st.caption(
            "The learning streak counts consecutive calendar days "
            "with at least one saved study session."
        )


# =====================================================
# 
# =====================================================
# 9. PRACTICE QUIZ PAGE
# =====================================================

elif menu == "Practice Quiz":

    st.title("📝 Practice Quiz")
    st.caption("Test your knowledge and improve with Gemini AI.")
    st.divider()

    # QUIZ GENERATION FORM
    with st.container(border=True):

        st.subheader("✨ Create Your Quiz")
        st.caption("Choose your subject, topic, and difficulty level.")

        with st.form("quiz_generation_form"):

            quiz_subject = st.text_input(
                "Subject",
                placeholder="e.g. Python Programming"
            )

            quiz_topic = st.text_input(
                "Topic",
                placeholder="e.g. Python Variables"
            )

            col1, col2 = st.columns(2)
            st.markdown("""
<style>
div[data-testid="stSelectbox"] div[data-baseweb="select"] span {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    opacity: 1 !important;
}

div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background-color: #1B2540 !important;
}

div[data-baseweb="popover"] li {
    color: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)
            with col1:
                quiz_level = st.radio(
                    "Knowledge Level",
                    ["Beginner", "Intermediate", "Advanced"],
                    horizontal=True,
                    key="quiz_level_radio"
                )

            with col2:
                number_of_questions = st.radio(
                    "Number of Questions",
                    [5, 10, 15, 20],
                    horizontal=True,
                    key="number_of_questions_radio"
                )

            generate_button = st.form_submit_button(
                "✨ Generate Quiz",
                type="primary",
                use_container_width=True
            )

    # GENERATE QUIZ
    if generate_button:

        if not quiz_subject.strip() or not quiz_topic.strip():

            st.warning("Enter subject and topic.")

        else:

            try:

                with st.spinner("🤖 Gemini AI is preparing your quiz..."):

                    quiz = create_quiz(
                        subject=quiz_subject,
                        topic=quiz_topic,
                        level=quiz_level,
                        number_of_questions=number_of_questions
                    )

                    st.session_state["quiz_data"] = quiz
                    st.session_state["quiz_result"] = None
                    st.session_state["quiz_submitted"] = False

                st.success("Quiz generated successfully!")

            except Exception as error:

                st.error(f"Quiz generation error: {error}")

    # DISPLAY QUIZ
    quiz = st.session_state.get("quiz_data")

    if quiz:

        st.write("")

        with st.container(border=True):

            st.subheader(f"📚 {quiz['topic']} Quiz")
            st.caption(
                f"Total Questions: {len(quiz['questions'])}  |  "
                "Choose the correct option for each question."
            )

            if not st.session_state["quiz_submitted"]:

                with st.form("quiz_answer_form"):

                    answers = {}

                    for index, question in enumerate(
                        quiz["questions"], start=1
                    ):

                        st.markdown(
                            f"**Question {index}**"
                        )

                        st.markdown(question["question"])

                        answers[index] = st.radio(
                            "Select your answer",
                            ["A", "B", "C", "D"],
                            format_func=lambda option, q=question:
                                f"{option}. {q['options'][option]}",
                            key=f"answer_{index}"
                        )

                        st.divider()

                    submit_quiz = st.form_submit_button(
                        "🚀 Submit Quiz",
                        type="primary",
                        use_container_width=True
                    )

                if submit_quiz:

                    try:

                        result = evaluate_quiz(quiz, answers)

                        learner_id = st.session_state.get("learner_id")

                        if learner_id is None:

                            st.warning(
                                "Create a study plan before saving quiz results."
                            )

                        else:

                            save_quiz_result(
                                learner_id,
                                quiz["topic"],
                                result
                            )

                            st.session_state["quiz_result"] = result
                            st.session_state["quiz_submitted"] = True

                            st.rerun()

                    except Exception as error:

                        st.error(f"Evaluation error: {error}")

            # QUIZ RESULTS
            if st.session_state["quiz_submitted"]:

                result = st.session_state["quiz_result"]

                st.success("🎉 Quiz completed!")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Score",
                        f"{result['score']}/{result['total_questions']}"
                    )

                with col2:
                    st.metric(
                        "Percentage",
                        f"{result['percentage']}%"
                    )

                with col3:
                    st.metric(
                        "Correct Answers",
                        result["score"]
                    )

                st.divider()
                st.subheader("📋 Answer Review")

                for item in result["results"]:

                    with st.container(border=True):

                        st.markdown(
                            f"**Question {item['question_number']}: "
                            f"{item['question']}**"
                        )

                        st.write(
                            "Your Answer:",
                            item["student_answer"]
                        )

                        st.write(
                            "Correct Answer:",
                            item["correct_answer"]
                        )

                        if item["is_correct"]:
                            st.success("Correct!")
                        else:
                            st.error("Incorrect!")

                        st.info(item["explanation"])

                st.divider()

                st.subheader("🤖 Learning Feedback")

                with st.container(border=True):
                    st.write(generate_feedback(result))

                recommendation = identify_weak_topic(
                    result,
                    quiz["topic"]
                )

                st.divider()
                st.subheader("🎯 Your Adaptive Learning Recommendation")

                with st.container(border=True):

                    st.write("**Topic:**", recommendation["topic"])

                    st.write(
                        "**Performance:**",
                        recommendation["performance"]
                    )

                    st.write(
                        "**Next Action:**",
                        recommendation["next_action"]
                    )

                    if recommendation["needs_revision"]:
                        st.warning(recommendation["recommendation"])

                    elif recommendation["performance"] == "Good":
                        st.info(recommendation["recommendation"])

                    else:
                        st.success(recommendation["recommendation"])

                st.write("")

                if st.button(
                    "🔄 Try Another Quiz",
                    type="primary",
                    use_container_width=True
                ):

                    st.session_state["quiz_data"] = None
                    st.session_state["quiz_result"] = None
                    st.session_state["quiz_submitted"] = False

                    st.rerun()


# =====================================================

# =====================================================
# 10. CONTENT LIBRARY PAGE
# =====================================================

elif menu == "Content Library":

    st.title("📚 Content Library")
    st.caption(
        "Explore curated documentation, tutorials, and practice platforms."
    )
    st.divider()

    # -------------------------------------------------
    # LEARNING RESOURCES
    # -------------------------------------------------

    resources = [
        {
            "title": "Python Official Tutorial",
            "subject": "Python",
            "type": "Documentation",
            "level": "Beginner",
            "description": "Learn Python syntax, data types, control flow, functions, and modules.",
            "url": "https://docs.python.org/3/tutorial/",
            "source": "Python.org"
        },
        {
            "title": "Python Practice",
            "subject": "Python",
            "type": "Practice",
            "level": "Beginner",
            "description": "Solve Python programming exercises and build problem-solving skills.",
            "url": "https://www.hackerrank.com/domains/python",
            "source": "HackerRank"
        },
        {
            "title": "Python Learning",
            "subject": "Python",
            "type": "Interactive Learning",
            "level": "Beginner",
            "description": "Beginner-friendly Python lessons and hands-on exercises.",
            "url": "https://www.learnpython.org/",
            "source": "LearnPython.org"
        },
        {
            "title": "Java Tutorials",
            "subject": "Java",
            "type": "Documentation",
            "level": "Beginner",
            "description": "Study Java basics, classes, objects, inheritance, and collections.",
            "url": "https://dev.java/learn/",
            "source": "Oracle / Java"
        },
        {
            "title": "Java Practice",
            "subject": "Java",
            "type": "Practice",
            "level": "Beginner",
            "description": "Practise Java coding problems from beginner to advanced levels.",
            "url": "https://www.hackerrank.com/domains/java",
            "source": "HackerRank"
        },
        {
            "title": "SQL Tutorial",
            "subject": "SQL",
            "type": "Interactive Learning",
            "level": "Beginner",
            "description": "Learn SELECT queries, filtering, sorting, joins, and aggregation.",
            "url": "https://www.w3schools.com/sql/",
            "source": "W3Schools"
        },
        {
            "title": "PostgreSQL Documentation",
            "subject": "SQL",
            "type": "Documentation",
            "level": "Intermediate",
            "description": "Reference material for SQL statements and relational database concepts.",
            "url": "https://www.postgresql.org/docs/",
            "source": "PostgreSQL"
        },
        {
            "title": "HTML Tutorial",
            "subject": "Web Development",
            "type": "Interactive Learning",
            "level": "Beginner",
            "description": "Learn HTML elements, page structure, forms, and semantic markup.",
            "url": "https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Structuring_content",
            "source": "MDN"
        },
        {
            "title": "CSS Tutorial",
            "subject": "Web Development",
            "type": "Documentation",
            "level": "Beginner",
            "description": "Learn selectors, the box model, layouts, flexbox, and responsive design.",
            "url": "https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics",
            "source": "MDN"
        },
        {
            "title": "JavaScript Guide",
            "subject": "Web Development",
            "type": "Documentation",
            "level": "Intermediate",
            "description": "Explore JavaScript fundamentals, functions, objects, and asynchronous code.",
            "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
            "source": "MDN"
        },
        {
            "title": "Kaggle Learn",
            "subject": "Data Science & ML",
            "type": "Interactive Learning",
            "level": "Beginner",
            "description": "Take practical courses in Python, pandas, data visualization, and machine learning.",
            "url": "https://www.kaggle.com/learn",
            "source": "Kaggle"
        },
        {
            "title": "scikit-learn User Guide",
            "subject": "Data Science & ML",
            "type": "Documentation",
            "level": "Intermediate",
            "description": "Study machine learning workflows, preprocessing, model selection, and evaluation.",
            "url": "https://scikit-learn.org/stable/user_guide.html",
            "source": "scikit-learn"
        },
        {
            "title": "NumPy Quickstart",
            "subject": "Data Science & ML",
            "type": "Documentation",
            "level": "Beginner",
            "description": "Understand NumPy arrays, indexing, operations, and numerical computing.",
            "url": "https://numpy.org/doc/stable/user/quickstart.html",
            "source": "NumPy"
        },
        {
            "title": "Database Systems Concepts",
            "subject": "DBMS",
            "type": "Study Reference",
            "level": "Intermediate",
            "description": "Review database concepts such as relational models, SQL, transactions, and normalization.",
            "url": "https://www.db-book.com/",
            "source": "Database System Concepts"
        },
        {
            "title": "GeeksforGeeks Computer Science",
            "subject": "Computer Science",
            "type": "Study Reference",
            "level": "Beginner",
            "description": "Revise programming, data structures, algorithms, operating systems, and core CS topics.",
            "url": "https://www.geeksforgeeks.org/computer-science-fundamentals/",
            "source": "GeeksforGeeks"
        }
    ]

    # -------------------------------------------------
    # CURRENT LEARNING SUBJECT
    # -------------------------------------------------

    profile = st.session_state.get("learner_profile", {})
    current_subject = profile.get("subject", "")

    if current_subject:
        st.info(
            f"Your current learning subject is **{current_subject}**. "
            "Choose that subject in the filter to focus on related resources."
        )

    # -------------------------------------------------
    # SEARCH
    # -------------------------------------------------

    st.markdown("### 🔎 Find Learning Resources")

    search_text = st.text_input(
        "Search resources",
        placeholder="Search by title, topic, subject, or keyword...",
        key="library_search"
    )

    # -------------------------------------------------
    # FILTER OPTIONS
    # -------------------------------------------------

    available_subjects = ["All Subjects"] + sorted(
        {item["subject"] for item in resources}
    )

    available_types = ["All Types"] + sorted(
        {item["type"] for item in resources}
    )

    available_levels = [
        "All Levels",
        "Beginner",
        "Intermediate"
    ]

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        subject_filter = st.selectbox(
            "Subject",
            available_subjects,
            key="library_subject_filter"
        )

    with filter_col2:
        type_filter = st.selectbox(
            "Resource Type",
            available_types,
            key="library_type_filter"
        )

    with filter_col3:
        level_filter = st.selectbox(
            "Difficulty",
            available_levels,
            key="library_level_filter"
        )

    # -------------------------------------------------
    # FILTERING LOGIC
    # -------------------------------------------------

    filtered_resources = []

    for item in resources:

        matches_search = (
            not search_text.strip()
            or search_text.lower() in " ".join([
                item["title"],
                item["subject"],
                item["type"],
                item["level"],
                item["description"],
                item["source"]
            ]).lower()
        )

        matches_subject = (
            subject_filter == "All Subjects"
            or item["subject"] == subject_filter
        )

        matches_type = (
            type_filter == "All Types"
            or item["type"] == type_filter
        )

        matches_level = (
            level_filter == "All Levels"
            or item["level"] == level_filter
        )

        if (
            matches_search
            and matches_subject
            and matches_type
            and matches_level
        ):
            filtered_resources.append(item)

    # -------------------------------------------------
    # RESOURCE RESULTS HEADER
    # -------------------------------------------------

    st.divider()

    result_col1, result_col2 = st.columns([3, 1])

    with result_col1:
        st.subheader("📚 Learning Resources")
        st.caption(
            "Explore curated resources selected for your learning journey."
        )

    with result_col2:
        with st.container(border=True):
            st.metric(
                "Resources Found",
                len(filtered_resources)
            )

    # -------------------------------------------------
    # RESOURCE CARDS
    # -------------------------------------------------

    if filtered_resources:

        for row_start in range(0, len(filtered_resources), 2):

            card_columns = st.columns(2)

            for offset, col in enumerate(card_columns):

                resource_index = row_start + offset

                if resource_index >= len(filtered_resources):
                    continue

                item = filtered_resources[resource_index]

                with col:

                    with st.container(border=True):

                        st.markdown(f"### 📘 {item['title']}")

                        st.caption(
                            f"{item['subject']} • "
                            f"{item['type']} • "
                            f"{item['level']}"
                        )

                        st.divider()

                        st.write(item["description"])

                        st.caption(
                            f"🔗 Source: {item['source']}"
                        )

                        st.link_button(
                            "✨ Open Resource",
                            item["url"],
                            use_container_width=True,
                            type="primary"
                        )

    # -------------------------------------------------
    # NO RESULTS MESSAGE
    # -------------------------------------------------

    else:

        with st.container(border=True):
            st.info(
                "🔍 No resources found. "
                "Try changing your search term or filters."
            )

    # -------------------------------------------------
    # FOOTER
    # -------------------------------------------------

    st.divider()

    st.caption(
        "These are curated external learning resources. "
        "AI Learn does not host third-party course content."
    )


# =====================================================
# 11. AI TUTOR PAGE
# =====================================================


# =====================================================
# 11. AI TUTOR PAGE
# =====================================================

elif menu == "AI Tutor":
    
    # AI TUTOR DARK CHAT INPUT STYLING
    st.markdown("""
    <style>
    
[data-testid="stChatInput"] {
    background: #151D32 !important;
    border: 1px solid #8055D9 !important;
    border-radius: 14px !important;
    box-shadow: none !important;
}

[data-testid="stChatInput"] form {
    background: #151D32 !important;
}

[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #F8FAFC !important;
}

[data-testid="stChatInput"] button {
    background: #7C3AED !important;
    color: #FFFFFF !important;
}

[data-testid="stChatInput"] > div {
    background: #151D32 !important;
}

/* REMOVE WHITE BACKGROUND FROM CHAT FOOTER */

[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottomBlockContainer"],
[data-testid="stBottomBlockContainer"] > div {
    background: #0B1120 !important;
    background-color: #0B1120 !important;
    border-top: 1px solid #30294F !important;
    box-shadow: none !important;
}

/* CHAT INPUT */
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] form {
    background: #151D32 !important;
    background-color: #151D32 !important;
    border: 1px solid #8055D9 !important;
    border-radius: 14px !important;
}

/* INPUT TEXT */
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #F8FAFC !important;
}

/* SEND BUTTON */
[data-testid="stChatInput"] button {
    background: #7C3AED !important;
    color: #FFFFFF !important;
}

/* =====================================
   GLOBAL SELECTBOX VISIBILITY FIX
===================================== */

div[data-testid="stSelectbox"] [data-baseweb="select"] {
    background-color: #1B2540 !important;
    border: 1px solid #A78BFA !important;
    border-radius: 10px !important;
}

/* Selected value text */
div[data-testid="stSelectbox"] [data-baseweb="select"] div,
div[data-testid="stSelectbox"] [data-baseweb="select"] span,
div[data-testid="stSelectbox"] [data-baseweb="select"] input {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    opacity: 1 !important;
}

/* Dropdown menu */
div[data-baseweb="popover"],
div[data-baseweb="popover"] ul {
    background-color: #151D32 !important;
}

div[data-baseweb="popover"] li,
div[data-baseweb="popover"] li span {
    color: #FFFFFF !important;
    opacity: 1 !important;
}

div[data-baseweb="popover"] li:hover {
    background-color: #33245F !important;
}    </style>
    """, unsafe_allow_html=True)
    

    st.title("🤖 AI Tutor")
    st.caption(
        "Your personal AI-powered learning assistant. "
        "Ask questions and learn at your own pace."
    )
    st.divider()

    # LEARNER PROFILE
    profile = st.session_state.get("learner_profile", {})

    subject = profile.get("subject", "General")
    level = profile.get("level", "Beginner")

    col1, col2 = st.columns(2)

    with col1:
        st.info(f"📚 Learning Subject: {subject}")

    with col2:
        st.info(f"🎯 Knowledge Level: {level}")

    # INITIALIZE CHAT HISTORY
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # WELCOME SCREEN
    if not st.session_state["chat_history"]:

        with st.container(border=True):

            st.markdown("## 👋 Welcome to AI Tutor!")

            st.write(
                "I'm your personal learning assistant. "
                "Ask me questions and I'll explain concepts "
                "in a simple and understandable way."
            )

        st.subheader("💡 Suggested Questions")

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "📖 Explain a concept",
                use_container_width=True
            ):
                st.session_state["tutor_suggestion"] = (
                    f"Explain an important concept in {subject} "
                    "with a simple example."
                )
                st.rerun()

            if st.button(
                "🎯 Give me practice questions",
                use_container_width=True
            ):
                st.session_state["tutor_suggestion"] = (
                    f"Give me five practice questions about {subject}."
                )
                st.rerun()

        with col2:

            if st.button(
                "💻 Explain with an example",
                use_container_width=True
            ):
                st.session_state["tutor_suggestion"] = (
                    f"Explain a practical example related to {subject}."
                )
                st.rerun()

            if st.button(
                "📝 Help me prepare for exams",
                use_container_width=True
            ):
                st.session_state["tutor_suggestion"] = (
                    f"Help me prepare for an exam in {subject}."
                )
                st.rerun()

    # DISPLAY CHAT HISTORY
    for message in st.session_state["chat_history"]:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # CHAT INPUT
    suggestion = st.session_state.pop(
        "tutor_suggestion",
        None
    )

    question = st.chat_input(
        "Ask your learning question..."
    )

    if suggestion and not question:
        question = suggestion

    # GENERATE RESPONSE
    if question:

        previous_history = list(
            st.session_state["chat_history"]
        )

        st.session_state["chat_history"].append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):

            with st.spinner("🤖 AI Tutor is thinking..."):

                try:

                    response = generate_tutor_response(
                        question=question,
                        subject=subject,
                        level=level,
                        conversation_history=previous_history
                    )

                    st.markdown(response)

                    st.session_state["chat_history"].append({
                        "role": "assistant",
                        "content": response
                    })

                except Exception as error:

                    st.error(f"AI Tutor error: {error}")

                    st.session_state["chat_history"].pop()

    # CLEAR CONVERSATION
    st.divider()

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):

        st.session_state["chat_history"] = []
        st.rerun()


# =====================================================
# 12. ANALYTICS PAGE
# =====================================================


# =====================================================
# 12. ANALYTICS PAGE
# =====================================================

elif menu == "Analytics":

    # -------------------------------------------------
    # PAGE HEADER
    # -------------------------------------------------

    st.title("📊 Learning Analytics")

    st.caption(
        "Monitor your learning performance, "
        "track quiz results, and understand your progress."
    )

    st.divider()

    # -------------------------------------------------
    # LEARNER DATA
    # -------------------------------------------------

    learner_id = st.session_state.get("learner_id")

    if learner_id:

        stats = get_dashboard_stats(learner_id)

        # -------------------------------------------------
        # PERFORMANCE SUMMARY CARDS
        # -------------------------------------------------

        st.subheader("📈 Performance Overview")

        col1, col2, col3 = st.columns(3)

        with col1:
            with st.container(border=True):
                st.metric(
                    "📝 Total Quizzes",
                    stats["total_quizzes"]
                )
                st.caption("Quizzes attempted")

        with col2:
            with st.container(border=True):
                st.metric(
                    "🎯 Average Quiz Score",
                    f'{stats["average_quiz_score"]}%'
                )
                st.caption("Overall quiz performance")

        with col3:
            with st.container(border=True):
                st.metric(
                    "📚 Completed Lessons",
                    stats["completed_lessons"]
                )
                st.caption("Lessons completed")

        st.divider()

        # -------------------------------------------------
        # QUIZ HISTORY
        # -------------------------------------------------

        st.subheader("📋 Quiz History")

        st.caption(
            "Review your previous quiz attempts and scores."
        )

        
        history = get_quiz_history(learner_id)

        if history:

            history_rows = []

            for attempt in history:

                percentage = round(
                    attempt["score"] /
                    attempt["total_questions"] * 100,
                    1
                )

                history_rows.append({
                    "Topic": attempt["topic"],
                    "Score": (
                        f"{attempt['score']}/"
                        f"{attempt['total_questions']}"
                    ),
                    "Percentage": f"{percentage}%",
                    "Date": attempt["attempted_at"]
                })

            with st.container(border=True):

                history_df = pd.DataFrame(history_rows)

                st.dataframe(
                    history_df,
                    width="stretch",
                    hide_index=True,
                    height=250
                )

            st.write("")

            # QUIZ PERFORMANCE CHART

            st.subheader("📈 Quiz Performance")

            st.caption(
                "Track how your quiz scores change "
                "across different attempts."
            )

            chart_data = [
                {
                    "Attempt": index + 1,
                    "Percentage": round(
                        row["score"] /
                        row["total_questions"] * 100,
                        1
                    )
                }
                for index, row in enumerate(reversed(history))
            ]

            with st.container(border=True):

                st.line_chart(
                    chart_data,
                    x="Attempt",
                    y="Percentage",
                    color="#A78BFA"
                )

            # PERFORMANCE INSIGHT

            latest_score = chart_data[-1]["Percentage"]

            st.divider()

            st.subheader("💡 Learning Insight")

            if latest_score >= 80:

                st.success(
                    f"Excellent work! Your latest quiz score is "
                    f"{latest_score}%. Keep maintaining your progress."
                )

            elif latest_score >= 50:

                st.info(
                    f"You're making progress! Your latest quiz score "
                    f"is {latest_score}%. Continue practising to improve."
                )

            else:

                st.warning(
                    f"Your latest quiz score is {latest_score}%. "
                    "Focus on revising the topic and practising more questions."
                )

        else:

            with st.container(border=True):

                st.info(
                    "📚 No quiz attempts available yet. "
                    "Complete your first practice quiz to see "
                    "your learning analytics here."
                )

    else:

        with st.container(border=True):

            st.info(
                "Create a learning plan to start tracking your progress."
            )



# =====================================================
# 13. SETTINGS PAGE
# =====================================================


# =====================================================
# 13. SETTINGS PAGE
# =====================================================

elif menu == "Settings":

    # -------------------------------------------------
    # PAGE HEADER
    # -------------------------------------------------

    st.title("⚙️ Settings")

    st.caption(
        "Manage your learner profile and personalize "
        "your learning experience."
    )

    st.divider()

    # -------------------------------------------------
    # LOAD PROFILE
    # -------------------------------------------------

    profile = st.session_state.get("learner_profile", {})
    learner_id = st.session_state.get("learner_id")

    if profile and learner_id:

        # -------------------------------------------------
        # EDIT PROFILE
        # -------------------------------------------------

        with st.container(border=True):

            st.subheader("👤 Edit Learner Profile")

            st.caption(
                "Update your personal details and learning preferences. "
                "Your changes will be saved to the database."
            )

            with st.form("edit_learner_profile_form"):

                learner_name = st.text_input(
                    "Learner Name",
                    value=profile.get("name", "Student")
                )

                edited_subject = st.text_input(
                    "Subject",
                    value=profile.get("subject", "")
                )

                edited_goal = st.text_area(
                    "Learning Goal",
                    value=profile.get("goal", ""),
                    height=110
                )

                st.markdown("### 🎯 Learning Preferences")

                level_options = [
                    "Beginner",
                    "Intermediate",
                    "Advanced"
                ]

                current_level = profile.get(
                    "level",
                    "Beginner"
                )

                level_index = (
                    level_options.index(current_level)
                    if current_level in level_options else 0
                )

                edited_level = st.selectbox(
                    "Knowledge Level",
                    level_options,
                    index=level_index
                )

                col1, col2 = st.columns(2)

                with col1:

                    edited_duration = st.number_input(
                        "Target Duration (Days)",
                        min_value=1,
                        max_value=365,
                        value=max(
                            1,
                            int(profile.get("duration", 7))
                        )
                    )

                with col2:

                    edited_study_time = st.number_input(
                        "Daily Study Time (Minutes)",
                        min_value=1,
                        max_value=600,
                        value=max(
                            1,
                            int(profile.get("study_time", 45))
                        )
                    )

                save_profile = st.form_submit_button(
                    "💾 Save Profile Changes",
                    use_container_width=True,
                    type="primary"
                )

        # -------------------------------------------------
        # SAVE PROFILE
        # -------------------------------------------------

        if save_profile:

            if not learner_name.strip():

                st.error("Please enter your name.")

            elif not edited_subject.strip():

                st.error("Please enter a subject.")

            elif not edited_goal.strip():

                st.error("Please enter a learning goal.")

            else:

                updated_profile = {
                    "name": learner_name.strip(),
                    "subject": edited_subject.strip(),
                    "goal": edited_goal.strip(),
                    "level": edited_level,
                    "duration": int(edited_duration),
                    "study_time": int(edited_study_time)
                }

                try:

                    update_learner_profile(
                        learner_id,
                        updated_profile
                    )

                    st.session_state["learner_profile"] = updated_profile

                    st.success(
                        "Your learner profile has been updated successfully!"
                    )

                    st.rerun()

                except Exception as error:

                    st.error(
                        f"Could not update profile: {error}"
                    )

        # -------------------------------------------------
        # CURRENT PROFILE
        # -------------------------------------------------

        st.write("")

        st.subheader("📋 Current Profile")

        st.caption(
            "Your currently saved learning information."
        )

        col1, col2 = st.columns(2)

        with col1:

            with st.container(border=True):

                st.markdown("### 👤 Personal Details")

                st.write("**Name**")
                st.write(profile.get("name", "Student"))

                st.divider()

                st.write("**Subject**")
                st.write(profile.get("subject", ""))

                st.divider()

                st.write("**Knowledge Level**")
                st.write(profile.get("level", ""))

        with col2:

            with st.container(border=True):

                st.markdown("### 🎯 Learning Goals")

                st.write("**Learning Goal**")
                st.write(profile.get("goal", ""))

                st.divider()

                st.write("**Target Duration**")
                st.write(
                    f"{profile.get('duration', 0)} days"
                )

                st.divider()

                st.write("**Daily Study Time**")
                st.write(
                    f"{profile.get('study_time', 0)} minutes"
                )

    # -------------------------------------------------
    # NO PROFILE
    # -------------------------------------------------

    else:

        with st.container(border=True):

            st.subheader("👋 Welcome to AI Learn")

            st.info(
                "No learner profile found. "
                "Create a study plan first to set up your profile."
            )

            if st.button(
                "📚 Create Study Plan",
                use_container_width=True,
                type="primary"
            ):

                st.session_state["menu"] = "Learning Path"
                st.rerun()


