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
@app.route('/login', methods=['GET', 'POST'])
def login():
    print(request.method)  # Check if the request method is POST
    print(request.form)  # Check the form data received

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
        elif selected_query == 'query4':
            print(f"Query 4 selected")
            result = execute_total_sales_by_date_query()
            print(f"Query Results: {result}")
            return jsonify(results=result, reload=True)
        elif selected_query == 'query5':
            print(f"Query 5 selected")
            result = execute_highest_avg_sales_postcode_query()
            print(f"Query Results: {result}")
            return jsonify(results=result, reload=True)
        elif selected_query == 'query6':
            print(f"Query 6 selected")
            result = execute_total_sales_by_year_query()
            print(f"Query Results: {result}")
            return jsonify(results=result, reload=True)
        elif selected_query == 'query7':
            print(f"Query 7 selected")
            result = execute_sales_ranking_by_postcode_query()
            print(f"Query Results: {result}")
            return jsonify(results=result, reload=True)
        elif selected_query == 'query8':
            print(f"Query 8 selected")
            result = execute_properties_sold_by_year_query()
            print(f"Query Results: {result}")
            return jsonify(results=result, reload=True)
        elif selected_query == 'query9':
            print(f"Query 9 selected")
            result = execute_avg_price_by_property_type_over_years_query()
            print(f"Query Results: {result}")
            return jsonify(results=result, reload=True)
        elif selected_query == 'query10':
            print(f"Query 10 selected")
            result = execute_avg_price_property_type_bedroom_query()
            print(f"Query Results: {result}")
            return jsonify(results=result, reload=True)
        elif selected_query == 'query11':
            print(f"Query 11 selected")
            result = execute_sold_property_by_type_bedroom_query()
            print(f"Query Results: {result}")
            return jsonify(results=result, reload=True)
        elif selected_query == 'query12':
            print(f"Query 12 selected")
            result = execute_min_price_property_by_bedroom_query()
            print(f"Query Results: {result}")
            return jsonify(results=result, reload=True)
        elif selected_query == 'query13':
            print(f"Query 13 selected")
            result = execute_sales_by_month_years_query()
            print(f"Query Results: {result}")
            return jsonify(results=result, reload=True)
        elif selected_query == 'query14':
            print(f"Query 14 selected")
            result = execute_avg_price_bedroom_query()
            print(f"Query Results: {result}")
            return jsonify(results=result, reload=True)
        else:
            result = []

    return render_template('main_page.html', results=result)


# QUERY1 OLDEST PROPERTY QUERY
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


# QUERY2 NEWEST PROPERTY QUERY
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


# QUERY3 SALES COUNT AND PRICE SUM BY DATE QUERY
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
        result = [{'datesold': row[0], 'number of sales': row[1], 'total sale value (USD)': row[2]} for row in rows]

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return result

    except Exception as e:
        print(f"Error executing sales count and price sum by date query: {str(e)}")
        return None


# QUERY4 TOTAL SALES BY DATE
def execute_total_sales_by_date_query():
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Retrieve the total sales per date sold
        cursor.execute("""
            SELECT datesold, count(1) AS sales_count, sum(price) AS price_sum
            FROM raw_sales
            GROUP BY datesold
            ORDER BY sales_count desc;
            """)
        results = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Convert the results to a list of dictionaries
        result_list = [{"Date sold": row[0], "Number of sales": row[1], "Total sale value (USD)": row[2]} for row in results]

        return result_list if result_list else None

    except Exception as e:
        print(f"Error executing total sales by date query: {str(e)}")
        return None



#QUERY5 HIGHEST AVERAGE SALES BY POSTCODES
def execute_highest_avg_sales_postcode_query():
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Retrieve the highest avg sales by postcode
        cursor.execute("""
            SELECT postcode, CAST(AVG(price) AS DECIMAL(10, 0)) AS price_avg, count(1) AS sales_count
            FROM raw_sales
            GROUP BY postcode
            ORDER BY price_avg DESC;
            """)
        results = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Convert the results to a list of dictionaries
        result_list = [{"Postcode": row[0], "Average price (USD)": row[1], "Number of sales": row[2]} for row in results]

        return result_list if result_list else None

    except Exception as e:
        print(f"Error executing highest average sales by postcode query: {str(e)}")
        return None


# QUERY6 TOTAL SALES BY YEAR
def execute_total_sales_by_year_query():
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Retrieve the total sales per year
        cursor.execute("""
            SELECT YEAR(datesold) AS sales_year, COUNT(1) AS sales_count, SUM(price) AS price_sum
            FROM raw_sales
            GROUP BY YEAR(datesold)
            ORDER BY sales_count;
            """)
        results = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Convert the results to a list of dictionaries
        result_list = [{"Sales year": row[0], "Number of sales": row[1], "Total sale value (USD)": row[2]} for row in results]

        return result_list if result_list else None

    except Exception as e:
        print(f"Error executing total sales by year query: {str(e)}")
        return None



# QUERY7 SALES RANKING BY POSTCODES
def execute_sales_ranking_by_postcode_query():
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Retrieve the sales ranking by postcode
        cursor.execute("""
            SELECT * FROM
            (
                SELECT year, postcode, price_sum, ROW_NUMBER() OVER (PARTITION BY year ORDER BY price_sum DESC) AS ranking
                FROM (
                    SELECT YEAR(datesold) AS year, postcode, SUM(price) AS price_sum
                    FROM raw_sales
                    GROUP BY YEAR(datesold), postcode
                ) AS a
            ) AS b
            WHERE ranking <= 5
            ORDER BY year, ranking;
        """)
        results = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Convert the results to a list of dictionaries
        result_list = [{"Sale year": row[0], "postcode": row[1], "Total sale value (USD)": row[2], "Ranking": row[3]} for row in results]

        return result_list if result_list else None

    except Exception as e:
        print(f"Error executing sales ranking by postcode query: {str(e)}")
        return None


