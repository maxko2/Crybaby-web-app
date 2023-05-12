from flask import Blueprint, session,redirect,url_for,render_template


home_bp = Blueprint('home', __name__, )

@home_bp.route('/home', methods=['GET','POST'])
def home():
    print(session)
    # Check if the user is logged in
    if 'logged_in' not in session or not session['logged_in'] :
        # If not, redirect to the login page
        return redirect(url_for('login.login'))
    else:
        # If the user is logged in, render the home page
        return render_template('home.html',username=session['username'])
    