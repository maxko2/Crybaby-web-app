from flask import Blueprint, request, session,redirect,url_for,render_template,flash
from services.predictionModels import predict
from services.mongoDB import db
import datetime


newborns_bp = Blueprint('newborns', __name__ )

@newborns_bp.route('/newborns', methods=['GET', 'POST'])
def newborns():
    if 'logged_in' not in session or not session['logged_in'] :
        # If not, redirect to the login page
        return redirect(url_for('login.login'))
    
    # Load the current user from the database
    current_user = db.users.find_one({'username': session['username']})
    date=datetime.datetime.now().strftime('%Y-%m-%d')
    if request.method == 'GET':
        return render_template('newborns.html', newborns=current_user['newborns'],date=date)
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
        return redirect(url_for('newborns.newborns'))