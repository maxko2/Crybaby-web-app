import subprocess
from flask import Blueprint, request, session,redirect,url_for,render_template,flash
from services.predictionModels import predict
from services.mongoDB import db
from werkzeug.datastructures import FileStorage
from datetime import datetime

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
    if request.method == 'GET':
        return render_template("record.html", newborns=newborns)
    else:
        # Get the file from the request
        file = request.files.get('file')

        if file is None:
            # Return an error message if the file is not in the request
            return 'No file uploaded', 400

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
        res = predict(data)
        print(res)
        filename=request.form['recording_name']
        file.seek(0)
        # Return the response
        # Get the selected newborn's name from the form
        selected_newborn_name = request.form['newborn_name']
        # datetime object containing current date and time
        now = datetime.now()
        # dd/mm/YY H:M:S
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        db.users.update_one(
            {"username": session['username'], "newborns.name": selected_newborn_name},
            {"$push": {"newborns.$.recordings": {"name": filename, "date": dt_string,  "file": file.read(), "label": res}}})
        return render_template("record.html", result=res,newborns=newborns)