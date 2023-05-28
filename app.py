from flask import Flask, render_template, request, flash, current_app, g, get_flashed_messages, redirect, url_for
from datetime import datetime
import sqlite3
import os
import secrets
import signal

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Set a secret key for flash messaging

# Flag to track application termination
app_terminated = False

app.config['DATABASE'] = 'data.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(current_app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST' and request.form:
        # Retrieve form data
        table_no = request.form.get('table_no')
        your_name = request.form.get('your_name')
        food_1 = request.form.get('food_1')
        food_2 = request.form.get('food_2')
        food_3 = request.form.get('food_3')
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        try:
            with app.app_context():
                db = get_db()
                cursor = db.cursor()

                # Create a table to store the form data
                cursor.execute('''CREATE TABLE IF NOT EXISTS form_data
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    table_no TEXT,
                    your_name TEXT,
                    food_1 TEXT,
                    food_2 TEXT,
                    food_3 TEXT)''')

                # Insert the form data into the table
                cursor.execute('''INSERT INTO form_data (timestamp, table_no, your_name, food_1, food_2, food_3)
                                VALUES (?, ?, ?, ?, ?, ?)''',
                            (timestamp, table_no, your_name, food_1, food_2, food_3))

                # Commit the changes to the database
                db.commit()

            return redirect(url_for('index'))
            # Display success message using flash
            # flash('Items added successfully!', 'success')
        except Exception as e:
            # Display error message using flash
            flash(f'Error occurred: {str(e)}', 'error')

    return render_template('questions.html', messages=get_flashed_messages())

@app.route('/data')
def data():
    try:
        db = get_db()
        cursor = db.cursor()
        # Fetch data from the database and sort by timestamp
        cursor.execute('''SELECT * FROM form_data ORDER BY timestamp''')
        rows = cursor.fetchall()
        
        if len(rows) == 0:
            # No data in the database
            message = "No data to display"
            return render_template('data.html', rows=rows, message=message)
        
        return render_template('data.html', rows=rows)
    except Exception as e:
        # Exception occurred while reading data
        message = f"Error occurred: {str(e)}"
        return render_template('data.html', message=message)
    
def terminate_app(signal, frame):
    global app_terminated
    app_terminated = True

# Register termination signal handler
signal.signal(signal.SIGTERM, terminate_app)

# Close the database connection when the application is terminated
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        try:
            if app_terminated:
                cursor = db.cursor()
                cursor.execute("DELETE FROM form_data")  # Delete all records from the table
                db.commit()  # Commit the changes

            db.close()
        except Exception as e:
            print(f"Error closing the database connection: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
