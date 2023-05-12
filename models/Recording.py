class Recording:
       def __init__(self, name, date, duration, filedata, label=None, feedback=None):
        self.name = name
        self.date = date
        self.filedata = filedata
        self.label = label
        self.feedback = feedback
