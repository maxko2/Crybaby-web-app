
from flask import Blueprint, render_template, request, session, redirect, url_for
from services.mongoDB import users_collection


user_bp = Blueprint('user', __name__ )

@user_bp.route('/user', methods=['GET', 'POST'])
def user():
    if 'logged_in' not in session or not session['logged_in']:
        # If not, redirect to the login page
        return redirect(url_for('login.login'))
    if request.method == 'GET':
        return render_template('user.html', email=session['email'], username=session['username'], password=session['password'])
    else:
        new_password = request.form['password']
        new_email = request.form['email']
        users = users_collection
        users.update_one({'username': session['username']}, {'$set': { 'password': new_password, 'email': new_email}}) 
        session['password'] = new_password
        session['email']=  new_email
        return redirect(url_for('home.home'))
    
@user_bp.record
def record(state):
    user_bp.mongo = state.app.config['mongo']