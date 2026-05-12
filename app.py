"""
Grand Stay Hotel Reservation System - Flask Application
Author: ISHIMWE Eric
Date: May 2026

This module implements the web application routing and user/admin management logic
using the Flask web framework. It handles authentication, session management, and
provides endpoints for guests and administrators.

Design Patterns Used:
1. Singleton Pattern: DatabaseManager ensures only one DB connection instance
2. Decorator Pattern: @admin_required decorator restricts routes to admin users
3. MVC Pattern: Flask routes (Controller), templates (View), database (Model)
"""

import sqlite3
import functools
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
from database import DatabaseManager

# Initialize Flask application with security configurations
app = Flask(__name__)
import os
app.secret_key = os.environ.get('SECRET_KEY', 'hotel_secret_key_2026')  # Use env var in production
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to session cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Auto-reload templates on changes
app.jinja_env.auto_reload = True

# Initialize database manager using Singleton pattern
# This ensures all parts of the application use the same database connection instance
db_manager = DatabaseManager('hotel.db')
db_manager.initialize_database()

# Decorator: Admin-only route protection
# This decorator verifies the user is authenticated and has admin role
# If not, it redirects unauthorized users to the guest dashboard
def admin_required(view_func):
    """
    Decorator to restrict route access to authenticated admin users only.
    
    Returns:
        - Redirects to login if user is not authenticated
        - Redirects to dashboard if user is authenticated but not admin
        - Calls the wrapped function if user is admin
    """
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        # Check if user is logged in
        if 'user_id' not in session:
            return redirect(url_for('login'))
        # Check if user has admin role
        if session.get('role') != 'admin':
            return redirect(url_for('dashboard'))
        return view_func(*args, **kwargs)
    return wrapper
# Create default admin account if it does not exist
# This seeds an admin user on first application startup for system management
admin_email = 'admin@hotel.com'
if not db_manager.get_user_by_email(admin_email):
    admin_password = generate_password_hash('Admin1234')
    db_manager.create_user('Admin', admin_email, admin_password, role='admin')

# ================== PUBLIC ROUTES ==================

@app.route('/')
def home():
    """
    Home page route.
    Redirects authenticated users to their dashboard, shows home page to guests.
    """
    if session.get('user_id'):
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration route.
    Handles both GET (display form) and POST (process registration).
    
    Validates input, hashes password, and creates user account in database.
    Redirects to login on success or shows error message on failure.
    """
    error = None
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()

        # Validate all required fields are provided
        if not name or not email or not password:
            error = 'All fields are required.'
        else:
            try:
                # Hash password for security before storing
                password_hash = generate_password_hash(password)
                db_manager.create_user(name, email, password_hash)
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                # Email already exists in database
                error = 'Email already exists. Please use another email.'
            except Exception:
                error = 'Unable to register at the moment. Please try again later.'

    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login route.
    Authenticates users by email/password and creates session.
    
    Behavior:
    - Admin users are redirected to /admin dashboard
    - Regular users are redirected to /dashboard
    - Invalid credentials show error message
    """
    error = None
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()

        # Query user by email from database
        user = db_manager.get_user_by_email(email)
        # Verify password matches stored hash
        if user and check_password_hash(user['password'], password):
            # Store user info in session for tracking authenticated user
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['role'] = user['role']
            # Route to appropriate dashboard based on user role
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))

        error = 'Invalid email or password.'

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    """
    User logout route.
    Clears session data and redirects to home page.
    """
    session.clear()
    return redirect(url_for('home'))

@app.route('/rooms')
def rooms():
    """
    Browse available rooms route.
    Displays all rooms with 'available' status that guests can book.
    """
    available_rooms = db_manager.get_available_rooms()
    return render_template('rooms.html', rooms=available_rooms)

# ================== GUEST ROUTES ==================

