
from flask import Flask, request, render_template
from tensorflow import keras
from keras.layers import Dense
from keras.models import Sequential, load_model
from PIL import Image
import csv
import os
import numpy as np
import logging
import sys



# Load the model
model=load_model("model1.h5")
model.summary()

#Used labels for the model
label_to_idx = {'Discomfort': 0, 'Hunger': 1, 'Tiredness': 2}

app = Flask(__name__)



# Define a route for the home page
@app.route('/', methods=['GET'])


def home():
    return render_template('home.html')
def upload():
    file = request.files['file']
    # Process the uploaded file
    return 'File uploaded successfully!'

# Define a route for handling predictions
@app.route('/predict', methods=['POST'])
def predict():
    # Get the input data from the user
    data = request.form['data']

    # Preprocess the data
    # ...

    # Make a prediction using the model
    prediction = model.predict(data)

    # Render the results template
    return render_template('results.html', prediction=prediction)


# Define 
@app.route('/results', methods=['GET'])
def results():
    # Render the results template
    return render_template('results.html')

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    app.run(debug=True)