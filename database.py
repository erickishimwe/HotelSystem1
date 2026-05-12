"""
Grand Stay Hotel Reservation System - Database Management
Author: ISHIMWE Eric
Date: May 2026

This module handles all database operations using SQLite3.
It implements the Singleton pattern to ensure a single database instance
across the entire application, preventing connection conflicts and
managing resources efficiently.

Singleton Pattern Implementation:
- _instances dictionary stores one instance per database path
- __new__ method returns existing instance or creates new one
- Ensures data consistency and prevents multiple DB connections
"""

import sqlite3
from werkzeug.security import generate_password_hash


class DatabaseManager:
    """
    Singleton database manager for SQLite operations.
    
    Ensures only one DatabaseManager instance exists per database file.
    Provides methods for user authentication, room management, and booking operations.
    """
    
    # Class-level dictionary to store singleton instances
    # Key: database path, Value: DatabaseManager instance
    _instances = {}

    def __new__(cls, db_path='hotel.db'):
        """
        Singleton pattern implementation.
        
        Args:
            db_path (str): Path to SQLite database file
            
        Returns:
            DatabaseManager: Existing or newly created instance for the given path
        """
        if db_path not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[db_path] = instance
        return cls._instances[db_path]

    def __init__(self, db_path='hotel.db'):
        """
        Initialize DatabaseManager with database path.
        
        Args:
            db_path (str): Path to SQLite database file (default: 'hotel.db')
        """
        self.db_path = db_path

    def get_connection(self):
        """
        Get database connection with Row factory enabled.
        
        Row factory allows accessing columns by name instead of index.
        Example: row['email'] instead of row[2]
        
        Returns:
            sqlite3.Connection: Database connection object
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn

    def initialize_database(self):
        """
        Initialize database schema and seed default data.
        
        Creates tables:
        - users: Stores guest and admin accounts
        - rooms: Stores hotel room inventory
        - bookings: Stores guest reservations
        - payments: Stores payment records for bookings
        
        Seeds:
        - Default rooms (101, 102, 201, 202)
        - Admin account (admin@hotel.com / Admin1234)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create users table with authentication info
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT DEFAULT 'guest'
                )
            ''')
            
            # Create rooms table with pricing and status
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rooms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_number TEXT NOT NULL,
                    room_type TEXT NOT NULL,
                    price_per_night REAL NOT NULL,
                    status TEXT DEFAULT 'available'
                )
            ''')
            
            # Create bookings table with guest and room relationships
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    room_id INTEGER NOT NULL,
                    check_in TEXT NOT NULL,
                    check_out TEXT NOT NULL,
                    status TEXT DEFAULT 'confirmed',
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (room_id) REFERENCES rooms(id)
                )
            ''')
            
            # Create payments table linked to bookings
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    booking_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    payment_method TEXT NOT NULL,
                    status TEXT DEFAULT 'paid',
                    FOREIGN KEY (booking_id) REFERENCES bookings(id)
                )
            ''')
            
            # Seed default data
            self._seed_rooms(cursor)
            self._seed_admin(cursor)
            conn.commit()

    def _seed_rooms(self, cursor):
        """
        Seed default hotel rooms on first database initialization.
        
        Only runs if no rooms exist in database.
        Creates 4 default rooms: Single, Double, Deluxe, Suite
        
        Args:
            cursor: SQLite cursor object
        """
        room_count = cursor.execute('SELECT COUNT(*) FROM rooms').fetchone()[0]
        if room_count == 0:
            # Define default room inventory
            default_rooms = [
                ('101', 'Single', 70.00, 'available'),
                ('102', 'Double', 100.00, 'available'),
                ('201', 'Deluxe', 150.00, 'available'),
                ('202', 'Suite', 220.00, 'available')
            ]
            cursor.executemany(
                'INSERT INTO rooms (room_number, room_type, price_per_night, status) VALUES (?, ?, ?, ?)',
                default_rooms
            )

    def _seed_admin(self, cursor):
        """
        Seed default admin account on first database initialization.
        
        Only runs if no admin account exists in database.
        Creates admin account with secure hashed password.
        
        Args:
            cursor: SQLite cursor object
        """
        admin_email = 'admin@hotel.com'
        admin_exists = cursor.execute(
            'SELECT COUNT(*) FROM users WHERE email = ?',
            (admin_email,)
        ).fetchone()[0]
        if admin_exists == 0:
            admin_password = generate_password_hash('Admin1234')
            cursor.execute(
                'INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)',
                ('Admin', admin_email, admin_password, 'admin')
            )

    # ================== USER MANAGEMENT ==================

    def create_user(self, name, email, password_hash, role='guest'):
        """
        Create new user account in database.
        
        Args:
            name (str): User's full name
            email (str): User's email (must be unique)
            password_hash (str): Hashed password using werkzeug.security
            role (str): User role - 'guest' (default) or 'admin'
            
        Raises:
            sqlite3.IntegrityError: If email already exists
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)',
                (name, email, password_hash, role)
            )
            conn.commit()

    def get_user_by_email(self, email):
        """
        Retrieve user record by email address.
        
        Args:
            email (str): User's email address
            
        Returns:
            sqlite3.Row or None: User record if found, None otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            return cursor.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()

    def get_all_users(self):
        """
        Retrieve all users in database (admin view).
        
        Returns:
            List[sqlite3.Row]: All user records with id, name, email, role
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            return cursor.execute('SELECT id, name, email, role FROM users ORDER BY id').fetchall()

    # ================== ROOM MANAGEMENT ==================

    def get_available_rooms(self):
        """
        Retrieve all rooms available for booking (guest view).
        
        Returns:
            List[sqlite3.Row]: Rooms with status='available'
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            return cursor.execute('SELECT * FROM rooms WHERE status = ?', ('available',)).fetchall()

    def get_all_rooms(self):
        """
        Retrieve all rooms in system (admin view).
        
        Returns:
            List[sqlite3.Row]: All room records ordered by ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            return cursor.execute('SELECT * FROM rooms ORDER BY id').fetchall()

    def get_room_by_id(self, room_id):
        """
        Retrieve specific room by ID.
        
        Args:
            room_id (int): Primary key of room
            
        Returns:
            sqlite3.Row or None: Room record if found, None otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            return cursor.execute('SELECT * FROM rooms WHERE id=?', (room_id,)).fetchone()

    def add_room(self, room_number, room_type, price_per_night, status='available'):
        """
        Add new room to inventory (admin operation).
        
        Args:
            room_number (str): Room identifier (e.g., '301')
            room_type (str): Room category (e.g., 'Single', 'Double')
            price_per_night (float): Nightly rate
            status (str): Room status (default: 'available')
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO rooms (room_number, room_type, price_per_night, status) VALUES (?, ?, ?, ?)',
                (room_number, room_type, price_per_night, status)
            )
            conn.commit()

    def update_room(self, room_id, room_number, room_type, price_per_night, status):
        """
        Update existing room details (admin operation).
        
        Args:
            room_id (int): Primary key of room to update
            room_number (str): New room number
            room_type (str): New room type
            price_per_night (float): New price
            status (str): New status
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE rooms SET room_number=?, room_type=?, price_per_night=?, status=? WHERE id=?',
                (room_number, room_type, price_per_night, status, room_id)
            )
            conn.commit()

    def delete_room(self, room_id):
        """
        Delete room from inventory (admin operation).
        
        Note: Consider implementing soft-delete for audit trail in production.
        
        Args:
            room_id (int): Primary key of room to delete
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM rooms WHERE id=?', (room_id,))
            conn.commit()

    def mark_room_unavailable(self, room_id):
        """
        Mark room as booked/unavailable after successful booking.
        
        Args:
            room_id (int): Primary key of room to mark as booked
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE rooms SET status = ? WHERE id = ?', ('booked', room_id))
            conn.commit()

    # ================== BOOKING MANAGEMENT ==================

    def create_booking(self, user_id, room_id, check_in, check_out, amount):
        """
        Create new booking and associated payment record.
        
        This is a transaction that creates both booking and payment entries.
        Both records are created or both fail (atomic operation).
        
        Args:
            user_id (int): ID of guest making reservation
            room_id (int): ID of room being booked
            check_in (str): Check-in date (YYYY-MM-DD)
            check_out (str): Check-out date (YYYY-MM-DD)
            amount (float): Price per night for payment calculation
            
        Returns:
            int: ID of created booking
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Create booking record
            cursor.execute(
                'INSERT INTO bookings (user_id, room_id, check_in, check_out) VALUES (?, ?, ?, ?)',
                (user_id, room_id, check_in, check_out)
            )
            # Get ID of newly created booking
            booking_id = cursor.lastrowid
            # Create associated payment record
            cursor.execute(
                'INSERT INTO payments (booking_id, amount, payment_method) VALUES (?, ?, ?)',
                (booking_id, amount, 'card')
            )
            conn.commit()
            return booking_id

    def get_booking_by_id(self, booking_id):
        """
        Retrieve specific booking by ID.
        
        Args:
            booking_id (int): Primary key of booking
            
        Returns:
            sqlite3.Row or None: Booking record if found, None otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            return cursor.execute('SELECT * FROM bookings WHERE id=?', (booking_id,)).fetchone()

    def get_all_bookings(self):
        """
        Retrieve all bookings with complete details (admin view).
        
        Performs JOIN to combine booking, user, room, and payment information
        into a single comprehensive result set.
        
        Returns:
            List[sqlite3.Row]: All bookings with guest, room, and payment details
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            return cursor.execute('''
                SELECT b.id,
                       u.name AS user_name,
                       u.email AS user_email,
                       r.room_number,
                       r.room_type,
                       b.check_in,
                       b.check_out,
                       b.status AS booking_status,
                       p.amount,
                       p.payment_method,
                       p.status AS payment_status
                FROM bookings b
                JOIN users u ON b.user_id = u.id
                JOIN rooms r ON b.room_id = r.id
                LEFT JOIN payments p ON b.id = p.booking_id
                ORDER BY b.id DESC
            ''').fetchall()


# ================== MODULE INITIALIZATION ==================

if __name__ == '__main__':
    # Initialize database when module is run directly
    DatabaseManager().initialize_database()
