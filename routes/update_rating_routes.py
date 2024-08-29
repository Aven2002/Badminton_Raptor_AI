# routes/update_rating_routes.py
from flask import Blueprint, request, jsonify
import mysql.connector
from mysql.connector import Error
from db import get_db_connection

update_rating_bp = Blueprint('update_rating', __name__)

@update_rating_bp.route('/api/update_rating', methods=['POST'])
def update_rating():
    data = request.json
    user_id = data.get('user_id')
    recommendation_id = data.get('recommendation_id')
    rating = data.get('rating')

    if not all([user_id, recommendation_id, rating]):
        return jsonify({'error': 'Missing required parameters'}), 400

    try:
        user_id = int(user_id)
        recommendation_id = int(recommendation_id)
        rating = float(rating)

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE recommendations
            SET rating = %s
            WHERE userID = %s AND recommendationID = %s
        """, (rating, user_id, recommendation_id))
        connection.commit()
        return jsonify({'message': 'Rating updated successfully'}), 200

    except Error as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred while updating the rating.'}), 500

    finally:
        cursor.close()
        connection.close()
