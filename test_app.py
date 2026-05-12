"""
Automated Test Suite - Grand Stay Hotel Reservation System
Author: ISHIMWE Eric
Date: May 2026

Covers all test cases defined in test_plan.md using Python's built-in unittest framework.
Run with: python -m unittest test_app.py -v
"""

import os
import unittest
from werkzeug.security import generate_password_hash
from database import DatabaseManager

# Use isolated test database
TEST_DB = 'test_hotel.db'
os.environ['SECRET_KEY'] = 'test_secret_key'

from app import app


class HotelReservationTests(unittest.TestCase):

    def setUp(self):
        """Set up isolated test client and database before each test."""
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_secret_key'
        self.client = app.test_client()

        # Patch app to use test database
        import app as app_module
        app_module.db_manager = DatabaseManager(TEST_DB)
        app_module.db_manager.initialize_database()
        self.db = app_module.db_manager

    def tearDown(self):
        """Remove test database after each test."""
        DatabaseManager._instances.pop(TEST_DB, None)
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    # TC-01: Register a new user
    def test_register_new_user(self):
        response = self.client.post('/register', data={
            'name': 'Test User',
            'email': 'newuser@example.com',
            'password': 'Test1234'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        user = self.db.get_user_by_email('newuser@example.com')
        self.assertIsNotNone(user)

    # TC-02: Prevent duplicate registration
    def test_duplicate_registration(self):
        self.client.post('/register', data={
            'name': 'User One',
            'email': 'duplicate@example.com',
            'password': 'Pass1234'
        })
        response = self.client.post('/register', data={
            'name': 'User Two',
            'email': 'duplicate@example.com',
            'password': 'Pass1234'
        })
        self.assertIn(b'Email already exists', response.data)

    # TC-03: Login with valid credentials
    def test_login_valid_credentials(self):
        response = self.client.post('/login', data={
            'email': 'admin@hotel.com',
            'password': 'Admin1234'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    # TC-04: Login with invalid credentials
    def test_login_invalid_credentials(self):
        response = self.client.post('/login', data={
            'email': 'wrong@example.com',
            'password': 'wrongpass'
        })
        self.assertIn(b'Invalid email or password', response.data)

    # TC-05: Browse available rooms
    def test_browse_available_rooms(self):
        response = self.client.get('/rooms')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Single', response.data)

    # TC-06: Booking date validation (check-out before check-in)
    def test_booking_date_validation(self):
        self.client.post('/login', data={
            'email': 'admin@hotel.com',
            'password': 'Admin1234'
        })
        response = self.client.post('/book/1', data={
            'check_in': '2026-06-10',
            'check_out': '2026-06-05'
        })
        self.assertIn(b'Check-out date must be later', response.data)

    # TC-07: Admin login redirects to admin dashboard
    def test_admin_login_redirects_to_admin_dashboard(self):
        response = self.client.post('/login', data={
            'email': 'admin@hotel.com',
            'password': 'Admin1234'
        }, follow_redirects=True)
        self.assertIn(b'Admin', response.data)

    # TC-08: Guest cannot access admin route
    def test_guest_cannot_access_admin_route(self):
        self.client.post('/register', data={
            'name': 'Guest User',
            'email': 'guest@example.com',
            'password': 'Guest1234'
        })
        self.client.post('/login', data={
            'email': 'guest@example.com',
            'password': 'Guest1234'
        })
        response = self.client.get('/admin', follow_redirects=True)
        self.assertNotIn(b'Admin Dashboard', response.data)

    # TC-09: Singleton pattern — same instance returned
    def test_singleton_same_instance(self):
        db1 = DatabaseManager(TEST_DB)
        db2 = DatabaseManager(TEST_DB)
        self.assertIs(db1, db2)

    # TC-10: Logout clears session
    def test_logout_clears_session(self):
        self.client.post('/login', data={
            'email': 'admin@hotel.com',
            'password': 'Admin1234'
        })
        self.client.get('/logout')
        response = self.client.get('/dashboard', follow_redirects=True)
        self.assertIn(b'Login', response.data)


if __name__ == '__main__':
    unittest.main(verbosity=2)
