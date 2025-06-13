import streamlit as st
import sqlite3
import os
from datetime import datetime, timedelta
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="ICU Bed Management System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database connection
def get_db_connection():
    """Create a connection to the SQLite database"""
    # Create database directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect('data/icu_system.db')
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

# Initialize database tables if they don't exist
def initialize_database():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Create users table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        first_name TEXT,
        last_name TEXT,
        is_admin INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create beds table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS beds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bed_number TEXT UNIQUE NOT NULL,
        bed_type TEXT NOT NULL,
        is_available INTEGER DEFAULT 1,
        description TEXT,
        price_per_day REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create bookings table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bed_id INTEGER REFERENCES beds(id),
        user_id INTEGER REFERENCES users(id),
        patient_name TEXT NOT NULL,
        patient_age INTEGER NOT NULL,
        patient_gender TEXT NOT NULL,
        contact_number TEXT NOT NULL,
        medical_condition TEXT NOT NULL,
        start_date DATE NOT NULL,
        end_date DATE,
        status TEXT DEFAULT 'pending',
        booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create ICU history table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS icu_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bed_id INTEGER REFERENCES beds(id),
        patient_name TEXT NOT NULL,
        patient_age INTEGER NOT NULL,
        patient_gender TEXT NOT NULL,
        admitted_date DATE NOT NULL,
        discharged_date DATE,
        treatment_details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Insert admin user if not exists
    cur.execute("SELECT * FROM users WHERE username = 'admin'")
    if cur.fetchone() is None:
        cur.execute('''
        INSERT INTO users (username, password, email, first_name, last_name, is_admin)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', ('admin', 'admin123', 'admin@icu.com', 'Admin', 'User', 1))
    
    # Insert some demo beds if the table is empty
    cur.execute("SELECT COUNT(*) FROM beds")
    if cur.fetchone()[0] == 0:
        beds_data = [
            ('ICU-001', 'general', 1, 'General ICU bed with ventilator support', 500.00),
            ('ICU-002', 'cardiac', 1, 'Cardiac ICU bed with heart monitoring', 650.00),
            ('ICU-003', 'neonatal', 1, 'Neonatal ICU for infants', 750.00),
            ('ICU-004', 'pediatric', 1, 'Pediatric ICU with child-friendly environment', 600.00),
            ('ICU-005', 'surgical', 1, 'Surgical ICU with post-operation monitoring', 700.00)
        ]
        for bed in beds_data:
            cur.execute('''
            INSERT INTO beds (bed_number, bed_type, is_available, description, price_per_day)
            VALUES (?, ?, ?, ?, ?)
            ''', bed)
    
    conn.commit()
    cur.close()
    conn.close()

# Initialize the database
initialize_database()

# Authentication functions
def authenticate(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, is_admin FROM users WHERE username = ? AND password = ?", (username, password))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def register_user(username, password, email, first_name, last_name):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('''
        INSERT INTO users (username, password, email, first_name, last_name)
        VALUES (?, ?, ?, ?, ?)
        ''', (username, password, email, first_name, last_name))
        conn.commit()
        result = True
    except Exception as e:
        conn.rollback()
        st.error(f"Registration failed: {e}")
        result = False
    finally:
        cur.close()
        conn.close()
    return result

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# Sidebar for navigation
with st.sidebar:
    st.title("ICU Bed System")
    
    if st.session_state.logged_in:
        st.write(f"Welcome, {'Admin' if st.session_state.is_admin else 'User'}")
        
        if st.button("Dashboard"):
            st.session_state.page = 'dashboard'
        
        if st.session_state.is_admin:
            if st.button("Admin Dashboard"):
                st.session_state.page = 'admin_dashboard'
            if st.button("Add ICU Bed"):
                st.session_state.page = 'add_bed'
            if st.button("Assign Bed"):
                st.session_state.page = 'assign_bed'
            if st.button("ICU History"):
                st.session_state.page = 'icu_history'
        else:
            if st.button("Book Bed"):
                st.session_state.page = 'book_bed'
            if st.button("My Bookings"):
                st.session_state.page = 'booking_history'
        
        if st.button("Profile"):
            st.session_state.page = 'profile'
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.is_admin = False
            st.session_state.page = 'home'
            st.rerun()
    else:
        if st.button("Home"):
            st.session_state.page = 'home'
        if st.button("Login"):
            st.session_state.page = 'login'
        if st.button("Register"):
            st.session_state.page = 'register'

# Home page
def show_home():
    st.title("Welcome to ICU Bed Management System")
    st.write("A real-time ICU bed availability and booking system")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("### Real-time Availability\nCheck the availability of ICU beds in real-time across various departments.")
    
    with col2:
        st.info("### Easy Booking\nBook available ICU beds for patients with just a few clicks.")
    
    with col3:
        st.info("### Booking History\nKeep track of all your ICU bed bookings and their status.")
    
    st.markdown("---")
    
    if not st.session_state.logged_in:
        st.write("Please login or create an account to access the system")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", key="home_login"):
                st.session_state.page = 'login'
                st.rerun()
        with col2:
            if st.button("Register", key="home_register"):
                st.session_state.page = 'register'
                st.rerun()
    else:
        if st.button("Go to Dashboard", key="goto_dashboard"):
            st.session_state.page = 'dashboard'
            st.rerun()
    
    st.markdown("---")
    
    st.subheader("About the System")
    st.write("""
    The ICU Bed Management System is designed to streamline the process of managing and booking ICU beds in healthcare facilities.
    It provides real-time information about bed availability, enabling efficient allocation of critical care resources.
    
    **Key Features:**
    - Real-time tracking of ICU bed availability
    - User-friendly booking interface for patients and staff
    - Comprehensive booking history and ICU usage records
    - Administrative tools for bed management and assignments
    - Secure and role-based access control
    """)

# Login page
def show_login():
    st.title("Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if username and password:
                user = authenticate(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user[0]
                    st.session_state.is_admin = user[1]
                    st.session_state.page = 'dashboard'
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.warning("Please enter both username and password")
    
    st.write("Don't have an account? [Register here](#)")
    if st.button("Go to Registration"):
        st.session_state.page = 'register'
        st.rerun()

# Registration page
def show_register():
    st.title("Register")
    
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Username")
            email = st.text_input("Email")
            first_name = st.text_input("First Name")
        
        with col2:
            last_name = st.text_input("Last Name")
            password = st.text_input("Password", type="password")
            password2 = st.text_input("Confirm Password", type="password")
        
        submit = st.form_submit_button("Register")
        
        if submit:
            if not (username and email and password and password2):
                st.warning("Please fill in all required fields")
            elif password != password2:
                st.error("Passwords do not match")
            else:
                if register_user(username, password, email, first_name, last_name):
                    st.success("Registration successful! You can now login.")
                    st.session_state.page = 'login'
                    st.rerun()
    
    st.write("Already have an account? [Login here](#)")
    if st.button("Go to Login"):
        st.session_state.page = 'login'
        st.rerun()

# Dashboard page for regular users
def show_dashboard():
    if not st.session_state.logged_in:
        st.warning("Please login to access the dashboard")
        return
    
    st.title("User Dashboard")
    
    # Fetch available beds
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT id, bed_number, bed_type, description, price_per_day 
    FROM beds WHERE is_available = 1
    """)
    available_beds = cur.fetchall()
    
    # Fetch recent bookings
    cur.execute("""
    SELECT b.id, bd.bed_number, b.patient_name, b.booking_date, b.start_date, b.status 
    FROM bookings b
    JOIN beds bd ON b.bed_id = bd.id
    WHERE b.user_id = ?
    ORDER BY b.booking_date DESC
    LIMIT 5
    """, (st.session_state.user_id,))
    recent_bookings = cur.fetchall()
    
    cur.close()
    conn.close()
    
    # Display available beds
    st.subheader("Available ICU Beds")
    if available_beds:
        bed_data = []
        for bed in available_beds:
            bed_types = {
                'general': 'General ICU',
                'cardiac': 'Cardiac ICU',
                'neonatal': 'Neonatal ICU',
                'pediatric': 'Pediatric ICU',
                'surgical': 'Surgical ICU'
            }
            bed_type_display = bed_types.get(bed[2], bed[2])
            bed_data.append({
                "Bed Number": bed[1],
                "Type": bed_type_display,
                "Description": bed[3] or "N/A",
                "Price per Day": f"${bed[4]}",
                "Action": bed[0]
            })
        
        df = pd.DataFrame(bed_data)
        df_display = df.copy()
        df_display["Action"] = "Book Now"
        
        st.dataframe(df_display, hide_index=True)
        
        selected_bed = st.selectbox("Select a bed to book", options=[f"{b[1]} - {b[2].capitalize()} ICU" for b in available_beds])
        if st.button("Book Selected Bed"):
            bed_id = available_beds[[b[1] for b in available_beds].index(selected_bed.split(" - ")[0])][0]
            st.session_state.selected_bed_id = bed_id
            st.session_state.page = 'book_bed'
            st.rerun()
    else:
        st.info("No ICU beds are available at the moment. Please check back later.")
    
    # Display recent bookings
    st.subheader("Your Recent Bookings")
    if recent_bookings:
        booking_data = []
        for booking in recent_bookings:
            status_badge = {
                'pending': '🟡 Pending',
                'confirmed': '🟢 Confirmed',
                'cancelled': '🔴 Cancelled',
                'completed': '🔵 Completed'
            }
            booking_data.append({
                "Booking ID": booking[0],
                "Bed Number": booking[1],
                "Patient Name": booking[2],
                "Booking Date": booking[3] if isinstance(booking[3], str) else booking[3].strftime("%b %d, %Y"),
                "Start Date": booking[4] if isinstance(booking[4], str) else booking[4].strftime("%b %d, %Y"),
                "Status": status_badge.get(booking[5], booking[5])
            })
        
        st.dataframe(pd.DataFrame(booking_data), hide_index=True)
        
        if st.button("View All Bookings"):
            st.session_state.page = 'booking_history'
            st.rerun()
    else:
        st.info("You have no recent bookings.")
        if st.button("Book a bed now"):
            st.session_state.page = 'book_bed'
            st.rerun()

# Admin Dashboard
def show_admin_dashboard():
    if not st.session_state.logged_in or not st.session_state.is_admin:
        st.warning("You do not have permission to access this page")
        return
    
    st.title("Admin Dashboard")
    
    # Fetch bed statistics
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM beds")
    total_beds = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM beds WHERE is_available = 1")
    available_beds_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM beds WHERE is_available = 0")
    occupied_beds_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM bookings WHERE status = 'pending'")
    pending_bookings_count = cur.fetchone()[0]
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total ICU Beds", total_beds)
    
    with col2:
        st.metric("Available Beds", available_beds_count)
    
    with col3:
        st.metric("Occupied Beds", occupied_beds_count)
    
    with col4:
        st.metric("Pending Bookings", pending_bookings_count)
    
    # Fetch all beds
    cur.execute("""
    SELECT id, bed_number, bed_type, is_available, price_per_day, updated_at
    FROM beds
    ORDER BY bed_number
    """)
    all_beds = cur.fetchall()
    
    # Fetch recent bookings
    cur.execute("""
    SELECT b.id, bd.bed_number, b.patient_name, u.username, b.start_date, b.status
    FROM bookings b
    JOIN beds bd ON b.bed_id = bd.id
    JOIN users u ON b.user_id = u.id
    ORDER BY b.booking_date DESC
    LIMIT 10
    """)
    recent_bookings = cur.fetchall()
    
    cur.close()
    conn.close()
    
    # Display beds management section
    st.subheader("ICU Bed Management")
    
    col1, col2 = st.columns([4, 1])
    with col2:
        st.write(" ")
        st.write(" ")
        add_bed_button = st.button("Add New Bed")
        if add_bed_button:
            st.session_state.page = 'add_bed'
            st.rerun()
        
        assign_bed_button = st.button("Assign Bed")
        if assign_bed_button:
            st.session_state.page = 'assign_bed'
            st.rerun()
    
    with col1:
        if all_beds:
            bed_data = []
            for bed in all_beds:
                bed_types = {
                    'general': 'General ICU',
                    'cardiac': 'Cardiac ICU',
                    'neonatal': 'Neonatal ICU',
                    'pediatric': 'Pediatric ICU',
                    'surgical': 'Surgical ICU'
                }
                bed_type_display = bed_types.get(bed[2], bed[2].capitalize())
                
                bed_data.append({
                    "ID": bed[0],
                    "Bed Number": bed[1],
                    "Type": bed_type_display,
                    "Status": "Available" if bed[3] else "Occupied",
                    "Price per Day": f"${bed[4]}",
                    "Last Updated": bed[5] if isinstance(bed[5], str) else bed[5].strftime("%b %d, %Y %H:%M")
                })
            
            st.dataframe(pd.DataFrame(bed_data), hide_index=True)
            
            # Edit bed functionality
            selected_bed_id = st.selectbox("Select a bed to edit", options=[f"{b[1]} (ID: {b[0]})" for b in all_beds])
            bed_id = int(selected_bed_id.split("ID: ")[1].strip(")"))
            
            if st.button("Edit Selected Bed"):
                st.session_state.edit_bed_id = bed_id
                st.session_state.page = 'edit_bed'
                st.rerun()
        else:
            st.info("No ICU beds have been added yet.")
    
    # Display recent bookings
    st.subheader("Recent Bookings")
    
    if recent_bookings:
        booking_data = []
        for booking in recent_bookings:
            status_badge = {
                'pending': '🟡 Pending',
                'confirmed': '🟢 Confirmed',
                'cancelled': '🔴 Cancelled',
                'completed': '🔵 Completed'
            }
            booking_data.append({
                "Booking ID": booking[0],
                "Bed Number": booking[1],
                "Patient Name": booking[2],
                "Booked By": booking[3],
                "Start Date": booking[4] if isinstance(booking[4], str) else booking[4].strftime("%b %d, %Y"),
                "Status": status_badge.get(booking[5], booking[5])
            })
        
        st.dataframe(pd.DataFrame(booking_data), hide_index=True)
        
        # Booking management
        selected_booking_id = st.number_input("Enter booking ID to manage", min_value=1, step=1)
        action = st.selectbox("Select action", ["Confirm", "Cancel", "Complete"])
        
        if st.button("Apply Action"):
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Verify booking exists
            cur.execute("SELECT id, bed_id, status FROM bookings WHERE id = ?", (selected_booking_id,))
            booking = cur.fetchone()
            
            if booking:
                if action == "Confirm" and booking[2] == 'pending':
                    cur.execute("UPDATE bookings SET status = 'confirmed', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (selected_booking_id,))
                    cur.execute("UPDATE beds SET is_available = 0 WHERE id = ?", (booking[1],))
                    st.success(f"Booking #{selected_booking_id} confirmed successfully")
                
                elif action == "Cancel":
                    cur.execute("UPDATE bookings SET status = 'cancelled', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (selected_booking_id,))
                    if booking[2] == 'confirmed':
                        cur.execute("UPDATE beds SET is_available = 1 WHERE id = ?", (booking[1],))
                    st.success(f"Booking #{selected_booking_id} cancelled successfully")
                
                elif action == "Complete" and booking[2] == 'confirmed':
                    cur.execute("UPDATE bookings SET status = 'completed', end_date = date('now'), updated_at = CURRENT_TIMESTAMP WHERE id = ?", (selected_booking_id,))
                    cur.execute("UPDATE beds SET is_available = 1 WHERE id = ?", (booking[1],))
                    
                    # Get booking details for history
                    cur.execute("""
                    SELECT bed_id, patient_name, patient_age, patient_gender, start_date
                    FROM bookings WHERE id = ?
                    """, (selected_booking_id,))
                    booking_details = cur.fetchone()
                    
                    # Add to ICU history
                    cur.execute("""
                    INSERT INTO icu_history (bed_id, patient_name, patient_age, patient_gender, admitted_date, discharged_date)
                    VALUES (?, ?, ?, ?, ?, date('now'))
                    """, (booking_details[0], booking_details[1], booking_details[2], booking_details[3], booking_details[4]))
                    
                    st.success(f"Booking #{selected_booking_id} completed successfully and added to ICU history")
                
                else:
                    st.warning("Invalid action for current booking status")
                
                conn.commit()
            else:
                st.error(f"Booking #{selected_booking_id} not found")
            
            cur.close()
            conn.close()
    else:
        st.info("No recent bookings found.")

# Add ICU Bed page
def show_add_bed():
    if not st.session_state.logged_in or not st.session_state.is_admin:
        st.warning("You do not have permission to access this page")
        return
    
    st.title("Add New ICU Bed")
    
    with st.form("add_bed_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            bed_number = st.text_input("Bed Number *")
            bed_type = st.selectbox("Bed Type *", options=[
                "general", "cardiac", "neonatal", "pediatric", "surgical"
            ], format_func=lambda x: {
                'general': 'General ICU',
                'cardiac': 'Cardiac ICU',
                'neonatal': 'Neonatal ICU',
                'pediatric': 'Pediatric ICU',
                'surgical': 'Surgical ICU'
            }.get(x, x.capitalize()))
        
        with col2:
            price_per_day = st.number_input("Price per Day ($) *", min_value=1.0, value=500.0, step=50.0)
            is_available = st.checkbox("Available for Booking", value=True)
        
        description = st.text_area("Description", height=100)
        
        submit = st.form_submit_button("Add ICU Bed")
        
        if submit:
            if not bed_number or not bed_type:
                st.warning("Please fill in all required fields")
            else:
                conn = get_db_connection()
                cur = conn.cursor()
                
                try:
                    cur.execute("""
                    INSERT INTO beds (bed_number, bed_type, is_available, description, price_per_day)
                    VALUES (?, ?, ?, ?, ?)
                    """, (bed_number, bed_type, 1 if is_available else 0, description, price_per_day))
                    
                    conn.commit()
                    st.success(f"ICU Bed {bed_number} added successfully!")
                    
                    # Reset form or redirect
                    if st.button("Return to Admin Dashboard"):
                        st.session_state.page = 'admin_dashboard'
                        st.rerun()
                except Exception as e:
                    conn.rollback()
                    st.error(f"Error adding bed: {e}")
                finally:
                    cur.close()
                    conn.close()

# Edit ICU Bed page
def show_edit_bed():
    if not st.session_state.logged_in or not st.session_state.is_admin:
        st.warning("You do not have permission to access this page")
        return
    
    if 'edit_bed_id' not in st.session_state:
        st.error("No bed selected for editing")
        return
    
    bed_id = st.session_state.edit_bed_id
    
    # Fetch bed details
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT bed_number, bed_type, is_available, description, price_per_day
    FROM beds WHERE id = ?
    """, (bed_id,))
    bed = cur.fetchone()
    cur.close()
    conn.close()
    
    if not bed:
        st.error("Bed not found")
        return
    
    st.title(f"Edit ICU Bed: {bed[0]}")
    
    with st.form("edit_bed_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            bed_number = st.text_input("Bed Number *", value=bed[0])
            bed_type = st.selectbox("Bed Type *", options=[
                "general", "cardiac", "neonatal", "pediatric", "surgical"
            ], index=["general", "cardiac", "neonatal", "pediatric", "surgical"].index(bed[1]),
            format_func=lambda x: {
                'general': 'General ICU',
                'cardiac': 'Cardiac ICU',
                'neonatal': 'Neonatal ICU',
                'pediatric': 'Pediatric ICU',
                'surgical': 'Surgical ICU'
            }.get(x, x.capitalize()))
        
        with col2:
            price_per_day = st.number_input("Price per Day ($) *", min_value=1.0, value=float(bed[4]), step=50.0)
            is_available = st.checkbox("Available for Booking", value=bed[2])
        
        description = st.text_area("Description", value=bed[3] if bed[3] else "", height=100)
        
        submit = st.form_submit_button("Update ICU Bed")
        
        if submit:
            if not bed_number or not bed_type:
                st.warning("Please fill in all required fields")
            else:
                conn = get_db_connection()
                cur = conn.cursor()
                
                try:
                    cur.execute("""
                    UPDATE beds 
                    SET bed_number = ?, bed_type = ?, is_available = ?, description = ?, price_per_day = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """, (bed_number, bed_type, 1 if is_available else 0, description, price_per_day, bed_id))
                    
                    conn.commit()
                    st.success(f"ICU Bed {bed_number} updated successfully!")
                    
                    if st.button("Return to Admin Dashboard"):
                        st.session_state.page = 'admin_dashboard'
                        st.rerun()
                except Exception as e:
                    conn.rollback()
                    st.error(f"Error updating bed: {e}")
                finally:
                    cur.close()
                    conn.close()
    
    if st.button("Cancel", key="cancel_edit"):
        st.session_state.page = 'admin_dashboard'
        st.rerun()

# Book Bed page
def show_book_bed():
    if not st.session_state.logged_in:
        st.warning("Please login to book a bed")
        return
    
    st.title("Book an ICU Bed")
    
    # Fetch available beds
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT id, bed_number, bed_type, price_per_day
    FROM beds WHERE is_available = 1
    ORDER BY bed_number
    """)
    available_beds = cur.fetchall()
    cur.close()
    conn.close()
    
    if not available_beds:
        st.warning("No ICU beds are available at the moment")
        if st.button("Return to Dashboard"):
            st.session_state.page = 'dashboard'
            st.rerun()
        return
    
    with st.form("book_bed_form"):
        # Bed selection
        if 'selected_bed_id' in st.session_state:
            default_bed_index = [b[0] for b in available_beds].index(st.session_state.selected_bed_id) if st.session_state.selected_bed_id in [b[0] for b in available_beds] else 0
        else:
            default_bed_index = 0
        
        bed_options = [f"{b[1]} - {b[2].capitalize()} ICU (${b[3]}/day)" for b in available_beds]
        selected_bed = st.selectbox("Select ICU Bed *", options=bed_options, index=default_bed_index)
        selected_bed_id = available_beds[bed_options.index(selected_bed)][0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input("Admission Date *", min_value=datetime.now().date(), value=datetime.now().date())
        
        st.subheader("Patient Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            patient_name = st.text_input("Patient Full Name *")
            patient_age = st.number_input("Patient Age *", min_value=0, max_value=120, step=1)
        
        with col2:
            patient_gender = st.selectbox("Patient Gender *", options=["male", "female", "other"], format_func=lambda x: x.capitalize())
            contact_number = st.text_input("Contact Number *")
        
        medical_condition = st.text_area("Medical Condition/Reason for ICU Admission *", height=100)
        
        st.info("Your booking will be pending until confirmed by an administrator. You will be notified once your booking is confirmed.")
        
        submit = st.form_submit_button("Book ICU Bed")
        
        if submit:
            if not (patient_name and patient_age and contact_number and medical_condition):
                st.warning("Please fill in all required fields")
            else:
                conn = get_db_connection()
                cur = conn.cursor()
                
                try:
                    cur.execute("""
                    INSERT INTO bookings (bed_id, user_id, patient_name, patient_age, patient_gender, contact_number, medical_condition, start_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (selected_bed_id, st.session_state.user_id, patient_name, patient_age, patient_gender, contact_number, medical_condition, start_date))
                    
                    conn.commit()
                    st.success("Booking submitted successfully! It will be reviewed by an administrator.")
                    
                    if st.button("View My Bookings"):
                        st.session_state.page = 'booking_history'
                        st.rerun()
                except Exception as e:
                    conn.rollback()
                    st.error(f"Error creating booking: {e}")
                finally:
                    cur.close()
                    conn.close()
    
    if st.button("Cancel Booking", key="cancel_booking"):
        st.session_state.page = 'dashboard'
        st.rerun()

# Assign Bed page (for admins)
def show_assign_bed():
    if not st.session_state.logged_in or not st.session_state.is_admin:
        st.warning("You do not have permission to access this page")
        return
    
    st.title("Assign ICU Bed to a Patient")
    
    st.info("This form allows administrators to directly assign an ICU bed to a patient, bypassing the normal booking process.")
    
    # Fetch available beds
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT id, bed_number, bed_type, price_per_day
    FROM beds WHERE is_available = 1
    ORDER BY bed_number
    """)
    available_beds = cur.fetchall()
    cur.close()
    conn.close()
    
    if not available_beds:
        st.warning("No ICU beds are available at the moment")
        if st.button("Return to Admin Dashboard"):
            st.session_state.page = 'admin_dashboard'
            st.rerun()
        return
    
    with st.form("assign_bed_form"):
        # Bed selection
        bed_options = [f"{b[1]} - {b[2].capitalize()} ICU (${b[3]}/day)" for b in available_beds]
        selected_bed = st.selectbox("Select ICU Bed *", options=bed_options)
        selected_bed_id = available_beds[bed_options.index(selected_bed)][0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input("Admission Date *", min_value=datetime.now().date(), value=datetime.now().date())
        
        st.subheader("Patient Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            patient_name = st.text_input("Patient Full Name *")
            patient_age = st.number_input("Patient Age *", min_value=0, max_value=120, step=1)
        
        with col2:
            patient_gender = st.selectbox("Patient Gender *", options=["male", "female", "other"], format_func=lambda x: x.capitalize())
            contact_number = st.text_input("Contact Number *")
        
        medical_condition = st.text_area("Medical Condition/Reason for ICU Admission *", height=100)
        
        status = st.selectbox("Booking Status *", options=["pending", "confirmed"], format_func=lambda x: x.capitalize())
        
        submit = st.form_submit_button("Assign Bed")
        
        if submit:
            if not (patient_name and patient_age and contact_number and medical_condition):
                st.warning("Please fill in all required fields")
            else:
                conn = get_db_connection()
                cur = conn.cursor()
                
                try:
                    # Create booking
                    cur.execute("""
                    INSERT INTO bookings (bed_id, user_id, patient_name, patient_age, patient_gender, contact_number, medical_condition, start_date, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (selected_bed_id, st.session_state.user_id, patient_name, patient_age, patient_gender, contact_number, medical_condition, start_date, status))
                    
                    # If confirmed, update bed availability
                    if status == "confirmed":
                        cur.execute("UPDATE beds SET is_available = 0 WHERE id = ?", (selected_bed_id,))
                    
                    conn.commit()
                    st.success(f"Bed assigned successfully with status: {status.capitalize()}")
                    
                    if st.button("Return to Admin Dashboard"):
                        st.session_state.page = 'admin_dashboard'
                        st.rerun()
                except Exception as e:
                    conn.rollback()
                    st.error(f"Error assigning bed: {e}")
                finally:
                    cur.close()
                    conn.close()
    
    if st.button("Cancel", key="cancel_assign"):
        st.session_state.page = 'admin_dashboard'
        st.rerun()

# Booking History page
def show_booking_history():
    if not st.session_state.logged_in:
        st.warning("Please login to view your booking history")
        return
    
    st.title("Your Booking History")
    
    # Fetch all bookings for the current user
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT b.id, bd.bed_number, bd.bed_type, b.patient_name, b.booking_date, b.start_date, b.end_date, bd.price_per_day, b.status
    FROM bookings b
    JOIN beds bd ON b.bed_id = bd.id
    WHERE b.user_id = ?
    ORDER BY b.booking_date DESC
    """, (st.session_state.user_id,))
    bookings = cur.fetchall()
    cur.close()
    conn.close()
    
    if bookings:
        booking_data = []
        for booking in bookings:
            bed_types = {
                'general': 'General ICU',
                'cardiac': 'Cardiac ICU',
                'neonatal': 'Neonatal ICU',
                'pediatric': 'Pediatric ICU',
                'surgical': 'Surgical ICU'
            }
            bed_type_display = bed_types.get(booking[2], booking[2])
            
            status_badge = {
                'pending': '🟡 Pending',
                'confirmed': '🟢 Confirmed',
                'cancelled': '🔴 Cancelled',
                'completed': '🔵 Completed'
            }
            
            booking_data.append({
                "Booking ID": booking[0],
                "Bed Number": booking[1],
                "Bed Type": bed_type_display,
                "Patient Name": booking[3],
                "Booking Date": booking[4] if isinstance(booking[4], str) else booking[4].strftime("%b %d, %Y"),
                "Start Date": booking[5] if isinstance(booking[5], str) else booking[5].strftime("%b %d, %Y"),
                "End Date": "--" if not booking[6] else (booking[6] if isinstance(booking[6], str) else booking[6].strftime("%b %d, %Y")),
                "Price per Day": f"${booking[7]}",
                "Status": status_badge.get(booking[8], booking[8]),
                "Actions": booking[0] if booking[8] in ['pending', 'confirmed'] else None
            })
        
        df = pd.DataFrame(booking_data)
        st.dataframe(df.drop(columns=["Actions"]), hide_index=True)
        
        # Cancel booking functionality
        cancelable_bookings = [b for b in bookings if b[8] in ['pending', 'confirmed']]
        if cancelable_bookings:
            st.subheader("Cancel a Booking")
            
            booking_to_cancel = st.selectbox(
                "Select a booking to cancel", 
                options=[f"ID: {b[0]} - Bed: {b[1]} - Patient: {b[3]} - Status: {b[8].capitalize()}" for b in cancelable_bookings]
            )
            booking_id = int(booking_to_cancel.split("ID: ")[1].split(" -")[0])
            
            if st.button("Cancel Selected Booking"):
                conn = get_db_connection()
                cur = conn.cursor()
                
                try:
                    # Check if booking is confirmed
                    cur.execute("SELECT status, bed_id FROM bookings WHERE id = ?", (booking_id,))
                    status, bed_id = cur.fetchone()
                    
                    # Update booking status
                    cur.execute("UPDATE bookings SET status = 'cancelled', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (booking_id,))
                    
                    # If booking was confirmed, make the bed available again
                    if status == 'confirmed':
                        cur.execute("UPDATE beds SET is_available = 1 WHERE id = ?", (bed_id,))
                    
                    conn.commit()
                    st.success(f"Booking #{booking_id} cancelled successfully")
                    st.rerun()
                except Exception as e:
                    conn.rollback()
                    st.error(f"Error cancelling booking: {e}")
                finally:
                    cur.close()
                    conn.close()
    else:
        st.info("You have not made any bookings yet.")
        if st.button("Book a bed now"):
            st.session_state.page = 'book_bed'
            st.rerun()
    
    st.subheader("Booking Status Information")
    status_info = {
        "🟡 Pending": "Your booking is awaiting confirmation from an administrator.",
        "🟢 Confirmed": "Your booking has been confirmed and the ICU bed is reserved for you.",
        "🔴 Cancelled": "The booking has been cancelled either by you or an administrator.",
        "🔵 Completed": "The patient has been discharged, and the ICU usage period is complete."
    }
    
    for status, description in status_info.items():
        st.write(f"**{status}:** {description}")

# ICU History page (for admins)
def show_icu_history():
    if not st.session_state.logged_in or not st.session_state.is_admin:
        st.warning("You do not have permission to access this page")
        return
    
    st.title("ICU Usage History")
    
    # Fetch ICU history
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
    SELECT h.id, b.bed_number, b.bed_type, h.patient_name, h.patient_age, h.patient_gender, h.admitted_date, h.discharged_date
    FROM icu_history h
    JOIN beds b ON h.bed_id = b.id
    ORDER BY h.admitted_date DESC
    """)
    histories = cur.fetchall()
    
    # Get statistics
    cur.execute("SELECT COUNT(*) FROM beds")
    bed_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM beds WHERE is_available = 0")
    occupied_count = cur.fetchone()[0]
    
    completed_histories = [h for h in histories if h[7] is not None]
    avg_duration = 0
    if completed_histories:
        total_days = 0
        for history in completed_histories:
            # Convert string dates to datetime objects if needed
            admitted_date = history[6] if isinstance(history[6], datetime) else datetime.strptime(history[6], "%Y-%m-%d")
            discharged_date = history[7] if isinstance(history[7], datetime) else datetime.strptime(history[7], "%Y-%m-%d")
            days = (discharged_date - admitted_date).days
            total_days += days
        avg_duration = total_days / len(completed_histories)
    
    occupancy_rate = 0
    if bed_count > 0:
        occupancy_rate = (occupied_count / bed_count) * 100
    
    cur.close()
    conn.close()
    
    # Display statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total ICU Admissions", len(histories))
    
    with col2:
        st.metric("Current Occupancy Rate", f"{occupancy_rate:.0f}%")
    
    with col3:
        st.metric("Average Stay Duration", f"{avg_duration:.1f} days" if completed_histories else "N/A")
    
    # Display history table
    st.subheader("Complete ICU History")
    
    if histories:
        history_data = []
        for history in histories:
            bed_types = {
                'general': 'General ICU',
                'cardiac': 'Cardiac ICU',
                'neonatal': 'Neonatal ICU',
                'pediatric': 'Pediatric ICU',
                'surgical': 'Surgical ICU'
            }
            bed_type_display = bed_types.get(history[2], history[2])
            
            gender_display = history[5].capitalize()
            
            duration = "Still admitted"
            if history[7]:
                # Convert string dates to datetime objects if needed
                admitted_date = history[6] if isinstance(history[6], datetime) else datetime.strptime(history[6], "%Y-%m-%d")
                discharged_date = history[7] if isinstance(history[7], datetime) else datetime.strptime(history[7], "%Y-%m-%d")
                duration = f"{(discharged_date - admitted_date).days} days"
            
            history_data.append({
                "Bed Number": history[1],
                "Bed Type": bed_type_display,
                "Patient Name": history[3],
                "Age": history[4],
                "Gender": gender_display,
                "Admitted Date": history[6] if isinstance(history[6], str) else history[6].strftime("%b %d, %Y"),
                "Discharged Date": "--" if not history[7] else (history[7] if isinstance(history[7], str) else history[7].strftime("%b %d, %Y")),
                "Duration": duration
            })
        
        st.dataframe(pd.DataFrame(history_data), hide_index=True)
    else:
        st.info("No ICU history records found.")

# Profile page
def show_profile():
    if not st.session_state.logged_in:
        st.warning("Please login to view your profile")
        return
    
    st.title("User Profile")
    
    # Fetch user details
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT username, email, first_name, last_name, is_admin, created_at
    FROM users WHERE id = ?
    """, (st.session_state.user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    
    if not user:
        st.error("User not found")
        return
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("""
        <div style="text-align: center;">
            <div style="font-size: 5rem; color: #0d6efd;">
                <i class="fas fa-user-circle"></i>
                👤
            </div>
            <h4>{}</h4>
            <p>@{}</p>
            <span class="badge" style="background-color: {}; color: white; padding: 5px 10px; border-radius: 5px;">
                {}
            </span>
        </div>
        """.format(
            f"{user[2] or ''} {user[3] or ''}",
            user[0],
            "#0d6efd" if user[4] else "#6c757d",
            "Administrator" if user[4] else "User"
        ), unsafe_allow_html=True)
    
    with col2:
        with st.form("update_profile_form"):
            first_name = st.text_input("First Name", value=user[2] or "")
            last_name = st.text_input("Last Name", value=user[3] or "")
            email = st.text_input("Email", value=user[1])
            
            update_button = st.form_submit_button("Update Profile")
            
            if update_button:
                if not email:
                    st.warning("Email is required")
                else:
                    conn = get_db_connection()
                    cur = conn.cursor()
                    
                    try:
                        cur.execute("""
                        UPDATE users 
                        SET first_name = ?, last_name = ?, email = ?
                        WHERE id = ?
                        """, (first_name, last_name, email, st.session_state.user_id))
                        
                        conn.commit()
                        st.success("Profile updated successfully!")
                        st.rerun()
                    except Exception as e:
                        conn.rollback()
                        st.error(f"Error updating profile: {e}")
                    finally:
                        cur.close()
                        conn.close()
    
    st.subheader("Account Information")
    
    account_info = {
        "Username": user[0],
        "Email": user[1],
        "Date Joined": user[5] if isinstance(user[5], str) else user[5].strftime("%B %d, %Y"),
        "Account Type": "Administrator" if user[4] else "Regular User"
    }
    
    for label, value in account_info.items():
        st.write(f"**{label}:** {value}")

# Main app logic
def main():
    if st.session_state.page == 'home':
        show_home()
    elif st.session_state.page == 'login':
        show_login()
    elif st.session_state.page == 'register':
        show_register()
    elif st.session_state.page == 'dashboard':
        show_dashboard()
    elif st.session_state.page == 'admin_dashboard':
        show_admin_dashboard()
    elif st.session_state.page == 'add_bed':
        show_add_bed()
    elif st.session_state.page == 'edit_bed':
        show_edit_bed()
    elif st.session_state.page == 'book_bed':
        show_book_bed()
    elif st.session_state.page == 'assign_bed':
        show_assign_bed()
    elif st.session_state.page == 'booking_history':
        show_booking_history()
    elif st.session_state.page == 'icu_history':
        show_icu_history()
    elif st.session_state.page == 'profile':
        show_profile()

if __name__ == "__main__":
    main()