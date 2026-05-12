# Hotel Reservation System

A Flask prototype for a hotel reservation system with user registration, login, room browsing, booking, and confirmation.

## Project contents
- `app.py`: Flask application with routes for home, register, login, dashboard, rooms, booking, and confirmation.
- `database.py`: Singleton `DatabaseManager` handling SQLite persistence, seeding default rooms, and booking operations.
- `requirements.txt`: Python dependencies.
- `templates/`: HTML pages used by the Flask app.

## Run locally
1. Create a Python virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Start the app:
   ```powershell
   python app.py
   ```
4. Open `http://127.0.0.1:5000` in the browser.

### Admin access
A default admin account is created automatically when the app first runs:
- Email: `admin@hotel.com`
- Password: `Admin1234`
- Admin dashboard: `/admin`

## Docker
Build the container:
```powershell
docker build -t hotel-reservation-system .
```
Run the container:
```powershell
docker run -p 5000:5000 hotel-reservation-system
```

## Version control
This project is ready for Git version control. Add and commit changes using:
```powershell
git add .
git commit -m "Initial hotel reservation system prototype"
```

## Design pattern and best practices
- `DatabaseManager` implements the Singleton pattern to centralize database access and avoid duplicate connection managers.
- Passwords are stored securely using hashed passwords via `werkzeug.security`.
- Route logic is separated from persistence logic for clearer responsibilities.
- The project uses meaningful names, consistent formatting, and modular code.

## Test plan
See `test_plan.md` for defined goals, test cases, and issue tracking guidance.
