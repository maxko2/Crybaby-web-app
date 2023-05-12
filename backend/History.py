from flask import Blueprint, session,redirect,url_for,render_template,flash,request
from services.predictionModels import predict
from services.mongoDB import db

history_bp = Blueprint('history', __name__ )

@history_bp.route('/history')
def history():
    if 'logged_in' not in session or not session['logged_in']:
        # If not, redirect to the login page
        return redirect(url_for('login.login'))

    # Load the current user from the database
    current_user = db.users.find_one({'username': session['username']})
    newborns = current_user['newborns']
    
    if request.method == 'POST':
        # Get the selected newborn name from the form data
        selected_newborn_name = request.form['newborn']

        # Find the selected newborn in the current user's list of newborns
        selected_newborn = next((newborn for newborn in current_user['newborns'] if newborn['name'] == selected_newborn_name), None)

        if selected_newborn:
            # If the selected newborn is found, retrieve its recordings
            recordings = selected_newborn.get('recordings', [])
            return render_template('history.html', selected_newborn=selected_newborn, recordings=recordings)
        else:
            # If the selected newborn is not found, display an error message
            flash('Selected newborn not found')
            return redirect(url_for('history'))

    return render_template('history.html', newborns=newborns)