# QUERY8 PROPERTIES SOLD BY YEARS
def execute_properties_sold_by_year_query():
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Retrieve the properties sold by years
        cursor.execute("""
            SELECT 
                YEAR(datesold) AS year, 
                SUM(CASE WHEN propertyType = 'house' THEN 1 ELSE 0 END) AS house_sales_count,
                SUM(CASE WHEN propertyType = 'unit' THEN 1 ELSE 0 END) AS unit_sales_count
            FROM raw_sales
            GROUP BY YEAR(datesold);
            """)
        results = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Convert the results to a list of dictionaries
        result_list = [{"Sale year": row[0], 
                        "Total House Sales": row[1], 
                        "Total Unit Sales": row[2]} for row in results]

        return result_list if result_list else None

    except Exception as e:
        print(f"Error executing properties sold by year query: {str(e)}")
        return None



# QUERY9 AVERAGE PRICE BY PROPERTY TYPE OVER YEARS
def execute_avg_price_by_property_type_over_years_query():
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Retrieve the avg_price_by_property_type_over_years
        cursor.execute("""
            SELECT 
                YEAR(datesold) as year,
                AVG(CASE WHEN propertyType = 'house' THEN price ELSE NULL END) as house_price_avg,
                AVG(CASE WHEN propertyType = 'unit' THEN price ELSE NULL END) as unit_price_avg
            FROM raw_sales
            GROUP BY YEAR(datesold);
            """)
        results = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Convert the results to a list of dictionaries
        result_list = [{"Sale Year": row[0], 
                        "House Price Avg (USD)": row[1], 
                        "Unit Price Avg (USD)": row[2]} for row in results]

        return result_list if result_list else None

    except Exception as e:
        print(f"Error executing average price by property type over years query: {str(e)}")
        return None


# QUERY10 AVERAGE PRICE BY PROPERTY TYPE & BEDROOMS
def execute_avg_price_property_type_bedroom_query():
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Retrieve the avg_price_property_type_bedroom
        cursor.execute("""
            SELECT propertyType, bedrooms, AVG(price) as avg_price
            FROM raw_sales
            GROUP BY propertyType, bedrooms;
            """)
        results = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Convert the results to a list of dictionaries
        result_list = [{"Property Type": row[0], "Number of Bedrooms": row[1], "Avg Price (USD)": row[2]} for row in results]

        return result_list if result_list else None

    except Exception as e:
        print(f"Error executing average price property type by bedroom query: {str(e)}")
        return None



# QUERY11 SOLD PROPERTIES BY PROPERTY TYPE & BEDROOMS
def execute_sold_property_by_type_bedroom_query():
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Retrieve the sold_property_by_type_bedroom
        cursor.execute("""
            SELECT propertyType, bedrooms, COUNT(*) as sales_count
            FROM raw_sales
            GROUP BY propertyType, bedrooms
            ORDER BY propertyType, bedrooms;
            """)
        results = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Convert the results to a list of dictionaries
        result_list = [{"Property Type": row[0], "Number Bedrooms": row[1], "Total Sales": row[2]} for row in results]

        return result_list if result_list else None

    except Exception as e:
        print(f"Error executing sold property by property type & bedroom query: {str(e)}")
        return None


# QUERY12 MINIMUM PRICE OF PROPERTIES BY BEDROOMS
def execute_min_price_property_by_bedroom_query():
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Retrieve the min_price_property_by_bedroom
        cursor.execute("""
            SELECT propertyType, bedrooms, MIN(price) as min_price
            FROM raw_sales
            GROUP BY propertyType, bedrooms
            ORDER BY propertyType, bedrooms;
            """)
        results = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Convert the results to a list of dictionaries
        result_list = [{"Property Type": row[0], "Number Bedrooms": row[1], "Min Price (USD)": row[2]} for row in results]

        return result_list if result_list else None

    except Exception as e:
        print(f"Error executing minimum price property by bedroom query: {str(e)}")
        return None


# QUERY13 SALES BY MONTHS OF YEARS
def execute_sales_by_month_years_query():
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Retrieve the sales_by_month_years
        cursor.execute("""
            SELECT FORMAT(datesold, 'yyyy-MM') AS sale_month, COUNT(*) AS sales_count
            FROM raw_sales
            GROUP BY FORMAT(datesold, 'yyyy-MM')
            ORDER BY sale_month;
            """)
        results = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Convert the results to a list of dictionaries
        result_list = [{"Sale Year-Month": row[0], "Total Sales": row[1]} for row in results]

        return result_list if result_list else None

    except Exception as e:
        print(f"Error executing sales by month years query: {str(e)}")
        return None


# QUERY14 AVERAGE PRICE BY BEDROOMS
def execute_avg_price_bedroom_query():
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Retrieve the avg_price_bedroom
        cursor.execute("""
            SELECT YEAR(datesold) AS sale_year, bedrooms, CAST(AVG(price) AS DECIMAL(10, 0)) AS avg_price
            FROM raw_sales
            GROUP BY YEAR(datesold), bedrooms
            ORDER BY sale_year, bedrooms;
            """)
        results = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Convert the results to a list of dictionaries
        result_list = [{"Sale Year": row[0], "Number Bedrooms": row[1], "Avg Price (USD)": row[2]} for row in results]

        return result_list if result_list else None

    except Exception as e:
        print(f"Error executing average price by bedroom query: {str(e)}")
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
            cursor.execute(query, (username, password))
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
