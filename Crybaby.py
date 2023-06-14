from flask import Flask
import os
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
from backend.Edit import edit_bp
from backend.Edit import delete_bp
import gdown
from waitress import serve
           
app = Flask(__name__, static_url_path='/static')

CORS(app)
CORS(app, origins=['http://127.0.0.1:5000'])
app.secret_key = 'mysecretkey'

## Configuration for MongoDB - change string to your online MongoDB database
#app.config['MONGO_URI'] = 'mongodb+srv://Crybaby:XtQUCMWF1HcKVjN9@cluster0.hleztpr.mongodb.net/'

# Local host configuration
app.config['MONGO_URI'] = 'mongodb://localhost:27017/'

app.config['mongo'] = PyMongo(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16mb file max
env_config = os.getenv("PROD_APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)  
app.register_blueprint(login_bp, url_prefix='/')
app.register_blueprint(logout_bp)
app.register_blueprint(home_bp)
app.register_blueprint(register_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(record_bp)
app.register_blueprint(history_bp)
app.register_blueprint(newborns_bp)
app.register_blueprint(user_bp)
app.register_blueprint(edit_bp)
app.register_blueprint(delete_bp)

def download_model():
    # Define the local file path to save the downloaded model
    output_file = "model1.h5"

    # Check if the model file already exists
    if not os.path.exists(output_file):
        # URL to download the model file from Google Drive
        url = "https://drive.google.com/uc?id=1OxnbLXM2ACvXUiXRAP64nqCoQs7xnv7Y"
        

        # Download the file using gdown library
        gdown.download(url, output_file, quiet=False)

        print("Model file downloaded successfully.")
    else:
        print("Model file already exists.")
 
# Call the function to download the model file (if needed)
download_model()

if __name__ == '__main__':
    # Development server
    #app.run(debug=True,host="0.0.0.0")
    app.run(debug=True)
  
    #Production server
    #serve(app, host='0.0.0.0', port=5000)
    