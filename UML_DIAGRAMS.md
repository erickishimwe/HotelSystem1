# UML DIAGRAMS - HOTEL RESERVATION SYSTEM

**Project:** Grand Stay Hotel Reservation System  
**Author:** ISHIMWE Eric  
**Date:** May 2026  

---

## 1. USE CASE DIAGRAM

### Description
Shows interactions between actors (Guest, Admin, System) and the system's primary use cases.

### Actors:
- **Guest:** Unregistered or registered user browsing/booking rooms
- **Admin:** Administrator managing rooms and bookings
- **System:** Automated database operations

### Use Cases:
- Guest: Register, Login, View Rooms, Book Room, Logout
- Admin: Login, View Dashboard, Manage Rooms (Add/Edit/Delete), View Bookings

```
┌─────────────────────────────────────────────────────────┐
│              Hotel Reservation System                    │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────┐              ┌────────────────┐           │
│  │  Guest   │              │   System       │           │
│  └──────────┘              └────────────────┘           │
│       │  └──────────────────────────────┘               │
│       │                                                  │
│      ◇ Register                                          │
│      ◇ Login                                             │
│      ◇ View Available Rooms                             │
│      ◇ Book Room                                         │
│      ◇ View Booking Confirmation                        │
│      ◇ Logout                                            │
│                                                           │
│  ┌──────────┐                                            │
│  │  Admin   │                                            │
│  └──────────┘                                            │
│       │                                                  │
│      ◇ Admin Login                                       │
│      ◇ View Dashboard (Users/Bookings)                  │
│      ◇ Add Room                                          │
│      ◇ Edit Room                                         │
│      ◇ Delete Room                                       │
│      ◇ View All Rooms                                    │
│      ◇ Logout                                            │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## 2. CLASS DIAGRAM

### Description
Shows the structure of classes, their attributes, and relationships.

```
┌─────────────────────────────────────────────────────────────────────┐
│                          User                                        │
├─────────────────────────────────────────────────────────────────────┤
│ - id: int (PK)                                                       │
│ - name: str                                                          │
│ - email: str (UNIQUE)                                                │
│ - password: str (hashed)                                             │
│ - role: str ('guest', 'admin')                                       │
├─────────────────────────────────────────────────────────────────────┤
│ + create(name, email, password, role)                                │
│ + get_by_email(email): User                                          │
│ + authenticate(email, password): bool                                │
└─────────────────────────────────────────────────────────────────────┘
         │                                    │
         │ 1                              0..* │
         │ creates                        books
         │                                    │
         └────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Booking                                       │
├─────────────────────────────────────────────────────────────────────┤
│ - id: int (PK)                                                       │
│ - user_id: int (FK → User)                                           │
│ - room_id: int (FK → Room)                                           │
│ - check_in: date                                                     │
│ - check_out: date                                                    │
│ - status: str ('confirmed', 'cancelled')                             │
├─────────────────────────────────────────────────────────────────────┤
│ + create(user_id, room_id, check_in, check_out): Booking             │
│ + get_by_id(id): Booking                                             │
│ + get_all(): List[Booking]                                           │
└─────────────────────────────────────────────────────────────────────┘
         │                                    │
         │ 1                              0..* │
         │ for                            has
         │                                    │
         └────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Room                                         │
├─────────────────────────────────────────────────────────────────────┤
│ - id: int (PK)                                                       │
│ - room_number: str                                                   │
│ - room_type: str ('Single', 'Double', 'Deluxe', 'Suite')            │
│ - price_per_night: float                                             │
│ - status: str ('available', 'booked')                                │
├─────────────────────────────────────────────────────────────────────┤
│ + add(number, type, price): Room                                     │
│ + update(id, details): void                                          │
│ + delete(id): void                                                   │
│ + get_all(): List[Room]                                              │
│ + get_available(): List[Room]                                        │
└─────────────────────────────────────────────────────────────────────┘
         │
         │ 1
         │ for
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Payment                                       │
├─────────────────────────────────────────────────────────────────────┤
│ - id: int (PK)                                                       │
│ - booking_id: int (FK → Booking)                                     │
│ - amount: float                                                      │
│ - payment_method: str ('card', 'cash', 'transfer')                  │
│ - status: str ('paid', 'pending')                                    │
├─────────────────────────────────────────────────────────────────────┤
│ + create(booking_id, amount, method): Payment                        │
│ + get_by_booking(booking_id): Payment                                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. ACTIVITY DIAGRAM

### Description
Shows the flow of activities and decision points in the booking process.

#### Guest Booking Flow:

```
                    ┌─────────────┐
                    │   START     │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ User Login  │
                    └──────┬──────┘
                           │
                    ┌──────▼────────────┐
                    │ View Rooms Page   │
                    └──────┬────────────┘
                           │
                    ┌──────▼──────────────┐
                    │ Select Room        │
                    └──────┬──────────────┘
                           │
                    ┌──────▼─────────────────┐
                    │ Enter Check-in/Out     │
                    └──────┬─────────────────┘
                           │
                    ┌──────▼─────────────────┐     No
                    │ Valid Dates?     ◇─────┴──────┐
                    └──────┬──────────────┘          │
                    Yes    │                        ▼
                           │                ┌───────────────┐
                           │                │ Show Error    │
                           │                └───────┬───────┘
                           │                        │
                           │                        └──┐
                           │                           │
                    ┌──────▼────────────────┐  ┌──────▼──┐
                    │ Create Booking       │  │ Retry   │
                    └──────┬────────────────┘  └────┬────┘
                           │                        │
                    ┌──────▼────────────────┐       │
                    │ Create Payment       │◄──────┘
                    └──────┬────────────────┘
                           │
                    ┌──────▼────────────────┐
                    │ Mark Room Unavail.   │
                    └──────┬────────────────┘
                           │
                    ┌──────▼────────────────┐
                    │ Show Confirmation    │
                    └──────┬────────────────┘
                           │
                    ┌──────▼──────┐
                    │    END      │
                    └─────────────┘
```

