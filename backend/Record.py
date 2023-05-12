import subprocess
from flask import Blueprint, request, session,redirect,url_for,render_template,flash
from services.predictionModels import predict
from services.mongoDB import db
from werkzeug.datastructures import FileStorage

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
        result = predict(data)

        # Return the response
        print(result)
        return result
