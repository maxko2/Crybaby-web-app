# App introduction 👶
Welcome to **Crybaby**. This project aims to classify newborn cries into 3 different categories (Tiredness, Hunger and Discomfort) using machine learning techniques utilizing audio files visual representation in the form of spectrograms. The web app provides an intuitive interface for users to record and analyze the cries of newborns, helping parents and caregivers gain insights into their baby's needs.


![image](https://github.com/maxko2/Crybaby-web-app/assets/49914498/51c0b2ef-26df-43a9-af8d-2c16cbf669c8)

# Contents
1. Initial Requirements
2. Model Training
3. App Installation

# Initial Requirements
 - Internet connection - for downloading the model automatically by the app and running a production server.
 - Trained model - h5 model file for predictions (explained in the next section).
 - Python version 3.11 - recommended for running the app [Download from Microsoft 
          store](https://apps.microsoft.com/store/detail/python-311/9NRWMJP3717K?hl=en-us&gl=us).
          
 - ffmpeg installed - [Download from official 
         website](https://ffmpeg.org/download.html).
         
 - Add ffmpeg path to System Environment Variables in the Path section 
 ![image](https://i.imgur.com/7jjHdyn.png)
 
 - MongoDB database - make sure to have Atlas account (for online database) or create localhost database (for local database) [MongoDB website](https://www.mongodb.com).


# Model Training

 - Download a dataset or create your own - we used [donate-a-cry corpus dataset](https://github.com/gveres/donateacry-corpus). Important to note we used the **cleaned and updated version**.
 - We combined burping and belly pain with discomfort and came up with 3 final labels - **Discomfort**, **Tiredness** and **Hunger**.
 - The dataset is unbalanced and 2 out of the 3 labels have very few audio samples - this will require augmentations to expand those labels and dataset.
 - Create a folder on you Google Drive and upload the dataset folders in this way:
 ![](https://i.imgur.com/v5RGZ2F.png)
 - Create 2 additional folders (**Exported model** and **Spectrograms**).
 - Make a copy of this Google Colab notebook [Crybaby model](https://colab.research.google.com/drive/1B4__lcx4jVSa0GyM7LuUFc3F71G0ot5w?authuser=1#scrollTo=ZWXv5pPWyQIg).
 - Follow the step by step guide to create and train the model.
 ## Step-by-step guide for creating and training the model
 
 - Set the WAV files directory to your **dataset** path, the results path to your **Spectrograms** path.
 - Run the code block to mount your Google Drive to the Google Colab notebook and to save the paths.
 ![](https://imgur.com/a/rkzyf9A)

# App Installation
Clone repo:

    git clone https://github.com/maxko2/Crybaby-web-app
        
Install requirements.txt:

    pip install requirements.txt
   

## Run app locally in development server

 - Create a localhost connection on MongoDB - recommended to use MongoDB Compass [MongoDB Compass](https://www.mongodb.com/try/download/compass).
 
 
![image](https://i.imgur.com/BGQXkiJ.png)
 - Connect to localhost.
 - On Crybaby.py and services.mongoDB.py use localhost connection string ('mongodb://localhost:27017/').
 ![](https://i.imgur.com/duk7Iv0.png)
 
 - Run Crybaby.py - using either **app.run(debug=True)** or **app.run(debug=True,host="0.0.0.0")**.
 - Wait for model file to download.
 - To start the app connect to **localhost:5000** or the **generated links(s)** - a database will be created with the name **Crybaby** and the collection **users**. If for some reason you are encountering a problem, create those manually.
![](https://i.imgur.com/8mhbRdy.png)
 
## Run app locally in production server
 
 - Open port 5000 or any other port you wish to be using, on your router interface.
 - Create a connection on MongoDB with **Atlas connection string** (or use localhost) - recommended to use MongoDB Compass [MongoDB Compass](https://www.mongodb.com/try/download/compass).
 
![](https://i.imgur.com/e8NVaSt.png)
 - Connect to your database.
 - On Crybaby.py and services.mongoDB.py use your Atlas connection string (or localhost string) - **follow local server instructions**.
 -  Run Crybaby.py - using **serve(app, host='0.0.0.0', port=5000)** 
 - Wait for model file to download.
 - To start the app connect to **localhost:5000** or the **generated links(s)** - a database will be created with the name **Crybaby** and the collection **users**. If for some reason you are encountering a problem, create those manually.
 - For others users to connect to your app use **external_ip:port**:
 
 **external_ip**=[find your external ip](https://whatismyipaddress.com)
 
 **port**=5000(default)
 
 

## **Alternative:**

 Run server.bat.
 


## Optional

 Use Ngrok to create free public domain and listen to your port [Ngrok download](https://ngrok.com/download).
 
    ngrok.exe http 5000
   ![](https://i.imgur.com/YRGSWly.png)



    
