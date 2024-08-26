from flask import Flask, request, jsonify
from utils.recommendation import generate_recommendations 

app = Flask(__name__)

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
    app.run(debug=True)
