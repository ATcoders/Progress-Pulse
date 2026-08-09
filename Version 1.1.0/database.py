import sqlite3
import os
import calendar
import hashlib

folder = os.path.join(os.getenv("LOCALAPPDATA"), "TaskPlanner")
os.makedirs(folder, exist_ok=True)
db_path = os.path.join(folder, "taskplanner.db")


def get_connection():
    return sqlite3.connect(db_path)


def create_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_name TEXT NOT NULL,
        month INTEGER NOT NULL,
        year INTEGER NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS progress(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER,
        day INTEGER,
        completed INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


def add_task(task_name, month, year):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO tasks (task_name, month, year) VALUES (?, ?, ?)", (task_name, month, year))
    task_id = cursor.lastrowid

    for day in range(1, 32):
        cursor.execute(
            "INSERT INTO progress (task_id, day, completed) VALUES (?, ?, ?)",
            (task_id, day, 0)
        )

    conn.commit()
    conn.close()
    return task_id


def update_progress(task_id, day, status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE progress SET completed = ? WHERE task_id = ? AND day = ?",
        (status, task_id, day)
    )

    conn.commit()
    conn.close()


def get_tasks(month, year):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, task_name FROM tasks WHERE month=? AND year=?", (month, year))
    data = cursor.fetchall()
    conn.close()
    return data


def get_progress(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT day, completed FROM progress WHERE task_id=?", (task_id,))
    data = cursor.fetchall()
    conn.close()
    return data


def get_task_progress(month, year):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT tasks.task_name,
    SUM(progress.completed)
    FROM tasks
    LEFT JOIN progress
    ON tasks.id = progress.task_id
    WHERE tasks.month=? AND tasks.year=?
    GROUP BY tasks.id
    """, (month, year))

    data = cursor.fetchall()
    conn.close()
    return data


def get_week_progress(month, year, week_start_day, week_end_day):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT tasks.task_name,
    SUM(progress.completed)
    FROM tasks
    LEFT JOIN progress
    ON tasks.id = progress.task_id
    AND progress.day BETWEEN ? AND ?
    WHERE tasks.month=? AND tasks.year=?
    GROUP BY tasks.id
    """, (week_start_day, week_end_day, month, year))

    data = cursor.fetchall()
    conn.close()
    return data


def get_month_comparison(year):
    """
    Returns [(month_number, completion_percentage), ...] for all 12 months
    of the given year, aggregated across all tasks that existed each month.
    """
    conn = get_connection()
    cursor = conn.cursor()

    results = []
    for month in range(1, 13):
        days_in_month = calendar.monthrange(year, month)[1]

        cursor.execute("""
        SELECT COUNT(DISTINCT tasks.id), COALESCE(SUM(progress.completed), 0)
        FROM tasks
        LEFT JOIN progress ON tasks.id = progress.task_id
        WHERE tasks.month=? AND tasks.year=?
        """, (month, year))

        task_count, total_completed = cursor.fetchone()
        task_count = task_count or 0

        if task_count > 0:
            percentage = (total_completed / (task_count * days_in_month)) * 100
        else:
            percentage = 0

        results.append((month, percentage))

    conn.close()
    return results


def get_week_comparison(month, year):
    """
    Returns [(week_number, completion_percentage, week_start_day, week_end_day), ...]
    for every week of the given month.
    """
    conn = get_connection()
    cursor = conn.cursor()

    days_in_month = calendar.monthrange(year, month)[1]
    num_weeks = -(-days_in_month // 7)

    cursor.execute("SELECT COUNT(*) FROM tasks WHERE month=? AND year=?", (month, year))
    task_count = cursor.fetchone()[0] or 0

    results = []
    for w in range(num_weeks):
        week_start = w * 7 + 1
        week_end = min(week_start + 6, days_in_month)
        week_days = week_end - week_start + 1

        cursor.execute("""
        SELECT COALESCE(SUM(progress.completed), 0)
        FROM tasks
        LEFT JOIN progress
        ON tasks.id = progress.task_id
        AND progress.day BETWEEN ? AND ?
        WHERE tasks.month=? AND tasks.year=?
        """, (week_start, week_end, month, year))

        total_completed = cursor.fetchone()[0] or 0

        if task_count > 0:
            percentage = (total_completed / (task_count * week_days)) * 100
        else:
            percentage = 0

        results.append((w + 1, percentage, week_start, week_end))

    conn.close()
    return results


def get_eligible_months(threshold=90):
    """
    Certificate eligibility. Returns [(month, year, percentage), ...] for
    every month (across all years) that reached >= threshold% completion.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT month, year FROM tasks")
    month_year_pairs = cursor.fetchall()

    eligible = []
    for month, year in month_year_pairs:
        days_in_month = calendar.monthrange(year, month)[1]

        cursor.execute("""
        SELECT COUNT(DISTINCT tasks.id), COALESCE(SUM(progress.completed), 0)
        FROM tasks
        LEFT JOIN progress ON tasks.id = progress.task_id
        WHERE tasks.month=? AND tasks.year=?
        """, (month, year))

        task_count, total_completed = cursor.fetchone()
        task_count = task_count or 0

        if task_count > 0:
            percentage = (total_completed / (task_count * days_in_month)) * 100
        else:
            percentage = 0

        if percentage >= threshold:
            eligible.append((month, year, percentage))

    conn.close()
    eligible.sort(key=lambda item: (item[1], item[0]))
    return eligible


def clear_tasks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks")
    cursor.execute("DELETE FROM progress")
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# User accounts (Login / Signup)
# ---------------------------------------------------------------------------

def create_users_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()
    _ensure_full_name_column()


def _ensure_full_name_column():
    # Migration for databases created before full_name existed, so
    # existing installs don't break when this feature was added.
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    if "full_name" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
        conn.commit()
    conn.close()


def hash_password(password):
    # Simple one-way hash. Good enough for a local desktop app;
    # not meant for storing sensitive/shared account data.
    return hashlib.sha256(password.encode()).hexdigest()


def username_exists(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE username=?", (username,))
    found = cursor.fetchone() is not None
    conn.close()
    return found


def username_taken_by_other(username, exclude_username):
    """
    Like username_exists, but ignores the current user's own username.
    Used when editing a profile so saving without changing the username
    doesn't falsely report it as taken.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM users WHERE username=? AND username != ?",
        (username, exclude_username)
    )
    found = cursor.fetchone() is not None
    conn.close()
    return found


def signup_user(username, full_name, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, full_name, password_hash) VALUES (?, ?, ?)",
        (username, full_name, hash_password(password))
    )
    conn.commit()
    conn.close()


def verify_login(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return False
    return row[0] == hash_password(password)


def get_user_profile(username):
    """Returns (full_name, username) for the given account, or None."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT full_name, username FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row


def update_profile(current_username, new_full_name, new_username, new_password=None):
    """
    Updates full name and/or username, and optionally the password.
    Pass new_password=None to leave the password unchanged.
    """
    conn = get_connection()
    cursor = conn.cursor()

    if new_password:
        cursor.execute(
            "UPDATE users SET full_name=?, username=?, password_hash=? WHERE username=?",
            (new_full_name, new_username, hash_password(new_password), current_username)
        )
    else:
        cursor.execute(
            "UPDATE users SET full_name=?, username=? WHERE username=?",
            (new_full_name, new_username, current_username)
        )

    conn.commit()
    conn.close()


def reset_password(username, new_password):
    """
    Overwrites the stored password hash for an existing username.
    Caller is responsible for confirming the username exists first
    (via username_exists) before calling this.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET password_hash = ? WHERE username = ?",
        (hash_password(new_password), username)
    )
    conn.commit()
    conn.close()