from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

def get_db_connection():
    # Replace with your own database connection logic
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='password',
        database='badminton_raptor'
    )

def update_rating():
    data = request.json
    user_id = data.get('user_id')
    recommendation_id = data.get('recommendation_id')
    rating = data.get('rating')

    # Validate input
    if not all([user_id, recommendation_id, rating]):
        return jsonify({'error': 'Missing required parameters'}), 400

    if not (1 <= rating <= 5):
        return jsonify({'error': 'Rating must be an integer between 1 and 5'}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Update the rating in the recommendations table
        query = """
            UPDATE recommendations
            SET rating = %s
            WHERE userID = %s AND FIND_IN_SET(%s, equipment_ids) > 0
        """
        cursor.execute(query, (rating, user_id, recommendation_id))
        
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({'error': 'No matching record found'}), 404

        return jsonify({'success': True})

    except Error as err:
        print(f"Database error: {err}")
        return jsonify({'error': 'An error occurred while updating the rating'}), 500

    finally:
        try:
            if connection.is_connected():
                connection.close()
        except Error as close_err:
            print(f"Error closing connection: {close_err}")

if __name__ == '__main__':
    app.run(debug=True)
