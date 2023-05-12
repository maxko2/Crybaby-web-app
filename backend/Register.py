from flask import Blueprint, request, session,redirect,url_for,render_template,flash
from services.mongoDB import users_collection
from models.User import User

register_bp = Blueprint('register', __name__, )


# Define a route for the register page
@register_bp.route('/register', methods=['GET','POST'])
def register():
    
    if request.method == 'POST':
        # Get the entered username and password from the form
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Check if username or email already exists in the database
        existing_user = users_collection.find_one({'$or': [{'username': username}, {'email': email}]})
        if existing_user:
            flash( "Username or email already exists. Please choose a different username or email.")
            return redirect(url_for('register.register'))
        # Create a new user
        
        
        session['logged_in'] = False
        session['username'] = username
        session['password'] = password
        session['email']=  email    
        new_user = User(username, password, email,False,None)

           
        # Insert the user object into the 'users' collection
        result = users_collection.insert_one({
            'username': new_user.username,
            'password': new_user.password,
            'email': new_user.email,
            'loggedin': False,
            'newborns': []
        })

        print(f'User added successfully with ID: {result.inserted_id}')
        # Redirect to the login page after successful registration
        return redirect(url_for('login.login'))

    # Render the register page
    return render_template('register.html')