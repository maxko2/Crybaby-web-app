from flask import Blueprint, redirect, render_template, request, session, url_for
from services.mongoDB import users_collection

logout_bp=Blueprint('logout',__name__)

@logout_bp.route('/logout')
def logout():
    users_collection.update_one({'username': session['username']}, {'$set': {'loggedin': False}})
    # Clear the session data
    session.clear()
    # Redirect to the login page
    return redirect(url_for('login.login'))