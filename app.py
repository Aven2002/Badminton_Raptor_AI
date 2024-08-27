from flask import Flask, request, jsonify
from utils.recommendation import generate_recommendations 
import mysql.connector  # Import mysql.connector for MySQL connection

app = Flask(__name__)

def connect_to_mysql():
    """ Function to connect to MySQL and print status """
    try:
        # Example connection (adjust parameters as needed)
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',  
            database='Badminton_Raptor_Store'
        )
        if connection.is_connected():
            print("MySQL connected...")
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

@app.route('/api/recommendations', methods=['GET'])
def recommendations():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    try:
        user_id = int(user_id)  # Ensure user_id is an integer
        recommendations = generate_recommendations(user_id)
        return jsonify(recommendations), 200
    except ValueError:
        return jsonify({'error': 'Invalid User ID format'}), 400

if __name__ == '__main__':
    connect_to_mysql()  # Call the MySQL connection function
    print("Server is running on http://localhost:5000")
    app.run(debug=True, port=5000)  # Set port to 5000