@app.route('/dashboard')
def dashboard():
    """
    Guest dashboard route.
    Displays personalized dashboard for logged-in guests.
    Redirects admin users to /admin instead.
    Requires user to be logged in.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Redirect admins to their dashboard
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))

    return render_template('dashboard.html', name=session.get('user_name'))

@app.route('/book/<int:room_id>', methods=['GET', 'POST'])
def book_room(room_id):
    """
    Room booking route.
    Allows authenticated guests to book available rooms.
    
    Validates:
    - User is logged in
    - Room exists and is available
    - Check-in and check-out dates are provided and valid
    
    On success:
    - Creates booking record
    - Creates payment record
    - Marks room as unavailable
    - Shows confirmation page
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Retrieve room details from database
    room = db_manager.get_room_by_id(room_id)
    # Verify room exists and is available
    if not room or room['status'] != 'available':
        return redirect(url_for('rooms'))

    error = None
    if request.method == 'POST':
        check_in = request.form['check_in'].strip()
        check_out = request.form['check_out'].strip()

        # Validate both dates are provided
        if not check_in or not check_out:
            error = 'Both dates are required.'
        # Validate check-out is after check-in
        elif check_out <= check_in:
            error = 'Check-out date must be later than check-in date.'
        else:
            # Create booking and associated payment
            booking_id = db_manager.create_booking(
                session['user_id'], room_id, check_in, check_out, room['price_per_night']
            )
            # Mark room as booked (unavailable)
            db_manager.mark_room_unavailable(room_id)
            # Retrieve booking details for confirmation display
            booking = db_manager.get_booking_by_id(booking_id)
            return render_template('confirmation.html', booking=booking)

    return render_template('book.html', room=room, error=error)

# ================== ADMIN ROUTES ==================

@app.route('/admin')
@admin_required
def admin_dashboard():
    """
    Admin dashboard route - Main admin control center.
    @admin_required: Only accessible to authenticated admin users
    
    Displays:
    - Count of registered clients
    - All bookings with guest and payment information
    - Link to room management interface
    """
    users = db_manager.get_all_users()
    bookings = db_manager.get_all_bookings()
    return render_template('admin_dashboard.html', name=session.get('user_name'), users=users, bookings=bookings)

@app.route('/admin/rooms')
@admin_required
def admin_rooms():
    """
    Admin room management list route.
    @admin_required: Only accessible to authenticated admin users
    
    Displays all rooms in the system with options to:
    - Edit room details (price, status)
    - Delete room
    - Add new room
    """
    rooms = db_manager.get_all_rooms()
    return render_template('admin_rooms.html', name=session.get('user_name'), rooms=rooms)

@app.route('/admin/rooms/add', methods=['GET', 'POST'])
@admin_required
def admin_add_room():
    """
    Admin add room route.
    @admin_required: Only accessible to authenticated admin users
    
    Handles room creation with validation:
    - All fields (room_number, type, price) required
    - Price must be valid numeric value
    - Status defaults to 'available' if not specified
    """
    error = None
    if request.method == 'POST':
        room_number = request.form['room_number'].strip()
        room_type = request.form['room_type'].strip()
        price = request.form['price_per_night'].strip()
        status = request.form.get('status', 'available').strip()

        # Validate required fields
        if not room_number or not room_type or not price:
            error = 'All fields are required.'
        else:
            try:
                # Convert price string to float and validate
                price_value = float(price)
                db_manager.add_room(room_number, room_type, price_value, status)
                return redirect(url_for('admin_rooms'))
            except ValueError:
                error = 'Price must be a number.'

    return render_template('admin_room_form.html', name=session.get('user_name'), form_title='Add Room', room=None, error=error, action=url_for('admin_add_room'))

@app.route('/admin/rooms/edit/<int:room_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_room(room_id):
    """
    Admin edit room route.
    @admin_required: Only accessible to authenticated admin users
    
    Allows admin to modify existing room details:
    - Update room number, type, price, status
    - Same validation as add_room
    """
    room = db_manager.get_room_by_id(room_id)
    if not room:
        return redirect(url_for('admin_rooms'))

    error = None
    if request.method == 'POST':
        room_number = request.form['room_number'].strip()
        room_type = request.form['room_type'].strip()
        price = request.form['price_per_night'].strip()
        status = request.form.get('status', 'available').strip()

        # Validate required fields
        if not room_number or not room_type or not price:
            error = 'All fields are required.'
        else:
            try:
                # Convert and validate price
                price_value = float(price)
                db_manager.update_room(room_id, room_number, room_type, price_value, status)
                return redirect(url_for('admin_rooms'))
            except ValueError:
                error = 'Price must be a number.'

    return render_template('admin_room_form.html', name=session.get('user_name'), form_title='Edit Room', room=room, error=error, action=url_for('admin_edit_room', room_id=room_id))

@app.route('/admin/rooms/delete/<int:room_id>', methods=['POST'])
@admin_required
def admin_delete_room(room_id):
    """
    Admin delete room route.
    @admin_required: Only accessible to authenticated admin users
    
    Permanently removes a room from the system.
    Note: Consider adding soft-delete for audit trail in production.
    """
    db_manager.delete_room(room_id)
    return redirect(url_for('admin_rooms'))

# ================== APPLICATION ENTRY POINT ==================

if __name__ == '__main__':
    # Run Flask development server with debug mode enabled
    # debug=True enables auto-reload on code changes and detailed error pages
    app.run(host='0.0.0.0', port=5000, debug=True)
