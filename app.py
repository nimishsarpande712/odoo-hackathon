from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ShreeKrisha@7@localhost/skill_swap'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database with app
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)