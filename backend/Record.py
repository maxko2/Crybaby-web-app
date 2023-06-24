import subprocess
from flask import Blueprint, request, session,redirect,url_for,render_template,flash
from services.predictionModels import predict
from services.mongoDB import db
from werkzeug.datastructures import FileStorage
from datetime import datetime
import os
import bson
record_bp = Blueprint('record', __name__ )

@record_bp.route('/record', methods=['POST', 'GET'])
def record():
    # Check if the user is logged in
    if 'logged_in' not in session or not session['logged_in']:
        # If not, redirect to the login page
        return redirect(url_for('login.login'))
    # get current user newborns
    current_user = db.users.find_one({'username': session['username']})
    newborns = current_user['newborns']
    document_size=len(bson.BSON.encode(current_user))
    if request.method == 'GET':
        return render_template("record.html", newborns=newborns)
    else:
        # Get the file from the request
        file = request.files.get('file')

        if file is None:
            # Return an error message if the file is not in the request
            return 'No file uploaded', 400
            # Calculate the total size of the document and the file
        total_size = document_size + file.content_length
        print(f"Document current size: {total_size} bytes")  # Print the total size
        # Check if the total size exceeds the limit (16MB)
        if total_size > 14 * 1024 * 1024:
            result="Error"
            return result

        # Get the filename from the request object
        filename = request.form.get('filename')
        if not filename:
            filename = 'output.wav'

        # Save the file to disk
        file_path = 'input.bin'
        file.save(file_path)

        # Use FFmpeg to convert the file to WAV format
        output_file_path = f'{filename}'
        subprocess.call(['ffmpeg', '-y', '-i', file_path, output_file_path])

        file = open('output.wav', 'rb')
        filename = 'output.wav'

        data = FileStorage(file, filename)
        # After performing the prediction
        result = predict(data)
        print(result)
        filename = request.form['recording_name']
        file.seek(0)
        # Return the response
        selected_newborn_name = request.form['newborn_name']
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        db.users.update_one(
            {"username": session['username'], "newborns.name": selected_newborn_name},
            {"$push": {"newborns.$.recordings": {"name": filename, "date": dt_string, "file": file.read(), "label": result}}})
        file.close()
        #os.remove("output.wav")
        #os.remove("input.bin")
        return result  # Return the prediction result as the response