from datetime import datetime
from flask import Blueprint, request, session,redirect,url_for,render_template,flash
from services.predictionModels import predict
from services.mongoDB import db

upload_bp = Blueprint('upload', __name__, )


@upload_bp.route('/upload', methods=['POST','GET'])
def upload():
    # Check if the user is logged in
    if 'logged_in' not in session or not session['logged_in']:
        # If not, redirect to the login page
        return redirect(url_for('login.login'))
    # get current user newborns
    current_user = db.users.find_one({'username': session['username']})
    newborns = current_user['newborns']
    if request.method == 'GET':
        return render_template("upload.html", newborns=newborns)
    else:
        file = request.files['file']
        if file is None:
            # Return an error message if the file is not in the request
            return 'No file uploaded', 400
        # call the predict function to get the result
        res = predict(file)
        # pass the result to the template as a variable
        print(res)
        binary_data = file.read()
        # Get the selected newborn's name from the form
        selected_newborn_name = request.form['newborn_name']
        # datetime object containing current date and time
        now = datetime.now()
        # dd/mm/YY H:M:S
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        recording_name = request.form['recording_name']
        db.users.update_one(
    {"username": session['username'], "newborns.name": selected_newborn_name},
    {"$push": {"newborns.$.recordings": {"name": recording_name, "date": dt_string,  "file": binary_data, "label": res}}})
        return render_template("upload.html", result=res,newborns=newborns)