---

## 4. SEQUENCE DIAGRAM

### Description
Shows interactions between objects/actors over time.

#### Login Sequence:

```
Guest        UI        Controller      Database
  │          │              │              │
  ├─ Enter email/pass ─────►│              │
  │          │              │              │
  │          │      ┌───────┴──────────────┤
  │          │      │ Query user by email  │
  │          │      │                      │
  │          │      │         Find user ◄──┤
  │          │      │                      │
  │          ◄──────┴──────────────────────┤
  │          │              │              │
  │          │      ┌───────┴──────────────┤
  │          │      │ Verify password hash │
  │          │      │                      │
  │          │      │         OK ◄─────────┤
  │          │      │                      │
  │          │      │ Create session       │
  │          │      │ Store user data      │
  │          │      │                      │
  │ ◄────────┴──────┴──────────────────────┤
  │        Redirect to Dashboard            │
  │          │              │              │
```

---

## 5. COMPONENT DIAGRAM

### Description
Shows high-level system architecture and component dependencies.

```
┌──────────────────────────────────────────────────────────────┐
│                   Hotel Reservation System                    │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              Presentation Layer                         ││
│  │  ┌──────────────────────────────────────────────────┐  ││
│  │  │  HTML Templates                                 │  ││
│  │  │  - login.html, register.html, dashboard.html    │  ││
│  │  │  - admin_dashboard.html, admin_rooms.html      │  ││
│  │  └──────────────────────────────────────────────────┘  ││
│  │  ┌──────────────────────────────────────────────────┐  ││
│  │  │  Static Files (CSS, JS)                          │  ││
│  │  │  - Styling and client-side validation           │  ││
│  │  └──────────────────────────────────────────────────┘  ││
│  └─────────────────────────────────────────────────────────┘│
│           │                                                  │
│           │ USES                                             │
│           ▼                                                  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │            Application Layer (Flask)                    ││
│  │  ┌──────────────────────────────────────────────────┐  ││
│  │  │  app.py (Flask Application)                      │  ││
│  │  │  - Route handlers                               │  ││
│  │  │  - Session management                           │  ││
│  │  │  - Decorators (@admin_required)                 │  ││
│  │  └──────────────────────────────────────────────────┘  ││
│  └─────────────────────────────────────────────────────────┘│
│           │                                                  │
│           │ USES                                             │
│           ▼                                                  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │           Business Logic Layer                         ││
│  │  ┌──────────────────────────────────────────────────┐  ││
│  │  │  DatabaseManager (Singleton)                    │  ││
│  │  │  - User management                              │  ││
│  │  │  - Room management                              │  ││
│  │  │  - Booking operations                           │  ││
│  │  │  - Payment tracking                             │  ││
│  │  └──────────────────────────────────────────────────┘  ││
│  └─────────────────────────────────────────────────────────┘│
│           │                                                  │
│           │ USES                                             │
│           ▼                                                  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │            Data Access Layer                           ││
│  │  ┌──────────────────────────────────────────────────┐  ││
│  │  │  SQLite3 Database                               │  ││
│  │  │  - users table                                  │  ││
│  │  │  - rooms table                                  │  ││
│  │  │  - bookings table                               │  ││
│  │  │  - payments table                               │  ││
│  │  └──────────────────────────────────────────────────┘  ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## 6. DESIGN PATTERNS USED

### 6.1 Singleton Pattern
**Location:** `database.py` - `DatabaseManager` class  
**Purpose:** Ensures only one database connection instance exists  
**Implementation:** `__new__` method with `_instances` dictionary

```python
class DatabaseManager:
    _instances = {}
    
    def __new__(cls, db_path='hotel.db'):
        if db_path not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[db_path] = instance
        return cls._instances[db_path]
```

### 6.2 Decorator Pattern
**Location:** `app.py` - `@admin_required` decorator  
**Purpose:** Restricts route access to authenticated admin users  
**Implementation:** Python function decorator

```python
def admin_required(view_func):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            return redirect(url_for('dashboard'))
        return view_func(*args, **kwargs)
    return wrapper
```

### 6.3 MVC Pattern
**Location:** Throughout the application  
**Components:**
- **Model:** `DatabaseManager` class (data operations)
- **View:** HTML templates in `templates/` directory
- **Controller:** Flask routes in `app.py`

---

## 7. DIAGRAM TOOLS USED

These diagrams can be created/edited using:
- **Mermaid:** https://mermaid.live (online diagram tool)
- **Lucidchart:** https://lucidchart.com
- **Draw.io:** https://draw.io
- **PlantUML:** http://plantuml.com

---

*Last Updated: May 12, 2026*
