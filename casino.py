from flask import Flask, render_template, request, session, redirect, url_for
import random
import mysql.connector
import string
from datetime import datetime
import secrets


app = Flask(__name__, static_url_path='/static')
app.secret_key = 'kjqfdsbsjhdfbuyzs'

DB_HOST = '127.0.0.1'
DB_USER = 'root'
DB_PASSWORD = ''
DB_DATABASE = 'manager2'

db = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_DATABASE
)
cur = db.cursor()


@app.route('/operations')
def operations():
    if 'username' not in session:
        return redirect(url_for('index'))

    client_operations_table = f"client_{session['username']}_operations"

    cur.execute(f"SELECT * FROM {client_operations_table}")
    operations = cur.fetchall()
    return render_template('index.html', operations=operations)


@app.route('/Pragmatic')
def pragmatic():

    return render_template('Pragmatic.html')


@app.route('/amatic')
def amatic():

    return render_template('Amatic.html')


@app.route('/soccer')
def soccer():

    return render_template('Soccer.html')


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('index1.html')


def connect_to_database():
    global db, cur
    db = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_DATABASE
    )
    cur = db.cursor()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connect_to_database()  # Establish database connection and cursor

        cur.execute(
            "SELECT * FROM clients WHERE name = %s AND password = %s", (username, password))
        client = cur.fetchone()

        if client:
            session['username'] = username
            create_client_tables(username)

            # Consume the result of the query before executing any other queries
            cur.fetchall()

            return redirect(url_for('dashboard'))
        else:
            # Consume the result of the query before rendering the template
            cur.fetchall()
            return render_template('login.html', error="Invalid username or password")
    else:
        return render_template('login.html')


@app.route('/logout', methods=['POST'])
def logout():
    if 'username' in session:
        session.pop('username')
        global cur  # Declare cur as a global variable
        cur.close()
        # Re-establish the database connection and cursor
        db = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE
        )
        cur = db.cursor()
    return redirect(url_for('index'))


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_name', None)
    global cur  # Declare cur as a global variable
    cur.close()
    # Re-establish the database connection and cursor
    db = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_DATABASE
    )
    cur = db.cursor()
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('index'))

    client_info_table = f"client_{session['username']}_info"
    client_operations_table = f"client_{session['username']}_operations"

    cur.execute(f"SELECT * FROM {client_info_table}")
    client_info = cur.fetchone()
    cur.fetchall()  # Consume the result set

    cur.execute(f"SELECT * FROM {client_operations_table}")
    operations = cur.fetchall()
    cur.fetchall()  # Consume the result set
    cur.execute("SELECT balance FROM clients WHERE name = %s",
                (session['username'],))
    current_balance = cur.fetchone()[0]

    # Fetch client's balance from the client table

    return render_template('dashboard.html', client_info=client_info, operations=operations, current_balance=current_balance)


@app.route('/create_user', methods=['POST'])
def create_user():

    number = ''.join(random.choices(string.digits, k=5))
    password = ''.join(random.choices(
        string.ascii_letters + string.digits, k=8))
    amount = request.form['amount']
   # Fetch client's balance
    cur.execute(
        "SELECT balance FROM clients WHERE name = %s", (session['username'],))
    client_balance = cur.fetchone()[0]

    client_info_table = f"client_{session['username']}_info"
    client_operations_table = f"client_{session['username']}_operations"
    if float(client_balance) >= float(amount):
        # Deduct amount from client's balance
        cur.execute(
            "UPDATE clients SET balance = balance - %s WHERE name = %s", (amount, session['username']))
        db.commit()

        cur.execute(f"INSERT INTO {client_info_table} (number, password, balance) VALUES (%s, %s, %s)",
                    (number, password, amount))
        db.commit()

        cur.execute(f"INSERT INTO {client_operations_table} (account_number, operation, amount, timestamp) VALUES (%s, %s, %s, %s)",
                    (number, "Create User", amount, datetime.now()))
        db.commit()

        message = "User created successfully! Number: {}, Password: {}".format(
            number, password)
        return render_template('dashboard.html', message1=message)
    else:
        return render_template('dashboard.html', message="Insufficient balance!")


@app.route('/recharge', methods=['POST'])
def recharge():
    number = request.form['number']
    amount = int(request.form['amount'])
 # Fetch client's balance
    cur.execute(
        "SELECT balance FROM clients WHERE name = %s", (session['username'],))
    client_balance = cur.fetchone()[0]

    client_info_table = f"client_{session['username']}_info"
    client_operations_table = f"client_{session['username']}_operations"
    if float(client_balance) >= float(amount):
        # Deduct amount from client's balance
        cur.execute(
            "UPDATE clients SET balance = balance - %s WHERE name = %s", (amount, session['username']))
        db.commit()

        cur.execute(
            f"UPDATE {client_info_table} SET balance = balance + %s WHERE number = %s", (amount, number))
        db.commit()

        cur.execute(f"INSERT INTO {client_operations_table} (account_number, operation, amount, timestamp) VALUES (%s, %s, %s, %s)",
                    (number, "Recharge", amount, datetime.now()))
        db.commit()

        return render_template('dashboard.html', message="Recharge successful!")
    else:
        return render_template('dashboard.html', message="Insufficient balance!")


