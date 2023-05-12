# Define Newborn schema
from models.Recording import Recording

class Newborn:
    def __init__(self, name, birthdate, gender):
        self.name = name
        self.birthdate = birthdate
        self.gender = gender
        self.recordings = []
    def add_recording(self, name, date, duration, filedata, label=None, feedback=None):
        recording = Recording(name, date, duration, filedata, label, feedback)
        self.recordings.append(recording)
        
