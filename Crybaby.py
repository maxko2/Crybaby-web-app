from flask import Flask, request, render_template,url_for,flash,redirect
from tensorflow import keras
from keras.layers import Dense
from keras.models import Sequential, load_model
import numpy as np
from PIL import Image
import logging
import sys
import time
import librosa
import matplotlib.pyplot as plt
import json
import cv2
import os
import uuid
import tensorflow as tf
from pymongo import MongoClient
from flask_pymongo import PyMongo
import sounddevice as sd
import scipy.io.wavfile as wav
from pydub import AudioSegment
from io import BytesIO


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

# Define User schema
class User:
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email







app = Flask(__name__)
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
            # If username and password are correct, redirect to a success page
            return render_template('home.html')
        else:
            # If username and password are incorrect, show an error message
            error = 'Invalid username or password. Please try again.'
            return render_template('login.html')
    else:
        # If it's a GET request, render the login page
        return render_template('login.html')


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
        new_user = User(username, password, email)
        # Insert the user object into the 'users' collection
        result = users_collection.insert_one({
            'username': new_user.username,
            'password': new_user.password,
            'email': new_user.email
        })

        print(f'User added successfully with ID: {result.inserted_id}')
        # Redirect to the login page after successful registration
        return redirect(url_for('login'))

    # Render the register page
    return render_template('register.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    return predict(file)

@app.route('/record', methods=['POST'])
def record():
    if request.method == 'POST':
        # Check if the request contains a file
        if 'record_file' not in request.files:
            return 'No file found', 400
        
        # Get the file from the request
        file = request.files['record_file']

        # Check if the file is valid
        if file and file.filename.endswith('.ogg'):  # Update the file extension based on the actual format
            # Convert the PCM data to WAV format
            audio_data = file.read()
            pcm_audio = AudioSegment.from_file(BytesIO(audio_data), format='ogg;codecs=opus')
            wav_audio = pcm_audio.export(format='wav')

            # Call your predict() function with the wav_audio data and get the appropriate response based on your application logic
            result = predict(wav_audio)

            # Return the response
            return result
        else:
            return 'Invalid file format', 400

# Define a route for handling predictions
@app.route('/predict', methods=['POST'])
def predict(file=None):
    # Add cache control headers to prevent caching
    response = app.make_response(render_template('results.html')) 
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'  # Prevent caching
    response.headers['Pragma'] = 'no-cache'  # Prevent caching
    response.headers['Expires'] = '0'  # Prevent caching
    if file is None:
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
    print(labels_array, file=sys.stderr)
    


    return display_results(labels_array)
# Define a route for displaying the results
@app.route('/results', methods=['GET'])
def display_results(labels_array):
    return render_template('results.html', prediction=labels_array)

if __name__ == '__main__':
    app.run(debug=True)
