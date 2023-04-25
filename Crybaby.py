import json
import logging
import os
import sys
import time
import uuid
from io import BytesIO
import cv2
import librosa
import matplotlib.pyplot as plt
import numpy as np
import scipy.io.wavfile as wav
import sounddevice as sd
import tensorflow as tf
from flask import Flask, flash, redirect, render_template, request, url_for, session
from flask_cors import CORS
from flask_pymongo import PyMongo
from keras.layers import Dense
from keras.models import Sequential, load_model
from PIL import Image
from pydub import AudioSegment
from pymongo import MongoClient
from tensorflow import keras
import secrets



def predict(file=None):
    response = app.make_response(render_template('results.html')) 
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'  # Prevent caching
    response.headers['Pragma'] = 'no-cache'  # Prevent caching
    response.headers['Expires'] = '0'  # Prevent caching
    if file is None:
        print("No file")
        file = request.files['file']
    # Set the sample rate and duration
    sr = 22050
    duration = 7

    # Calculate the number of samples needed to reach the desired duration
    desired_samples = int(duration * sr)

    # Preprocess the data
    if file and file.filename.endswith('.wav'):
        audio_data, sr = librosa.load(file, sr=sr, mono=True, duration=None)

        # Check the duration of the file
        file_duration = librosa.get_duration(y=audio_data, sr=sr)

        if file_duration < duration:
            # Add silence to the end
            silence_samples = desired_samples - len(audio_data)
            silence = np.zeros(silence_samples)
            audio_data = np.concatenate((audio_data, silence))

        elif file_duration > duration:
            # Crop the end
            crop_samples = len(audio_data) - desired_samples
            audio_data = audio_data[:-crop_samples]

         # Split the audio into two 3.5-second segments
        segment_duration = 3.5
        segment_samples = int(segment_duration * sr)
        segment1 = audio_data[:segment_samples]
        segment2 = audio_data[segment_samples:2*segment_samples]

         # Compute the spectrograms for each segment
        img1 = librosa.feature.melspectrogram(y=segment1, sr=sr)
        img2 = librosa.feature.melspectrogram(y=segment2, sr=sr)
       
        
        # Convert mel-spectrograms to images
        # Save the spectrogram with a unique filename using timestamp
        timestamp = str(time.time())
        img1_filename = f'spec1_{timestamp}.png'
        img2_filename = f'spec2_{timestamp}.png'
        
        img1 = librosa.power_to_db(img1, ref=np.max)
        img1 = cv2.normalize(img1, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)  # Normalize to [0,255] for the color map
        img1 = cv2.applyColorMap(img1, cv2.COLORMAP_MAGMA)  # Apply 'jet' color map
        cv2.imwrite(img1_filename, img1)  # Save the spectrogram as an image with 'jet' color map

        img2 = librosa.power_to_db(img2, ref=np.max)
        img2 = cv2.normalize(img2, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)  # Normalize to [0,255] for the color map
        img2 = cv2.applyColorMap(img2, cv2.COLORMAP_MAGMA)  # Apply 'jet' color map
        cv2.imwrite(img2_filename, img2)  # Save the spectrogram as an image with 'jet' color map
            

        images=[]
        # Load and resize images to 224x224
        with Image.open(img1_filename) as img:
            # Convert the image to RGB format (remove alpha channel)
            img = img.convert('RGB')
            img = img.resize((224, 224))
             # Convert the image to a numpy array and normalize the pixel values
            img_array = np.array(img) / 255.0
            # Add the image data to the list
            images.append(img_array)
            
        with Image.open(img2_filename) as img:
            # Convert the image to RGB format (remove alpha channel)
            img = img.convert('RGB')
            img = img.resize((224, 224))
                # Convert the image to a numpy array and normalize the pixel values
            img_array = np.array(img) / 255.0
            # Add the image data to the list
            images.append(img_array)

        # Convert the list of images to a batch of images
        images = np.stack(images, axis=0)
        # Make a prediction using the model
        prediction = model.predict(images)
        prediction=np.sum(prediction, axis=0)

       
        
        print(prediction)
        
        # Convert the prediction to a dictionary
        prediction_dict = {}
        for label, idx in label_to_idx.items():
            prediction_dict[label] = float(prediction[idx])
        print(prediction_dict, file=sys.stderr)
        # Get the label with the highest value
        max_label = max(prediction_dict, key=prediction_dict.get)
        
        
        # Create an array with the corresponding label
        labels_array = []
        for label, value in prediction_dict.items():
            if value == prediction_dict[max_label]:
                labels_array.append(label)
    return labels_array[0]





