from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from backend.Login import login_bp
from backend.Logout import logout_bp
from backend.Home import home_bp
from backend.Register import register_bp
from backend.Upload import upload_bp
from backend.Record import record_bp
from backend.History import history_bp
from backend.Newborns import newborns_bp
from backend.User import user_bp


app = Flask(__name__, static_url_path='/static')
CORS(app)
CORS(app, origins=['http://127.0.0.1:5000'])
app.secret_key = 'mysecretkey'

# Configuration for MongoDB
app.config['MONGO_URI'] = 'mongodb://localhost:27017/Crybaby'
app.config['mongo'] = PyMongo(app)

app.register_blueprint(login_bp, url_prefix='/')
app.register_blueprint(logout_bp)
app.register_blueprint(home_bp)
app.register_blueprint(register_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(record_bp)
app.register_blueprint(history_bp)
app.register_blueprint(newborns_bp)
app.register_blueprint(user_bp)


if __name__ == '__main__':    app.run(debug=True)
