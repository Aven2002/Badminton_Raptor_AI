# utils/recommendation.py
import json
from flask import jsonify
from db import get_db_connection
import numpy as np
from datetime import datetime
import mysql.connector

WEIGHTS = {
    'category': 0.3,
    'price': 0.4,
    'feature_similarity': 0.3
}

def generate_recommendations(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Step 1: Determine User Preferences
        cursor.execute("""
            SELECT e.equipID, e.equipName, e.equipPrice, e.equipCategory, e.equipBrand, f.created_at
            FROM favorite f
            JOIN equipment e ON f.equipID = e.equipID
            WHERE f.userID = %s
        """, (user_id,))
        favorites = cursor.fetchall()

        if not favorites:
            cursor.execute("""
                SELECT equipID, equipName, equipPrice, equipCategory, equipBrand
                FROM equipment
                ORDER BY RAND() LIMIT 30
            """)
            fallback_recommendations = cursor.fetchall()
            cursor.execute("""
                INSERT INTO recommendations (userID, equipment_ids, category_scores, price_scores, feature_scores, final_scores, last_shown_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                json.dumps([item['equipID'] for item in fallback_recommendations]),
                json.dumps([0] * len(fallback_recommendations)),
                json.dumps([0] * len(fallback_recommendations)),
                json.dumps([0] * len(fallback_recommendations)),
                json.dumps([0] * len(fallback_recommendations)),
                datetime.now()
            ))
            connection.commit()
            return {'recommendations': fallback_recommendations}

        # Extract dates and calculate dynamic price range
        dates = [fav['created_at'] for fav in favorites]
        min_date = min(dates) if dates else datetime.now()
        max_date = max(dates) if dates else datetime.now()

        prices = [float(fav['equipPrice']) for fav in favorites]
        median_price = np.median(prices) if prices else 0
        q1, q3 = np.percentile(prices, [25, 75]) if prices else (0, 0)
        iqr = q3 - q1
        lower_bound = median_price - 1.5 * iqr if iqr else 0
        upper_bound = median_price + 1.5 * iqr if iqr else median_price

        # Calculate category and brand scores
        category_scores = {}
        brand_preference = {}
        for fav in favorites:
            category = fav['equipCategory']
            brand = fav['equipBrand']
            created_at = fav['created_at']

            days_range = (max_date - min_date).days
            recency_weight = 1 + (created_at - min_date).days / days_range if days_range > 0 else 1

            category_scores[category] = category_scores.get(category, 0) + recency_weight
            brand_preference[brand] = brand_preference.get(brand, 0) + 1

        # Step 2: Generate Recommendations
        cursor.execute("""
            SELECT e.equipID, e.equipName, e.equipPrice, e.equipCategory, e.equipBrand
            FROM equipment e
            LEFT JOIN favorite f ON e.equipID = f.equipID AND f.userID = %s
            WHERE f.equipID IS NULL
        """, (user_id,))
        all_equipment = cursor.fetchall()

        recommendations = []
        for item in all_equipment:
            category_score = category_scores.get(item['equipCategory'], 0)
            price_score = max(0, 100 - abs(float(item['equipPrice']) - median_price) / median_price * 100)
            feature_score = brand_preference.get(item['equipBrand'], 0)
            
            final_score = (WEIGHTS['category'] * category_score) + \
                          (WEIGHTS['price'] * price_score) + \
                          (WEIGHTS['feature_similarity'] * feature_score)
            
            if lower_bound <= float(item['equipPrice']) <= upper_bound:
                score = {
                    'equipID': item['equipID'],
                    'category_score': category_score,
                    'price_score': price_score,
                    'feature_score': feature_score,
                    'final_score': final_score
                }
                recommendations.append(score)

        recommendations.sort(key=lambda x: x['final_score'], reverse=True)
        top_recommendations = recommendations[:30]  # Get top 30 recommendations

        # Step 3: Insert into the database
        cursor.execute("""
            SELECT equipment_ids
            FROM recommendations
            WHERE userID = %s
        """, (user_id,))
        existing_recommendations = cursor.fetchone()
        
        existing_ids = json.loads(existing_recommendations['equipment_ids']) if existing_recommendations else []

        new_ids = [item['equipID'] for item in top_recommendations]

        if set(existing_ids) == set(new_ids):
            cursor.execute("""
                UPDATE recommendations
                SET last_shown_at = %s
                WHERE userID = %s
            """, (datetime.now(), user_id))
        else:
            cursor.execute("""
                INSERT INTO recommendations (userID, equipment_ids, category_scores, price_scores, feature_scores, final_scores, last_shown_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    equipment_ids = VALUES(equipment_ids),
                    category_scores = VALUES(category_scores),
                    price_scores = VALUES(price_scores),
                    feature_scores = VALUES(feature_scores),
                    final_scores = VALUES(final_scores),
                    last_shown_at = VALUES(last_shown_at)
            """, (
                user_id,
                json.dumps(new_ids),
                json.dumps([item['category_score'] for item in top_recommendations]),
                json.dumps([float(item['price_score']) for item in top_recommendations]),
                json.dumps([item['feature_score'] for item in top_recommendations]),
                json.dumps([item['final_score'] for item in top_recommendations]),
                datetime.now()
            ))
        connection.commit()

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return {'error': 'An error occurred while generating recommendations.'}

    finally:
        cursor.close()
        connection.close()

    return {'recommendations': top_recommendations}
