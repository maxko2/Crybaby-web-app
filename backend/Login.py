from flask import Blueprint, flash, redirect, render_template, request, session, url_for , current_app
import flask
from services.mongoDB import users_collection
from flask_pymongo import PyMongo

login_bp = Blueprint('login', __name__, )


@login_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get the entered username and password from the form
        username = request.form['username']
        password = request.form['password']
        # Perform authentication logic here by querying MongoDB
        user = users_collection.find_one({'username': username, 'password': password})

        if user:
            users_collection.update_one({'username': username}, {'$set': {'loggedin': True}})
            session['logged_in'] = True
            session['username'] = username
            session['password'] = password
            session['email']=  users_collection.find_one({'username': username}).get('email')
            

            # If username and password are correct, redirect to a success page
            return redirect(url_for('home.home'))
        else:
            # If username and password are incorrect, show an error message
            flash('Invalid username or password. Please try again.')
            return render_template('login.html')
    else:
        # If it's a GET request, render the login page
        return render_template('login.html')
    
@login_bp.record
def record(state):
    login_bp.mongo = state.app.config['mongo']