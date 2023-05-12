# Define User schema
from models.Newborn import Newborn


class User:
    def __init__(self, username, password, email,  loggedin, newborns):
        self.username = username
        self.password = password
        self.email = email
        self.loggedin=loggedin
        self.newborns = []

    def add_newborn(self, name, birthdate,gender):
        newborn = Newborn(name, birthdate,gender)
        self.newborns.append(newborn)
        
    def get_newborn_by_name(self, name):
        for newborn in self.newborns:
            if newborn.name == name:
                return newborn
        return None