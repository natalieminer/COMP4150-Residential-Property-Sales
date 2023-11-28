from flask import Flask, render_template, request, redirect, url_for, jsonify
import pyodbc
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, static_folder='static')

# Retrieve database credentials from environment variables
server = os.getenv('DB_SERVER')
database = os.getenv('DB_DATABASE')
username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')
driver = os.getenv('DB_DRIVER')

# Create a connection string
connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};'

# Function to create a database connection
def create_connection():
    try:
        connection = pyodbc.connect(connection_string)
        print(f"Database connected successfully")
        return connection
    except pyodbc.Error as ex:
        # Handle database connection error
        print(f"Database connection error: {ex}")
        return None

# Function to run before each request
@app.before_request
def before_request():
    if not hasattr(app, 'database_connection'):
        # Open a connection to the database at server startup
        app.database_connection = create_connection()

# Function to run after each request
@app.teardown_appcontext
def teardown_appcontext(exception=None):
    # Close the database connection after each request if it's not closed already
    connection = getattr(app, 'database_connection', None)
    if connection is not None and not connection.closed:
        connection.close()

# Route for the login page
@app.route('/login', methods=['GET','POST'])
def login():
    print(request.method)  # Check if the request method is POST
    print(request.form)    # Check the form data received

    if request.method == 'POST':
        # Use request.form.get() to access form data
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"UsernameServer: {username}")
        print(f"PasswordServer: {password}")

        # Protect against SQL injection (use parameterized queries for production)
        query = f"SELECT * FROM users WHERE username=? AND password_hash=?"

        try:
            # Get the database connection from the app context
            connection = getattr(app, 'database_connection', None)

            if connection is None:
                # Database connection error, return an error message
                return render_template('login.html', error='Error connecting to the database'), 500

            if connection.closed:
                # Database connection is closed, reopen it
                connection = create_connection()
                setattr(app, 'database_connection', connection)

            # Execute the query with parameters
            cursor = connection.cursor()
            cursor.execute(query, (username, password))

            # Fetch user data
            user_data = cursor.fetchone()

            # Close the cursor (connection remains open for subsequent requests)
            cursor.close()

            if user_data:
                # Successful login, redirect to a new page or perform further actions
                print(f"Connection successful")
                return redirect(url_for('main_page'))

            # Invalid login
            return render_template('login.html', error='Invalid username or password'), 401

        except Exception as e:
            return f"Error: {str(e)}", 500  # Internal Server Error

    return render_template('login.html')


# Route for Main Page
@app.route('/main_page', methods=['GET', 'POST'])
def main_page():
    result = []  # Initialize the result variable outside the if block
    
    if request.method == 'POST':
        selected_query = request.form.get('querySelector')

        if selected_query == 'query1':
            print(f"Query 1 selected")
            result = execute_oldest_property_sale_query()
            print(f"Query Results: {result}")
            return jsonify(results=result)
        elif selected_query == 'query2':
            print(f"Query 2 selected")
            result = execute_newest_property_sale_query()
            print(f"Query Results: {result}")
            return jsonify(results=result)
        elif selected_query == 'query3':
            print(f"Query 3 selected")
            result = execute_sales_count_and_price_sum_by_date_query()
            print(f"Query Results: {result}")
            return jsonify(results=result, reload=True)
        else:
            result = []

    return render_template('main_page.html', results=result)


    
# OLDEST PROPERTY QUERY
def execute_oldest_property_sale_query():
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Retrieve the oldest property sale date
        cursor.execute("SELECT FORMAT(MIN(datesold), 'MM/dd/yyyy') AS oldest_property_sale FROM raw_sales;")
        result = cursor.fetchone()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return [result[0]] if result else None

    except Exception as e:
        print(f"Error executing oldest property sale query: {str(e)}")
        return None

# NEWEST PROPERTY QUERY
def execute_newest_property_sale_query():
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Retrieve the newest property sale date
        cursor.execute("SELECT FORMAT(MAX(datesold), 'MM/dd/yyyy') AS newest_property_sale FROM raw_sales;")
        result = cursor.fetchone()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return [result[0]] if result else None

    except Exception as e:
        print(f"Error executing newest property sale query: {str(e)}")
        return None

# SALES COUNT AND PRICE SUM BY DATE QUERY
def execute_sales_count_and_price_sum_by_date_query():
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Retrieve sales count and price sum by date
        cursor.execute("""
            SELECT TOP 10 datesold, count(1) as sales_count, sum(price) as price_sum
            FROM raw_sales
            GROUP BY datesold
            ORDER BY sales_count DESC;
        """)
        rows = cursor.fetchall()

        # Convert rows to a list of dictionaries
        result = [{'datesold': row[0], 'sales_count': row[1], 'price_sum': row[2]} for row in rows]

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return result

    except Exception as e:
        print(f"Error executing sales count and price sum by date query: {str(e)}")
        return None


# Route for about us page
@app.route('/about_us_page')
def about_us_page():
    return render_template('about_us_page.html')


# Route for sign up page
@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"Received form data - Username: {username}, Password: {password}")
    
        # Insert user data into the 'users' table
        query = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
  
        try:
            connection = getattr(app, 'database_connection', None)

            if connection is None:
                # Database connection error, return an error message
                return render_template('login.html', error='Error connecting to the database'), 401
            
            if connection.closed:
                # Database connection is closed, reopen it
                connection = create_connection()
                setattr(app, 'database_connection', connection)
               

            cursor = connection.cursor()
            cursor.execute(query, (username, password, access_type))
            connection.commit()
            cursor.close()

        except Exception as e:
            import traceback
            traceback.print_exc()
            return render_template('sign_up.html', error=f"Error: {str(e)}"), 500

    return render_template('sign_up.html')


# Route for admin page
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        # Retrieve form data
        datesold = request.form.get('datesold')
        postcode = request.form.get('postcode')
        price = request.form.get('price')
        property_type = request.form.get('propertyType')
        bedrooms = request.form.get('bedrooms')

        # Insert the form data into the database
        query = "INSERT INTO raw_sales (datesold, postcode, price, propertyType, bedrooms) VALUES (?, ?, ?, ?, ?)"
        
        try:
            connection = getattr(app, 'database_connection', None)

            if connection is None:
                # Database connection error, return an error message
                return render_template('admin.html', error='Error connecting to the database'), 401

            if connection.closed:
                # Database connection is closed, reopen it
                connection = create_connection()
                setattr(app, 'database_connection', connection)

            cursor = connection.cursor()
            cursor.execute(query, (datesold, postcode, price, property_type, bedrooms))
            connection.commit()
            cursor.close()
            return "New Property submitted successfully"

        except Exception as e:
            import traceback
            traceback.print_exc()
            return render_template('admin.html', error=f"Error: {str(e)}"), 500

    return render_template('admin.html')


if __name__ == '__main__':
    app.run(debug=True)
