import json
import base64
import subprocess
import os

def extract_and_save_recordings(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)

    current_path = os.getcwd()  # Get the current working directory

    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                newborns = item.get('newborns', [])
                for newborn in newborns:
                    recordings = newborn.get('recordings', [])
                    for index, recording in enumerate(recordings):
                        file_data = recording.get('file', None)
                        feedback = recording.get('feedback', None)
                        # Only recordings classified as correct would be extracted
                        if file_data and feedback == 'correct':
                            if isinstance(file_data, dict) and '$binary' in file_data:
                                binary_data = file_data['$binary']
                                if isinstance(binary_data, dict) and 'base64' in binary_data:
                                    # Extract the binary data
                                    file_bytes = base64.b64decode(binary_data['base64'])

                                    # Generate the file name based on label and index
                                    label = recording['label']
                                    file_name = f"{label}_{index}.wav"

                                    # Save the binary data to a temporary file
                                    temp_file = f"temp{index}.raw"
                                    with open(temp_file, 'wb') as temp:
                                        temp.write(file_bytes)

                                    # Convert the temporary file to WAV using ffmpeg
                                    subprocess.run(['ffmpeg', '-f', 's16le', '-ar', '44100', '-ac', '1', '-i', temp_file, '-y', os.path.join(current_path, file_name)])

                                    # Remove the temporary file
                                    os.remove(temp_file)

                                    print(f"Recording {file_name} extracted and saved.")

# Export json file of users collection from MongoDB database and place the file in same folder as this py file
json_file = 'users.json'
extract_and_save_recordings(json_file)
