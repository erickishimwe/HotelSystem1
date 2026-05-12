import sqlite3
import os

path = 'hotel.db'
print('db path:', os.path.abspath(path))
conn = sqlite3.connect(path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print('tables:')
for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
    print('-', row['name'])

print('\nusers rows:')
for row in cur.execute('SELECT id, name, email, password FROM users LIMIT 10'):
    print(dict(row))

print('\nrooms rows:')
for row in cur.execute('SELECT id, room_number, room_type, price_per_night, status FROM rooms LIMIT 10'):
    print(dict(row))

print('\nbookings rows:')
for row in cur.execute('SELECT id, user_id, room_id, check_in, check_out, status FROM bookings LIMIT 10'):
    print(dict(row))

print('\npayments rows:')
for row in cur.execute('SELECT id, booking_id, amount, payment_method, status FROM payments LIMIT 10'):
    print(dict(row))

conn.close()
