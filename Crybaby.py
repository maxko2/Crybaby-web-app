from flask import Flask, request, render_template
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

# Load the model
model = load_model("model1.h5")
model.summary()

# Used labels for the model
label_to_idx = {'Discomfort': 0, 'Hunger': 1, 'Tiredness': 2}

app = Flask(__name__)

# Define a route for the home page
@app.route('/', methods=['GET','POST'])
def home():
    return render_template('home.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    return predict()

# Define a route for handling predictions
@app.route('/predict', methods=['POST'])
def predict():
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
        
        
        # Convert mel-spectrograms to images
        # Save the spectrogram

        plt.figure(figsize=(10, 4))
        librosa.display.specshow(librosa.power_to_db(img1, ref=np.max), y_axis='mel', fmax=8000, x_axis='time')
        plt.colorbar(format='%+2.0f dB')
        plt.title( 'Spectrogram')
        plt.xlabel('Time (s)')
        plt.ylabel('Frequency (Hz)')
        plt.savefig( "spec1",bbox_inches='tight')
        plt.close()

        img2 = librosa.feature.melspectrogram(y=segment2, sr=sr)
        # Save the spectrogram

        plt.figure(figsize=(10, 4))
        librosa.display.specshow(librosa.power_to_db(img2, ref=np.max), y_axis='mel', fmax=8000, x_axis='time')
        plt.colorbar(format='%+2.0f dB')
        plt.title('Spectrogram')
        plt.xlabel('Time (s)')
        plt.ylabel('Frequency (Hz)')
        plt.savefig( "spec2", bbox_inches='tight')
        plt.close()
        # Load and resize images to 224x224
        with Image.open('img1.png') as img:
            img = img.resize((224, 224))
            spec1 = np.array(img.convert('RGB'))



        with Image.open('img2.png') as img:
            img = img.resize((224, 224))
            spec2 = np.array(img.convert('RGB'))
     
        

        # Combine the spectrograms into a single array
        data = np.array([spec1, spec2])

        # Make a prediction using the model
        prediction = model.predict(data)
        
        # Convert the prediction to a dictionary
        prediction_dict = {}
        for label, idx in label_to_idx.items():
            prediction_dict[label] = float(prediction[0][idx])
        
        # Get the label with the highest value
        max_label = max(prediction_dict, key=prediction_dict.get)
        
        # Create an array with the corresponding label
        labels_array = []
        for label, value in prediction_dict.items():
            if value == prediction_dict[max_label]:
                labels_array.append(label)

    return labels_array
# Define a route for displaying the results
@app.route('/results', methods=['GET'])
def display_results():
   labels_array = request.args.get('labels_array')
   print(labels_array, file=sys.stderr)
   return render_template('results.html', prediction=labels_array)

if __name__ == '__main__':
    app.run(debug=True)
