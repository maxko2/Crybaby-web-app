from flask import Blueprint, redirect, render_template, request, session, url_for , current_app
from services.mongoDB import db


edit_bp = Blueprint('edit', __name__, )


@edit_bp.route('/newborns/<int:index>/edit', methods=['GET', 'POST'])
def edit_newborn(index):
    if 'logged_in' not in session or not session['logged_in']:
        # If not logged in, redirect to the login page
        return redirect(url_for('login.login'))

    # Load the current user from the database
    current_user = db.users.find_one({'username': session['username']})

    # Get the newborn to edit
    newborn = current_user['newborns'][index]

    if request.method == 'POST':
        # Get the form data
        name = request.form['name']
        birthdate = request.form['birthdate']
        gender = request.form['gender']

        # Check if the new name is already taken by another newborn
        for i, nb in enumerate(current_user['newborns']):
            if i != index and nb['name'] == name:
                # Name already exists, notify the user
                notification = {
                    'type': 'error',
                    'message': 'Name already exists. Please choose a different name.'
                }
                return render_template('edit_newborn.html', index=index, newborn=newborn, notification=notification)

        # Update the newborn object
        newborn['name'] = name
        newborn['birthdate'] = birthdate
        newborn['gender'] = gender

        # Save the updated user to the database
        db.users.update_one({'username': current_user['username']}, {'$set': current_user})

        # Redirect to the newborns page
        return redirect(url_for('newborns.newborns'))

    return render_template('edit_newborn.html', index=index, newborn=newborn)



delete_bp = Blueprint('delete', __name__, )
@delete_bp.route('/newborns/<int:newborn_id>', methods=['POST', 'DELETE'])
def delete_newborn(newborn_id):
    if 'logged_in' not in session or not session['logged_in']:
        # If not, redirect to the login page
        return redirect(url_for('login.login'))
    
    # Load the current user from the database
    current_user = db.users.find_one({'username': session['username']})

    # Remove the newborn from the user's list
    current_user['newborns'].pop(newborn_id)

    # Save the updated user to the database
    db.users.update_one({'username': current_user['username']}, {'$set': current_user})

    # Redirect to the newborns page
    return redirect(url_for('newborns.newborns'))