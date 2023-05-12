

import os
import sys
import time
import cv2
import librosa
import numpy as np
from flask import Flask, flash, redirect, render_template, request, url_for, session
from flask_cors import CORS
from flask_pymongo import PyMongo
from keras.models import  load_model
from PIL import Image
from pymongo import MongoClient
import subprocess
from werkzeug.datastructures import FileStorage


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
        cv2.imwrite(img1_filename, img1)  # Save the spectrogram as an image with 'MAGMA' color map

        img2 = librosa.power_to_db(img2, ref=np.max)
        img2 = cv2.normalize(img2, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)  # Normalize to [0,255] for the color map
        img2 = cv2.applyColorMap(img2, cv2.COLORMAP_MAGMA)  # Apply 'jet' color map
        cv2.imwrite(img2_filename, img2)  # Save the spectrogram as an image with 'MAGMA' color map
            

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

        # Delete the files
        os.remove(img1_filename)
        os.remove(img2_filename)


        
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
