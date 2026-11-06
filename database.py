import sqlite3
import json
from datetime import datetime

# =====================================================
# DATABASE CONFIGURATION
# =====================================================

DB_NAME = "learning_coach.db"


# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_connection():
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    return connection


# =====================================================
# INITIALIZE DATABASE
# =====================================================

def initialize_db():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learner_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            subject TEXT NOT NULL,
            goal TEXT NOT NULL,
            level TEXT NOT NULL,
            duration INTEGER NOT NULL,
            daily_study_time INTEGER NOT NULL,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            learner_id INTEGER,
            subject TEXT NOT NULL,
            plan_content TEXT NOT NULL,
            created_at TEXT,
            FOREIGN KEY (learner_id) REFERENCES learner_profiles(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            learner_id INTEGER,
            topic TEXT NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            attempted_at TEXT,
            FOREIGN KEY (learner_id) REFERENCES learner_profiles(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topic_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            learner_id INTEGER,
            topic TEXT NOT NULL,
            status TEXT DEFAULT 'Not Started',
            progress INTEGER DEFAULT 0,
            updated_at TEXT,
            UNIQUE(learner_id, topic),
            FOREIGN KEY (learner_id) REFERENCES learner_profiles(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            learner_id INTEGER,
            duration_minutes INTEGER NOT NULL,
            session_date TEXT,
            FOREIGN KEY (learner_id) REFERENCES learner_profiles(id)
        )
    """)

    connection.commit()
    connection.close()


# =====================================================
# SAVE LEARNER PROFILE
# =====================================================

def save_learner_profile(profile):
    required_fields = [
        "subject", "goal", "level", "duration", "study_time"
    ]

    for field in required_fields:
        if field not in profile or str(profile[field]).strip() == "":
            raise ValueError(f"Missing learner profile field: {field}")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO learner_profiles (
            name, subject, goal, level, duration,
            daily_study_time, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        profile.get("name", "Student"),
        profile["subject"].strip(),
        profile["goal"].strip(),
        profile["level"],
        int(profile["duration"]),
        int(profile["study_time"]),
        datetime.now().isoformat()
    ))

    learner_id = cursor.lastrowid
    connection.commit()
    connection.close()

    return learner_id


# =====================================================
# GET LATEST LEARNER PROFILE
# =====================================================

def get_latest_profile():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM learner_profiles
        ORDER BY id DESC
        LIMIT 1
    """)

    result = cursor.fetchone()
    connection.close()

    return dict(result) if result else None


def get_profile_by_id(learner_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM learner_profiles WHERE id = ?",
        (learner_id,)
    )

    result = cursor.fetchone()
    connection.close()

    return dict(result) if result else None


# =====================================================
# UPDATE EXISTING LEARNER PROFILE
# =====================================================

def update_learner_profile(learner_id, profile):
    required_fields = [
        "subject", "goal", "level", "duration", "study_time"
    ]

    for field in required_fields:
        if field not in profile or str(profile[field]).strip() == "":
            raise ValueError(f"Missing learner profile field: {field}")

    duration = int(profile["duration"])
    study_time = int(profile["study_time"])

    if duration < 1 or study_time < 1:
        raise ValueError(
            "Duration and daily study time must be positive."
        )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE learner_profiles
        SET name = ?,
            subject = ?,
            goal = ?,
            level = ?,
            duration = ?,
            daily_study_time = ?
        WHERE id = ?
    """, (
        profile.get("name", "Student").strip(),
        profile["subject"].strip(),
        profile["goal"].strip(),
        profile["level"],
        duration,
        study_time,
        learner_id
    ))

    updated_rows = cursor.rowcount

    connection.commit()
    connection.close()

    if updated_rows == 0:
        raise ValueError("Learner profile was not found.")

    return True


# =====================================================
# SAVE STUDY PLAN
# =====================================================

def save_study_plan(learner_id, plan):
    connection = get_connection()
    cursor = connection.cursor()

    plan_content = json.dumps(
        plan,
        ensure_ascii=False
    )

    cursor.execute("""
        INSERT INTO study_plans (
            learner_id,
            subject,
            plan_content,
            created_at
        )
        VALUES (?, ?, ?, ?)
    """, (
        learner_id,
        plan["subject"],
        plan_content,
        datetime.now().isoformat()
    ))

    plan_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return plan_id


# =====================================================
# GET LATEST STUDY PLAN
# =====================================================

def get_latest_study_plan(learner_id=None):
    connection = get_connection()
    cursor = connection.cursor()

    if learner_id is None:
        cursor.execute("""
            SELECT *
            FROM study_plans
            ORDER BY id DESC
            LIMIT 1
        """)
    else:
        cursor.execute("""
            SELECT *
            FROM study_plans
            WHERE learner_id = ?
            ORDER BY id DESC
            LIMIT 1
        """, (learner_id,))

    result = cursor.fetchone()
    connection.close()

    if result:
        data = dict(result)

        try:
            data["plan_content"] = json.loads(
                data["plan_content"]
            )

        except (json.JSONDecodeError, TypeError):
            data["plan_content"] = {
                "plan": data["plan_content"]
            }

        return data

    return None


# =====================================================
# SAVE QUIZ ATTEMPT
# =====================================================

def save_quiz_attempt(
    learner_id,
    topic,
    score,
    total_questions
):
    if total_questions <= 0:
        raise ValueError("Total questions must be positive.")

    if score < 0 or score > total_questions:
        raise ValueError("Invalid quiz score.")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO quiz_attempts (
            learner_id,
            topic,
            score,
            total_questions,
            attempted_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        learner_id,
        topic,
        score,
        total_questions,
        datetime.now().isoformat()
    ))

    attempt_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return attempt_id


# =====================================================
# GET QUIZ HISTORY
# =====================================================

def get_quiz_history(learner_id=None):
    connection = get_connection()
    cursor = connection.cursor()

    if learner_id is None:
        cursor.execute("""
            SELECT *
            FROM quiz_attempts
            ORDER BY id DESC
        """)
    else:
        cursor.execute("""
            SELECT *
            FROM quiz_attempts
            WHERE learner_id = ?
            ORDER BY id DESC
        """, (learner_id,))

    results = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return results


# =====================================================
# UPDATE TOPIC PROGRESS
# =====================================================

def update_topic_progress(
    learner_id,
    topic,
    status,
    progress
):
    if status not in [
        "Not Started",
        "In Progress",
        "Completed"
    ]:
        raise ValueError("Invalid topic status.")

    if not 0 <= progress <= 100:
        raise ValueError(
            "Progress must be between 0 and 100."
        )

    if status == "Completed":
        progress = 100

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO topic_progress (
            learner_id,
            topic,
            status,
            progress,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?)

        ON CONFLICT(learner_id, topic)
        DO UPDATE SET
            status = excluded.status,
            progress = excluded.progress,
            updated_at = excluded.updated_at
    """, (
        learner_id,
        topic,
        status,
        progress,
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()


# =====================================================
# GET TOPIC PROGRESS
# =====================================================

def get_topic_progress(learner_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM topic_progress
        WHERE learner_id = ?
        ORDER BY id DESC
    """, (learner_id,))

    results = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return results


# =====================================================
# RECORD STUDY TIME
# =====================================================

def record_study_time(
    learner_id,
    duration_minutes
):
    if duration_minutes <= 0:
        raise ValueError("Study time must be positive.")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO study_sessions (
            learner_id,
            duration_minutes,
            session_date
        )
        VALUES (?, ?, ?)
    """, (
        learner_id,
        duration_minutes,
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()


# =====================================================
# DASHBOARD STATISTICS
# =====================================================

def get_dashboard_stats(learner_id):
    connection = get_connection()
    cursor = connection.cursor()

    # Completed lessons
    cursor.execute("""
        SELECT COUNT(*)
        FROM topic_progress
        WHERE learner_id = ?
        AND status = 'Completed'
    """, (learner_id,))

    completed_lessons = cursor.fetchone()[0]

    # In-progress topics
    cursor.execute("""
        SELECT COUNT(*)
        FROM topic_progress
        WHERE learner_id = ?
        AND status = 'In Progress'
    """, (learner_id,))

    in_progress = cursor.fetchone()[0]

    # Total study time
    cursor.execute("""
        SELECT COALESCE(SUM(duration_minutes), 0)
        FROM study_sessions
        WHERE learner_id = ?
    """, (learner_id,))

    total_minutes = cursor.fetchone()[0]

    # Average progress
    cursor.execute("""
        SELECT COALESCE(AVG(progress), 0)
        FROM topic_progress
        WHERE learner_id = ?
    """, (learner_id,))

    average_progress = cursor.fetchone()[0]

    # Total quizzes
    cursor.execute("""
        SELECT COUNT(*)
        FROM quiz_attempts
        WHERE learner_id = ?
    """, (learner_id,))

    total_quizzes = cursor.fetchone()[0]

    # Average quiz score
    cursor.execute("""
        SELECT COALESCE(
            AVG(score * 100.0 / total_questions), 0
        )
        FROM quiz_attempts
        WHERE learner_id = ?
    """, (learner_id,))

    average_quiz_score = cursor.fetchone()[0]

    connection.close()

    return {
        "completed_lessons": completed_lessons,
        "in_progress": in_progress,
        "total_study_minutes": total_minutes,
        "total_study_hours": round(
            total_minutes / 60, 2
        ),
        "average_progress": round(
            average_progress, 1
        ),
        "total_quizzes": total_quizzes,
        "average_quiz_score": round(
            average_quiz_score, 1
        )
    }


# =====================================================
# GET STUDY SESSION HISTORY
# =====================================================

def get_study_sessions(learner_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM study_sessions
        WHERE learner_id = ?
        ORDER BY session_date DESC, id DESC
    """, (learner_id,))

    results = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return results


# =====================================================
# CALCULATE CURRENT LEARNING STREAK
# =====================================================

def get_learning_streak(learner_id):
    sessions = get_study_sessions(learner_id)

    study_dates = set()

    for session in sessions:
        try:
            session_date = datetime.fromisoformat(
                session["session_date"]
            ).date()

            study_dates.add(session_date)

        except (TypeError, ValueError):
            continue

    if not study_dates:
        return 0

    today = datetime.now().date()

    if today in study_dates:
        current_date = today
    else:
        current_date = today.fromordinal(
            today.toordinal() - 1
        )

    if current_date not in study_dates:
        return 0

    streak = 0

    while current_date in study_dates:
        streak += 1

        current_date = current_date.fromordinal(
            current_date.toordinal() - 1
        )

    return streak


# =====================================================
# INITIALIZE DATABASE
# =====================================================

initialize_db()