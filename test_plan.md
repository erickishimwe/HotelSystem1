# Test Plan

## Testing goals
- Validate core system requirements: registration, authentication, room browsing, booking, and confirmation.
- Verify that user journeys match expected workflows.
- Confirm that data is saved and retrieved correctly from the database.
- Identify any functional issues before final submission.

## Features to test
- User registration and email uniqueness.
- User login and session handling.
- Room browsing with available-room filtering.
- Room booking workflow and booking confirmation.
- Database seeding for default rooms.

## Test cases

### 1. Register a new user
- Steps:
  1. Open `/register`.
  2. Enter name, email, and password.
  3. Submit the form.
- Expected result: Redirect to login page and user record is created.

### 2. Prevent duplicate registration
- Steps:
  1. Register once with an email.
  2. Attempt to register again using the same email.
- Expected result: Form shows an error and no duplicate account is created.

### 3. Log in with valid credentials
- Steps:
  1. Open `/login`.
  2. Enter correct email and password.
  3. Submit.
- Expected result: User is redirected to `/dashboard` and session is created.

### 4. Browse available rooms
- Steps:
  1. Open `/rooms`.
- Expected result: Available rooms are displayed on the page.

### 5. Book a room
- Steps:
  1. Log in.
  2. Open `/rooms` and select a room.
  3. Enter valid check-in and check-out dates.
  4. Submit the booking form.
- Expected result: Booking confirmation page appears and room status changes to booked.

### 6. Booking date validation
- Steps:
  1. Attempt to book with check-out before check-in.
- Expected result: The booking form displays a validation error.

### 7. Admin login redirects to admin dashboard
- Steps:
  1. Open `/login`.
  2. Enter admin credentials (`admin@hotel.com` / `Admin1234`).
  3. Submit.
- Expected result: Redirected to `/admin` dashboard, not guest dashboard.

### 8. Guest cannot access admin route
- Steps:
  1. Log in as a regular guest.
  2. Navigate to `/admin` directly.
- Expected result: Redirected to `/dashboard`, admin panel not shown.

### 9. Singleton pattern — single database instance
- Steps:
  1. Create two `DatabaseManager` instances with the same path.
- Expected result: Both variables point to the exact same object.

### 10. Logout clears session
- Steps:
  1. Log in as any user.
  2. Navigate to `/logout`.
  3. Try to access `/dashboard`.
- Expected result: Redirected to `/login`, session is cleared.

## Issue tracking
- Use Git commit history to capture functional changes.
- Note bugs and fixes in a simple issue list or in version control messages.
- Expected issue tracking method: clear issue title, steps to reproduce, and resolution status.

## Known issues log
| # | Issue | Status |
|---|-------|--------|
| 1 | Room stays booked after checkout date passes | Open — requires scheduled job |
| 2 | No password strength validation on register form | Open — client-side validation to be added |
