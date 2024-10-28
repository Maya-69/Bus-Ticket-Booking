from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key for session management

# Database setup function
def init_sqlite_db():
    # Create a SQLite database and tables if they do not exist
    with sqlite3.connect('bus_ticket_booking.db') as conn:
        cursor = conn.cursor()
        # Users table to store usernames and hashed passwords
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )''')
        # Routes table to store bus route details
        cursor.execute('''CREATE TABLE IF NOT EXISTS routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            route_name TEXT NOT NULL,
            bus_name TEXT NOT NULL,
            departure_time TEXT NOT NULL,
            price REAL NOT NULL
        )''')
        # Seats table to store seat availability for routes
        cursor.execute('''CREATE TABLE IF NOT EXISTS seats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            route_id INTEGER NOT NULL,
            seat_number TEXT NOT NULL,
            is_booked BOOLEAN NOT NULL DEFAULT 0,
            FOREIGN KEY (route_id) REFERENCES routes (id)
        )''')
    conn.close()

# Initialize the database
init_sqlite_db()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        with sqlite3.connect('bus_ticket_booking.db') as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
                conn.commit()
                flash('Signup successful! Please log in.', 'success')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('Username already exists. Please choose a different one.', 'error')

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Hardcoded check for admin credentials
        if username == 'admin' and password == 'adminpass':
            session['user'] = 'admin'
            return redirect(url_for('admin_dashboard'))

        with sqlite3.connect('bus_ticket_booking.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
            record = cursor.fetchone()
        
        if record and check_password_hash(record[0], password):
            session['user'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('main_page'))
        
        flash('Incorrect username or password. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/main')
def main_page():
    if 'user' not in session:
        flash('You must log in first!', 'error')
        return redirect(url_for('login'))
    return render_template('main.html', user=session['user'])

@app.route('/admin', methods=['GET'])
def admin_dashboard():
    if 'user' not in session or session['user'] != 'admin':
        flash('Unauthorized access to admin dashboard!', 'error')
        return redirect(url_for('login'))
    
    with sqlite3.connect('bus_ticket_booking.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM routes")
        routes = cursor.fetchall()
    
    return render_template('admin.html', routes=routes)

@app.route('/view-route', methods=['GET'])
def view_route():
    if 'user' not in session or session['user'] != 'admin':
        flash('Unauthorized access!', 'error')
        return redirect(url_for('login'))

    with sqlite3.connect('bus_ticket_booking.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM routes")
        routes = cursor.fetchall()
    
    return render_template('view-route.html', routes=routes)

@app.route('/delete-route/<int:route_id>', methods=['POST'])
def delete_route(route_id):
    if 'user' not in session or session['user'] != 'admin':
        flash('Unauthorized access!', 'error')
        return redirect(url_for('login'))

    with sqlite3.connect('bus_ticket_booking.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM routes WHERE id = ?", (route_id,))
        conn.commit()
        
    flash('Route deleted successfully!', 'success')
    return redirect(url_for('view_route'))

@app.route('/add-route', methods=['GET', 'POST'])
def add_route():
    if 'user' not in session or session['user'] != 'admin':
        flash('Unauthorized access!', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        bus_name = request.form['bus_name']
        route_name = request.form['route_name']
        departure_time = request.form['departure_time']
        price = request.form['price']
        num_seats = int(request.form['num_seats'])

        with sqlite3.connect('bus_ticket_booking.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO routes (route_name, bus_name, departure_time, price) VALUES (?, ?, ?, ?)",
                           (route_name, bus_name, departure_time, price))
            route_id = cursor.lastrowid
            
            for seat_num in range(1, num_seats + 1):
                seat_number = f'Seat-{seat_num}'
                cursor.execute("INSERT INTO seats (route_id, seat_number) VALUES (?, ?)", (route_id, seat_number))
            
            conn.commit()
        
        flash('Bus route and seats added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('add-route.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/book-bus')
def book_bus():
    with sqlite3.connect('bus_ticket_booking.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM routes")
        routes = cursor.fetchall()
    return render_template('book-bus.html', routes=routes)

@app.route('/book/available-seats/<int:route_id>', methods=['GET'])
def available_seats(route_id):
    if 'user' not in session:
        flash('You must log in first!', 'error')
        return redirect(url_for('login'))

    with sqlite3.connect('bus_ticket_booking.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT seat_number, is_booked FROM seats WHERE route_id = ?", (route_id,))
        available_seats = cursor.fetchall()
        seats = [{'number': seat[0], 'available': not seat[1]} for seat in available_seats]

    return render_template('available-seats.html', route_id=route_id, seats=seats)

@app.route('/book-seat', methods=['POST'])
def book_seat():
    if 'user' not in session:
        flash('You must log in first!', 'error')
        return redirect(url_for('login'))

    data = request.get_json()

    if not data or 'seat_number' not in data or 'route_id' not in data:
        return jsonify({'message': 'Invalid data received'}), 400

    seat_number = data['seat_number']
    route_id = data['route_id']

    with sqlite3.connect('bus_ticket_booking.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_booked FROM seats WHERE route_id = ? AND seat_number = ?", (route_id, seat_number))
        seat_status = cursor.fetchone()

        if seat_status and seat_status[0] == 0:
            cursor.execute("UPDATE seats SET is_booked = 1 WHERE route_id = ? AND seat_number = ?", (route_id, seat_number))
            conn.commit()
            return jsonify({'message': f'Booking successful for seat {seat_number}'}), 200
        else:
            return jsonify({'message': f'Seat {seat_number} is already booked.'}), 410

@app.route('/my-bookings')
def my_bookings():
    if 'user' not in session:
        flash('You must log in first!', 'error')
        return redirect(url_for('login'))

    username = session['user']

    with sqlite3.connect('bus_ticket_booking.db') as conn:
        cursor = conn.cursor()
        
        # Retrieve bookings for the logged-in user
        cursor.execute('''SELECT routes.route_name, seats.seat_number, routes.departure_time, routes.price, seats.id AS seat_id 
                          FROM seats 
                          JOIN routes ON seats.route_id = routes.id 
                          WHERE seats.is_booked = 1
                          ''')
        bookings = cursor.fetchall()

    # Check if no bookings were found
    if not bookings:
        flash('No bookings found.', 'info')
    
    return render_template('my-bookings.html', bookings=bookings)

@app.route('/delete-booking/<int:seat_id>', methods=['POST'])
def delete_booking(seat_id):
    if 'user' not in session:
        flash('You must log in first!', 'error')
        return redirect(url_for('login'))

    with sqlite3.connect('bus_ticket_booking.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE seats SET is_booked = 0 WHERE id = ?", (seat_id,))
        conn.commit()
        
    flash('Booking deleted successfully!', 'success')
    return redirect(url_for('my_bookings'))

if __name__ == '__main__':
    app.run(debug=True)
