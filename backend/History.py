from flask import Blueprint, session,redirect,url_for,render_template,flash
from services.predictionModels import predict
from services.mongoDB import db

history_bp = Blueprint('history', __name__ )

@history_bp.route('/history')
def history():
    if 'logged_in' not in session or not session['logged_in'] :
        # If not, redirect to the login page
        return redirect(url_for('login'))
    return render_template('history.html', history=history)