# Load the model
model = load_model("model1.h5")
model.summary()

# Used labels for the model
label_to_idx = {'Discomfort': 0, 'Hunger': 1, 'Tiredness': 2}

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')  # Update connection string as per your MongoDB setup
db = client['Crybaby']  # Replace 'my_database' with the name of your database

# Check if 'users' collection exists in the database
if 'users' not in db.list_collection_names():
    # Create 'users' collection
    users_collection = db['users']
    print("Collection 'users' created successfully.")
else:
    users_collection = db['users']
    print("Collection 'users' already exists.")

# # Delete all documents in the 'users' collection
# result = users_collection.delete_many({})  # Empty filter to match all documents



################## DB ##################
########################################


# Define Recording schema
class Recording:
    def __init__(self, date, duration, filepath):
        self.date = date
        self.duration = duration
        self.filepath = filepath

# Define Newborn schema
class Newborn:
    def __init__(self, name, birthdate,gender):
        self.name = name
        self.birthdate = birthdate
        self.gender=gender
        self.recordings = []

    def add_recording(self, date, duration, filepath):
        recording = Recording(date, duration, filepath)
        self.recordings.append(recording)
        


# Define User schema
class User:
    def __init__(self, username, password, email,  loggedin, newborns):
        self.username = username
        self.password = password
        self.email = email
        self.loggedin=loggedin
        self.newborns = []

    def add_newborn(self, name, birthdate,gender):
        newborn = Newborn(name, birthdate,gender)
        self.newborns.append(newborn)
        
    def get_newborn_by_name(self, name):
        for newborn in self.newborns:
            if newborn.name == name:
                return newborn
        return None
    

       
    
    # EXAMPLES #
    
# user = User("username", "password", "email")
# user.add_newborn("Baby", "2022-01-01")

#newborn = user.get_newborn_by_name("Baby")

#newborn.add_recording("2022-01-01", 60, "/path/to/recording.wav")


################## DB ##################
########################################


app = Flask(__name__, static_url_path='/static')

CORS(app)
CORS(app, origins=['http://127.0.0.1:5000'])
app.secret_key = 'mysecretkey'

# Configuration for MongoDB
app.config['MONGO_URI'] = 'mongodb://localhost:27017/Crybaby'
mongo = PyMongo(app)

# Define a route for the home page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get the entered username and password from the form
        username = request.form['username']
        password = request.form['password']

        # Perform authentication logic here by querying MongoDB
        # Replace this with your own authentication implementation
        users = mongo.db.users
        user = users.find_one({'username': username, 'password': password})
        if user:
            users_collection.update_one({'username': username}, {'$set': {'loggedin': True}})
            session['logged_in'] = True
            session['username'] = username
            session['password'] = password
            session['email']=  users_collection.find_one({'username': username}).get('email')
            

            # If username and password are correct, redirect to a success page
            return redirect(url_for('home'))
        else:
            # If username and password are incorrect, show an error message
            error = 'Invalid username or password. Please try again.'
            return redirect(url_for('login'))
    else:
        # If it's a GET request, render the login page
        return render_template('login.html')


@app.route('/logout')
def logout():
    users_collection.update_one({'username': session['username']}, {'$set': {'loggedin': False}})
    # Clear the session data
    session.clear()
    # Redirect to the login page
    return redirect(url_for('login'))

