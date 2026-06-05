import streamlit as st
import sqlite3
import bcrypt
import os
from datetime import datetime

DB_DIR = "database"
DB_PATH = "database/users.db"
REPORT_DIR = "outputs/module_12_reports"

os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)


def create_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT,
            password TEXT,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            login_time TEXT
        )
    """)

    conn.commit()
    conn.close()


def hash_password(password):
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def check_password(password, hashed_password):
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def register_user(username, email, password):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (username, email, password, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (username, email, hash_password(password), str(datetime.now()))
        )
        conn.commit()
        return True, "User registered successfully."

    except sqlite3.IntegrityError:
        return False, "Username already exists."

    finally:
        conn.close()


def login_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password FROM users WHERE username = ?",
        (username,)
    )

    result = cursor.fetchone()

    if result is None:
        conn.close()
        return False, "User not found."

    hashed_password = result[0]

    if check_password(password, hashed_password):
        cursor.execute(
            """
            INSERT INTO login_history (username, login_time)
            VALUES (?, ?)
            """,
            (username, str(datetime.now()))
        )
        conn.commit()
        conn.close()
        return True, "Login successful."

    conn.close()
    return False, "Incorrect password."


def get_total_users():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]

    conn.close()
    return count


def get_login_count(username):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM login_history WHERE username = ?",
        (username,)
    )

    count = cursor.fetchone()[0]

    conn.close()
    return count


def get_last_login(username):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT login_time FROM login_history
        WHERE username = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (username,)
    )

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else "No login history"


def get_reports():
    if not os.path.exists(REPORT_DIR):
        return []

    reports = []

    for file in os.listdir(REPORT_DIR):
        if file.endswith(".pdf"):
            path = os.path.join(REPORT_DIR, file)
            reports.append({
                "file_name": file,
                "path": path,
                "created_time": datetime.fromtimestamp(
                    os.path.getctime(path)
                ).strftime("%Y-%m-%d %H:%M:%S")
            })

    return sorted(reports, key=lambda x: x["created_time"], reverse=True)


def initialize_session():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "username" not in st.session_state:
        st.session_state.username = ""


def show_register_page():
    st.subheader("Create New Account")

    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if username == "" or email == "" or password == "":
            st.error("Please fill all fields.")

        elif password != confirm_password:
            st.error("Passwords do not match.")

        elif len(password) < 6:
            st.error("Password must be at least 6 characters.")

        else:
            success, message = register_user(username, email, password)

            if success:
                st.success(message)
            else:
                st.error(message)


def show_login_page():
    st.subheader("User Login")

    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        success, message = login_user(username, password)

        if success:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(message)
            st.rerun()
        else:
            st.error(message)


def show_user_dashboard():
    username = st.session_state.username

    st.subheader(f"Welcome, {username}")

    reports = get_reports()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Users", get_total_users())

    with col2:
        st.metric("Your Login Count", get_login_count(username))

    with col3:
        st.metric("Total PDF Reports", len(reports))

    st.info(f"Last Login: {get_last_login(username)}")

    st.subheader("Generated Report History")

    if reports:
        for report in reports:
            with st.expander(report["file_name"]):
                st.write("Created Time:", report["created_time"])
                st.write("Path:", report["path"])

                with open(report["path"], "rb") as file:
                    st.download_button(
                        label="Download Report",
                        data=file,
                        file_name=report["file_name"],
                        mime="application/pdf"
                    )
    else:
        st.warning("No PDF reports found. Generate reports in Module 12 first.")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.success("Logged out successfully.")
        st.rerun()


def show_module_13_user_management():
    create_tables()
    initialize_session()

    st.title("Module 13: User Management & Report History")

    st.write(
        "This module adds user registration, login, session management, "
        "and report history to the AI Prescription Reader project."
    )

    if st.session_state.logged_in:
        show_user_dashboard()

    else:
        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            show_login_page()

        with tab2:
            show_register_page()

    st.warning(
        "This login system is created for internship project demonstration. "
        "For production, stronger authentication and security should be used."
    )