@app.route('/withdraw', methods=['POST'])
def withdraw():
    number = request.form['number']
    amount = int(request.form['amount'])
    # Fetch user balance

    client_info_table = f"client_{session['username']}_info"
    client_operations_table = f"client_{session['username']}_operations"

    cur.execute(
        f"SELECT balance FROM {client_info_table} WHERE number = %s", (number,))
    user = cur.fetchone()

    if user:
        current_balance = user[0]
        if current_balance >= amount:
            cur.execute(
                f"UPDATE {client_info_table} SET balance = balance - %s WHERE number = %s", (amount, number))
            db.commit()
            cur.execute(
                "SELECT balance FROM clients WHERE name = %s", (session['username'],))
            client_balance = cur.fetchone()[0]
            cur.execute(
                "UPDATE clients SET balance = balance + %s WHERE name = %s", (amount, session['username']))
            db.commit()

            cur.execute(f"INSERT INTO {client_operations_table} (account_number, operation, amount, timestamp) VALUES (%s, %s, %s, %s)",
                        (number, "Withdraw", amount, datetime.now()))
            db.commit()

            return render_template('dashboard.html', message="Withdrawal successful!")
        else:
            return render_template('dashboard.html', message="Insufficient funds!")
    else:
        return render_template('dashboard.html', message="User not found!")


def create_client_tables(username):
    client_info_table = f"client_{username}_info"
    client_operations_table = f"client_{username}_operations"

    cur.execute("SHOW TABLES LIKE %s", (client_info_table,))
    info_table_exists = cur.fetchone()
    cur.execute("SHOW TABLES LIKE %s", (client_operations_table,))
    operations_table_exists = cur.fetchone()

    if not info_table_exists:
        cur.execute(f"""
            CREATE TABLE {client_info_table} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                number VARCHAR(5),
                password VARCHAR(8),
                balance DECIMAL(10, 2)
            )
        """)
        db.commit()

    if not operations_table_exists:
        cur.execute(f"""
            CREATE TABLE {client_operations_table} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                account_number VARCHAR(5),
                operation VARCHAR(255),
                amount DECIMAL(10, 2),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.commit()


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connect_to_database()  # Establish database connection and cursor

        cur.execute(
            "SELECT * FROM admins WHERE username = %s AND password = %s", (username, password))
        admin = cur.fetchone()

        if admin:
            session['admin'] = username  # Store admin username in session
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error="Invalid username or password")
    else:
        return render_template('admin_login.html')


@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    # Fetching clients list tables
    cur.execute("SHOW TABLES LIKE 'client\_%\_info'")
    client_tables = cur.fetchall()

    # Fetching clients' balances and calculating the sum
    cur.execute("SELECT SUM(balance) FROM clients")
    total_balance = cur.fetchone()[0]

    # Fetching the client with the highest balance
    cur.execute(
        "SELECT name, balance FROM clients ORDER BY balance DESC LIMIT 1")
    most_balance_client = cur.fetchone()

    return render_template('admin_dashboard.html', client_tables=client_tables,
                           total_balance=total_balance, most_balance_client=most_balance_client)


@app.route('/admin/create_client', methods=['POST'])
def create_client():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        client_name = request.form['client_name']
        initial_balance = request.form['initial_balance']
        password = generate_password()

        # Perform input validation if necessary

        connect_to_database()  # Establish database connection and cursor

        # Insert new client into the clients table
        cur.execute("INSERT INTO clients (name, password, balance) VALUES (%s, %s, %s)",
                    (client_name, password, initial_balance))
        db.commit()

        return redirect(url_for('admin_dashboard'))
    else:
        return render_template('admin_dashboard.html')


def generate_password():
    # Generate a random password using uppercase letters, lowercase letters, and digits
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(8))
    return password


@app.route('/admin/withdraw', methods=['POST'])
def admin_withdraw():
    client_name = request.form['client_name_withdraw']
    amount = float(request.form['withdraw_amount'])

    # Fetch client's balance
    cur.execute("SELECT balance FROM clients WHERE name = %s", (client_name,))
    client_balance = cur.fetchone()[0]

    if client_balance >= amount:
        # Deduct amount from client's balance
        cur.execute(
            "UPDATE clients SET balance = balance - %s WHERE name = %s", (amount, client_name))
        db.commit()

        return redirect(url_for('admin_dashboard'))
    else:
        return render_template('admin_dashboard.html', error="Insufficient funds!")


@app.route('/admin/recharge', methods=['POST'])
def admin_recharge():
    client_name = request.form['client_name_recharge']
    amount = float(request.form['recharge_amount'])

    # Add amount to client's balance
    cur.execute(
        "UPDATE clients SET balance = balance + %s WHERE name = %s", (amount, client_name))
    db.commit()

    return redirect(url_for('admin_dashboard'))


@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connect_to_database()  # Establish database connection and cursor
        cur.execute("SHOW TABLES LIKE 'client_%_info'")
        client_tables = cur.fetchall()

        for table in client_tables:
            client_table = table[0]
            cur.execute(
                f"SELECT * FROM {client_table} WHERE number = %s AND password = %s", (username, password))
            user = cur.fetchone()
            if user:
                session['username'] = username
                session['client_table'] = client_table
                return redirect(url_for('user_dashboard'))

        return render_template('user_login.html', error="Invalid username or password")
    else:
        return render_template('user_login.html')


@app.route('/user/dashboard')
def user_dashboard():
    if 'username' in session:

        cur.execute(
            f"SELECT * FROM {session['client_table']} WHERE number = %s", (session['username'],))
        user_data = cur.fetchone()
        return render_template('user_dashboard.html', user_data=user_data)
    else:
        return redirect(url_for('user_login'))


@app.route('/user/logout')
def user_logout():
    if 'username' in session:
        session.pop('username')
    if 'client_table' in session:
        session.pop('client_table')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