@app.route('/home', methods=['GET','POST'])
def home():
    print(session)
    # Check if the user is logged in
    if 'logged_in' not in session or not session['logged_in'] :
        # If not, redirect to the login page
        return redirect(url_for('login'))
    else:
        # If the user is logged in, render the home page
        return render_template('home.html',username=session['username'])
    

# Define a route for the register page
@app.route('/register', methods=['GET','POST'])
def register():
    
    if request.method == 'POST':
        # Get the entered username and password from the form
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Check if username or email already exists in the database
        existing_user = users_collection.find_one({'$or': [{'username': username}, {'email': email}]})
        if existing_user:
            flash( "Username or email already exists. Please choose a different username or email.")
            return redirect(url_for('register'))
        # Create a new user
        
        
        # Generate a verification token
        token = secrets.token_hex(16)
        
        session['logged_in'] = False
        session['username'] = username
        session['password'] = password
        session['email']=  email    
        new_user = User(username, password, email,False,None)

           
        # Insert the user object into the 'users' collection
        result = users_collection.insert_one({
            'username': new_user.username,
            'password': new_user.password,
            'email': new_user.email,
            'loggedin': False,
            'newborns': []
        })

        print(f'User added successfully with ID: {result.inserted_id}')
        # Redirect to the login page after successful registration
        return redirect(url_for('login'))

    # Render the register page
    return render_template('register.html')


@app.route('/upload', methods=['POST','GET'])
def upload():
    # Check if the user is logged in
    if 'logged_in' not in session or not session['logged_in']:
        # If not, redirect to the login page
        return redirect(url_for('login'))
    
    if request.method == 'GET':
        return render_template("upload.html")
    else:
        file = request.files['file']
        # call the predict function to get the result
        res = predict(file)
        # pass the result to the template as a variable
        print(res)
        return render_template("upload.html", result=res)


@app.route('/record', methods=['POST','GET'])
def record():
    #print(request.files.keys()) 
    # Check if the user is logged in
    if 'logged_in' not in session or not session['logged_in'] :
        # If not, redirect to the login page
        return redirect(url_for('login'))
    if request.method == 'POST':
        # Get the file from the request
        file = request.files['file']
        file.save("test.wav")
        # Check if the file is valid
        # Call your predict() function with the wav_audio data and get the appropriate response based on your application logic
        result = predict(file)
        # Return the response
        print(result)
        return result

    else:
        return render_template("record.html")


@app.route('/history')
def history():
    if 'logged_in' not in session or not session['logged_in'] :
        # If not, redirect to the login page
        return redirect(url_for('login'))
    return render_template('history.html', history=history)



@app.route('/user', methods=['GET', 'POST'])
def user():
    if 'logged_in' not in session or not session['logged_in']:
        # If not, redirect to the login page
        return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template('user.html', email=session['email'], username=session['username'], password=session['password'])
    else:
        new_password = request.form['password']
        new_email = request.form['email']
        users = mongo.db.users
        users.update_one({'username': session['username']}, {'$set': { 'password': new_password, 'email': new_email}}) 
        session['password'] = new_password
        session['email']=  new_email
        return redirect(url_for('home'))
    
@app.route('/newborns', methods=['GET', 'POST'])
def newborns():
    if 'logged_in' not in session or not session['logged_in'] :
        # If not, redirect to the login page
        return redirect(url_for('login'))
    
    # Load the current user from the database
    current_user = db.users.find_one({'username': session['username']})
    
    if request.method == 'GET':
        return render_template('newborns.html', newborns=current_user['newborns'])
    else:
        # Get the form data
        name = request.form['name']
        birthdate = request.form['birthdate']
        gender = request.form['gender']
        
        # Create a new newborn object and add it to the current user
        newborn = {'name': name, 'birthdate': birthdate, 'gender': gender, 'recordings': []}
        current_user['newborns'].append(newborn)
        
        # Save the updated user to the database
        db.users.update_one({'username': current_user['username']}, {'$set': current_user})
        
        # Redirect to the newborns page
        return redirect(url_for('newborns'))




if __name__ == '__main__':
    app.run(debug=True)
