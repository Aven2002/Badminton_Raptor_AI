from flask import Flask
from flask_cors import CORS
from routes.recommendations_routes import recommendations_bp
from routes.update_rating_routes import update_rating_bp

app = Flask(__name__)

# Enable CORS for all origins (for development purposes)
CORS(app)

app.register_blueprint(recommendations_bp)
app.register_blueprint(update_rating_bp)

if __name__ == '__main__':
    app.run(debug=True)
