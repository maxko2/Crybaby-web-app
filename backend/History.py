from flask import Blueprint, jsonify, session, redirect, url_for, render_template, flash, request
from services.predictionModels import predict
from services.mongoDB import db
import base64


history_bp = Blueprint('history', __name__)

@history_bp.route('/history')
def history():
    if 'logged_in' not in session or not session['logged_in']:
        # If not logged in, redirect to the login page
        return redirect(url_for('login.login'))

    # Load the current user from the database
    current_user = db.users.find_one({'username': session['username']})
    newborns = current_user['newborns']

    return render_template('history.html', newborns=newborns)


@history_bp.route('/history', methods=['POST'])
def history_post():
    if 'logged_in' not in session or not session['logged_in']:
        # If not logged in, redirect to the login page
        return redirect(url_for('login.login'))

    # Load the current user from the database
    current_user = db.users.find_one({'username': session['username']})
    newborns = current_user['newborns']

    # Get the selected newborn name from the form data
    selected_newborn_name = request.form['newborn']

    # Find the selected newborn in the current user's list of newborns
    selected_newborn = next((newborn for newborn in newborns if newborn['name'] == selected_newborn_name), None)

    if selected_newborn:
        # If the selected newborn is found, retrieve its recordings
        recordings = selected_newborn.get('recordings', [])
        return render_template('history.html', selected_newborn=selected_newborn, recordings=recordings)
    else:
        # If the selected newborn is not found, display an error message
        flash('Selected newborn not found')
        return redirect(url_for('history.history'))





@history_bp.route('/api/recordings/<newborn_name>', methods=['GET'])
def get_recordings(newborn_name):
    current_user = db.users.find_one({'username': session['username'], 'newborns.name': newborn_name})
    if current_user:
        newborn = next((newborn for newborn in current_user['newborns'] if newborn['name'] == newborn_name), None)
        if newborn:
            recordings = newborn.get('recordings', [])
            recordings_json = []
            for recording in recordings:
                recording_data = {
                    'name': recording['name'],
                    'date': recording['date'],
                    'prediction': recording['label'],
                    'feedback': recording.get('feedback', '')  # Include the feedback in the response
                }
                file_data = recording['file']
                if file_data:
                    # Encode the file data as Base64 string
                    file_base64 = base64.b64encode(file_data).decode('utf-8')
                    recording_data['file'] = file_base64
                
                recordings_json.append(recording_data)
            
            return jsonify(recordings_json), 200
        else:
            return jsonify({"error": "Newborn not found"}), 404
    else:
        return jsonify({"error": "User not found"}), 404


    
@history_bp.route('/api/recordings/<newborn_name>/<int:index>/feedback', methods=['POST'])
def update_feedback(newborn_name, index):
    feedback = request.form.get('feedback')
    current_user = db.users.find_one({'username': session['username'], 'newborns.name': newborn_name})
    if current_user:
        newborn = next((newborn for newborn in current_user['newborns'] if newborn['name'] == newborn_name), None)
        if newborn:
            recordings = newborn.get('recordings', [])
            if index < len(recordings):
                recording = recordings[index]
                recording['feedback'] = feedback
                db.users.update_one(
                    {'username': session['username'], 'newborns.name': newborn_name},
                    {'$set': {'newborns.$.recordings': recordings}}
                )
                return jsonify({"success": True})
            else:
                return jsonify({"error": "Recording not found"}), 404
        else:
            return jsonify({"error": "Newborn not found"}), 404
    else:
        return jsonify({"error": "User not found"}), 404

    
@history_bp.route('/api/recordings/<newborn_name>/<int:index>', methods=['DELETE'])
def delete_recording(newborn_name, index):
    current_user = db.users.find_one({'username': session['username'], 'newborns.name': newborn_name})
    if current_user:
        newborn = next((newborn for newborn in current_user['newborns'] if newborn['name'] == newborn_name), None)
        if newborn:
            recordings = newborn.get('recordings', [])
            if index < len(recordings):
                recordings.pop(index)
                db.users.update_one(
                    {'username': session['username'], 'newborns.name': newborn_name},
                    {'$set': {'newborns.$.recordings': recordings}}
                )
                return jsonify({"success": True})
            else:
                return jsonify({"error": "Recording not found"}), 404
        else:
            return jsonify({"error": "Newborn not found"}), 404
    else:
        return jsonify({"error": "User not found"}), 404
